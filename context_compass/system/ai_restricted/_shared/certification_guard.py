"""Certification gate helpers for context_compass tooling."""

import logging
from pathlib import Path
from typing import Optional

from context_compass.system.ai_restricted._shared import agent_profile_store
from context_compass.system.ai_restricted._shared import certification_state
from context_compass.system.ai_restricted.database_management import sqlite_crud

APPROVAL_TOKEN = "CERTIFY: APPROVED"
CHANGES_TOKEN = "CERTIFY: CHANGES"


def default_certification_state() -> dict:
    """
    Return a default certification state payload.

    Returns:
        dict: Default certification state data.
    """

    return certification_state.default_certification_state()


def parse_approval_token(text: str) -> Optional[str]:
    """
    Parse an approval token from user text.

    Args:
        text (str): User response text.

    Returns:
        Optional[str]: "APPROVED", "CHANGES", or None.
    """
    stripped = text.strip()
    if stripped == APPROVAL_TOKEN:
        return "APPROVED"
    if stripped.startswith(CHANGES_TOKEN):
        return "CHANGES"
    return None


def is_certified(state: dict) -> bool:
    """
    Return True if the certification state is certified.

    Args:
        state (dict): Certification state data.

    Returns:
        bool: True when certified.
    """
    return state.get("state") == "CERTIFIED" and state.get("certified") is True


def ensure_certified(repo_root: Path, agent_id: str) -> None:
    """
    Fail fast if the repo is not in a certified state.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.

    Raises:
        SystemExit: If certification is missing or not certified.
    """
    logger = logging.getLogger(__name__)
    try:
        snapshot = agent_profile_store.load_profile(repo_root, agent_id, actor_id=agent_id)
    except sqlite_crud.SqliteCrudError as exc:
        logger.error(
            "Failed to load agent profile from SQLite for certification: %s",
            exc.meaning,
        )
        raise SystemExit(1)
    if not snapshot.exists:
        logger.error("Missing agent profile record for certification: %s", agent_id)
        raise SystemExit(1)
    state = snapshot.payload.get("certification_state")
    if not isinstance(state, dict) or not is_certified(state):
        logger.error("Certification required before running tools.")
        raise SystemExit(1)
