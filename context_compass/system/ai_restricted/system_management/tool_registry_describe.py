"""
Describe ToolCommandAPI registry entries with full details.

Purpose
- Provide a command registry inspector that includes script paths.
- Return full registry rows for system and user scopes.

Contract
- Requires agent_id for certification checks.
- Honors work_mode and requires work_id in hard mode.
- Supports user/system scopes or both.
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
)
from context_compass.system.ai_restricted.database_management.system_orm_models import (
    CommandRegistrySystem,
)
from context_compass.system.ai_restricted.database_management.user_orm_models import (
    CommandRegistryUser,
)


Scope = Literal["system", "user"]


def _normalize_scopes(scope: str) -> list[Scope]:
    """
    Normalize a scope selector into a list of registry scopes.

    Args:
        scope (str): Requested scope value (system, user, both).

    Returns:
        list[Scope]: Normalized list of registry scopes to query.

    Raises:
        ValueError: If the scope value is invalid.

    Contract:
        - Accepts system, user, or both (case-insensitive).
        - Returns scopes in deterministic order: system then user.
    """

    normalized = scope.strip().lower()
    if normalized == "system":
        return ["system"]
    if normalized == "user":
        return ["user"]
    if normalized == "both":
        return ["system", "user"]
    raise ValueError("scope must be one of: system, user, both")


def _record_to_dict(record: CommandRegistrySystem | CommandRegistryUser) -> dict:
    """
    Convert a command registry row into a JSON-serializable payload.

    Args:
        record (CommandRegistrySystem | CommandRegistryUser): ORM row instance.

    Returns:
        dict: Serialized registry record with all columns.

    Raises:
        None: This helper does not raise.

    Contract:
        - Includes entry and spec_json values without redaction.
        - Uses command_name as the record identifier.
    """

    return {
        "record_id": record.command_name,
        "command_name": record.command_name,
        "category": record.category,
        "entry": record.entry,
        "summary": record.summary,
        "requires_certification": record.requires_certification,
        "requires_work_id": record.requires_work_id,
        "feature_flag": record.feature_flag,
        "notes": record.notes,
        "spec_json": record.spec_json,
        "registry_schema_version": record.registry_schema_version,
        "registry_generated_at": record.registry_generated_at,
        "registry_updated_at": record.registry_updated_at,
    }


def _fetch_command_registry(
    repo_root: Path,
    scope: Scope,
    command_name: str | None,
) -> list[dict]:
    """
    Fetch command registry records for a specific scope.

    Args:
        repo_root (Path): Repository root path.
        scope (Scope): Registry scope to query.
        command_name (str | None): Optional command_name filter.

    Returns:
        list[dict]: Ordered list of registry records.

    Raises:
        FileNotFoundError: If the scoped database file is missing.
        Exception: Propagates ORM and SQLAlchemy errors.

    Contract:
        - Records are ordered by command_name.
        - When command_name is provided, returns at most one record.
    """

    if scope == "system":
        db_path = system_db_path(repo_root)
        model = CommandRegistrySystem
    else:
        db_path = user_db_path(repo_root)
        model = CommandRegistryUser
    with sqlite_session(db_path, must_exist=True) as session:
        stmt = select(model).order_by(model.command_name)
        if command_name:
            stmt = stmt.where(model.command_name == command_name)
        result = session.execute(stmt)
        return [_record_to_dict(row) for row in result.scalars().all()]


def _build_payload(
    repo_root: Path,
    scopes: Iterable[Scope],
    command_name: str | None,
) -> dict:
    """
    Build a registry description payload for one or more scopes.

    Args:
        repo_root (Path): Repository root path.
        scopes (Iterable[Scope]): Scopes to include in the payload.
        command_name (str | None): Optional command_name filter.

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
        records = _fetch_command_registry(repo_root, scope, command_name)
        payload[scope] = {
            "count": len(records),
            "records": records,
        }
    return payload


def main() -> None:
    """
    CLI entrypoint for tool registry inspection.

    Returns:
        None: Logs the registry payload as minified JSON.

    Raises:
        SystemExit: When validation or registry reads fail.
    """

    parser = argparse.ArgumentParser(
        description="Describe ToolCommandAPI registry entries with full details."
    )
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument(
        "--scope",
        default="both",
        help="Registry scope to inspect (system, user, or both)",
    )
    parser.add_argument(
        "--command-name",
        default=None,
        help="Optional command name to filter",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    try:
        ensure_certified(repo_root, args.agent_id)
        ensure_work_mode(repo_root, args.work_id, "describe tool registry")
        scopes = _normalize_scopes(args.scope)
        payload = _build_payload(repo_root, scopes, args.command_name)
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
        logger.exception("Tool registry describe failed: %s", exc)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
