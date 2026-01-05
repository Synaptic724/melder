"""
Release a lease lock for file/dir ctx resources or explicit lock keys.
"""

import argparse
import logging
from pathlib import Path
from typing import Optional

from context_compass.system.ai_restricted._shared import branch_paths
from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
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
from context_compass.system.ai_restricted.database_management import sqlite_crud
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


def _release_lock(repo_root: Path, resource: Path, owner_id: str) -> bool:
    """
    Release a lease lock and report whether a row was removed.

    Args:
        repo_root (Path): Repository root.
        resource (Path): Logical resource identifier.
        owner_id (str): Lock owner id.

    Returns:
        bool: True if a lock row was deleted.

    Raises:
        sqlite_crud.SqliteCrudError: If the CRUD request fails.
        FileNotFoundError: If the system database is missing.
    """
    resolved_repo_id = lease._resolve_repo_id(repo_root, owner_id)
    resolved_type = lease._infer_resource_type(resource)
    resource_key = lease._normalize_resource_key(repo_root, resource, resolved_type)
    lock_id = lease._lock_id(resolved_repo_id, resolved_type, resource_key)
    response = sqlite_crud.execute_request(
        repo_root,
        sqlite_crud.SqliteCrudRequest(
            operation="delete",
            scope="system",
            table_name="lease_locks",
            action="release_lock",
            payload={
                "record_id": lock_id,
                "lock_id": lock_id,
                "repo_id": resolved_repo_id,
                "resource_type": resolved_type,
                "resource_key": resource_key,
                "owner_id": owner_id,
            },
            actor_id=owner_id,
        ),
    )
    deleted = response.output.get("result", {}).get("deleted")
    return bool(deleted)


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Release a lease lock using the command runner contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result indicating release status.

    Raises:
        None: Errors are returned as CommandResult payloads.

    Contract:
        - Requires agent_id, work_id, and kind.
        - For file/dir kinds, path is required and branch defaults to current.
    """
    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        agent_id = require_string(payload, "agent_id", command_name)
        work_id = require_string(payload, "work_id", command_name)
        kind = require_choice(payload, "kind", command_name, _kind_choices())
        path_value = optional_string(payload, "path", command_name=command_name)
        resource_key = optional_string(payload, "resource", command_name=command_name)
        branch_name = optional_string(payload, "branch", command_name=command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    try:
        resource = _resource_from_kind(
            repo_root, kind, path_value, resource_key, branch_name
        )
    except (ValueError, FileNotFoundError) as exc:
        return error_result(
            code="resource_invalid",
            meaning="Lock resource could not be resolved.",
            details={"command_name": command_name, "error": str(exc)},
        )

    try:
        ensure_certified(repo_root, agent_id)
        ensure_work_mode(repo_root, work_id, "release lease lock")
        deleted = _release_lock(repo_root, resource, agent_id)
        return ok_result(
            output={
                "resource": str(resource),
                "kind": kind,
                "deleted": deleted,
            }
        )
    except FileNotFoundError as exc:
        return error_result(
            code="db_missing",
            meaning="System database not found for lease locks.",
            details={"command_name": command_name, "error": str(exc)},
        )
    except sqlite_crud.SqliteCrudError as exc:
        return error_result(
            code=exc.code,
            meaning=exc.meaning,
            details={"command_name": command_name, **exc.details},
        )
    except Exception as exc:
        return exception_result(command_name, exc)


def _build_parser() -> argparse.ArgumentParser:
    """
    Build the CLI argument parser for lock release.

    Returns:
        argparse.ArgumentParser: Configured argument parser.
    """
    parser = argparse.ArgumentParser(description="Release a lease lock.")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", required=True, help="Work identifier")
    parser.add_argument(
        "--kind",
        required=True,
        choices=_kind_choices(),
        help="Lock kind (file, dir, or resource)",
    )
    parser.add_argument("--path", help="Repo-relative path for file/dir locks")
    parser.add_argument("--resource", help="Explicit resource key for kind=resource")
    parser.add_argument("--branch", help="Branch name override for file/dir locks")
    return parser


def main() -> None:
    """
    CLI entrypoint for releasing a lease lock.

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
        "kind": args.kind,
        "path": args.path,
        "resource": args.resource,
        "branch": args.branch,
    }
    context = ExecutionContext(
        command_name="lock_release",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("lock_release failed: %s", result.errors)
        raise SystemExit(1)
    logger.info("lock released: %s", result.output.get("resource"))


if __name__ == "__main__":
    main()
