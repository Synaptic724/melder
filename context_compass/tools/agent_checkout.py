"""Check out an agent and mark it inactive."""

import argparse
import logging
import sys
from pathlib import Path

from context_compass.tools._shared import agent_presence
from context_compass.tools._shared.certification_guard import ensure_certified


def main() -> None:
    """
    CLI entrypoint for agent checkout.
    """
    parser = argparse.ArgumentParser(description="Check out an agent and stop heartbeat tracking")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--mode", default="agent", help="Agent mode")
    parser.add_argument("--notes", default=None, help="Optional notes")
    parser.add_argument("--owner-id", default=None, help="Lock owner id override")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    ensure_certified(repo_root, args.owner_id or args.agent_id)

    agent_presence.checkout(
        repo_root,
        agent_id=args.agent_id,
        mode=args.mode,
        notes=args.notes,
        command_name="agent_checkout",
        command_args=sys.argv[1:],
        owner_id=args.owner_id,
    )
    logger.info("agent checked out: %s", args.agent_id)


if __name__ == "__main__":
    main()
