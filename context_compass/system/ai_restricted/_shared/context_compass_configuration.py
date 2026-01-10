"""Load context_compass configuration for feature gating and skill overrides."""

from __future__ import annotations

from pathlib import Path

from context_compass.system.ai_restricted.database_management import sqlite_crud
from context_compass.system.ai_restricted.database_management.orm_session import system_db_path


CONFIG_CONTEXT_COMPASS_TABLE = "config_context_compass_core"
CONFIG_CONTEXT_COMPASS_FLAGS_TABLE = "config_context_compass_flags"
CONFIG_CONTEXT_COMPASS_SKILL_RULES_TABLE = "config_context_compass_skill_rules"
CONFIG_CONTEXT_COMPASS_ACTION = "by_config_id"
CONFIG_CONTEXT_COMPASS_ID = 1
CONFIG_ACTOR_ID = "system:context_compass_configuration"


def _default_features() -> dict:
    """
    Return default feature flags.

    Returns:
        dict: Feature flag defaults.
    """
    return {
        "scan": True,
        "context_profiles": True,
        "architecture_contexts": True,
        "environment_check": True,
        "repo_state": True,
        "memory": True,
        "command_registry": True,
        "work_management": True,
        "ticket_intake": True,
        "validation": True,
    }


def _default_skills() -> dict:
    """
    Return default skill override settings.

    Returns:
        dict: Skill override defaults.
    """
    return {"disabled_skill_ids": [], "disabled_skill_prefixes": []}


def default_configuration() -> dict:
    """
    Build a default configuration payload.

    Returns:
        dict: Default configuration payload.
    """
    return {
        "schema_version": 1,
        "features": _default_features(),
        "skills": _default_skills(),
        "work_mode": "soft",
        "notes": None,
    }


def _load_skill_rules(
    rules: list[dict], rule_type: str
) -> list[str]:
    """
    Extract ordered skill rule values for a rule type.

    Args:
        rules (list[dict]): Rule records from the database.
        rule_type (str): Rule type to extract ("id" or "prefix").

    Returns:
        list[str]: Ordered rule values.
    """

    filtered = [rule for rule in rules if rule.get("rule_type") == rule_type]
    filtered.sort(
        key=lambda rule: (
            rule.get("position") is None,
            rule.get("position") if rule.get("position") is not None else 0,
            rule.get("rule_value") or "",
        )
    )
    return [rule.get("rule_value") for rule in filtered if rule.get("rule_value")]


def _raise_crud_error(exc: sqlite_crud.SqliteCrudError, db_path: Path, message: str) -> None:
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
    if exc.code in {"table_missing", "table_not_registered", "action_not_registered", "registry_missing"}:
        raise RuntimeError("Missing configuration tables in system.db.") from exc
    if exc.code == "record_not_found":
        raise RuntimeError(message) from exc
    raise exc


def _read_core_config(repo_root: Path, actor_id: str) -> dict:
    """
    Read the core configuration record from SQLite.

    Args:
        repo_root (Path): Repository root.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        dict: Core configuration record.

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
                table_name=CONFIG_CONTEXT_COMPASS_TABLE,
                action=CONFIG_CONTEXT_COMPASS_ACTION,
                payload={"config_id": CONFIG_CONTEXT_COMPASS_ID},
                actor_id=actor_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        _raise_crud_error(
            exc,
            db_path,
            "Missing config_context_compass_core row for config_id=1.",
        )
    record = response.output.get("result", {}).get("record")
    if not isinstance(record, dict):
        raise ValueError("config_context_compass_core read returned an invalid record payload.")
    return record


def _read_flag_records(repo_root: Path, actor_id: str) -> list[dict]:
    """
    Read feature flag records from SQLite.

    Args:
        repo_root (Path): Repository root.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        list[dict]: Feature flag records.

    Raises:
        FileNotFoundError: If system.db is missing.
        RuntimeError: If required tables are missing.
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
                table_name=CONFIG_CONTEXT_COMPASS_FLAGS_TABLE,
                action=CONFIG_CONTEXT_COMPASS_ACTION,
                payload={"config_id": CONFIG_CONTEXT_COMPASS_ID},
                actor_id=actor_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        _raise_crud_error(
            exc,
            db_path,
            "Missing config_context_compass_flags rows for config_id=1.",
        )
    records = response.output.get("result", {}).get("records")
    if not isinstance(records, list):
        raise ValueError("config_context_compass_flags read returned an invalid record payload.")
    return [record for record in records if isinstance(record, dict)]


def _read_skill_rule_records(repo_root: Path, actor_id: str) -> list[dict]:
    """
    Read skill rule records from SQLite.

    Args:
        repo_root (Path): Repository root.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        list[dict]: Skill rule records.

    Raises:
        FileNotFoundError: If system.db is missing.
        RuntimeError: If required tables are missing.
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
                table_name=CONFIG_CONTEXT_COMPASS_SKILL_RULES_TABLE,
                action=CONFIG_CONTEXT_COMPASS_ACTION,
                payload={"config_id": CONFIG_CONTEXT_COMPASS_ID},
                actor_id=actor_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        _raise_crud_error(
            exc,
            db_path,
            "Missing config_context_compass_skill_rules rows for config_id=1.",
        )
    records = response.output.get("result", {}).get("records")
    if not isinstance(records, list):
        raise ValueError("config_context_compass_skill_rules read returned an invalid record payload.")
    return [record for record in records if isinstance(record, dict)]


def load_configuration(repo_root: Path) -> dict:
    """
    Load context_compass configuration from SQLite with defaults applied.

    Contract:
    - system.db must exist and contain the config tables.
    - config_id=1 must exist in config_context_compass_core.

    Args:
        repo_root (Path): Repository root.

    Returns:
        dict: Configuration payload.

    Raises:
        FileNotFoundError: If the system database is missing.
        RuntimeError: If required tables or config rows are missing.
        ValueError: If configuration values are invalid.
    """

    actor_id = CONFIG_ACTOR_ID
    core = _read_core_config(repo_root, actor_id)
    flags = _read_flag_records(repo_root, actor_id)
    rules = _read_skill_rule_records(repo_root, actor_id)

    schema_version = core.get("schema_version")
    work_mode = core.get("work_mode")
    notes = core.get("notes")
    if not isinstance(schema_version, int):
        raise ValueError("config_context_compass_core.schema_version must be an integer.")
    if not isinstance(work_mode, str):
        raise ValueError("config_context_compass_core.work_mode must be a string.")
    if work_mode not in ("hard", "soft"):
        raise ValueError("config_context_compass_core.work_mode must be 'hard' or 'soft'.")
    if notes is not None and not isinstance(notes, str):
        raise ValueError("config_context_compass_core.notes must be a string or null.")

    config = default_configuration()
    config["schema_version"] = schema_version
    config["work_mode"] = work_mode
    config["notes"] = notes

    features = _default_features()
    for flag in flags:
        name = flag.get("feature_name")
        enabled = flag.get("enabled")
        if not isinstance(name, str):
            raise ValueError("config_context_compass_flags.feature_name must be a string.")
        features[name] = bool(enabled)
    config["features"] = features

    config["skills"] = {
        "disabled_skill_ids": _load_skill_rules(rules, "id"),
        "disabled_skill_prefixes": _load_skill_rules(rules, "prefix"),
    }
    return config
