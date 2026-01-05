"""
SQLite-backed storage helpers for branch work queues.

Purpose
- Provide consistent read/write access to branch work queues in SQLite.
- Preserve the existing queue payload schema while moving persistence to relational tables.

Contract
- Branch queues are stored in shared work_queues tables.
- Each queue is keyed by scope/bucket/work_kind and stored under a queue_id.
- Payloads follow the tasks.schema.json shape at command boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import json

from context_compass.system.ai_restricted.database_management import sqlite_query
from context_compass.system.ai_restricted.database_management.orm_session import user_db_path


QUEUE_SCOPE = "branch"
QUEUE_TABLE_NAME = "work_queues"
READ_QUEUE_QUERY = "read_branch_work_queue"
WRITE_QUEUE_QUERY = "write_branch_work_queue"
DELETE_QUEUE_QUERY = "delete_branch_work_queues"
DEFAULT_ACTOR_ID = "system:branch_work_queue_store"


@dataclass(frozen=True)
class BranchQueueSnapshot:
    """
    Snapshot of a branch work queue payload.

    Attributes:
        payload (dict[str, Any]): Queue payload dictionary.
        exists (bool): True if the queue record exists in SQLite.

    Contract:
        - payload is always a dict and contains a queue list.
        - exists reports whether the queue row was found in SQLite.
    """

    payload: dict[str, Any]
    exists: bool


def queue_table_name(_branch_name: str, _bucket: str, _work_type: str) -> str:
    """
    Return the SQLite table name for branch work queues.

    Args:
        _branch_name (str): Branch identifier (unused).
        _bucket (str): Work bucket name (unused).
        _work_type (str): Work type name (unused).

    Returns:
        str: SQLite table name for branch queues.
    """

    return QUEUE_TABLE_NAME


def lock_resource(branch_name: str, bucket: str, work_type: str) -> Path:
    """
    Build a synthetic lock resource path for a branch work queue.

    Args:
        branch_name (str): Branch identifier.
        bucket (str): Work bucket name.
        work_type (str): Work type name.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"branch_work_queue::{branch_name}::{bucket}::{work_type}")


def _queue_id(branch_name: str, bucket: str, work_type: str) -> str:
    """
    Build the queue_id for a branch work queue.

    Args:
        branch_name (str): Branch identifier.
        bucket (str): Work bucket name.
        work_type (str): Work type name.

    Returns:
        str: Stable queue identifier.
    """

    return f"{QUEUE_SCOPE}:{branch_name}:{bucket}:{work_type}"


def _default_queue(now: str) -> dict[str, Any]:
    """
    Build a default branch work queue payload.

    Args:
        now (str): Current timestamp.

    Returns:
        dict[str, Any]: Default queue payload with empty entries.
    """

    return {"schema_version": 1, "repo_id": None, "updated_at": now, "queue": []}


def _require_string(payload: dict[str, Any], key: str) -> str:
    """
    Require a non-empty string payload field.

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
        raise ValueError(f"tasks.{key} must be a non-empty string.")
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
        raise ValueError(f"tasks.{key} must be a string or null.")
    return value


def _require_int(payload: dict[str, Any], key: str) -> int:
    """
    Require an integer payload field.

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
        raise ValueError(f"tasks.{key} must be an integer.")
    return value


def _require_list(payload: dict[str, Any], key: str) -> list[Any]:
    """
    Require a list payload field.

    Args:
        payload (dict[str, Any]): Payload to inspect.
        key (str): Field name to extract.

    Returns:
        list[Any]: Field value.

    Raises:
        ValueError: If the field is missing or invalid.
    """

    value = payload.get(key)
    if not isinstance(value, list):
        raise ValueError(f"tasks.{key} must be a list.")
    return value


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


def load_queue(
    repo_root: Path,
    branch_name: str,
    bucket: str,
    work_type: str,
    actor_id: str,
) -> BranchQueueSnapshot:
    """
    Load a branch work queue payload from SQLite.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        bucket (str): Work bucket name.
        work_type (str): Work type name.
        actor_id (str): Actor identifier reserved for audit logging.

    Returns:
        BranchQueueSnapshot: Snapshot containing payload and existence flag.

    Raises:
        FileNotFoundError: If the user database is missing.
        ValueError: If the stored payload is not a dict.
    """

    try:
        response = sqlite_query.execute_request(
            repo_root,
            sqlite_query.SqliteQueryRequest(
                scope="user",
                query_name=READ_QUEUE_QUERY,
                payload={
                    "branch_name": branch_name,
                    "bucket": bucket,
                    "work_type": work_type,
                },
                actor_id=actor_id,
            ),
        )
    except sqlite_query.SqliteQueryError as exc:
        _raise_query_error(exc, repo_root)

    result = response.output.get("result")
    if not isinstance(result, dict):
        raise ValueError("branch_work_queue read returned an invalid result payload.")
    queue_payload = result.get("queue")
    exists = result.get("exists")
    if not isinstance(queue_payload, dict):
        raise ValueError("branch_work_queue read returned an invalid queue payload.")
    if not isinstance(exists, bool):
        raise ValueError("branch_work_queue read returned an invalid exists flag.")
    return BranchQueueSnapshot(payload=queue_payload, exists=exists)


def write_queue(
    repo_root: Path,
    branch_name: str,
    bucket: str,
    work_type: str,
    payload: dict[str, Any],
    actor_id: str,
    *,
    exists: bool,
) -> None:
    """
    Persist a branch work queue payload to SQLite.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        bucket (str): Work bucket name.
        work_type (str): Work type name.
        payload (dict[str, Any]): Queue payload to persist.
        actor_id (str): Actor identifier for audit logging.
        exists (bool): Whether the queue record already exists.

    Raises:
        FileNotFoundError: If the user database is missing.
        ValueError: If payload is not a dict.

    Contract:
        - updated_at is refreshed at write time when absent.
        - Replaces child rows with the provided payload state.
    """

    if not isinstance(payload, dict):
        raise ValueError("Queue payload must be a JSON object.")

    try:
        sqlite_query.execute_request(
            repo_root,
            sqlite_query.SqliteQueryRequest(
                scope="user",
                query_name=WRITE_QUEUE_QUERY,
                payload={
                    "branch_name": branch_name,
                    "bucket": bucket,
                    "work_type": work_type,
                    "queue_payload": payload,
                    "exists": exists,
                },
                actor_id=actor_id,
            ),
        )
    except sqlite_query.SqliteQueryError as exc:
        _raise_query_error(exc, repo_root)


def delete_branch_queues(repo_root: Path, branch_name: str, actor_id: str) -> list[str]:
    """
    Delete branch-scoped work queue rows from shared tables.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier reserved for audit logging.

    Returns:
        list[str]: Queue ids removed for the branch.

    Raises:
        FileNotFoundError: If the user database is missing.
    """

    try:
        response = sqlite_query.execute_request(
            repo_root,
            sqlite_query.SqliteQueryRequest(
                scope="user",
                query_name=DELETE_QUEUE_QUERY,
                payload={"branch_name": branch_name},
                actor_id=actor_id,
            ),
        )
    except sqlite_query.SqliteQueryError as exc:
        _raise_query_error(exc, repo_root)

    result = response.output.get("result")
    if not isinstance(result, dict):
        raise ValueError("branch_work_queue delete returned an invalid result payload.")
    queue_ids = result.get("queue_ids")
    if not isinstance(queue_ids, list):
        raise ValueError("branch_work_queue delete returned an invalid queue_ids payload.")
    if any(not isinstance(entry, str) for entry in queue_ids):
        raise ValueError("branch_work_queue delete returned non-string queue_ids.")
    return queue_ids
