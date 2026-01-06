"""
SQLite query script to read component_contexts payloads.

Purpose
- Load component_contexts or test_component_contexts payloads by kind.
- Return a complete payload reconstructed from relational tables.

Contract
- Requires payload.branch_name and payload.kind.
- kind must be component_contexts or test_component_contexts.
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
    ComponentContexts,
    ComponentContextsAgentSummary,
    ComponentContextsComponent,
    ComponentContextsComponentItem,
    ComponentContextsMatrix,
    ComponentContextsStalenessReason,
)
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)


ALLOWED_KINDS = ("component_contexts", "test_component_contexts")


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


def _items_by_type(rows: Iterable[ComponentContextsComponentItem]) -> dict[str, list[str]]:
    """
    Group component item rows by item_type with position ordering.

    Args:
        rows (Iterable[ComponentContextsComponentItem]): Rows with item_type, position, value.

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


def _build_payload(
    session: Any,
    row: ComponentContexts,
) -> dict[str, Any]:
    """
    Build a component_contexts payload from database rows.

    Args:
        session (Any): Active SQLAlchemy session.
        row (ComponentContexts): Core row instance.

    Returns:
        dict[str, Any]: component_contexts payload.

    Contract:
        - Payload is reconstructed from child tables.
        - Item ordering reflects stored positions.
    """

    component_rows = (
        session.query(ComponentContextsComponent)
        .filter_by(branch_name=row.branch_name, kind=row.kind)
        .order_by(ComponentContextsComponent.component_id)
        .all()
    )
    item_rows = (
        session.query(ComponentContextsComponentItem)
        .filter_by(branch_name=row.branch_name, kind=row.kind)
        .order_by(
            ComponentContextsComponentItem.component_id,
            ComponentContextsComponentItem.item_type,
            ComponentContextsComponentItem.position,
        )
        .all()
    )
    items_by_component: dict[str, dict[str, list[str]]] = {}
    for component_id in {item.component_id for item in item_rows}:
        subset = [item for item in item_rows if item.component_id == component_id]
        items_by_component[component_id] = _items_by_type(subset)

    components: list[dict[str, Any]] = []
    for component in component_rows:
        items = items_by_component.get(component.component_id, {})
        components.append(
            {
                "component_id": component.component_id,
                "name": component.name,
                "summary": {
                    "one_liner": component.summary_one_liner,
                    "detail": component.summary_detail,
                },
                "responsibilities": items.get("responsibilities", []),
                "boundaries": items.get("boundaries", []),
                "key_flows": items.get("key_flows", []),
                "ctx_paths": items.get("ctx_paths", []),
            }
        )

    matrix_rows = (
        session.query(ComponentContextsMatrix)
        .filter_by(branch_name=row.branch_name, kind=row.kind)
        .order_by(ComponentContextsMatrix.position)
        .all()
    )
    reason_rows = (
        session.query(ComponentContextsStalenessReason)
        .filter_by(branch_name=row.branch_name, kind=row.kind)
        .order_by(ComponentContextsStalenessReason.position)
        .all()
    )

    summary = session.get(ComponentContextsAgentSummary, (row.branch_name, row.kind))
    agent_payload: dict[str, Any] = {}
    if summary is not None:
        agent_payload["summary"] = {
            "one_liner": summary.one_liner,
            "detail": summary.detail,
        }

    payload = {
        "schema_version": row.schema_version,
        "kind": row.kind,
        "updated_at": row.artifact_updated_at,
        "agent": agent_payload,
        "components": components,
        "computed": {
            "freshness_state": row.freshness_state,
            "holes_count": row.holes_count,
            "holes_ratio": row.holes_ratio,
            "good_ratio": row.good_ratio,
            "inputs_hash": row.inputs_hash,
            "last_checked_at": row.last_checked_at,
            "matrix": [
                {
                    "ctx_path": item.ctx_path,
                    "ctx_kind": item.ctx_kind,
                    "code_hash_sha256": item.code_hash_sha256,
                    "subtree_hash_sha256": item.subtree_hash_sha256,
                    "ctx_semantic_hash_sha256": item.ctx_semantic_hash_sha256,
                    "freshness_state": item.freshness_state,
                }
                for item in matrix_rows
            ],
            "staleness_reasons": [item.reason for item in reason_rows],
        },
    }
    if payload.get("updated_at") is None:
        payload["updated_at"] = utc_now_iso()
    return payload


def _read_payload(
    repo_root: Path,
    branch_name: str,
    kind: str,
) -> tuple[dict[str, Any], bool]:
    """
    Read a component_contexts payload from SQLite.

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
        row = session.get(ComponentContexts, (branch_name, kind))
        if row is None:
            payload = architecture_contexts.default_component_contexts(kind, utc_now_iso())
            return payload, False
        payload = _build_payload(session, row)
        return payload, True


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Read a component_contexts payload by kind.

    Args:
        payload (dict): Command payload containing payload.branch_name/kind.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing component_contexts payload and existence flag.

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
