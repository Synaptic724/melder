"""Agent presence helpers for heartbeat, checkin, checkout, and cleanup."""

import importlib.util
from pathlib import Path
from typing import Iterable, Optional

from context_compass.tools import lease
from context_compass.tools._shared import branch_paths
from context_compass.tools._shared.json_io import load_json, write_json_atomic
from context_compass.tools._shared.timeutils import utc_now_iso


def _default_policies() -> dict:
    """
    Return default policy values used by agent presence tooling.

    Returns:
        dict: Default policy values.
    """
    return {"lease_ttl_seconds": 300, "lock_wait_seconds": 10}


def load_policies(repo_root: Path) -> dict:
    """
    Load policy configuration with defaults applied.

    Args:
        repo_root (Path): Repository root.

    Returns:
        dict: Effective policies.
    """
    policies = _default_policies()
    config_path = repo_root / "context_compass" / "config" / "policies.json"
    if config_path.exists():
        data = load_json(config_path)
        if isinstance(data, dict):
            policies.update({k: v for k, v in data.items() if k in policies})
    return policies


def _load_or_init_active_agents(path: Path, now: str) -> dict:
    """
    Load active_agents.json or initialize a default structure.

    Args:
        path (Path): active_agents.json path.
        now (str): Current timestamp.

    Returns:
        dict: Active agents data.
    """
    if path.exists():
        data = load_json(path)
        if isinstance(data, dict):
            return data
    return {"schema_version": 1, "updated_at": now, "agents": []}


def _upsert_active_agent(
    active: dict,
    agent_id: str,
    mode: str,
    current_task_id: Optional[str],
    current_target: Optional[str],
    notes: Optional[str],
    agent_kind: Optional[str],
    model_name: Optional[str],
    runtime: Optional[str],
    now: str,
) -> None:
    """
    Insert or update an agent entry in active_agents.json.

    Args:
        active (dict): Active agents data.
        agent_id (str): Agent identifier.
        mode (str): Agent mode.
        current_task_id (Optional[str]): Current task id.
        current_target (Optional[str]): Current target path.
        notes (Optional[str]): Optional notes.
        now (str): Current timestamp.
    """
    agents = active.setdefault("agents", [])
    for entry in agents:
        if entry.get("agent_id") == agent_id:
            entry["mode"] = mode
            entry["last_heartbeat_at"] = now
            entry["current_task_id"] = current_task_id
            entry["current_target"] = current_target
            entry["notes"] = notes
            if agent_kind is not None:
                entry["agent_kind"] = agent_kind
            if model_name is not None:
                entry["model_name"] = model_name
            if runtime is not None:
                entry["runtime"] = runtime
            return
    agents.append(
        {
            "agent_id": agent_id,
            "agent_kind": agent_kind,
            "mode": mode,
            "model_name": model_name,
            "runtime": runtime,
            "started_at": now,
            "last_heartbeat_at": now,
            "current_task_id": current_task_id,
            "current_target": current_target,
            "lease": None,
            "notes": notes,
        }
    )


def _remove_active_agent(active: dict, agent_id: str) -> bool:
    """
    Remove an agent entry from active_agents data.

    Args:
        active (dict): Active agents data.
        agent_id (str): Agent identifier.

    Returns:
        bool: True if an entry was removed.
    """
    agents = active.get("agents", [])
    original = len(agents)
    active["agents"] = [entry for entry in agents if entry.get("agent_id") != agent_id]
    return len(active["agents"]) != original


def _default_profile(agent_id: str, now: str) -> dict:
    """
    Return a default agent profile payload.

    Args:
        agent_id (str): Agent identifier.
        now (str): Current timestamp.

    Returns:
        dict: Agent profile payload.
    """
    return {
        "schema_version": 1,
        "agent_id": agent_id,
        "agent_kind": None,
        "created_at": now,
        "updated_at": now,
        "status": "inactive",
        "last_heartbeat_at": None,
        "last_checkin_at": None,
        "last_checkout_at": None,
        "mode": "agent",
        "model_name": None,
        "current_task_id": None,
        "current_target": None,
        "notes": None,
        "runtime": None,
        "last_command": None,
    }


def _load_or_init_profile(path: Path, agent_id: str, now: str) -> dict:
    """
    Load agent profile data or initialize a default structure.

    Args:
        path (Path): Agent profile path.
        agent_id (str): Agent identifier.
        now (str): Current timestamp.

    Returns:
        dict: Agent profile data.
    """
    if path.exists():
        data = load_json(path)
        if isinstance(data, dict):
            return data
    return _default_profile(agent_id, now)


def _update_profile(
    profile: dict,
    agent_id: str,
    mode: str,
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
    Update profile fields for a heartbeat, checkin, or checkout.

    Args:
        profile (dict): Agent profile data.
        agent_id (str): Agent identifier.
        mode (str): Agent mode.
        current_task_id (Optional[str]): Current task id.
        current_target (Optional[str]): Current target path.
        notes (Optional[str]): Optional notes.
        now (str): Current timestamp.
        status (Optional[str]): Optional status override.
        command_name (Optional[str]): Command name to record.
        command_args (Optional[list[str]]): Command arguments to record.
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
        profile["status"] = "active"
    profile["mode"] = mode
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
    profile["last_heartbeat_at"] = now
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


def _acquire_locks(locks_dir: Path, resources: Iterable[Path], owner_id: str, ttl_seconds: int) -> list[Path]:
    """
    Acquire locks for a set of resources in deterministic order.

    Args:
        locks_dir (Path): Lock directory.
        resources (Iterable[Path]): Resources to lock.
        owner_id (str): Lock owner id.
        ttl_seconds (int): Lease TTL in seconds.

    Returns:
        list[Path]: Resources locked.
    """
    locked: list[Path] = []
    for resource in sorted({r.resolve() for r in resources}, key=lambda p: str(p)):
        lease.acquire_lock(locks_dir, resource, owner_id, ttl_seconds)
        locked.append(resource)
    return locked


def _release_locks(locks_dir: Path, resources: Iterable[Path], owner_id: str) -> None:
    """
    Release locks for a set of resources in reverse order.

    Args:
        locks_dir (Path): Lock directory.
        resources (Iterable[Path]): Resources to unlock.
        owner_id (str): Lock owner id.
    """
    for resource in reversed(list(resources)):
        lease.release_lock(locks_dir, resource, owner_id)


def ensure_profile_file(profile_path: Path, agent_id: str) -> None:
    """
    Create a profile file if missing.

    Args:
        profile_path (Path): Agent profile path.
        agent_id (str): Agent identifier.
    """
    if profile_path.exists():
        return
    now = utc_now_iso()
    write_json_atomic(profile_path, _default_profile(agent_id, now))


def run_cleanup_scripts(repo_root: Path, agent_id: str, now: Optional[str] = None) -> list[str]:
    """
    Run all cleanup scripts under tools/cleanup_agents.

    Contract:
    - Executes each cleanup module's cleanup(repo_root, agent_id, now=...).
    - Scripts are executed in sorted filename order.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent id executing cleanup.
        now (Optional[str]): Override current timestamp for cleanup scripts.

    Returns:
        list[str]: Cleanup script filenames executed.
    """
    cleanup_dir = repo_root / "context_compass" / "tools" / "cleanup_agents"
    if not cleanup_dir.exists():
        return []

    current = now or utc_now_iso()
    executed: list[str] = []
    for script in sorted(cleanup_dir.glob("*.py"), key=lambda p: p.name):
        if script.name.startswith("_"):
            continue
        if script.name == "__init__.py":
            continue
        module_name = f"context_compass.tools.cleanup_agents.{script.stem}"
        spec = importlib.util.spec_from_file_location(module_name, script)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Unable to load cleanup script: {script}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cleanup = getattr(module, "cleanup", None)
        if not callable(cleanup):
            raise RuntimeError(f"Cleanup script missing cleanup() function: {script}")
        cleanup(repo_root, agent_id, now=current)
        executed.append(script.name)
    return executed


def record_heartbeat(
    repo_root: Path,
    agent_id: str,
    mode: str,
    current_task_id: Optional[str],
    current_target: Optional[str],
    notes: Optional[str],
    command_name: Optional[str],
    command_args: Optional[list[str]],
    agent_kind: Optional[str] = None,
    model_name: Optional[str] = None,
    runtime: Optional[str] = None,
    owner_id: Optional[str] = None,
    run_cleanup: bool = True,
) -> None:
    """
    Record a heartbeat for the agent and update active_agents and profile state.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        mode (str): Agent mode.
        current_task_id (Optional[str]): Current task id.
        current_target (Optional[str]): Current target path.
        notes (Optional[str]): Optional notes.
        command_name (Optional[str]): Command name to record.
        command_args (Optional[list[str]]): Command arguments to record.
        owner_id (Optional[str]): Lock owner id override.
        run_cleanup (bool): Whether to run cleanup scripts before heartbeat.
    """
    now = utc_now_iso()
    if run_cleanup:
        run_cleanup_scripts(repo_root, agent_id, now=now)
    locks_dir = branch_paths.self_context_locks_dir(repo_root)
    locks_dir.mkdir(parents=True, exist_ok=True)
    active_path = repo_root / "context_compass" / "self_context" / "active_agents.json"
    profile_path = repo_root / "context_compass" / "self_context" / "agents" / f"{agent_id}.profile.json"
    active_path.parent.mkdir(parents=True, exist_ok=True)
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    policies = load_policies(repo_root)
    lock_owner = owner_id or agent_id

    locked = _acquire_locks(
        locks_dir,
        [active_path, profile_path],
        lock_owner,
        policies["lease_ttl_seconds"],
    )
    try:
        active = _load_or_init_active_agents(active_path, now)
        _upsert_active_agent(
            active,
            agent_id,
            mode,
            current_task_id,
            current_target,
            notes,
            agent_kind,
            model_name,
            runtime,
            now,
        )
        active["updated_at"] = now
        write_json_atomic(active_path, active)

        profile = _load_or_init_profile(profile_path, agent_id, now)
        _update_profile(
            profile,
            agent_id,
            mode,
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
            checkin=False,
            checkout=False,
        )
        write_json_atomic(profile_path, profile)
    finally:
        _release_locks(locks_dir, locked, lock_owner)


def checkin(
    repo_root: Path,
    agent_id: str,
    mode: str,
    current_task_id: Optional[str],
    current_target: Optional[str],
    notes: Optional[str],
    command_name: Optional[str],
    command_args: Optional[list[str]],
    agent_kind: Optional[str] = None,
    model_name: Optional[str] = None,
    runtime: Optional[str] = None,
    owner_id: Optional[str] = None,
    run_cleanup: bool = True,
) -> None:
    """
    Record a checkin for the agent and mark it active.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        mode (str): Agent mode.
        current_task_id (Optional[str]): Current task id.
        current_target (Optional[str]): Current target path.
        notes (Optional[str]): Optional notes.
        command_name (Optional[str]): Command name to record.
        command_args (Optional[list[str]]): Command arguments to record.
        owner_id (Optional[str]): Lock owner id override.
        run_cleanup (bool): Whether to run cleanup scripts before checkin.
    """
    now = utc_now_iso()
    if run_cleanup:
        run_cleanup_scripts(repo_root, agent_id, now=now)
    locks_dir = branch_paths.self_context_locks_dir(repo_root)
    locks_dir.mkdir(parents=True, exist_ok=True)
    active_path = repo_root / "context_compass" / "self_context" / "active_agents.json"
    profile_path = repo_root / "context_compass" / "self_context" / "agents" / f"{agent_id}.profile.json"
    active_path.parent.mkdir(parents=True, exist_ok=True)
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    policies = load_policies(repo_root)
    lock_owner = owner_id or agent_id

    locked = _acquire_locks(
        locks_dir,
        [active_path, profile_path],
        lock_owner,
        policies["lease_ttl_seconds"],
    )
    try:
        active = _load_or_init_active_agents(active_path, now)
        _upsert_active_agent(
            active,
            agent_id,
            mode,
            current_task_id,
            current_target,
            notes,
            agent_kind,
            model_name,
            runtime,
            now,
        )
        active["updated_at"] = now
        write_json_atomic(active_path, active)

        profile = _load_or_init_profile(profile_path, agent_id, now)
        _update_profile(
            profile,
            agent_id,
            mode,
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
        write_json_atomic(profile_path, profile)
    finally:
        _release_locks(locks_dir, locked, lock_owner)


def checkout(
    repo_root: Path,
    agent_id: str,
    mode: str,
    notes: Optional[str],
    command_name: Optional[str],
    command_args: Optional[list[str]],
    owner_id: Optional[str] = None,
    run_cleanup: bool = True,
) -> None:
    """
    Record a checkout for the agent and mark it inactive.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        mode (str): Agent mode.
        notes (Optional[str]): Optional notes.
        command_name (Optional[str]): Command name to record.
        command_args (Optional[list[str]]): Command arguments to record.
        owner_id (Optional[str]): Lock owner id override.
        run_cleanup (bool): Whether to run cleanup scripts before checkout.
    """
    now = utc_now_iso()
    if run_cleanup:
        run_cleanup_scripts(repo_root, agent_id, now=now)
    locks_dir = branch_paths.self_context_locks_dir(repo_root)
    locks_dir.mkdir(parents=True, exist_ok=True)
    active_path = repo_root / "context_compass" / "self_context" / "active_agents.json"
    profile_path = repo_root / "context_compass" / "self_context" / "agents" / f"{agent_id}.profile.json"
    active_path.parent.mkdir(parents=True, exist_ok=True)
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    policies = load_policies(repo_root)
    lock_owner = owner_id or agent_id

    locked = _acquire_locks(
        locks_dir,
        [active_path, profile_path],
        lock_owner,
        policies["lease_ttl_seconds"],
    )
    try:
        active = _load_or_init_active_agents(active_path, now)
        _remove_active_agent(active, agent_id)
        active["updated_at"] = now
        write_json_atomic(active_path, active)

        profile = _load_or_init_profile(profile_path, agent_id, now)
        _update_profile(
            profile,
            agent_id,
            mode,
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
        write_json_atomic(profile_path, profile)
    finally:
        _release_locks(locks_dir, locked, lock_owner)
