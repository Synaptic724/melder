"""
File ctx payload helpers for SQLite query scripts.

Purpose
- Provide shared load/write/delete helpers for file_ctx query scripts.
- Centralize file_ctx payload validation and hydration logic.

Contract
- All functions accept an active SQLAlchemy session; they do not open sessions.
- Validation raises ValueError with file_ctx-specific messages.
- Payloads emitted by build_file_ctx_payload conform to file_ctx.schema.json.
"""

from __future__ import annotations

from typing import Any, Iterable

from context_compass.system.ai_restricted._shared.timeutils import utc_now_iso
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

    Contract:
        - Always returns a dict when validation succeeds.
        - Raises ValueError with file_ctx-prefixed context.
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

    Contract:
        - Returns a non-empty string.
        - Raises ValueError with file_ctx-prefixed context.
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

    Contract:
        - Accepts null values as None.
        - Raises ValueError with file_ctx-prefixed context on type mismatches.
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

    Contract:
        - Accepts null values as None.
        - Raises ValueError with file_ctx-prefixed context on type mismatches.
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

    Contract:
        - Accepts null values as None.
        - Raises ValueError with file_ctx-prefixed context on type mismatches.
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

    Contract:
        - Treats null values as an empty list.
        - Raises ValueError with file_ctx-prefixed context on type mismatches.
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

    Contract:
        - Returns lists ordered by position ascending.
        - Missing item types are omitted from the result.
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


def build_file_ctx_payload(session: Any, row: FileCtx) -> dict[str, Any]:
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
        {"title": item.title, "code": item.code} for item in examples_snippets
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


def load_file_ctx_snapshot(
    session: Any,
    branch_name: str,
    file_path: str,
) -> tuple[dict[str, Any], bool]:
    """
    Load a file_ctx payload for a file path.

    Args:
        session (Any): Active SQLAlchemy session.
        branch_name (str): Branch identifier.
        file_path (str): Repo-relative file path.

    Returns:
        tuple[dict[str, Any], bool]: Payload and exists flag.

    Contract:
        - Returns an empty payload with exists False when no row is found.
    """

    row = session.get(FileCtx, (branch_name, file_path))
    if row is None:
        return {}, False
    payload = build_file_ctx_payload(session, row)
    return payload, True


def load_file_ctx_snapshot_by_ctx_path(
    session: Any,
    branch_name: str,
    ctx_path: str,
) -> tuple[dict[str, Any], bool]:
    """
    Load a file_ctx payload using ctx_path.

    Args:
        session (Any): Active SQLAlchemy session.
        branch_name (str): Branch identifier.
        ctx_path (str): Repo-relative ctx path.

    Returns:
        tuple[dict[str, Any], bool]: Payload and exists flag.

    Contract:
        - Returns an empty payload with exists False when no row is found.
    """

    row = (
        session.query(FileCtx)
        .filter_by(branch_name=branch_name, ctx_path=ctx_path)
        .first()
    )
    if row is None:
        return {}, False
    payload = build_file_ctx_payload(session, row)
    return payload, True


def list_file_ctx_payloads(session: Any, branch_name: str) -> list[dict[str, Any]]:
    """
    List file_ctx payloads for a branch.

    Args:
        session (Any): Active SQLAlchemy session.
        branch_name (str): Branch identifier.

    Returns:
        list[dict[str, Any]]: file_ctx payloads for the branch.
    """

    rows = session.query(FileCtx).filter_by(branch_name=branch_name).all()
    return [build_file_ctx_payload(session, row) for row in rows]


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

    Contract:
        - Sets created/updated audit fields on each row.
        - Does nothing when rows is empty.
    """

    if not rows:
        return
    for row in rows:
        row.created_at = now
        row.created_by = actor_id
        row.updated_at = now
        row.updated_by = actor_id
    session.add_all(rows)


def persist_file_ctx_payload(
    session: Any,
    branch_name: str,
    payload: dict[str, Any],
    actor_id: str,
) -> str:
    """
    Persist a file_ctx payload to SQLite.

    Args:
        session (Any): Active SQLAlchemy session.
        branch_name (str): Branch identifier.
        payload (dict[str, Any]): file_ctx payload.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        str: file_path for the persisted record.

    Raises:
        ValueError: If payload validation fails.

    Contract:
        - Updates updated_at and updated_by on every write.
        - Replaces child rows with the provided payload state.
        - Returns the canonical file_path for subsequent lookups.
    """

    if payload.get("kind") != "file_ctx":
        raise ValueError("file_ctx payload kind must be 'file_ctx'.")

    identity = _require_mapping(payload, "identity")
    agent = _require_mapping(payload, "agent")
    computed = _require_mapping(payload, "computed")

    file_path = _require_string(identity, "path")
    ctx_path = _require_string(identity, "ctx_path")
    language = _require_string(identity, "language")
    module = _optional_string(identity, "module")

    schema_version = payload.get("schema_version")
    if not isinstance(schema_version, int) or schema_version < 1:
        raise ValueError("file_ctx.schema_version must be an integer >= 1.")

    freshness_state = _require_string(computed, "freshness_state")
    staleness_reasons = _string_list(computed, "staleness_reasons")
    checksums = _require_mapping(computed, "checksums")
    last_scan = (
        computed.get("last_scan") if isinstance(computed.get("last_scan"), dict) else {}
    )
    review = computed.get("review") if isinstance(computed.get("review"), dict) else {}
    facts = computed.get("facts") if isinstance(computed.get("facts"), dict) else {}

    code_hash = _optional_string(checksums, "code_hash_sha256")
    ctx_semantic_hash = _optional_string(checksums, "ctx_semantic_hash_sha256")
    template_version = _optional_string(checksums, "template_version")
    analyzer_version = _optional_string(checksums, "analyzer_version")

    last_scan_id = _optional_string(last_scan, "scan_id")
    last_scanned_at = _optional_string(last_scan, "scanned_at")
    review_every = _optional_int(review, "review_every_n_scans")
    scan_counter = _optional_int(review, "scan_counter")
    last_review_scan_id = _optional_string(review, "last_review_scan_id")

    summary = _require_mapping(agent, "summary")
    role_in_system = _require_mapping(agent, "role_in_system")
    public_surface = _require_mapping(agent, "public_surface")
    behavioral_contract = _require_mapping(agent, "behavioral_contract")
    dependencies = _require_mapping(agent, "dependencies")
    dependents = _require_mapping(agent, "dependents")
    lifecycle = _require_mapping(agent, "lifecycle")
    testing = _require_mapping(agent, "testing")
    examples = _require_mapping(agent, "examples")

    role_layer = _require_string(role_in_system, "layer")
    public_interfaces = public_surface.get("interfaces", {})
    if not isinstance(public_interfaces, dict):
        raise ValueError("file_ctx.public_surface.interfaces must be a JSON object.")

    error_model = _require_mapping(behavioral_contract, "error_model")
    error_logging = _require_string(error_model, "logging")

    cleanup = _require_mapping(lifecycle, "cleanup")
    threading = _require_mapping(lifecycle, "threading")
    cleanup_has_cleanup = _optional_bool(cleanup, "has_cleanup")
    if cleanup_has_cleanup is None:
        raise ValueError("file_ctx.lifecycle.cleanup.has_cleanup must be a boolean.")
    threading_thread_safe = _optional_bool(threading, "thread_safe")
    if threading_thread_safe is None:
        raise ValueError("file_ctx.lifecycle.threading.thread_safe must be a boolean.")
    threading_async = _optional_bool(threading, "async")
    if threading_async is None:
        raise ValueError("file_ctx.lifecycle.threading.async must be a boolean.")

    now = utc_now_iso()
    existing = session.get(FileCtx, (branch_name, file_path))
    created_at = existing.created_at if existing else now
    created_by = existing.created_by if existing else actor_id

    core = FileCtx(
        branch_name=branch_name,
        file_path=file_path,
        ctx_path=ctx_path,
        language=language,
        module=module,
        schema_version=schema_version,
        freshness_state=freshness_state,
        last_scan_id=last_scan_id,
        last_scanned_at=last_scanned_at,
        review_every_n_scans=review_every,
        scan_counter=scan_counter,
        last_review_scan_id=last_review_scan_id,
        code_hash_sha256=code_hash,
        ctx_semantic_hash_sha256=ctx_semantic_hash,
        template_version=template_version,
        analyzer_version=analyzer_version,
        created_at=created_at,
        created_by=created_by,
        updated_at=now,
        updated_by=actor_id,
    )
    session.merge(core)

    session.query(FileCtxStalenessReason).filter_by(
        branch_name=branch_name, file_path=file_path
    ).delete()
    session.query(FileCtxAgentSummary).filter_by(
        branch_name=branch_name, file_path=file_path
    ).delete()
    session.query(FileCtxAgentRole).filter_by(
        branch_name=branch_name, file_path=file_path
    ).delete()
    session.query(FileCtxAgentRoleItem).filter_by(
        branch_name=branch_name, file_path=file_path
    ).delete()
    session.query(FileCtxAgentPublicSurfaceItem).filter_by(
        branch_name=branch_name, file_path=file_path
    ).delete()
    session.query(FileCtxAgentBehavioralContract).filter_by(
        branch_name=branch_name, file_path=file_path
    ).delete()
    session.query(FileCtxAgentBehavioralContractItem).filter_by(
        branch_name=branch_name, file_path=file_path
    ).delete()
    session.query(FileCtxAgentErrorModelItem).filter_by(
        branch_name=branch_name, file_path=file_path
    ).delete()
    session.query(FileCtxAgentDependencyItem).filter_by(
        branch_name=branch_name, file_path=file_path
    ).delete()
    session.query(FileCtxAgentDependents).filter_by(
        branch_name=branch_name, file_path=file_path
    ).delete()
    session.query(FileCtxAgentDependentItem).filter_by(
        branch_name=branch_name, file_path=file_path
    ).delete()
    session.query(FileCtxAgentLifecycle).filter_by(
        branch_name=branch_name, file_path=file_path
    ).delete()
    session.query(FileCtxAgentLifecycleItem).filter_by(
        branch_name=branch_name, file_path=file_path
    ).delete()
    session.query(FileCtxAgentTestingItem).filter_by(
        branch_name=branch_name, file_path=file_path
    ).delete()
    session.query(FileCtxAgentExampleSnippet).filter_by(
        branch_name=branch_name, file_path=file_path
    ).delete()
    session.query(FileCtxAgentExampleItem).filter_by(
        branch_name=branch_name, file_path=file_path
    ).delete()
    session.query(FileCtxAgentChangeRiskItem).filter_by(
        branch_name=branch_name, file_path=file_path
    ).delete()
    session.query(FileCtxFactSymbol).filter_by(
        branch_name=branch_name, file_path=file_path
    ).delete()
    session.query(FileCtxFactImport).filter_by(
        branch_name=branch_name, file_path=file_path
    ).delete()
    session.query(FileCtxFactExport).filter_by(
        branch_name=branch_name, file_path=file_path
    ).delete()

    rows: list[Any] = []
    rows.extend(
        FileCtxStalenessReason(
            branch_name=branch_name,
            file_path=file_path,
            position=idx,
            reason=reason,
        )
        for idx, reason in enumerate(staleness_reasons, start=1)
    )

    rows.append(
        FileCtxAgentSummary(
            branch_name=branch_name,
            file_path=file_path,
            one_liner=_require_string(summary, "one_liner"),
            detail=_require_string(summary, "detail"),
        )
    )
    rows.append(
        FileCtxAgentRole(
            branch_name=branch_name,
            file_path=file_path,
            layer=role_layer,
        )
    )
    rows.append(
        FileCtxAgentBehavioralContract(
            branch_name=branch_name,
            file_path=file_path,
            error_logging=error_logging,
        )
    )
    rows.append(
        FileCtxAgentDependents(
            branch_name=branch_name,
            file_path=file_path,
            notes=_require_string(dependents, "notes"),
        )
    )
    rows.append(
        FileCtxAgentLifecycle(
            branch_name=branch_name,
            file_path=file_path,
            construction=_require_string(lifecycle, "construction"),
            ownership=_require_string(lifecycle, "ownership"),
            cleanup_has_cleanup=cleanup_has_cleanup,
            threading_thread_safe=threading_thread_safe,
            threading_async=threading_async,
        )
    )

    role_items = {
        "responsibilities": _string_list(role_in_system, "responsibilities"),
        "non_goals": _string_list(role_in_system, "non_goals"),
        "invariants": _string_list(role_in_system, "invariants"),
        "pitfalls": _string_list(role_in_system, "pitfalls"),
    }
    for item_type, values in role_items.items():
        rows.extend(
            FileCtxAgentRoleItem(
                branch_name=branch_name,
                file_path=file_path,
                item_type=item_type,
                position=idx,
                value=value,
            )
            for idx, value in enumerate(values, start=1)
        )

    public_items = {
        "entrypoints": _string_list(public_surface, "entrypoints"),
        "exports": _string_list(public_surface, "exports"),
        "interfaces_abc": _string_list(public_interfaces, "abc"),
        "interfaces_datamodels": _string_list(public_interfaces, "datamodels"),
        "interfaces_protocols": _string_list(public_interfaces, "protocols"),
    }
    for item_type, values in public_items.items():
        rows.extend(
            FileCtxAgentPublicSurfaceItem(
                branch_name=branch_name,
                file_path=file_path,
                item_type=item_type,
                position=idx,
                value=value,
            )
            for idx, value in enumerate(values, start=1)
        )

    contract_items = {
        "inputs": _string_list(behavioral_contract, "inputs"),
        "outputs": _string_list(behavioral_contract, "outputs"),
        "side_effects": _string_list(behavioral_contract, "side_effects"),
    }
    for item_type, values in contract_items.items():
        rows.extend(
            FileCtxAgentBehavioralContractItem(
                branch_name=branch_name,
                file_path=file_path,
                item_type=item_type,
                position=idx,
                value=value,
            )
            for idx, value in enumerate(values, start=1)
        )

    error_items = {
        "raises": _string_list(error_model, "raises"),
        "retryable": _string_list(error_model, "retryable"),
    }
    for item_type, values in error_items.items():
        rows.extend(
            FileCtxAgentErrorModelItem(
                branch_name=branch_name,
                file_path=file_path,
                item_type=item_type,
                position=idx,
                value=value,
            )
            for idx, value in enumerate(values, start=1)
        )

    dependency_items = {
        "internal_imports": _string_list(dependencies, "internal_imports"),
        "external_imports": _string_list(dependencies, "external_imports"),
        "runtime_couplings": _string_list(dependencies, "runtime_couplings"),
        "depends_on_files": _string_list(dependencies, "depends_on_files"),
    }
    for item_type, values in dependency_items.items():
        rows.extend(
            FileCtxAgentDependencyItem(
                branch_name=branch_name,
                file_path=file_path,
                item_type=item_type,
                position=idx,
                value=value,
            )
            for idx, value in enumerate(values, start=1)
        )

    dependents_items = {
        "used_by_files": _string_list(dependents, "used_by_files"),
        "used_by_dirs": _string_list(dependents, "used_by_dirs"),
    }
    for item_type, values in dependents_items.items():
        rows.extend(
            FileCtxAgentDependentItem(
                branch_name=branch_name,
                file_path=file_path,
                item_type=item_type,
                position=idx,
                value=value,
            )
            for idx, value in enumerate(values, start=1)
        )

    cleanup_items = {
        "cleanup_method_names": _string_list(cleanup, "method_names"),
        "cleanup_order_constraints": _string_list(cleanup, "order_constraints"),
    }
    threading_items = {"threading_locks": _string_list(threading, "locks")}
    for item_type, values in {**cleanup_items, **threading_items}.items():
        rows.extend(
            FileCtxAgentLifecycleItem(
                branch_name=branch_name,
                file_path=file_path,
                item_type=item_type,
                position=idx,
                value=value,
            )
            for idx, value in enumerate(values, start=1)
        )

    testing_items = {
        "test_types": _string_list(testing, "test_types"),
        "commands": _string_list(testing, "commands"),
        "mocks": _string_list(testing, "mocks"),
        "fixtures": _string_list(testing, "fixtures"),
        "coverage_expectations": _string_list(testing, "coverage_expectations"),
    }
    for item_type, values in testing_items.items():
        rows.extend(
            FileCtxAgentTestingItem(
                branch_name=branch_name,
                file_path=file_path,
                item_type=item_type,
                position=idx,
                value=value,
            )
            for idx, value in enumerate(values, start=1)
        )

    usage_snippets = examples.get("usage_snippets", [])
    if usage_snippets is None:
        usage_snippets = []
    if not isinstance(usage_snippets, list):
        raise ValueError("file_ctx.examples.usage_snippets must be a list.")
    for idx, snippet in enumerate(usage_snippets, start=1):
        if not isinstance(snippet, dict):
            raise ValueError("file_ctx.examples.usage_snippets entries must be objects.")
        rows.append(
            FileCtxAgentExampleSnippet(
                branch_name=branch_name,
                file_path=file_path,
                position=idx,
                title=_require_string(snippet, "title"),
                code=_require_string(snippet, "code"),
            )
        )

    integration_flow = _string_list(examples, "integration_flow")
    rows.extend(
        FileCtxAgentExampleItem(
            branch_name=branch_name,
            file_path=file_path,
            item_type="integration_flow",
            position=idx,
            value=value,
        )
        for idx, value in enumerate(integration_flow, start=1)
    )

    change_risk = agent.get("change_risk")
    if isinstance(change_risk, dict):
        change_risk_items = {
            "review_triggers": _string_list(change_risk, "review_triggers"),
            "risky_changes": _string_list(change_risk, "risky_changes"),
            "safe_changes": _string_list(change_risk, "safe_changes"),
        }
        for item_type, values in change_risk_items.items():
            rows.extend(
                FileCtxAgentChangeRiskItem(
                    branch_name=branch_name,
                    file_path=file_path,
                    item_type=item_type,
                    position=idx,
                    value=value,
                )
                for idx, value in enumerate(values, start=1)
            )

    symbols = facts.get("symbols", []) if isinstance(facts, dict) else []
    if symbols is None:
        symbols = []
    if not isinstance(symbols, list):
        raise ValueError("file_ctx.computed.facts.symbols must be a list.")
    for idx, symbol in enumerate(symbols, start=1):
        if not isinstance(symbol, dict):
            raise ValueError("file_ctx.computed.facts.symbols entries must be objects.")
        rows.append(
            FileCtxFactSymbol(
                branch_name=branch_name,
                file_path=file_path,
                position=idx,
                name=_require_string(symbol, "name"),
                kind=_optional_string(symbol, "kind"),
                signature=_optional_string(symbol, "signature"),
                docstring=_optional_string(symbol, "docstring"),
                lineno_start=_optional_int(symbol, "lineno_start"),
                lineno_end=_optional_int(symbol, "lineno_end"),
            )
        )

    imports = _string_list(facts, "imports") if isinstance(facts, dict) else []
    rows.extend(
        FileCtxFactImport(
            branch_name=branch_name,
            file_path=file_path,
            position=idx,
            value=value,
        )
        for idx, value in enumerate(imports, start=1)
    )

    exports = _string_list(facts, "exports") if isinstance(facts, dict) else []
    rows.extend(
        FileCtxFactExport(
            branch_name=branch_name,
            file_path=file_path,
            position=idx,
            value=value,
        )
        for idx, value in enumerate(exports, start=1)
    )

    _persist_items(session, now, actor_id, rows)
    return file_path


def delete_file_ctx_by_branch(session: Any, branch_name: str) -> bool:
    """
    Delete all file_ctx records for a branch.

    Args:
        session (Any): Active SQLAlchemy session.
        branch_name (str): Branch identifier.

    Returns:
        bool: True if any file_ctx rows existed before deletion.

    Contract:
        - Deletes child rows before core file_ctx rows.
        - Returns False when no rows were present.
    """

    has_rows = (
        session.query(FileCtx.branch_name).filter_by(branch_name=branch_name).first()
        is not None
    )
    session.query(FileCtxStalenessReason).filter_by(branch_name=branch_name).delete()
    session.query(FileCtxAgentSummary).filter_by(branch_name=branch_name).delete()
    session.query(FileCtxAgentRole).filter_by(branch_name=branch_name).delete()
    session.query(FileCtxAgentRoleItem).filter_by(branch_name=branch_name).delete()
    session.query(FileCtxAgentPublicSurfaceItem).filter_by(branch_name=branch_name).delete()
    session.query(FileCtxAgentBehavioralContract).filter_by(branch_name=branch_name).delete()
    session.query(FileCtxAgentBehavioralContractItem).filter_by(branch_name=branch_name).delete()
    session.query(FileCtxAgentErrorModelItem).filter_by(branch_name=branch_name).delete()
    session.query(FileCtxAgentDependencyItem).filter_by(branch_name=branch_name).delete()
    session.query(FileCtxAgentDependents).filter_by(branch_name=branch_name).delete()
    session.query(FileCtxAgentDependentItem).filter_by(branch_name=branch_name).delete()
    session.query(FileCtxAgentLifecycle).filter_by(branch_name=branch_name).delete()
    session.query(FileCtxAgentLifecycleItem).filter_by(branch_name=branch_name).delete()
    session.query(FileCtxAgentTestingItem).filter_by(branch_name=branch_name).delete()
    session.query(FileCtxAgentExampleSnippet).filter_by(branch_name=branch_name).delete()
    session.query(FileCtxAgentExampleItem).filter_by(branch_name=branch_name).delete()
    session.query(FileCtxAgentChangeRiskItem).filter_by(branch_name=branch_name).delete()
    session.query(FileCtxFactSymbol).filter_by(branch_name=branch_name).delete()
    session.query(FileCtxFactImport).filter_by(branch_name=branch_name).delete()
    session.query(FileCtxFactExport).filter_by(branch_name=branch_name).delete()
    session.query(FileCtx).filter_by(branch_name=branch_name).delete()
    return has_rows
