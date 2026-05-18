from pathlib import Path

import pytest

from flightrecorder.project_registry import (
    ProjectEntry,
    ProjectRegistry,
    ProjectRegistryError,
    load_project_registry,
)

FIXTURE = (
    Path(__file__).resolve().parent.parent
    / "fixtures"
    / "project_registry"
    / "projects.json"
)


def test_load_project_registry_reads_fixture() -> None:
    registry = load_project_registry(FIXTURE)

    assert len(registry.projects) == 3
    assert registry.projects[0].ref == "pulse-oximeter"
    assert registry.projects[1].ref == "fnirs"
    assert registry.projects[2].ref == "keyboard"


def test_active_projects_filters_inactive() -> None:
    registry = load_project_registry(FIXTURE)

    active = registry.active()
    refs = [p.ref for p in active]

    assert len(active) == 2
    assert "pulse-oximeter" in refs
    assert "fnirs" in refs
    assert "keyboard" not in refs


def test_lookup_returns_entry_by_ref() -> None:
    registry = load_project_registry(FIXTURE)

    entry = registry.lookup("fnirs")
    assert entry is not None
    assert entry.name == "fNIRS System"
    assert entry.active is True


def test_lookup_returns_none_for_unknown_ref() -> None:
    registry = load_project_registry(FIXTURE)

    assert registry.lookup("no-such-project") is None


def test_load_rejects_non_json(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text("not json", encoding="utf-8")

    with pytest.raises(ProjectRegistryError):
        load_project_registry(path)


def test_load_rejects_non_array(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text('{"key": "value"}', encoding="utf-8")

    with pytest.raises(ProjectRegistryError):
        load_project_registry(path)


def test_load_rejects_entry_without_name(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text(
        '[{"ref": "test", "path": "/tmp"}]',
        encoding="utf-8",
    )

    with pytest.raises(ProjectRegistryError):
        load_project_registry(path)


def test_load_rejects_ref_not_matching_slug_form(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text(
        '[{"name": "Test", "ref": "Bad Ref", "path": "/tmp"}]',
        encoding="utf-8",
    )

    with pytest.raises(ProjectRegistryError):
        load_project_registry(path)


def test_load_accepts_missing_active_defaults_to_true(tmp_path: Path) -> None:
    path = tmp_path / "minimal.json"
    path.write_text(
        '[{"name": "Test", "ref": "test", "path": "/tmp"}]',
        encoding="utf-8",
    )

    registry = load_project_registry(path)

    assert len(registry.projects) == 1
    assert registry.projects[0].active is True


def test_project_entry_fields_match_fixture_first_row() -> None:
    registry = load_project_registry(FIXTURE)
    entry = registry.projects[0]

    assert entry.name == "Pulse Oximeter"
    assert entry.ref == "pulse-oximeter"
    assert entry.path == "/home/demo/Documents/Projekter/pulse-oximeter"
    assert entry.active is True
    assert "DTU thesis" in entry.description
