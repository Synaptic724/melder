"""
SQLite query script to persist onboarding bundle snapshots atomically.

Purpose
- Store onboarding bundle headers and child rows in one transaction.
- Provide a single entrypoint for bundle snapshot persistence.

Contract
- Requires payload.bundle and payload.bundle_format.
- bundle.files, bundle.missing, and bundle.errors are validated for type safety.
- All onboarding_bundle tables are written in a single transaction.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_string,
    require_choice,
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
    OnboardingBundle,
    OnboardingBundleError,
    OnboardingBundleFile,
    OnboardingBundleMissing,
)
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)


def _payload_keys(payload: Mapping[str, Any]) -> list[str]:
    """
    Return sorted payload keys for error context.

    Args:
        payload (Mapping[str, Any]): Payload mapping to inspect.

    Returns:
        list[str]: Sorted payload keys.
    """

    return sorted(payload.keys())


def _require_payload(payload: Mapping[str, Any], command_name: str) -> dict[str, Any]:
    """
    Require and validate the nested payload object.

    Args:
        payload (Mapping[str, Any]): Command payload containing a nested payload object.
        command_name (str): Command name for error context.

    Returns:
        dict[str, Any]: Nested payload dictionary.

    Raises:
        PayloadError: If the payload is missing or invalid.
    """

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
    return raw_payload


def _require_field(
    payload: Mapping[str, Any],
    field: str,
    expected: str,
    command_name: str,
    context: str,
) -> Any:
    """
    Require a field to exist in a nested payload.

    Args:
        payload (Mapping[str, Any]): Payload mapping to inspect.
        field (str): Field name to require.
        expected (str): Human-readable expected type description.
        command_name (str): Command name for error context.
        context (str): Context prefix for nested fields.

    Returns:
        Any: Field value from the payload.

    Raises:
        PayloadError: If the field is missing.
    """

    if field not in payload:
        raise PayloadError(
            code="payload_missing",
            details={
                "command_name": command_name,
                "field": f"{context}.{field}",
                "expected": expected,
                "payload_keys": _payload_keys(payload),
            },
        )
    return payload[field]


def _require_mapping(
    payload: Mapping[str, Any],
    field: str,
    command_name: str,
    context: str,
) -> dict[str, Any]:
    """
    Require a mapping value in a nested payload.

    Args:
        payload (Mapping[str, Any]): Payload mapping to inspect.
        field (str): Mapping field name to require.
        command_name (str): Command name for error context.
        context (str): Context prefix for nested fields.

    Returns:
        dict[str, Any]: Mapping value.

    Raises:
        PayloadError: If the value is missing or not a mapping.
    """

    value = _require_field(payload, field, "object", command_name, context)
    if not isinstance(value, dict):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": f"{context}.{field}",
                "expected": "object",
                "actual_type": type(value).__name__,
            },
        )
    return value


def _require_list(
    payload: Mapping[str, Any],
    field: str,
    command_name: str,
    context: str,
) -> list[Any]:
    """
    Require a list value in a nested payload.

    Args:
        payload (Mapping[str, Any]): Payload mapping to inspect.
        field (str): List field name to require.
        command_name (str): Command name for error context.
        context (str): Context prefix for nested fields.

    Returns:
        list[Any]: List value.

    Raises:
        PayloadError: If the value is missing or not a list.
    """

    value = _require_field(payload, field, "list", command_name, context)
    if not isinstance(value, list):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": f"{context}.{field}",
                "expected": "list",
                "actual_type": type(value).__name__,
            },
        )
    return value


def _require_string(
    payload: Mapping[str, Any],
    field: str,
    command_name: str,
    context: str,
) -> str:
    """
    Require a non-empty string value in a nested payload.

    Args:
        payload (Mapping[str, Any]): Payload mapping to inspect.
        field (str): String field name to require.
        command_name (str): Command name for error context.
        context (str): Context prefix for nested fields.

    Returns:
        str: Non-empty string value.

    Raises:
        PayloadError: If the value is missing or invalid.
    """

    value = _require_field(payload, field, "string", command_name, context)
    if not isinstance(value, str) or not value:
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": f"{context}.{field}",
                "expected": "non-empty string",
                "actual_type": type(value).__name__,
            },
        )
    return value


def _parse_files(
    payload: Mapping[str, Any], command_name: str
) -> list[dict[str, str]]:
    """
    Parse and normalize onboarding bundle file entries.

    Args:
        payload (Mapping[str, Any]): Bundle payload mapping.
        command_name (str): Command name for error context.

    Returns:
        list[dict[str, str]]: Normalized file entry mappings.

    Raises:
        PayloadError: If file entries are missing or invalid.
    """

    items = _require_list(payload, "files", command_name, "bundle")
    normalized: list[dict[str, str]] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise PayloadError(
                code="payload_type_error",
                details={
                    "command_name": command_name,
                    "field": f"bundle.files[{index}]",
                    "expected": "object",
                    "actual_type": type(item).__name__,
                },
            )
        path = _require_string(item, "path", command_name, f"bundle.files[{index}]")
        sha256 = _require_string(item, "sha256", command_name, f"bundle.files[{index}]")
        content_value = item.get("content")
        if content_value is None:
            content = ""
        elif not isinstance(content_value, str):
            raise PayloadError(
                code="payload_type_error",
                details={
                    "command_name": command_name,
                    "field": f"bundle.files[{index}].content",
                    "expected": "string",
                    "actual_type": type(content_value).__name__,
                },
            )
        else:
            content = content_value
        normalized.append({"path": path, "sha256": sha256, "content": content})
    return normalized


def _parse_missing(
    payload: Mapping[str, Any], command_name: str
) -> list[str]:
    """
    Parse and normalize missing path entries.

    Args:
        payload (Mapping[str, Any]): Bundle payload mapping.
        command_name (str): Command name for error context.

    Returns:
        list[str]: Normalized missing paths.

    Raises:
        PayloadError: If missing entries are invalid.
    """

    items = _require_list(payload, "missing", command_name, "bundle")
    normalized: list[str] = []
    for index, item in enumerate(items):
        if not isinstance(item, str) or not item:
            raise PayloadError(
                code="payload_type_error",
                details={
                    "command_name": command_name,
                    "field": f"bundle.missing[{index}]",
                    "expected": "non-empty string",
                    "actual_type": type(item).__name__,
                },
            )
        normalized.append(item)
    return normalized


def _parse_errors(
    payload: Mapping[str, Any], command_name: str
) -> list[dict[str, str]]:
    """
    Parse and normalize error entries.

    Args:
        payload (Mapping[str, Any]): Bundle payload mapping.
        command_name (str): Command name for error context.

    Returns:
        list[dict[str, str]]: Normalized error entries.

    Raises:
        PayloadError: If error entries are invalid.
    """

    items = _require_list(payload, "errors", command_name, "bundle")
    normalized: list[dict[str, str]] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise PayloadError(
                code="payload_type_error",
                details={
                    "command_name": command_name,
                    "field": f"bundle.errors[{index}]",
                    "expected": "object",
                    "actual_type": type(item).__name__,
                },
            )
        path = _require_string(item, "path", command_name, f"bundle.errors[{index}]")
        error = _require_string(item, "error", command_name, f"bundle.errors[{index}]")
        normalized.append({"path": path, "error": error})
    return normalized


def _parse_bundle(
    bundle: Mapping[str, Any],
    command_name: str,
) -> dict[str, Any]:
    """
    Parse and validate a bundle payload.

    Args:
        bundle (Mapping[str, Any]): Bundle payload mapping.
        command_name (str): Command name for error context.

    Returns:
        dict[str, Any]: Parsed bundle payload with normalized values.

    Raises:
        PayloadError: If any bundle fields are invalid.
    """

    schema_version = bundle.get("schema_version", 1)
    if not isinstance(schema_version, int) or schema_version < 1:
        raise PayloadError(
            code="payload_value_error",
            details={
                "command_name": command_name,
                "field": "bundle.schema_version",
                "expected": "integer >= 1",
            },
        )
    generated_at = bundle.get("generated_at")
    if generated_at is not None and not isinstance(generated_at, str):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": "bundle.generated_at",
                "expected": "string",
                "actual_type": type(generated_at).__name__,
            },
        )

    files = _parse_files(bundle, command_name)
    missing = _parse_missing(bundle, command_name)
    errors = _parse_errors(bundle, command_name)
    return {
        "schema_version": schema_version,
        "generated_at": generated_at,
        "files": files,
        "missing": missing,
        "errors": errors,
    }


def _bundle_file_rows(
    bundle_id: str,
    files: list[dict[str, str]],
    now: str,
    actor_id: str,
) -> list[OnboardingBundleFile]:
    """
    Build ORM rows for onboarding bundle file entries.

    Args:
        bundle_id (str): Bundle identifier for the snapshot.
        files (list[dict[str, str]]): Normalized file entries.
        now (str): ISO-8601 timestamp for audit fields.
        actor_id (str): Actor identifier for audit fields.

    Returns:
        list[OnboardingBundleFile]: ORM rows for file entries.
    """

    rows: list[OnboardingBundleFile] = []
    for position, item in enumerate(files):
        content = item["content"]
        content_bytes = len(content.encode("utf-8"))
        rows.append(
            OnboardingBundleFile(
                bundle_id=bundle_id,
                position=position,
                path=item["path"],
                sha256=item["sha256"],
                content=content,
                content_bytes=content_bytes,
                created_at=now,
                created_by=actor_id,
                updated_at=now,
                updated_by=actor_id,
            )
        )
    return rows


def _bundle_missing_rows(
    bundle_id: str,
    missing: list[str],
    now: str,
    actor_id: str,
) -> list[OnboardingBundleMissing]:
    """
    Build ORM rows for missing file entries.

    Args:
        bundle_id (str): Bundle identifier for the snapshot.
        missing (list[str]): Missing file paths.
        now (str): ISO-8601 timestamp for audit fields.
        actor_id (str): Actor identifier for audit fields.

    Returns:
        list[OnboardingBundleMissing]: ORM rows for missing entries.
    """

    rows: list[OnboardingBundleMissing] = []
    for position, path in enumerate(missing):
        rows.append(
            OnboardingBundleMissing(
                bundle_id=bundle_id,
                position=position,
                path=path,
                created_at=now,
                created_by=actor_id,
                updated_at=now,
                updated_by=actor_id,
            )
        )
    return rows


def _bundle_error_rows(
    bundle_id: str,
    errors: list[dict[str, str]],
    now: str,
    actor_id: str,
) -> list[OnboardingBundleError]:
    """
    Build ORM rows for bundle error entries.

    Args:
        bundle_id (str): Bundle identifier for the snapshot.
        errors (list[dict[str, str]]): Error entries.
        now (str): ISO-8601 timestamp for audit fields.
        actor_id (str): Actor identifier for audit fields.

    Returns:
        list[OnboardingBundleError]: ORM rows for error entries.
    """

    rows: list[OnboardingBundleError] = []
    for position, item in enumerate(errors):
        rows.append(
            OnboardingBundleError(
                bundle_id=bundle_id,
                position=position,
                path=item["path"],
                error=item["error"],
                created_at=now,
                created_by=actor_id,
                updated_at=now,
                updated_by=actor_id,
            )
        )
    return rows


def _persist_bundle(
    repo_root: Path,
    bundle_format: str,
    bundle: dict[str, Any],
    actor_id: str,
    command_name: str,
) -> CommandResult:
    """
    Persist onboarding bundle rows in a single transaction.

    Args:
        repo_root (Path): Repository root.
        bundle_format (str): Requested output format for the bundle.
        bundle (dict[str, Any]): Normalized bundle payload.
        actor_id (str): Actor identifier for audit logging.
        command_name (str): Command name for error context.

    Returns:
        CommandResult: Result containing the new bundle_id and counts.
    """

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
    bundle_id = uuid4().hex
    generated_at = bundle.get("generated_at") or now
    files = bundle["files"]
    missing = bundle["missing"]
    errors = bundle["errors"]

    bundle_row = OnboardingBundle(
        bundle_id=bundle_id,
        schema_version=bundle["schema_version"],
        bundle_format=bundle_format,
        generated_at=str(generated_at),
        file_count=len(files),
        missing_count=len(missing),
        error_count=len(errors),
        created_at=now,
        created_by=actor_id,
        updated_at=now,
        updated_by=actor_id,
    )
    file_rows = _bundle_file_rows(bundle_id, files, now, actor_id)
    missing_rows = _bundle_missing_rows(bundle_id, missing, now, actor_id)
    error_rows = _bundle_error_rows(bundle_id, errors, now, actor_id)

    try:
        with sqlite_session(db_path, must_exist=True) as session:
            session.add(bundle_row)
            if file_rows:
                session.add_all(file_rows)
            if missing_rows:
                session.add_all(missing_rows)
            if error_rows:
                session.add_all(error_rows)
        return ok_result(
            output={
                "bundle_id": bundle_id,
                "file_count": len(files),
                "missing_count": len(missing),
                "error_count": len(errors),
                "generated_at": generated_at,
            }
        )
    except Exception as exc:
        return exception_result(command_name, exc)


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Persist onboarding bundle payloads using the query API contract.

    Args:
        payload (dict): Command payload containing bundle data.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result describing the persisted bundle.

    Raises:
        None: All errors are returned as CommandResult payloads.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        actor_id = require_string(payload, "actor_id", command_name)
        raw_payload = _require_payload(payload, command_name)
        bundle_format = require_choice(
            raw_payload, "bundle_format", command_name, ["markdown", "json"]
        )
        bundle = _require_mapping(raw_payload, "bundle", command_name, "payload")
        parsed_bundle = _parse_bundle(bundle, command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    return _persist_bundle(
        repo_root=repo_root,
        bundle_format=bundle_format,
        bundle=parsed_bundle,
        actor_id=actor_id,
        command_name=command_name,
    )
