"""
Read memory entries from the user or system memory store.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_bool,
    optional_int,
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
from context_compass.system.ai_restricted._shared.memory_store import load_store
from context_compass.system.ai_restricted._shared.timeutils import utc_now_iso
from context_compass.system.ai_restricted._shared.work_mode_guard import ensure_work_mode
from context_compass.system.ai_restricted._shared.json_io import dump_minified
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)


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


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Read memory entries using the ToolCommandAPI contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing the memory read payload.

    Raises:
        None: All errors are returned as CommandResult payloads.

    Contract:
        - Requires agent_id and store in the payload.
        - Optional filters include memory_id, recent, and include_archived.
        - JSON output paths are not supported; results are returned in the payload.
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
        memory_id = optional_string(payload, "memory_id", command_name=command_name)
        recent = optional_int(payload, "recent", command_name=command_name)
        include_archived = optional_bool(
            payload, "include_archived", command_name=command_name, default=False
        )
        output_path_value = optional_string(
            payload, "output_path", command_name=command_name
        )
    except PayloadError as exc:
        return payload_error_result(command_name, exc)
    if output_path_value is not None:
        return payload_error_result(
            command_name,
            PayloadError(
                code="payload_unsupported",
                details={
                    "command_name": command_name,
                    "field": "output_path",
                    "message": "output_path is not supported; memory_read returns payload only.",
                },
            ),
        )

    try:
        ensure_certified(repo_root, agent_id)
        ensure_feature_enabled(repo_root, "memory", "read memory")
        ensure_work_mode(repo_root, work_id, "read memory")

        read_payload = read_memory(
            repo_root=repo_root,
            store=store,
            memory_id=memory_id,
            recent=recent,
            include_archived=include_archived,
        )

        output: dict = {
            "store": store,
            "memory_id": memory_id,
            "recent": recent,
            "include_archived": include_archived,
            "memories": read_payload.get("memories", []),
        }
        return ok_result(output=output, artifacts=[])
    except Exception as exc:
        return exception_result(
            command_name,
            exc,
            details={"store": store, "agent_id": agent_id},
        )


def main() -> None:
    """
    CLI entrypoint for memory reads.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """
    parser = argparse.ArgumentParser(description="Read memory entries")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--store", required=True, choices=["user", "system"], help="Memory store name")
    parser.add_argument("--memory-id", default=None, help="Optional memory identifier")
    parser.add_argument("--recent", type=int, default=None, help="Return only N most recent")
    parser.add_argument("--include-archived", action="store_true", help="Include archived entries")
    parser.add_argument(
        "--output",
        default=None,
        help="Deprecated: JSON output files are no longer supported.",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "agent_id": args.agent_id,
        "work_id": args.work_id,
        "store": args.store,
        "memory_id": args.memory_id,
        "recent": args.recent,
        "include_archived": args.include_archived,
        "output_path": args.output,
    }
    context = ExecutionContext(
        command_name="memory_read",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("memory_read failed: %s", result.errors)
        raise SystemExit(1)
    sys.stdout.write(dump_minified(result.output) + "\n")


if __name__ == "__main__":
    main()
