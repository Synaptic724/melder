"""
SQLite query script to persist context_profiles payloads.

Purpose
- Persist context_profiles payloads for a branch.
- Return the stored payload after the write.

Contract
- Requires payload.branch_name, payload.context_profiles, and payload.exists.
- Writes are performed within the SQLite transaction scope.
- Returns the stored payload after persistence.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_string,
    require_bool,
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
    ContextProfileItem,
    ContextProfileItemPath,
    ContextProfileItemStalenessReason,
    ContextProfilesCore,
)
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)


ALLOWED_GRADES = ("excellent", "good", "ok", "poor", "bad")
ALLOWED_FRESHNESS_STATES = ("fresh", "stale", "needs_review", "blocked")


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


def _require_profiles(raw_payload: dict, command_name: str) -> dict:
    """
    Require the context_profiles payload object.

    Args:
        raw_payload (dict): Parsed payload object.
        command_name (str): Command name for error context.

    Returns:
        dict: Context profiles payload.

    Raises:
        PayloadError: If context_profiles is missing or invalid.

    Contract:
        - context_profiles must be a JSON object.
    """

    profiles_payload = raw_payload.get("context_profiles")
    if not isinstance(profiles_payload, dict):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": "context_profiles",
                "expected": "object",
                "payload_type": type(profiles_payload).__name__,
            },
        )
    return profiles_payload


def _require_mapping(payload: dict, key: str) -> dict:
    """
    Require a mapping field in a payload.

    Args:
        payload (dict): Payload to inspect.
        key (str): Mapping key to extract.

    Returns:
        dict: Mapping value.

    Raises:
        ValueError: If the mapping is missing or invalid.
    """

    value = payload.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"context_profiles.{key} must be a JSON object.")
    return value


def _require_string(payload: dict, key: str) -> str:
    """
    Require a non-empty string field in a payload.

    Args:
        payload (dict): Payload to inspect.
        key (str): Field name to extract.

    Returns:
        str: Field value.

    Raises:
        ValueError: If the field is missing or not a string.
    """

    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"context_profiles.{key} must be a non-empty string.")
    return value


def _optional_string(payload: dict, key: str) -> str | None:
    """
    Return an optional string field.

    Args:
        payload (dict): Payload to inspect.
        key (str): Field name to extract.

    Returns:
        str | None: Field value if present.

    Raises:
        ValueError: If the field is not a string when provided.
    """

    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"context_profiles.{key} must be a string or null.")
    return value


def _require_int(payload: dict, key: str, *, min_value: int | None = None) -> int:
    """
    Require an integer field in a payload.

    Args:
        payload (dict): Payload to inspect.
        key (str): Field name to extract.
        min_value (int | None): Optional minimum value.

    Returns:
        int: Field value.

    Raises:
        ValueError: If the field is missing or not an integer.
    """

    value = payload.get(key)
    if not isinstance(value, int):
        raise ValueError(f"context_profiles.{key} must be an integer.")
    if min_value is not None and value < min_value:
        raise ValueError(f"context_profiles.{key} must be >= {min_value}.")
    return value


def _require_number(payload: dict, key: str) -> float:
    """
    Require a numeric field in a payload.

    Args:
        payload (dict): Payload to inspect.
        key (str): Field name to extract.

    Returns:
        float: Field value.

    Raises:
        ValueError: If the field is missing or not a number.
    """

    value = payload.get(key)
    if not isinstance(value, (int, float)):
        raise ValueError(f"context_profiles.{key} must be a number.")
    return float(value)


def _string_list(payload: dict, key: str) -> list[str]:
    """
    Return a list of strings from a payload field.

    Args:
        payload (dict): Payload to inspect.
        key (str): Field name to extract.

    Returns:
        list[str]: List of strings.

    Raises:
        ValueError: If the field is missing or not a list of strings.
    """

    value = payload.get(key)
    if not isinstance(value, list):
        raise ValueError(f"context_profiles.{key} must be a JSON array.")
    items: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError(f"context_profiles.{key} items must be strings.")
        items.append(item)
    return items


def _require_profiles_list(payload: dict) -> list[dict[str, Any]]:
    """
    Require the profiles list in a payload.

    Args:
        payload (dict): Payload to inspect.

    Returns:
        list[dict[str, Any]]: Profiles list.

    Raises:
        ValueError: If profiles is missing or invalid.
    """

    profiles = payload.get("profiles")
    if not isinstance(profiles, list):
        raise ValueError("context_profiles.profiles must be a JSON array.")
    parsed: list[dict[str, Any]] = []
    for item in profiles:
        if not isinstance(item, dict):
            raise ValueError("context_profiles.profiles entries must be JSON objects.")
        parsed.append(item)
    return parsed


def _validate_grade(value: str) -> str:
    """
    Validate and normalize profile grade values.

    Args:
        value (str): Grade value to validate.

    Returns:
        str: Normalized grade value.

    Raises:
        ValueError: If the grade is invalid.
    """

    normalized = value.strip().lower()
    if normalized not in ALLOWED_GRADES:
        raise ValueError(f"context_profiles.grade must be one of {ALLOWED_GRADES}.")
    return normalized


def _validate_freshness_state(value: str) -> str:
    """
    Validate and normalize freshness state values.

    Args:
        value (str): Freshness state to validate.

    Returns:
        str: Normalized freshness state value.

    Raises:
        ValueError: If the freshness state is invalid.
    """

    normalized = value.strip().lower()
    if normalized not in ALLOWED_FRESHNESS_STATES:
        raise ValueError(
            "context_profiles.freshness_state must be one of "
            f"{ALLOWED_FRESHNESS_STATES}."
        )
    return normalized


def _require_review_counts(payload: dict) -> dict[str, int]:
    """
    Require review_counts mapping with all expected keys.

    Args:
        payload (dict): Profile payload to inspect.

    Returns:
        dict[str, int]: Review count mapping.

    Raises:
        ValueError: If review_counts is missing or invalid.
    """

    value = payload.get("review_counts")
    if not isinstance(value, dict):
        raise ValueError("context_profiles.review_counts must be a JSON object.")
    required = ("excellent", "good", "ok", "poor", "bad")
    counts: dict[str, int] = {}
    for key in required:
        count = value.get(key)
        if not isinstance(count, int):
            raise ValueError(
                "context_profiles.review_counts must include integer entries for "
                f"{required}."
            )
        if count < 0:
            raise ValueError("context_profiles.review_counts values must be >= 0.")
        counts[key] = count
    return counts


def _parse_payload(payload: dict[str, Any], now: str) -> dict[str, Any]:
    """
    Parse a context_profiles payload into normalized values.

    Args:
        payload (dict[str, Any]): Payload to parse.
        now (str): Timestamp to apply for updates.

    Returns:
        dict[str, Any]: Parsed payload data.

    Raises:
        ValueError: If payload validation fails.
    """

    schema_version = payload.get("schema_version")
    if not isinstance(schema_version, int) or schema_version < 1:
        raise ValueError("context_profiles.schema_version must be an integer >= 1.")
    rules_version = payload.get("rules_version")
    if rules_version is not None and not isinstance(rules_version, str):
        raise ValueError("context_profiles.rules_version must be a string or null.")

    limits = _require_mapping(payload, "limits")
    max_items = _require_int(limits, "max_items_per_profile", min_value=1)
    max_bytes = _require_int(limits, "max_bytes_per_profile", min_value=1)

    updated_at = payload.get("updated_at")
    if updated_at is not None and not isinstance(updated_at, str):
        raise ValueError("context_profiles.updated_at must be a string or null.")

    profiles = _require_profiles_list(payload)
    parsed_profiles: list[dict[str, Any]] = []
    seen_names: set[str] = set()

    for index, profile in enumerate(profiles):
        name = _require_string(profile, "name")
        if name in seen_names:
            raise ValueError(f"Duplicate context profile name: {name}")
        seen_names.add(name)

        paths = _string_list(profile, "paths")
        score = _require_number(profile, "score")
        grade = _validate_grade(_require_string(profile, "grade"))
        usage_count = _require_int(profile, "usage_count", min_value=0)
        last_used_at = _optional_string(profile, "last_used_at")
        last_review_at = _optional_string(profile, "last_review_at")
        last_review_notes = _optional_string(profile, "last_review_notes")
        last_reviewed_by = _optional_string(profile, "last_reviewed_by")
        review_counts = _require_review_counts(profile)
        reason = _require_string(profile, "reason")
        size_bytes = _require_int(profile, "size_bytes", min_value=0)
        freshness_state = _validate_freshness_state(
            _require_string(profile, "freshness_state")
        )
        staleness_reasons = _string_list(profile, "staleness_reasons")
        inputs_hash = _optional_string(profile, "inputs_hash")
        last_checked_at = _optional_string(profile, "last_checked_at")
        profile_updated_at = _optional_string(profile, "updated_at")

        parsed_profiles.append(
            {
                "position": index,
                "name": name,
                "paths": paths,
                "score": score,
                "grade": grade,
                "usage_count": usage_count,
                "last_used_at": last_used_at,
                "last_review_at": last_review_at,
                "last_review_notes": last_review_notes,
                "last_reviewed_by": last_reviewed_by,
                "review_counts": review_counts,
                "reason": reason,
                "size_bytes": size_bytes,
                "freshness_state": freshness_state,
                "staleness_reasons": staleness_reasons,
                "inputs_hash": inputs_hash,
                "last_checked_at": last_checked_at,
                "profile_updated_at": profile_updated_at,
            }
        )

    return {
        "schema_version": schema_version,
        "rules_version": rules_version,
        "limits_max_items_per_profile": max_items,
        "limits_max_bytes_per_profile": max_bytes,
        "artifact_updated_at": now,
        "profiles": parsed_profiles,
    }


def _profile_item_rows(branch_name: str, profiles: list[dict[str, Any]]) -> list[ContextProfileItem]:
    """
    Build ContextProfileItem rows from parsed profile payloads.

    Args:
        branch_name (str): Branch identifier owning the profiles.
        profiles (list[dict[str, Any]]): Parsed profile payloads.

    Returns:
        list[ContextProfileItem]: ORM rows for profile items.
    """

    rows: list[ContextProfileItem] = []
    for profile in profiles:
        review_counts = profile["review_counts"]
        rows.append(
            ContextProfileItem(
                branch_name=branch_name,
                profile_name=profile["name"],
                position=profile["position"],
                score=profile["score"],
                grade=profile["grade"],
                usage_count=profile["usage_count"],
                last_used_at=profile["last_used_at"],
                last_review_at=profile["last_review_at"],
                last_review_notes=profile["last_review_notes"],
                last_reviewed_by=profile["last_reviewed_by"],
                review_count_excellent=review_counts["excellent"],
                review_count_good=review_counts["good"],
                review_count_ok=review_counts["ok"],
                review_count_poor=review_counts["poor"],
                review_count_bad=review_counts["bad"],
                reason=profile["reason"],
                size_bytes=profile["size_bytes"],
                freshness_state=profile["freshness_state"],
                inputs_hash=profile["inputs_hash"],
                last_checked_at=profile["last_checked_at"],
                profile_updated_at=profile["profile_updated_at"],
            )
        )
    return rows


def _profile_path_rows(branch_name: str, profiles: list[dict[str, Any]]) -> list[ContextProfileItemPath]:
    """
    Build ContextProfileItemPath rows from parsed profile payloads.

    Args:
        branch_name (str): Branch identifier owning the profiles.
        profiles (list[dict[str, Any]]): Parsed profile payloads.

    Returns:
        list[ContextProfileItemPath]: ORM rows for profile paths.
    """

    rows: list[ContextProfileItemPath] = []
    for profile in profiles:
        for position, path in enumerate(profile["paths"]):
            rows.append(
                ContextProfileItemPath(
                    branch_name=branch_name,
                    profile_name=profile["name"],
                    position=position,
                    path=path,
                )
            )
    return rows


def _profile_reason_rows(
    branch_name: str,
    profiles: list[dict[str, Any]],
) -> list[ContextProfileItemStalenessReason]:
    """
    Build ContextProfileItemStalenessReason rows from parsed profile payloads.

    Args:
        branch_name (str): Branch identifier owning the profiles.
        profiles (list[dict[str, Any]]): Parsed profile payloads.

    Returns:
        list[ContextProfileItemStalenessReason]: ORM rows for staleness reasons.
    """

    rows: list[ContextProfileItemStalenessReason] = []
    for profile in profiles:
        for position, reason in enumerate(profile["staleness_reasons"]):
            rows.append(
                ContextProfileItemStalenessReason(
                    branch_name=branch_name,
                    profile_name=profile["name"],
                    position=position,
                    reason=reason,
                )
            )
    return rows


def _apply_audit_fields(now: str, actor_id: str, rows: Iterable[Any]) -> None:
    """
    Apply audit fields to ORM rows before insertion.

    Args:
        now (str): Timestamp to apply to audit fields.
        actor_id (str): Actor identifier for audit fields.
        rows (Iterable[Any]): ORM row instances to update.

    Returns:
        None: Rows are updated in-place.
    """

    for row in rows:
        row.created_at = now
        row.created_by = actor_id
        row.updated_at = now
        row.updated_by = actor_id


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


def _load_payload(repo_root: Path, branch_name: str) -> tuple[dict[str, Any], bool]:
    """
    Load a context_profiles payload from SQLite after a write.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.

    Returns:
        tuple[dict[str, Any], bool]: Payload and exists flag.
    """

    db_path = user_db_path(repo_root)
    with sqlite_session(db_path, must_exist=True) as session:
        core = session.get(ContextProfilesCore, branch_name)
        if core is None:
            return {}, False

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


def _write_payload(
    repo_root: Path,
    branch_name: str,
    payload: dict[str, Any],
    actor_id: str,
    now: str,
) -> None:
    """
    Write a context_profiles payload to SQLite.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        payload (dict[str, Any]): Context profiles payload.
        actor_id (str): Actor identifier for audit logging.
        now (str): Timestamp to apply for updates.

    Raises:
        ValueError: If payload validation fails.
    """

    parsed = _parse_payload(payload, now)
    db_path = user_db_path(repo_root)
    with sqlite_session(db_path, must_exist=True) as session:
        core = session.get(ContextProfilesCore, branch_name)
        if core is None:
            core = ContextProfilesCore(
                branch_name=branch_name,
                schema_version=parsed["schema_version"],
                rules_version=parsed["rules_version"],
                limits_max_items_per_profile=parsed["limits_max_items_per_profile"],
                limits_max_bytes_per_profile=parsed["limits_max_bytes_per_profile"],
                artifact_updated_at=parsed["artifact_updated_at"],
                created_at=now,
                created_by=actor_id,
                updated_at=now,
                updated_by=actor_id,
            )
            session.add(core)
        else:
            core.schema_version = parsed["schema_version"]
            core.rules_version = parsed["rules_version"]
            core.limits_max_items_per_profile = parsed["limits_max_items_per_profile"]
            core.limits_max_bytes_per_profile = parsed["limits_max_bytes_per_profile"]
            core.artifact_updated_at = parsed["artifact_updated_at"]
            core.updated_at = now
            core.updated_by = actor_id

        session.query(ContextProfileItemPath).filter_by(branch_name=branch_name).delete()
        session.query(ContextProfileItemStalenessReason).filter_by(branch_name=branch_name).delete()
        session.query(ContextProfileItem).filter_by(branch_name=branch_name).delete()

        items = _profile_item_rows(branch_name, parsed["profiles"])
        path_rows = _profile_path_rows(branch_name, parsed["profiles"])
        reason_rows = _profile_reason_rows(branch_name, parsed["profiles"])

        _apply_audit_fields(now, actor_id, items)
        _apply_audit_fields(now, actor_id, path_rows)
        _apply_audit_fields(now, actor_id, reason_rows)

        session.add_all(items)
        session.add_all(path_rows)
        session.add_all(reason_rows)


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Persist a context_profiles payload to SQLite.

    Args:
        payload (dict): Command payload containing payload.branch_name/context_profiles.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing the stored context_profiles payload.

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
        require_bool(raw_payload, "exists", command_name)
        context_profiles = _require_profiles(raw_payload, command_name)
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
        _write_payload(repo_root, branch_name, context_profiles, actor_id, now)
        record, exists = _load_payload(repo_root, branch_name)
        if not isinstance(record, dict):
            return error_result(
                code="payload_invalid",
                meaning="context_profiles write returned invalid payload.",
                details={
                    "command_name": command_name,
                    "branch_name": branch_name,
                    "payload_type": type(record).__name__,
                },
            )
        return ok_result(
            output={
                "branch_name": branch_name,
                "record": record,
                "exists": exists,
            }
        )
    except Exception as exc:
        return exception_result(command_name, exc)
