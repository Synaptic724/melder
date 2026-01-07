"""
SQLite query script to read context_profiles payloads for a branch.

Purpose
- Load context_profiles payloads using branch_name identifiers.
- Return a complete context_profiles payload reconstructed from relational tables.

Contract
- Requires payload.branch_name.
- Returns record payload and exists flag.
- Errors when the SQLite database is missing.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

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
    ContextProfileItem,
    ContextProfileItemPath,
    ContextProfileItemStalenessReason,
    ContextProfilesCore,
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


def _parse_payload(raw_payload: dict, command_name: str) -> dict[str, str]:
    """
    Parse the branch_name from the payload.

    Args:
        raw_payload (dict): Nested payload dictionary.
        command_name (str): Command name for error context.

    Returns:
        dict[str, str]: Parsed branch_name.

    Raises:
        PayloadError: If branch_name is missing or invalid.
    """

    branch_name = require_string(raw_payload, "branch_name", command_name)
    return {"branch_name": branch_name}


def _default_limits() -> dict[str, int]:
    """
    Return default context profile limits.

    Returns:
        dict[str, int]: Limits payload.
    """

    return {"max_items_per_profile": 25, "max_bytes_per_profile": 120000}


def _default_profiles(now: str, limits: dict[str, int]) -> dict[str, Any]:
    """
    Return a default context_profiles payload.

    Args:
        now (str): Current timestamp.
        limits (dict[str, int]): Limits payload.

    Returns:
        dict[str, Any]: Context profiles payload.
    """

    return {
        "schema_version": 1,
        "updated_at": now,
        "rules_version": "context_profiles@v1",
        "limits": limits,
        "profiles": [],
    }


def _group_paths(rows: Iterable[ContextProfileItemPath]) -> dict[str, list[str]]:
    """
    Group path rows by profile name with ordering.

    Args:
        rows (Iterable[ContextProfileItemPath]): Path rows to group.

    Returns:
        dict[str, list[str]]: Mapping of profile_name to ordered paths.
    """

    grouped: dict[str, list[tuple[int, str]]] = {}
    for row in rows:
        grouped.setdefault(row.profile_name, []).append((row.position, row.path))

    ordered: dict[str, list[str]] = {}
    for profile_name, pairs in grouped.items():
        pairs.sort(key=lambda item: item[0])
        ordered[profile_name] = [value for _, value in pairs]
    return ordered


def _group_reasons(
    rows: Iterable[ContextProfileItemStalenessReason],
) -> dict[str, list[str]]:
    """
    Group staleness reason rows by profile name with ordering.

    Args:
        rows (Iterable[ContextProfileItemStalenessReason]): Reason rows to group.

    Returns:
        dict[str, list[str]]: Mapping of profile_name to ordered reasons.
    """

    grouped: dict[str, list[tuple[int, str]]] = {}
    for row in rows:
        grouped.setdefault(row.profile_name, []).append((row.position, row.reason))

    ordered: dict[str, list[str]] = {}
    for profile_name, pairs in grouped.items():
        pairs.sort(key=lambda item: item[0])
        ordered[profile_name] = [value for _, value in pairs]
    return ordered


def _build_payload(
    core: ContextProfilesCore,
    items: Iterable[ContextProfileItem],
    path_rows: Iterable[ContextProfileItemPath],
    reason_rows: Iterable[ContextProfileItemStalenessReason],
) -> dict[str, Any]:
    """
    Build a context_profiles payload from database rows.

    Args:
        core (ContextProfilesCore): Core ORM row.
        items (Iterable[ContextProfileItem]): Profile item rows.
        path_rows (Iterable[ContextProfileItemPath]): Path rows for profiles.
        reason_rows (Iterable[ContextProfileItemStalenessReason]): Staleness reason rows.

    Returns:
        dict[str, Any]: context_profiles payload.
    """

    paths_by_profile = _group_paths(path_rows)
    reasons_by_profile = _group_reasons(reason_rows)

    profiles: list[dict[str, Any]] = []
    for item in items:
        profile_name = item.profile_name
        profiles.append(
            {
                "name": profile_name,
                "paths": paths_by_profile.get(profile_name, []),
                "score": item.score,
                "grade": item.grade,
                "usage_count": item.usage_count,
                "last_used_at": item.last_used_at,
                "last_review_at": item.last_review_at,
                "last_review_notes": item.last_review_notes,
                "last_reviewed_by": item.last_reviewed_by,
                "review_counts": {
                    "excellent": item.review_count_excellent,
                    "good": item.review_count_good,
                    "ok": item.review_count_ok,
                    "poor": item.review_count_poor,
                    "bad": item.review_count_bad,
                },
                "reason": item.reason,
                "size_bytes": item.size_bytes,
                "freshness_state": item.freshness_state,
                "staleness_reasons": reasons_by_profile.get(profile_name, []),
                "inputs_hash": item.inputs_hash,
                "last_checked_at": item.last_checked_at,
                "updated_at": item.profile_updated_at,
            }
        )

    return {
        "schema_version": core.schema_version,
        "updated_at": core.artifact_updated_at,
        "rules_version": core.rules_version,
        "limits": {
            "max_items_per_profile": core.limits_max_items_per_profile,
            "max_bytes_per_profile": core.limits_max_bytes_per_profile,
        },
        "profiles": profiles,
    }


def _load_profiles(repo_root: Path, branch_name: str, now: str) -> tuple[dict[str, Any], bool]:
    """
    Load a context_profiles payload from SQLite.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        now (str): Timestamp for default payloads.

    Returns:
        tuple[dict[str, Any], bool]: Payload and exists flag.
    """

    db_path = user_db_path(repo_root)
    with sqlite_session(db_path, must_exist=True) as session:
        core = session.get(ContextProfilesCore, branch_name)
        if core is None:
            return _default_profiles(now, _default_limits()), False

        items = (
            session.query(ContextProfileItem)
            .filter_by(branch_name=branch_name)
            .order_by(ContextProfileItem.position, ContextProfileItem.profile_name)
            .all()
        )
        path_rows = (
            session.query(ContextProfileItemPath)
            .filter_by(branch_name=branch_name)
            .order_by(ContextProfileItemPath.profile_name, ContextProfileItemPath.position)
            .all()
        )
        reason_rows = (
            session.query(ContextProfileItemStalenessReason)
            .filter_by(branch_name=branch_name)
            .order_by(
                ContextProfileItemStalenessReason.profile_name,
                ContextProfileItemStalenessReason.position,
            )
            .all()
        )
        payload = _build_payload(core, items, path_rows, reason_rows)
        return payload, True


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Read a context_profiles payload by branch_name.

    Args:
        payload (dict): Command payload containing payload.branch_name.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing context_profiles payload and existence flag.

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
        parsed = _parse_payload(raw_payload, command_name)
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
        now = utc_now_iso()
        record, exists = _load_profiles(repo_root, parsed["branch_name"], now)
        return ok_result(
            output={
                "branch_name": parsed["branch_name"],
                "record": record,
                "exists": exists,
            }
        )
    except Exception as exc:
        return exception_result(command_name, exc)
