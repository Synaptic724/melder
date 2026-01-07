"""
Switch the active branch for context_compass state and work queues.
"""

import argparse
import logging
from pathlib import Path
from typing import Optional

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_string,
    require_string,
)
from context_compass.system.ai_restricted._shared.command_results import (
    exception_result,
    ok_result,
    payload_error_result,
)
from context_compass.system.ai_restricted._shared.certification_guard import ensure_certified
from context_compass.system.ai_restricted._shared.work_mode_guard import ensure_work_mode
from context_compass.system.ai_restricted.database_management import sqlite_crud
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)

BRANCH_REGISTRY_TABLE = "branch_registry"
CURRENT_BRANCH_TABLE = "current_branch"
CURRENT_BRANCH_RECORD_ID = "current"


def _require_branch_registered(repo_root: Path, branch_name: str, actor_id: str) -> None:
    """
    Ensure a branch exists in the system branch_registry table.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch name to check.
        actor_id (str): Actor identifier for audit logging.

    Raises:
        FileNotFoundError: If the branch is not registered or the DB is missing.
        sqlite_crud.SqliteCrudError: For unexpected CRUD failures.
    """

    try:
        sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="read",
                scope="system",
                table_name=BRANCH_REGISTRY_TABLE,
                action="by_branch_name",
                payload={"record_id": branch_name},
                actor_id=actor_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        if exc.code in {"record_not_found", "db_missing"}:
            raise FileNotFoundError(
                f"Branch is not registered: {branch_name}. Run branch_init.py first."
            ) from exc
        raise


def _set_current_branch(repo_root: Path, branch_name: str, actor_id: str) -> None:
    """
    Persist the active branch name in the current_branch table.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch name to activate.
        actor_id (str): Actor identifier for audit logging.

    Raises:
        FileNotFoundError: If the user database is missing.
        sqlite_crud.SqliteCrudError: For unexpected CRUD failures.
    """

    try:
        sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="update",
                scope="user",
                table_name=CURRENT_BRANCH_TABLE,
                action="set_current_branch",
                payload={
                    "record_id": CURRENT_BRANCH_RECORD_ID,
                    "branch_name": branch_name,
                },
                actor_id=actor_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        if exc.code == "db_missing":
            raise FileNotFoundError("User database not found for current_branch.") from exc
        raise


def switch_branch(
    repo_root: Path,
    branch_name: str,
    agent_id: str,
    work_id: Optional[str],
) -> None:
    """
    Switch the active branch pointer.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch name to activate.
        agent_id (str): Agent id for certification checks.
        work_id (Optional[str]): Work id for work_mode enforcement.

    Raises:
        FileNotFoundError: If the branch is not registered in the system registry.
    """
    ensure_certified(repo_root, agent_id)
    ensure_work_mode(repo_root, work_id, "switch branch management state")
    actor_id = f"agent:{agent_id}"
    _require_branch_registered(repo_root, branch_name, actor_id)
    _set_current_branch(repo_root, branch_name, actor_id)


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Switch the active branch using the ToolCommandAPI contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing the activated branch name.

    Raises:
        None: All errors are captured and returned in the CommandResult.

    Contract:
        - Requires agent_id and branch_name.
        - Enforces certification and work mode guards.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        branch_name = require_string(payload, "branch_name", command_name)
        agent_id = require_string(payload, "agent_id", command_name)
        work_id = optional_string(payload, "work_id", command_name=command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    try:
        switch_branch(
            repo_root=repo_root,
            branch_name=branch_name,
            agent_id=agent_id,
            work_id=work_id,
        )
        return ok_result(output={"branch_name": branch_name})
    except Exception as exc:
        return exception_result(command_name, exc)


def main() -> None:
    """
    CLI entrypoint.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """
    parser = argparse.ArgumentParser(description="Switch the active context_compass branch state.")
    parser.add_argument("--repo-root", default=".", help="Repository root (default: .)")
    parser.add_argument("--branch-name", required=True, help="Branch name to activate.")
    parser.add_argument("--agent-id", required=True, help="Agent id for certification checks.")
    parser.add_argument("--work-id", default=None, help="Work id for hard work_mode enforcement.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    payload = {
        "repo_root": args.repo_root,
        "branch_name": args.branch_name,
        "agent_id": args.agent_id,
        "work_id": args.work_id,
    }
    context = ExecutionContext(
        command_name="branch_switch",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logging.getLogger(__name__).error("branch_switch failed: %s", result.errors)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
