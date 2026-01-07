"""
Command wrapper for SQLite CRUD operations.

Purpose
- Expose SQLite CRUD operations through the command runner contract.
- Validate payloads, enforce guardrails, and translate CRUD errors into CommandResult output.

Contract
- Payloads are JSON-serializable kwargs with explicit CRUD parameters.
- actor_id is required and must match the executing agent_id.
- All CRUD execution is delegated to sqlite_crud.execute_request.
- action is required and selects the script within the operation folder.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any

from context_compass.system.ai_restricted.database_management import sqlite_crud
from context_compass.system.ai_restricted._shared.certification_guard import ensure_certified
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
from context_compass.system.ai_restricted._shared.work_mode_guard import ensure_work_mode
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)


def _parse_payload_json(raw: str, command_name: str) -> dict[str, Any]:
    """
    Parse a JSON payload string into a dict.

    Args:
        raw (str): Raw JSON string to parse.
        command_name (str): Command name for error context.

    Returns:
        dict[str, Any]: Parsed JSON object.

    Raises:
        PayloadError: If the JSON is invalid or not an object.
    """

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PayloadError(
            code="payload_json_invalid",
            details={
                "command_name": command_name,
                "error": str(exc),
                "payload_preview": raw[:200],
            },
        ) from exc
    if not isinstance(payload, dict):
        raise PayloadError(
            code="payload_json_invalid",
            details={
                "command_name": command_name,
                "payload_type": type(payload).__name__,
                "expected": "object",
            },
        )
    return payload


def _normalize_payload(
    payload_value: object | None,
    payload_json: str | None,
    command_name: str,
) -> dict[str, Any] | None:
    """
    Normalize payload inputs into a JSON object or None.

    Args:
        payload_value (object | None): Payload value supplied in the kwargs.
        payload_json (str | None): Optional JSON payload string.
        command_name (str): Command name for error context.

    Returns:
        dict[str, Any] | None: Normalized payload dictionary or None.

    Raises:
        PayloadError: If payload inputs conflict or are not valid JSON objects.
    """

    if payload_value is not None and payload_json is not None:
        raise PayloadError(
            code="payload_conflict",
            details={
                "command_name": command_name,
                "message": "Provide either payload or payload_json, not both.",
            },
        )
    if payload_value is None and payload_json is None:
        return None
    if payload_json is not None:
        return _parse_payload_json(payload_json, command_name)
    if isinstance(payload_value, dict):
        return payload_value
    if isinstance(payload_value, str):
        return _parse_payload_json(payload_value, command_name)
    raise PayloadError(
        code="payload_invalid",
        details={
            "command_name": command_name,
            "payload_type": type(payload_value).__name__,
            "expected": "object",
        },
    )


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Execute a SQLite CRUD operation with command runner guards.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result payload containing CRUD output and log metadata.

    Raises:
        None: All errors are returned as CommandResult payloads.

    Contract:
        - Enforces certification and work mode guards.
        - actor_id must match ctx.agent_id.
        - action is required and selects the script to execute.
        - Payload conflicts or invalid JSON yield payload_error_result.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        agent_id = require_string(payload, "agent_id", command_name)
        work_id = optional_string(payload, "work_id", command_name=command_name)
        operation = require_string(payload, "operation", command_name)
        scope = require_string(payload, "scope", command_name)
        table_name = require_string(payload, "table_name", command_name)
        action = require_string(payload, "action", command_name)
        actor_id = require_string(payload, "actor_id", command_name)
        request_id = optional_string(payload, "request_id", command_name=command_name)
        transaction_id = optional_string(
            payload, "transaction_id", command_name=command_name
        )
        payload_json = optional_string(payload, "payload_json", command_name=command_name)
        payload_value = payload.get("payload")
        normalized_payload = _normalize_payload(payload_value, payload_json, command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    if ctx.agent_id and actor_id != ctx.agent_id:
        return error_result(
            code="actor_mismatch",
            meaning="actor_id must match the executing agent_id.",
            details={
                "command_name": command_name,
                "agent_id": ctx.agent_id,
                "actor_id": actor_id,
            },
        )

    try:
        ensure_certified(repo_root, agent_id)
        ensure_work_mode(repo_root, work_id, "execute sqlite_crud")
        request = sqlite_crud.SqliteCrudRequest(
            operation=operation,
            scope=scope,
            table_name=table_name,
            action=action,
            payload=normalized_payload,
            actor_id=actor_id,
            request_id=request_id,
            transaction_id=transaction_id,
        )
        response = sqlite_crud.execute_request(repo_root, request)
        return ok_result(
            output={
                "result": response.output,
                "log": response.log,
            }
        )
    except sqlite_crud.SqliteCrudError as exc:
        details = {
            "command_name": command_name,
            "operation": operation,
            "scope": scope,
            "table_name": table_name,
            "action": action,
            "actor_id": actor_id,
        }
        details.update(exc.details)
        return error_result(code=exc.code, meaning=exc.meaning, details=details)
    except Exception as exc:
        return exception_result(command_name, exc)


def _build_parser() -> argparse.ArgumentParser:
    """
    Build the CLI argument parser for sqlite_crud.

    Returns:
        argparse.ArgumentParser: Configured parser instance.

    Contract:
        - Uses explicit args for CRUD parameters.
        - Accepts JSON payload via --payload-json.
    """

    parser = argparse.ArgumentParser(
        description="Execute SQLite CRUD operations via registry enforcement."
    )
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument(
        "--operation",
        required=True,
        choices=sqlite_crud.SUPPORTED_OPERATIONS,
        help="CRUD operation to execute",
    )
    parser.add_argument(
        "--action",
        required=True,
        help="Script action name within the operation folder",
    )
    parser.add_argument(
        "--scope",
        required=True,
        choices=sqlite_crud.SUPPORTED_SCOPES,
        help="Target database scope",
    )
    parser.add_argument("--table-name", required=True, help="Registered table name")
    parser.add_argument("--payload-json", default=None, help="JSON payload for create/update")
    parser.add_argument("--actor-id", required=True, help="Actor identifier for audit")
    parser.add_argument("--request-id", default=None, help="Optional request identifier")
    parser.add_argument(
        "--transaction-id", default=None, help="Optional transaction identifier"
    )
    return parser


def main() -> None:
    """
    CLI entrypoint for SQLite CRUD operations.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """

    parser = _build_parser()
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "agent_id": args.agent_id,
        "work_id": args.work_id,
        "operation": args.operation,
        "action": args.action,
        "scope": args.scope,
        "table_name": args.table_name,
        "payload_json": args.payload_json,
        "actor_id": args.actor_id,
        "request_id": args.request_id,
        "transaction_id": args.transaction_id,
    }
    context = ExecutionContext(
        command_name="sqlite_crud",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("sqlite_crud failed: %s", result.errors)
        raise SystemExit(1)
    logger.info("sqlite_crud completed: %s", result.output.get("result"))


if __name__ == "__main__":
    main()
