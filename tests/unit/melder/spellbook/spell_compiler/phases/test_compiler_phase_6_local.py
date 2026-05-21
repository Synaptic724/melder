"""Unit tests for current-surface compiler phase 6 local validation behavior."""

from types import SimpleNamespace
from typing import Any, Dict, Optional, Set

import pytest

import melder.aether.spellbook.spell_compiler.phases.compiler_phase_6 as compiler_phase_6_module
from melder.aether.spellbook.spell_compiler.phases.compiler_phase_6 import (
    CompilerPhase6,
)
from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
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


class _SpellSystemStatesStub:
    """Minimal spell-system-state registry for phase 6 local tests."""

    def __init__(self) -> None:
        """Initialize empty topology and bulk-update capture."""
        self._local_topology_by_id: Dict[str, Any] = {}
        self.bulk_spell_validity_calls: list[tuple[str, dict[str, Any], Any]] = []
        self.bulk_root_validity_calls: list[tuple[str, dict[str, Any], Any]] = []
        self.recorded_conduit_diagnostics: list[tuple[str, list[Any]]] = []

    def set_local_topology_for_id(self, spell_id: str, topology: Any) -> None:
        """Record topology for one spell id."""
        self._local_topology_by_id[spell_id] = topology

    def get_local_topology_by_id(self, spell_id: str) -> Any:
        """Return the topology for the supplied spell id."""
        return self._local_topology_by_id.get(spell_id)

    def bulk_set_conduit_spell_validity(
            self,
            conduit_id: str,
            values: dict[str, Any],
            change_reason: Any,
    ) -> None:
        """Record a bulk spell-validity update."""
        self.bulk_spell_validity_calls.append((conduit_id, values, change_reason))

    def bulk_set_conduit_root_validity(
            self,
            conduit_id: str,
            values: dict[str, Any],
            change_reason: Any,
    ) -> None:
        """Record a bulk root-validity update."""
        self.bulk_root_validity_calls.append((conduit_id, values, change_reason))

    def record_conduit_diagnostics(self, conduit_id: str, diagnostics: list[Any]) -> None:
        """Record conduit diagnostics."""
        self.recorded_conduit_diagnostics.append((conduit_id, diagnostics))


class _ValidatorStub:
    """Minimal system-validation stub for scoped phase 6 tests."""

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
    """Build a minimal spellbook stub for phase 6 local tests."""
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


def test_collect_local_visibility_gap_diagnostics_emits_one_error_per_missing_edge() -> None:
    """Local Phase 6 should dedupe repeated missing dependency edges."""
    phase = CompilerPhase6()
    states = _SpellSystemStatesStub()
    spellbook = _make_spellbook_stub()
    root_spell = _make_spell_stub("root", spellbook=spellbook)

    class _Socket:
        def __init__(self, param_name: str, target_spell_ids: tuple[str, ...]) -> None:
            self.param_name = param_name
            self.target_spell_ids = target_spell_ids

    class _Topology:
        def __init__(self, sockets: list[_Socket]) -> None:
            self._sockets = sockets

        def iter_sockets(self) -> list[_Socket]:
            return list(self._sockets)

    states.set_local_topology_for_id(
        "root",
        _Topology(
            [
                _Socket("svc", ("missing-dep",)),
                _Socket("svc", ("missing-dep",)),
            ]
        ),
    )

    diagnostics = phase._collect_local_visibility_gap_diagnostics(
        spell=root_spell,
        spell_system_states=states,
        scoped_spell_ids={"root"},
        spell_lookup={"root": root_spell},
        root_ids={"root"},
    )

    assert len(diagnostics) == 1
    diagnostic = diagnostics[0]
    assert diagnostic.code == "visibility_gap_dependency_filtered"
    assert diagnostic.spell_id == "root"
    assert diagnostic.root_id == "root"
    assert diagnostic.details["missing_dependency_id"] == "missing-dep"


def test_collect_local_blueprint_visibility_gap_diagnostics_emits_missing_nodes() -> None:
    """Local Phase 6 should emit diagnostics for missing blueprint DAG nodes."""
    phase = CompilerPhase6()
    spellbook = _make_spellbook_stub()
    root_spell = _make_spell_stub("root", spellbook=spellbook)
    blueprint = SimpleNamespace(
        dag=SimpleNamespace(
            nodes={
                "root": object(),
                "missing-dep": object(),
            }
        )
    )

    diagnostics = phase._collect_local_blueprint_visibility_gap_diagnostics(
        blueprints={"root": blueprint},
        spell_lookup={"root": root_spell},
    )

    assert len(diagnostics) == 1
    diagnostic = diagnostics[0]
    assert diagnostic.code == "visibility_gap_dependency_filtered"
    assert diagnostic.spell_id == "missing-dep"
    assert diagnostic.root_id == "root"
    assert diagnostic.details["missing_dependency_id"] == "missing-dep"


def test_collect_local_blueprint_visibility_gap_diagnostics_dedupes_duplicate_missing_nodes() -> None:
    """Local Phase 6 should dedupe repeated missing blueprint nodes per root."""
    phase = CompilerPhase6()
    blueprint = SimpleNamespace(
        dag=SimpleNamespace(
            nodes={
                "root": object(),
                "missing-dep": object(),
            }
        )
    )

    diagnostics = phase._collect_local_blueprint_visibility_gap_diagnostics(
        blueprints={
            "root": blueprint,
            "root-duplicate": blueprint,
        },
        spell_lookup={"root": object()},
    )

    assert len(diagnostics) == 2
    assert {(diag.root_id, diag.spell_id) for diag in diagnostics} == {
        ("root", "missing-dep"),
        ("root-duplicate", "missing-dep"),
    }


def test_run_local_requires_phase5_local_artifacts() -> None:
    """Local Phase 6 should require the scoped Phase 5 artifacts."""
    phase = CompilerPhase6()
    spellbook = _make_spellbook_stub()
    root_spell = _make_spell_stub("root", spellbook=spellbook)

    with pytest.raises(RuntimeError, match="Phase 6 local requires Phase 5 local artifacts"):
        phase.run_local(
            root_spell,
            root_spell._compiler_artifact,
            spellbook,
            _SpellSystemStatesStub(),
            "cid",
        )


def test_run_local_marks_invalid_on_visibility_gap() -> None:
    """Local Phase 6 should short-circuit invalid on visibility gaps."""
    phase = CompilerPhase6()
    states = _SpellSystemStatesStub()
    spellbook = _make_spellbook_stub()
    root_spell = _make_spell_stub("root", spellbook=spellbook)

    class _Socket:
        def __init__(self, param_name: str, target_spell_ids: tuple[str, ...]) -> None:
            self.param_name = param_name
            self.target_spell_ids = target_spell_ids

    class _Topology:
        def __init__(self, sockets: list[_Socket]) -> None:
            self._sockets = sockets

        def iter_sockets(self) -> list[_Socket]:
            return list(self._sockets)

    states.set_local_topology_for_id(
        "root",
        _Topology([_Socket("svc", ("missing-dep",))]),
    )

    root_spell._compiler_artifact._spell_system_index_phase5 = SimpleNamespace(nodes={"root": object()})
    root_spell._compiler_artifact._entire_dag_blueprint_phase5 = {
        "root": SimpleNamespace(
            dag=SimpleNamespace(nodes={"root": object()}),
        )
    }

    phase.run_local(
        root_spell,
        root_spell._compiler_artifact,
        spellbook,
        states,
        "cid",
    )

    validation_state = root_spell._compiler_artifact._validation_result_phase6
    assert validation_state is not None
    assert validation_state.is_valid is False
    assert len(validation_state.errors) == 1
    assert states.bulk_spell_validity_calls == [
        (
            "cid",
            {"root": compiler_phase_6_module.SpellValidity.invalid},
            compiler_phase_6_module.SpellStateChangeReason.validation_failed,
        )
    ]
    assert states.bulk_root_validity_calls == [
        (
            "cid",
            {"root": compiler_phase_6_module.SpellValidity.invalid},
            compiler_phase_6_module.SpellStateChangeReason.validation_failed,
        )
    ]
    assert len(states.recorded_conduit_diagnostics) == 1


def test_run_local_uses_scoped_lookup_and_broken_ids(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Local Phase 6 should validate only scoped spells and publish scoped state."""
    phase = CompilerPhase6()
    states = _SpellSystemStatesStub()
    spellbook = _make_spellbook_stub()
    root_spell = _make_spell_stub("root", spellbook=spellbook)
    dep_spell = _make_spell_stub("dep", spellbook=spellbook)
    outside_spell = _make_spell_stub("outside", spellbook=spellbook)
    dep_spell._compiler_artifact._is_broken = True
    root_spell._compiler_artifact._spell_system_index_phase5 = SimpleNamespace(
        nodes={
            "root": object(),
            "dep": object(),
        }
    )
    root_spell._compiler_artifact._entire_dag_blueprint_phase5 = {
        "root": SimpleNamespace(
            dag=SimpleNamespace(
                nodes={
                    "root": object(),
                    "dep": object(),
                }
            )
        ),
    }
    _ValidatorStub.next_result = {"state": "ok"}
    monkeypatch.setattr(
        compiler_phase_6_module,
        "SpellSystemValidationSystem",
        _ValidatorStub,
    )

    phase.run_local(
        root_spell,
        root_spell._compiler_artifact,
        spellbook,
        states,
        "cid",
    )

    validator = _ValidatorStub.last_instance
    assert validator is not None
    call = validator.validate_calls[0]
    assert set(call["spell_lookup"].keys()) == {"root", "dep"}
    assert call["broken_spell_ids"] == {"dep"}
    assert root_spell._compiler_artifact._validation_result_phase6 == {"state": "ok"}
    assert dep_spell._compiler_artifact._validation_result_phase6 == {"state": "ok"}
    assert outside_spell._compiler_artifact._validation_result_phase6 is None
