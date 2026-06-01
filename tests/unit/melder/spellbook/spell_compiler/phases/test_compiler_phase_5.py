"""Unit tests for current-surface compiler phase 5 rooted-blueprint behavior."""

from types import SimpleNamespace
from typing import Any, Callable, Dict, Optional, Set

import pytest

import melder.aether.spellbook.spell_compiler.phases.compiler_phase_5 as compiler_phase_5_module
import melder.aether.spellbook.spell_compiler.spell_compiler_system as compiler_system_module
from melder.aether.spellbook.spell_compiler.phases.compiler_phase_5 import (
    CompilerPhase5,
)
from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)
from melder.aether.spellbook.spell_compiler.system.spell_system_adjacency_snapshot import (
    SpellSystemAdjacencySnapshot,
)
from melder.aether.spellbook.spell_types.spell_types import SpellType


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


class _SpellStateStub:
    """Minimal spell-system-state stand-in for lineage lookup."""

    __slots__ = [
        "current_spell_id",
        "spell_index_id",
    ]

    def __init__(self, spell_id: str, spell_index_id: str) -> None:
        """Store lineage metadata."""
        self.current_spell_id = spell_id
        self.spell_index_id = spell_index_id


class _SpellSystemStatesStub:
    """Minimal spell-system-state registry for phase 5 tests."""

    def __init__(self, states: list[_SpellStateStub]) -> None:
        """Index states by spell id for lookup."""
        self._states_by_spell_id = {
            state.current_spell_id: state
            for state in states
        }

    def get_by_spell_id(self, spell_id: str) -> Optional[_SpellStateStub]:
        """Return the state for the supplied spell id."""
        return self._states_by_spell_id.get(spell_id)


class _RootBlueprintStub:
    """Minimal root-blueprint stand-in."""

    __slots__ = [
        "root_spell_id",
        "ordered_node_ids",
        "requires_spellspace_request",
    ]

    def __init__(
            self,
            root_spell_id: str,
            *,
            ordered_node_ids: Optional[tuple[str, ...]] = None,
            requires_spellspace_request: bool = False,
    ) -> None:
        """Store the root spell id and stable ordered node ids."""
        self.root_spell_id = root_spell_id
        if ordered_node_ids is None:
            ordered_node_ids = (root_spell_id,)
        self.ordered_node_ids = ordered_node_ids
        self.requires_spellspace_request = requires_spellspace_request


class _AdjacencyBuilderStub:
    """Record Phase 5 adjacency-builder calls and return one snapshot."""

    next_snapshot: Any = None
    last_instance: Optional["_AdjacencyBuilderStub"] = None

    def __init__(self) -> None:
        """Capture the latest builder instance."""
        self.calls: list[Any] = []
        _AdjacencyBuilderStub.last_instance = self

    def build(self, spell_system_states: Any) -> Any:
        """Record the state surface and return the configured snapshot."""
        self.calls.append(spell_system_states)
        return self.next_snapshot


class _RootBlueprintBuilderStub:
    """Record blueprint-builder calls and return configured outputs."""

    next_blueprints: Dict[str, Any] = {}
    next_fallback_blueprint: Any = None
    last_instance: Optional["_RootBlueprintBuilderStub"] = None

    def __init__(self) -> None:
        """Capture the latest builder instance."""
        self.build_root_blueprints_calls: list[Any] = []
        self.build_blueprint_for_spell_id_calls: list[tuple[str, Any]] = []
        _RootBlueprintBuilderStub.last_instance = self

    def build_root_blueprints(
            self,
            snapshot: Any,
            spellspace_scoped_spell_ids: Optional[set[str]] = None,
    ) -> Dict[str, Any]:
        """Record the snapshot and return configured root blueprints."""
        self.build_root_blueprints_calls.append(snapshot)
        return dict(self.next_blueprints)

    def build_blueprint_for_spell_id(
            self,
            root_spell_id: str,
            snapshot: Any,
            spellspace_scoped_spell_ids: Optional[set[str]] = None,
    ) -> Any:
        """Record the fallback request and return the configured fallback blueprint."""
        self.build_blueprint_for_spell_id_calls.append((root_spell_id, snapshot))
        if self.next_fallback_blueprint is not None:
            return self.next_fallback_blueprint
        return _RootBlueprintStub(root_spell_id)


class _ChangeControlManagerStub:
    """Minimal change-control manager for phase 5 revalidator wiring tests."""

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

    def __init__(
            self,
            manager: Optional[_ChangeControlManagerStub] = None,
            *,
            raise_on_get: bool = False,
    ) -> None:
        """Store the manager and optional failure mode."""
        self._manager = manager
        self._raise_on_get = raise_on_get

    def _get_change_control_manager(self, _frame_name: str) -> _ChangeControlManagerStub:
        """Return the configured manager or raise the configured failure."""
        if self._raise_on_get:
            raise RuntimeError("boom")
        return self._manager


def _make_spellbook_stub(
        *,
        spell_system_states: _SpellSystemStatesStub,
        aether: Optional[_AetherStub] = None,
        frame_name: str = "frame",
) -> Any:
    """Build a minimal spellbook stub for phase 5 tests."""
    spellbook = SimpleNamespace(
        _spell_id_pool={},
        _spells_by_id={},
        _aether=aether if aether is not None else _AetherStub(_ChangeControlManagerStub()),
        _aetheric_frame=frame_name,
        _spell_system_states=spell_system_states,
    )
    return spellbook


def _make_spell_stub(
        spell_id: str,
        *,
        spellbook: Any,
        spell_system_states: _SpellSystemStatesStub,
        spell_type: SpellType = SpellType.SPELL,
        owner_conduit_id: Optional[str] = None,
        is_existing_creation: bool = False,
) -> Any:
    """Build a minimal spell stub with a current compiler artifact."""
    artifact = SpellCompilerArtifact(spell_id)
    spell = SimpleNamespace(
        spell_id=spell_id,
        spell_name=spell_id,
        spell_type=spell_type,
        spell_index=_SpellIndexStub(spell_id),
        existence="existence:{0}".format(spell_id),
        _owner_conduit_id=owner_conduit_id,
        _spellbook=spellbook,
        _compiler_artifact=artifact,
        is_existing_creation=is_existing_creation,
    )
    spell._cleanup_creation_context = lambda: None
    spellbook._spell_id_pool[spell_id] = spell
    if not is_existing_creation:
        spellbook._spells_by_id[spell_id] = spell
    return spell


def _patch_ir_exports(monkeypatch: pytest.MonkeyPatch) -> dict[str, list[tuple[Any, Any]]]:
    """Disable real IR export and record capture calls instead."""
    captured = {
        "capture": [],
    }
    monkeypatch.setattr(
        compiler_phase_5_module.SharedCompilerExecutions,
        "capture_phase2_5_codegen_ir",
        lambda spell, artifact: captured["capture"].append((spell, artifact)),
    )
    return captured


def test_set_root_blueprint_phase5_rejects_none(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Phase 5 helper should reject a null root blueprint."""
    phase = CompilerPhase5()
    captured = _patch_ir_exports(monkeypatch)
    spellbook = _make_spellbook_stub(
        spell_system_states=_SpellSystemStatesStub(
            [_SpellStateStub("root", "lineage-root")]
        )
    )
    spell = _make_spell_stub(
        "root",
        spellbook=spellbook,
        spell_system_states=spellbook._spell_system_states,
    )

    with pytest.raises(ValueError, match="blueprint must not be None"):
        phase._set_root_blueprint_phase5(
            spell,
            spell._compiler_artifact,
            None,
        )

    assert captured["capture"] == []


def test_set_root_blueprint_phase5_sets_value_and_refreshes_ir(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Phase 5 helper should store the root blueprint and refresh IR caches."""
    phase = CompilerPhase5()
    captured = _patch_ir_exports(monkeypatch)
    spellbook = _make_spellbook_stub(
        spell_system_states=_SpellSystemStatesStub(
            [_SpellStateStub("root", "lineage-root")]
        )
    )
    spell = _make_spell_stub(
        "root",
        spellbook=spellbook,
        spell_system_states=spellbook._spell_system_states,
    )
    blueprint = _RootBlueprintStub("root")

    phase._set_root_blueprint_phase5(
        spell,
        spell._compiler_artifact,
        blueprint,
    )

    assert spell._compiler_artifact._root_blueprint_phase5 is blueprint
    assert spell._compiler_artifact._requires_spellspace_request_phase5 is False
    assert spell.requires_spellspace_request is False
    assert captured["capture"] == [(spell, spell._compiler_artifact)]


def test_set_root_blueprint_phase5_sets_spellspace_request_flag(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Phase 5 helper should bind spellspace-request truth onto spell and artifact."""
    phase = CompilerPhase5()
    captured = _patch_ir_exports(monkeypatch)
    spellbook = _make_spellbook_stub(
        spell_system_states=_SpellSystemStatesStub(
            [_SpellStateStub("root", "lineage-root")]
        )
    )
    spell = _make_spell_stub(
        "root",
        spellbook=spellbook,
        spell_system_states=spellbook._spell_system_states,
    )
    blueprint = _RootBlueprintStub("root", requires_spellspace_request=True)

    phase._set_root_blueprint_phase5(
        spell,
        spell._compiler_artifact,
        blueprint,
    )

    assert spell._compiler_artifact._root_blueprint_phase5 is blueprint
    assert spell._compiler_artifact._requires_spellspace_request_phase5 is True
    assert spell.requires_spellspace_request is True
    assert captured["capture"] == [(spell, spell._compiler_artifact)]


def test_set_spell_system_index_phase5_rejects_none(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Phase 5 helper should reject a null system index."""
    phase = CompilerPhase5()
    captured = _patch_ir_exports(monkeypatch)
    spellbook = _make_spellbook_stub(
        spell_system_states=_SpellSystemStatesStub(
            [_SpellStateStub("root", "lineage-root")]
        )
    )
    spell = _make_spell_stub(
        "root",
        spellbook=spellbook,
        spell_system_states=spellbook._spell_system_states,
    )

    with pytest.raises(ValueError, match="index must not be None"):
        phase._set_spell_system_index_phase5(spell, spell._compiler_artifact, None)

    assert captured["capture"] == []


def test_set_spell_system_index_phase5_sets_value_and_refreshes_ir(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Phase 5 helper should store the system index and refresh IR caches."""
    phase = CompilerPhase5()
    captured = _patch_ir_exports(monkeypatch)
    spellbook = _make_spellbook_stub(
        spell_system_states=_SpellSystemStatesStub(
            [_SpellStateStub("root", "lineage-root")]
        )
    )
    spell = _make_spell_stub(
        "root",
        spellbook=spellbook,
        spell_system_states=spellbook._spell_system_states,
    )
    index = compiler_phase_5_module.SpellSystemIndex()

    phase._set_spell_system_index_phase5(spell, spell._compiler_artifact, index)

    assert spell._compiler_artifact._spell_system_index_phase5 is index
    assert captured["capture"] == [(spell, spell._compiler_artifact)]


def test_run_frame_wide_builds_index_and_attaches_blueprints(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Phase 5 global entrypoint should attach blueprints and build the index."""
    phase = CompilerPhase5()
    states = _SpellSystemStatesStub(
        [
            _SpellStateStub("root", "lineage-root"),
            _SpellStateStub("dep", "lineage-dep"),
        ]
    )
    spellbook = _make_spellbook_stub(spell_system_states=states)
    root_spell = _make_spell_stub(
        "root",
        spellbook=spellbook,
        spell_system_states=states,
        owner_conduit_id="conduit-root",
    )
    dep_spell = _make_spell_stub(
        "dep",
        spellbook=spellbook,
        spell_system_states=states,
        owner_conduit_id="conduit-dep",
    )
    captured = _patch_ir_exports(monkeypatch)
    snapshot = SpellSystemAdjacencySnapshot(
        dependencies={
            "root": {"dep"},
            "dep": set(),
        },
        reverse_dependencies={
            "dep": {"root"},
        },
        all_spell_ids={"root", "dep"},
        root_spell_ids={"root"},
        topologies={},
    )
    blueprint = _RootBlueprintStub("root")
    _AdjacencyBuilderStub.next_snapshot = snapshot
    _RootBlueprintBuilderStub.next_blueprints = {"root": blueprint}
    _RootBlueprintBuilderStub.next_fallback_blueprint = None
    monkeypatch.setattr(
        compiler_phase_5_module,
        "SpellSystemAdjacencyBuilder",
        _AdjacencyBuilderStub,
    )
    monkeypatch.setattr(
        compiler_phase_5_module,
        "SpellSystemRootBlueprintBuilder",
        _RootBlueprintBuilderStub,
    )

    phase.run_frame_wide(
        root_spell,
        root_spell._compiler_artifact,
        spellbook,
        states,
        "cid",
    )

    index = root_spell._compiler_artifact._spell_system_index_phase5
    assert root_spell._compiler_artifact._root_blueprint_phase5 is blueprint
    assert index is not None
    root_node = index.get_node("root")
    dep_node = index.get_node("dep")
    assert root_node is not None
    assert dep_node is not None
    assert root_node.dependencies == {"dep"}
    assert root_node.is_root is True
    assert dep_node.is_root is False
    assert dep_node.conduit_id == "conduit-dep"
    assert root_spell._compiler_artifact._entire_dag_blueprint_phase5 == {
        "root": blueprint,
    }
    assert captured["capture"][-1] == (root_spell, root_spell._compiler_artifact)


def test_run_frame_wide_attaches_fallback_blueprint_when_root_missing(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Phase 5 global entrypoint should build a fallback blueprint for the root spell."""
    phase = CompilerPhase5()
    states = _SpellSystemStatesStub([_SpellStateStub("root", "lineage-root")])
    spellbook = _make_spellbook_stub(spell_system_states=states)
    root_spell = _make_spell_stub(
        "root",
        spellbook=spellbook,
        spell_system_states=states,
    )
    _patch_ir_exports(monkeypatch)
    snapshot = SpellSystemAdjacencySnapshot(
        dependencies={},
        reverse_dependencies={},
        all_spell_ids={"root"},
        root_spell_ids={"missing"},
        topologies={},
    )
    fallback = _RootBlueprintStub("root")
    _AdjacencyBuilderStub.next_snapshot = snapshot
    _RootBlueprintBuilderStub.next_blueprints = {"missing": _RootBlueprintStub("missing")}
    _RootBlueprintBuilderStub.next_fallback_blueprint = fallback
    monkeypatch.setattr(
        compiler_phase_5_module,
        "SpellSystemAdjacencyBuilder",
        _AdjacencyBuilderStub,
    )
    monkeypatch.setattr(
        compiler_phase_5_module,
        "SpellSystemRootBlueprintBuilder",
        _RootBlueprintBuilderStub,
    )

    phase.run_frame_wide(
        root_spell,
        root_spell._compiler_artifact,
        spellbook,
        states,
        "cid",
    )

    assert root_spell._compiler_artifact._root_blueprint_phase5 is fallback
    builder = _RootBlueprintBuilderStub.last_instance
    assert builder is not None
    assert len(builder.build_blueprint_for_spell_id_calls) == 1
    root_id, scoped_snapshot = builder.build_blueprint_for_spell_id_calls[0]
    assert root_id == "root"
    assert scoped_snapshot.all_spell_ids == {"root"}


def test_run_frame_wide_filters_component_of_rebuild_to_owned_roots(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Phase 5 should rebuild component_of only for owned roots."""
    phase = CompilerPhase5()
    manager = _ChangeControlManagerStub()
    aether = _AetherStub(manager)
    states = _SpellSystemStatesStub(
        [
            _SpellStateStub("owned", "lineage-owned"),
            _SpellStateStub("contracted", "lineage-contracted"),
        ]
    )
    spellbook = _make_spellbook_stub(
        spell_system_states=states,
        aether=aether,
    )
    owned_spell = _make_spell_stub(
        "owned",
        spellbook=spellbook,
        spell_system_states=states,
    )
    _make_spell_stub(
        "contracted",
        spellbook=spellbook,
        spell_system_states=states,
        is_existing_creation=True,
    )
    _patch_ir_exports(monkeypatch)
    snapshot = SpellSystemAdjacencySnapshot(
        dependencies={
            "owned": set(),
            "contracted": set(),
        },
        reverse_dependencies={},
        all_spell_ids={"owned", "contracted"},
        root_spell_ids={"owned", "contracted"},
        topologies={},
    )
    blueprints = {
        "owned": _RootBlueprintStub("owned"),
        "contracted": _RootBlueprintStub("contracted"),
    }
    _AdjacencyBuilderStub.next_snapshot = snapshot
    _RootBlueprintBuilderStub.next_blueprints = blueprints
    monkeypatch.setattr(
        compiler_phase_5_module,
        "SpellSystemAdjacencyBuilder",
        _AdjacencyBuilderStub,
    )
    monkeypatch.setattr(
        compiler_phase_5_module,
        "SpellSystemRootBlueprintBuilder",
        _RootBlueprintBuilderStub,
    )

    phase.run_frame_wide(
        owned_spell,
        owned_spell._compiler_artifact,
        spellbook,
        states,
        "cid",
    )

    assert manager.rebuild_calls == [
        {
            "conduit_id": "cid",
            "root_blueprints": {"owned": blueprints["owned"]},
        }
    ]


def test_run_frame_wide_registers_revalidator_and_revalidates_dirty_roots(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Phase 5 should register a revalidator that replays compiler-system phases."""
    phase = CompilerPhase5()
    manager = _ChangeControlManagerStub()
    aether = _AetherStub(manager)
    states = _SpellSystemStatesStub([_SpellStateStub("root", "lineage-root")])
    spellbook = _make_spellbook_stub(
        spell_system_states=states,
        aether=aether,
    )
    root_spell = _make_spell_stub(
        "root",
        spellbook=spellbook,
        spell_system_states=states,
    )
    _patch_ir_exports(monkeypatch)
    snapshot = SpellSystemAdjacencySnapshot(
        dependencies={"root": set()},
        reverse_dependencies={},
        all_spell_ids={"root"},
        root_spell_ids={"root"},
        topologies={},
    )
    _AdjacencyBuilderStub.next_snapshot = snapshot
    _RootBlueprintBuilderStub.next_blueprints = {"root": _RootBlueprintStub("root")}
    monkeypatch.setattr(
        compiler_phase_5_module,
        "SpellSystemAdjacencyBuilder",
        _AdjacencyBuilderStub,
    )
    monkeypatch.setattr(
        compiler_phase_5_module,
        "SpellSystemRootBlueprintBuilder",
        _RootBlueprintBuilderStub,
    )
    run_calls: list[dict[str, Any]] = []
    cleanup_calls: list[str] = []

    class _CompilerSystemStub:
        """Compiler-system stand-in for phase-5 revalidation."""

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
        root_spell,
        root_spell._compiler_artifact,
        spellbook,
        states,
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


def test_run_frame_wide_propagates_change_control_lookup_error_after_artifacts(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Phase 5 should build artifacts before a change-control lookup failure propagates."""
    phase = CompilerPhase5()
    aether = _AetherStub(raise_on_get=True)
    states = _SpellSystemStatesStub([_SpellStateStub("root", "lineage-root")])
    spellbook = _make_spellbook_stub(
        spell_system_states=states,
        aether=aether,
    )
    root_spell = _make_spell_stub(
        "root",
        spellbook=spellbook,
        spell_system_states=states,
    )
    _patch_ir_exports(monkeypatch)
    snapshot = SpellSystemAdjacencySnapshot(
        dependencies={"root": set()},
        reverse_dependencies={},
        all_spell_ids={"root"},
        root_spell_ids=set(),
        topologies={},
    )
    _AdjacencyBuilderStub.next_snapshot = snapshot
    _RootBlueprintBuilderStub.next_blueprints = {}
    monkeypatch.setattr(
        compiler_phase_5_module,
        "SpellSystemAdjacencyBuilder",
        _AdjacencyBuilderStub,
    )
    monkeypatch.setattr(
        compiler_phase_5_module,
        "SpellSystemRootBlueprintBuilder",
        _RootBlueprintBuilderStub,
    )

    with pytest.raises(RuntimeError, match="boom"):
        phase.run_frame_wide(
            root_spell,
            root_spell._compiler_artifact,
            spellbook,
            states,
            "cid",
        )

    assert root_spell._compiler_artifact._spell_system_index_phase5 is not None
