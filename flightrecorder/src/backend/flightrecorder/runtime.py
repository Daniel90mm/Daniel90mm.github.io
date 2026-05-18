"""Runtime wiring for backend services."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sqlite3

from flightrecorder.config import AppConfig, load_config_from_environment, parse_config
from flightrecorder.database import connect_metadata_db
from flightrecorder.storage import SessionStore


@dataclass(frozen=True)
class RuntimeContext:
    config: AppConfig
    database: sqlite3.Connection
    sessions: SessionStore


def build_runtime_context(
    config: AppConfig | None = None,
    database: sqlite3.Connection | None = None,
) -> RuntimeContext:
    """Build runtime services for the backend app."""

    resolved_config = config or load_config_from_environment()
    runtime_home = resolved_config.paths.runtime_home
    resolved_database = database or connect_metadata_db(runtime_home)
    return RuntimeContext(
        config=resolved_config,
        database=resolved_database,
        sessions=SessionStore(runtime_home, resolved_database),
    )


def build_runtime_context_for_path(runtime_home: Path) -> RuntimeContext:
    """Build runtime services for a specific runtime home."""

    config = parse_config({"paths": {"runtime_home": str(runtime_home)}})
    return build_runtime_context(config)
