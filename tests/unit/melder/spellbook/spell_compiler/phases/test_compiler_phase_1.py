"""Unit tests for current-surface compiler phase 1 requirements extraction."""

from typing import Any

import pytest

import melder.aether.spellbook.spell_compiler.phases.compiler_phase_1 as compiler_phase_1_module
from melder.aether.spellbook.spell_compiler.phases.compiler_phase_1 import (
    CompilerPhase1,
)
from melder.aether.spellbook.spell_compiler.phases.utility import (
    CompilerPhaseUtility,
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


@pytest.mark.parametrize(
    ("is_set", "expect_raise"),
    [
        (True, True),
        (False, False),
    ],
)
def test_phase_utility_throw_if_cancelled_honors_event(
        is_set: bool,
        expect_raise: bool,
) -> None:
    """CompilerPhaseUtility should only raise when the event is set."""
    cancel_event = _CancelStub(is_set=is_set)

    if expect_raise:
        with pytest.raises(RuntimeError, match="cancelled"):
            CompilerPhaseUtility.throw_if_cancelled(cancel_event)
        assert cancel_event.throw_calls == 1
    else:
        CompilerPhaseUtility.throw_if_cancelled(cancel_event)
        assert cancel_event.throw_calls == 0


def test_run_builds_requirements_once(monkeypatch: pytest.MonkeyPatch) -> None:
    """Phase 1 should build and store requirements through the finder."""
    spell = make_spell("spell-1")
    artifact = spell._compiler_artifact
    recorded: dict[str, Any] = {}

    class _FinderStub:
        """Capture the spell and cancellation input used by Phase 1."""

        def __init__(self, bound_spell: Any) -> None:
            recorded["spell"] = bound_spell

        def build_requirements(self, cancel_event=None) -> Any:
            recorded["cancel_event"] = cancel_event
            return {"requirements_for": recorded["spell"].spell_id}

    monkeypatch.setattr(
        compiler_phase_1_module,
        "SpellRequirementsFinder",
        _FinderStub,
    )
    monkeypatch.setattr(
        CompilerPhase1,
        "_build_phase1_requirements_shape_profile",
        staticmethod(lambda requirements: {}),
    )

    phase = CompilerPhase1()
    phase.run(spell, artifact)

    assert recorded["spell"] is spell
    assert recorded["cancel_event"] is None
    assert artifact._requirements == {"requirements_for": "spell-1"}


def test_run_skips_when_requirements_already_exist(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Phase 1 should not rebuild requirements when cached."""
    spell = make_spell("spell-1")
    artifact = spell._compiler_artifact
    artifact._requirements = "existing"

    class _FinderStub:
        """Sentinel finder that should never be constructed."""

        def __init__(self, _bound_spell: Any) -> None:
            raise AssertionError("finder should not be constructed")

    monkeypatch.setattr(
        compiler_phase_1_module,
        "SpellRequirementsFinder",
        _FinderStub,
    )
    monkeypatch.setattr(
        CompilerPhase1,
        "_build_phase1_requirements_shape_profile",
        staticmethod(lambda requirements: {}),
    )

    phase = CompilerPhase1()
    phase.run(spell, artifact)

    assert artifact._requirements == "existing"


def test_run_honors_cancellation_before_build(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Phase 1 should abort before constructing the finder when cancelled."""
    spell = make_spell("spell-1")
    artifact = spell._compiler_artifact
    cancel_event = _CancelStub(is_set=True)

    class _FinderStub:
        """Sentinel finder that should never be constructed."""

        def __init__(self, _bound_spell: Any) -> None:
            raise AssertionError("finder should not be constructed")

    monkeypatch.setattr(
        compiler_phase_1_module,
        "SpellRequirementsFinder",
        _FinderStub,
    )

    phase = CompilerPhase1()

    with pytest.raises(RuntimeError, match="cancelled"):
        phase.run(spell, artifact, cancel_event=cancel_event)

    assert cancel_event.throw_calls == 1
