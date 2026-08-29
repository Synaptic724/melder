"""Contract tests for the architecture documentation render/check tool."""

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path
from types import ModuleType
from typing import Any
from unittest.mock import patch

import pytest


def _load_tool_module() -> ModuleType:
    """
    Load the documentation tool from its repository file path.

    Returns:
        ModuleType: Executed architecture tool module.
    """
    repo_root = Path(__file__).resolve().parents[3]
    tool_path = repo_root / "architecture_and_design" / "tools" / "architecture_docs.py"
    spec = importlib.util.spec_from_file_location("architecture_docs_tool", tool_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha256(path: Path) -> str:
    """
    Hash one fixture file exactly as the production tool does.

    Args:
        path: Fixture file.

    Returns:
        str: Lowercase hexadecimal SHA-256 digest.
    """
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _build_fixture_tree(tmp_path: Path) -> tuple[ModuleType, Any, Path, dict[str, Any]]:
    """
    Build one internally consistent documentation fixture.

    Args:
        tmp_path: Pytest-owned temporary root.

    Returns:
        tuple[ModuleType, Any, Path, dict[str, Any]]: Tool module, tool instance,
        documentation root, and mutable manifest payload.
    """
    module = _load_tool_module()
    repo_root = tmp_path / "repo"
    docs_root = repo_root / "architecture_and_design"
    source_dir = docs_root / "diagrams" / "source"
    rendered_dir = docs_root / "diagrams" / "rendered"
    source_dir.mkdir(parents=True)
    rendered_dir.mkdir(parents=True)
    (repo_root / "evidence.txt").write_text("evidence\n", encoding="utf-8")
    source = source_dir / "sample.mmd"
    source.write_text(
        "flowchart LR\naccTitle: Sample\naccDescr: Accessible sample\nA --> B\n",
        encoding="utf-8",
    )
    rendered = rendered_dir / "sample.svg"
    rendered.write_text(
        '<svg viewBox="0 0 10 10"><title>Sample</title><desc>Accessible sample</desc></svg>\n',
        encoding="utf-8",
    )
    (docs_root / "diagrams" / "config.json").write_text("{}\n", encoding="utf-8")
    (docs_root / "README.md").write_text(
        "# Sample\n\n"
        "<!--\n"
        "Audience: evaluator\n"
        "Depth: high\n"
        "Status: current\n"
        "Verified against: fixture\n"
        "Last verified: 2026-08-29\n"
        "Diagram source: diagrams/source/sample.mmd\n"
        "Source anchors: evidence.txt\n"
        "-->\n\n"
        "![Sample](diagrams/rendered/sample.svg)\n"
        "[Source](diagrams/source/sample.mmd)\n",
        encoding="utf-8",
    )
    manifest: dict[str, Any] = {
        "schema_version": 1,
        "documentation": {
            "renderer_config": "diagrams/config.json",
            "last_rendered": None,
        },
        "documents": [
            {
                "path": "README.md",
                "source_anchors": ["evidence.txt"],
            }
        ],
        "diagrams": [
            {
                "name": "sample",
                "source": "diagrams/source/sample.mmd",
                "rendered": "diagrams/rendered/sample.svg",
                "source_sha256": _sha256(source),
                "rendered_sha256": _sha256(rendered),
            }
        ],
    }
    (docs_root / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    tool = module.ArchitectureDocsTool(docs_root)
    return module, tool, docs_root, manifest


def test_docs_root_is_resolved(tmp_path: Path) -> None:
    """The configured documentation root is stored as an absolute path."""
    _module, tool, docs_root, _manifest = _build_fixture_tree(tmp_path)
    assert tool.docs_root == docs_root.resolve()


def test_clean_fixture_passes_check(tmp_path: Path) -> None:
    """A complete page/diagram/source-anchor fixture has no validation problems."""
    _module, tool, _docs_root, _manifest = _build_fixture_tree(tmp_path)
    assert tool.check() == []


def test_missing_manifest_is_reported(tmp_path: Path) -> None:
    """Check mode reports a missing manifest rather than raising."""
    module = _load_tool_module()
    tool = module.ArchitectureDocsTool(tmp_path / "missing")
    problems = tool.check()
    assert len(problems) == 1
    assert "manifest.json" in problems[0]


def test_invalid_manifest_schema_is_reported(tmp_path: Path) -> None:
    """An unsupported schema version fails the manifest contract."""
    _module, tool, docs_root, manifest = _build_fixture_tree(tmp_path)
    manifest["schema_version"] = 2
    (docs_root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    assert "schema_version" in tool.check()[0]


def test_missing_registered_document_is_reported(tmp_path: Path) -> None:
    """A document registry entry cannot point at a missing page."""
    _module, tool, docs_root, _manifest = _build_fixture_tree(tmp_path)
    (docs_root / "README.md").unlink()
    assert any("Registered document is missing" in item for item in tool.check())


def test_missing_page_metadata_is_reported(tmp_path: Path) -> None:
    """Every page must carry the shared metadata contract near its start."""
    _module, tool, docs_root, _manifest = _build_fixture_tree(tmp_path)
    (docs_root / "README.md").write_text("# Missing metadata\n", encoding="utf-8")
    assert any("Audience:" in item for item in tool.check())


def test_broken_local_markdown_link_is_reported(tmp_path: Path) -> None:
    """Local Markdown links must resolve relative to the page containing them."""
    _module, tool, docs_root, _manifest = _build_fixture_tree(tmp_path)
    page = docs_root / "README.md"
    page.write_text(page.read_text(encoding="utf-8") + "[Broken](missing.md)\n", encoding="utf-8")
    assert any("broken local link" in item for item in tool.check())


def test_external_markdown_links_are_allowed(tmp_path: Path) -> None:
    """HTTP links remain outside local path validation."""
    _module, tool, docs_root, _manifest = _build_fixture_tree(tmp_path)
    page = docs_root / "README.md"
    page.write_text(page.read_text(encoding="utf-8") + "[Web](https://example.com)\n", encoding="utf-8")
    assert tool.check() == []


def test_missing_source_anchor_is_reported(tmp_path: Path) -> None:
    """Evidence paths registered for a page must exist in the repository."""
    _module, tool, docs_root, manifest = _build_fixture_tree(tmp_path)
    manifest["documents"][0]["source_anchors"] = ["missing.py"]
    (docs_root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    assert any("source anchor is missing" in item for item in tool.check())


def test_document_path_escape_is_rejected(tmp_path: Path) -> None:
    """Manifest document paths cannot escape the documentation root."""
    _module, tool, docs_root, manifest = _build_fixture_tree(tmp_path)
    manifest["documents"][0]["path"] = "../evidence.txt"
    (docs_root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    assert any("escapes its root" in item for item in tool.check())


def test_missing_diagram_accessibility_metadata_is_reported(tmp_path: Path) -> None:
    """Canonical Mermaid sources require accessible title and description fields."""
    _module, tool, docs_root, manifest = _build_fixture_tree(tmp_path)
    source = docs_root / "diagrams" / "source" / "sample.mmd"
    source.write_text("flowchart LR\nA --> B\n", encoding="utf-8")
    manifest["diagrams"][0]["source_sha256"] = _sha256(source)
    (docs_root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    assert any("accessibility metadata" in item for item in tool.check())


def test_missing_svg_accessibility_metadata_is_reported(tmp_path: Path) -> None:
    """Rendered SVGs require title and description elements."""
    _module, tool, docs_root, manifest = _build_fixture_tree(tmp_path)
    rendered = docs_root / "diagrams" / "rendered" / "sample.svg"
    rendered.write_text('<svg viewBox="0 0 10 10"></svg>\n', encoding="utf-8")
    manifest["diagrams"][0]["rendered_sha256"] = _sha256(rendered)
    (docs_root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    assert any("lacks title/description" in item for item in tool.check())


def test_source_hash_drift_is_reported(tmp_path: Path) -> None:
    """Editing Mermaid source without rendering makes the manifest stale."""
    _module, tool, docs_root, _manifest = _build_fixture_tree(tmp_path)
    source = docs_root / "diagrams" / "source" / "sample.mmd"
    source.write_text(source.read_text(encoding="utf-8") + "B --> C\n", encoding="utf-8")
    assert any("source hash is stale" in item for item in tool.check())


def test_rendered_hash_drift_is_reported(tmp_path: Path) -> None:
    """Editing generated SVG bytes without a render pass makes the manifest stale."""
    _module, tool, docs_root, _manifest = _build_fixture_tree(tmp_path)
    rendered = docs_root / "diagrams" / "rendered" / "sample.svg"
    rendered.write_text(rendered.read_text(encoding="utf-8") + "<!-- drift -->\n", encoding="utf-8")
    assert any("Rendered diagram hash is stale" in item for item in tool.check())


def test_render_requires_an_available_mermaid_cli(tmp_path: Path) -> None:
    """Render mode fails loudly when the requested executable cannot resolve."""
    _module, tool, _docs_root, _manifest = _build_fixture_tree(tmp_path)
    with pytest.raises(FileNotFoundError, match="Mermaid CLI was not found"):
        tool.render("definitely-not-a-real-mermaid-command")


def test_render_refreshes_svg_and_manifest_hashes(tmp_path: Path) -> None:
    """A successful renderer call replaces SVG output and records current hashes."""
    module, tool, docs_root, _manifest = _build_fixture_tree(tmp_path)
    fake_renderer = docs_root / "fake-mmdc.exe"
    fake_renderer.write_text("fixture\n", encoding="utf-8")

    def fake_run(command: list[str], **_kwargs: Any) -> subprocess.CompletedProcess[str]:
        """Write accessible SVG output at the requested CLI destination."""
        output_path = Path(command[command.index("-o") + 1])
        output_path.write_text(
            '<svg viewBox="0 0 10 10"><title>Rendered</title><desc>Rendered fixture</desc></svg>\n',
            encoding="utf-8",
        )
        return subprocess.CompletedProcess(command, 0, "", "")

    with patch.object(module.subprocess, "run", side_effect=fake_run) as runner:
        assert tool.render(str(fake_renderer)) == 1
    runner.assert_called_once()
    manifest = json.loads((docs_root / "manifest.json").read_text(encoding="utf-8"))
    diagram = manifest["diagrams"][0]
    assert diagram["source_sha256"] == _sha256(
        docs_root / "diagrams" / "source" / "sample.mmd"
    )
    assert diagram["rendered_sha256"] == _sha256(
        docs_root / "diagrams" / "rendered" / "sample.svg"
    )
    assert manifest["documentation"]["last_rendered"].endswith("Z")


def test_cli_check_returns_success_for_clean_tree(tmp_path: Path) -> None:
    """The CLI returns zero for a clean manifest-controlled tree."""
    _module, tool, _docs_root, _manifest = _build_fixture_tree(tmp_path)
    assert tool.run(["check"]) == 0


def test_cli_check_returns_failure_for_drift(tmp_path: Path) -> None:
    """The CLI returns one when validation detects source drift."""
    _module, tool, docs_root, _manifest = _build_fixture_tree(tmp_path)
    source = docs_root / "diagrams" / "source" / "sample.mmd"
    source.write_text(source.read_text(encoding="utf-8") + "B --> C\n", encoding="utf-8")
    assert tool.run(["check"]) == 1
