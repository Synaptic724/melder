"""
Describe SQLite CRUD action registry entries with full details.

Purpose
- Provide a db_action_registry inspector with script paths and metadata.
- Return full registry rows for system, user, and user_defined scopes.

Contract
- Requires agent_id for certification checks.
- Honors work_mode and requires work_id in hard mode.
- Supports scope filters and optional action filters.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Iterable, Literal

from sqlalchemy import select

from context_compass.system.ai_restricted._shared.certification_guard import ensure_certified
from context_compass.system.ai_restricted._shared.json_io import dump_minified
from context_compass.system.ai_restricted._shared.work_mode_guard import WorkModeError, ensure_work_mode
from context_compass.system.ai_restricted.database_management.orm_session import (
    sqlite_session,
    system_db_path,
    user_db_path,
    user_defined_db_path,
)
from context_compass.system.ai_restricted.database_management.system_orm_models import (
    DbActionRegistry as SystemActionRegistry,
)
from context_compass.system.ai_restricted.database_management.user_orm_models import (
    DbActionRegistry as UserActionRegistry,
)
from context_compass.system.ai_restricted.database_management.user_defined_orm_models import (
    DbActionRegistry as UserDefinedActionRegistry,
)


Scope = Literal["system", "user", "user_defined"]


def _normalize_scopes(scope: str) -> list[Scope]:
    """
    Normalize a scope selector into a list of registry scopes.

    Args:
        scope (str): Requested scope value (system, user, user_defined, all).

    Returns:
        list[Scope]: Normalized list of registry scopes to query.

    Raises:
        ValueError: If the scope value is invalid.

    Contract:
        - Accepts system, user, user_defined, or all (case-insensitive).
        - Returns scopes in deterministic order: system, user, user_defined.
    """

    normalized = scope.strip().lower()
    if normalized == "system":
        return ["system"]
    if normalized == "user":
        return ["user"]
    if normalized == "user_defined":
        return ["user_defined"]
    if normalized == "all":
        return ["system", "user", "user_defined"]
    raise ValueError("scope must be one of: system, user, user_defined, all")


def _record_to_dict(
    record: SystemActionRegistry | UserActionRegistry | UserDefinedActionRegistry,
) -> dict:
    """
    Convert a db_action_registry row into a JSON-serializable payload.

    Args:
        record (SystemActionRegistry | UserActionRegistry | UserDefinedActionRegistry): ORM row.

    Returns:
        dict: Serialized registry record with all columns.

    Raises:
        None: This helper does not raise.

    Contract:
        - Includes script_path and schema JSON fields without redaction.
        - Uses the composite key fields as record_id components.
    """

    return {
        "record_id": {
            "scope": record.scope,
            "table_name": record.table_name,
            "operation": record.operation,
            "action": record.action,
        },
        "scope": record.scope,
        "table_name": record.table_name,
        "operation": record.operation,
        "action": record.action,
        "script_path": record.script_path,
        "purpose": record.purpose,
        "operation_notes": record.operation_notes,
        "payload_schema_json": record.payload_schema_json,
        "output_schema_json": record.output_schema_json,
        "examples_json": record.examples_json,
        "requires_actor": record.requires_actor,
        "requires_work_id": record.requires_work_id,
        "enabled": record.enabled,
        "owner_id": record.owner_id,
        "created_at": record.created_at,
        "updated_at": record.updated_at,
    }


def _fetch_action_registry(
    repo_root: Path,
    scope: Scope,
    table_name: str | None,
    operation: str | None,
    action: str | None,
) -> list[dict]:
    """
    Fetch action registry records for a specific scope.

    Args:
        repo_root (Path): Repository root path.
        scope (Scope): Registry scope to query.
        table_name (str | None): Optional table_name filter.
        operation (str | None): Optional operation filter.
        action (str | None): Optional action filter.

    Returns:
        list[dict]: Ordered list of registry records.

    Raises:
        FileNotFoundError: If the scoped database file is missing.
        Exception: Propagates ORM and SQLAlchemy errors.

    Contract:
        - Records are ordered by table_name, operation, then action.
        - Filters are applied only when values are provided.
    """

    if scope == "system":
        db_path = system_db_path(repo_root)
        model = SystemActionRegistry
    elif scope == "user":
        db_path = user_db_path(repo_root)
        model = UserActionRegistry
    else:
        db_path = user_defined_db_path(repo_root)
        model = UserDefinedActionRegistry
    with sqlite_session(db_path, must_exist=True) as session:
        stmt = select(model).order_by(model.table_name, model.operation, model.action)
        if table_name:
            stmt = stmt.where(model.table_name == table_name)
        if operation:
            stmt = stmt.where(model.operation == operation)
        if action:
            stmt = stmt.where(model.action == action)
        result = session.execute(stmt)
        return [_record_to_dict(row) for row in result.scalars().all()]


def _build_payload(
    repo_root: Path,
    scopes: Iterable[Scope],
    table_name: str | None,
    operation: str | None,
    action: str | None,
) -> dict:
    """
    Build an action registry payload for one or more scopes.

    Args:
        repo_root (Path): Repository root path.
        scopes (Iterable[Scope]): Scopes to include in the payload.
        table_name (str | None): Optional table_name filter.
        operation (str | None): Optional operation filter.
        action (str | None): Optional action filter.

    Returns:
        dict: Payload keyed by scope with records and counts.

    Raises:
        FileNotFoundError: If a scoped database file is missing.
        Exception: Propagates ORM and SQLAlchemy errors.

    Contract:
        - Each scope key includes records and count fields.
        - Scopes are emitted in the order provided.
    """

    payload: dict[str, dict] = {}
    for scope in scopes:
        records = _fetch_action_registry(repo_root, scope, table_name, operation, action)
        payload[scope] = {
            "count": len(records),
            "records": records,
        }
    return payload


def main() -> None:
    """
    CLI entrypoint for db_action_registry inspection.

    Returns:
        None: Logs the registry payload as minified JSON.

    Raises:
        SystemExit: When validation or registry reads fail.
    """

    parser = argparse.ArgumentParser(
        description="Describe SQLite CRUD action registry entries with full details."
    )
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument(
        "--scope",
        default="all",
        help="Registry scope to inspect (system, user, user_defined, or all)",
    )
    parser.add_argument("--table-name", default=None, help="Optional table_name filter")
    parser.add_argument("--operation", default=None, help="Optional operation filter")
    parser.add_argument("--action", default=None, help="Optional action filter")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    try:
        ensure_certified(repo_root, args.agent_id)
        ensure_work_mode(repo_root, args.work_id, "describe SQL CRUD registry")
        scopes = _normalize_scopes(args.scope)
        payload = _build_payload(
            repo_root,
            scopes,
            args.table_name,
            args.operation,
            args.action,
        )
        logger.info(dump_minified(payload))
    except WorkModeError as exc:
        logger.error(str(exc))
        raise SystemExit(1) from exc
    except FileNotFoundError as exc:
        logger.error("Registry database missing: %s", exc)
        raise SystemExit(1) from exc
    except ValueError as exc:
        logger.error("Invalid input: %s", exc)
        raise SystemExit(1) from exc
    except SystemExit:
        raise
    except Exception as exc:
        logger.exception("SQL CRUD registry describe failed: %s", exc)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
