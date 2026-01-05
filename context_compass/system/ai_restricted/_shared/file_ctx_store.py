"""
SQLite-backed helpers for file_ctx records stored in normalized tables.

Purpose
- Route file_ctx reads/writes/deletes through sqlite_query scripts.
- Keep file_ctx payloads aligned to file_ctx.schema.json at command boundaries.

Contract
- Primary key for file_ctx is (branch_name, file_path).
- Query scripts must be registered in db_query_registry for user scope.
- Payloads returned by query scripts are treated as immutable snapshots.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from context_compass.system.ai_restricted.database_management import sqlite_query
from context_compass.system.ai_restricted.database_management.orm_session import user_db_path
from context_compass.system.ai_restricted.database_management.user_orm_models import (
    FileCtx,
    FileCtxAgentBehavioralContract,
    FileCtxAgentBehavioralContractItem,
    FileCtxAgentChangeRiskItem,
    FileCtxAgentDependentItem,
    FileCtxAgentDependents,
    FileCtxAgentDependencyItem,
    FileCtxAgentErrorModelItem,
    FileCtxAgentExampleItem,
    FileCtxAgentExampleSnippet,
    FileCtxAgentLifecycle,
    FileCtxAgentLifecycleItem,
    FileCtxAgentPublicSurfaceItem,
    FileCtxAgentRole,
    FileCtxAgentRoleItem,
    FileCtxAgentSummary,
    FileCtxAgentTestingItem,
    FileCtxFactExport,
    FileCtxFactImport,
    FileCtxFactSymbol,
    FileCtxStalenessReason,
)


READ_FILE_CTX_QUERY = "read_file_ctx_by_file_path"
READ_FILE_CTX_BY_CTX_PATH_QUERY = "read_file_ctx_by_ctx_path"
LIST_FILE_CTX_QUERY = "list_file_ctx_payloads"
WRITE_FILE_CTX_QUERY = "write_file_ctx"
DELETE_FILE_CTX_BY_BRANCH_QUERY = "delete_file_ctx_by_branch"


@dataclass(frozen=True)
class FileCtxSnapshot:
    """
    Snapshot of a file_ctx payload.

    Attributes:
        payload (dict[str, Any]): Context payload.
        exists (bool): True if the record exists in SQLite.

    Contract:
        - payload is always a dict.
        - exists reports whether the record was found.
    """

    payload: dict[str, Any]
    exists: bool


def lock_resource(branch_name: str, file_path: str) -> Path:
    """
    Build a synthetic lock resource path for file_ctx updates.

    Args:
        branch_name (str): Branch identifier.
        file_path (str): Repo-relative file path.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"file_ctx::{branch_name}::{file_path}")


def _raise_query_error(exc: sqlite_query.SqliteQueryError, repo_root: Path) -> None:
    """
    Raise a consistent error for query failures.

    Args:
        exc (sqlite_query.SqliteQueryError): Query error to map.
        repo_root (Path): Repository root for error context.

    Raises:
        FileNotFoundError: If user.db is missing.
        ValueError: If the query payload is invalid.
        sqlite_query.SqliteQueryError: For unexpected query failures.
    """

    if exc.code == "db_missing":
        db_path = user_db_path(repo_root)
        raise FileNotFoundError(f"User database not found: {db_path}") from exc
    if exc.code.startswith("payload_"):
        details = json.dumps(exc.details, ensure_ascii=True)
        raise ValueError(f"{exc.meaning} Details: {details}") from exc
    raise exc


def _require_mapping(payload: dict, key: str) -> dict:
    """
    Require a mapping field in a payload.

    Args:
        payload (dict): Payload to inspect.
        key (str): Mapping key to extract.

    Returns:
        dict: Mapping value.

    Raises:
        ValueError: If the mapping is missing or invalid.
    """

    value = payload.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"file_ctx.{key} must be a JSON object.")
    return value


def _require_string(payload: dict, key: str) -> str:
    """
    Require a string field in a payload.

    Args:
        payload (dict): Payload to inspect.
        key (str): Field name to extract.

    Returns:
        str: Field value.

    Raises:
        ValueError: If the field is missing or not a string.
    """

    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"file_ctx.{key} must be a non-empty string.")
    return value


def _optional_string(payload: dict, key: str) -> str | None:
    """
    Return an optional string field.

    Args:
        payload (dict): Payload to inspect.
        key (str): Field name to extract.

    Returns:
        str | None: Field value if present.

    Raises:
        ValueError: If the field is not a string when provided.
    """

    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"file_ctx.{key} must be a string or null.")
    return value


def _optional_int(payload: dict, key: str) -> int | None:
    """
    Return an optional integer field.

    Args:
        payload (dict): Payload to inspect.
        key (str): Field name to extract.

    Returns:
        int | None: Field value if present.

    Raises:
        ValueError: If the field is not an integer when provided.
    """

    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, int):
        raise ValueError(f"file_ctx.{key} must be an integer or null.")
    return value


def _optional_bool(payload: dict, key: str) -> bool | None:
    """
    Return an optional boolean field.

    Args:
        payload (dict): Payload to inspect.
        key (str): Field name to extract.

    Returns:
        bool | None: Field value if present.

    Raises:
        ValueError: If the field is not a boolean when provided.
    """

    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ValueError(f"file_ctx.{key} must be a boolean or null.")
    return value


def _string_list(payload: dict, key: str) -> list[str]:
    """
    Return a list of strings from a payload field.

    Args:
        payload (dict): Payload to inspect.
        key (str): Field name to extract.

    Returns:
        list[str]: List of strings.

    Raises:
        ValueError: If the field is missing or not a list of strings.
    """

    value = payload.get(key, [])
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"file_ctx.{key} must be a JSON array.")
    items: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError(f"file_ctx.{key} items must be strings.")
        items.append(item)
    return items


def _items_by_type(rows: Iterable[Any]) -> dict[str, list[str]]:
    """
    Group item rows by item_type with position ordering.

    Args:
        rows (Iterable[Any]): Rows with item_type, position, and value attributes.

    Returns:
        dict[str, list[str]]: Item values grouped by item_type.
    """

    grouped: dict[str, list[tuple[int, str]]] = {}
    for row in rows:
        grouped.setdefault(row.item_type, []).append((row.position, row.value))
    return {
        item_type: [value for _, value in sorted(items, key=lambda pair: pair[0])]
        for item_type, items in grouped.items()
    }


def _snapshot_checksums(row: FileCtx) -> dict:
    """
    Build a checksums payload from a FileCtx row.

    Args:
        row (FileCtx): Core row instance.

    Returns:
        dict: Checksums payload.
    """

    return {
        "code_hash_sha256": row.code_hash_sha256,
        "ctx_semantic_hash_sha256": row.ctx_semantic_hash_sha256,
        "template_version": row.template_version,
        "analyzer_version": row.analyzer_version,
    }


def _snapshot_review(row: FileCtx) -> dict:
    """
    Build a review payload from a FileCtx row.

    Args:
        row (FileCtx): Core row instance.

    Returns:
        dict: Review payload.
    """

    return {
        "review_every_n_scans": row.review_every_n_scans,
        "scan_counter": row.scan_counter,
        "last_review_scan_id": row.last_review_scan_id,
    }


def _snapshot_last_scan(row: FileCtx) -> dict:
    """
    Build a last_scan payload from a FileCtx row.

    Args:
        row (FileCtx): Core row instance.

    Returns:
        dict: Last scan payload.
    """

    return {
        "scan_id": row.last_scan_id,
        "scanned_at": row.last_scanned_at,
    }


def _build_payload(session: Any, row: FileCtx) -> dict[str, Any]:
    """
    Build a file_ctx payload from database rows.

    Args:
        session (Any): Active SQLAlchemy session.
        row (FileCtx): Core row instance.

    Returns:
        dict[str, Any]: file_ctx payload.
    """

    reasons = (
        session.query(FileCtxStalenessReason)
        .filter_by(branch_name=row.branch_name, file_path=row.file_path)
        .order_by(FileCtxStalenessReason.position)
        .all()
    )
    summary = session.get(FileCtxAgentSummary, (row.branch_name, row.file_path))
    role = session.get(FileCtxAgentRole, (row.branch_name, row.file_path))
    dependents = session.get(FileCtxAgentDependents, (row.branch_name, row.file_path))
    lifecycle = session.get(FileCtxAgentLifecycle, (row.branch_name, row.file_path))
    behavioral_contract = session.get(
        FileCtxAgentBehavioralContract, (row.branch_name, row.file_path)
    )

    role_items = (
        session.query(FileCtxAgentRoleItem)
        .filter_by(branch_name=row.branch_name, file_path=row.file_path)
        .order_by(FileCtxAgentRoleItem.position)
        .all()
    )
    public_items = (
        session.query(FileCtxAgentPublicSurfaceItem)
        .filter_by(branch_name=row.branch_name, file_path=row.file_path)
        .order_by(FileCtxAgentPublicSurfaceItem.position)
        .all()
    )
    contract_items = (
        session.query(FileCtxAgentBehavioralContractItem)
        .filter_by(branch_name=row.branch_name, file_path=row.file_path)
        .order_by(FileCtxAgentBehavioralContractItem.position)
        .all()
    )
    error_items = (
        session.query(FileCtxAgentErrorModelItem)
        .filter_by(branch_name=row.branch_name, file_path=row.file_path)
        .order_by(FileCtxAgentErrorModelItem.position)
        .all()
    )
    dependency_items = (
        session.query(FileCtxAgentDependencyItem)
        .filter_by(branch_name=row.branch_name, file_path=row.file_path)
        .order_by(FileCtxAgentDependencyItem.position)
        .all()
    )
    dependent_items = (
        session.query(FileCtxAgentDependentItem)
        .filter_by(branch_name=row.branch_name, file_path=row.file_path)
        .order_by(FileCtxAgentDependentItem.position)
        .all()
    )
    lifecycle_items = (
        session.query(FileCtxAgentLifecycleItem)
        .filter_by(branch_name=row.branch_name, file_path=row.file_path)
        .order_by(FileCtxAgentLifecycleItem.position)
        .all()
    )
    testing_items = (
        session.query(FileCtxAgentTestingItem)
        .filter_by(branch_name=row.branch_name, file_path=row.file_path)
        .order_by(FileCtxAgentTestingItem.position)
        .all()
    )
    examples_snippets = (
        session.query(FileCtxAgentExampleSnippet)
        .filter_by(branch_name=row.branch_name, file_path=row.file_path)
        .order_by(FileCtxAgentExampleSnippet.position)
        .all()
    )
    examples_items = (
        session.query(FileCtxAgentExampleItem)
        .filter_by(branch_name=row.branch_name, file_path=row.file_path)
        .order_by(FileCtxAgentExampleItem.position)
        .all()
    )
    change_risk_items = (
        session.query(FileCtxAgentChangeRiskItem)
        .filter_by(branch_name=row.branch_name, file_path=row.file_path)
        .order_by(FileCtxAgentChangeRiskItem.position)
        .all()
    )
    fact_symbols = (
        session.query(FileCtxFactSymbol)
        .filter_by(branch_name=row.branch_name, file_path=row.file_path)
        .order_by(FileCtxFactSymbol.position)
        .all()
    )
    fact_imports = (
        session.query(FileCtxFactImport)
        .filter_by(branch_name=row.branch_name, file_path=row.file_path)
        .order_by(FileCtxFactImport.position)
        .all()
    )
    fact_exports = (
        session.query(FileCtxFactExport)
        .filter_by(branch_name=row.branch_name, file_path=row.file_path)
        .order_by(FileCtxFactExport.position)
        .all()
    )

    role_map = _items_by_type(role_items)
    public_map = _items_by_type(public_items)
    contract_map = _items_by_type(contract_items)
    error_map = _items_by_type(error_items)
    dependency_map = _items_by_type(dependency_items)
    dependent_map = _items_by_type(dependent_items)
    lifecycle_map = _items_by_type(lifecycle_items)
    testing_map = _items_by_type(testing_items)
    examples_map = _items_by_type(examples_items)
    change_risk_map = _items_by_type(change_risk_items)

    snippets_payload = [
        {"title": row.title, "code": row.code} for row in examples_snippets
    ]

    facts_payload: dict[str, Any] = {}
    if fact_symbols:
        facts_payload["symbols"] = [
            {
                "name": symbol.name,
                "kind": symbol.kind,
                "signature": symbol.signature,
                "docstring": symbol.docstring,
                "lineno_start": symbol.lineno_start,
                "lineno_end": symbol.lineno_end,
            }
            for symbol in fact_symbols
        ]
    if fact_imports:
        facts_payload["imports"] = [item.value for item in fact_imports]
    if fact_exports:
        facts_payload["exports"] = [item.value for item in fact_exports]

    agent_payload = {
        "summary": {
            "one_liner": summary.one_liner if summary else None,
            "detail": summary.detail if summary else None,
        },
        "role_in_system": {
            "layer": role.layer if role else None,
            "responsibilities": role_map.get("responsibilities", []),
            "non_goals": role_map.get("non_goals", []),
            "invariants": role_map.get("invariants", []),
            "pitfalls": role_map.get("pitfalls", []),
        },
        "public_surface": {
            "entrypoints": public_map.get("entrypoints", []),
            "exports": public_map.get("exports", []),
            "interfaces": {
                "abc": public_map.get("interfaces_abc", []),
                "datamodels": public_map.get("interfaces_datamodels", []),
                "protocols": public_map.get("interfaces_protocols", []),
            },
        },
        "behavioral_contract": {
            "inputs": contract_map.get("inputs", []),
            "outputs": contract_map.get("outputs", []),
            "side_effects": contract_map.get("side_effects", []),
            "error_model": {
                "logging": behavioral_contract.error_logging if behavioral_contract else None,
                "raises": error_map.get("raises", []),
                "retryable": error_map.get("retryable", []),
            },
        },
        "dependencies": {
            "internal_imports": dependency_map.get("internal_imports", []),
            "external_imports": dependency_map.get("external_imports", []),
            "runtime_couplings": dependency_map.get("runtime_couplings", []),
            "depends_on_files": dependency_map.get("depends_on_files", []),
        },
        "dependents": {
            "used_by_files": dependent_map.get("used_by_files", []),
            "used_by_dirs": dependent_map.get("used_by_dirs", []),
            "notes": dependents.notes if dependents else None,
        },
        "lifecycle": {
            "construction": lifecycle.construction if lifecycle else None,
            "ownership": lifecycle.ownership if lifecycle else None,
            "cleanup": {
                "has_cleanup": lifecycle.cleanup_has_cleanup if lifecycle else None,
                "method_names": lifecycle_map.get("cleanup_method_names", []),
                "order_constraints": lifecycle_map.get("cleanup_order_constraints", []),
            },
            "threading": {
                "thread_safe": lifecycle.threading_thread_safe if lifecycle else None,
                "locks": lifecycle_map.get("threading_locks", []),
                "async": lifecycle.threading_async if lifecycle else None,
            },
        },
        "testing": {
            "test_types": testing_map.get("test_types", []),
            "commands": testing_map.get("commands", []),
            "mocks": testing_map.get("mocks", []),
            "fixtures": testing_map.get("fixtures", []),
            "coverage_expectations": testing_map.get("coverage_expectations", []),
        },
        "examples": {
            "usage_snippets": snippets_payload,
            "integration_flow": examples_map.get("integration_flow", []),
        },
    }

    if change_risk_map:
        agent_payload["change_risk"] = {
            "review_triggers": change_risk_map.get("review_triggers", []),
            "risky_changes": change_risk_map.get("risky_changes", []),
            "safe_changes": change_risk_map.get("safe_changes", []),
        }

    computed_payload = {
        "freshness_state": row.freshness_state,
        "staleness_reasons": [item.reason for item in reasons],
        "checksums": _snapshot_checksums(row),
        "last_scan": _snapshot_last_scan(row),
        "review": _snapshot_review(row),
    }
    if facts_payload:
        computed_payload["facts"] = facts_payload

    payload = {
        "kind": "file_ctx",
        "schema_version": row.schema_version,
        "identity": {
            "path": row.file_path,
            "ctx_path": row.ctx_path,
            "language": row.language,
            "module": row.module,
        },
        "agent": agent_payload,
        "computed": computed_payload,
    }
    return payload


def load_file_ctx(
    repo_root: Path,
    branch_name: str,
    file_path: str,
    actor_id: str,
) -> FileCtxSnapshot:
    """
    Load a file_ctx payload from SQLite.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        file_path (str): Repo-relative file path.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        FileCtxSnapshot: Snapshot containing payload and existence flag.

    Raises:
        FileNotFoundError: If user.db is missing.
    """

    try:
        response = sqlite_query.execute_request(
            repo_root,
            sqlite_query.SqliteQueryRequest(
                scope="user",
                query_name=READ_FILE_CTX_QUERY,
                payload={
                    "branch_name": branch_name,
                    "file_path": file_path,
                },
                actor_id=actor_id,
            ),
        )
    except sqlite_query.SqliteQueryError as exc:
        _raise_query_error(exc, repo_root)

    result = response.output.get("result")
    if not isinstance(result, dict):
        raise ValueError("file_ctx read returned an invalid result payload.")
    record_payload = result.get("record")
    exists = result.get("exists")
    if not isinstance(record_payload, dict):
        raise ValueError("file_ctx read returned an invalid record payload.")
    if not isinstance(exists, bool):
        raise ValueError("file_ctx read returned an invalid exists flag.")
    return FileCtxSnapshot(payload=record_payload, exists=exists)


def load_file_ctx_by_ctx_path(
    repo_root: Path,
    branch_name: str,
    ctx_path: str,
) -> FileCtxSnapshot:
    """
    Load a file_ctx payload using its ctx_path value.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        ctx_path (str): Repo-relative ctx path.

    Returns:
        FileCtxSnapshot: Snapshot containing payload and existence flag.

    Raises:
        FileNotFoundError: If user.db is missing.
    """

    try:
        response = sqlite_query.execute_request(
            repo_root,
            sqlite_query.SqliteQueryRequest(
                scope="user",
                query_name=READ_FILE_CTX_BY_CTX_PATH_QUERY,
                payload={
                    "branch_name": branch_name,
                    "ctx_path": ctx_path,
                },
                actor_id="system",
            ),
        )
    except sqlite_query.SqliteQueryError as exc:
        _raise_query_error(exc, repo_root)

    result = response.output.get("result")
    if not isinstance(result, dict):
        raise ValueError("file_ctx read returned an invalid result payload.")
    record_payload = result.get("record")
    exists = result.get("exists")
    if not isinstance(record_payload, dict):
        raise ValueError("file_ctx read returned an invalid record payload.")
    if not isinstance(exists, bool):
        raise ValueError("file_ctx read returned an invalid exists flag.")
    return FileCtxSnapshot(payload=record_payload, exists=exists)


def list_file_ctx(repo_root: Path, branch_name: str) -> list[dict[str, Any]]:
    """
    List file_ctx payloads for a branch.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.

    Returns:
        list[dict[str, Any]]: file_ctx payloads for the branch.

    Raises:
        FileNotFoundError: If user.db is missing.
    """

    try:
        response = sqlite_query.execute_request(
            repo_root,
            sqlite_query.SqliteQueryRequest(
                scope="user",
                query_name=LIST_FILE_CTX_QUERY,
                payload={"branch_name": branch_name},
                actor_id="system",
            ),
        )
    except sqlite_query.SqliteQueryError as exc:
        _raise_query_error(exc, repo_root)

    result = response.output.get("result")
    if not isinstance(result, dict):
        raise ValueError("file_ctx list returned an invalid result payload.")
    records = result.get("records")
    if not isinstance(records, list):
        raise ValueError("file_ctx list returned an invalid records payload.")
    return records


def _persist_items(
    session: Any,
    now: str,
    actor_id: str,
    rows: Iterable[Any],
) -> None:
    """
    Persist rows in bulk within a session.

    Args:
        session (Any): Active SQLAlchemy session.
        now (str): Timestamp for audit fields.
        actor_id (str): Actor identifier for audit fields.
        rows (Iterable[Any]): ORM row instances to add.

    Returns:
        None: Rows are added to the session.
    """

    if not rows:
        return
    for row in rows:
        row.created_at = now
        row.created_by = actor_id
        row.updated_at = now
        row.updated_by = actor_id
    session.add_all(rows)


def write_file_ctx(
    repo_root: Path,
    branch_name: str,
    payload: dict[str, Any],
    actor_id: str,
    *,
    exists: bool,
) -> None:
    """
    Persist a file_ctx payload to SQLite.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        payload (dict[str, Any]): Context payload.
        actor_id (str): Actor identifier for audit logging.
        exists (bool): Whether the record already exists.

    Raises:
        FileNotFoundError: If user.db is missing.
        ValueError: If payload validation fails.

    Contract:
        - Writes are delegated to sqlite_query for atomic persistence.
        - The payload must contain kind=\"file_ctx\".
    """

    if not isinstance(payload, dict):
        raise ValueError("file_ctx payload must be a JSON object.")

    try:
        sqlite_query.execute_request(
            repo_root,
            sqlite_query.SqliteQueryRequest(
                scope="user",
                query_name=WRITE_FILE_CTX_QUERY,
                payload={
                    "branch_name": branch_name,
                    "file_ctx": payload,
                    "exists": exists,
                },
                actor_id=actor_id,
            ),
        )
    except sqlite_query.SqliteQueryError as exc:
        _raise_query_error(exc, repo_root)



def delete_branch_file_ctx(repo_root: Path, branch_name: str) -> None:
    """
    Delete all file_ctx records for a branch.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.

    Returns:
        None: Rows are deleted in-place.

    Raises:
        FileNotFoundError: If user.db is missing.
    """

    try:
        sqlite_query.execute_request(
            repo_root,
            sqlite_query.SqliteQueryRequest(
                scope="user",
                query_name=DELETE_FILE_CTX_BY_BRANCH_QUERY,
                payload={"branch_name": branch_name},
                actor_id="system",
            ),
        )
    except sqlite_query.SqliteQueryError as exc:
        _raise_query_error(exc, repo_root)
