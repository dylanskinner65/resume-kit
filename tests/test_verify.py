"""Consumer-visible PDF failures, using actual PDF documents rather than mocks."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from verify import load_checks, verify


class VerifyTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.checks = {"max_pages": 1, "required_text": ["Alex Morgan", "32%"], "expected_links": []}

    def document(self, text="Alex Morgan: cost reduced 32%", pages=1, off_page=False, urls=()):
        path = self.root / "input.pdf"
        with pymupdf.open() as document:
            for _ in range(pages):
                page = document.new_page(width=612, height=792)
                page.insert_text((36, 50), text)
                if off_page:
                    page.insert_text((620, 80), "Clipped accomplishment")
                for index, url in enumerate(urls):
                    page.insert_link({"kind": pymupdf.LINK_URI, "from": pymupdf.Rect(36, 90 + index * 20, 120, 105 + index * 20), "uri": url})
            document.save(path)
        return path

    def check(self, **kwargs):
        return verify(self.document(**kwargs), self.checks, self.root / "output")

    def test_missing_metric_fails_even_when_candidate_name_is_present(self):
        report = self.check(text="Alex Morgan: cost reduced")
        self.assertFalse(report["passed"])
        self.assertIn("Missing required text: 32%", report["errors"])

    def test_text_beyond_page_is_detected_instead_of_silently_clipped(self):
        report = self.check(off_page=True)
        self.assertFalse(report["passed"])
        self.assertTrue(any("text outside page" in error for error in report["errors"]))

    def test_extra_page_fails_configured_limit(self):
        report = self.check(pages=2)
        self.assertFalse(report["passed"])
        self.assertIn("Expected 1..1 pages; found 2", report["errors"])

    def test_replaced_link_fails_even_when_link_count_matches(self):
        self.checks["expected_links"] = ["https://example.com/portfolio"]
        report = self.check(urls=["https://example.com/wrong"])
        self.assertFalse(report["passed"])
        self.assertIn("Missing link: https://example.com/portfolio", report["errors"])
        self.assertIn("Unexpected link: https://example.com/wrong", report["errors"])

    def test_wrapped_link_annotations_do_not_count_as_unexpected_urls(self):
        self.checks["expected_links"] = ["https://example.com/portfolio"]
        report = self.check(urls=["https://example.com/portfolio", "https://example.com/portfolio"])
        self.assertTrue(report["passed"], report["errors"])
        self.assertEqual(report["links"], ["https://example.com/portfolio"])

    def test_line_wrapping_preserves_required_phrase_matching(self):
        self.checks["required_text"] = ["Alex Morgan", "reduced cost 32%"]
        report = self.check(text="Alex Morgan\nreduced cost\n32%")
        self.assertTrue(report["passed"], report["errors"])

    def test_misspelled_check_field_is_not_silently_ignored(self):
        path = self.root / "checks.json"
        path.write_text(json.dumps({"max_pages": 1, "required_text": ["Alex"], "expected_link": []}))
        with self.assertRaisesRegex(ValueError, "exactly"):
            load_checks(path)


if __name__ == "__main__":
    unittest.main()
