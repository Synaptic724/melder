"""Unit tests for current-surface compiler phase 13 compile caching behavior."""

from types import SimpleNamespace
from typing import Any

import pytest

import melder.aether.spellbook.spell_compiler.phases.compiler_phase_13 as compiler_phase_13_module
from melder.aether.spellbook.spell_compiler.phases.compiler_phase_13 import (
    CompilerPhase13,
)
from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)


def _make_spellbook_stub() -> Any:
    """Build a minimal spellbook stub for phase 13 tests."""
    return SimpleNamespace(
        _spell_id_pool={},
    )


def _make_spell_stub(spell_id: str) -> Any:
    """Build a minimal spell stub for phase 13 tests."""
    return SimpleNamespace(
        spell_id=spell_id,
        spell_index=SimpleNamespace(current=spell_id),
        resolution_complete=False,
    )


def test_compile_no_overrides_executor_from_payload_requires_signature_field() -> None:
    """Phase 13 payload compile should fail fast on missing required fields."""
    phase = CompilerPhase13()
    spellbook = _make_spellbook_stub()
    spell = _make_spell_stub("root")
    artifact = SpellCompilerArtifact("root")

    with pytest.raises(RuntimeError, match="missing required field 'signature'"):
        phase.compile_no_overrides_executor_from_payload(
            spellbook,
            spell,
            artifact,
            {
                "step_count": 1,
                "root_spell_id": "root",
                "steps_rows": [("row",)],
            },
        )


def test_compile_no_overrides_executor_from_payload_requires_steps_rows() -> None:
    """Phase 13 payload compile should require non-empty step rows."""
    phase = CompilerPhase13()
    spellbook = _make_spellbook_stub()
    spell = _make_spell_stub("root")
    artifact = SpellCompilerArtifact("root")

    with pytest.raises(RuntimeError, match="'steps_rows'"):
        phase.compile_no_overrides_executor_from_payload(
            spellbook,
            spell,
            artifact,
            {
                "signature": "sig",
                "step_count": 1,
                "root_spell_id": "root",
                "steps_rows": [],
            },
        )


def test_compile_no_overrides_executor_from_payload_reuses_cached_signature() -> None:
    """Phase 13 payload compile should reuse the cached executor when signatures match."""
    phase = CompilerPhase13()
    spellbook = _make_spellbook_stub()
    spell = _make_spell_stub("root")
    artifact = SpellCompilerArtifact("root")
    artifact._phase13_no_overrides_executor_signature = "sig"
    artifact._phase13_no_overrides_executor = object()

    phase.compile_no_overrides_executor_from_payload(
        spellbook,
        spell,
        artifact,
        {
            "signature": "sig",
            "step_count": 1,
            "root_spell_id": "root",
            "steps_rows": [("row",)],
        },
    )

    assert artifact._phase13_no_overrides_executor_signature == "sig"
    assert artifact._phase13_no_overrides_executor is not None
    assert spell.resolution_complete is True


def test_compile_no_overrides_executor_from_plan_reuses_cached_signature() -> None:
    """Phase 13 plan compile should reuse the cached executor when signatures match."""
    phase = CompilerPhase13()
    spell = _make_spell_stub("root")
    artifact = SpellCompilerArtifact("root")
    plan = SimpleNamespace(steps=[object()])
    artifact._phase11_no_overrides_plan_signature = "sig"
    artifact._phase13_no_overrides_executor_signature = "sig"
    artifact._phase13_no_overrides_executor = object()

    phase.compile_no_overrides_executor_from_plan(
        spell,
        artifact,
        plan,
    )

    assert artifact._phase13_no_overrides_executor_signature == "sig"
    assert artifact._phase13_no_overrides_executor is not None
    assert spell.resolution_complete is True


def test_compile_no_overrides_executor_from_plan_recompiles_on_signature_change(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Phase 13 plan compile should rebuild the executor when the cached signature changes."""
    phase = CompilerPhase13()
    spell = _make_spell_stub("root")
    artifact = SpellCompilerArtifact("root")
    plan = SimpleNamespace(steps=[object()])
    artifact._phase11_no_overrides_plan_signature = "sig-new"
    artifact._phase11_no_overrides_transient_schema = {"schema": 1}
    artifact._phase13_no_overrides_executor_signature = "sig-old"
    compiled_executor = object()
    compile_calls: list[tuple[Any, Any]] = []

    monkeypatch.setattr(
        compiler_phase_13_module,
        "compile_phase13_no_overrides_executor_from_plan",
        lambda plan, transient_schema: compile_calls.append((plan, transient_schema)) or compiled_executor,
    )

    phase.compile_no_overrides_executor_from_plan(
        spell,
        artifact,
        plan,
    )

    assert compile_calls == [(plan, {"schema": 1})]
    assert artifact._phase13_no_overrides_executor is compiled_executor
    assert artifact._phase13_no_overrides_executor_signature == "sig-new"
    assert spell.resolution_complete is True

