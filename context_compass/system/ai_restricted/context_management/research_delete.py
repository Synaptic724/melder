"""
Delete research artifacts from a lifecycle bucket.

Purpose:
- Provide a deterministic cleanup utility for research artifacts.
- Remove artifacts after explicit user approval or retention decisions.

Contract:
- Operates only within context_compass/user/research.
- Deletes files only; directories are rejected.
- Logs deletions, missing artifacts, and errors.
"""

import argparse
import logging
from pathlib import Path

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
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)


_BUCKETS = ("pending", "ready", "active", "archived", "delete")


def _bucket_names() -> list[str]:
    """
    Return valid research bucket names.

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


def delete_research_items(repo_root: Path, bucket: str, names: list[str]) -> dict:
    """
    Delete research artifacts from a bucket.

    Contract:
    - Skips missing items and reports them in the summary.
    - Refuses to delete directories.

    Args:
        repo_root (Path): Repository root.
        bucket (str): Bucket name.
        names (list[str]): Artifact names or relative paths.

    Returns:
        dict: Summary of deleted, missing, and errored artifacts.
    """
    bucket_dir = _bucket_path(repo_root, bucket)
    bucket_dir.mkdir(parents=True, exist_ok=True)

    deleted: list[str] = []
    missing: list[str] = []
    errors: list[dict] = []

    logger = logging.getLogger(__name__)
    for name in names:
        try:
            target = _resolve_item_path(bucket_dir, name)
        except ValueError as exc:
            errors.append({"name": name, "error": str(exc)})
            continue
        if not target.exists():
            missing.append(name)
            continue
        if not target.is_file():
            errors.append({"name": name, "error": "Artifact is not a file"})
            continue
        _warn_if_non_md(logger, target)
        target.unlink()
        deleted.append(name)

    return {"bucket": bucket, "deleted": deleted, "missing": missing, "errors": errors}


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Delete research artifacts using the command runner contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing deletion summary data.

    Raises:
        None: All errors are captured and returned in the CommandResult.

    Contract:
        - Requires agent_id, bucket, and names.
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
        bucket = require_choice(payload, "bucket", command_name, _bucket_names())
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
        ensure_work_mode(repo_root, work_id, "delete research artifacts")
        summary = delete_research_items(repo_root, bucket, list(names))
        return ok_result(output=summary)
    except Exception as exc:
        return exception_result(command_name, exc)


def main() -> None:
    """
    CLI entrypoint for deleting research artifacts.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """
    parser = argparse.ArgumentParser(description="Delete research artifacts from a bucket")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--bucket", required=True, choices=_bucket_names(), help="Bucket name")
    parser.add_argument("--names", nargs="+", required=True, help="Artifact names or relative paths")
    parser.add_argument("--owner-id", default=None, help="Lock owner id override")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "agent_id": args.agent_id,
        "work_id": args.work_id,
        "bucket": args.bucket,
        "names": args.names,
        "owner_id": args.owner_id,
    }
    context = ExecutionContext(
        command_name="research_delete",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("research_delete failed: %s", result.errors)
        raise SystemExit(1)

    summary = result.output
    logger.info(
        "research delete complete: deleted=%s missing=%s errors=%s",
        len(summary.get("deleted", [])),
        len(summary.get("missing", [])),
        len(summary.get("errors", [])),
    )
    if summary.get("missing"):
        logger.warning("missing artifacts: %s", summary["missing"])
    if summary.get("errors"):
        logger.warning("artifact errors: %s", summary["errors"])


if __name__ == "__main__":
    main()
