"""
SQL tool script to read repo_state by branch_name.

Purpose
- Load repo_state payloads for a specific branch.
- Provide a deterministic default payload when no record exists.

Contract
- Requires payload.branch_name and actor_id.
- Returns a repo_state payload plus an exists flag.
- Defaults are computed from repo_root when the record is missing.
"""

from __future__ import annotations

from pathlib import Path

from context_compass.system.ai_restricted._shared import branch_repo_state_store
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


def _default_payload(repo_root: Path) -> dict:
    """
    Build the default repo_state payload for a repo root.

    Args:
        repo_root (Path): Repository root.

    Returns:
        dict: Default repo_state payload.
    """

    now = utc_now_iso()
    return branch_repo_state_store.default_repo_state(repo_root, now)


def _payload_from_rows(
    repo_root: Path,
    row: RepoState,
    disabled_rows: list[RepoStateToolingDisabledFeature],
) -> dict:
    """
    Build a repo_state payload from ORM rows.

    Args:
        repo_root (Path): Repository root.
        row (RepoState): RepoState ORM row.
        disabled_rows (list[RepoStateToolingDisabledFeature]): Disabled feature rows.

    Returns:
        dict: Repo state payload.
    """

    repo_root_value = row.repo_root or str(repo_root)
    disabled_features = [entry.feature_name for entry in disabled_rows]
    payload = {
        "schema_version": row.schema_version,
        "repo_id": row.repo_id,
        "repo_root": repo_root_value,
        "git": {"head": row.git_head},
        "scan_counter": row.scan_counter,
        "last_scan_id": row.last_scan_id,
        "last_scan_at": row.last_scan_at,
        "scanner_version": row.scanner_version,
        "template_versions": {
            "file_ctx": row.template_file_ctx_version,
            "dir_ctx": row.template_dir_ctx_version,
        },
        "lifecycle": {
            "stage": row.lifecycle_stage,
            "assessment": row.lifecycle_assessment,
            "confidence": row.lifecycle_confidence,
            "assessed_at": row.lifecycle_assessed_at,
        },
        "tooling_policy": {
            "mode": row.tooling_policy_mode,
            "disabled_features": disabled_features,
            "notes": row.tooling_policy_notes,
            "updated_at": row.tooling_policy_updated_at,
        },
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }
    payload.setdefault("schema_version", 1)
    payload.setdefault("repo_root", str(repo_root))
    payload.setdefault("updated_at", utc_now_iso())
    return payload


def _load_repo_state_rows(repo_root: Path, branch_name: str) -> tuple[dict, bool]:
    """
    Load repo_state payloads directly from SQLite.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.

    Returns:
        tuple[dict, bool]: Repo state payload and exists flag.

    Raises:
        FileNotFoundError: If the user database is missing.
        ValueError: If stored values violate repo_state expectations.
    """

    db_path = user_db_path(repo_root)
    if not db_path.exists():
        raise FileNotFoundError(f"User database not found: {db_path}")

    with sqlite_session(db_path, must_exist=True) as session:
        row = session.get(RepoState, branch_name)
        if row is None:
            return _default_payload(repo_root), False
        disabled_rows = (
            session.query(RepoStateToolingDisabledFeature)
            .filter_by(branch_name=branch_name)
            .order_by(RepoStateToolingDisabledFeature.position)
            .all()
        )
        payload = _payload_from_rows(repo_root, row, disabled_rows)
        return payload, True


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Read a repo_state payload for a branch.

    Args:
        payload (dict): Command payload containing payload.branch_name.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing repo_state and existence metadata.

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
        record, exists = _load_repo_state_rows(repo_root, branch_name)
        return ok_result(
            output={
                "branch_name": branch_name,
                "record": record,
                "exists": exists,
            }
        )
    except ValueError:
        default_payload = _default_payload(repo_root)
        return ok_result(
            output={
                "branch_name": branch_name,
                "record": default_payload,
                "exists": False,
            }
        )
    except Exception as exc:
        return exception_result(command_name, exc)
