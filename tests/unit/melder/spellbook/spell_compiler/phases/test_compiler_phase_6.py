"""Unit tests for current-surface compiler phase 6 frame-wide validation behavior."""

from types import SimpleNamespace
from typing import Any, Optional

import pytest

import melder.aether.spellbook.spell_compiler.phases.compiler_phase_6 as compiler_phase_6_module
from melder.aether.spellbook.spell_compiler.phases.compiler_phase_6 import (
    CompilerPhase6,
)
from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)
from melder.aether.spellbook.spell_compiler.system.spell_system_index import (
    SpellSystemIndex,
)
from melder.aether.spellbook.spell_types.spell_types import SpellType


class _SpellIndexStub:
    """Hashable SpellIndex stand-in for phase tests."""

    __slots__ = [
        "current",
        "id",
    ]

    def __init__(self, spell_id: str) -> None:
        """Store current and lineage ids."""
        self.current = spell_id
        self.id = "lineage-{0}".format(spell_id)

    def __hash__(self) -> int:
        """Keep the stub usable in dictionaries like real SpellIndex."""
        return hash((self.current, self.id))


class _ValidatorStub:
    """Minimal system-validation stub for frame-wide phase 6 tests."""

    last_instance: Optional["_ValidatorStub"] = None
    next_result: Any = None

    def __init__(self, strategies: Any) -> None:
        """Capture strategies and initialize validate-call recording."""
        self.strategies = strategies
        self.validate_calls: list[dict[str, Any]] = []
        _ValidatorStub.last_instance = self

    def validate(self, **kwargs: Any) -> Any:
        """Record the validate call and return the configured result."""
        self.validate_calls.append(kwargs)
        return self.next_result


def _make_spellbook_stub() -> Any:
    """Build a minimal spellbook stub for phase 6 tests."""
    return SimpleNamespace(
        _spell_id_pool={},
    )


def _make_spell_stub(
        spell_id: str,
        *,
        spellbook: Any,
        spell_type: SpellType = SpellType.SPELL,
) -> Any:
    """Build a minimal spell stub with a current compiler artifact."""
    artifact = SpellCompilerArtifact(spell_id)
    spell = SimpleNamespace(
        spell_id=spell_id,
        spell_name=spell_id,
        spell_type=spell_type,
        spell_index=_SpellIndexStub(spell_id),
        _spellbook=spellbook,
        _compiler_artifact=artifact,
    )
    spellbook._spell_id_pool[spell_id] = spell
    return spell


@pytest.mark.parametrize(
    ("missing_blueprints", "missing_index"),
    [
        (True, False),
        (False, True),
    ],
)
def test_run_frame_wide_requires_phase5_artifacts(
        missing_blueprints: bool,
        missing_index: bool,
) -> None:
    """Frame-wide Phase 6 should require the Phase 5 blueprint map and index."""
    phase = CompilerPhase6()
    spellbook = _make_spellbook_stub()
    root_spell = _make_spell_stub("root", spellbook=spellbook)

    if not missing_blueprints:
        root_spell._compiler_artifact._entire_dag_blueprint_phase5 = {
            "root": object(),
        }
    if not missing_index:
        root_spell._compiler_artifact._spell_system_index_phase5 = (
            SpellSystemIndex()
        )

    with pytest.raises(RuntimeError, match="Phase 5"):
        phase.run_frame_wide(
            root_spell._compiler_artifact,
            spellbook,
            SimpleNamespace(),
            "cid",
        )


def test_run_frame_wide_collects_phase4_and_broken_ids(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Frame-wide Phase 6 should aggregate Phase 4 outputs and broken ids."""
    phase = CompilerPhase6()
    spellbook = _make_spellbook_stub()
    root_spell = _make_spell_stub("root", spellbook=spellbook)
    other_spell = _make_spell_stub("other", spellbook=spellbook)
    root_spell._compiler_artifact._entire_dag_blueprint_phase5 = {
        "root": object(),
    }
    root_spell._compiler_artifact._spell_system_index_phase5 = (
        SpellSystemIndex()
    )
    root_spell._compiler_artifact._validation_result_phase4 = "phase4-root"
    other_spell._compiler_artifact._validation_result_phase4 = "phase4-other"
    other_spell._compiler_artifact._is_broken = True
    _ValidatorStub.next_result = {"state": "ok"}
    monkeypatch.setattr(
        compiler_phase_6_module,
        "SpellSystemValidationSystem",
        _ValidatorStub,
    )

    phase.run_frame_wide(
        root_spell._compiler_artifact,
        spellbook,
        SimpleNamespace(),
        "cid",
    )

    validator = _ValidatorStub.last_instance
    assert validator is not None
    call = validator.validate_calls[0]
    assert call["phase4_results"] == {
        "root": "phase4-root",
        "other": "phase4-other",
    }
    assert call["broken_spell_ids"] == {"other"}


def test_run_frame_wide_sets_flags_for_all_visible_spells(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Frame-wide Phase 6 should publish one shared phase-6 result to all visible spells."""
    phase = CompilerPhase6()
    spellbook = _make_spellbook_stub()
    root_spell = _make_spell_stub("root", spellbook=spellbook)
    other_spell = _make_spell_stub("other", spellbook=spellbook)
    root_spell._compiler_artifact._entire_dag_blueprint_phase5 = {
        "root": object(),
    }
    root_spell._compiler_artifact._spell_system_index_phase5 = (
        SpellSystemIndex()
    )
    validation_state = {"state": "frame-ok"}
    _ValidatorStub.next_result = validation_state
    monkeypatch.setattr(
        compiler_phase_6_module,
        "SpellSystemValidationSystem",
        _ValidatorStub,
    )

    phase.run_frame_wide(
        root_spell._compiler_artifact,
        spellbook,
        SimpleNamespace(),
        "cid",
    )

    assert root_spell._compiler_artifact._validation_result_phase6 == validation_state
    assert root_spell._compiler_artifact._validated_phase6 is True
    assert other_spell._compiler_artifact._validation_result_phase6 == validation_state
    assert other_spell._compiler_artifact._validated_phase6 is True
