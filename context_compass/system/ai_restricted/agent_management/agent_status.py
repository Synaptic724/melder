"""
Report agent profile status and current branch metadata.
"""

import argparse
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from context_compass.system.ai_restricted._shared import branch_paths
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
from context_compass.system.ai_restricted._shared.certification_guard import ensure_certified
from context_compass.system.ai_restricted._shared.work_mode_guard import ensure_work_mode
from context_compass.system.ai_restricted.database_management import sqlite_query
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)


def _load_agent_profile(repo_root: Path, agent_id: str) -> Tuple[Dict[str, Any], bool]:
    """
    Load the agent profile payload from SQLite.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.

    Returns:
        Tuple[Dict[str, Any], bool]: Profile payload and existence flag.

    Raises:
        sqlite_query.SqliteQueryError: If the query fails.
        ValueError: If the result payload is invalid.
    """
    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name="read_agent_profile",
            payload={"agent_id": agent_id},
            actor_id=agent_id,
        ),
    )
    result = response.output.get("result")
    if not isinstance(result, dict):
        raise ValueError("agent_profile read returned an invalid result payload.")
    record = result.get("record")
    exists = result.get("exists")
    if not isinstance(record, dict):
        raise ValueError("agent_profile read returned an invalid record payload.")
    if not isinstance(exists, bool):
        raise ValueError("agent_profile read returned an invalid exists flag.")
    return record, exists


def _try_current_branch(repo_root: Path) -> Tuple[Optional[str], Optional[str]]:
    """
    Load the current branch name and capture any error.

    Args:
        repo_root (Path): Repository root.

    Returns:
        Tuple[Optional[str], Optional[str]]: Branch name and error message.
    """
    try:
        return branch_paths.load_current_branch(repo_root), None
    except Exception as exc:
        return None, str(exc)


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Report agent status using the command runner contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing agent profile and branch info.

    Raises:
        None: Errors are returned as CommandResult payloads.

    Contract:
        - Requires agent_id and work_id.
        - Returns agent_profile data and current branch if available.
    """
    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        agent_id = require_string(payload, "agent_id", command_name)
        work_id = require_string(payload, "work_id", command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    try:
        ensure_certified(repo_root, agent_id)
        ensure_work_mode(repo_root, work_id, "read agent status")
        profile, exists = _load_agent_profile(repo_root, agent_id)
        branch_name, branch_error = _try_current_branch(repo_root)
        return ok_result(
            output={
                "agent_id": agent_id,
                "exists": exists,
                "profile": profile,
                "current_branch": branch_name,
                "branch_error": branch_error,
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
    Build the CLI argument parser for agent status.

    Returns:
        argparse.ArgumentParser: Configured argument parser.
    """
    parser = argparse.ArgumentParser(description="Report agent status.")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", required=True, help="Work identifier")
    return parser


def main() -> None:
    """
    CLI entrypoint for agent status.

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
    }
    context = ExecutionContext(
        command_name="agent_status",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("agent_status failed: %s", result.errors)
        raise SystemExit(1)
    logger.info("agent status loaded: %s", result.output.get("agent_id"))


if __name__ == "__main__":
    main()
