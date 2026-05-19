"""Smoke test: build Hugo site and check generated internal links."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
HREF_RE = re.compile(r"""href=([\"'])(.*?)\1|href=([^\s>\"']+)""")


def is_external(url: str) -> bool:
    parsed = urlparse(url)
    return bool(parsed.scheme and parsed.scheme in ("http", "https"))


def resolve_and_check(href: str, html_file: Path, destination: Path) -> tuple[bool, str]:
    if href.startswith("/"):
        target = destination / href.lstrip("/")
        candidates = [target / "index.html", target.with_suffix(".html"), target]
    elif href.startswith(("#", "?")) or href.startswith("mailto:"):
        return True, ""
    else:
        base_dir = html_file.parent
        target = (base_dir / href).resolve()
        if not str(target).startswith(str(destination.resolve())):
            return False, f"relative link {href} resolves outside destination"
        candidates = [target, target / "index.html", target.with_suffix(".html")]

    for candidate in candidates:
        if candidate.is_file():
            return True, ""

    return False, f"broken link {href} from {html_file.relative_to(destination)}"


def main() -> None:
    museum_dir = REPO_ROOT / "museum"
    hugo_toml = museum_dir / "hugo.toml"
    if not hugo_toml.exists():
        print(f"missing: {hugo_toml}", file=sys.stderr)
        sys.exit(1)

    if shutil.which("hugo") is None:
        print("ERROR: hugo executable not found on PATH", file=sys.stderr)
        sys.exit(1)

    with tempfile.TemporaryDirectory() as temp_dir:
        destination = Path(temp_dir)
        env = {
            **os.environ,
            "HUGO_ENVIRONMENT": "production",
            "HUGO_ENV": "production",
            "HUGO_BASEURL": "https://daniel90mm.github.io/",
        }
        result = subprocess.run(
            [
                "hugo",
                "--gc",
                "--minify",
                "--destination",
                str(destination),
            ],
            cwd=museum_dir,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0:
            print(result.stdout, file=sys.stdout)
            print(result.stderr, file=sys.stderr)
            print("ERROR: hugo production build failed", file=sys.stderr)
            sys.exit(result.returncode)

        html_files = list(destination.rglob("*.html"))
        if not html_files:
            print("ERROR: no HTML files in build output", file=sys.stderr)
            sys.exit(1)

        checked: int = 0
        broken: list[str] = []
        for html_file in html_files:
            text = html_file.read_text(encoding="utf-8")
            for m in HREF_RE.finditer(text):
                href = m.group(2) if m.group(2) else m.group(3)
                if not href:
                    continue
                if is_external(href):
                    continue
                if href.startswith("mailto:"):
                    continue
                if href.startswith("#") or href.startswith("?"):
                    continue

                ok, reason = resolve_and_check(href, html_file, destination)
                if not ok:
                    broken.append(reason)
                checked += 1

        if broken:
            for reason in broken:
                print(f"  {reason}", file=sys.stderr)
            print(f"ERROR: {len(broken)} broken internal link(s)", file=sys.stderr)
            sys.exit(1)

        print(f"checked_internal_links: {checked}")
        print("hugo internal link smoke test passed")


if __name__ == "__main__":
    main()
