"""Smoke test: ensure documents repo, append, commit, print latest commit subject."""

from __future__ import annotations

import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src" / "backend"))

from flightrecorder.documents import (
    ProjectAppend,
    append_to_project_document,
    commit_documents_repo,
    create_project_document,
    documents_dir,
    ensure_documents_repo,
)


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        runtime_home = Path(tmp)
        now = datetime.now(timezone.utc)

        docs_path = documents_dir(runtime_home)
        ensure_documents_repo(docs_path)
        assert (docs_path / ".git").exists()

        create_project_document(runtime_home, "pulse-oximeter", now)

        append = ProjectAppend(
            project_ref="pulse-oximeter",
            section="TODOs",
            content="test the git auto-commit path",
            timestamp=now.isoformat(),
            source_session="2026-05-18-1730-test-abcd1234",
        )
        append_to_project_document(runtime_home, append)

        committed = commit_documents_repo(
            docs_path, "smoke test append from S51"
        )
        print(f"committed: {committed}")

        import subprocess
        result = subprocess.run(
            ["git", "-C", str(docs_path), "log", "--oneline", "-1"],
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"latest_commit: {result.stdout.strip()}")

    print("documents git smoke test passed")


if __name__ == "__main__":
    main()
