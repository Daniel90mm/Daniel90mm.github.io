"""Typed project registry loader for runtime projects.json."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json
import re

from flightrecorder.documents import sanitize_project_ref


class ProjectRegistryError(RuntimeError):
    """Raised when projects.json cannot be loaded or validated."""


@dataclass(frozen=True)
class ProjectEntry:
    name: str
    ref: str
    path: str
    active: bool
    description: str = ""


@dataclass(frozen=True)
class ProjectRegistry:
    projects: list[ProjectEntry]

    def active(self) -> list[ProjectEntry]:
        return [p for p in self.projects if p.active]

    def lookup(self, ref: str) -> ProjectEntry | None:
        for p in self.projects:
            if p.ref == ref:
                return p
        return None


def load_project_registry(path: Path) -> ProjectRegistry:
    """Load and validate a project registry from a JSON file."""

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ProjectRegistryError("projects.json is not valid JSON") from exc

    if not isinstance(data, list):
        raise ProjectRegistryError("projects.json must be a JSON array")

    projects: list[ProjectEntry] = []
    for i, raw in enumerate(data):
        if not isinstance(raw, dict):
            raise ProjectRegistryError(f"projects.json entry {i} must be an object")
        projects.append(_parse_entry(raw, i))

    return ProjectRegistry(projects=projects)


def _parse_entry(item: dict[str, object], index: int) -> ProjectEntry:
    name = _required_str(item, "name", index)
    raw_ref = _required_str(item, "ref", index)
    path = _required_str(item, "path", index)
    active = _optional_bool(item, "active")
    description = _optional_str(item, "description")

    sanitized = sanitize_project_ref(raw_ref)
    if sanitized != raw_ref:
        raise ProjectRegistryError(
            f"projects.json entry {index} ref {raw_ref!r} does not match "
            f"slug form {sanitized!r}"
        )

    return ProjectEntry(
        name=name,
        ref=sanitized,
        path=path,
        active=active,
        description=description,
    )


def _required_str(item: dict[str, object], key: str, index: int) -> str:
    value = item.get(key)
    if not isinstance(value, str) or value.strip() == "":
        raise ProjectRegistryError(
            f"projects.json entry {index}.{key} must be a non-empty string"
        )
    return value


def _optional_str(item: dict[str, object], key: str) -> str:
    value = item.get(key)
    if value is None:
        return ""
    if not isinstance(value, str):
        return ""
    return value


def _optional_bool(item: dict[str, object], key: str) -> bool:
    value = item.get(key)
    if value is None:
        return True
    if isinstance(value, bool):
        return value
    return True
