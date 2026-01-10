"""
Describe SQLite query registry entries with full details.

Purpose
- Provide a db_query_registry inspector with script paths and metadata.
- Return full registry rows for system, user, and user_defined scopes.

Contract
- Requires agent_id for certification checks.
- Honors work_mode and requires work_id in hard mode.
- Supports scope filters and optional query filters.
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
    DbQueryRegistry as SystemQueryRegistry,
)
from context_compass.system.ai_restricted.database_management.user_orm_models import (
    DbQueryRegistry as UserQueryRegistry,
)
from context_compass.system.ai_restricted.database_management.user_defined_orm_models import (
    DbQueryRegistry as UserDefinedQueryRegistry,
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
    record: SystemQueryRegistry | UserQueryRegistry | UserDefinedQueryRegistry,
) -> dict:
    """
    Convert a db_query_registry row into a JSON-serializable payload.

    Args:
        record (SystemQueryRegistry | UserQueryRegistry | UserDefinedQueryRegistry): ORM row.

    Returns:
        dict: Serialized registry record with all columns.

    Raises:
        None: This helper does not raise.

    Contract:
        - Includes script_path and schema JSON fields without redaction.
        - Uses query_name as the record identifier.
    """

    return {
        "record_id": record.query_name,
        "query_name": record.query_name,
        "scope": record.scope,
        "script_path": record.script_path,
        "tables_involved_json": record.tables_involved_json,
        "operation_type": record.operation_type,
        "operation_notes": record.operation_notes,
        "schema_ref": record.schema_ref,
        "purpose": record.purpose,
        "notes": record.notes,
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


def _fetch_query_registry(
    repo_root: Path,
    scope: Scope,
    query_name: str | None,
) -> list[dict]:
    """
    Fetch query registry records for a specific scope.

    Args:
        repo_root (Path): Repository root path.
        scope (Scope): Registry scope to query.
        query_name (str | None): Optional query_name filter.

    Returns:
        list[dict]: Ordered list of registry records.

    Raises:
        FileNotFoundError: If the scoped database file is missing.
        Exception: Propagates ORM and SQLAlchemy errors.

    Contract:
        - Records are ordered by query_name.
        - When query_name is provided, returns at most one record.
    """

    if scope == "system":
        db_path = system_db_path(repo_root)
        model = SystemQueryRegistry
    elif scope == "user":
        db_path = user_db_path(repo_root)
        model = UserQueryRegistry
    else:
        db_path = user_defined_db_path(repo_root)
        model = UserDefinedQueryRegistry
    with sqlite_session(db_path, must_exist=True) as session:
        stmt = select(model).order_by(model.query_name)
        if query_name:
            stmt = stmt.where(model.query_name == query_name)
        result = session.execute(stmt)
        return [_record_to_dict(row) for row in result.scalars().all()]


def _build_payload(
    repo_root: Path,
    scopes: Iterable[Scope],
    query_name: str | None,
) -> dict:
    """
    Build a query registry payload for one or more scopes.

    Args:
        repo_root (Path): Repository root path.
        scopes (Iterable[Scope]): Scopes to include in the payload.
        query_name (str | None): Optional query_name filter.

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
        records = _fetch_query_registry(repo_root, scope, query_name)
        payload[scope] = {
            "count": len(records),
            "records": records,
        }
    return payload


def main() -> None:
    """
    CLI entrypoint for db_query_registry inspection.

    Returns:
        None: Logs the registry payload as minified JSON.

    Raises:
        SystemExit: When validation or registry reads fail.
    """

    parser = argparse.ArgumentParser(
        description="Describe SQLite query registry entries with full details."
    )
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument(
        "--scope",
        default="all",
        help="Registry scope to inspect (system, user, user_defined, or all)",
    )
    parser.add_argument("--query-name", default=None, help="Optional query_name filter")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    try:
        ensure_certified(repo_root, args.agent_id)
        ensure_work_mode(repo_root, args.work_id, "describe SQL query registry")
        scopes = _normalize_scopes(args.scope)
        payload = _build_payload(repo_root, scopes, args.query_name)
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
        logger.exception("SQL query registry describe failed: %s", exc)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
