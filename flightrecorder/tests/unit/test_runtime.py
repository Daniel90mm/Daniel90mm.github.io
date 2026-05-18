from pathlib import Path

from flightrecorder.runtime import build_runtime_context_for_path


def test_build_runtime_context_for_path(tmp_path: Path) -> None:
    runtime = build_runtime_context_for_path(tmp_path)

    assert runtime.config.paths.runtime_home == tmp_path
    assert runtime.sessions.runtime_home == tmp_path
    assert (tmp_path / "metadata.db").exists()
