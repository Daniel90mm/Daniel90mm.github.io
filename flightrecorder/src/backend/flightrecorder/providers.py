"""Provider abstraction for LLM backends."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
import json
from typing import Any, Protocol

from flightrecorder.config import AppConfig, RoleConfig


@dataclass(frozen=True)
class Message:
    role: str
    content: str


@dataclass(frozen=True)
class TokenEvent:
    """One streamed text chunk from the provider."""

    text: str


@dataclass(frozen=True)
class UsageEvent:
    """Final token counts. Emitted once at the end of every successful stream."""

    input_tokens: int
    output_tokens: int
    cached_tokens: int = 0


ChatEvent = TokenEvent | UsageEvent


class Provider(Protocol):
    name: str
    model: str
    supports_images: bool
    max_context_tokens: int

    def chat(
        self,
        messages: list[Message],
        system: str | None = None,
    ) -> AsyncIterator[ChatEvent]:
        """Stream a provider response as TokenEvent... then one final UsageEvent."""


class ProviderError(RuntimeError):
    """Raised when a provider call fails."""


@dataclass(frozen=True)
class ProviderDescriptor:
    supports_images: bool
    max_context_tokens: int


class ConfiguredProvider:
    """Configured provider shell. Subclasses implement real chat streaming.

    The base class chat() raises ProviderError so an unconfigured provider
    cannot silently produce empty output. AnthropicChatProvider overrides it
    with real streaming against the anthropic SDK.
    """

    name: str
    model: str
    supports_images: bool
    max_context_tokens: int
    _api_key: str

    def __init__(
        self,
        name: str,
        model: str,
        api_key: str,
        supports_images: bool,
        max_context_tokens: int,
    ) -> None:
        self.name = name
        self.model = model
        self._api_key = api_key
        self.supports_images = supports_images
        self.max_context_tokens = max_context_tokens

    async def chat(
        self,
        messages: list[Message],
        system: str | None = None,
    ) -> AsyncIterator[ChatEvent]:
        if False:
            yield TokenEvent(text="")
        raise ProviderError(f"provider {self.name} chat is not implemented")

    @property
    def is_configured(self) -> bool:
        """Return whether this provider has a non-empty API key."""

        return bool(self._api_key)


class AnthropicChatProvider(ConfiguredProvider):
    """Streaming chat provider backed by the anthropic SDK.

    The client is injected at construction time so unit tests can pass a fake
    that mimics the real anthropic.AsyncAnthropic streaming surface without
    needing the real SDK or network. In production, _default_client() builds
    a real AsyncAnthropic from the configured API key.
    """

    _client: Any
    _max_tokens: int

    def __init__(
        self,
        model: str,
        api_key: str,
        supports_images: bool = True,
        max_context_tokens: int = 200_000,
        max_output_tokens: int = 4_096,
        client: Any | None = None,
    ) -> None:
        super().__init__(
            name="anthropic",
            model=model,
            api_key=api_key,
            supports_images=supports_images,
            max_context_tokens=max_context_tokens,
        )
        self._client = client if client is not None else _default_anthropic_client(api_key)
        self._max_tokens = max_output_tokens

    async def chat(
        self,
        messages: list[Message],
        system: str | None = None,
    ) -> AsyncIterator[ChatEvent]:
        if not self.is_configured:
            raise ProviderError("anthropic provider has no api key configured")
        for message in messages:
            if message.role not in {"user", "assistant"}:
                raise ProviderError(
                    f"anthropic role must be 'user' or 'assistant', got {message.role!r}"
                )

        request_messages = [
            {"role": message.role, "content": message.content} for message in messages
        ]
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": self._max_tokens,
            "messages": request_messages,
        }
        if system is not None:
            kwargs["system"] = system

        try:
            async with self._client.messages.stream(**kwargs) as stream:
                async for chunk in stream.text_stream:
                    yield TokenEvent(text=chunk)
                final = await stream.get_final_message()
        except ProviderError:
            raise
        except Exception as exc:  # provider SDK exceptions vary widely
            raise ProviderError(f"anthropic stream failed: {exc}") from exc

        usage = getattr(final, "usage", None)
        if usage is None:
            raise ProviderError("anthropic stream finished without usage info")
        cached = (
            getattr(usage, "cache_read_input_tokens", None)
            or getattr(usage, "cached_tokens", None)
            or 0
        )
        yield UsageEvent(
            input_tokens=int(getattr(usage, "input_tokens", 0)),
            output_tokens=int(getattr(usage, "output_tokens", 0)),
            cached_tokens=int(cached),
        )


class PrototypeProvider(ConfiguredProvider):
    """Deterministic local provider for offline dogfood demos.

    This is intentionally simple: no network, no secrets, and no hidden model
    behavior. It lets the browser MVP run end-to-end before paid providers are
    configured.
    """

    def __init__(self, model: str) -> None:
        super().__init__(
            name="prototype",
            model=model,
            api_key="prototype",
            supports_images=False,
            max_context_tokens=16_000,
        )

    async def chat(
        self,
        messages: list[Message],
        system: str | None = None,
    ) -> AsyncIterator[ChatEvent]:
        prompt = messages[-1].content.strip() if messages else ""
        if "idea-capture" in self.model or "idea_capture" in self.model:
            text = self._idea_capture_response(prompt)
        else:
            text = self._brainstorm_response(prompt)

        for index in range(0, len(text), 32):
            yield TokenEvent(text=text[index : index + 32])
        yield UsageEvent(
            input_tokens=max(1, len(prompt.split())),
            output_tokens=max(1, len(text.split())),
            cached_tokens=0,
        )

    def _brainstorm_response(self, prompt: str) -> str:
        topic = _summarize_prompt(prompt)
        return (
            "Prototype response: capture the main idea, decide whether it "
            f"belongs in a project note, and keep one loose follow-up about {topic}."
        )

    def _idea_capture_response(self, transcript: str) -> str:
        topic = _summarize_prompt(transcript)
        return json.dumps(
            [
                {
                    "type": "project_append",
                    "project_ref": "prototype",
                    "section": "Ideas",
                    "content": f"Prototype captured a project note about {topic}.",
                },
                {
                    "type": "spaghetti",
                    "tags": ["prototype"],
                    "topics": ["dogfood"],
                    "content": f"Loose follow-up from prototype session: {topic}.",
                },
            ]
        )


def _summarize_prompt(prompt: str) -> str:
    words = [word.strip(".,:;!?()[]{}\"'").lower() for word in prompt.split()]
    useful = [word for word in words if len(word) > 3]
    if not useful:
        return "the session"
    return " ".join(useful[:8])


def _default_anthropic_client(api_key: str) -> Any:
    """Build a real AsyncAnthropic client. Imported lazily so tests can skip the SDK."""

    from anthropic import AsyncAnthropic

    return AsyncAnthropic(api_key=api_key)


PROVIDER_DESCRIPTORS = {
    "anthropic": ProviderDescriptor(supports_images=True, max_context_tokens=200_000),
    "google": ProviderDescriptor(supports_images=True, max_context_tokens=0),
    "openai": ProviderDescriptor(supports_images=True, max_context_tokens=0),
    "prototype": ProviderDescriptor(supports_images=False, max_context_tokens=16_000),
}


def create_provider(name: str, model: str, api_key: str) -> ConfiguredProvider:
    """Create a configured provider by name."""

    try:
        descriptor = PROVIDER_DESCRIPTORS[name]
    except KeyError as exc:
        raise ProviderError(f"unknown provider {name}") from exc

    if name == "anthropic":
        return AnthropicChatProvider(
            model=model,
            api_key=api_key,
            supports_images=descriptor.supports_images,
            max_context_tokens=descriptor.max_context_tokens,
            client=_default_anthropic_client(api_key) if api_key else _UnconfiguredClient(),
        )
    if name == "prototype":
        return PrototypeProvider(model=model)

    return ConfiguredProvider(
        name=name,
        model=model,
        api_key=api_key,
        supports_images=descriptor.supports_images,
        max_context_tokens=descriptor.max_context_tokens,
    )


class _UnconfiguredClient:
    """Stand-in client used when no api key is configured.

    Lets AnthropicChatProvider construct cleanly so is_configured can be
    queried. Any actual chat() call fails closed via the api-key check.
    """

    class _Messages:
        @asynccontextmanager
        async def stream(self, **_: Any) -> AsyncIterator[Any]:
            raise ProviderError("anthropic provider has no api key configured")
            yield  # pragma: no cover

    messages = _Messages()


def create_role_provider(config: AppConfig, role_name: str) -> ConfiguredProvider:
    """Create the configured provider for one role."""

    try:
        role = config.roles[role_name]
    except KeyError as exc:
        raise ProviderError(f"unknown role {role_name}") from exc

    return create_provider_for_role(config, role)


def create_provider_for_role(
    config: AppConfig,
    role: RoleConfig,
) -> ConfiguredProvider:
    """Create a configured provider from a role config."""

    try:
        provider_config = config.providers[role.provider]
    except KeyError as exc:
        raise ProviderError(
            f"role provider {role.provider} is missing provider config"
        ) from exc

    return create_provider(
        name=role.provider,
        model=role.model,
        api_key=provider_config.api_key,
    )
