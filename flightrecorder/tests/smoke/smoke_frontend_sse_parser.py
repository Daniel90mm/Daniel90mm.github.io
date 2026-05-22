"""Smoke test: verify SSE parser in app.js handles all required event types."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
APP_JS = REPO / "src" / "frontend" / "app.js"
APP_UTILS_JS = REPO / "src" / "frontend" / "app-utils.js"


def extract_parser_source(app_js_text: str) -> str:
    """Extract the createSSEParser function from app.js."""
    start = app_js_text.find("function createSSEParser() {")
    if start == -1:
        raise SystemExit("createSSEParser not found in app.js")

    depth = 0
    end = start
    for i, ch in enumerate(app_js_text[start:], start=start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break

    return app_js_text[start:end]


TEST_SCRIPT = """
__PARSER_CODE__

var parser = createSSEParser();
var results = [];

// Test 1: token event
results.push({test: "token", events: parser.parseChunk('event: token\\ndata: {"token":"Hello"}\\n\\n')});

// Test 2: done event
results.push({test: "done", events: parser.parseChunk('event: done\\ndata: {"input_tokens":10,"output_tokens":5}\\n\\n')});

// Test 3: error event
results.push({test: "error", events: parser.parseChunk('event: error\\ndata: {"error":"something broke"}\\n\\n')});

// Test 4: multiple events in one chunk
results.push({test: "multi", events: parser.parseChunk('event: token\\ndata: {"token":"A"}\\n\\nevent: token\\ndata: {"token":"B"}\\n\\n')});

// Test 5: partial trailing event
results.push({test: "partial", events: parser.parseChunk('event: token\\ndata: {"token":"C"}')});

// Test 6: resume partial
results.push({test: "resume", events: parser.parseChunk('\\nevent: done\\ndata: {"input_tokens":1}\\n\\n')});

// Test 7: malformed data skipped
results.push({test: "malformed", events: parser.parseChunk('event: token\\ndata: {\"not valid json\\n\\n')});

console.log(JSON.stringify(results));
"""


def main() -> None:
    app_js_text = APP_JS.read_text(encoding="utf-8")
    app_utils_text = APP_UTILS_JS.read_text(encoding="utf-8")

    if "createSSEParser" not in app_utils_text:
        print("createSSEParser not found in app-utils.js", file=sys.stderr)
        sys.exit(1)
    for literal in ('event === "token"', 'event === "done"', 'event === "error"'):
        if literal not in app_js_text:
            print(f"missing parser event handling text: {literal}", file=sys.stderr)
            sys.exit(1)

    if shutil.which("node") is None:
        print("node not found; skipped runtime JS execution")
        print("SSE parser smoke test passed")
        return

    parser_code = extract_parser_source(app_utils_text)
    full_script = TEST_SCRIPT.replace("__PARSER_CODE__", parser_code)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".js", encoding="utf-8", delete=False
    ) as f:
        f.write(full_script)
        tmp_path = f.name

    try:
        result = subprocess.run(
            ["node", tmp_path],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            print(f"node execution failed: {result.stderr}", file=sys.stderr)
            sys.exit(1)

        parsed = json.loads(result.stdout.strip())

        assert len(parsed) >= 7, f"expected at least 7 test results, got {len(parsed)}"

        token_test = [t for t in parsed if t["test"] == "token"][0]
        assert len(token_test["events"]) == 1
        assert token_test["events"][0]["event"] == "token"
        assert token_test["events"][0]["data"]["token"] == "Hello"

        done_test = [t for t in parsed if t["test"] == "done"][0]
        assert done_test["events"][0]["event"] == "done"
        assert done_test["events"][0]["data"]["input_tokens"] == 10

        error_test = [t for t in parsed if t["test"] == "error"][0]
        assert error_test["events"][0]["event"] == "error"
        assert error_test["events"][0]["data"]["error"] == "something broke"

        multi_test = [t for t in parsed if t["test"] == "multi"][0]
        assert len(multi_test["events"]) == 2
        assert multi_test["events"][0]["data"]["token"] == "A"
        assert multi_test["events"][1]["data"]["token"] == "B"

        partial_test = [t for t in parsed if t["test"] == "partial"][0]
        assert len(partial_test["events"]) == 0, "partial chunk should produce no events"

        resume_test = [t for t in parsed if t["test"] == "resume"][0]
        assert len(resume_test["events"]) == 2
        assert resume_test["events"][0]["event"] == "token"
        assert resume_test["events"][0]["data"]["token"] == "C"
        assert resume_test["events"][1]["event"] == "done"

        malformed_test = [t for t in parsed if t["test"] == "malformed"][0]
        assert len(malformed_test["events"]) == 0, "malformed data should be skipped"

        print("SSE parser smoke test passed")
    finally:
        Path(tmp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    main()
