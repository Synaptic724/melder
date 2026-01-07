"""
Acquire a lease lock for file/dir ctx resources or explicit lock keys.
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
from context_compass.system.ai_restricted.database_management import sqlite_crud
from context_compass.system.ai_restricted.system_management import lease
from context_compass.system.ai_restricted._shared.command_contracts import (
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


def _load_policies(repo_root: Path, owner_id: str) -> Dict[str, int]:
    """
    Load policy configuration values for lease behavior.

    Args:
        repo_root (Path): Repository root.
        owner_id (str): Actor identifier for audit logging.

    Returns:
        Dict[str, int]: Policy values including lease_ttl_seconds.

    Raises:
        ValueError: If required policy fields are missing or invalid.
        sqlite_crud.SqliteCrudError: If the CRUD request fails.
    """
    response = sqlite_crud.execute_request(
        repo_root,
        sqlite_crud.SqliteCrudRequest(
            operation="read",
            scope="system",
            table_name="config_policies_core",
            action="by_config_id",
            payload={"config_id": 1},
            actor_id=owner_id,
        ),
    )
    record = response.output.get("result", {}).get("record", {})
    lease_ttl = record.get("lease_ttl_seconds")
    if not isinstance(lease_ttl, int) or lease_ttl < 1:
        raise ValueError("lease_ttl_seconds must be an integer >= 1.")
    return {"lease_ttl_seconds": lease_ttl}


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


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Acquire a lease lock using the ToolCommandAPI contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing the acquired lease payload.

    Raises:
        None: Errors are returned as CommandResult payloads.

    Contract:
        - Requires agent_id, work_id, and kind.
        - For file/dir kinds, path is required and branch defaults to current.
        - Returns the lease record emitted by lease.acquire_lock.
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
        ttl_override = optional_int(payload, "ttl_seconds", command_name=command_name)
        ticket_id = optional_string(payload, "ticket_id", command_name=command_name)
        lock_group_id = optional_string(payload, "lock_group_id", command_name=command_name)
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
        ensure_work_mode(repo_root, work_id, "acquire lease lock")
        if ttl_override is None:
            policies = _load_policies(repo_root, agent_id)
            ttl_seconds = policies["lease_ttl_seconds"]
        else:
            if ttl_override < 1:
                return error_result(
                    code="payload_value_error",
                    meaning="ttl_seconds must be a positive integer.",
                    details={"command_name": command_name, "ttl_seconds": ttl_override},
                )
            ttl_seconds = ttl_override
        record = lease.acquire_lock(
            repo_root,
            resource,
            agent_id,
            ttl_seconds=ttl_seconds,
            work_id=work_id,
            ticket_id=ticket_id,
            lock_group_id=lock_group_id,
        )
        return ok_result(
            output={
                "resource": str(resource),
                "kind": kind,
                "lock": record,
            }
        )
    except RuntimeError as exc:
        return error_result(
            code="lock_held",
            meaning="Lock already held by another owner.",
            details={"command_name": command_name, "error": str(exc)},
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
    Build the CLI argument parser for lock acquisition.

    Returns:
        argparse.ArgumentParser: Configured argument parser.
    """
    parser = argparse.ArgumentParser(description="Acquire a lease lock.")
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
    parser.add_argument("--ttl-seconds", type=int, help="Override TTL in seconds")
    parser.add_argument("--ticket-id", help="Optional ticket id for traceability")
    parser.add_argument("--lock-group-id", help="Optional lock group id")
    return parser


def main() -> None:
    """
    CLI entrypoint for acquiring a lease lock.

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
        "ttl_seconds": args.ttl_seconds,
        "ticket_id": args.ticket_id,
        "lock_group_id": args.lock_group_id,
    }
    context = ExecutionContext(
        command_name="lock_acquire",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("lock_acquire failed: %s", result.errors)
        raise SystemExit(1)
    logger.info("lock acquired: %s", result.output.get("resource"))


if __name__ == "__main__":
    main()
