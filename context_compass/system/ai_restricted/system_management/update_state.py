"""
context_compass.system.ai_restricted.update_state

State mutation helpers for context_compass artifacts.

Contracts
- Acquire state locks before any write.
- Re-read current state after acquiring the lock.
- Persist branch state and work queues in SQLite.
- Do not update agent profiles automatically.
"""

import argparse
import logging
from pathlib import Path
from typing import Optional

from context_compass.system.ai_restricted.system_management import lease
from context_compass.system.ai_restricted._shared import branch_paths
from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_int,
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
from context_compass.system.ai_restricted._shared.feature_guard import ensure_feature_enabled
from context_compass.system.ai_restricted._shared.work_mode_guard import ensure_work_mode
from context_compass.system.ai_restricted._shared.timeutils import utc_now_iso
from context_compass.system.ai_restricted.database_management import sqlite_crud
from context_compass.system.ai_restricted.database_management import sqlite_query
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)


POLICIES_TABLE_NAME = "config_policies_core"
POLICIES_ACTION = "by_config_id"
POLICIES_CONFIG_ID = 1


def _current_branch(repo_root: Path) -> str:
    """
    Load the active branch name for SQLite-backed state updates.

    Args:
        repo_root (Path): Repository root.

    Returns:
        str: Active branch name.
    """
    return branch_paths.load_current_branch(repo_root)


def _load_policies(repo_root: Path, owner_id: str) -> dict:
    """
    Load policy configuration values via sqlite_crud.

    Args:
        repo_root (Path): Repository root.
        owner_id (str): Actor identifier for audit logging.

    Returns:
        dict: Policy values including lease_ttl_seconds and lock_wait_seconds.

    Raises:
        ValueError: If required policy fields are missing or invalid.
        sqlite_crud.SqliteCrudError: If the CRUD request fails.
    """

    response = sqlite_crud.execute_request(
        repo_root,
        sqlite_crud.SqliteCrudRequest(
            operation="read",
            scope="system",
            table_name=POLICIES_TABLE_NAME,
            action=POLICIES_ACTION,
            payload={"config_id": POLICIES_CONFIG_ID},
            actor_id=owner_id,
        ),
    )
    record = response.output.get("result", {}).get("record", {})
    lease_ttl = record.get("lease_ttl_seconds")
    lock_wait = record.get("lock_wait_seconds")
    if not isinstance(lease_ttl, int) or lease_ttl < 1:
        raise ValueError("lease_ttl_seconds must be an integer >= 1.")
    if not isinstance(lock_wait, int) or lock_wait < 0:
        raise ValueError("lock_wait_seconds must be an integer >= 0.")
    return {
        "lease_ttl_seconds": lease_ttl,
        "lock_wait_seconds": lock_wait,
    }


def _queue_id(branch_name: str, bucket: str, work_type: str) -> str:
    """
    Build a stable queue_id for a branch work queue.

    Args:
        branch_name (str): Branch identifier.
        bucket (str): Work bucket name.
        work_type (str): Work type name.

    Returns:
        str: Queue identifier.
    """

    return f"branch:{branch_name}:{bucket}:{work_type}"


def _repo_state_lock_resource(branch_name: str) -> Path:
    """
    Build a synthetic lock resource path for repo_state.

    Args:
        branch_name (str): Branch identifier.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"branch_repo_state::{branch_name}")


def _work_queue_lock_resource(branch_name: str, bucket: str, work_type: str) -> Path:
    """
    Build a synthetic lock resource path for a branch work queue.

    Args:
        branch_name (str): Branch identifier.
        bucket (str): Work bucket name.
        work_type (str): Work type name.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"branch_work_queue::{branch_name}::{bucket}::{work_type}")


def _read_repo_state(repo_root: Path, branch_name: str, actor_id: str) -> tuple[dict, bool]:
    """
    Read repo_state via sqlite_crud.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        tuple[dict, bool]: repo_state payload and existence flag.

    Raises:
        ValueError: If the CRUD response payload is invalid.
        sqlite_crud.SqliteCrudError: If the CRUD request fails.
    """

    response = sqlite_crud.execute_request(
        repo_root,
        sqlite_crud.SqliteCrudRequest(
            operation="read",
            scope="user",
            table_name="repo_state",
            action="by_branch_name",
            payload={"branch_name": branch_name},
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    record = result.get("record")
    exists = result.get("exists")
    if not isinstance(record, dict):
        raise ValueError("repo_state read returned an invalid record payload.")
    if not isinstance(exists, bool):
        raise ValueError("repo_state read returned an invalid exists flag.")
    return record, exists


def _write_repo_state(
    repo_root: Path,
    branch_name: str,
    payload: dict,
    actor_id: str,
    exists: bool,
) -> dict:
    """
    Write repo_state via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        payload (dict): Repo state payload to persist.
        actor_id (str): Actor identifier for audit logging.
        exists (bool): Whether the repo_state record already exists.

    Returns:
        dict: Updated repo_state payload.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name="write_repo_state",
            payload={
                "branch_name": branch_name,
                "repo_state": payload,
                "exists": exists,
            },
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    record = result.get("record")
    if not isinstance(record, dict):
        raise ValueError("repo_state write returned an invalid record payload.")
    return record


def bump_scan_state(
    repo_root: Path,
    scan_id: str,
    scanned_at: str,
    scanner_version: Optional[str],
    repo_id: Optional[str],
    git_head: Optional[str],
    template_versions: Optional[dict],
    owner_id: str,
) -> dict:
    """
    Update repo_state with the latest scan metadata.

    Args:
        repo_root (Path): Repository root.
        scan_id (str): Scan identifier.
        scanned_at (str): Scan timestamp.
        scanner_version (Optional[str]): Scanner version.
        repo_id (Optional[str]): Repo identifier override.
        git_head (Optional[str]): Git head override.
        template_versions (Optional[dict]): Template version overrides.
        owner_id (str): Lock owner id.

    Returns:
        dict: Updated repo state payload.
    """
    now = utc_now_iso()
    branch_name = _current_branch(repo_root)
    policies = _load_policies(repo_root, owner_id)
    lock_resource = _repo_state_lock_resource(branch_name)

    lease.acquire_lock(
        repo_root,
        lock_resource,
        owner_id,
        ttl_seconds=policies["lease_ttl_seconds"],
    )
    try:
        record, exists = _read_repo_state(repo_root, branch_name, owner_id)
        state = dict(record)
        state["scan_counter"] = int(state.get("scan_counter") or 0) + 1
        state["last_scan_id"] = scan_id
        state["last_scan_at"] = scanned_at
        if repo_id is not None:
            state["repo_id"] = repo_id
        if git_head is not None:
            state.setdefault("git", {})["head"] = git_head
        if scanner_version is not None:
            state["scanner_version"] = scanner_version
        if template_versions:
            state.setdefault("template_versions", {}).update(template_versions)
        state["updated_at"] = now
        if state.get("created_at") is None:
            state["created_at"] = now
        state = _write_repo_state(repo_root, branch_name, state, owner_id, exists)
    finally:
        lease.release_lock(repo_root, lock_resource, owner_id)
    return state


def update_work_item_state(
    repo_root: Path,
    bucket: str,
    work_type: str,
    work_id: str,
    owner_id: str,
    state: Optional[str] = None,
    attempts: Optional[int] = None,
    last_error_ref: Optional[str] = None,
    priority: Optional[int] = None,
) -> dict:
    """
    Update fields for a work item in a work_management queue.

    Args:
        repo_root (Path): Repository root.
        bucket (str): Work bucket.
        work_type (str): Work type.
        work_id (str): Work identifier.
        owner_id (str): Lock owner id.
        state (Optional[str]): New state.
        attempts (Optional[int]): Attempts override.
        last_error_ref (Optional[str]): Error reference override.
        priority (Optional[int]): Priority override.

    Returns:
        dict: Updated work item payload.
    """
    branch_name = _current_branch(repo_root)
    policies = _load_policies(repo_root, owner_id)
    lock_resource = _work_queue_lock_resource(branch_name, bucket, work_type)
    queue_id = _queue_id(branch_name, bucket, work_type)

    lease.acquire_lock(
        repo_root,
        lock_resource,
        owner_id,
        ttl_seconds=policies["lease_ttl_seconds"],
    )
    try:
        response = sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="update",
                scope="user",
                table_name="work_queue_items",
                action="update_item_state",
                payload={
                    "queue_id": queue_id,
                    "work_id": work_id,
                    "state": state,
                    "attempts": attempts,
                    "last_error_ref": last_error_ref,
                    "priority": priority,
                },
                actor_id=owner_id,
            ),
        )
        result = response.output.get("result", {})
        record = result.get("record")
        if not isinstance(record, dict):
            raise ValueError("Work item update returned an invalid record payload.")
        try:
            sqlite_crud.execute_request(
                repo_root,
                sqlite_crud.SqliteCrudRequest(
                    operation="update",
                    scope="user",
                    table_name="work_queues",
                    action="touch_queue",
                    payload={"queue_id": queue_id},
                    actor_id=owner_id,
                ),
            )
        except sqlite_crud.SqliteCrudError as exc:
            if exc.code != "record_missing":
                raise
        return record
    except sqlite_crud.SqliteCrudError as exc:
        if exc.code == "record_missing":
            raise ValueError(f"Work item not found: {work_id}") from exc
        raise
    finally:
        lease.release_lock(repo_root, lock_resource, owner_id)


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Update scan or work item state using the command runner contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing the updated state payload.

    Raises:
        None: All errors are captured and returned in the CommandResult.

    Contract:
        - Requires agent_id and command ("scan" or "work-item").
        - Enforces certification, feature flags, and work mode guards.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        agent_id = require_string(payload, "agent_id", command_name)
        mode = require_choice(payload, "command", command_name, ["scan", "work-item"])
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    if mode == "scan":
        try:
            scan_id = require_string(payload, "scan_id", command_name)
            work_id = optional_string(payload, "work_id", command_name=command_name)
            scanned_at = optional_string(payload, "scanned_at", command_name=command_name)
            scanner_version = optional_string(
                payload, "scanner_version", command_name=command_name
            )
            repo_id = optional_string(payload, "repo_id", command_name=command_name)
            git_head = optional_string(payload, "git_head", command_name=command_name)
            file_template_version = optional_string(
                payload, "file_template_version", command_name=command_name
            )
            dir_template_version = optional_string(
                payload, "dir_template_version", command_name=command_name
            )
        except PayloadError as exc:
            return payload_error_result(command_name, exc)

        try:
            ensure_certified(repo_root, agent_id)
            ensure_feature_enabled(repo_root, "scan", "update scan state")
            ensure_work_mode(repo_root, work_id, "update scan state")
            templates: dict[str, str] = {}
            if file_template_version is not None:
                templates["file_ctx"] = file_template_version
            if dir_template_version is not None:
                templates["dir_ctx"] = dir_template_version
            state = bump_scan_state(
                repo_root,
                scan_id=scan_id,
                scanned_at=scanned_at or utc_now_iso(),
                scanner_version=scanner_version,
                repo_id=repo_id,
                git_head=git_head,
                template_versions=templates or None,
                owner_id=agent_id,
            )
            return ok_result(output={"repo_state": state})
        except Exception as exc:
            return exception_result(command_name, exc)

    if mode == "work-item":
        try:
            bucket = require_choice(
                payload,
                "bucket",
                command_name,
                ["ready", "active", "backlog", "completed", "denied"],
            )
            work_type = require_choice(payload, "work_type", command_name, ["epic", "story", "task"])
            work_id = require_string(payload, "work_id", command_name)
            state = optional_string(payload, "state", command_name=command_name)
            attempts = optional_int(payload, "attempts", command_name=command_name)
            last_error_ref = optional_string(
                payload, "last_error_ref", command_name=command_name
            )
            priority = optional_int(payload, "priority", command_name=command_name)
        except PayloadError as exc:
            return payload_error_result(command_name, exc)

        try:
            ensure_certified(repo_root, agent_id)
            ensure_feature_enabled(repo_root, "work_management", "update work items")
            ensure_work_mode(repo_root, work_id, "update work items")
            item = update_work_item_state(
                repo_root,
                bucket,
                work_type,
                work_id,
                owner_id=agent_id,
                state=state,
                attempts=attempts,
                last_error_ref=last_error_ref,
                priority=priority,
            )
            return ok_result(output={"work_item": item})
        except Exception as exc:
            return exception_result(command_name, exc)

    return payload_error_result(
        command_name,
        PayloadError(
            code="payload_value_error",
            details={
                "command_name": command_name,
                "field": "command",
                "expected": "scan or work-item",
                "actual": mode,
            },
        ),
    )


def main() -> None:
    """
    CLI entrypoint for update_state operations.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """
    parser = argparse.ArgumentParser(description="Update context_compass state")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Update repo_state scan metadata")
    scan_parser.add_argument("--scan-id", required=True, help="Scan identifier")
    scan_parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    scan_parser.add_argument("--scanned-at", default=None, help="Scan timestamp override")
    scan_parser.add_argument("--scanner-version", default=None, help="Scanner version")
    scan_parser.add_argument("--repo-id", default=None, help="Repo identifier override")
    scan_parser.add_argument("--git-head", default=None, help="Git head override")
    scan_parser.add_argument("--file-template-version", default=None, help="File ctx template version")
    scan_parser.add_argument("--dir-template-version", default=None, help="Dir ctx template version")

    work_parser = subparsers.add_parser("work-item", help="Update a work item in a queue")
    work_parser.add_argument(
        "--bucket",
        required=True,
        choices=["ready", "active", "backlog", "completed", "denied"],
    )
    work_parser.add_argument("--work-type", required=True, choices=["epic", "story", "task"])
    work_parser.add_argument("--work-id", required=True, help="Work identifier")
    work_parser.add_argument("--state", default=None, help="New work item state")
    work_parser.add_argument("--attempts", type=int, default=None, help="Attempts override")
    work_parser.add_argument("--last-error-ref", default=None, help="Error reference override")
    work_parser.add_argument("--priority", type=int, default=None, help="Priority override")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "agent_id": args.agent_id,
        "command": args.command,
    }
    if args.command == "scan":
        payload.update(
            {
                "scan_id": args.scan_id,
                "work_id": args.work_id,
                "scanned_at": args.scanned_at,
                "scanner_version": args.scanner_version,
                "repo_id": args.repo_id,
                "git_head": args.git_head,
                "file_template_version": args.file_template_version,
                "dir_template_version": args.dir_template_version,
            }
        )
    if args.command == "work-item":
        payload.update(
            {
                "bucket": args.bucket,
                "work_type": args.work_type,
                "work_id": args.work_id,
                "state": args.state,
                "attempts": args.attempts,
                "last_error_ref": args.last_error_ref,
                "priority": args.priority,
            }
        )

    context = ExecutionContext(
        command_name="update_state",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("update_state failed: %s", result.errors)
        raise SystemExit(1)
    if args.command == "scan":
        logger.info("scan state updated: %s", args.scan_id)
    if args.command == "work-item":
        logger.info("work item updated: %s", args.work_id)


if __name__ == "__main__":
    main()
