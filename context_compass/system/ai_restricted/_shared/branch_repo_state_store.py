"""
SQLite-backed helpers for branch repo_state payloads.

Purpose
- Store repo_state records for each branch in SQLite.
- Provide defaults for new branches and safe update helpers.

Contract
- Repo state lives in the shared repo_state table in user.db.
- Each branch uses branch_name as the primary key.
- Disabled tooling features are stored in repo_state_tooling_disabled_features rows.
- Payloads follow repo_state.schema.json at command boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from context_compass.system.ai_restricted.database_management import sqlite_crud, sqlite_query
from context_compass.system.ai_restricted.database_management.orm_session import user_db_path
from context_compass.system.ai_restricted._shared.timeutils import utc_now_iso


REPO_STATE_RECORD_ID = "current"
REPO_STATE_TABLE = "repo_state"
REPO_STATE_ACTION = "by_branch_name"
QUERY_WRITE_REPO_STATE = "write_repo_state"
QUERY_DELETE_REPO_STATE = "delete_repo_state"
LIFECYCLE_STAGES = (
    "new",
    "active_dev",
    "stable",
    "production",
    "maintenance",
    "experimental",
    "archived",
)
TOOLING_POLICY_MODES = ("normal", "restricted")


@dataclass(frozen=True)
class RepoStateSnapshot:
    """
    Snapshot of a repo_state payload.

    Attributes:
        payload (dict[str, Any]): Repo state payload.
        exists (bool): True if the record exists in SQLite.

    Contract:
        - payload is always a dict.
        - exists reports whether the record was found in SQLite.
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
        db_path (Path): User database path for error context.
        message (str): Message to use for missing record cases.

    Raises:
        FileNotFoundError: If user.db is missing.
        RuntimeError: If required tables or registry entries are missing.
        sqlite_crud.SqliteCrudError: For unexpected CRUD failures.
    """

    if exc.code == "db_missing":
        raise FileNotFoundError(f"User database not found: {db_path}") from exc
    if exc.code in {"table_missing", "table_not_registered", "action_not_registered", "registry_missing"}:
        raise RuntimeError(message) from exc
    raise exc


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


def _read_repo_state_record(
    repo_root: Path,
    branch_name: str,
    actor_id: str,
) -> tuple[dict[str, Any], bool]:
    """
    Read repo_state records via sqlite_crud.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        tuple[dict[str, Any], bool]: Repo state payload and exists flag.

    Raises:
        FileNotFoundError: If user.db is missing.
        RuntimeError: If required tables or registry entries are missing.
        ValueError: If the CRUD response payload is invalid.
        sqlite_crud.SqliteCrudError: For unexpected CRUD failures.
    """

    db_path = user_db_path(repo_root)
    response = sqlite_crud.execute_request(
        repo_root,
        sqlite_crud.SqliteCrudRequest(
            operation="read",
            scope="user",
            table_name=REPO_STATE_TABLE,
            action=REPO_STATE_ACTION,
            payload={"branch_name": branch_name},
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    record = result.get("record")
    exists = result.get("exists")
    if not isinstance(record, dict):
        raise ValueError("repo_state read returned an invalid record payload.")
    if not isinstance(exists, bool):
        raise ValueError("repo_state read returned an invalid exists flag.")
    return record, exists


def table_name(branch_name: str) -> str:
    """
    Build the SQLite table name for branch repo_state.

    Args:
        branch_name (str): Branch identifier.

    Returns:
        str: SQLite table name for repo_state.

    Contract:
        - The table name is shared across branches.
        - branch_name is not used to form the table name.
    """

    return REPO_STATE_TABLE


def lock_resource(branch_name: str) -> Path:
    """
    Build a synthetic lock resource path for repo_state.

    Args:
        branch_name (str): Branch identifier.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"branch_repo_state::{branch_name}")


def default_repo_state(repo_root: Path, now: str) -> dict[str, Any]:
    """
    Return a default repo_state payload.

    Args:
        repo_root (Path): Repository root.
        now (str): Current timestamp.

    Returns:
        dict[str, Any]: Repo state payload.
    """

    return {
        "schema_version": 1,
        "repo_id": None,
        "repo_root": str(repo_root),
        "git": {"head": None},
        "scan_counter": 0,
        "last_scan_id": None,
        "last_scan_at": None,
        "scanner_version": None,
        "template_versions": {"file_ctx": None, "dir_ctx": None},
        "lifecycle": {
            "stage": "new",
            "assessment": "Initial assessment pending",
            "confidence": 0.0,
            "assessed_at": None,
        },
        "tooling_policy": {
            "mode": "restricted",
            "disabled_features": ["scan", "context_profiles"],
            "notes": "Auto-restricted for new repos; update repo_state to enable.",
            "updated_at": now,
        },
        "created_at": now,
        "updated_at": now,
    }


def load_repo_state(repo_root: Path, branch_name: str, actor_id: str) -> RepoStateSnapshot:
    """
    Load a repo_state payload from SQLite.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier reserved for audit logging.

    Returns:
        RepoStateSnapshot: Snapshot containing payload and existence flag.

    Raises:
        FileNotFoundError: If user.db is missing.
        ValueError: If stored values violate repo_state expectations.
    """

    db_path = user_db_path(repo_root)
    try:
        record, exists = _read_repo_state_record(repo_root, branch_name, actor_id)
        return RepoStateSnapshot(payload=record, exists=exists)
    except sqlite_crud.SqliteCrudError as exc:
        if exc.code == "record_not_found":
            now = utc_now_iso()
            return RepoStateSnapshot(payload=default_repo_state(repo_root, now), exists=False)
        _raise_crud_error(
            exc,
            db_path,
            "Missing repo_state registry entries in user.db.",
        )


def write_repo_state(
    repo_root: Path,
    branch_name: str,
    payload: dict[str, Any],
    actor_id: str,
    *,
    exists: bool,
) -> None:
    """
    Persist a repo_state payload to SQLite.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        payload (dict[str, Any]): Repo state payload.
        actor_id (str): Actor identifier for audit logging.
        exists (bool): Whether the record already exists.

    Raises:
        FileNotFoundError: If user.db is missing.
        ValueError: If payload values violate repo_state expectations.

    Contract:
        - updated_at is refreshed at write time.
        - The tooling disabled feature list is replaced in full.
        - If exists disagrees with the database, the database state wins.
    """

    if not isinstance(payload, dict):
        raise ValueError("repo_state payload must be a JSON object.")
    db_path = user_db_path(repo_root)
    try:
        sqlite_query.execute_request(
            repo_root,
            sqlite_query.SqliteQueryRequest(
                scope="user",
                query_name=QUERY_WRITE_REPO_STATE,
                payload={
                    "branch_name": branch_name,
                    "repo_state": payload,
                    "exists": exists,
                },
                actor_id=actor_id,
            ),
        )
    except sqlite_query.SqliteQueryError as exc:
        _raise_query_error(
            exc,
            db_path,
            "Missing repo_state query registry entries in user.db.",
        )


def delete_repo_state(repo_root: Path, branch_name: str, actor_id: str) -> bool:
    """
    Delete repo_state rows for a branch in SQLite.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier reserved for audit logging.

    Returns:
        bool: True if the repo_state row existed and was removed.

    Raises:
        FileNotFoundError: If user.db is missing.
    """

    db_path = user_db_path(repo_root)
    try:
        response = sqlite_query.execute_request(
            repo_root,
            sqlite_query.SqliteQueryRequest(
                scope="user",
                query_name=QUERY_DELETE_REPO_STATE,
                payload={"branch_name": branch_name},
                actor_id=actor_id,
            ),
        )
    except sqlite_query.SqliteQueryError as exc:
        _raise_query_error(
            exc,
            db_path,
            "Missing repo_state query registry entries in user.db.",
        )
    result = response.output.get("result", {})
    deleted = result.get("deleted")
    if not isinstance(deleted, bool):
        raise ValueError("repo_state delete returned an invalid deleted flag.")
    return deleted


def _payload_from_rows(
    repo_root: Path,
    row: RepoState,
    disabled_rows: list[RepoStateToolingDisabledFeature],
) -> dict[str, Any]:
    """
    Build a repo_state payload from ORM rows.

    Args:
        repo_root (Path): Repository root.
        row (RepoState): RepoState ORM row.
        disabled_rows (list[RepoStateToolingDisabledFeature]): Disabled feature rows.

    Returns:
        dict[str, Any]: Repo state payload.
    """

    repo_root_value = row.repo_root or str(repo_root)
    disabled_features = [entry.feature_name for entry in disabled_rows]
    payload = {
        "schema_version": row.schema_version,
        "repo_id": row.repo_id,
        "repo_root": repo_root_value,
        "git": {"head": row.git_head},
        "scan_counter": row.scan_counter,
        "last_scan_id": row.last_scan_id,
        "last_scan_at": row.last_scan_at,
        "scanner_version": row.scanner_version,
        "template_versions": {
            "file_ctx": row.template_file_ctx_version,
            "dir_ctx": row.template_dir_ctx_version,
        },
        "lifecycle": {
            "stage": row.lifecycle_stage,
            "assessment": row.lifecycle_assessment,
            "confidence": row.lifecycle_confidence,
            "assessed_at": row.lifecycle_assessed_at,
        },
        "tooling_policy": {
            "mode": row.tooling_policy_mode,
            "disabled_features": disabled_features,
            "notes": row.tooling_policy_notes,
            "updated_at": row.tooling_policy_updated_at,
        },
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }
    payload.setdefault("schema_version", 1)
    payload.setdefault("repo_root", str(repo_root))
    payload.setdefault("updated_at", utc_now_iso())
    return payload


def _parse_repo_state_payload(
    payload: dict[str, Any],
    repo_root: Path,
    now: str,
    actor_id: str,
) -> dict[str, Any]:
    """
    Validate and normalize a repo_state payload into row fields.

    Args:
        payload (dict[str, Any]): Repo state payload.
        repo_root (Path): Repository root.
        now (str): Current timestamp.

    Returns:
        dict[str, Any]: Normalized repo_state fields.

    Raises:
        ValueError: If payload values are invalid.
    """

    schema_version = payload.get("schema_version", 1)
    schema_version = _require_int(schema_version, "repo_state.schema_version", minimum=1)

    repo_id = _optional_string(payload.get("repo_id"), "repo_state.repo_id")
    repo_root_value = _optional_string(payload.get("repo_root"), "repo_state.repo_root")
    if repo_root_value is None:
        repo_root_value = str(repo_root)

    git = _optional_mapping(payload.get("git"), "repo_state.git")
    git_head = _optional_string(git.get("head"), "repo_state.git.head")

    scan_counter = _require_int(payload.get("scan_counter"), "repo_state.scan_counter", minimum=0)
    last_scan_id = _optional_string(payload.get("last_scan_id"), "repo_state.last_scan_id")
    last_scan_at = _optional_string(payload.get("last_scan_at"), "repo_state.last_scan_at")
    scanner_version = _optional_string(payload.get("scanner_version"), "repo_state.scanner_version")

    template_versions = _optional_mapping(
        payload.get("template_versions"),
        "repo_state.template_versions",
    )
    template_file_ctx_version = _optional_string(
        template_versions.get("file_ctx"),
        "repo_state.template_versions.file_ctx",
    )
    template_dir_ctx_version = _optional_string(
        template_versions.get("dir_ctx"),
        "repo_state.template_versions.dir_ctx",
    )

    lifecycle = _optional_mapping(payload.get("lifecycle"), "repo_state.lifecycle")
    lifecycle_stage = _optional_enum(
        lifecycle.get("stage"),
        "repo_state.lifecycle.stage",
        LIFECYCLE_STAGES,
    )
    lifecycle_assessment = _optional_string(
        lifecycle.get("assessment"),
        "repo_state.lifecycle.assessment",
    )
    lifecycle_confidence = _optional_number(
        lifecycle.get("confidence"),
        "repo_state.lifecycle.confidence",
        minimum=0.0,
        maximum=1.0,
    )
    lifecycle_assessed_at = _optional_string(
        lifecycle.get("assessed_at"),
        "repo_state.lifecycle.assessed_at",
    )

    tooling_policy = _optional_mapping(
        payload.get("tooling_policy"),
        "repo_state.tooling_policy",
    )
    tooling_policy_mode = _optional_enum(
        tooling_policy.get("mode"),
        "repo_state.tooling_policy.mode",
        TOOLING_POLICY_MODES,
    )
    tooling_policy_notes = _optional_string(
        tooling_policy.get("notes"),
        "repo_state.tooling_policy.notes",
    )
    tooling_policy_updated_at = _optional_string(
        tooling_policy.get("updated_at"),
        "repo_state.tooling_policy.updated_at",
    )
    disabled_features = _optional_string_list(
        tooling_policy.get("disabled_features"),
        "repo_state.tooling_policy.disabled_features",
    )

    created_at = _optional_string(payload.get("created_at"), "repo_state.created_at") or now
    updated_at = now

    return {
        "schema_version": schema_version,
        "repo_id": repo_id,
        "repo_root": repo_root_value,
        "git_head": git_head,
        "scan_counter": scan_counter,
        "last_scan_id": last_scan_id,
        "last_scan_at": last_scan_at,
        "scanner_version": scanner_version,
        "template_file_ctx_version": template_file_ctx_version,
        "template_dir_ctx_version": template_dir_ctx_version,
        "lifecycle_stage": lifecycle_stage,
        "lifecycle_assessment": lifecycle_assessment,
        "lifecycle_confidence": lifecycle_confidence,
        "lifecycle_assessed_at": lifecycle_assessed_at,
        "tooling_policy_mode": tooling_policy_mode,
        "tooling_policy_notes": tooling_policy_notes,
        "tooling_policy_updated_at": tooling_policy_updated_at,
        "disabled_features": disabled_features,
        "created_at": created_at,
        "created_by": actor_id,
        "updated_at": updated_at,
        "updated_by": actor_id,
    }


def _optional_mapping(value: Any, label: str) -> dict[str, Any]:
    """
    Normalize an optional mapping value.

    Args:
        value (Any): Candidate mapping value.
        label (str): Field label for errors.

    Returns:
        dict[str, Any]: Mapping value or an empty dict.

    Raises:
        ValueError: If the value is not a mapping or null.
    """

    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object.")
    return value


def _optional_string(value: Any, label: str) -> str | None:
    """
    Normalize an optional string value.

    Args:
        value (Any): Candidate string value.
        label (str): Field label for errors.

    Returns:
        str | None: Normalized string or None.

    Raises:
        ValueError: If the value is not a string or null.
    """

    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a string or null.")
    return value


def _require_int(value: Any, label: str, *, minimum: int) -> int:
    """
    Require an integer value within a minimum bound.

    Args:
        value (Any): Candidate integer value.
        label (str): Field label for errors.
        minimum (int): Minimum allowed value.

    Returns:
        int: Normalized integer.

    Raises:
        ValueError: If the value is not an integer or below minimum.
    """

    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be an integer.")
    if value < minimum:
        raise ValueError(f"{label} must be >= {minimum}.")
    return value


def _optional_number(
    value: Any,
    label: str,
    *,
    minimum: float,
    maximum: float,
) -> float | None:
    """
    Normalize an optional numeric value within bounds.

    Args:
        value (Any): Candidate numeric value.
        label (str): Field label for errors.
        minimum (float): Minimum allowed value.
        maximum (float): Maximum allowed value.

    Returns:
        float | None: Normalized numeric value or None.

    Raises:
        ValueError: If the value is not a number or out of bounds.
    """

    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a number or null.")
    numeric = float(value)
    if numeric < minimum or numeric > maximum:
        raise ValueError(f"{label} must be between {minimum} and {maximum}.")
    return numeric


def _optional_enum(value: Any, label: str, allowed: tuple[str, ...]) -> str | None:
    """
    Normalize an optional enum value.

    Args:
        value (Any): Candidate enum value.
        label (str): Field label for errors.
        allowed (tuple[str, ...]): Allowed enum values.

    Returns:
        str | None: Normalized enum value or None.

    Raises:
        ValueError: If the value is not in the allowed set.
    """

    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a string or null.")
    if value not in allowed:
        allowed_csv = ", ".join(allowed)
        raise ValueError(f"{label} must be one of: {allowed_csv}.")
    return value


def _optional_string_list(value: Any, label: str) -> list[str]:
    """
    Normalize an optional list of strings.

    Args:
        value (Any): Candidate list value.
        label (str): Field label for errors.

    Returns:
        list[str]: List of string values (empty if None).

    Raises:
        ValueError: If the value is not a list of strings.
    """

    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list of strings.")
    normalized: list[str] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, str):
            raise ValueError(f"{label} must contain only strings.")
        if item in seen:
            raise ValueError(f"{label} must not contain duplicate values.")
        seen.add(item)
        normalized.append(item)
    return normalized
