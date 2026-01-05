"""
SQL tool script for creating hook_registry_user records.

Purpose
- Register a user hook for command execution.
- Persist hook metadata for runner discovery.

Contract
- Requires payload.record_id (hook_id), payload, and actor_id.
- record_id must be "<hook_id>" and non-empty.
- payload must include: phase, order, script_kind, script_path, entrypoint, enabled.
- Optional payload fields: applies_to, notes, owner_id.
"""

from __future__ import annotations

import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType
from typing import Any

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_string,
    require_bool,
    require_choice,
    require_int,
    require_string,
)
from context_compass.system.ai_restricted._shared.command_results import (
    error_result,
    exception_result,
    ok_result,
    payload_error_result,
)
from context_compass.system.ai_restricted._shared.timeutils import utc_now_iso
from context_compass.system.ai_restricted.database_management.orm_session import (
    sqlite_session,
    user_db_path,
)
from context_compass.system.ai_restricted.database_management.user_orm_models import (
    HookRegistryUser,
)
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)


HOOK_PHASES = ("pre", "activation", "post", "on_error")
SCRIPT_KINDS = ("python",)


def _context_compass_root(repo_root: Path) -> Path:
    """
    Resolve the context_compass system root for hook paths.

    Args:
        repo_root (Path): Repository root path.

    Returns:
        Path: context_compass system root path.
    """

    return repo_root / "context_compass" / "system"


def _resolve_script_path(
    repo_root: Path,
    script_path: str,
    command_name: str,
    hook_id: str,
) -> Path:
    """
    Resolve the hook script path relative to context_compass.

    Args:
        repo_root (Path): Repository root.
        script_path (str): Script path from payload.
        command_name (str): Command name for error context.
        hook_id (str): Hook id for error context.

    Returns:
        Path: Resolved script path.

    Raises:
        PayloadError: If the script path is missing or invalid.
    """

    path = Path(script_path)
    if not path.is_absolute():
        path = _context_compass_root(repo_root) / script_path
    if not path.exists() or not path.is_file():
        raise PayloadError(
            code="script_path_missing",
            details={
                "command_name": command_name,
                "hook_id": hook_id,
                "script_path": script_path,
                "resolved_path": str(path),
            },
        )
    return path


def _load_hook_module(
    path: Path,
    hook_id: str,
    command_name: str,
) -> ModuleType:
    """
    Load a hook module from a file path for validation.

    Args:
        path (Path): Script path to load.
        hook_id (str): Hook id for error context.
        command_name (str): Command name for error context.

    Returns:
        ModuleType: Loaded module instance.

    Raises:
        PayloadError: If the module cannot be loaded.
    """

    module_name = f"cc_hook_validate_{hook_id}"
    spec = spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise PayloadError(
            code="script_path_invalid",
            details={
                "command_name": command_name,
                "hook_id": hook_id,
                "script_path": str(path),
            },
        )
    module = module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        raise PayloadError(
            code="script_import_failed",
            details={
                "command_name": command_name,
                "hook_id": hook_id,
                "script_path": str(path),
                "error": str(exc),
            },
        ) from exc
    return module


def _validate_hook_entrypoint(
    repo_root: Path,
    hook_id: str,
    command_name: str,
    script_kind: str,
    script_path: str,
    entrypoint: str,
) -> None:
    """
    Validate the hook script path and entrypoint.

    Args:
        repo_root (Path): Repository root.
        hook_id (str): Hook id for error context.
        command_name (str): Command name for error context.
        script_kind (str): Script kind (python).
        script_path (str): Script path from payload.
        entrypoint (str): Entrypoint function name.

    Returns:
        None: Raises on validation failures.

    Raises:
        PayloadError: If the script path or entrypoint is invalid.
    """

    if script_kind != "python":
        raise PayloadError(
            code="script_kind_invalid",
            details={
                "command_name": command_name,
                "hook_id": hook_id,
                "script_kind": script_kind,
            },
        )
    resolved_path = _resolve_script_path(repo_root, script_path, command_name, hook_id)
    module = _load_hook_module(resolved_path, hook_id, command_name)
    entry = getattr(module, entrypoint, None)
    if entry is None:
        raise PayloadError(
            code="entrypoint_missing",
            details={
                "command_name": command_name,
                "hook_id": hook_id,
                "script_path": str(resolved_path),
                "entrypoint": entrypoint,
            },
        )
    if not callable(entry):
        raise PayloadError(
            code="entrypoint_invalid",
            details={
                "command_name": command_name,
                "hook_id": hook_id,
                "script_path": str(resolved_path),
                "entrypoint": entrypoint,
            },
        )


def _parse_record_id(record_id: str, command_name: str) -> str:
    """
    Parse the record_id into a hook id.

    Args:
        record_id (str): Record id string in "<hook_id>" form.
        command_name (str): Command name for error context.

    Returns:
        str: Parsed hook id.

    Raises:
        PayloadError: If record_id is invalid.
    """

    if not record_id.strip():
        raise PayloadError(
            code="record_id_invalid",
            details={
                "command_name": command_name,
                "record_id": record_id,
                "expected": "non-empty record_id",
            },
        )
    return record_id


def _record_id(hook_id: str) -> str:
    """
    Build a canonical record_id for a hook registry entry.

    Args:
        hook_id (str): Hook id primary key.

    Returns:
        str: Canonical record_id string.
    """

    return hook_id


def _normalize_applies_to(value: Any, command_name: str) -> str | None:
    """
    Normalize applies_to selectors into a JSON string.

    Args:
        value (Any): Raw applies_to value.
        command_name (str): Command name for error context.

    Returns:
        str | None: Minified JSON string or None when not provided.

    Raises:
        PayloadError: If applies_to is invalid.
    """

    if value is None:
        return None
    if not isinstance(value, dict):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": "applies_to",
                "expected": "object",
                "payload_type": type(value).__name__,
            },
        )
    normalized: dict[str, list[str]] = {}
    for key in ("command_names", "categories", "tags"):
        items = value.get(key)
        if items is None:
            continue
        if not isinstance(items, list) or not items or not all(
            isinstance(item, str) and item.strip() for item in items
        ):
            raise PayloadError(
                code="payload_value_error",
                details={
                    "command_name": command_name,
                    "field": f"applies_to.{key}",
                    "expected": "non-empty list of strings",
                },
            )
        normalized[key] = items
    if not normalized:
        return None
    return json.dumps(normalized, separators=(",", ":"))


def _require_payload_hook_id(
    raw_payload: dict,
    hook_id_value: str,
    command_name: str,
) -> None:
    """
    Ensure payload.hook_id matches the record_id, if supplied.

    Args:
        raw_payload (dict): Parsed payload object.
        hook_id_value (str): Parsed hook_id from record_id.
        command_name (str): Command name for error context.

    Raises:
        PayloadError: If payload.hook_id conflicts with record_id.
    """

    payload_hook_id = raw_payload.get("hook_id")
    if payload_hook_id is None:
        return
    if not isinstance(payload_hook_id, str):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": "hook_id",
                "expected": "string",
                "payload_type": type(payload_hook_id).__name__,
            },
        )
    if payload_hook_id != hook_id_value:
        raise PayloadError(
            code="payload_value_error",
            details={
                "command_name": command_name,
                "field": "hook_id",
                "expected": hook_id_value,
                "actual": payload_hook_id,
            },
        )


def _record_to_dict(row: HookRegistryUser) -> dict:
    """
    Convert a hook registry ORM row into a dictionary.

    Args:
        row (HookRegistryUser): ORM row instance.

    Returns:
        dict: Serialized hook registry payload.
    """

    record_id = _record_id(row.hook_id)
    return {
        "record_id": record_id,
        "hook_id": row.hook_id,
        "phase": row.phase,
        "order": row.order,
        "script_kind": row.script_kind,
        "script_path": row.script_path,
        "entrypoint": row.entrypoint,
        "applies_to_json": row.applies_to_json,
        "enabled": row.enabled,
        "notes": row.notes,
        "owner_id": row.owner_id,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Create a hook_registry_user record.

    Args:
        payload (dict): Command payload containing payload.record_id and hook data.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing the created hook registry record.

    Raises:
        None: All errors are returned as CommandResult payloads.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        raw_payload = payload.get("payload")
        if not isinstance(raw_payload, dict):
            raise PayloadError(
                code="payload_invalid",
                details={
                    "command_name": command_name,
                    "field": "payload",
                    "expected": "object",
                    "payload_type": type(raw_payload).__name__,
                },
            )
        record_id = require_string(raw_payload, "record_id", command_name)
        actor_id = require_string(payload, "actor_id", command_name)
        hook_id_value = _parse_record_id(record_id, command_name)
        _require_payload_hook_id(raw_payload, hook_id_value, command_name)
        phase = require_choice(raw_payload, "phase", command_name, HOOK_PHASES)
        order = require_int(raw_payload, "order", command_name)
        script_kind = require_choice(
            raw_payload, "script_kind", command_name, SCRIPT_KINDS
        )
        script_path = require_string(raw_payload, "script_path", command_name)
        entrypoint = require_string(raw_payload, "entrypoint", command_name)
        enabled = require_bool(raw_payload, "enabled", command_name)
        notes = optional_string(raw_payload, "notes", command_name=command_name)
        owner_id = optional_string(raw_payload, "owner_id", command_name=command_name)
        applies_to_json = _normalize_applies_to(
            raw_payload.get("applies_to"), command_name
        )
        _validate_hook_entrypoint(
            repo_root,
            hook_id_value,
            command_name,
            script_kind,
            script_path,
            entrypoint,
        )
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    db_path = user_db_path(repo_root)
    if not db_path.exists():
        return error_result(
            code="db_missing",
            meaning="User database does not exist.",
            details={
                "command_name": command_name,
                "db_path": str(db_path),
            },
        )

    now = utc_now_iso()
    try:
        with sqlite_session(db_path, must_exist=True) as session:
            existing = session.get(HookRegistryUser, hook_id_value)
            if existing is not None:
                return error_result(
                    code="record_exists",
                    meaning="Hook registry record already exists.",
                    details={
                        "command_name": command_name,
                        "record_id": record_id,
                    },
                )
            row = HookRegistryUser(
                hook_id=hook_id_value,
                phase=phase,
                order=order,
                script_kind=script_kind,
                script_path=script_path,
                entrypoint=entrypoint,
                applies_to_json=applies_to_json,
                enabled=enabled,
                notes=notes,
                owner_id=owner_id or actor_id,
                created_at=now,
                updated_at=now,
            )
            session.add(row)
            session.flush()
            record = _record_to_dict(row)
        return ok_result(output={"record": record})
    except Exception as exc:
        return exception_result(command_name, exc)
