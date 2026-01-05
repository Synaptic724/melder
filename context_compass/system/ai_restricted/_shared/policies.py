"""
Load policy configuration for context_compass from SQLite.
"""

from __future__ import annotations

from pathlib import Path

from context_compass.system.ai_restricted.database_management import sqlite_crud
from context_compass.system.ai_restricted.database_management.orm_session import system_db_path


CONFIG_POLICIES_TABLE = "config_policies_core"
CONFIG_POLICIES_ACTION = "by_config_id"
CONFIG_POLICIES_ID = 1
CONFIG_ACTOR_ID = "system:policies"


def default_policies() -> dict:
    """
    Return default policy values for context_compass behavior.

    Contract:
        - Returns a new dict on each call (no shared mutation).
        - Keys match the config_policies_* schema.

    Returns:
        dict: Default policy payload with all supported keys populated.
    """
    return {
        "architecture_context_faulty_ratio_threshold": 0.6,
        "architecture_context_good_ratio_threshold": 0.9,
        "architecture_context_stale_ratio_threshold": 0.75,
        "ci_fail_on_needs_review": False,
        "ci_fail_states": ["missing", "stale", "blocked"],
        "context_profiles_max_bytes_per_profile": 120000,
        "context_profiles_max_items_per_profile": 25,
        "context_profiles_optimize_score_threshold": 0.6,
        "context_profiles_popular_usage_threshold": 10,
        "context_profiles_prune_score_threshold": 0.3,
        "dir_review_every_n_scans_default": 20,
        "lease_heartbeat_seconds": 30,
        "lease_ttl_seconds": 300,
        "lock_wait_seconds": 10,
        "max_task_attempts": 3,
        "review_every_n_scans_default": 30,
        "schema_version": 1,
    }


def policies_path(repo_root: Path) -> Path:
    """
    Return the policies.json seed path.

    Args:
        repo_root (Path): Repository root.

    Returns:
        Path: policies.json location used for install-time seeding.

    Contract:
        - Path is derived deterministically from repo_root.
    """
    return (
        repo_root
        / "context_compass"
        / "system"
        / "config"
        / "policies.json"
    )


def _raise_crud_error(
    exc: sqlite_crud.SqliteCrudError,
    db_path: Path,
    message: str,
) -> None:
    """
    Raise a consistent error for CRUD lookup failures.

    Args:
        exc (sqlite_crud.SqliteCrudError): CRUD error to map.
        db_path (Path): System database path for error context.
        message (str): Message to use for missing record cases.

    Raises:
        FileNotFoundError: If system.db is missing.
        RuntimeError: If required tables or records are missing.
        sqlite_crud.SqliteCrudError: For unexpected CRUD failures.
    """

    if exc.code == "db_missing":
        raise FileNotFoundError(f"System database not found: {db_path}") from exc
    if exc.code in {
        "table_missing",
        "table_not_registered",
        "action_not_registered",
        "registry_missing",
    }:
        raise RuntimeError("Missing policy configuration tables in system.db.") from exc
    if exc.code == "record_not_found":
        raise RuntimeError(message) from exc
    raise exc


def _read_policy_record(repo_root: Path, actor_id: str) -> dict:
    """
    Read the policy configuration record from SQLite.

    Args:
        repo_root (Path): Repository root.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        dict: Policy configuration record.

    Raises:
        FileNotFoundError: If system.db is missing.
        RuntimeError: If required tables or the core record are missing.
        sqlite_crud.SqliteCrudError: For unexpected CRUD failures.
        ValueError: If the CRUD response payload is invalid.
    """

    db_path = system_db_path(repo_root)
    try:
        response = sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="read",
                scope="system",
                table_name=CONFIG_POLICIES_TABLE,
                action=CONFIG_POLICIES_ACTION,
                payload={"config_id": CONFIG_POLICIES_ID},
                actor_id=actor_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        _raise_crud_error(
            exc,
            db_path,
            "Missing config_policies_core row for config_id=1.",
        )
    record = response.output.get("result", {}).get("record")
    if not isinstance(record, dict):
        raise ValueError("config_policies_core read returned an invalid record payload.")
    return record


def _validate_policies(payload: dict) -> dict:
    """
    Validate and normalize a policy payload.

    Args:
        payload (dict): Policy payload to validate.

    Returns:
        dict: Validated policy payload.

    Raises:
        ValueError: If any required field is missing or invalid.

    Contract:
        - Unknown keys are ignored.
        - Defaults are applied for missing keys.
    """
    policies = default_policies()
    for key in policies:
        if key in payload:
            policies[key] = payload[key]

    schema_version = policies.get("schema_version")
    if not isinstance(schema_version, int) or schema_version < 1:
        raise ValueError("policies schema_version must be an integer >= 1.")

    ci_fail_states = policies.get("ci_fail_states")
    if not isinstance(ci_fail_states, list) or not all(
        isinstance(entry, str) for entry in ci_fail_states
    ):
        raise ValueError("policies ci_fail_states must be a list of strings.")

    def _require_number(name: str) -> float:
        value = policies.get(name)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"policies {name} must be a number.")
        return float(value)

    def _require_int(name: str) -> int:
        value = policies.get(name)
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"policies {name} must be an integer.")
        return value

    for key in (
        "review_every_n_scans_default",
        "dir_review_every_n_scans_default",
        "lock_wait_seconds",
        "max_task_attempts",
        "context_profiles_popular_usage_threshold",
    ):
        if _require_int(key) < 0:
            raise ValueError(f"policies {key} must be >= 0.")

    for key in (
        "lease_ttl_seconds",
        "lease_heartbeat_seconds",
        "context_profiles_max_bytes_per_profile",
        "context_profiles_max_items_per_profile",
    ):
        if _require_int(key) < 1:
            raise ValueError(f"policies {key} must be >= 1.")

    for key in (
        "context_profiles_prune_score_threshold",
        "context_profiles_optimize_score_threshold",
    ):
        if _require_number(key) < 0:
            raise ValueError(f"policies {key} must be >= 0.")

    for key in (
        "architecture_context_good_ratio_threshold",
        "architecture_context_stale_ratio_threshold",
        "architecture_context_faulty_ratio_threshold",
    ):
        value = _require_number(key)
        if value < 0 or value > 1:
            raise ValueError(f"policies {key} must be between 0 and 1.")

    ci_fail_on_needs_review = policies.get("ci_fail_on_needs_review")
    if not isinstance(ci_fail_on_needs_review, bool):
        raise ValueError("policies ci_fail_on_needs_review must be a boolean.")

    return policies


def load_policies(repo_root: Path) -> dict:
    """
    Load policy configuration from SQLite.

    Contract:
        - system.db must exist with policy tables.
        - config_id=1 must exist in config_policies_core.

    Args:
        repo_root (Path): Repository root.

    Returns:
        dict: Validated policy payload.

    Raises:
        FileNotFoundError: If system.db is missing.
        RuntimeError: If required policy tables or rows are missing.
        ValueError: If policy values are invalid.
    """

    record = _read_policy_record(repo_root, CONFIG_ACTOR_ID)
    return _validate_policies(record)
