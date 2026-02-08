from types import SimpleNamespace

import pytest

from melder.spellbook.spell_crafter.blueprints.execution_plan import (
    ExecutionPlanCallMode,
)
import melder.spellbook.spell_crafter.blueprints.phase12_no_overrides_executor as phase12_module


def _make_spell(spell_id: str) -> SimpleNamespace:
    """Build a minimal callable spell stub for schema hydration tests."""
    return SimpleNamespace(
        spell_index=SimpleNamespace(current=spell_id),
        spell_name=spell_id,
        is_class_spell=True,
        is_method_spell=False,
        is_lambda_spell=False,
        spell=lambda: f"value:{spell_id}",
    )


def _make_step_row(spell_id: str) -> dict[str, object]:
    """Build a minimal schema row accepted by no-overrides step hydration."""
    return {
        "instance_key": (spell_id, None),
        "spell_id": spell_id,
        "existence": "many",
        "creations_target_kind": 1,
        "dependency_resolution_order": (),
        "uses_positional_override": False,
        "contract_positional_override": None,
        "has_contract_payload": False,
        "contract_payload_items": (),
        "use_spell_lock_hint": False,
        "must_register": False,
    }


def _make_transient_schema() -> dict[str, object]:
    """Build a one-step transient schema row set for codegen-path tests."""
    return {
        "step_count": 1,
        "root_step_index": 0,
        "call_modes": (ExecutionPlanCallMode.CALL0,),
        "dep1": (-1,),
        "dep2a": (-1,),
        "dep2b": (-1,),
        "dep3a": (-1,),
        "dep3b": (-1,),
        "dep3c": (-1,),
        "dep4a": (-1,),
        "dep4b": (-1,),
        "dep4c": (-1,),
        "dep4d": (-1,),
        "dep5a": (-1,),
        "dep5b": (-1,),
        "dep5c": (-1,),
        "dep5d": (-1,),
        "dep5e": (-1,),
        "dep6a": (-1,),
        "dep6b": (-1,),
        "dep6c": (-1,),
        "dep6d": (-1,),
        "dep6e": (-1,),
        "dep6f": (-1,),
        "dep7a": (-1,),
        "dep7b": (-1,),
        "dep7c": (-1,),
        "dep7d": (-1,),
        "dep7e": (-1,),
        "dep7f": (-1,),
        "dep7g": (-1,),
        "dep8a": (-1,),
        "dep8b": (-1,),
        "dep8c": (-1,),
        "dep8d": (-1,),
        "dep8e": (-1,),
        "dep8f": (-1,),
        "dep8g": (-1,),
        "dep8h": (-1,),
    }


def test_compile_phase12_no_overrides_executor_raises_on_transient_compile_error(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Ensure transient source compile failures are hard-fail errors.

    Contract:
        - Invalid generated transient source raises RuntimeError.
    """
    codegen_ir = {
        "steps_rows": (_make_step_row("root"),),
        "root_spell_id": "root",
        "transient_schema": _make_transient_schema(),
    }
    monkeypatch.setattr(
        phase12_module,
        "_build_phase12_executor_source",
        lambda transient_schema: "def _phase12_executor(:\n    pass",
    )
    monkeypatch.setattr(
        phase12_module,
        "_build_executor_namespace",
        lambda transient_schema, steps: {},
    )

    with pytest.raises(RuntimeError, match="code generation failed"):
        phase12_module.compile_phase12_no_overrides_executor(
            codegen_ir=codegen_ir,
            spell_lookup={"root": _make_spell("root")},
        )


def test_compile_phase12_no_overrides_executor_raises_when_callable_missing(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Ensure generated source must define the transient executor callable.

    Contract:
        - Missing `_phase12_executor` symbol raises RuntimeError.
    """
    codegen_ir = {
        "steps_rows": (_make_step_row("root"),),
        "root_spell_id": "root",
        "transient_schema": _make_transient_schema(),
    }
    monkeypatch.setattr(
        phase12_module,
        "_build_phase12_executor_source",
        lambda transient_schema: "x = 1",
    )
    monkeypatch.setattr(
        phase12_module,
        "_build_executor_namespace",
        lambda transient_schema, steps: {},
    )

    with pytest.raises(RuntimeError, match="did not define a callable _phase12_executor"):
        phase12_module.compile_phase12_no_overrides_executor(
            codegen_ir=codegen_ir,
            spell_lookup={"root": _make_spell("root")},
        )


def test_compile_phase12_no_overrides_executor_falls_back_when_source_unavailable(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Ensure non-generated transient paths use the step-plan fallback.

    Contract:
        - When transient source generation returns None, step-plan executor is returned.
    """
    codegen_ir = {
        "steps_rows": (_make_step_row("root"),),
        "root_spell_id": "root",
        "transient_schema": _make_transient_schema(),
    }
    monkeypatch.setattr(
        phase12_module,
        "_build_phase12_executor_source",
        lambda transient_schema: None,
    )

    executor = phase12_module.compile_phase12_no_overrides_executor(
        codegen_ir=codegen_ir,
        spell_lookup={"root": _make_spell("root")},
    )

    assert callable(executor)


def test_compile_phase12_no_overrides_executor_supports_steps_rows_schema() -> None:
    """
    Ensure schema-only step rows can be hydrated into executable plan steps.

    Contract:
        - `steps_rows` plus `spell_lookup` compiles into a callable executor.
    """
    codegen_ir = {
        "steps_rows": (_make_step_row("root"),),
        "root_spell_id": "root",
        "transient_schema": None,
    }

    executor = phase12_module.compile_phase12_no_overrides_executor(
        codegen_ir=codegen_ir,
        spell_lookup={"root": _make_spell("root")},
    )

    assert callable(executor)


def test_compile_phase12_no_overrides_executor_requires_spell_lookup_for_steps_rows() -> None:
    """
    Ensure schema-only step rows fail fast when spell lookup is missing.

    Contract:
        - Missing spell_lookup with `steps_rows` raises RuntimeError.
    """
    codegen_ir = {
        "steps_rows": (_make_step_row("root"),),
        "root_spell_id": "root",
        "transient_schema": None,
    }

    with pytest.raises(RuntimeError, match="require spell_lookup"):
        phase12_module.compile_phase12_no_overrides_executor(codegen_ir=codegen_ir)


def test_compile_phase12_no_overrides_executor_rejects_invalid_transient_schema() -> None:
    """Malformed transient schema fails fast before transient code generation."""
    codegen_ir = {
        "steps_rows": (_make_step_row("root"),),
        "root_spell_id": "root",
        "transient_schema": {"step_count": 1},
    }

    with pytest.raises(RuntimeError, match="missing required field 'root_step_index'"):
        phase12_module.compile_phase12_no_overrides_executor(
            codegen_ir=codegen_ir,
            spell_lookup={"root": _make_spell("root")},
        )
