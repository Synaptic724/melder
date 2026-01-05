"""
Path helpers for sql_tools CRUD script resolution.

Purpose
- Centralize filesystem layout rules for sql_tools scripts.
- Provide deterministic table/operation path helpers for the CRUD router.

Contract
- All scripts live under sql_tools/<table>/<operation>/<action>.py.
- Callers must pass valid operation and action strings.
"""

from __future__ import annotations

from pathlib import Path


SUPPORTED_OPERATIONS = ("create", "read", "update", "delete")


def sql_tools_root(repo_root: Path) -> Path:
    """
    Resolve the sql_tools root directory for the repository.

    Args:
        repo_root (Path): Repository root path.

    Returns:
        Path: Root directory containing sql_tools scripts.
    """

    repo_path = (
        repo_root
        / "context_compass"
        / "system"
        / "ai_restricted"
        / "sql_tools"
    )
    if repo_path.exists():
        return repo_path
    legacy_path = (
        repo_root
        / "src"
        / "context_compass"
        / "system"
        / "ai_restricted"
        / "sql_tools"
    )
    if legacy_path.exists():
        return legacy_path
    return Path(__file__).resolve().parents[1] / "sql_tools"


def script_path_for(
    table_name: str,
    operation: str,
    action: str,
    *,
    base_dir: Path,
) -> Path:
    """
    Build the expected script path for a table operation.

    Args:
        table_name (str): Table directory name.
        operation (str): CRUD operation name.
        action (str): Script action name within the operation folder.
        base_dir (Path): sql_tools root directory.

    Returns:
        Path: Expected script path.
    """

    return base_dir / table_name / operation / f"{action}.py"
