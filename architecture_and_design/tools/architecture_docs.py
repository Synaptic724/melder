"""
Validate and render the repository's architecture-and-design documentation.

Contract:
- The manifest is the authoritative page/diagram registry.
- Mermaid sources are canonical and SVG files are generated consumers.
- Check mode is read-only and returns every detected problem.
- Render mode invokes an external Mermaid CLI and refreshes manifest hashes.
- The tool depends only on the Python standard library.
"""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Optional


class ArchitectureDocsTool:
    """
    Own validation and rendering for one architecture documentation root.

    Contract:
    - All manifest-controlled paths remain beneath the documentation root.
    - Source anchors remain beneath the repository root.
    - Rendered SVG hashes must match the canonical source/render manifest pair.
    - The class owns no persistent process resources and requires no cleanup.
    """

    _MANIFEST_NAME = "manifest.json"
    _PAGE_METADATA_TOKENS = (
        "Audience:",
        "Depth:",
        "Status:",
        "Verified against:",
        "Last verified:",
        "Diagram source:",
        "Source anchors:",
    )
    _LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
    _EXTERNAL_LINK_PREFIXES = ("http://", "https://", "mailto:", "#")

    def __init__(self, docs_root: Optional[Path] = None) -> None:
        """
        Initialize the tool for one documentation root.

        Args:
            docs_root: Optional architecture-and-design root. The directory above this
                script is used when omitted.

        Returns:
            None.
        """
        selected_root = docs_root or Path(__file__).resolve().parents[1]
        self._docs_root = selected_root.resolve()
        self._repo_root = self._docs_root.parent.resolve()
        self._manifest_path = self._docs_root / self._MANIFEST_NAME

    @property
    def docs_root(self) -> Path:
        """
        Return the documentation root governed by this tool.

        Returns:
            Path: Absolute architecture-and-design directory.
        """
        return self._docs_root

    def _resolve_docs_path(self, relative_path: str) -> Path:
        """
        Resolve and constrain one manifest path to the documentation root.

        Args:
            relative_path: Documentation-root-relative path.

        Returns:
            Path: Resolved absolute path.

        Raises:
            ValueError: If the path escapes the documentation root.
        """
        candidate = (self._docs_root / relative_path).resolve()
        try:
            candidate.relative_to(self._docs_root)
        except ValueError as error:
            raise ValueError(
                f"Documentation path escapes its root: {relative_path}"
            ) from error
        return candidate

    def _resolve_source_anchor(self, relative_path: str) -> Path:
        """
        Resolve and constrain one evidence anchor to the repository root.

        Args:
            relative_path: Repository-root-relative evidence path.

        Returns:
            Path: Resolved absolute path.

        Raises:
            ValueError: If the path escapes the repository root.
        """
        candidate = (self._repo_root / relative_path).resolve()
        try:
            candidate.relative_to(self._repo_root)
        except ValueError as error:
            raise ValueError(f"Source anchor escapes repository: {relative_path}") from error
        return candidate

    def _load_manifest(self) -> dict[str, Any]:
        """
        Load and minimally validate the JSON manifest.

        Returns:
            dict[str, Any]: Mutable manifest object.

        Raises:
            FileNotFoundError: If the manifest does not exist.
            ValueError: If the manifest root or schema is invalid.
        """
        payload = json.loads(self._manifest_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise TypeError("Architecture manifest root must be a JSON object.")
        if payload.get("schema_version") != 1:
            raise ValueError("Architecture manifest schema_version must equal 1.")
        if not isinstance(payload.get("documents"), list):
            raise TypeError("Architecture manifest documents must be a list.")
        if not isinstance(payload.get("diagrams"), list):
            raise TypeError("Architecture manifest diagrams must be a list.")
        return payload

    def _write_manifest(self, manifest: Mapping[str, Any]) -> None:
        """
        Write the manifest deterministically after a render pass.

        Args:
            manifest: Manifest payload containing refreshed hashes.

        Returns:
            None.
        """
        rendered = json.dumps(manifest, indent=2, sort_keys=False) + "\n"
        self._manifest_path.write_text(rendered, encoding="utf-8", newline="\n")

    def _sha256(self, path: Path) -> str:
        """
        Compute the SHA-256 digest of one file's exact bytes.

        Args:
            path: File to hash.

        Returns:
            str: Lowercase hexadecimal digest.
        """
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def _check_document(self, entry: Mapping[str, Any]) -> list[str]:
        """
        Validate one registered Markdown document and its local links.

        Args:
            entry: Manifest document entry.

        Returns:
            list[str]: Validation problems for this document.
        """
        problems: list[str] = []
        relative_path = entry.get("path")
        if not isinstance(relative_path, str):
            return ["Document entry is missing a string path."]
        try:
            path = self._resolve_docs_path(relative_path)
        except ValueError as error:
            return [str(error)]
        if not path.is_file():
            return [f"Registered document is missing: {relative_path}"]

        text = path.read_text(encoding="utf-8")
        metadata_window = "\n".join(text.splitlines()[:30])
        for token in self._PAGE_METADATA_TOKENS:
            if token not in metadata_window:
                problems.append(f"{relative_path} is missing metadata token {token}")

        for match in self._LINK_PATTERN.finditer(text):
            raw_target = match.group(1).strip().strip("<>")
            target = raw_target.split("#", 1)[0]
            if not target or raw_target.startswith(self._EXTERNAL_LINK_PREFIXES):
                continue
            linked_path = (path.parent / target).resolve()
            if not linked_path.exists():
                problems.append(f"{relative_path} has a broken local link: {raw_target}")

        anchors = entry.get("source_anchors", [])
        if not isinstance(anchors, list):
            problems.append(f"{relative_path} source_anchors must be a list.")
            return problems
        for anchor in anchors:
            if not isinstance(anchor, str):
                problems.append(f"{relative_path} has a non-string source anchor.")
                continue
            try:
                anchor_path = self._resolve_source_anchor(anchor)
            except ValueError as error:
                problems.append(str(error))
                continue
            if not anchor_path.exists():
                problems.append(f"{relative_path} source anchor is missing: {anchor}")
        return problems

    def _check_diagram(self, entry: Mapping[str, Any]) -> list[str]:
        """
        Validate one canonical Mermaid source and rendered SVG pair.

        Args:
            entry: Manifest diagram entry.

        Returns:
            list[str]: Validation problems for this diagram.
        """
        problems: list[str] = []
        name = entry.get("name", "<unnamed>")
        source_value = entry.get("source")
        rendered_value = entry.get("rendered")
        if not isinstance(source_value, str) or not isinstance(rendered_value, str):
            return [f"Diagram {name} requires string source and rendered paths."]
        try:
            source = self._resolve_docs_path(source_value)
            rendered = self._resolve_docs_path(rendered_value)
        except ValueError as error:
            return [str(error)]
        if not source.is_file():
            return [f"Diagram source is missing: {source_value}"]
        if not rendered.is_file():
            return [f"Rendered diagram is missing: {rendered_value}"]

        source_text = source.read_text(encoding="utf-8")
        if "accTitle:" not in source_text or "accDescr:" not in source_text:
            problems.append(f"Diagram source lacks accessibility metadata: {source_value}")
        svg_text = rendered.read_text(encoding="utf-8")
        if "<title" not in svg_text or "<desc" not in svg_text:
            problems.append(f"Rendered SVG lacks title/description: {rendered_value}")

        expected_source_hash = entry.get("source_sha256")
        expected_rendered_hash = entry.get("rendered_sha256")
        actual_source_hash = self._sha256(source)
        actual_rendered_hash = self._sha256(rendered)
        if expected_source_hash != actual_source_hash:
            problems.append(f"Diagram source hash is stale: {source_value}")
        if expected_rendered_hash != actual_rendered_hash:
            problems.append(f"Rendered diagram hash is stale: {rendered_value}")
        return problems

    def check(self) -> list[str]:
        """
        Validate all registered documents and diagram pairs without writing.

        Returns:
            list[str]: Every detected validation problem; empty means success.
        """
        try:
            manifest = self._load_manifest()
        except (FileNotFoundError, json.JSONDecodeError, TypeError, ValueError) as error:
            return [str(error)]

        problems: list[str] = []
        for document in manifest["documents"]:
            if not isinstance(document, dict):
                problems.append("Manifest document entries must be objects.")
                continue
            problems.extend(self._check_document(document))
        for diagram in manifest["diagrams"]:
            if not isinstance(diagram, dict):
                problems.append("Manifest diagram entries must be objects.")
                continue
            problems.extend(self._check_diagram(diagram))
        return problems

    def _resolve_renderer(self, requested: Optional[str]) -> str:
        """
        Resolve the Mermaid CLI executable without installing anything.

        Args:
            requested: Explicit executable path/name, or None to use `mmdc` from PATH.

        Returns:
            str: Resolved executable path.

        Raises:
            FileNotFoundError: If no executable can be resolved.
        """
        candidate = requested or "mmdc"
        discovered = shutil.which(candidate)
        if discovered:
            return discovered
        explicit_path = Path(candidate)
        if explicit_path.is_file():
            return str(explicit_path.resolve())
        raise FileNotFoundError(
            "Mermaid CLI was not found. Install @mermaid-js/mermaid-cli or pass --mmdc."
        )

    def render(self, requested_renderer: Optional[str] = None) -> int:
        """
        Render all registered Mermaid sources and refresh manifest hashes.

        Args:
            requested_renderer: Explicit `mmdc` executable path/name.

        Returns:
            int: Number of rendered diagram pairs.

        Raises:
            FileNotFoundError: If the renderer or required inputs are missing.
            RuntimeError: If Mermaid CLI rejects a diagram.
            ValueError: If manifest-controlled paths are invalid.
        """
        manifest = self._load_manifest()
        renderer = self._resolve_renderer(requested_renderer)
        documentation = manifest.get("documentation", {})
        if not isinstance(documentation, dict):
            raise TypeError("Architecture manifest documentation must be an object.")
        config_value = documentation.get("renderer_config")
        if not isinstance(config_value, str):
            raise TypeError("Architecture manifest renderer_config must be a string.")
        config = self._resolve_docs_path(config_value)
        if not config.is_file():
            raise FileNotFoundError(f"Mermaid config is missing: {config_value}")

        rendered_count = 0
        for diagram in manifest["diagrams"]:
            if not isinstance(diagram, dict):
                raise TypeError("Manifest diagram entries must be objects.")
            source_value = diagram.get("source")
            rendered_value = diagram.get("rendered")
            if not isinstance(source_value, str) or not isinstance(rendered_value, str):
                raise TypeError("Diagram entries require string source/rendered paths.")
            source = self._resolve_docs_path(source_value)
            rendered = self._resolve_docs_path(rendered_value)
            rendered.parent.mkdir(parents=True, exist_ok=True)
            command = [
                renderer,
                "-i",
                str(source),
                "-o",
                str(rendered),
                "-c",
                str(config),
                "-b",
                "#ffffff",
            ]
            try:
                subprocess.run(command, check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as error:
                detail = error.stderr.strip() or error.stdout.strip() or str(error)
                raise RuntimeError(f"Mermaid rendering failed for {source_value}: {detail}") from error
            diagram["source_sha256"] = self._sha256(source)
            diagram["rendered_sha256"] = self._sha256(rendered)
            rendered_count += 1

        documentation["last_rendered"] = datetime.now(UTC).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        self._write_manifest(manifest)
        return rendered_count

    def run(self, argv: Optional[Sequence[str]] = None) -> int:
        """
        Execute the command-line interface.

        Args:
            argv: Optional argument sequence excluding the executable name.

        Returns:
            int: Process exit code (`0` success, `1` validation/render failure).
        """
        parser = argparse.ArgumentParser(
            description="Render or validate architecture-and-design documentation."
        )
        subparsers = parser.add_subparsers(dest="command", required=True)
        subparsers.add_parser("check", help="Validate without writing.")
        render_parser = subparsers.add_parser("render", help="Render all Mermaid diagrams.")
        render_parser.add_argument("--mmdc", help="Path or command name for Mermaid CLI.")
        arguments = parser.parse_args(argv)

        if arguments.command == "check":
            problems = self.check()
            if problems:
                sys.stderr.write("\n".join(problems) + "\n")
                return 1
            sys.stdout.write("Architecture documentation check passed.\n")
            return 0

        try:
            count = self.render(arguments.mmdc)
        except (
            FileNotFoundError,
            json.JSONDecodeError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as error:
            sys.stderr.write(str(error) + "\n")
            return 1
        sys.stdout.write(f"Rendered {count} architecture diagram(s).\n")
        return 0


if __name__ == "__main__":
    raise SystemExit(ArchitectureDocsTool().run())
