"""
Installation build runner for database initialization and scripted setup.

Purpose
- Create SQLite and Kuzu databases defined in the build manifest.
- Execute build and custom build scripts in manifest order.

Contract
- The manifest is JSON stored next to this file by default.
- Manifest paths are resolved relative to the context_compass root directory.
- Stops on the first failure and exits with a non-zero status.
- Build scripts must implement run(context: BuildContext) -> None.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Mapping, Sequence

def _ensure_context_compass_on_path() -> None:
    """
    Ensure the context_compass package root is on sys.path.

    This allows running build_runner.py directly from:
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

from context_compass.system.ai_restricted.database_management.orm_session import (  # noqa: E402
    build_sqlite_engine,
)

try:
    import kuzu
except ImportError:  # pragma: no cover - runtime dependency check
    kuzu = None


DEFAULT_MANIFEST_NAME = "build_manifest.json"
ALLOWED_PHASES = ("build", "custom_build")


@dataclass(frozen=True)
class BuildContext:
    """
    Read-only build context shared with installation scripts.

    Attributes:
        context_compass_root (Path): Root directory of the context_compass tree.
        storage_root (Path): Root directory for storage assets.
        sqlite_paths (Mapping[str, Path]): Named SQLite database file paths.
        kuzu_paths (Mapping[str, Path]): Named Kuzu database paths.
        manifest_path (Path): Manifest path used to drive the build.

    Contract:
        - All paths are absolute and must exist after initialization steps.
        - Callers must treat the mappings as read-only configuration.
    """

    context_compass_root: Path
    storage_root: Path
    sqlite_paths: Mapping[str, Path]
    kuzu_paths: Mapping[str, Path]
    manifest_path: Path


@dataclass(frozen=True)
class BuildStep:
    """
    Normalized build step definition loaded from the manifest.

    Attributes:
        step_id (str): Stable identifier for the step.
        phase (str): Phase name (build or custom_build).
        path (Path): Absolute path to the script file.
        enabled (bool): Whether the step should execute.

    Contract:
        - Paths must point to importable Python files.
        - Steps are executed in the order they appear in the manifest.
    """

    step_id: str
    phase: str
    path: Path
    enabled: bool


def _configure_logging() -> None:
    """
    Configure logging for the build runner.

    Contract:
        - Uses INFO-level output with a minimal formatter.
    """

    logging.basicConfig(level=logging.INFO, format="%(message)s")


def _default_manifest_path() -> Path:
    """
    Return the default manifest path next to this runner.

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
    Load and validate the build manifest JSON.

    Args:
        manifest_path (Path): Path to the manifest file.

    Returns:
        dict: Parsed manifest data.

    Raises:
        FileNotFoundError: If the manifest does not exist.
        ValueError: If the manifest structure is invalid.
    """

    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")
    raw = manifest_path.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Manifest is not valid JSON: {manifest_path}") from exc
    if not isinstance(data, dict):
        raise ValueError("Manifest root must be a JSON object.")
    _validate_manifest(data)
    return data


def _validate_manifest(manifest: dict) -> None:
    """
    Validate manifest schema requirements.

    Args:
        manifest (dict): Parsed manifest content.

    Raises:
        ValueError: If required keys or types are invalid.
    """

    if manifest.get("version") != 1:
        raise ValueError("Manifest version must be 1.")
    dbs = manifest.get("dbs")
    if not isinstance(dbs, dict):
        raise ValueError("Manifest 'dbs' must be an object.")
    sqlite_cfg = dbs.get("sqlite")
    kuzu_cfg = dbs.get("kuzu")
    if not isinstance(sqlite_cfg, dict):
        raise ValueError("Manifest 'dbs.sqlite' must be an object.")
    if not isinstance(kuzu_cfg, dict):
        raise ValueError("Manifest 'dbs.kuzu' must be an object.")
    steps = manifest.get("steps")
    if not isinstance(steps, list):
        raise ValueError("Manifest 'steps' must be a list.")
    for index, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            raise ValueError(f"Manifest step #{index} must be an object.")
        phase = step.get("phase")
        if phase not in ALLOWED_PHASES:
            raise ValueError(
                "Manifest step phase must be one of: "
                f"{', '.join(ALLOWED_PHASES)}."
            )
        path = step.get("path")
        if not isinstance(path, str) or not path.strip():
            raise ValueError(f"Manifest step #{index} requires a non-empty path.")
        enabled = step.get("enabled", True)
        if not isinstance(enabled, bool):
            raise ValueError(f"Manifest step #{index} 'enabled' must be boolean.")


def _resolve_path(context_compass_root: Path, path_text: str) -> Path:
    """
    Resolve a manifest path into an absolute filesystem path.

    Args:
        context_compass_root (Path): Base context_compass directory.
        path_text (str): Manifest path string.

    Returns:
        Path: Absolute path for the manifest entry.
    """

    candidate = Path(path_text)
    if candidate.is_absolute():
        return candidate
    return context_compass_root / candidate


def _resolve_db_paths(
    context_compass_root: Path, db_entries: Mapping[str, str]
) -> dict[str, Path]:
    """
    Resolve database path mappings from the manifest.

    Args:
        context_compass_root (Path): Base context_compass directory.
        db_entries (Mapping[str, str]): Database name-to-path mapping.

    Returns:
        dict[str, Path]: Database name-to-path mapping with absolute Paths.
    """

    resolved: dict[str, Path] = {}
    for name, path_text in db_entries.items():
        if not isinstance(path_text, str) or not path_text.strip():
            raise ValueError(f"Database path for '{name}' must be a non-empty string.")
        resolved[name] = _resolve_path(context_compass_root, path_text)
    return resolved


def _normalize_steps(
    context_compass_root: Path, steps: Sequence[dict]
) -> list[BuildStep]:
    """
    Normalize manifest steps into BuildStep objects.

    Args:
        context_compass_root (Path): Base context_compass directory.
        steps (Sequence[dict]): Raw manifest step objects.

    Returns:
        list[BuildStep]: Normalized build steps.

    Raises:
        ValueError: If required fields are missing or invalid.
    """

    normalized: list[BuildStep] = []
    for index, step in enumerate(steps, start=1):
        step_id = step.get("id")
        if step_id is None:
            step_id = f"step_{index}"
        if not isinstance(step_id, str) or not step_id.strip():
            raise ValueError(f"Manifest step #{index} has an invalid id.")
        phase = step.get("phase")
        if phase not in ALLOWED_PHASES:
            raise ValueError(
                "Manifest step phase must be one of: "
                f"{', '.join(ALLOWED_PHASES)}."
            )
        path_text = step.get("path")
        if not isinstance(path_text, str) or not path_text.strip():
            raise ValueError(f"Manifest step '{step_id}' requires a path.")
        enabled = step.get("enabled", True)
        if not isinstance(enabled, bool):
            raise ValueError(f"Manifest step '{step_id}' has invalid enabled flag.")
        normalized.append(
            BuildStep(
                step_id=step_id,
                phase=phase,
                path=_resolve_path(context_compass_root, path_text),
                enabled=enabled,
            )
        )
    return normalized


def _ensure_sqlite_db(db_path: Path) -> None:
    """
    Ensure a SQLite database file exists on disk.

    Args:
        db_path (Path): SQLite database file path.

    Raises:
        RuntimeError: If SQLAlchemy cannot create the database.
    """

    try:
        engine = build_sqlite_engine(db_path, must_exist=False)
        with engine.connect():
            pass
        engine.dispose()
    except Exception as exc:
        raise RuntimeError(f"SQLite init failed for {db_path}: {exc}") from exc


def _ensure_kuzu_db(db_path: Path) -> None:
    """
    Ensure a Kuzu database exists on disk.

    Args:
        db_path (Path): Kuzu database path.

    Raises:
        RuntimeError: If Kuzu is unavailable or initialization fails.
    """

    if kuzu is None:
        raise RuntimeError("kuzu is not available; install graphiti-core[kuzu].")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db = kuzu.Database(str(db_path))
    conn = kuzu.Connection(db)
    try:
        conn.close()
    except AttributeError:
        pass
    db = None
    conn = None


def _import_module_from_path(path: Path, module_name: str) -> ModuleType:
    """
    Import a Python module from a filesystem path.

    Args:
        path (Path): Python file to import.
        module_name (str): Unique module name for import isolation.

    Returns:
        ModuleType: Imported module.

    Raises:
        RuntimeError: If the module cannot be imported.
    """

    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import module at {path}.")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        raise RuntimeError(f"Failed to import {path}: {exc}") from exc
    return module


def _execute_step(step: BuildStep, context: BuildContext) -> None:
    """
    Execute a single build step by importing and calling its run() function.

    Args:
        step (BuildStep): Step definition to execute.
        context (BuildContext): Shared build context.

    Raises:
        RuntimeError: If the build script contract is not met.
    """

    logger = logging.getLogger(__name__)
    if not step.enabled:
        logger.info("Skipping disabled step: %s", step.step_id)
        return
    if not step.path.exists():
        raise RuntimeError(f"Build step '{step.step_id}' not found: {step.path}")
    module_name = f"cc_build_{step.phase}_{step.step_id}"
    module = _import_module_from_path(step.path, module_name)
    run_func = getattr(module, "run", None)
    if run_func is None or not callable(run_func):
        raise RuntimeError(
            f"Build step '{step.step_id}' must define callable run(context)."
        )
    logger.info("Running %s (%s)", step.step_id, step.path)
    run_func(context)


def run_build(manifest_path: Path, context_compass_root: Path | None = None) -> None:
    """
    Execute database initialization and build steps from a manifest.

    Args:
        manifest_path (Path): Path to the build manifest.
        context_compass_root (Path | None): Override for context_compass root.

    Raises:
        RuntimeError: If database initialization or any build step fails.
        ValueError: If the manifest is invalid.
    """

    logger = logging.getLogger(__name__)
    context_root = (
        context_compass_root
        if context_compass_root is not None
        else _resolve_context_compass_root()
    )
    manifest = _load_manifest(manifest_path)
    dbs = manifest["dbs"]
    sqlite_paths = _resolve_db_paths(context_root, dbs["sqlite"])
    kuzu_paths = _resolve_db_paths(context_root, dbs["kuzu"])
    steps = _normalize_steps(context_root, manifest["steps"])

    logger.info("Using manifest: %s", manifest_path)
    for name, path in sqlite_paths.items():
        logger.info("Ensuring SQLite DB '%s': %s", name, path)
        _ensure_sqlite_db(path)
    for name, path in kuzu_paths.items():
        logger.info("Ensuring Kuzu DB '%s': %s", name, path)
        _ensure_kuzu_db(path)

    context = BuildContext(
        context_compass_root=context_root,
        storage_root=context_root / "storage",
        sqlite_paths=sqlite_paths,
        kuzu_paths=kuzu_paths,
        manifest_path=manifest_path,
    )
    for step in steps:
        _execute_step(step, context)


def _parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for the build runner.

    Returns:
        argparse.Namespace: Parsed CLI arguments.
    """

    parser = argparse.ArgumentParser(
        description="Initialize databases and run installation build scripts."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=_default_manifest_path(),
        help="Path to build manifest JSON.",
    )
    return parser.parse_args()


def main() -> None:
    """
    CLI entrypoint for the build runner.
    """

    _configure_logging()
    logger = logging.getLogger(__name__)
    args = _parse_args()
    try:
        run_build(args.manifest)
    except Exception as exc:
        logger.error("Build runner failed: %s", exc)
        raise SystemExit(1) from exc
    logger.info("Build runner completed successfully.")


if __name__ == "__main__":
    main()
