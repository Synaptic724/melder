"""
SQLite query API for registry-enforced query scripts.

Purpose
- Provide a single programmatic interface for registered SQLite query scripts.
- Enforce that all queries are registered in db_query_registry for the target scope.
- Log every query execution into db_operation_log with timing and actor metadata.
- Dispatch query execution to scripts in ai_restricted/sql_queries/<scope>.

Contract
- Scopes are limited to system/user/user_defined.
- query_name must be registered in db_query_registry for the target scope.
- script_path is required in db_query_registry for execution.
- Script execution is deterministic and resolved by scope/query_name.
- All query executions are logged to db_operation_log for the target database.
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
    DbQueryRegistry as SystemQueryRegistry,
)
from context_compass.system.ai_restricted.database_management.user_defined_orm_models import (
    DbOperationLog as UserDefinedOperationLog,
    DbQueryRegistry as UserDefinedQueryRegistry,
)
from context_compass.system.ai_restricted.database_management.user_orm_models import (
    DbOperationLog as UserOperationLog,
    DbQueryRegistry as UserQueryRegistry,
)
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)


SUPPORTED_SCOPES = ("system", "user", "user_defined")
QUERY_REGISTRY_NAME = "db_query_registry"
OPERATION_LOG_NAME = "db_operation_log"
QUERY_NAME_PATTERN = re.compile(r"^[a-z0-9_]+$")


@dataclass(frozen=True)
class SqliteQueryRequest:
    """
    Query request payload for SQLite operations.

    Attributes:
        scope (str): Target scope (system, user, user_defined).
        query_name (str): Registered query name to execute.
        payload (dict[str, Any] | None): Optional JSON payload for the query.
        actor_id (str): Actor identifier for audit logging.
        request_id (str | None): Optional request identifier for tracing.
        transaction_id (str | None): Optional transaction identifier for grouping.

    Contract:
        - scope must be one of SUPPORTED_SCOPES.
        - query_name must be a lowercase snake_case identifier.
        - actor_id is required and non-empty.
    """

    scope: str
    query_name: str
    payload: dict[str, Any] | None
    actor_id: str
    request_id: str | None = None
    transaction_id: str | None = None


@dataclass(frozen=True)
class SqliteQueryResponse:
    """
    Response payload returned by SQLite query operations.

    Attributes:
        status (str): Result status (ok or error).
        output (dict[str, Any]): Query output payload.
        log (dict[str, Any]): Log identifiers recorded for the request.

    Contract:
        - status is "ok" for successful operations.
        - output includes script result payloads.
        - log contains log_id, request_id, and transaction_id.
    """

    status: str
    output: dict[str, Any]
    log: dict[str, Any]


class SqliteQueryError(Exception):
    """
    Error raised for SQLite query failures.

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
        Initialize a query error.

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
        SqliteQueryError: If the scope is not supported.
    """

    if scope not in SUPPORTED_SCOPES:
        raise SqliteQueryError(
            code="invalid_scope",
            meaning="Scope is not supported.",
            details={"scope": scope, "supported": list(SUPPORTED_SCOPES)},
        )


def _require_query_name(query_name: str) -> None:
    """
    Ensure the requested query name is valid.

    Args:
        query_name (str): Query name to validate.

    Raises:
        SqliteQueryError: If the query name is missing or invalid.
    """

    if not query_name:
        raise SqliteQueryError(
            code="query_required",
            meaning="query_name is required for query execution.",
            details={"query_name": query_name},
        )
    if not QUERY_NAME_PATTERN.fullmatch(query_name):
        raise SqliteQueryError(
            code="invalid_query_name",
            meaning="query_name must be lowercase snake_case.",
            details={"query_name": query_name},
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
        SqliteQueryError: If the scope is invalid.
    """

    _require_scope(scope)
    if scope == "system":
        return system_db_path(repo_root)
    if scope == "user":
        return user_db_path(repo_root)
    return user_defined_db_path(repo_root)


def _registry_models(
    scope: str,
) -> tuple[type[SystemQueryRegistry], type[SystemOperationLog]]:
    """
    Resolve registry ORM models for the requested scope.

    Args:
        scope (str): SQLite database scope.

    Returns:
        tuple[type[SystemQueryRegistry], type[SystemOperationLog]]: Registry and log models.

    Raises:
        SqliteQueryError: If the scope is invalid.
    """

    _require_scope(scope)
    if scope == "system":
        return SystemQueryRegistry, SystemOperationLog
    if scope == "user":
        return UserQueryRegistry, UserOperationLog
    return UserDefinedQueryRegistry, UserDefinedOperationLog


def _ensure_registry_tables(engine: Any, scope: str) -> None:
    """
    Ensure registry and log tables exist in the target database.

    Args:
        engine (Any): SQLAlchemy engine bound to the target database.
        scope (str): SQLite database scope.

    Raises:
        SqliteQueryError: If registry or log tables are missing.
    """

    inspector = inspect(engine)
    if not inspector.has_table(QUERY_REGISTRY_NAME):
        raise SqliteQueryError(
            code="registry_missing",
            meaning="Required registry tables are missing.",
            details={"table_name": QUERY_REGISTRY_NAME, "scope": scope},
        )
    if not inspector.has_table(OPERATION_LOG_NAME):
        raise SqliteQueryError(
            code="registry_missing",
            meaning="Required registry tables are missing.",
            details={"table_name": OPERATION_LOG_NAME, "scope": scope},
        )


def _fetch_query_entry(
    session: Session, registry_model: type[SystemQueryRegistry], query_name: str
) -> dict | None:
    """
    Fetch a registry entry for a query name.

    Args:
        session (Session): Active SQLAlchemy session.
        registry_model (type[SystemQueryRegistry]): ORM registry model.
        query_name (str): Query name to fetch.

    Returns:
        dict | None: Registry entry dict or None if missing.
    """

    row = session.get(registry_model, query_name)
    if row is None:
        return None
    return {
        "query_name": row.query_name,
        "scope": row.scope,
        "script_path": row.script_path,
        "tables_involved_json": row.tables_involved_json,
        "operation_type": row.operation_type,
        "operation_notes": row.operation_notes,
        "schema_ref": row.schema_ref,
        "purpose": row.purpose,
        "notes": row.notes,
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


def _ensure_query_registered(
    session: Session,
    registry_model: type[SystemQueryRegistry],
    scope: str,
    query_name: str,
) -> dict:
    """
    Ensure a query is registered before execution.

    Args:
        session (Session): Active SQLAlchemy session.
        registry_model (type[SystemQueryRegistry]): ORM registry model.
        scope (str): Requested SQLite scope.
        query_name (str): Query name to validate.

    Returns:
        dict: Registry entry for the query.

    Raises:
        SqliteQueryError: If the query is not registered.
    """

    entry = _fetch_query_entry(session, registry_model, query_name)
    if entry is None:
        raise SqliteQueryError(
            code="query_not_registered",
            meaning="Query is not present in db_query_registry.",
            details={"query_name": query_name},
        )
    if entry["scope"] != scope:
        raise SqliteQueryError(
            code="query_scope_mismatch",
            meaning="Query registry entry scope does not match the request scope.",
            details={
                "scope": scope,
                "query_scope": entry["scope"],
                "query_name": query_name,
            },
        )
    if not entry["enabled"]:
        raise SqliteQueryError(
            code="query_disabled",
            meaning="Query is disabled in db_query_registry.",
            details={"scope": scope, "query_name": query_name},
        )
    if not entry["script_path"]:
        raise SqliteQueryError(
            code="script_path_missing",
            meaning="Query registry entry is missing script_path.",
            details={"scope": scope, "query_name": query_name},
        )
    return entry


def _sql_queries_root(repo_root: Path) -> Path:
    """
    Resolve the sql_queries root directory for the repository.

    Args:
        repo_root (Path): Repository root path.

    Returns:
        Path: Root directory containing sql_queries scripts.
    """

    repo_path = (
        repo_root
        / "context_compass"
        / "system"
        / "ai_restricted"
        / "sql_queries"
    )
    if repo_path.exists():
        return repo_path
    legacy_path = (
        repo_root
        / "src"
        / "context_compass"
        / "system"
        / "ai_restricted"
        / "sql_queries"
    )
    if legacy_path.exists():
        return legacy_path
    return Path(__file__).resolve().parents[1] / "sql_queries"


def _resolve_script_path(repo_root: Path, script_path_value: str) -> Path:
    """
    Resolve a query script path from a registry entry.

    Args:
        repo_root (Path): Repository root path.
        script_path_value (str): Script path stored in the query registry.

    Returns:
        Path: Script path to execute.

    Raises:
        SqliteQueryError: If no script is found for the query.
    """

    if not script_path_value:
        raise SqliteQueryError(
            code="script_path_missing",
            meaning="Query registry entry is missing script_path.",
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
        raise SqliteQueryError(
            code="script_not_found",
            meaning="No SQL query script found for the requested query.",
            details={"script_path": script_path_value, "resolved_path": str(resolved)},
        )
    return resolved


def _load_script(script_path: Path) -> ModuleType:
    """
    Load a SQL query module from a script path.

    Args:
        script_path (Path): Script path to load.

    Returns:
        ModuleType: Imported module instance.

    Raises:
        SqliteQueryError: If the module cannot be loaded.
    """

    module_name = f"sql_query_{script_path.stem}_{uuid4().hex}"
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise SqliteQueryError(
            code="script_load_failed",
            meaning="Failed to load SQL query script.",
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
    script_path: Path, repo_root: Path, request: SqliteQueryRequest
) -> CommandResult:
    """
    Execute a SQL query script for the request.

    Args:
        script_path (Path): Script path to execute.
        repo_root (Path): Repository root path.
        request (SqliteQueryRequest): Query request payload.

    Returns:
        CommandResult: CommandResult returned by the script.

    Raises:
        SqliteQueryError: If the script fails or returns an invalid payload.
    """

    module = _load_script(script_path)
    try:
        run_fn = module.run
    except AttributeError as exc:
        raise SqliteQueryError(
            code="script_missing_entrypoint",
            meaning="SQL query script does not define a run() entrypoint.",
            details={"script_path": str(script_path)},
        ) from exc

    payload = {
        "repo_root": str(repo_root),
        "scope": request.scope,
        "query_name": request.query_name,
        "payload": request.payload,
        "actor_id": request.actor_id,
        "request_id": request.request_id,
        "transaction_id": request.transaction_id,
    }
    ctx = ExecutionContext(
        command_name=f"sqlite_query::{request.scope}::{request.query_name}",
        agent_id=request.actor_id,
        work_id=None,
        correlation_id=request.request_id,
    )
    result = run_fn(payload, ctx)
    if not isinstance(result, CommandResult):
        raise SqliteQueryError(
            code="script_invalid_response",
            meaning="SQL query script returned an invalid result type.",
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
        table_name (str): Target table name (query name for queries).
        record_id (str | None): Record id involved in the operation.
        actor_id (str): Actor identifier.
        status (str): Operation status.
        error_code (str | None): Optional error code.
        error_details (Mapping[str, Any] | None): Optional error details.
        started_at (str): Start timestamp.
        completed_at (str): Completion timestamp.
        duration_ms (int): Duration in milliseconds.

    Raises:
        SqliteQueryError: If the log insert fails.
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
        raise SqliteQueryError(
            code="log_insert_failed",
            meaning="Failed to insert operation log entry.",
            details={"error": str(exc)},
        ) from exc


def _validate_payload_object(payload: Any) -> dict[str, Any] | None:
    """
    Validate payload inputs for query operations.

    Args:
        payload (Any): Payload value supplied in the request.

    Returns:
        dict[str, Any] | None: Normalized payload or None if not provided.

    Raises:
        SqliteQueryError: If payload is not a JSON object.
    """

    if payload is None:
        return None
    if not isinstance(payload, dict):
        raise SqliteQueryError(
            code="payload_invalid",
            meaning="Payload must be a JSON object.",
            details={"payload_type": type(payload).__name__},
        )
    return payload


def execute_request(repo_root: Path, request: SqliteQueryRequest) -> SqliteQueryResponse:
    """
    Execute a SQLite query request with registry enforcement and logging.

    Args:
        repo_root (Path): Repository root path.
        request (SqliteQueryRequest): Query request payload.

    Returns:
        SqliteQueryResponse: Query response payload with log metadata.

    Raises:
        SqliteQueryError: If validation or query execution fails.
    """

    _require_scope(request.scope)
    _require_query_name(request.query_name)
    if not request.actor_id:
        raise SqliteQueryError(
            code="actor_required",
            meaning="actor_id is required for query operations.",
            details={"actor_id": request.actor_id},
        )

    db_path = _resolve_db_path(repo_root, request.scope)
    if not db_path.exists():
        raise SqliteQueryError(
            code="db_missing",
            meaning="SQLite database does not exist.",
            details={"db_path": str(db_path), "scope": request.scope},
        )

    log_id = str(uuid4())
    request_id = request.request_id or str(uuid4())
    transaction_id = request.transaction_id or request_id
    started_at = utc_now_iso()
    started_monotonic = time.monotonic()
    log_operation = f"query::{request.query_name}"

    registry_model, log_model = _registry_models(request.scope)
    engine = build_sqlite_engine(db_path, must_exist=True)
    factory = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    registry_entry: dict[str, Any] | None = None
    _validate_payload_object(request.payload)

    try:
        _ensure_registry_tables(engine, request.scope)
        session = factory()
        try:
            registry_entry = _ensure_query_registered(
                session,
                registry_model,
                request.scope,
                request.query_name,
            )
            session.commit()
        except SqliteQueryError:
            session.rollback()
            raise
        finally:
            session.close()

        script_path = _resolve_script_path(
            repo_root, registry_entry["script_path"] if registry_entry else ""
        )
        result = _run_script(script_path, repo_root, request)

        if result.status != "ok":
            errors = _command_error_payload(result.errors)
            error_code = errors[0]["code"] if errors else "script_error"
            raise SqliteQueryError(
                code=error_code,
                meaning="SQL query script reported an error.",
                details={
                    "query_name": request.query_name,
                    "scope": request.scope,
                    "script_path": str(script_path),
                    "registry_entry": registry_entry,
                    "script_status": result.status,
                    "script_errors": errors,
                    "script_output": result.output,
                    "script_metadata": result.metadata,
                },
            )

        output: dict[str, Any] = {
            "scope": request.scope,
            "query_name": request.query_name,
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
                table_name=request.query_name,
                record_id=None,
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
        return SqliteQueryResponse(
            status="ok",
            output=output,
            log={
                "log_id": log_id,
                "request_id": request_id,
                "transaction_id": transaction_id,
            },
        )
    except SqliteQueryError as exc:
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
                table_name=request.query_name,
                record_id=None,
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
        except SqliteQueryError:
            log_session.rollback()
        finally:
            log_session.close()
        raise
    finally:
        engine.dispose()
