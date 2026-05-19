"""Smoke test: verify example config and pricing files are loadable and self-consistent."""

from __future__ import annotations

import sys
from pathlib import Path

from flightrecorder.config import load_config
from flightrecorder.costs import load_pricing

REPO = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = REPO / "config.example.toml"
PRICING_PATH = REPO / "pricing.example.toml"
PROTOTYPE_CONFIG_PATH = REPO / "config.prototype.toml"
PROTOTYPE_PRICING_PATH = REPO / "pricing.prototype.toml"


def main() -> None:
    config = load_config(CONFIG_PATH)
    pricing = load_pricing(PRICING_PATH)

    assert "brainstorm" in config.roles, "brainstorm role missing"
    assert "idea_capture" in config.roles, "idea_capture role missing"

    brainstorm = config.roles["brainstorm"]
    assert brainstorm.provider in config.providers, (
        f"brainstorm provider {brainstorm.provider} not in providers"
    )

    capture = config.roles["idea_capture"]
    assert capture.provider in config.providers, (
        f"idea_capture provider {capture.provider} not in providers"
    )

    assert brainstorm.model in pricing.models, (
        f"brainstorm model {brainstorm.model} not in pricing"
    )
    assert capture.model in pricing.models, (
        f"idea_capture model {capture.model} not in pricing"
    )

    assert config.paths.pricing_path is not None, (
        "pricing_path must be set in the example config"
    )

    pricing_model = pricing.models[brainstorm.model]
    assert pricing_model.provider == brainstorm.provider, (
        f"pricing provider {pricing_model.provider} != brainstorm provider {brainstorm.provider}"
    )

    prototype_config = load_config(PROTOTYPE_CONFIG_PATH)
    prototype_pricing = load_pricing(PROTOTYPE_PRICING_PATH)
    assert prototype_config.roles["brainstorm"].provider == "prototype"
    assert prototype_config.roles["idea_capture"].provider == "prototype"
    assert prototype_config.roles["brainstorm"].model in prototype_pricing.models
    assert prototype_config.roles["idea_capture"].model in prototype_pricing.models

    print("example config and pricing smoke test passed")


if __name__ == "__main__":
    main()
