"""
Move research artifacts between lifecycle buckets.

Purpose:
- Provide a safe, repeatable way to move research artifacts across buckets.
- Keep research artifacts organized for downstream context consumption.

Contract:
- Operates only within context_compass/user/research.
- Preserves relative paths and creates destination directories as needed.
- Logs moved, missing, and conflicting items.
"""

import argparse
import logging
from pathlib import Path
from typing import Optional

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_string,
    require_choice,
    require_string,
)
from context_compass.system.ai_restricted._shared.command_results import (
    exception_result,
    ok_result,
    payload_error_result,
)
from context_compass.system.ai_restricted._shared.certification_guard import ensure_certified
from context_compass.system.ai_restricted._shared.work_mode_guard import ensure_work_mode
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)


_BUCKETS = ("pending", "ready", "active", "archived", "delete")


def _bucket_names() -> list[str]:
    """
    Return valid research bucket names.

    Purpose:
    - Centralize bucket validation for CLI and helper usage.

    Returns:
        list[str]: Allowed bucket names.
    """
    return list(_BUCKETS)


def _research_root(repo_root: Path) -> Path:
    """
    Resolve the research root directory.

    Args:
        repo_root (Path): Repository root.

    Returns:
        Path: Research root path.
    """
    return repo_root / "context_compass" / "user" / "research"


def _bucket_path(repo_root: Path, bucket: str) -> Path:
    """
    Resolve a bucket directory path and validate the bucket name.

    Args:
        repo_root (Path): Repository root.
        bucket (str): Bucket name.

    Returns:
        Path: Bucket directory path.

    Raises:
        ValueError: If the bucket name is invalid.
    """
    normalized = bucket.strip()
    if normalized not in _BUCKETS:
        raise ValueError(f"Invalid bucket: {bucket}")
    return _research_root(repo_root) / normalized


def _validate_relative_name(name: str) -> Path:
    """
    Validate a research artifact name as a relative path.

    Contract:
    - Rejects absolute paths and parent traversal segments.
    - Preserves nested relative paths when provided.

    Args:
        name (str): Input name or relative path.

    Returns:
        Path: Normalized relative path.

    Raises:
        ValueError: If the path is empty or unsafe.
    """
    trimmed = name.strip()
    if not trimmed:
        raise ValueError("Artifact name must not be empty")
    rel = Path(trimmed)
    if rel.is_absolute():
        raise ValueError("Artifact name must be a relative path")
    if any(part in ("..", "") for part in rel.parts):
        raise ValueError("Artifact name contains invalid path segments")
    return rel


def _resolve_item_path(bucket_dir: Path, name: str) -> Path:
    """
    Resolve a research artifact path within a bucket directory.

    Contract:
    - Ensures the resolved path stays within the bucket directory.

    Args:
        bucket_dir (Path): Bucket directory path.
        name (str): Artifact name or relative path.

    Returns:
        Path: Resolved artifact path.

    Raises:
        ValueError: If the resolved path escapes the bucket directory.
    """
    rel = _validate_relative_name(name)
    candidate = (bucket_dir / rel).resolve()
    bucket_root = bucket_dir.resolve()
    try:
        candidate.relative_to(bucket_root)
    except ValueError as exc:
        raise ValueError("Artifact path escapes bucket directory") from exc
    return candidate


def _warn_if_non_md(logger: logging.Logger, path: Path) -> None:
    """
    Warn when a research artifact is not markdown.

    Args:
        logger (logging.Logger): Logger for warnings.
        path (Path): Artifact path.
    """
    if path.suffix.lower() != ".md":
        logger.warning("Non-markdown artifact: %s", path.name)


def move_research_items(
    repo_root: Path,
    source_bucket: str,
    dest_bucket: str,
    names: list[str],
) -> dict:
    """
    Move research artifacts between buckets.

    Contract:
    - Skips missing items and reports them in the summary.
    - Skips items that already exist in the destination.
    - Creates destination subdirectories as needed.

    Args:
        repo_root (Path): Repository root.
        source_bucket (str): Source bucket name.
        dest_bucket (str): Destination bucket name.
        names (list[str]): Artifact names or relative paths.

    Returns:
        dict: Summary of moved, missing, and conflicting artifacts.

    Raises:
        ValueError: If source and destination buckets match.
    """
    if source_bucket == dest_bucket:
        raise ValueError("source and destination buckets must differ")
    source_dir = _bucket_path(repo_root, source_bucket)
    dest_dir = _bucket_path(repo_root, dest_bucket)
    source_dir.mkdir(parents=True, exist_ok=True)
    dest_dir.mkdir(parents=True, exist_ok=True)

    moved: list[str] = []
    missing: list[str] = []
    conflicts: list[str] = []
    errors: list[dict] = []

    logger = logging.getLogger(__name__)
    for name in names:
        try:
            source_path = _resolve_item_path(source_dir, name)
            dest_path = _resolve_item_path(dest_dir, name)
        except ValueError as exc:
            errors.append({"name": name, "error": str(exc)})
            continue
        if not source_path.exists():
            missing.append(name)
            continue
        if not source_path.is_file():
            errors.append({"name": name, "error": "Artifact is not a file"})
            continue
        if dest_path.exists():
            conflicts.append(name)
            continue
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        _warn_if_non_md(logger, source_path)
        source_path.replace(dest_path)
        moved.append(name)

    return {
        "source_bucket": source_bucket,
        "dest_bucket": dest_bucket,
        "moved": moved,
        "missing": missing,
        "conflicts": conflicts,
        "errors": errors,
    }


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Move research artifacts using the ToolCommandAPI contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing the move summary.

    Raises:
        None: All errors are captured and returned in the CommandResult.

    Contract:
        - Requires agent_id, source, dest, and names.
        - Enforces certification and work mode guards.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        agent_id = require_string(payload, "agent_id", command_name)
        work_id = optional_string(payload, "work_id", command_name=command_name)
        source_bucket = require_choice(payload, "source", command_name, _bucket_names())
        dest_bucket = require_choice(payload, "dest", command_name, _bucket_names())
        names = payload.get("names")
        owner_id = optional_string(payload, "owner_id", command_name=command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    if names is None:
        return payload_error_result(
            command_name,
            PayloadError(
                code="payload_missing",
                details={
                    "command_name": command_name,
                    "field": "names",
                    "expected": "list of artifact names",
                },
            ),
        )
    if not isinstance(names, list):
        return payload_error_result(
            command_name,
            PayloadError(
                code="payload_type_error",
                details={
                    "command_name": command_name,
                    "field": "names",
                    "expected": "list",
                    "actual_type": type(names).__name__,
                },
            ),
        )
    if not all(isinstance(item, str) and item.strip() for item in names):
        return payload_error_result(
            command_name,
            PayloadError(
                code="payload_value_error",
                details={
                    "command_name": command_name,
                    "field": "names",
                    "expected": "list of non-empty strings",
                    "actual": names,
                },
            ),
        )

    try:
        ensure_certified(repo_root, owner_id or agent_id)
        ensure_work_mode(repo_root, work_id, "move research artifacts")
        summary = move_research_items(
            repo_root,
            source_bucket,
            dest_bucket,
            list(names),
        )
        return ok_result(output=summary)
    except Exception as exc:
        return exception_result(command_name, exc)


def main() -> None:
    """
    CLI entrypoint for moving research artifacts between buckets.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """
    parser = argparse.ArgumentParser(description="Move research artifacts between buckets")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--source", required=True, choices=_bucket_names(), help="Source bucket")
    parser.add_argument("--dest", required=True, choices=_bucket_names(), help="Destination bucket")
    parser.add_argument("--names", nargs="+", required=True, help="Artifact names or relative paths")
    parser.add_argument("--owner-id", default=None, help="Lock owner id override")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "agent_id": args.agent_id,
        "work_id": args.work_id,
        "source": args.source,
        "dest": args.dest,
        "names": args.names,
        "owner_id": args.owner_id,
    }
    context = ExecutionContext(
        command_name="research_move",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("research_move failed: %s", result.errors)
        raise SystemExit(1)

    summary = result.output
    logger.info(
        "research move complete: moved=%s missing=%s conflicts=%s errors=%s",
        len(summary.get("moved", [])),
        len(summary.get("missing", [])),
        len(summary.get("conflicts", [])),
        len(summary.get("errors", [])),
    )
    if summary.get("missing"):
        logger.warning("missing artifacts: %s", summary["missing"])
    if summary.get("conflicts"):
        logger.warning("destination conflicts: %s", summary["conflicts"])
    if summary.get("errors"):
        logger.warning("artifact errors: %s", summary["errors"])


if __name__ == "__main__":
    main()
