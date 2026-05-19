"""Smoke test: publisher pipeline fail-closed defaults with adversarial fixtures."""

from __future__ import annotations

import sys

from flightrecorder.publisher import (
    NullCurator,
    NullReviewer,
    PipelineResult,
    adversarial_fixture_dir,
    run_publish_pipeline,
)


def main() -> None:
    fixture_dir = adversarial_fixture_dir()
    txt_files = sorted(fixture_dir.glob("*.txt"))
    if not txt_files:
        print("ERROR: no fixture files found", file=sys.stderr)
        sys.exit(1)

    results: dict[str, PipelineResult] = {}
    for txt_path in txt_files:
        stem = txt_path.stem
        body = txt_path.read_text(encoding="utf-8")
        result = run_publish_pipeline(
            source_kind="adversarial",
            source_id=stem,
            source_body=body,
        )
        results[stem] = result
        print(f"{stem}: approved={len(result.approved)} reason={result.rejection_reason}")

    total_approved = sum(len(r.approved) for r in results.values())
    all_rejected = all(r.rejection_reason is not None for r in results.values())

    print(f"total_fixtures: {len(results)}")
    print(f"total_approved: {total_approved}")
    print(f"all_rejected: {all_rejected}")

    leaked: list[str] = []
    if total_approved > 0:
        for stem, result in results.items():
            if result.approved:
                snippet_ids = [s.snippet_id for s in result.approved]
                leaked.append(f"{stem}: {snippet_ids}")

    missing_reason: list[str] = []
    for stem, result in results.items():
        if result.rejection_reason is None:
            missing_reason.append(stem)

    if leaked:
        for l in leaked:
            print(f"LEAKED: {l}", file=sys.stderr)
    if missing_reason:
        for m in missing_reason:
            print(f"NO REASON: {m}", file=sys.stderr)

    if leaked or missing_reason:
        if leaked:
            print(
                f"ERROR: {len(leaked)} fixture(s) leaked approved snippets",
                file=sys.stderr,
            )
        if missing_reason:
            print(
                f"ERROR: {len(missing_reason)} fixture(s) missing rejection_reason",
                file=sys.stderr,
            )
        sys.exit(1)

    print("publisher pipeline smoke test passed (fail-closed verified)")


if __name__ == "__main__":
    main()
