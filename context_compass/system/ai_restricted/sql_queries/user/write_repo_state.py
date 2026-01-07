"""
SQLite query script to write repo_state payloads in one transaction.

Purpose
- Persist repo_state and repo_state_tooling_disabled_features together.
- Provide a query-level write that spans multiple tables.

Contract
- Requires payload.branch_name, payload.repo_state, and payload.exists.
- repo_state must be a JSON object matching repo_state expectations.
- Writes are executed with a single SQLite transaction.
"""

from __future__ import annotations

from pathlib import Path

from context_compass.system.ai_restricted._shared import branch_repo_state_store
from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_string,
    require_bool,
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
    RepoState,
    RepoStateToolingDisabledFeature,
)
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)


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


def _require_repo_state(raw_payload: dict, command_name: str) -> dict:
    """
    Require the repo_state payload object.

    Args:
        raw_payload (dict): Parsed payload object.
        command_name (str): Command name for error context.

    Returns:
        dict: Repo state payload.

    Raises:
        PayloadError: If repo_state is missing or invalid.
    """

    repo_state = raw_payload.get("repo_state")
    if not isinstance(repo_state, dict):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": "repo_state",
                "expected": "object",
                "payload_type": type(repo_state).__name__,
            },
        )
    return repo_state


def _apply_repo_state_fields(row: RepoState, parsed: dict[str, object]) -> None:
    """
    Apply parsed repo_state fields to an ORM row.

    Args:
        row (RepoState): RepoState ORM row to update.
        parsed (dict[str, object]): Parsed repo_state fields.
    """

    row.schema_version = parsed["schema_version"]
    row.repo_id = parsed["repo_id"]
    row.repo_root = parsed["repo_root"]
    row.git_head = parsed["git_head"]
    row.scan_counter = parsed["scan_counter"]
    row.last_scan_id = parsed["last_scan_id"]
    row.last_scan_at = parsed["last_scan_at"]
    row.scanner_version = parsed["scanner_version"]
    row.template_file_ctx_version = parsed["template_file_ctx_version"]
    row.template_dir_ctx_version = parsed["template_dir_ctx_version"]
    row.lifecycle_stage = parsed["lifecycle_stage"]
    row.lifecycle_assessment = parsed["lifecycle_assessment"]
    row.lifecycle_confidence = parsed["lifecycle_confidence"]
    row.lifecycle_assessed_at = parsed["lifecycle_assessed_at"]
    row.tooling_policy_mode = parsed["tooling_policy_mode"]
    row.tooling_policy_notes = parsed["tooling_policy_notes"]
    row.tooling_policy_updated_at = parsed["tooling_policy_updated_at"]
    row.updated_at = parsed["updated_at"]
    row.updated_by = parsed["updated_by"]


def _write_repo_state_rows(
    repo_root: Path,
    branch_name: str,
    repo_state: dict,
    actor_id: str,
) -> dict:
    """
    Persist repo_state and disabled features in one transaction.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        repo_state (dict): Repo state payload to persist.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        dict: Stored repo_state payload.

    Raises:
        FileNotFoundError: If user.db is missing.
        ValueError: If the repo_state payload is invalid.
    """

    if not isinstance(repo_state, dict):
        raise ValueError("repo_state payload must be a JSON object.")

    now = utc_now_iso()
    parsed = branch_repo_state_store._parse_repo_state_payload(
        repo_state, repo_root, now, actor_id
    )

    db_path = user_db_path(repo_root)
    if not db_path.exists():
        raise FileNotFoundError(f"User database not found: {db_path}")

    with sqlite_session(db_path, must_exist=True) as session:
        row = session.get(RepoState, branch_name)
        if row is None:
            row = RepoState(
                branch_name=branch_name,
                created_at=parsed["created_at"],
                created_by=parsed["created_by"],
            )
            session.add(row)
        _apply_repo_state_fields(row, parsed)
        if not row.created_at:
            row.created_at = parsed["created_at"]
        if not row.created_by:
            row.created_by = parsed["created_by"]

        session.query(RepoStateToolingDisabledFeature).filter_by(branch_name=branch_name).delete()
        disabled_rows: list[RepoStateToolingDisabledFeature] = []
        for idx, feature_name in enumerate(parsed["disabled_features"], start=1):
            entry = RepoStateToolingDisabledFeature(
                branch_name=branch_name,
                position=idx,
                feature_name=feature_name,
                created_at=parsed["updated_at"],
                created_by=parsed["updated_by"],
                updated_at=parsed["updated_at"],
                updated_by=parsed["updated_by"],
            )
            session.add(entry)
            disabled_rows.append(entry)
        session.flush()
        record = branch_repo_state_store._payload_from_rows(repo_root, row, disabled_rows)
    return record


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Write repo_state payloads across repo_state tables.

    Args:
        payload (dict): Command payload containing payload.branch_name/repo_state.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing the stored repo_state payload.

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
        exists = require_bool(raw_payload, "exists", command_name)
        repo_state = _require_repo_state(raw_payload, command_name)
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

    _ = exists
    try:
        record = _write_repo_state_rows(repo_root, branch_name, repo_state, actor_id)
        return ok_result(
            output={
                "branch_name": branch_name,
                "record": record,
                "exists": True,
            }
        )
    except ValueError as exc:
        return error_result(
            code="payload_value_error",
            meaning="Invalid repo_state payload.",
            details={
                "command_name": command_name,
                "branch_name": branch_name,
                "error": str(exc),
            },
        )
    except Exception as exc:
        return exception_result(command_name, exc)
