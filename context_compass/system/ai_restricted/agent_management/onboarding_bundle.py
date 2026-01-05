"""
Generate a consolidated onboarding bundle of context_compass documentation.

This tool is permitted to run before certification and stores snapshots in user.db.
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Iterable, Optional
from uuid import uuid4

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_string,
    require_choice,
)
from context_compass.system.ai_restricted._shared.command_results import (
    exception_result,
    ok_result,
    payload_error_result,
)
from context_compass.system.ai_restricted._shared.hashing import hash_text
from context_compass.system.ai_restricted._shared.json_io import dump_minified
from context_compass.system.ai_restricted._shared.timeutils import utc_now_iso
from context_compass.system.ai_restricted.database_management import sqlite_query
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)


def _allowed_formats() -> list[str]:
    """
    Return supported output formats.

    Returns:
        list[str]: Supported formats.
    """
    return ["markdown", "json"]


QUERY_WRITE_ONBOARDING_BUNDLE = "write_onboarding_bundle"


def _resolve_actor_id(ctx: ExecutionContext) -> str:
    """
    Resolve the actor identifier for audit fields.

    Args:
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        str: Actor identifier or \"unknown\" when unavailable.
    """

    return ctx.agent_id or "unknown"


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
    return [base / "onboarding" / "AGENTS.md", base / "onboarding" / "agent" / "SKILLS.md"]


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
            paths.append(f"onboarding/agent/{entry}")
        elif entry.startswith("onboarding/agent/"):
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

    skills_path = repo_root / "context_compass" / "onboarding" / "agent" / "SKILLS.md"
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


def _store_bundle_snapshot(
    repo_root: Path, bundle: dict, output_format: str, actor_id: str
) -> str:
    """
    Persist an onboarding bundle snapshot to the user SQLite database.

    Args:
        repo_root (Path): Repository root.
        bundle (dict): Bundle payload to store.
        output_format (str): Output format requested for the bundle.
        actor_id (str): Actor identifier for audit fields.

    Returns:
        str: Bundle identifier recorded in SQLite.

    Raises:
        FileNotFoundError: If the user database is missing.
        ValueError: If the query response is invalid.
        sqlite_query.SqliteQueryError: For unexpected query failures.
    """

    try:
        response = sqlite_query.execute_request(
            repo_root,
            sqlite_query.SqliteQueryRequest(
                scope="user",
                query_name=QUERY_WRITE_ONBOARDING_BUNDLE,
                payload={
                    "bundle": bundle,
                    "bundle_format": output_format,
                },
                actor_id=actor_id,
            ),
        )
    except sqlite_query.SqliteQueryError as exc:
        if exc.code == "db_missing":
            db_path = sqlite_query._resolve_db_path(repo_root, "user")
            raise FileNotFoundError(f"User database not found: {db_path}") from exc
        if exc.code.startswith("payload_"):
            details = exc.details
            raise ValueError(f"{exc.meaning} Details: {details}") from exc
        raise

    result = response.output.get("result")
    if not isinstance(result, dict):
        raise ValueError("onboarding bundle write returned an invalid result payload.")
    bundle_id = result.get("bundle_id")
    if not isinstance(bundle_id, str) or not bundle_id:
        raise ValueError("onboarding bundle write returned an invalid bundle_id.")
    return bundle_id


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


def build_bundle(repo_root: Path) -> dict:
    """
    Build the onboarding bundle payload.

    Args:
        repo_root (Path): Repository root.

    Returns:
        dict: Bundle payload.
    """
    return _bundle_payload(repo_root)


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Generate an onboarding bundle using the command runner contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing bundle content or artifact path.

    Raises:
        None: All errors are returned as CommandResult payloads.

    Contract:
        - format must be markdown or json.
        - output_path is not supported; bundles are stored in SQLite only.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        output_format = require_choice(
            payload, "format", command_name, _allowed_formats()
        )
        output_path_value = optional_string(
            payload, "output_path", command_name=command_name
        )
    except PayloadError as exc:
        return payload_error_result(command_name, exc)
    if output_path_value is not None:
        return payload_error_result(
            command_name,
            PayloadError(
                code="payload_unsupported",
                details={
                    "command_name": command_name,
                    "field": "output_path",
                    "message": "output_path is not supported; onboarding_bundle stores results in SQLite.",
                },
            ),
        )

    try:
        bundle = build_bundle(repo_root)
        actor_id = _resolve_actor_id(ctx)
        bundle_id = _store_bundle_snapshot(
            repo_root=repo_root,
            bundle=bundle,
            output_format=output_format,
            actor_id=actor_id,
        )
        if output_format == "json":
            content = dump_minified(bundle)
        else:
            content = _render_markdown(bundle)
        output = {
            "format": output_format,
            "bundle_id": bundle_id,
            "generated_at": bundle.get("generated_at"),
            "file_count": len(bundle.get("files", [])),
            "missing_count": len(bundle.get("missing", [])),
            "error_count": len(bundle.get("errors", [])),
            "content": content,
        }
        return ok_result(output=output, artifacts=[])
    except Exception as exc:
        return exception_result(command_name, exc)


def main() -> None:
    """
    CLI entrypoint for onboarding bundle generation.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """
    parser = argparse.ArgumentParser(
        description="Generate onboarding bundle from context_compass docs"
    )
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--format", default="markdown", choices=_allowed_formats(), help="Output format")
    parser.add_argument(
        "--output",
        default=None,
        help="Unsupported (returns error); onboarding_bundle stores snapshots in SQLite.",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "format": args.format,
        "output_path": args.output,
    }
    context = ExecutionContext(
        command_name="onboarding_bundle",
        agent_id=None,
        work_id=None,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("onboarding_bundle failed: %s", result.errors)
        raise SystemExit(1)
    output_path = result.output.get("output_path")
    if output_path:
        logger.info("onboarding bundle written: %s", output_path)
        return
    content = result.output.get("content", "")
    sys.stdout.write(content + ("\n" if result.output.get("format") == "json" else ""))


if __name__ == "__main__":
    main()
