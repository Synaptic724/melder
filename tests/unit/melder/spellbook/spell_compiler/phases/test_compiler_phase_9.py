"""Unit tests for current-surface compiler phase 9 run-cache behavior."""

from types import SimpleNamespace
from typing import Any

import melder.aether.spellbook.spell_compiler.phases.compiler_phase_9 as compiler_phase_9_module
from melder.aether.spellbook.spell_compiler.phases.compiler_phase_9 import (
    CompilerPhase9,
)


def test_run_reuses_cached_plan_when_input_signature_unchanged(
        monkeypatch,
) -> None:
    """Phase 9 should skip rebuild when the cached signature and plan still match."""
    phase = CompilerPhase9()
    spell = SimpleNamespace(is_existing_creation=False)
    artifact = SimpleNamespace(
        check_cleaned=lambda: None,
        _occurrence_plan_phase8=object(),
        _phase8_occurrence_plan_input_signature="phase8-sig",
        _phase9_injection_plan_input_signature="phase8-sig",
        _injection_plan_phase9="cached-plan",
        _phase8_11_codegen_ir_dirty=False,
    )

    monkeypatch.setattr(
        compiler_phase_9_module,
        "InjectionPlanBuilder",
        lambda **kwargs: (_ for _ in ()).throw(
            AssertionError("builder should not run")
        ),
    )

    phase.run(spell, artifact)

    assert artifact._injection_plan_phase9 == "cached-plan"
    assert artifact._phase8_11_codegen_ir_dirty is False


def test_run_rebuilds_when_input_signature_changes(
        monkeypatch,
) -> None:
    """Phase 9 should rebuild and mark IR dirty when the input signature changes."""
    phase = CompilerPhase9()
    spell = SimpleNamespace(is_existing_creation=False)
    occurrence_plan = object()
    artifact = SimpleNamespace(
        check_cleaned=lambda: None,
        _occurrence_plan_phase8=occurrence_plan,
        _phase8_occurrence_plan_input_signature="phase8-sig-new",
        _phase9_injection_plan_input_signature="phase8-sig-old",
        _injection_plan_phase9="old-plan",
        _phase8_11_codegen_ir_dirty=False,
    )
    build_calls: list[str] = []
    built_plan = object()

    class _BuilderStub:
        def __init__(self, **kwargs: Any) -> None:
            build_calls.append("init")

        def build(self) -> object:
            build_calls.append("build")
            return built_plan

    monkeypatch.setattr(compiler_phase_9_module, "InjectionPlanBuilder", _BuilderStub)
    monkeypatch.setattr(
        CompilerPhase9,
        "_build_phase9_injection_shape_profile",
        staticmethod(lambda **kwargs: {}),
    )

    phase.run(spell, artifact)

    assert build_calls == ["init", "build"]
    assert artifact._injection_plan_phase9 is built_plan
    assert artifact._phase9_injection_plan_input_signature == "phase8-sig-new"
    assert artifact._phase8_11_codegen_ir_dirty is True


def test_run_marks_phase8_11_dirty_without_eager_capture(monkeypatch) -> None:
    """Phase 9 rebuild should mark the late IR dirty without eagerly exporting it."""
    phase = CompilerPhase9()
    spell = SimpleNamespace(is_existing_creation=False)
    artifact = SimpleNamespace(
        check_cleaned=lambda: None,
        _occurrence_plan_phase8=object(),
        _phase8_occurrence_plan_input_signature="phase8-sig-new",
        _phase9_injection_plan_input_signature="phase8-sig-old",
        _injection_plan_phase9=None,
        _phase8_11_codegen_ir_dirty=False,
    )

    class _BuilderStub:
        def __init__(self, **kwargs: Any) -> None:
            pass

        def build(self) -> object:
                return object()

    monkeypatch.setattr(compiler_phase_9_module, "InjectionPlanBuilder", _BuilderStub)
    monkeypatch.setattr(
        CompilerPhase9,
        "_build_phase9_injection_shape_profile",
        staticmethod(lambda **kwargs: {}),
    )

    phase.run(spell, artifact)

    assert artifact._phase8_11_codegen_ir_dirty is True
