"""Append-only project document helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
import subprocess


PROJECT_SECTIONS = (
    "Problem",
    "Current state",
    "Decisions made",
    "Open questions",
    "TODOs",
    "Ideas",
)


class ProjectDocumentError(RuntimeError):
    """Raised when a project document cannot be updated safely."""


class ProjectSectionMissingError(ProjectDocumentError):
    """Raised when the target append section is absent."""


@dataclass(frozen=True)
class ProjectAppend:
    project_ref: str
    section: str
    content: str
    timestamp: str
    source_session: str | None = None


def documents_dir(runtime_home: Path) -> Path:
    """Return the runtime project documents directory."""

    return runtime_home / "documents"


def project_document_path(runtime_home: Path, project_ref: str) -> Path:
    """Return the markdown file path for one project document."""

    return documents_dir(runtime_home) / f"{sanitize_project_ref(project_ref)}.md"


def create_project_document(
    runtime_home: Path,
    project_ref: str,
    created_at: datetime,
) -> Path:
    """Create a project document with stable sections if it does not exist."""

    path = project_document_path(runtime_home, project_ref)
    if path.exists():
        return path

    safe_ref = sanitize_project_ref(project_ref)
    path.parent.mkdir(parents=True, exist_ok=True)
    created_date = created_at.date().isoformat()
    created_timestamp = created_at.isoformat()
    path.write_text(
        "\n".join(
            [
                "---",
                f"project: {safe_ref}",
                f"created: {created_date}",
                f"last_appended: {created_timestamp}",
                "---",
                "",
                f"# {safe_ref}",
                "",
                "## Problem",
                "",
                "## Current state",
                "",
                "## Decisions made",
                "",
                "## Open questions",
                "",
                "## TODOs",
                "",
                "## Ideas",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


def append_to_project_document(runtime_home: Path, append: ProjectAppend) -> Path:
    """Append one idea operation under the named project document section."""

    if append.section not in PROJECT_SECTIONS:
        raise ProjectDocumentError(f"unknown project document section: {append.section}")

    path = project_document_path(runtime_home, append.project_ref)
    text = path.read_text(encoding="utf-8")
    updated = update_last_appended(
        insert_append_block(text, append.section, render_append_block(append)),
        append.timestamp,
    )
    path.write_text(updated, encoding="utf-8")
    return path


def insert_append_block(text: str, section: str, block: str) -> str:
    """Return text with block appended to section without reflowing other text."""

    section_match = re.search(rf"(?m)^## {re.escape(section)}$", text)
    if section_match is None:
        raise ProjectSectionMissingError(f"missing project document section: {section}")

    next_section_match = re.search(r"(?m)^## ", text[section_match.end() :])
    if next_section_match is None:
        insert_at = len(text)
    else:
        insert_at = section_match.end() + next_section_match.start()

    before = text[:insert_at].rstrip()
    after = text[insert_at:]
    insertion = f"\n\n{block.rstrip()}\n"
    if after:
        return before + insertion + after
    return before + insertion


def render_append_block(append: ProjectAppend) -> str:
    """Render an append operation as one markdown bullet."""

    content = normalize_bullet_content(append.content)
    if not content:
        raise ProjectDocumentError("project append content is empty")
    if "\n" in content:
        raise ProjectDocumentError("project append content must be one paragraph")

    source = f" [source: {append.source_session}]" if append.source_session else ""
    return f"- {append.timestamp}: {content}{source}"


def update_last_appended(text: str, timestamp: str) -> str:
    """Update the frontmatter last_appended field without touching body text."""

    updated, count = re.subn(
        r"(?m)^last_appended: .*$",
        f"last_appended: {timestamp}",
        text,
        count=1,
    )
    if count == 0:
        raise ProjectDocumentError("project document is missing last_appended")
    return updated


def ensure_documents_repo(documents_path: Path) -> None:
    """Ensure the project documents directory is an initialized git repo."""

    documents_path.mkdir(parents=True, exist_ok=True)
    if (documents_path / ".git").exists():
        return
    subprocess.run(
        ["git", "-C", str(documents_path), "init"],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def commit_documents_repo(documents_path: Path, message: str) -> bool:
    """Commit changed project documents in their own git repository."""

    ensure_documents_repo(documents_path)

    subprocess.run(
        ["git", "-C", str(documents_path), "add", "."],
        check=True,
    )
    diff = subprocess.run(
        ["git", "-C", str(documents_path), "diff", "--cached", "--quiet"],
        check=False,
    )
    if diff.returncode == 0:
        return False
    subprocess.run(
        [
            "git",
            "-C",
            str(documents_path),
            "-c",
            "user.name=flightrecorder",
            "-c",
            "user.email=flightrecorder@example.invalid",
            "commit",
            "-m",
            message,
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return True


def sanitize_project_ref(value: str) -> str:
    """Return a conservative project document filename stem."""

    safe = re.sub(r"[^a-z0-9_-]+", "-", value.lower()).strip("-")
    if not safe:
        raise ProjectDocumentError("project_ref is empty after sanitization")
    return safe


def normalize_bullet_content(value: str) -> str:
    """Strip one leading markdown bullet marker from generated content."""

    return re.sub(r"^\s*[-*]\s+", "", value.strip())
