from __future__ import annotations

import json
import zipfile
from datetime import UTC, datetime
from pathlib import Path

import pytest

from chat_chronicle.adapters.claude_export import (
    ClaudeImportResult,
    load_conversations,
    parse_conversations_json,
)
from chat_chronicle.models import Conversation

FIXTURES = Path(__file__).parent / "fixtures" / "claude"


def _fixture_path(name: str) -> Path:
    return FIXTURES / name / "conversations.json"


def _load_fixture(name: str) -> object:
    return json.loads(_fixture_path(name).read_text(encoding="utf-8"))


def _parse(name: str) -> ClaudeImportResult:
    return parse_conversations_json(_load_fixture(name))


def _error_codes(result: ClaudeImportResult) -> set[str]:
    return {error.error for error in result.errors}


def _only(result: ClaudeImportResult) -> Conversation:
    assert len(result.conversations) == 1
    return result.conversations[0]


# --- minimal export -------------------------------------------------------


def test_parse_minimal_export_returns_one_conversation() -> None:
    result = _parse("minimal")

    assert result.errors == []
    conversation = _only(result)
    assert isinstance(conversation, Conversation)
    assert len(conversation.messages) == 2


def test_minimal_conversation_metadata_is_normalized() -> None:
    conversation = _only(_parse("minimal"))

    assert conversation.provider == "claude"
    assert conversation.provider_conv_id == "conv-minimal-1"
    assert conversation.title == "SQLite FTS5 ranking"
    assert conversation.url == "https://claude.ai/chat/conv-minimal-1"
    assert conversation.created_at == datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
    assert conversation.updated_at == datetime(2026, 1, 1, 1, 0, 0, 500_000, tzinfo=UTC)


def test_minimal_messages_are_ordered_and_mapped() -> None:
    human, assistant = _only(_parse("minimal")).messages

    assert [human.seq, assistant.seq] == [0, 1]
    assert human.role == "human"
    assert human.provider_message_id == "msg-human"
    assert human.body == "How does bm25() ranking work in FTS5?"
    assert human.created_at == datetime(2026, 1, 1, 0, 0, tzinfo=UTC)

    assert assistant.role == "assistant"
    # Multiple text blocks are joined with a blank line.
    assert assistant.body == (
        "It scores rows by term frequency and inverse document frequency.\n\n"
        "Lower scores rank higher, so order by bm25() ascending."
    )


# --- realistic (sanitized) export shape -----------------------------------


def test_realistic_export_parses_flat_conversation_list() -> None:
    result = _parse("realistic")

    assert result.errors == []
    assert [conversation.provider_conv_id for conversation in result.conversations] == [
        "9f1c1a4e-0000-4000-8000-000000000001",
        "9f1c1a4e-0000-4000-8000-000000000002",
    ]


def test_realistic_export_preserves_chat_message_order_with_contiguous_seq() -> None:
    conversation = _parse("realistic").conversations[0]

    assert [message.seq for message in conversation.messages] == [0, 1]
    assert [message.role for message in conversation.messages] == ["human", "assistant"]
    assert conversation.messages[0].body.startswith("What is the simplest way")
    assert conversation.messages[1].body == "Use Task Scheduler with schtasks.exe."


def test_realistic_export_normalizes_timestamps_to_utc() -> None:
    conversation = _parse("realistic").conversations[0]

    assert conversation.created_at == datetime(2026, 2, 14, 9, 12, 33, 412_915, tzinfo=UTC)
    assert conversation.updated_at == datetime(2026, 2, 14, 9, 20, 4, 881_220, tzinfo=UTC)
    for message in conversation.messages:
        assert message.created_at is not None
        assert message.created_at.tzinfo is UTC


# --- content extraction ---------------------------------------------------


def test_mixed_content_preserves_text_and_reports_non_text_blocks() -> None:
    result = _parse("mixed_content")
    conversation = _only(result)

    human, assistant = conversation.messages
    assert human.body == (
        "Here is the throughput chart.\n\nWhy does it flatten after 1k conversations?"
    )
    assert "non_text_content_block" in _error_codes(result)


def test_message_with_only_non_text_content_is_skipped_and_seq_stays_contiguous() -> None:
    conversation = _only(_parse("mixed_content"))

    ids = [message.provider_message_id for message in conversation.messages]
    assert "msg-mixed-tool-only" not in ids
    assert [message.seq for message in conversation.messages] == [0, 1]


def test_plain_string_content_is_supported() -> None:
    conversation = _only(_parse("mixed_content"))

    assert conversation.messages[1].provider_message_id == "msg-mixed-plain-string"
    assert conversation.messages[1].body == (
        "Batch inserts amortize; the flattening is the transaction commit cost."
    )


# --- missing optional fields ----------------------------------------------


def test_missing_optional_fields_degrade_cleanly() -> None:
    conversation = _parse("missing_optional").conversations[0]

    assert conversation.title is None
    assert all(message.provider_message_id is None for message in conversation.messages)
    # No conversation-level updated_at: fall back to the newest message timestamp.
    assert conversation.updated_at == datetime(2026, 6, 1, 12, 7, 30, tzinfo=UTC)


def test_updated_at_falls_back_to_created_at_when_no_message_timestamps() -> None:
    conversation = _parse("missing_optional").conversations[1]

    assert conversation.messages[0].created_at is None
    assert conversation.updated_at == conversation.created_at
    assert conversation.updated_at == datetime(2026, 6, 2, 12, 0, tzinfo=UTC)


# --- malformed records ----------------------------------------------------


def test_malformed_records_do_not_abort_parsing_of_valid_conversations() -> None:
    result = _parse("malformed")

    ids = [conversation.provider_conv_id for conversation in result.conversations]
    assert ids == ["conv-bad-chat-messages", "conv-mixed-validity"]

    # The non-dict entry and the message with unusable content are dropped; a message
    # whose only problem is a bad role keeps its body.
    survivor = result.conversations[1]
    assert [message.provider_message_id for message in survivor.messages] == [
        "msg-bad-role",
        "msg-good",
    ]
    assert [message.seq for message in survivor.messages] == [0, 1]


def test_malformed_records_report_expected_error_codes() -> None:
    codes = _error_codes(_parse("malformed"))

    assert {
        "invalid_conversation_record",
        "missing_conversation_uuid",
        "invalid_chat_messages",
        "invalid_title",
        "invalid_timestamp",
        "invalid_message_record",
        "invalid_message_content",
    } <= codes


def test_conversation_with_invalid_chat_messages_keeps_identity_and_empty_messages() -> None:
    conversation = _parse("malformed").conversations[0]

    assert conversation.provider_conv_id == "conv-bad-chat-messages"
    assert conversation.messages == []


def test_invalid_role_is_reported_and_message_body_survives() -> None:
    result = _parse("malformed")
    survivor = result.conversations[1]

    by_id = {message.provider_message_id: message for message in survivor.messages}
    bad_role = by_id["msg-bad-role"]
    assert bad_role.role is None
    assert bad_role.body == "Roles must be strings."
    assert "invalid_role" in _error_codes(result)


def test_offset_aware_timestamps_are_converted_to_utc() -> None:
    conversation = _parse("malformed").conversations[1]

    # "2026-05-02T10:30:00+02:00" -> 08:30 UTC.
    assert conversation.updated_at == datetime(2026, 5, 2, 8, 30, tzinfo=UTC)
    # "not-a-timestamp" degrades to None and is reported.
    assert conversation.created_at is None


def test_non_list_payload_is_reported_not_raised() -> None:
    result = parse_conversations_json({"conversations": []})

    assert result.conversations == []
    assert _error_codes(result) == {"unexpected_export_shape"}


def test_errors_are_json_serializable_for_ingest_runs() -> None:
    result = _parse("malformed")

    payload = [error.model_dump() for error in result.errors]
    encoded = json.dumps(payload)

    assert json.loads(encoded) == payload
    assert all(set(entry) == {"record_id", "message_id", "error", "detail"} for entry in payload)


# --- load_conversations() sources -----------------------------------------


def test_load_conversations_from_direct_json_path() -> None:
    result = load_conversations(_fixture_path("minimal"))

    assert result.errors == []
    assert _only(result).provider_conv_id == "conv-minimal-1"


def test_load_conversations_from_directory() -> None:
    result = load_conversations(_fixture_path("minimal").parent)

    assert result.errors == []
    assert _only(result).provider_conv_id == "conv-minimal-1"


def test_load_conversations_from_zip(tmp_path: Path) -> None:
    archive_path = tmp_path / "claude-export.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.write(_fixture_path("minimal"), "data-2026-01-01/conversations.json")

    result = load_conversations(archive_path)

    assert result.errors == []
    assert _only(result).provider_conv_id == "conv-minimal-1"


def test_load_conversations_reports_missing_source(tmp_path: Path) -> None:
    result = load_conversations(tmp_path / "nope.json")

    assert result.conversations == []
    assert _error_codes(result) == {"source_not_found"}


def test_load_conversations_reports_directory_without_conversations_json(tmp_path: Path) -> None:
    result = load_conversations(tmp_path)

    assert result.conversations == []
    assert _error_codes(result) == {"conversations_json_not_found"}


def test_load_conversations_reports_zip_without_conversations_json(tmp_path: Path) -> None:
    archive_path = tmp_path / "empty-export.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("data-2026-01-01/users.json", "{}")

    result = load_conversations(archive_path)

    assert result.conversations == []
    assert _error_codes(result) == {"conversations_json_not_found"}


def test_load_conversations_reports_invalid_json(tmp_path: Path) -> None:
    broken = tmp_path / "conversations.json"
    broken.write_text("{not json", encoding="utf-8")

    result = load_conversations(broken)

    assert result.conversations == []
    assert _error_codes(result) == {"invalid_json"}


@pytest.mark.parametrize("name", ["minimal", "realistic", "mixed_content", "missing_optional"])
def test_all_parsed_conversations_use_the_claude_provider_and_url(name: str) -> None:
    for conversation in _parse(name).conversations:
        assert conversation.provider == "claude"
        assert conversation.url == f"https://claude.ai/chat/{conversation.provider_conv_id}"
