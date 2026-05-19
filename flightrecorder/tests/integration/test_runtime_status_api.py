"""Integration tests for GET /api/runtime provider status endpoint."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from flightrecorder.app import create_app
from flightrecorder.config import parse_config
from flightrecorder.costs import ModelPricing, PricingTable
from flightrecorder.runtime import build_runtime_context


def make_app(tmp_path: Path) -> TestClient:
    config = parse_config({"paths": {"runtime_home": str(tmp_path)}})
    runtime = build_runtime_context(config)
    app = create_app(config=config, runtime=runtime)
    return TestClient(app)


def test_runtime_status_no_roles_configured(tmp_path: Path) -> None:
    client = make_app(tmp_path)

    response = client.get("/api/runtime")
    assert response.status_code == 200
    body = response.json()

    assert "runtime_home" in body
    assert body["runtime_home"] == str(tmp_path)

    assert "roles" in body
    assert "brainstorm" in body["roles"]
    assert "idea_capture" in body["roles"]

    brainstorm = body["roles"]["brainstorm"]
    assert brainstorm["configured"] is False
    assert brainstorm["provider"] == "none"
    assert brainstorm["issues"] == ["role_missing"]

    capture = body["roles"]["idea_capture"]
    assert capture["configured"] is False
    assert capture["provider"] == "none"
    assert capture["issues"] == ["role_missing"]


def test_runtime_status_with_role_config(tmp_path: Path) -> None:
    config = parse_config(
        {
            "paths": {"runtime_home": str(tmp_path)},
            "providers": {"anthropic": {"api_key": "sk-test"}},
            "roles": {
                "brainstorm": {"provider": "anthropic", "model": "test-model"},
                "idea_capture": {"provider": "anthropic", "model": "test-model"},
            },
        }
    )
    runtime = build_runtime_context(config)
    pricing = PricingTable(
        models={
            "test-model": ModelPricing(
                provider="anthropic",
                model="test-model",
                input_per_1k=0.01,
                output_per_1k=0.03,
                cached_per_1k=0.0,
                currency="DKK",
            )
        },
        exchange_rates_to_dkk={"DKK": 1.0},
    )
    object.__setattr__(runtime, "pricing", pricing)
    app = create_app(config=config, runtime=runtime)
    client = TestClient(app)

    response = client.get("/api/runtime")
    assert response.status_code == 200
    body = response.json()

    brainstorm = body["roles"]["brainstorm"]
    assert brainstorm["configured"] is True
    assert brainstorm["provider"] == "anthropic"
    assert brainstorm["model"] == "test-model"
    assert brainstorm["issues"] == []

    capture = body["roles"]["idea_capture"]
    assert capture["configured"] is True
    assert capture["provider"] == "anthropic"
    assert capture["model"] == "test-model"
    assert capture["issues"] == []


def test_runtime_status_provider_mismatch(tmp_path: Path) -> None:
    config = parse_config(
        {
            "paths": {"runtime_home": str(tmp_path)},
            "providers": {"anthropic": {"api_key": "sk-test"}},
            "roles": {
                "brainstorm": {"provider": "anthropic", "model": "test-model"},
            },
        }
    )
    runtime = build_runtime_context(config)
    pricing = PricingTable(
        models={
            "test-model": ModelPricing(
                provider="wrongprov",
                model="test-model",
                input_per_1k=0.01,
                output_per_1k=0.03,
                cached_per_1k=0.0,
                currency="DKK",
            )
        },
        exchange_rates_to_dkk={"DKK": 1.0},
    )
    object.__setattr__(runtime, "pricing", pricing)
    app = create_app(config=config, runtime=runtime)
    client = TestClient(app)

    response = client.get("/api/runtime")
    assert response.status_code == 200
    body = response.json()

    brainstorm = body["roles"]["brainstorm"]
    assert brainstorm["configured"] is False
    assert brainstorm["issues"] == ["pricing_provider_mismatch"]


def test_runtime_status_rejects_placeholder_api_key(tmp_path: Path) -> None:
    config = parse_config(
        {
            "paths": {"runtime_home": str(tmp_path)},
            "providers": {"anthropic": {"api_key": "sk-ant-api03-CHANGEME"}},
            "roles": {
                "brainstorm": {"provider": "anthropic", "model": "test-model"},
            },
        }
    )
    runtime = build_runtime_context(config)
    pricing = PricingTable(
        models={
            "test-model": ModelPricing(
                provider="anthropic",
                model="test-model",
                input_per_1k=0.01,
                output_per_1k=0.03,
                cached_per_1k=0.0,
                currency="DKK",
            )
        },
        exchange_rates_to_dkk={"DKK": 1.0},
    )
    object.__setattr__(runtime, "pricing", pricing)
    app = create_app(config=config, runtime=runtime)
    client = TestClient(app)

    response = client.get("/api/runtime")
    assert response.status_code == 200
    brainstorm = response.json()["roles"]["brainstorm"]
    assert brainstorm["configured"] is False
    assert brainstorm["issues"] == ["api_key_missing"]


def test_runtime_status_rejects_unimplemented_provider_for_now(tmp_path: Path) -> None:
    config = parse_config(
        {
            "paths": {"runtime_home": str(tmp_path)},
            "providers": {"openai": {"api_key": "sk-test"}},
            "roles": {
                "brainstorm": {"provider": "openai", "model": "test-model"},
            },
        }
    )
    runtime = build_runtime_context(config)
    pricing = PricingTable(
        models={
            "test-model": ModelPricing(
                provider="openai",
                model="test-model",
                input_per_1k=0.01,
                output_per_1k=0.03,
                cached_per_1k=0.0,
                currency="DKK",
            )
        },
        exchange_rates_to_dkk={"DKK": 1.0},
    )
    object.__setattr__(runtime, "pricing", pricing)
    app = create_app(config=config, runtime=runtime)
    client = TestClient(app)

    response = client.get("/api/runtime")
    assert response.status_code == 200
    brainstorm = response.json()["roles"]["brainstorm"]
    assert brainstorm["configured"] is False
    assert brainstorm["issues"] == ["provider_not_implemented"]


def test_runtime_status_accepts_deepseek_provider(tmp_path: Path) -> None:
    config = parse_config(
        {
            "paths": {"runtime_home": str(tmp_path)},
            "providers": {"deepseek": {"api_key": "sk-test"}},
            "roles": {
                "brainstorm": {"provider": "deepseek", "model": "deepseek-chat"},
                "idea_capture": {"provider": "deepseek", "model": "deepseek-chat"},
            },
        }
    )
    runtime = build_runtime_context(config)
    pricing = PricingTable(
        models={
            "deepseek-chat": ModelPricing(
                provider="deepseek",
                model="deepseek-chat",
                input_per_1k=0.01,
                output_per_1k=0.03,
                cached_per_1k=0.0,
                currency="DKK",
            )
        },
        exchange_rates_to_dkk={"DKK": 1.0},
    )
    object.__setattr__(runtime, "pricing", pricing)
    app = create_app(config=config, runtime=runtime)
    client = TestClient(app)

    response = client.get("/api/runtime")
    assert response.status_code == 200
    body = response.json()
    assert body["roles"]["brainstorm"]["configured"] is True
    assert body["roles"]["brainstorm"]["issues"] == []
    assert body["roles"]["idea_capture"]["configured"] is True
    assert body["roles"]["idea_capture"]["issues"] == []


def test_runtime_status_accepts_prototype_provider_without_api_key(tmp_path: Path) -> None:
    config = parse_config(
        {
            "paths": {"runtime_home": str(tmp_path)},
            "providers": {"prototype": {}},
            "roles": {
                "brainstorm": {"provider": "prototype", "model": "prototype-brainstorm"},
                "idea_capture": {"provider": "prototype", "model": "prototype-idea-capture"},
            },
        }
    )
    runtime = build_runtime_context(config)
    pricing = PricingTable(
        models={
            "prototype-brainstorm": ModelPricing(
                provider="prototype",
                model="prototype-brainstorm",
                input_per_1k=0.0,
                output_per_1k=0.0,
                cached_per_1k=0.0,
                currency="DKK",
            ),
            "prototype-idea-capture": ModelPricing(
                provider="prototype",
                model="prototype-idea-capture",
                input_per_1k=0.0,
                output_per_1k=0.0,
                cached_per_1k=0.0,
                currency="DKK",
            ),
        },
        exchange_rates_to_dkk={"DKK": 1.0},
    )
    object.__setattr__(runtime, "pricing", pricing)
    app = create_app(config=config, runtime=runtime)
    client = TestClient(app)

    response = client.get("/api/runtime")
    assert response.status_code == 200
    body = response.json()
    assert body["roles"]["brainstorm"]["configured"] is True
    assert body["roles"]["idea_capture"]["configured"] is True


def test_no_secrets_in_response(tmp_path: Path) -> None:
    config = parse_config(
        {
            "paths": {"runtime_home": str(tmp_path)},
            "providers": {"anthropic": {"api_key": "sk-secret-test"}},
            "roles": {
                "brainstorm": {"provider": "anthropic", "model": "test-model"},
            },
        }
    )
    runtime = build_runtime_context(config)
    pricing = PricingTable(
        models={
            "test-model": ModelPricing(
                provider="anthropic",
                model="test-model",
                input_per_1k=0.01,
                output_per_1k=0.03,
                cached_per_1k=0.0,
                currency="DKK",
            )
        },
        exchange_rates_to_dkk={"DKK": 1.0},
    )
    object.__setattr__(runtime, "pricing", pricing)
    app = create_app(config=config, runtime=runtime)
    client = TestClient(app)

    response = client.get("/api/runtime")
    assert response.status_code == 200
    body = response.text
    assert "sk-secret-test" not in body
    assert "api_key" not in body
