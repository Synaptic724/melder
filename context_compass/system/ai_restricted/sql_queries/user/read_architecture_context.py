"""
SQLite query script to read architecture_context payloads.

Purpose
- Load architecture_context or test_architecture_context payloads by kind.
- Return a complete payload reconstructed from relational tables.

Contract
- Requires payload.branch_name and payload.kind.
- kind must be architecture_context or test_architecture_context.
- Returns record payload and exists flag.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from context_compass.system.ai_restricted._shared import architecture_contexts
from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_string,
    require_choice,
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
    ArchitectureContext,
    ArchitectureContextAgentDirectory,
    ArchitectureContextAgentItem,
    ArchitectureContextAgentNotes,
    ArchitectureContextAgentSummary,
    ArchitectureContextMatrix,
    ArchitectureContextStalenessReason,
)
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)


ALLOWED_KINDS = ("architecture_context", "test_architecture_context")


def _require_payload(payload: dict, command_name: str) -> dict:
    """
    Require and validate the nested payload object.

    Args:
        payload (dict): Command payload containing a nested payload object.
        command_name (str): Command name for error context.

    Returns:
        dict: Nested payload dictionary.

    Raises:
        PayloadError: If the payload is missing or invalid.

    Contract:
        - Always returns a dict when validation succeeds.
        - Does not mutate the input payload.
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


def _items_by_type(rows: Iterable[ArchitectureContextAgentItem]) -> dict[str, list[str]]:
    """
    Group agent item rows by item_type with position ordering.

    Args:
        rows (Iterable[ArchitectureContextAgentItem]): Rows with item_type, position, value.

    Returns:
        dict[str, list[str]]: Mapping of item_type to ordered values.

    Contract:
        - Output lists preserve the stored position ordering.
        - Unknown item_type values are passed through as-is.
    """

    grouped: dict[str, list[tuple[int, str]]] = {}
    for row in rows:
        grouped.setdefault(row.item_type, []).append((row.position, row.value))
    ordered: dict[str, list[str]] = {}
    for item_type, pairs in grouped.items():
        pairs.sort(key=lambda item: item[0])
        ordered[item_type] = [value for _, value in pairs]
    return ordered


def _directory_payloads(
    directory_rows: Iterable[ArchitectureContextAgentDirectory],
) -> list[dict[str, Any]]:
    """
    Build directory payload entries from stored rows.

    Args:
        directory_rows (Iterable[ArchitectureContextAgentDirectory]): Directory rows.

    Returns:
        list[dict[str, Any]]: Directory payload entries.

    Contract:
        - Each entry includes path, one_liner, and detail keys.
        - Ordering follows the stored position values.
    """

    payloads: list[dict[str, Any]] = []
    for row in directory_rows:
        payloads.append(
            {
                "path": row.path,
                "one_liner": row.summary_one_liner,
                "detail": row.summary_detail,
            }
        )
    return payloads


def _agent_payload(
    summary: ArchitectureContextAgentSummary | None,
    notes: ArchitectureContextAgentNotes | None,
    directory_rows: Iterable[ArchitectureContextAgentDirectory],
    item_rows: Iterable[ArchitectureContextAgentItem],
) -> dict[str, Any]:
    """
    Build the agent payload block for architecture_context.

    Args:
        summary (ArchitectureContextAgentSummary | None): Summary row if present.
        notes (ArchitectureContextAgentNotes | None): Notes row if present.
        directory_rows (Iterable[ArchitectureContextAgentDirectory]): Directory rows.
        item_rows (Iterable[ArchitectureContextAgentItem]): Agent item rows.

    Returns:
        dict[str, Any]: Agent payload mapping.

    Contract:
        - Includes summary/notes only when stored rows exist.
        - Always includes directories as a list (possibly empty).
    """

    agent_payload: dict[str, Any] = {}
    if summary is not None:
        agent_payload["summary"] = {
            "one_liner": summary.one_liner,
            "detail": summary.detail,
        }
    if notes is not None:
        agent_payload["notes"] = notes.notes

    directories = _directory_payloads(directory_rows)
    agent_payload["directories"] = directories

    items = _items_by_type(item_rows)
    if "key_flows" in items:
        agent_payload["key_flows"] = items["key_flows"]
    if "boundaries" in items:
        agent_payload["boundaries"] = items["boundaries"]
    return agent_payload


def _build_payload(
    row: ArchitectureContext,
    summary: ArchitectureContextAgentSummary | None,
    notes: ArchitectureContextAgentNotes | None,
    directory_rows: list[ArchitectureContextAgentDirectory],
    item_rows: list[ArchitectureContextAgentItem],
    matrix_rows: list[ArchitectureContextMatrix],
    reason_rows: list[ArchitectureContextStalenessReason],
) -> dict[str, Any]:
    """
    Build an architecture_context payload from database rows.

    Args:
        row (ArchitectureContext): Core architecture_context row.
        summary (ArchitectureContextAgentSummary | None): Agent summary row.
        notes (ArchitectureContextAgentNotes | None): Agent notes row.
        directory_rows (list[ArchitectureContextAgentDirectory]): Directory rows.
        item_rows (list[ArchitectureContextAgentItem]): Agent item rows.
        matrix_rows (list[ArchitectureContextMatrix]): Matrix rows.
        reason_rows (list[ArchitectureContextStalenessReason]): Staleness reason rows.

    Returns:
        dict[str, Any]: architecture_context payload.

    Contract:
        - Computed block mirrors stored computed fields and child tables.
        - Agent block mirrors stored summary, notes, directories, and items.
    """

    agent_payload = _agent_payload(summary, notes, directory_rows, item_rows)
    payload = {
        "schema_version": row.schema_version,
        "kind": row.kind,
        "updated_at": row.artifact_updated_at,
        "agent": agent_payload,
        "computed": {
            "freshness_state": row.freshness_state,
            "holes_count": row.holes_count,
            "holes_ratio": row.holes_ratio,
            "good_ratio": row.good_ratio,
            "inputs_hash": row.inputs_hash,
            "last_checked_at": row.last_checked_at,
            "matrix": [
                {
                    "ctx_path": entry.ctx_path,
                    "ctx_kind": entry.ctx_kind,
                    "code_hash_sha256": entry.code_hash_sha256,
                    "subtree_hash_sha256": entry.subtree_hash_sha256,
                    "ctx_semantic_hash_sha256": entry.ctx_semantic_hash_sha256,
                    "freshness_state": entry.freshness_state,
                }
                for entry in matrix_rows
            ],
            "staleness_reasons": [entry.reason for entry in reason_rows],
        },
    }
    if payload.get("updated_at") is None:
        payload["updated_at"] = utc_now_iso()
    if payload.get("agent") is None:
        payload["agent"] = {}
    return payload


def _read_payload(
    repo_root: Path,
    branch_name: str,
    kind: str,
) -> tuple[dict[str, Any], bool]:
    """
    Read an architecture_context payload from SQLite.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        kind (str): Context kind identifier.

    Returns:
        tuple[dict[str, Any], bool]: Payload and existence flag.

    Raises:
        FileNotFoundError: If user.db is missing.

    Contract:
        - Returns default payload when no record exists.
        - Uses relational tables as the source of truth.
    """

    db_path = user_db_path(repo_root)
    if not db_path.exists():
        raise FileNotFoundError(f"User database not found: {db_path}")

    with sqlite_session(db_path, must_exist=True) as session:
        row = session.get(ArchitectureContext, (branch_name, kind))
        if row is None:
            payload = architecture_contexts.default_architecture_context(
                kind, utc_now_iso()
            )
            return payload, False

        summary = session.get(ArchitectureContextAgentSummary, (branch_name, kind))
        notes = session.get(ArchitectureContextAgentNotes, (branch_name, kind))
        directories = (
            session.query(ArchitectureContextAgentDirectory)
            .filter_by(branch_name=branch_name, kind=kind)
            .order_by(ArchitectureContextAgentDirectory.position)
            .all()
        )
        items = (
            session.query(ArchitectureContextAgentItem)
            .filter_by(branch_name=branch_name, kind=kind)
            .order_by(
                ArchitectureContextAgentItem.item_type,
                ArchitectureContextAgentItem.position,
            )
            .all()
        )
        matrix_rows = (
            session.query(ArchitectureContextMatrix)
            .filter_by(branch_name=branch_name, kind=kind)
            .order_by(ArchitectureContextMatrix.position)
            .all()
        )
        reason_rows = (
            session.query(ArchitectureContextStalenessReason)
            .filter_by(branch_name=branch_name, kind=kind)
            .order_by(ArchitectureContextStalenessReason.position)
            .all()
        )
        payload = _build_payload(
            row,
            summary,
            notes,
            directories,
            items,
            matrix_rows,
            reason_rows,
        )
        return payload, True


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Read an architecture_context payload by kind.

    Args:
        payload (dict): Command payload containing payload.branch_name/kind.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing architecture_context payload and existence flag.

    Raises:
        None: All errors are returned as CommandResult payloads.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        require_string(payload, "actor_id", command_name)
        raw_payload = _require_payload(payload, command_name)
        branch_name = require_string(raw_payload, "branch_name", command_name)
        kind = require_choice(raw_payload, "kind", command_name, ALLOWED_KINDS)
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

    try:
        record, exists = _read_payload(repo_root, branch_name, kind)
        return ok_result(
            output={
                "branch_name": branch_name,
                "kind": kind,
                "record": record,
                "exists": exists,
            }
        )
    except Exception as exc:
        return exception_result(command_name, exc)
