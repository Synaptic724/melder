"""Summarize agent profile status and heartbeat activity."""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from context_compass.tools._shared import agent_presence
from context_compass.tools._shared.certification_guard import ensure_certified
from context_compass.tools._shared.json_io import load_json, write_json_atomic
from context_compass.tools._shared.timeutils import parse_iso8601, utc_now_iso


def _default_policies() -> dict:
    """
    Return default policy values for agent sweeps.

    Returns:
        dict: Default policy values.
    """
    return {"agent_heartbeat_stale_seconds": 14400}


def _load_policies(repo_root: Path) -> dict:
    """
    Load policy configuration with defaults applied.

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
            policies.update({k: v for k, v in data.items() if k in policies})
    return policies


def _is_stale(last_heartbeat_at: Optional[str], now: str, stale_seconds: int) -> Optional[bool]:
    """
    Return whether the heartbeat is stale under the threshold.

    Args:
        last_heartbeat_at (Optional[str]): Last heartbeat timestamp.
        now (str): Current timestamp.
        stale_seconds (int): Stale threshold in seconds.

    Returns:
        Optional[bool]: True if stale, False if not stale, or None if unknown.
    """
    if not last_heartbeat_at:
        return None
    try:
        elapsed = (parse_iso8601(now) - parse_iso8601(last_heartbeat_at)).total_seconds()
    except (TypeError, ValueError):
        return None
    return elapsed >= stale_seconds


def sweep_profiles(repo_root: Path, now: Optional[str] = None) -> dict:
    """
    Sweep agent profiles and summarize status counts.

    Args:
        repo_root (Path): Repository root.
        now (Optional[str]): Override current timestamp.

    Returns:
        dict: Sweep summary payload.
    """
    current = now or utc_now_iso()
    policies = _load_policies(repo_root)
    stale_seconds = int(policies["agent_heartbeat_stale_seconds"])
    agents_dir = repo_root / "context_compass" / "self_context" / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)

    summaries: list[dict] = []
    counts = {"total": 0, "active": 0, "inactive": 0, "stale": 0, "unknown": 0, "stale_by_threshold": 0}

    for path in sorted(agents_dir.glob("*.profile.json"), key=lambda p: p.name):
        data = load_json(path)
        if not isinstance(data, dict):
            counts["unknown"] += 1
            continue
        agent_id = str(data.get("agent_id") or path.stem.replace(".profile", ""))
        status = str(data.get("status") or "unknown")
        last_heartbeat = data.get("last_heartbeat_at")
        stale_by_threshold = _is_stale(last_heartbeat, current, stale_seconds)
        summaries.append(
            {
                "agent_id": agent_id,
                "status": status,
                "last_heartbeat_at": last_heartbeat,
                "stale_by_threshold": stale_by_threshold,
            }
        )
        counts["total"] += 1
        if status in counts:
            counts[status] += 1
        else:
            counts["unknown"] += 1
        if stale_by_threshold is True:
            counts["stale_by_threshold"] += 1

    return {
        "schema_version": 1,
        "updated_at": current,
        "counts": counts,
        "agents": summaries,
    }


def main() -> None:
    """
    CLI entrypoint for agent profile sweeps.
    """
    parser = argparse.ArgumentParser(description="Summarize agent profile status counts")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--mode", default="agent", help="Agent mode")
    parser.add_argument("--now", default=None, help="Override current timestamp (ISO-8601)")
    parser.add_argument("--output", default=None, help="Optional output JSON path for sweep results")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    ensure_certified(repo_root, args.agent_id)
    agent_presence.record_heartbeat(
        repo_root,
        agent_id=args.agent_id,
        mode=args.mode,
        current_task_id=None,
        current_target=None,
        notes=None,
        command_name="agent_sweep",
        command_args=sys.argv[1:],
    )
    payload = sweep_profiles(repo_root, now=args.now)

    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = repo_root / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        write_json_atomic(output_path, payload)
        logger.info("agent sweep written to %s", output_path)
    else:
        logger.info("agent sweep counts: %s", payload["counts"])


if __name__ == "__main__":
    main()
