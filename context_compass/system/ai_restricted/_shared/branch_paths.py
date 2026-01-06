"""
context_compass.system.ai_restricted._shared.branch_paths

Branch-aware helpers for context_compass branch identifiers.

Contracts
- The active branch is stored in SQLite (user DB current_branch table).
- Branch state and queues live in SQLite (no filesystem branch roots).
- self_context remains global (not branch-scoped).
"""

from pathlib import Path
from context_compass.system.ai_restricted._shared import branch_registry_store


def _validate_branch_name(branch_name: str) -> str:
    """
    Validate a branch name for safe on-disk usage.

    Args:
        branch_name (str): Branch name.

    Returns:
        str: Normalized branch name.

    Raises:
        ValueError: If the branch name is empty or unsafe.
    """
    normalized = str(branch_name).strip()
    if not normalized:
        raise ValueError("branch_name is required")
    branch_path = Path(normalized)
    if branch_path.is_absolute():
        raise ValueError("branch_name must be a relative path")
    if any(part in ("..", "") for part in branch_path.parts):
        raise ValueError("branch_name contains invalid path segments")
    return normalized


def load_current_branch(repo_root: Path) -> str:
    """
    Load the active branch name from SQLite.

    Args:
        repo_root (Path): Repository root.

    Returns:
        str: Active branch name.

    Raises:
        FileNotFoundError: If current branch is not recorded.
        ValueError: If the stored payload is invalid.
    """
    branch_name = branch_registry_store.load_current_branch(repo_root, actor_id="system:branch_paths")
    return _validate_branch_name(branch_name)

