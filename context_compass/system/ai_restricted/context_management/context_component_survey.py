"""
Survey and build component_contexts artifacts from directory ctx only.

Purpose
- Persist component_contexts records in SQLite per branch.
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
from context_compass.system.ai_restricted._shared.hashing import hash_json
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
    Return default policy values for component contexts.

    Returns:
        dict: Default policy values for component contexts.
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
        dict: Effective policies for component contexts.

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


def _component_from_dir_ctx(repo_root: Path, payload: dict) -> dict:
    """
    Build a component entry from a directory ctx payload.

    Args:
        repo_root (Path): Repository root.
        payload (dict): Directory ctx payload.

    Returns:
        dict: Component entry.
    """
    identity = payload.get("identity", {})
    if not isinstance(identity, dict):
        raise ValueError("dir_ctx.identity must be a JSON object.")
    ctx_path = identity.get("ctx_path")
    if not isinstance(ctx_path, str) or not ctx_path:
        raise ValueError("dir_ctx.identity.ctx_path must be a string.")
    rel_ctx = repo_relative_path(repo_root, repo_root / ctx_path)
    name = Path(ctx_path).stem.replace("__", "").replace(".dir", "")
    summary = {"one_liner": None, "detail": None}
    responsibilities: list[str] = []
    key_flows: list[str] = []
    boundaries: list[str] = []

    identity_name = identity.get("name")
    if isinstance(identity_name, str) and identity_name:
        name = identity_name
    agent = payload.get("agent", {})
    if isinstance(agent, dict):
        summary_data = agent.get("summary", {})
        if isinstance(summary_data, dict):
            summary["one_liner"] = summary_data.get("one_liner")
            summary["detail"] = summary_data.get("detail")
        architecture = agent.get("architecture", {})
        if isinstance(architecture, dict):
            resp = architecture.get("responsibilities")
            if isinstance(resp, list):
                responsibilities = [item for item in resp if isinstance(item, str)]
            flows = architecture.get("key_flows")
            if isinstance(flows, list):
                key_flows = [
                    flow.get("name")
                    for flow in flows
                    if isinstance(flow, dict) and isinstance(flow.get("name"), str)
                ]
            deps = architecture.get("dependency_rules")
            if isinstance(deps, dict):
                allowed = deps.get("allowed_outbound")
                if isinstance(allowed, list):
                    boundaries.extend([item for item in allowed if isinstance(item, str)])

    component_id = f"component_{hash_json({'ctx_path': rel_ctx})[:8]}"
    return {
        "component_id": component_id,
        "name": name,
        "summary": summary,
        "responsibilities": responsibilities,
        "boundaries": boundaries,
        "key_flows": key_flows,
        "ctx_paths": [rel_ctx],
    }


def _build_components(repo_root: Path, ctx_payloads: list[dict]) -> list[dict]:
    """
    Build component entries from directory ctx payloads.

    Args:
        repo_root (Path): Repository root.
        ctx_payloads (list[dict]): Directory ctx payloads.

    Returns:
        list[dict]: Component list.
    """
    return [_component_from_dir_ctx(repo_root, payload) for payload in ctx_payloads]


def _build_agent_section(target: str, components: list[dict]) -> dict:
    """
    Build the agent section for component_contexts.

    Args:
        target (str): Target scope.
        components (list[dict]): Component list.

    Returns:
        dict: Agent section payload.
    """
    return {
        "summary": {
            "one_liner": f"{target} component contexts derived from directory ctx.",
            "detail": f"Derived from {len(components)} components.",
        }
    }


def _component_context_lock_resource(branch_name: str, kind: str) -> Path:
    """
    Build a synthetic lock resource path for component contexts.

    Args:
        branch_name (str): Branch identifier.
        kind (str): Context kind identifier.

    Returns:
        Path: Resource path for lease locks.

    Contract:
        - Pure mapping from inputs to lock resource path.
        - No filesystem access is performed.
    """

    return Path(f"branch_component_contexts::{branch_name}::{kind}")


def _read_component_contexts(
    repo_root: Path,
    branch_name: str,
    kind: str,
    actor_id: str,
) -> tuple[dict, bool]:
    """
    Read component_contexts via sqlite_query.

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
            query_name="read_component_contexts",
            payload={"branch_name": branch_name, "kind": kind},
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    record = result.get("record")
    exists = result.get("exists")
    if not isinstance(record, dict):
        raise ValueError("component_contexts read returned an invalid record payload.")
    if not isinstance(exists, bool):
        raise ValueError("component_contexts read returned an invalid exists flag.")
    return record, exists


def _write_component_contexts(
    repo_root: Path,
    branch_name: str,
    kind: str,
    payload: dict,
    actor_id: str,
    exists: bool,
) -> dict:
    """
    Persist component_contexts via sqlite_query.

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
            query_name="write_component_contexts",
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
        raise ValueError("component_contexts write returned an invalid record payload.")
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
    Write the component contexts payload if it changed.

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
    resource = _component_context_lock_resource(branch_name, kind)
    lease.acquire_lock(repo_root, resource, owner_id, ttl_seconds=policies["lease_ttl_seconds"])
    try:
        _write_component_contexts(repo_root, branch_name, kind, payload, owner_id, exists)
        return True
    finally:
        lease.release_lock(repo_root, resource, owner_id)


def survey_components(
    repo_root: Path,
    agent_id: str,
    work_id: Optional[str],
    target: str,
    dry_run: bool,
) -> dict:
    """
    Build component_contexts from directory ctx.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        work_id (Optional[str]): Work id for hard mode enforcement.
        target (str): Target scope ("prod" or "test").
        dry_run (bool): If True, do not write output.

    Returns:
        dict: Component contexts payload.
    """
    ensure_feature_enabled(repo_root, "architecture_contexts", "survey component contexts")
    ensure_work_mode(repo_root, work_id, "survey component contexts")
    now = utc_now_iso()
    policies = _load_policies(repo_root, agent_id)
    ignore_config = load_ignore_config(repo_root)
    branch_name = branch_paths.load_current_branch(repo_root)
    ctx_payloads = architecture_contexts.collect_dir_ctx_payloads(
        repo_root, branch_name, target, ignore_config, agent_id
    )
    components = _build_components(repo_root, ctx_payloads)
    matrix = architecture_contexts.build_matrix(repo_root, branch_name, ctx_payloads, agent_id)
    evaluation = architecture_contexts.evaluate_matrix(
        repo_root, branch_name, matrix, agent_id
    )
    thresholds = architecture_contexts.thresholds_from_policies(policies)
    state = architecture_contexts.derive_state(evaluation["good_ratio"], thresholds)

    payload = {
        "schema_version": 1,
        "kind": "component_contexts" if target == "prod" else "test_component_contexts",
        "updated_at": now,
        "agent": _build_agent_section(target, components),
        "components": components,
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
        record, exists = _read_component_contexts(
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
    Survey component contexts using the ToolCommandAPI contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing the component contexts payload.

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
        ensure_feature_enabled(repo_root, "architecture_contexts", "survey component contexts")
        result_payload = survey_components(
            repo_root=repo_root,
            agent_id=agent_id,
            work_id=work_id,
            target=target,
            dry_run=bool(dry_run),
        )
        return ok_result(output={"component_contexts": result_payload})
    except Exception as exc:
        return exception_result(command_name, exc)


def main() -> None:
    """
    CLI entrypoint for component context surveys.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """
    parser = argparse.ArgumentParser(description="Survey component_contexts from directory ctx")
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
        command_name="context_component_survey",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("context_component_survey failed: %s", result.errors)
        raise SystemExit(1)
    component_contexts = result.output.get("component_contexts", {})
    logger.info("component_contexts refreshed: kind=%s", component_contexts.get("kind"))


if __name__ == "__main__":
    main()
