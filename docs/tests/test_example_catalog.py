"""Verify catalog coverage, source-only parsing, and consistent downloadable collections."""

import hashlib
import shutil
import subprocess
import sys
import unittest
import uuid
import zipfile
from pathlib import Path
from html.parser import HTMLParser

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from example_catalog import ExampleCatalog


class CatalogHtml(HTMLParser):
    """Collect actual rendered card attributes for the Markdown-to-HTML regression."""

    def __init__(self) -> None:
        """Initialize one isolated parser with no external resources."""
        super().__init__()
        self.cards: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, object]]) -> None:
        """Capture card data only after the real HTML parser has reconstructed its attributes."""
        values = {key: value for key, value in attrs if isinstance(value, str)}
        if tag == "li" and "example-item" in values.get("class", "").split():
            self.cards.append(values)


class CatalogContractTests(unittest.TestCase):
    """Use a real four-level fixture whose source would fail if the catalog executed it."""

    def setUp(self) -> None:
        """Create a contained workspace with one declared lesson per level and one helper."""
        parent = Path(__file__).resolve().parents[1] / "_build" / "test-workspaces"
        parent.mkdir(parents=True, exist_ok=True)
        self.root = parent / uuid.uuid4().hex
        self.root.mkdir()
        if not self.root.resolve().is_relative_to(parent.resolve()):
            raise ValueError("Catalog test root escaped its generated directory.")
        self.addCleanup(shutil.rmtree, self.root)
        self.configuration = self.root / "catalog.toml"
        self.manifest = 'schema_version = 1\nrepository_url = "https://example.invalid/project"\nsource_ref = "fixture"\n'
        for number, level in enumerate(ExampleCatalog._LEVELS, 1):
            directory = f"{number:02d}_{level}"
            location = self.root / "UX_and_AIX_experiences" / directory
            location.mkdir(parents=True)
            (location / "01_example.py").write_text(
                f'"""\nTIER: {level}\nGOAL: Bind a service and check its lifecycle.\n'
                'SURFACE EXERCISED: md.Spellbook\n"""\nraise RuntimeError("Do not execute during docs generation")\n',
                encoding="utf-8")
            self.manifest += (f'\n[[level]]\nslug="{level}"\ndirectory="{directory}"\n'
                              'sources=["01_example.py"]\n')
        self.configuration.write_text(self.manifest, encoding="utf-8")
        self.beginner = self.root / "UX_and_AIX_experiences/01_beginner"
        (self.beginner / "_helper.py").write_text('VALUE = "helper"\n', encoding="utf-8")

    def test_inventory_is_complete_without_executing_sources(self) -> None:
        """Source-only construction succeeds even when executing a lesson would raise."""
        catalog = ExampleCatalog(self.root, self.configuration)
        self.assertEqual(len(catalog.lessons), 4)
        self.assertEqual(len({lesson.identifier for lesson in catalog.lessons}), 4)
        self.assertEqual({lesson.level for lesson in catalog.lessons}, set(ExampleCatalog._LEVELS))

    def test_new_unregistered_lesson_is_not_silently_hidden(self) -> None:
        """A new file requires an explicit catalog update."""
        (self.beginner / "02_new.py").write_text("pass\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "unregistered=.*02_new"):
            ExampleCatalog(self.root, self.configuration)

    def test_missing_declared_lesson_is_not_silently_removed(self) -> None:
        """A deleted source cannot disappear from the published curriculum without review."""
        (self.beginner / "01_example.py").unlink()
        with self.assertRaisesRegex(ValueError, "missing=.*01_example"):
            ExampleCatalog(self.root, self.configuration)

    def test_missing_header_is_an_actionable_error(self) -> None:
        """A filename does not substitute for the lesson's declared public-surface metadata."""
        source = self.beginner / "01_example.py"
        source.write_text(source.read_text(encoding="utf-8").replace("SURFACE EXERCISED:", "OLD FIELD:"),
                          encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "missing SURFACE EXERCISED"):
            ExampleCatalog(self.root, self.configuration)

    def test_bundle_includes_helpers_and_the_validated_source_snapshot(self) -> None:
        """Download bytes and digests remain consistent if source changes after metadata loading."""
        catalog = ExampleCatalog(self.root, self.configuration)
        original = (self.beginner / "01_example.py").read_bytes()
        (self.beginner / "01_example.py").write_text("changed after load\n", encoding="utf-8")
        output = self.root / "output"
        output.mkdir()
        catalog.write_assets(output)
        download = output / "downloads/01_beginner/01_example.py"
        self.assertEqual(download.read_bytes(), original)
        self.assertEqual(catalog.lessons[0].digest, hashlib.sha256(original).hexdigest())
        with zipfile.ZipFile(output / "downloads/beginner-examples.zip") as archive:
            self.assertIn("UX_and_AIX_experiences/01_beginner/_helper.py", archive.namelist())
            self.assertEqual(archive.read("UX_and_AIX_experiences/01_beginner/01_example.py"), original)

    def test_multiline_goals_survive_real_sphinx_html_rendering(self) -> None:
        """Blank paragraphs and quotes in source metadata must never break rendered card markup."""
        source = self.beginner / "01_example.py"
        source.write_text(source.read_text(encoding="utf-8").replace(
            "GOAL: Bind a service and check its lifecycle.",
            'GOAL: Bind a "real" service.\n\n      Preserve the second paragraph.'), encoding="utf-8")
        catalog = ExampleCatalog(self.root, self.configuration)
        docs = self.root / "render-source"
        docs.mkdir()
        (docs / "conf.py").write_text("extensions = ['myst_parser']\nroot_doc = 'index'\n", encoding="utf-8")
        (docs / "index.md").write_text("# Catalog\n\n" + catalog._cards("index", catalog.lessons) + "\n",
                                      encoding="utf-8")
        result = subprocess.run([sys.executable, "-m", "sphinx", "-q", "-b", "html", "-W",
                                 str(docs), str(self.root / "rendered")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        parsed = CatalogHtml()
        parsed.feed((self.root / "rendered/index.html").read_text(encoding="utf-8"))
        self.assertEqual(len(parsed.cards), 4)
        self.assertIn('"real" service.', parsed.cards[0]["data-search"])
        self.assertIn("preserve the second paragraph", parsed.cards[0]["data-search"])


if __name__ == "__main__":
    unittest.main()
