"""
Update an existing memory entry in the user or system memory store.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from context_compass.tools import lease
from context_compass.tools._shared import agent_presence
from context_compass.tools._shared.certification_guard import ensure_certified
from context_compass.tools._shared.feature_guard import ensure_feature_enabled
from context_compass.tools._shared.memory_store import (
    find_memory,
    load_store,
    memory_locks_dir,
    normalize_tags,
    write_store,
)
from context_compass.tools._shared.timeutils import utc_now_iso
from context_compass.tools._shared.work_mode_guard import ensure_work_mode
from context_compass.tools._shared.json_io import load_json


def _default_policies() -> dict:
    """
    Return default policy values for memory updates.

    Returns:
        dict: Default policy values.
    """
    return {"lease_ttl_seconds": 300, "lock_wait_seconds": 10}


def _load_policies(repo_root: Path) -> dict:
    """
    Load policy values from config with defaults.

    Args:
        repo_root (Path): Repository root.

    Returns:
        dict: Effective policies.
    """
    policies = _default_policies()
    config_path = repo_root / "context_compass" / "config" / "policies.json"
    if config_path.exists():
        data = load_json(config_path)
        if isinstance(data, dict):
            policies.update({key: value for key, value in data.items() if key in policies})
    return policies


def _parse_tags(raw_tags: Optional[list[str]], raw_csv: Optional[str]) -> Optional[list[str]]:
    """
    Parse tag inputs from flags.

    Args:
        raw_tags (Optional[list[str]]): Repeated tag values.
        raw_csv (Optional[str]): Comma-separated tags.

    Returns:
        Optional[list[str]]: Normalized tags or None if no tags provided.
    """
    tags: list[str] = []
    if raw_tags:
        tags.extend(raw_tags)
    if raw_csv:
        tags.extend([part.strip() for part in raw_csv.split(",")])
    if not tags:
        return None
    return normalize_tags(tags)


def update_memory(
    repo_root: Path,
    store: str,
    memory_id: str,
    agent_id: str,
    title: Optional[str],
    content: Optional[str],
    tags: Optional[list[str]],
    notes: Optional[str],
    source_kind: Optional[str],
    source_ref: Optional[str],
    state: Optional[str],
) -> dict:
    """
    Update a memory entry by id.

    Args:
        repo_root (Path): Repository root.
        store (str): Store name (user/system).
        memory_id (str): Memory identifier.
        agent_id (str): Agent identifier.
        title (Optional[str]): Optional title update.
        content (Optional[str]): Optional content update.
        tags (Optional[list[str]]): Optional tags update.
        notes (Optional[str]): Optional notes update.
        source_kind (Optional[str]): Optional source kind update.
        source_ref (Optional[str]): Optional source reference update.
        state (Optional[str]): Optional state update (active/archived).

    Returns:
        dict: Updated memory entry.
    """
    now = utc_now_iso()
    store_path, data = load_store(repo_root, store)
    memories = data.setdefault("memories", [])
    entry = find_memory(memories, memory_id)
    if entry is None:
        raise ValueError(f"memory_id not found: {memory_id}")

    if title is not None:
        entry["title"] = title
    if content is not None:
        entry["content"] = content
    if tags is not None:
        entry["tags"] = tags
    if notes is not None:
        entry["notes"] = notes
    if source_kind is not None or source_ref is not None:
        entry["source"] = {"kind": source_kind or entry.get("source", {}).get("kind"), "ref": source_ref}
    if state is not None:
        if state not in ("active", "archived"):
            raise ValueError("state must be active or archived")
        entry["state"] = state

    entry["updated_at"] = now
    entry["updated_by"] = agent_id
    data["updated_at"] = now
    write_store(store_path, data)
    return entry


def main() -> None:
    """
    CLI entrypoint for memory updates.
    """
    parser = argparse.ArgumentParser(description="Update a memory entry")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--mode", default="agent", help="Agent mode for heartbeat")
    parser.add_argument("--store", required=True, choices=["user", "system"], help="Memory store name")
    parser.add_argument("--memory-id", required=True, help="Memory identifier")
    parser.add_argument("--title", default=None, help="Optional title update")
    parser.add_argument("--content", default=None, help="Optional content update")
    parser.add_argument("--tag", action="append", default=None, help="Repeatable tag")
    parser.add_argument("--tags", default=None, help="Comma-separated tags")
    parser.add_argument("--notes", default=None, help="Optional notes update")
    parser.add_argument("--source-kind", default=None, help="Optional source kind update")
    parser.add_argument("--source-ref", default=None, help="Optional source reference update")
    parser.add_argument("--state", default=None, choices=["active", "archived"], help="Optional state update")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    ensure_certified(repo_root, args.agent_id)
    ensure_feature_enabled(repo_root, "memory", "update memory")
    ensure_work_mode(repo_root, args.work_id, "update memory")

    policies = _load_policies(repo_root)
    locks_dir = memory_locks_dir(repo_root)
    locks_dir.mkdir(parents=True, exist_ok=True)
    store_path, _ = load_store(repo_root, args.store)
    lease.acquire_lock(locks_dir, store_path, args.agent_id, policies["lease_ttl_seconds"], args.work_id)
    try:
        entry = update_memory(
            repo_root=repo_root,
            store=args.store,
            memory_id=args.memory_id,
            agent_id=args.agent_id,
            title=args.title,
            content=args.content,
            tags=_parse_tags(args.tag, args.tags),
            notes=args.notes,
            source_kind=args.source_kind,
            source_ref=args.source_ref,
            state=args.state,
        )
    finally:
        lease.release_lock(locks_dir, store_path, args.agent_id)

    agent_presence.record_heartbeat(
        repo_root,
        agent_id=args.agent_id,
        mode=args.mode,
        current_task_id=args.work_id,
        current_target=str(store_path),
        notes=None,
        command_name="memory_update",
        command_args=sys.argv[1:],
    )
    logger.info("memory updated: %s", entry.get("memory_id"))


if __name__ == "__main__":
    main()
