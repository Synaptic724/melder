"""
Generate command registries for context_compass tools.

Purpose
- Produce a machine-readable command registry for system/user audiences.
- Persist registry rows into SQLite command registry tables.
- Return registry payloads to the caller for inspection or logging.

Contract
- Registry payloads are generated deterministically from the command catalog.
- Writes to SQLite command_registry_system and command_registry_user tables.
- Registry payloads are not exported to JSON files by this command.
"""

import argparse
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_string,
    require_string,
)
from context_compass.system.ai_restricted._shared.command_results import (
    exception_result,
    ok_result,
    payload_error_result,
)
from context_compass.system.ai_restricted._shared.certification_guard import ensure_certified
from context_compass.system.ai_restricted._shared.feature_guard import ensure_feature_enabled
from context_compass.system.ai_restricted._shared.timeutils import utc_now_iso
from context_compass.system.ai_restricted._shared.work_mode_guard import ensure_work_mode
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)
from context_compass.system.ai_restricted.database_management import sqlite_crud
from sqlalchemy import inspect


COMMAND_TABLE_COLUMNS = (
    "command_name",
    "category",
    "entry",
    "summary",
    "requires_certification",
    "requires_work_id",
    "feature_flag",
    "notes",
    "spec_json",
    "registry_schema_version",
    "registry_generated_at",
    "registry_updated_at",
)
COMMAND_TABLES = (
    ("system", "command_registry_system"),
    ("user", "command_registry_user"),
)
COMMAND_REGISTRY_TABLE_BY_SCOPE = {
    "system": "command_registry_system",
    "user": "command_registry_user",
}
COMMAND_REGISTRY_CREATE_ACTION = "register_command"
COMMAND_REGISTRY_UPDATE_ACTION = "by_command_name"


@dataclass(frozen=True)
class RegistryMetadata:
    """
    Registry-level metadata for command registry rows.

    Attributes:
        schema_version (int): Registry schema version number.
        generated_at (str | None): Registry generation timestamp.
        updated_at (str | None): Registry update timestamp.

    Contract:
        - schema_version is a positive integer.
        - Timestamp fields are ISO-8601 strings or None.
    """

    schema_version: int
    generated_at: str | None
    updated_at: str | None


def _registry_db_path(repo_root: Path, scope: str) -> Path:
    """
    Resolve the SQLite database path for a registry scope.

    Args:
        repo_root (Path): Repository root directory.
        scope (str): Registry scope ("system" or "user").

    Returns:
        Path: SQLite database path.

    Raises:
        ValueError: If the scope is unsupported.
    """

    if scope not in ("system", "user"):
        raise ValueError(f"Unsupported command registry scope: {scope}")
    return (
        repo_root
        / "context_compass"
        / "system"
        / "storage"
        / "sqlite"
        / f"{scope}.db"
    )


def _require_registry_db(db_path: Path) -> None:
    """
    Ensure the registry database exists before writing.

    Args:
        db_path (Path): SQLite database path.

    Raises:
        FileNotFoundError: If the database file does not exist.
    """

    if not db_path.exists():
        raise FileNotFoundError(f"Command registry database not found: {db_path}")


def _ensure_table_exists(engine, table_name: str) -> None:
    """
    Ensure the named table exists in the SQLite database.

    Args:
        engine: SQLAlchemy engine bound to the registry database.
        table_name (str): Table name that must exist.

    Raises:
        RuntimeError: If the table is missing.
    """

    inspector = inspect(engine)
    if not inspector.has_table(table_name):
        raise RuntimeError(f"Missing SQLite table: {table_name}")


def _extract_registry_metadata(payload: dict, label: str) -> RegistryMetadata:
    """
    Extract registry metadata from a registry payload.

    Args:
        payload (dict): Registry payload.
        label (str): Label for error context.

    Returns:
        RegistryMetadata: Parsed registry metadata.

    Raises:
        ValueError: If required metadata fields are missing or invalid.
    """

    schema_version = payload.get("schema_version")
    if not isinstance(schema_version, int):
        raise ValueError(f"Registry schema_version must be an integer: {label}")
    generated_at = payload.get("generated_at")
    if generated_at is not None and not isinstance(generated_at, str):
        raise ValueError(f"Registry generated_at must be a string or null: {label}")
    updated_at = payload.get("updated_at")
    if updated_at is not None and not isinstance(updated_at, str):
        raise ValueError(f"Registry updated_at must be a string or null: {label}")
    return RegistryMetadata(
        schema_version=schema_version,
        generated_at=generated_at,
        updated_at=updated_at,
    )


def _extract_command_entries(payload: dict, label: str) -> list[dict]:
    """
    Extract command entries from a registry payload.

    Args:
        payload (dict): Registry payload.
        label (str): Label for error context.

    Returns:
        list[dict]: Command entry dictionaries.

    Raises:
        ValueError: If commands are missing or invalid.
    """

    commands = payload.get("commands")
    if not isinstance(commands, list):
        raise ValueError(f"Registry commands must be a list: {label}")
    for entry in commands:
        if not isinstance(entry, dict):
            raise ValueError(f"Registry commands must contain objects: {label}")
    return commands


def _require_string(command: dict, field: str, label: str) -> str:
    """
    Require a non-empty string field from a command entry.

    Args:
        command (dict): Command entry dictionary.
        field (str): Field name to extract.
        label (str): Registry label for error context.

    Returns:
        str: Extracted string value.

    Raises:
        ValueError: If the field is missing or invalid.
    """

    value = command.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Command '{field}' must be a non-empty string: {label}")
    return value


def _require_bool(command: dict, field: str, label: str) -> bool:
    """
    Require a boolean field from a command entry.

    Args:
        command (dict): Command entry dictionary.
        field (str): Field name to extract.
        label (str): Registry label for error context.

    Returns:
        bool: Extracted boolean value.

    Raises:
        ValueError: If the field is missing or invalid.
    """

    value = command.get(field)
    if not isinstance(value, bool):
        raise ValueError(f"Command '{field}' must be a boolean: {label}")
    return value


def _optional_string(command: dict, field: str, label: str) -> str | None:
    """
    Extract an optional string field from a command entry.

    Args:
        command (dict): Command entry dictionary.
        field (str): Field name to extract.
        label (str): Registry label for error context.

    Returns:
        str | None: String value or None if absent.

    Raises:
        ValueError: If the field exists but is not a string or null.
    """

    value = command.get(field)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"Command '{field}' must be a string or null: {label}")
    return value


def _serialize_spec(command: dict, label: str) -> str | None:
    """
    Serialize the optional spec field for SQLite storage.

    Args:
        command (dict): Command entry dictionary.
        label (str): Registry label for error context.

    Returns:
        str | None: Minified JSON spec payload or None.

    Raises:
        ValueError: If spec is present but not a JSON object.
    """

    spec = command.get("spec")
    if spec is None:
        return None
    if not isinstance(spec, dict):
        raise ValueError(f"Command spec must be an object or null: {label}")
    return json.dumps(spec, separators=(",", ":"))


def _command_row(command: dict, metadata: RegistryMetadata, label: str) -> tuple:
    """
    Build a SQLite row tuple for a command registry entry.

    Args:
        command (dict): Command entry dictionary.
        metadata (RegistryMetadata): Registry metadata.
        label (str): Registry label for error context.

    Returns:
        tuple: Ordered row matching COMMAND_TABLE_COLUMNS.
    """

    return (
        _require_string(command, "name", label),
        _require_string(command, "category", label),
        _require_string(command, "entry", label),
        _require_string(command, "summary", label),
        1 if _require_bool(command, "requires_certification", label) else 0,
        1 if _require_bool(command, "requires_work_id", label) else 0,
        _optional_string(command, "feature_flag", label),
        _optional_string(command, "notes", label),
        _serialize_spec(command, label),
        metadata.schema_version,
        metadata.generated_at,
        metadata.updated_at,
    )


def _command_payload(command: dict, metadata: RegistryMetadata, label: str) -> dict:
    """
    Build a CRUD payload for a command registry entry.

    Args:
        command (dict): Command entry dictionary.
        metadata (RegistryMetadata): Registry metadata.
        label (str): Registry label for error context.

    Returns:
        dict: CRUD payload matching command registry columns.
    """

    row = _command_row(command, metadata, label)
    values = dict(zip(COMMAND_TABLE_COLUMNS, row))
    command_name = values["command_name"]
    return {
        "record_id": command_name,
        "command_name": command_name,
        "category": values["category"],
        "entry": values["entry"],
        "summary": values["summary"],
        "requires_certification": bool(values["requires_certification"]),
        "requires_work_id": bool(values["requires_work_id"]),
        "feature_flag": values["feature_flag"],
        "notes": values["notes"],
        "spec_json": values["spec_json"],
        "registry_schema_version": values["registry_schema_version"],
        "registry_generated_at": values["registry_generated_at"],
        "registry_updated_at": values["registry_updated_at"],
    }


def _registry_table_name(scope: str) -> str:
    """
    Resolve the command registry table name for a scope.

    Args:
        scope (str): Registry scope ("system" or "user").

    Returns:
        str: Command registry table name.

    Raises:
        ValueError: If scope is unsupported.
    """

    table_name = COMMAND_REGISTRY_TABLE_BY_SCOPE.get(scope)
    if table_name is None:
        raise ValueError(f"Unsupported command registry scope: {scope}")
    return table_name


def _upsert_command_entry(
    *,
    repo_root: Path,
    scope: str,
    payload: dict,
    actor_id: str,
    label: str,
) -> None:
    """
    Upsert a command registry entry via the CRUD API.

    Args:
        repo_root (Path): Repository root.
        scope (str): Registry scope ("system" or "user").
        payload (dict): Command registry payload for create/update.
        actor_id (str): Actor identifier for audit logging.
        label (str): Registry label for error context.

    Raises:
        FileNotFoundError: If the registry database is missing.
        sqlite_crud.SqliteCrudError: For unexpected CRUD failures.
    """

    table_name = _registry_table_name(scope)
    try:
        sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="update",
                scope=scope,
                table_name=table_name,
                action=COMMAND_REGISTRY_UPDATE_ACTION,
                payload=payload,
                actor_id=actor_id,
            ),
        )
        return
    except sqlite_crud.SqliteCrudError as exc:
        if exc.code == "record_not_found":
            pass
        elif exc.code == "db_missing":
            raise FileNotFoundError(
                f"Command registry database not found for scope: {label}"
            ) from exc
        else:
            raise

    try:
        sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="create",
                scope=scope,
                table_name=table_name,
                action=COMMAND_REGISTRY_CREATE_ACTION,
                payload=payload,
                actor_id=actor_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        if exc.code == "record_exists":
            sqlite_crud.execute_request(
                repo_root,
                sqlite_crud.SqliteCrudRequest(
                    operation="update",
                    scope=scope,
                    table_name=table_name,
                    action=COMMAND_REGISTRY_UPDATE_ACTION,
                    payload=payload,
                    actor_id=actor_id,
                ),
            )
            return
        if exc.code == "db_missing":
            raise FileNotFoundError(
                f"Command registry database not found for scope: {label}"
            ) from exc
        raise


def _build_upsert_sql(table_name: str) -> str:
    """
    Build the upsert SQL statement for command registry rows.

    Args:
        table_name (str): Command registry table name.

    Returns:
        str: Parameterized upsert SQL statement.
    """

    columns = ", ".join(COMMAND_TABLE_COLUMNS)
    placeholders = ", ".join("?" for _ in COMMAND_TABLE_COLUMNS)
    update_cols = [
        f"{column}=excluded.{column}"
        for column in COMMAND_TABLE_COLUMNS
        if column != "command_name"
    ]
    update_clause = ", ".join(update_cols)
    return (
        f"INSERT INTO \"{table_name}\" ({columns}) "
        f"VALUES ({placeholders}) "
        "ON CONFLICT(command_name) DO UPDATE SET "
        f"{update_clause}"
    )


def _upsert_registry_table(
    *,
    repo_root: Path,
    scope: str,
    payload: dict,
    label: str,
    actor_id: str,
) -> None:
    """
    Insert or update registry rows into a command registry table.

    Args:
        repo_root (Path): Repository root.
        scope (str): Registry scope ("system" or "user").
        payload (dict): Registry payload to persist.
        label (str): Registry label for error context.
        actor_id (str): Actor identifier for audit logging.

    Raises:
        FileNotFoundError: If the registry database is missing.
        ValueError: If the payload is missing required fields.
        sqlite_crud.SqliteCrudError: For unexpected CRUD failures.
    """

    metadata = _extract_registry_metadata(payload, label)
    commands = _extract_command_entries(payload, label)
    for command in commands:
        entry_payload = _command_payload(command, metadata, label)
        _upsert_command_entry(
            repo_root=repo_root,
            scope=scope,
            payload=entry_payload,
            actor_id=actor_id,
            label=label,
        )




def _script_entry(script_path: str, cli_args: str) -> str:
    """
    Build a path-based CLI entry string for a command script.

    Args:
        script_path (str): Script path relative to context_compass/system.
        cli_args (str): CLI arguments to append after the script path.

    Returns:
        str: Full CLI entry string for the command.

    Contract:
        - Uses a path-based entry rooted at context_compass/system.
        - CLI arguments are preserved verbatim.
    """

    suffix = cli_args.strip()
    entry = f"python context_compass/system/{script_path}".strip()
    return f"{entry} {suffix}".strip()


def _execution_spec(script_path: str) -> dict:
    """
    Build a deterministic execution spec for a command script.

    Args:
        script_path (str): Script path relative to context_compass/system.

    Returns:
        dict: Execution spec payload for the command registry.

    Contract:
        - Commands execute via the run() entrypoint.
        - Payloads are JSON kwargs in and kwargs out.
    """

    return {
        "execution": {
            "script_path": script_path,
            "entrypoint": "run",
            "kwargs_in": True,
            "kwargs_out": True,
        }
    }


def _commands_catalog() -> list[dict]:
    """
    Return the canonical command catalog.

    Returns:
        list[dict]: Command definitions with audience tags and execution specs.

    Contract:
        - Each command includes a path-based entry string.
        - Each command includes a spec.execution block for the runner.
    """

    commands = [
        {
            "name": "python_certified",
            "script_path": "ai_restricted/agent_management/python_certified.py",
            "cli_args": "--repo-root . --agent-id <agent_id> --approval-token \"CERTIFY: APPROVED\"",
            "summary": "Finalize certification state after approval.",
            "category": "certification",
            "requires_certification": False,
            "requires_work_id": False,
            "feature_flag": None,
            "notes": "Run only after receiving CERTIFY: APPROVED.",
            "audience": ["user", "system"],
        },
        {
            "name": "agent_id",
            "script_path": "ai_restricted/agent_management/agent_id.py",
            "cli_args": "--prefix agent",
            "summary": "Generate a session-scoped agent id.",
            "category": "lifecycle",
            "requires_certification": False,
            "requires_work_id": False,
            "feature_flag": None,
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "agent_manage",
            "script_path": "ai_restricted/agent_management/agent_manage.py",
            "cli_args": "<create|archive|delete> --repo-root . --agent-id <agent_id> --agent-role <role>",
            "summary": "Create, archive, or delete agent files.",
            "category": "lifecycle",
            "requires_certification": True,
            "requires_work_id": False,
            "feature_flag": None,
            "notes": "Add --owner-id to record the actor managing another agent.",
            "audience": ["user", "system"],
        },
        {
            "name": "agent_checkin",
            "script_path": "ai_restricted/agent_management/agent_checkin.py",
            "cli_args": "--repo-root . --agent-id <agent_id> --agent-role <role> --agent-kind <kind> --model-name <model> --runtime <runtime>",
            "summary": "Check in an agent and mark the profile active.",
            "category": "lifecycle",
            "requires_certification": True,
            "requires_work_id": False,
            "feature_flag": None,
            "notes": "Metadata fields are optional but recommended.",
            "audience": ["user", "system"],
        },
        {
            "name": "agent_checkout",
            "script_path": "ai_restricted/agent_management/agent_checkout.py",
            "cli_args": "--repo-root . --agent-id <agent_id> --agent-role <role>",
            "summary": "Check out an agent and mark the profile inactive.",
            "category": "lifecycle",
            "requires_certification": True,
            "requires_work_id": False,
            "feature_flag": None,
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "branch_init",
            "script_path": "ai_restricted/system_management/branch_init.py",
            "cli_args": "--repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>",
            "summary": "Initialize branch-scoped state and queues.",
            "category": "branch",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": None,
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "branch_switch",
            "script_path": "ai_restricted/system_management/branch_switch.py",
            "cli_args": "--repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>",
            "summary": "Switch the active branch pointer.",
            "category": "branch",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": None,
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "branch_clone",
            "script_path": "ai_restricted/system_management/branch_clone.py",
            "cli_args": "--repo-root . --source-branch <branch> --dest-branch <branch> --agent-id <agent_id> --work-id <work_id>",
            "summary": "Clone branch state and work queues into a new branch.",
            "category": "branch",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": None,
            "notes": "Use --activate to switch to the new branch.",
            "audience": ["user", "system"],
        },
        {
            "name": "branch_copy_context",
            "script_path": "ai_restricted/system_management/branch_copy_context.py",
            "cli_args": "--repo-root . --source-branch <branch> --dest-branch <branch> --agent-id <agent_id> --work-id <work_id>",
            "summary": "Copy branch context records into another branch.",
            "category": "branch",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": None,
            "notes": "Use --preserve-repo-state to keep scan counters.",
            "audience": ["user", "system"],
        },
        {
            "name": "branch_copy_work",
            "script_path": "ai_restricted/system_management/branch_copy_work.py",
            "cli_args": "--repo-root . --source-branch <branch> --dest-branch <branch> --agent-id <agent_id> --work-id <work_id>",
            "summary": "Copy branch work queues into another branch.",
            "category": "branch",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": None,
            "notes": "Use --preserve-state to keep in_progress or leased states.",
            "audience": ["user", "system"],
        },
        {
            "name": "branch_delete_context",
            "script_path": "ai_restricted/system_management/branch_delete_context.py",
            "cli_args": "--repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>",
            "summary": "Delete context records for a branch.",
            "category": "branch",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": None,
            "notes": "Use --include-repo-state to remove the repo_state record too.",
            "audience": ["user", "system"],
        },
        {
            "name": "branch_delete_work",
            "script_path": "ai_restricted/system_management/branch_delete_work.py",
            "cli_args": "--repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>",
            "summary": "Clear branch work queues.",
            "category": "branch",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": None,
            "notes": "Resets epics/stories/tasks queues to empty.",
            "audience": ["user", "system"],
        },
        {
            "name": "branch_delete",
            "script_path": "ai_restricted/system_management/branch_delete.py",
            "cli_args": "--repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>",
            "summary": "Hard-delete a branch (drop SQLite tables and remove registry records).",
            "category": "branch",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": None,
            "notes": "Drops branch-scoped SQLite tables and removes the branch registry entry.",
            "audience": ["user", "system"],
        },
        {
            "name": "repo_state_assess",
            "script_path": "ai_restricted/system_management/repo_state_assess.py",
            "cli_args": "--repo-root . --agent-id <agent_id> --work-id <work_id> --stage <stage>",
            "summary": "Assess repo lifecycle stage and tooling policy.",
            "category": "repo_state",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "repo_state",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "environment_check",
            "script_path": "ai_restricted/system_management/environment_check.py",
            "cli_args": "--repo-root . --agent-id <agent_id> --work-id <work_id>",
            "summary": "Collect OS/runtime/tool availability and optionally persist.",
            "category": "environment",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "environment_check",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "onboarding_bundle",
            "script_path": "ai_restricted/agent_management/onboarding_bundle.py",
            "cli_args": "--repo-root . --format markdown",
            "summary": "Generate a consolidated onboarding bundle of docs.",
            "category": "onboarding",
            "requires_certification": False,
            "requires_work_id": False,
            "feature_flag": None,
            "notes": "Allowed before certification.",
            "audience": ["user", "system"],
        },
        {
            "name": "agent_onboarding_start",
            "script_path": "ai_restricted/agent_management/agent_onboarding_start.py",
            "cli_args": "--repo-root . --agent-id <agent_id> [--agent-role <career>]",
            "summary": "Select a career and create the agent profile.",
            "category": "onboarding",
            "requires_certification": True,
            "requires_work_id": False,
            "feature_flag": None,
            "notes": "Defaults to developer when no career is provided.",
            "audience": ["user", "system"],
        },
        {
            "name": "onboarding_bundle_restore",
            "script_path": "ai_restricted/agent_management/onboarding_bundle_restore.py",
            "cli_args": (
                "--repo-root . --bundle-id <bundle_id> "
                "--path <path> [--path <path>] "
                "--target-root <path> --allow-overwrite"
            ),
            "summary": "Restore selected onboarding docs from a bundle snapshot.",
            "category": "onboarding",
            "requires_certification": False,
            "requires_work_id": False,
            "feature_flag": None,
            "notes": "Requires explicit paths; refuses overwrite unless allowed.",
            "audience": ["user", "system"],
        },
        {
            "name": "scan",
            "script_path": "ai_restricted/system_management/scan.py",
            "cli_args": "--repo-root . --agent-id <agent_id> --work-id <work_id>",
            "summary": "Scan repo for ctx freshness and emit tasks.",
            "category": "scan",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "scan",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "context_profiles_survey",
            "script_path": "ai_restricted/context_management/context_profiles_survey.py",
            "cli_args": "--repo-root . --agent-id <agent_id> --work-id <work_id>",
            "summary": "Survey and build context profiles from ctx JSON.",
            "category": "context_profiles",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "context_profiles",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "context_profiles_read",
            "script_path": "ai_restricted/context_management/context_profiles_read.py",
            "cli_args": "--repo-root . --agent-id <agent_id> --work-id <work_id> --profile <name>",
            "summary": "Read a named context profile and emit ctx bundle.",
            "category": "context_profiles",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "context_profiles",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "context_profiles_review",
            "script_path": "ai_restricted/context_management/context_profiles_review.py",
            "cli_args": "--repo-root . --agent-id <agent_id> --work-id <work_id> --profile <name> --grade <grade>",
            "summary": "Record a profile review and emit optimize/prune tasks.",
            "category": "context_profiles",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "context_profiles",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "context_profiles_resurvey",
            "script_path": "ai_restricted/context_management/context_profiles_resurvey.py",
            "cli_args": "--repo-root . --agent-id <agent_id> --work-id <work_id>",
            "summary": "Process resurvey_context_profile tasks.",
            "category": "context_profiles",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "context_profiles",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "context_architecture_survey",
            "script_path": "ai_restricted/context_management/context_architecture_survey.py",
            "cli_args": "--repo-root . --agent-id <agent_id> --work-id <work_id> --target <prod|test>",
            "summary": "Build architecture_context record from directory ctx.",
            "category": "architecture",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "architecture_contexts",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "context_architecture_check",
            "script_path": "ai_restricted/context_management/context_architecture_check.py",
            "cli_args": "--repo-root . --agent-id <agent_id> --work-id <work_id> --target <prod|test>",
            "summary": "Check architecture context freshness.",
            "category": "architecture",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "architecture_contexts",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "context_architecture_resurvey",
            "script_path": "ai_restricted/context_management/context_architecture_resurvey.py",
            "cli_args": "--repo-root . --agent-id <agent_id> --work-id <work_id> --target <prod|test>",
            "summary": "Process resurvey_architecture_context tasks.",
            "category": "architecture",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "architecture_contexts",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "context_component_survey",
            "script_path": "ai_restricted/context_management/context_component_survey.py",
            "cli_args": "--repo-root . --agent-id <agent_id> --work-id <work_id> --target <prod|test>",
            "summary": "Build component_contexts record from directory ctx.",
            "category": "architecture",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "architecture_contexts",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "context_component_check",
            "script_path": "ai_restricted/context_management/context_component_check.py",
            "cli_args": "--repo-root . --agent-id <agent_id> --work-id <work_id> --target <prod|test>",
            "summary": "Check component context freshness.",
            "category": "architecture",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "architecture_contexts",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "context_component_resurvey",
            "script_path": "ai_restricted/context_management/context_component_resurvey.py",
            "cli_args": "--repo-root . --agent-id <agent_id> --work-id <work_id> --target <prod|test>",
            "summary": "Process resurvey_component_contexts tasks.",
            "category": "architecture",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "architecture_contexts",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "work_item_add",
            "script_path": "ai_restricted/work_management/work_item_add.py",
            "cli_args": "--repo-root . --bucket <bucket> --kind <kind>",
            "summary": "Add a work item to global work queues.",
            "category": "work_management",
            "requires_certification": True,
            "requires_work_id": False,
            "feature_flag": "work_management",
            "notes": "work_id is auto-generated when omitted.",
            "audience": ["user", "system"],
        },
        {
            "name": "work_item_move",
            "script_path": "ai_restricted/work_management/work_item_move.py",
            "cli_args": "--repo-root . --work-id <work_id> --src-bucket <bucket> --dest-bucket <bucket>",
            "summary": "Move a work item between global buckets.",
            "category": "work_management",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "work_management",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "work_item_bulk_move",
            "script_path": "ai_restricted/work_management/work_item_bulk_move.py",
            "cli_args": (
                "--repo-root . --agent-id <agent_id> --source-bucket <bucket> --dest-bucket <bucket> "
                "--work-type <epic|story|task> --work-ids <work_id> [<work_id> ...] --work-id <work_id>"
            ),
            "summary": "Move multiple work items between buckets.",
            "category": "work_management",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "work_management",
            "notes": "Provide --work-ids or --quantity to select items.",
            "audience": ["user", "system"],
        },
        {
            "name": "work_item_close",
            "script_path": "ai_restricted/work_management/work_item_close.py",
            "cli_args": "--repo-root . --work-id <work_id> --kind <kind>",
            "summary": "Close a work item and move it to completed.",
            "category": "work_management",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "work_management",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "work_queue_add",
            "script_path": "ai_restricted/work_management/work_queue_add.py",
            "cli_args": "--repo-root . --agent-id <agent_id>",
            "summary": "Add a work item to a per-agent queue.",
            "category": "work_management",
            "requires_certification": True,
            "requires_work_id": False,
            "feature_flag": "work_management",
            "notes": "work_id is auto-generated when omitted.",
            "audience": ["user", "system"],
        },
        {
            "name": "work_item_global_to_branch",
            "script_path": "ai_restricted/work_management/work_item_global_to_branch.py",
            "cli_args": "--repo-root . --work-id <work_id>",
            "summary": "Move a global work item into branch queues.",
            "category": "work_management",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "work_management",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "work_item_branch_to_global",
            "script_path": "ai_restricted/work_management/work_item_branch_to_global.py",
            "cli_args": "--repo-root . --work-id <work_id>",
            "summary": "Move a branch work item into global queues.",
            "category": "work_management",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "work_management",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "work_item_agent_to_branch",
            "script_path": "ai_restricted/work_management/work_item_agent_to_branch.py",
            "cli_args": "--repo-root . --agent-id <agent_id> --work-id <work_id>",
            "summary": "Move a per-agent work item into branch queues.",
            "category": "work_management",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "work_management",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "work_item_agent_to_global",
            "script_path": "ai_restricted/work_management/work_item_agent_to_global.py",
            "cli_args": "--repo-root . --agent-id <agent_id> --work-id <work_id>",
            "summary": "Move a per-agent work item into global queues.",
            "category": "work_management",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "work_management",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "ticket_promote",
            "script_path": "ai_restricted/work_management/ticket_promote.py",
            "cli_args": "--repo-root . --agent-id <agent_id> --ticket-path <path> [--child-items-json <json>]",
            "summary": "Promote a GitHub ticket markdown into work queues.",
            "category": "work_management",
            "requires_certification": True,
            "requires_work_id": False,
            "feature_flag": "ticket_intake",
            "notes": "work_id is auto-generated when omitted.",
            "audience": ["user", "system"],
        },
        {
            "name": "validate",
            "script_path": "ai_restricted/system_management/validate.py",
            "cli_args": "--repo-root . --agent-id <agent_id> --work-id <work_id>",
            "summary": "Validate schemas and required artifacts.",
            "category": "validation",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "validation",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "memory_add",
            "script_path": "ai_restricted/memory/memory_add.py",
            "cli_args": "--repo-root . --agent-id <agent_id> --work-id <work_id> --store <user|system> --title <title> --content <content>",
            "summary": "Add a memory entry to user or system store.",
            "category": "memory",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "memory",
            "notes": "User memory requires explicit user request.",
            "audience": ["user", "system"],
        },
        {
            "name": "memory_update",
            "script_path": "ai_restricted/memory/memory_update.py",
            "cli_args": "--repo-root . --agent-id <agent_id> --work-id <work_id> --store <user|system> --memory-id <id>",
            "summary": "Update a memory entry.",
            "category": "memory",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "memory",
            "notes": None,
            "audience": ["user", "system"],
        },
        {
            "name": "memory_remove",
            "script_path": "ai_restricted/memory/memory_remove.py",
            "cli_args": "--repo-root . --agent-id <agent_id> --work-id <work_id> --store <user|system> --memory-id <id>",
            "summary": "Remove a memory entry.",
            "category": "memory",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "memory",
            "notes": "Removes entries entirely (no soft delete).",
            "audience": ["user", "system"],
        },
        {
            "name": "memory_read",
            "script_path": "ai_restricted/memory/memory_read.py",
            "cli_args": "--repo-root . --agent-id <agent_id> --work-id <work_id> --store <user|system>",
            "summary": "Read memory entries.",
            "category": "memory",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "memory",
            "notes": "Use --recent to limit output.",
            "audience": ["user", "system"],
        },
        {
            "name": "command_registry_validator",
            "script_path": "ai_restricted/system_management/command_registry_validator.py",
            "cli_args": "--repo-root . --agent-id <agent_id> --work-id <work_id>",
            "summary": "Validate command registry tables in SQLite.",
            "category": "commands",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "command_registry",
            "notes": "Use --system-db/--user-db to override default db paths.",
            "audience": ["system"],
        },
        {
            "name": "command_registry_generate",
            "script_path": "ai_restricted/system_management/command_registry_generate.py",
            "cli_args": "--repo-root . --agent-id <agent_id> --work-id <work_id>",
            "summary": "Generate command registries in SQLite.",
            "category": "commands",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "command_registry",
            "notes": None,
            "spec": {
                "purpose": "Generate command registry tables in SQLite.",
                "returns": "Registry payloads for user and system.",
                "side_effects": ["writes sqlite tables"],
            },
            "audience": ["user", "system"],
        },
        {
            "name": "command_registry_describe",
            "script_path": "ai_restricted/system_management/command_registry_describe.py",
            "cli_args": (
                "--repo-root . --agent-id <agent_id> --actor-id <actor_id> "
                "--scope <system|user> --command-name <command_name> "
                "--work-id <work_id>"
            ),
            "summary": "Describe command registry entries without exposing paths.",
            "category": "commands",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "command_registry",
            "notes": "Paths are hidden by default; use command_registry_path for a single path.",
            "spec": {
                "purpose": "Return detailed command registry records with paths redacted.",
                "parameters": [
                    {
                        "name": "scope",
                        "description": "Registry scope to query.",
                        "type": "string",
                        "required": True,
                        "constraints": "system|user",
                    },
                    {
                        "name": "command_name",
                        "description": "Optional command name filter.",
                        "type": "string",
                        "required": False,
                    },
                    {
                        "name": "actor_id",
                        "description": "Actor identifier recorded in CRUD logs.",
                        "type": "string",
                        "required": True,
                    },
                ],
                "returns": "Minified JSON plus structured command descriptors.",
                "side_effects": ["reads sqlite tables", "may seed sqlite registries"],
            },
            "audience": ["user", "system"],
        },
        {
            "name": "command_registry_path",
            "script_path": "ai_restricted/system_management/command_registry_path.py",
            "cli_args": (
                "--repo-root . --agent-id <agent_id> --actor-id <actor_id> "
                "--scope <system|user> --command-name <command_name> "
                "--work-id <work_id>"
            ),
            "summary": "Resolve a single command's script path and entrypoint.",
            "category": "commands",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": "command_registry",
            "notes": "Path access is restricted to this single-command tool.",
            "spec": {
                "purpose": "Return the script path for one command registry entry.",
                "parameters": [
                    {
                        "name": "scope",
                        "description": "Registry scope to query.",
                        "type": "string",
                        "required": True,
                        "constraints": "system|user",
                    },
                    {
                        "name": "command_name",
                        "description": "Command name to resolve.",
                        "type": "string",
                        "required": True,
                    },
                    {
                        "name": "actor_id",
                        "description": "Actor identifier recorded in CRUD logs.",
                        "type": "string",
                        "required": True,
                    },
                ],
                "returns": "Minified JSON plus script path and entrypoint.",
                "side_effects": ["reads sqlite tables", "may seed sqlite registries"],
            },
            "audience": ["system"],
        },
        {
            "name": "sqlite_crud",
            "script_path": "ai_restricted/database_management/sqlite_crud_command.py",
            "cli_args": (
                "--repo-root . --agent-id <agent_id> --work-id <work_id> "
                "--operation <create|read|update|delete> --action <action> "
                "--scope <system|user|user_defined> --table-name <table_name> "
                "--payload-json <json> "
                "--actor-id <actor_id> --request-id <request_id> --transaction-id <transaction_id>"
            ),
            "summary": "CRUD interface for SQLite tables via registry enforcement.",
            "category": "database_management",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": None,
            "notes": "Payload JSON is required for create/update operations. action selects the script.",
            "spec": {
                "purpose": "Execute CRUD operations against SQLite tables with registry enforcement.",
                "parameters": [
                    {
                        "name": "operation",
                        "description": "CRUD operation to execute.",
                        "type": "string",
                        "required": True,
                        "constraints": "create|read|update|delete",
                    },
                    {
                        "name": "action",
                        "description": "Script action name within the operation folder.",
                        "type": "string",
                        "required": True,
                    },
                    {
                        "name": "scope",
                        "description": "Target database scope (system, user, user_defined).",
                        "type": "string",
                        "required": True,
                        "constraints": "system|user|user_defined",
                    },
                    {
                        "name": "table_name",
                        "description": "Registered table name for CRUD operations.",
                        "type": "string",
                        "required": True,
                    },
                    {
                        "name": "payload",
                        "description": "JSON payload object for create/update.",
                        "type": "object",
                        "required": False,
                    },
                    {
                        "name": "actor_id",
                        "description": "Actor identifier recorded in CRUD and log metadata.",
                        "type": "string",
                        "required": True,
                    },
                    {
                        "name": "request_id",
                        "description": "Optional request identifier for tracing.",
                        "type": "string",
                        "required": False,
                    },
                    {
                        "name": "transaction_id",
                        "description": "Optional transaction identifier for grouping operations.",
                        "type": "string",
                        "required": False,
                    },
                ],
                "returns": "CRUD output payload plus log identifiers.",
                "side_effects": ["writes sqlite tables", "writes operation log entries"],
            },
            "audience": ["system"],
        },
        {
            "name": "sqlite_query",
            "script_path": "ai_restricted/database_management/sqlite_query_command.py",
            "cli_args": (
                "--repo-root . --agent-id <agent_id> --work-id <work_id> "
                "--scope <system|user|user_defined> --query-name <query_name> "
                "--payload-json <json> --actor-id <actor_id> "
                "--request-id <request_id> --transaction-id <transaction_id>"
            ),
            "summary": "Execute registered SQLite query scripts via the query registry.",
            "category": "database_management",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": None,
            "notes": "Queries must be registered in db_query_registry for the target scope.",
            "spec": {
                "purpose": "Execute registered query scripts that may span multiple tables.",
                "parameters": [
                    {
                        "name": "scope",
                        "description": "Target database scope (system, user, user_defined).",
                        "type": "string",
                        "required": True,
                        "constraints": "system|user|user_defined",
                    },
                    {
                        "name": "query_name",
                        "description": "Registered query name to execute.",
                        "type": "string",
                        "required": True,
                    },
                    {
                        "name": "payload",
                        "description": "Optional JSON payload for the query script.",
                        "type": "object",
                        "required": False,
                    },
                    {
                        "name": "actor_id",
                        "description": "Actor identifier for audit logging.",
                        "type": "string",
                        "required": True,
                    },
                    {
                        "name": "request_id",
                        "description": "Optional request identifier for tracing.",
                        "type": "string",
                        "required": False,
                    },
                    {
                        "name": "transaction_id",
                        "description": "Optional transaction identifier for grouping.",
                        "type": "string",
                        "required": False,
                    },
                ],
                "returns": "Query output payload plus log identifiers.",
                "side_effects": ["reads sqlite tables", "writes operation log entries"],
            },
            "audience": ["system"],
        },
        {
            "name": "self_context",
            "script_path": "ai_restricted/agent_management/self_context.py",
            "cli_args": "--repo-root . --agent-id <agent_id>",
            "summary": "Initialize or update self context records.",
            "category": "self_context",
            "requires_certification": True,
            "requires_work_id": False,
            "feature_flag": None,
            "notes": "Use --init-self to create the self context file.",
            "audience": ["system"],
        },
        {
            "name": "skill_receipt",
            "script_path": "ai_restricted/agent_management/skill_receipt.py",
            "cli_args": "--repo-root . --agent-id <agent_id> --skill-id <skill>",
            "summary": "Write skill read receipts into self context.",
            "category": "self_context",
            "requires_certification": True,
            "requires_work_id": False,
            "feature_flag": None,
            "notes": None,
            "audience": ["system"],
        },
        {
            "name": "update_state",
            "script_path": "ai_restricted/system_management/update_state.py",
            "cli_args": "--repo-root . --agent-id <agent_id> --work-id <work_id> <scan|work-item>",
            "summary": "Update scan counters or work item state.",
            "category": "state",
            "requires_certification": True,
            "requires_work_id": True,
            "feature_flag": None,
            "notes": "Internal maintenance helper.",
            "audience": ["system"],
        },
        {
            "name": "lease",
            "script_path": "ai_restricted/system_management/lease.py",
            "cli_args": "",
            "summary": "Lock leasing helper (library module, not a CLI).",
            "category": "state",
            "requires_certification": False,
            "requires_work_id": False,
            "feature_flag": None,
            "notes": "Do not call directly; used by tools.",
            "audience": ["system"],
        },
    ]
    for command in commands:
        script_path = command.pop("script_path")
        cli_args = command.pop("cli_args")
        existing_spec = command.pop("spec", None)
        command["entry"] = _script_entry(script_path, cli_args)
        execution_spec = _execution_spec(script_path)
        if existing_spec is None:
            command["spec"] = execution_spec
        else:
            merged_spec = dict(existing_spec)
            merged_spec["execution"] = execution_spec["execution"]
            command["spec"] = merged_spec
    return commands


def _filter_commands(commands: Iterable[dict], audience: str) -> list[dict]:
    """
    Filter commands by audience and strip internal keys.

    Args:
        commands (Iterable[dict]): Command definitions.
        audience (str): Audience filter.

    Returns:
        list[dict]: Filtered command list.
    """
    filtered: list[dict] = []
    for command in commands:
        audiences = command.get("audience", [])
        if audience not in audiences:
            continue
        entry = {key: value for key, value in command.items() if key != "audience"}
        filtered.append(entry)
    return filtered


def _registry_payload(now: str, commands: list[dict]) -> dict:
    """
    Build a registry payload.

    Args:
        now (str): Current timestamp.
        commands (list[dict]): Command list.

    Returns:
        dict: Registry payload.
    """
    return {
        "schema_version": 1,
        "updated_at": now,
        "generated_at": now,
        "commands": commands,
    }


def generate_registries(repo_root: Path, actor_id: str) -> dict:
    """
    Generate both user and system command registries.

    Args:
        repo_root (Path): Repository root.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        dict: Registry payloads for user and system.

    Raises:
        FileNotFoundError: If required SQLite databases are missing.
        ValueError: If the registry payloads are malformed.
        sqlite_crud.SqliteCrudError: For unexpected CRUD failures.
    """
    now = utc_now_iso()
    catalog = _commands_catalog()
    user_commands = _filter_commands(catalog, "user")
    system_commands = _filter_commands(catalog, "system")

    payload_user = _registry_payload(now, user_commands)
    payload_system = _registry_payload(now, system_commands)

    registry_targets = [
        ("system", payload_system, "system"),
        ("user", payload_user, "user"),
    ]
    for scope, payload, label in registry_targets:
        _upsert_registry_table(
            repo_root=repo_root,
            scope=scope,
            payload=payload,
            label=label,
            actor_id=actor_id,
        )
    return {"user": payload_user, "system": payload_system}


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Generate command registries using the command runner contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing user/system registry payloads.

    Raises:
        None: All errors are captured and returned in the CommandResult.

    Contract:
        - Requires agent_id.
        - Enforces certification, feature flags, and work mode guards.
        - Writes registry rows into SQLite command registry tables.
        - Registry payloads are written only to SQLite.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        agent_id = require_string(payload, "agent_id", command_name)
        work_id = optional_string(payload, "work_id", command_name=command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    try:
        ensure_certified(repo_root, agent_id)
        ensure_feature_enabled(repo_root, "command_registry", "generate command registries")
        ensure_work_mode(repo_root, work_id, "generate command registries")
        registries = generate_registries(repo_root, agent_id)
        return ok_result(output={"registries": registries})
    except Exception as exc:
        return exception_result(command_name, exc)


def main() -> None:
    """
    CLI entrypoint for command registry generation.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """
    parser = argparse.ArgumentParser(description="Generate context_compass command registries")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "agent_id": args.agent_id,
        "work_id": args.work_id,
    }
    context = ExecutionContext(
        command_name="command_registry_generate",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("command_registry_generate failed: %s", result.errors)
        raise SystemExit(1)
    registries = result.output.get("registries", {"user": {"commands": []}, "system": {"commands": []}})
    logger.info(
        "command registries generated: user=%s system=%s",
        len(registries["user"]["commands"]),
        len(registries["system"]["commands"]),
    )


if __name__ == "__main__":
    main()
