"""
SQLite query script to persist architecture_context payloads.

Purpose
- Persist architecture_context or test_architecture_context payloads.
- Return the stored payload after the write.

Contract
- Requires payload.branch_name, payload.kind, payload.context, and payload.exists.
- kind must be architecture_context or test_architecture_context.
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


def _require_context(raw_payload: dict, command_name: str) -> dict:
    """
    Require the architecture context payload object.

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


def _parse_directories(agent_payload: dict) -> list[dict[str, Any]]:
    """
    Parse directory entries from the agent payload.

    Args:
        agent_payload (dict): Agent payload mapping.

    Returns:
        list[dict[str, Any]]: Parsed directory entries.

    Raises:
        ValueError: If directory entries are malformed.

    Contract:
        - Each entry contains a non-empty path string.
        - Summary fields are optional and may be null.
    """

    directories = agent_payload.get("directories", [])
    if directories is None:
        return []
    if not isinstance(directories, list):
        raise ValueError("architecture_context.agent.directories must be a list.")

    parsed: list[dict[str, Any]] = []
    for entry in directories:
        if not isinstance(entry, dict):
            raise ValueError(
                "architecture_context.agent.directories entries must be objects."
            )
        path = entry.get("path")
        if not isinstance(path, str) or not path:
            raise ValueError(
                "architecture_context.agent.directories.path must be a non-empty string."
            )
        parsed.append(
            {
                "path": path,
                "one_liner": _optional_string(
                    entry,
                    "one_liner",
                    "architecture_context.agent.directories.one_liner",
                ),
                "detail": _optional_string(
                    entry,
                    "detail",
                    "architecture_context.agent.directories.detail",
                ),
            }
        )
    return parsed


def _parse_agent_items(agent_payload: dict, key: str) -> list[str]:
    """
    Parse an agent string list for a specific key.

    Args:
        agent_payload (dict): Agent payload mapping.
        key (str): Agent list key (key_flows/boundaries).

    Returns:
        list[str]: Parsed string list for the key.

    Raises:
        ValueError: If the list is malformed.
    """

    label = f"architecture_context.agent.{key}"
    return _string_list(agent_payload, key, label)


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
        - Agent mapping is required by schema.
        - Summary/notes are optional and may be null.
    """

    agent_payload = context_payload.get("agent")
    if agent_payload is None:
        agent_payload = {}
    if not isinstance(agent_payload, dict):
        raise ValueError("architecture_context.agent must be a JSON object.")

    summary_present = "summary" in agent_payload
    summary_payload = agent_payload.get("summary") or {}
    if summary_present and not isinstance(summary_payload, dict):
        raise ValueError("architecture_context.agent.summary must be an object.")

    notes_present = "notes" in agent_payload
    notes_value = agent_payload.get("notes") if notes_present else None
    if notes_present and notes_value is not None and not isinstance(notes_value, str):
        raise ValueError("architecture_context.agent.notes must be a string or null.")

    directories = _parse_directories(agent_payload)
    key_flows = _parse_agent_items(agent_payload, "key_flows")
    boundaries = _parse_agent_items(agent_payload, "boundaries")

    return {
        "summary_present": summary_present,
        "summary_one_liner": _optional_string(
            summary_payload,
            "one_liner",
            "architecture_context.agent.summary.one_liner",
        ),
        "summary_detail": _optional_string(
            summary_payload,
            "detail",
            "architecture_context.agent.summary.detail",
        ),
        "notes_present": notes_present,
        "notes": notes_value,
        "directories": directories,
        "items": {
            "key_flows": key_flows,
            "boundaries": boundaries,
        },
    }


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
        raise ValueError("architecture_context.computed.matrix must be a list.")

    parsed: list[dict[str, Any]] = []
    for entry in matrix:
        if not isinstance(entry, dict):
            raise ValueError("architecture_context.computed.matrix entries must be objects.")
        ctx_path = entry.get("ctx_path")
        if not isinstance(ctx_path, str) or not ctx_path:
            raise ValueError(
                "architecture_context.computed.matrix.ctx_path must be a string."
            )
        parsed.append(
            {
                "ctx_path": ctx_path,
                "ctx_kind": _optional_string(
                    entry,
                    "ctx_kind",
                    "architecture_context.computed.matrix.ctx_kind",
                ),
                "code_hash_sha256": _optional_string(
                    entry,
                    "code_hash_sha256",
                    "architecture_context.computed.matrix.code_hash_sha256",
                ),
                "subtree_hash_sha256": _optional_string(
                    entry,
                    "subtree_hash_sha256",
                    "architecture_context.computed.matrix.subtree_hash_sha256",
                ),
                "ctx_semantic_hash_sha256": _optional_string(
                    entry,
                    "ctx_semantic_hash_sha256",
                    "architecture_context.computed.matrix.ctx_semantic_hash_sha256",
                ),
                "freshness_state": _optional_string(
                    entry,
                    "freshness_state",
                    "architecture_context.computed.matrix.freshness_state",
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

    computed = _require_mapping(
        context_payload, "computed", "architecture_context.computed"
    )
    freshness_state = computed.get("freshness_state")
    if not isinstance(freshness_state, str):
        raise ValueError("architecture_context.computed.freshness_state must be a string.")

    holes_count = computed.get("holes_count")
    if not isinstance(holes_count, int):
        raise ValueError("architecture_context.computed.holes_count must be an integer.")

    holes_ratio = computed.get("holes_ratio")
    if holes_ratio is not None and not isinstance(holes_ratio, (int, float)):
        raise ValueError("architecture_context.computed.holes_ratio must be numeric or null.")

    good_ratio = computed.get("good_ratio")
    if good_ratio is not None and not isinstance(good_ratio, (int, float)):
        raise ValueError("architecture_context.computed.good_ratio must be numeric or null.")

    inputs_hash = _optional_string(
        computed,
        "inputs_hash",
        "architecture_context.computed.inputs_hash",
    )
    last_checked_at = _optional_string(
        computed,
        "last_checked_at",
        "architecture_context.computed.last_checked_at",
    )
    matrix_entries = _parse_matrix_entries(computed)
    staleness_reasons = _string_list(
        computed,
        "staleness_reasons",
        "architecture_context.computed.staleness_reasons",
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
    Parse the full architecture_context payload.

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
        raise ValueError("architecture_context payload kind mismatch.")

    schema_version = context_payload.get("schema_version")
    if not isinstance(schema_version, int) or schema_version < 1:
        raise ValueError("architecture_context.schema_version must be an integer >= 1.")

    agent_payload = _parse_agent_payload(context_payload)
    computed_payload = _parse_computed_payload(context_payload)
    artifact_updated_at = _optional_string(
        context_payload,
        "updated_at",
        "architecture_context.updated_at",
    )

    return {
        "schema_version": schema_version,
        "artifact_updated_at": artifact_updated_at,
        "agent": agent_payload,
        "computed": computed_payload,
    }


def _write_rows(
    repo_root: Path,
    branch_name: str,
    kind: str,
    context_payload: dict,
    actor_id: str,
) -> dict[str, Any]:
    """
    Persist architecture_context rows within a single transaction.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        kind (str): Context kind.
        context_payload (dict): Context payload to write.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        dict[str, Any]: Stored architecture_context payload.

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
        existing = session.get(ArchitectureContext, (branch_name, kind))
        created_at = existing.created_at if existing else now
        created_by = existing.created_by if existing else actor_id

        core = ArchitectureContext(
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

        session.query(ArchitectureContextAgentItem).filter_by(
            branch_name=branch_name, kind=kind
        ).delete()
        session.query(ArchitectureContextAgentDirectory).filter_by(
            branch_name=branch_name, kind=kind
        ).delete()
        session.query(ArchitectureContextAgentSummary).filter_by(
            branch_name=branch_name, kind=kind
        ).delete()
        session.query(ArchitectureContextAgentNotes).filter_by(
            branch_name=branch_name, kind=kind
        ).delete()
        session.query(ArchitectureContextMatrix).filter_by(
            branch_name=branch_name, kind=kind
        ).delete()
        session.query(ArchitectureContextStalenessReason).filter_by(
            branch_name=branch_name, kind=kind
        ).delete()

        agent = parsed["agent"]
        if agent["summary_present"]:
            session.add(
                ArchitectureContextAgentSummary(
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
        if agent["notes_present"]:
            session.add(
                ArchitectureContextAgentNotes(
                    branch_name=branch_name,
                    kind=kind,
                    notes=agent["notes"],
                    created_at=now,
                    created_by=actor_id,
                    updated_at=now,
                    updated_by=actor_id,
                )
            )

        for idx, entry in enumerate(agent["directories"], start=1):
            session.add(
                ArchitectureContextAgentDirectory(
                    branch_name=branch_name,
                    kind=kind,
                    position=idx,
                    path=entry["path"],
                    summary_one_liner=entry["one_liner"],
                    summary_detail=entry["detail"],
                    created_at=now,
                    created_by=actor_id,
                    updated_at=now,
                    updated_by=actor_id,
                )
            )

        for item_type, values in agent["items"].items():
            for idx, value in enumerate(values, start=1):
                session.add(
                    ArchitectureContextAgentItem(
                        branch_name=branch_name,
                        kind=kind,
                        item_type=item_type,
                        position=idx,
                        value=value,
                        created_at=now,
                        created_by=actor_id,
                        updated_at=now,
                        updated_by=actor_id,
                    )
                )

        for idx, entry in enumerate(parsed["computed"]["matrix_entries"], start=1):
            session.add(
                ArchitectureContextMatrix(
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
                ArchitectureContextStalenessReason(
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

        stored_row = session.get(ArchitectureContext, (branch_name, kind))
        if stored_row is None:
            raise ValueError("architecture_context write failed to persist core row.")

    from context_compass.system.ai_restricted.sql_queries.user.read_architecture_context import (
        _read_payload,
    )

    record, _exists = _read_payload(repo_root, branch_name, kind)
    return record


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Persist an architecture_context payload to SQLite.

    Args:
        payload (dict): Command payload containing payload.branch_name/kind/context.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing the stored architecture_context payload.

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
            meaning="Invalid architecture_context payload.",
            details={
                "command_name": command_name,
                "branch_name": branch_name,
                "kind": kind,
                "error": str(exc),
            },
        )
    except Exception as exc:
        return exception_result(command_name, exc)
