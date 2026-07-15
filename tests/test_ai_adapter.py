from __future__ import annotations

import asyncio
import builtins
import sys
from types import SimpleNamespace

import pytest

from chat_chronicle.ai import CompletionRequest, LiteLLMClient, LLMError


def _request() -> CompletionRequest:
    return CompletionRequest(
        model="mock/model",
        messages=[{"role": "user", "content": "synthetic"}],
        response_schema={"type": "object", "required": ["result"]},
        enforce_schema=True,
        temperature=0,
        max_tokens=20,
        timeout=5,
        retries=1,
    )


def test_missing_optional_dependency_names_install_extra(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_import = builtins.__import__

    def importing(name, *args, **kwargs):
        if name == "litellm":
            raise ImportError("synthetic missing dependency")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", importing)
    with pytest.raises(LLMError, match="poetry install -E enrich") as caught:
        asyncio.run(LiteLLMClient().complete(_request()))
    assert caught.value.kind == "dependency"


def test_adapter_sends_json_schema_and_normalizes_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured = {}

    async def completion(**kwargs):
        captured.update(kwargs)
        message = SimpleNamespace(content='{"result":"ok"}')
        return SimpleNamespace(
            choices=[SimpleNamespace(message=message)],
            provider="mock-provider",
            model="mock-model",
            usage=SimpleNamespace(model_dump=lambda: {"total_tokens": 2}),
        )

    monkeypatch.setitem(sys.modules, "litellm", SimpleNamespace(acompletion=completion))
    result = asyncio.run(LiteLLMClient().complete(_request()))
    assert captured["response_format"]["type"] == "json_schema"
    assert captured["response_format"]["json_schema"]["schema"] == _request().response_schema
    assert captured["num_retries"] == 1
    assert captured["model"] == "mock/model"
    assert result.provider == "mock-provider"
    assert result.model == "mock-model"


def test_adapter_explicitly_degrades_when_profile_disables_schema_enforcement(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured = {}

    async def completion(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content='{"result":"ok"}'))],
            model="mock",
        )

    monkeypatch.setitem(sys.modules, "litellm", SimpleNamespace(acompletion=completion))
    request = _request()
    request = CompletionRequest(**{**request.__dict__, "enforce_schema": False})
    asyncio.run(LiteLLMClient().complete(request))
    assert captured["response_format"] == {"type": "json_object"}


@pytest.mark.parametrize(
    ("exception_name", "kind"),
    [
        ("TimeoutError", "timeout"),
        ("ConnectionError", "connection"),
        ("AuthenticationError", "authentication"),
        ("RateLimitError", "rate_limit"),
        ("UnexpectedError", "provider"),
    ],
)
def test_adapter_normalizes_provider_errors(
    monkeypatch: pytest.MonkeyPatch, exception_name: str, kind: str
) -> None:
    error_type = type(exception_name, (Exception,), {})

    async def completion(**kwargs):
        raise error_type("secret provider payload")

    monkeypatch.setitem(sys.modules, "litellm", SimpleNamespace(acompletion=completion))
    with pytest.raises(LLMError) as caught:
        asyncio.run(LiteLLMClient().complete(_request()))
    assert caught.value.kind == kind
    assert "secret provider payload" not in str(caught.value)


@pytest.mark.parametrize("content", ["", "   "])
def test_adapter_rejects_empty_completion(monkeypatch: pytest.MonkeyPatch, content: str) -> None:
    async def completion(**kwargs):
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=content))],
            model="mock",
        )

    monkeypatch.setitem(sys.modules, "litellm", SimpleNamespace(acompletion=completion))
    with pytest.raises(LLMError, match="empty"):
        asyncio.run(LiteLLMClient().complete(_request()))
