"""
SQLite-backed helpers for architecture_context payloads.

Purpose
- Store architecture_context and test_architecture_context records via SQLite queries.
- Provide defaults for new branches when no record exists.

Contract
- Records live in the architecture_context table with branch_name + kind keys.
- Payloads follow architecture_context.schema.json.
- Query execution is delegated to sqlite_query.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from context_compass.system.ai_restricted._shared import architecture_contexts
from context_compass.system.ai_restricted.database_management import sqlite_query
from context_compass.system.ai_restricted.database_management.orm_session import user_db_path


ARCHITECTURE_CONTEXT_TABLE = "architecture_context"
QUERY_READ_ARCHITECTURE_CONTEXT = "read_architecture_context"
QUERY_WRITE_ARCHITECTURE_CONTEXT = "write_architecture_context"
QUERY_DELETE_ARCHITECTURE_CONTEXT = "delete_architecture_context"


@dataclass(frozen=True)
class ArchitectureContextSnapshot:
    """
    Snapshot of an architecture_context payload.

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
    Return the SQLite table name for architecture contexts.

    Args:
        _branch_name (str): Branch identifier (unused).

    Returns:
        str: SQLite table name for architecture contexts.
    """

    return ARCHITECTURE_CONTEXT_TABLE


def lock_resource(branch_name: str, kind: str) -> Path:
    """
    Build a synthetic lock resource path for architecture contexts.

    Args:
        branch_name (str): Branch identifier.
        kind (str): Context kind.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"branch_architecture_context::{branch_name}::{kind}")


def default_context(kind: str, now: str) -> dict[str, Any]:
    """
    Return a default architecture context payload.

    Args:
        kind (str): Context kind.
        now (str): Current timestamp.

    Returns:
        dict[str, Any]: Default context payload.
    """

    return architecture_contexts.default_architecture_context(kind, now)


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
) -> ArchitectureContextSnapshot:
    """
    Read an architecture_context snapshot via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        kind (str): Context kind.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        ArchitectureContextSnapshot: Snapshot containing payload and existence flag.

    Raises:
        FileNotFoundError: If user.db is missing.
        RuntimeError: If registry or query metadata is missing.
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: For unexpected query failures.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_READ_ARCHITECTURE_CONTEXT,
            payload={"branch_name": branch_name, "kind": kind},
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    record = result.get("record")
    exists = result.get("exists")
    if not isinstance(record, dict):
        raise ValueError("architecture_context read returned an invalid record payload.")
    if not isinstance(exists, bool):
        raise ValueError("architecture_context read returned an invalid exists flag.")
    return ArchitectureContextSnapshot(payload=record, exists=exists)


def load_context(
    repo_root: Path,
    branch_name: str,
    kind: str,
    actor_id: str,
) -> ArchitectureContextSnapshot:
    """
    Load an architecture context payload from SQLite.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        kind (str): Context kind (architecture_context/test_architecture_context).
        actor_id (str): Actor identifier for audit logging.

    Returns:
        ArchitectureContextSnapshot: Snapshot containing payload and existence flag.

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
            "Missing architecture_context query registry entries in user.db.",
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
    Persist an architecture context payload to SQLite.

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
        raise ValueError("architecture_context payload must be a JSON object.")

    db_path = user_db_path(repo_root)
    try:
        sqlite_query.execute_request(
            repo_root,
            sqlite_query.SqliteQueryRequest(
                scope="user",
                query_name=QUERY_WRITE_ARCHITECTURE_CONTEXT,
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
            "Missing architecture_context query registry entries in user.db.",
        )


def delete_context(
    repo_root: Path,
    branch_name: str,
    kind: str,
) -> bool:
    """
    Delete an architecture_context record and its child rows.

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
                query_name=QUERY_DELETE_ARCHITECTURE_CONTEXT,
                payload={"branch_name": branch_name, "kind": kind},
                actor_id="system:branch_architecture_context_store",
            ),
        )
    except sqlite_query.SqliteQueryError as exc:
        _raise_query_error(
            exc,
            db_path,
            "Missing architecture_context query registry entries in user.db.",
        )
    result = response.output.get("result", {})
    deleted = result.get("deleted")
    if not isinstance(deleted, bool):
        raise ValueError("architecture_context delete returned an invalid deleted flag.")
    return deleted
