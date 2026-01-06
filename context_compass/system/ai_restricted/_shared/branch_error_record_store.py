"""
SQLite-backed helpers for branch error records.

Purpose
- Route scan error record writes/deletes through sqlite_crud/sqlite_query.
- Keep error record payloads aligned to scan_error_records tooling.

Contract
- Error records live in scan_error_records in user.db.
- Each error record uses (branch_name, error_id) as a composite key.
- Payloads follow error_record.schema.json at command boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import json

from context_compass.system.ai_restricted.database_management import sqlite_crud, sqlite_query
from context_compass.system.ai_restricted.database_management.orm_session import user_db_path


ERROR_TABLE_NAME = "scan_error_records"
WRITE_ERROR_ACTION = "write_error_record"
DELETE_BRANCH_QUERY = "delete_scan_error_records_by_branch"


@dataclass(frozen=True)
class ErrorRecordSnapshot:
    """
    Snapshot of an error record payload.

    Attributes:
        payload (dict[str, Any]): Error record payload.
        exists (bool): True if the record exists in SQLite.

    Contract:
        - payload is always a dict.
        - exists reports whether the record was found.
    """

    payload: dict[str, Any]
    exists: bool


def table_name(branch_name: str) -> str:
    """
    Build the SQLite table name for error records.

    Args:
        branch_name (str): Branch identifier.

    Returns:
        str: SQLite table name for error records.
    """

    return ERROR_TABLE_NAME


def lock_resource(branch_name: str, error_id: str) -> Path:
    """
    Build a synthetic lock resource path for error records.

    Args:
        branch_name (str): Branch identifier.
        error_id (str): Error identifier.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"branch_error_record::{branch_name}::{error_id}")


def write_error_record(
    repo_root: Path,
    branch_name: str,
    error_id: str,
    payload: dict[str, Any],
    actor_id: str,
    *,
    exists: bool,
) -> None:
    """
    Persist an error record payload to SQLite.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        error_id (str): Error identifier.
        payload (dict[str, Any]): Error record payload.
        actor_id (str): Actor identifier for audit logging.
        exists (bool): Whether the record already exists.

    Raises:
        FileNotFoundError: If user.db is missing.
        ValueError: If payload is not a dict.

    Contract:
        - Replaces existing error rows for the error_id when present.
        - Stores details as minified JSON text.
    """

    if not isinstance(payload, dict):
        raise ValueError("Error record payload must be a JSON object.")

    try:
        sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="create",
                scope="user",
                table_name=ERROR_TABLE_NAME,
                action=WRITE_ERROR_ACTION,
                payload={
                    "branch_name": branch_name,
                    "error_id": error_id,
                    "error_record": payload,
                },
                actor_id=actor_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        if exc.code == "db_missing":
            db_path = user_db_path(repo_root)
            raise FileNotFoundError(f"User database not found: {db_path}") from exc
        if exc.code.startswith("payload_"):
            details = json.dumps(exc.details, ensure_ascii=True)
            raise ValueError(f"{exc.meaning} Details: {details}") from exc
        raise


def delete_branch_error_records(repo_root: Path, branch_name: str) -> None:
    """
    Delete all scan error records for a branch.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.

    Returns:
        None: Rows are deleted in-place.

    Raises:
        FileNotFoundError: If user.db is missing.
    """

    try:
        sqlite_query.execute_request(
            repo_root,
            sqlite_query.SqliteQueryRequest(
                scope="user",
                query_name=DELETE_BRANCH_QUERY,
                payload={"branch_name": branch_name},
                actor_id="system",
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
