"""Provider abstraction for LLM backends."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Protocol

from flightrecorder.config import AppConfig, RoleConfig


@dataclass(frozen=True)
class Message:
    role: str
    content: str


class Provider(Protocol):
    name: str
    supports_images: bool
    max_context_tokens: int

    async def chat(
        self,
        messages: list[Message],
        system: str | None = None,
        stream: bool = True,
    ) -> AsyncIterator[str]:
        """Stream a provider response."""


class ProviderError(RuntimeError):
    """Raised when a provider call fails."""


@dataclass(frozen=True)
class ProviderDescriptor:
    supports_images: bool
    max_context_tokens: int


class ConfiguredProvider:
    """Configured provider shell used before paid API calls are implemented."""

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
        stream: bool = True,
    ) -> AsyncIterator[str]:
        if False:
            yield ""
        raise ProviderError(f"provider {self.name} chat is not implemented")

    @property
    def is_configured(self) -> bool:
        """Return whether this provider has a non-empty API key."""

        return bool(self._api_key)


PROVIDER_DESCRIPTORS = {
    "anthropic": ProviderDescriptor(supports_images=True, max_context_tokens=0),
    "google": ProviderDescriptor(supports_images=True, max_context_tokens=0),
    "openai": ProviderDescriptor(supports_images=True, max_context_tokens=0),
}


def create_provider(name: str, model: str, api_key: str) -> ConfiguredProvider:
    """Create a provider placeholder for a configured provider name."""

    try:
        descriptor = PROVIDER_DESCRIPTORS[name]
    except KeyError as exc:
        raise ProviderError(f"unknown provider {name}") from exc

    return ConfiguredProvider(
        name=name,
        model=model,
        api_key=api_key,
        supports_images=descriptor.supports_images,
        max_context_tokens=descriptor.max_context_tokens,
    )


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
