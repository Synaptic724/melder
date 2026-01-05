"""
SQLite-backed helpers for dir_ctx records stored in normalized tables.

Purpose
- Route dir_ctx reads/writes/deletes through sqlite_query scripts.
- Keep dir_ctx payloads aligned to dir_ctx.schema.json at command boundaries.

Contract
- Primary key for dir_ctx is (branch_name, dir_path).
- Query scripts must be registered in db_query_registry for user scope.
- Payloads returned by query scripts are treated as immutable snapshots.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from context_compass.system.ai_restricted.database_management import sqlite_query
from context_compass.system.ai_restricted.database_management.orm_session import user_db_path


READ_DIR_CTX_QUERY = "read_dir_ctx_by_dir_path"
READ_DIR_CTX_BY_CTX_PATH_QUERY = "read_dir_ctx_by_ctx_path"
LIST_DIR_CTX_QUERY = "list_dir_ctx_payloads"
WRITE_DIR_CTX_QUERY = "write_dir_ctx"
DELETE_DIR_CTX_BY_BRANCH_QUERY = "delete_dir_ctx_by_branch"


@dataclass(frozen=True)
class DirCtxSnapshot:
    """
    Snapshot of a dir_ctx payload.

    Attributes:
        payload (dict[str, Any]): Context payload.
        exists (bool): True if the record exists in SQLite.

    Contract:
        - payload is always a dict.
        - exists reports whether the record was found.
    """

    payload: dict[str, Any]
    exists: bool


def lock_resource(branch_name: str, dir_path: str) -> Path:
    """
    Build a synthetic lock resource path for dir_ctx updates.

    Args:
        branch_name (str): Branch identifier.
        dir_path (str): Repo-relative directory path.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"dir_ctx::{branch_name}::{dir_path}")


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


def load_dir_ctx(
    repo_root: Path,
    branch_name: str,
    dir_path: str,
    actor_id: str,
) -> DirCtxSnapshot:
    """
    Load a dir_ctx payload from SQLite.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        dir_path (str): Repo-relative directory path.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        DirCtxSnapshot: Snapshot containing payload and existence flag.

    Raises:
        FileNotFoundError: If user.db is missing.
        ValueError: If the stored payload is invalid.
    """

    try:
        response = sqlite_query.execute_request(
            repo_root,
            sqlite_query.SqliteQueryRequest(
                scope="user",
                query_name=READ_DIR_CTX_QUERY,
                payload={
                    "branch_name": branch_name,
                    "dir_path": dir_path,
                },
                actor_id=actor_id,
            ),
        )
    except sqlite_query.SqliteQueryError as exc:
        _raise_query_error(exc, repo_root)

    result = response.output.get("result")
    if not isinstance(result, dict):
        raise ValueError("dir_ctx read returned an invalid result payload.")
    record_payload = result.get("record")
    exists = result.get("exists")
    if not isinstance(record_payload, dict):
        raise ValueError("dir_ctx read returned an invalid record payload.")
    if not isinstance(exists, bool):
        raise ValueError("dir_ctx read returned an invalid exists flag.")
    return DirCtxSnapshot(payload=record_payload, exists=exists)


def load_dir_ctx_by_ctx_path(
    repo_root: Path,
    branch_name: str,
    ctx_path: str,
) -> DirCtxSnapshot:
    """
    Load a dir_ctx payload using its ctx_path value.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        ctx_path (str): Repo-relative ctx path.

    Returns:
        DirCtxSnapshot: Snapshot containing payload and existence flag.

    Raises:
        FileNotFoundError: If user.db is missing.
        ValueError: If the stored payload is invalid.
    """

    try:
        response = sqlite_query.execute_request(
            repo_root,
            sqlite_query.SqliteQueryRequest(
                scope="user",
                query_name=READ_DIR_CTX_BY_CTX_PATH_QUERY,
                payload={
                    "branch_name": branch_name,
                    "ctx_path": ctx_path,
                },
                actor_id="system",
            ),
        )
    except sqlite_query.SqliteQueryError as exc:
        _raise_query_error(exc, repo_root)

    result = response.output.get("result")
    if not isinstance(result, dict):
        raise ValueError("dir_ctx read returned an invalid result payload.")
    record_payload = result.get("record")
    exists = result.get("exists")
    if not isinstance(record_payload, dict):
        raise ValueError("dir_ctx read returned an invalid record payload.")
    if not isinstance(exists, bool):
        raise ValueError("dir_ctx read returned an invalid exists flag.")
    return DirCtxSnapshot(payload=record_payload, exists=exists)


def list_dir_ctx(repo_root: Path, branch_name: str) -> list[dict[str, Any]]:
    """
    List dir_ctx payloads for a branch.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.

    Returns:
        list[dict[str, Any]]: dir_ctx payloads for the branch.

    Raises:
        FileNotFoundError: If user.db is missing.
        ValueError: If the stored payload is invalid.
    """

    try:
        response = sqlite_query.execute_request(
            repo_root,
            sqlite_query.SqliteQueryRequest(
                scope="user",
                query_name=LIST_DIR_CTX_QUERY,
                payload={"branch_name": branch_name},
                actor_id="system",
            ),
        )
    except sqlite_query.SqliteQueryError as exc:
        _raise_query_error(exc, repo_root)

    result = response.output.get("result")
    if not isinstance(result, dict):
        raise ValueError("dir_ctx list returned an invalid result payload.")
    records = result.get("records")
    if not isinstance(records, list):
        raise ValueError("dir_ctx list returned an invalid records payload.")
    return records


def write_dir_ctx(
    repo_root: Path,
    branch_name: str,
    payload: dict[str, Any],
    actor_id: str,
    *,
    exists: bool,
) -> None:
    """
    Persist a dir_ctx payload to SQLite.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        payload (dict[str, Any]): Context payload.
        actor_id (str): Actor identifier for audit logging.
        exists (bool): Whether the record already exists.

    Raises:
        FileNotFoundError: If user.db is missing.
        ValueError: If payload validation fails.

    Contract:
        - Writes are delegated to sqlite_query for atomic persistence.
        - The payload must contain kind="dir_ctx".
    """

    if not isinstance(payload, dict):
        raise ValueError("dir_ctx payload must be a JSON object.")

    try:
        sqlite_query.execute_request(
            repo_root,
            sqlite_query.SqliteQueryRequest(
                scope="user",
                query_name=WRITE_DIR_CTX_QUERY,
                payload={
                    "branch_name": branch_name,
                    "dir_ctx": payload,
                    "exists": exists,
                },
                actor_id=actor_id,
            ),
        )
    except sqlite_query.SqliteQueryError as exc:
        _raise_query_error(exc, repo_root)


def delete_branch_dir_ctx(repo_root: Path, branch_name: str) -> None:
    """
    Delete all dir_ctx records for a branch.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.

    Returns:
        None: Rows are deleted in-place.

    Raises:
        FileNotFoundError: If user.db is missing.
        ValueError: If the stored payload is invalid.
    """

    try:
        sqlite_query.execute_request(
            repo_root,
            sqlite_query.SqliteQueryRequest(
                scope="user",
                query_name=DELETE_DIR_CTX_BY_BRANCH_QUERY,
                payload={"branch_name": branch_name},
                actor_id="system",
            ),
        )
    except sqlite_query.SqliteQueryError as exc:
        _raise_query_error(exc, repo_root)
