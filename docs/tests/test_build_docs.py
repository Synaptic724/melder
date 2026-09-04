"""Regression checks for source containment, navigation integrity, and docstring presentation."""

import hashlib
import sys
import shutil
import unittest
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from build_docs import DocumentationBuilder
from docstring_format import DocstringFormatter


class BuildContractTests(unittest.TestCase):
    """Exercise real temporary source trees; invalid input must not destroy existing output."""

    def setUp(self) -> None:
        """Create an isolated repository-shaped fixture and register deterministic cleanup."""
        workspaces = Path(__file__).resolve().parents[1] / "_build" / "test-workspaces"
        workspaces.mkdir(parents=True, exist_ok=True)
        # Python's restrictive Windows tempfile ACL can exclude a sandbox token.
        # Inherit the repository's workspace ACL and constrain cleanup explicitly.
        self.root = workspaces / uuid.uuid4().hex
        self.root.mkdir()
        if not self.root.resolve().is_relative_to(workspaces.resolve()):
            raise ValueError("Test workspace escaped its generated root.")
        self.addCleanup(shutil.rmtree, self.root)
        self.docs = self.root / "docs"
        self.docs.mkdir()
        self.manifest = 'schema_version = 1\n'
        definitions = [("index", "Melder", "")]
        definitions.extend(zip(DocumentationBuilder._LEVEL_IDS, DocumentationBuilder._LEVEL_TITLES,
                               ("index",) * 4))
        definitions.append(("contents", "Full Contents", "index"))
        for identifier, title, parent in definitions:
            source = "" if identifier == "contents" else identifier + ".md"
            self.manifest += (f'\n[[page]]\nid = "{identifier}"\ntitle = "{title}"\n'
                              f'source = "{source}"\nparent = "{parent}"\n')
            if source:
                path = self.docs / source
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"# {title}\n\nReal authored content.\n", encoding="utf-8")
        self._save(self.manifest)

    def _save(self, text: str) -> None:
        """Replace only the temporary fixture's navigation source."""
        (self.docs / "navigation.toml").write_text(text, encoding="utf-8")

    def test_invalid_input_preserves_prior_generated_output(self) -> None:
        """Duplicate page IDs must fail before the previous generated site is cleaned."""
        source = DocumentationBuilder(self.root).prepare()
        sentinel = source / "previous.txt"
        sentinel.write_text("keep", encoding="utf-8")
        self._save(self.manifest + '\n[[page]]\nid="index"\ntitle="Duplicate"\nsource="index.md"\nparent=""\n')
        with self.assertRaisesRegex(ValueError, "duplicate"):
            DocumentationBuilder(self.root).prepare()
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")

    def test_source_traversal_is_refused(self) -> None:
        """A page cannot use a path outside the authored documentation root."""
        self._save(self.manifest.replace('source = "index.md"', 'source = "../private.md"', 1))
        with self.assertRaisesRegex(ValueError, "contained relative path"):
            DocumentationBuilder(self.root).prepare()

    def test_generated_root_cannot_be_a_cleanup_target(self) -> None:
        """The output resolver refuses root/traversal spellings before any destructive operation."""
        builder = DocumentationBuilder(self.root)
        for name in (".", "..", "../outside", "C:/outside", "source/../outside"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                builder._output(name)

    def test_private_coordination_asset_is_refused(self) -> None:
        """Asset selection must not publish coordination files under a renamed download path."""
        self._save(self.manifest + '\n[[asset]]\nsource="context_compass/attention_board.md"\ntarget="download.txt"\n')
        with self.assertRaisesRegex(ValueError, "public input roots"):
            DocumentationBuilder(self.root).prepare()

    def test_level_names_and_root_placement_are_enforced(self) -> None:
        """A valid page ID does not permit renaming or burying the owner's learning levels."""
        self._save(self.manifest.replace("🟢 Beginner", "Basics"))
        with self.assertRaisesRegex(ValueError, "README exactly"):
            DocumentationBuilder(self.root).prepare()

    def test_repeat_generation_preserves_contents_and_removes_stale_pages(self) -> None:
        """Identical inputs yield identical page bytes; deleted generated pages cannot linger."""
        builder = DocumentationBuilder(self.root)
        source = builder.prepare()
        before = {path.relative_to(source).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                  for path in source.rglob("*.md")}
        (source / "retired.md").write_text("stale", encoding="utf-8")
        builder.prepare()
        after = {path.relative_to(source).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                 for path in source.rglob("*.md")}
        self.assertEqual(before, after)
        contents = (source / "contents.md").read_text(encoding="utf-8")
        self.assertLess(contents.index("Beginner"), contents.index("Intermediate"))
        self.assertLess(contents.index("Advanced"), contents.index("Expert"))


class DocstringPresentationTests(unittest.TestCase):
    """Keep literal examples intact while converting the repository's known fence formats."""

    def test_legacy_fence_preserves_nested_python(self) -> None:
        """The malformed SpellMap fence shape becomes a valid code block without code loss."""
        result = DocstringFormatter.normalize(
            ["Example:", "`python", "class Service:", "    value = 3", "`", "Contract:"], "Sample")
        self.assertIn(".. code-block:: python", result)
        self.assertIn("    class Service:", result)
        self.assertIn("        value = 3", result)
        self.assertEqual(result[-1], "Contract:")

    def test_unclosed_fence_fails_instead_of_losing_content(self) -> None:
        """A truncated fenced example must produce an actionable failure."""
        with self.assertRaisesRegex(ValueError, "Unclosed python.*Sample"):
            DocstringFormatter.normalize(["```python", "answer = 42"], "Sample")

    def test_inline_code_and_native_rst_are_unchanged(self) -> None:
        """Normal prose/code markup is not rewritten by the fence bridge."""
        lines = ["Return `value`.", "", ".. code-block:: python", "", "    result = 1"]
        self.assertEqual(DocstringFormatter.normalize(lines, "Sample"), lines)


if __name__ == "__main__":
    unittest.main()
