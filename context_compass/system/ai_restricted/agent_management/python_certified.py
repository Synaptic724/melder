"""Finalize agent certification state after user approval."""

import argparse
import logging
from pathlib import Path
from typing import Optional

from context_compass.system.ai_restricted.system_management import lease
from context_compass.system.ai_restricted._shared import agent_presence
from context_compass.system.ai_restricted._shared.certification_guard import (
    APPROVAL_TOKEN,
    is_certified,
    parse_approval_token,
)
from context_compass.system.ai_restricted._shared.certification_state import default_certification_state
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
from context_compass.system.ai_restricted._shared.timeutils import utc_now_iso
from context_compass.system.ai_restricted.database_management import sqlite_query
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)

QUERY_READ_AGENT_PROFILE = "read_agent_profile"
QUERY_WRITE_AGENT_PROFILE = "write_agent_profile"


def _build_parser() -> argparse.ArgumentParser:
    """
    Build the CLI argument parser for certification finalization.

    Returns:
        argparse.ArgumentParser: Configured parser instance.
    """
    parser = argparse.ArgumentParser(description="Finalize agent certification state")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--approval-token", required=True, help="Approval token (CERTIFY: APPROVED)")
    return parser


def _normalize_schema_version(value: object) -> int:
    """
    Normalize a schema version into a positive integer.

    Args:
        value (object): Raw schema version value.

    Returns:
        int: Normalized schema version (>= 1).
    """
    try:
        version = int(value)
    except (TypeError, ValueError):
        return 1
    return version if version >= 1 else 1


def _already_certified(existing_state: object, approval_token: str) -> bool:
    """
    Return True when certification is already finalized with the same token.

    Args:
        existing_state (object): Existing certification_state payload.
        approval_token (str): Approval token to compare.

    Returns:
        bool: True if certification is already complete with the same token.
    """
    if not isinstance(existing_state, dict):
        return False
    if not is_certified(existing_state):
        return False
    stored_token = existing_state.get("approval_token")
    if not isinstance(stored_token, str) or not stored_token:
        return False
    return stored_token == approval_token


def _load_profile(repo_root: Path, agent_id: str, actor_id: str) -> tuple[dict, bool]:
    """
    Load an agent profile payload via the SQLite query API.

    Contract:
    - Returns a snapshot with payload defaults applied.
    - exists indicates whether the record was present in SQLite.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        tuple[dict, bool]: Profile payload and existence flag.
    """
    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_READ_AGENT_PROFILE,
            payload={"agent_id": agent_id},
            actor_id=actor_id,
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


def _write_profile(
    repo_root: Path,
    agent_id: str,
    profile: dict,
    actor_id: str,
    exists: bool,
) -> None:
    """
    Persist an agent profile payload via the SQLite query API.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        profile (dict): Agent profile payload to persist.
        actor_id (str): Actor identifier for audit logging.
        exists (bool): Whether the profile record already exists.
    """
    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_WRITE_AGENT_PROFILE,
            payload={
                "agent_id": agent_id,
                "agent_profile": profile,
                "exists": exists,
            },
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result")
    if not isinstance(result, dict):
        raise ValueError("agent_profile write returned an invalid result payload.")
    record = result.get("record")
    if not isinstance(record, dict):
        raise ValueError("agent_profile write returned an invalid record payload.")


def _apply_certification_state(
    existing_state: Optional[dict],
    approval_token: str,
    now: str,
) -> dict:
    """
    Build a certified state payload from existing certification data.

    Contract:
    - Returns a new dict and does not mutate the input mapping.
    - Preserves existing approved_by, notes, and self_certification_hash values.
    - Sets the state to CERTIFIED and updates certified timestamps.

    Args:
        existing_state (Optional[dict]): Existing certification state or None.
        approval_token (str): Approval token string to record.
        now (str): ISO-8601 timestamp for certification updates.

    Returns:
        dict: Updated certification state data.
    """
    state = default_certification_state()
    if isinstance(existing_state, dict):
        state.update(existing_state)
    state["schema_version"] = _normalize_schema_version(state.get("schema_version"))
    if not state.get("approved_at"):
        state["approved_at"] = now
    state["approval_token"] = approval_token
    state["state"] = "CERTIFIED"
    state["certified"] = True
    if not state.get("certified_at"):
        state["certified_at"] = now
    return state


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


def _validate_approval_token(token: str, logger: logging.Logger) -> None:
    """
    Validate the approval token and exit if not approved.

    Args:
        token (str): Approval token string.
        logger (logging.Logger): Logger for error output.

    Raises:
        SystemExit: If the token is missing, invalid, or indicates changes.
    """
    result = parse_approval_token(token)
    if result == "APPROVED":
        return
    if result == "CHANGES":
        logger.error("Approval token indicates changes requested; certification not updated.")
        raise SystemExit(1)
    logger.error("Invalid approval token; expected %s.", APPROVAL_TOKEN)
    raise SystemExit(1)


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Finalize certification using the ToolCommandAPI contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result indicating certification status.

    Raises:
        None: All errors are returned as CommandResult payloads.

    Contract:
        - Requires agent_id and approval_token in the payload.
        - Rejects approval tokens that indicate changes or invalid approvals.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        agent_id = require_string(payload, "agent_id", command_name)
        approval_token = require_string(payload, "approval_token", command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    token_status = parse_approval_token(approval_token)
    if token_status != "APPROVED":
        return error_result(
            code="approval_token_invalid",
            meaning="Approval token is not approved.",
            details={
                "agent_id": agent_id,
                "status": token_status,
                "expected": APPROVAL_TOKEN,
            },
        )

    try:
        policies = agent_presence.load_policies(repo_root, actor_id=agent_id)
        resource = Path(f"agent_profile::{agent_id}")
        _acquire_lock(repo_root, resource, agent_id, policies["lease_ttl_seconds"])
        try:
            profile, exists = _load_profile(repo_root, agent_id, actor_id=agent_id)
            profile = dict(profile)
            if _already_certified(profile.get("certification_state"), approval_token):
                return ok_result(output={"agent_id": agent_id, "certified": True})
            now = utc_now_iso()
            profile["certification_state"] = _apply_certification_state(
                profile.get("certification_state"),
                approval_token,
                now,
            )
            profile["updated_at"] = now
            _write_profile(repo_root, agent_id, profile, actor_id=agent_id, exists=exists)
        finally:
            _release_lock(repo_root, resource, agent_id)
    except Exception as exc:
        return exception_result(
            command_name,
            exc,
            details={"agent_id": agent_id},
        )

    return ok_result(output={"agent_id": agent_id, "certified": True})


def main() -> None:
    """
    CLI entrypoint for certification finalization.

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
        "approval_token": args.approval_token,
    }
    context = ExecutionContext(
        command_name="python_certified",
        agent_id=args.agent_id,
        work_id=None,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("python_certified failed: %s", result.errors)
        raise SystemExit(1)
    logger.info("Certification finalized for agent %s", result.output.get("agent_id"))


if __name__ == "__main__":
    main()
