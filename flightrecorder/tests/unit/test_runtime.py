from pathlib import Path

from flightrecorder.config import parse_config
from flightrecorder.runtime import build_runtime_context, build_runtime_context_for_path


def test_build_runtime_context_for_path(tmp_path: Path) -> None:
    runtime = build_runtime_context_for_path(tmp_path)

    assert runtime.config.paths.runtime_home == tmp_path
    assert runtime.sessions.runtime_home == tmp_path
    assert (tmp_path / "metadata.db").exists()
    assert runtime.brainstorm_provider.name == "none"
    assert runtime.idea_capture_provider.name == "none"


def test_build_runtime_context_wires_idea_capture_role(tmp_path: Path) -> None:
    config = parse_config(
        {
            "providers": {
                "anthropic": {"api_key": "test-key"},
            },
            "roles": {
                "idea_capture": {
                    "provider": "anthropic",
                    "model": "claude-sonnet-4-6",
                },
            },
            "paths": {"runtime_home": str(tmp_path)},
        }
    )

    runtime = build_runtime_context(config)

    assert runtime.idea_capture_provider.name == "anthropic"
    assert runtime.idea_capture_provider.model == "claude-sonnet-4-6"
