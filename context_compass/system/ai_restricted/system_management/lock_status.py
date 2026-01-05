"""
List lease locks filtered by owner or resource criteria.
"""

import argparse
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from context_compass.system.ai_restricted._shared import branch_paths
from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_int,
    optional_string,
    require_choice,
    require_string,
)
from context_compass.system.ai_restricted._shared.command_results import (
    error_result,
    exception_result,
    ok_result,
    payload_error_result,
)
from context_compass.system.ai_restricted._shared.certification_guard import ensure_certified
from context_compass.system.ai_restricted._shared.work_mode_guard import ensure_work_mode
from context_compass.system.ai_restricted.database_management.orm_session import (
    sqlite_session,
    system_db_path,
)
from context_compass.system.ai_restricted.database_management.system_orm_models import LeaseLock
from context_compass.system.ai_restricted.system_management import lease
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)


def _kind_choices() -> list[str]:
    """
    Return the supported lock kinds.

    Returns:
        list[str]: Allowed lock kind values.
    """
    return ["file", "dir", "resource"]


def _resolve_branch(repo_root: Path, branch_name: Optional[str]) -> str:
    """
    Resolve the branch name for file/dir lock resources.

    Args:
        repo_root (Path): Repository root.
        branch_name (Optional[str]): Optional branch override.

    Returns:
        str: Active branch name.

    Raises:
        FileNotFoundError: If the current branch is missing.
        ValueError: If the stored branch name is invalid.
    """
    if branch_name:
        return branch_name
    return branch_paths.load_current_branch(repo_root)


def _resource_from_kind(
    repo_root: Path,
    kind: str,
    path_value: Optional[str],
    resource_key: Optional[str],
    branch_name: Optional[str],
) -> Path:
    """
    Build a lease resource key from the lock kind and path inputs.

    Args:
        repo_root (Path): Repository root.
        kind (str): Lock kind (file, dir, resource).
        path_value (Optional[str]): Repo-relative path for file/dir locks.
        resource_key (Optional[str]): Explicit resource key for resource locks.
        branch_name (Optional[str]): Optional branch override.

    Returns:
        Path: Logical resource key wrapped as a Path.

    Raises:
        ValueError: If required fields are missing or invalid.
    """
    if kind == "resource":
        if not resource_key:
            raise ValueError("resource key is required for kind=resource.")
        return Path(resource_key)
    if not path_value:
        raise ValueError("path is required for file/dir locks.")
    resolved_branch = _resolve_branch(repo_root, branch_name)
    prefix = "file_ctx" if kind == "file" else "dir_ctx"
    return Path(f"{prefix}::{resolved_branch}::{path_value}")


def _normalize_resource_key(
    repo_root: Path,
    kind: Optional[str],
    path_value: Optional[str],
    resource_key: Optional[str],
    branch_name: Optional[str],
) -> Optional[str]:
    """
    Normalize a resource key for querying lease locks.

    Args:
        repo_root (Path): Repository root.
        kind (Optional[str]): Lock kind when path_value is provided.
        path_value (Optional[str]): Repo-relative path for file/dir locks.
        resource_key (Optional[str]): Explicit resource key for resource locks.
        branch_name (Optional[str]): Optional branch override.

    Returns:
        Optional[str]: Normalized resource key or None when no resource filter is set.

    Raises:
        ValueError: If path/resource inputs are inconsistent.
    """
    if not path_value and not resource_key:
        return None
    if not kind:
        raise ValueError("kind is required when filtering by path/resource.")
    resource = _resource_from_kind(repo_root, kind, path_value, resource_key, branch_name)
    resource_type = lease._infer_resource_type(resource)
    return lease._normalize_resource_key(repo_root, resource, resource_type)


def _serialize_lock(row: LeaseLock) -> Dict[str, Any]:
    """
    Convert a LeaseLock ORM row into a response payload.

    Args:
        row (LeaseLock): ORM row instance.

    Returns:
        Dict[str, Any]: Serialized lock payload.
    """
    return {
        "lock_id": row.lock_id,
        "repo_id": row.repo_id,
        "resource_type": row.resource_type,
        "resource_key": row.resource_key,
        "owner_id": row.owner_id,
        "schema_version": row.schema_version,
        "work_id": row.work_id,
        "ticket_id": row.ticket_id,
        "lock_group_id": row.lock_group_id,
        "created_at": row.created_at,
        "heartbeat_at": row.heartbeat_at,
        "expires_at": row.expires_at,
        "updated_at": row.updated_at,
        "created_by": row.created_by,
        "updated_by": row.updated_by,
    }


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    List lease locks using the command runner contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing matching lease locks.

    Raises:
        None: Errors are returned as CommandResult payloads.

    Contract:
        - Requires agent_id and work_id.
        - Supports filtering by owner_id, resource key, and lock identifiers.
        - Returns locks ordered by expires_at then lock_id.
    """
    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        agent_id = require_string(payload, "agent_id", command_name)
        work_id = require_string(payload, "work_id", command_name)
        owner_id = optional_string(payload, "owner_id", command_name=command_name)
        kind = optional_string(payload, "kind", command_name=command_name)
        path_value = optional_string(payload, "path", command_name=command_name)
        resource_key = optional_string(payload, "resource", command_name=command_name)
        branch_name = optional_string(payload, "branch", command_name=command_name)
        lock_group_id = optional_string(payload, "lock_group_id", command_name=command_name)
        ticket_id = optional_string(payload, "ticket_id", command_name=command_name)
        work_filter = optional_string(payload, "lock_work_id", command_name=command_name)
        limit_value = optional_int(payload, "limit", command_name=command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    if kind is not None and kind not in _kind_choices():
        return payload_error_result(
            command_name,
            PayloadError(
                code="payload_value_error",
                details={
                    "command_name": command_name,
                    "field": "kind",
                    "expected": f"one of {_kind_choices()}",
                    "actual": kind,
                },
            ),
        )
    if limit_value is not None and limit_value < 1:
        return error_result(
            code="payload_value_error",
            meaning="limit must be a positive integer.",
            details={"command_name": command_name, "limit": limit_value},
        )

    try:
        normalized_resource = _normalize_resource_key(
            repo_root, kind, path_value, resource_key, branch_name
        )
    except (ValueError, FileNotFoundError) as exc:
        return error_result(
            code="resource_invalid",
            meaning="Resource filter could not be resolved.",
            details={"command_name": command_name, "error": str(exc)},
        )

    try:
        ensure_certified(repo_root, agent_id)
        ensure_work_mode(repo_root, work_id, "list lease locks")
        db_path = system_db_path(repo_root)
        if not db_path.exists():
            return error_result(
                code="db_missing",
                meaning="System database does not exist.",
                details={"command_name": command_name, "db_path": str(db_path)},
            )
        with sqlite_session(db_path, must_exist=True) as session:
            query = session.query(LeaseLock)
            if owner_id:
                query = query.filter(LeaseLock.owner_id == owner_id)
            if normalized_resource:
                query = query.filter(LeaseLock.resource_key == normalized_resource)
            if lock_group_id:
                query = query.filter(LeaseLock.lock_group_id == lock_group_id)
            if ticket_id:
                query = query.filter(LeaseLock.ticket_id == ticket_id)
            if work_filter:
                query = query.filter(LeaseLock.work_id == work_filter)
            query = query.order_by(LeaseLock.expires_at, LeaseLock.lock_id)
            if limit_value:
                query = query.limit(limit_value)
            rows = query.all()
        locks = [_serialize_lock(row) for row in rows]
        return ok_result(
            output={
                "count": len(locks),
                "locks": locks,
            }
        )
    except Exception as exc:
        return exception_result(command_name, exc)


def _build_parser() -> argparse.ArgumentParser:
    """
    Build the CLI argument parser for lock status.

    Returns:
        argparse.ArgumentParser: Configured argument parser.
    """
    parser = argparse.ArgumentParser(description="List lease locks.")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", required=True, help="Work identifier")
    parser.add_argument("--owner-id", help="Filter by lock owner id")
    parser.add_argument("--kind", choices=_kind_choices(), help="Lock kind filter")
    parser.add_argument("--path", help="Repo-relative path for file/dir locks")
    parser.add_argument("--resource", help="Explicit resource key for kind=resource")
    parser.add_argument("--branch", help="Branch name override for file/dir locks")
    parser.add_argument("--lock-group-id", help="Filter by lock group id")
    parser.add_argument("--ticket-id", help="Filter by ticket id")
    parser.add_argument("--lock-work-id", help="Filter by lock work id")
    parser.add_argument("--limit", type=int, help="Limit number of rows")
    return parser


def main() -> None:
    """
    CLI entrypoint for listing lease locks.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """
    parser = _build_parser()
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "agent_id": args.agent_id,
        "work_id": args.work_id,
        "owner_id": args.owner_id,
        "kind": args.kind,
        "path": args.path,
        "resource": args.resource,
        "branch": args.branch,
        "lock_group_id": args.lock_group_id,
        "ticket_id": args.ticket_id,
        "lock_work_id": args.lock_work_id,
        "limit": args.limit,
    }
    context = ExecutionContext(
        command_name="lock_status",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("lock_status failed: %s", result.errors)
        raise SystemExit(1)
    logger.info("locks listed: %s", result.output.get("count"))


if __name__ == "__main__":
    main()
