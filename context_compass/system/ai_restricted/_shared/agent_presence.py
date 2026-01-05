"""Agent presence helpers for checkin, checkout, and lifecycle updates."""

from pathlib import Path
from typing import Iterable, Optional

from context_compass.system.ai_restricted.system_management import lease
from context_compass.system.ai_restricted._shared.certification_state import default_certification_state
from context_compass.system.ai_restricted._shared.timeutils import utc_now_iso
from context_compass.system.ai_restricted.database_management import sqlite_crud, sqlite_query


CONFIG_POLICIES_TABLE = "config_policies_core"
CONFIG_POLICIES_ACTION = "by_config_id"
CONFIG_POLICIES_ID = 1
DEFAULT_LEASE_TTL_SECONDS = 300
DEFAULT_LOCK_WAIT_SECONDS = 10
QUERY_READ_AGENT_PROFILE = "read_agent_profile"
QUERY_WRITE_AGENT_PROFILE = "write_agent_profile"


def _default_policies() -> dict:
    """
    Return default policy values used by agent presence tooling.

    Returns:
        dict: Default policy values for lease TTL and lock wait.
    """
    return {
        "lease_ttl_seconds": DEFAULT_LEASE_TTL_SECONDS,
        "lock_wait_seconds": DEFAULT_LOCK_WAIT_SECONDS,
    }


def load_policies(repo_root: Path, actor_id: str | None = None) -> dict:
    """
    Load policy configuration with defaults applied.

    Args:
        repo_root (Path): Repository root.
        actor_id (str | None): Actor identifier for audit logging.

    Returns:
        dict: Effective policies for lease TTL and lock wait.

    Raises:
        ValueError: If policy values are invalid.
        sqlite_crud.SqliteCrudError: If the policy lookup fails.
    """
    defaults = _default_policies()
    owner_id = actor_id or "system:agent_presence"
    response = sqlite_crud.execute_request(
        repo_root,
        sqlite_crud.SqliteCrudRequest(
            operation="read",
            scope="system",
            table_name=CONFIG_POLICIES_TABLE,
            action=CONFIG_POLICIES_ACTION,
            payload={"config_id": CONFIG_POLICIES_ID},
            actor_id=owner_id,
        ),
    )
    record = response.output.get("result", {}).get("record")
    if not isinstance(record, dict):
        raise ValueError("config_policies_core read returned an invalid record payload.")
    lease_ttl = record.get("lease_ttl_seconds")
    lock_wait = record.get("lock_wait_seconds")
    if isinstance(lease_ttl, int):
        defaults["lease_ttl_seconds"] = lease_ttl
    if isinstance(lock_wait, int):
        defaults["lock_wait_seconds"] = lock_wait
    return defaults


def _agent_profile_lock_resource(agent_id: str) -> Path:
    """
    Build a synthetic lock resource path for an agent profile.

    Args:
        agent_id (str): Agent identifier.

    Returns:
        Path: Resource path for lease locks.
    """
    return Path(f"agent_profile::{agent_id}")


def _load_or_init_profile(
    repo_root: Path,
    agent_id: str,
    actor_id: str,
    now: str,
) -> tuple[dict, bool]:
    """
    Load agent profile data or initialize a default structure.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        actor_id (str): Actor identifier for audit logging.
        now (str): Current timestamp.

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


def _update_profile(
    profile: dict,
    agent_id: str,
    agent_role: str,
    current_task_id: Optional[str],
    current_target: Optional[str],
    notes: Optional[str],
    now: str,
    status: Optional[str],
    command_name: Optional[str],
    command_args: Optional[list[str]],
    agent_kind: Optional[str],
    model_name: Optional[str],
    runtime: Optional[str],
    checkin: bool,
    checkout: bool,
) -> None:
    """
    Update profile fields for a lifecycle action (checkin, checkout, manage).

    Args:
        profile (dict): Agent profile data.
        agent_id (str): Agent identifier.
        agent_role (str): Agent role label.
        current_task_id (Optional[str]): Current task id.
        current_target (Optional[str]): Current target path.
        notes (Optional[str]): Optional notes.
        now (str): Current timestamp.
        status (Optional[str]): Optional status override.
        command_name (Optional[str]): Command name to record.
        command_args (Optional[list[str]]): Command arguments to record.
        agent_kind (Optional[str]): Agent kind label.
        model_name (Optional[str]): Model name or variant.
        runtime (Optional[str]): Runtime identifier.
        checkin (bool): Whether this update is a checkin.
        checkout (bool): Whether this update is a checkout.
    """
    profile["schema_version"] = int(profile.get("schema_version") or 1)
    profile["agent_id"] = agent_id
    profile.setdefault("created_at", now)
    profile["updated_at"] = now
    if status is not None:
        profile["status"] = status
    elif profile.get("status") is None:
        profile["status"] = "inactive"
    if profile.get("status") not in {"active", "inactive"}:
        profile["status"] = "inactive"
    profile["agent_role"] = agent_role
    if "mode" in profile:
        profile.pop("mode", None)
    if checkout:
        profile["current_task_id"] = None
        profile["current_target"] = None
    else:
        profile["current_task_id"] = current_task_id
        profile["current_target"] = current_target
    profile["notes"] = notes
    if agent_kind is not None:
        profile["agent_kind"] = agent_kind
    if model_name is not None:
        profile["model_name"] = model_name
    if runtime is not None:
        profile["runtime"] = runtime
    if "last_heartbeat_at" in profile:
        profile.pop("last_heartbeat_at", None)
    if command_name is not None:
        profile["last_command"] = {"name": command_name, "args": command_args or []}
    elif "last_command" not in profile:
        profile["last_command"] = None
    if checkin:
        profile["last_checkin_at"] = now
    elif "last_checkin_at" not in profile:
        profile["last_checkin_at"] = None
    if checkout:
        profile["last_checkout_at"] = now
    elif "last_checkout_at" not in profile:
        profile["last_checkout_at"] = None
    if "certification_state" not in profile or not isinstance(profile.get("certification_state"), dict):
        profile["certification_state"] = default_certification_state()


def _acquire_locks(repo_root: Path, resources: Iterable[Path], owner_id: str, ttl_seconds: int) -> list[Path]:
    """
    Acquire locks for a set of resources in deterministic order.

    Args:
        repo_root (Path): Repository root used for lock scoping.
        resources (Iterable[Path]): Resources to lock.
        owner_id (str): Lock owner id.
        ttl_seconds (int): Lease TTL in seconds.

    Returns:
        list[Path]: Resources locked.
    """
    lock_targets: list[tuple[str, Path]] = []
    for resource in resources:
        lock_key = lease.lock_path_for(repo_root, resource)
        lock_targets.append((str(lock_key), resource))
    lock_targets.sort(key=lambda item: item[0])
    locked: list[Path] = []
    for _, resource in lock_targets:
        lease.acquire_lock(repo_root, resource, owner_id, ttl_seconds)
        locked.append(resource)
    return locked


def _release_locks(repo_root: Path, resources: Iterable[Path], owner_id: str) -> None:
    """
    Release locks for a set of resources in reverse order.

    Args:
        repo_root (Path): Repository root used for lock scoping.
        resources (Iterable[Path]): Resources to unlock.
        owner_id (str): Lock owner id.
    """
    for resource in reversed(list(resources)):
        lease.release_lock(repo_root, resource, owner_id)


def ensure_profile_file(repo_root: Path, agent_id: str, actor_id: str) -> None:
    """
    Create a profile record if missing.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        actor_id (str): Actor identifier for audit logging.
    """
    now = utc_now_iso()
    profile, exists = _load_or_init_profile(repo_root, agent_id, actor_id, now)
    if exists:
        return
    _write_profile(repo_root, agent_id, profile, actor_id, exists=False)


def record_lifecycle_update(
    repo_root: Path,
    agent_id: str,
    agent_role: str,
    current_task_id: Optional[str],
    current_target: Optional[str],
    notes: Optional[str],
    command_name: Optional[str],
    command_args: Optional[list[str]],
    agent_kind: Optional[str] = None,
    model_name: Optional[str] = None,
    runtime: Optional[str] = None,
    owner_id: Optional[str] = None,
) -> None:
    """
    Record a lifecycle update for explicit agent management commands.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        agent_role (str): Agent role label.
        current_task_id (Optional[str]): Current task id.
        current_target (Optional[str]): Current target path.
        notes (Optional[str]): Optional notes.
        command_name (Optional[str]): Command name to record.
        command_args (Optional[list[str]]): Command arguments to record.
        agent_kind (Optional[str]): Agent kind label.
        model_name (Optional[str]): Model name or variant.
        runtime (Optional[str]): Runtime identifier.
        owner_id (Optional[str]): Lock owner id override.
    """
    allowed = {"agent_manage", "agent_checkin", "agent_checkout"}
    if command_name not in allowed:
        return
    now = utc_now_iso()
    lock_owner = owner_id or agent_id
    policies = load_policies(repo_root, actor_id=lock_owner)

    locked = _acquire_locks(
        repo_root,
        [_agent_profile_lock_resource(agent_id)],
        lock_owner,
        policies["lease_ttl_seconds"],
    )
    try:
        profile, exists = _load_or_init_profile(repo_root, agent_id, lock_owner, now)
        _update_profile(
            profile,
            agent_id,
            agent_role,
            current_task_id,
            current_target,
            notes,
            now,
            status=None,
            command_name=command_name,
            command_args=command_args,
            agent_kind=agent_kind,
            model_name=model_name,
            runtime=runtime,
            checkin=False,
            checkout=False,
        )
        _write_profile(repo_root, agent_id, profile, lock_owner, exists=exists)
    finally:
        _release_locks(repo_root, locked, lock_owner)


def checkin(
    repo_root: Path,
    agent_id: str,
    agent_role: str,
    current_task_id: Optional[str],
    current_target: Optional[str],
    notes: Optional[str],
    command_name: Optional[str],
    command_args: Optional[list[str]],
    agent_kind: Optional[str] = None,
    model_name: Optional[str] = None,
    runtime: Optional[str] = None,
    owner_id: Optional[str] = None,
) -> None:
    """
    Record a checkin for the agent and mark it active.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        agent_role (str): Agent role label.
        current_task_id (Optional[str]): Current task id.
        current_target (Optional[str]): Current target path.
        notes (Optional[str]): Optional notes.
        command_name (Optional[str]): Command name to record.
        command_args (Optional[list[str]]): Command arguments to record.
        agent_kind (Optional[str]): Agent kind label.
        model_name (Optional[str]): Model name or variant.
        runtime (Optional[str]): Runtime identifier.
        owner_id (Optional[str]): Lock owner id override.
    """
    now = utc_now_iso()
    lock_owner = owner_id or agent_id
    policies = load_policies(repo_root, actor_id=lock_owner)

    locked = _acquire_locks(
        repo_root,
        [_agent_profile_lock_resource(agent_id)],
        lock_owner,
        policies["lease_ttl_seconds"],
    )
    try:
        profile, exists = _load_or_init_profile(repo_root, agent_id, lock_owner, now)
        _update_profile(
            profile,
            agent_id,
            agent_role,
            current_task_id,
            current_target,
            notes,
            now,
            status="active",
            command_name=command_name,
            command_args=command_args,
            agent_kind=agent_kind,
            model_name=model_name,
            runtime=runtime,
            checkin=True,
            checkout=False,
        )
        _write_profile(repo_root, agent_id, profile, lock_owner, exists=exists)
    finally:
        _release_locks(repo_root, locked, lock_owner)


def checkout(
    repo_root: Path,
    agent_id: str,
    agent_role: str,
    notes: Optional[str],
    command_name: Optional[str],
    command_args: Optional[list[str]],
    owner_id: Optional[str] = None,
) -> None:
    """
    Record a checkout for the agent and mark it inactive.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        agent_role (str): Agent role label.
        notes (Optional[str]): Optional notes.
        command_name (Optional[str]): Command name to record.
        command_args (Optional[list[str]]): Command arguments to record.
        owner_id (Optional[str]): Lock owner id override.
    """
    now = utc_now_iso()
    lock_owner = owner_id or agent_id
    policies = load_policies(repo_root, actor_id=lock_owner)

    locked = _acquire_locks(
        repo_root,
        [_agent_profile_lock_resource(agent_id)],
        lock_owner,
        policies["lease_ttl_seconds"],
    )
    try:
        profile, exists = _load_or_init_profile(repo_root, agent_id, lock_owner, now)
        _update_profile(
            profile,
            agent_id,
            agent_role,
            current_task_id=None,
            current_target=None,
            notes=notes,
            now=now,
            status="inactive",
            command_name=command_name,
            command_args=command_args,
            agent_kind=None,
            model_name=None,
            runtime=None,
            checkin=False,
            checkout=True,
        )
        _write_profile(repo_root, agent_id, profile, lock_owner, exists=exists)
    finally:
        _release_locks(repo_root, locked, lock_owner)
