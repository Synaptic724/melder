"""
SQL tool script for reading config_policies_core records.

Purpose
- Fetch policy configuration by config_id.
- Provide policy values for lease/lock defaults in downstream tooling.

Contract
- Requires payload.config_id and actor_id.
- Returns ci_fail_states ordered by position (then state).
- Returns record payload shaped for policy consumers.
"""

from __future__ import annotations

from pathlib import Path

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_string,
    require_int,
    require_string,
)
from context_compass.system.ai_restricted._shared.command_results import (
    error_result,
    exception_result,
    ok_result,
    payload_error_result,
)
from context_compass.system.ai_restricted.database_management.orm_session import (
    sqlite_session,
    system_db_path,
)
from context_compass.system.ai_restricted.database_management.system_orm_models import (
    ConfigPoliciesCiFailState,
    ConfigPoliciesCore,
)
from context_compass.system.ai_restricted.system_management.command_runner import (
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


def _load_ci_fail_states(states: list[ConfigPoliciesCiFailState]) -> list[str]:
    """
    Return ordered CI fail state values.

    Args:
        states (list[ConfigPoliciesCiFailState]): CI fail state rows.

    Returns:
        list[str]: Ordered CI fail state values.

    Contract:
        - Orders by position (None values sort last) then state.
    """

    ordered = sorted(
        states,
        key=lambda state: (
            state.position if state.position is not None else 999_999,
            state.state,
        ),
    )
    return [state.state for state in ordered]


def _record_to_dict(row: ConfigPoliciesCore) -> dict:
    """
    Convert a ConfigPoliciesCore ORM row into a dictionary.

    Args:
        row (ConfigPoliciesCore): ORM row instance.

    Returns:
        dict: Serialized policy configuration payload.
    """

    return {
        "config_id": row.config_id,
        "schema_version": row.schema_version,
        "architecture_context_faulty_ratio_threshold": row.architecture_context_faulty_ratio_threshold,
        "architecture_context_good_ratio_threshold": row.architecture_context_good_ratio_threshold,
        "architecture_context_stale_ratio_threshold": row.architecture_context_stale_ratio_threshold,
        "ci_fail_on_needs_review": row.ci_fail_on_needs_review,
        "ci_fail_states": _load_ci_fail_states(list(row.ci_fail_states)),
        "context_profiles_max_bytes_per_profile": row.context_profiles_max_bytes_per_profile,
        "context_profiles_max_items_per_profile": row.context_profiles_max_items_per_profile,
        "context_profiles_optimize_score_threshold": row.context_profiles_optimize_score_threshold,
        "context_profiles_popular_usage_threshold": row.context_profiles_popular_usage_threshold,
        "context_profiles_prune_score_threshold": row.context_profiles_prune_score_threshold,
        "dir_review_every_n_scans_default": row.dir_review_every_n_scans_default,
        "lease_heartbeat_seconds": row.lease_heartbeat_seconds,
        "lease_ttl_seconds": row.lease_ttl_seconds,
        "lock_wait_seconds": row.lock_wait_seconds,
        "max_task_attempts": row.max_task_attempts,
        "review_every_n_scans_default": row.review_every_n_scans_default,
        "created_at": row.created_at,
        "created_by": row.created_by,
        "updated_at": row.updated_at,
        "updated_by": row.updated_by,
    }


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Read a config_policies_core record by config_id.

    Args:
        payload (dict): Command payload containing payload.config_id.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing the policy configuration record.

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
        config_id = require_int(raw_payload, "config_id", command_name)
        if config_id < 1:
            raise PayloadError(
                code="payload_value_error",
                details={
                    "command_name": command_name,
                    "field": "config_id",
                    "expected": "integer >= 1",
                    "actual": config_id,
                },
            )
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    db_path = system_db_path(repo_root)
    if not db_path.exists():
        return error_result(
            code="db_missing",
            meaning="System database does not exist.",
            details={
                "command_name": command_name,
                "db_path": str(db_path),
            },
        )

    try:
        with sqlite_session(db_path, must_exist=True) as session:
            row = session.get(ConfigPoliciesCore, (config_id))
            if row is None:
                return error_result(
                    code="record_not_found",
                    meaning="Record not found.",
                    details={
                        "command_name": command_name,
                        "config_id": config_id,
                    },
                )
            record = _record_to_dict(row)
        return ok_result(output={"record": record})
    except Exception as exc:
        return exception_result(command_name, exc)
