"""Unit tests for current-surface compiler phase 4 validation behavior."""

from types import SimpleNamespace
from typing import Any, Optional

import pytest

import melder.aether.spellbook.spell_compiler.phases.compiler_phase_4 as compiler_phase_4_module
from melder.aether.spellbook.spell_compiler.phases.compiler_phase_4 import (
    CompilerPhase4,
)
from tests.unit.melder.spellbook.spell_compiler.support.compiler_test_support import (
    make_spell,
)


class _CancelStub:
    """Minimal cancellation stub for compiler phase tests."""

    def __init__(self, is_set: bool) -> None:
        """Store the initial cancellation posture."""
        self.is_set = is_set
        self.throw_calls = 0

    def throw_if_set(self) -> None:
        """Record cancellation and raise the expected runtime error."""
        self.throw_calls += 1
        raise RuntimeError("cancelled")


class _StateStub:
    """Track structural-validity changes published by Phase 4."""

    def __init__(self, validity: Any) -> None:
        """Initialize the state with one starting validity."""
        self.validity = validity
        self.clear_dirty_calls: list[float] = []
        self.set_validity_calls: list[dict[str, Any]] = []

    def clear_dirty(self, timestamp: float) -> None:
        """Record a dirty-clear operation."""
        self.clear_dirty_calls.append(timestamp)

    def set_validity(
            self,
            validity: Any,
            *,
            change_reason: Any = None,
            flags_to_add: Optional[list[Any]] = None,
            flags_to_remove: Optional[list[Any]] = None,
    ) -> None:
        """Record a validity transition."""
        self.validity = validity
        self.set_validity_calls.append(
            {
                "validity": validity,
                "change_reason": change_reason,
                "flags_to_add": flags_to_add,
                "flags_to_remove": flags_to_remove,
            }
        )


def _make_validator(result: Any, calls: list[dict[str, Any]]) -> Any:
    """Build a validator stub that returns one predetermined result."""
    return SimpleNamespace(
        validate_spell=lambda **kwargs: calls.append(kwargs) or result,
    )


def _make_states(state: _StateStub) -> Any:
    """Build a minimal spell-system-state registry stub."""
    return SimpleNamespace(
        get_by_index_id=lambda _index_id: state,
    )


def _prime_structural_artifacts(artifact: Any) -> None:
    """Populate the required Phase 1-3 artifact fields for Phase 4."""
    artifact._requirements = "requirements"
    artifact._symbolic_graph = "symbolic-graph"
    artifact._resolution_frame = "resolution-frame"


def test_run_raises_without_phase1_to_3_artifacts() -> None:
    """Phase 4 should fail fast when earlier structural artifacts are missing."""
    spell = make_spell("spell-1")
    artifact = spell._compiler_artifact

    phase = CompilerPhase4()

    with pytest.raises(RuntimeError, match="before Phases 1-3 have completed"):
        phase.run(
            spell,
            artifact,
            SimpleNamespace(validate_spell=lambda **_kwargs: None),
            None,
        )


def test_run_caches_clean_validation_and_marks_lineage_valid(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Phase 4 should cache a clean result and mark the lineage valid."""
    spell = make_spell("spell-1")
    artifact = spell._compiler_artifact
    _prime_structural_artifacts(artifact)
    state = _StateStub(compiler_phase_4_module.SpellValidity.unknown)
    validator_calls: list[dict[str, Any]] = []
    captured_calls: list[tuple[Any, Any]] = []
    result = SimpleNamespace(has_errors=False, issues=[])

    monkeypatch.setattr(
        compiler_phase_4_module.SharedCompilerExecutions,
        "capture_phase2_5_codegen_ir",
        lambda bound_spell, compiler_artifact: captured_calls.append(
            (bound_spell, compiler_artifact)
        ),
    )

    phase = CompilerPhase4()
    phase.run(
        spell,
        artifact,
        _make_validator(result, validator_calls),
        _make_states(state),
    )

    assert len(validator_calls) == 1
    assert artifact._validation_result_phase4 is result
    assert artifact._validated_phase4 is True
    assert artifact._is_broken is False
    assert len(state.clear_dirty_calls) == 1
    assert state.set_validity_calls[-1]["validity"] is compiler_phase_4_module.SpellValidity.valid
    assert state.set_validity_calls[-1]["change_reason"] is (
        compiler_phase_4_module.SpellStateChangeReason.validation_passed
    )
    assert state.set_validity_calls[-1]["flags_to_remove"] == [
        compiler_phase_4_module.SpellState.contract_unvalidated
    ]
    # Eager phase2_5 IR capture was removed from the phase body (write-only
    # snapshot, discarded same pass); guard against reintroduction.
    assert captured_calls == []


def test_run_marks_lineage_invalid_when_validation_has_errors() -> None:
    """Phase 4 should mark the lineage invalid when validation reports errors."""
    spell = make_spell("spell-1")
    artifact = spell._compiler_artifact
    _prime_structural_artifacts(artifact)
    state = _StateStub(compiler_phase_4_module.SpellValidity.unknown)
    result = SimpleNamespace(has_errors=True, issues=[])
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(
        compiler_phase_4_module.SharedCompilerExecutions,
        "capture_phase2_5_codegen_ir",
        lambda _spell, _artifact: None,
    )

    try:
        phase = CompilerPhase4()
        phase.run(
            spell,
            artifact,
            _make_validator(result, []),
            _make_states(state),
        )
    finally:
        monkeypatch.undo()

    assert artifact._is_broken is True
    assert state.set_validity_calls[-1]["validity"] is compiler_phase_4_module.SpellValidity.invalid
    assert state.set_validity_calls[-1]["change_reason"] is (
        compiler_phase_4_module.SpellStateChangeReason.validation_failed
    )


def test_run_marks_lineage_gated_when_contract_provider_is_missing() -> None:
    """Phase 4 should gate the lineage when a SpellContract provider is missing."""
    spell = make_spell("spell-1")
    artifact = spell._compiler_artifact
    _prime_structural_artifacts(artifact)
    state = _StateStub(compiler_phase_4_module.SpellValidity.unknown)
    issue = SimpleNamespace(code="SPELL_CONTRACT_MISSING_PROVIDER")
    result = SimpleNamespace(has_errors=False, issues=[issue])
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(
        compiler_phase_4_module.SharedCompilerExecutions,
        "capture_phase2_5_codegen_ir",
        lambda _spell, _artifact: None,
    )

    try:
        phase = CompilerPhase4()
        phase.run(
            spell,
            artifact,
            _make_validator(result, []),
            _make_states(state),
        )
    finally:
        monkeypatch.undo()

    assert state.set_validity_calls[-1]["validity"] is compiler_phase_4_module.SpellValidity.gated
    assert state.set_validity_calls[-1]["change_reason"] is (
        compiler_phase_4_module.SpellStateChangeReason.contract_unvalidated
    )
    assert state.set_validity_calls[-1]["flags_to_add"] == [
        compiler_phase_4_module.SpellState.contract_unvalidated
    ]


def test_run_skips_revalidation_when_cached_and_still_valid() -> None:
    """Phase 4 should short-circuit when the cached result is still valid."""
    spell = make_spell("spell-1")
    artifact = spell._compiler_artifact
    artifact._validated_phase4 = True
    artifact._validation_result_phase4 = "cached"
    state = _StateStub(compiler_phase_4_module.SpellValidity.valid)

    phase = CompilerPhase4()
    phase.run(
        spell,
        artifact,
        SimpleNamespace(
            validate_spell=lambda **_kwargs: (_ for _ in ()).throw(
                AssertionError("validator should not run")
            )
        ),
        _make_states(state),
    )

    assert artifact._validation_result_phase4 == "cached"


def test_run_honors_cancellation_before_validation() -> None:
    """Phase 4 should abort before validation when the cancel event is set."""
    spell = make_spell("spell-1")
    artifact = spell._compiler_artifact
    _prime_structural_artifacts(artifact)
    cancel_event = _CancelStub(is_set=True)
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(
        compiler_phase_4_module.SharedCompilerExecutions,
        "capture_phase2_5_codegen_ir",
        lambda _spell, _artifact: None,
    )

    try:
        phase = CompilerPhase4()

        with pytest.raises(RuntimeError, match="cancelled"):
            phase.run(
                spell,
                artifact,
                SimpleNamespace(
                    validate_spell=lambda **_kwargs: (_ for _ in ()).throw(
                        AssertionError("validator should not run")
                    )
                ),
                None,
                cancel_event=cancel_event,
            )
    finally:
        monkeypatch.undo()

    assert cancel_event.throw_calls == 1
