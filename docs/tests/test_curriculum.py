"""Protect canonical README section selection from truncation and code-fence confusion."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from curriculum import ReadmeSections
from build_docs import DocumentationBuilder


class ReadmeSelectionTests(unittest.TestCase):
    """Select actual headings without interpreting heading-looking text inside examples."""

    def test_code_headings_do_not_end_the_section(self) -> None:
        """A Python comment beginning with hashes stays inside its selected code block."""
        source = "# Tour\n## First\nProse.\n```python\n## Second\nvalue = 1\n```\n### Detail\nMore.\n## Second\nNext.\n"
        body = ReadmeSections(source).body("First")
        self.assertIn("```python\n## Second\nvalue = 1\n```", body)
        self.assertIn("## Detail", body)
        self.assertNotIn("Next.", body)

    def test_long_outer_fence_contains_shorter_fences(self) -> None:
        """Nested Markdown examples must not introduce false navigation headings."""
        source = "# Tour\n## First\n````markdown\n```python\n## Hidden\n```\n````\n## Next\nDone.\n"
        sections = ReadmeSections(source)
        self.assertIn("## Hidden", sections.body("First"))
        with self.assertRaisesRegex(ValueError, "found 0"):
            sections.body("Hidden")

    def test_changed_heading_refuses_instead_of_silently_dropping_content(self) -> None:
        """A source rename requires an explicit curriculum mapping update."""
        with self.assertRaisesRegex(ValueError, "match exactly once"):
            ReadmeSections("# Tour\n## New name\nContent.").body("Old name")

    def test_duplicate_heading_is_not_arbitrarily_selected(self) -> None:
        """Ambiguous canonical section names are errors, not first-match selection."""
        with self.assertRaisesRegex(ValueError, "found 2"):
            ReadmeSections("## Topic\nOne.\n## Topic\nTwo.").body("Topic")

    def test_unclosed_fence_is_reported(self) -> None:
        """A broken source fence cannot silently hide later curriculum headings."""
        with self.assertRaisesRegex(ValueError, "unclosed code fence"):
            ReadmeSections("# Tour\n```python\n## Hidden")


class CurriculumRouteTests(unittest.TestCase):
    """Check real chapter-to-lesson routes without generating or executing the examples."""

    def test_lessons_link_back_to_the_guides_that_teach_them(self) -> None:
        """Both the established Hello URL and cross-level cluster lesson retain guide routes."""
        builder = DocumentationBuilder(Path(__file__).resolve().parents[2])
        builder.load()
        hello = builder.generated_bodies["examples/hello-melder"]
        self.assertIn("../beginner/hello.md", hello)
        cluster = builder.generated_bodies["examples/intermediate/25-clusters-unique-per-cluster"]
        self.assertIn("../../advanced/clusters.md", cluster)
        self.assertIn("../../intermediate/connected-subsystems.md", cluster)


if __name__ == "__main__":
    unittest.main()
