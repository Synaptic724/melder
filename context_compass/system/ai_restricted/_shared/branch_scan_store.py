"""
SQLite-backed helpers for branch scan records.

Purpose
- Store scan records in SQLite by scan_id.

Contract
- Scan records live in relational scan_* tables in user.db.
- Each scan run is addressed by (branch_name, scan_id).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from context_compass.system.ai_restricted.database_management import sqlite_query
from context_compass.system.ai_restricted.database_management.orm_session import user_db_path


SCAN_REGISTRY_TABLE = "scan_registry"
DELETE_SCAN_RECORDS_QUERY = "delete_scan_records_by_branch"
DEFAULT_ACTOR_ID = "system:branch_scan_store"


@dataclass(frozen=True)
class ScanRecordSnapshot:
    """
    Snapshot of a scan record payload.

    Attributes:
        payload (dict[str, Any]): Scan record payload.
        exists (bool): True if the record exists in SQLite.

    Contract:
        - payload is always a dict.
        - exists reports whether the record was found.
    """

    payload: dict[str, Any]
    exists: bool


def table_name(branch_name: str) -> str:
    """
    Build the SQLite table name for scan records.

    Args:
        branch_name (str): Branch identifier.

    Returns:
        str: SQLite table name for scan records.
    """

    _ = branch_name
    return SCAN_REGISTRY_TABLE


def lock_resource(branch_name: str, scan_id: str) -> Path:
    """
    Build a synthetic lock resource path for scan records.

    Args:
        branch_name (str): Branch identifier.
        scan_id (str): Scan identifier.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"branch_scan::{branch_name}::{scan_id}")


def write_scan_record(
    repo_root: Path,
    branch_name: str,
    scan_id: str,
    payload: dict[str, Any],
    actor_id: str,
    *,
    exists: bool,
) -> None:
    """
    Persist a scan record payload to SQLite.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        scan_id (str): Scan identifier.
        payload (dict[str, Any]): Scan record payload.
        actor_id (str): Actor identifier for audit logging.
        exists (bool): Whether the record already exists.

    Raises:
        FileNotFoundError: If user.db is missing.
        ValueError: If payload is not a dict.

    Contract:
        - Delegates persistence to the SQLite query API for atomic writes.
        - Replaces existing scan rows for the scan_id when present.
        - Uses relational tables with audit fields for all rows.
    """

    if not isinstance(payload, dict):
        raise ValueError("Scan record payload must be a JSON object.")

    scan_id_payload = _require_string(payload, "scan_id", "scan_record")
    if scan_id_payload != scan_id:
        raise ValueError("scan_record.scan_id must match the scan_id argument.")

    try:
        sqlite_query.execute_request(
            repo_root,
            sqlite_query.SqliteQueryRequest(
                scope="user",
                query_name="write_scan_record",
                payload={
                    "branch_name": branch_name,
                    "scan_id": scan_id,
                    "scan_record": payload,
                },
                actor_id=actor_id,
            ),
        )
    except sqlite_query.SqliteQueryError as exc:
        if exc.code == "db_missing":
            db_path = user_db_path(repo_root)
            raise FileNotFoundError(f"User database not found: {db_path}") from exc
        if exc.code.startswith("payload_"):
            details = json.dumps(exc.details, ensure_ascii=True)
            raise ValueError(f"{exc.meaning} Details: {details}") from exc
        raise


def _require_mapping(payload: dict[str, Any], key: str, context: str) -> dict[str, Any]:
    """
    Require a mapping value in a payload.

    Args:
        payload (dict[str, Any]): Payload to inspect.
        key (str): Mapping key to extract.
        context (str): Context label for error reporting.

    Returns:
        dict[str, Any]: Mapping value.

    Raises:
        ValueError: If the mapping is missing or invalid.
    """

    value = payload.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{context}.{key} must be a JSON object.")
    return value


def _require_list(payload: dict[str, Any], key: str, context: str) -> list[Any]:
    """
    Require a list value in a payload.

    Args:
        payload (dict[str, Any]): Payload to inspect.
        key (str): List key to extract.
        context (str): Context label for error reporting.

    Returns:
        list[Any]: List value.

    Raises:
        ValueError: If the list is missing or invalid.
    """

    value = payload.get(key)
    if not isinstance(value, list):
        raise ValueError(f"{context}.{key} must be a list.")
    return value


def _require_string(payload: dict[str, Any], key: str, context: str) -> str:
    """
    Require a non-empty string value in a payload.

    Args:
        payload (dict[str, Any]): Payload to inspect.
        key (str): String key to extract.
        context (str): Context label for error reporting.

    Returns:
        str: String value.

    Raises:
        ValueError: If the value is missing or invalid.
    """

    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{context}.{key} must be a non-empty string.")
    return value


def _optional_string(payload: dict[str, Any], key: str, context: str) -> str | None:
    """
    Return an optional string value from a payload.

    Args:
        payload (dict[str, Any]): Payload to inspect.
        key (str): String key to extract.
        context (str): Context label for error reporting.

    Returns:
        str | None: String value or None if missing.

    Raises:
        ValueError: If the value is not a string or null.
    """

    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{context}.{key} must be a string or null.")
    return value


def _require_int(payload: dict[str, Any], key: str, context: str) -> int:
    """
    Require an integer value in a payload.

    Args:
        payload (dict[str, Any]): Payload to inspect.
        key (str): Integer key to extract.
        context (str): Context label for error reporting.

    Returns:
        int: Integer value.

    Raises:
        ValueError: If the value is missing or invalid.
    """

    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{context}.{key} must be an integer.")
    return value


def _require_string_list(payload: dict[str, Any], key: str, context: str) -> list[str]:
    """
    Require a list of strings in a payload.

    Args:
        payload (dict[str, Any]): Payload to inspect.
        key (str): List key to extract.
        context (str): Context label for error reporting.

    Returns:
        list[str]: List of strings.

    Raises:
        ValueError: If the list is missing or contains non-strings.
    """

    value = payload.get(key)
    if not isinstance(value, list):
        raise ValueError(f"{context}.{key} must be a list.")
    if any(not isinstance(item, str) for item in value):
        raise ValueError(f"{context}.{key} must contain only strings.")
    return value


def _raise_query_error(
    exc: sqlite_query.SqliteQueryError,
    repo_root: Path,
) -> None:
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


def delete_branch_scan_records(repo_root: Path, branch_name: str) -> None:
    """
    Delete all scan records for a branch via the query API.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.

    Returns:
        None: Deletion is performed via the query API.

    Raises:
        FileNotFoundError: If user.db is missing.
        ValueError: If the query payload is invalid.
        sqlite_query.SqliteQueryError: For unexpected query failures.
    """

    try:
        sqlite_query.execute_request(
            repo_root,
            sqlite_query.SqliteQueryRequest(
                scope="user",
                query_name=DELETE_SCAN_RECORDS_QUERY,
                payload={"branch_name": branch_name},
                actor_id=DEFAULT_ACTOR_ID,
            ),
        )
    except sqlite_query.SqliteQueryError as exc:
        _raise_query_error(exc, repo_root)
