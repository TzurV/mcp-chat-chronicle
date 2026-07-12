from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path

import pytest

from chat_chronicle.adapters.openai_codex import (
    OpenAICodexExtractResult,
    load_conversations,
    parse_session_jsonl,
)
from chat_chronicle.models import Conversation

FIXTURES = Path(__file__).parent / "fixtures" / "openai_codex"


def _fixture_path(name: str, filename: str | None = None) -> Path:
    directory = FIXTURES / name
    if filename is not None:
        return directory / filename
    matches = sorted(directory.glob("*.jsonl"))
    assert len(matches) == 1
    return matches[0]


def _parse(name: str) -> OpenAICodexExtractResult:
    path = _fixture_path(name)
    return parse_session_jsonl(path.read_text(encoding="utf-8"), source_name=str(path))


def _error_codes(result: OpenAICodexExtractResult) -> set[str]:
    return {error.error for error in result.errors}


def _only(result: OpenAICodexExtractResult) -> Conversation:
    assert len(result.conversations) == 1
    return result.conversations[0]


def test_parse_minimal_session_returns_one_conversation() -> None:
    result = _parse("minimal")

    assert result.errors == []
    conversation = _only(result)
    assert isinstance(conversation, Conversation)
    assert conversation.provider == "openai_codex"
    assert conversation.provider_conv_id == "codex-minimal-1"
    assert conversation.url is None
    assert conversation.origin_path == str(_fixture_path("minimal").resolve())
    assert conversation.resume_hint is None
    assert len(conversation.messages) == 2


def test_minimal_session_metadata_and_timestamps_are_normalized() -> None:
    conversation = _only(_parse("minimal"))

    assert conversation.created_at == datetime(2026, 6, 1, 10, 0, tzinfo=UTC)
    assert conversation.updated_at == datetime(2026, 6, 1, 10, 2, tzinfo=UTC)
    assert conversation.title == "How do I list Codex session files?"


def test_input_text_and_output_text_blocks_become_ordered_message_bodies() -> None:
    user, assistant = _only(_parse("minimal")).messages

    assert [user.seq, assistant.seq] == [0, 1]
    assert user.role == "user"
    assert user.provider_message_id == "msg-user"
    assert user.body == "How do I list Codex session files?"
    assert user.created_at == datetime(2026, 6, 1, 10, 1, tzinfo=UTC)

    assert assistant.role == "assistant"
    assert assistant.provider_message_id == "msg-assistant"
    assert assistant.body == "Look under the sessions directory.\n\nEach rollout file is JSONL."
    assert assistant.created_at == datetime(2026, 6, 1, 10, 2, tzinfo=UTC)


def test_known_metadata_rows_are_skipped_without_errors() -> None:
    result = _parse("metadata")
    conversation = _only(result)

    assert result.errors == []
    assert [message.role for message in conversation.messages] == ["developer"]
    assert conversation.messages[0].body == "Keep this fixture synthetic."
    assert conversation.messages[0].seq == 0


def test_agent_reasoning_event_rows_are_skipped_without_errors() -> None:
    result = _parse("metadata")

    assert "unknown_event_msg_type" not in _error_codes(result)
    assert result.errors == []


def test_event_message_fallback_handles_user_and_agent_messages() -> None:
    conversation = _only(_parse("event_fallback"))

    assert [message.role for message in conversation.messages] == ["user", "assistant"]
    assert [message.body for message in conversation.messages] == [
        "Summarize the fixture policy.",
        "Use synthetic fixtures only.",
    ]
    assert [message.seq for message in conversation.messages] == [0, 1]


def test_duplicate_event_and_response_messages_prefer_response_items() -> None:
    conversation = _only(_parse("duplicates"))

    assert [message.provider_message_id for message in conversation.messages] == [
        "msg-user-canonical",
        "msg-assistant-canonical",
    ]
    assert [message.body for message in conversation.messages] == [
        "Run the parser tests.",
        "The parser tests pass.",
    ]
    assert [message.seq for message in conversation.messages] == [0, 1]


def test_invalid_jsonl_line_records_error_and_does_not_abort() -> None:
    result = _parse("malformed")
    conversation = _only(result)

    assert [message.body for message in conversation.messages] == ["Valid messages still parse."]
    assert {
        "invalid_jsonl_line",
        "unknown_record_type",
        "unknown_response_item_type",
        "unknown_event_msg_type",
        "invalid_timestamp",
    } <= _error_codes(result)


def test_missing_session_id_falls_back_to_filename_identity() -> None:
    result = _parse("missing_id")
    conversation = _only(result)

    assert conversation.provider_conv_id == "rollout-no-session-meta-id"
    assert conversation.title == "Use the filename when the session id is absent."
    assert "missing_session_id" in _error_codes(result)


def test_load_conversations_from_jsonl_file() -> None:
    result = load_conversations(_fixture_path("minimal"))

    assert result.errors == []
    assert _only(result).provider_conv_id == "codex-minimal-1"


def test_load_conversations_from_nested_sessions_directory(tmp_path: Path) -> None:
    target = tmp_path / "sessions" / "2026" / "06" / "01"
    target.mkdir(parents=True)
    shutil.copyfile(_fixture_path("minimal"), target / "rollout-minimal.jsonl")
    shutil.copyfile(_fixture_path("event_fallback"), target / "rollout-event-fallback.jsonl")

    result = load_conversations(tmp_path)

    assert result.errors == []
    assert [conversation.provider_conv_id for conversation in result.conversations] == [
        "codex-event-1",
        "codex-minimal-1",
    ]


def test_session_index_title_and_updated_at_metadata_is_applied(tmp_path: Path) -> None:
    target = tmp_path / "sessions" / "2026" / "06" / "01"
    target.mkdir(parents=True)
    shutil.copyfile(_fixture_path("minimal"), target / "rollout-minimal.jsonl")
    (tmp_path / "session_index.jsonl").write_text(
        json.dumps(
            {
                "id": "codex-minimal-1",
                "thread_name": "Indexed Codex Thread",
                "updated_at": "2026-06-01T11:30:00Z",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    conversation = _only(load_conversations(tmp_path))

    assert conversation.title == "Indexed Codex Thread"
    assert conversation.updated_at == datetime(2026, 6, 1, 11, 30, tzinfo=UTC)


def test_load_conversations_reports_missing_or_unsupported_sources(tmp_path: Path) -> None:
    missing = load_conversations(tmp_path / "missing.jsonl")
    unsupported = tmp_path / "session.txt"
    unsupported.write_text("{}", encoding="utf-8")
    unsupported_result = load_conversations(unsupported)

    assert _error_codes(missing) == {"source_not_found"}
    assert _error_codes(unsupported_result) == {"unsupported_source_file"}


def test_load_conversations_reports_directory_without_sessions(tmp_path: Path) -> None:
    result = load_conversations(tmp_path)

    assert result.conversations == []
    assert _error_codes(result) == {"session_files_not_found"}


def test_errors_are_json_serializable_for_ingest_runs() -> None:
    result = _parse("malformed")

    payload = [error.model_dump() for error in result.errors]
    encoded = json.dumps(payload)

    assert json.loads(encoded) == payload
    assert all(set(entry) == {"record_id", "line_number", "error", "detail"} for entry in payload)


@pytest.mark.parametrize(
    "name",
    ["minimal", "metadata", "event_fallback", "duplicates", "malformed", "missing_id"],
)
def test_all_parsed_conversations_use_openai_codex_provider_and_no_url(name: str) -> None:
    for conversation in _parse(name).conversations:
        assert conversation.provider == "openai_codex"
        assert conversation.url is None
