"""Start agent onboarding by selecting a career and creating the agent profile."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from context_compass.system.ai_restricted.agent_management import agent_manage
from context_compass.system.ai_restricted._shared import agent_careers
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


DEFAULT_CAREER = "developer"


def _load_careers(repo_root: Path) -> list[str]:
    """
    Load available careers from onboarding content.

    Args:
        repo_root (Path): Repository root.

    Returns:
        list[str]: Sorted list of available career names.

    Raises:
        ValueError: If the careers directory is missing or empty.
    """

    return agent_careers.list_careers(repo_root)


def _resolve_agent_role(
    command_name: str,
    agent_role: str | None,
    careers: list[str],
) -> tuple[str, bool]:
    """
    Resolve the career to use for onboarding.

    Args:
        command_name (str): Command name for error context.
        agent_role (str | None): Optional career label from the payload.
        careers (list[str]): Allowed career values.

    Returns:
        tuple[str, bool]: (resolved career, default_used flag).

    Raises:
        PayloadError: If the requested career is invalid or default is unavailable.
    """

    if agent_role is None:
        if DEFAULT_CAREER not in careers:
            raise PayloadError(
                code="payload_value_error",
                details={
                    "command_name": command_name,
                    "field": "agent_role",
                    "expected": f"default {DEFAULT_CAREER} to exist in {careers}",
                    "actual": None,
                },
            )
        return DEFAULT_CAREER, True
    if agent_role not in careers:
        raise PayloadError(
            code="payload_value_error",
            details={
                "command_name": command_name,
                "field": "agent_role",
                "expected": f"one of {careers}",
                "actual": agent_role,
            },
        )
    return agent_role, False


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Start onboarding by selecting a career and creating the agent profile.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing the resolved career and agent id.

    Raises:
        None: All errors are returned as CommandResult payloads.

    Contract:
        - Requires agent_id in the payload.
        - agent_role is optional and defaults to developer.
        - Delegates to agent_manage create for profile creation and certification checks.
        - Returns default_role_used to indicate when the default was applied.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        agent_id = require_string(payload, "agent_id", command_name)
        owner_id = optional_string(payload, "owner_id", command_name=command_name)
        agent_role = optional_string(payload, "agent_role", command_name=command_name)
        command_args = optional_list(payload, "command_args", command_name=command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    try:
        careers = _load_careers(repo_root)
        resolved_role, default_used = _resolve_agent_role(
            command_name,
            agent_role,
            careers,
        )
    except PayloadError as exc:
        return payload_error_result(command_name, exc)
    except Exception as exc:
        return exception_result(
            command_name,
            exc,
            details={
                "agent_id": agent_id,
                "agent_role": agent_role,
                "owner_id": owner_id,
            },
        )

    try:
        manage_payload = {
            "repo_root": str(repo_root),
            "agent_id": agent_id,
            "owner_id": owner_id,
            "agent_role": resolved_role,
            "action": "create",
            "command_args": command_args,
        }
        manage_context = ExecutionContext(
            command_name="agent_manage",
            agent_id=agent_id,
            work_id=ctx.work_id,
            correlation_id=ctx.correlation_id,
        )
        manage_result = agent_manage.run(manage_payload, manage_context)
        if manage_result.status != "ok":
            return manage_result
    except Exception as exc:
        return exception_result(
            command_name,
            exc,
            details={
                "agent_id": agent_id,
                "agent_role": resolved_role,
                "owner_id": owner_id,
            },
        )

    return ok_result(
        output={
            "agent_id": agent_id,
            "agent_role": resolved_role,
            "action": "create",
            "default_role_used": default_used,
        }
    )


def main() -> None:
    """
    CLI entrypoint for onboarding start.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """

    parser = argparse.ArgumentParser(
        description="Start onboarding by selecting a career and creating the agent profile"
    )
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--owner-id", help="Lock owner id (defaults to agent-id)")
    parser.add_argument(
        "--agent-role",
        default=None,
        help="Career label for the agent (defaults to developer)",
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "agent_id": args.agent_id,
        "owner_id": args.owner_id,
        "agent_role": args.agent_role,
        "command_args": sys.argv[1:],
    }
    context = ExecutionContext(
        command_name="agent_onboarding_start",
        agent_id=args.agent_id,
        work_id=None,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("agent_onboarding_start failed: %s", result.errors)
        raise SystemExit(1)
    logger.info(
        "onboarding start: %s (%s)",
        result.output.get("agent_id"),
        result.output.get("agent_role"),
    )


if __name__ == "__main__":
    main()
