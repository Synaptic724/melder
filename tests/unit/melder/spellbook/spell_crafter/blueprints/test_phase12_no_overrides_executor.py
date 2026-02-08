from types import SimpleNamespace

import pytest

from melder.spellbook.existence.existence import Existence
import melder.spellbook.spell_crafter.blueprints.phase12_no_overrides_executor as phase12_module


def _make_step(spell_id: str) -> SimpleNamespace:
    spell = SimpleNamespace(
        spell_index=SimpleNamespace(current=spell_id),
    )
    return SimpleNamespace(
        instance_key=(spell_id, None),
        spell=spell,
        existence=Existence.many,
        must_register=False,
    )


def test_compile_phase12_no_overrides_executor_raises_on_transient_compile_error(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Ensure transient source compile failures are hard-fail errors.

    Contract:
        - Invalid generated transient source raises RuntimeError.
    """
    step = _make_step("root")
    codegen_ir = {
        "steps": (step,),
        "root_spell_id": "root",
        "transient_plan": (1, 0),
    }
    monkeypatch.setattr(
        phase12_module,
        "_build_phase12_executor_source",
        lambda transient_plan: "def _phase12_executor(:\n    pass",
    )
    monkeypatch.setattr(
        phase12_module,
        "_build_executor_namespace",
        lambda transient_plan, steps: {},
    )

    with pytest.raises(RuntimeError, match="code generation failed"):
        phase12_module.compile_phase12_no_overrides_executor(codegen_ir=codegen_ir)


def test_compile_phase12_no_overrides_executor_raises_when_callable_missing(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Ensure generated source must define the transient executor callable.

    Contract:
        - Missing `_phase12_executor` symbol raises RuntimeError.
    """
    step = _make_step("root")
    codegen_ir = {
        "steps": (step,),
        "root_spell_id": "root",
        "transient_plan": (1, 0),
    }
    monkeypatch.setattr(
        phase12_module,
        "_build_phase12_executor_source",
        lambda transient_plan: "x = 1",
    )
    monkeypatch.setattr(
        phase12_module,
        "_build_executor_namespace",
        lambda transient_plan, steps: {},
    )

    with pytest.raises(RuntimeError, match="did not define a callable _phase12_executor"):
        phase12_module.compile_phase12_no_overrides_executor(codegen_ir=codegen_ir)


def test_compile_phase12_no_overrides_executor_falls_back_when_source_unavailable(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Ensure non-generated transient paths use the step-plan fallback.

    Contract:
        - When transient source generation returns None, step-plan executor is returned.
    """
    step = _make_step("root")
    codegen_ir = {
        "steps": (step,),
        "root_spell_id": "root",
        "transient_plan": (1, 0),
    }
    monkeypatch.setattr(
        phase12_module,
        "_build_phase12_executor_source",
        lambda transient_plan: None,
    )

    executor = phase12_module.compile_phase12_no_overrides_executor(codegen_ir=codegen_ir)

    assert callable(executor)


def test_compile_phase12_no_overrides_executor_supports_steps_rows_schema() -> None:
    """
    Ensure schema-only step rows can be hydrated into executable plan steps.

    Contract:
        - `steps_rows` plus `spell_lookup` compiles into a callable executor.
    """
    spell = SimpleNamespace(
        spell_index=SimpleNamespace(current="root"),
        spell_name="root",
    )
    codegen_ir = {
        "steps_rows": (
            {
                "instance_key": ("root", None),
                "spell_id": "root",
                "existence": "many",
                "creations_target_kind": 1,
                "dependency_resolution_order": (),
                "uses_positional_override": False,
                "contract_positional_override": None,
                "has_contract_payload": False,
                "contract_payload_items": (),
                "use_spell_lock_hint": False,
                "must_register": False,
            },
        ),
        "root_spell_id": "root",
        "transient_plan": None,
    }

    executor = phase12_module.compile_phase12_no_overrides_executor(
        codegen_ir=codegen_ir,
        spell_lookup={"root": spell},
    )

    assert callable(executor)


def test_compile_phase12_no_overrides_executor_requires_spell_lookup_for_steps_rows() -> None:
    """
    Ensure schema-only step rows fail fast when spell lookup is missing.

    Contract:
        - Missing spell_lookup with `steps_rows` raises RuntimeError.
    """
    codegen_ir = {
        "steps_rows": (
            {
                "instance_key": ("root", None),
                "spell_id": "root",
                "existence": "many",
                "creations_target_kind": 1,
                "dependency_resolution_order": (),
                "uses_positional_override": False,
                "contract_positional_override": None,
                "has_contract_payload": False,
                "contract_payload_items": (),
                "use_spell_lock_hint": False,
                "must_register": False,
            },
        ),
        "root_spell_id": "root",
        "transient_plan": None,
    }

    with pytest.raises(RuntimeError, match="require spell_lookup"):
        phase12_module.compile_phase12_no_overrides_executor(codegen_ir=codegen_ir)
