"""Smoke test: parse a tiny in-memory pricing table, compute one call cost."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src" / "backend"))

from flightrecorder.costs import compute_cost_dkk, parse_pricing


def main() -> None:
    data = {
        "models": {
            "fake-model": {
                "provider": "test",
                "input_per_1k": 1.0,
                "output_per_1k": 2.0,
                "cached_per_1k": 0.5,
                "currency": "USD",
            }
        },
        "exchange_rates_to_dkk": {"USD": 0.9},
    }

    pricing = parse_pricing(data)

    cost = compute_cost_dkk(
        pricing,
        model="fake-model",
        input_tokens=1000,
        output_tokens=500,
        cached_tokens=200,
    )

    expected = (1000 / 1000 * 1.0 + 500 / 1000 * 2.0 + 200 / 1000 * 0.5) * 0.9
    print(f"computed_cost_dkk: {cost}")
    print(f"expected_cost_dkk: {expected}")

    assert abs(cost - expected) < 0.001, f"cost mismatch: {cost} vs {expected}"

    print("pricing smoke test passed")


if __name__ == "__main__":
    main()
