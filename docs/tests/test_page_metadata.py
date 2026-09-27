"""Verify metadata ownership, input validation and actual Sphinx HTML escaping."""

import json
import shutil
import subprocess
import sys
import unittest
import uuid
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from curriculum import Curriculum
from example_catalog import ExampleCatalog


class DescriptionTags(HTMLParser):
    """Collect decoded descriptions and public fragment targets from rendered HTML."""

    def __init__(self, content: str) -> None:
        """Parse one document and retain its description tag values in occurrence order."""
        super().__init__(convert_charrefs=True)
        self.values: list[str] = []
        self.identifiers: set[str] = set()
        self.feed(content)
        self.close()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        """Record description metadata after HTML entity decoding has reconstructed the text."""
        attributes = dict(attrs)
        identifier = attributes.get("id")
        if identifier:
            self.identifiers.add(identifier)
        if tag == "meta" and attributes.get("name") == "description":
            self.values.append(attributes.get("content") or "")


class PageMetadataTests(unittest.TestCase):
    """Build a small real catalog/curriculum with no imports of executable lesson code."""

    def setUp(self) -> None:
        """Create an isolated repository-shaped fixture with contained, inherited-permission cleanup."""
        parent = Path(__file__).resolve().parents[1] / "_build/test-workspaces"
        parent.mkdir(parents=True, exist_ok=True)
        self.root = parent / uuid.uuid4().hex
        self.root.mkdir()
        if not self.root.resolve().is_relative_to(parent.resolve()):
            raise ValueError("Metadata fixture escaped the documentation workspace.")
        self.addCleanup(shutil.rmtree, self.root)
        self.docs = self.root / "docs"
        self.docs.mkdir()
        (self.root / "README.md").write_text("# Tour\n\n## Topic\n\nKeep this original paragraph.\n", encoding="utf-8")
        self.catalog_path = self.docs / "catalog.toml"
        self.manifest = 'schema_version = 1\nrepository_url = "https://example.invalid/repo"\nsource_ref = "fixture"\n'
        for number, level in enumerate(ExampleCatalog._LEVELS, 1):
            directory = f"{number:02d}_{level}"
            source = self.root / "UX_and_AIX_experiences" / directory
            source.mkdir(parents=True)
            (source / "01_example.py").write_text(
                f'"""TIER: {level}\nGOAL: Keep the original lesson text.\nSURFACE EXERCISED: example\n"""\n'
                'raise RuntimeError("Documentation must not execute this lesson")\n', encoding="utf-8"
            )
            self.manifest += (f'\n[[level]]\nslug = "{level}"\ndirectory = "{directory}"\n'
                              'sources = ["01_example.py"]\n')
        self.catalog_path.write_text(self.manifest, encoding="utf-8")
        self.curriculum_path = self.docs / "curriculum.toml"
        self.chapter = ('schema_version = 1\n[[chapter]]\nid = "beginner/topic"\n'
                        'title = "Topic"\nlevel = "beginner"\nreadme = "Topic"\n')

    def _catalog_description(self, value: object) -> None:
        """Write a TOML editorial value without interpreting its content as syntax."""
        self.catalog_path.write_text(
            self.manifest + '\n[[lesson]]\nsource = "UX_and_AIX_experiences/01_beginner/01_example.py"\n'
            + "description = " + json.dumps(value, ensure_ascii=False) + "\n", encoding="utf-8"
        )

    def _render(self, catalog: ExampleCatalog, curriculum: Curriculum) -> Path:
        """Render actual generator bodies with their assets and valid fixture navigation."""
        source = self.root / "render-source"
        source.mkdir()
        (source / "conf.py").write_text(
            "extensions = ['myst_parser']\nroot_doc = 'index'\n", encoding="utf-8"
        )
        bodies = dict(catalog.bodies)
        bodies["examples/index"] = "# Examples\n" + bodies["examples/index"]
        bodies.update(curriculum.bodies)
        bodies["contents"] = "# Full contents\n"
        for level in ExampleCatalog._LEVELS:
            bodies[level + "/index"] = "# " + level.title() + "\n"
        for identifier, body in bodies.items():
            destination = source / (identifier + ".md")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(body, encoding="utf-8")
        catalog.write_assets(source)
        (source / "index.md").write_text(
            "# Fixture\n\n```{toctree}\n\n" + "\n".join(bodies) + "\n```\n", encoding="utf-8"
        )
        output = self.root / "html"
        result = subprocess.run(
            [sys.executable, "-m", "sphinx", "-q", "-b", "html", "-W", str(source), str(output)],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return output

    def test_descriptions_survive_real_html_rendering_without_changing_prose(self) -> None:
        """Quotes, Unicode and YAML-looking text remain one literal description in each generator."""
        value = 'Explain "shared" & fresh objects: café.\n---\nrobots: noindex'
        expected = 'Explain "shared" & fresh objects: café. --- robots: noindex'
        self._catalog_description(value)
        self.curriculum_path.write_text(
            self.chapter + "description = " + json.dumps(value, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        catalog = ExampleCatalog(self.root, self.catalog_path)
        curriculum = Curriculum(self.root, self.curriculum_path, catalog)
        output = self._render(catalog, curriculum)
        lesson = (output / "examples/beginner/01-example.html").read_text(encoding="utf-8")
        chapter = (output / "beginner/topic.html").read_text(encoding="utf-8")
        self.assertEqual(DescriptionTags(lesson).values, [expected])
        self.assertEqual(DescriptionTags(chapter).values, [expected])
        self.assertIn("Keep the original lesson text.", lesson)
        self.assertIn("Keep this original paragraph.", chapter)
        self.assertNotIn('name="robots"', lesson + chapter)
        other = (output / "examples/advanced/01-example.html").read_text(encoding="utf-8")
        self.assertEqual(DescriptionTags(other).values, [])

    def test_invalid_lesson_description_names_the_source(self) -> None:
        """Supplied empty/nontext metadata is rejected instead of silently generating bad HTML."""
        for value in ("", "  ", 42, ["fragment"]):
            with self.subTest(value=value):
                self._catalog_description(value)
                with self.assertRaisesRegex(ValueError, "Description for UX_and_AIX_experiences/01_beginner"):
                    ExampleCatalog(self.root, self.catalog_path)

    def test_editorial_title_preserves_the_published_heading_fragment(self) -> None:
        """A distinct search title keeps the old heading address available in actual HTML."""
        self.catalog_path.write_text(
            self.manifest + '\n[[lesson]]\nsource = "UX_and_AIX_experiences/01_beginner/01_example.py"\n'
            'title = "An improved example title"\nlegacy_anchor = "example"\n', encoding="utf-8"
        )
        self.curriculum_path.write_text(self.chapter, encoding="utf-8")
        catalog = ExampleCatalog(self.root, self.catalog_path)
        curriculum = Curriculum(self.root, self.curriculum_path, catalog)
        output = self._render(catalog, curriculum)
        lesson = (output / "examples/beginner/01-example.html").read_text(encoding="utf-8")
        self.assertIn("example", DescriptionTags(lesson).identifiers)
        self.assertIn("An improved example title", lesson)

    def test_invalid_chapter_description_names_the_page(self) -> None:
        """A malformed chapter value fails while source data is loaded, before publication."""
        catalog = ExampleCatalog(self.root, self.catalog_path)
        self.curriculum_path.write_text(self.chapter + "description = 42\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Description for beginner/topic"):
            Curriculum(self.root, self.curriculum_path, catalog)

    def test_authored_chapter_rejects_a_second_description_owner(self) -> None:
        """An authored page cannot receive competing manifest and frontmatter descriptions."""
        catalog = ExampleCatalog(self.root, self.catalog_path)
        authored = self.chapter.replace('readme = "Topic"', 'source = "topic.md"')
        self.curriculum_path.write_text(authored + 'description = "Duplicate owner"\n', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Authored chapter beginner/topic.*source frontmatter"):
            Curriculum(self.root, self.curriculum_path, catalog)


if __name__ == "__main__":
    unittest.main()
