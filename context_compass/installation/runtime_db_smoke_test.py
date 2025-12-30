"""
Runtime smoke test for SQLite and Kuzu database backends.

Purpose
- Validate that SQLite and Kuzu can create, write, and read a minimal schema.
- Ensure database files live under context_compass/assets for easy cleanup.

Contract
- Creates a Kuzu database directory and a SQLite database file.
- Uses deterministic, small test data with explicit schema.
- Logs each step and exits non-zero on failures.
"""

import logging
import os
import shutil
import sqlite3
import sys
from pathlib import Path
from typing import Iterable

try:
    import kuzu
except ImportError:  # pragma: no cover - runtime dependency check
    kuzu = None


ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"
KUZU_DB_PATH = ASSETS_DIR / "test_kuzu_db"
SQLITE_DB_PATH = ASSETS_DIR / "test_sqlite.db"


def _configure_logging() -> None:
    """
    Configure logging for the smoke test.
    """
    logging.basicConfig(level=logging.INFO, format="%(message)s")


def _cleanup(paths: Iterable[Path]) -> None:
    """
    Remove previous test artifacts.

    Args:
        paths (Iterable[Path]): Paths to remove.
    """
    for path in paths:
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        elif path.exists():
            try:
                path.unlink()
            except OSError:
                pass


def _test_kuzu() -> None:
    """
    Run a minimal Kuzu read/write test.

    Raises:
        RuntimeError: If Kuzu operations fail.
    """
    logger = logging.getLogger(__name__)
    if kuzu is None:
        raise RuntimeError("kuzu is not available; install graphiti-core[kuzu].")

    logger.info("TESTING KUZU (Graph DB)")
    KUZU_DB_PATH.mkdir(parents=True, exist_ok=True)
    db = kuzu.Database(str(KUZU_DB_PATH))
    conn = kuzu.Connection(db)

    try:
        conn.execute(
            """
            CREATE NODE TABLE CodeFile(
                path STRING,
                hash STRING,
                status STRING,
                PRIMARY KEY (path)
            )
            """
        )
        logger.info("  Schema created: CodeFile")
    except RuntimeError:
        logger.info("  Schema already exists")

    file_path = "src/auth.py"
    file_hash = "abc_123_hash"
    conn.execute(
        """
        MERGE (f:CodeFile {path: $path})
        ON CREATE SET f.hash = $hash, f.status = "New"
        ON MATCH SET f.status = "Updated"
        RETURN f
        """,
        {"path": file_path, "hash": file_hash},
    )
    logger.info("  Inserted node: %s", file_path)

    result = conn.execute("MATCH (n:CodeFile) RETURN n.path, n.status")
    while result.hasNext():
        row = result.getNext()
        logger.info("  Found: %s [Status: %s]", row[0], row[1])


def _test_sqlite() -> None:
    """
    Run a minimal SQLite read/write test.

    Raises:
        RuntimeError: If SQLite operations fail.
    """
    logger = logging.getLogger(__name__)
    logger.info("TESTING SQLITE (Relational DB)")
    conn = sqlite3.connect(SQLITE_DB_PATH)
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS code_files (
                path TEXT PRIMARY KEY,
                hash TEXT,
                status TEXT
            )
            """
        )
        logger.info("  Schema created: code_files")
        cursor.execute(
            """
            INSERT INTO code_files (path, hash, status)
            VALUES (?, ?, ?)
            ON CONFLICT(path) DO UPDATE SET status='Updated'
            """,
            ("src/auth.py", "abc_123_hash", "New"),
        )
        conn.commit()
        logger.info("  Inserted row: src/auth.py")
        cursor.execute("SELECT path, status FROM code_files")
        for row in cursor.fetchall():
            logger.info("  Found: %s [Status: %s]", row[0], row[1])
    except sqlite3.Error as exc:
        raise RuntimeError(f"SQLite failure: {exc}") from exc
    finally:
        conn.close()


def main() -> None:
    """
    Run the database smoke tests for Kuzu and SQLite.
    """
    _configure_logging()
    logger = logging.getLogger(__name__)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    _cleanup([KUZU_DB_PATH, SQLITE_DB_PATH])
    logger.info("Cleanup complete.")

    try:
        _test_kuzu()
        _test_sqlite()
    except Exception as exc:
        logger.error("Smoke test failed: %s", exc)
        raise SystemExit(1) from exc
    logger.info("All systems operational.")


if __name__ == "__main__":
    main()
