"""
Short-lived ORM session helpers for context_compass SQLite databases.

Purpose
- Provide explicit, short-lived SQLAlchemy sessions without pooling.
- Prevent implicit database creation in read-only paths.

Contract
- No module-level engines or session factories are retained.
- Each helper call builds a new Engine and disposes it after use.
- Callers control whether a database must already exist.
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool


def system_db_path(repo_root: Path) -> Path:
    """
    Resolve the system SQLite database path.

    Args:
        repo_root (Path): Repository root path.

    Returns:
        Path: Path to system.db.
    """

    return (
        repo_root
        / "context_compass"
        / "system"
        / "storage"
        / "sqlite"
        / "system.db"
    )


def user_db_path(repo_root: Path) -> Path:
    """
    Resolve the user SQLite database path.

    Args:
        repo_root (Path): Repository root path.

    Returns:
        Path: Path to user.db.
    """

    return (
        repo_root
        / "context_compass"
        / "system"
        / "storage"
        / "sqlite"
        / "user.db"
    )


def user_defined_db_path(repo_root: Path) -> Path:
    """
    Resolve the user-defined SQLite database path.

    Args:
        repo_root (Path): Repository root path.

    Returns:
        Path: Path to user_defined.db.
    """

    return (
        repo_root
        / "context_compass"
        / "system"
        / "storage"
        / "sqlite"
        / "user_defined.db"
    )




def _configure_sqlite_pragmas(
    dbapi_connection: object, _connection_record: object
) -> None:
    """
    Configure SQLite connection-level pragmas for concurrency and integrity.

    Args:
        dbapi_connection (object): SQLite DB-API connection object.
        _connection_record (object): SQLAlchemy connection record (unused).

    Returns:
        None: Pragmas are applied in-place to the connection.

    Raises:
        Exception: Propagates underlying DB-API exceptions if pragmas fail.

    Contract:
        - WAL mode reduces reader/writer contention for file-based SQLite.
        - busy_timeout reduces immediate lock failures under contention.
        - synchronous NORMAL balances durability and throughput for WAL.
        - foreign_keys ON enforces relational integrity where configured.
    """

    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA busy_timeout=5000;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.execute("PRAGMA foreign_keys=ON;")
    finally:
        cursor.close()


def build_sqlite_engine(db_path: Path, *, must_exist: bool) -> Engine:
    """
    Build a SQLAlchemy engine for a SQLite database.

    Args:
        db_path (Path): SQLite database path.
        must_exist (bool): Require that the database file exists.

    Returns:
        Engine: SQLAlchemy engine bound to the database path.

    Raises:
        FileNotFoundError: If must_exist is True and the database file is missing.

    Contract:
        - Applies SQLite pragmas for WAL, busy_timeout, synchronous, and foreign_keys.
    """

    if must_exist and not db_path.exists():
        raise FileNotFoundError(f"SQLite database not found: {db_path}")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    url = f"sqlite:///{db_path}"
    engine = create_engine(url, future=True, poolclass=NullPool)
    event.listen(engine, "connect", _configure_sqlite_pragmas)
    return engine


@contextmanager
def sqlite_session(db_path: Path, *, must_exist: bool) -> Iterator[Session]:
    """
    Yield a short-lived SQLAlchemy session for the given database.

    Args:
        db_path (Path): SQLite database path.
        must_exist (bool): Require that the database file exists.

    Yields:
        Session: Active SQLAlchemy session.

    Raises:
        FileNotFoundError: If must_exist is True and the database file is missing.

    Contract:
        - Commits on normal exit, rolls back on exceptions.
        - Disposes the engine after the session is closed.
    """

    engine = build_sqlite_engine(db_path, must_exist=must_exist)
    factory = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
        engine.dispose()
