"""
SQLite query script to persist component_contexts payloads.

Purpose
- Persist component_contexts or test_component_contexts payloads.
- Return the stored payload after the write.

Contract
- Requires payload.branch_name, payload.kind, payload.context, and payload.exists.
- kind must be component_contexts or test_component_contexts.
- Writes are performed within the SQLite transaction scope.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_string,
    require_bool,
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
    ComponentContexts,
    ComponentContextsAgentSummary,
    ComponentContextsComponent,
    ComponentContextsComponentItem,
    ComponentContextsMatrix,
    ComponentContextsStalenessReason,
)
from context_compass.system.ai_restricted._shared.command_contracts import (
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


def _require_context(raw_payload: dict, command_name: str) -> dict:
    """
    Require the component_contexts payload object.

    Args:
        raw_payload (dict): Parsed payload object.
        command_name (str): Command name for error context.

    Returns:
        dict: Context payload.

    Raises:
        PayloadError: If context is missing or invalid.

    Contract:
        - Returns a dict when validation succeeds.
        - Does not mutate the input payload.
    """

    context_payload = raw_payload.get("context")
    if not isinstance(context_payload, dict):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": "context",
                "expected": "object",
                "payload_type": type(context_payload).__name__,
            },
        )
    return context_payload


def _require_mapping(payload: dict, key: str, label: str) -> dict:
    """
    Require a mapping field in a payload.

    Args:
        payload (dict): Payload to inspect.
        key (str): Mapping key to extract.
        label (str): Fully-qualified field label for error messages.

    Returns:
        dict: Mapping value.

    Raises:
        ValueError: If the mapping is missing or invalid.
    """

    value = payload.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object.")
    return value


def _require_string(payload: dict, key: str, label: str) -> str:
    """
    Require a non-empty string field in a payload.

    Args:
        payload (dict): Payload to inspect.
        key (str): Field name to extract.
        label (str): Fully-qualified field label for error messages.

    Returns:
        str: Field value.

    Raises:
        ValueError: If the field is missing or not a non-empty string.
    """

    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string.")
    return value


def _optional_string(payload: dict, key: str, label: str) -> str | None:
    """
    Return an optional string field.

    Args:
        payload (dict): Payload to inspect.
        key (str): Field name to extract.
        label (str): Fully-qualified field label for error messages.

    Returns:
        str | None: Field value if present.

    Raises:
        ValueError: If the field is not a string when provided.
    """

    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a string or null.")
    return value


def _string_list(payload: dict, key: str, label: str) -> list[str]:
    """
    Return a list of strings from a payload field.

    Args:
        payload (dict): Payload to inspect.
        key (str): Field name to extract.
        label (str): Fully-qualified field label for error messages.

    Returns:
        list[str]: List of strings.

    Raises:
        ValueError: If the field is missing or not a list of strings.
    """

    value = payload.get(key, [])
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list.")
    items: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError(f"{label} items must be strings.")
        items.append(item)
    return items


def _component_items(component: dict, key: str) -> list[str]:
    """
    Extract a list of component item strings for a key.

    Args:
        component (dict): Component payload.
        key (str): Item list key.

    Returns:
        list[str]: Component item values.

    Raises:
        ValueError: If the values are not a list of strings.
    """

    label = f"component_contexts.components.{key}"
    return _string_list(component, key, label)


def _parse_agent_payload(context_payload: dict) -> dict[str, Any]:
    """
    Parse the agent payload section.

    Args:
        context_payload (dict): Full context payload.

    Returns:
        dict[str, Any]: Parsed agent payload metadata.

    Raises:
        ValueError: If agent fields are malformed.

    Contract:
        - Summary is optional and may be null.
        - Returns a summary_present flag to control persistence.
    """

    agent_payload = context_payload.get("agent")
    if agent_payload is None:
        agent_payload = {}
    if not isinstance(agent_payload, dict):
        raise ValueError("component_contexts.agent must be a JSON object.")

    summary_present = "summary" in agent_payload
    summary_payload = agent_payload.get("summary") or {}
    if summary_present and not isinstance(summary_payload, dict):
        raise ValueError("component_contexts.agent.summary must be an object.")

    return {
        "summary_present": summary_present,
        "summary_one_liner": _optional_string(
            summary_payload,
            "one_liner",
            "component_contexts.agent.summary.one_liner",
        ),
        "summary_detail": _optional_string(
            summary_payload,
            "detail",
            "component_contexts.agent.summary.detail",
        ),
    }


def _parse_component_entries(context_payload: dict) -> list[dict[str, Any]]:
    """
    Parse component entries from the payload.

    Args:
        context_payload (dict): Full context payload.

    Returns:
        list[dict[str, Any]]: Parsed component entries.

    Raises:
        ValueError: If component entries are malformed.

    Contract:
        - component_id is required for each component.
        - Summary fields are optional and may be null.
    """

    components = context_payload.get("components", [])
    if components is None:
        return []
    if not isinstance(components, list):
        raise ValueError("component_contexts.components must be a list.")

    parsed: list[dict[str, Any]] = []
    for component in components:
        if not isinstance(component, dict):
            raise ValueError("component_contexts.components entries must be objects.")
        component_id = _require_string(
            component, "component_id", "component_contexts.components.component_id"
        )
        summary_payload = component.get("summary") or {}
        if not isinstance(summary_payload, dict):
            raise ValueError("component_contexts.components.summary must be an object.")
        parsed.append(
            {
                "component_id": component_id,
                "name": _optional_string(
                    component,
                    "name",
                    "component_contexts.components.name",
                ),
                "summary_one_liner": _optional_string(
                    summary_payload,
                    "one_liner",
                    "component_contexts.components.summary.one_liner",
                ),
                "summary_detail": _optional_string(
                    summary_payload,
                    "detail",
                    "component_contexts.components.summary.detail",
                ),
                "items": {
                    "responsibilities": _component_items(component, "responsibilities"),
                    "boundaries": _component_items(component, "boundaries"),
                    "key_flows": _component_items(component, "key_flows"),
                    "ctx_paths": _component_items(component, "ctx_paths"),
                },
            }
        )
    return parsed


def _parse_matrix_entries(computed_payload: dict) -> list[dict[str, Any]]:
    """
    Parse matrix entries from the computed payload.

    Args:
        computed_payload (dict): Computed payload mapping.

    Returns:
        list[dict[str, Any]]: Parsed matrix entries.

    Raises:
        ValueError: If matrix entries are malformed.
    """

    matrix = computed_payload.get("matrix", [])
    if matrix is None:
        return []
    if not isinstance(matrix, list):
        raise ValueError("component_contexts.computed.matrix must be a list.")

    parsed: list[dict[str, Any]] = []
    for entry in matrix:
        if not isinstance(entry, dict):
            raise ValueError("component_contexts.computed.matrix entries must be objects.")
        ctx_path = entry.get("ctx_path")
        if not isinstance(ctx_path, str) or not ctx_path:
            raise ValueError("component_contexts.computed.matrix.ctx_path must be a string.")
        parsed.append(
            {
                "ctx_path": ctx_path,
                "ctx_kind": _optional_string(
                    entry,
                    "ctx_kind",
                    "component_contexts.computed.matrix.ctx_kind",
                ),
                "code_hash_sha256": _optional_string(
                    entry,
                    "code_hash_sha256",
                    "component_contexts.computed.matrix.code_hash_sha256",
                ),
                "subtree_hash_sha256": _optional_string(
                    entry,
                    "subtree_hash_sha256",
                    "component_contexts.computed.matrix.subtree_hash_sha256",
                ),
                "ctx_semantic_hash_sha256": _optional_string(
                    entry,
                    "ctx_semantic_hash_sha256",
                    "component_contexts.computed.matrix.ctx_semantic_hash_sha256",
                ),
                "freshness_state": _optional_string(
                    entry,
                    "freshness_state",
                    "component_contexts.computed.matrix.freshness_state",
                ),
            }
        )
    return parsed


def _parse_computed_payload(context_payload: dict) -> dict[str, Any]:
    """
    Parse the computed payload section.

    Args:
        context_payload (dict): Full context payload.

    Returns:
        dict[str, Any]: Parsed computed payload values.

    Raises:
        ValueError: If computed fields are malformed.

    Contract:
        - freshness_state and holes_count are required.
        - Matrix and staleness_reasons default to empty lists.
    """

    computed = _require_mapping(context_payload, "computed", "component_contexts.computed")
    freshness_state = computed.get("freshness_state")
    if not isinstance(freshness_state, str):
        raise ValueError("component_contexts.computed.freshness_state must be a string.")

    holes_count = computed.get("holes_count")
    if not isinstance(holes_count, int):
        raise ValueError("component_contexts.computed.holes_count must be an integer.")

    holes_ratio = computed.get("holes_ratio")
    if holes_ratio is not None and not isinstance(holes_ratio, (int, float)):
        raise ValueError("component_contexts.computed.holes_ratio must be numeric or null.")

    good_ratio = computed.get("good_ratio")
    if good_ratio is not None and not isinstance(good_ratio, (int, float)):
        raise ValueError("component_contexts.computed.good_ratio must be numeric or null.")

    inputs_hash = _optional_string(
        computed,
        "inputs_hash",
        "component_contexts.computed.inputs_hash",
    )
    last_checked_at = _optional_string(
        computed,
        "last_checked_at",
        "component_contexts.computed.last_checked_at",
    )
    matrix_entries = _parse_matrix_entries(computed)
    staleness_reasons = _string_list(
        computed,
        "staleness_reasons",
        "component_contexts.computed.staleness_reasons",
    )

    return {
        "freshness_state": freshness_state,
        "holes_count": holes_count,
        "holes_ratio": float(holes_ratio) if holes_ratio is not None else None,
        "good_ratio": float(good_ratio) if good_ratio is not None else None,
        "inputs_hash": inputs_hash,
        "last_checked_at": last_checked_at,
        "matrix_entries": matrix_entries,
        "staleness_reasons": staleness_reasons,
    }


def _parse_context_payload(kind: str, context_payload: dict) -> dict[str, Any]:
    """
    Parse the full component_contexts payload.

    Args:
        kind (str): Expected context kind.
        context_payload (dict): Payload object to parse.

    Returns:
        dict[str, Any]: Parsed context values for persistence.

    Raises:
        ValueError: If payload fields are malformed.

    Contract:
        - kind must match the payload kind field.
        - schema_version must be an integer >= 1.
    """

    if context_payload.get("kind") != kind:
        raise ValueError("component_contexts payload kind mismatch.")

    schema_version = context_payload.get("schema_version")
    if not isinstance(schema_version, int) or schema_version < 1:
        raise ValueError("component_contexts.schema_version must be an integer >= 1.")

    agent_payload = _parse_agent_payload(context_payload)
    computed_payload = _parse_computed_payload(context_payload)
    components = _parse_component_entries(context_payload)
    artifact_updated_at = _optional_string(
        context_payload,
        "updated_at",
        "component_contexts.updated_at",
    )

    return {
        "schema_version": schema_version,
        "artifact_updated_at": artifact_updated_at,
        "agent": agent_payload,
        "computed": computed_payload,
        "components": components,
    }


def _write_rows(
    repo_root: Path,
    branch_name: str,
    kind: str,
    context_payload: dict,
    actor_id: str,
) -> dict[str, Any]:
    """
    Persist component_contexts rows within a single transaction.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        kind (str): Context kind.
        context_payload (dict): Context payload to write.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        dict[str, Any]: Stored component_contexts payload.

    Raises:
        FileNotFoundError: If user.db is missing.
        ValueError: If payload validation fails.
    """

    parsed = _parse_context_payload(kind, context_payload)
    now = utc_now_iso()
    db_path = user_db_path(repo_root)
    if not db_path.exists():
        raise FileNotFoundError(f"User database not found: {db_path}")

    with sqlite_session(db_path, must_exist=True) as session:
        existing = session.get(ComponentContexts, (branch_name, kind))
        created_at = existing.created_at if existing else now
        created_by = existing.created_by if existing else actor_id

        core = ComponentContexts(
            branch_name=branch_name,
            kind=kind,
            schema_version=parsed["schema_version"],
            artifact_updated_at=parsed["artifact_updated_at"] or now,
            freshness_state=parsed["computed"]["freshness_state"],
            holes_count=parsed["computed"]["holes_count"],
            holes_ratio=parsed["computed"]["holes_ratio"],
            good_ratio=parsed["computed"]["good_ratio"],
            inputs_hash=parsed["computed"]["inputs_hash"],
            last_checked_at=parsed["computed"]["last_checked_at"],
            created_at=created_at,
            created_by=created_by,
            updated_at=now,
            updated_by=actor_id,
        )
        session.merge(core)

        session.query(ComponentContextsComponentItem).filter_by(
            branch_name=branch_name, kind=kind
        ).delete()
        session.query(ComponentContextsAgentSummary).filter_by(
            branch_name=branch_name, kind=kind
        ).delete()
        session.query(ComponentContextsComponent).filter_by(
            branch_name=branch_name, kind=kind
        ).delete()
        session.query(ComponentContextsMatrix).filter_by(
            branch_name=branch_name, kind=kind
        ).delete()
        session.query(ComponentContextsStalenessReason).filter_by(
            branch_name=branch_name, kind=kind
        ).delete()

        for component in parsed["components"]:
            session.add(
                ComponentContextsComponent(
                    branch_name=branch_name,
                    kind=kind,
                    component_id=component["component_id"],
                    name=component["name"],
                    summary_one_liner=component["summary_one_liner"],
                    summary_detail=component["summary_detail"],
                    created_at=now,
                    created_by=actor_id,
                    updated_at=now,
                    updated_by=actor_id,
                )
            )
            for item_type, values in component["items"].items():
                for idx, value in enumerate(values, start=1):
                    session.add(
                        ComponentContextsComponentItem(
                            branch_name=branch_name,
                            kind=kind,
                            component_id=component["component_id"],
                            item_type=item_type,
                            position=idx,
                            value=value,
                            created_at=now,
                            created_by=actor_id,
                            updated_at=now,
                            updated_by=actor_id,
                        )
                    )

        agent = parsed["agent"]
        if agent["summary_present"]:
            session.add(
                ComponentContextsAgentSummary(
                    branch_name=branch_name,
                    kind=kind,
                    one_liner=agent["summary_one_liner"],
                    detail=agent["summary_detail"],
                    created_at=now,
                    created_by=actor_id,
                    updated_at=now,
                    updated_by=actor_id,
                )
            )

        for idx, entry in enumerate(parsed["computed"]["matrix_entries"], start=1):
            session.add(
                ComponentContextsMatrix(
                    branch_name=branch_name,
                    kind=kind,
                    position=idx,
                    ctx_path=entry["ctx_path"],
                    ctx_kind=entry["ctx_kind"],
                    code_hash_sha256=entry["code_hash_sha256"],
                    subtree_hash_sha256=entry["subtree_hash_sha256"],
                    ctx_semantic_hash_sha256=entry["ctx_semantic_hash_sha256"],
                    freshness_state=entry["freshness_state"],
                    created_at=now,
                    created_by=actor_id,
                    updated_at=now,
                    updated_by=actor_id,
                )
            )

        for idx, reason in enumerate(parsed["computed"]["staleness_reasons"], start=1):
            session.add(
                ComponentContextsStalenessReason(
                    branch_name=branch_name,
                    kind=kind,
                    position=idx,
                    reason=reason,
                    created_at=now,
                    created_by=actor_id,
                    updated_at=now,
                    updated_by=actor_id,
                )
            )

        stored_row = session.get(ComponentContexts, (branch_name, kind))
        if stored_row is None:
            raise ValueError("component_contexts write failed to persist core row.")

    from context_compass.system.ai_restricted.sql_queries.user.read_component_contexts import (
        _read_payload,
    )

    record, _exists = _read_payload(repo_root, branch_name, kind)
    return record


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Persist a component_contexts payload to SQLite.

    Args:
        payload (dict): Command payload containing payload.branch_name/kind/context.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing the stored component_contexts payload.

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
        branch_name = require_string(raw_payload, "branch_name", command_name)
        kind = require_choice(raw_payload, "kind", command_name, ALLOWED_KINDS)
        require_bool(raw_payload, "exists", command_name)
        context_payload = _require_context(raw_payload, command_name)
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
        record = _write_rows(repo_root, branch_name, kind, context_payload, actor_id)
        return ok_result(
            output={
                "branch_name": branch_name,
                "kind": kind,
                "record": record,
                "exists": True,
            }
        )
    except ValueError as exc:
        return error_result(
            code="payload_value_error",
            meaning="Invalid component_contexts payload.",
            details={
                "command_name": command_name,
                "branch_name": branch_name,
                "kind": kind,
                "error": str(exc),
            },
        )
    except Exception as exc:
        return exception_result(command_name, exc)
