"""
Claim a work item by moving it into an active queue state.
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
    error_result,
    exception_result,
    ok_result,
    payload_error_result,
)
from context_compass.system.ai_restricted._shared.certification_guard import ensure_certified
from context_compass.system.ai_restricted._shared.feature_guard import ensure_feature_enabled
from context_compass.system.ai_restricted._shared.work_mode_guard import ensure_work_mode
from context_compass.system.ai_restricted.database_management import sqlite_query
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)
from context_compass.system.ai_restricted.work_management import work_item_move


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


def _normalize_state(value: Optional[str]) -> str:
    """
    Normalize the desired state for a claimed work item.

    Args:
        value (Optional[str]): Requested state override.

    Returns:
        str: Normalized state value.

    Raises:
        ValueError: If the state is not supported.
    """
    if value is None:
        return "in_progress"
    if value not in _state_choices():
        raise ValueError(f"Unsupported state: {value}")
    return value


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Claim a work item using the command runner contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result describing the claim operation.

    Raises:
        None: Errors are returned as CommandResult payloads.

    Contract:
        - Requires agent_id and work_id.
        - Moves work items from source_bucket to dest_bucket.
        - Defaults to moving ready -> active with state in_progress.
    """
    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        agent_id = require_string(payload, "agent_id", command_name)
        work_id = require_string(payload, "work_id", command_name)
        work_type = optional_string(payload, "work_type", command_name=command_name)
        source_bucket = optional_string(
            payload, "source_bucket", command_name=command_name, default="ready"
        )
        dest_bucket = optional_string(
            payload, "dest_bucket", command_name=command_name, default="active"
        )
        state_override = optional_string(payload, "state", command_name=command_name)
        owner_id = optional_string(payload, "owner_id", command_name=command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    if source_bucket not in _bucket_choices():
        return payload_error_result(
            command_name,
            PayloadError(
                code="payload_value_error",
                details={
                    "command_name": command_name,
                    "field": "source_bucket",
                    "expected": f"one of {_bucket_choices()}",
                    "actual": source_bucket,
                },
            ),
        )
    if dest_bucket not in _bucket_choices():
        return payload_error_result(
            command_name,
            PayloadError(
                code="payload_value_error",
                details={
                    "command_name": command_name,
                    "field": "dest_bucket",
                    "expected": f"one of {_bucket_choices()}",
                    "actual": dest_bucket,
                },
            ),
        )
    if work_type is None:
        work_type = "task"
    if work_type not in _work_type_choices():
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

    try:
        state_value = _normalize_state(state_override)
    except ValueError as exc:
        return error_result(
            code="payload_value_error",
            meaning=str(exc),
            details={"command_name": command_name},
        )

    effective_owner = owner_id or agent_id
    try:
        ensure_certified(repo_root, effective_owner)
        ensure_feature_enabled(repo_root, "work_management", "claim work items")
        ensure_work_mode(repo_root, work_id, "claim work items")
        work_item_move.move_work_item(
            repo_root=repo_root,
            work_id=work_id,
            source_bucket=source_bucket,
            dest_bucket=dest_bucket,
            work_type=work_type,
            owner_id=effective_owner,
            new_state=state_value,
        )
        return ok_result(
            output={
                "work_id": work_id,
                "work_type": work_type,
                "source_bucket": source_bucket,
                "dest_bucket": dest_bucket,
                "state": state_value,
            }
        )
    except sqlite_query.SqliteQueryError as exc:
        return error_result(
            code=exc.code,
            meaning=exc.meaning,
            details={"command_name": command_name, **exc.details},
        )
    except Exception as exc:
        return exception_result(command_name, exc)


def _build_parser() -> argparse.ArgumentParser:
    """
    Build the CLI argument parser for work item claims.

    Returns:
        argparse.ArgumentParser: Configured argument parser.
    """
    parser = argparse.ArgumentParser(description="Claim a work item.")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", required=True, help="Work item identifier")
    parser.add_argument(
        "--work-type",
        choices=_work_type_choices(),
        default="task",
        help="Work item type",
    )
    parser.add_argument(
        "--source-bucket",
        choices=_bucket_choices(),
        default="ready",
        help="Source bucket",
    )
    parser.add_argument(
        "--dest-bucket",
        choices=_bucket_choices(),
        default="active",
        help="Destination bucket",
    )
    parser.add_argument(
        "--state",
        choices=_state_choices(),
        default="in_progress",
        help="State to set on claim",
    )
    parser.add_argument("--owner-id", help="Lock owner id override")
    return parser


def main() -> None:
    """
    CLI entrypoint for claiming work items.

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
        "work_type": args.work_type,
        "source_bucket": args.source_bucket,
        "dest_bucket": args.dest_bucket,
        "state": args.state,
        "owner_id": args.owner_id,
    }
    context = ExecutionContext(
        command_name="work_item_claim",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("work_item_claim failed: %s", result.errors)
        raise SystemExit(1)
    logger.info("work item claimed: %s", result.output.get("work_id"))


if __name__ == "__main__":
    main()
