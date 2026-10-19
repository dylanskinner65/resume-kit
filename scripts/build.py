#!/usr/bin/env python3
"""Compile trusted local Typst content, verify it, and render review previews."""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from verify import load_checks, verify

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Typst content inside this repository")
    parser.add_argument("--checks", type=Path, help="Defaults to source with .checks.json suffix")
    parser.add_argument("--output", type=Path, help="Defaults to build/<source stem>/")
    args = parser.parse_args()
    source = args.source.resolve()
    if not source.is_relative_to(ROOT) or source.suffix != ".typ" or not source.is_file():
        parser.exit(1, "Source must be an existing .typ file inside this repository\n")
    if shutil.which("typst") is None:
        parser.exit(1, "Typst is not installed or not on PATH; see README.md\n")
    checks_path = args.checks or source.with_suffix(".checks.json")
    output = (args.output or ROOT / "build" / source.stem).resolve()
    try:
        checks = load_checks(checks_path)
        # Publish only a complete, mechanically verified build. Failed attempts leave old output unchanged.
        scratch = ROOT / "build"
        scratch.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".resume-build-", dir=scratch) as temporary:
            stage = Path(temporary)
            pdf = stage / "resume.pdf"
            result = subprocess.run(
                ["typst", "compile", "--root", str(ROOT), str(source), str(pdf)],
                capture_output=True, text=True, check=False,
            )
            if result.returncode or "warning:" in result.stderr.lower():
                detail = result.stderr.strip() or result.stdout.strip() or f"exit code {result.returncode}"
                raise ValueError(f"Typst compilation failed or emitted warnings (no silent font fallback):\n{detail}")
            report = verify(pdf, checks, stage)
            if not report["passed"]:
                raise ValueError("PDF verification failed:\n" + "\n".join(report["errors"]))
            output.mkdir(parents=True, exist_ok=True)
            # Only replace artifacts owned by this command; leave application notes/source alone.
            for previous in output.glob("page-*.png"):
                previous.unlink()
            for artifact in stage.iterdir():
                shutil.copy2(artifact, output / artifact.name)
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(1, f"Build failed; no new verified PDF delivered: {error}\n")
    print(f"PASS: {report['pages']} page(s), {len(report['links'])} distinct URL(s)")
    print(f"PDF: {output / 'resume.pdf'}")
    print(f"Report: {output / 'report.json'}")
    for preview in report["previews"]:
        print(f"Review preview: {output / preview}")
    print("Visual and factual review are still required. No application was submitted.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
