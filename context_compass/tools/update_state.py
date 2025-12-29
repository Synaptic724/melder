"""
context_compass.tools.update_state

State mutation helpers for context_compass artifacts.

Contracts
- Acquire state locks before any write.
- Re-read current state after acquiring the lock.
- Write JSON atomically with minified output.
- Update agent heartbeat for the executing agent.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from context_compass.tools import lease
from context_compass.tools._shared import agent_presence, branch_paths
from context_compass.tools._shared.certification_guard import ensure_certified
from context_compass.tools._shared.feature_guard import ensure_feature_enabled
from context_compass.tools._shared.work_mode_guard import ensure_work_mode
from context_compass.tools._shared.json_io import load_json, write_json_atomic
from context_compass.tools._shared.timeutils import utc_now_iso


def _default_repo_state(repo_root: Path, now: str) -> dict:
    """
    Return a default repo_state payload.

    Args:
        repo_root (Path): Repository root.
        now (str): Current timestamp.

    Returns:
        dict: Repo state payload.
    """
    return {
        "schema_version": 1,
        "repo_id": None,
        "repo_root": str(repo_root),
        "git": {"head": None},
        "scan_counter": 0,
        "last_scan_id": None,
        "last_scan_at": None,
        "scanner_version": None,
        "template_versions": {"file_ctx": None, "dir_ctx": None},
        "lifecycle": {
            "stage": "new",
            "assessment": "Initial assessment pending",
            "confidence": 0.0,
            "assessed_at": None,
        },
        "tooling_policy": {
            "mode": "restricted",
            "disabled_features": ["scan", "context_profiles"],
            "notes": "Auto-restricted for new repos; update repo_state to enable.",
            "updated_at": now,
        },
        "created_at": now,
        "updated_at": now,
    }


def _load_repo_state(repo_root: Path, path: Path, now: str) -> dict:
    """
    Load repo_state.json or initialize a default structure.

    Args:
        repo_root (Path): Repository root.
        path (Path): Repo state path.
        now (str): Current timestamp.

    Returns:
        dict: Repo state payload.
    """
    if path.exists():
        data = load_json(path)
        if isinstance(data, dict):
            return data
    return _default_repo_state(repo_root, now)


def _work_queue_path(repo_root: Path, bucket: str, work_type: str) -> Path:
    """
    Resolve the work_management queue path.

    Args:
        repo_root (Path): Repository root.
        bucket (str): Work bucket.
        work_type (str): Work type.

    Returns:
        Path: Queue file path.
    """
    filename = {"epic": "epics.json", "story": "stories.json", "task": "tasks.json"}[work_type]
    return branch_paths.work_root(repo_root) / bucket / filename


def bump_scan_state(
    repo_root: Path,
    scan_id: str,
    scanned_at: str,
    scanner_version: Optional[str],
    repo_id: Optional[str],
    git_head: Optional[str],
    template_versions: Optional[dict],
    owner_id: str,
) -> dict:
    """
    Update repo_state.json with the latest scan metadata.

    Args:
        repo_root (Path): Repository root.
        scan_id (str): Scan identifier.
        scanned_at (str): Scan timestamp.
        scanner_version (Optional[str]): Scanner version.
        repo_id (Optional[str]): Repo identifier override.
        git_head (Optional[str]): Git head override.
        template_versions (Optional[dict]): Template version overrides.
        owner_id (str): Lock owner id.

    Returns:
        dict: Updated repo state payload.
    """
    now = utc_now_iso()
    state_path = branch_paths.state_root(repo_root) / "repo_state.json"
    locks_dir = branch_paths.state_root(repo_root) / "locks"
    locks_dir.mkdir(parents=True, exist_ok=True)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    policies = agent_presence.load_policies(repo_root)

    lease.acquire_lock(locks_dir, state_path, owner_id, ttl_seconds=policies["lease_ttl_seconds"])
    try:
        state = _load_repo_state(repo_root, state_path, now)
        state["scan_counter"] = int(state.get("scan_counter") or 0) + 1
        state["last_scan_id"] = scan_id
        state["last_scan_at"] = scanned_at
        if repo_id is not None:
            state["repo_id"] = repo_id
        if git_head is not None:
            state.setdefault("git", {})["head"] = git_head
        if scanner_version is not None:
            state["scanner_version"] = scanner_version
        if template_versions:
            state.setdefault("template_versions", {}).update(template_versions)
        state["updated_at"] = now
        if state.get("created_at") is None:
            state["created_at"] = now
        write_json_atomic(state_path, state)
    finally:
        lease.release_lock(locks_dir, state_path, owner_id)
    return state


def update_work_item_state(
    repo_root: Path,
    bucket: str,
    work_type: str,
    work_id: str,
    owner_id: str,
    state: Optional[str] = None,
    attempts: Optional[int] = None,
    last_error_ref: Optional[str] = None,
    priority: Optional[int] = None,
) -> dict:
    """
    Update fields for a work item in a work_management queue.

    Args:
        repo_root (Path): Repository root.
        bucket (str): Work bucket.
        work_type (str): Work type.
        work_id (str): Work identifier.
        owner_id (str): Lock owner id.
        state (Optional[str]): New state.
        attempts (Optional[int]): Attempts override.
        last_error_ref (Optional[str]): Error reference override.
        priority (Optional[int]): Priority override.

    Returns:
        dict: Updated work item payload.
    """
    queue_path = _work_queue_path(repo_root, bucket, work_type)
    if not queue_path.exists():
        raise FileNotFoundError(f"Queue not found: {queue_path}")
    locks_dir = branch_paths.state_root(repo_root) / "locks"
    locks_dir.mkdir(parents=True, exist_ok=True)
    policies = agent_presence.load_policies(repo_root)

    lease.acquire_lock(locks_dir, queue_path, owner_id, ttl_seconds=policies["lease_ttl_seconds"])
    try:
        data = load_json(queue_path)
        if not isinstance(data, dict):
            raise ValueError("Queue must be a JSON object")
        queue = data.get("queue", [])
        if not isinstance(queue, list):
            raise ValueError("Queue must contain a list")
        for item in queue:
            if item.get("work_id") != work_id:
                continue
            if state is not None:
                item["state"] = state
            if attempts is not None:
                item["attempts"] = attempts
            if last_error_ref is not None:
                item["last_error_ref"] = last_error_ref
            if priority is not None:
                item["priority"] = priority
            item["updated_at"] = utc_now_iso()
            data["updated_at"] = item["updated_at"]
            write_json_atomic(queue_path, data)
            return item
        raise ValueError(f"Work item not found: {work_id}")
    finally:
        lease.release_lock(locks_dir, queue_path, owner_id)


def main() -> None:
    """
    CLI entrypoint for update_state operations.
    """
    parser = argparse.ArgumentParser(description="Update context_compass state")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--mode", default="agent", help="Agent mode for heartbeat")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Update repo_state scan metadata")
    scan_parser.add_argument("--scan-id", required=True, help="Scan identifier")
    scan_parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    scan_parser.add_argument("--scanned-at", default=None, help="Scan timestamp override")
    scan_parser.add_argument("--scanner-version", default=None, help="Scanner version")
    scan_parser.add_argument("--repo-id", default=None, help="Repo identifier override")
    scan_parser.add_argument("--git-head", default=None, help="Git head override")
    scan_parser.add_argument("--file-template-version", default=None, help="File ctx template version")
    scan_parser.add_argument("--dir-template-version", default=None, help="Dir ctx template version")

    work_parser = subparsers.add_parser("work-item", help="Update a work item in a queue")
    work_parser.add_argument("--bucket", required=True, choices=["active", "backlog", "completed", "denied"])
    work_parser.add_argument("--work-type", required=True, choices=["epic", "story", "task"])
    work_parser.add_argument("--work-id", required=True, help="Work identifier")
    work_parser.add_argument("--state", default=None, help="New work item state")
    work_parser.add_argument("--attempts", type=int, default=None, help="Attempts override")
    work_parser.add_argument("--last-error-ref", default=None, help="Error reference override")
    work_parser.add_argument("--priority", type=int, default=None, help="Priority override")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    ensure_certified(repo_root)

    if args.command == "scan":
        ensure_feature_enabled(repo_root, "scan", "update scan state")
        ensure_work_mode(repo_root, args.work_id, "update scan state")
        scanned_at = args.scanned_at or utc_now_iso()
        templates = {}
        if args.file_template_version is not None:
            templates["file_ctx"] = args.file_template_version
        if args.dir_template_version is not None:
            templates["dir_ctx"] = args.dir_template_version
        bump_scan_state(
            repo_root,
            scan_id=args.scan_id,
            scanned_at=scanned_at,
            scanner_version=args.scanner_version,
            repo_id=args.repo_id,
            git_head=args.git_head,
            template_versions=templates or None,
            owner_id=args.agent_id,
        )
        agent_presence.record_heartbeat(
            repo_root,
            agent_id=args.agent_id,
            mode=args.mode,
            current_task_id=args.work_id,
            current_target=args.scan_id,
            notes=None,
            command_name="update_state scan",
            command_args=sys.argv[1:],
        )
        logger.info("scan state updated: %s", args.scan_id)
        return

    if args.command == "work-item":
        ensure_feature_enabled(repo_root, "work_management", "update work items")
        ensure_work_mode(repo_root, args.work_id, "update work items")
        update_work_item_state(
            repo_root,
            args.bucket,
            args.work_type,
            args.work_id,
            owner_id=args.agent_id,
            state=args.state,
            attempts=args.attempts,
            last_error_ref=args.last_error_ref,
            priority=args.priority,
        )
        agent_presence.record_heartbeat(
            repo_root,
            agent_id=args.agent_id,
            mode=args.mode,
            current_task_id=args.work_id,
            current_target=args.work_id,
            notes=None,
            command_name="update_state work-item",
            command_args=sys.argv[1:],
        )
        logger.info("work item updated: %s", args.work_id)


if __name__ == "__main__":
    main()
