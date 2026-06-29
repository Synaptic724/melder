"""Unit tests for current-surface compiler phase 7 frame-wide change-control wiring."""

from types import SimpleNamespace
from typing import Any, Callable, Dict, Optional, Set

import pytest

import melder.aether.spellbook.spell_compiler.spell_compiler_system as compiler_system_module
from melder.aether.spellbook.spell_compiler.phases.compiler_phase_7 import (
    CompilerPhase7,
)
from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)


class _SpellIndexStub:
    """Hashable SpellIndex stand-in for phase tests."""

    __slots__ = [
        "selected_spell_id",
        "id",
    ]

    def __init__(self, spell_id: str) -> None:
        """Store current and lineage ids."""
        self.selected_spell_id = spell_id
        self.id = "lineage-{0}".format(spell_id)

    def __hash__(self) -> int:
        """Keep the stub usable in dictionaries like real SpellIndex."""
        return hash((self.selected_spell_id, self.id))


class _RootBlueprintStub:
    """Minimal root-blueprint stand-in."""

    __slots__ = [
        "root_spell_id",
    ]

    def __init__(self, root_spell_id: str) -> None:
        """Store the root spell id."""
        self.root_spell_id = root_spell_id


class _ChangeControlManagerStub:
    """Minimal change-control manager for phase 7 wiring tests."""

    def __init__(self) -> None:
        """Initialize rebuild/revalidator call capture."""
        self.rebuild_calls: list[dict[str, Any]] = []
        self.set_calls = 0
        self._revalidate_fn_by_conduit: Dict[str, Callable[..., Any]] = {}

    def rebuild_component_of(
            self,
            conduit_id: str,
            root_blueprints: Dict[str, Any],
    ) -> None:
        """Record one component-of rebuild request."""
        self.rebuild_calls.append(
            {
                "conduit_id": conduit_id,
                "root_blueprints": root_blueprints,
            }
        )

    def has_revalidator_for_conduit(self, conduit_id: str) -> bool:
        """Report whether a revalidator is already registered."""
        return conduit_id in self._revalidate_fn_by_conduit

    def set_revalidator(
            self,
            conduit_id: str,
            revalidate_fn: Callable[..., Any],
    ) -> None:
        """Record one revalidator registration."""
        self.set_calls += 1
        self._revalidate_fn_by_conduit[conduit_id] = revalidate_fn


class _AetherStub:
    """Minimal Aether stand-in exposing change-control lookup."""

    def __init__(self, manager: _ChangeControlManagerStub) -> None:
        """Store the change-control manager."""
        self._manager = manager

    def _get_change_control_manager(self, _frame_name: str) -> _ChangeControlManagerStub:
        """Return the configured change-control manager."""
        return self._manager


def _make_spellbook_stub(*, manager: _ChangeControlManagerStub, frame_name: str = "frame") -> Any:
    """Build a minimal spellbook stub for phase 7 tests."""
    return SimpleNamespace(
        _spell_id_pool={},
        _spells_by_id={},
        _aether=_AetherStub(manager),
        _aetheric_frame_name=frame_name,
    )


def _make_spell_stub(
        spell_id: str,
        *,
        spellbook: Any,
        owned: bool = True,
) -> Any:
    """Build a minimal spell stub with a current compiler artifact."""
    artifact = SpellCompilerArtifact(spell_id)
    spell = SimpleNamespace(
        spell_id=spell_id,
        spell_name=spell_id,
        spell_index=_SpellIndexStub(spell_id),
        _spellbook=spellbook,
        _compiler_artifact=artifact,
    )
    spellbook._spell_id_pool[spell_id] = spell
    if owned:
        spellbook._spells_by_id[spell_id] = spell
    return spell


class _CancelStub:
    """Minimal cancellation stub for change-control revalidator tests."""

    def __init__(self, is_set: bool) -> None:
        """Store the initial cancellation posture."""
        self.is_set = is_set
        self.throw_calls = 0

    def throw_if_set(self) -> None:
        """Record cancellation and raise the expected runtime error."""
        self.throw_calls += 1
        raise RuntimeError("cancelled")


def test_run_frame_wide_rebuilds_owned_roots_and_registers_revalidator(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Phase 7 should rebuild component_of for owned roots and register a revalidator."""
    phase = CompilerPhase7()
    manager = _ChangeControlManagerStub()
    spellbook = _make_spellbook_stub(manager=manager)
    owned_spell = _make_spell_stub("owned", spellbook=spellbook, owned=True)
    _make_spell_stub("contracted", spellbook=spellbook, owned=False)
    owned_spell._compiler_artifact._entire_dag_blueprint_phase5 = {
        "owned": _RootBlueprintStub("owned"),
        "contracted": _RootBlueprintStub("contracted"),
    }

    phase.run_frame_wide(
        owned_spell._compiler_artifact,
        spellbook,
        "cid",
    )

    assert manager.rebuild_calls == [
        {
            "conduit_id": "cid",
            "root_blueprints": {
                "owned": owned_spell._compiler_artifact._entire_dag_blueprint_phase5["owned"],
            },
        }
    ]
    assert manager.set_calls == 1
    assert manager._revalidate_fn_by_conduit["cid"] is not None


def test_run_frame_wide_revalidator_replays_all_phases_for_dirty_roots(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Phase 7 revalidator should call back into SpellCompilerSystem.run_all_phases."""
    phase = CompilerPhase7()
    manager = _ChangeControlManagerStub()
    spellbook = _make_spellbook_stub(manager=manager)
    root_spell = _make_spell_stub("root", spellbook=spellbook, owned=True)
    root_spell._compiler_artifact._entire_dag_blueprint_phase5 = {
        "root": _RootBlueprintStub("root"),
    }
    run_calls: list[dict[str, Any]] = []
    cleanup_calls: list[str] = []

    class _CompilerSystemStub:
        """Compiler-system stand-in for phase-7 revalidation."""

        def run_all_phases(
                self,
                bound_spellbook: Any,
                bound_spell: Any,
                *,
                conduit_id: str,
                cancel_event: Any = None,
        ) -> None:
            run_calls.append(
                {
                    "spellbook": bound_spellbook,
                    "spell": bound_spell,
                    "conduit_id": conduit_id,
                    "cancel_event": cancel_event,
                }
            )

        def cleanup(self) -> None:
            cleanup_calls.append("cleanup")

    monkeypatch.setattr(
        compiler_system_module,
        "SpellCompilerSystem",
        _CompilerSystemStub,
    )

    phase.run_frame_wide(
        root_spell._compiler_artifact,
        spellbook,
        "cid",
    )

    revalidate_fn = manager._revalidate_fn_by_conduit.get("cid")
    assert revalidate_fn is not None
    cancel = _CancelStub(is_set=False)
    validated = revalidate_fn(set(["root"]), cancel)

    assert validated == {"root"}
    assert run_calls == [
        {
            "spellbook": spellbook,
            "spell": root_spell,
            "conduit_id": "cid",
            "cancel_event": cancel,
        }
    ]
    assert cleanup_calls == ["cleanup"]


def test_run_frame_wide_skips_revalidator_registration_when_present() -> None:
    """Phase 7 should not replace an existing revalidator."""
    phase = CompilerPhase7()
    manager = _ChangeControlManagerStub()
    sentinel = lambda dirty_roots, cancel_event: set()  # noqa: E731
    manager._revalidate_fn_by_conduit["cid"] = sentinel
    spellbook = _make_spellbook_stub(manager=manager)
    root_spell = _make_spell_stub("root", spellbook=spellbook, owned=True)
    root_spell._compiler_artifact._entire_dag_blueprint_phase5 = {
        "root": _RootBlueprintStub("root"),
    }

    phase.run_frame_wide(
        root_spell._compiler_artifact,
        spellbook,
        "cid",
    )

    assert manager.set_calls == 0
    assert manager._revalidate_fn_by_conduit["cid"] is sentinel
