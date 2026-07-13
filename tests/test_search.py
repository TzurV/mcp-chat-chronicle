from __future__ import annotations

import time
from datetime import UTC, datetime
from pathlib import Path

import pytest

from chat_chronicle.db import connect, rebuild_fts, upsert_conversation
from chat_chronicle.models import Conversation, Message
from chat_chronicle.search import (
    get_conversation_detail,
    list_recent_conversations,
    search_conversations,
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
) -> Conversation:
    created_at = created_at or updated_at
    return Conversation(
        provider=provider,
        provider_conv_id=provider_conv_id,
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
