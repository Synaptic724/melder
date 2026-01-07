"""
Assess repo lifecycle stage and update repo_state records in SQLite.
"""

import argparse
import logging
from pathlib import Path
from typing import Optional

from context_compass.system.ai_restricted.system_management import lease
from context_compass.system.ai_restricted._shared import branch_paths
from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_bool,
    optional_list,
    optional_string,
    require_choice,
    require_string,
)
from context_compass.system.ai_restricted._shared.command_results import (
    exception_result,
    ok_result,
    payload_error_result,
)
from context_compass.system.ai_restricted._shared.certification_guard import ensure_certified
from context_compass.system.ai_restricted._shared.feature_guard import ensure_feature_enabled
from context_compass.system.ai_restricted._shared.work_mode_guard import ensure_work_mode
from context_compass.system.ai_restricted._shared.timeutils import utc_now_iso
from context_compass.system.ai_restricted.database_management import sqlite_crud
from context_compass.system.ai_restricted.database_management import sqlite_query
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)


POLICIES_TABLE_NAME = "config_policies_core"
POLICIES_ACTION = "by_config_id"
POLICIES_CONFIG_ID = 1


def _allowed_stages() -> list[str]:
    """
    Return allowed lifecycle stage values.

    Returns:
        list[str]: Allowed stage values.
    """
    return ["new", "active_dev", "stable", "production", "maintenance", "experimental", "archived"]


def _load_policies(repo_root: Path, owner_id: str) -> dict:
    """
    Load policy configuration values via sqlite_crud.

    Args:
        repo_root (Path): Repository root.
        owner_id (str): Actor identifier for audit logging.

    Returns:
        dict: Policy values including lease_ttl_seconds and lock_wait_seconds.

    Raises:
        ValueError: If required policy fields are missing or invalid.
        sqlite_crud.SqliteCrudError: If the CRUD request fails.
    """

    response = sqlite_crud.execute_request(
        repo_root,
        sqlite_crud.SqliteCrudRequest(
            operation="read",
            scope="system",
            table_name=POLICIES_TABLE_NAME,
            action=POLICIES_ACTION,
            payload={"config_id": POLICIES_CONFIG_ID},
            actor_id=owner_id,
        ),
    )
    record = response.output.get("result", {}).get("record", {})
    lease_ttl = record.get("lease_ttl_seconds")
    lock_wait = record.get("lock_wait_seconds")
    if not isinstance(lease_ttl, int) or lease_ttl < 1:
        raise ValueError("lease_ttl_seconds must be an integer >= 1.")
    if not isinstance(lock_wait, int) or lock_wait < 0:
        raise ValueError("lock_wait_seconds must be an integer >= 0.")
    return {
        "lease_ttl_seconds": lease_ttl,
        "lock_wait_seconds": lock_wait,
    }


def _repo_state_lock_resource(branch_name: str) -> Path:
    """
    Build a synthetic lock resource path for repo_state.

    Args:
        branch_name (str): Branch identifier.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"branch_repo_state::{branch_name}")


def _apply_defaults_for_stage(stage: str) -> dict:
    """
    Return default tooling policy updates for a given stage.

    Args:
        stage (str): Lifecycle stage.

    Returns:
        dict: Tooling policy defaults.
    """
    if stage == "new":
        return {
            "mode": "restricted",
            "disabled_features": ["scan", "context_profiles"],
            "notes": "Auto-restricted for new repos; update repo_state to enable.",
        }
    return {"mode": "normal", "disabled_features": [], "notes": None}


def _read_repo_state(
    repo_root: Path,
    branch_name: str,
    actor_id: str,
) -> tuple[dict, bool]:
    """
    Read repo_state via sqlite_crud.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        tuple[dict, bool]: repo_state payload and existence flag.

    Raises:
        ValueError: If the CRUD response payload is invalid.
        sqlite_crud.SqliteCrudError: If the CRUD request fails.
    """

    response = sqlite_crud.execute_request(
        repo_root,
        sqlite_crud.SqliteCrudRequest(
            operation="read",
            scope="user",
            table_name="repo_state",
            action="by_branch_name",
            payload={"branch_name": branch_name},
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    record = result.get("record")
    exists = result.get("exists")
    if not isinstance(record, dict):
        raise ValueError("repo_state read returned an invalid record payload.")
    if not isinstance(exists, bool):
        raise ValueError("repo_state read returned an invalid exists flag.")
    return record, exists


def _write_repo_state(
    repo_root: Path,
    branch_name: str,
    payload: dict,
    actor_id: str,
    exists: bool,
) -> dict:
    """
    Write repo_state via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        payload (dict): Repo state payload to persist.
        actor_id (str): Actor identifier for audit logging.
        exists (bool): Whether the repo_state record already exists.

    Returns:
        dict: Updated repo_state payload.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name="write_repo_state",
            payload={
                "branch_name": branch_name,
                "repo_state": payload,
                "exists": exists,
            },
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    record = result.get("record")
    if not isinstance(record, dict):
        raise ValueError("repo_state write returned an invalid record payload.")
    return record


def assess_repo_state(
    repo_root: Path,
    agent_id: str,
    work_id: Optional[str],
    stage: str,
    assessment: Optional[str],
    confidence: float,
    tooling_mode: Optional[str],
    disabled_features: list[str],
    clear_disabled: bool,
    notes: Optional[str],
    owner_id: Optional[str],
) -> dict:
    """
    Update repo_state records in SQLite with lifecycle and tooling assessment.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        work_id (Optional[str]): Work id for hard mode.
        stage (str): Lifecycle stage.
        assessment (Optional[str]): Assessment notes.
        confidence (float): Confidence score (0-1).
        tooling_mode (Optional[str]): Tooling policy mode override.
        disabled_features (list[str]): Disabled features list.
        clear_disabled (bool): Whether to clear disabled features.
        notes (Optional[str]): Tooling policy notes.
        owner_id (Optional[str]): Lock owner id override.

    Returns:
        dict: Updated repo state payload.
    """
    now = utc_now_iso()
    branch_name = branch_paths.load_current_branch(repo_root)
    resource = _repo_state_lock_resource(branch_name)
    lock_owner = owner_id or agent_id
    policies = _load_policies(repo_root, lock_owner)

    lease.acquire_lock(
        repo_root,
        resource,
        lock_owner,
        ttl_seconds=policies["lease_ttl_seconds"],
    )
    try:
        record, exists = _read_repo_state(repo_root, branch_name, agent_id)
        state = dict(record)
        lifecycle = state.get("lifecycle")
        if not isinstance(lifecycle, dict):
            lifecycle = {}
        lifecycle["stage"] = stage
        if assessment is not None:
            lifecycle["assessment"] = assessment
        lifecycle["confidence"] = max(0.0, min(1.0, float(confidence)))
        lifecycle["assessed_at"] = now
        state["lifecycle"] = lifecycle

        tooling = state.get("tooling_policy")
        if not isinstance(tooling, dict):
            tooling = {}

        if tooling_mode is None and not tooling:
            tooling.update(_apply_defaults_for_stage(stage))
        if tooling_mode is not None:
            tooling["mode"] = tooling_mode
        if clear_disabled:
            tooling["disabled_features"] = []
        elif disabled_features:
            tooling["disabled_features"] = sorted({str(item) for item in disabled_features})
        if notes is not None:
            tooling["notes"] = notes
        tooling["updated_at"] = now
        state["tooling_policy"] = tooling

        state["updated_at"] = now
        if state.get("created_at") is None:
            state["created_at"] = now
        state = _write_repo_state(repo_root, branch_name, state, agent_id, exists)
    finally:
        lease.release_lock(repo_root, resource, lock_owner)

    return state


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Assess repo state using the ToolCommandAPI contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing the updated repo_state payload.

    Raises:
        None: All errors are captured and returned in the CommandResult.

    Contract:
        - Requires agent_id and stage.
        - Enforces certification, feature flags, and work mode guards.
        - confidence must be numeric (0-1 clamped).
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        agent_id = require_string(payload, "agent_id", command_name)
        work_id = optional_string(payload, "work_id", command_name=command_name)
        stage = require_choice(payload, "stage", command_name, _allowed_stages())
        assessment = optional_string(payload, "assessment", command_name=command_name)
        tooling_mode = optional_string(payload, "tooling_mode", command_name=command_name)
        disabled_features = optional_list(
            payload, "disabled_features", command_name=command_name, default=[]
        )
        clear_disabled = optional_bool(
            payload, "clear_disabled", command_name=command_name, default=False
        )
        notes = optional_string(payload, "notes", command_name=command_name)
        owner_id = optional_string(payload, "owner_id", command_name=command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    confidence_value = payload.get("confidence", 0.5)
    if not isinstance(confidence_value, (int, float)):
        return payload_error_result(
            command_name,
            PayloadError(
                code="payload_type_error",
                details={
                    "command_name": command_name,
                    "field": "confidence",
                    "expected": "number",
                    "actual_type": type(confidence_value).__name__,
                },
            ),
        )
    if tooling_mode is not None and tooling_mode not in ("normal", "restricted"):
        return payload_error_result(
            command_name,
            PayloadError(
                code="payload_value_error",
                details={
                    "command_name": command_name,
                    "field": "tooling_mode",
                    "expected": "normal or restricted",
                    "actual": tooling_mode,
                },
            ),
        )

    try:
        ensure_certified(repo_root, owner_id or agent_id)
        ensure_feature_enabled(repo_root, "repo_state", "update repo state")
        ensure_work_mode(repo_root, work_id, "update repo state")
        state = assess_repo_state(
            repo_root=repo_root,
            agent_id=agent_id,
            work_id=work_id,
            stage=stage,
            assessment=assessment,
            confidence=float(confidence_value),
            tooling_mode=tooling_mode,
            disabled_features=list(disabled_features or []),
            clear_disabled=bool(clear_disabled),
            notes=notes,
            owner_id=owner_id,
        )
        return ok_result(output={"repo_state": state})
    except Exception as exc:
        return exception_result(command_name, exc)


def main() -> None:
    """
    CLI entrypoint for repo_state assessment.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """
    parser = argparse.ArgumentParser(
        description="Assess repo lifecycle and update repo_state records."
    )
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--stage", required=True, choices=_allowed_stages(), help="Lifecycle stage")
    parser.add_argument("--assessment", default=None, help="Assessment notes")
    parser.add_argument("--confidence", type=float, default=0.5, help="Confidence (0-1)")
    parser.add_argument("--tooling-mode", choices=["normal", "restricted"], default=None, help="Tooling mode override")
    parser.add_argument("--disable-feature", action="append", default=[], help="Feature to disable (repeatable)")
    parser.add_argument("--clear-disabled", action="store_true", help="Clear disabled feature list")
    parser.add_argument("--notes", default=None, help="Tooling policy notes")
    parser.add_argument("--owner-id", default=None, help="Lock owner id override")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "agent_id": args.agent_id,
        "work_id": args.work_id,
        "stage": args.stage,
        "assessment": args.assessment,
        "confidence": args.confidence,
        "tooling_mode": args.tooling_mode,
        "disabled_features": args.disable_feature,
        "clear_disabled": args.clear_disabled,
        "notes": args.notes,
        "owner_id": args.owner_id,
    }
    context = ExecutionContext(
        command_name="repo_state_assess",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("repo_state_assess failed: %s", result.errors)
        raise SystemExit(1)
    repo_state = result.output.get("repo_state", {})
    logger.info("repo_state updated: stage=%s", repo_state.get("lifecycle", {}).get("stage"))


if __name__ == "__main__":
    main()
