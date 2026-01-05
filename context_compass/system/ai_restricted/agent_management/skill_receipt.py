"""Write deterministic skill read receipts for context_compass."""

import argparse
import logging
from pathlib import Path

from context_compass.system.ai_restricted.system_management import lease
from context_compass.system.ai_restricted._shared.certification_guard import ensure_certified
from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_string,
    require_int,
    require_string,
)
from context_compass.system.ai_restricted._shared.command_results import (
    exception_result,
    ok_result,
    payload_error_result,
)
from context_compass.system.ai_restricted._shared.timeutils import utc_now_iso
from context_compass.system.ai_restricted.database_management import sqlite_crud, sqlite_query
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)


CONFIG_POLICIES_TABLE = "config_policies_core"
CONFIG_POLICIES_ACTION = "by_config_id"
CONFIG_POLICIES_ID = 1
DEFAULT_LEASE_TTL_SECONDS = 300
QUERY_READ_SELF_CONTEXT = "read_self_context"
QUERY_WRITE_SELF_CONTEXT = "write_self_context"


def _default_policies() -> dict:
    """
    Return default policy values used by skill receipt tooling.

    Returns:
        dict: Default policy values for lease TTL.
    """
    return {"lease_ttl_seconds": DEFAULT_LEASE_TTL_SECONDS}


def _load_policies(repo_root: Path, actor_id: str) -> dict:
    """
    Load policy configuration with defaults applied.

    Args:
        repo_root (Path): Repository root.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        dict: Effective policies for lease TTL.

    Raises:
        ValueError: If policy values are invalid.
        sqlite_crud.SqliteCrudError: If the policy lookup fails.
    """
    defaults = _default_policies()
    response = sqlite_crud.execute_request(
        repo_root,
        sqlite_crud.SqliteCrudRequest(
            operation="read",
            scope="system",
            table_name=CONFIG_POLICIES_TABLE,
            action=CONFIG_POLICIES_ACTION,
            payload={"config_id": CONFIG_POLICIES_ID},
            actor_id=actor_id,
        ),
    )
    record = response.output.get("result", {}).get("record")
    if not isinstance(record, dict):
        raise ValueError("config_policies_core read returned an invalid record payload.")
    lease_ttl = record.get("lease_ttl_seconds")
    if isinstance(lease_ttl, int):
        defaults["lease_ttl_seconds"] = lease_ttl
    return defaults


def _acquire_lock(repo_root: Path, resource: Path, owner_id: str, ttl_seconds: int) -> None:
    """
    Acquire or steal a lease lock for a resource.

    Args:
        repo_root (Path): Repository root used for lock scoping.
        resource (Path): Resource to lock.
        owner_id (str): Lock owner id.
        ttl_seconds (int): Lease TTL in seconds.

    Raises:
        RuntimeError: If a non-expired lock is held by another owner.
    """
    lease.acquire_lock(repo_root, resource, owner_id, ttl_seconds)


def _release_lock(repo_root: Path, resource: Path, owner_id: str) -> None:
    """
    Release a lease lock if owned by the caller.

    Args:
        repo_root (Path): Repository root used for lock scoping.
        resource (Path): Resource to unlock.
        owner_id (str): Lock owner id.
    """
    lease.release_lock(repo_root, resource, owner_id)


def _self_context_lock_resource(agent_id: str) -> Path:
    """
    Build a synthetic lock resource path for a self-context record.

    Args:
        agent_id (str): Agent identifier.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"self_context::{agent_id}")


def _read_self_context(repo_root: Path, agent_id: str, actor_id: str) -> tuple[dict, bool]:
    """
    Read a self_context payload via the SQLite query API.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        tuple[dict, bool]: Self-context payload and existence flag.

    Raises:
        ValueError: If the query returns an invalid payload structure.
        sqlite_query.SqliteQueryError: If the query execution fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_READ_SELF_CONTEXT,
            payload={"agent_id": agent_id},
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result")
    if not isinstance(result, dict):
        raise ValueError("self_context read returned an invalid result payload.")
    record = result.get("record")
    exists = result.get("exists")
    if not isinstance(record, dict):
        raise ValueError("self_context read returned an invalid record payload.")
    if not isinstance(exists, bool):
        raise ValueError("self_context read returned an invalid exists flag.")
    return record, exists


def _write_self_context(
    repo_root: Path,
    agent_id: str,
    self_context: dict,
    actor_id: str,
    exists: bool,
) -> None:
    """
    Persist a self_context payload via the SQLite query API.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        self_context (dict): Self-context payload to persist.
        actor_id (str): Actor identifier for audit logging.
        exists (bool): Whether the self-context record already exists.

    Raises:
        ValueError: If the query returns an invalid payload structure.
        sqlite_query.SqliteQueryError: If the query execution fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_WRITE_SELF_CONTEXT,
            payload={
                "agent_id": agent_id,
                "self_context": self_context,
                "exists": exists,
            },
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result")
    if not isinstance(result, dict):
        raise ValueError("self_context write returned an invalid result payload.")
    record = result.get("record")
    if not isinstance(record, dict):
        raise ValueError("self_context write returned an invalid record payload.")


def _upsert_receipt(self_data: dict, skill_id: str, version: int, summary: str) -> bool:
    """
    Insert or update a skill receipt entry.

    Args:
        self_data (dict): Self-context data.
        skill_id (str): Skill identifier.
        version (int): Skill version.
        summary (str): Agent summary of the skill.

    Returns:
        bool: True if changes were made.
    """
    receipts = self_data.setdefault("skill_receipts", [])
    for entry in receipts:
        if entry.get("skill_id") == skill_id and entry.get("version") == version:
            if entry.get("agent_summary") == summary:
                return False
            entry["agent_summary"] = summary
            entry["read_at"] = utc_now_iso()
            return True
    receipts.append(
        {
            "skill_id": skill_id,
            "version": version,
            "read_at": utc_now_iso(),
            "agent_summary": summary,
        }
    )
    return True


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Write a skill receipt using the command runner contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result indicating whether the receipt was updated.

    Raises:
        None: All errors are returned as CommandResult payloads.

    Contract:
        - Requires agent_id, skill_id, version, and summary in the payload.
        - Updates updated_at when the receipt changes.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        agent_id = require_string(payload, "agent_id", command_name)
        skill_id = require_string(payload, "skill_id", command_name)
        version = require_int(payload, "version", command_name)
        summary = require_string(payload, "summary", command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    try:
        ensure_certified(repo_root, agent_id)
        policies = _load_policies(repo_root, agent_id)
        resource = _self_context_lock_resource(agent_id)
        _acquire_lock(repo_root, resource, agent_id, ttl_seconds=policies["lease_ttl_seconds"])
        try:
            record, exists = _read_self_context(repo_root, agent_id, actor_id=agent_id)
            data = dict(record)
            changed = _upsert_receipt(data, skill_id, version, summary)
            if changed:
                data["updated_at"] = utc_now_iso()
                _write_self_context(
                    repo_root,
                    agent_id,
                    data,
                    actor_id=agent_id,
                    exists=exists,
                )
        finally:
            _release_lock(repo_root, resource, agent_id)
    except Exception as exc:
        return exception_result(
            command_name,
            exc,
            details={"agent_id": agent_id, "skill_id": skill_id, "version": version},
        )

    return ok_result(
        output={"skill_id": skill_id, "version": version, "updated": bool(changed)}
    )


def main() -> None:
    """
    CLI entrypoint for skill receipt updates.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """
    parser = argparse.ArgumentParser(description="Write context_compass skill receipts")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--skill-id", required=True, help="Skill identifier")
    parser.add_argument("--version", type=int, required=True, help="Skill version")
    parser.add_argument("--summary", required=True, help="Agent summary of the skill")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "agent_id": args.agent_id,
        "skill_id": args.skill_id,
        "version": args.version,
        "summary": args.summary,
    }
    context = ExecutionContext(
        command_name="skill_receipt",
        agent_id=args.agent_id,
        work_id=None,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("skill_receipt failed: %s", result.errors)
        raise SystemExit(1)
    if result.output.get("updated"):
        logger.info("skill receipt updated for %s", result.output.get("skill_id"))
    else:
        logger.info("skill receipt already up to date for %s", result.output.get("skill_id"))


if __name__ == "__main__":
    main()
