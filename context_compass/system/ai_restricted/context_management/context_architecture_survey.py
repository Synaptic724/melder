"""
Survey and build architecture_context artifacts from directory ctx only.

Purpose
- Persist architecture_context records in SQLite per branch.
"""

import argparse
import logging
from pathlib import Path
from typing import Optional

from context_compass.system.ai_restricted.system_management import lease
from context_compass.system.ai_restricted._shared import architecture_contexts, branch_paths
from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_bool,
    optional_string,
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
from context_compass.system.ai_restricted._shared.ignore_rules import load_ignore_config
from context_compass.system.ai_restricted._shared.paths import repo_relative_path
from context_compass.system.ai_restricted._shared.timeutils import utc_now_iso
from context_compass.system.ai_restricted.database_management import sqlite_crud, sqlite_query
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)

CONFIG_POLICIES_TABLE = "config_policies_core"
CONFIG_POLICIES_ACTION = "by_config_id"
CONFIG_POLICIES_ID = 1
DEFAULT_LEASE_TTL_SECONDS = 300
DEFAULT_LOCK_WAIT_SECONDS = 10
DEFAULT_ARCHITECTURE_GOOD_RATIO_THRESHOLD = 0.9
DEFAULT_ARCHITECTURE_STALE_RATIO_THRESHOLD = 0.75
DEFAULT_ARCHITECTURE_FAULTY_RATIO_THRESHOLD = 0.6


def _default_policies() -> dict:
    """
    Return default policy values for architecture contexts.

    Returns:
        dict: Default policy values for architecture contexts.
    """
    return {
        "lease_ttl_seconds": DEFAULT_LEASE_TTL_SECONDS,
        "lock_wait_seconds": DEFAULT_LOCK_WAIT_SECONDS,
        "architecture_context_good_ratio_threshold": DEFAULT_ARCHITECTURE_GOOD_RATIO_THRESHOLD,
        "architecture_context_stale_ratio_threshold": DEFAULT_ARCHITECTURE_STALE_RATIO_THRESHOLD,
        "architecture_context_faulty_ratio_threshold": DEFAULT_ARCHITECTURE_FAULTY_RATIO_THRESHOLD,
    }


def _load_policies(repo_root: Path, actor_id: str) -> dict:
    """
    Load policy configuration with defaults applied.

    Args:
        repo_root (Path): Repository root.

    Returns:
        dict: Effective policies for architecture contexts.

    Raises:
        ValueError: If policy values are invalid.
        sqlite_crud.SqliteCrudError: If the policy lookup fails.
    """
    defaults = _default_policies()
    response = sqlite_crud.execute_request(
        repo_root,
        sqlite_crud.SqliteCrudRequest(
            operation="read",
            scope="system",
            table_name=CONFIG_POLICIES_TABLE,
            action=CONFIG_POLICIES_ACTION,
            payload={"config_id": CONFIG_POLICIES_ID},
            actor_id=actor_id,
        ),
    )
    record = response.output.get("result", {}).get("record")
    if not isinstance(record, dict):
        raise ValueError("config_policies_core read returned an invalid record payload.")
    lease_ttl = record.get("lease_ttl_seconds")
    lock_wait = record.get("lock_wait_seconds")
    good_ratio = record.get("architecture_context_good_ratio_threshold")
    stale_ratio = record.get("architecture_context_stale_ratio_threshold")
    faulty_ratio = record.get("architecture_context_faulty_ratio_threshold")
    if isinstance(lease_ttl, int):
        defaults["lease_ttl_seconds"] = lease_ttl
    if isinstance(lock_wait, int):
        defaults["lock_wait_seconds"] = lock_wait
    if isinstance(good_ratio, (int, float)):
        defaults["architecture_context_good_ratio_threshold"] = good_ratio
    if isinstance(stale_ratio, (int, float)):
        defaults["architecture_context_stale_ratio_threshold"] = stale_ratio
    if isinstance(faulty_ratio, (int, float)):
        defaults["architecture_context_faulty_ratio_threshold"] = faulty_ratio
    return defaults


def _directory_summaries(repo_root: Path, ctx_payloads: list[dict]) -> list[dict]:
    """
    Build directory summaries from dir ctx payloads.

    Args:
        repo_root (Path): Repository root.
        ctx_payloads (list[dict]): Directory ctx payloads.

    Returns:
        list[dict]: Directory summary payloads.
    """
    summaries: list[dict] = []
    for payload in ctx_payloads:
        if not isinstance(payload, dict):
            continue
        identity = payload.get("identity", {})
        if not isinstance(identity, dict):
            continue
        ctx_path = identity.get("ctx_path")
        if not isinstance(ctx_path, str) or not ctx_path:
            continue
        rel_path = repo_relative_path(repo_root, repo_root / ctx_path)
        entry = {"path": rel_path, "one_liner": None, "detail": None}
        agent = payload.get("agent", {})
        if isinstance(agent, dict):
            summary = agent.get("summary", {})
            if isinstance(summary, dict):
                entry["one_liner"] = summary.get("one_liner")
                entry["detail"] = summary.get("detail")
        summaries.append(entry)
    return summaries


def _build_agent_section(repo_root: Path, ctx_payloads: list[dict], target: str) -> dict:
    """
    Build the agent section for architecture_context.

    Args:
        repo_root (Path): Repository root.
        ctx_payloads (list[dict]): Directory ctx payloads.
        target (str): Target scope.

    Returns:
        dict: Agent section payload.
    """
    summaries = _directory_summaries(repo_root, ctx_payloads)
    return {
        "summary": {
            "one_liner": f"{target} architecture context derived from directory ctx.",
            "detail": f"Derived from {len(ctx_payloads)} directory ctx artifacts.",
        },
        "directories": summaries,
        "notes": "Directory ctx is the sole source of structural truth.",
    }


def _architecture_context_lock_resource(branch_name: str, kind: str) -> Path:
    """
    Build a synthetic lock resource path for architecture contexts.

    Args:
        branch_name (str): Branch identifier.
        kind (str): Context kind identifier.

    Returns:
        Path: Resource path for lease locks.

    Contract:
        - Pure mapping from inputs to lock resource path.
        - No filesystem access is performed.
    """

    return Path(f"branch_architecture_context::{branch_name}::{kind}")


def _read_architecture_context(
    repo_root: Path,
    branch_name: str,
    kind: str,
    actor_id: str,
) -> tuple[dict, bool]:
    """
    Read architecture_context via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        kind (str): Context kind identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        tuple[dict, bool]: Stored payload and existence flag.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.

    Contract:
        - Returns the payload stored in SQLite (or the default payload if missing).
        - Does not mutate the stored record.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name="read_architecture_context",
            payload={"branch_name": branch_name, "kind": kind},
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    record = result.get("record")
    exists = result.get("exists")
    if not isinstance(record, dict):
        raise ValueError("architecture_context read returned an invalid record payload.")
    if not isinstance(exists, bool):
        raise ValueError("architecture_context read returned an invalid exists flag.")
    return record, exists


def _write_architecture_context(
    repo_root: Path,
    branch_name: str,
    kind: str,
    payload: dict,
    actor_id: str,
    exists: bool,
) -> dict:
    """
    Persist architecture_context via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        kind (str): Context kind identifier.
        payload (dict): Payload to write.
        actor_id (str): Actor identifier for audit logging.
        exists (bool): Whether the record already exists.

    Returns:
        dict: Stored payload returned from the query.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.

    Contract:
        - Writes are delegated to the registered sqlite_query script.
        - Returns the payload as stored after the write completes.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name="write_architecture_context",
            payload={
                "branch_name": branch_name,
                "kind": kind,
                "context": payload,
                "exists": exists,
            },
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    record = result.get("record")
    if not isinstance(record, dict):
        raise ValueError("architecture_context write returned an invalid record payload.")
    return record


def _write_if_changed(
    repo_root: Path,
    branch_name: str,
    kind: str,
    payload: dict,
    owner_id: str,
    policies: dict,
    *,
    existing: Optional[dict],
    exists: bool,
) -> bool:
    """
    Write the architecture context payload if it changed.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        kind (str): Context kind identifier.
        payload (dict): Payload to write.
        owner_id (str): Lock owner id.
        policies (dict): Policy values.
        existing (Optional[dict]): Existing payload for comparison.
        exists (bool): Whether the record already exists.

    Returns:
        bool: True if the record was updated.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.

    Contract:
        - Skips the write when payloads match exactly.
        - Acquires and releases a lease lock around the write.
    """
    if existing == payload:
        return False
    resource = _architecture_context_lock_resource(branch_name, kind)
    lease.acquire_lock(repo_root, resource, owner_id, ttl_seconds=policies["lease_ttl_seconds"])
    try:
        _write_architecture_context(repo_root, branch_name, kind, payload, owner_id, exists)
        return True
    finally:
        lease.release_lock(repo_root, resource, owner_id)


def survey_architecture(
    repo_root: Path,
    agent_id: str,
    work_id: Optional[str],
    target: str,
    dry_run: bool,
) -> dict:
    """
    Build an architecture_context artifact from directory ctx.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        work_id (Optional[str]): Work id for hard mode enforcement.
        target (str): Target scope ("prod" or "test").
        dry_run (bool): If True, do not write output.

    Returns:
        dict: Architecture context payload.
    """
    ensure_feature_enabled(repo_root, "architecture_contexts", "survey architecture contexts")
    ensure_work_mode(repo_root, work_id, "survey architecture contexts")
    now = utc_now_iso()
    policies = _load_policies(repo_root, agent_id)
    ignore_config = load_ignore_config(repo_root)
    branch_name = branch_paths.load_current_branch(repo_root)
    ctx_payloads = architecture_contexts.collect_dir_ctx_payloads(
        repo_root, branch_name, target, ignore_config, agent_id
    )
    matrix = architecture_contexts.build_matrix(repo_root, branch_name, ctx_payloads, agent_id)
    evaluation = architecture_contexts.evaluate_matrix(
        repo_root, branch_name, matrix, agent_id
    )
    thresholds = architecture_contexts.thresholds_from_policies(policies)
    state = architecture_contexts.derive_state(evaluation["good_ratio"], thresholds)

    payload = {
        "schema_version": 1,
        "kind": "architecture_context" if target == "prod" else "test_architecture_context",
        "updated_at": now,
        "agent": _build_agent_section(repo_root, ctx_payloads, target),
        "computed": {
            "freshness_state": state,
            "holes_count": evaluation["holes_count"],
            "holes_ratio": evaluation["holes_ratio"],
            "good_ratio": evaluation["good_ratio"],
            "inputs_hash": evaluation["inputs_hash"],
            "last_checked_at": now,
            "matrix": evaluation["matrix"],
            "staleness_reasons": evaluation["staleness_reasons"],
        },
    }

    if not dry_run:
        branch_name = branch_paths.load_current_branch(repo_root)
        record, exists = _read_architecture_context(
            repo_root,
            branch_name,
            payload["kind"],
            actor_id=agent_id,
        )
        _write_if_changed(
            repo_root,
            branch_name,
            payload["kind"],
            payload,
            agent_id,
            policies,
            existing=record,
            exists=exists,
        )

    return payload


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Survey architecture context using the ToolCommandAPI contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing the architecture context payload.

    Raises:
        None: All errors are captured and returned in the CommandResult.

    Contract:
        - Requires agent_id.
        - Enforces certification, feature flags, and work mode guards.
        - target defaults to "prod" and dry_run defaults to False.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        agent_id = require_string(payload, "agent_id", command_name)
        work_id = optional_string(payload, "work_id", command_name=command_name)
        target = optional_string(payload, "target", command_name=command_name, default="prod")
        dry_run = optional_bool(payload, "dry_run", command_name=command_name, default=False)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    if target not in ("prod", "test"):
        return payload_error_result(
            command_name,
            PayloadError(
                code="payload_value_error",
                details={
                    "command_name": command_name,
                    "field": "target",
                    "expected": "prod or test",
                    "actual": target,
                },
            ),
        )

    try:
        ensure_certified(repo_root, agent_id)
        ensure_feature_enabled(repo_root, "architecture_contexts", "survey architecture contexts")
        result_payload = survey_architecture(
            repo_root=repo_root,
            agent_id=agent_id,
            work_id=work_id,
            target=target,
            dry_run=bool(dry_run),
        )
        return ok_result(output={"architecture_context": result_payload})
    except Exception as exc:
        return exception_result(command_name, exc)


def main() -> None:
    """
    CLI entrypoint for architecture context surveys.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """
    parser = argparse.ArgumentParser(description="Survey architecture_context from directory ctx")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--target", choices=["prod", "test"], default="prod", help="Target scope")
    parser.add_argument("--dry-run", action="store_true", help="Do not write outputs")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "agent_id": args.agent_id,
        "work_id": args.work_id,
        "target": args.target,
        "dry_run": args.dry_run,
    }
    context = ExecutionContext(
        command_name="context_architecture_survey",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("context_architecture_survey failed: %s", result.errors)
        raise SystemExit(1)
    architecture_context = result.output.get("architecture_context", {})
    logger.info("architecture_context refreshed: kind=%s", architecture_context.get("kind"))


if __name__ == "__main__":
    main()
