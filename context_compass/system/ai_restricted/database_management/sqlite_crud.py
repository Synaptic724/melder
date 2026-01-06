"""
SQLite CRUD API for registry-enforced table access.

Purpose
- Provide a single programmatic interface for SQLite CRUD operations.
- Enforce that all operations target tables registered in db_table_registry.
- Enforce that all operations target actions registered in db_action_registry.
- Log every CRUD request into db_operation_log with timing and actor metadata.
- Dispatch CRUD operations to script implementations in ai_restricted/sql_tools.

Contract
- Operations are limited to create/read/update/delete.
- action is required and selects the script within the operation folder.
- Table names must be present in db_table_registry for the target scope.
- Script execution is deterministic and resolved by table/operation/action.
- All operations are logged to db_operation_log for the target database.
"""

from __future__ import annotations

import importlib.util
import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Mapping, Sequence
from uuid import uuid4

from sqlalchemy import inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from context_compass.system.ai_restricted._shared.timeutils import utc_now_iso
from context_compass.system.ai_restricted.database_management.orm_session import (
    build_sqlite_engine,
    system_db_path,
    user_db_path,
    user_defined_db_path,
)
from context_compass.system.ai_restricted.database_management.system_orm_models import (
    DbOperationLog as SystemOperationLog,
    DbActionRegistry as SystemActionRegistry,
    DbTableRegistry as SystemTableRegistry,
)
from context_compass.system.ai_restricted.database_management.user_defined_orm_models import (
    DbOperationLog as UserDefinedOperationLog,
    DbActionRegistry as UserDefinedActionRegistry,
    DbTableRegistry as UserDefinedTableRegistry,
)
from context_compass.system.ai_restricted.database_management.user_orm_models import (
    DbOperationLog as UserOperationLog,
    DbActionRegistry as UserActionRegistry,
    DbTableRegistry as UserTableRegistry,
)
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)


SUPPORTED_SCOPES = ("system", "user", "user_defined")
SUPPORTED_OPERATIONS = ("create", "read", "update", "delete")
TABLE_REGISTRY_NAME = "db_table_registry"
ACTION_REGISTRY_NAME = "db_action_registry"
OPERATION_LOG_NAME = "db_operation_log"
ACTION_PATTERN = re.compile(r"^[a-z0-9_]+$")


@dataclass(frozen=True)
class SqliteCrudRequest:
    """
    CRUD request payload for SQLite operations.

    Attributes:
        operation (str): CRUD operation to execute.
        scope (str): Target scope (system, user, user_defined).
        table_name (str): Registered table name to operate on.
        action (str): Script action name for the operation.
        payload (dict[str, Any] | None): JSON payload for create/update.
        actor_id (str): Actor identifier for audit logging.
        request_id (str | None): Optional request identifier for tracing.
        transaction_id (str | None): Optional transaction identifier for grouping.

    Contract:
        - operation must be one of SUPPORTED_OPERATIONS.
        - scope must be one of SUPPORTED_SCOPES.
        - action must be a non-empty script name segment.
        - actor_id is required and non-empty.
        - action must be registered in db_action_registry for the target scope.
    """

    operation: str
    scope: str
    table_name: str
    action: str
    payload: dict[str, Any] | None
    actor_id: str
    request_id: str | None = None
    transaction_id: str | None = None


@dataclass(frozen=True)
class SqliteCrudResponse:
    """
    Response payload returned by SQLite CRUD operations.

    Attributes:
        status (str): Result status (ok or error).
        output (dict[str, Any]): Operation output payload including action metadata.
        log (dict[str, Any]): Log identifiers recorded for the request.

    Contract:
        - status is "ok" for successful operations.
        - output includes script result payloads.
        - log contains log_id, request_id, and transaction_id.
    """

    status: str
    output: dict[str, Any]
    log: dict[str, Any]


class SqliteCrudError(Exception):
    """
    Error raised for SQLite CRUD failures.

    Attributes:
        code (str): Stable error code for machine handling.
        meaning (str): Human-readable error description.
        details (dict[str, Any]): Structured error details.

    Contract:
        - code must be stable and non-empty.
        - details is JSON-serializable.
    """

    def __init__(self, code: str, meaning: str, details: Mapping[str, Any]) -> None:
        """
        Initialize a CRUD error.

        Args:
            code (str): Stable error code identifier.
            meaning (str): Human-readable error description.
            details (Mapping[str, Any]): Structured error details.
        """

        super().__init__(meaning)
        self.code = code
        self.meaning = meaning
        self.details = dict(details)


def _require_scope(scope: str) -> None:
    """
    Ensure the requested scope is supported.

    Args:
        scope (str): Scope value to validate.

    Raises:
        SqliteCrudError: If the scope is not supported.
    """

    if scope not in SUPPORTED_SCOPES:
        raise SqliteCrudError(
            code="invalid_scope",
            meaning="Scope is not supported.",
            details={"scope": scope, "supported": list(SUPPORTED_SCOPES)},
        )


def _require_operation(operation: str) -> None:
    """
    Ensure the requested operation is supported.

    Args:
        operation (str): Operation value to validate.

    Raises:
        SqliteCrudError: If the operation is not supported.
    """

    if operation not in SUPPORTED_OPERATIONS:
        raise SqliteCrudError(
            code="invalid_operation",
            meaning="Operation is not supported.",
            details={"operation": operation, "supported": list(SUPPORTED_OPERATIONS)},
        )


def _require_action(action: str) -> None:
    """
    Ensure the requested action name is valid.

    Args:
        action (str): Action value to validate.

    Raises:
        SqliteCrudError: If the action is missing or invalid.
    """

    if not action:
        raise SqliteCrudError(
            code="action_required",
            meaning="action is required for CRUD operations.",
            details={"action": action},
        )
    if not ACTION_PATTERN.fullmatch(action):
        raise SqliteCrudError(
            code="invalid_action",
            meaning="action must be lowercase snake_case.",
            details={"action": action},
        )


def _resolve_db_path(repo_root: Path, scope: str) -> Path:
    """
    Resolve the SQLite database path for a given scope.

    Args:
        repo_root (Path): Repository root path.
        scope (str): Database scope.

    Returns:
        Path: SQLite database path for the scope.

    Raises:
        SqliteCrudError: If the scope is invalid.
    """

    _require_scope(scope)
    if scope == "system":
        return system_db_path(repo_root)
    if scope == "user":
        return user_db_path(repo_root)
    return user_defined_db_path(repo_root)


def _registry_models(
    scope: str,
) -> tuple[
    type[SystemTableRegistry],
    type[SystemActionRegistry],
    type[SystemOperationLog],
]:
    """
    Resolve registry ORM models for the requested scope.

    Args:
        scope (str): SQLite database scope.

    Returns:
        tuple[type[SystemTableRegistry], type[SystemActionRegistry], type[SystemOperationLog]]:
            Registry and log models.

    Raises:
        SqliteCrudError: If the scope is invalid.
    """

    _require_scope(scope)
    if scope == "system":
        return SystemTableRegistry, SystemActionRegistry, SystemOperationLog
    if scope == "user":
        return UserTableRegistry, UserActionRegistry, UserOperationLog
    return UserDefinedTableRegistry, UserDefinedActionRegistry, UserDefinedOperationLog


def _ensure_registry_tables(engine: Any, scope: str) -> None:
    """
    Ensure registry and log tables exist in the target database.

    Args:
        engine (Any): SQLAlchemy engine bound to the target database.
        scope (str): SQLite database scope.

    Raises:
        SqliteCrudError: If registry or log tables are missing.
    """

    inspector = inspect(engine)
    if not inspector.has_table(TABLE_REGISTRY_NAME):
        raise SqliteCrudError(
            code="registry_missing",
            meaning="Required registry tables are missing.",
            details={"table_name": TABLE_REGISTRY_NAME, "scope": scope},
        )
    if not inspector.has_table(ACTION_REGISTRY_NAME):
        raise SqliteCrudError(
            code="registry_missing",
            meaning="Required registry tables are missing.",
            details={"table_name": ACTION_REGISTRY_NAME, "scope": scope},
        )
    if not inspector.has_table(OPERATION_LOG_NAME):
        raise SqliteCrudError(
            code="registry_missing",
            meaning="Required registry tables are missing.",
            details={"table_name": OPERATION_LOG_NAME, "scope": scope},
        )


def _fetch_registry_entry(
    session: Session, registry_model: type[SystemTableRegistry], table_name: str
) -> dict | None:
    """
    Fetch a registry entry for a table name.

    Args:
        session (Session): Active SQLAlchemy session.
        registry_model (type[SystemTableRegistry]): ORM registry model.
        table_name (str): Table name to fetch.

    Returns:
        dict | None: Registry entry dict or None if missing.
    """

    row = session.get(registry_model, table_name)
    if row is None:
        return None
    return {
        "table_name": row.table_name,
        "schema_ref": row.schema_ref,
        "purpose": row.purpose,
        "notes": row.notes,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }


def _placeholder_regex(placeholder: str) -> re.Pattern[str]:
    """
    Build a regex pattern from a placeholder table name.

    Args:
        placeholder (str): Placeholder table name containing <chevrons>.

    Returns:
        re.Pattern[str]: Compiled regex pattern for matching dynamic names.

    Contract:
        - Placeholder segments match non-whitespace characters.
        - The returned pattern enforces a full-string match.
    """

    parts = re.split(r"(<[^>]+>)", placeholder)
    pattern_parts: list[str] = []
    for part in parts:
        if part.startswith("<") and part.endswith(">"):
            pattern_parts.append(r"[^\s]+")
        elif part:
            pattern_parts.append(re.escape(part))
    pattern = "^" + "".join(pattern_parts) + "$"
    return re.compile(pattern)


def _find_placeholder_entry(
    session: Session, registry_model: type[SystemTableRegistry], table_name: str
) -> dict | None:
    """
    Find a placeholder registry entry that matches a concrete table name.

    Args:
        session (Session): Active SQLAlchemy session.
        registry_model (type[SystemTableRegistry]): ORM registry model.
        table_name (str): Concrete table name to match.

    Returns:
        dict | None: Matching placeholder entry or None if no match is found.
    """

    rows = session.execute(
        select(registry_model).where(registry_model.table_name.like("%<%>%"))
    ).scalars()
    for row in rows:
        placeholder = row.table_name
        if _placeholder_regex(placeholder).fullmatch(table_name):
            return {
                "table_name": placeholder,
                "schema_ref": row.schema_ref,
                "purpose": row.purpose,
                "notes": row.notes,
                "created_at": row.created_at,
                "updated_at": row.updated_at,
            }
    return None


def _register_dynamic_table(
    session: Session,
    registry_model: type[SystemTableRegistry],
    table_name: str,
    placeholder_entry: dict,
) -> dict:
    """
    Register a concrete table name based on a placeholder entry.

    Args:
        session (Session): Active SQLAlchemy session.
        registry_model (type[SystemTableRegistry]): ORM registry model.
        table_name (str): Concrete table name to register.
        placeholder_entry (dict): Placeholder registry entry to copy metadata from.

    Returns:
        dict: Newly registered table entry.

    Raises:
        SqliteCrudError: If the registry insert fails.
    """

    now = utc_now_iso()
    entry = registry_model(
        table_name=table_name,
        schema_ref=placeholder_entry.get("schema_ref"),
        purpose=placeholder_entry.get("purpose"),
        notes=placeholder_entry.get("notes"),
        created_at=now,
        updated_at=now,
    )
    session.add(entry)
    try:
        session.flush()
    except IntegrityError:
        existing = _fetch_registry_entry(session, registry_model, table_name)
        if existing is not None:
            return existing
        raise SqliteCrudError(
            code="registry_insert_failed",
            meaning="Failed to register dynamic table entry.",
            details={"table_name": table_name},
        )
    except Exception as exc:
        raise SqliteCrudError(
            code="registry_insert_failed",
            meaning="Failed to register dynamic table entry.",
            details={"table_name": table_name, "error": str(exc)},
        ) from exc

    return {
        "table_name": table_name,
        "schema_ref": placeholder_entry.get("schema_ref"),
        "purpose": placeholder_entry.get("purpose"),
        "notes": placeholder_entry.get("notes"),
        "created_at": now,
        "updated_at": now,
    }


def _ensure_table_registered(
    session: Session,
    registry_model: type[SystemTableRegistry],
    table_name: str,
) -> dict:
    """
    Ensure a table is registered before CRUD operations.

    Args:
        session (Session): Active SQLAlchemy session.
        registry_model (type[SystemTableRegistry]): ORM registry model.
        table_name (str): Table name to validate.

    Returns:
        dict: Registry entry for the table.

    Raises:
        SqliteCrudError: If the table is not registered.
    """

    entry = _fetch_registry_entry(session, registry_model, table_name)
    if entry is not None:
        return entry
    placeholder_entry = _find_placeholder_entry(session, registry_model, table_name)
    if placeholder_entry is not None:
        return _register_dynamic_table(session, registry_model, table_name, placeholder_entry)
    raise SqliteCrudError(
        code="table_not_registered",
        meaning="Table is not present in db_table_registry.",
        details={"table_name": table_name},
    )


def _fetch_action_entry(
    session: Session,
    action_registry_model: type[SystemActionRegistry],
    scope: str,
    table_name: str,
    operation: str,
    action: str,
) -> dict | None:
    """
    Fetch a registry entry for a CRUD action.

    Args:
        session (Session): Active SQLAlchemy session.
        action_registry_model (type[SystemActionRegistry]): ORM action registry model.
        scope (str): Requested SQLite scope.
        table_name (str): Target table name.
        operation (str): CRUD operation name.
        action (str): Action name within the operation folder.

    Returns:
        dict | None: Action registry entry dict or None if missing.
    """

    row = session.execute(
        select(action_registry_model).where(
            action_registry_model.scope == scope,
            action_registry_model.table_name == table_name,
            action_registry_model.operation == operation,
            action_registry_model.action == action,
        )
    ).scalar_one_or_none()
    if row is None:
        return None
    return {
        "scope": row.scope,
        "table_name": row.table_name,
        "operation": row.operation,
        "action": row.action,
        "script_path": row.script_path,
        "purpose": row.purpose,
        "operation_notes": row.operation_notes,
        "payload_schema_json": row.payload_schema_json,
        "output_schema_json": row.output_schema_json,
        "examples_json": row.examples_json,
        "requires_actor": row.requires_actor,
        "requires_work_id": row.requires_work_id,
        "enabled": row.enabled,
        "owner_id": row.owner_id,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }


def _ensure_action_registered(
    session: Session,
    action_registry_model: type[SystemActionRegistry],
    scope: str,
    table_name: str,
    operation: str,
    action: str,
) -> dict:
    """
    Ensure a CRUD action is registered and enabled.

    Args:
        session (Session): Active SQLAlchemy session.
        action_registry_model (type[SystemActionRegistry]): ORM action registry model.
        scope (str): Requested SQLite scope.
        table_name (str): Target table name.
        operation (str): CRUD operation name.
        action (str): Action name within the operation folder.

    Returns:
        dict: Action registry entry for the action.

    Raises:
        SqliteCrudError: If the action is missing, disabled, or mis-scoped.
    """

    entry = _fetch_action_entry(
        session,
        action_registry_model,
        scope,
        table_name,
        operation,
        action,
    )
    if entry is None:
        raise SqliteCrudError(
            code="action_not_registered",
            meaning="Action is not present in db_action_registry.",
            details={
                "scope": scope,
                "table_name": table_name,
                "operation": operation,
                "action": action,
            },
        )
    if entry["scope"] != scope:
        raise SqliteCrudError(
            code="action_scope_mismatch",
            meaning="Action registry entry scope does not match the request scope.",
            details={
                "scope": scope,
                "action_scope": entry["scope"],
                "table_name": table_name,
                "operation": operation,
                "action": action,
            },
        )
    if not entry["enabled"]:
        raise SqliteCrudError(
            code="action_disabled",
            meaning="Action is disabled in db_action_registry.",
            details={
                "scope": scope,
                "table_name": table_name,
                "operation": operation,
                "action": action,
            },
        )
    return entry


def _table_exists(engine: Any, table_name: str) -> bool:
    """
    Check if a physical table exists in SQLite.

    Args:
        engine (Any): SQLAlchemy engine bound to the target database.
        table_name (str): Table name to check.

    Returns:
        bool: True if the table exists, False otherwise.
    """

    inspector = inspect(engine)
    return inspector.has_table(table_name)


def _resolve_script_path(repo_root: Path, script_path_value: str) -> Path:
    """
    Resolve an action script path from a registry entry.

    Args:
        repo_root (Path): Repository root path.
        script_path_value (str): Script path stored in the action registry.

    Returns:
        Path: Resolved script path to execute.

    Raises:
        SqliteCrudError: If the script path is missing or cannot be resolved.
    """

    if not script_path_value:
        raise SqliteCrudError(
            code="script_path_missing",
            meaning="Action registry entry is missing script_path.",
            details={"script_path": script_path_value},
        )
    candidate = Path(script_path_value)
    if candidate.is_absolute():
        resolved = candidate
    else:
        repo_candidate = (
            repo_root / "context_compass" / "system" / candidate
        )
        if repo_candidate.exists():
            resolved = repo_candidate
        else:
            resolved = Path(__file__).resolve().parents[2] / candidate
    if not resolved.exists():
        raise SqliteCrudError(
            code="script_not_found",
            meaning="No SQL tool script found for the requested operation.",
            details={"script_path": script_path_value, "resolved_path": str(resolved)},
        )
    return resolved


def _load_script(script_path: Path) -> ModuleType:
    """
    Load a SQL tool module from a script path.

    Args:
        script_path (Path): Script path to load.

    Returns:
        ModuleType: Imported module instance.

    Raises:
        SqliteCrudError: If the module cannot be loaded.
    """

    module_name = f"sql_tool_{script_path.stem}_{uuid4().hex}"
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise SqliteCrudError(
            code="script_load_failed",
            meaning="Failed to load SQL tool script.",
            details={"script_path": str(script_path)},
        )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _command_error_payload(errors: Sequence[Any]) -> list[dict[str, Any]]:
    """
    Normalize CommandError entries into serializable dicts.

    Args:
        errors (Sequence[Any]): CommandError sequence from CommandResult.

    Returns:
        list[dict[str, Any]]: Normalized error payloads.
    """

    payloads: list[dict[str, Any]] = []
    for error in errors:
        details = error.details
        parsed_details: Any = None
        if isinstance(details, str):
            try:
                parsed_details = json.loads(details)
            except json.JSONDecodeError:
                parsed_details = {"raw": details}
        payloads.append(
            {
                "code": error.code,
                "meaning": error.meaning,
                "details": parsed_details,
            }
        )
    return payloads


def _run_script(
    script_path: Path, repo_root: Path, request: SqliteCrudRequest
) -> CommandResult:
    """
    Execute a SQL tool script for the CRUD request.

    Args:
        script_path (Path): Script path to execute.
        repo_root (Path): Repository root path.
        request (SqliteCrudRequest): CRUD request payload.

    Returns:
        CommandResult: CommandResult returned by the script.

    Raises:
        SqliteCrudError: If the script fails or returns an invalid payload.
    """

    module = _load_script(script_path)
    try:
        run_fn = module.run
    except AttributeError as exc:
        raise SqliteCrudError(
            code="script_missing_entrypoint",
            meaning="SQL tool script does not define a run() entrypoint.",
            details={"script_path": str(script_path)},
        ) from exc

    payload = {
        "repo_root": str(repo_root),
        "scope": request.scope,
        "table_name": request.table_name,
        "operation": request.operation,
        "action": request.action,
        "payload": request.payload,
        "actor_id": request.actor_id,
        "request_id": request.request_id,
        "transaction_id": request.transaction_id,
    }
    ctx = ExecutionContext(
        command_name=(
            f"sqlite_crud::{request.table_name}::{request.operation}::{request.action}"
        ),
        agent_id=request.actor_id,
        work_id=None,
        correlation_id=request.request_id,
    )
    result = run_fn(payload, ctx)
    if not isinstance(result, CommandResult):
        raise SqliteCrudError(
            code="script_invalid_response",
            meaning="SQL tool script returned an invalid result type.",
            details={
                "script_path": str(script_path),
                "returned_type": type(result).__name__,
            },
        )
    return result


def _serialize_error_details(details: Mapping[str, Any] | None) -> str | None:
    """
    Serialize error details for persistence in db_operation_log.

    Args:
        details (Mapping[str, Any] | None): Error details mapping.

    Returns:
        str | None: Minified JSON string or None.
    """

    if details is None:
        return None
    return json.dumps(details, separators=(",", ":"))


def _extract_record_id(payload: dict[str, Any] | None) -> str | None:
    """
    Extract a record_id value from the nested payload if present.

    Args:
        payload (dict[str, Any] | None): Nested payload object from the request.

    Returns:
        str | None: record_id string if present and valid, otherwise None.
    """

    if not isinstance(payload, dict):
        return None
    record_id = payload.get("record_id")
    if isinstance(record_id, str) and record_id:
        return record_id
    return None


def _insert_log(
    session: Session,
    log_model: type[SystemOperationLog],
    *,
    log_id: str,
    transaction_id: str,
    request_id: str,
    operation: str,
    table_name: str,
    record_id: str | None,
    actor_id: str,
    status: str,
    error_code: str | None,
    error_details: Mapping[str, Any] | None,
    started_at: str,
    completed_at: str,
    duration_ms: int,
) -> None:
    """
    Insert a log row into db_operation_log.

    Args:
        session (Session): Active SQLAlchemy session.
        log_model (type[SystemOperationLog]): ORM model for db_operation_log.
        log_id (str): Log identifier.
        transaction_id (str): Transaction identifier.
        request_id (str): Request identifier.
        operation (str): Operation name.
        table_name (str): Target table name.
        record_id (str | None): Record id involved in the operation.
        actor_id (str): Actor identifier.
        status (str): Operation status.
        error_code (str | None): Optional error code.
        error_details (Mapping[str, Any] | None): Optional error details.
        started_at (str): Start timestamp.
        completed_at (str): Completion timestamp.
        duration_ms (int): Duration in milliseconds.

    Raises:
        SqliteCrudError: If the log insert fails.
    """

    entry = log_model(
        log_id=log_id,
        transaction_id=transaction_id,
        request_id=request_id,
        operation=operation,
        table_name=table_name,
        record_id=record_id,
        actor_id=actor_id,
        status=status,
        error_code=error_code,
        error_details=_serialize_error_details(error_details),
        started_at=started_at,
        completed_at=completed_at,
        duration_ms=duration_ms,
    )
    session.add(entry)
    try:
        session.flush()
    except Exception as exc:
        raise SqliteCrudError(
            code="log_insert_failed",
            meaning="Failed to insert operation log entry.",
            details={"error": str(exc)},
        ) from exc


def _validate_payload_object(payload: Any, operation: str) -> dict[str, Any] | None:
    """
    Validate and normalize payload inputs for CRUD operations.

    Args:
        payload (Any): Payload value supplied in the request.
        operation (str): CRUD operation to validate for.

    Returns:
        dict[str, Any] | None: Normalized payload or None if not required.

    Raises:
        SqliteCrudError: If payload is missing or invalid for the operation.
    """

    if operation in ("create", "update"):
        if payload is None:
            raise SqliteCrudError(
                code="payload_required",
                meaning="Payload is required for create/update operations.",
                details={"operation": operation},
            )
        if not isinstance(payload, dict):
            raise SqliteCrudError(
                code="payload_invalid",
                meaning="Payload must be a JSON object.",
                details={"operation": operation, "payload_type": type(payload).__name__},
            )
        return payload
    return None


def execute_request(repo_root: Path, request: SqliteCrudRequest) -> SqliteCrudResponse:
    """
    Execute a SQLite CRUD request with registry enforcement and logging.

    Args:
        repo_root (Path): Repository root path.
        request (SqliteCrudRequest): CRUD request payload.

    Returns:
        SqliteCrudResponse: CRUD response payload with log metadata.

    Raises:
        SqliteCrudError: If validation or CRUD execution fails.
    """

    _require_operation(request.operation)
    _require_action(request.action)
    if not request.actor_id:
        raise SqliteCrudError(
            code="actor_required",
            meaning="actor_id is required for CRUD operations.",
            details={"actor_id": request.actor_id},
        )
    if not request.table_name:
        raise SqliteCrudError(
            code="table_required",
            meaning="table_name is required for CRUD operations.",
            details={},
        )

    db_path = _resolve_db_path(repo_root, request.scope)
    if not db_path.exists():
        raise SqliteCrudError(
            code="db_missing",
            meaning="SQLite database does not exist.",
            details={"db_path": str(db_path), "scope": request.scope},
        )

    log_id = str(uuid4())
    request_id = request.request_id or str(uuid4())
    transaction_id = request.transaction_id or request_id
    started_at = utc_now_iso()
    started_monotonic = time.monotonic()
    log_operation = f"{request.operation}:{request.action}"

    table_registry_model, action_registry_model, log_model = _registry_models(request.scope)
    engine = build_sqlite_engine(db_path, must_exist=True)
    factory = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    registry_entry: dict[str, Any] | None = None
    action_entry: dict[str, Any] | None = None
    record_id = _extract_record_id(request.payload)

    try:
        _ensure_registry_tables(engine, request.scope)
        session = factory()
        try:
            registry_entry = _ensure_table_registered(
                session, table_registry_model, request.table_name
            )
            action_entry = _ensure_action_registered(
                session,
                action_registry_model,
                request.scope,
                request.table_name,
                request.operation,
                request.action,
            )
            if not _table_exists(engine, request.table_name):
                raise SqliteCrudError(
                    code="table_missing",
                    meaning="Target table does not exist in SQLite.",
                    details={"table_name": request.table_name},
                )
            session.commit()
        except SqliteCrudError:
            session.rollback()
            raise
        finally:
            session.close()

        _validate_payload_object(request.payload, request.operation)
        script_path = _resolve_script_path(
            repo_root, action_entry["script_path"] if action_entry else ""
        )
        result = _run_script(script_path, repo_root, request)

        if result.status != "ok":
            errors = _command_error_payload(result.errors)
            error_code = errors[0]["code"] if errors else "script_error"
            raise SqliteCrudError(
                code=error_code,
                meaning="SQL tool script reported an error.",
                details={
                    "table_name": request.table_name,
                    "operation": request.operation,
                    "action": request.action,
                    "script_path": str(script_path),
                    "registry_entry": registry_entry,
                    "action_entry": action_entry,
                    "script_status": result.status,
                    "script_errors": errors,
                    "script_output": result.output,
                    "script_metadata": result.metadata,
                },
            )

        output: dict[str, Any] = {
            "operation": request.operation,
            "action": request.action,
            "scope": request.scope,
            "table_name": request.table_name,
            "registry_entry": registry_entry,
            "script": {
                "path": str(script_path),
                "entrypoint": "run",
            },
            "result": result.output,
            "metadata": result.metadata,
            "artifacts": result.artifacts,
            "queries": result.queries,
        }

        completed_at = utc_now_iso()
        duration_ms = int((time.monotonic() - started_monotonic) * 1000)
        log_session = factory()
        try:
            _insert_log(
                log_session,
                log_model,
                log_id=log_id,
                transaction_id=transaction_id,
                request_id=request_id,
                operation=log_operation,
                table_name=request.table_name,
                record_id=record_id,
                actor_id=request.actor_id,
                status="ok",
                error_code=None,
                error_details=None,
                started_at=started_at,
                completed_at=completed_at,
                duration_ms=duration_ms,
            )
            log_session.commit()
        finally:
            log_session.close()
        return SqliteCrudResponse(
            status="ok",
            output=output,
            log={
                "log_id": log_id,
                "request_id": request_id,
                "transaction_id": transaction_id,
            },
        )
    except SqliteCrudError as exc:
        if exc.code == "registry_missing":
            raise
        completed_at = utc_now_iso()
        duration_ms = int((time.monotonic() - started_monotonic) * 1000)
        error_details = dict(exc.details)
        error_details.update(
            {
                "log_id": log_id,
                "request_id": request_id,
                "transaction_id": transaction_id,
            }
        )
        log_session = factory()
        try:
            _insert_log(
                log_session,
                log_model,
                log_id=log_id,
                transaction_id=transaction_id,
                request_id=request_id,
                operation=log_operation,
                table_name=request.table_name,
                record_id=record_id,
                actor_id=request.actor_id,
                status="error",
                error_code=exc.code,
                error_details=error_details,
                started_at=started_at,
                completed_at=completed_at,
                duration_ms=duration_ms,
            )
            log_session.commit()
            exc.details.update(
                {
                    "log_id": log_id,
                    "request_id": request_id,
                    "transaction_id": transaction_id,
                }
            )
        except SqliteCrudError:
            log_session.rollback()
        finally:
            log_session.close()
        raise
    finally:
        engine.dispose()
