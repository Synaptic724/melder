"""Check out an agent and mark the profile inactive."""

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
from context_compass.system.ai_restricted.system_management.command_runner import (
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
    Resolve the agent career for checkout operations.

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
    Check out an agent using the command runner contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing the checked-out agent id.

    Raises:
        None: All errors are returned as CommandResult payloads.

    Contract:
        - Requires agent_id in the payload.
        - Resolves agent_role from payload or stored profile career.
        - Optional notes are recorded in the agent profile.
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
        notes = optional_string(payload, "notes", command_name=command_name)
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
        agent_presence.checkout(
            repo_root,
            agent_id=agent_id,
            agent_role=resolved_role,
            notes=notes,
            command_name=command_name,
            command_args=[str(arg) for arg in command_args] if command_args else None,
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
    CLI entrypoint for agent checkout.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """
    parser = argparse.ArgumentParser(description="Check out an agent and mark the profile inactive")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument(
        "--agent-role",
        default=None,
        help="Career label for the agent (developer/analyst/project_manager)",
    )
    parser.add_argument("--notes", default=None, help="Optional notes")
    parser.add_argument("--owner-id", default=None, help="Lock owner id override")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "agent_id": args.agent_id,
        "agent_role": args.agent_role,
        "notes": args.notes,
        "owner_id": args.owner_id,
        "command_args": sys.argv[1:],
    }
    context = ExecutionContext(
        command_name="agent_checkout",
        agent_id=args.agent_id,
        work_id=None,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("agent_checkout failed: %s", result.errors)
        raise SystemExit(1)
    logger.info("agent checked out: %s", result.output.get("agent_id"))


if __name__ == "__main__":
    main()
