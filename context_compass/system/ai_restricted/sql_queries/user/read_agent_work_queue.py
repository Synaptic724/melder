"""
SQLite query script to read agent work queue payloads.

Purpose
- Load agent work queue payloads by agent_id.
- Return a complete payload reconstructed from normalized tables.

Contract
- Requires payload.agent_id.
- actor_id is required for audit logging.
- Returns queue payload and exists flag.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_string,
    require_string,
)
from context_compass.system.ai_restricted._shared.command_results import (
    error_result,
    exception_result,
    ok_result,
    payload_error_result,
)
from context_compass.system.ai_restricted._shared.timeutils import utc_now_iso
from context_compass.system.ai_restricted.database_management.orm_session import (
    sqlite_session,
    user_db_path,
)
from context_compass.system.ai_restricted.database_management.user_orm_models import (
    AgentWorkItem,
    AgentWorkItemLease,
    AgentWorkItemReason,
    AgentWorkQueue,
)
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)


def _require_payload(payload: dict, command_name: str) -> dict:
    """
    Require and validate the nested payload object.

    Args:
        payload (dict): Command payload containing a nested payload object.
        command_name (str): Command name for error context.

    Returns:
        dict: Nested payload dictionary.

    Raises:
        PayloadError: If the payload is missing or invalid.
    """

    raw_payload = payload.get("payload")
    if not isinstance(raw_payload, dict):
        raise PayloadError(
            code="payload_invalid",
            details={
                "command_name": command_name,
                "field": "payload",
                "expected": "object",
                "payload_type": type(raw_payload).__name__,
            },
        )
    return raw_payload


def _parse_payload(raw_payload: dict, command_name: str) -> dict:
    """
    Parse and validate queue lookup fields.

    Args:
        raw_payload (dict): Nested payload dictionary.
        command_name (str): Command name for error context.

    Returns:
        dict: Parsed payload values for agent_id.

    Raises:
        PayloadError: If required fields are missing or invalid.
    """

    agent_id = require_string(raw_payload, "agent_id", command_name)
    return {"agent_id": agent_id}


def _default_queue(now: str, agent_id: str) -> dict[str, Any]:
    """
    Build a default agent work queue payload.

    Args:
        now (str): Current timestamp.
        agent_id (str): Agent identifier.

    Returns:
        dict[str, Any]: Default queue payload with empty entries.
    """

    return {"schema_version": 1, "agent_id": agent_id, "updated_at": now, "queue": []}


def _build_reasons_map(reasons: list[AgentWorkItemReason]) -> dict[str, list[str]]:
    """
    Build a map of work_id to ordered reason strings.

    Args:
        reasons (list[AgentWorkItemReason]): Reason rows for an agent queue.

    Returns:
        dict[str, list[str]]: Mapping of work_id to reason list.
    """

    reasons_by_work: dict[str, list[str]] = {}
    for row in reasons:
        reasons_by_work.setdefault(row.work_id, []).append(row.reason)
    return reasons_by_work


def _build_lease_map(leases: list[AgentWorkItemLease]) -> dict[str, dict[str, Any]]:
    """
    Build a map of work_id to lease payloads.

    Args:
        leases (list[AgentWorkItemLease]): Lease rows for an agent queue.

    Returns:
        dict[str, dict[str, Any]]: Mapping of work_id to lease payloads.
    """

    lease_by_work: dict[str, dict[str, Any]] = {}
    for row in leases:
        lease_by_work[row.work_id] = {
            "schema_version": row.schema_version,
            "resource": row.resource,
            "owner_id": row.owner_id,
            "created_at": row.created_at,
            "heartbeat_at": row.heartbeat_at,
            "expires_at": row.expires_at,
            "work_id": row.lease_work_id,
        }
    return lease_by_work


def _build_queue_entries(
    items: list[AgentWorkItem],
    reasons_by_work: dict[str, list[str]],
    lease_by_work: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Build queue entry payloads from ORM rows.

    Args:
        items (list[AgentWorkItem]): Work item rows for an agent queue.
        reasons_by_work (dict[str, list[str]]): Reason mapping by work_id.
        lease_by_work (dict[str, dict[str, Any]]): Lease payload mapping by work_id.

    Returns:
        list[dict[str, Any]]: Queue entry payloads.
    """

    queue: list[dict[str, Any]] = []
    for item in items:
        queue.append(
            {
                "work_id": item.work_id,
                "parent_work_id": item.parent_work_id,
                "root_work_id": item.root_work_id,
                "state": item.state,
                "kind": item.kind,
                "target_path": item.target_path,
                "ctx_path": item.ctx_path,
                "reason": reasons_by_work.get(item.work_id, []),
                "priority": item.priority,
                "lease": lease_by_work.get(item.work_id),
                "attempts": item.attempts,
                "last_error_ref": item.last_error_ref,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
            }
        )
    return queue


def _load_queue_payload(
    repo_root: Path,
    agent_id: str,
    now: str,
) -> tuple[dict[str, Any], bool]:
    """
    Load a queue payload from ORM tables.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        now (str): Timestamp for default payloads.

    Returns:
        tuple[dict[str, Any], bool]: Queue payload and existence flag.
    """

    db_path = user_db_path(repo_root)
    with sqlite_session(db_path, must_exist=True) as session:
        core = session.get(AgentWorkQueue, agent_id)
        if core is None:
            return _default_queue(now, agent_id), False

        items = (
            session.query(AgentWorkItem)
            .filter_by(agent_id=agent_id)
            .order_by(AgentWorkItem.position)
            .all()
        )
        reasons = (
            session.query(AgentWorkItemReason)
            .filter_by(agent_id=agent_id)
            .order_by(AgentWorkItemReason.work_id, AgentWorkItemReason.position)
            .all()
        )
        leases = session.query(AgentWorkItemLease).filter_by(agent_id=agent_id).all()

        reasons_by_work = _build_reasons_map(reasons)
        lease_by_work = _build_lease_map(leases)
        queue = _build_queue_entries(items, reasons_by_work, lease_by_work)
        payload = {
            "schema_version": core.schema_version,
            "agent_id": core.agent_id,
            "updated_at": core.updated_at or now,
            "queue": queue,
        }
        return payload, True


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Read an agent work queue payload by agent_id.

    Args:
        payload (dict): Command payload containing payload.agent_id.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing agent work queue payload and existence flag.

    Raises:
        None: All errors are returned as CommandResult payloads.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        require_string(payload, "actor_id", command_name)
        raw_payload = _require_payload(payload, command_name)
        parsed = _parse_payload(raw_payload, command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    db_path = user_db_path(repo_root)
    if not db_path.exists():
        return error_result(
            code="db_missing",
            meaning="User database does not exist.",
            details={
                "command_name": command_name,
                "db_path": str(db_path),
            },
        )

    try:
        now = utc_now_iso()
        queue_payload, exists = _load_queue_payload(repo_root, parsed["agent_id"], now)
        return ok_result(
            output={
                "agent_id": parsed["agent_id"],
                "queue": queue_payload,
                "exists": exists,
            }
        )
    except Exception as exc:
        return exception_result(command_name, exc)
