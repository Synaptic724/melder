"""
List branch or global work queues with optional filtering.
"""

import argparse
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

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
from context_compass.system.ai_restricted._shared.feature_guard import ensure_feature_enabled
from context_compass.system.ai_restricted._shared.work_mode_guard import ensure_work_mode
from context_compass.system.ai_restricted.database_management.orm_session import (
    sqlite_session,
    user_db_path,
)
from context_compass.system.ai_restricted.database_management.user_orm_models import (
    WorkQueue,
    WorkQueueItem,
    WorkQueueItemLease,
    WorkQueueItemReason,
)
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)


def _scope_choices() -> list[str]:
    """
    Return supported queue scopes.

    Returns:
        list[str]: Allowed queue scope values.
    """
    return ["branch", "global"]


def _bucket_choices() -> list[str]:
    """
    Return allowed work bucket values.

    Returns:
        list[str]: Allowed bucket values.
    """
    return ["ready", "active", "backlog", "completed", "denied"]


def _work_type_choices() -> list[str]:
    """
    Return supported work type values.

    Returns:
        list[str]: Allowed work type values.
    """
    return ["epic", "story", "task"]


def _state_choices() -> list[str]:
    """
    Return allowed work item state values.

    Returns:
        list[str]: Allowed state values.
    """
    return ["queued", "leased", "in_progress", "done", "failed", "cancelled"]


def _resolve_branch(repo_root: Path, branch_name: Optional[str]) -> str:
    """
    Resolve the branch name when listing branch queues.

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


def _build_reasons_map(
        session,
        queue_id: str,
) -> Dict[str, List[str]]:
    """
    Build a map of work_id to ordered reason lists.

    Args:
        session: SQLAlchemy session.
        queue_id (str): Queue identifier.

    Returns:
        Dict[str, List[str]]: Mapping of work_id to reasons.
    """
    reasons: Dict[str, List[str]] = {}
    rows = (
        session.query(WorkQueueItemReason)
        .filter(WorkQueueItemReason.queue_id == queue_id)
        .order_by(WorkQueueItemReason.position)
        .all()
    )
    for row in rows:
        reasons.setdefault(row.work_id, []).append(row.reason)
    return reasons


def _build_lease_map(
        session,
        queue_id: str,
) -> Dict[str, Dict[str, Any]]:
    """
    Build a map of work_id to lease payloads.

    Args:
        session: SQLAlchemy session.
        queue_id (str): Queue identifier.

    Returns:
        Dict[str, Dict[str, Any]]: Mapping of work_id to lease payloads.
    """
    leases: Dict[str, Dict[str, Any]] = {}
    rows = (
        session.query(WorkQueueItemLease)
        .filter(WorkQueueItemLease.queue_id == queue_id)
        .all()
    )
    for row in rows:
        leases[row.work_id] = {
            "schema_version": row.schema_version,
            "resource": row.resource,
            "owner_id": row.owner_id,
            "created_at": row.created_at,
            "heartbeat_at": row.heartbeat_at,
            "expires_at": row.expires_at,
            "work_id": row.lease_work_id,
        }
    return leases


def _filter_items(
        items: List[WorkQueueItem],
        *,
        state_filter: Optional[str],
        kind_filter: Optional[str],
        work_id_filter: Optional[str],
) -> List[WorkQueueItem]:
    """
    Filter work queue items by state, kind, or work_id.

    Args:
        items (List[WorkQueueItem]): Candidate work items.
        state_filter (Optional[str]): Optional state filter.
        kind_filter (Optional[str]): Optional kind filter.
        work_id_filter (Optional[str]): Optional work_id filter.

    Returns:
        List[WorkQueueItem]: Filtered work items.
    """
    filtered = items
    if state_filter:
        filtered = [item for item in filtered if item.state == state_filter]
    if kind_filter:
        filtered = [item for item in filtered if item.kind == kind_filter]
    if work_id_filter:
        filtered = [item for item in filtered if item.work_id == work_id_filter]
    return filtered


def _build_item_payloads(
        items: List[WorkQueueItem],
        reasons: Dict[str, List[str]],
        leases: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Build queue entry payloads for work items.

    Args:
        items (List[WorkQueueItem]): Work queue items.
        reasons (Dict[str, List[str]]): Reason mapping by work_id.
        leases (Dict[str, Dict[str, Any]]): Lease mapping by work_id.

    Returns:
        List[Dict[str, Any]]: Queue entry payloads.
    """
    payloads: List[Dict[str, Any]] = []
    for item in items:
        payloads.append(
            {
                "work_id": item.work_id,
                "parent_work_id": item.parent_work_id,
                "root_work_id": item.root_work_id,
                "state": item.state,
                "kind": item.kind,
                "target_path": item.target_path,
                "ctx_path": item.ctx_path,
                "reason": reasons.get(item.work_id, []),
                "priority": item.priority,
                "lease": leases.get(item.work_id),
                "attempts": item.attempts,
                "last_error_ref": item.last_error_ref,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
            }
        )
    return payloads


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    List work queues using the command runner contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing queue payloads and item counts.

    Raises:
        None: Errors are returned as CommandResult payloads.

    Contract:
        - Requires agent_id and work_id.
        - Defaults to branch scope with the active branch name.
        - Filters by bucket, work_type, state, and work_id when supplied.
    """
    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        agent_id = require_string(payload, "agent_id", command_name)
        work_id = require_string(payload, "work_id", command_name)
        scope = require_choice(payload, "scope", command_name, _scope_choices())
        branch_name = optional_string(payload, "branch_name", command_name=command_name)
        bucket = optional_string(payload, "bucket", command_name=command_name)
        work_type = optional_string(payload, "work_type", command_name=command_name)
        state_filter = optional_string(payload, "state", command_name=command_name)
        kind_filter = optional_string(payload, "kind", command_name=command_name)
        work_id_filter = optional_string(payload, "filter_work_id", command_name=command_name)
        limit_value = optional_int(payload, "limit", command_name=command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    if bucket is not None and bucket not in _bucket_choices():
        return payload_error_result(
            command_name,
            PayloadError(
                code="payload_value_error",
                details={
                    "command_name": command_name,
                    "field": "bucket",
                    "expected": f"one of {_bucket_choices()}",
                    "actual": bucket,
                },
            ),
        )
    if work_type is not None and work_type not in _work_type_choices():
        return payload_error_result(
            command_name,
            PayloadError(
                code="payload_value_error",
                details={
                    "command_name": command_name,
                    "field": "work_type",
                    "expected": f"one of {_work_type_choices()}",
                    "actual": work_type,
                },
            ),
        )
    if state_filter is not None and state_filter not in _state_choices():
        return payload_error_result(
            command_name,
            PayloadError(
                code="payload_value_error",
                details={
                    "command_name": command_name,
                    "field": "state",
                    "expected": f"one of {_state_choices()}",
                    "actual": state_filter,
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
        ensure_certified(repo_root, agent_id)
        ensure_feature_enabled(repo_root, "work_management", "list work queues")
        ensure_work_mode(repo_root, work_id, "list work queues")
        db_path = user_db_path(repo_root)
        if not db_path.exists():
            return error_result(
                code="db_missing",
                meaning="User database does not exist.",
                details={"command_name": command_name, "db_path": str(db_path)},
            )
        resolved_branch = None
        if scope == "branch":
            try:
                resolved_branch = _resolve_branch(repo_root, branch_name)
            except (FileNotFoundError, ValueError) as exc:
                return error_result(
                    code="record_missing",
                    meaning="Branch name could not be resolved.",
                    details={"command_name": command_name, "error": str(exc)},
                )
        with sqlite_session(db_path, must_exist=True) as session:
            queue_query = session.query(WorkQueue).filter(WorkQueue.scope == scope)
            if scope == "branch":
                queue_query = queue_query.filter(WorkQueue.branch_name == resolved_branch)
            if bucket:
                queue_query = queue_query.filter(WorkQueue.bucket == bucket)
            if work_type:
                queue_query = queue_query.filter(WorkQueue.work_kind == work_type)
            queues = queue_query.order_by(WorkQueue.queue_id).all()
            queue_payloads: List[Dict[str, Any]] = []
            total_items = 0
            for queue in queues:
                items = (
                    session.query(WorkQueueItem)
                    .filter(WorkQueueItem.queue_id == queue.queue_id)
                    .order_by(WorkQueueItem.position)
                    .all()
                )
                items = _filter_items(
                    items,
                    state_filter=state_filter,
                    kind_filter=kind_filter,
                    work_id_filter=work_id_filter,
                )
                reasons = _build_reasons_map(session, queue.queue_id)
                leases = _build_lease_map(session, queue.queue_id)
                entries = _build_item_payloads(items, reasons, leases)
                if limit_value:
                    entries = entries[:limit_value]
                total_items += len(entries)
                queue_payloads.append(
                    {
                        "queue_id": queue.queue_id,
                        "scope": queue.scope,
                        "branch_name": queue.branch_name,
                        "bucket": queue.bucket,
                        "work_kind": queue.work_kind,
                        "schema_version": queue.schema_version,
                        "repo_id": queue.repo_id,
                        "updated_at": queue.updated_at,
                        "items": entries,
                    }
                )
        return ok_result(
            output={
                "scope": scope,
                "branch_name": resolved_branch,
                "queues": queue_payloads,
                "total_items": total_items,
            }
        )
    except Exception as exc:
        return exception_result(command_name, exc)


def _build_parser() -> argparse.ArgumentParser:
    """
    Build the CLI argument parser for work queue listing.

    Returns:
        argparse.ArgumentParser: Configured argument parser.
    """
    parser = argparse.ArgumentParser(description="List work queues.")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", required=True, help="Work identifier")
    parser.add_argument(
        "--scope",
        choices=_scope_choices(),
        default="branch",
        help="Queue scope",
    )
    parser.add_argument("--branch-name", help="Branch name for branch scope")
    parser.add_argument("--bucket", choices=_bucket_choices(), help="Bucket filter")
    parser.add_argument("--work-type", choices=_work_type_choices(), help="Work type filter")
    parser.add_argument("--state", choices=_state_choices(), help="State filter")
    parser.add_argument("--kind", help="Kind filter")
    parser.add_argument("--filter-work-id", help="Work id filter")
    parser.add_argument("--limit", type=int, help="Limit items per queue")
    return parser


def main() -> None:
    """
    CLI entrypoint for listing work queues.

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
        "scope": args.scope,
        "branch_name": args.branch_name,
        "bucket": args.bucket,
        "work_type": args.work_type,
        "state": args.state,
        "kind": args.kind,
        "filter_work_id": args.filter_work_id,
        "limit": args.limit,
    }
    context = ExecutionContext(
        command_name="work_queue_list",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("work_queue_list failed: %s", result.errors)
        raise SystemExit(1)
    logger.info("queues listed: %s", len(result.output.get("queues", [])))


if __name__ == "__main__":
    main()
