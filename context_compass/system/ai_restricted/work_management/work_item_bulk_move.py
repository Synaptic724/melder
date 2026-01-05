"""
Bulk move work items between work_management queues.

Purpose:
- Provide deterministic bulk moves across work buckets without duplicating lock logic.

Contract:
- Uses work_item_move for per-item locking and writes.
- Selection can be explicit (work_ids) or by quantity from a source queue.
"""

import argparse
import logging
from pathlib import Path
from typing import Optional

from context_compass.system.ai_restricted.work_management import work_item_move
from context_compass.system.ai_restricted._shared import branch_paths
from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_int,
    optional_list,
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
from context_compass.system.ai_restricted.database_management import sqlite_crud, sqlite_query
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)


def _work_files() -> dict:
    """
    Return the supported work queue types with legacy filename mapping.

    Purpose:
    - Centralize queue filename mapping for bulk operations.

    Returns:
        dict: Mapping of work types to legacy queue filenames.
    """
    return {"epic": "epic", "story": "story", "task": "task"}


def _aliases() -> dict:
    """
    Return kind aliases that normalize to canonical work types.

    Purpose:
    - Normalize kind input for queue selection.

    Returns:
        dict: Mapping of kind aliases to canonical work types.
    """
    return {"epic": "epic", "story": "story", "task": "task"}


def _bucket_choices() -> list[str]:
    """
    Return allowed work bucket values.

    Purpose:
    - Keep bulk moves within the known bucket set.

    Returns:
        list[str]: Allowed bucket values.
    """
    return ["ready", "active", "backlog", "completed", "denied"]


def _state_choices() -> list[str]:
    """
    Return allowed work item state values.

    Purpose:
    - Restrict state updates to the standard enum.

    Returns:
        list[str]: Allowed state values.
    """
    return ["queued", "leased", "in_progress", "done", "failed", "cancelled"]


def _format_bulk_move_error(exc: Exception) -> str:
    """
    Build a human-readable error message for a bulk move failure.

    Args:
        exc (Exception): Raised exception during a move attempt.

    Returns:
        str: Error message suitable for bulk move reporting.

    Contract:
        - Prefers query script error meanings when available.
        - Falls back to the exception message when details are absent.
    """

    if isinstance(exc, sqlite_query.SqliteQueryError):
        details = exc.details
        if isinstance(details, dict):
            script_errors = details.get("script_errors")
            if isinstance(script_errors, list) and script_errors:
                first = script_errors[0]
                if isinstance(first, dict):
                    meaning = first.get("meaning")
                    if isinstance(meaning, str) and meaning:
                        return meaning
        return exc.meaning
    return str(exc)


def _normalize_kind(kind: str) -> tuple[str, Optional[str]]:
    """
    Normalize a kind string and infer a work type.

    Purpose:
    - Accept canonical work types while tolerating case differences.

    Args:
        kind (str): Input kind string.

    Returns:
        tuple[str, Optional[str]]: Normalized kind and inferred work type.
    """
    normalized = kind.strip()
    lowered = normalized.lower()
    aliases = _aliases()
    if lowered in aliases:
        canonical = aliases[lowered]
        return canonical, canonical
    if lowered in _work_files():
        return lowered, lowered
    return normalized, None


def _resolve_work_type(work_type: Optional[str], kind: Optional[str]) -> str:
    """
    Resolve the effective work type for queue operations.

    Purpose:
    - Ensure queue selection is explicit and deterministic.

    Contract:
    - work_type wins when provided and valid.
    - kind is used for inference when work_type is omitted.
    - Defaults to "task" when neither is provided.

    Args:
        work_type (Optional[str]): Explicit work type override.
        kind (Optional[str]): Kind used to infer work type.

    Returns:
        str: Resolved work type.

    Raises:
        ValueError: If work_type or kind cannot be resolved.
    """
    if work_type:
        lowered = work_type.strip().lower()
        if lowered not in _work_files():
            raise ValueError(f"Invalid work_type: {work_type}")
        return lowered
    if kind:
        _, inferred = _normalize_kind(kind)
        if inferred:
            return inferred
        raise ValueError(f"Invalid work kind: {kind}")
    return "task"


def _queue_id(branch_name: str, bucket: str, work_type: str) -> str:
    """
    Build a branch queue_id for work_queues rows.

    Args:
        branch_name (str): Branch identifier.
        bucket (str): Work bucket name.
        work_type (str): Work type key.

    Returns:
        str: Queue identifier for work_queues.
    """

    return f"branch:{branch_name}:{bucket}:{work_type}"


def _load_queue(
    repo_root: Path,
    branch_name: str,
    bucket: str,
    work_type: str,
    owner_id: str,
) -> list[dict]:
    """
    Load queue items from SQLite for a branch work queue.

    Purpose:
    - Ensure bulk selection reads valid queue payloads.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        bucket (str): Work bucket name.
        work_type (str): Work type key.
        owner_id (str): Actor identifier for audit logging.

    Returns:
        list[dict]: Queue items in stored order.

    Raises:
        ValueError: If the returned items payload is invalid.
    """
    queue_id = _queue_id(branch_name, bucket, work_type)
    response = sqlite_crud.execute_request(
        repo_root,
        sqlite_crud.SqliteCrudRequest(
            operation="read",
            scope="user",
            table_name="work_queue_items",
            action="list_by_queue_id",
            payload={"queue_id": queue_id},
            actor_id=owner_id,
        ),
    )
    result = response.output.get("result", {})
    items = result.get("items")
    if not isinstance(items, list):
        raise ValueError("Queue items payload must be a list")
    return items


def _normalize_work_ids(work_ids: list[str]) -> list[str]:
    """
    Normalize and de-duplicate a list of work ids.

    Purpose:
    - Enforce non-empty identifiers and preserve order.

    Contract:
    - Trims whitespace.
    - Drops duplicates while preserving the first occurrence.

    Args:
        work_ids (list[str]): Input work id list.

    Returns:
        list[str]: Normalized work ids.

    Raises:
        ValueError: If any work id is empty or if the result is empty.
    """
    normalized: list[str] = []
    seen: set[str] = set()
    for raw in work_ids:
        if not isinstance(raw, str):
            raise ValueError("work_ids must be strings")
        candidate = raw.strip()
        if not candidate:
            raise ValueError("work_ids must not be empty")
        if candidate in seen:
            continue
        seen.add(candidate)
        normalized.append(candidate)
    if not normalized:
        raise ValueError("work_ids resolved to an empty selection")
    return normalized


def _select_ids_from_queue(queue: list[dict], quantity: int) -> list[str]:
    """
    Select work ids from a queue in stored order.

    Purpose:
    - Provide deterministic selection when quantity is used.

    Contract:
    - Returns up to quantity ids in queue order.
    - Raises when queue items lack work_id metadata.

    Args:
        queue (list[dict]): Queue items.
        quantity (int): Desired number of items.

    Returns:
        list[str]: Selected work ids.

    Raises:
        ValueError: If quantity is invalid or queue items are malformed.
    """
    if quantity <= 0:
        raise ValueError("quantity must be positive")
    selected: list[str] = []
    for item in queue:
        if len(selected) >= quantity:
            break
        if not isinstance(item, dict):
            raise ValueError("Queue items must be objects")
        work_id = item.get("work_id")
        if not isinstance(work_id, str) or not work_id.strip():
            raise ValueError("Queue item missing work_id")
        selected.append(work_id)
    return selected


def resolve_bulk_work_ids(
    repo_root: Path,
    branch_name: str,
    source_bucket: str,
    work_type: str,
    work_ids: Optional[list[str]],
    quantity: Optional[int],
    owner_id: str,
) -> list[str]:
    """
    Resolve the work ids to move for a bulk operation.

    Purpose:
    - Normalize explicit selections or derive them from the source queue.

    Contract:
    - If work_ids is provided, quantity is ignored.
    - If work_ids is omitted, quantity must be provided and positive.
    - Selection preserves queue order and may return fewer than quantity.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        source_bucket (str): Source bucket name.
        work_type (str): Work type queue to inspect.
        work_ids (Optional[list[str]]): Explicit work ids to move.
        quantity (Optional[int]): Quantity to select when work_ids is omitted.
        owner_id (str): Actor identifier for audit logging.

    Returns:
        list[str]: Resolved work ids to move.

    Raises:
        ValueError: If selection inputs are invalid or resolve to none.
        FileNotFoundError: If the source queue does not exist.
    """
    if work_ids:
        return _normalize_work_ids(work_ids)
    if quantity is None:
        raise ValueError("quantity is required when work_ids is not provided")
    queue = _load_queue(repo_root, branch_name, source_bucket, work_type, owner_id)
    selected = _select_ids_from_queue(queue, quantity)
    if not selected:
        raise ValueError("No work items available for bulk move")
    return selected


def bulk_move_work_items(
    repo_root: Path,
    work_ids: list[str],
    source_bucket: str,
    dest_bucket: str,
    work_type: str,
    owner_id: str,
    new_state: Optional[str] = None,
) -> dict:
    """
    Move multiple work items between buckets and report results.

    Purpose:
    - Apply the same bucket transition to multiple work ids.

    Contract:
    - Continues on per-item failures, returning moved and failed lists.
    - Uses work_item_move for locking and persistence.

    Args:
        repo_root (Path): Repository root.
        work_ids (list[str]): Work ids to move.
        source_bucket (str): Source bucket name.
        dest_bucket (str): Destination bucket name.
        work_type (str): Work type queue to use.
        owner_id (str): Lock owner id.
        new_state (Optional[str]): Optional new state for moved items.

    Returns:
        dict: Summary including moved and failed work ids.

    Raises:
        ValueError: If inputs are invalid.
    """
    ensure_feature_enabled(repo_root, "work_management", "bulk move work items")
    if not work_ids:
        raise ValueError("work_ids must not be empty")
    if source_bucket == dest_bucket:
        raise ValueError("source and destination buckets must differ")
    if work_type not in _work_files():
        raise ValueError(f"Invalid work type: {work_type}")

    moved: list[str] = []
    failed: list[dict] = []
    for work_id in work_ids:
        try:
            work_item_move.move_work_item(
                repo_root,
                work_id,
                source_bucket,
                dest_bucket,
                work_type,
                owner_id,
                new_state=new_state,
            )
        except Exception as exc:
            failed.append({"work_id": work_id, "error": _format_bulk_move_error(exc)})
            continue
        moved.append(work_id)

    return {
        "source_bucket": source_bucket,
        "dest_bucket": dest_bucket,
        "work_type": work_type,
        "selected": list(work_ids),
        "moved": moved,
        "failed": failed,
    }


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Bulk move work items using the command runner contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing bulk move summary data.

    Raises:
        None: All errors are returned as CommandResult payloads.

    Contract:
        - Requires agent_id, source_bucket, and dest_bucket.
        - Requires work_ids or quantity for selection.
        - Enforces certification, feature flag, and work mode policies.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        agent_id = require_string(payload, "agent_id", command_name)
        work_id = optional_string(payload, "work_id", command_name=command_name)
        source_bucket = require_choice(
            payload, "source_bucket", command_name, _bucket_choices()
        )
        dest_bucket = require_choice(
            payload, "dest_bucket", command_name, _bucket_choices()
        )
        work_type = optional_string(payload, "work_type", command_name=command_name)
        kind = optional_string(payload, "kind", command_name=command_name)
        state = optional_string(payload, "state", command_name=command_name)
        work_ids = optional_list(payload, "work_ids", command_name=command_name)
        quantity = optional_int(payload, "quantity", command_name=command_name)
        owner_id = optional_string(payload, "owner_id", command_name=command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    if work_type is not None and work_type not in _work_files():
        return payload_error_result(
            command_name,
            PayloadError(
                code="payload_value_error",
                details={
                    "command_name": command_name,
                    "field": "work_type",
                    "expected": f"one of {sorted(_work_files())}",
                    "actual": work_type,
                },
            ),
        )

    if state is not None and state not in _state_choices():
        return payload_error_result(
            command_name,
            PayloadError(
                code="payload_value_error",
                details={
                    "command_name": command_name,
                    "field": "state",
                    "expected": f"one of {_state_choices()}",
                    "actual": state,
                },
            ),
        )

    try:
        resolved_work_type = _resolve_work_type(work_type, kind)
    except ValueError as exc:
        return payload_error_result(
            command_name,
            PayloadError(
                code="payload_value_error",
                details={
                    "command_name": command_name,
                    "field": "work_type",
                    "expected": "valid work_type or kind",
                    "actual": work_type or kind,
                    "message": str(exc),
                },
            ),
        )

    if work_ids is None and quantity is None:
        return payload_error_result(
            command_name,
            PayloadError(
                code="payload_missing",
                details={
                    "command_name": command_name,
                    "field": "work_ids or quantity",
                    "expected": "work_ids list or quantity",
                },
            ),
        )

    effective_owner = owner_id or agent_id

    branch_name = branch_paths.load_current_branch(repo_root)
    try:
        selected_ids = resolve_bulk_work_ids(
            repo_root=repo_root,
            branch_name=branch_name,
            source_bucket=source_bucket,
            work_type=resolved_work_type,
            work_ids=work_ids,
            quantity=quantity,
            owner_id=effective_owner,
        )
    except ValueError as exc:
        return payload_error_result(
            command_name,
            PayloadError(
                code="payload_value_error",
                details={
                    "command_name": command_name,
                    "field": "work_ids",
                    "expected": "valid work ids",
                    "actual": work_ids,
                    "message": str(exc),
                },
            ),
        )
    except FileNotFoundError as exc:
        return exception_result(command_name, exc)

    if not selected_ids:
        return payload_error_result(
            command_name,
            PayloadError(
                code="payload_value_error",
                details={
                    "command_name": command_name,
                    "field": "work_ids",
                    "expected": "non-empty selection",
                    "actual": selected_ids,
                },
            ),
        )

    work_mode_id = work_id or selected_ids[0]
    try:
        ensure_certified(repo_root, effective_owner)
        ensure_feature_enabled(repo_root, "work_management", "bulk move work items")
        ensure_work_mode(repo_root, work_mode_id, "bulk move work items")
        summary = bulk_move_work_items(
            repo_root=repo_root,
            work_ids=selected_ids,
            source_bucket=source_bucket,
            dest_bucket=dest_bucket,
            work_type=resolved_work_type,
            owner_id=effective_owner,
            new_state=state,
        )
        summary["work_id"] = work_mode_id
        return ok_result(output=summary)
    except Exception as exc:
        return exception_result(command_name, exc)


def main() -> None:
    """
    CLI entrypoint for bulk moving work items between buckets.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """
    parser = argparse.ArgumentParser(description="Bulk move work items between work_management queues")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--source-bucket", required=True, choices=_bucket_choices(), help="Source bucket")
    parser.add_argument("--dest-bucket", required=True, choices=_bucket_choices(), help="Destination bucket")
    parser.add_argument("--work-type", choices=["epic", "story", "task"], help="Queue type override")
    parser.add_argument("--kind", default=None, help="Work kind (used to infer work type)")
    parser.add_argument("--state", default=None, choices=_state_choices(), help="Optional new state")
    parser.add_argument("--work-ids", nargs="+", default=None, help="Work item identifiers to move")
    parser.add_argument(
        "--quantity",
        type=int,
        default=None,
        help="Number of items to move when work ids are not provided",
    )
    parser.add_argument("--owner-id", default=None, help="Lock owner id override")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "agent_id": args.agent_id,
        "work_id": args.work_id,
        "source_bucket": args.source_bucket,
        "dest_bucket": args.dest_bucket,
        "work_type": args.work_type,
        "kind": args.kind,
        "state": args.state,
        "work_ids": args.work_ids,
        "quantity": args.quantity,
        "owner_id": args.owner_id,
    }
    context = ExecutionContext(
        command_name="work_item_bulk_move",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("work_item_bulk_move failed: %s", result.errors)
        raise SystemExit(1)

    moved = result.output.get("moved", [])
    failed = result.output.get("failed", [])
    logger.info(
        "bulk move complete: moved=%s failed=%s",
        len(moved),
        len(failed),
    )
    if failed:
        logger.warning("bulk move failures: %s", failed)


if __name__ == "__main__":
    main()
