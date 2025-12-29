"""Check in an agent and start its heartbeat profile."""

import argparse
import logging
import sys
from pathlib import Path

from context_compass.tools._shared import agent_presence
from context_compass.tools._shared.certification_guard import ensure_certified


def main() -> None:
    """
    CLI entrypoint for agent checkin.
    """
    parser = argparse.ArgumentParser(description="Check in an agent and start heartbeat tracking")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--mode", default="agent", help="Agent mode")
    parser.add_argument("--current-task-id", default=None, help="Current task id")
    parser.add_argument("--current-target", default=None, help="Current target path")
    parser.add_argument("--notes", default=None, help="Optional notes")
    parser.add_argument("--agent-kind", default=None, help="Agent kind (codex/gemini/etc)")
    parser.add_argument("--model-name", default=None, help="Model name or variant")
    parser.add_argument("--runtime", default=None, help="Runtime identifier (cli/api/ci)")
    parser.add_argument("--owner-id", default=None, help="Lock owner id override")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    ensure_certified(repo_root)

    agent_presence.checkin(
        repo_root,
        agent_id=args.agent_id,
        mode=args.mode,
        current_task_id=args.current_task_id,
        current_target=args.current_target,
        notes=args.notes,
        command_name="agent_checkin",
        command_args=sys.argv[1:],
        agent_kind=args.agent_kind,
        model_name=args.model_name,
        runtime=args.runtime,
        owner_id=args.owner_id,
    )
    logger.info("agent checked in: %s", args.agent_id)


if __name__ == "__main__":
    main()
