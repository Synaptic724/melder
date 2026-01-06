"""
SQLite-backed storage helpers for agent profile records.

Purpose
- Provide read/write access to agent_profile records in SQLite.
- Keep agent lifecycle state in relational user.db tables.

Contract
- Profiles live in SQLite user.db table agent_profile with child tables for
  certification and last command details.
- Payloads follow schemas/agent_profile.schema.json.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from context_compass.system.ai_restricted._shared.certification_state import default_certification_state
from context_compass.system.ai_restricted._shared.timeutils import utc_now_iso
from context_compass.system.ai_restricted.database_management import sqlite_crud, sqlite_query


PROFILE_TABLE_NAME = "agent_profile"
QUERY_READ_AGENT_PROFILE = "read_agent_profile"
QUERY_WRITE_AGENT_PROFILE = "write_agent_profile"
PROFILE_LIST_ACTION = "list_agent_ids"


@dataclass(frozen=True)
class AgentProfileSnapshot:
    """
    Snapshot of an agent profile payload.

    Attributes:
        payload (dict[str, Any]): Profile payload dictionary.
        exists (bool): True if the profile record exists in SQLite.

    Contract:
        - payload is always a dict and matches agent_profile.schema.json.
        - exists reports whether the profile row was found in SQLite.
    """

    payload: dict[str, Any]
    exists: bool


def table_name(agent_id: str) -> str:
    """
    Return the SQLite table name for agent profiles.

    Args:
        agent_id (str): Agent identifier (unused).

    Returns:
        str: SQLite table name for the agent profile.
    """

    return PROFILE_TABLE_NAME


def lock_resource(agent_id: str) -> Path:
    """
    Build a synthetic lock resource path for an agent profile.

    Args:
        agent_id (str): Agent identifier.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"agent_profile::{agent_id}")


def default_profile(agent_id: str, now: str, agent_role: str | None = None) -> dict[str, Any]:
    """
    Build a default agent profile payload.

    Args:
        agent_id (str): Agent identifier.
        now (str): Timestamp for created_at/updated_at fields.
        agent_role (str | None): Career label for the agent profile.

    Returns:
        dict[str, Any]: Default profile payload.

    Contract:
        - When agent_role is provided it is stored as-is.
        - When agent_role is missing, a placeholder value is used for non-persisted defaults.
    """

    role_value = agent_role if isinstance(agent_role, str) and agent_role.strip() else "unassigned"
    return {
        "schema_version": 1,
        "agent_id": agent_id,
        "agent_kind": None,
        "created_at": now,
        "updated_at": now,
        "status": "inactive",
        "last_checkin_at": None,
        "last_checkout_at": None,
        "agent_role": role_value,
        "model_name": None,
        "current_task_id": None,
        "current_target": None,
        "notes": None,
        "runtime": None,
        "last_command": None,
        "certification_state": default_certification_state(),
    }


def _require_string(payload: dict[str, Any], key: str) -> str:
    """
    Require a non-empty string payload field.

    Args:
        payload (dict[str, Any]): Payload to inspect.
        key (str): Field name to extract.

    Returns:
        str: Field value.

    Raises:
        ValueError: If the field is missing or not a string.
    """

    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"agent_profile.{key} must be a non-empty string.")
    return value


def _optional_string(payload: dict[str, Any], key: str) -> str | None:
    """
    Return an optional string field.

    Args:
        payload (dict[str, Any]): Payload to inspect.
        key (str): Field name to extract.

    Returns:
        str | None: Field value if present.

    Raises:
        ValueError: If the field is not a string or null.
    """

    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"agent_profile.{key} must be a string or null.")
    return value


def _optional_bool(payload: dict[str, Any], key: str) -> bool | None:
    """
    Return an optional boolean field.

    Args:
        payload (dict[str, Any]): Payload to inspect.
        key (str): Field name to extract.

    Returns:
        bool | None: Field value if present.

    Raises:
        ValueError: If the field is not a boolean or null.
    """

    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ValueError(f"agent_profile.{key} must be a boolean or null.")
    return value


def _parse_last_command(payload: dict[str, Any]) -> tuple[str | None, list[str]]:
    """
    Parse last_command payload fields.

    Args:
        payload (dict[str, Any]): Profile payload.

    Returns:
        tuple[str | None, list[str]]: Command name and args list.

    Raises:
        ValueError: If last_command payload is invalid.
    """

    last_command = payload.get("last_command")
    if last_command is None:
        return None, []
    if not isinstance(last_command, dict):
        raise ValueError("agent_profile.last_command must be an object or null.")
    name = last_command.get("name")
    args = last_command.get("args")
    if not isinstance(name, str) or not name:
        raise ValueError("agent_profile.last_command.name must be a non-empty string.")
    if not isinstance(args, list):
        raise ValueError("agent_profile.last_command.args must be a list.")
    arg_values: list[str] = []
    for value in args:
        if not isinstance(value, str):
            raise ValueError("agent_profile.last_command.args entries must be strings.")
        arg_values.append(value)
    return name, arg_values


def _parse_certification_state(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Parse certification_state payload fields.

    Args:
        payload (dict[str, Any]): Profile payload.

    Returns:
        dict[str, Any]: Certification state payload.

    Raises:
        ValueError: If certification_state payload is invalid.
    """

    state = payload.get("certification_state")
    if state is None:
        return default_certification_state()
    if not isinstance(state, dict):
        raise ValueError("agent_profile.certification_state must be a JSON object.")
    return state


def load_profile(repo_root: Path, agent_id: str, actor_id: str) -> AgentProfileSnapshot:
    """
    Load an agent profile payload from SQLite.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        AgentProfileSnapshot: Snapshot containing payload and existence flag.

    Raises:
        FileNotFoundError: If the user database is missing.
        ValueError: If the stored payload is not a dict.
    """

    now = utc_now_iso()
    try:
        response = sqlite_query.execute_request(
            repo_root,
            sqlite_query.SqliteQueryRequest(
                scope="user",
                query_name=QUERY_READ_AGENT_PROFILE,
                payload={"agent_id": agent_id},
                actor_id=actor_id,
            ),
        )
    except sqlite_query.SqliteQueryError as exc:
        if exc.code == "db_missing":
            raise FileNotFoundError(
                "User database not found for agent_profile queries."
            ) from exc
        raise

    result = response.output.get("result", {})
    record = result.get("record")
    exists = result.get("exists")
    if not isinstance(record, dict):
        raise ValueError("agent_profile read returned an invalid record payload.")
    if not isinstance(exists, bool):
        raise ValueError("agent_profile read returned an invalid exists flag.")
    if not exists:
        return AgentProfileSnapshot(
            payload=default_profile(agent_id, now, agent_role="unassigned"),
            exists=False,
        )
    return AgentProfileSnapshot(payload=record, exists=exists)


def write_profile(
    repo_root: Path,
    agent_id: str,
    payload: dict[str, Any],
    actor_id: str,
    *,
    exists: bool,
) -> None:
    """
    Persist an agent profile payload to SQLite.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        payload (dict[str, Any]): Profile payload to persist.
        actor_id (str): Actor identifier for audit logging.
        exists (bool): Whether the profile record already exists.

    Raises:
        FileNotFoundError: If the user database is missing.
        ValueError: If payload is not a dict.

    Contract:
        - Updates updated_at and updated_by on each write.
        - Replaces child rows with the provided payload state.
    """

    if not isinstance(payload, dict):
        raise ValueError("Agent profile payload must be a JSON object.")
    if payload.get("agent_id") != agent_id:
        raise ValueError("agent_profile.agent_id must match the requested agent_id.")
    schema_version = payload.get("schema_version")
    if not isinstance(schema_version, int) or schema_version < 1:
        raise ValueError("agent_profile.schema_version must be an integer >= 1.")

    status = _require_string(payload, "status")
    agent_role = _require_string(payload, "agent_role")
    created_at = _require_string(payload, "created_at")
    updated_at = _require_string(payload, "updated_at")
    last_checkin_at = _optional_string(payload, "last_checkin_at")
    last_checkout_at = _optional_string(payload, "last_checkout_at")
    agent_kind = _optional_string(payload, "agent_kind")
    model_name = _optional_string(payload, "model_name")
    runtime = _optional_string(payload, "runtime")
    current_task_id = _optional_string(payload, "current_task_id")
    current_target = _optional_string(payload, "current_target")
    notes = _optional_string(payload, "notes")
    command_name, command_args = _parse_last_command(payload)
    certification = _parse_certification_state(payload)

    cert_schema_version = certification.get("schema_version")
    if not isinstance(cert_schema_version, int) or cert_schema_version < 1:
        raise ValueError("agent_profile.certification_state.schema_version must be >= 1.")
    cert_state = _require_string(certification, "state")
    certified = _optional_bool(certification, "certified")
    if certified is None:
        raise ValueError("agent_profile.certification_state.certified must be a boolean.")

    try:
        sqlite_query.execute_request(
            repo_root,
            sqlite_query.SqliteQueryRequest(
                scope="user",
                query_name=QUERY_WRITE_AGENT_PROFILE,
                payload={
                    "agent_id": agent_id,
                    "agent_profile": payload,
                    "exists": bool(exists),
                },
                actor_id=actor_id,
            ),
        )
    except sqlite_query.SqliteQueryError as exc:
        if exc.code == "db_missing":
            raise FileNotFoundError(
                "User database not found for agent_profile queries."
            ) from exc
        raise


def ensure_profile(repo_root: Path, agent_id: str, actor_id: str) -> dict[str, Any]:
    """
    Ensure a default agent profile record exists in SQLite.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        dict[str, Any]: The profile payload after ensuring persistence.

    Raises:
        FileNotFoundError: If the user database is missing.
    """

    snapshot = load_profile(repo_root, agent_id, actor_id)
    if snapshot.exists:
        return snapshot.payload
    write_profile(repo_root, agent_id, snapshot.payload, actor_id, exists=False)
    return snapshot.payload


def list_agent_ids(repo_root: Path) -> list[str]:
    """
    List agent identifiers with registered profile tables and records.

    Args:
        repo_root (Path): Repository root.

    Returns:
        list[str]: Agent identifiers that have a profile record.
    """

    try:
        response = sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="read",
                scope="user",
                table_name=PROFILE_TABLE_NAME,
                action=PROFILE_LIST_ACTION,
                payload=None,
                actor_id="system",
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        if exc.code == "db_missing":
            return []
        raise
    result = response.output.get("result", {})
    agent_ids = result.get("agent_ids")
    if not isinstance(agent_ids, list):
        raise ValueError("agent_profile list returned an invalid agent_ids payload.")
    return [value for value in agent_ids if isinstance(value, str)]
