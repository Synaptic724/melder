"""
SQLite query script to persist scan records in one transaction.

Purpose
- Store a full scan run across scan_registry and related scan_* tables.
- Replace prior scan rows for (branch_name, scan_id) atomically.

Contract
- Requires payload.branch_name, payload.scan_id, payload.scan_record.
- scan_record must match the scan_id argument and existing scan_record schema.
- All related scan_* rows are written in a single transaction.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_string,
    require_string,
)
from context_compass.system.ai_restricted._shared.sql_command_results import (
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
    ScanArchitectureItem,
    ScanArchitectureItemReason,
    ScanDirectoryItem,
    ScanDirectoryItemReason,
    ScanEmittedTask,
    ScanErrorRef,
    ScanFileItem,
    ScanFileItemReason,
    ScanIgnoreConfigCore,
    ScanIgnoreRule,
    ScanRegistry,
)
from context_compass.system.ai_restricted._shared.command_contracts import (
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
    if not isinstance(value, str):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": f"{context}.{field}",
                "expected": "string",
                "actual_type": type(value).__name__,
            },
        )
    if not value.strip():
        raise PayloadError(
            code="payload_empty",
            details={
                "command_name": command_name,
                "field": f"{context}.{field}",
                "expected": "non-empty string",
            },
        )
    return value


def _optional_string(
    payload: Mapping[str, Any],
    field: str,
    command_name: str,
    context: str,
) -> str | None:
    """
    Read an optional string value in a nested payload.

    Args:
        payload (Mapping[str, Any]): Payload mapping to inspect.
        field (str): String field name to read.
        command_name (str): Command name for error context.
        context (str): Context prefix for nested fields.

    Returns:
        str | None: String value or None if missing.

    Raises:
        PayloadError: If the value is not a string or null.
    """

    if field not in payload:
        return None
    value = payload[field]
    if value is None:
        return None
    if not isinstance(value, str):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": f"{context}.{field}",
                "expected": "string",
                "actual_type": type(value).__name__,
            },
        )
    if not value.strip():
        return None
    return value


def _require_int(
    payload: Mapping[str, Any],
    field: str,
    command_name: str,
    context: str,
) -> int:
    """
    Require an integer value in a nested payload.

    Args:
        payload (Mapping[str, Any]): Payload mapping to inspect.
        field (str): Integer field name to require.
        command_name (str): Command name for error context.
        context (str): Context prefix for nested fields.

    Returns:
        int: Integer value.

    Raises:
        PayloadError: If the value is missing or invalid.
    """

    value = _require_field(payload, field, "integer", command_name, context)
    if isinstance(value, bool) or not isinstance(value, int):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": f"{context}.{field}",
                "expected": "integer",
                "actual_type": type(value).__name__,
            },
        )
    return value


def _require_string_list(
    payload: Mapping[str, Any],
    field: str,
    command_name: str,
    context: str,
) -> list[str]:
    """
    Require a list of strings in a nested payload.

    Args:
        payload (Mapping[str, Any]): Payload mapping to inspect.
        field (str): List field name to require.
        command_name (str): Command name for error context.
        context (str): Context prefix for nested fields.

    Returns:
        list[str]: List of strings.

    Raises:
        PayloadError: If the value is missing or contains non-strings.
    """

    value = _require_list(payload, field, command_name, context)
    if any(not isinstance(item, str) for item in value):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": f"{context}.{field}",
                "expected": "list of strings",
                "actual_type": "list",
            },
        )
    return value


def _require_payload(payload: dict, command_name: str) -> dict[str, Any]:
    """
    Require and validate the nested payload object.

    Args:
        payload (dict): Command payload containing a nested payload object.
        command_name (str): Command name for error context.

    Returns:
        dict[str, Any]: Nested payload dictionary.

    Raises:
        PayloadError: If the nested payload is missing or invalid.
    """

    raw_payload = payload.get("payload")
    if not isinstance(raw_payload, dict):
        raise PayloadError(
            code="payload_invalid",
            details={
                "command_name": command_name,
                "field": "payload",
                "expected": "object",
                "actual_type": type(raw_payload).__name__,
            },
        )
    return raw_payload


def _require_scan_record(
    raw_payload: Mapping[str, Any], command_name: str
) -> dict[str, Any]:
    """
    Require and validate the scan_record object.

    Args:
        raw_payload (Mapping[str, Any]): Nested payload dictionary.
        command_name (str): Command name for error context.

    Returns:
        dict[str, Any]: scan_record payload dictionary.

    Raises:
        PayloadError: If scan_record is missing or invalid.
    """

    scan_record = raw_payload.get("scan_record")
    if not isinstance(scan_record, dict):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": "payload.scan_record",
                "expected": "object",
                "actual_type": type(scan_record).__name__,
            },
        )
    return scan_record


def _parse_summary(summary: Mapping[str, Any], command_name: str) -> dict[str, int]:
    """
    Parse the summary block of a scan_record payload.

    Args:
        summary (Mapping[str, Any]): Summary payload mapping.
        command_name (str): Command name for error context.

    Returns:
        dict[str, int]: Parsed summary values.
    """

    context = "scan_record.summary"
    files_scanned = _require_int(summary, "files_scanned", command_name, context)
    dirs_scanned = _require_int(summary, "dirs_scanned", command_name, context)
    tasks_emitted = _require_int(summary, "tasks_emitted", command_name, context)
    missing = _require_int(summary, "missing", command_name, context)
    stale = _require_int(summary, "stale", command_name, context)
    needs_review = _require_int(summary, "needs_review", command_name, context)
    blocked = _require_int(summary, "blocked", command_name, context)

    files_skipped = _require_mapping(summary, "files_skipped", command_name, context)
    files_skipped_init = _require_int(
        files_skipped, "init", command_name, f"{context}.files_skipped"
    )
    files_skipped_excluded = _require_int(
        files_skipped, "excluded", command_name, f"{context}.files_skipped"
    )
    files_skipped_unknown = _require_int(
        files_skipped, "unknown", command_name, f"{context}.files_skipped"
    )

    return {
        "files_scanned": files_scanned,
        "dirs_scanned": dirs_scanned,
        "tasks_emitted": tasks_emitted,
        "missing": missing,
        "stale": stale,
        "needs_review": needs_review,
        "blocked": blocked,
        "files_skipped_init": files_skipped_init,
        "files_skipped_excluded": files_skipped_excluded,
        "files_skipped_unknown": files_skipped_unknown,
    }


def _parse_ignore_config(
    ignore_config: Mapping[str, Any],
    command_name: str,
) -> dict[str, Any]:
    """
    Parse the effective ignore config block.

    Args:
        ignore_config (Mapping[str, Any]): Ignore config payload mapping.
        command_name (str): Command name for error context.

    Returns:
        dict[str, Any]: Parsed ignore config values.

    Raises:
        PayloadError: If ignore config schema_version is invalid.
    """

    context = "scan_record.effective_ignore_config"
    schema_version = ignore_config.get("schema_version")
    if not isinstance(schema_version, int) or schema_version < 1:
        raise PayloadError(
            code="payload_value_error",
            details={
                "command_name": command_name,
                "field": f"{context}.schema_version",
                "expected": "integer >= 1",
                "actual": schema_version,
            },
        )
    include_globs = _require_string_list(ignore_config, "include_globs", command_name, context)
    exclude_globs = _require_string_list(ignore_config, "exclude_globs", command_name, context)
    include_dirs = _require_string_list(ignore_config, "include_dirs", command_name, context)
    exclude_dirs = _require_string_list(ignore_config, "exclude_dirs", command_name, context)
    code_extensions = _require_string_list(ignore_config, "code_extensions", command_name, context)

    return {
        "schema_version": schema_version,
        "include_globs": include_globs,
        "exclude_globs": exclude_globs,
        "include_dirs": include_dirs,
        "exclude_dirs": exclude_dirs,
        "code_extensions": code_extensions,
    }


def _parse_scan_lists(
    scan_record: Mapping[str, Any],
    command_name: str,
) -> dict[str, Any]:
    """
    Parse list-based scan_record sections.

    Args:
        scan_record (Mapping[str, Any]): Scan record payload mapping.
        command_name (str): Command name for error context.

    Returns:
        dict[str, Any]: Parsed list sections for files, dirs, and refs.
    """

    context = "scan_record"
    file_entries = _require_list(scan_record, "files", command_name, context)
    dir_entries = _require_list(scan_record, "directories", command_name, context)
    architecture_entries = scan_record.get("architecture_contexts", [])
    if not isinstance(architecture_entries, list):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": "scan_record.architecture_contexts",
                "expected": "list",
                "actual_type": type(architecture_entries).__name__,
            },
        )
    emitted_tasks = scan_record.get("emitted_tasks", [])
    if not isinstance(emitted_tasks, list):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": "scan_record.emitted_tasks",
                "expected": "list",
                "actual_type": type(emitted_tasks).__name__,
            },
        )
    error_refs = scan_record.get("errors", [])
    if not isinstance(error_refs, list):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": "scan_record.errors",
                "expected": "list",
                "actual_type": type(error_refs).__name__,
            },
        )

    return {
        "file_entries": file_entries,
        "dir_entries": dir_entries,
        "architecture_entries": architecture_entries,
        "emitted_tasks": emitted_tasks,
        "error_refs": error_refs,
    }


def _parse_scan_record(
    scan_record: Mapping[str, Any],
    scan_id: str,
    command_name: str,
) -> dict[str, Any]:
    """
    Parse and validate the scan_record payload.

    Args:
        scan_record (Mapping[str, Any]): Scan record payload mapping.
        scan_id (str): Scan identifier from the request.
        command_name (str): Command name for error context.

    Returns:
        dict[str, Any]: Parsed scan record values.
    """

    context = "scan_record"
    scan_id_payload = _require_string(scan_record, "scan_id", command_name, context)
    if scan_id_payload != scan_id:
        raise PayloadError(
            code="payload_value_error",
            details={
                "command_name": command_name,
                "field": "scan_record.scan_id",
                "expected": scan_id,
                "actual": scan_id_payload,
            },
        )
    schema_version = scan_record.get("schema_version")
    if not isinstance(schema_version, int) or schema_version < 1:
        raise PayloadError(
            code="payload_value_error",
            details={
                "command_name": command_name,
                "field": "scan_record.schema_version",
                "expected": "integer >= 1",
                "actual": schema_version,
            },
        )
    scanned_at = _require_string(scan_record, "scanned_at", command_name, context)
    repo_root_value = _require_string(scan_record, "repo_root", command_name, context)
    repo_id = _optional_string(scan_record, "repo_id", command_name, context)
    git_head = _optional_string(scan_record, "git_head", command_name, context)
    scanner_version = _require_string(scan_record, "scanner_version", command_name, context)

    summary = _require_mapping(scan_record, "summary", command_name, context)
    summary_values = _parse_summary(summary, command_name)

    ignore_config = _require_mapping(
        scan_record, "effective_ignore_config", command_name, context
    )
    ignore_values = _parse_ignore_config(ignore_config, command_name)

    list_values = _parse_scan_lists(scan_record, command_name)

    return {
        "scan_id": scan_id_payload,
        "schema_version": schema_version,
        "scanned_at": scanned_at,
        "repo_root": repo_root_value,
        "repo_id": repo_id,
        "git_head": git_head,
        "scanner_version": scanner_version,
        "summary": summary_values,
        "ignore": ignore_values,
        "file_entries": list_values["file_entries"],
        "dir_entries": list_values["dir_entries"],
        "architecture_entries": list_values["architecture_entries"],
        "emitted_tasks": list_values["emitted_tasks"],
        "error_refs": list_values["error_refs"],
    }


def _parse_request(raw_payload: Mapping[str, Any], command_name: str) -> dict[str, Any]:
    """
    Parse the nested query request payload.

    Args:
        raw_payload (Mapping[str, Any]): Nested payload mapping.
        command_name (str): Command name for error context.

    Returns:
        dict[str, Any]: Parsed request values.
    """

    branch_name = require_string(raw_payload, "branch_name", command_name)
    scan_id = require_string(raw_payload, "scan_id", command_name)
    scan_record = _require_scan_record(raw_payload, command_name)
    scan_values = _parse_scan_record(scan_record, scan_id, command_name)
    return {
        "branch_name": branch_name,
        "scan_id": scan_id,
        "scan_record": scan_record,
        "scan_values": scan_values,
    }


def _bulk_add(session: Any, now: str, actor_id: str, rows: list[Any]) -> None:
    """
    Add ORM rows and apply audit fields.

    Args:
        session (Any): SQLAlchemy session.
        now (str): Timestamp for audit columns.
        actor_id (str): Actor identifier for audit columns.
        rows (list[Any]): ORM rows to add.

    Returns:
        None: Rows are added to the session.
    """

    if not rows:
        return
    for row in rows:
        row.created_at = now
        row.created_by = actor_id
        row.updated_at = now
        row.updated_by = actor_id
    session.add_all(rows)


def _build_ignore_rules(
    branch_name: str,
    scan_id: str,
    include_globs: list[str],
    exclude_globs: list[str],
    include_dirs: list[str],
    exclude_dirs: list[str],
    code_extensions: list[str],
) -> list[ScanIgnoreRule]:
    """
    Build ignore rule rows for a scan run.

    Args:
        branch_name (str): Branch identifier.
        scan_id (str): Scan identifier.
        include_globs (list[str]): Include glob rules.
        exclude_globs (list[str]): Exclude glob rules.
        include_dirs (list[str]): Include directory rules.
        exclude_dirs (list[str]): Exclude directory rules.
        code_extensions (list[str]): Code extension rules.

    Returns:
        list[ScanIgnoreRule]: ORM rows in deterministic order.
    """

    rules: list[ScanIgnoreRule] = []
    position = 1
    rule_sets = [
        ("include_glob", include_globs),
        ("exclude_glob", exclude_globs),
        ("include_dir", include_dirs),
        ("exclude_dir", exclude_dirs),
        ("code_extension", code_extensions),
    ]
    for rule_type, values in rule_sets:
        for value in values:
            rules.append(
                ScanIgnoreRule(
                    branch_name=branch_name,
                    scan_id=scan_id,
                    position=position,
                    rule_type=rule_type,
                    rule_value=value,
                    created_at="",
                    created_by="",
                    updated_at="",
                    updated_by="",
                )
            )
            position += 1
    return rules


def _build_file_rows(
    branch_name: str,
    scan_id: str,
    entries: list[Any],
    command_name: str,
) -> tuple[list[ScanFileItem], list[ScanFileItemReason]]:
    """
    Build scan file item rows from payload entries.

    Args:
        branch_name (str): Branch identifier.
        scan_id (str): Scan identifier.
        entries (list[Any]): File entry payloads.
        command_name (str): Command name for error context.

    Returns:
        tuple[list[ScanFileItem], list[ScanFileItemReason]]: ORM rows.

    Raises:
        PayloadError: If file entries are malformed.
    """

    items: list[ScanFileItem] = []
    reasons: list[ScanFileItemReason] = []
    context = "scan_record.files"
    for idx, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            raise PayloadError(
                code="payload_type_error",
                details={
                    "command_name": command_name,
                    "field": context,
                    "expected": "object",
                    "actual_type": type(entry).__name__,
                },
            )
        file_path = _require_string(entry, "path", command_name, context)
        ctx_path = _require_string(entry, "ctx_path", command_name, context)
        state = _require_string(entry, "state", command_name, context)
        reason_values = _require_string_list(entry, "reasons", command_name, context)
        items.append(
            ScanFileItem(
                branch_name=branch_name,
                scan_id=scan_id,
                file_path=file_path,
                ctx_path=ctx_path,
                state=state,
                position=idx,
                created_at="",
                created_by="",
                updated_at="",
                updated_by="",
            )
        )
        for reason_idx, reason in enumerate(reason_values, start=1):
            reasons.append(
                ScanFileItemReason(
                    branch_name=branch_name,
                    scan_id=scan_id,
                    file_path=file_path,
                    position=reason_idx,
                    reason=reason,
                    created_at="",
                    created_by="",
                    updated_at="",
                    updated_by="",
                )
            )
    return items, reasons


def _build_dir_rows(
    branch_name: str,
    scan_id: str,
    entries: list[Any],
    command_name: str,
) -> tuple[list[ScanDirectoryItem], list[ScanDirectoryItemReason]]:
    """
    Build scan directory item rows from payload entries.

    Args:
        branch_name (str): Branch identifier.
        scan_id (str): Scan identifier.
        entries (list[Any]): Directory entry payloads.
        command_name (str): Command name for error context.

    Returns:
        tuple[list[ScanDirectoryItem], list[ScanDirectoryItemReason]]: ORM rows.

    Raises:
        PayloadError: If directory entries are malformed.
    """

    items: list[ScanDirectoryItem] = []
    reasons: list[ScanDirectoryItemReason] = []
    context = "scan_record.directories"
    for idx, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            raise PayloadError(
                code="payload_type_error",
                details={
                    "command_name": command_name,
                    "field": context,
                    "expected": "object",
                    "actual_type": type(entry).__name__,
                },
            )
        dir_path = _require_string(entry, "path", command_name, context)
        ctx_path = _require_string(entry, "ctx_path", command_name, context)
        state = _require_string(entry, "state", command_name, context)
        reason_values = _require_string_list(entry, "reasons", command_name, context)
        items.append(
            ScanDirectoryItem(
                branch_name=branch_name,
                scan_id=scan_id,
                dir_path=dir_path,
                ctx_path=ctx_path,
                state=state,
                position=idx,
                created_at="",
                created_by="",
                updated_at="",
                updated_by="",
            )
        )
        for reason_idx, reason in enumerate(reason_values, start=1):
            reasons.append(
                ScanDirectoryItemReason(
                    branch_name=branch_name,
                    scan_id=scan_id,
                    dir_path=dir_path,
                    position=reason_idx,
                    reason=reason,
                    created_at="",
                    created_by="",
                    updated_at="",
                    updated_by="",
                )
            )
    return items, reasons


def _build_architecture_rows(
    branch_name: str,
    scan_id: str,
    entries: list[Any],
    command_name: str,
) -> tuple[list[ScanArchitectureItem], list[ScanArchitectureItemReason]]:
    """
    Build architecture/component scan rows from payload entries.

    Args:
        branch_name (str): Branch identifier.
        scan_id (str): Scan identifier.
        entries (list[Any]): Architecture entry payloads.
        command_name (str): Command name for error context.

    Returns:
        tuple[list[ScanArchitectureItem], list[ScanArchitectureItemReason]]: ORM rows.

    Raises:
        PayloadError: If entries are malformed.
    """

    items: list[ScanArchitectureItem] = []
    reasons: list[ScanArchitectureItemReason] = []
    context = "scan_record.architecture_contexts"
    for idx, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            raise PayloadError(
                code="payload_type_error",
                details={
                    "command_name": command_name,
                    "field": context,
                    "expected": "object",
                    "actual_type": type(entry).__name__,
                },
            )
        path_value = _require_string(entry, "path", command_name, context)
        kind = _require_string(entry, "kind", command_name, context)
        state = _require_string(entry, "state", command_name, context)
        reason_values = _require_string_list(entry, "reasons", command_name, context)
        items.append(
            ScanArchitectureItem(
                branch_name=branch_name,
                scan_id=scan_id,
                position=idx,
                path=path_value,
                kind=kind,
                state=state,
                created_at="",
                created_by="",
                updated_at="",
                updated_by="",
            )
        )
        for reason_idx, reason in enumerate(reason_values, start=1):
            reasons.append(
                ScanArchitectureItemReason(
                    branch_name=branch_name,
                    scan_id=scan_id,
                    item_position=idx,
                    position=reason_idx,
                    reason=reason,
                    created_at="",
                    created_by="",
                    updated_at="",
                    updated_by="",
                )
            )
    return items, reasons


def _delete_scan_rows(session: Any, branch_name: str, scan_id: str) -> None:
    """
    Delete scan rows for a specific scan run.

    Args:
        session (Any): SQLAlchemy session.
        branch_name (str): Branch identifier.
        scan_id (str): Scan identifier.

    Returns:
        None: Rows are deleted in-place.
    """

    session.query(ScanIgnoreRule).filter_by(branch_name=branch_name, scan_id=scan_id).delete()
    session.query(ScanIgnoreConfigCore).filter_by(branch_name=branch_name, scan_id=scan_id).delete()
    session.query(ScanFileItemReason).filter_by(branch_name=branch_name, scan_id=scan_id).delete()
    session.query(ScanFileItem).filter_by(branch_name=branch_name, scan_id=scan_id).delete()
    session.query(ScanDirectoryItemReason).filter_by(branch_name=branch_name, scan_id=scan_id).delete()
    session.query(ScanDirectoryItem).filter_by(branch_name=branch_name, scan_id=scan_id).delete()
    session.query(ScanArchitectureItemReason).filter_by(branch_name=branch_name, scan_id=scan_id).delete()
    session.query(ScanArchitectureItem).filter_by(branch_name=branch_name, scan_id=scan_id).delete()
    session.query(ScanEmittedTask).filter_by(branch_name=branch_name, scan_id=scan_id).delete()
    session.query(ScanErrorRef).filter_by(branch_name=branch_name, scan_id=scan_id).delete()
    session.query(ScanRegistry).filter_by(branch_name=branch_name, scan_id=scan_id).delete()


def _build_registry_row(
    branch_name: str,
    scan_values: dict[str, Any],
    actor_id: str,
    now: str,
) -> ScanRegistry:
    """
    Build the scan registry ORM row.

    Args:
        branch_name (str): Branch identifier.
        scan_values (dict[str, Any]): Parsed scan record values.
        actor_id (str): Actor identifier for audit logging.
        now (str): Timestamp for audit columns.

    Returns:
        ScanRegistry: ORM row for scan_registry.
    """

    summary = scan_values["summary"]
    return ScanRegistry(
        branch_name=branch_name,
        scan_id=scan_values["scan_id"],
        schema_version=scan_values["schema_version"],
        scanned_at=scan_values["scanned_at"],
        repo_root=scan_values["repo_root"],
        repo_id=scan_values["repo_id"],
        git_head=scan_values["git_head"],
        scanner_version=scan_values["scanner_version"],
        files_scanned=summary["files_scanned"],
        dirs_scanned=summary["dirs_scanned"],
        files_skipped_init=summary["files_skipped_init"],
        files_skipped_excluded=summary["files_skipped_excluded"],
        files_skipped_unknown=summary["files_skipped_unknown"],
        tasks_emitted=summary["tasks_emitted"],
        missing=summary["missing"],
        stale=summary["stale"],
        needs_review=summary["needs_review"],
        blocked=summary["blocked"],
        created_at=now,
        created_by=actor_id,
        updated_at=now,
        updated_by=actor_id,
    )


def _build_ignore_core(
    branch_name: str,
    scan_values: dict[str, Any],
    actor_id: str,
    now: str,
) -> ScanIgnoreConfigCore:
    """
    Build the scan ignore config core row.

    Args:
        branch_name (str): Branch identifier.
        scan_values (dict[str, Any]): Parsed scan record values.
        actor_id (str): Actor identifier for audit logging.
        now (str): Timestamp for audit columns.

    Returns:
        ScanIgnoreConfigCore: ORM row for scan_ignore_config_core.
    """

    ignore_config = scan_values["ignore"]
    return ScanIgnoreConfigCore(
        branch_name=branch_name,
        scan_id=scan_values["scan_id"],
        schema_version=ignore_config["schema_version"],
        created_at=now,
        created_by=actor_id,
        updated_at=now,
        updated_by=actor_id,
    )


def _build_task_rows(
    branch_name: str,
    scan_values: dict[str, Any],
    actor_id: str,
    now: str,
    command_name: str,
) -> list[ScanEmittedTask]:
    """
    Build emitted task rows for the scan run.

    Args:
        branch_name (str): Branch identifier.
        scan_values (dict[str, Any]): Parsed scan record values.
        actor_id (str): Actor identifier for audit logging.
        now (str): Timestamp for audit columns.
        command_name (str): Command name for error context.

    Returns:
        list[ScanEmittedTask]: ORM rows for scan_emitted_tasks.

    Raises:
        PayloadError: If emitted task identifiers are invalid.
    """

    rows: list[ScanEmittedTask] = []
    for idx, value in enumerate(scan_values["emitted_tasks"], start=1):
        rows.append(
            ScanEmittedTask(
                branch_name=branch_name,
                scan_id=scan_values["scan_id"],
                position=idx,
                work_id=_require_string(
                    {"value": value}, "value", command_name, "scan_record.emitted_tasks"
                ),
                created_at=now,
                created_by=actor_id,
                updated_at=now,
                updated_by=actor_id,
            )
        )
    return rows


def _build_error_rows(
    branch_name: str,
    scan_values: dict[str, Any],
    actor_id: str,
    now: str,
    command_name: str,
) -> list[ScanErrorRef]:
    """
    Build error reference rows for the scan run.

    Args:
        branch_name (str): Branch identifier.
        scan_values (dict[str, Any]): Parsed scan record values.
        actor_id (str): Actor identifier for audit logging.
        now (str): Timestamp for audit columns.
        command_name (str): Command name for error context.

    Returns:
        list[ScanErrorRef]: ORM rows for scan_error_refs.

    Raises:
        PayloadError: If error identifiers are invalid.
    """

    rows: list[ScanErrorRef] = []
    for idx, value in enumerate(scan_values["error_refs"], start=1):
        rows.append(
            ScanErrorRef(
                branch_name=branch_name,
                scan_id=scan_values["scan_id"],
                position=idx,
                error_id=_require_string({"value": value}, "value", command_name, "scan_record.errors"),
                created_at=now,
                created_by=actor_id,
                updated_at=now,
                updated_by=actor_id,
            )
        )
    return rows


def _insert_registry(
    session: Any,
    branch_name: str,
    scan_values: dict[str, Any],
    actor_id: str,
    now: str,
) -> dict[str, int]:
    """
    Insert the scan_registry row and return summary values.

    Args:
        session (Any): SQLAlchemy session.
        branch_name (str): Branch identifier.
        scan_values (dict[str, Any]): Parsed scan record values.
        actor_id (str): Actor identifier for audit logging.
        now (str): Timestamp for audit columns.

    Returns:
        dict[str, int]: Summary metrics used for output.
    """

    summary = scan_values["summary"]
    session.add(_build_registry_row(branch_name, scan_values, actor_id, now))
    return summary


def _insert_ignore_config(
    session: Any,
    branch_name: str,
    scan_values: dict[str, Any],
    actor_id: str,
    now: str,
) -> None:
    """
    Insert ignore config core and rule rows.

    Args:
        session (Any): SQLAlchemy session.
        branch_name (str): Branch identifier.
        scan_values (dict[str, Any]): Parsed scan record values.
        actor_id (str): Actor identifier for audit logging.
        now (str): Timestamp for audit columns.

    Returns:
        None: Rows are added to the session.
    """

    ignore_config = scan_values["ignore"]
    session.add(_build_ignore_core(branch_name, scan_values, actor_id, now))
    ignore_rows = _build_ignore_rules(
        branch_name,
        scan_values["scan_id"],
        ignore_config["include_globs"],
        ignore_config["exclude_globs"],
        ignore_config["include_dirs"],
        ignore_config["exclude_dirs"],
        ignore_config["code_extensions"],
    )
    _bulk_add(session, now, actor_id, ignore_rows)


def _insert_file_rows(
    session: Any,
    branch_name: str,
    scan_values: dict[str, Any],
    actor_id: str,
    now: str,
    command_name: str,
) -> None:
    """
    Insert scan file rows and reason rows.

    Args:
        session (Any): SQLAlchemy session.
        branch_name (str): Branch identifier.
        scan_values (dict[str, Any]): Parsed scan record values.
        actor_id (str): Actor identifier for audit logging.
        now (str): Timestamp for audit columns.
        command_name (str): Command name for error context.

    Returns:
        None: Rows are added to the session.
    """

    file_rows, file_reason_rows = _build_file_rows(
        branch_name,
        scan_values["scan_id"],
        scan_values["file_entries"],
        command_name,
    )
    _bulk_add(session, now, actor_id, file_rows)
    _bulk_add(session, now, actor_id, file_reason_rows)


def _insert_dir_rows(
    session: Any,
    branch_name: str,
    scan_values: dict[str, Any],
    actor_id: str,
    now: str,
    command_name: str,
) -> None:
    """
    Insert scan directory rows and reason rows.

    Args:
        session (Any): SQLAlchemy session.
        branch_name (str): Branch identifier.
        scan_values (dict[str, Any]): Parsed scan record values.
        actor_id (str): Actor identifier for audit logging.
        now (str): Timestamp for audit columns.
        command_name (str): Command name for error context.

    Returns:
        None: Rows are added to the session.
    """

    dir_rows, dir_reason_rows = _build_dir_rows(
        branch_name,
        scan_values["scan_id"],
        scan_values["dir_entries"],
        command_name,
    )
    _bulk_add(session, now, actor_id, dir_rows)
    _bulk_add(session, now, actor_id, dir_reason_rows)


def _insert_architecture_rows(
    session: Any,
    branch_name: str,
    scan_values: dict[str, Any],
    actor_id: str,
    now: str,
    command_name: str,
) -> None:
    """
    Insert architecture/context rows and reason rows.

    Args:
        session (Any): SQLAlchemy session.
        branch_name (str): Branch identifier.
        scan_values (dict[str, Any]): Parsed scan record values.
        actor_id (str): Actor identifier for audit logging.
        now (str): Timestamp for audit columns.
        command_name (str): Command name for error context.

    Returns:
        None: Rows are added to the session.
    """

    architecture_rows, architecture_reason_rows = _build_architecture_rows(
        branch_name,
        scan_values["scan_id"],
        scan_values["architecture_entries"],
        command_name,
    )
    _bulk_add(session, now, actor_id, architecture_rows)
    _bulk_add(session, now, actor_id, architecture_reason_rows)


def _insert_task_rows(
    session: Any,
    branch_name: str,
    scan_values: dict[str, Any],
    actor_id: str,
    now: str,
    command_name: str,
) -> None:
    """
    Insert emitted task rows.

    Args:
        session (Any): SQLAlchemy session.
        branch_name (str): Branch identifier.
        scan_values (dict[str, Any]): Parsed scan record values.
        actor_id (str): Actor identifier for audit logging.
        now (str): Timestamp for audit columns.
        command_name (str): Command name for error context.

    Returns:
        None: Rows are added to the session.
    """

    _bulk_add(
        session,
        now,
        actor_id,
        _build_task_rows(branch_name, scan_values, actor_id, now, command_name),
    )


def _insert_error_rows(
    session: Any,
    branch_name: str,
    scan_values: dict[str, Any],
    actor_id: str,
    now: str,
    command_name: str,
) -> None:
    """
    Insert scan error reference rows.

    Args:
        session (Any): SQLAlchemy session.
        branch_name (str): Branch identifier.
        scan_values (dict[str, Any]): Parsed scan record values.
        actor_id (str): Actor identifier for audit logging.
        now (str): Timestamp for audit columns.
        command_name (str): Command name for error context.

    Returns:
        None: Rows are added to the session.
    """

    _bulk_add(
        session,
        now,
        actor_id,
        _build_error_rows(branch_name, scan_values, actor_id, now, command_name),
    )


def _persist_scan_record(
    repo_root: Path,
    *,
    branch_name: str,
    scan_values: dict[str, Any],
    actor_id: str,
    command_name: str,
) -> CommandResult:
    """
    Persist a scan record to SQLite.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        scan_values (dict[str, Any]): Parsed scan record values.
        actor_id (str): Actor identifier for audit logging.
        command_name (str): Command name for error context.

    Returns:
        CommandResult: Result describing the persisted scan record.
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
    try:
        with sqlite_session(db_path, must_exist=True) as session:
            _delete_scan_rows(session, branch_name, scan_values["scan_id"])

            summary = _insert_registry(session, branch_name, scan_values, actor_id, now)
            _insert_ignore_config(session, branch_name, scan_values, actor_id, now)
            _insert_file_rows(session, branch_name, scan_values, actor_id, now, command_name)
            _insert_dir_rows(session, branch_name, scan_values, actor_id, now, command_name)
            _insert_architecture_rows(
                session, branch_name, scan_values, actor_id, now, command_name
            )
            _insert_task_rows(session, branch_name, scan_values, actor_id, now, command_name)
            _insert_error_rows(session, branch_name, scan_values, actor_id, now, command_name)

        return ok_result(
            output={
                "branch_name": branch_name,
                "scan_id": scan_values["scan_id"],
                "files_scanned": summary["files_scanned"],
                "dirs_scanned": summary["dirs_scanned"],
                "tasks_emitted": summary["tasks_emitted"],
                "errors": len(scan_values["error_refs"]),
            }
        )
    except PayloadError as exc:
        return payload_error_result(command_name, exc)
    except Exception as exc:
        return exception_result(command_name, exc)


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Persist a scan record payload using the query API contract.

    Args:
        payload (dict): Command payload containing scan record data.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result describing the persisted scan record.

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
        request_values = _parse_request(raw_payload, command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    return _persist_scan_record(
        repo_root,
        branch_name=request_values["branch_name"],
        scan_values=request_values["scan_values"],
        actor_id=actor_id,
        command_name=command_name,
    )
