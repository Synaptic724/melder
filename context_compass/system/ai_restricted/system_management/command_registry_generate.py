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


def _command_manifest_path(repo_root: Path) -> Path:
    """
    Resolve the command manifest path for this repository.

    Args:
        repo_root (Path): Repository root directory.

    Returns:
        Path: Manifest JSON path.
    """
    return (
        repo_root
        / "context_compass"
        / "system"
        / "ai_restricted"
        / "system_management"
        / "command_manifest.json"
    )


def _load_command_manifest(repo_root: Path) -> list[dict]:
    """
    Load the command manifest entries from JSON.

    Args:
        repo_root (Path): Repository root directory.

    Returns:
        list[dict]: Command manifest entries.

    Raises:
        FileNotFoundError: If the manifest is missing.
        ValueError: If the manifest payload is invalid.
    """
    manifest_path = _command_manifest_path(repo_root)
    if not manifest_path.exists():
        raise FileNotFoundError(f"Command manifest not found: {manifest_path}")
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Command manifest JSON is invalid: {manifest_path}") from exc
    if not isinstance(payload, dict):
        raise ValueError("Command manifest must be a JSON object.")
    schema_version = payload.get("schema_version")
    if not isinstance(schema_version, int) or schema_version < 1:
        raise ValueError("Command manifest schema_version must be an integer >= 1.")
    commands = payload.get("commands")
    if not isinstance(commands, list):
        raise ValueError("Command manifest commands must be a list.")
    for entry in commands:
        if not isinstance(entry, dict):
            raise ValueError("Command manifest commands must contain objects.")
    return [dict(entry) for entry in commands]


def _commands_catalog(repo_root: Path) -> list[dict]:
    """
    Return the canonical command catalog.

    Args:
        repo_root (Path): Repository root directory.

    Returns:
        list[dict]: Command definitions with audience tags and execution specs.

    Contract:
        - Loads command metadata from command_manifest.json.
        - Each command includes a path-based entry string.
        - Each command includes a spec.execution block for the runner.
    """
    commands = _load_command_manifest(repo_root)
    for command in commands:
        name = command.get("name", "<unknown>")
        script_path = command.pop("script_path", None)
        cli_args = command.pop("cli_args", None)
        if not isinstance(script_path, str) or not script_path:
            raise ValueError(f"Command manifest missing script_path for {name}.")
        if not isinstance(cli_args, str):
            raise ValueError(f"Command manifest missing cli_args for {name}.")
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
    catalog = _commands_catalog(repo_root)
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
