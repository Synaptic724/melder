"""
Collect environment metadata for context_compass and optionally persist it.
"""

import argparse
import logging
import platform
import shutil
import sys
from pathlib import Path
from typing import Optional

from context_compass.system.ai_restricted.system_management import lease
from context_compass.system.ai_restricted._shared import agent_presence
from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_bool,
    optional_string,
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
from context_compass.system.ai_restricted._shared.timeutils import utc_now_iso
from context_compass.system.ai_restricted.database_management import sqlite_crud
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)


ENV_STATE_RECORD_ID = "current"
ENV_STATE_TABLE = "environment_state"
ENV_STATE_ACTION = "set_environment_state"


def _default_policies() -> dict:
    """
    Return default policy values for environment checks.

    Returns:
        dict: Policy defaults.
    """
    return {"lease_ttl_seconds": 300, "lock_wait_seconds": 10}


def _load_policies(repo_root: Path) -> dict:
    """
    Load policy configuration with defaults applied.

    Args:
        repo_root (Path): Repository root.

    Returns:
        dict: Effective policies.
    """
    policies = _default_policies()
    data = agent_presence.load_policies(repo_root)
    if isinstance(data, dict):
        policies.update({key: value for key, value in data.items() if key in policies})
    return policies


def _tool_entry(name: str) -> dict:
    """
    Build a tool availability payload.

    Args:
        name (str): Executable name.

    Returns:
        dict: Availability payload with path if present.
    """
    path = shutil.which(name)
    return {"available": path is not None, "path": path}


def _os_payload() -> dict:
    """
    Collect OS metadata for the current runtime.

    Returns:
        dict: OS payload matching environment_state schema.
    """
    name = platform.system() or ""
    platform_id = sys.platform or ""
    release = platform.release() or ""
    version = platform.version() or ""
    machine = platform.machine() or ""
    processor = platform.processor() or ""
    lower = name.lower()
    return {
        "name": str(name),
        "platform": str(platform_id),
        "release": str(release),
        "version": str(version),
        "machine": str(machine),
        "processor": str(processor),
        "is_windows": "win" in lower,
        "is_linux": "linux" in lower,
        "is_macos": "darwin" in lower or "mac" in lower,
    }


def _python_payload() -> dict:
    """
    Collect Python runtime metadata.

    Returns:
        dict: Python payload matching environment_state schema.
    """
    version_info = [int(sys.version_info.major), int(sys.version_info.minor), int(sys.version_info.micro)]
    return {
        "available": True,
        "executable": str(sys.executable) if sys.executable else None,
        "version": str(platform.python_version()),
        "version_info": version_info,
        "implementation": str(platform.python_implementation()),
    }


def _environment_payload(now: str) -> dict:
    """
    Build the full environment state payload.

    Args:
        now (str): Current timestamp.

    Returns:
        dict: Environment payload.
    """
    return {
        "schema_version": 1,
        "checked_at": now,
        "os": _os_payload(),
        "python": _python_payload(),
        "tools": {
            "git": _tool_entry("git"),
            "rg": _tool_entry("rg"),
            "pytest": _tool_entry("pytest"),
        },
    }


def _write_state(
    repo_root: Path,
    payload: dict,
    owner_id: str,
) -> None:
    """
    Persist environment state using a lease lock and the CRUD API.

    Args:
        repo_root (Path): Repository root.
        payload (dict): Environment payload.
        owner_id (str): Lock owner id.

    Raises:
        FileNotFoundError: If the system database is missing.
        sqlite_crud.SqliteCrudError: For unexpected CRUD failures.
    """
    policies = _load_policies(repo_root)
    resource = Path("environment_state::current")
    lease.acquire_lock(
        repo_root,
        resource,
        owner_id,
        ttl_seconds=policies["lease_ttl_seconds"],
    )
    try:
        request_payload = {
            "record_id": ENV_STATE_RECORD_ID,
            "schema_version": payload.get("schema_version"),
            "checked_at": payload.get("checked_at"),
            "os": payload.get("os"),
            "python": payload.get("python"),
            "tools": payload.get("tools"),
        }
        try:
            sqlite_crud.execute_request(
                repo_root,
                sqlite_crud.SqliteCrudRequest(
                    operation="update",
                    scope="system",
                    table_name=ENV_STATE_TABLE,
                    action=ENV_STATE_ACTION,
                    payload=request_payload,
                    actor_id=owner_id,
                ),
            )
        except sqlite_crud.SqliteCrudError as exc:
            if exc.code == "db_missing":
                raise FileNotFoundError("System database not found for environment state.") from exc
            raise
    finally:
        lease.release_lock(repo_root, resource, owner_id)


def run_environment_check(
    repo_root: Path,
    agent_id: str,
    work_id: Optional[str],
    owner_id: Optional[str],
    branch_name: Optional[str],
    write_state: bool,
) -> dict:
    """
    Execute the environment check and optionally persist state.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier for certification checks.
        work_id (Optional[str]): Work identifier for hard mode.
        owner_id (Optional[str]): Optional lock owner override.
        branch_name (Optional[str]): Optional branch override (retained for CLI compatibility).
        write_state (bool): Whether to persist environment state in SQLite.

    Returns:
        dict: Environment payload.

    Contract:
        - branch_name is ignored for persistence; environment state is system-scoped.
    """
    now = utc_now_iso()
    payload = _environment_payload(now)
    if write_state:
        _write_state(repo_root, payload, owner_id or agent_id)
    return payload


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Collect environment metadata using the command runner contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing the environment payload.

    Raises:
        None: All errors are captured and returned in the CommandResult.

    Contract:
        - Requires agent_id.
        - Enforces certification, feature flags, and work mode guards.
        - Persists environment_state in system.db unless write_state is false.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        agent_id = require_string(payload, "agent_id", command_name)
        work_id = optional_string(payload, "work_id", command_name=command_name)
        owner_id = optional_string(payload, "owner_id", command_name=command_name)
        branch_name = optional_string(payload, "branch_name", command_name=command_name)
        write_state = optional_bool(
            payload, "write_state", command_name=command_name, default=True
        )
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    try:
        ensure_certified(repo_root, owner_id or agent_id)
        ensure_feature_enabled(repo_root, "environment_check", "run environment check")
        ensure_work_mode(repo_root, work_id, "run environment check")
        payload_result = run_environment_check(
            repo_root=repo_root,
            agent_id=agent_id,
            work_id=work_id,
            owner_id=owner_id,
            branch_name=branch_name,
            write_state=bool(write_state),
        )
        return ok_result(output={"environment": payload_result})
    except Exception as exc:
        return exception_result(command_name, exc)


def main() -> None:
    """
    CLI entrypoint for environment_check.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """
    parser = argparse.ArgumentParser(description="Collect environment metadata for context_compass")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--owner-id", default=None, help="Lock owner id override")
    parser.add_argument("--branch-name", default=None, help="Optional branch override")
    parser.add_argument("--no-write", action="store_true", help="Skip writing environment state to SQLite")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "agent_id": args.agent_id,
        "work_id": args.work_id,
        "owner_id": args.owner_id,
        "branch_name": args.branch_name,
        "write_state": not args.no_write,
    }
    context = ExecutionContext(
        command_name="environment_check",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("environment_check failed: %s", result.errors)
        raise SystemExit(1)
    logger.info("environment_check completed")


if __name__ == "__main__":
    main()
