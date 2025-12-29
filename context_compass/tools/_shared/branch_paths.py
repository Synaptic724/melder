"""
context_compass.tools._shared.branch_paths

Branch-aware path helpers for context_compass state and work queues.

Contracts
- The active branch is stored in context_compass/branch_management/current_branch.json.
- Branch state and queues live under context_compass/branch_management/<branch_name>/.
- self_context remains global (not branch-scoped).
"""

from pathlib import Path
from typing import Optional

from context_compass.tools._shared.json_io import load_json


def branch_management_root(repo_root: Path) -> Path:
    """
    Return the branch_management root directory.

    Args:
        repo_root (Path): Repository root.

    Returns:
        Path: branch_management root path.
    """
    return repo_root / "context_compass" / "branch_management"


def current_branch_path(repo_root: Path) -> Path:
    """
    Return the current_branch.json path.

    Args:
        repo_root (Path): Repository root.

    Returns:
        Path: Current branch pointer path.
    """
    return branch_management_root(repo_root) / "current_branch.json"


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
    Load the active branch name from current_branch.json.

    Args:
        repo_root (Path): Repository root.

    Returns:
        str: Active branch name.

    Raises:
        FileNotFoundError: If current_branch.json is missing.
        ValueError: If the file is invalid or missing branch_name.
    """
    path = current_branch_path(repo_root)
    if not path.exists():
        raise FileNotFoundError(
            "Missing current_branch.json; run context_compass/tools/branch_init.py first."
        )
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError("current_branch.json must be an object")
    branch_name = data.get("branch_name")
    if branch_name is None:
        raise ValueError("current_branch.json missing branch_name")
    return _validate_branch_name(str(branch_name))


def branch_root(repo_root: Path, branch_name: Optional[str] = None) -> Path:
    """
    Resolve the branch root directory for state and queues.

    Args:
        repo_root (Path): Repository root.
        branch_name (Optional[str]): Override branch name.

    Returns:
        Path: Branch root path.
    """
    name = _validate_branch_name(branch_name) if branch_name is not None else load_current_branch(repo_root)
    return branch_management_root(repo_root) / name


def state_root(repo_root: Path, branch_name: Optional[str] = None) -> Path:
    """
    Resolve the branch-specific state root.

    Args:
        repo_root (Path): Repository root.
        branch_name (Optional[str]): Override branch name.

    Returns:
        Path: Branch state root path.
    """
    return branch_root(repo_root, branch_name) / "state"


def work_root(repo_root: Path, branch_name: Optional[str] = None) -> Path:
    """
    Resolve the branch-specific work_management root.

    Args:
        repo_root (Path): Repository root.
        branch_name (Optional[str]): Override branch name.

    Returns:
        Path: Branch work_management root path.
    """
    return branch_root(repo_root, branch_name) / "work_management"


def self_context_root(repo_root: Path) -> Path:
    """
    Return the global self_context root.

    Args:
        repo_root (Path): Repository root.

    Returns:
        Path: self_context root path.
    """
    return repo_root / "context_compass" / "self_context"


def self_context_locks_dir(repo_root: Path) -> Path:
    """
    Return the global locks directory for self_context operations.

    Args:
        repo_root (Path): Repository root.

    Returns:
        Path: self_context locks path.
    """
    return self_context_root(repo_root) / "locks"
