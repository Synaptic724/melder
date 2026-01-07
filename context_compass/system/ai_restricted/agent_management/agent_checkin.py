"""Check in an agent and mark the profile active."""

import argparse
import logging
import sys
from pathlib import Path

from context_compass.system.ai_restricted._shared import agent_careers, agent_presence, agent_profile_store
from context_compass.system.ai_restricted._shared.certification_guard import ensure_certified
from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_list,
    optional_string,
    require_string,
)
from context_compass.system.ai_restricted._shared.command_results import (
    exception_result,
    ok_result,
    payload_error_result,
)
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)


def _load_careers(repo_root: Path) -> list[str]:
    """
    Load available careers from onboarding content.

    Args:
        repo_root (Path): Repository root.

    Returns:
        list[str]: Sorted list of valid careers.

    Raises:
        ValueError: If career discovery fails.
    """

    return agent_careers.list_careers(repo_root)


def _validate_career_choice(command_name: str, career: str, careers: list[str]) -> str:
    """
    Validate a career choice against the available careers list.

    Args:
        command_name (str): Command name for error context.
        career (str): Career value to validate.
        careers (list[str]): Allowed career values.

    Returns:
        str: Validated career value.

    Raises:
        PayloadError: If the career is not an allowed value.
    """

    if career not in careers:
        raise PayloadError(
            code="payload_value_error",
            details={
                "command_name": command_name,
                "field": "agent_role",
                "expected": f"one of {careers}",
                "actual": career,
            },
        )
    return career


def _resolve_agent_role(
    repo_root: Path,
    agent_id: str,
    actor_id: str,
    command_name: str,
    agent_role: str | None,
    careers: list[str],
) -> str:
    """
    Resolve the agent career for checkin operations.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        actor_id (str): Actor identifier for audit logging.
        command_name (str): Command name for error context.
        agent_role (str | None): Optional career label from payload.
        careers (list[str]): Allowed career values.

    Returns:
        str: Resolved career label.

    Raises:
        PayloadError: If the career is missing or invalid.
        FileNotFoundError: If the user database is missing.
        ValueError: If the stored profile payload is invalid.
    """

    if agent_role is not None:
        return _validate_career_choice(command_name, agent_role, careers)

    snapshot = agent_profile_store.load_profile(repo_root, agent_id, actor_id=actor_id)
    if not snapshot.exists:
        raise PayloadError(
            code="payload_missing",
            details={
                "command_name": command_name,
                "field": "agent_role",
                "expected": f"one of {careers}",
                "detail": "agent profile missing; create with a career first",
            },
        )
    stored_role = snapshot.payload.get("agent_role")
    if not isinstance(stored_role, str) or not stored_role.strip():
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": "agent_role",
                "expected": "non-empty string",
                "actual_type": type(stored_role).__name__,
            },
        )
    return _validate_career_choice(command_name, stored_role, careers)


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Check in an agent using the ToolCommandAPI contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing the checked-in agent id.

    Raises:
        None: All errors are returned as CommandResult payloads.

    Contract:
        - Requires agent_id in the payload.
        - Resolves agent_role from payload or stored profile career.
        - Optional fields update task, target, notes, and runtime metadata.
        - Missing agent_role is an error if the profile does not exist yet.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        agent_id = require_string(payload, "agent_id", command_name)
        agent_role = optional_string(payload, "agent_role", command_name=command_name)
        current_task_id = optional_string(
            payload, "current_task_id", command_name=command_name
        )
        current_target = optional_string(
            payload, "current_target", command_name=command_name
        )
        notes = optional_string(payload, "notes", command_name=command_name)
        agent_kind = optional_string(payload, "agent_kind", command_name=command_name)
        model_name = optional_string(payload, "model_name", command_name=command_name)
        runtime = optional_string(payload, "runtime", command_name=command_name)
        owner_id = optional_string(payload, "owner_id", command_name=command_name)
        command_args = optional_list(payload, "command_args", command_name=command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    try:
        careers = _load_careers(repo_root)
        resolved_role = _resolve_agent_role(
            repo_root,
            agent_id,
            owner_id or agent_id,
            command_name,
            agent_role,
            careers,
        )
        ensure_certified(repo_root, owner_id or agent_id)
        agent_presence.checkin(
            repo_root,
            agent_id=agent_id,
            agent_role=resolved_role,
            current_task_id=current_task_id,
            current_target=current_target,
            notes=notes,
            command_name=command_name,
            command_args=[str(arg) for arg in command_args] if command_args else None,
            agent_kind=agent_kind,
            model_name=model_name,
            runtime=runtime,
            owner_id=owner_id,
        )
    except Exception as exc:
        return exception_result(
            command_name,
            exc,
            details={"agent_id": agent_id, "owner_id": owner_id or agent_id},
        )

    return ok_result(output={"agent_id": agent_id})


def main() -> None:
    """
    CLI entrypoint for agent checkin.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """
    parser = argparse.ArgumentParser(description="Check in an agent and mark the profile active")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument(
        "--agent-role",
        default=None,
        help="Career label for the agent (developer/analyst/project_manager)",
    )
    parser.add_argument("--current-task-id", default=None, help="Current task id")
    parser.add_argument("--current-target", default=None, help="Current target path")
    parser.add_argument("--notes", default=None, help="Optional notes")
    parser.add_argument("--agent-kind", default=None, help="Agent kind (codex/gemini/etc)")
    parser.add_argument("--model-name", default=None, help="Model name or variant")
    parser.add_argument("--runtime", default=None, help="Runtime identifier (cli/api/ci)")
    parser.add_argument("--owner-id", default=None, help="Lock owner id override")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "agent_id": args.agent_id,
        "agent_role": args.agent_role,
        "current_task_id": args.current_task_id,
        "current_target": args.current_target,
        "notes": args.notes,
        "agent_kind": args.agent_kind,
        "model_name": args.model_name,
        "runtime": args.runtime,
        "owner_id": args.owner_id,
        "command_args": sys.argv[1:],
    }
    context = ExecutionContext(
        command_name="agent_checkin",
        agent_id=args.agent_id,
        work_id=None,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("agent_checkin failed: %s", result.errors)
        raise SystemExit(1)
    logger.info("agent checked in: %s", result.output.get("agent_id"))


if __name__ == "__main__":
    main()
