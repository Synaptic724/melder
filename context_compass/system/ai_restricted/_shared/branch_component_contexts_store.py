"""
SQLite-backed helpers for component_contexts payloads.

Purpose
- Store component_contexts and test_component_contexts records via SQLite queries.
- Provide defaults for new branches when no record exists.

Contract
- Records live in the component_contexts table with branch_name + kind keys.
- Payloads follow component_contexts.schema.json.
- Query execution is delegated to sqlite_query.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from context_compass.system.ai_restricted._shared import architecture_contexts
from context_compass.system.ai_restricted.database_management import sqlite_query
from context_compass.system.ai_restricted.database_management.orm_session import user_db_path


COMPONENT_CONTEXTS_TABLE = "component_contexts"
QUERY_READ_COMPONENT_CONTEXTS = "read_component_contexts"
QUERY_WRITE_COMPONENT_CONTEXTS = "write_component_contexts"
QUERY_DELETE_COMPONENT_CONTEXTS = "delete_component_contexts"


@dataclass(frozen=True)
class ComponentContextsSnapshot:
    """
    Snapshot of a component_contexts payload.

    Attributes:
        payload (dict[str, Any]): Context payload.
        exists (bool): True if the record exists in SQLite.

    Contract:
        - payload is always a dict.
        - exists reports whether the record was found.
    """

    payload: dict[str, Any]
    exists: bool


def table_name(_branch_name: str) -> str:
    """
    Return the SQLite table name for component contexts.

    Args:
        _branch_name (str): Branch identifier (unused).

    Returns:
        str: SQLite table name for component contexts.
    """

    return COMPONENT_CONTEXTS_TABLE


def lock_resource(branch_name: str, kind: str) -> Path:
    """
    Build a synthetic lock resource path for component contexts.

    Args:
        branch_name (str): Branch identifier.
        kind (str): Context kind.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"branch_component_contexts::{branch_name}::{kind}")


def default_context(kind: str, now: str) -> dict[str, Any]:
    """
    Return a default component_contexts payload.

    Args:
        kind (str): Context kind.
        now (str): Current timestamp.

    Returns:
        dict[str, Any]: Default context payload.
    """

    return architecture_contexts.default_component_contexts(kind, now)


def _raise_query_error(
    exc: sqlite_query.SqliteQueryError,
    db_path: Path,
    message: str,
) -> None:
    """
    Raise a consistent error for query execution failures.

    Args:
        exc (sqlite_query.SqliteQueryError): Query error to map.
        db_path (Path): User database path for error context.
        message (str): Message to use for missing registry cases.

    Raises:
        FileNotFoundError: If user.db is missing.
        RuntimeError: If registry or query metadata is missing.
        ValueError: If the query payload is invalid.
        sqlite_query.SqliteQueryError: For unexpected query failures.
    """

    if exc.code == "db_missing":
        raise FileNotFoundError(f"User database not found: {db_path}") from exc
    if exc.code in {
        "registry_missing",
        "query_not_registered",
        "query_scope_mismatch",
        "query_disabled",
        "script_path_missing",
    }:
        raise RuntimeError(message) from exc
    if exc.code in {"payload_invalid", "payload_type_error", "payload_value_error"}:
        raise ValueError(exc.meaning) from exc
    raise exc


def _read_snapshot(
    repo_root: Path,
    branch_name: str,
    kind: str,
    actor_id: str,
) -> ComponentContextsSnapshot:
    """
    Read a component_contexts snapshot via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        kind (str): Context kind.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        ComponentContextsSnapshot: Snapshot containing payload and existence flag.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_READ_COMPONENT_CONTEXTS,
            payload={"branch_name": branch_name, "kind": kind},
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    record = result.get("record")
    exists = result.get("exists")
    if not isinstance(record, dict):
        raise ValueError("component_contexts read returned an invalid record payload.")
    if not isinstance(exists, bool):
        raise ValueError("component_contexts read returned an invalid exists flag.")
    return ComponentContextsSnapshot(payload=record, exists=exists)


def load_context(
    repo_root: Path,
    branch_name: str,
    kind: str,
    actor_id: str,
) -> ComponentContextsSnapshot:
    """
    Load a component contexts payload from SQLite.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        kind (str): Context kind (component_contexts/test_component_contexts).
        actor_id (str): Actor identifier for audit logging.

    Returns:
        ComponentContextsSnapshot: Snapshot containing payload and existence flag.

    Raises:
        FileNotFoundError: If user.db is missing.
        RuntimeError: If registry or query metadata is missing.
        ValueError: If the query response payload is invalid.
    """

    db_path = user_db_path(repo_root)
    try:
        return _read_snapshot(repo_root, branch_name, kind, actor_id)
    except sqlite_query.SqliteQueryError as exc:
        _raise_query_error(
            exc,
            db_path,
            "Missing component_contexts query registry entries in user.db.",
        )


def write_context(
    repo_root: Path,
    branch_name: str,
    kind: str,
    payload: dict[str, Any],
    actor_id: str,
    *,
    exists: bool,
) -> None:
    """
    Persist a component contexts payload to SQLite.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        kind (str): Context kind.
        payload (dict[str, Any]): Context payload.
        actor_id (str): Actor identifier for audit logging.
        exists (bool): Whether the record already exists.

    Raises:
        FileNotFoundError: If user.db is missing.
        ValueError: If payload validation fails.
    """

    if not isinstance(payload, dict):
        raise ValueError("component_contexts payload must be a JSON object.")

    db_path = user_db_path(repo_root)
    try:
        sqlite_query.execute_request(
            repo_root,
            sqlite_query.SqliteQueryRequest(
                scope="user",
                query_name=QUERY_WRITE_COMPONENT_CONTEXTS,
                payload={
                    "branch_name": branch_name,
                    "kind": kind,
                    "context": payload,
                    "exists": exists,
                },
                actor_id=actor_id,
            ),
        )
    except sqlite_query.SqliteQueryError as exc:
        _raise_query_error(
            exc,
            db_path,
            "Missing component_contexts query registry entries in user.db.",
        )


def delete_context(
    repo_root: Path,
    branch_name: str,
    kind: str,
) -> bool:
    """
    Delete a component_contexts record and its child rows.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        kind (str): Context kind to delete.

    Returns:
        bool: True if a record was deleted, False if no record existed.

    Raises:
        FileNotFoundError: If user.db is missing.
        RuntimeError: If registry or query metadata is missing.
        ValueError: If the query response payload is invalid.
    """

    db_path = user_db_path(repo_root)
    try:
        response = sqlite_query.execute_request(
            repo_root,
            sqlite_query.SqliteQueryRequest(
                scope="user",
                query_name=QUERY_DELETE_COMPONENT_CONTEXTS,
                payload={"branch_name": branch_name, "kind": kind},
                actor_id="system:branch_component_contexts_store",
            ),
        )
    except sqlite_query.SqliteQueryError as exc:
        _raise_query_error(
            exc,
            db_path,
            "Missing component_contexts query registry entries in user.db.",
        )
    result = response.output.get("result", {})
    deleted = result.get("deleted")
    if not isinstance(deleted, bool):
        raise ValueError("component_contexts delete returned an invalid deleted flag.")
    return deleted
