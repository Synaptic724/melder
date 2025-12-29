"""Run cleanup scripts registered under tools/cleanup_agents."""

import argparse
import logging
import sys
from pathlib import Path

from context_compass.tools._shared import agent_presence
from context_compass.tools._shared.certification_guard import ensure_certified


def run_cleanup(repo_root: Path, agent_id: str) -> list[str]:
    """
    Run all cleanup scripts for the repo.

    Contract:
    - Executes cleanup(repo_root, agent_id, now=...) for each script in tools/cleanup_agents.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent id executing cleanup.

    Returns:
        list[str]: Cleanup script filenames that were executed.
    """
    return agent_presence.run_cleanup_scripts(repo_root, agent_id)


def main() -> None:
    """
    CLI entrypoint for cleanup execution.
    """
    parser = argparse.ArgumentParser(description="Run context_compass cleanup scripts")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--mode", default="agent", help="Agent mode")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    ensure_certified(repo_root)
    executed = run_cleanup(repo_root, args.agent_id)
    agent_presence.record_heartbeat(
        repo_root,
        agent_id=args.agent_id,
        mode=args.mode,
        current_task_id=None,
        current_target=None,
        notes=None,
        command_name="agent_cleanup",
        command_args=sys.argv[1:],
        run_cleanup=False,
    )
    logger.info("cleanup scripts executed: %s", executed)


if __name__ == "__main__":
    main()
