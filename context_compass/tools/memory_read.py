"""
Read memory entries from the user or system memory store.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from context_compass.tools._shared import agent_presence
from context_compass.tools._shared.certification_guard import ensure_certified
from context_compass.tools._shared.feature_guard import ensure_feature_enabled
from context_compass.tools._shared.memory_store import load_store
from context_compass.tools._shared.timeutils import utc_now_iso
from context_compass.tools._shared.work_mode_guard import ensure_work_mode
from context_compass.tools._shared.json_io import dump_minified, write_json_atomic


def _filter_memories(
    memories: list[dict],
    memory_id: Optional[str],
    include_archived: bool,
) -> list[dict]:
    """
    Filter memories by id and state.

    Args:
        memories (list[dict]): Memory entries.
        memory_id (Optional[str]): Optional memory id filter.
        include_archived (bool): Whether to include archived entries.

    Returns:
        list[dict]: Filtered memories.
    """
    filtered: list[dict] = []
    for entry in memories:
        if memory_id and entry.get("memory_id") != memory_id:
            continue
        state = entry.get("state")
        if state == "archived" and not include_archived:
            continue
        if state == "deleted":
            continue
        filtered.append(entry)
    return filtered


def _sort_memories(memories: list[dict]) -> list[dict]:
    """
    Sort memories by updated_at descending.

    Args:
        memories (list[dict]): Memory entries.

    Returns:
        list[dict]: Sorted memories.
    """
    return sorted(memories, key=lambda entry: entry.get("updated_at") or "", reverse=True)


def read_memory(
    repo_root: Path,
    store: str,
    memory_id: Optional[str],
    recent: Optional[int],
    include_archived: bool,
) -> dict:
    """
    Read memory entries from a store.

    Args:
        repo_root (Path): Repository root.
        store (str): Store name (user/system).
        memory_id (Optional[str]): Optional memory id filter.
        recent (Optional[int]): Optional recent limit.
        include_archived (bool): Whether to include archived entries.

    Returns:
        dict: Memory read payload.
    """
    now = utc_now_iso()
    store_path, data = load_store(repo_root, store)
    memories = data.get("memories", [])
    if not isinstance(memories, list):
        memories = []

    filtered = _filter_memories(memories, memory_id, include_archived)
    sorted_memories = _sort_memories(filtered)
    if recent is not None and recent > 0:
        sorted_memories = sorted_memories[:recent]

    return {
        "schema_version": 1,
        "generated_at": now,
        "store": store,
        "filters": {
            "memory_id": memory_id,
            "recent": recent,
            "include_archived": include_archived,
        },
        "memories": sorted_memories,
    }


def main() -> None:
    """
    CLI entrypoint for memory reads.
    """
    parser = argparse.ArgumentParser(description="Read memory entries")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--mode", default="agent", help="Agent mode for heartbeat")
    parser.add_argument("--store", required=True, choices=["user", "system"], help="Memory store name")
    parser.add_argument("--memory-id", default=None, help="Optional memory identifier")
    parser.add_argument("--recent", type=int, default=None, help="Return only N most recent")
    parser.add_argument("--include-archived", action="store_true", help="Include archived entries")
    parser.add_argument("--output", default=None, help="Optional output JSON path")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    ensure_certified(repo_root, args.agent_id)
    ensure_feature_enabled(repo_root, "memory", "read memory")
    ensure_work_mode(repo_root, args.work_id, "read memory")

    payload = read_memory(
        repo_root=repo_root,
        store=args.store,
        memory_id=args.memory_id,
        recent=args.recent,
        include_archived=args.include_archived,
    )

    store_path, _ = load_store(repo_root, args.store)
    agent_presence.record_heartbeat(
        repo_root,
        agent_id=args.agent_id,
        mode=args.mode,
        current_task_id=args.work_id,
        current_target=str(store_path),
        notes=None,
        command_name="memory_read",
        command_args=sys.argv[1:],
    )

    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = repo_root / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        write_json_atomic(output_path, payload)
        logger.info("memory output written: %s", output_path)
        return

    sys.stdout.write(dump_minified(payload) + "\n")


if __name__ == "__main__":
    main()
