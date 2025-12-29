"""
Generate a consolidated onboarding bundle of context_compass documentation.

This tool is permitted to run before certification and does not mutate repo state.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Iterable, Optional

from context_compass.tools._shared.hashing import hash_text
from context_compass.tools._shared.json_io import dump_minified, write_json_atomic
from context_compass.tools._shared.timeutils import utc_now_iso


def _allowed_formats() -> list[str]:
    """
    Return supported output formats.

    Returns:
        list[str]: Supported formats.
    """
    return ["markdown", "json"]


def _root_docs(repo_root: Path) -> list[Path]:
    """
    Return core documentation files at the repo root.

    Args:
        repo_root (Path): Repository root.

    Returns:
        list[Path]: Root doc paths.
    """
    return [repo_root / "AGENTS.md"]


def _context_compass_docs(repo_root: Path) -> list[Path]:
    """
    Return core context_compass docs.

    Args:
        repo_root (Path): Repository root.

    Returns:
        list[Path]: context_compass core docs.
    """
    base = repo_root / "context_compass"
    return [base / "AGENTS.md", base / "SKILLS.md"]


def _parse_skill_paths(skills_path: Path) -> list[str]:
    """
    Parse skill file paths from SKILLS.md.

    Args:
        skills_path (Path): SKILLS.md path.

    Returns:
        list[str]: Skill paths relative to context_compass.
    """
    if not skills_path.exists():
        return []
    text = skills_path.read_text(encoding="utf-8")
    paths: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        entry = stripped[2:].strip()
        if not entry.endswith(".md"):
            continue
        if entry.startswith("skills/"):
            paths.append(entry)
    return _dedupe_list(paths)


def _dedupe_list(items: Iterable[str]) -> list[str]:
    """
    Deduplicate values while preserving order.

    Args:
        items (Iterable[str]): Input values.

    Returns:
        list[str]: Deduplicated list.
    """
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def _collect_context_compass_markdown(repo_root: Path) -> list[Path]:
    """
    Collect all markdown files under context_compass.

    Args:
        repo_root (Path): Repository root.

    Returns:
        list[Path]: Markdown file paths.
    """
    base = repo_root / "context_compass"
    if not base.exists():
        return []
    paths = sorted(base.rglob("*.md"), key=lambda p: str(p))
    return list(paths)


def _ordered_bundle_paths(repo_root: Path) -> list[Path]:
    """
    Build the ordered list of onboarding bundle paths.

    Args:
        repo_root (Path): Repository root.

    Returns:
        list[Path]: Ordered paths.
    """
    ordered: list[Path] = []
    seen: set[Path] = set()

    def add(path: Path) -> None:
        resolved = path.resolve()
        if resolved in seen:
            return
        seen.add(resolved)
        ordered.append(path)

    for path in _root_docs(repo_root):
        add(path)

    for path in _context_compass_docs(repo_root):
        add(path)

    skills_path = repo_root / "context_compass" / "SKILLS.md"
    for rel in _parse_skill_paths(skills_path):
        add(repo_root / "context_compass" / rel)

    for path in _collect_context_compass_markdown(repo_root):
        add(path)

    return ordered


def _read_file(path: Path) -> tuple[Optional[str], Optional[str]]:
    """
    Read a file and return its content or an error message.

    Args:
        path (Path): File path.

    Returns:
        tuple[Optional[str], Optional[str]]: (content, error).
    """
    try:
        return path.read_text(encoding="utf-8"), None
    except Exception as exc:
        return None, str(exc)


def _bundle_payload(repo_root: Path) -> dict:
    """
    Build the onboarding bundle payload.

    Args:
        repo_root (Path): Repository root.

    Returns:
        dict: Bundle payload.
    """
    now = utc_now_iso()
    files: list[dict] = []
    missing: list[str] = []
    errors: list[dict] = []

    for path in _ordered_bundle_paths(repo_root):
        rel_path = os.path.relpath(path, repo_root).replace("\\", "/")
        if not path.exists():
            missing.append(rel_path)
            continue
        content, error = _read_file(path)
        if error:
            errors.append({"path": rel_path, "error": error})
            continue
        checksum = hash_text(content or "")
        files.append({"path": rel_path, "sha256": checksum, "content": content})

    return {
        "schema_version": 1,
        "generated_at": now,
        "files": files,
        "missing": missing,
        "errors": errors,
    }


def _render_markdown(payload: dict) -> str:
    """
    Render a markdown onboarding bundle.

    Args:
        payload (dict): Bundle payload.

    Returns:
        str: Markdown output.
    """
    lines: list[str] = []
    lines.append("# onboarding_bundle")
    lines.append("")
    lines.append(f"- generated_at: {payload.get('generated_at')}")
    lines.append(f"- file_count: {len(payload.get('files', []))}")
    if payload.get("missing"):
        lines.append(f"- missing: {len(payload.get('missing', []))}")
    if payload.get("errors"):
        lines.append(f"- errors: {len(payload.get('errors', []))}")
    lines.append("")

    for item in payload.get("files", []):
        path = item.get("path")
        lines.append(f"## START {path}")
        lines.append(item.get("content") or "")
        lines.append(f"## END {path}")
        lines.append("")

    if payload.get("missing"):
        lines.append("## MISSING")
        for path in payload["missing"]:
            lines.append(f"- {path}")
        lines.append("")

    if payload.get("errors"):
        lines.append("## ERRORS")
        for error in payload["errors"]:
            lines.append(f"- {error.get('path')}: {error.get('error')}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _write_text_atomic(path: Path, content: str) -> None:
    """
    Atomically write a text file.

    Args:
        path (Path): Destination path.
        content (str): Text content.
    """
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(content, encoding="utf-8")
    os.replace(tmp_path, path)


def build_bundle(repo_root: Path) -> dict:
    """
    Build the onboarding bundle payload.

    Args:
        repo_root (Path): Repository root.

    Returns:
        dict: Bundle payload.
    """
    return _bundle_payload(repo_root)


def main() -> None:
    """
    CLI entrypoint for onboarding bundle generation.
    """
    parser = argparse.ArgumentParser(description="Generate onboarding bundle from context_compass docs")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--format", default="markdown", choices=_allowed_formats(), help="Output format")
    parser.add_argument("--output", default=None, help="Optional output file path")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    payload = build_bundle(repo_root)

    if args.format == "json":
        content = dump_minified(payload)
        if args.output:
            output_path = Path(args.output)
            if not output_path.is_absolute():
                output_path = repo_root / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            write_json_atomic(output_path, payload)
            logger.info("onboarding bundle written: %s", output_path)
            return
        sys.stdout.write(content + "\n")
        return

    content = _render_markdown(payload)
    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = repo_root / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        _write_text_atomic(output_path, content)
        logger.info("onboarding bundle written: %s", output_path)
        return

    sys.stdout.write(content)


if __name__ == "__main__":
    main()
