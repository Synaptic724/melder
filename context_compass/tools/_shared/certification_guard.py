"""Certification gate helpers for context_compass tooling."""

import logging
from pathlib import Path
from typing import Optional

from context_compass.tools._shared.json_io import load_json

APPROVAL_TOKEN = "CERTIFY: APPROVED"
CHANGES_TOKEN = "CERTIFY: CHANGES"


def default_certification_state() -> dict:
    """
    Return a default certification state payload.

    Returns:
        dict: Default certification state data.
    """
    return {
        "schema_version": 1,
        "state": "UNCERTIFIED",
        "certified": False,
        "certified_at": None,
        "approved_at": None,
        "approval_token": None,
        "approved_by": None,
        "self_certification_hash": None,
        "notes": None,
    }


def certification_profile_path(repo_root: Path, agent_id: str) -> Path:
    """
    Return the agent profile path that stores certification state.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.

    Returns:
        Path: Path to the agent profile JSON.
    """
    return repo_root / "context_compass" / "self_context" / "agents" / f"{agent_id}.profile.json"


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
    profile_path = certification_profile_path(repo_root, agent_id)
    if not profile_path.exists():
        logger.error("Missing agent profile for certification: %s", profile_path)
        raise SystemExit(1)
    profile = load_json(profile_path)
    if not isinstance(profile, dict):
        logger.error("Invalid agent profile JSON: %s", profile_path)
        raise SystemExit(1)
    state = profile.get("certification_state")
    if not isinstance(state, dict) or not is_certified(state):
        logger.error("Certification required before running tools.")
        raise SystemExit(1)
