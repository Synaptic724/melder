"""
Reset the local installation state to a pre-build baseline.

Purpose
- Remove database artifacts created by the build runner.
- Remove active environments created by the installation bootstrap.
- Preserve manifests, schemas, and build scripts so the system can be rebuilt.

Contract
- Uses the build manifest to locate database paths.
- Deletes only the DB artifacts (SQLite files, sidecars, Kuzu paths).
- Deletes active environments under installation/environments/active_environments.
- Defaults to dry-run unless --apply is provided.
- Never deletes registry manifests or build scripts.
"""

from __future__ import annotations

import argparse
import logging
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

def _ensure_context_compass_on_path() -> None:
    """
    Ensure the context_compass package root is on sys.path.

    This allows running reset_system.py directly from:
    - repo_root/context_compass/...
    """

    here = Path(__file__).resolve()
    for parent in here.parents:
        if parent.name == "context_compass":
            package_root = parent.parent
            package_root_str = str(package_root)
            if package_root_str not in sys.path:
                sys.path.insert(0, package_root_str)
            return

    raise RuntimeError(
        "Unable to locate the context_compass package root. "
        "Ensure the package directory is named 'context_compass' and lives "
        "under a parent added to PYTHONPATH (e.g., repo_root/context_compass)."
    )


_ensure_context_compass_on_path()

from context_compass.system.installation import build_runner  # noqa: E402


DEFAULT_MANIFEST_NAME = "build_manifest.json"
SQLITE_SIDECAR_SUFFIXES = ("-wal", "-shm", "-journal")


@dataclass(frozen=True)
class ResetPlan:
    """
    Reset plan derived from the build manifest.

    Attributes:
        context_compass_root (Path): Root directory of the context_compass tree.
        manifest_path (Path): Manifest path used to plan the reset.
        sqlite_paths (tuple[Path, ...]): SQLite DB file paths to remove.
        kuzu_paths (tuple[Path, ...]): Kuzu DB paths (file or dir) to remove.
        sqlite_sidecars (tuple[Path, ...]): Sidecar files for SQLite WAL/journal.
        env_paths (tuple[Path, ...]): Active environment directories to remove.

    Contract:
        - All paths are absolute and resolve from the manifest.
        - Paths are ordered deterministically for logging and tests.
    """

    context_compass_root: Path
    manifest_path: Path
    sqlite_paths: tuple[Path, ...]
    kuzu_paths: tuple[Path, ...]
    sqlite_sidecars: tuple[Path, ...]
    env_paths: tuple[Path, ...]


@dataclass(frozen=True)
class ResetSummary:
    """
    Summary of reset execution.

    Attributes:
        removed (tuple[Path, ...]): Paths removed during reset.
        missing (tuple[Path, ...]): Paths that were absent at reset time.
        dry_run (bool): True when no deletions were performed.

    Contract:
        - Paths are absolute.
        - When dry_run is True, removed is always empty.
    """

    removed: tuple[Path, ...]
    missing: tuple[Path, ...]
    dry_run: bool


def _configure_logging() -> None:
    """
    Configure logging for reset output.

    Contract:
        - Uses INFO-level output with a minimal formatter.
    """

    logging.basicConfig(level=logging.INFO, format="%(message)s")


def _default_manifest_path() -> Path:
    """
    Return the default build manifest path next to this script.

    Returns:
        Path: Default manifest path.
    """

    return Path(__file__).with_name(DEFAULT_MANIFEST_NAME)


def _resolve_context_compass_root() -> Path:
    """
    Resolve the context_compass root directory for this installation.

    Returns:
        Path: Absolute path to the context_compass directory.
    """

    return Path(__file__).resolve().parents[1]


def _load_manifest(manifest_path: Path) -> dict:
    """
    Load and validate the build manifest.

    Args:
        manifest_path (Path): Manifest file path.

    Returns:
        dict: Parsed manifest data.

    Raises:
        FileNotFoundError: If the manifest does not exist.
        ValueError: If the manifest structure is invalid.
    """

    return build_runner._load_manifest(manifest_path)


def _resolve_db_paths(
    context_root: Path, db_entries: Mapping[str, str]
) -> tuple[Path, ...]:
    """
    Resolve database paths declared in the manifest.

    Args:
        context_root (Path): context_compass root directory.
        db_entries (Mapping[str, str]): Manifest DB mapping.

    Returns:
        tuple[Path, ...]: Absolute DB paths.
    """

    resolved = build_runner._resolve_db_paths(context_root, db_entries)
    return tuple(resolved[name] for name in sorted(resolved))


def _collect_sqlite_sidecars(sqlite_paths: Sequence[Path]) -> tuple[Path, ...]:
    """
    Collect SQLite sidecar paths for each SQLite DB.

    Args:
        sqlite_paths (Sequence[Path]): SQLite DB paths.

    Returns:
        tuple[Path, ...]: Sidecar file paths to remove.
    """

    sidecars: list[Path] = []
    for sqlite_path in sqlite_paths:
        for suffix in SQLITE_SIDECAR_SUFFIXES:
            sidecars.append(Path(f"{sqlite_path}{suffix}"))
    return tuple(sidecars)


def _resolve_active_env_paths(context_root: Path) -> tuple[Path, ...]:
    """
    Resolve active environment directories for removal.

    Args:
        context_root (Path): context_compass root directory.

    Returns:
        tuple[Path, ...]: Active environment paths, sorted for determinism.
    """

    env_root = context_root / "installation" / "environments" / "active_environments"
    if not env_root.exists():
        env_root = (
            context_root
            / "system"
            / "installation"
            / "environments"
            / "active_environments"
        )
    if not env_root.exists():
        return ()
    return tuple(sorted(path for path in env_root.iterdir()))


def _build_reset_plan(
    manifest_path: Path, context_root: Path | None
) -> ResetPlan:
    """
    Build a reset plan from the manifest.

    Args:
        manifest_path (Path): Manifest file path.
        context_root (Path | None): Override for context_compass root.

    Returns:
        ResetPlan: Reset plan with resolved database paths.
    """

    resolved_root = (
        context_root if context_root is not None else _resolve_context_compass_root()
    )
    manifest = _load_manifest(manifest_path)
    dbs = manifest["dbs"]
    sqlite_paths = _resolve_db_paths(resolved_root, dbs["sqlite"])
    kuzu_paths = _resolve_db_paths(resolved_root, dbs["kuzu"])
    sqlite_sidecars = _collect_sqlite_sidecars(sqlite_paths)
    env_paths = _resolve_active_env_paths(resolved_root)
    return ResetPlan(
        context_compass_root=resolved_root,
        manifest_path=manifest_path,
        sqlite_paths=sqlite_paths,
        kuzu_paths=kuzu_paths,
        sqlite_sidecars=sqlite_sidecars,
        env_paths=env_paths,
    )


def _iter_reset_targets(plan: ResetPlan) -> Iterable[Path]:
    """
    Yield reset targets in a deterministic order.

    Args:
        plan (ResetPlan): Reset plan with path sets.

    Returns:
        Iterable[Path]: Paths to remove.
    """

    for path in plan.sqlite_paths:
        yield path
    for path in plan.sqlite_sidecars:
        yield path
    for path in plan.kuzu_paths:
        yield path
    for path in plan.env_paths:
        yield path


def _remove_path(path: Path, dry_run: bool, logger: logging.Logger) -> bool:
    """
    Remove a file or directory path if present.

    Args:
        path (Path): Path to remove.
        dry_run (bool): When True, only log the deletion.
        logger (logging.Logger): Logger for status output.

    Returns:
        bool: True when a deletion occurred (or would occur in dry-run).
    """

    if not path.exists():
        logger.info("Missing: %s", path)
        return False
    if dry_run:
        logger.info("Dry-run delete: %s", path)
        return True
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()
    logger.info("Deleted: %s", path)
    return True


def run_reset(
    manifest_path: Path,
    apply: bool,
    context_compass_root: Path | None = None,
) -> ResetSummary:
    """
    Execute a reset run for the build manifest.

    Args:
        manifest_path (Path): Manifest file path.
        apply (bool): When True, perform deletions. False is dry-run.
        context_compass_root (Path | None): Override root directory.

    Returns:
        ResetSummary: Summary of removed and missing paths.
    """

    logger = logging.getLogger(__name__)
    plan = _build_reset_plan(manifest_path, context_compass_root)
    removed: list[Path] = []
    missing: list[Path] = []
    dry_run = not apply
    logger.info("Reset manifest: %s", plan.manifest_path)
    logger.info("Reset mode: %s", "APPLY" if apply else "DRY-RUN")
    for path in _iter_reset_targets(plan):
        deleted = _remove_path(path, dry_run=dry_run, logger=logger)
        if deleted:
            if not dry_run:
                removed.append(path)
        else:
            missing.append(path)
    return ResetSummary(
        removed=tuple(removed),
        missing=tuple(missing),
        dry_run=dry_run,
    )


def _parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for the reset script.

    Returns:
        argparse.Namespace: Parsed CLI arguments.
    """

    parser = argparse.ArgumentParser(
        description="Reset context_compass DB artifacts to a baseline state."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=_default_manifest_path(),
        help="Path to build manifest JSON.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply deletions (default is dry-run).",
    )
    return parser.parse_args()


def main() -> None:
    """
    CLI entrypoint for reset_system.
    """

    _configure_logging()
    logger = logging.getLogger(__name__)
    args = _parse_args()
    try:
        summary = run_reset(args.manifest, apply=args.apply)
    except Exception as exc:
        logger.error("Reset failed: %s", exc)
        raise SystemExit(1) from exc
    if summary.dry_run:
        logger.info("Dry-run complete; no files removed.")
    else:
        logger.info("Reset complete; removed %d paths.", len(summary.removed))


if __name__ == "__main__":
    main()
