"""Configuration loading for flightrecorder."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import os
import tomllib


CONFIG_ENV_VAR = "FLIGHTRECORDER_CONFIG"
DEFAULT_CONFIG_PATH = "~/flightrecorder/config.toml"


@dataclass(frozen=True)
class ProviderConfig:
    name: str
    api_key: str


@dataclass(frozen=True)
class RoleConfig:
    provider: str
    model: str


@dataclass(frozen=True)
class BudgetConfig:
    warn_at_eur: float
    hard_stop_eur: float
    currency: str


@dataclass(frozen=True)
class PathConfig:
    runtime_home: Path
    hugo_site: Path
    pricing_path: Path | None = None


@dataclass(frozen=True)
class AppConfig:
    providers: dict[str, ProviderConfig]
    roles: dict[str, RoleConfig]
    budget: BudgetConfig
    paths: PathConfig


def expand_path(value: str) -> Path:
    """Expand environment variables and home markers in a config path."""

    return Path(os.path.expandvars(os.path.expanduser(value)))


def load_config(path: Path) -> AppConfig:
    """Load a TOML config file."""

    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return parse_config(data)


def config_path_from_environment(
    environment: Mapping[str, str] | None = None,
) -> Path:
    """Resolve the config path from environment variables."""

    resolved_environment = environment if environment is not None else os.environ
    return expand_path(resolved_environment.get(CONFIG_ENV_VAR, DEFAULT_CONFIG_PATH))


def load_config_from_environment(
    environment: Mapping[str, str] | None = None,
    required: bool = False,
) -> AppConfig:
    """Load config from FLIGHTRECORDER_CONFIG or the default runtime path."""

    path = config_path_from_environment(environment)
    if path.exists():
        return load_config(path)
    if required:
        raise FileNotFoundError(f"config file not found: {path}")
    return parse_config({})


def parse_config(data: dict[str, Any]) -> AppConfig:
    """Parse already-loaded TOML data into typed config objects."""

    providers = {
        name: ProviderConfig(name=name, api_key=str(values.get("api_key", "")))
        for name, values in data.get("providers", {}).items()
    }
    roles = {
        name: RoleConfig(provider=str(values["provider"]), model=str(values["model"]))
        for name, values in data.get("roles", {}).items()
    }

    budget_data = data.get("budget", {})
    budget = BudgetConfig(
        warn_at_eur=float(budget_data.get("warn_at_eur", 30)),
        hard_stop_eur=float(budget_data.get("hard_stop_eur", 80)),
        currency=str(budget_data.get("currency", "EUR")),
    )

    paths_data = data.get("paths", {})
    runtime_home = expand_path(str(paths_data.get("runtime_home", "~/flightrecorder")))
    hugo_site = expand_path(str(paths_data.get("hugo_site", "~/hugo-site")))
    pricing_raw = paths_data.get("pricing_path")
    pricing_path = expand_path(str(pricing_raw)) if pricing_raw else None
    paths = PathConfig(runtime_home=runtime_home, hugo_site=hugo_site, pricing_path=pricing_path)

    return AppConfig(providers=providers, roles=roles, budget=budget, paths=paths)
