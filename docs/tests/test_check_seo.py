"""Exercise actual local publication outcomes without network or search-engine assumptions."""

import html
import json
import os
import shutil
import subprocess
import sys
import unittest
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from check_seo import SeoCheck, SeoMetadata, SeoReport


class SeoCheckTests(unittest.TestCase):
    """Audit synthetic generated sites and CLI behavior inside one contained workspace per test."""

    _BASE = "https://example.invalid/en/latest/"

    def setUp(self) -> None:
        """Create a fixture with inherited Windows permissions and explicit cleanup containment."""
        parent = Path(__file__).resolve().parents[1] / "_build/test-workspaces"
        parent.mkdir(parents=True, exist_ok=True)
        self.root = parent / uuid.uuid4().hex
        self.root.mkdir()
        if not self.root.resolve().is_relative_to(parent.resolve()):
            raise ValueError("SEO fixture escaped the generated workspace.")
        self.addCleanup(shutil.rmtree, self.root)

    @classmethod
    def page(cls, name: str = "index.html", title: str = "Melder", description: Optional[str] = "An example.",
             extra: str = "") -> str:
        """Return an ordinary HTML document with one explicit canonical and optional description."""
        meta = "" if description is None else f'<meta name="description" content="{html.escape(description, quote=True)}">'
        return (f'<html lang="en"><head><title>{html.escape(title)}</title>'
                f'<link rel="canonical" href="{cls._BASE}{name}">{meta}{extra}'
                '</head><body><h1>Melder</h1></body></html>')

    def site(self, pages: dict[str, str], urls: Optional[list[str]] = None) -> None:
        """Write the supplied fixture pages and a namespaced page sitemap."""
        for name, content in pages.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        sitemap = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
        for url in urls if urls is not None else [self._BASE + name for name in pages]:
            entry = ET.SubElement(sitemap, "url")
            ET.SubElement(entry, "loc").text = url
        ET.ElementTree(sitemap).write(self.root / "sitemap.xml", encoding="utf-8", xml_declaration=True)

    @staticmethod
    def messages(report: SeoReport) -> list[str]:
        """Expose observed issue text for behavior assertions independent of internal parser state."""
        return [issue["message"] for issue in report["issues"]]

    def test_valid_site_needs_no_local_robots_override(self) -> None:
        """A valid RTD build passes without replacing the platform's root robots.txt file."""
        self.site({"index.html": self.page()})
        report = SeoCheck(self.root, self._BASE, ("index.html",)).run()
        self.assertEqual((report["content_pages"], report["errors"], report["warnings"]), (1, 0, 0))

    def test_description_requirement_is_an_explicit_policy(self) -> None:
        """Optional metadata warns, while the same absent value fails a required-page policy."""
        self.site({"index.html": self.page(description=None)})
        optional = SeoCheck(self.root, self._BASE).run()
        required = SeoCheck(self.root, self._BASE, ("index.html",)).run()
        self.assertEqual((optional["errors"], optional["warnings"]), (0, 1))
        self.assertEqual((required["errors"], required["warnings"]), (1, 0))

    def test_duplicate_titles_fail_but_repeated_descriptions_warn(self) -> None:
        """Shared titles are ambiguous publication results; descriptions remain editorial warnings."""
        self.site({"index.html": self.page(), "guide.html": self.page("guide.html", title=" MELDER ")})
        report = SeoCheck(self.root, self._BASE).run()
        self.assertTrue(any("Duplicate title" in message for message in self.messages(report)))
        self.assertTrue(any(issue["level"] == "warning" and "Duplicate description" in issue["message"]
                            for issue in report["issues"]))

    def test_wrong_or_multiple_canonicals_fail(self) -> None:
        """Canonical ownership and version-local destinations must be unambiguous."""
        for content in (self.page("wrong.html"), self.page(extra='<link rel="canonical" href="other">')):
            with self.subTest(content=content):
                self.site({"index.html": content})
                report = SeoCheck(self.root, self._BASE).run()
                self.assertTrue(any("canonical" in message.lower() for message in self.messages(report)))
                self.assertGreater(report["errors"], 0)

    def test_missing_title_cannot_be_satisfied_by_body_markup(self) -> None:
        """A title outside head cannot disguise an absent document title."""
        content = self.page().replace("<title>Melder</title>", "").replace("<body>", "<body><title>Fake</title>")
        self.site({"index.html": content})
        self.assertTrue(any("nonempty title" in message for message in self.messages(SeoCheck(self.root, self._BASE).run())))

    def test_duplicate_description_tags_fail(self) -> None:
        """Two generators cannot publish competing description tags on the same page."""
        self.site({"index.html": self.page(extra='<meta name="description" content="Second">')})
        self.assertTrue(any("More than one description" in message
                            for message in self.messages(SeoCheck(self.root, self._BASE).run())))

    def test_noindex_is_allowed_only_for_intentional_previews(self) -> None:
        """Robots and googlebot directives fail public mode but remain visible in preview reports."""
        for name, value in (("robots", "NOINDEX,follow"), ("googlebot", "none")):
            with self.subTest(name=name):
                self.site({"index.html": self.page(extra=f'<meta name="{name}" content="{value}">')})
                public = SeoCheck(self.root, self._BASE).run()
                preview = SeoCheck(self.root, self._BASE, allow_noindex=True).run()
                self.assertTrue(any("Unexpected noindex" in message for message in self.messages(public)))
                self.assertEqual(preview["errors"], 0)
                self.assertTrue(preview["pages"][0]["noindex"])

    def test_sitemap_destinations_and_inclusion_are_checked(self) -> None:
        """Wrong hosts, missing destinations, traversal, queries, omissions and duplicates are failures."""
        cases = (
            (["https://elsewhere.invalid/index.html"], "outside the expected base"),
            ([self._BASE + "absent.html"], "existing local file"),
            ([self._BASE + "../outside.html"], "existing local file"),
            ([self._BASE + "index.html?q=test"], "Query or fragment"),
            ([], "Content page missing"),
            ([self._BASE + "index.html", self._BASE + "index.html"], "Duplicate sitemap URL"),
        )
        for urls, expected in cases:
            with self.subTest(expected=expected):
                self.site({"index.html": self.page()}, urls)
                self.assertTrue(any(expected in message
                                    for message in self.messages(SeoCheck(self.root, self._BASE).run())))

    def test_missing_or_wrong_sitemap_shape_fails(self) -> None:
        """A missing sitemap and a version index are not accepted as the expected page urlset."""
        (self.root / "index.html").write_text(self.page(), encoding="utf-8")
        self.assertTrue(any("Missing sitemap" in message
                            for message in self.messages(SeoCheck(self.root, self._BASE).run())))
        (self.root / "sitemap.xml").write_text('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"/>')
        self.assertTrue(any("page-level sitemap" in message
                            for message in self.messages(SeoCheck(self.root, self._BASE).run())))

    def test_empty_audit_and_unmatched_globs_fail(self) -> None:
        """Empty or misspelled audit scopes cannot silently claim successful coverage."""
        self.site({})
        empty = SeoCheck(self.root, self._BASE, ("missing/*.html",)).run()
        self.assertTrue(any("No content HTML" in message for message in self.messages(empty)))
        self.assertTrue(any("matched no page" in message for message in self.messages(empty)))

    def test_utility_pages_are_not_public_content_requirements(self) -> None:
        """Source, search and download HTML may omit SEO metadata without failing content policy."""
        self.site({"index.html": self.page()})
        for name in ("search.html", "_modules/example.html", "downloads/example.html"):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("<html><body>Utility</body></html>", encoding="utf-8")
        report = SeoCheck(self.root, self._BASE).run()
        self.assertEqual((report["content_pages"], report["errors"]), (1, 0))

    def test_report_survives_a_later_run(self) -> None:
        """Reusing an audit instance cannot mutate the result already returned to its caller."""
        self.site({"index.html": self.page()})
        check = SeoCheck(self.root, self._BASE)
        first = check.run()
        self.site({"index.html": self.page(description=None)})
        second = check.run()
        self.assertEqual(first["pages"][0]["description"], "An example.")
        self.assertEqual(first["issues"], [])
        self.assertEqual(second["warnings"], 1)

    def test_invalid_inputs_and_policy_are_rejected(self) -> None:
        """Bad roots/base URLs and malformed policy values are input failures, not valid audits."""
        for base in ("/relative/", "ftp://example.invalid/", self._BASE + "?x=1", self._BASE + "#part"):
            with self.subTest(base=base), self.assertRaises(ValueError):
                SeoCheck(self.root, base)
        with self.assertRaises(ValueError):
            SeoCheck(self.root / "missing", self._BASE)
        policy = self.root / "seo.toml"
        policy.write_text('schema_version = 1\nrequired_descriptions = ["index.html"]\n')
        self.assertEqual(SeoCheck.policy_patterns(policy), ("index.html",))
        policy.write_text('schema_version = 1\nrequired_descriptions = [42]\n')
        with self.assertRaises(ValueError):
            SeoCheck.policy_patterns(policy)

    def test_metadata_decodes_entities_and_ignores_body_directives(self) -> None:
        """Parsed text reflects human content; body metadata cannot introduce indexing policy."""
        content = self.page(title='A & B', description='A "quoted" café').replace(
            "<body>", '<body><meta name="robots" content="noindex">'
        )
        metadata = SeoMetadata(content)
        self.assertEqual(metadata.titles, ["A & B"])
        self.assertEqual(metadata.descriptions, ['A "quoted" café'])
        self.assertEqual(metadata.robots, [])

    def test_cli_reports_success_policy_failure_and_input_failure(self) -> None:
        """CLI exit codes and JSON reflect actual policy outcomes, including RTD external previews."""
        self.site({"index.html": self.page(extra='<meta name="robots" content="noindex">')})
        command = [sys.executable, str(Path(__file__).resolve().parents[1] / "tools/check_seo.py"),
                   str(self.root), "--base-url", self._BASE, "--json", str(self.root / "report.json")]
        environment = dict(os.environ)
        environment.pop("READTHEDOCS_VERSION_TYPE", None)
        public = subprocess.run(command, capture_output=True, text=True, env=environment)
        self.assertEqual(public.returncode, 1, public.stdout + public.stderr)
        environment["READTHEDOCS_VERSION_TYPE"] = "external"
        preview = subprocess.run(command, capture_output=True, text=True, env=environment)
        self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
        report = json.loads((self.root / "report.json").read_text(encoding="utf-8"))
        self.assertTrue(report["allow_noindex"])
        (self.root / "sitemap.xml").write_text("<not-valid", encoding="utf-8")
        unreadable = subprocess.run(command, capture_output=True, text=True, env=environment)
        self.assertEqual(unreadable.returncode, 2, unreadable.stdout + unreadable.stderr)


if __name__ == "__main__":
    unittest.main()
