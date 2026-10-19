#!/usr/bin/env python3
"""Check PDF artifacts, not the truth of their claims or visual quality."""

import argparse
import json
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urlsplit

import pymupdf


def normalize(text):
    return " ".join(unicodedata.normalize("NFKC", text).replace("\u00ad", "").split())


def load_checks(path):
    checks = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(checks, dict) or set(checks) != {"max_pages", "required_text", "expected_links"}:
        raise ValueError("Checks must contain exactly max_pages, required_text, and expected_links")
    if type(checks["max_pages"]) is not int or checks["max_pages"] < 1:
        raise ValueError("max_pages must be a positive integer")
    for key in ("required_text", "expected_links"):
        if not isinstance(checks[key], list) or not all(isinstance(s, str) and s.strip() for s in checks[key]):
            raise ValueError(f"{key} must be an array of nonblank strings")
    if not checks["required_text"]:
        raise ValueError("required_text must include at least the candidate name")
    return checks


def supported_url(uri):
    parsed = urlsplit(uri)
    return (parsed.scheme in {"https", "http"} and bool(parsed.netloc)) or (
        parsed.scheme == "mailto" and bool(parsed.path) and "@" in parsed.path
    )


def verify(pdf_path, checks, output):
    """Write previews/report and return a report with an explicit passed flag."""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    errors, text_parts, urls, previews = [], [], [], []
    with pymupdf.open(pdf_path) as document:
        page_count = len(document)
        if not 1 <= page_count <= checks["max_pages"]:
            errors.append(f"Expected 1..{checks['max_pages']} pages; found {page_count}")
        for number, page in enumerate(document, 1):
            # Default extraction clips to the page and would hide the overflow we need to detect.
            text_parts.append(page.get_text(clip=pymupdf.INFINITE_RECT()))
            blocks = page.get_text("dict", clip=pymupdf.INFINITE_RECT())["blocks"]
            for block in blocks:
                for line in block.get("lines", []):
                    for span in line["spans"]:
                        if span["text"].strip() and not page.rect.contains(pymupdf.Rect(span["bbox"])):
                            errors.append(f"Page {number}: text outside page: {span['text']!r}")
            for link in page.get_links():
                uri = link.get("uri")
                if uri is None:
                    errors.append(f"Page {number}: non-URL link annotation is not supported")
                    continue
                urls.append(uri)
                if not supported_url(uri):
                    errors.append(f"Page {number}: unsupported or malformed URL: {uri}")
                if not page.rect.contains(link["from"]):
                    errors.append(f"Page {number}: link annotation outside page: {uri}")
            preview = f"page-{number}.png"
            page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5)).save(output / preview)
            previews.append(preview)

    text = "\n".join(text_parts)
    normalized = normalize(text)
    if not normalized:
        errors.append("PDF contains no extractable text")
    for required in checks["required_text"]:
        if normalize(required) not in normalized:
            errors.append(f"Missing required text: {required}")
    actual, expected = set(urls), set(checks["expected_links"])
    for uri in sorted(expected - actual):
        errors.append(f"Missing link: {uri}")
    for uri in sorted(actual - expected):
        errors.append(f"Unexpected link: {uri}")
    report = {
        "passed": not errors,
        "pdf": Path(pdf_path).name,
        "pages": page_count,
        "links": sorted(actual),
        "previews": previews,
        "errors": errors,
        "extracted_text": text,
        "visual_review": "Required: open previews; mechanical checks do not establish visual quality or factual accuracy.",
    }
    (output / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--checks", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="Directory for report.json and page-N.png")
    args = parser.parse_args()
    try:
        report = verify(args.pdf, load_checks(args.checks), args.output)
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(1, f"Verification failed: {error}\n")
    for error in report["errors"]:
        print(error, file=sys.stderr)
    print(f"{'PASS' if report['passed'] else 'FAIL'}: {report['pages']} page(s); report: {args.output / 'report.json'}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
