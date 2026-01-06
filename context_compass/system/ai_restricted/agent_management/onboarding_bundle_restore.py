"""
Restore selected onboarding bundle files from a stored SQLite snapshot.

Purpose
- Restore a curated subset of onboarding docs from a bundle_id snapshot.
- Support rewind workflows without relying on JSON artifacts on disk.

Contract
- Requires an explicit list of paths to restore.
- Refuses to overwrite existing files unless allow_overwrite is true.
- Writes only under the target_root directory.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Iterable

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_bool,
    optional_list,
    optional_string,
    require_string,
)
from context_compass.system.ai_restricted._shared.command_results import (
    exception_result,
    ok_result,
    payload_error_result,
)
from context_compass.system.ai_restricted.database_management import sqlite_crud
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)


ONBOARDING_BUNDLE_TABLE = "onboarding_bundle"
ONBOARDING_BUNDLE_FILES_TABLE = "onboarding_bundle_files"
ONBOARDING_BUNDLE_MISSING_TABLE = "onboarding_bundle_missing"
ONBOARDING_BUNDLE_ERRORS_TABLE = "onboarding_bundle_errors"
ONBOARDING_BUNDLE_ACTION = "by_bundle_id"
ONBOARDING_BUNDLE_FILES_ACTION = "by_bundle_id_and_paths"
ONBOARDING_BUNDLE_MISSING_ACTION = "by_bundle_id_and_paths"
ONBOARDING_BUNDLE_ERRORS_ACTION = "by_bundle_id_and_paths"


def _resolve_actor_id(ctx: ExecutionContext) -> str:
    """
    Resolve the actor identifier for CRUD auditing.

    Args:
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        str: Actor identifier or "unknown" when unavailable.
    """

    return ctx.agent_id or "unknown"


def _normalize_relative_path(path: str) -> str:
    """
    Normalize a repo-relative path into POSIX form.

    Args:
        path (str): Input path.

    Returns:
        str: Normalized path using forward slashes.
    """

    normalized = path.replace("\\", "/").strip()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def _validate_restore_paths(paths: Iterable[object], command_name: str) -> list[str]:
    """
    Validate and normalize restore paths from the payload.

    Args:
        paths (Iterable[object]): Raw path values from payload.
        command_name (str): Command name for error context.

    Returns:
        list[str]: Normalized relative paths.

    Raises:
        PayloadError: If any path is invalid or unsafe.
    """

    normalized: list[str] = []
    for value in paths:
        if not isinstance(value, str):
            raise PayloadError(
                code="payload_type_error",
                details={
                    "command_name": command_name,
                    "field": "paths",
                    "expected": "list of strings",
                    "actual_type": type(value).__name__,
                },
            )
        text = _normalize_relative_path(value)
        if not text:
            raise PayloadError(
                code="payload_empty",
                details={
                    "command_name": command_name,
                    "field": "paths",
                    "expected": "non-empty path",
                },
            )
        parts = Path(text).parts
        if Path(text).is_absolute() or ".." in parts:
            raise PayloadError(
                code="payload_value_error",
                details={
                    "command_name": command_name,
                    "field": "paths",
                    "expected": "relative paths without '..'",
                    "actual": value,
                },
            )
        normalized.append(text)
    if not normalized:
        raise PayloadError(
            code="payload_missing",
            details={
                "command_name": command_name,
                "field": "paths",
                "expected": "non-empty list of paths",
            },
        )
    return normalized


def _resolve_target_root(repo_root: Path, target_root_value: str | None) -> Path:
    """
    Resolve the target root for restored files.

    Args:
        repo_root (Path): Repository root.
        target_root_value (str | None): Target root override from payload.

    Returns:
        Path: Resolved target root path.
    """

    if target_root_value is None:
        return repo_root
    target_root = Path(target_root_value)
    if not target_root.is_absolute():
        target_root = repo_root / target_root
    return target_root.resolve()


def _safe_output_path(target_root: Path, rel_path: str) -> Path:
    """
    Resolve an output path safely under the target root.

    Args:
        target_root (Path): Base directory for restored files.
        rel_path (str): Repo-relative file path from the bundle.

    Returns:
        Path: Resolved output path.

    Raises:
        ValueError: If the resolved path escapes the target root.
    """

    output_path = (target_root / rel_path).resolve()
    if output_path != target_root and target_root not in output_path.parents:
        raise ValueError(f"Restore path escapes target root: {rel_path}")
    return output_path


def _write_text_atomic(path: Path, content: str) -> None:
    """
    Atomically write a text file.

    Args:
        path (Path): Destination path.
        content (str): Text content.
    """

    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(content, encoding="utf-8")
    tmp_path.replace(path)


def _read_bundle_header(
    repo_root: Path, bundle_id: str, actor_id: str
) -> dict:
    """
    Load onboarding bundle header metadata for a bundle_id.

    Args:
        repo_root (Path): Repository root.
        bundle_id (str): Bundle identifier to read.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        dict: Onboarding bundle header record.

    Raises:
        FileNotFoundError: If the user database is missing.
        PayloadError: If the bundle_id is not found.
        sqlite_crud.SqliteCrudError: For unexpected CRUD failures.
        ValueError: If the CRUD response is malformed.
    """

    try:
        response = sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="read",
                scope="user",
                table_name=ONBOARDING_BUNDLE_TABLE,
                action=ONBOARDING_BUNDLE_ACTION,
                payload={"bundle_id": bundle_id},
                actor_id=actor_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        if exc.code == "db_missing":
            raise FileNotFoundError("User database not found for onboarding bundles.") from exc
        if exc.code == "record_not_found":
            raise PayloadError(
                code="payload_value_error",
                details={
                    "bundle_id": bundle_id,
                    "message": "Bundle id not found.",
                },
            ) from exc
        raise

    record = response.output.get("result", {}).get("record")
    if not isinstance(record, dict):
        raise ValueError("onboarding_bundle read returned an invalid record payload.")
    return record


def _read_bundle_records(
    repo_root: Path,
    bundle_id: str,
    paths: list[str],
    *,
    table_name: str,
    action: str,
    actor_id: str,
) -> list[dict]:
    """
    Read bundle records for a specific onboarding table and path list.

    Args:
        repo_root (Path): Repository root.
        bundle_id (str): Bundle identifier to read.
        paths (list[str]): Normalized relative paths to restore.
        table_name (str): Target onboarding bundle table.
        action (str): Read action name for the table.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        list[dict]: Matching records for the requested table.

    Raises:
        FileNotFoundError: If the user database is missing.
        sqlite_crud.SqliteCrudError: For unexpected CRUD failures.
        ValueError: If the CRUD response is malformed.
    """

    try:
        response = sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="read",
                scope="user",
                table_name=table_name,
                action=action,
                payload={
                    "bundle_id": bundle_id,
                    "paths": paths,
                },
                actor_id=actor_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        if exc.code == "db_missing":
            raise FileNotFoundError("User database not found for onboarding bundles.") from exc
        raise

    records = response.output.get("result", {}).get("records")
    if not isinstance(records, list):
        raise ValueError(f"{table_name} read returned an invalid records payload.")
    return records


def _load_bundle_rows(
    repo_root: Path, bundle_id: str, paths: list[str], actor_id: str
) -> tuple[list[dict], list[dict], list[dict]]:
    """
    Load onboarding bundle rows for the requested paths.

    Args:
        repo_root (Path): Repository root.
        bundle_id (str): Bundle identifier to read.
        paths (list[str]): Normalized relative paths to restore.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        tuple[list[dict], list[dict], list[dict]]: Matching file, missing,
            and error records.
    """

    _read_bundle_header(repo_root, bundle_id, actor_id)
    file_rows = _read_bundle_records(
        repo_root,
        bundle_id,
        paths,
        table_name=ONBOARDING_BUNDLE_FILES_TABLE,
        action=ONBOARDING_BUNDLE_FILES_ACTION,
        actor_id=actor_id,
    )
    missing_rows = _read_bundle_records(
        repo_root,
        bundle_id,
        paths,
        table_name=ONBOARDING_BUNDLE_MISSING_TABLE,
        action=ONBOARDING_BUNDLE_MISSING_ACTION,
        actor_id=actor_id,
    )
    error_rows = _read_bundle_records(
        repo_root,
        bundle_id,
        paths,
        table_name=ONBOARDING_BUNDLE_ERRORS_TABLE,
        action=ONBOARDING_BUNDLE_ERRORS_ACTION,
        actor_id=actor_id,
    )
    return file_rows, missing_rows, error_rows


def _validate_bundle_paths(
    command_name: str,
    bundle_id: str,
    paths: list[str],
    file_rows: list[dict],
    missing_rows: list[dict],
    error_rows: list[dict],
) -> None:
    """
    Validate that requested paths are present and error-free in the bundle.

    Args:
        command_name (str): Command name for error context.
        bundle_id (str): Bundle identifier for error context.
        paths (list[str]): Requested paths.
        file_rows (list[dict]): File records loaded from SQLite.
        missing_rows (list[dict]): Missing records for bundle.
        error_rows (list[dict]): Error records for bundle.

    Raises:
        PayloadError: If any requested paths are missing or errored.
    """

    file_paths = {
        row.get("path")
        for row in file_rows
        if isinstance(row, dict) and isinstance(row.get("path"), str)
    }
    missing_paths = {
        row.get("path")
        for row in missing_rows
        if isinstance(row, dict) and isinstance(row.get("path"), str)
    }
    error_paths = {
        row.get("path")
        for row in error_rows
        if isinstance(row, dict) and isinstance(row.get("path"), str)
    }
    requested = set(paths)
    unavailable = {
        path: "missing" for path in sorted(requested & missing_paths)
    }
    unavailable.update({path: "error" for path in sorted(requested & error_paths)})
    not_found = sorted(requested - file_paths - missing_paths - error_paths)
    for path in not_found:
        unavailable[path] = "not_in_bundle"
    if unavailable:
        raise PayloadError(
            code="payload_value_error",
            details={
                "command_name": command_name,
                "bundle_id": bundle_id,
                "message": "Some requested paths are not restorable.",
                "unavailable": unavailable,
            },
        )


def _restore_files(
    file_rows: list[dict],
    target_root: Path,
    allow_overwrite: bool,
) -> list[str]:
    """
    Restore onboarding bundle files to the target root.

    Args:
        file_rows (list[dict]): File records to restore.
        target_root (Path): Base directory for restores.
        allow_overwrite (bool): Whether to overwrite existing files.

    Returns:
        list[str]: Restored relative paths.

    Raises:
        FileExistsError: If a file exists and overwrite is not allowed.
        ValueError: If an output path escapes the target root.
    """

    restored: list[str] = []
    target_root.mkdir(parents=True, exist_ok=True)
    if target_root.exists() and not target_root.is_dir():
        raise ValueError(f"Target root is not a directory: {target_root}")
    for row in file_rows:
        path_value = row.get("path")
        content = row.get("content")
        if not isinstance(path_value, str):
            raise ValueError("onboarding bundle restore encountered a row without path.")
        if not isinstance(content, str):
            raise ValueError("onboarding bundle restore encountered a row without content.")
        output_path = _safe_output_path(target_root, path_value)
        if output_path.exists() and not allow_overwrite:
            raise FileExistsError(f"Refusing to overwrite: {output_path}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        _write_text_atomic(output_path, content)
        restored.append(path_value)
    return restored


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Restore onboarding bundle files using the command runner contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing restored path details.

    Raises:
        None: All errors are returned as CommandResult payloads.

    Contract:
        - bundle_id is required.
        - paths is required (explicit list).
        - target_root defaults to repo_root.
        - allow_overwrite defaults to False.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        bundle_id = require_string(payload, "bundle_id", command_name)
        raw_paths = optional_list(payload, "paths", command_name=command_name)
        allow_overwrite = optional_bool(
            payload, "allow_overwrite", command_name=command_name, default=False
        )
        target_root_value = optional_string(
            payload, "target_root", command_name=command_name
        )
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    try:
        paths = _validate_restore_paths(raw_paths or [], command_name)
        target_root = _resolve_target_root(repo_root, target_root_value)
        actor_id = _resolve_actor_id(ctx)
        file_rows, missing_rows, error_rows = _load_bundle_rows(
            repo_root, bundle_id, paths, actor_id
        )
        _validate_bundle_paths(
            command_name, bundle_id, paths, file_rows, missing_rows, error_rows
        )
        restored = _restore_files(file_rows, target_root, bool(allow_overwrite))
        output = {
            "bundle_id": bundle_id,
            "target_root": target_root.as_posix(),
            "restored_paths": restored,
            "restored_count": len(restored),
            "allow_overwrite": bool(allow_overwrite),
        }
        return ok_result(output=output, artifacts=[])
    except PayloadError as exc:
        return payload_error_result(command_name, exc)
    except Exception as exc:
        return exception_result(
            command_name,
            exc,
            details={
                "bundle_id": bundle_id,
                "target_root": target_root_value,
            },
        )


def main() -> None:
    """
    CLI entrypoint for onboarding bundle restore.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """

    parser = argparse.ArgumentParser(
        description="Restore onboarding bundle files from SQLite snapshots"
    )
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--bundle-id", required=True, help="Bundle snapshot id")
    parser.add_argument(
        "--path",
        action="append",
        default=[],
        help="Path to restore (repeatable).",
    )
    parser.add_argument(
        "--target-root",
        default=None,
        help="Target root for restored files (default: repo root).",
    )
    parser.add_argument(
        "--allow-overwrite",
        action="store_true",
        help="Allow overwriting existing files.",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "bundle_id": args.bundle_id,
        "paths": args.path,
        "target_root": args.target_root,
        "allow_overwrite": args.allow_overwrite,
    }
    context = ExecutionContext(
        command_name="onboarding_bundle_restore",
        agent_id=None,
        work_id=None,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("onboarding_bundle_restore failed: %s", result.errors)
        raise SystemExit(1)
    logger.info(
        "Restored %s files to %s",
        result.output.get("restored_count"),
        result.output.get("target_root"),
    )
