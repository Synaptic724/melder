import pytest
from unittest.mock import MagicMock, call
from melder.aether.dev_ops.spell_system_states.spell_system_states import SpellSystemStates
from melder.aether.dev_ops.spell_system_states.spell_system_state import SpellSystemState
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.utilities.interfaces.interfaces import ISpellIndex, ISpell

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
    index = MagicMock(spec=ISpellIndex)
    index.id = "idx-1"
    index.current = "spell-1"
    return index

@pytest.fixture
def mock_spell():
    return MagicMock(spec=ISpell)

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

def test_register_lineage_creates_new(states_manager, mock_spell_index, mock_spell):
    """
    Verify registering a new lineage creates a `SpellSystemState`.

    Contract:
    - A new `SpellSystemState` object is created and returned.
    - The state is indexed by lineage ID and current spell version ID.
    - The lineage is marked dirty upon registration.
    """
    state = states_manager.register_lineage(mock_spell_index, mock_spell)
    
    assert isinstance(state, SpellSystemState)
    assert state.spell_index_id == "idx-1"
    assert state.current_spell_id == "spell-1"
    
    # Check indexes
    assert states_manager.get_by_index_id("idx-1") is state
    assert states_manager.get_by_spell_id("spell-1") is state
    
    # Check dirty tracking
    dirty = states_manager.consume_dirty_lineages()
    assert "idx-1" in dirty

def test_register_lineage_updates_existing(states_manager, mock_spell_index, mock_spell):
    states_manager.register_lineage(mock_spell_index, mock_spell)
    
    # Update index current
    mock_spell_index.current = "spell-2"
    
    state = states_manager.register_lineage(mock_spell_index, mock_spell)
    assert state.current_spell_id == "spell-2"
    assert states_manager.get_by_spell_id("spell-2") is state

def test_register_validation(states_manager, mock_spell):
    with pytest.raises(ValueError):
        states_manager.register_lineage(None, mock_spell)

# ----------------------------------------------------------------------
# 2.5. Unregistration
# ----------------------------------------------------------------------

def test_unregister_lineage_triggers_risk_manager(
    states_manager: SpellSystemStates,
    mock_spell_index: ISpellIndex,
    mock_spell: ISpell,
) -> None:
    """
    Verify unregister_lineage notifies RiskManager.

    Contract:
    - register_lineage notifies with SpellValidity.gated.
    - unregister_lineage notifies with SpellValidity.cleaned.
    """
    risk_manager = MagicMock()
    states_manager.set_risk_manager(risk_manager)

    states_manager.register_lineage(mock_spell_index, mock_spell)
    states_manager.unregister_lineage(mock_spell_index)

    calls = risk_manager.on_structural_validity_change.call_args_list
    assert calls[0] == call("idx-1", SpellValidity.gated)
    assert calls[-1] == call("idx-1", SpellValidity.cleaned)
    assert len(calls) == 2

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
    states_manager.register_lineage(mock_spell_index, mock_spell)
    
    # Register a dependency (so we can check reverse edges)
    dep_index = MagicMock(spec=ISpellIndex, id="idx-dep", current="spell-dep")
    states_manager.register_lineage(dep_index, mock_spell)
    
    # Consume dirty to clear initial
    states_manager.consume_dirty_lineages()
    
    # Update dependencies: main -> dep
    states_manager.update_dependencies(mock_spell_index, ["spell-dep"])
    
    # Verify main has dep
    main_state = states_manager.get_by_index_id("idx-1")
    assert "spell-dep" in main_state.direct_dependencies
    
    # Verify dep knows about main (reverse edge uses lineage id)
    dep_state = states_manager.get_by_index_id("idx-dep")
    assert "idx-1" in dep_state.direct_dependents
    
    # Verify dirty
    assert "idx-1" in states_manager.consume_dirty_lineages()

def test_update_dependencies_removes_old(states_manager, mock_spell_index, mock_spell):
    # Setup: Main -> Dep1
    dep1 = MagicMock(spec=ISpellIndex, id="d1", current="s-d1")
    states_manager.register_lineage(dep1, mock_spell)
    states_manager.register_lineage(mock_spell_index, mock_spell)
    states_manager.update_dependencies(mock_spell_index, ["s-d1"])
    
    # Setup: New: Main -> Dep2 (removes Dep1)
    dep2 = MagicMock(spec=ISpellIndex, id="d2", current="s-d2")
    states_manager.register_lineage(dep2, mock_spell)
    
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
    idx_a = MagicMock(spec=ISpellIndex, id="A", current="s-A")
    idx_b = MagicMock(spec=ISpellIndex, id="B", current="s-B")
    idx_c = MagicMock(spec=ISpellIndex, id="C", current="s-C")
    
    # Register
    states_manager.register_lineage(idx_a, mock_spell)
    states_manager.register_lineage(idx_b, mock_spell)
    states_manager.register_lineage(idx_c, mock_spell)
    
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
    dirty = states_manager.consume_dirty_lineages()
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
    states_manager.register_lineage(mock_spell_index, mock_spell)
    states_manager.cleanup()
    
    assert states_manager._cleaned
    assert states_manager._states_by_index_id is None
    assert states_manager._frame is None
    
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
    states_manager.register_lineage(mock_spell_index, mock_spell)
    states = states_manager.iter_states()
    assert len(states) == 1
    assert states[0].spell_index_id == "idx-1"
