"""Contract tests for Phase12 override specialization compiler."""

import threading
from types import SimpleNamespace
from typing import Any, Dict

import pytest

from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.blueprints.execution_plan import ExecutionPlanTargetKind
from melder.spellbook.spell_crafter.blueprints.phase12_overrides_executor import (
    compile_phase12_overrides_executor,
)


def _make_spell(spell_id: str) -> Any:
    """Build a minimal spell stub for schema-row override compiler tests."""
    return SimpleNamespace(
        spell_id=spell_id,
        spell_name=spell_id,
        spell_index=SimpleNamespace(current=spell_id),
        existence=Existence.many,
        is_existing_creation=False,
        is_class_spell=False,
        is_method_spell=False,
        is_lambda_spell=False,
        spell=f"value:{spell_id}",
        _owner_creations=None,
        _lock=threading.RLock(),
    )


def _make_plan_row(spell_id: str) -> Dict[str, Any]:
    """Build a minimal schema step row accepted by override compiler hydration."""
    return {
        "instance_key": (spell_id, None),
        "spell_id": spell_id,
        "existence": "many",
        "creations_target_kind": ExecutionPlanTargetKind.CALLER,
        "shared_instance": True,
        "dependency_resolution_order": (),
        "override_match_prefix": None,
        "override_match_prefix_len": 0,
        "uses_positional_override": False,
        "contract_positional_override": None,
        "has_contract_payload": False,
        "contract_payload_items": (),
        "use_spell_lock_hint": False,
        "must_register": False,
    }


def test_compile_phase12_overrides_executor_requires_spell_lookup_for_schema_rows() -> None:
    """Schema-row override compile fails fast when spell lookup is missing."""
    with pytest.raises(RuntimeError, match="require spell_lookup"):
        compile_phase12_overrides_executor(
            execution_plan=None,
            plan_rows=(_make_plan_row("root"),),
            root_spell_id="root",
            spell_lookup=None,
            override_targets_by_spell_id={},
            any_overrides_present=False,
            path_registry=None,
        )


def test_compile_phase12_overrides_executor_rejects_schema_rows_missing_required_field() -> None:
    """Schema-row override compile fails fast for missing required row fields."""
    row = _make_plan_row("root")
    row.pop("instance_key")
    with pytest.raises(RuntimeError, match="missing required field 'instance_key'"):
        compile_phase12_overrides_executor(
            execution_plan=None,
            plan_rows=(row,),
            root_spell_id="root",
            spell_lookup={"root": _make_spell("root")},
            override_targets_by_spell_id={},
            any_overrides_present=False,
            path_registry=None,
        )


def test_compile_phase12_overrides_executor_rejects_unknown_spell_id_in_schema_rows() -> None:
    """Schema-row override compile fails when spell lookup cannot resolve a row spell id."""
    with pytest.raises(RuntimeError, match="unknown spell_id 'root'"):
        compile_phase12_overrides_executor(
            execution_plan=None,
            plan_rows=(_make_plan_row("root"),),
            root_spell_id="root",
            spell_lookup={},
            override_targets_by_spell_id={},
            any_overrides_present=False,
            path_registry=None,
        )


def test_compile_phase12_overrides_executor_rejects_unknown_existence_name() -> None:
    """Schema-row override compile fails for unknown existence enum names."""
    row = _make_plan_row("root")
    row["existence"] = "not_an_existence"
    with pytest.raises(RuntimeError, match="unknown existence"):
        compile_phase12_overrides_executor(
            execution_plan=None,
            plan_rows=(row,),
            root_spell_id="root",
            spell_lookup={"root": _make_spell("root")},
            override_targets_by_spell_id={},
            any_overrides_present=False,
            path_registry=None,
        )


def test_compile_phase12_overrides_executor_supports_schema_rows_execution() -> None:
    """Schema-row override compile path emits a callable executor that executes."""
    spell = _make_spell("root")
    executor = compile_phase12_overrides_executor(
        execution_plan=None,
        plan_rows=(_make_plan_row("root"),),
        root_spell_id="root",
        spell_lookup={"root": spell},
        override_targets_by_spell_id={},
        any_overrides_present=False,
        path_registry=None,
    )

    context = SimpleNamespace(
        caller_creations=SimpleNamespace(_lock=threading.RLock()),
        caller_creations_lock_held=False,
    )
    result = executor(context, {}, None)

    assert result == "value:root"
