"""Smoke test: create a project document, append a TODO, assert it lands in TODOs section."""

from __future__ import annotations

import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src" / "backend"))

from flightrecorder.documents import (
    ProjectAppend,
    append_to_project_document,
    create_project_document,
    project_document_path,
)


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        runtime_home = Path(tmp)
        project_ref = "pulse-oximeter"
        now = datetime.now(timezone.utc)

        path = create_project_document(runtime_home, project_ref, now)
        assert path.exists()

        append = ProjectAppend(
            project_ref=project_ref,
            section="TODOs",
            content="investigate PCA for denoising multispectral data",
            timestamp=now.isoformat(),
            source_session="2026-05-18-1730-test-abcd1234",
        )

        updated_path = append_to_project_document(runtime_home, append)
        content = updated_path.read_text(encoding="utf-8")

        assert "investigate PCA for denoising multispectral data" in content
        assert "[source: 2026-05-18-1730-test-abcd1234]" in content

        todos_index = content.index("## TODOs")
        ideas_index = content.index("## Ideas")
        assert todos_index < ideas_index
        assert "investigate PCA" in content[todos_index:ideas_index]

        print(f"project_document_path: {path}")
        print(f"todos_present: True")
        print(f"todo_between_todos_and_ideas: True")

    print("project document smoke test passed")


if __name__ == "__main__":
    main()
