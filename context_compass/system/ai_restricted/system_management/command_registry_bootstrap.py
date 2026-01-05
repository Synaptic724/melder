"""
SQLite bootstrap helpers for command registry access.

Purpose
- Ensure command registry tables exist and are seeded before reads.
- Run the minimal SQLite build steps required for registry access.

Contract
- Only SQLite steps are executed; Kuzu is not initialized here.
- Build steps are idempotent and safe to rerun.
- Raises on missing context_compass layout or build failures.
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

from context_compass.system.installation.build import (
    init_sqlite_tables,
    seed_sqlite_actions,
    seed_sqlite_commands,
    seed_sqlite_config,
    seed_sqlite_hooks,
    seed_sqlite_queries,
    seed_sqlite_registry,
)
from context_compass.system.installation.build_runner import BuildContext


COMMAND_REGISTRY_SYSTEM_TABLE = "command_registry_system"
COMMAND_REGISTRY_USER_TABLE = "command_registry_user"


def _configure_logging() -> None:
    """
    Ensure logging is configured for bootstrap output.

    Contract:
        - Uses INFO-level logging with a minimal formatter if not configured.
    """

    logging.basicConfig(level=logging.INFO, format="%(message)s")


def _context_compass_root(repo_root: Path) -> Path:
    """
    Resolve the context_compass system root for a repository.

    Args:
        repo_root (Path): Repository root path.

    Returns:
        Path: Path to context_compass/system.

    Raises:
        FileNotFoundError: If the context_compass system directory is missing.
    """

    context_root = repo_root / "context_compass" / "system"
    if not context_root.exists():
        raise FileNotFoundError(
            "context_compass system directory not found: "
            f"{context_root}"
        )
    return context_root


def _build_context(repo_root: Path) -> BuildContext:
    """
    Build a minimal BuildContext for SQLite seeding.

    Args:
        repo_root (Path): Repository root path.

    Returns:
        BuildContext: Build context configured with SQLite paths only.
    """

    context_root = _context_compass_root(repo_root)
    storage_root = context_root / "storage"
    sqlite_root = storage_root / "sqlite"
    return BuildContext(
        context_compass_root=context_root,
        storage_root=storage_root,
        sqlite_paths={
            "system": sqlite_root / "system.db",
            "user": sqlite_root / "user.db",
            "user_defined": sqlite_root / "user_defined.db",
        },
        kuzu_paths={},
        manifest_path=context_root / "installation" / "build_manifest.json",
    )


def _table_row_count(db_path: Path, table_name: str) -> int:
    """
    Return the row count for a SQLite table.

    Args:
        db_path (Path): SQLite database path.
        table_name (str): Table name to query.

    Returns:
        int: Row count for the table.

    Raises:
        sqlite3.Error: If the query fails.
    """

    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        ).fetchone()
        if not row or row[0] == 0:
            return 0
        count_row = conn.execute(
            f"SELECT COUNT(*) FROM {table_name}"
        ).fetchone()
        return int(count_row[0]) if count_row else 0
    finally:
        conn.close()


def _registry_ready(db_path: Path, table_name: str) -> bool:
    """
    Determine whether a registry table exists and has data.

    Args:
        db_path (Path): SQLite database path.
        table_name (str): Registry table name.

    Returns:
        bool: True if the table exists and has rows.
    """

    if not db_path.exists():
        return False
    try:
        return _table_row_count(db_path, table_name) > 0
    except sqlite3.Error:
        return False


def ensure_registry_seeded(repo_root: Path) -> None:
    """
    Ensure command registry tables are seeded for system and user scopes.

    Args:
        repo_root (Path): Repository root path.

    Raises:
        Exception: Propagates build failures from seed steps.
    """

    context = _build_context(repo_root)
    system_ready = _registry_ready(
        context.sqlite_paths["system"], COMMAND_REGISTRY_SYSTEM_TABLE
    )
    user_ready = _registry_ready(
        context.sqlite_paths["user"], COMMAND_REGISTRY_USER_TABLE
    )
    if system_ready and user_ready:
        return

    _configure_logging()
    logger = logging.getLogger(__name__)
    logger.info("Seeding SQLite registries for command discovery.")
    init_sqlite_tables.run(context)
    seed_sqlite_registry.run(context)
    seed_sqlite_actions.run(context)
    seed_sqlite_hooks.run(context)
    seed_sqlite_queries.run(context)
    seed_sqlite_config.run(context)
    seed_sqlite_commands.run(context)
