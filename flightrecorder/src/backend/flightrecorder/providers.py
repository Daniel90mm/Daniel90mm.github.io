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
    tool_calls: tuple[dict, ...] = ()
    tool_call_id: str | None = None
    name: str | None = None


@dataclass(frozen=True)
class TokenEvent:
    """One streamed text chunk from the provider."""

    text: str


@dataclass(frozen=True)
class ToolCallEvent:
    """One complete tool call requested by the model in this turn."""

    id: str
    name: str
    arguments: str


@dataclass(frozen=True)
class UsageEvent:
    """Final token counts. Emitted once at the end of every successful stream."""

    input_tokens: int
    output_tokens: int
    cached_tokens: int = 0


ChatEvent = TokenEvent | UsageEvent | ToolCallEvent


class Provider(Protocol):
    name: str
    model: str
    supports_images: bool
    max_context_tokens: int

    def chat(
        self,
        messages: list[Message],
        system: str | None = None,
        tools: list[dict] | None = None,
    ) -> AsyncIterator[ChatEvent]:
        """Stream a provider response as TokenEvent... then one final UsageEvent.

        When tools is provided, ToolCallEvents may also be yielded for any
        function calls the model requests before the UsageEvent.
        """


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
        tools: list[dict] | None = None,
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
        tools: list[dict] | None = None,
    ) -> AsyncIterator[ChatEvent]:
        if not self.is_configured:
            raise ProviderError("anthropic provider has no api key configured")
        if tools:
            # TODO: implement anthropic tool_use/tool_result content blocks.
            # DeepSeek is the default brainstorm provider, so this is deferred.
            raise NotImplementedError(
                "anthropic provider does not yet support web_search tool calling"
            )
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


class OpenAICompatibleChatProvider(ConfiguredProvider):
    """Streaming chat provider for OpenAI-compatible chat completions APIs."""

    _client: Any

    def __init__(
        self,
        name: str,
        model: str,
        api_key: str,
        base_url: str | None = None,
        supports_images: bool = True,
        max_context_tokens: int = 128_000,
        client: Any | None = None,
    ) -> None:
        super().__init__(
            name=name,
            model=model,
            api_key=api_key,
            supports_images=supports_images,
            max_context_tokens=max_context_tokens,
        )
        self._client = (
            client
            if client is not None
            else _default_openai_compatible_client(api_key=api_key, base_url=base_url)
        )

    async def chat(
        self,
        messages: list[Message],
        system: str | None = None,
        tools: list[dict] | None = None,
    ) -> AsyncIterator[ChatEvent]:
        if not self.is_configured:
            raise ProviderError(f"{self.name} provider has no api key configured")

        request_messages: list[dict[str, Any]] = []
        if system is not None:
            request_messages.append({"role": "system", "content": system})
        for message in messages:
            if message.role not in {"user", "assistant", "system", "tool"}:
                raise ProviderError(
                    f"{self.name} role must be user, assistant, system, or tool, "
                    f"got {message.role!r}"
                )
            if message.role == "tool":
                if message.tool_call_id is None:
                    raise ProviderError(
                        f"{self.name} tool message requires tool_call_id"
                    )
                tool_entry: dict[str, Any] = {
                    "role": "tool",
                    "content": message.content,
                    "tool_call_id": message.tool_call_id,
                }
                if message.name is not None:
                    tool_entry["name"] = message.name
                request_messages.append(tool_entry)
            elif message.role == "assistant" and message.tool_calls:
                assistant_entry: dict[str, Any] = {
                    "role": "assistant",
                    "content": message.content or None,
                    "tool_calls": [dict(call) for call in message.tool_calls],
                }
                request_messages.append(assistant_entry)
            else:
                request_messages.append(
                    {"role": message.role, "content": message.content}
                )

        create_kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": request_messages,
            "stream": True,
            "stream_options": {"include_usage": True},
        }
        if tools is not None:
            create_kwargs["tools"] = tools

        # Accumulate streamed tool_call deltas keyed by index. Each delta may
        # carry partial fields (id and function.name typically arrive on the
        # first chunk for that index; function.arguments is incremental).
        tool_call_accumulator: dict[int, dict[str, str]] = {}

        try:
            stream = await self._client.chat.completions.create(**create_kwargs)
            usage: Any | None = None
            async for chunk in stream:
                usage = getattr(chunk, "usage", None) or usage
                choices = getattr(chunk, "choices", None) or []
                if not choices:
                    continue
                delta = getattr(choices[0], "delta", None)
                content = getattr(delta, "content", None)
                if content:
                    yield TokenEvent(text=str(content))
                delta_tool_calls = getattr(delta, "tool_calls", None) or []
                for delta_call in delta_tool_calls:
                    index = getattr(delta_call, "index", 0) or 0
                    slot = tool_call_accumulator.setdefault(
                        int(index),
                        {"id": "", "name": "", "arguments": ""},
                    )
                    call_id = getattr(delta_call, "id", None)
                    if call_id:
                        slot["id"] = str(call_id)
                    function = getattr(delta_call, "function", None)
                    if function is not None:
                        fn_name = getattr(function, "name", None)
                        if fn_name:
                            slot["name"] = str(fn_name)
                        fn_args = getattr(function, "arguments", None)
                        if fn_args:
                            slot["arguments"] += str(fn_args)
        except ProviderError:
            raise
        except Exception as exc:
            raise ProviderError(f"{self.name} stream failed: {exc}") from exc

        if usage is None:
            raise ProviderError(f"{self.name} stream finished without usage info")

        for index in sorted(tool_call_accumulator.keys()):
            slot = tool_call_accumulator[index]
            if not slot["id"] or not slot["name"]:
                continue
            yield ToolCallEvent(
                id=slot["id"],
                name=slot["name"],
                arguments=slot["arguments"],
            )

        cached = (
            getattr(usage, "prompt_cache_hit_tokens", None)
            or getattr(usage, "cached_tokens", None)
            or 0
        )
        yield UsageEvent(
            input_tokens=int(getattr(usage, "prompt_tokens", 0)),
            output_tokens=int(getattr(usage, "completion_tokens", 0)),
            cached_tokens=int(cached),
        )


class DeepSeekChatProvider(OpenAICompatibleChatProvider):
    """DeepSeek provider via its OpenAI-compatible chat completions API."""

    def __init__(
        self,
        model: str,
        api_key: str,
        client: Any | None = None,
    ) -> None:
        super().__init__(
            name="deepseek",
            model=model,
            api_key=api_key,
            base_url="https://api.deepseek.com",
            supports_images=False,
            max_context_tokens=64_000,
            client=client,
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
        tools: list[dict] | None = None,
    ) -> AsyncIterator[ChatEvent]:
        del tools  # prototype ignores tool calling
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


def _default_openai_compatible_client(api_key: str, base_url: str | None = None) -> Any:
    """Build an AsyncOpenAI client. Imported lazily so tests can inject fakes."""

    from openai import AsyncOpenAI

    kwargs: dict[str, Any] = {"api_key": api_key}
    if base_url is not None:
        kwargs["base_url"] = base_url
    return AsyncOpenAI(**kwargs)


PROVIDER_DESCRIPTORS = {
    "anthropic": ProviderDescriptor(supports_images=True, max_context_tokens=200_000),
    "deepseek": ProviderDescriptor(supports_images=False, max_context_tokens=64_000),
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
    if name == "deepseek":
        provider = DeepSeekChatProvider(
            model=model,
            api_key=api_key,
            client=None if api_key else _UnconfiguredOpenAICompatibleClient(name),
        )
        return provider

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


class _UnconfiguredOpenAICompatibleClient:
    """Stand-in OpenAI-compatible client used when no api key is configured."""

    def __init__(self, provider_name: str) -> None:
        self.chat = self._Chat(provider_name)

    class _Chat:
        def __init__(self, provider_name: str) -> None:
            self.completions = _UnconfiguredOpenAICompatibleClient._Completions(
                provider_name
            )

    class _Completions:
        def __init__(self, provider_name: str) -> None:
            self._provider_name = provider_name

        async def create(self, **_: Any) -> Any:
            raise ProviderError(f"{self._provider_name} provider has no api key configured")


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
