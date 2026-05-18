from datetime import datetime
from pathlib import Path

import pytest

from flightrecorder.documents import (
    PROJECT_SECTIONS,
    ProjectAppend,
    ProjectDocumentError,
    ProjectSectionMissingError,
    append_to_project_document,
    commit_documents_repo,
    create_project_document,
    documents_dir,
    ensure_documents_repo,
    insert_append_block,
    normalize_bullet_content,
    project_document_path,
    sanitize_project_ref,
    update_last_appended,
)


def test_create_project_document_writes_stable_sections(tmp_path: Path) -> None:
    created_at = datetime.fromisoformat("2026-05-18T18:45:00+02:00")

    path = create_project_document(tmp_path, "fNIRS", created_at)

    assert path == tmp_path / "documents" / "fnirs.md"
    text = path.read_text(encoding="utf-8")
    assert "project: fnirs" in text
    assert "last_appended: 2026-05-18T18:45:00+02:00" in text
    for section in PROJECT_SECTIONS:
        assert f"## {section}" in text


def test_append_to_project_document_inserts_under_target_section(tmp_path: Path) -> None:
    create_project_document(
        tmp_path,
        "fnirs",
        datetime.fromisoformat("2026-05-18T18:45:00+02:00"),
    )

    path = append_to_project_document(
        tmp_path,
        ProjectAppend(
            project_ref="fnirs",
            section="TODOs",
            content="prototype the differential amplifier stage [open]",
            timestamp="2026-05-18T19:00:00+02:00",
            source_session="2026-05-18-1730-fnirs-abcd1234",
        ),
    )

    text = path.read_text(encoding="utf-8")
    assert "last_appended: 2026-05-18T19:00:00+02:00" in text
    assert (
        "- 2026-05-18T19:00:00+02:00: prototype the differential amplifier stage "
        "[open] [source: 2026-05-18-1730-fnirs-abcd1234]"
    ) in text
    assert text.index("## TODOs") < text.index("prototype the differential amplifier")
    assert text.index("prototype the differential amplifier") < text.index("## Ideas")


def test_insert_append_block_preserves_other_sections_exactly() -> None:
    original = "\n".join(
        [
            "---",
            "project: fnirs",
            "last_appended: 2026-05-01T00:00:00+02:00",
            "---",
            "",
            "# fnirs",
            "",
            "## Problem",
            "existing problem text",
            "",
            "## TODOs",
            "- old todo",
            "",
            "## Ideas",
            "existing idea text",
            "",
        ]
    )

    updated = insert_append_block(original, "TODOs", "- new todo")

    assert "## Problem\nexisting problem text\n\n" in updated
    assert "## Ideas\nexisting idea text" in updated
    assert "## TODOs\n- old todo\n\n- new todo\n## Ideas" in updated


def test_append_rejects_unknown_section(tmp_path: Path) -> None:
    create_project_document(
        tmp_path,
        "fnirs",
        datetime.fromisoformat("2026-05-18T18:45:00+02:00"),
    )

    with pytest.raises(ProjectDocumentError):
        append_to_project_document(
            tmp_path,
            ProjectAppend(
                project_ref="fnirs",
                section="Not a section",
                content="something",
                timestamp="2026-05-18T19:00:00+02:00",
            ),
        )


def test_append_rejects_missing_section(tmp_path: Path) -> None:
    path = project_document_path(tmp_path, "fnirs")
    path.parent.mkdir(parents=True)
    path.write_text("# fnirs\n\n## TODOs\n", encoding="utf-8")

    with pytest.raises(ProjectSectionMissingError):
        append_to_project_document(
            tmp_path,
            ProjectAppend(
                project_ref="fnirs",
                section="Ideas",
                content="something",
                timestamp="2026-05-18T19:00:00+02:00",
            ),
        )


def test_update_last_appended_rejects_missing_frontmatter_field() -> None:
    with pytest.raises(ProjectDocumentError):
        update_last_appended("# fnirs\n\n## Ideas\n", "2026-05-18T19:00:00+02:00")


def test_normalize_bullet_content_strips_one_marker() -> None:
    assert normalize_bullet_content("- investigate PCA") == "investigate PCA"
    assert normalize_bullet_content("* investigate PCA") == "investigate PCA"


def test_sanitize_project_ref_rejects_empty_value() -> None:
    with pytest.raises(ProjectDocumentError):
        sanitize_project_ref("...")


def test_sanitize_lowercases() -> None:
    assert sanitize_project_ref("FNIRS") == "fnirs"


def test_sanitize_replaces_spaces_with_hyphens() -> None:
    assert sanitize_project_ref("pulse oximeter") == "pulse-oximeter"


def test_sanitize_preserves_hyphens_and_underscores() -> None:
    assert sanitize_project_ref("pulse_oximeter-v2") == "pulse_oximeter-v2"


def test_sanitize_strips_trailing_special_chars() -> None:
    assert sanitize_project_ref("--fnirs--") == "fnirs"


def test_sanitize_squashes_multiple_special_chars() -> None:
    assert sanitize_project_ref("pulse  oximeter") == "pulse-oximeter"


def test_ensure_documents_repo_initializes_git_repo(tmp_path: Path) -> None:
    path = documents_dir(tmp_path)

    ensure_documents_repo(path)

    assert (path / ".git").exists()


def test_commit_documents_repo_commits_changes_and_skips_clean_tree(
    tmp_path: Path,
) -> None:
    path = documents_dir(tmp_path)
    create_project_document(
        tmp_path,
        "fnirs",
        datetime.fromisoformat("2026-05-18T18:45:00+02:00"),
    )

    committed = commit_documents_repo(path, "Initial project docs")
    skipped = commit_documents_repo(path, "No changes")

    assert committed is True
    assert skipped is False


def test_append_preserves_hand_written_text_around_section(tmp_path: Path) -> None:
    path = project_document_path(tmp_path, "fnirs")
    path.parent.mkdir(parents=True)
    original = "\n".join(
        [
            "---",
            "project: fnirs",
            "last_appended: 2026-05-01T00:00:00+02:00",
            "---",
            "",
            "# fnirs",
            "",
            "## Problem",
            "some handwritten background text",
            "that spans multiple lines",
            "",
            "## TODOs",
            "- old todo item from manual edit",
            "",
            "## Ideas",
            "## Decisions made",
            "",
        ]
    )
    path.write_text(original, encoding="utf-8")

    append_to_project_document(
        tmp_path,
        ProjectAppend(
            project_ref="fnirs",
            section="TODOs",
            content="new todo from system",
            timestamp="2026-05-18T19:00:00+02:00",
        ),
    )

    updated = path.read_text(encoding="utf-8")
    assert "some handwritten background text" in updated
    assert "that spans multiple lines" in updated
    assert "old todo item from manual edit" in updated
    assert "new todo from system" in updated


def test_append_preserves_non_standard_text_between_sections(tmp_path: Path) -> None:
    path = project_document_path(tmp_path, "fnirs")
    path.parent.mkdir(parents=True)
    original = "\n".join(
        [
            "---",
            "project: fnirs",
            "last_appended: 2026-05-01T00:00:00+02:00",
            "---",
            "",
            "# fnirs",
            "",
            "Some freeform text before sections.",
            "",
            "## Problem",
            "problem text",
            "",
            "More text between sections.",
            "",
            "## TODOs",
            "- old todo",
            "",
            "## Ideas",
            "",
        ]
    )
    path.write_text(original, encoding="utf-8")

    append_to_project_document(
        tmp_path,
        ProjectAppend(
            project_ref="fnirs",
            section="TODOs",
            content="new todo",
            timestamp="2026-05-18T19:00:00+02:00",
        ),
    )

    updated = path.read_text(encoding="utf-8")
    assert "Some freeform text before sections." in updated
    assert "More text between sections." in updated
    assert "old todo" in updated
    assert "new todo" in updated
