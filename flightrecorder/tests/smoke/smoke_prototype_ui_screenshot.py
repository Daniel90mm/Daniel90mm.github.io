"""Smoke test: capture a prototype UI screenshot with google-chrome --headless.

Skips cleanly if google-chrome is unavailable.
"""

from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
CONFIG_TOML = REPO / "config.prototype.toml"
SCREENSHOT_PATH = Path("/tmp/flightrecorder-prototype-ui.png")


def _chrome_available() -> bool:
    return shutil.which("google-chrome") is not None


def _setup_prototype_data() -> None:
    os.environ["FLIGHTRECORDER_CONFIG"] = str(CONFIG_TOML)

    from flightrecorder.app import create_app
    from flightrecorder.config import load_config_from_environment

    config = load_config_from_environment()
    runtime_home = Path(config.paths.runtime_home)

    if runtime_home.exists():
        shutil.rmtree(runtime_home)

    from flightrecorder.runtime import build_runtime_context
    runtime = build_runtime_context(config)
    app = create_app(config=config, runtime=runtime)

    from fastapi.testclient import TestClient
    client = TestClient(app)

    create = client.post(
        "/api/sessions",
        json={"provider": "prototype", "model": "prototype-brainstorm", "slug": "ui-smoke"},
    )
    assert create.status_code == 201, f"create session: {create.status_code}"
    session_id = create.json()["session_id"]

    chat = client.post(
        f"/api/sessions/{session_id}/messages",
        json={"content": "brainstorm a fNIRS signal processing pipeline"},
    )
    assert chat.status_code == 200, f"chat: {chat.status_code}"

    extract = client.post(f"/api/sessions/{session_id}/extract")
    assert extract.status_code == 200, f"extract: {extract.status_code}"

    print(f"prototype data ready: session_id={session_id}")


def main() -> None:
    if not _chrome_available():
        print("skipped: google-chrome not found")
        return

    _setup_prototype_data()

    os.environ["FLIGHTRECORDER_CONFIG"] = str(CONFIG_TOML)
    server_proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "flightrecorder.app:create_app",
            "--factory",
            "--host",
            "127.0.0.1",
            "--port",
            "8765",
        ],
        cwd=str(REPO),
        env={**os.environ, "PYTHONPATH": str(REPO / "src" / "backend")},
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        for _ in range(30):
            time.sleep(0.5)
            try:
                import urllib.request
                urllib.request.urlopen("http://127.0.0.1:8765/health", timeout=2)
                break
            except Exception:
                pass
        else:
            server_proc.terminate()
            server_proc.wait(timeout=5)
            print("ERROR: server did not become ready", file=sys.stderr)
            sys.exit(1)

        result = subprocess.run(
            [
                "google-chrome",
                "--headless=new",
                "--no-sandbox",
                "--disable-gpu",
                "--window-size=900,800",
                f"--screenshot={SCREENSHOT_PATH}",
                "http://127.0.0.1:8765/",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            print(f"chrome screenshot failed: {result.stderr}", file=sys.stderr)
            sys.exit(1)
    finally:
        server_proc.terminate()
        try:
            server_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_proc.kill()
            server_proc.wait(timeout=5)

    if not SCREENSHOT_PATH.is_file():
        print(f"ERROR: screenshot missing: {SCREENSHOT_PATH}", file=sys.stderr)
        sys.exit(1)

    size = SCREENSHOT_PATH.stat().st_size
    if size == 0:
        print(f"ERROR: screenshot is empty: {SCREENSHOT_PATH}", file=sys.stderr)
        sys.exit(1)

    print(f"prototype UI screenshot smoke test passed ({size} bytes at {SCREENSHOT_PATH})")


if __name__ == "__main__":
    main()
