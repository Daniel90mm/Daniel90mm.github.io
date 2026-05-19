"""Smoke test: verify static frontend files exist and app.js references expected API routes."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
FE_DIR = REPO / "src" / "frontend"

FILES = ["index.html", "styles.css", "app.js"]

REQUIRED_ROUTES = [
    '"/api/sessions"',
    '"/messages"',
    '"/extract"',
    '"/api/budget"',
    '"/upload"',
    '"/api/documents"',
    '"/api/spaghetti"',
    '"/api/runtime"',
    'api/api-calls',
    'api/publish/preview',
    'api/matchmaker/run',
]


def main() -> None:
    for name in FILES:
        path = FE_DIR / name
        if not path.is_file():
            print(f"missing: {path}", file=sys.stderr)
            sys.exit(1)
    print(f"frontend static files: {len(FILES)} found")

    app_js = (FE_DIR / "app.js").read_text(encoding="utf-8")
    for route in REQUIRED_ROUTES:
        if route not in app_js:
            print(f"missing route reference in app.js: {route}", file=sys.stderr)
            sys.exit(1)
    if "refreshSessionList(true)" not in app_js:
        print("missing initial session auto-select", file=sys.stderr)
        sys.exit(1)
    if "DOM.callsList.innerHTML = html" in app_js:
        print("calls panel must not render API rows with innerHTML", file=sys.stderr)
        sys.exit(1)
    print(f"route references in app.js: {len(REQUIRED_ROUTES)} found")

    index_html = (FE_DIR / "index.html").read_text(encoding="utf-8")
    for asset in ("/assets/styles.css", "/assets/app.js"):
        if asset not in index_html:
            print(f"missing asset reference in index.html: {asset}", file=sys.stderr)
            sys.exit(1)
    if 'id="budget-summary"' not in index_html:
        print("missing budget summary in index.html", file=sys.stderr)
        sys.exit(1)
    if 'id="runtime-status"' not in index_html:
        print("missing runtime status in index.html", file=sys.stderr)
        sys.exit(1)
    if 'id="calls-list"' not in index_html:
        print("missing calls list in index.html", file=sys.stderr)
        sys.exit(1)
    if 'id="upload-file"' not in index_html:
        print("missing upload file input in index.html", file=sys.stderr)
        sys.exit(1)
    if 'accept="image/*,.pdf,.txt,.md,text/plain,text/markdown,application/pdf"' not in index_html:
        print("upload file input must accept image/pdf/text/markdown", file=sys.stderr)
        sys.exit(1)
    if 'id="session-summary"' not in index_html:
        print("missing selected-session summary in index.html", file=sys.stderr)
        sys.exit(1)
    if 'id="preview-session-btn"' not in index_html:
        print("missing session publish preview button in index.html", file=sys.stderr)
        sys.exit(1)
    if 'id="asset-list"' not in index_html:
        print("missing uploaded asset list in index.html", file=sys.stderr)
        sys.exit(1)
    if 'id="run-matchmaker-btn"' not in index_html:
        print("missing matchmaker run button in index.html", file=sys.stderr)
        sys.exit(1)
    if 'id="attachment-context-panel"' not in index_html:
        print("missing attachment context panel in index.html", file=sys.stderr)
        sys.exit(1)
    if 'id="preview-attachments-btn"' not in index_html:
        print("missing attachment context preview button in index.html", file=sys.stderr)
        sys.exit(1)
    if "voice or type" in index_html:
        print("frontend must not imply voice support exists", file=sys.stderr)
        sys.exit(1)
    if "deleteAsset" not in app_js:
        print("missing frontend asset delete handler", file=sys.stderr)
        sys.exit(1)
    if "previewAttachmentContext" not in app_js:
        print("missing frontend attachment context handler", file=sys.stderr)
        sys.exit(1)

    print("frontend static files smoke test passed")


if __name__ == "__main__":
    main()
