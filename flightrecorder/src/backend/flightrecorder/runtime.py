"""Runtime wiring for backend services."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import sqlite3

from flightrecorder.config import AppConfig, load_config_from_environment, parse_config
from flightrecorder.costs import PricingTable, ProviderCallGuard, load_pricing, parse_pricing
from flightrecorder.database import connect_metadata_db
from flightrecorder.providers import ConfiguredProvider, ProviderError, create_role_provider
from flightrecorder.storage import SessionStore
from flightrecorder.web_search import SearchClient, TavilySearchClient


@dataclass(frozen=True)
class RuntimeContext:
    config: AppConfig
    database: sqlite3.Connection
    sessions: SessionStore
    pricing: PricingTable
    brainstorm_provider: ConfiguredProvider
    idea_capture_provider: ConfiguredProvider
    search_client: SearchClient | None = None

    def guard(self) -> ProviderCallGuard:
        return ProviderCallGuard(
            runtime_home=self.config.paths.runtime_home,
            connection=self.database,
            pricing=self.pricing,
            warn_at_dkk=self.config.budget.warn_at_dkk,
            hard_stop_dkk=self.config.budget.hard_stop_dkk,
        )


def build_runtime_context(
    config: AppConfig | None = None,
    database: sqlite3.Connection | None = None,
) -> RuntimeContext:
    """Build runtime services for the backend app."""

    resolved_config = config or load_config_from_environment()
    runtime_home = resolved_config.paths.runtime_home
    resolved_database = database or connect_metadata_db(runtime_home)

    pricing_path = resolved_config.paths.pricing_path
    if pricing_path is None:
        pricing_path = runtime_home.parent / "pricing.toml"

    pricing = _load_pricing_safe(pricing_path)
    brainstorm = _create_role_safe(resolved_config, "brainstorm")
    idea_capture = _create_role_safe(resolved_config, "idea_capture")
    search_client = _create_search_client_safe()

    return RuntimeContext(
        config=resolved_config,
        database=resolved_database,
        sessions=SessionStore(runtime_home, resolved_database),
        pricing=pricing,
        brainstorm_provider=brainstorm,
        idea_capture_provider=idea_capture,
        search_client=search_client,
    )


def build_runtime_context_for_path(runtime_home: Path) -> RuntimeContext:
    """Build runtime services for a specific runtime home."""

    config = parse_config({"paths": {"runtime_home": str(runtime_home)}})
    return build_runtime_context(config)


def _load_pricing_safe(path: Path) -> PricingTable:
    """Load pricing from disk or return a zero-priced default for local tests."""

    if path.exists():
        return load_pricing(path)
    return parse_pricing({"models": {}})


def _create_role_safe(config: AppConfig, role_name: str) -> ConfiguredProvider:
    """Create a role provider, falling back to unconfigured if missing."""

    try:
        return create_role_provider(config, role_name)
    except ProviderError:
        return ConfiguredProvider(
            name="none",
            model="none",
            api_key="",
            supports_images=False,
            max_context_tokens=0,
        )


def _create_search_client_safe() -> SearchClient | None:
    """Create an optional search client from local environment."""

    api_key = os.environ.get("TAVILY_API_KEY", "").strip()
    if not api_key or "CHANGEME" in api_key:
        return None
    return TavilySearchClient(api_key=api_key)
