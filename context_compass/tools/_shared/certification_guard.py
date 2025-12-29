"""Certification gate helpers for context_compass tooling."""

import logging
from pathlib import Path
from typing import Optional

from context_compass.tools._shared.json_io import load_json

APPROVAL_TOKEN = "CERTIFY: APPROVED"
CHANGES_TOKEN = "CERTIFY: CHANGES"


def certification_state_path(repo_root: Path) -> Path:
    """
    Return the certification state path for the repo.

    Args:
        repo_root (Path): Repository root.

    Returns:
        Path: Path to certification_state.json.
    """
    return repo_root / "context_compass" / "self_context" / "certification_state.json"


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


def ensure_certified(repo_root: Path) -> None:
    """
    Fail fast if the repo is not in a certified state.

    Args:
        repo_root (Path): Repository root.

    Raises:
        SystemExit: If certification is missing or not certified.
    """
    logger = logging.getLogger(__name__)
    state_path = certification_state_path(repo_root)
    if not state_path.exists():
        logger.error("Missing certification state: %s", state_path)
        raise SystemExit(1)
    state = load_json(state_path)
    if not isinstance(state, dict) or not is_certified(state):
        logger.error("Certification required before running tools.")
        raise SystemExit(1)
