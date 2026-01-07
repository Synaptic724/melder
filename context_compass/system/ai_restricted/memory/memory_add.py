"""
Add a memory entry to the user or system memory store.
"""

import argparse
import logging
from pathlib import Path
from typing import Optional

from context_compass.system.ai_restricted.system_management import lease
from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
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
from context_compass.system.ai_restricted._shared.memory_store import (
    generate_memory_id,
    load_store,
    normalize_tags,
    write_store,
)
from context_compass.system.ai_restricted._shared import policies as policy_store
from context_compass.system.ai_restricted._shared.timeutils import utc_now_iso
from context_compass.system.ai_restricted._shared.work_mode_guard import ensure_work_mode
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)


def _default_policies() -> dict:
    """
    Return default policy values for memory writes.

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
    Load memory policy values from config with defaults.

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


def _parse_tags(raw_tags: Optional[list[str]], raw_csv: Optional[str]) -> list[str]:
    """
    Parse tag inputs from flags.

    Args:
        raw_tags (Optional[list[str]]): Repeated tag values.
        raw_csv (Optional[str]): Comma-separated tags.

    Returns:
        list[str]: Normalized tags.
    """
    tags: list[str] = []
    if raw_tags:
        tags.extend(raw_tags)
    if raw_csv:
        tags.extend([part.strip() for part in raw_csv.split(",")])
    return normalize_tags(tags)


def add_memory(
    repo_root: Path,
    store: str,
    title: str,
    content: str,
    tags: list[str],
    agent_id: str,
    notes: Optional[str],
    source_kind: Optional[str],
    source_ref: Optional[str],
    memory_id: Optional[str],
) -> str:
    """
    Add a memory entry to the selected store.

    Args:
        repo_root (Path): Repository root.
        store (str): Store name (user/system).
        title (str): Memory title.
        content (str): Memory content.
        tags (list[str]): Tag list.
        agent_id (str): Agent identifier.
        notes (Optional[str]): Optional notes.
        source_kind (Optional[str]): Optional source kind.
        source_ref (Optional[str]): Optional source reference.
        memory_id (Optional[str]): Optional memory id override.

    Returns:
        str: Memory id.
    """
    now = utc_now_iso()
    store_path, data = load_store(repo_root, store)
    memories = data.setdefault("memories", [])
    entry_id = memory_id or generate_memory_id()
    if any(item.get("memory_id") == entry_id for item in memories):
        raise ValueError(f"memory_id already exists: {entry_id}")

    entry = {
        "memory_id": entry_id,
        "title": title,
        "content": content,
        "tags": tags,
        "state": "active",
        "created_at": now,
        "updated_at": now,
        "created_by": agent_id,
        "updated_by": agent_id,
        "deleted_at": None,
        "notes": notes,
        "source": {"kind": source_kind or "agent", "ref": source_ref},
    }
    memories.append(entry)
    data["updated_at"] = now
    write_store(store_path, data)
    return entry_id


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Add a memory entry using the ToolCommandAPI contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing the new memory id on success.

    Raises:
        None: All errors are returned as CommandResult payloads.

    Contract:
        - Requires agent_id, store, title, and content in the payload.
        - Enforces certification, feature, and work mode guards.
        - Returns memory_id and store in the output payload.
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
        title = require_string(payload, "title", command_name)
        content = require_string(payload, "content", command_name)
        tags = optional_list(payload, "tags", command_name=command_name, default=[])
        tags_csv = optional_string(payload, "tags_csv", command_name=command_name)
        notes = optional_string(payload, "notes", command_name=command_name)
        source_kind = optional_string(payload, "source_kind", command_name=command_name)
        source_ref = optional_string(payload, "source_ref", command_name=command_name)
        memory_id = optional_string(payload, "memory_id", command_name=command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    try:
        ensure_certified(repo_root, agent_id)
        ensure_feature_enabled(repo_root, "memory", "write memory")
        ensure_work_mode(repo_root, work_id, "write memory")

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
            entry_id = add_memory(
                repo_root=repo_root,
                store=store,
                title=title,
                content=content,
                tags=_parse_tags(tags, tags_csv),
                agent_id=agent_id,
                notes=notes,
                source_kind=source_kind,
                source_ref=source_ref,
                memory_id=memory_id,
            )
        finally:
            lease.release_lock(repo_root, store_path, agent_id)
    except Exception as exc:
        return exception_result(
            command_name,
            exc,
            details={"store": store, "agent_id": agent_id},
        )

    return ok_result(output={"memory_id": entry_id, "store": store})


def main() -> None:
    """
    CLI entrypoint for memory adds.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """
    parser = argparse.ArgumentParser(description="Add a memory entry")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--store", required=True, choices=["user", "system"], help="Memory store name")
    parser.add_argument("--title", required=True, help="Memory title")
    parser.add_argument("--content", required=True, help="Memory content")
    parser.add_argument("--tag", action="append", default=None, help="Repeatable tag")
    parser.add_argument("--tags", default=None, help="Comma-separated tags")
    parser.add_argument("--notes", default=None, help="Optional notes")
    parser.add_argument("--source-kind", default=None, help="Optional source kind")
    parser.add_argument("--source-ref", default=None, help="Optional source reference")
    parser.add_argument("--memory-id", default=None, help="Optional memory id override")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "agent_id": args.agent_id,
        "work_id": args.work_id,
        "store": args.store,
        "title": args.title,
        "content": args.content,
        "tags": args.tag,
        "tags_csv": args.tags,
        "notes": args.notes,
        "source_kind": args.source_kind,
        "source_ref": args.source_ref,
        "memory_id": args.memory_id,
    }
    context = ExecutionContext(
        command_name="memory_add",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("memory_add failed: %s", result.errors)
        raise SystemExit(1)
    logger.info("memory added: %s", result.output.get("memory_id"))


if __name__ == "__main__":
    main()
