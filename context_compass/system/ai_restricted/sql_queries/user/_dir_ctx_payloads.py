"""
Dir ctx payload helpers for SQLite query scripts.

Purpose
- Provide shared load/write/delete helpers for dir_ctx query scripts.
- Centralize dir_ctx payload validation and hydration logic.

Contract
- All functions accept an active SQLAlchemy session; they do not open sessions.
- Validation raises ValueError with dir_ctx-specific messages.
- Payloads emitted by build_dir_ctx_payload conform to dir_ctx.schema.json.
"""

from __future__ import annotations

from typing import Any, Iterable

from context_compass.system.ai_restricted._shared.timeutils import utc_now_iso
from context_compass.system.ai_restricted.database_management.user_orm_models import (
    DirCtx,
    DirCtxAgentArchitectureItem,
    DirCtxAgentChangeSafetyItem,
    DirCtxAgentDependencyRuleItem,
    DirCtxAgentDependencyRules,
    DirCtxAgentIntegrationItem,
    DirCtxAgentInventoryFile,
    DirCtxAgentInventorySubdir,
    DirCtxAgentKeyFlow,
    DirCtxAgentKeyFlowItem,
    DirCtxAgentSummary,
    DirCtxAgentTestingItem,
    DirCtxStalenessReason,
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
        - Raises ValueError with dir_ctx-prefixed context.
    """

    value = payload.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"dir_ctx.{key} must be a JSON object.")
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
        - Raises ValueError with dir_ctx-prefixed context.
    """

    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"dir_ctx.{key} must be a non-empty string.")
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
        - Raises ValueError with dir_ctx-prefixed context on type mismatches.
    """

    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"dir_ctx.{key} must be a string or null.")
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
        - Raises ValueError with dir_ctx-prefixed context on type mismatches.
    """

    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, int):
        raise ValueError(f"dir_ctx.{key} must be an integer or null.")
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
        - Raises ValueError with dir_ctx-prefixed context on type mismatches.
    """

    value = payload.get(key, [])
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"dir_ctx.{key} must be a JSON array.")
    items: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError(f"dir_ctx.{key} items must be strings.")
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


def _snapshot_checksums(row: DirCtx) -> dict:
    """
    Build a checksums payload from a DirCtx row.

    Args:
        row (DirCtx): Core row instance.

    Returns:
        dict: Checksums payload.
    """

    return {
        "subtree_hash_sha256": row.subtree_hash_sha256,
        "ctx_semantic_hash_sha256": row.ctx_semantic_hash_sha256,
        "template_version": row.template_version,
        "analyzer_version": row.analyzer_version,
    }


def _snapshot_review(row: DirCtx) -> dict:
    """
    Build a review payload from a DirCtx row.

    Args:
        row (DirCtx): Core row instance.

    Returns:
        dict: Review payload.
    """

    return {
        "review_every_n_scans": row.review_every_n_scans,
        "scan_counter": row.scan_counter,
        "last_review_scan_id": row.last_review_scan_id,
    }


def _snapshot_last_scan(row: DirCtx) -> dict:
    """
    Build a last_scan payload from a DirCtx row.

    Args:
        row (DirCtx): Core row instance.

    Returns:
        dict: Last scan payload.
    """

    return {
        "scan_id": row.last_scan_id,
        "scanned_at": row.last_scanned_at,
    }


def build_dir_ctx_payload(session: Any, row: DirCtx) -> dict[str, Any]:
    """
    Build a dir_ctx payload from database rows.

    Args:
        session (Any): Active SQLAlchemy session.
        row (DirCtx): Core row instance.

    Returns:
        dict[str, Any]: dir_ctx payload.

    Contract:
        - Uses child tables to hydrate agent and computed fields.
        - Preserves list ordering from position columns.
    """

    reasons = (
        session.query(DirCtxStalenessReason)
        .filter_by(branch_name=row.branch_name, dir_path=row.dir_path)
        .order_by(DirCtxStalenessReason.position)
        .all()
    )
    summary = session.get(DirCtxAgentSummary, (row.branch_name, row.dir_path))
    dependency_rules = session.get(
        DirCtxAgentDependencyRules, (row.branch_name, row.dir_path)
    )

    architecture_items = (
        session.query(DirCtxAgentArchitectureItem)
        .filter_by(branch_name=row.branch_name, dir_path=row.dir_path)
        .order_by(DirCtxAgentArchitectureItem.position)
        .all()
    )
    dependency_items = (
        session.query(DirCtxAgentDependencyRuleItem)
        .filter_by(branch_name=row.branch_name, dir_path=row.dir_path)
        .order_by(DirCtxAgentDependencyRuleItem.position)
        .all()
    )
    key_flows = (
        session.query(DirCtxAgentKeyFlow)
        .filter_by(branch_name=row.branch_name, dir_path=row.dir_path)
        .order_by(DirCtxAgentKeyFlow.position)
        .all()
    )
    integration_items = (
        session.query(DirCtxAgentIntegrationItem)
        .filter_by(branch_name=row.branch_name, dir_path=row.dir_path)
        .order_by(DirCtxAgentIntegrationItem.position)
        .all()
    )
    testing_items = (
        session.query(DirCtxAgentTestingItem)
        .filter_by(branch_name=row.branch_name, dir_path=row.dir_path)
        .order_by(DirCtxAgentTestingItem.position)
        .all()
    )
    change_safety_items = (
        session.query(DirCtxAgentChangeSafetyItem)
        .filter_by(branch_name=row.branch_name, dir_path=row.dir_path)
        .order_by(DirCtxAgentChangeSafetyItem.position)
        .all()
    )
    inventory_files = (
        session.query(DirCtxAgentInventoryFile)
        .filter_by(branch_name=row.branch_name, dir_path=row.dir_path)
        .order_by(DirCtxAgentInventoryFile.position)
        .all()
    )
    inventory_subdirs = (
        session.query(DirCtxAgentInventorySubdir)
        .filter_by(branch_name=row.branch_name, dir_path=row.dir_path)
        .order_by(DirCtxAgentInventorySubdir.position)
        .all()
    )

    architecture_map = _items_by_type(architecture_items)
    dependency_map = _items_by_type(dependency_items)
    integration_map = _items_by_type(integration_items)
    testing_map = _items_by_type(testing_items)
    change_safety_map = _items_by_type(change_safety_items)

    key_flow_payloads: list[dict] = []
    for flow in key_flows:
        flow_items = (
            session.query(DirCtxAgentKeyFlowItem)
            .filter_by(
                branch_name=flow.branch_name,
                dir_path=flow.dir_path,
                flow_name=flow.flow_name,
            )
            .order_by(DirCtxAgentKeyFlowItem.position)
            .all()
        )
        flow_map = _items_by_type(flow_items)
        key_flow_payloads.append(
            {
                "name": flow.flow_name,
                "steps": flow_map.get("steps", []),
                "invariants": flow_map.get("invariants", []),
            }
        )

    agent_payload = {
        "summary": {
            "one_liner": summary.one_liner if summary else None,
            "detail": summary.detail if summary else None,
        },
        "architecture": {
            "responsibilities": architecture_map.get("responsibilities", []),
            "non_goals": architecture_map.get("non_goals", []),
            "core_concepts": architecture_map.get("core_concepts", []),
            "key_flows": key_flow_payloads,
            "dependency_rules": {
                "allowed_inbound": dependency_map.get("allowed_inbound", []),
                "allowed_outbound": dependency_map.get("allowed_outbound", []),
                "forbidden_dependencies": dependency_map.get("forbidden_dependencies", []),
                "notes": dependency_rules.notes if dependency_rules else None,
            },
        },
        "inventory": {
            "files": [
                {"path": item.file_path, "ctx": item.ctx_path, "role": item.role}
                for item in inventory_files
            ],
            "subdirs": [
                {"path": item.subdir_path, "ctx": item.ctx_path, "role": item.role}
                for item in inventory_subdirs
            ],
        },
        "integration": {
            "entrypoints": integration_map.get("entrypoints", []),
            "used_by": integration_map.get("used_by", []),
            "uses": integration_map.get("uses", []),
            "runtime_notes": integration_map.get("runtime_notes", []),
        },
        "testing": {
            "commands": testing_map.get("commands", []),
            "required_when_changed": testing_map.get("required_when_changed", []),
            "recommended_when_changed": testing_map.get("recommended_when_changed", []),
        },
    }

    if change_safety_map:
        agent_payload["change_safety"] = {
            "review_triggers": change_safety_map.get("review_triggers", []),
            "risky_changes": change_safety_map.get("risky_changes", []),
            "safe_changes": change_safety_map.get("safe_changes", []),
        }

    computed_payload = {
        "freshness_state": row.freshness_state,
        "staleness_reasons": [item.reason for item in reasons],
        "checksums": _snapshot_checksums(row),
        "last_scan": _snapshot_last_scan(row),
        "review": _snapshot_review(row),
    }

    payload = {
        "kind": "dir_ctx",
        "schema_version": row.schema_version,
        "identity": {
            "dir_path": row.dir_path,
            "ctx_path": row.ctx_path,
            "name": row.name,
        },
        "agent": agent_payload,
        "computed": computed_payload,
    }
    return payload


def load_dir_ctx_snapshot(
    session: Any, branch_name: str, dir_path: str
) -> tuple[dict[str, Any], bool]:
    """
    Load a dir_ctx payload by branch_name and dir_path.

    Args:
        session (Any): Active SQLAlchemy session.
        branch_name (str): Branch identifier.
        dir_path (str): Repo-relative directory path.

    Returns:
        tuple[dict[str, Any], bool]: Payload and exists flag.

    Contract:
        - Returns an empty payload with exists=False when not found.
    """

    row = session.get(DirCtx, (branch_name, dir_path))
    if row is None:
        return {}, False
    return build_dir_ctx_payload(session, row), True


def load_dir_ctx_snapshot_by_ctx_path(
    session: Any, branch_name: str, ctx_path: str
) -> tuple[dict[str, Any], bool]:
    """
    Load a dir_ctx payload by ctx_path.

    Args:
        session (Any): Active SQLAlchemy session.
        branch_name (str): Branch identifier.
        ctx_path (str): Repo-relative ctx path.

    Returns:
        tuple[dict[str, Any], bool]: Payload and exists flag.

    Contract:
        - Returns an empty payload with exists=False when not found.
    """

    row = (
        session.query(DirCtx)
        .filter_by(branch_name=branch_name, ctx_path=ctx_path)
        .first()
    )
    if row is None:
        return {}, False
    return build_dir_ctx_payload(session, row), True


def list_dir_ctx_payloads(session: Any, branch_name: str) -> list[dict[str, Any]]:
    """
    List dir_ctx payloads for a branch.

    Args:
        session (Any): Active SQLAlchemy session.
        branch_name (str): Branch identifier.

    Returns:
        list[dict[str, Any]]: dir_ctx payloads for the branch.

    Contract:
        - Returns an empty list when no rows exist.
    """

    rows = session.query(DirCtx).filter_by(branch_name=branch_name).all()
    return [build_dir_ctx_payload(session, row) for row in rows]


def _persist_items(session: Any, now: str, actor_id: str, rows: Iterable[Any]) -> None:
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


def persist_dir_ctx_payload(
    session: Any,
    branch_name: str,
    payload: dict[str, Any],
    actor_id: str,
) -> str:
    """
    Persist a dir_ctx payload to SQLite.

    Args:
        session (Any): Active SQLAlchemy session.
        branch_name (str): Branch identifier.
        payload (dict[str, Any]): dir_ctx payload.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        str: dir_path for the persisted record.

    Raises:
        ValueError: If payload validation fails.

    Contract:
        - Updates updated_at and updated_by on every write.
        - Replaces child rows with the provided payload state.
        - Returns the canonical dir_path for subsequent lookups.
    """

    if payload.get("kind") != "dir_ctx":
        raise ValueError("dir_ctx payload kind must be 'dir_ctx'.")

    identity = _require_mapping(payload, "identity")
    agent = _require_mapping(payload, "agent")
    computed = _require_mapping(payload, "computed")

    dir_path = _require_string(identity, "dir_path")
    ctx_path = _require_string(identity, "ctx_path")
    name = _require_string(identity, "name")

    schema_version = payload.get("schema_version")
    if not isinstance(schema_version, int) or schema_version < 1:
        raise ValueError("dir_ctx.schema_version must be an integer >= 1.")

    freshness_state = _require_string(computed, "freshness_state")
    staleness_reasons = _string_list(computed, "staleness_reasons")
    checksums = _require_mapping(computed, "checksums")
    last_scan = (
        computed.get("last_scan") if isinstance(computed.get("last_scan"), dict) else {}
    )
    review = computed.get("review") if isinstance(computed.get("review"), dict) else {}

    subtree_hash = _optional_string(checksums, "subtree_hash_sha256")
    ctx_semantic_hash = _optional_string(checksums, "ctx_semantic_hash_sha256")
    template_version = _optional_string(checksums, "template_version")
    analyzer_version = _optional_string(checksums, "analyzer_version")

    last_scan_id = _optional_string(last_scan, "scan_id")
    last_scanned_at = _optional_string(last_scan, "scanned_at")
    review_every = _optional_int(review, "review_every_n_scans")
    scan_counter = _optional_int(review, "scan_counter")
    last_review_scan_id = _optional_string(review, "last_review_scan_id")

    summary = _require_mapping(agent, "summary")
    architecture = _require_mapping(agent, "architecture")
    inventory = _require_mapping(agent, "inventory")
    integration = _require_mapping(agent, "integration")
    testing = _require_mapping(agent, "testing")
    dependency_rules = _require_mapping(architecture, "dependency_rules")

    now = utc_now_iso()
    existing = session.get(DirCtx, (branch_name, dir_path))
    created_at = existing.created_at if existing else now
    created_by = existing.created_by if existing else actor_id

    core = DirCtx(
        branch_name=branch_name,
        dir_path=dir_path,
        ctx_path=ctx_path,
        name=name,
        schema_version=schema_version,
        freshness_state=freshness_state,
        last_scan_id=last_scan_id,
        last_scanned_at=last_scanned_at,
        review_every_n_scans=review_every,
        scan_counter=scan_counter,
        last_review_scan_id=last_review_scan_id,
        subtree_hash_sha256=subtree_hash,
        ctx_semantic_hash_sha256=ctx_semantic_hash,
        template_version=template_version,
        analyzer_version=analyzer_version,
        created_at=created_at,
        created_by=created_by,
        updated_at=now,
        updated_by=actor_id,
    )
    session.merge(core)

    session.query(DirCtxStalenessReason).filter_by(
        branch_name=branch_name, dir_path=dir_path
    ).delete()
    session.query(DirCtxAgentSummary).filter_by(
        branch_name=branch_name, dir_path=dir_path
    ).delete()
    session.query(DirCtxAgentArchitectureItem).filter_by(
        branch_name=branch_name, dir_path=dir_path
    ).delete()
    session.query(DirCtxAgentDependencyRules).filter_by(
        branch_name=branch_name, dir_path=dir_path
    ).delete()
    session.query(DirCtxAgentDependencyRuleItem).filter_by(
        branch_name=branch_name, dir_path=dir_path
    ).delete()
    session.query(DirCtxAgentIntegrationItem).filter_by(
        branch_name=branch_name, dir_path=dir_path
    ).delete()
    session.query(DirCtxAgentTestingItem).filter_by(
        branch_name=branch_name, dir_path=dir_path
    ).delete()
    session.query(DirCtxAgentChangeSafetyItem).filter_by(
        branch_name=branch_name, dir_path=dir_path
    ).delete()
    session.query(DirCtxAgentInventoryFile).filter_by(
        branch_name=branch_name, dir_path=dir_path
    ).delete()
    session.query(DirCtxAgentInventorySubdir).filter_by(
        branch_name=branch_name, dir_path=dir_path
    ).delete()

    session.query(DirCtxAgentKeyFlowItem).filter_by(
        branch_name=branch_name,
        dir_path=dir_path,
    ).delete()
    session.query(DirCtxAgentKeyFlow).filter_by(
        branch_name=branch_name,
        dir_path=dir_path,
    ).delete()

    rows: list[Any] = []
    rows.extend(
        DirCtxStalenessReason(
            branch_name=branch_name,
            dir_path=dir_path,
            position=idx,
            reason=reason,
        )
        for idx, reason in enumerate(staleness_reasons, start=1)
    )

    rows.append(
        DirCtxAgentSummary(
            branch_name=branch_name,
            dir_path=dir_path,
            one_liner=_require_string(summary, "one_liner"),
            detail=_require_string(summary, "detail"),
        )
    )

    rows.append(
        DirCtxAgentDependencyRules(
            branch_name=branch_name,
            dir_path=dir_path,
            notes=_optional_string(dependency_rules, "notes"),
        )
    )

    architecture_items = {
        "responsibilities": _string_list(architecture, "responsibilities"),
        "non_goals": _string_list(architecture, "non_goals"),
        "core_concepts": _string_list(architecture, "core_concepts"),
    }
    for item_type, values in architecture_items.items():
        rows.extend(
            DirCtxAgentArchitectureItem(
                branch_name=branch_name,
                dir_path=dir_path,
                item_type=item_type,
                position=idx,
                value=value,
            )
            for idx, value in enumerate(values, start=1)
        )

    dependency_items = {
        "allowed_inbound": _string_list(dependency_rules, "allowed_inbound"),
        "allowed_outbound": _string_list(dependency_rules, "allowed_outbound"),
        "forbidden_dependencies": _string_list(
            dependency_rules, "forbidden_dependencies"
        ),
    }
    for item_type, values in dependency_items.items():
        rows.extend(
            DirCtxAgentDependencyRuleItem(
                branch_name=branch_name,
                dir_path=dir_path,
                item_type=item_type,
                position=idx,
                value=value,
            )
            for idx, value in enumerate(values, start=1)
        )

    key_flows = architecture.get("key_flows", [])
    if key_flows is None:
        key_flows = []
    if not isinstance(key_flows, list):
        raise ValueError("dir_ctx.architecture.key_flows must be a list.")

    for idx, flow in enumerate(key_flows, start=1):
        if not isinstance(flow, dict):
            raise ValueError("dir_ctx.architecture.key_flows entries must be objects.")
        flow_name = _require_string(flow, "name")
        rows.append(
            DirCtxAgentKeyFlow(
                branch_name=branch_name,
                dir_path=dir_path,
                flow_name=flow_name,
                position=idx,
            )
        )
        rows.extend(
            DirCtxAgentKeyFlowItem(
                branch_name=branch_name,
                dir_path=dir_path,
                flow_name=flow_name,
                item_type="steps",
                position=step_idx,
                value=value,
            )
            for step_idx, value in enumerate(_string_list(flow, "steps"), start=1)
        )
        rows.extend(
            DirCtxAgentKeyFlowItem(
                branch_name=branch_name,
                dir_path=dir_path,
                flow_name=flow_name,
                item_type="invariants",
                position=inv_idx,
                value=value,
            )
            for inv_idx, value in enumerate(_string_list(flow, "invariants"), start=1)
        )

    inventory_files = inventory.get("files", [])
    if inventory_files is None:
        inventory_files = []
    if not isinstance(inventory_files, list):
        raise ValueError("dir_ctx.inventory.files must be a list.")
    for idx, item in enumerate(inventory_files, start=1):
        if not isinstance(item, dict):
            raise ValueError("dir_ctx.inventory.files entries must be objects.")
        rows.append(
            DirCtxAgentInventoryFile(
                branch_name=branch_name,
                dir_path=dir_path,
                position=idx,
                file_path=_require_string(item, "path"),
                ctx_path=_optional_string(item, "ctx"),
                role=_optional_string(item, "role"),
            )
        )

    inventory_subdirs = inventory.get("subdirs", [])
    if inventory_subdirs is None:
        inventory_subdirs = []
    if not isinstance(inventory_subdirs, list):
        raise ValueError("dir_ctx.inventory.subdirs must be a list.")
    for idx, item in enumerate(inventory_subdirs, start=1):
        if not isinstance(item, dict):
            raise ValueError("dir_ctx.inventory.subdirs entries must be objects.")
        rows.append(
            DirCtxAgentInventorySubdir(
                branch_name=branch_name,
                dir_path=dir_path,
                position=idx,
                subdir_path=_require_string(item, "path"),
                ctx_path=_optional_string(item, "ctx"),
                role=_optional_string(item, "role"),
            )
        )

    integration_items = {
        "entrypoints": _string_list(integration, "entrypoints"),
        "used_by": _string_list(integration, "used_by"),
        "uses": _string_list(integration, "uses"),
        "runtime_notes": _string_list(integration, "runtime_notes"),
    }
    for item_type, values in integration_items.items():
        rows.extend(
            DirCtxAgentIntegrationItem(
                branch_name=branch_name,
                dir_path=dir_path,
                item_type=item_type,
                position=idx,
                value=value,
            )
            for idx, value in enumerate(values, start=1)
        )

    testing_items = {
        "commands": _string_list(testing, "commands"),
        "required_when_changed": _string_list(testing, "required_when_changed"),
        "recommended_when_changed": _string_list(testing, "recommended_when_changed"),
    }
    for item_type, values in testing_items.items():
        rows.extend(
            DirCtxAgentTestingItem(
                branch_name=branch_name,
                dir_path=dir_path,
                item_type=item_type,
                position=idx,
                value=value,
            )
            for idx, value in enumerate(values, start=1)
        )

    change_safety = agent.get("change_safety")
    if isinstance(change_safety, dict):
        change_items = {
            "review_triggers": _string_list(change_safety, "review_triggers"),
            "risky_changes": _string_list(change_safety, "risky_changes"),
            "safe_changes": _string_list(change_safety, "safe_changes"),
        }
        for item_type, values in change_items.items():
            rows.extend(
                DirCtxAgentChangeSafetyItem(
                    branch_name=branch_name,
                    dir_path=dir_path,
                    item_type=item_type,
                    position=idx,
                    value=value,
                )
                for idx, value in enumerate(values, start=1)
            )

    _persist_items(session, now, actor_id, rows)
    return dir_path


def delete_dir_ctx_by_branch(session: Any, branch_name: str) -> bool:
    """
    Delete all dir_ctx records for a branch.

    Args:
        session (Any): Active SQLAlchemy session.
        branch_name (str): Branch identifier.

    Returns:
        bool: True if any dir_ctx rows existed before deletion.

    Contract:
        - Deletes child rows before core dir_ctx rows.
        - Returns False when no rows were present.
    """

    has_rows = (
        session.query(DirCtx.branch_name).filter_by(branch_name=branch_name).first()
        is not None
    )
    session.query(DirCtxStalenessReason).filter_by(branch_name=branch_name).delete()
    session.query(DirCtxAgentSummary).filter_by(branch_name=branch_name).delete()
    session.query(DirCtxAgentArchitectureItem).filter_by(branch_name=branch_name).delete()
    session.query(DirCtxAgentDependencyRules).filter_by(branch_name=branch_name).delete()
    session.query(DirCtxAgentDependencyRuleItem).filter_by(branch_name=branch_name).delete()
    session.query(DirCtxAgentIntegrationItem).filter_by(branch_name=branch_name).delete()
    session.query(DirCtxAgentTestingItem).filter_by(branch_name=branch_name).delete()
    session.query(DirCtxAgentChangeSafetyItem).filter_by(branch_name=branch_name).delete()
    session.query(DirCtxAgentInventoryFile).filter_by(branch_name=branch_name).delete()
    session.query(DirCtxAgentInventorySubdir).filter_by(branch_name=branch_name).delete()

    session.query(DirCtxAgentKeyFlowItem).filter_by(branch_name=branch_name).delete()
    session.query(DirCtxAgentKeyFlow).filter_by(branch_name=branch_name).delete()
    session.query(DirCtx).filter_by(branch_name=branch_name).delete()
    return has_rows
