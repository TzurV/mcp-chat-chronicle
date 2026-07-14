from __future__ import annotations

import time
from datetime import UTC, datetime
from pathlib import Path

import pytest

from chat_chronicle.db import connect, get_or_create_project, rebuild_fts, upsert_conversation
from chat_chronicle.models import Conversation, Message
from chat_chronicle.search import (
    get_conversation_detail,
    list_recent_conversations,
    search_conversations,
    should_show_broad_search_hint,
)


def _conversation(
    provider_conv_id: str,
    body: str,
    *,
    provider: str = "chatgpt",
    title: str = "Synthetic Search Chat",
    updated_at: datetime = datetime(2026, 1, 1, 12, 0, tzinfo=UTC),
    url: str | None = "https://chatgpt.com/c/synthetic",
    origin_path: str | None = None,
    resume_hint: str | None = None,
    created_at: datetime | None = None,
    set_updated_at: bool = True,
    project_id: int | None = None,
) -> Conversation:
    created_at = created_at or updated_at
    return Conversation(
        provider=provider,
        provider_conv_id=provider_conv_id,
        project_id=project_id,
        title=title,
        url=url,
        origin_path=origin_path,
        resume_hint=resume_hint,
        created_at=created_at,
        updated_at=updated_at if set_updated_at else None,
        messages=[
            Message(
                role="user",
                created_at=created_at,
                body=body,
                seq=0,
            )
        ],
    )


def test_search_uses_fts_ranking_and_fallback_snippet(tmp_path: Path) -> None:
    with connect(tmp_path / "chronicle.db") as conn:
        stronger = upsert_conversation(
            conn,
            None,
            _conversation("strong", "needle needle needle target phrase"),
        )
        weaker = upsert_conversation(
            conn,
            None,
            _conversation("weak", "needle appears once beside unrelated filler words"),
        )
        rebuild_fts(conn)

        results = search_conversations(conn, "needle", limit=2)

    assert [result.conversation_id for result in results] == [
        stronger.conversation_id,
        weaker.conversation_id,
    ]
    assert results[0].rank <= results[1].rank
    assert "needle needle needle target phrase" in results[0].snippet


def test_provider_since_until_and_tag_filters(tmp_path: Path) -> None:
    with connect(tmp_path / "chronicle.db") as conn:
        chatgpt = upsert_conversation(
            conn,
            None,
            _conversation(
                "chatgpt-filter",
                "docker filter target",
                provider="chatgpt",
                updated_at=datetime(2026, 1, 10, 12, 0, tzinfo=UTC),
            ),
        )
        upsert_conversation(
            conn,
            None,
            _conversation(
                "claude-filter",
                "docker filter target",
                provider="claude",
                updated_at=datetime(2026, 2, 10, 12, 0, tzinfo=UTC),
                url="https://claude.ai/chat/claude-filter",
            ),
        )
        conn.execute(
            """
            INSERT INTO enrichments (conversation_id, tags_json)
            VALUES (?, ?)
            """,
            (chatgpt.conversation_id, '["networking","docker"]'),
        )
        rebuild_fts(conn)

        provider_results = search_conversations(conn, "docker", provider="chatgpt")
        since_results = search_conversations(conn, "docker", since="2026-02-01")
        until_results = search_conversations(conn, "docker", until="2026-01-31")
        tag_results = search_conversations(conn, "docker", tag="networking")

    assert {result.provider for result in provider_results} == {"chatgpt"}
    assert {result.provider for result in since_results} == {"claude"}
    assert {result.provider for result in until_results} == {"chatgpt"}
    assert [result.conversation_id for result in tag_results] == [chatgpt.conversation_id]


def test_search_finds_linked_project_name_without_message_match(tmp_path: Path) -> None:
    with connect(tmp_path / "chronicle.db") as conn:
        project_id = get_or_create_project(conn, name="CAR GUI")
        inserted = upsert_conversation(
            conn,
            None,
            _conversation(
                "project-linked-search",
                "The transcript mentions panes and commands but not the project label.",
                provider="claude",
                title="Window layout discussion",
                url="https://claude.ai/chat/project-linked-search",
                project_id=project_id,
            ),
        )
        rebuild_fts(conn)

        results = search_conversations(conn, "CAR GUI", provider="claude")
        phrase_results = search_conversations(conn, "CAR GUI", provider="claude", phrase=True)

    assert [result.conversation_id for result in results] == [inserted.conversation_id]
    assert "CAR GUI" in results[0].snippet
    assert [result.conversation_id for result in phrase_results] == [inserted.conversation_id]


def test_default_search_remains_broad_token_search(tmp_path: Path) -> None:
    with connect(tmp_path / "chronicle.db") as conn:
        scattered = upsert_conversation(
            conn,
            None,
            _conversation(
                "broad-scattered",
                "YOU are reviewing unrelated filler before the MANAGER arrives",
            ),
        )
        rebuild_fts(conn)

        results = search_conversations(conn, "YOU are the MANAGER")

    assert [result.conversation_id for result in results] == [scattered.conversation_id]


def test_phrase_search_requires_exact_body_phrase(tmp_path: Path) -> None:
    with connect(tmp_path / "chronicle.db") as conn:
        exact = upsert_conversation(
            conn,
            None,
            _conversation("phrase-exact", "Before we continue: YOU are the MANAGER."),
        )
        upsert_conversation(
            conn,
            None,
            _conversation(
                "phrase-partial",
                "YOU are reviewing unrelated filler before the MANAGER arrives",
            ),
        )
        rebuild_fts(conn)

        results = search_conversations(conn, "YOU are the MANAGER", phrase=True)

    assert [result.conversation_id for result in results] == [exact.conversation_id]
    assert "YOU are the MANAGER" in results[0].snippet


def test_phrase_search_supports_provider_and_limit(tmp_path: Path) -> None:
    with connect(tmp_path / "chronicle.db") as conn:
        first = upsert_conversation(
            conn,
            None,
            _conversation(
                "phrase-first",
                "exact provider phrase",
                provider="openai_codex",
                updated_at=datetime(2026, 1, 2, 12, 0, tzinfo=UTC),
                url=None,
            ),
        )
        upsert_conversation(
            conn,
            None,
            _conversation(
                "phrase-second",
                "exact provider phrase",
                provider="openai_codex",
                updated_at=datetime(2026, 1, 1, 12, 0, tzinfo=UTC),
                url=None,
            ),
        )
        upsert_conversation(
            conn,
            None,
            _conversation(
                "phrase-other-provider",
                "exact provider phrase",
                provider="chatgpt",
            ),
        )
        rebuild_fts(conn)

        results = search_conversations(
            conn,
            "exact provider phrase",
            provider="openai_codex",
            limit=1,
            phrase=True,
        )

    assert [result.conversation_id for result in results] == [first.conversation_id]
    assert {result.provider for result in results} == {"openai_codex"}


def test_phrase_search_supports_date_and_tag_filters(tmp_path: Path) -> None:
    with connect(tmp_path / "chronicle.db") as conn:
        tagged = upsert_conversation(
            conn,
            None,
            _conversation(
                "phrase-tagged",
                "filtered exact phrase",
                updated_at=datetime(2026, 2, 10, 12, 0, tzinfo=UTC),
            ),
        )
        upsert_conversation(
            conn,
            None,
            _conversation(
                "phrase-untagged",
                "filtered exact phrase",
                updated_at=datetime(2026, 3, 10, 12, 0, tzinfo=UTC),
            ),
        )
        conn.execute(
            "INSERT INTO enrichments (conversation_id, tags_json) VALUES (?, ?)",
            (tagged.conversation_id, '["phrase-filter"]'),
        )
        rebuild_fts(conn)

        results = search_conversations(
            conn,
            "filtered exact phrase",
            since="2026-02-01",
            until="2026-02-28",
            tag="phrase-filter",
            phrase=True,
        )

    assert [result.conversation_id for result in results] == [tagged.conversation_id]


def test_phrase_search_title_matches_rank_above_body_matches(tmp_path: Path) -> None:
    with connect(tmp_path / "chronicle.db") as conn:
        body_match = upsert_conversation(
            conn,
            None,
            _conversation(
                "body-phrase",
                "the body contains title phrase target",
                title="Later body match",
                updated_at=datetime(2026, 3, 1, 12, 0, tzinfo=UTC),
            ),
        )
        title_match = upsert_conversation(
            conn,
            None,
            _conversation(
                "title-phrase",
                "body has only filler text",
                title="Title Phrase Target",
                updated_at=datetime(2026, 1, 1, 12, 0, tzinfo=UTC),
            ),
        )
        rebuild_fts(conn)

        results = search_conversations(conn, "title phrase target", phrase=True)

    assert [result.conversation_id for result in results] == [
        title_match.conversation_id,
        body_match.conversation_id,
    ]
    assert results[0].rank < results[1].rank


def test_body_only_phrase_matches_sort_by_last_activity_descending(
    tmp_path: Path,
) -> None:
    with connect(tmp_path / "chronicle.db") as conn:
        older = upsert_conversation(
            conn,
            None,
            _conversation(
                "body-older",
                "body only exact phrase",
                updated_at=datetime(2026, 1, 1, 12, 0, tzinfo=UTC),
            ),
        )
        newest = upsert_conversation(
            conn,
            None,
            _conversation(
                "body-newest",
                "body only exact phrase",
                updated_at=datetime(2026, 3, 1, 12, 0, tzinfo=UTC),
            ),
        )
        created_only = upsert_conversation(
            conn,
            None,
            _conversation(
                "body-created-only",
                "body only exact phrase",
                updated_at=datetime(2026, 2, 1, 12, 0, tzinfo=UTC),
                set_updated_at=False,
            ),
        )
        rebuild_fts(conn)

        results = search_conversations(conn, "body only exact phrase", phrase=True)

    assert [result.conversation_id for result in results] == [
        newest.conversation_id,
        created_only.conversation_id,
        older.conversation_id,
    ]


def test_body_only_phrase_timestamp_ties_sort_by_id_descending(tmp_path: Path) -> None:
    timestamp = datetime(2026, 4, 1, 12, 0, tzinfo=UTC)
    with connect(tmp_path / "chronicle.db") as conn:
        older_id = upsert_conversation(
            conn,
            None,
            _conversation("tie-older", "tied exact phrase", updated_at=timestamp),
        ).conversation_id
        newer_id = upsert_conversation(
            conn,
            None,
            _conversation("tie-newer", "tied exact phrase", updated_at=timestamp),
        ).conversation_id
        rebuild_fts(conn)

        results = search_conversations(conn, "tied exact phrase", phrase=True)

    assert [result.conversation_id for result in results] == [newer_id, older_id]


def test_phrase_search_handles_embedded_quotes(tmp_path: Path) -> None:
    with connect(tmp_path / "chronicle.db") as conn:
        exact = upsert_conversation(
            conn,
            None,
            _conversation("quoted-phrase", 'The answer was say "hello" now.'),
        )
        upsert_conversation(
            conn,
            None,
            _conversation("quoted-partial", 'The answer was say "hello" later, not now.'),
        )
        rebuild_fts(conn)

        results = search_conversations(conn, 'say "hello" now', phrase=True)

    assert [result.conversation_id for result in results] == [exact.conversation_id]


def test_broad_search_hint_detection() -> None:
    assert should_show_broad_search_hint("YOU are the MANAGER")
    assert not should_show_broad_search_hint("manager")
    assert not should_show_broad_search_hint("YOU are the MANAGER", phrase=True)
    assert not should_show_broad_search_hint('"YOU are the MANAGER"')
    assert not should_show_broad_search_hint("docker AND network")


def test_recent_conversations_default_limit_and_sorting(tmp_path: Path) -> None:
    with connect(tmp_path / "chronicle.db") as conn:
        inserted_ids: list[int] = []
        for index in range(12):
            inserted = upsert_conversation(
                conn,
                None,
                _conversation(
                    f"recent-{index:02d}",
                    f"recent body {index}",
                    updated_at=datetime(2026, 1, index + 1, 12, 0, tzinfo=UTC),
                    title=f"Recent {index:02d}",
                ),
            )
            inserted_ids.append(inserted.conversation_id)

        results = list_recent_conversations(conn)

    assert len(results) == 10
    assert [result.conversation_id for result in results] == list(reversed(inserted_ids[2:]))
    assert results[0].last_activity_at == "2026-01-12T12:00:00.000000Z"


def test_recent_conversations_filters_on_last_activity_and_provider(tmp_path: Path) -> None:
    with connect(tmp_path / "chronicle.db") as conn:
        upsert_conversation(
            conn,
            None,
            _conversation(
                "old-created-new-updated",
                "uses updated activity",
                provider="chatgpt",
                created_at=datetime(2026, 1, 1, 12, 0, tzinfo=UTC),
                updated_at=datetime(2026, 3, 15, 12, 0, tzinfo=UTC),
                title="Updated wins",
            ),
        )
        created_only = upsert_conversation(
            conn,
            None,
            _conversation(
                "created-only",
                "created only activity",
                provider="chatgpt",
                updated_at=datetime(2026, 2, 15, 12, 0, tzinfo=UTC),
                title="Created only",
                set_updated_at=False,
            ),
        )
        upsert_conversation(
            conn,
            None,
            _conversation(
                "claude-later",
                "claude later activity",
                provider="claude",
                updated_at=datetime(2026, 4, 1, 12, 0, tzinfo=UTC),
                title="Claude later",
                url="https://claude.ai/chat/claude-later",
            ),
        )

        provider_results = list_recent_conversations(conn, provider="chatgpt")
        window_results = list_recent_conversations(
            conn,
            since="2026-02-01",
            until="2026-02-28",
        )

    assert {result.provider for result in provider_results} == {"chatgpt"}
    assert provider_results[0].title == "Updated wins"
    assert [result.conversation_id for result in window_results] == [
        created_only.conversation_id
    ]
    assert window_results[0].last_activity_at == "2026-02-15T12:00:00.000000Z"


def test_recent_conversations_tie_breaks_by_id_descending(tmp_path: Path) -> None:
    timestamp = datetime(2026, 5, 1, 12, 0, tzinfo=UTC)
    with connect(tmp_path / "chronicle.db") as conn:
        older_id = upsert_conversation(
            conn,
            None,
            _conversation("same-time-a", "first same time", updated_at=timestamp),
        ).conversation_id
        newer_id = upsert_conversation(
            conn,
            None,
            _conversation("same-time-b", "second same time", updated_at=timestamp),
        ).conversation_id

        results = list_recent_conversations(conn, limit=2)

    assert [result.conversation_id for result in results] == [newer_id, older_id]


def test_recent_conversations_limit_and_date_validation(tmp_path: Path) -> None:
    with connect(tmp_path / "chronicle.db") as conn:
        with pytest.raises(ValueError, match="Limit must be between"):
            list_recent_conversations(conn, limit=0)
        with pytest.raises(ValueError, match="Invalid date filter"):
            list_recent_conversations(conn, since="not-a-date")


@pytest.mark.parametrize("limit", [0, 101])
def test_search_rejects_invalid_limit(tmp_path: Path, limit: int) -> None:
    with connect(tmp_path / "chronicle.db") as conn:
        with pytest.raises(ValueError, match="Limit must be between"):
            search_conversations(conn, "anything", limit=limit)


def test_search_rejects_empty_query(tmp_path: Path) -> None:
    with connect(tmp_path / "chronicle.db") as conn:
        with pytest.raises(ValueError, match="cannot be empty"):
            search_conversations(conn, "   ")


def test_get_conversation_detail_returns_ordered_messages_and_link_back(
    tmp_path: Path,
) -> None:
    with connect(tmp_path / "chronicle.db") as conn:
        inserted = upsert_conversation(
            conn,
            None,
            _conversation(
                "local-detail",
                "first local message",
                provider="openai_codex",
                url=None,
                origin_path="C:/synthetic/session.jsonl",
                resume_hint="codex resume local-detail",
            ),
        )

        detail = get_conversation_detail(conn, inserted.conversation_id)

    assert detail is not None
    assert detail.conversation_id == inserted.conversation_id
    assert detail.origin_path == "C:/synthetic/session.jsonl"
    assert detail.resume_hint == "codex resume local-detail"
    assert [message.body for message in detail.messages] == ["first local message"]


def test_search_performance_smoke_uses_indexed_fts_path(tmp_path: Path) -> None:
    with connect(tmp_path / "chronicle.db") as conn:
        for index in range(350):
            body = f"bulk filler row {index}"
            if index % 50 == 0:
                body = f"bulk needleterm row {index}"
            upsert_conversation(
                conn,
                None,
                _conversation(f"bulk-{index}", body, title=f"Bulk {index}"),
            )
        rebuild_fts(conn)

        started = time.perf_counter()
        results = search_conversations(conn, "needleterm", limit=10)
        elapsed = time.perf_counter() - started

    assert len(results) == 7
    assert elapsed < 2.0
