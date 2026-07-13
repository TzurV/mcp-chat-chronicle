from __future__ import annotations

import time
from datetime import UTC, datetime
from pathlib import Path

import pytest

from chat_chronicle.db import connect, rebuild_fts, upsert_conversation
from chat_chronicle.models import Conversation, Message
from chat_chronicle.search import get_conversation_detail, search_conversations


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
) -> Conversation:
    return Conversation(
        provider=provider,
        provider_conv_id=provider_conv_id,
        title=title,
        url=url,
        origin_path=origin_path,
        resume_hint=resume_hint,
        created_at=updated_at,
        updated_at=updated_at,
        messages=[
            Message(
                role="user",
                created_at=updated_at,
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
