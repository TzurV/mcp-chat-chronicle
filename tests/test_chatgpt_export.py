from __future__ import annotations

import copy
import json
import zipfile
from datetime import UTC, datetime
from pathlib import Path

import pytest

from chat_chronicle.adapters.chatgpt_export import (
    ChatGPTImportResult,
    load_conversations,
    parse_conversations_json,
)
from chat_chronicle.models import Conversation

FIXTURES = Path(__file__).parent / "fixtures" / "chatgpt"


def _load_fixture(name: str) -> object:
    return json.loads((FIXTURES / name / "conversations.json").read_text(encoding="utf-8"))


def _parse(name: str) -> ChatGPTImportResult:
    return parse_conversations_json(_load_fixture(name))


def _error_codes(result: ChatGPTImportResult) -> set[str]:
    return {error.error for error in result.errors}


def _only(result: ChatGPTImportResult) -> Conversation:
    assert len(result.conversations) == 1
    return result.conversations[0]


def _minimal_record(conv_id: str, title: str, user_body: str) -> dict[str, object]:
    fixture = _load_fixture("minimal")
    assert isinstance(fixture, list)
    record = copy.deepcopy(fixture[0])
    assert isinstance(record, dict)
    record["id"] = conv_id
    record["title"] = title
    mapping = record["mapping"]
    assert isinstance(mapping, dict)
    user = mapping["node-user"]
    assert isinstance(user, dict)
    message = user["message"]
    assert isinstance(message, dict)
    content = message["content"]
    assert isinstance(content, dict)
    content["parts"] = [user_body]
    return record


def _write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


# --- minimal export -------------------------------------------------------


def test_parse_minimal_export_returns_one_conversation() -> None:
    result = _parse("minimal")

    assert result.errors == []
    conversation = _only(result)
    assert isinstance(conversation, Conversation)
    assert len(conversation.messages) == 2


def test_minimal_conversation_metadata_is_normalized() -> None:
    conversation = _only(_parse("minimal"))

    assert conversation.provider == "chatgpt"
    assert conversation.provider_conv_id == "conv-minimal-1"
    assert conversation.title == "Docker networking notes"
    assert conversation.url == "https://chatgpt.com/c/conv-minimal-1"
    assert conversation.created_at == datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
    assert conversation.updated_at == datetime(2026, 1, 1, 1, 0, 0, 500_000, tzinfo=UTC)


def test_minimal_messages_are_ordered_and_mapped() -> None:
    user, assistant = _only(_parse("minimal")).messages

    assert [user.seq, assistant.seq] == [0, 1]
    assert user.role == "user"
    assert user.provider_message_id == "msg-user"
    assert user.body == "How do I inspect a docker bridge network?"
    assert user.created_at == datetime(2026, 1, 1, 0, 0, tzinfo=UTC)

    assert assistant.role == "assistant"
    # Multiple string parts are joined with a blank line.
    assert assistant.body == (
        "Run `docker network inspect bridge`.\n\nIt prints the subnet and gateway."
    )


# --- branch selection -----------------------------------------------------


def test_current_node_selects_regenerated_branch() -> None:
    conversation = _only(_parse("branched"))

    bodies = [message.body for message in conversation.messages]
    assert bodies == [
        "Explain FTS5 tokenizers.",
        "KEPT regenerated answer: unicode61 is the default tokenizer.",
    ]
    assert all("ABANDONED" not in body for body in bodies)


def test_invalid_current_node_falls_back_to_deepest_chain() -> None:
    result = _parse("deepest_chain")
    conversation = _only(result)

    assert "invalid_current_node" in _error_codes(result)
    bodies = [message.body for message in conversation.messages]
    assert bodies == [
        "Start of the thread.",
        "KEPT first deep reply.",
        "KEPT follow-up question.",
        "KEPT final deep reply.",
    ]
    assert [message.seq for message in conversation.messages] == [0, 1, 2, 3]


def test_missing_current_node_falls_back_to_deepest_chain() -> None:
    record = _load_fixture("deepest_chain")
    assert isinstance(record, list)
    del record[0]["current_node"]

    result = parse_conversations_json(record)

    assert "missing_current_node" in _error_codes(result)
    assert len(_only(result).messages) == 4


# --- content parts --------------------------------------------------------


def test_non_text_parts_are_skipped_and_reported() -> None:
    result = _parse("non_text_parts")
    conversation = _only(result)

    bodies = [message.body for message in conversation.messages]
    # The mixed message keeps only its string parts; the image-only message is dropped.
    assert bodies == [
        "Here is the screenshot.\n\nWhat is wrong with it?",
        "The alt text is missing.",
    ]

    codes = _error_codes(result)
    assert "non_text_content_part" in codes
    assert "unsupported_content_type" in codes

    non_text = [error for error in result.errors if error.error == "non_text_content_part"]
    assert {error.node_id for error in non_text} == {"node-mixed", "node-image-only"}


@pytest.mark.parametrize("content_type", ["thoughts", "reasoning_recap"])
def test_known_openai_metadata_content_types_are_skipped_without_errors(
    content_type: str,
) -> None:
    record = _minimal_record("conv-metadata", "Metadata skip", "visible user text")
    mapping = record["mapping"]
    assert isinstance(mapping, dict)
    user = mapping["node-user"]
    assert isinstance(user, dict)
    message = user["message"]
    assert isinstance(message, dict)
    message["content"] = {
        "content_type": content_type,
        "parts": ["synthetic non-visible metadata"],
    }

    result = parse_conversations_json([record])

    assert result.errors == []
    conversation = _only(result)
    assert [message.body for message in conversation.messages] == [
        "Run `docker network inspect bridge`.\n\nIt prints the subnet and gateway."
    ]


# --- malformed records ----------------------------------------------------


def test_malformed_records_do_not_abort_parsing() -> None:
    result = _parse("malformed")

    parsed_ids = {conversation.provider_conv_id for conversation in result.conversations}
    assert "conv-healthy" in parsed_ids

    codes = _error_codes(result)
    assert "invalid_conversation_record" in codes
    assert "missing_conversation_id" in codes
    assert "missing_mapping" in codes
    assert "invalid_timestamp" in codes
    assert "broken_parent_chain" in codes


def test_malformed_record_timestamps_degrade_to_none() -> None:
    result = _parse("malformed")
    degraded = next(
        conversation
        for conversation in result.conversations
        if conversation.provider_conv_id == "conv-degraded"
    )

    assert degraded.created_at is None
    assert degraded.updated_at is not None
    assert degraded.messages[0].created_at is None


def test_healthy_message_without_id_falls_back_to_node_id() -> None:
    result = _parse("malformed")
    healthy = next(
        conversation
        for conversation in result.conversations
        if conversation.provider_conv_id == "conv-healthy"
    )

    assert healthy.messages[-1].provider_message_id == "node-assistant"


def test_non_list_payload_is_reported_not_raised() -> None:
    result = parse_conversations_json({"conversations": []})

    assert result.conversations == []
    assert _error_codes(result) == {"unexpected_export_shape"}


def test_errors_are_json_serializable_for_ingest_runs() -> None:
    result = _parse("malformed")

    payload = [error.model_dump() for error in result.errors]
    assert json.loads(json.dumps(payload)) == payload


# --- load_conversations() source handling ---------------------------------


def test_load_conversations_from_json_file() -> None:
    result = load_conversations(FIXTURES / "minimal" / "conversations.json")

    assert result.errors == []
    assert _only(result).provider_conv_id == "conv-minimal-1"


def test_load_conversations_from_directory() -> None:
    result = load_conversations(FIXTURES / "minimal")

    assert result.errors == []
    assert _only(result).provider_conv_id == "conv-minimal-1"


def test_load_conversations_from_zip(tmp_path: Path) -> None:
    archive_path = tmp_path / "chatgpt-export.zip"
    source = FIXTURES / "minimal" / "conversations.json"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("chat.html", "<html></html>")
        archive.writestr("conversations.json", source.read_text(encoding="utf-8"))

    result = load_conversations(archive_path)

    assert result.errors == []
    assert _only(result).provider_conv_id == "conv-minimal-1"


def test_load_conversations_from_split_zip(tmp_path: Path) -> None:
    archive_path = tmp_path / "chatgpt-split-export.zip"
    first = _minimal_record("conv-split-000", "Split zero", "first split record")
    second = _minimal_record("conv-split-001", "Split one", "second split record")
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("chat.html", "<html></html>")
        archive.writestr("conversations-001.json", json.dumps([second]))
        archive.writestr("conversations-000.json", json.dumps([first]))

    result = load_conversations(archive_path)

    assert result.errors == []
    assert [conversation.provider_conv_id for conversation in result.conversations] == [
        "conv-split-000",
        "conv-split-001",
    ]


def test_load_conversations_from_nested_zip(tmp_path: Path) -> None:
    archive_path = tmp_path / "nested-export.zip"
    source = FIXTURES / "minimal" / "conversations.json"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("export/conversations.json", source.read_text(encoding="utf-8"))

    result = load_conversations(archive_path)

    assert result.errors == []
    assert _only(result).provider_conv_id == "conv-minimal-1"


def test_conversations_json_is_preferred_over_split_members(tmp_path: Path) -> None:
    archive_path = tmp_path / "chatgpt-mixed-export.zip"
    canonical = _minimal_record("conv-canonical", "Canonical", "canonical record")
    split = _minimal_record("conv-split", "Split", "split record")
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("conversations-000.json", json.dumps([split]))
        archive.writestr("conversations.json", json.dumps([canonical]))

    result = load_conversations(archive_path)

    assert result.errors == []
    assert [conversation.provider_conv_id for conversation in result.conversations] == [
        "conv-canonical"
    ]


def test_load_conversations_from_split_directory(tmp_path: Path) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    first = _minimal_record("conv-dir-000", "Directory zero", "first directory record")
    second = _minimal_record("conv-dir-001", "Directory one", "second directory record")
    _write_json(nested / "conversations-001.json", [second])
    _write_json(nested / "conversations-000.json", [first])

    result = load_conversations(tmp_path)

    assert result.errors == []
    assert [conversation.provider_conv_id for conversation in result.conversations] == [
        "conv-dir-000",
        "conv-dir-001",
    ]


def test_load_conversations_from_direct_split_json_file(tmp_path: Path) -> None:
    split_path = tmp_path / "conversations-000.json"
    _write_json(
        split_path,
        [_minimal_record("conv-direct-split", "Direct split", "direct split record")],
    )

    result = load_conversations(split_path)

    assert result.errors == []
    assert _only(result).provider_conv_id == "conv-direct-split"


def test_malformed_split_member_reports_error_and_valid_members_still_parse(
    tmp_path: Path,
) -> None:
    valid = _minimal_record("conv-valid-split", "Valid split", "valid split record")
    _write_json(tmp_path / "conversations-000.json", [valid])
    _write_json(tmp_path / "conversations-001.json", {"not": "a list"})

    result = load_conversations(tmp_path)

    assert [conversation.provider_conv_id for conversation in result.conversations] == [
        "conv-valid-split"
    ]
    assert _error_codes(result) == {"unexpected_export_shape"}
    payload = [error.model_dump() for error in result.errors]
    assert json.loads(json.dumps(payload)) == payload


@pytest.mark.parametrize(
    ("factory", "expected_error"),
    [
        (lambda tmp: tmp / "missing.json", "source_not_found"),
        (lambda tmp: tmp, "conversations_json_not_found"),
    ],
)
def test_load_conversations_missing_sources_report_errors(
    tmp_path: Path,
    factory: object,
    expected_error: str,
) -> None:
    result = load_conversations(factory(tmp_path))  # type: ignore[operator]

    assert result.conversations == []
    assert _error_codes(result) == {expected_error}


def test_load_conversations_zip_without_conversations_json(tmp_path: Path) -> None:
    archive_path = tmp_path / "empty-export.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("chat.html", "<html></html>")

    result = load_conversations(archive_path)

    assert result.conversations == []
    assert _error_codes(result) == {"conversations_json_not_found"}


def test_load_conversations_invalid_json_is_reported(tmp_path: Path) -> None:
    bad = tmp_path / "conversations.json"
    bad.write_text("{not json", encoding="utf-8")

    result = load_conversations(bad)

    assert result.conversations == []
    assert _error_codes(result) == {"invalid_json"}
