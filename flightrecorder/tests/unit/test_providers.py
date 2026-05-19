import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any

import pytest

from flightrecorder.config import parse_config
from flightrecorder.providers import (
    AnthropicChatProvider,
    ConfiguredProvider,
    Message,
    ProviderError,
    PrototypeProvider,
    TokenEvent,
    UsageEvent,
    create_provider,
    create_role_provider,
)


def test_configured_provider_shell_raises() -> None:
    provider = ConfiguredProvider(
        name="google",
        model="gemini-2.5-pro",
        api_key="test-key",
        supports_images=True,
        max_context_tokens=200000,
    )

    with pytest.raises(ProviderError):
        asyncio.run(_drain(provider))


async def _drain(provider: ConfiguredProvider) -> list[Any]:
    return [event async for event in provider.chat([Message(role="user", content="hi")])]


def test_create_provider_descriptors() -> None:
    anthropic = create_provider("anthropic", "claude-haiku-4-5", "test-key")
    google = create_provider("google", "gemini-2.5-pro", "test-key")
    openai = create_provider("openai", "gpt-5-mini", "test-key")
    prototype = create_provider("prototype", "prototype-brainstorm", "")

    assert isinstance(anthropic, AnthropicChatProvider)
    assert anthropic.supports_images is True
    assert anthropic.model == "claude-haiku-4-5"
    assert anthropic.is_configured is True
    assert google.supports_images is True
    assert google.max_context_tokens == 0
    assert openai.name == "openai"
    assert isinstance(prototype, PrototypeProvider)
    assert prototype.is_configured is True
    assert prototype.supports_images is False


def test_create_provider_rejects_unknown_provider() -> None:
    with pytest.raises(ProviderError):
        create_provider("local-llama", "local-model", "test-key")


def test_create_role_provider_uses_role_model_and_provider_key() -> None:
    config = parse_config(
        {
            "providers": {
                "anthropic": {"api_key": "test-anthropic-key"},
            },
            "roles": {
                "tagger": {"provider": "anthropic", "model": "claude-haiku-4-5"},
            },
        }
    )

    provider = create_role_provider(config, "tagger")

    assert provider.name == "anthropic"
    assert provider.model == "claude-haiku-4-5"
    assert provider.is_configured is True


def test_create_role_provider_rejects_missing_provider_config() -> None:
    config = parse_config(
        {
            "roles": {
                "tagger": {"provider": "anthropic", "model": "claude-haiku-4-5"},
            },
        }
    )

    with pytest.raises(ProviderError):
        create_role_provider(config, "tagger")


# --- AnthropicChatProvider streaming, against a fake client ---


@dataclass
class _FakeUsage:
    input_tokens: int
    output_tokens: int
    cache_read_input_tokens: int = 0


@dataclass
class _FakeFinalMessage:
    usage: _FakeUsage


class _FakeStream:
    """Minimal stand-in for the anthropic streaming response."""

    def __init__(
        self,
        chunks: list[str],
        usage: _FakeUsage,
        captured_kwargs: dict[str, Any],
        kwargs: dict[str, Any],
        raise_during: BaseException | None = None,
    ) -> None:
        self._chunks = chunks
        self._usage = usage
        self._raise_during = raise_during
        captured_kwargs.update(kwargs)

    async def __aenter__(self) -> "_FakeStream":
        return self

    async def __aexit__(self, *_: object) -> None:
        return None

    @property
    def text_stream(self) -> AsyncIterator[str]:
        return self._iter_chunks()

    async def _iter_chunks(self) -> AsyncIterator[str]:
        for chunk in self._chunks:
            if self._raise_during is not None:
                raise self._raise_during
            yield chunk

    async def get_final_message(self) -> _FakeFinalMessage:
        return _FakeFinalMessage(usage=self._usage)


class _FakeMessages:
    def __init__(
        self,
        chunks: list[str],
        usage: _FakeUsage,
        captured_kwargs: dict[str, Any],
        raise_during: BaseException | None = None,
    ) -> None:
        self._chunks = chunks
        self._usage = usage
        self._captured = captured_kwargs
        self._raise_during = raise_during

    def stream(self, **kwargs: Any) -> _FakeStream:
        return _FakeStream(
            self._chunks,
            self._usage,
            self._captured,
            kwargs,
            self._raise_during,
        )


@dataclass
class _FakeAnthropicClient:
    messages: _FakeMessages


def _make_provider(
    chunks: list[str],
    usage: _FakeUsage,
    captured: dict[str, Any] | None = None,
    raise_during: BaseException | None = None,
) -> tuple[AnthropicChatProvider, dict[str, Any]]:
    captured_kwargs = captured if captured is not None else {}
    client = _FakeAnthropicClient(
        messages=_FakeMessages(chunks, usage, captured_kwargs, raise_during)
    )
    provider = AnthropicChatProvider(
        model="claude-haiku-4-5-20251001",
        api_key="test-key",
        client=client,
    )
    return provider, captured_kwargs


def test_anthropic_provider_streams_tokens_then_usage() -> None:
    captured: dict[str, Any] = {}
    provider, kwargs = _make_provider(
        chunks=["Hello", " ", "world"],
        usage=_FakeUsage(input_tokens=12, output_tokens=3, cache_read_input_tokens=5),
        captured=captured,
    )

    events = asyncio.run(
        _drain_chat(
            provider,
            [Message(role="user", content="hi there")],
            system="be brief",
        )
    )

    assert events[:-1] == [
        TokenEvent(text="Hello"),
        TokenEvent(text=" "),
        TokenEvent(text="world"),
    ]
    final = events[-1]
    assert isinstance(final, UsageEvent)
    assert final.input_tokens == 12
    assert final.output_tokens == 3
    assert final.cached_tokens == 5

    assert kwargs["model"] == "claude-haiku-4-5-20251001"
    assert kwargs["system"] == "be brief"
    assert kwargs["messages"] == [{"role": "user", "content": "hi there"}]


def test_anthropic_provider_omits_system_when_none() -> None:
    captured: dict[str, Any] = {}
    provider, kwargs = _make_provider(
        chunks=["x"],
        usage=_FakeUsage(input_tokens=1, output_tokens=1),
        captured=captured,
    )

    asyncio.run(_drain_chat(provider, [Message(role="user", content="hi")]))

    assert "system" not in kwargs


def test_anthropic_provider_rejects_unknown_role() -> None:
    provider, _ = _make_provider(
        chunks=[],
        usage=_FakeUsage(input_tokens=0, output_tokens=0),
    )

    with pytest.raises(ProviderError):
        asyncio.run(_drain_chat(provider, [Message(role="system", content="oops")]))


def test_anthropic_provider_wraps_sdk_exceptions() -> None:
    provider, _ = _make_provider(
        chunks=["partial"],
        usage=_FakeUsage(input_tokens=1, output_tokens=1),
        raise_during=RuntimeError("simulated 429"),
    )

    with pytest.raises(ProviderError, match="anthropic stream failed"):
        asyncio.run(_drain_chat(provider, [Message(role="user", content="hi")]))


def test_anthropic_provider_without_api_key_fails_closed() -> None:
    config = parse_config(
        {
            "providers": {"anthropic": {"api_key": ""}},
            "roles": {
                "brainstorm": {"provider": "anthropic", "model": "claude-haiku-4-5"},
            },
        }
    )
    provider = create_role_provider(config, "brainstorm")

    assert provider.is_configured is False
    with pytest.raises(ProviderError):
        asyncio.run(_drain_chat(provider, [Message(role="user", content="hi")]))


def test_prototype_provider_streams_deterministic_brainstorm_response() -> None:
    provider = create_provider("prototype", "prototype-brainstorm", "")

    events = asyncio.run(
        _drain_chat(provider, [Message(role="user", content="Build the MVP loop")])
    )

    text = "".join(event.text for event in events if isinstance(event, TokenEvent))
    assert "Prototype response" in text
    assert isinstance(events[-1], UsageEvent)


def test_prototype_provider_can_emit_idea_capture_json() -> None:
    provider = create_provider("prototype", "prototype-idea-capture", "")

    events = asyncio.run(
        _drain_chat(provider, [Message(role="user", content="## user\nBuild visible MVP")])
    )

    text = "".join(event.text for event in events if isinstance(event, TokenEvent))
    assert '"type": "project_append"' in text
    assert '"type": "spaghetti"' in text
    assert isinstance(events[-1], UsageEvent)


async def _drain_chat(
    provider: ConfiguredProvider,
    messages: list[Message],
    system: str | None = None,
) -> list[Any]:
    return [event async for event in provider.chat(messages, system=system)]
