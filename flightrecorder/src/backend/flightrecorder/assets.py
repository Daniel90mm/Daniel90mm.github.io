"""Text extraction from uploaded text-like assets.

Pure functions with no external dependencies. Separate from any provider
or API wiring, so the extraction boundary can be tested in isolation.
"""

from __future__ import annotations

from pathlib import Path

TEXT_EXTENSIONS = frozenset({".txt", ".md", ".markdown"})
MAX_CHARS = 20_000


def extract_text_from_asset(
    path: Path,
    mime_type: str | None = None,
) -> str | None:
    """Return decoded text from a safe uploaded asset, or None if unsupported.

    Accepts files with extensions `.txt`, `.md`, or `.markdown`, and files
    whose content type begins with `text/`. Caps output at `MAX_CHARS` (20,000
    characters). Returns `None` for binary assets such as images and PDFs.
    """

    allowed = path.suffix.lower() in TEXT_EXTENSIONS
    if not allowed and mime_type and mime_type.startswith("text/"):
        allowed = True
    if not allowed:
        return None

    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None

    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS]

    return text
