"""Unit tests for current-surface compiler phase 5 local scoping behavior."""

from types import SimpleNamespace
from typing import Any, Dict, Optional

import pytest

import melder.aether.spellbook.spell_compiler.phases.compiler_phase_5 as compiler_phase_5_module
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
        "requires_spellspace_request",
    ]

    def __init__(
            self,
            root_spell_id: str,
            *,
            requires_spellspace_request: bool = False,
    ) -> None:
        """Store the root spell id and spellspace-request flag."""
        self.root_spell_id = root_spell_id
        self.requires_spellspace_request = requires_spellspace_request


class _AdjacencyBuilderStub:
    """Record Phase 5 adjacency-builder calls and return one snapshot."""

    next_snapshot: Any = None

    def build(self, _spell_system_states: Any) -> Any:
        """Return the configured snapshot."""
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


def _make_spellbook_stub(*, spell_system_states: _SpellSystemStatesStub) -> Any:
    """Build a minimal spellbook stub for local phase 5 tests."""
    return SimpleNamespace(
        _spell_id_pool={},
        _spells_by_id={},
        _spell_system_states=spell_system_states,
        _aether=None,
        _aetheric_frame_name="frame",
    )


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


def test_collect_local_scope_spell_ids_returns_dependency_closure() -> None:
    """Phase 5 local scoping should follow the dependency closure from the root."""
    phase = CompilerPhase5()
    snapshot = SimpleNamespace(
        all_spell_ids=set(["root", "dep1", "dep2", "leaf"]),
        dependencies={
            "root": set(["dep1", "dep2"]),
            "dep1": set(["leaf"]),
            "dep2": set(["outside"]),
            "leaf": set(),
        },
    )

    assert phase._collect_local_scope_spell_ids(
        root_spell_id="root",
        snapshot=snapshot,
    ) == set(["root", "dep1", "dep2", "leaf"])
    assert phase._collect_local_scope_spell_ids(
        root_spell_id="missing",
        snapshot=snapshot,
    ) == set()


def test_filter_snapshot_to_visible_spells_recomputes_roots_and_topologies() -> None:
    """Phase 5 local filtering should trim dependencies and recompute roots."""
    phase = CompilerPhase5()
    snapshot = SimpleNamespace(
        dependencies={
            "root": set(["dep", "hidden"]),
            "dep": set(),
            "hidden": set(["dep"]),
        },
        topologies={
            "root": "top-root",
            "dep": "top-dep",
            "hidden": "top-hidden",
        },
    )

    filtered = phase._filter_snapshot_to_visible_spells(
        snapshot=snapshot,
        visible_spell_ids=set(["root", "dep"]),
    )

    assert filtered.dependencies == {
        "root": set(["dep"]),
        "dep": set(),
    }
    assert filtered.reverse_dependencies == {
        "dep": set(["root"]),
    }
    assert filtered.root_spell_ids == set(["root"])
    assert filtered.topologies == {
        "root": "top-root",
        "dep": "top-dep",
    }
    assert filtered.all_spell_ids == set(["root", "dep"])


def test_build_system_index_for_snapshot_populates_spell_metadata() -> None:
    """Phase 5 local system-index build should preserve lineage and conduit metadata."""
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
    snapshot = SimpleNamespace(
        dependencies={
            "root": set(["dep"]),
            "dep": set(),
        },
        root_spell_ids=set(["root"]),
    )

    system_index, spellspace_scoped_spell_ids = phase._build_system_index_for_snapshot(
        snapshot=snapshot,
        spell_lookup=spellbook._spell_id_pool,
        spell_system_states=states,
    )

    root_node = system_index.get_node("root")
    dep_node = system_index.get_node("dep")
    assert root_node is not None
    assert dep_node is not None
    assert root_node.lineage_id == "lineage-root"
    assert dep_node.lineage_id == "lineage-dep"
    assert root_node.dependencies == set(["dep"])
    assert dep_node.dependencies == set()
    assert root_node.is_root is True
    assert dep_node.is_root is False
    assert root_node.conduit_id == "conduit-root"
    assert dep_node.conduit_id == "conduit-dep"
    assert spellspace_scoped_spell_ids == set()


def test_attach_phase5_artifacts_for_snapshot_scopes_spell_updates(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Phase 5 local attachment should update only scoped spells."""
    phase = CompilerPhase5()
    states = _SpellSystemStatesStub([_SpellStateStub("root", "lineage-root")])
    spellbook = _make_spellbook_stub(spell_system_states=states)
    root_spell = _make_spell_stub(
        "root",
        spellbook=spellbook,
        spell_system_states=states,
    )
    dep_spell = _make_spell_stub(
        "dep",
        spellbook=spellbook,
        spell_system_states=states,
    )
    existing_spell = _make_spell_stub(
        "existing",
        spellbook=spellbook,
        spell_system_states=states,
        is_existing_creation=True,
    )
    outside_spell = _make_spell_stub(
        "outside",
        spellbook=spellbook,
        spell_system_states=states,
    )
    captured = _patch_ir_exports(monkeypatch)
    system_index = compiler_phase_5_module.SpellSystemIndex()
    root_blueprint = _RootBlueprintStub("root")
    dep_blueprint = _RootBlueprintStub("dep")
    _RootBlueprintBuilderStub.next_blueprints = {
        "root": root_blueprint,
        "dep": dep_blueprint,
    }
    _RootBlueprintBuilderStub.next_fallback_blueprint = dep_blueprint
    root_builder = _RootBlueprintBuilderStub()
    snapshot = SimpleNamespace(all_spell_ids=set(["root", "dep", "existing"]))

    phase._attach_phase5_artifacts_for_snapshot(
        snapshot=snapshot,
        root_blueprints={"root": root_blueprint},
        system_index=system_index,
        spell_lookup=spellbook._spell_id_pool,
        root_builder=root_builder,
    )

    assert root_spell._compiler_artifact._spell_system_index_phase5 is system_index
    assert dep_spell._compiler_artifact._spell_system_index_phase5 is system_index
    assert existing_spell._compiler_artifact._spell_system_index_phase5 is system_index
    assert root_spell._compiler_artifact._root_blueprint_phase5 is root_blueprint
    assert dep_spell._compiler_artifact._root_blueprint_phase5 is dep_blueprint
    assert existing_spell._compiler_artifact._root_blueprint_phase5 is None
    assert outside_spell._compiler_artifact._root_blueprint_phase5 is None
    assert root_builder.build_blueprint_for_spell_id_calls == [("dep", snapshot)]
    # Eager phase2_5 IR capture removed (write-only snapshot).
    assert captured["capture"] == []


def test_run_local_scopes_to_dependency_closure(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Phase 5 local entrypoint should only materialize the target dependency closure."""
    phase = CompilerPhase5()
    states = _SpellSystemStatesStub(
        [
            _SpellStateStub("root", "lineage-root"),
            _SpellStateStub("dep", "lineage-dep"),
            _SpellStateStub("outside", "lineage-outside"),
        ]
    )
    spellbook = _make_spellbook_stub(spell_system_states=states)
    root_spell = _make_spell_stub(
        "root",
        spellbook=spellbook,
        spell_system_states=states,
    )
    dep_spell = _make_spell_stub(
        "dep",
        spellbook=spellbook,
        spell_system_states=states,
    )
    outside_spell = _make_spell_stub(
        "outside",
        spellbook=spellbook,
        spell_system_states=states,
    )
    captured = _patch_ir_exports(monkeypatch)
    full_snapshot = SpellSystemAdjacencySnapshot(
        dependencies={
            "root": set(["dep"]),
            "dep": set(),
            "outside": set(),
        },
        reverse_dependencies={
            "dep": set(["root"]),
        },
        all_spell_ids=set(["root", "dep", "outside"]),
        root_spell_ids=set(["root", "outside"]),
        topologies={
            "root": "top-root",
            "dep": "top-dep",
            "outside": "top-outside",
        },
    )
    _AdjacencyBuilderStub.next_snapshot = full_snapshot
    _RootBlueprintBuilderStub.next_blueprints = {
        "root": _RootBlueprintStub("root"),
    }
    _RootBlueprintBuilderStub.next_fallback_blueprint = _RootBlueprintStub("dep")
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

    phase.run_local(
        root_spell,
        root_spell._compiler_artifact,
        spellbook,
        states,
        "cid",
    )

    scoped_blueprints = root_spell._compiler_artifact._entire_dag_blueprint_phase5
    assert scoped_blueprints is not None
    assert set(scoped_blueprints.keys()) == set(["root"])
    index = root_spell._compiler_artifact._spell_system_index_phase5
    assert index is not None
    assert index.get_node("root") is not None
    assert index.get_node("dep") is not None
    assert index.get_node("outside") is None
    assert root_spell._compiler_artifact._root_blueprint_phase5 is not None
    assert dep_spell._compiler_artifact._root_blueprint_phase5 is not None
    assert outside_spell._compiler_artifact._root_blueprint_phase5 is None
    # Eager phase2_5 IR capture removed (write-only snapshot).
    assert captured["capture"] == []
