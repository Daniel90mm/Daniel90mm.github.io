"""Unit tests for flightrecorder.assets.extract_text_from_asset."""

from __future__ import annotations

from pathlib import Path

from flightrecorder.assets import MAX_CHARS, extract_text_from_asset


def test_extracts_txt_file(tmp_path: Path) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello from txt", encoding="utf-8")
    result = extract_text_from_asset(path)
    assert result == "hello from txt"


def test_extracts_md_file(tmp_path: Path) -> None:
    path = tmp_path / "readme.md"
    path.write_text("# Title\n\ncontent.\n", encoding="utf-8")
    result = extract_text_from_asset(path)
    assert result == "# Title\n\ncontent.\n"


def test_extracts_markdown_file(tmp_path: Path) -> None:
    path = tmp_path / "docs.markdown"
    path.write_text("markdown note", encoding="utf-8")
    result = extract_text_from_asset(path)
    assert result == "markdown note"


def test_extracts_by_mime_type(tmp_path: Path) -> None:
    path = tmp_path / "log.output"
    path.write_text("some log text", encoding="utf-8")
    result = extract_text_from_asset(path, mime_type="text/plain")
    assert result == "some log text"


def test_rejects_png(tmp_path: Path) -> None:
    path = tmp_path / "photo.png"
    path.write_bytes(b"\x89PNG")
    result = extract_text_from_asset(path)
    assert result is None


def test_rejects_pdf(tmp_path: Path) -> None:
    path = tmp_path / "doc.pdf"
    path.write_text("pretend pdf", encoding="utf-8")
    result = extract_text_from_asset(path)
    assert result is None


def test_truncates_long_text(tmp_path: Path) -> None:
    path = tmp_path / "big.txt"
    long_text = "x" * (MAX_CHARS + 1000)
    path.write_text(long_text, encoding="utf-8")
    result = extract_text_from_asset(path)
    assert result is not None
    assert len(result) == MAX_CHARS
    assert result == "x" * MAX_CHARS


def test_handles_binary_masquerading_as_txt(tmp_path: Path) -> None:
    path = tmp_path / "not-really.txt"
    path.write_bytes(b"\x80\x81\x82\x83")
    result = extract_text_from_asset(path)
    assert result is None
