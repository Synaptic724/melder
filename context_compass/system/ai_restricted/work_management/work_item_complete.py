"""
Complete a work item and move it to a terminal queue state.
"""

import argparse
import logging
from pathlib import Path
from typing import Optional

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_bool,
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
from context_compass.system.ai_restricted.database_management import sqlite_crud, sqlite_query
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)
from context_compass.system.ai_restricted.work_management import work_item_close


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
    Return allowed terminal state values for completion.

    Returns:
        list[str]: Allowed terminal state values.
    """
    return ["done", "failed", "cancelled"]


def _normalize_state(value: Optional[str]) -> str:
    """
    Normalize the desired completion state.

    Args:
        value (Optional[str]): Requested state override.

    Returns:
        str: Normalized completion state.

    Raises:
        ValueError: If the state is not supported.
    """
    if value is None:
        return "done"
    if value not in _state_choices():
        raise ValueError(f"Unsupported completion state: {value}")
    return value


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Complete a work item using the command runner contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result describing the completion operation.

    Raises:
        None: Errors are returned as CommandResult payloads.

    Contract:
        - Requires agent_id and work_id.
        - Moves work items into a terminal bucket with a terminal state.
        - Optionally removes the work item from agent queues.
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
            payload, "source_bucket", command_name=command_name, default="active"
        )
        dest_bucket = optional_string(
            payload, "dest_bucket", command_name=command_name, default="completed"
        )
        state_override = optional_string(payload, "state", command_name=command_name)
        queue_agent_id = optional_string(payload, "queue_agent_id", command_name=command_name)
        skip_queue_removal = optional_bool(
            payload, "skip_queue_removal", command_name=command_name, default=False
        )
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
    if skip_queue_removal:
        queue_agent = None
    else:
        queue_agent = queue_agent_id or agent_id

    try:
        ensure_certified(repo_root, effective_owner)
        ensure_feature_enabled(repo_root, "work_management", "complete work items")
        ensure_work_mode(repo_root, work_id, "complete work items")
        work_item_close.close_work_item(
            repo_root=repo_root,
            work_id=work_id,
            work_type=work_type,
            source_bucket=source_bucket,
            dest_bucket=dest_bucket,
            owner_id=effective_owner,
            new_state=state_value,
            queue_agent_id=queue_agent,
        )
        return ok_result(
            output={
                "work_id": work_id,
                "work_type": work_type,
                "source_bucket": source_bucket,
                "dest_bucket": dest_bucket,
                "state": state_value,
                "queue_agent_id": queue_agent,
            }
        )
    except sqlite_query.SqliteQueryError as exc:
        return error_result(
            code=exc.code,
            meaning=exc.meaning,
            details={"command_name": command_name, **exc.details},
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
    Build the CLI argument parser for work item completion.

    Returns:
        argparse.ArgumentParser: Configured argument parser.
    """
    parser = argparse.ArgumentParser(description="Complete a work item.")
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
        default="active",
        help="Source bucket",
    )
    parser.add_argument(
        "--dest-bucket",
        choices=_bucket_choices(),
        default="completed",
        help="Destination bucket",
    )
    parser.add_argument(
        "--state",
        choices=_state_choices(),
        default="done",
        help="Terminal state to set",
    )
    parser.add_argument("--queue-agent-id", help="Agent queue to remove work from")
    parser.add_argument(
        "--skip-queue-removal",
        action="store_true",
        help="Do not remove from agent queues",
    )
    parser.add_argument("--owner-id", help="Lock owner id override")
    return parser


def main() -> None:
    """
    CLI entrypoint for completing work items.

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
        "queue_agent_id": args.queue_agent_id,
        "skip_queue_removal": args.skip_queue_removal,
        "owner_id": args.owner_id,
    }
    context = ExecutionContext(
        command_name="work_item_complete",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("work_item_complete failed: %s", result.errors)
        raise SystemExit(1)
    logger.info("work item completed: %s", result.output.get("work_id"))


if __name__ == "__main__":
    main()
