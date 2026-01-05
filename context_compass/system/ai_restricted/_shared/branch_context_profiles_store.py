"""
SQLite-backed helpers for branch context_profiles payloads.

Purpose
- Route context_profiles reads/writes/deletes through sqlite_query.
- Preserve the context_profiles payload shape at command boundaries.

Contract
- Profiles live under the shared context_profiles tables.
- Each branch uses branch_name as the primary key.
- Payloads follow context_profiles.schema.json at command boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json

from context_compass.system.ai_restricted.database_management import sqlite_query
from context_compass.system.ai_restricted.database_management.orm_session import user_db_path


QUEUE_TABLE_NAME = "context_profiles"
READ_CONTEXT_PROFILES_QUERY = "read_context_profiles"
WRITE_CONTEXT_PROFILES_QUERY = "write_context_profiles"
DELETE_CONTEXT_PROFILES_QUERY = "delete_context_profiles"


@dataclass(frozen=True)
class ContextProfilesSnapshot:
    """
    Snapshot of a context_profiles payload.

    Attributes:
        payload (dict[str, Any]): Context profiles payload.
        exists (bool): True if the record exists in SQLite.

    Contract:
        - payload is always a dict.
        - exists reports whether the branch row was found in SQLite.
    """

    payload: dict[str, Any]
    exists: bool


def table_name(_branch_name: str) -> str:
    """
    Return the shared SQLite table name for context profiles.

    Args:
        _branch_name (str): Branch identifier (unused).

    Returns:
        str: SQLite table name for context profiles.
    """

    return QUEUE_TABLE_NAME


def lock_resource(branch_name: str) -> Path:
    """
    Build a synthetic lock resource path for context profiles.

    Args:
        branch_name (str): Branch identifier.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"branch_context_profiles::{branch_name}")


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


def load_profiles(
    repo_root: Path,
    branch_name: str,
    actor_id: str,
) -> ContextProfilesSnapshot:
    """
    Load context_profiles payload from SQLite.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier reserved for audit logging.

    Returns:
        ContextProfilesSnapshot: Snapshot containing payload and existence flag.

    Raises:
        FileNotFoundError: If user.db is missing.
        ValueError: If the query returned an invalid payload.
    """

    try:
        response = sqlite_query.execute_request(
            repo_root,
            sqlite_query.SqliteQueryRequest(
                scope="user",
                query_name=READ_CONTEXT_PROFILES_QUERY,
                payload={"branch_name": branch_name},
                actor_id=actor_id,
            ),
        )
    except sqlite_query.SqliteQueryError as exc:
        _raise_query_error(exc, repo_root)

    result = response.output.get("result")
    if not isinstance(result, dict):
        raise ValueError("context_profiles read returned an invalid result payload.")
    record = result.get("record")
    exists = result.get("exists")
    if not isinstance(record, dict):
        raise ValueError("context_profiles read returned an invalid record payload.")
    if not isinstance(exists, bool):
        raise ValueError("context_profiles read returned an invalid exists flag.")
    return ContextProfilesSnapshot(payload=record, exists=exists)


def write_profiles(
    repo_root: Path,
    branch_name: str,
    payload: dict[str, Any],
    actor_id: str,
    *,
    exists: bool,
) -> None:
    """
    Persist context_profiles payload to SQLite.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        payload (dict[str, Any]): Context profiles payload.
        actor_id (str): Actor identifier for audit logging.
        exists (bool): Whether the record already exists.

    Raises:
        FileNotFoundError: If user.db is missing.
        ValueError: If payload validation fails.

    Contract:
        - Updates payload updated_at at write time.
        - Replaces profile rows with the provided payload state.
    """

    if not isinstance(payload, dict):
        raise ValueError("context_profiles payload must be a JSON object.")

    try:
        sqlite_query.execute_request(
            repo_root,
            sqlite_query.SqliteQueryRequest(
                scope="user",
                query_name=WRITE_CONTEXT_PROFILES_QUERY,
                payload={
                    "branch_name": branch_name,
                    "context_profiles": payload,
                    "exists": exists,
                },
                actor_id=actor_id,
            ),
        )
    except sqlite_query.SqliteQueryError as exc:
        _raise_query_error(exc, repo_root)


def delete_profiles(repo_root: Path, branch_name: str, actor_id: str) -> bool:
    """
    Delete context_profiles rows for a branch in SQLite.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier reserved for audit logging.

    Returns:
        bool: True if the core row existed and was removed.

    Raises:
        FileNotFoundError: If user.db is missing.
        ValueError: If the query returned an invalid payload.
    """

    try:
        response = sqlite_query.execute_request(
            repo_root,
            sqlite_query.SqliteQueryRequest(
                scope="user",
                query_name=DELETE_CONTEXT_PROFILES_QUERY,
                payload={"branch_name": branch_name},
                actor_id=actor_id,
            ),
        )
    except sqlite_query.SqliteQueryError as exc:
        _raise_query_error(exc, repo_root)

    result = response.output.get("result")
    if not isinstance(result, dict):
        raise ValueError("context_profiles delete returned an invalid result payload.")
    deleted = result.get("deleted")
    if not isinstance(deleted, bool):
        raise ValueError("context_profiles delete returned an invalid deleted flag.")
    return deleted
