import asyncio

import pytest

from flightrecorder.providers import (
    ConfiguredProvider,
    Message,
    ProviderError,
    create_provider,
    create_role_provider,
)
from flightrecorder.config import parse_config


def test_configured_provider_shell_raises() -> None:
    provider = ConfiguredProvider(
        name="anthropic",
        model="claude-haiku-4-5",
        api_key="test-key",
        supports_images=True,
        max_context_tokens=200000,
    )

    with pytest.raises(ProviderError):
        asyncio.run(_read_first_chunk(provider))


async def _read_first_chunk(provider: ConfiguredProvider) -> None:
    chunks = provider.chat([Message(role="user", content="hello")])
    await anext(chunks)


def test_create_provider_descriptors() -> None:
    anthropic = create_provider("anthropic", "claude-haiku-4-5", "test-key")
    google = create_provider("google", "gemini-2.5-pro", "test-key")
    openai = create_provider("openai", "gpt-5-mini", "test-key")

    assert anthropic.supports_images is True
    assert anthropic.model == "claude-haiku-4-5"
    assert anthropic.is_configured is True
    assert google.supports_images is True
    assert google.max_context_tokens == 0
    assert openai.name == "openai"


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
