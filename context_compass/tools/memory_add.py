"""
Add a memory entry to the user or system memory store.
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
    generate_memory_id,
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
    Return default policy values for memory writes.

    Returns:
        dict: Default policy values.
    """
    return {"lease_ttl_seconds": 300, "lock_wait_seconds": 10}


def _load_policies(repo_root: Path) -> dict:
    """
    Load memory policy values from config with defaults.

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


def main() -> None:
    """
    CLI entrypoint for memory adds.
    """
    parser = argparse.ArgumentParser(description="Add a memory entry")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--mode", default="agent", help="Agent mode for heartbeat")
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

    repo_root = Path(args.repo_root).resolve()
    ensure_certified(repo_root)
    ensure_feature_enabled(repo_root, "memory", "write memory")
    ensure_work_mode(repo_root, args.work_id, "write memory")

    policies = _load_policies(repo_root)
    locks_dir = memory_locks_dir(repo_root)
    locks_dir.mkdir(parents=True, exist_ok=True)
    store_path, _ = load_store(repo_root, args.store)
    lease.acquire_lock(locks_dir, store_path, args.agent_id, policies["lease_ttl_seconds"], args.work_id)
    try:
        memory_id = add_memory(
            repo_root=repo_root,
            store=args.store,
            title=args.title,
            content=args.content,
            tags=_parse_tags(args.tag, args.tags),
            agent_id=args.agent_id,
            notes=args.notes,
            source_kind=args.source_kind,
            source_ref=args.source_ref,
            memory_id=args.memory_id,
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
        command_name="memory_add",
        command_args=sys.argv[1:],
    )
    logger.info("memory added: %s", memory_id)


if __name__ == "__main__":
    main()
