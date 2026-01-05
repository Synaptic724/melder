"""
SQLite-backed helpers for branch registry and current branch state.

Purpose
- Record which branches exist in the system database.
- Store the active branch pointer in the user database.

Contract
- branch_registry is stored in the system DB under table branch_registry.
- current branch is stored in the user DB under table current_branch.
- Record ids are stable: branch name for registry, "current" for current branch.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from context_compass.system.ai_restricted.database_management import sqlite_crud
from context_compass.system.ai_restricted.database_management.orm_session import (
    system_db_path,
    user_db_path,
)


CURRENT_BRANCH_TABLE = "current_branch"
BRANCH_REGISTRY_TABLE = "branch_registry"
CURRENT_BRANCH_RECORD_ID = "current"
CURRENT_BRANCH_READ_ACTION = "by_record_id"
CURRENT_BRANCH_SET_ACTION = "set_current_branch"
BRANCH_REGISTRY_CREATE_ACTION = "register_branch"
BRANCH_REGISTRY_READ_ACTION = "by_branch_name"
BRANCH_REGISTRY_UPDATE_ACTION = "by_branch_name"


@dataclass(frozen=True)
class BranchRegistrySnapshot:
    """
    Snapshot for branch registry or current branch row data.

    Attributes:
        payload (dict[str, Any]): Stored row data payload.
        exists (bool): True if the record exists in SQLite.

    Contract:
        - payload is always a dict.
        - exists indicates whether a record was found.
    """

    payload: dict[str, Any]
    exists: bool


def _raise_crud_error(
    exc: sqlite_crud.SqliteCrudError,
    db_path: Path,
    message: str,
) -> None:
    """
    Raise a consistent error for CRUD lookup failures.

    Args:
        exc (sqlite_crud.SqliteCrudError): CRUD error to map.
        db_path (Path): Target database path for error context.
        message (str): Message to use for missing record cases.

    Raises:
        FileNotFoundError: If the target database is missing.
        RuntimeError: If required registry tables/actions are missing.
        sqlite_crud.SqliteCrudError: For unexpected CRUD failures.
    """

    if exc.code == "db_missing":
        raise FileNotFoundError(f"SQLite database not found: {db_path}") from exc
    if exc.code in {"table_missing", "table_not_registered", "action_not_registered", "registry_missing"}:
        raise RuntimeError(message) from exc
    raise exc


def _read_current_branch_record(repo_root: Path, actor_id: str) -> dict[str, Any]:
    """
    Read the current_branch record via sqlite_crud.

    Args:
        repo_root (Path): Repository root.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        dict[str, Any]: Current branch record payload.

    Raises:
        FileNotFoundError: If user.db is missing.
        RuntimeError: If required tables/actions are missing.
        ValueError: If the CRUD response payload is invalid.
        sqlite_crud.SqliteCrudError: For unexpected CRUD failures.
    """

    db_path = user_db_path(repo_root)
    try:
        response = sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="read",
                scope="user",
                table_name=CURRENT_BRANCH_TABLE,
                action=CURRENT_BRANCH_READ_ACTION,
                payload={"record_id": CURRENT_BRANCH_RECORD_ID},
                actor_id=actor_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        if exc.code == "record_not_found":
            raise FileNotFoundError(
                "Active branch not found; run branch_init or branch_switch first."
            ) from exc
        _raise_crud_error(
            exc,
            db_path,
            "Missing current_branch registry entries in user.db.",
        )
    record = response.output.get("result", {}).get("record")
    if not isinstance(record, dict):
        raise ValueError("current_branch read returned an invalid record payload.")
    return record


def _read_branch_registry_record(
    repo_root: Path,
    branch_name: str,
    actor_id: str,
) -> dict[str, Any]:
    """
    Read a branch_registry record via sqlite_crud.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        dict[str, Any]: Branch registry record payload.

    Raises:
        FileNotFoundError: If system.db is missing.
        RuntimeError: If required tables/actions are missing.
        ValueError: If the CRUD response payload is invalid.
        sqlite_crud.SqliteCrudError: For unexpected CRUD failures.
    """

    db_path = system_db_path(repo_root)
    try:
        response = sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="read",
                scope="system",
                table_name=BRANCH_REGISTRY_TABLE,
                action=BRANCH_REGISTRY_READ_ACTION,
                payload={"record_id": branch_name},
                actor_id=actor_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        _raise_crud_error(
            exc,
            db_path,
            "Missing branch_registry registry entries in system.db.",
        )
    record = response.output.get("result", {}).get("record")
    if not isinstance(record, dict):
        raise ValueError("branch_registry read returned an invalid record payload.")
    return record


def load_current_branch(repo_root: Path, actor_id: str) -> str:
    """
    Load the active branch name from the SQLite current_branch table.

    Args:
        repo_root (Path): Repository root.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        str: Active branch name.

    Raises:
        FileNotFoundError: If the user database or current branch row is missing.
        ValueError: If the stored payload is invalid.
        Exception: If the database session fails unexpectedly.
    """

    record = _read_current_branch_record(repo_root, actor_id)
    branch_name = record.get("branch_name")
    if not isinstance(branch_name, str) or not branch_name.strip():
        raise ValueError("Current branch payload missing branch_name.")
    return branch_name


def set_current_branch(repo_root: Path, branch_name: str, actor_id: str) -> None:
    """
    Persist the active branch name to the SQLite current_branch table.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch name to record.
        actor_id (str): Actor identifier for audit logging.

    Raises:
        FileNotFoundError: If the user database is missing.
        Exception: If the database session fails unexpectedly.
    """

    db_path = user_db_path(repo_root)
    try:
        sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="update",
                scope="user",
                table_name=CURRENT_BRANCH_TABLE,
                action=CURRENT_BRANCH_SET_ACTION,
                payload={
                    "record_id": CURRENT_BRANCH_RECORD_ID,
                    "branch_name": branch_name,
                    "notes": None,
                },
                actor_id=actor_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        _raise_crud_error(
            exc,
            db_path,
            "Missing current_branch registry entries in user.db.",
        )


def register_branch(repo_root: Path, branch_name: str, actor_id: str) -> None:
    """
    Register a branch in the system branch_registry table.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch name to register.
        actor_id (str): Actor identifier for audit logging.

    Raises:
        FileNotFoundError: If the system database is missing.
        Exception: If the database session fails unexpectedly.
    """

    db_path = system_db_path(repo_root)
    payload = {
        "record_id": branch_name,
        "branch_name": branch_name,
        "schema_version": 1,
        "status": "active",
        "notes": None,
    }
    try:
        sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="create",
                scope="system",
                table_name=BRANCH_REGISTRY_TABLE,
                action=BRANCH_REGISTRY_CREATE_ACTION,
                payload=payload,
                actor_id=actor_id,
            ),
        )
        return
    except sqlite_crud.SqliteCrudError as exc:
        if exc.code != "record_exists":
            _raise_crud_error(
                exc,
                db_path,
                "Missing branch_registry registry entries in system.db.",
            )

    try:
        sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="update",
                scope="system",
                table_name=BRANCH_REGISTRY_TABLE,
                action=BRANCH_REGISTRY_UPDATE_ACTION,
                payload=payload,
                actor_id=actor_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        _raise_crud_error(
            exc,
            db_path,
            "Missing branch_registry registry entries in system.db.",
        )


def branch_registered(repo_root: Path, branch_name: str, actor_id: str) -> bool:
    """
    Check whether a branch exists in the system branch_registry table.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch name to check.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        bool: True if the branch is registered, False otherwise.

    Raises:
        FileNotFoundError: If the system database is missing.
        Exception: If the database session fails unexpectedly.
    """

    db_path = system_db_path(repo_root)
    try:
        _read_branch_registry_record(repo_root, branch_name, actor_id)
    except sqlite_crud.SqliteCrudError as exc:
        if exc.code == "record_not_found":
            return False
        _raise_crud_error(
            exc,
            db_path,
            "Missing branch_registry registry entries in system.db.",
        )
    return True
