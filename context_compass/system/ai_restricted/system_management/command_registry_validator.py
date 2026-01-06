"""
Validator for SQLite-backed command registry tables.

Purpose
- Verify command registry tables exist and expose the required columns.
- Validate stored command rows for basic type and contract correctness.

Contract
- Validation is read-only and does not mutate database state.
- Missing columns or invalid row values are reported as issues.
"""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

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
from context_compass.system.ai_restricted._shared.work_mode_guard import ensure_work_mode
from context_compass.system.ai_restricted.database_management import sqlite_crud, sqlite_query
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)

REQUIRED_COLUMNS: Sequence[str] = (
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
VALIDATION_ACTOR_ID = "command_registry_validator"


@dataclass(frozen=True)
class RegistryValidationIssue:
    """
    Validation issue reported during registry checks.

    Attributes:
        table_name (str): Registry table name.
        command_name (str | None): Command name when applicable.
        message (str): Human-readable error description.

    Contract:
        - command_name may be None for table-level issues.
        - message should explain the validation failure clearly.
    """

    table_name: str
    command_name: str | None
    message: str


def _repo_root_from_db_path(db_path: Path) -> Path:
    """
    Resolve the repository root from a registry database path.

    Args:
        db_path (Path): SQLite database path under context_compass/system/storage/sqlite.

    Returns:
        Path: Repository root path.

    Raises:
        ValueError: If the database path is not under context_compass/system/storage/sqlite.
    """

    resolved = db_path.resolve()
    try:
        sqlite_root = resolved.parent
        storage_root = sqlite_root.parent
        system_root = storage_root.parent
        context_root = system_root.parent
        repo_root = context_root.parent
    except IndexError as exc:
        raise ValueError(
            "db_path must be located under context_compass/system/storage/sqlite."
        ) from exc
    if (
        sqlite_root.name != "sqlite"
        or storage_root.name != "storage"
        or system_root.name != "system"
        or context_root.name != "context_compass"
    ):
        raise ValueError(
            "db_path must be located under context_compass/system/storage/sqlite."
        )
    return repo_root


def _scope_for_registry_table(table_name: str) -> str:
    """
    Resolve the registry scope for a command registry table name.

    Args:
        table_name (str): Registry table name to resolve.

    Returns:
        str: Registry scope ("system" or "user").

    Raises:
        ValueError: If the table name is not a command registry table.
    """

    if table_name == "command_registry_system":
        return "system"
    if table_name == "command_registry_user":
        return "user"
    raise ValueError(f"Unsupported registry table: {table_name}")


def _describe_table(
    repo_root: Path,
    scope: str,
    table_name: str,
    actor_id: str,
) -> tuple[bool, list[str], list[RegistryValidationIssue]]:
    """
    Describe a registry table using the query API.

    Args:
        repo_root (Path): Repository root path.
        scope (str): Registry scope ("system" or "user").
        table_name (str): Table name to inspect.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        tuple[bool, list[str], list[RegistryValidationIssue]]: Exists flag, columns,
        and validation issues.

    Raises:
        None: Errors are converted into validation issues.
    """

    issues: list[RegistryValidationIssue] = []
    try:
        response = sqlite_query.execute_request(
            repo_root,
            sqlite_query.SqliteQueryRequest(
                scope=scope,
                query_name="describe_table",
                payload={"table_name": table_name},
                actor_id=actor_id,
            ),
        )
    except sqlite_query.SqliteQueryError as exc:
        issues.append(
            RegistryValidationIssue(
                table_name=table_name,
                command_name=None,
                message=f"Failed to describe table: {exc.code}",
            )
        )
        return False, [], issues

    result = response.output.get("result")
    if not isinstance(result, dict):
        issues.append(
            RegistryValidationIssue(
                table_name=table_name,
                command_name=None,
                message="describe_table returned invalid result payload.",
            )
        )
        return False, [], issues

    exists = result.get("exists")
    columns = result.get("columns")
    if not isinstance(exists, bool):
        issues.append(
            RegistryValidationIssue(
                table_name=table_name,
                command_name=None,
                message="describe_table returned invalid exists flag.",
            )
        )
        return False, [], issues
    if not isinstance(columns, list) or any(
        not isinstance(column, str) for column in columns
    ):
        issues.append(
            RegistryValidationIssue(
                table_name=table_name,
                command_name=None,
                message="describe_table returned invalid columns payload.",
            )
        )
        return exists, [], issues
    return exists, columns, issues


def _validate_schema(
    repo_root: Path,
    scope: str,
    table_name: str,
    actor_id: str,
) -> tuple[list[RegistryValidationIssue], list[str]]:
    """
    Validate required columns for a registry table.

    Args:
        repo_root (Path): Repository root path.
        scope (str): Registry scope ("system" or "user").
        table_name (str): Registry table to validate.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        tuple[list[RegistryValidationIssue], list[str]]: Issues and missing columns.

    Raises:
        None: Errors are converted into validation issues.
    """

    exists, columns, issues = _describe_table(repo_root, scope, table_name, actor_id)
    if not exists:
        issues.append(
            RegistryValidationIssue(
                table_name=table_name,
                command_name=None,
                message="Registry table is missing.",
            )
        )
        return issues, list(REQUIRED_COLUMNS)

    missing = [column for column in REQUIRED_COLUMNS if column not in columns]
    for column in missing:
        issues.append(
            RegistryValidationIssue(
                table_name=table_name,
                command_name=None,
                message=f"Missing required column: {column}",
            )
        )
    return issues, missing


def _validate_spec_json(
    table_name: str, command_name: str, spec_json: str
) -> list[RegistryValidationIssue]:
    """
    Validate a spec JSON payload stored in a registry row.

    Args:
        table_name (str): Registry table name.
        command_name (str): Command name being validated.
        spec_json (str): JSON string payload.

    Returns:
        list[RegistryValidationIssue]: Validation issues for the spec payload.

    Contract:
        - spec.execution must exist and be an object.
        - spec.execution.script_path must be a non-empty string.
        - spec.execution.entrypoint must be "run".
        - spec.execution.module is rejected to enforce path-based execution.
    """

    try:
        payload = json.loads(spec_json)
    except json.JSONDecodeError:
        return [
            RegistryValidationIssue(
                table_name=table_name,
                command_name=command_name,
                message="spec_json is not valid JSON.",
            )
        ]
    if not isinstance(payload, dict):
        return [
            RegistryValidationIssue(
                table_name=table_name,
                command_name=command_name,
                message="spec_json must decode to an object.",
            )
        ]
    execution = payload.get("execution")
    if execution is None or not isinstance(execution, dict):
        return [
            RegistryValidationIssue(
                table_name=table_name,
                command_name=command_name,
                message="spec.execution must be an object.",
            )
        ]
    module = execution.get("module")
    if module is not None:
        return [
            RegistryValidationIssue(
                table_name=table_name,
                command_name=command_name,
                message="spec.execution.module is not supported; use script_path.",
            )
        ]
    script_path = execution.get("script_path")
    if not isinstance(script_path, str) or not script_path.strip():
        return [
            RegistryValidationIssue(
                table_name=table_name,
                command_name=command_name,
                message="spec.execution.script_path must be a non-empty string.",
            )
        ]
    entrypoint = execution.get("entrypoint")
    if not isinstance(entrypoint, str) or not entrypoint.strip():
        return [
            RegistryValidationIssue(
                table_name=table_name,
                command_name=command_name,
                message="spec.execution.entrypoint must be a non-empty string.",
            )
        ]
    if entrypoint != "run":
        return [
            RegistryValidationIssue(
                table_name=table_name,
                command_name=command_name,
                message="spec.execution.entrypoint must be 'run'.",
            )
        ]
    return []


def _record_to_row(record: dict) -> tuple[object, ...]:
    """
    Convert a command registry record dict into a row tuple.

    Args:
        record (dict): Command registry record payload.

    Returns:
        tuple[object, ...]: Row tuple ordered by REQUIRED_COLUMNS.

    Raises:
        None: This helper does not raise.
    """

    return tuple(record.get(column) for column in REQUIRED_COLUMNS)


def _list_registry_records(
    repo_root: Path,
    scope: str,
    table_name: str,
    actor_id: str,
) -> tuple[list[dict], list[RegistryValidationIssue]]:
    """
    List command registry records using the CRUD API.

    Args:
        repo_root (Path): Repository root path.
        scope (str): Registry scope ("system" or "user").
        table_name (str): Registry table name to list.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        tuple[list[dict], list[RegistryValidationIssue]]: Records and validation issues.

    Raises:
        None: Errors are converted into validation issues.
    """

    issues: list[RegistryValidationIssue] = []
    try:
        response = sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="read",
                scope=scope,
                table_name=table_name,
                action="list_commands",
                payload=None,
                actor_id=actor_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        issues.append(
            RegistryValidationIssue(
                table_name=table_name,
                command_name=None,
                message=f"Failed to list registry rows: {exc.code}",
            )
        )
        return [], issues

    result = response.output.get("result")
    if not isinstance(result, dict):
        issues.append(
            RegistryValidationIssue(
                table_name=table_name,
                command_name=None,
                message="Registry list command returned invalid result payload.",
            )
        )
        return [], issues

    records = result.get("records")
    if not isinstance(records, list) or any(not isinstance(row, dict) for row in records):
        issues.append(
            RegistryValidationIssue(
                table_name=table_name,
                command_name=None,
                message="Registry list command returned invalid records payload.",
            )
        )
        return [], issues

    return records, issues


def _validate_row(
    table_name: str, row: Sequence[object]
) -> list[RegistryValidationIssue]:
    """
    Validate a single registry row.

    Args:
        table_name (str): Registry table name.
        row (Sequence[object]): Row values in REQUIRED_COLUMNS order.

    Returns:
        list[RegistryValidationIssue]: Validation issues for the row.

    Contract:
        - spec_json is required for execution metadata.
        - registry schema metadata must be present and valid.
    """

    issues: list[RegistryValidationIssue] = []
    command_name = row[0]
    if not isinstance(command_name, str) or not command_name.strip():
        issues.append(
            RegistryValidationIssue(
                table_name=table_name,
                command_name=None,
                message="command_name must be a non-empty string.",
            )
        )
        command_name = "<missing>"

    for index, field in enumerate(("category", "entry", "summary"), start=1):
        value = row[index]
        if not isinstance(value, str) or not value.strip():
            issues.append(
                RegistryValidationIssue(
                    table_name=table_name,
                    command_name=command_name,
                    message=f"{field} must be a non-empty string.",
                )
            )

    for index, field in enumerate(("requires_certification", "requires_work_id"), start=4):
        value = row[index]
        if value not in (0, 1):
            issues.append(
                RegistryValidationIssue(
                    table_name=table_name,
                    command_name=command_name,
                    message=f"{field} must be 0 or 1.",
                )
            )

    feature_flag = row[6]
    if feature_flag is not None and not isinstance(feature_flag, str):
        issues.append(
            RegistryValidationIssue(
                table_name=table_name,
                command_name=command_name,
                message="feature_flag must be a string or null.",
            )
        )

    notes = row[7]
    if notes is not None and not isinstance(notes, str):
        issues.append(
            RegistryValidationIssue(
                table_name=table_name,
                command_name=command_name,
                message="notes must be a string or null.",
            )
        )

    spec_json = row[8]
    if spec_json is None:
        issues.append(
            RegistryValidationIssue(
                table_name=table_name,
                command_name=command_name,
                message="spec_json is required for command execution.",
            )
        )
    elif not isinstance(spec_json, str):
        issues.append(
            RegistryValidationIssue(
                table_name=table_name,
                command_name=command_name,
                message="spec_json must be a string.",
            )
        )
    else:
        issues.extend(_validate_spec_json(table_name, command_name, spec_json))

    schema_version = row[9]
    if not isinstance(schema_version, int) or schema_version < 1:
        issues.append(
            RegistryValidationIssue(
                table_name=table_name,
                command_name=command_name,
                message="registry_schema_version must be an integer >= 1.",
            )
        )

    for index, field in enumerate(("registry_generated_at", "registry_updated_at"), start=10):
        value = row[index]
        if value is not None and not isinstance(value, str):
            issues.append(
                RegistryValidationIssue(
                    table_name=table_name,
                    command_name=command_name,
                    message=f"{field} must be a string or null.",
                )
            )

    return issues


def validate_registry_table(db_path: Path, table_name: str) -> list[RegistryValidationIssue]:
    """
    Validate a single registry table in a SQLite database.

    Args:
        db_path (Path): SQLite database path.
        table_name (str): Registry table name to validate.

    Returns:
        list[RegistryValidationIssue]: Validation issues found.

    Raises:
        None: Errors are converted into validation issues.
    """

    try:
        repo_root = _repo_root_from_db_path(db_path)
    except ValueError as exc:
        return [
            RegistryValidationIssue(
                table_name=table_name,
                command_name=None,
                message=str(exc),
            )
        ]

    try:
        scope = _scope_for_registry_table(table_name)
    except ValueError as exc:
        return [
            RegistryValidationIssue(
                table_name=table_name,
                command_name=None,
                message=str(exc),
            )
        ]
    issues, missing = _validate_schema(repo_root, scope, table_name, VALIDATION_ACTOR_ID)
    if missing:
        return issues

    records, list_issues = _list_registry_records(
        repo_root, scope, table_name, VALIDATION_ACTOR_ID
    )
    issues.extend(list_issues)
    if list_issues:
        return issues
    for record in records:
        issues.extend(_validate_row(table_name, _record_to_row(record)))
    return issues


def validate_registry_set(
    system_db: Path,
    user_db: Path,
    system_table: str = "command_registry_system",
    user_table: str = "command_registry_user",
) -> list[RegistryValidationIssue]:
    """
    Validate system and user registry tables together.

    Args:
        system_db (Path): SQLite system database path.
        user_db (Path): SQLite user database path.
        system_table (str): System registry table name.
        user_table (str): User registry table name.

    Returns:
        list[RegistryValidationIssue]: Combined validation issues.
    """

    issues = validate_registry_table(system_db, system_table)
    issues.extend(validate_registry_table(user_db, user_table))
    return issues


def _db_exists(db_path: Path, label: str) -> None:
    """
    Ensure a registry database file exists before validation.

    Args:
        db_path (Path): Database file path to check.
        label (str): Human-readable label for error context.

    Raises:
        FileNotFoundError: If the database path does not exist.

    Contract:
        - This validator is read-only; missing DB files are treated as errors.
    """

    if not db_path.exists():
        raise FileNotFoundError(f"Missing {label} database: {db_path}")


def _issue_payload(issue: RegistryValidationIssue) -> dict:
    """
    Convert a validation issue into a JSON-serializable payload.

    Args:
        issue (RegistryValidationIssue): Validation issue to serialize.

    Returns:
        dict: Serialized issue payload.

    Contract:
        - Keys match the RegistryValidationIssue attribute names.
    """

    return {
        "table_name": issue.table_name,
        "command_name": issue.command_name,
        "message": issue.message,
    }


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Validate command registry tables using the command runner contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing validation issues and summary stats.

    Raises:
        None: All errors are captured and returned in the CommandResult.

    Contract:
        - Requires agent_id.
        - Enforces certification, feature flags, and work mode guards.
        - Uses repo_root/context_compass/system/storage/sqlite by default.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        agent_id = require_string(payload, "agent_id", command_name)
        work_id = optional_string(payload, "work_id", command_name=command_name)
        system_db_value = optional_string(payload, "system_db", command_name=command_name)
        user_db_value = optional_string(payload, "user_db", command_name=command_name)
        system_table = optional_string(
            payload,
            "system_table",
            command_name=command_name,
            default="command_registry_system",
        )
        user_table = optional_string(
            payload,
            "user_table",
            command_name=command_name,
            default="command_registry_user",
        )
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    try:
        ensure_certified(repo_root, agent_id)
        ensure_feature_enabled(repo_root, "command_registry", "validate command registries")
        ensure_work_mode(repo_root, work_id, "validate command registries")

        storage_root = (
            repo_root
            / "context_compass"
            / "system"
            / "storage"
            / "sqlite"
        )
        system_db = (
            Path(system_db_value).resolve()
            if system_db_value
            else (storage_root / "system.db")
        )
        user_db = (
            Path(user_db_value).resolve()
            if user_db_value
            else (storage_root / "user.db")
        )
        _db_exists(system_db, "system")
        _db_exists(user_db, "user")
        issues = validate_registry_set(system_db, user_db, system_table, user_table)
        return ok_result(
            output={
                "issues": [_issue_payload(issue) for issue in issues],
                "issue_count": len(issues),
                "valid": len(issues) == 0,
                "system_db": system_db.as_posix(),
                "user_db": user_db.as_posix(),
                "system_table": system_table,
                "user_table": user_table,
            }
        )
    except Exception as exc:
        return exception_result(command_name, exc)


def main() -> None:
    """
    CLI entrypoint for registry validation.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """

    parser = argparse.ArgumentParser(
        description="Validate command registry tables for system and user registries."
    )
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--system-db", default=None, help="Override system db path")
    parser.add_argument("--user-db", default=None, help="Override user db path")
    parser.add_argument(
        "--system-table",
        default="command_registry_system",
        help="System registry table name",
    )
    parser.add_argument(
        "--user-table",
        default="command_registry_user",
        help="User registry table name",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    payload = {
        "repo_root": args.repo_root,
        "agent_id": args.agent_id,
        "work_id": args.work_id,
        "system_db": args.system_db,
        "user_db": args.user_db,
        "system_table": args.system_table,
        "user_table": args.user_table,
    }
    context = ExecutionContext(
        command_name="command_registry_validator",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("command_registry_validator failed: %s", result.errors)
        raise SystemExit(1)

    issue_count = result.output.get("issue_count", 0)
    if issue_count:
        logger.warning("Registry validation reported %d issue(s).", issue_count)
    else:
        logger.info("Registry validation reported no issues.")


if __name__ == "__main__":
    main()
