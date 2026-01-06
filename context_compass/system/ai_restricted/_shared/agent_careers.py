"""
Career discovery helpers for onboarding-driven agent profiles.

Purpose
- Provide a single place to discover the available agent careers.
- Enforce the rule that "general" is shared baseline content, not a career.
"""

from __future__ import annotations

from pathlib import Path


CAREERS_DIRNAME = "careers"
GENERAL_CAREER_NAME = "general"


def careers_root(repo_root: Path) -> Path:
    """
    Resolve the filesystem root for onboarding careers.

    Args:
        repo_root (Path): Repository root directory.

    Returns:
        Path: Directory containing career subfolders.
    """

    return repo_root / "context_compass" / "onboarding" / "agent" / CAREERS_DIRNAME


def list_careers(repo_root: Path) -> list[str]:
    """
    List available careers under onboarding/agent/careers.

    Args:
        repo_root (Path): Repository root directory.

    Returns:
        list[str]: Sorted career names excluding "general".

    Raises:
        ValueError: If the careers directory is missing or empty.
    """

    root = careers_root(repo_root)
    if not root.exists():
        raise ValueError(f"careers directory missing: {root}")
    careers: list[str] = []
    for entry in root.iterdir():
        if not entry.is_dir():
            continue
        if entry.name == GENERAL_CAREER_NAME:
            continue
        careers.append(entry.name)
    careers.sort()
    if not careers:
        raise ValueError(f"no careers found under: {root}")
    return careers
