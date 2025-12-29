"""
context_compass.tools._shared.paths

Path utilities for context_compass tooling.

Contracts
- Normalize repo-relative paths using forward slashes.
- Preserve original casing on Windows by avoiding case normalization.
- Avoid raising for paths outside the repo; return a stable string.
"""

from pathlib import Path


def _normalize_rel_path(path: Path) -> str:
    """
    Normalize a relative path to POSIX form without leading './'.

    Args:
        path (Path): Relative path.

    Returns:
        str: Normalized POSIX path.
    """
    text = path.as_posix()
    if text.startswith("./"):
        return text[2:]
    return text


def repo_relative_path(repo_root: Path, path: Path) -> str:
    """
    Convert a path into a repo-relative POSIX string when possible.

    Contract:
    - If path is inside repo_root, return a relative POSIX path.
    - If path is outside repo_root, return a POSIX absolute path string.

    Args:
        repo_root (Path): Repository root.
        path (Path): Path to normalize.

    Returns:
        str: Normalized path string.
    """
    root = repo_root
    target = path if path.is_absolute() else repo_root / path
    try:
        rel = target.relative_to(root)
    except ValueError:
        return target.as_posix()
    return _normalize_rel_path(rel)


def repo_relative_dir(repo_root: Path, path: Path) -> str:
    """
    Convert a directory path into a repo-relative POSIX string.

    Contract:
    - Returns "" for the repo root directory itself.

    Args:
        repo_root (Path): Repository root.
        path (Path): Directory path to normalize.

    Returns:
        str: Normalized directory string ("" for root).
    """
    rel = repo_relative_path(repo_root, path)
    return "" if rel in (".", "") else rel
