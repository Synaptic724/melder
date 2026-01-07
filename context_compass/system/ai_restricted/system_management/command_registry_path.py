"""
Resolve a single command's script path from the registry.

Purpose
- Return script path and entrypoint for a registered command.
- Keep path access separate from general command description.
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
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)


SUPPORTED_SCOPES = ("system", "user")
COMMAND_REGISTRY_TABLES = {
    "system": "command_registry_system",
    "user": "command_registry_user",
}
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


def _parse_spec(record: Mapping[str, Any]) -> dict[str, Any] | None:
    """
    Parse the spec_json payload from a registry record.

    Args:
        record (Mapping[str, Any]): Raw registry record.

    Returns:
        dict[str, Any] | None: Parsed spec payload, if available.
    """

    spec_json = record.get("spec_json")
    if not isinstance(spec_json, str) or not spec_json.strip():
        return None
    try:
        return json.loads(spec_json)
    except json.JSONDecodeError:
        return None


def _extract_path_payload(
    record: Mapping[str, Any],
    scope: str,
) -> dict[str, Any]:
    """
    Extract a path response payload from a registry record.

    Args:
        record (Mapping[str, Any]): Raw registry record.

    Returns:
        dict[str, Any]: Extracted path payload.
    """

    entry = record.get("entry") or ""
    entry_path, cli_args = _split_entry(str(entry))
    spec = _parse_spec(record)
    execution = spec.get("execution") if isinstance(spec, dict) else None
    script_path = None
    entrypoint = None
    if isinstance(execution, dict):
        script_path = execution.get("script_path")
        entrypoint = execution.get("entrypoint")
    payload = {
        "command_name": record.get("command_name"),
        "scope": scope,
        "script_path": script_path or entry_path,
        "entrypoint": entrypoint or "run",
        "cli_args": cli_args,
    }
    if entry:
        payload["entry"] = entry
    return payload


def _load_registry_record(
    repo_root: Path,
    scope: str,
    actor_id: str,
    command_name: str,
) -> dict[str, Any] | None:
    """
    Load a single command registry record via sqlite_crud.

    Args:
        repo_root (Path): Repository root.
        scope (str): Registry scope.
        actor_id (str): Actor identifier for CRUD logging.
        command_name (str): Command name to fetch.

    Returns:
        dict[str, Any] | None: Raw registry record payload.

    Raises:
        sqlite_crud.SqliteCrudError: If CRUD execution fails.
    """

    table_name = COMMAND_REGISTRY_TABLES[scope]
    payload = {"record_id": command_name}
    response = sqlite_crud.execute_request(
        repo_root,
        sqlite_crud.SqliteCrudRequest(
            operation="read",
            scope=scope,
            table_name=table_name,
            action=READ_ACTION,
            payload=payload,
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    record = result.get("record")
    return record if isinstance(record, dict) else None


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
    Resolve script path details for a command registry entry.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Minified JSON output containing script path details.
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
        target_command = require_string(payload, "command_name", command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    try:
        ensure_certified(repo_root, payload["agent_id"])
        ensure_feature_enabled(repo_root, "command_registry", "resolve command path")
        ensure_work_mode(repo_root, work_id, "resolve command path")
        ensure_registry_seeded(repo_root)
        table_name = COMMAND_REGISTRY_TABLES[scope]
        record = _load_registry_record(repo_root, scope, actor_id, target_command)
        if record is None:
            return error_result(
                code="record_not_found",
                meaning="Command registry entry not found.",
                details={
                    "command_name": command_name,
                    "target": target_command,
                    "scope": scope,
                },
            )
        payload_value = _extract_path_payload(record, scope)
        payload_json = dump_minified(payload_value)
        return ok_result(
            output={
                "path": payload_value,
                "path_json": payload_json,
            }
        )
    except sqlite_crud.SqliteCrudError as exc:
        return _crud_error(command_name, scope, COMMAND_REGISTRY_TABLES[scope], exc)
    except Exception as exc:
        return exception_result(command_name, exc)


def main() -> None:
    """
    CLI entrypoint for command registry path lookup.
    """

    import argparse

    parser = argparse.ArgumentParser(description="Resolve command registry paths.")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--actor-id", required=True, help="Actor identifier")
    parser.add_argument("--scope", default="user", help="Registry scope (system/user)")
    parser.add_argument("--command-name", required=True, help="Command name to resolve")
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
        command_name="command_registry_path",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("command_registry_path failed: %s", result.errors)
        raise SystemExit(1)
    logger.info(result.output.get("path_json"))


if __name__ == "__main__":
    main()
