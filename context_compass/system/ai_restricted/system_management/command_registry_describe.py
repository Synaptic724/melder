"""
Describe command registry entries without exposing script paths.

Purpose
- Return detailed command registry entries as minified JSON.
- Hide script paths by default to avoid leaking implementation details.
- Seed SQLite registries when the system is not yet initialized.

Contract
- Uses sqlite_crud for registry reads (no sqlite_query).
- Requires agent_id and actor_id for auditing.
- Honors feature flags and work_mode guards.
"""

from __future__ import annotations

import json
import logging
import shlex
from pathlib import Path
from typing import Any, Mapping

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_string,
    require_string,
)
from context_compass.system.ai_restricted._shared.command_results import (
    error_result,
    exception_result,
    ok_result,
    payload_error_result,
)
from context_compass.system.ai_restricted._shared.feature_guard import ensure_feature_enabled
from context_compass.system.ai_restricted._shared.json_io import dump_minified
from context_compass.system.ai_restricted._shared.work_mode_guard import ensure_work_mode
from context_compass.system.ai_restricted._shared.certification_guard import ensure_certified
from context_compass.system.ai_restricted.database_management import sqlite_crud
from context_compass.system.ai_restricted.system_management.command_registry_bootstrap import (
    ensure_registry_seeded,
)
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)


SUPPORTED_SCOPES = ("system", "user")
COMMAND_REGISTRY_TABLES = {
    "system": "command_registry_system",
    "user": "command_registry_user",
}
LIST_ACTION = "list_commands"
READ_ACTION = "by_command_name"


def _normalize_scope(scope: str, command_name: str) -> str:
    """
    Normalize and validate a registry scope value.

    Args:
        scope (str): Scope value supplied in the payload.
        command_name (str): Command name for error context.

    Returns:
        str: Normalized scope value.

    Raises:
        PayloadError: If the scope is invalid.
    """

    normalized = scope.strip().lower()
    if normalized in SUPPORTED_SCOPES:
        return normalized
    raise PayloadError(
        code="payload_invalid",
        details={
            "command_name": command_name,
            "field": "scope",
            "expected": f"one of {', '.join(SUPPORTED_SCOPES)}",
            "value": scope,
        },
    )


def _split_entry(entry: str) -> tuple[str | None, str]:
    """
    Split a registry entry into script path and CLI args.

    Args:
        entry (str): Registry entry string.

    Returns:
        tuple[str | None, str]: Script path and CLI argument string.
    """

    if not entry:
        return None, ""
    try:
        parts = shlex.split(entry)
    except ValueError:
        return None, ""
    if not parts:
        return None, ""
    if parts[0] != "python" or len(parts) < 2:
        return None, " ".join(parts[1:])
    script_path = parts[1]
    cli_args = " ".join(parts[2:])
    return script_path, cli_args


def _sanitize_spec(raw_spec: dict[str, Any] | None) -> dict[str, Any] | None:
    """
    Redact execution paths from a registry spec payload.

    Args:
        raw_spec (dict[str, Any] | None): Parsed spec payload.

    Returns:
        dict[str, Any] | None: Sanitized spec payload without script paths.
    """

    if raw_spec is None:
        return None
    sanitized = dict(raw_spec)
    execution = sanitized.get("execution")
    if isinstance(execution, dict):
        redacted = dict(execution)
        redacted.pop("script_path", None)
        redacted["path_hidden"] = True
        sanitized["execution"] = redacted
    return sanitized


def _sanitize_record(record: Mapping[str, Any]) -> dict[str, Any]:
    """
    Convert a raw registry record into a path-safe description payload.

    Args:
        record (Mapping[str, Any]): Raw registry record from SQLite.

    Returns:
        dict[str, Any]: Sanitized record without script path details.
    """

    entry = record.get("entry") or ""
    _, cli_args = _split_entry(str(entry))
    spec_json = record.get("spec_json")
    spec = None
    if isinstance(spec_json, str) and spec_json.strip():
        try:
            spec = json.loads(spec_json)
        except json.JSONDecodeError:
            spec = None
    return {
        "command_name": record.get("command_name"),
        "category": record.get("category"),
        "summary": record.get("summary"),
        "notes": record.get("notes"),
        "requires_certification": bool(record.get("requires_certification")),
        "requires_work_id": bool(record.get("requires_work_id")),
        "feature_flag": record.get("feature_flag"),
        "registry_schema_version": record.get("registry_schema_version"),
        "registry_generated_at": record.get("registry_generated_at"),
        "registry_updated_at": record.get("registry_updated_at"),
        "invocation": {
            "command_name": record.get("command_name"),
            "cli_args": cli_args,
        },
        "spec": _sanitize_spec(spec),
    }


def _load_registry_records(
    repo_root: Path,
    scope: str,
    actor_id: str,
    command_name: str | None,
) -> list[dict[str, Any]]:
    """
    Load command registry records via sqlite_crud.

    Args:
        repo_root (Path): Repository root.
        scope (str): Registry scope.
        actor_id (str): Actor identifier for CRUD logging.
        command_name (str | None): Optional command_name to filter.

    Returns:
        list[dict[str, Any]]: Raw registry record payloads.

    Raises:
        sqlite_crud.SqliteCrudError: If CRUD execution fails.
    """

    table_name = COMMAND_REGISTRY_TABLES[scope]
    if command_name:
        payload = {"record_id": command_name}
        action = READ_ACTION
    else:
        payload = None
        action = LIST_ACTION
    response = sqlite_crud.execute_request(
        repo_root,
        sqlite_crud.SqliteCrudRequest(
            operation="read",
            scope=scope,
            table_name=table_name,
            action=action,
            payload=payload,
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    if command_name:
        record = result.get("record")
        return [record] if isinstance(record, dict) else []
    records = result.get("records", [])
    if isinstance(records, list):
        return [record for record in records if isinstance(record, dict)]
    return []


def _crud_error(
    command_name: str,
    scope: str,
    table_name: str,
    exc: sqlite_crud.SqliteCrudError,
) -> CommandResult:
    """
    Convert a SqliteCrudError into a safe CommandResult.

    Args:
        command_name (str): Command name for context.
        scope (str): Registry scope.
        table_name (str): Registry table name.
        exc (sqlite_crud.SqliteCrudError): CRUD exception to map.

    Returns:
        CommandResult: Error result without script path details.
    """

    return error_result(
        code=exc.code,
        meaning=exc.meaning,
        details={
            "command_name": command_name,
            "scope": scope,
            "table_name": table_name,
        },
    )


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Describe command registry entries without exposing script paths.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Minified JSON output of command registry details.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        scope_value = optional_string(
            payload, "scope", command_name=command_name, default="user"
        )
        scope = _normalize_scope(scope_value or "user", command_name)
        actor_id = require_string(payload, "actor_id", command_name)
        require_string(payload, "agent_id", command_name)
        work_id = optional_string(payload, "work_id", command_name=command_name)
        command_filter = optional_string(
            payload, "command_name", command_name=command_name
        )
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    try:
        ensure_certified(repo_root, payload["agent_id"])
        ensure_feature_enabled(repo_root, "command_registry", "describe command registry")
        ensure_work_mode(repo_root, work_id, "describe command registry")
        ensure_registry_seeded(repo_root)
        table_name = COMMAND_REGISTRY_TABLES[scope]
        records = _load_registry_records(repo_root, scope, actor_id, command_filter)
        sanitized = [_sanitize_record(record) for record in records]
        payload_json = dump_minified(
            {
                "scope": scope,
                "count": len(sanitized),
                "commands": sanitized,
                "paths_hidden": True,
            }
        )
        return ok_result(
            output={
                "scope": scope,
                "count": len(sanitized),
                "commands": sanitized,
                "commands_json": payload_json,
                "paths_hidden": True,
            }
        )
    except sqlite_crud.SqliteCrudError as exc:
        return _crud_error(command_name, scope, COMMAND_REGISTRY_TABLES[scope], exc)
    except Exception as exc:
        return exception_result(command_name, exc)


def main() -> None:
    """
    CLI entrypoint for command registry description.
    """

    import argparse

    parser = argparse.ArgumentParser(description="Describe command registry entries.")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--actor-id", required=True, help="Actor identifier")
    parser.add_argument("--scope", default="user", help="Registry scope (system/user)")
    parser.add_argument("--command-name", default=None, help="Optional command name filter")
    parser.add_argument("--work-id", default=None, help="Work identifier")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "agent_id": args.agent_id,
        "actor_id": args.actor_id,
        "scope": args.scope,
        "command_name": args.command_name,
        "work_id": args.work_id,
    }
    context = ExecutionContext(
        command_name="command_registry_describe",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("command_registry_describe failed: %s", result.errors)
        raise SystemExit(1)
    logger.info(result.output.get("commands_json"))


if __name__ == "__main__":
    main()
