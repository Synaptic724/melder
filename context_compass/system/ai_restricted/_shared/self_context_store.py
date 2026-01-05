"""
SQLite-backed storage helpers for self-context records.

Purpose
- Provide read/write access to self_context records in SQLite.
- Keep agent self-understanding state in relational user.db tables.

Contract
- Self-context records live in SQLite user.db table self_context with child tables
  for list and map fields.
- Payloads follow schemas/self_context.schema.json.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from context_compass.system.ai_restricted.database_management import sqlite_crud, sqlite_query
from context_compass.system.ai_restricted.database_management.orm_session import user_db_path


SELF_CONTEXT_TABLE_NAME = "self_context"
READ_SELF_CONTEXT_QUERY = "read_self_context"
WRITE_SELF_CONTEXT_QUERY = "write_self_context"
LIST_AGENT_IDS_ACTION = "list_agent_ids"


@dataclass(frozen=True)
class SelfContextSnapshot:
    """
    Snapshot of a self-context payload.

    Attributes:
        payload (dict[str, Any]): Self-context payload dictionary.
        exists (bool): True if the self-context record exists in SQLite.

    Contract:
        - payload is always a dict and matches self_context.schema.json.
        - exists reports whether the record was found in SQLite.
    """

    payload: dict[str, Any]
    exists: bool


def table_name(agent_id: str) -> str:
    """
    Return the SQLite table name for self-context records.

    Args:
        agent_id (str): Agent identifier (unused).

    Returns:
        str: SQLite table name for the self-context record.
    """

    return SELF_CONTEXT_TABLE_NAME


def lock_resource(agent_id: str) -> Path:
    """
    Build a synthetic lock resource path for a self-context record.

    Args:
        agent_id (str): Agent identifier.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"self_context::{agent_id}")


def _raise_query_error(exc: sqlite_query.SqliteQueryError, repo_root: Path) -> None:
    """
    Raise a consistent error for query failures.

    Args:
        exc (sqlite_query.SqliteQueryError): Query error to map.
        repo_root (Path): Repository root for error context.

    Raises:
        FileNotFoundError: If user.db is missing.
        ValueError: If the query payload is invalid.
        sqlite_query.SqliteQueryError: For unexpected query failures.
    """

    if exc.code == "db_missing":
        db_path = user_db_path(repo_root)
        raise FileNotFoundError(f"User database not found: {db_path}") from exc
    if exc.code.startswith("payload_"):
        details = json.dumps(exc.details, ensure_ascii=True)
        raise ValueError(f"{exc.meaning} Details: {details}") from exc
    raise exc


def default_self_context(agent_id: str, now: str) -> dict[str, Any]:
    """
    Build a default self-context payload.

    Args:
        agent_id (str): Agent identifier.
        now (str): Timestamp for created_at/updated_at fields.

    Returns:
        dict[str, Any]: Default self-context payload.
    """

    return {
        "schema_version": 1,
        "agent_id": agent_id,
        "created_at": now,
        "updated_at": now,
        "understanding": {
            "repo_purpose": "TODO: describe repo purpose",
            "non_negotiables": [],
            "style_model": {},
        },
        "skill_receipts": [],
        "open_questions": [],
        "opinions": {
            "what_is_working": [],
            "what_is_confusing": [],
            "suggested_skill_improvements": [],
        },
    }


def _require_mapping(payload: dict[str, Any], key: str) -> dict[str, Any]:
    """
    Require a mapping field in a payload.

    Args:
        payload (dict[str, Any]): Payload to inspect.
        key (str): Mapping key to extract.

    Returns:
        dict[str, Any]: Mapping value.

    Raises:
        ValueError: If the mapping is missing or invalid.
    """

    value = payload.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"self_context.{key} must be a JSON object.")
    return value


def _require_string(payload: dict[str, Any], key: str) -> str:
    """
    Require a non-empty string field.

    Args:
        payload (dict[str, Any]): Payload to inspect.
        key (str): Field name to extract.

    Returns:
        str: Field value.

    Raises:
        ValueError: If the field is missing or invalid.
    """

    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"self_context.{key} must be a non-empty string.")
    return value


def _require_int(payload: dict[str, Any], key: str) -> int:
    """
    Require an integer field.

    Args:
        payload (dict[str, Any]): Payload to inspect.
        key (str): Field name to extract.

    Returns:
        int: Field value.

    Raises:
        ValueError: If the field is missing or invalid.
    """

    value = payload.get(key)
    if not isinstance(value, int):
        raise ValueError(f"self_context.{key} must be an integer.")
    return value


def _string_list(payload: dict[str, Any], key: str) -> list[str]:
    """
    Return a list of strings from a payload field.

    Args:
        payload (dict[str, Any]): Payload to inspect.
        key (str): Field name to extract.

    Returns:
        list[str]: List of strings.

    Raises:
        ValueError: If the field is missing or invalid.
    """

    value = payload.get(key)
    if not isinstance(value, list):
        raise ValueError(f"self_context.{key} must be a list.")
    results: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError(f"self_context.{key} items must be strings.")
        results.append(item)
    return results


def _style_model_value(value: Any) -> tuple[str, str | None, float | None, bool | None, str | None]:
    """
    Normalize a style_model value into typed storage columns.

    Args:
        value (Any): Style model value.

    Returns:
        tuple[str, str | None, float | None, bool | None, str | None]:
            Value type plus text/number/bool/json column values.

    Raises:
        ValueError: If the value cannot be serialized.
    """

    if value is None:
        return "null", None, None, None, None
    if isinstance(value, bool):
        return "boolean", None, None, value, None
    if isinstance(value, (int, float)):
        return "number", None, float(value), None, None
    if isinstance(value, str):
        return "text", value, None, None, None
    try:
        encoded = json.dumps(value, separators=(",", ":"), ensure_ascii=True)
    except (TypeError, ValueError) as exc:
        raise ValueError("self_context.understanding.style_model contains non-serializable values.") from exc
    return "json", None, None, None, encoded


def _materialize_style_model(rows: list[SelfContextStyleModelItem]) -> dict[str, Any]:
    """
    Build the style_model object from stored rows.

    Args:
        rows (list[SelfContextStyleModelItem]): Stored style model rows.

    Returns:
        dict[str, Any]: Style model mapping.

    Raises:
        ValueError: If stored rows are inconsistent.
    """

    result: dict[str, Any] = {}
    for row in rows:
        if row.value_type == "text":
            if row.value_text is None:
                raise ValueError("self_context.style_model text values cannot be null.")
            result[row.style_key] = row.value_text
            continue
        if row.value_type == "number":
            if row.value_number is None:
                raise ValueError("self_context.style_model number values cannot be null.")
            result[row.style_key] = row.value_number
            continue
        if row.value_type == "boolean":
            if row.value_bool is None:
                raise ValueError("self_context.style_model boolean values cannot be null.")
            result[row.style_key] = row.value_bool
            continue
        if row.value_type == "json":
            if row.value_json is None:
                raise ValueError("self_context.style_model json values cannot be null.")
            result[row.style_key] = json.loads(row.value_json)
            continue
        if row.value_type == "null":
            result[row.style_key] = None
            continue
        raise ValueError(f"self_context.style_model has unsupported value_type: {row.value_type}")
    return result


def load_self_context(repo_root: Path, agent_id: str, actor_id: str) -> SelfContextSnapshot:
    """
    Load a self-context payload from SQLite.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        SelfContextSnapshot: Snapshot containing payload and existence flag.

    Raises:
        FileNotFoundError: If the user database is missing.
        ValueError: If the stored payload is not a dict.
    """

    try:
        response = sqlite_query.execute_request(
            repo_root,
            sqlite_query.SqliteQueryRequest(
                scope="user",
                query_name=READ_SELF_CONTEXT_QUERY,
                payload={"agent_id": agent_id},
                actor_id=actor_id,
            ),
        )
    except sqlite_query.SqliteQueryError as exc:
        _raise_query_error(exc, repo_root)

    result = response.output.get("result", {})
    record = result.get("record")
    exists = result.get("exists")
    if not isinstance(record, dict):
        raise ValueError("self_context read returned an invalid record payload.")
    if not isinstance(exists, bool):
        raise ValueError("self_context read returned an invalid exists flag.")
    return SelfContextSnapshot(payload=record, exists=exists)


def write_self_context(
    repo_root: Path,
    agent_id: str,
    payload: dict[str, Any],
    actor_id: str,
    *,
    exists: bool,
) -> None:
    """
    Persist a self-context payload to SQLite.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        payload (dict[str, Any]): Self-context payload to persist.
        actor_id (str): Actor identifier for audit logging.
        exists (bool): Whether the record already exists.

    Raises:
        FileNotFoundError: If the user database is missing.
        ValueError: If payload is not a dict.

    Contract:
        - Updates updated_at and updated_by on each write.
        - Replaces child rows with the provided payload state.
    """

    if not isinstance(payload, dict):
        raise ValueError("Self-context payload must be a JSON object.")
    if payload.get("agent_id") != agent_id:
        raise ValueError("self_context.agent_id must match the requested agent_id.")
    schema_version = payload.get("schema_version")
    if not isinstance(schema_version, int) or schema_version < 1:
        raise ValueError("self_context.schema_version must be an integer >= 1.")
    _require_string(payload, "created_at")
    _require_string(payload, "updated_at")
    understanding = _require_mapping(payload, "understanding")
    _require_string(understanding, "repo_purpose")
    _string_list(understanding, "non_negotiables")
    if not isinstance(understanding.get("style_model"), dict):
        raise ValueError("self_context.understanding.style_model must be a JSON object.")
    if not isinstance(payload.get("skill_receipts"), list):
        raise ValueError("self_context.skill_receipts must be a list.")
    if not isinstance(payload.get("open_questions"), list):
        raise ValueError("self_context.open_questions must be a list.")
    if not isinstance(payload.get("opinions"), dict):
        raise ValueError("self_context.opinions must be a JSON object.")

    try:
        sqlite_query.execute_request(
            repo_root,
            sqlite_query.SqliteQueryRequest(
                scope="user",
                query_name=WRITE_SELF_CONTEXT_QUERY,
                payload={
                    "agent_id": agent_id,
                    "self_context": payload,
                    "exists": exists,
                },
                actor_id=actor_id,
            ),
        )
    except sqlite_query.SqliteQueryError as exc:
        _raise_query_error(exc, repo_root)


def ensure_self_context(repo_root: Path, agent_id: str, actor_id: str) -> dict[str, Any]:
    """
    Ensure a default self-context record exists in SQLite.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        dict[str, Any]: The self-context payload after ensuring persistence.

    Raises:
        FileNotFoundError: If the user database is missing.
    """

    snapshot = load_self_context(repo_root, agent_id, actor_id)
    if snapshot.exists:
        return snapshot.payload
    write_self_context(repo_root, agent_id, snapshot.payload, actor_id, exists=False)
    return snapshot.payload


def list_agent_ids(repo_root: Path) -> list[str]:
    """
    List agent identifiers with registered self-context tables and records.

    Args:
        repo_root (Path): Repository root.

    Returns:
        list[str]: Agent identifiers that have a self-context record.
    """

    try:
        response = sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="read",
                scope="user",
                table_name=SELF_CONTEXT_TABLE_NAME,
                action=LIST_AGENT_IDS_ACTION,
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
        raise ValueError("self_context list returned an invalid agent_ids payload.")
    return [value for value in agent_ids if isinstance(value, str)]
