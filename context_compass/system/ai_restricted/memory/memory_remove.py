"""
Remove a memory entry from the user or system memory store.
"""

import argparse
import logging
from pathlib import Path

from context_compass.system.ai_restricted.system_management import lease
from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_string,
    require_choice,
    require_string,
)
from context_compass.system.ai_restricted._shared.command_results import (
    error_result,
    exception_result,
    ok_result,
    payload_error_result,
)
from context_compass.system.ai_restricted._shared.certification_guard import ensure_certified
from context_compass.system.ai_restricted._shared.feature_guard import ensure_feature_enabled
from context_compass.system.ai_restricted._shared.memory_store import load_store, write_store
from context_compass.system.ai_restricted._shared import policies as policy_store
from context_compass.system.ai_restricted._shared.timeutils import utc_now_iso
from context_compass.system.ai_restricted._shared.work_mode_guard import ensure_work_mode
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)


def _default_policies() -> dict:
    """
    Return default policy values for memory deletes.

    Returns:
        dict: Default policy values for lease TTL and lock wait.
    """
    policies = policy_store.default_policies()
    return {
        "lease_ttl_seconds": policies["lease_ttl_seconds"],
        "lock_wait_seconds": policies["lock_wait_seconds"],
    }


def _load_policies(repo_root: Path) -> dict:
    """
    Load policy values from config with defaults.

    Args:
        repo_root (Path): Repository root.

    Returns:
        dict: Effective policies for lease TTL and lock wait.

    Raises:
        FileNotFoundError: If the system database is missing.
        RuntimeError: If required policy tables or rows are missing.
        ValueError: If policy values are invalid.
    """
    policies = policy_store.load_policies(repo_root)
    return {
        "lease_ttl_seconds": policies["lease_ttl_seconds"],
        "lock_wait_seconds": policies["lock_wait_seconds"],
    }


def remove_memory(repo_root: Path, store: str, memory_id: str) -> bool:
    """
    Remove a memory entry by id.

    Args:
        repo_root (Path): Repository root.
        store (str): Store name (user/system).
        memory_id (str): Memory identifier.

    Returns:
        bool: True if the entry was removed.
    """
    now = utc_now_iso()
    store_path, data = load_store(repo_root, store)
    memories = data.get("memories", [])
    if not isinstance(memories, list):
        memories = []
    original = len(memories)
    data["memories"] = [entry for entry in memories if entry.get("memory_id") != memory_id]
    if len(data["memories"]) == original:
        return False
    data["updated_at"] = now
    write_store(store_path, data)
    return True


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Remove a memory entry using the ToolCommandAPI contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing the removed memory id.

    Raises:
        None: All errors are returned as CommandResult payloads.

    Contract:
        - Requires agent_id, store, and memory_id in the payload.
        - Enforces certification, feature, and work mode guards.
        - Returns an error if the memory id does not exist.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        agent_id = require_string(payload, "agent_id", command_name)
        work_id = optional_string(payload, "work_id", command_name=command_name)
        store = require_choice(payload, "store", command_name, ["user", "system"])
        memory_id = require_string(payload, "memory_id", command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    try:
        ensure_certified(repo_root, agent_id)
        ensure_feature_enabled(repo_root, "memory", "remove memory")
        ensure_work_mode(repo_root, work_id, "remove memory")

        policies = _load_policies(repo_root)
        store_path, _ = load_store(repo_root, store)
        lease.acquire_lock(
            repo_root,
            store_path,
            agent_id,
            policies["lease_ttl_seconds"],
            work_id,
        )
        try:
            removed = remove_memory(repo_root, store, memory_id)
        finally:
            lease.release_lock(repo_root, store_path, agent_id)
    except Exception as exc:
        return exception_result(
            command_name,
            exc,
            details={"store": store, "memory_id": memory_id, "agent_id": agent_id},
        )

    if not removed:
        return error_result(
            code="memory_not_found",
            meaning="memory_id not found.",
            details={"memory_id": memory_id, "store": store},
        )
    return ok_result(output={"memory_id": memory_id, "store": store})


def main() -> None:
    """
    CLI entrypoint for memory removals.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """
    parser = argparse.ArgumentParser(description="Remove a memory entry")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--store", required=True, choices=["user", "system"], help="Memory store name")
    parser.add_argument("--memory-id", required=True, help="Memory identifier")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "agent_id": args.agent_id,
        "work_id": args.work_id,
        "store": args.store,
        "memory_id": args.memory_id,
    }
    context = ExecutionContext(
        command_name="memory_remove",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("memory_remove failed: %s", result.errors)
        raise SystemExit(1)
    logger.info("memory removed: %s", result.output.get("memory_id"))


if __name__ == "__main__":
    main()
