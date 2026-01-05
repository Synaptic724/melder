"""
SQLite-backed storage helpers for per-agent work queues.

Purpose
- Provide consistent read/write access to agent work queues via sqlite_query/sqlite_crud.
- Preserve the existing agent_work queue payload schema at command boundaries.

Contract
- Agent queues live in relational tables under user.db.
- Payloads follow the agent_work.schema.json shape.
- Query/API scripts own ORM interaction; this module routes requests.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json

from context_compass.system.ai_restricted.database_management import sqlite_crud, sqlite_query
from context_compass.system.ai_restricted.database_management.orm_session import user_db_path


QUEUE_TABLE_NAME = "agent_work_queue"
READ_QUEUE_QUERY = "read_agent_work_queue"
WRITE_QUEUE_QUERY = "write_agent_work_queue"
QUEUE_LIST_ACTION = "list_agent_ids"


@dataclass(frozen=True)
class AgentQueueSnapshot:
    """
    Snapshot of an agent work queue payload.

    Attributes:
        payload (dict[str, Any]): Queue payload dictionary.
        exists (bool): True if the queue record exists in SQLite.

    Contract:
        - payload is always a dict and contains a queue list.
        - exists reports whether the record was found in SQLite.
    """

    payload: dict[str, Any]
    exists: bool


def queue_table_name(agent_id: str) -> str:
    """
    Return the SQLite table name for agent work queues.

    Args:
        agent_id (str): Agent identifier (unused).

    Returns:
        str: SQLite table name for the queue.
    """

    return QUEUE_TABLE_NAME


def lock_resource(agent_id: str) -> Path:
    """
    Build a synthetic lock resource path for an agent queue table.

    Args:
        agent_id (str): Agent identifier.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"agent_work::{agent_id}")


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
    agent_id: str,
    actor_id: str,
) -> AgentQueueSnapshot:
    """
    Load a per-agent work queue payload from SQLite.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        AgentQueueSnapshot: Snapshot containing payload and existence flag.

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
                payload={"agent_id": agent_id},
                actor_id=actor_id,
            ),
        )
    except sqlite_query.SqliteQueryError as exc:
        _raise_query_error(exc, repo_root)

    result = response.output.get("result")
    if not isinstance(result, dict):
        raise ValueError("agent_work_queue read returned an invalid result payload.")
    queue_payload = result.get("queue")
    exists = result.get("exists")
    if not isinstance(queue_payload, dict):
        raise ValueError("agent_work_queue read returned an invalid queue payload.")
    if not isinstance(exists, bool):
        raise ValueError("agent_work_queue read returned an invalid exists flag.")
    return AgentQueueSnapshot(payload=queue_payload, exists=exists)


def write_queue(
    repo_root: Path,
    agent_id: str,
    payload: dict[str, Any],
    actor_id: str,
    *,
    exists: bool,
) -> None:
    """
    Persist a per-agent work queue payload to SQLite.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
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
        raise ValueError("Agent queue payload must be a JSON object.")

    try:
        sqlite_query.execute_request(
            repo_root,
            sqlite_query.SqliteQueryRequest(
                scope="user",
                query_name=WRITE_QUEUE_QUERY,
                payload={
                    "agent_id": agent_id,
                    "queue_payload": payload,
                    "exists": exists,
                },
                actor_id=actor_id,
            ),
        )
    except sqlite_query.SqliteQueryError as exc:
        _raise_query_error(exc, repo_root)


def list_agent_ids(repo_root: Path) -> list[str]:
    """
    List agent identifiers registered in the user SQLite registry.

    Args:
        repo_root (Path): Repository root.

    Returns:
        list[str]: Agent identifiers with registered queue tables.
    """

    try:
        response = sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="read",
                scope="user",
                table_name=QUEUE_TABLE_NAME,
                action=QUEUE_LIST_ACTION,
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
        raise ValueError("agent_work_queue list returned an invalid agent_ids payload.")
    return [value for value in agent_ids if isinstance(value, str)]
