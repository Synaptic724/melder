"""
Shared payload helpers for self_context query scripts.

Purpose
- Provide ORM-backed helpers for loading and persisting self_context payloads.
- Keep validation and serialization logic centralized for query scripts.

Contract
- Callers must supply a live SQLAlchemy session.
- Payloads follow schemas/self_context.schema.json.
- Helpers raise ValueError for invalid payloads or schema violations.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from context_compass.system.ai_restricted._shared.timeutils import utc_now_iso
from context_compass.system.ai_restricted.database_management.user_orm_models import (
    SelfContext,
    SelfContextNonNegotiable,
    SelfContextOpenQuestion,
    SelfContextOpinionItem,
    SelfContextSkillReceipt,
    SelfContextStyleModelItem,
)
from sqlalchemy.orm import Session


@dataclass(frozen=True)
class SelfContextParts:
    """
    Parsed components of a self_context payload.

    Attributes:
        schema_version (int): Schema version for the payload.
        created_at (str): ISO-8601 creation timestamp.
        updated_at (str): ISO-8601 update timestamp.
        repo_purpose (str): Repository purpose summary.
        non_negotiables (list[str]): Ordered non-negotiable items.
        style_model (dict[str, Any]): Style model values.
        skill_receipts (list[dict]): Ordered skill receipt objects.
        open_questions (list[dict]): Ordered open question objects.
        opinions (dict[str, list[str]]): Opinion lists keyed by opinion category.

    Contract:
        - Values are validated and normalized from the payload.
        - Lists preserve order from the payload.
    """

    schema_version: int
    created_at: str
    updated_at: str
    repo_purpose: str
    non_negotiables: list[str]
    style_model: dict[str, Any]
    skill_receipts: list[dict]
    open_questions: list[dict]
    opinions: dict[str, list[str]]


def default_self_context_payload(agent_id: str, now: str) -> dict[str, Any]:
    """
    Build a default self_context payload.

    Args:
        agent_id (str): Agent identifier.
        now (str): Timestamp for created_at/updated_at fields.

    Returns:
        dict[str, Any]: Default self_context payload.
    """

    return {
        "schema_version": 1,
        "agent_id": agent_id,
        "created_at": now,
        "updated_at": now,
        "understanding": {
            "repo_purpose": "TODO: describe repo purpose",
            "non_negotiables": [],
            "style_model": {},
        },
        "skill_receipts": [],
        "open_questions": [],
        "opinions": {
            "what_is_working": [],
            "what_is_confusing": [],
            "suggested_skill_improvements": [],
        },
    }


def _require_mapping(payload: dict[str, Any], key: str) -> dict[str, Any]:
    """
    Require a mapping field in a payload.

    Args:
        payload (dict[str, Any]): Payload to inspect.
        key (str): Mapping key to extract.

    Returns:
        dict[str, Any]: Mapping value.

    Raises:
        ValueError: If the mapping is missing or invalid.
    """

    value = payload.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"self_context.{key} must be a JSON object.")
    return value


def _require_string(payload: dict[str, Any], key: str) -> str:
    """
    Require a non-empty string field.

    Args:
        payload (dict[str, Any]): Payload to inspect.
        key (str): Field name to extract.

    Returns:
        str: Field value.

    Raises:
        ValueError: If the field is missing or invalid.
    """

    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"self_context.{key} must be a non-empty string.")
    return value


def _require_int(payload: dict[str, Any], key: str) -> int:
    """
    Require an integer field.

    Args:
        payload (dict[str, Any]): Payload to inspect.
        key (str): Field name to extract.

    Returns:
        int: Field value.

    Raises:
        ValueError: If the field is missing or invalid.
    """

    value = payload.get(key)
    if not isinstance(value, int):
        raise ValueError(f"self_context.{key} must be an integer.")
    return value


def _string_list(payload: dict[str, Any], key: str) -> list[str]:
    """
    Return a list of strings from a payload field.

    Args:
        payload (dict[str, Any]): Payload to inspect.
        key (str): Field name to extract.

    Returns:
        list[str]: List of strings.

    Raises:
        ValueError: If the field is missing or invalid.
    """

    value = payload.get(key)
    if not isinstance(value, list):
        raise ValueError(f"self_context.{key} must be a list.")
    results: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError(f"self_context.{key} items must be strings.")
        results.append(item)
    return results


def _style_model_value(
    value: Any,
) -> tuple[str, str | None, float | None, bool | None, str | None]:
    """
    Normalize a style_model value into typed storage columns.

    Args:
        value (Any): Style model value.

    Returns:
        tuple[str, str | None, float | None, bool | None, str | None]:
            Value type plus text/number/bool/json column values.

    Raises:
        ValueError: If the value cannot be serialized.
    """

    if value is None:
        return ("null", None, None, None, None)
    if isinstance(value, bool):
        return ("boolean", None, None, value, None)
    if isinstance(value, int):
        return ("number", None, float(value), None, None)
    if isinstance(value, float):
        return ("number", None, value, None, None)
    if isinstance(value, str):
        return ("text", value, None, None, None)
    try:
        return ("json", None, None, None, json.dumps(value, separators=(",", ":")))
    except (TypeError, ValueError) as exc:
        raise ValueError("self_context.style_model values must be JSON-serializable.") from exc


def _materialize_style_model(rows: list[SelfContextStyleModelItem]) -> dict[str, Any]:
    """
    Build a style_model mapping from ORM rows.

    Args:
        rows (list[SelfContextStyleModelItem]): Style model rows to materialize.

    Returns:
        dict[str, Any]: Style model mapping.

    Raises:
        ValueError: If the stored rows contain unsupported value types.
    """

    result: dict[str, Any] = {}
    for row in rows:
        if row.value_type == "text":
            result[row.style_key] = row.value_text
            continue
        if row.value_type == "number":
            result[row.style_key] = row.value_number
            continue
        if row.value_type == "boolean":
            if row.value_bool is None:
                raise ValueError("self_context.style_model boolean values cannot be null.")
            result[row.style_key] = row.value_bool
            continue
        if row.value_type == "json":
            if row.value_json is None:
                raise ValueError("self_context.style_model json values cannot be null.")
            result[row.style_key] = json.loads(row.value_json)
            continue
        if row.value_type == "null":
            result[row.style_key] = None
            continue
        raise ValueError(f"self_context.style_model has unsupported value_type: {row.value_type}")
    return result


def _parse_payload(agent_id: str, payload: dict[str, Any]) -> SelfContextParts:
    """
    Validate and parse a self_context payload into components.

    Args:
        agent_id (str): Agent identifier the payload must match.
        payload (dict[str, Any]): Self_context payload to parse.

    Returns:
        SelfContextParts: Parsed payload components.

    Raises:
        ValueError: If the payload violates schema constraints.
    """

    if not isinstance(payload, dict):
        raise ValueError("Self-context payload must be a JSON object.")
    if payload.get("agent_id") != agent_id:
        raise ValueError("self_context.agent_id must match the requested agent_id.")
    schema_version = payload.get("schema_version")
    if not isinstance(schema_version, int) or schema_version < 1:
        raise ValueError("self_context.schema_version must be an integer >= 1.")
    created_at = _require_string(payload, "created_at")
    updated_at = _require_string(payload, "updated_at")
    understanding = _require_mapping(payload, "understanding")
    repo_purpose = _require_string(understanding, "repo_purpose")
    non_negotiables = _string_list(understanding, "non_negotiables")
    style_model = understanding.get("style_model")
    if not isinstance(style_model, dict):
        raise ValueError("self_context.understanding.style_model must be a JSON object.")
    skill_receipts = payload.get("skill_receipts")
    if not isinstance(skill_receipts, list):
        raise ValueError("self_context.skill_receipts must be a list.")
    open_questions = payload.get("open_questions")
    if not isinstance(open_questions, list):
        raise ValueError("self_context.open_questions must be a list.")
    opinions = payload.get("opinions")
    if not isinstance(opinions, dict):
        raise ValueError("self_context.opinions must be a JSON object.")
    return SelfContextParts(
        schema_version=schema_version,
        created_at=created_at,
        updated_at=updated_at,
        repo_purpose=repo_purpose,
        non_negotiables=non_negotiables,
        style_model=style_model,
        skill_receipts=skill_receipts,
        open_questions=open_questions,
        opinions=opinions,
    )


def load_self_context_snapshot(
    session: Session,
    agent_id: str,
) -> tuple[dict[str, Any], bool]:
    """
    Load a self_context payload and existence flag from SQLite.

    Args:
        session (Session): Active SQLAlchemy session.
        agent_id (str): Agent identifier.

    Returns:
        tuple[dict[str, Any], bool]: Payload dictionary and existence flag.

    Raises:
        ValueError: If stored rows contain invalid data.
    """

    now = utc_now_iso()
    core = session.get(SelfContext, agent_id)
    if core is None:
        return default_self_context_payload(agent_id, now), False

    non_negotiables = (
        session.query(SelfContextNonNegotiable)
        .filter_by(agent_id=agent_id)
        .order_by(SelfContextNonNegotiable.position)
        .all()
    )
    style_rows = (
        session.query(SelfContextStyleModelItem)
        .filter_by(agent_id=agent_id)
        .order_by(SelfContextStyleModelItem.style_key)
        .all()
    )
    receipts = (
        session.query(SelfContextSkillReceipt)
        .filter_by(agent_id=agent_id)
        .order_by(SelfContextSkillReceipt.position)
        .all()
    )
    open_questions = (
        session.query(SelfContextOpenQuestion)
        .filter_by(agent_id=agent_id)
        .order_by(SelfContextOpenQuestion.position)
        .all()
    )
    opinion_rows = (
        session.query(SelfContextOpinionItem)
        .filter_by(agent_id=agent_id)
        .order_by(SelfContextOpinionItem.opinion_key, SelfContextOpinionItem.position)
        .all()
    )

    opinions: dict[str, list[str]] = {}
    for row in opinion_rows:
        opinions.setdefault(row.opinion_key, []).append(row.value)

    payload = {
        "schema_version": core.schema_version,
        "agent_id": core.agent_id,
        "created_at": core.created_at or now,
        "updated_at": core.updated_at or now,
        "understanding": {
            "repo_purpose": core.understanding_repo_purpose,
            "non_negotiables": [row.value for row in non_negotiables],
            "style_model": _materialize_style_model(style_rows),
        },
        "skill_receipts": [
            {
                "skill_id": row.skill_id,
                "version": row.version,
                "read_at": row.read_at,
                "agent_summary": row.agent_summary,
            }
            for row in receipts
        ],
        "open_questions": [
            {
                "topic": row.topic,
                "question": row.question,
                "blocking": row.blocking,
            }
            for row in open_questions
        ],
        "opinions": opinions,
    }
    return payload, True


def _delete_children(session: Session, agent_id: str) -> None:
    """
    Delete child rows for a self_context record.

    Args:
        session (Session): Active SQLAlchemy session.
        agent_id (str): Agent identifier.

    Returns:
        None: Child rows are removed in-place.
    """

    session.query(SelfContextNonNegotiable).filter_by(agent_id=agent_id).delete()
    session.query(SelfContextStyleModelItem).filter_by(agent_id=agent_id).delete()
    session.query(SelfContextSkillReceipt).filter_by(agent_id=agent_id).delete()
    session.query(SelfContextOpenQuestion).filter_by(agent_id=agent_id).delete()
    session.query(SelfContextOpinionItem).filter_by(agent_id=agent_id).delete()


def _insert_non_negotiables(
    session: Session,
    agent_id: str,
    values: list[str],
    *,
    created_at: str,
    created_by: str,
    updated_at: str,
    updated_by: str,
) -> None:
    """
    Insert non-negotiable rows for self_context.

    Args:
        session (Session): Active SQLAlchemy session.
        agent_id (str): Agent identifier.
        values (list[str]): Ordered non-negotiable values.
        created_at (str): Creation timestamp to persist.
        created_by (str): Actor that created the record.
        updated_at (str): Update timestamp to persist.
        updated_by (str): Actor that updated the record.
    """

    for idx, value in enumerate(values, start=1):
        session.add(
            SelfContextNonNegotiable(
                agent_id=agent_id,
                position=idx,
                value=value,
                created_at=created_at,
                created_by=created_by,
                updated_at=updated_at,
                updated_by=updated_by,
            )
        )


def _insert_style_model_items(
    session: Session,
    agent_id: str,
    style_model: dict[str, Any],
    *,
    created_at: str,
    created_by: str,
    updated_at: str,
    updated_by: str,
) -> None:
    """
    Insert style model rows for self_context.

    Args:
        session (Session): Active SQLAlchemy session.
        agent_id (str): Agent identifier.
        style_model (dict[str, Any]): Style model mapping.
        created_at (str): Creation timestamp to persist.
        created_by (str): Actor that created the record.
        updated_at (str): Update timestamp to persist.
        updated_by (str): Actor that updated the record.
    """

    for key, value in style_model.items():
        value_type, value_text, value_number, value_bool, value_json = _style_model_value(value)
        session.add(
            SelfContextStyleModelItem(
                agent_id=agent_id,
                style_key=str(key),
                value_type=value_type,
                value_text=value_text,
                value_number=value_number,
                value_bool=value_bool,
                value_json=value_json,
                created_at=created_at,
                created_by=created_by,
                updated_at=updated_at,
                updated_by=updated_by,
            )
        )


def _insert_skill_receipts(
    session: Session,
    agent_id: str,
    receipts: list[dict],
    *,
    created_at: str,
    created_by: str,
    updated_at: str,
    updated_by: str,
) -> None:
    """
    Insert skill receipt rows for self_context.

    Args:
        session (Session): Active SQLAlchemy session.
        agent_id (str): Agent identifier.
        receipts (list[dict]): Skill receipt payloads.
        created_at (str): Creation timestamp to persist.
        created_by (str): Actor that created the record.
        updated_at (str): Update timestamp to persist.
        updated_by (str): Actor that updated the record.

    Raises:
        ValueError: If receipt entries are invalid.
    """

    for idx, item in enumerate(receipts, start=1):
        if not isinstance(item, dict):
            raise ValueError("self_context.skill_receipts entries must be objects.")
        session.add(
            SelfContextSkillReceipt(
                agent_id=agent_id,
                position=idx,
                skill_id=_require_string(item, "skill_id"),
                version=_require_int(item, "version"),
                read_at=_require_string(item, "read_at"),
                agent_summary=_require_string(item, "agent_summary"),
                created_at=created_at,
                created_by=created_by,
                updated_at=updated_at,
                updated_by=updated_by,
            )
        )


def _insert_open_questions(
    session: Session,
    agent_id: str,
    questions: list[dict],
    *,
    created_at: str,
    created_by: str,
    updated_at: str,
    updated_by: str,
) -> None:
    """
    Insert open question rows for self_context.

    Args:
        session (Session): Active SQLAlchemy session.
        agent_id (str): Agent identifier.
        questions (list[dict]): Open question payloads.
        created_at (str): Creation timestamp to persist.
        created_by (str): Actor that created the record.
        updated_at (str): Update timestamp to persist.
        updated_by (str): Actor that updated the record.

    Raises:
        ValueError: If open question entries are invalid.
    """

    for idx, item in enumerate(questions, start=1):
        if not isinstance(item, dict):
            raise ValueError("self_context.open_questions entries must be objects.")
        blocking = item.get("blocking")
        if not isinstance(blocking, bool):
            raise ValueError("self_context.open_questions.blocking must be a boolean.")
        session.add(
            SelfContextOpenQuestion(
                agent_id=agent_id,
                position=idx,
                topic=_require_string(item, "topic"),
                question=_require_string(item, "question"),
                blocking=blocking,
                created_at=created_at,
                created_by=created_by,
                updated_at=updated_at,
                updated_by=updated_by,
            )
        )


def _insert_opinions(
    session: Session,
    agent_id: str,
    opinions: dict[str, list[str]],
    *,
    created_at: str,
    created_by: str,
    updated_at: str,
    updated_by: str,
) -> None:
    """
    Insert opinion rows for self_context.

    Args:
        session (Session): Active SQLAlchemy session.
        agent_id (str): Agent identifier.
        opinions (dict[str, list[str]]): Opinion values keyed by opinion type.
        created_at (str): Creation timestamp to persist.
        created_by (str): Actor that created the record.
        updated_at (str): Update timestamp to persist.
        updated_by (str): Actor that updated the record.

    Raises:
        ValueError: If opinion entries are invalid.
    """

    for opinion_key, values in opinions.items():
        if not isinstance(values, list):
            raise ValueError("self_context.opinions values must be lists.")
        for idx, value in enumerate(values, start=1):
            if not isinstance(value, str):
                raise ValueError("self_context.opinions list values must be strings.")
            session.add(
                SelfContextOpinionItem(
                    agent_id=agent_id,
                    opinion_key=str(opinion_key),
                    position=idx,
                    value=value,
                    created_at=created_at,
                    created_by=created_by,
                    updated_at=updated_at,
                    updated_by=updated_by,
                )
            )


def persist_self_context_payload(
    session: Session,
    agent_id: str,
    payload: dict[str, Any],
    actor_id: str,
    *,
    exists: bool,
) -> None:
    """
    Persist a self_context payload using the active session.

    Args:
        session (Session): Active SQLAlchemy session.
        agent_id (str): Agent identifier.
        payload (dict[str, Any]): Self_context payload to persist.
        actor_id (str): Actor identifier for audit logging.
        exists (bool): Whether the record is expected to exist.

    Raises:
        ValueError: If payload validation fails.
    """

    _ = exists
    parts = _parse_payload(agent_id, payload)
    now = utc_now_iso()

    existing = session.get(SelfContext, agent_id)
    record_created_at = existing.created_at if existing else parts.created_at
    record_created_by = existing.created_by if existing else actor_id
    updated_at = parts.updated_at or now

    core = SelfContext(
        agent_id=agent_id,
        schema_version=parts.schema_version,
        understanding_repo_purpose=parts.repo_purpose,
        created_at=record_created_at,
        created_by=record_created_by,
        updated_at=updated_at,
        updated_by=actor_id,
    )
    session.merge(core)

    _delete_children(session, agent_id)
    _insert_non_negotiables(
        session,
        agent_id,
        parts.non_negotiables,
        created_at=record_created_at,
        created_by=record_created_by,
        updated_at=updated_at,
        updated_by=actor_id,
    )
    _insert_style_model_items(
        session,
        agent_id,
        parts.style_model,
        created_at=record_created_at,
        created_by=record_created_by,
        updated_at=updated_at,
        updated_by=actor_id,
    )
    _insert_skill_receipts(
        session,
        agent_id,
        parts.skill_receipts,
        created_at=record_created_at,
        created_by=record_created_by,
        updated_at=updated_at,
        updated_by=actor_id,
    )
    _insert_open_questions(
        session,
        agent_id,
        parts.open_questions,
        created_at=record_created_at,
        created_by=record_created_by,
        updated_at=updated_at,
        updated_by=actor_id,
    )
    _insert_opinions(
        session,
        agent_id,
        parts.opinions,
        created_at=record_created_at,
        created_by=record_created_by,
        updated_at=updated_at,
        updated_by=actor_id,
    )
