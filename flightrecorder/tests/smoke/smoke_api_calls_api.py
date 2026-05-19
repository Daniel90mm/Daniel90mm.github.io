"""Smoke test: exercise GET /api/api-calls with TestClient."""

from __future__ import annotations

import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from flightrecorder.app import create_app
from flightrecorder.config import parse_config
from flightrecorder.costs import ApiCallRecord, log_api_call
from flightrecorder.runtime import build_runtime_context


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        config = parse_config({"paths": {"runtime_home": str(tmp_path)}})
        runtime = build_runtime_context(config)

        log_api_call(
            runtime.database,
            ApiCallRecord(
                timestamp=datetime.now(timezone.utc).isoformat(),
                provider="smoke-prov",
                model="smoke-model",
                role="smoke",
                input_tokens=1,
                output_tokens=1,
                cached_tokens=0,
                cost_dkk=0.01,
            ),
        )

        app = create_app(config=config, runtime=runtime)
        client = TestClient(app)

        resp = client.get("/api/api-calls")
        assert resp.status_code == 200
        body = resp.json()
        assert "api_calls" in body
        assert len(body["api_calls"]) == 1
        assert body["api_calls"][0]["role"] == "smoke"

        resp = client.get("/api/api-calls?limit=5")
        assert resp.status_code == 200

        resp = client.get("/api/api-calls?limit=0")
        assert resp.status_code == 422

        print("api calls API smoke test passed")


if __name__ == "__main__":
    main()
