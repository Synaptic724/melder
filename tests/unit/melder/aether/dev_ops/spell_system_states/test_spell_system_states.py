import pytest
from unittest.mock import MagicMock, call
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import SpellSystemStates
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_state import SpellSystemState
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state import SpellState
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import (
    SpellLocalTopology,
    SpellSocketDescriptor,
)
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.spell import Spell

# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------

@pytest.fixture
def mock_frame():
    return MagicMock()

@pytest.fixture
def states_manager(mock_frame):
    return SpellSystemStates(mock_frame)

@pytest.fixture
def mock_spell_index():
    index = MagicMock(spec=SpellIndex)
    index.id = "idx-1"
    index.current = "spell-1"
    return index

@pytest.fixture
def mock_spell():
    return MagicMock(spec=Spell)


def _build_owned_spell(spellbook_id: str = "book-1") -> Spell:
    """
    Create a spell double whose `_spellbook` carries a concrete owner id.

    Contract:
    - `SpellSystemStates._resolve_spellbook_id(...)` can read `_spellbook._id`.
    - The returned mock still behaves like a `Spell` boundary object.
    """
    spell = MagicMock(spec=Spell)
    spell._spellbook = MagicMock()
    spell._spellbook._id = spellbook_id
    return spell


def _attach_index_owner(index: SpellIndex, spell: Spell) -> SpellIndex:
    """
    Mirror the live Spellbook bind path by stamping owner references onto the index.
    """
    index._owner_spellbook = spell._spellbook
    index._owner_spell = spell
    return index


def _build_topology(
    spell_id: str,
    *,
    collection_frame_key: str = "frame-a",
    contract_key: tuple[str, str] = ("iface", "primary"),
) -> SpellLocalTopology:
    """
    Build a local topology with one collection socket and one contract socket.

    Contract:
    - The NORMAL collection socket populates the collection index.
    - The SPELL_CONTRACT socket populates the contract index.
    """
    return SpellLocalTopology(
        spell_id=spell_id,
        sockets=(
            SpellSocketDescriptor(
                spell_id=spell_id,
                param_name="collection_dep",
                position=0,
                socket_kind=SocketKind.NORMAL,
                is_collection=True,
                is_optional=False,
                target_spell_ids=("dep-1",),
                dependency_key=(collection_frame_key, "__default__"),
            ),
            SpellSocketDescriptor(
                spell_id=spell_id,
                param_name="contract_dep",
                position=1,
                socket_kind=SocketKind.SPELL_CONTRACT,
                is_collection=False,
                is_optional=False,
                target_spell_ids=(),
                contract_key=contract_key,
            ),
        ),
    )

# ----------------------------------------------------------------------
# 1. Initialization
# ----------------------------------------------------------------------

def test_init_success(states_manager, mock_frame):
    assert states_manager._frame is mock_frame
    assert len(states_manager._states_by_index_id) == 0

def test_init_validation():
    with pytest.raises(ValueError):
        SpellSystemStates(None)

# ----------------------------------------------------------------------
# 2. Registration & Lookup
# ----------------------------------------------------------------------

def test_register_index_creates_new(states_manager, mock_spell_index, mock_spell):
    """
    Verify registering a new lineage creates a `SpellSystemState`.

    Contract:
    - A new `SpellSystemState` object is created and returned.
    - The state is indexed by lineage ID and current spell version ID.
    - The lineage is marked dirty upon registration.
    """
    state = states_manager.register_index(mock_spell_index)
    
    assert isinstance(state, SpellSystemState)
    assert state.spell_index_id == "idx-1"
    assert state.current_spell_id == "spell-1"
    
    # Check indexes
    assert states_manager.get_by_index_id("idx-1") is state
    assert states_manager.get_by_spell_id("spell-1") is state
    
    # Check dirty tracking
    dirty = states_manager.consume_dirty_indexes()
    assert "idx-1" in dirty

def test_register_index_updates_existing(states_manager, mock_spell_index, mock_spell):
    states_manager.register_index(mock_spell_index)
    
    # Update index current
    mock_spell_index.current = "spell-2"
    
    state = states_manager.register_index(mock_spell_index)
    assert state.current_spell_id == "spell-2"
    assert states_manager.get_by_spell_id("spell-2") is state

def test_register_validation(states_manager, mock_spell):
    with pytest.raises(ValueError):
        states_manager.register_index(None)

# ----------------------------------------------------------------------
# 2.5. Unregistration
# ----------------------------------------------------------------------

def test_unregister_index_triggers_risk_manager(
    states_manager: SpellSystemStates,
    mock_spell_index: SpellIndex,
    mock_spell: Spell,
) -> None:
    """
    Verify unregister_index notifies RiskManager.

    Contract:
    - register_index notifies with SpellValidity.gated.
    - unregister_index notifies with SpellValidity.cleaned.
    """
    risk_manager = MagicMock()
    states_manager.set_risk_manager(risk_manager)

    states_manager.register_index(mock_spell_index)
    states_manager.unregister_index(mock_spell_index)

    calls = risk_manager.on_structural_validity_change.call_args_list
    assert calls[0] == call("idx-1", SpellValidity.gated)
    assert calls[-1] == call("idx-1", SpellValidity.cleaned)
    assert len(calls) == 2

def test_unregister_index_marks_dependents_gated(
    states_manager: SpellSystemStates,
    mock_spell: Spell,
) -> None:
    """
    Verify unregister_index gates dependent lineages.

    Contract:
    - Direct dependents are marked gated/dirty when a lineage is unregistered.
    - Impacted dependents receive the impacted_by_dependency flag.
    """
    idx_a = MagicMock(spec=SpellIndex, id="idx-a", current="spell-a")
    idx_b = MagicMock(spec=SpellIndex, id="idx-b", current="spell-b")

    states_manager.register_index(idx_a)
    states_manager.register_index(idx_b)
    states_manager.update_dependencies(idx_b, ["spell-a"])
    states_manager.consume_dirty_indexes()

    states_manager.unregister_index(idx_a)

    state_b = states_manager.get_by_index_id("idx-b")
    assert state_b.validity is SpellValidity.gated
    assert SpellState.impacted_by_dependency in state_b.flags
    assert "idx-b" in states_manager.consume_dirty_indexes()

# ----------------------------------------------------------------------
# 3. Dependency Wiring
# ----------------------------------------------------------------------

def test_update_dependencies(states_manager, mock_spell_index, mock_spell):
    """
    Verify `update_dependencies` wires the graph correctly.

    Contract:
    - Direct dependencies are updated on the subject lineage.
    - Reverse edges (dependents) are updated on the referenced lineages.
    - The subject lineage is marked dirty.
    """
    # Register main spell
    states_manager.register_index(mock_spell_index)
    
    # Register a dependency (so we can check reverse edges)
    dep_index = MagicMock(spec=SpellIndex, id="idx-dep", current="spell-dep")
    states_manager.register_index(dep_index)
    
    # Consume dirty to clear initial
    states_manager.consume_dirty_indexes()
    
    # Update dependencies: main -> dep
    states_manager.update_dependencies(mock_spell_index, ["spell-dep"])
    
    # Verify main has dep
    main_state = states_manager.get_by_index_id("idx-1")
    assert "spell-dep" in main_state.direct_dependencies
    
    # Verify dep knows about main (reverse edge uses lineage id)
    dep_state = states_manager.get_by_index_id("idx-dep")
    assert "idx-1" in dep_state.direct_dependents
    
    # Verify dirty
    assert "idx-1" in states_manager.consume_dirty_indexes()

def test_update_dependencies_removes_old(states_manager, mock_spell_index, mock_spell):
    # Setup: Main -> Dep1
    dep1 = MagicMock(spec=SpellIndex, id="d1", current="s-d1")
    states_manager.register_index(dep1)
    states_manager.register_index(mock_spell_index)
    states_manager.update_dependencies(mock_spell_index, ["s-d1"])
    
    # Setup: New: Main -> Dep2 (removes Dep1)
    dep2 = MagicMock(spec=SpellIndex, id="d2", current="s-d2")
    states_manager.register_index(dep2)
    
    states_manager.update_dependencies(mock_spell_index, ["s-d2"])
    
    main_state = states_manager.get_by_index_id("idx-1")
    assert "s-d1" not in main_state.direct_dependencies
    assert "s-d2" in main_state.direct_dependencies
    
    # Verify reverse edges cleaned
    d1_state = states_manager.get_by_index_id("d1")
    assert "idx-1" not in d1_state.direct_dependents

# ----------------------------------------------------------------------
# 4. Impact Closure
# ----------------------------------------------------------------------

def test_compute_impact_closure(states_manager, mock_spell):
    """
    Verify transitive impact calculation.

    Contract:
    - Starting from a root change, traverse reverse edges to find all dependents.
    - Mark all reachable nodes as `transitively_dirty` (unless they are the root itself).
    - Return the full set of impacted lineage IDs.
    - All impacted IDs are added to the dirty list.
    """
    # A -> B -> C
    # Define indexes
    idx_a = MagicMock(spec=SpellIndex, id="A", current="s-A")
    idx_b = MagicMock(spec=SpellIndex, id="B", current="s-B")
    idx_c = MagicMock(spec=SpellIndex, id="C", current="s-C")
    
    # Register
    states_manager.register_index(idx_a)
    states_manager.register_index(idx_b)
    states_manager.register_index(idx_c)
    
    # Wire dependencies: B depends on A, C depends on B
    # A <- B <- C
    states_manager.update_dependencies(idx_b, ["s-A"])
    states_manager.update_dependencies(idx_c, ["s-B"])
    
    # Change A
    impacted = states_manager.compute_impact_closure(["A"])
    
    assert "A" in impacted
    assert "B" in impacted
    assert "C" in impacted
    
    # Verify dirty state logic
    dirty = states_manager.consume_dirty_indexes()
    assert set(dirty) == {"A", "B", "C"}
    
    state_c = states_manager.get_by_index_id("C")
    assert state_c.transitively_dirty

# ----------------------------------------------------------------------
# 5. Cleanup
# ----------------------------------------------------------------------

def test_cleanup(states_manager, mock_spell_index, mock_spell):
    """
    Verify `cleanup` properly tears down the registry.

    Contract:
    - Internal indexes are cleared/nulled.
    - Reference to the frame is dropped.
    - Accessors raise RuntimeError after cleanup.
    """
    states_manager.register_index(mock_spell_index)
    states_manager.cleanup()
    
    assert states_manager._cleaned
    assert not hasattr(states_manager, '_states_by_index_id')
    assert not hasattr(states_manager, '_frame')
    
    with pytest.raises(RuntimeError):
        states_manager.get_by_index_id("idx-1")

def test_cleanup_idempotent(states_manager):
    states_manager.cleanup()
    states_manager.cleanup()

# ----------------------------------------------------------------------
# 6. Introspection
# ----------------------------------------------------------------------

def test_iter_states(states_manager, mock_spell_index, mock_spell):
    """
    Verify `iter_states` returns a safe snapshot list of all states.
    """
    states_manager.register_index(mock_spell_index)
    states = states_manager.iter_states()
    assert len(states) == 1
    assert states[0].spell_index_id == "idx-1"


# ----------------------------------------------------------------------
# 7. Per-Conduit Resolution State Wrappers
# ----------------------------------------------------------------------

def test_conduit_resolution_wrappers_track_state_and_cleanup(
    states_manager: SpellSystemStates,
) -> None:
    """
    Verify conduit-resolution wrappers expose the real resolution-state contract.

    Contract:
    - Per-conduit state is created once and reused.
    - Spell/root validity updates, diagnostics, and dirty-state clearing flow
      through the wrapper methods.
    - Dropping the conduit state cleans the owned state object.
    """
    risk_manager = MagicMock()
    states_manager.set_risk_manager(risk_manager)

    assert states_manager.get_conduit_resolution_state("conduit-1") is None

    state = states_manager.get_or_create_conduit_resolution_state("conduit-1")
    other_state = states_manager.get_or_create_conduit_resolution_state("conduit-2")

    states_manager.set_conduit_spell_validity(
        "conduit-1",
        "spell-1",
        SpellValidity.valid,
        change_reason=SpellStateChangeReason.dependencies_changed,
    )
    states_manager.bulk_set_conduit_spell_validity(
        "conduit-1",
        {"spell-2": SpellValidity.gated},
        change_reason=SpellStateChangeReason.structure_changed,
    )
    states_manager.set_conduit_root_validity(
        "conduit-1",
        "root-1",
        SpellValidity.gated,
        change_reason=SpellStateChangeReason.structure_changed,
    )
    states_manager.bulk_set_conduit_root_validity(
        "conduit-1",
        {"root-2": SpellValidity.valid},
        change_reason=SpellStateChangeReason.dependencies_changed,
    )

    diagnostic = SystemDiagnostic(
        code="D-1",
        message="broken root",
        severity=SystemDiagnosticSeverity.WARNING,
        root_id="root-1",
        source="unit-test",
    )
    states_manager.record_conduit_diagnostics("conduit-1", [diagnostic])

    snapshot = list(states_manager.iter_conduit_resolution_states())
    assert state in snapshot
    assert other_state in snapshot
    assert state.get_spell_validity("spell-1") is SpellValidity.valid
    assert state.get_spell_validity("spell-2") is SpellValidity.gated
    assert state.get_root_validity("root-1") is SpellValidity.gated
    assert state.get_root_validity("root-2") is SpellValidity.valid
    diagnostics = state.list_diagnostics()
    assert len(diagnostics) == 1
    assert diagnostics[0].code == "D-1"
    assert diagnostics[0] is not diagnostic
    assert state.has_warnings() is True

    states_manager.clear_conduit_diagnostics("conduit-1")
    assert state.list_diagnostics() == []

    states_manager.mark_conduit_dirty(
        "conduit-1",
        change_reason=SpellStateChangeReason.dependencies_changed,
    )
    assert state.is_dirty() is True
    states_manager.clear_conduit_dirty("conduit-1", 123.0)
    assert state.is_dirty() is False
    assert state.last_validated_at() == 123.0

    calls = risk_manager.on_resolution_validity_change.call_args_list
    assert call("conduit-1", "spell-1", SpellValidity.valid) in calls
    assert call("conduit-1", "spell-2", SpellValidity.gated) in calls
    assert call("conduit-1", "root-1", SpellValidity.gated) in calls
    assert call("conduit-1", "root-2", SpellValidity.valid) in calls

    states_manager.drop_conduit_resolution_state("conduit-1")
    assert states_manager.get_conduit_resolution_state("conduit-1") is None
    assert state.cleaned is True
    assert list(states_manager.iter_conduit_resolution_states()) == [other_state]


def test_conduit_resolution_state_guards_invalid_ids_and_cleaned_manager(
    states_manager: SpellSystemStates,
) -> None:
    """
    Verify conduit-resolution state helpers fail fast on invalid access.

    Contract:
    - Empty conduit ids do not create state.
    - A cleaned manager rejects state creation through its public API.
    """
    assert states_manager.get_conduit_resolution_state("") is None

    with pytest.raises(ValueError):
        states_manager.get_or_create_conduit_resolution_state("")

    states_manager.cleanup()

    with pytest.raises(RuntimeError):
        states_manager.get_or_create_conduit_resolution_state("conduit-1")


# ----------------------------------------------------------------------
# 8. Topology Indexing and Dirty Propagation
# ----------------------------------------------------------------------

def test_register_local_topology_builds_collection_and_contract_indexes(
    states_manager: SpellSystemStates,
) -> None:
    """
    Verify local-topology registration feeds both dependency invalidation paths.

    Contract:
    - Registering a topology stores it by current spell id.
    - Collection frame keys and contract keys are indexed under the owning
      spellbook.
    - Dirty-mark helpers gate the indexed lineage with the expected reasons.
    """
    spell = _build_owned_spell("book-1")
    index = SpellIndex("spell-topology-1")
    _attach_index_owner(index, spell)
    states_manager.register_index(index)
    states_manager.consume_dirty_indexes()

    topology = _build_topology(index.current)
    states_manager.register_local_topology(index, topology)

    assert states_manager.get_local_topology(index) is topology
    assert states_manager.get_local_topology_by_id(index.current) is topology

    impacted = states_manager.mark_collection_dependents_dirty(
        spellbook_id="book-1",
        frame_keys=["frame-a"],
    )
    assert impacted == {index.id}
    state = states_manager.get_by_index_id(index.id)
    assert state is not None
    assert state.change_reason is SpellStateChangeReason.dependencies_changed
    assert index.id in states_manager.consume_dirty_indexes()

    state.clear_dirty(last_validated_at=1.0)
    states_manager.consume_dirty_indexes()

    impacted = states_manager.mark_contract_dependents_dirty(
        spellbook_id="book-1",
        contract_keys=[("iface", "primary")],
    )
    assert impacted == {index.id}
    assert state.validity is SpellValidity.gated
    assert state.change_reason is SpellStateChangeReason.contract_unvalidated
    assert SpellState.contract_unvalidated in state.flags
    assert index.id in states_manager.consume_dirty_indexes()


def test_register_local_topology_replaces_stale_collection_and_contract_keys(
    states_manager: SpellSystemStates,
) -> None:
    """
    Verify replacing a topology removes stale index entries.

    Contract:
    - Re-registering the same lineage replaces collection and contract keys.
    - Dirty propagation only follows the currently registered keys.
    """
    spell = _build_owned_spell("book-1")
    index = SpellIndex("spell-topology-replace")
    _attach_index_owner(index, spell)
    states_manager.register_index(index)
    states_manager.consume_dirty_indexes()

    topology_a = _build_topology(
        index.current,
        collection_frame_key="frame-a",
        contract_key=("iface", "primary"),
    )
    topology_b = _build_topology(
        index.current,
        collection_frame_key="frame-b",
        contract_key=("iface", "secondary"),
    )

    states_manager.register_local_topology(index, topology_a)
    states_manager.register_local_topology(index, topology_b)

    assert states_manager.mark_collection_dependents_dirty(
        spellbook_id="book-1",
        frame_keys=["frame-a"],
    ) == set()
    assert states_manager.mark_contract_dependents_dirty(
        spellbook_id="book-1",
        contract_keys=[("iface", "primary")],
    ) == set()

    impacted_collection = states_manager.mark_collection_dependents_dirty(
        spellbook_id="book-1",
        frame_keys=["frame-b"],
    )
    impacted_contract = states_manager.mark_contract_dependents_dirty(
        spellbook_id="book-1",
        contract_keys=[("iface", "secondary")],
    )

    assert impacted_collection == {index.id}
    assert impacted_contract == {index.id}


def test_mark_contract_dependents_dirty_marks_all_keys_when_unspecified(
    states_manager: SpellSystemStates,
) -> None:
    """
    Verify contract invalidation without explicit keys fans out across the book.

    Contract:
    - Passing `contract_keys=None` marks all contract-indexed lineages in the
      owning spellbook dirty.
    """
    spell = _build_owned_spell("book-1")
    first_index = SpellIndex("spell-contract-a")
    second_index = SpellIndex("spell-contract-b")

    _attach_index_owner(first_index, spell)
    _attach_index_owner(second_index, spell)
    states_manager.register_index(first_index)
    states_manager.register_index(second_index)
    states_manager.consume_dirty_indexes()

    first_topology = _build_topology(
        first_index.current,
        collection_frame_key="frame-a",
        contract_key=("iface", "alpha"),
    )
    second_topology = _build_topology(
        second_index.current,
        collection_frame_key="frame-b",
        contract_key=("iface", "beta"),
    )

    states_manager.register_local_topology(first_index, first_topology)
    states_manager.register_local_topology(second_index, second_topology)

    impacted = states_manager.mark_contract_dependents_dirty(spellbook_id="book-1")

    assert impacted == {first_index.id, second_index.id}
    dirty = set(states_manager.consume_dirty_indexes())
    assert dirty == {first_index.id, second_index.id}


def test_cleanup_cascades_to_resolution_states_topologies_and_indexes(
    states_manager: SpellSystemStates,
) -> None:
    """
    Verify cleanup tears down all owned control-plane children and indexes.

    Contract:
    - Cleanup propagates to stored topology and conduit-resolution children.
    - Registry/index structures are nulled after teardown.
    - Cleanup remains safe for later fail-fast access.
    """
    spell = _build_owned_spell("book-cleanup")
    index = SpellIndex("spell-cleanup")
    _attach_index_owner(index, spell)
    states_manager.register_index(index)
    topology = _build_topology(index.current)
    states_manager.register_local_topology(index, topology)

    states_manager.set_conduit_spell_validity(
        "conduit-cleanup",
        "spell-cleanup",
        SpellValidity.valid,
    )
    conduit_state = states_manager.get_conduit_resolution_state("conduit-cleanup")
    assert conduit_state is not None

    states_manager.cleanup()

    assert topology.cleaned is True
    assert conduit_state.cleaned is True
    assert not hasattr(states_manager, '_local_topologies')
    assert not hasattr(states_manager, '_resolution_by_conduit_id')
    assert not hasattr(states_manager, '_collection_dependents_by_spellbook')
    assert not hasattr(states_manager, '_collection_frames_by_index')
    assert not hasattr(states_manager, '_contract_dependents_by_spellbook')
    assert not hasattr(states_manager, '_contract_keys_by_index')
    assert not hasattr(states_manager, '_index_owner_spellbook_id')
    assert not hasattr(states_manager, '_risk_manager')


def test_register_index_owner_change_rebuilds_topology_indexes_under_new_book(
    states_manager: SpellSystemStates,
) -> None:
    """
    Verify owner changes remove stale topology indexes before re-registration.

    Contract:
    - Rebinding a lineage to a different Spellbook removes stale old-book
      collection and contract entries.
    - Re-registering topology under the new owner restores dirty propagation.
    """
    first_spell = _build_owned_spell("book-a")
    second_spell = _build_owned_spell("book-b")
    index = SpellIndex("spell-owner-change")

    _attach_index_owner(index, first_spell)
    states_manager.register_index(index)
    topology = _build_topology(index.current)
    states_manager.register_local_topology(index, topology)
    states_manager.consume_dirty_indexes()

    _attach_index_owner(index, second_spell)
    states_manager.register_index(index)

    assert states_manager.mark_collection_dependents_dirty(
        spellbook_id="book-a",
        frame_keys=["frame-a"],
    ) == set()
    assert states_manager.mark_contract_dependents_dirty(
        spellbook_id="book-a",
        contract_keys=[("iface", "primary")],
    ) == set()

    states_manager.register_local_topology(index, topology)

    assert states_manager.mark_collection_dependents_dirty(
        spellbook_id="book-b",
        frame_keys=["frame-a"],
    ) == {index.id}
    states_manager.consume_dirty_indexes()
    assert states_manager.mark_contract_dependents_dirty(
        spellbook_id="book-b",
        contract_keys=[("iface", "primary")],
    ) == {index.id}


def test_update_dependencies_creates_missing_lineage_state_on_first_use(
    states_manager: SpellSystemStates,
) -> None:
    """
    Verify dependency wiring can create a lineage state before registration.

    Contract:
    - update_dependencies creates the missing SpellSystemState on first use.
    - Reverse dependency edges are still wired for known dependencies.
    """
    root_index = SpellIndex("spell-late-root")
    dependency_index = SpellIndex("spell-late-dependency")

    _attach_index_owner(dependency_index, _build_owned_spell("book-1"))
    states_manager.register_index(dependency_index)
    states_manager.consume_dirty_indexes()

    states_manager.update_dependencies(root_index, [dependency_index.current])

    root_state = states_manager.get_by_index_id(root_index.id)
    dependency_state = states_manager.get_by_index_id(dependency_index.id)
    assert root_state is not None
    assert dependency_state is not None
    assert root_state.current_spell_id == root_index.current
    assert dependency_index.current in root_state.direct_dependencies
    assert root_index.id in dependency_state.direct_dependents
    assert root_index.id in states_manager.consume_dirty_indexes()


def test_mark_structural_change_creates_missing_lineage_state_on_first_use(
    states_manager: SpellSystemStates,
) -> None:
    """
    Verify structural invalidation can seed an unseen lineage.

    Contract:
    - mark_structural_change creates a missing state for the target lineage.
    - The seeded state is gated with the requested change reason.
    """
    index = SpellIndex("spell-structural-seed")

    states_manager.mark_structural_change(index)

    state = states_manager.get_by_index_id(index.id)
    assert state is not None
    assert state.current_spell_id == index.current
    assert state.validity is SpellValidity.gated
    assert state.change_reason is SpellStateChangeReason.structure_changed
    assert SpellState.structure_changed in state.flags
    assert index.id in states_manager.consume_dirty_indexes()


def test_set_risk_manager_propagates_to_existing_resolution_states(
    states_manager: SpellSystemStates,
) -> None:
    """
    Verify set_risk_manager updates states that already exist.

    Contract:
    - Existing conduit-resolution states receive the new risk manager.
    - Later validity changes still emit resolution-change callbacks.
    """
    states_manager.get_or_create_conduit_resolution_state("conduit-existing")
    risk_manager = MagicMock()

    states_manager.set_risk_manager(risk_manager)
    states_manager.set_conduit_spell_validity(
        "conduit-existing",
        "spell-risk",
        SpellValidity.valid,
    )

    risk_manager.on_resolution_validity_change.assert_called_once_with(
        "conduit-existing",
        "spell-risk",
        SpellValidity.valid,
    )


def test_unregister_index_removes_topology_indexes_and_reverse_edges(
    states_manager: SpellSystemStates,
) -> None:
    """
    Verify unregister_index detaches all owned topology and dependency state.

    Contract:
    - Local topology and spell-id indexes are removed with the lineage.
    - Collection/contract indexes no longer route dirtying for the removed
      lineage.
    - Reverse dependency edges are detached from remaining dependency states.
    """
    spell = _build_owned_spell("book-remove")
    root_index = SpellIndex("spell-remove-root")
    dependency_index = SpellIndex("spell-remove-dependency")

    _attach_index_owner(dependency_index, _build_owned_spell("book-remove"))
    _attach_index_owner(root_index, spell)
    states_manager.register_index(dependency_index)
    states_manager.register_index(root_index)
    states_manager.register_local_topology(root_index, _build_topology(root_index.current))
    states_manager.update_dependencies(root_index, [dependency_index.current])
    states_manager.consume_dirty_indexes()

    removed_state = states_manager.unregister_index(root_index)

    dependency_state = states_manager.get_by_index_id(dependency_index.id)
    assert removed_state is not None
    assert removed_state.cleaned is True
    assert states_manager.get_by_index_id(root_index.id) is None
    assert states_manager.get_by_spell_id(root_index.current) is None
    assert states_manager.get_local_topology_by_id(root_index.current) is None
    assert dependency_state is not None
    assert root_index.id not in dependency_state.direct_dependents
    assert states_manager.mark_collection_dependents_dirty(
        spellbook_id="book-remove",
        frame_keys=["frame-a"],
    ) == set()
    assert states_manager.mark_contract_dependents_dirty(
        spellbook_id="book-remove",
        contract_keys=[("iface", "primary")],
    ) == set()


def test_register_local_topology_ignores_irrelevant_socket_shapes(
    states_manager: SpellSystemStates,
) -> None:
    """
    Verify topology indexing only tracks collection NORMAL and SPELL_CONTRACT sockets.

    Contract:
    - Non-collection NORMAL sockets do not enter the collection index.
    - Collection sockets without dependency keys are ignored.
    - MUTATION_CONTRACT sockets do not enter the SpellContract index.
    """
    spell = _build_owned_spell("book-filter")
    index = SpellIndex("spell-filter")
    _attach_index_owner(index, spell)
    states_manager.register_index(index)
    states_manager.consume_dirty_indexes()

    topology = SpellLocalTopology(
        spell_id=index.current,
        sockets=(
            SpellSocketDescriptor(
                spell_id=index.current,
                param_name="plain_dep",
                position=0,
                socket_kind=SocketKind.NORMAL,
                is_collection=False,
                is_optional=False,
                target_spell_ids=("dep-a",),
                dependency_key=("ignored-frame", "__default__"),
            ),
            SpellSocketDescriptor(
                spell_id=index.current,
                param_name="collection_without_key",
                position=1,
                socket_kind=SocketKind.NORMAL,
                is_collection=True,
                is_optional=False,
                target_spell_ids=("dep-b",),
                dependency_key=None,
            ),
            SpellSocketDescriptor(
                spell_id=index.current,
                param_name="mutation_contract",
                position=2,
                socket_kind=SocketKind.MUTATION_CONTRACT,
                is_collection=False,
                is_optional=False,
                target_spell_ids=(),
                contract_key=("iface", "mutation"),
            ),
            SpellSocketDescriptor(
                spell_id=index.current,
                param_name="valid_collection",
                position=3,
                socket_kind=SocketKind.NORMAL,
                is_collection=True,
                is_optional=False,
                target_spell_ids=("dep-c",),
                dependency_key=("frame-valid", "__default__"),
            ),
            SpellSocketDescriptor(
                spell_id=index.current,
                param_name="valid_contract",
                position=4,
                socket_kind=SocketKind.SPELL_CONTRACT,
                is_collection=False,
                is_optional=False,
                target_spell_ids=(),
                contract_key=("iface", "valid"),
            ),
        ),
    )

    states_manager.register_local_topology(index, topology)

    assert states_manager.mark_collection_dependents_dirty(
        spellbook_id="book-filter",
        frame_keys=["ignored-frame"],
    ) == set()
    assert states_manager.mark_collection_dependents_dirty(
        spellbook_id="book-filter",
        frame_keys=["frame-valid"],
    ) == {index.id}
    states_manager.consume_dirty_indexes()
    assert states_manager.mark_contract_dependents_dirty(
        spellbook_id="book-filter",
        contract_keys=[("iface", "mutation")],
    ) == set()
    assert states_manager.mark_contract_dependents_dirty(
        spellbook_id="book-filter",
        contract_keys=[("iface", "valid")],
    ) == {index.id}


def test_cleanup_tolerates_child_cleanup_failures(
    states_manager: SpellSystemStates,
) -> None:
    """
    Verify cleanup remains best-effort when child cleanup hooks fail.

    Contract:
    - Failing topology or conduit-resolution cleanup does not abort manager
      teardown.
    - Index structures are still cleared and nulled.
    """
    states_manager._local_topologies["spell-fail"] = MagicMock(
        cleanup=MagicMock(side_effect=RuntimeError("topology cleanup failed"))
    )
    states_manager._resolution_by_conduit_id["conduit-fail"] = MagicMock(
        cleanup=MagicMock(side_effect=RuntimeError("resolution cleanup failed"))
    )

    states_manager.cleanup()

    assert not hasattr(states_manager, '_local_topologies')
    assert not hasattr(states_manager, '_resolution_by_conduit_id')
    assert not hasattr(states_manager, '_states_by_index_id')
    assert not hasattr(states_manager, '_dirty_indexes')


def test_lookup_and_topology_helpers_validate_public_inputs(
    states_manager: SpellSystemStates,
) -> None:
    """
    Verify public lookup and topology helpers enforce their input contracts.

    Contract:
    - Empty lookup ids return no state.
    - Topology registration and lookup reject missing required identifiers.
    """
    topology = _build_topology("spell-input-check")
    index = SpellIndex("spell-input-check")

    assert states_manager.get_by_index_id("") is None
    assert states_manager.get_by_spell_id("") is None
    assert states_manager.get_local_topology_by_id("spell-missing") is None

    with pytest.raises(ValueError):
        states_manager.update_dependencies(None, [])

    with pytest.raises(ValueError):
        states_manager.mark_structural_change(None)

    with pytest.raises(ValueError):
        states_manager.register_local_topology(None, topology)

    with pytest.raises(ValueError):
        states_manager.register_local_topology(index, None)

    with pytest.raises(ValueError):
        states_manager.get_local_topology(None)

    with pytest.raises(ValueError):
        states_manager.get_local_topology_by_id("")


def test_dirty_helpers_noop_for_empty_scope_or_missing_indexes(
    states_manager: SpellSystemStates,
) -> None:
    """
    Verify dirty helpers stay side-effect free when scope inputs are empty.

    Contract:
    - Missing spellbook ids, empty frame keys, and unknown books return empty
      impacted sets.
    - Contract invalidation behaves the same when scope is absent.
    """
    assert states_manager.mark_collection_dependents_dirty(
        spellbook_id="",
        frame_keys=["frame-a"],
    ) == set()
    assert states_manager.mark_collection_dependents_dirty(
        spellbook_id="book-missing",
        frame_keys=[],
    ) == set()
    assert states_manager.mark_collection_dependents_dirty(
        spellbook_id="book-missing",
        frame_keys=["frame-a"],
    ) == set()

    assert states_manager.mark_contract_dependents_dirty(
        spellbook_id="",
        contract_keys=[("iface", "primary")],
    ) == set()
    assert states_manager.mark_contract_dependents_dirty(
        spellbook_id="book-missing",
        contract_keys=[("iface", "primary")],
    ) == set()


def test_conduit_resolution_noop_helpers_ignore_missing_state(
    states_manager: SpellSystemStates,
) -> None:
    """
    Verify missing conduit-resolution entries stay non-throwing for noop helpers.

    Contract:
    - Clearing diagnostics, clearing dirty, and dropping state are safe when
      the conduit is unknown.
    """
    states_manager.clear_conduit_diagnostics("conduit-missing")
    states_manager.clear_conduit_dirty("conduit-missing", 11.0)
    states_manager.drop_conduit_resolution_state("conduit-missing")
    states_manager.drop_conduit_resolution_state("")

    assert list(states_manager.iter_conduit_resolution_states()) == []


def test_unregister_index_missing_state_clears_stale_spell_id_mapping(
    states_manager: SpellSystemStates,
) -> None:
    """
    Verify unregister_index clears a stale spell-id index even without state.

    Contract:
    - A missing lineage returns None.
    - A stale current spell-id entry is still removed.
    """
    index = SpellIndex("spell-stale")
    states_manager._states_by_spell_id[index.current] = MagicMock()

    removed_state = states_manager.unregister_index(index)

    assert removed_state is None
    assert states_manager.get_by_spell_id(index.current) is None

