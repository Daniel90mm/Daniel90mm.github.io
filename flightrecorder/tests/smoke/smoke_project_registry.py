"""Smoke test: load fixture registry and print active project refs."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src" / "backend"))

from flightrecorder.project_registry import load_project_registry


def main() -> None:
    fixture = (
        Path(__file__).resolve().parent.parent
        / "fixtures"
        / "project_registry"
        / "projects.json"
    )

    registry = load_project_registry(fixture)

    print(f"total_projects: {len(registry.projects)}")

    active = registry.active()
    print(f"active_projects: {len(active)}")
    for entry in active:
        print(f"  {entry.ref}: {entry.name}")

    assert len(registry.projects) == 3
    assert len(active) == 2

    print("project registry smoke test passed")


if __name__ == "__main__":
    main()
