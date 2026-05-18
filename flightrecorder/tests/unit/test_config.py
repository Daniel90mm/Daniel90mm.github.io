from pathlib import Path

import pytest

from flightrecorder.config import (
    CONFIG_ENV_VAR,
    config_path_from_environment,
    load_config,
    load_config_from_environment,
    parse_config,
)

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "config"


def test_parse_config_defaults_paths_and_budget() -> None:
    config = parse_config({})

    assert config.budget.warn_at_eur == 30
    assert config.budget.hard_stop_eur == 80
    assert config.budget.currency == "EUR"
    assert config.paths.runtime_home == Path.home() / "flightrecorder"
    assert config.paths.hugo_site == Path.home() / "hugo-site"


def test_parse_config_roles_and_providers() -> None:
    config = parse_config(
        {
            "providers": {
                "anthropic": {"api_key": "test-anthropic-key"},
            },
            "roles": {
                "tagger": {"provider": "anthropic", "model": "claude-haiku-4-5"},
            },
            "budget": {"warn_at_eur": 12, "hard_stop_eur": 34, "currency": "EUR"},
            "paths": {
                "runtime_home": "~/flightrecorder",
                "hugo_site": "~/hugo-site",
            },
        }
    )

    assert config.providers["anthropic"].api_key == "test-anthropic-key"
    assert config.roles["tagger"].provider == "anthropic"
    assert config.roles["tagger"].model == "claude-haiku-4-5"
    assert config.budget.hard_stop_eur == 34
    assert config.paths.runtime_home == Path.home() / "flightrecorder"


def test_config_path_from_environment_uses_explicit_path(tmp_path: Path) -> None:
    path = tmp_path / "config.toml"

    assert config_path_from_environment({CONFIG_ENV_VAR: str(path)}) == path


def test_load_config_from_environment_returns_defaults_when_missing() -> None:
    config = load_config_from_environment({}, required=False)

    assert config.paths.runtime_home == Path.home() / "flightrecorder"


def test_load_config_from_environment_can_require_file(tmp_path: Path) -> None:
    missing = tmp_path / "missing.toml"

    with pytest.raises(FileNotFoundError):
        load_config_from_environment({CONFIG_ENV_VAR: str(missing)}, required=True)


def test_load_config_from_environment_reads_file(tmp_path: Path) -> None:
    path = tmp_path / "config.toml"
    path.write_text(
        """
        [providers.google]
        api_key = "test-google-key"
        """,
        encoding="utf-8",
    )

    config = load_config_from_environment({CONFIG_ENV_VAR: str(path)})

    assert config.providers["google"].api_key == "test-google-key"


def test_load_config_reads_minimal_fixture() -> None:
    config = load_config(FIXTURES_DIR / "minimal.toml")

    assert config.budget.warn_at_eur == 30
    assert config.budget.hard_stop_eur == 10
    assert config.budget.currency == "EUR"
    assert config.providers == {}
    assert config.roles == {}


def test_load_config_reads_full_fixture() -> None:
    config = load_config(FIXTURES_DIR / "full.toml")

    assert config.providers["anthropic"].api_key == "test-anthropic-key"
    assert config.providers["openai"].api_key == "test-openai-key"
    assert config.providers["google"].api_key == "test-google-key"
    assert config.roles["brainstorm"].provider == "google"
    assert config.roles["brainstorm"].model == "gemini-2.5-pro"
    assert config.roles["reviewer"].provider == "openai"
    assert config.roles["reviewer"].model == "gpt-5-mini"
    assert config.budget.hard_stop_eur == 80
    assert config.paths.runtime_home == Path.home() / "flightrecorder"
    assert config.paths.hugo_site == Path.home() / "hugo-site"


def test_parse_config_preserves_budget_thresholds_without_ordering_validation() -> None:
    """Config parsing does not currently validate that warn <= hard_stop.
    That validation lives in costs.evaluate_budget."""
    config = parse_config(
        {
            "budget": {
                "warn_at_eur": 90,
                "hard_stop_eur": 50,
                "currency": "EUR",
            }
        }
    )

    assert config.budget.warn_at_eur == 90
    assert config.budget.hard_stop_eur == 50


def test_parse_config_accepts_zero_budget_thresholds() -> None:
    config = parse_config(
        {
            "budget": {
                "warn_at_eur": 0,
                "hard_stop_eur": 0,
                "currency": "EUR",
            }
        }
    )

    assert config.budget.warn_at_eur == 0
    assert config.budget.hard_stop_eur == 0


def test_parse_config_defaults_currency_to_eur_when_absent() -> None:
    config = parse_config({"budget": {"warn_at_eur": 5, "hard_stop_eur": 10}})

    assert config.budget.currency == "EUR"
