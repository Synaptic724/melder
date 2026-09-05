"""Protect API completeness and canonical architecture publication boundaries."""

import hashlib
import json
import shutil
import sys
import unittest
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from api_reference import ApiReference
from architecture_reference import ArchitectureReference


class ReferenceTests(unittest.TestCase):
    """Use contained source fixtures so negative cases cannot publish or modify real source."""

    def setUp(self) -> None:
        """Create a generated workspace with inherited Windows permissions and bounded cleanup."""
        parent = Path(__file__).resolve().parents[1] / "_build/test-workspaces"
        parent.mkdir(parents=True, exist_ok=True)
        self.root = parent / uuid.uuid4().hex
        self.root.mkdir()
        if not self.root.resolve().is_relative_to(parent.resolve()):
            raise ValueError("Reference fixture escaped its generated workspace.")
        self.addCleanup(shutil.rmtree, self.root)

    def _api(self) -> Path:
        """Create a facade that fails on import, proving selection is static and side-effect free."""
        package = self.root / "src/melder"
        package.mkdir(parents=True)
        (package / "__init__.py").write_text(
            'raise RuntimeError("must not import")\nfrom melder.core import Service\n__all__ = ["Service"]\n',
            encoding="utf-8",
        )
        (package / "core.py").write_text('class Service:\n    """Public service."""\n', encoding="utf-8")
        docs = self.root / "docs/reference"
        docs.mkdir(parents=True)
        (docs / "api.md").write_text("# API Reference\n", encoding="utf-8")
        configuration = self.root / "docs/api.toml"
        configuration.write_text(
            'schema_version = 1\nfunctions = []\n[[group]]\nid = "binding"\n'
            'title = "Binding"\nguide = "beginner/registration"\nexports = ["Service"]\n',
            encoding="utf-8",
        )
        return configuration

    def _architecture(self, body: str) -> Path:
        """Create a manifest whose LF hashes must survive a CRLF source checkout."""
        directory = self.root / "architecture_and_design"
        directory.mkdir()
        (directory / "README.md").write_text(body, encoding="utf-8")
        (directory / "other.md").write_text("# Other\n", encoding="utf-8")
        diagram = b"flowchart TD\n  A --> B\n"
        svg = b'<svg xmlns="http://www.w3.org/2000/svg"><title>Flow</title></svg>'
        (directory / "flow.mmd").write_bytes(diagram.replace(b"\n", b"\r\n"))
        (directory / "flow.svg").write_bytes(svg)
        manifest = {
            "schema_version": 1,
            "documents": [{"path": "README.md"}, {"path": "other.md"}],
            "diagrams": [{"source": "flow.mmd", "rendered": "flow.svg",
                          "source_sha256": hashlib.sha256(diagram).hexdigest(),
                          "rendered_sha256": hashlib.sha256(svg).hexdigest()}],
        }
        (directory / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        return directory

    def test_public_api_selection_does_not_import_the_package(self) -> None:
        """A raising facade can be inventoried and gets a revision-pinned source route."""
        reference = ApiReference(self.root, self._api(), "abc123")
        self.assertIn("/blob/abc123/src/melder/core.py", reference.bodies["reference/api/binding/service"])
        self.assertEqual(reference.inventory[0]["name"], "Service")

    def test_new_public_export_requires_a_disposition(self) -> None:
        """New package surface cannot silently disappear from the published API inventory."""
        configuration = self._api()
        facade = self.root / "src/melder/__init__.py"
        facade.write_text('from melder.core import Service\n__all__ = ["Service", "NewSurface"]\n', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "NewSurface"):
            ApiReference(self.root, configuration, "abc123")

    def test_duplicate_selection_refuses(self) -> None:
        """One exported name cannot acquire competing canonical reference parents."""
        configuration = self._api()
        configuration.write_text(configuration.read_text(encoding="utf-8").replace(
            'exports = ["Service"]', 'exports = ["Service", "Service"]'), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "selection drift"):
            ApiReference(self.root, configuration, "abc123")

    def test_architecture_downloads_and_document_links_follow_selected_sources(self) -> None:
        """Local drawings are real downloads; manifest documents become local site routes."""
        self._architecture("# Architecture\n\n![Flow](flow.svg)\n[Full size](flow.svg)\n[Next](other.md)\n")
        reference = ArchitectureReference(self.root, "abc123")
        body = reference.bodies["reference/architecture"]
        self.assertIn("{download}`Full size <../media/architecture/flow.svg>`", body)
        self.assertIn("[Next](architecture/other.md)", body)
        self.assertEqual(len(reference.assets), 1)

    def test_architecture_link_examples_remain_literal(self) -> None:
        """A Markdown link inside a displayed code example is never resolved or rewritten."""
        self._architecture("# Architecture\n\n```markdown\n[Example](does-not-exist.md)\n```\n")
        reference = ArchitectureReference(self.root, "abc123")
        self.assertIn("[Example](does-not-exist.md)", reference.bodies["reference/architecture"])

    def test_private_coordination_link_is_refused(self) -> None:
        """A public source document cannot turn a work-state path into a published Git link."""
        private = self.root / "context_compass"
        private.mkdir()
        (private / "attention_board.md").write_text("private work", encoding="utf-8")
        self._architecture("# Architecture\n\n[Work](../context_compass/attention_board.md)\n")
        with self.assertRaisesRegex(ValueError, "private work state"):
            ArchitectureReference(self.root, "abc123")

    def test_stale_diagram_refuses_instead_of_regenerating(self) -> None:
        """A changed drawing cannot be published under an older manifest verification stamp."""
        directory = self._architecture("# Architecture\n")
        (directory / "flow.svg").write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Stale rendered diagram"):
            ArchitectureReference(self.root, "abc123")


if __name__ == "__main__":
    unittest.main()
