from __future__ import annotations

from melder.aether.aetheric_frame import AethericFrame
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.system.spell_system_adjacency_builder import (
    SpellSystemAdjacencyBuilder,
)
from melder.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.spellbook.spell_crafter.system.spell_system_node import SpellSystemNode
from melder.spellbook.spell_crafter.system.spell_system_validation_system import (
    SpellSystemValidationSystem,
)
from melder.spellbook.spell_crafter.system.spell_system_root_blueprint_builder import (
    SpellSystemRootBlueprintBuilder,
)
from melder.spellbook.spell_crafter.system.validation.graph_consistency_strategy import (
    GraphConsistencyStrategy,
)
from melder.spellbook.spell_types.spell_types import SpellType
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity


def _register_lineage(states, spell_id: str) -> SpellIndex:
    """
    Purpose:
        Register a spell lineage into SpellSystemStates.
    Contract:
        - Returns a SpellIndex with current id set to spell_id.
        - Registers the lineage in the states registry.
    Args:
        states: SpellSystemStates registry.
        spell_id: Version id to register.
    Returns:
        SpellIndex: The created spell index.
    """
    index = SpellIndex(spell_id)
    states.register_lineage(index, object())
    return index


def _build_index(snapshot, states) -> SpellSystemIndex:
    """
    Purpose:
        Build a SpellSystemIndex using a snapshot and live states.
    Contract:
        - Lineage ids are sourced from SpellSystemStates when available.
        - Root flags follow snapshot.root_spell_ids.
    Args:
        snapshot: SpellSystemAdjacencySnapshot for dependency structure.
        states: SpellSystemStates for lineage lookup.
    Returns:
        SpellSystemIndex: Populated index.
    """
    index = SpellSystemIndex()
    for spell_id, deps in snapshot.dependencies.items():
        state = states.get_by_spell_id(spell_id)
        lineage_id = state.spell_index_id if state is not None else f"lineage-{spell_id}"
        node = SpellSystemNode(
            spell_id=spell_id,
            lineage_id=lineage_id,
            dependencies=deps,
            is_root=spell_id in snapshot.root_spell_ids,
        )
        index.upsert_node(node)
    return index


def test_component_index_builds_nodes_from_states() -> None:
    """
    Purpose:
        Validate index nodes inherit lineage ids from SpellSystemStates.
    Contract:
        - Node lineage_id matches the SpellSystemState lineage id.
        - Node dependencies mirror the snapshot.
    Returns:
        None.
    Raises:
        AssertionError: If lineage ids or dependencies are incorrect.
    """
    frame = AethericFrame("component-index-lineage")
    states = frame._spell_system_states
    root_id = "root-index-lineage"
    dep_id = "dep-index-lineage"
    root_index = _register_lineage(states, root_id)
    dep_index = _register_lineage(states, dep_id)
    states.update_dependencies(root_index, [dep_id])

    try:
        snapshot = SpellSystemAdjacencyBuilder.build(states)
        index = _build_index(snapshot, states)
        root_node = index.get_node(root_id)
        dep_node = index.get_node(dep_id)
        assert root_node is not None
        assert dep_node is not None
        assert root_node.lineage_id == root_index.id
        assert dep_node.lineage_id == dep_index.id
        assert root_node.dependencies == {dep_id}
        assert dep_node.dependencies == set()
    finally:
        frame.cleanup()


def test_component_index_marks_root_flags_from_snapshot() -> None:
    """
    Purpose:
        Validate root flags are assigned based on snapshot roots.
    Contract:
        - Root node is marked as root.
        - Dependency node is not marked as root.
    Returns:
        None.
    Raises:
        AssertionError: If root flags are incorrect.
    """
    frame = AethericFrame("component-index-roots")
    states = frame._spell_system_states
    root_id = "root-index"
    dep_id = "dep-index"
    root_index = _register_lineage(states, root_id)
    _register_lineage(states, dep_id)
    states.update_dependencies(root_index, [dep_id])

    try:
        snapshot = SpellSystemAdjacencyBuilder.build(states)
        index = _build_index(snapshot, states)
        root_node = index.get_node(root_id)
        dep_node = index.get_node(dep_id)
        assert root_node is not None
        assert dep_node is not None
        assert root_node.is_root is True
        assert dep_node.is_root is False
    finally:
        frame.cleanup()


def test_component_index_validation_state_nodes_mapping_is_live() -> None:
    """
    Purpose:
        Validate validation state returns the live index node mapping.
    Contract:
        - Validation state nodes mapping is the index node mapping.
        - New nodes added to the index appear in the validation state.
    Returns:
        None.
    Raises:
        AssertionError: If node mappings diverge.
    """
    frame = AethericFrame("component-index-live-mapping")
    states = frame._spell_system_states
    root_id = "root-live"
    root_index = _register_lineage(states, root_id)
    states.update_dependencies(root_index, [])

    try:
        snapshot = SpellSystemAdjacencyBuilder.build(states)
        index = _build_index(snapshot, states)
        system = SpellSystemValidationSystem([])
        try:
            result = system.validate(
                index=index,
                blueprints={},
                phase4_results={},
                broken_spell_ids=set(),
                spell_system_states=states,
            )
        finally:
            system.cleanup()

        assert result.nodes is index.nodes
        extra = SpellSystemNode(spell_id="extra-node", lineage_id="lineage-extra")
        index.upsert_node(extra)
        assert "extra-node" in result.nodes
    finally:
        frame.cleanup()


def test_component_index_preserves_node_metadata() -> None:
    """
    Purpose:
        Validate node metadata survives through validation state.
    Contract:
        - Existence, spell type, conduit id, and ward id are preserved.
    Returns:
        None.
    Raises:
        AssertionError: If metadata is lost.
    """
    frame = AethericFrame("component-index-metadata")
    states = frame._spell_system_states
    root_id = "root-meta"
    root_index = _register_lineage(states, root_id)
    states.update_dependencies(root_index, [])

    try:
        snapshot = SpellSystemAdjacencyBuilder.build(states)
        index = _build_index(snapshot, states)
        node = index.get_node(root_id)
        assert node is not None
        node.existence = Existence.unique
        node.spell_type = SpellType.SPELL
        node.conduit_id = "conduit-meta"
        node.ward_id = "ward-meta"

        system = SpellSystemValidationSystem([])
        try:
            result = system.validate(
                index=index,
                blueprints={},
                phase4_results={},
                broken_spell_ids=set(),
                spell_system_states=states,
            )
        finally:
            system.cleanup()

        stored = result.nodes[root_id]
        assert stored.existence is Existence.unique
        assert stored.spell_type is SpellType.SPELL
        assert stored.conduit_id == "conduit-meta"
        assert stored.ward_id == "ward-meta"
    finally:
        frame.cleanup()


def test_component_index_rebuild_reflects_dependency_changes() -> None:
    """
    Purpose:
        Validate rebuilding the index reflects updated dependencies.
    Contract:
        - Dependencies are updated after state changes.
        - Root flags adjust to the new structure.
    Returns:
        None.
    Raises:
        AssertionError: If rebuilt index is stale.
    """
    frame = AethericFrame("component-index-rebuild")
    states = frame._spell_system_states
    root_id = "root-rebuild"
    dep_id = "dep-rebuild"
    root_index = _register_lineage(states, root_id)
    _register_lineage(states, dep_id)
    states.update_dependencies(root_index, [dep_id])
    states.update_dependencies(root_index, [])

    try:
        snapshot = SpellSystemAdjacencyBuilder.build(states)
        index = _build_index(snapshot, states)
        root_node = index.get_node(root_id)
        dep_node = index.get_node(dep_id)
        assert root_node is not None
        assert dep_node is not None
        assert root_node.dependencies == set()
        assert root_node.is_root is True
        assert dep_node.is_root is True
    finally:
        frame.cleanup()


def test_component_index_handles_spells_without_dependencies() -> None:
    """
    Purpose:
        Validate index creation when spells have no dependencies.
    Contract:
        - Node dependencies are empty.
        - Root flag is set when no incoming edges exist.
    Returns:
        None.
    Raises:
        AssertionError: If dependencies or root flags are incorrect.
    """
    frame = AethericFrame("component-index-no-deps")
    states = frame._spell_system_states
    root_id = "root-nodeps"
    root_index = _register_lineage(states, root_id)
    states.update_dependencies(root_index, [])

    try:
        snapshot = SpellSystemAdjacencyBuilder.build(states)
        index = _build_index(snapshot, states)
        node = index.get_node(root_id)
        assert node is not None
        assert node.dependencies == set()
        assert node.is_root is True
    finally:
        frame.cleanup()


def test_component_index_validation_with_graph_consistency_strategy() -> None:
    """
    Purpose:
        Validate index and blueprint alignment passes graph consistency checks.
    Contract:
        - GraphConsistencyStrategy emits no diagnostics for a clean graph.
        - Conduit resolution validity is marked valid for the index nodes.
    Returns:
        None.
    Raises:
        AssertionError: If validation incorrectly reports errors.
    """
    frame = AethericFrame("component-index-graph-consistency")
    states = frame._spell_system_states
    root_id = "root-graph-consistency"
    dep_id = "dep-graph-consistency"
    root_index = _register_lineage(states, root_id)
    _register_lineage(states, dep_id)
    states.update_dependencies(root_index, [dep_id])

    try:
        snapshot = SpellSystemAdjacencyBuilder.build(states)
        blueprints = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)
        index = _build_index(snapshot, states)
        system = SpellSystemValidationSystem([GraphConsistencyStrategy()])
        try:
            result = system.validate(
                index=index,
                blueprints=blueprints,
                phase4_results={root_id: object(), dep_id: object()},
                broken_spell_ids=set(),
                spell_system_states=states,
                conduit_id="cid",
            )
        finally:
            system.cleanup()

        assert result.is_valid is True
        assert result.errors == []
        conduit_state = states.get_conduit_resolution_state("cid")
        assert conduit_state is not None
        assert conduit_state.get_spell_validity(root_id) is SpellValidity.valid
        assert conduit_state.get_spell_validity(dep_id) is SpellValidity.valid
    finally:
        frame.cleanup()


def test_component_index_validation_multiple_roots_stay_valid() -> None:
    """
    Purpose:
        Validate validation marks multiple root-only nodes as valid.
    Contract:
        - GraphConsistencyStrategy emits no diagnostics for isolated roots.
        - Conduit resolution validity is set to valid for each root.
    Returns:
        None.
    Raises:
        AssertionError: If resolution validity is incorrect.
    """
    frame = AethericFrame("component-index-multi-root-valid")
    states = frame._spell_system_states
    root_a = "root-multi-a"
    root_b = "root-multi-b"
    root_a_index = _register_lineage(states, root_a)
    root_b_index = _register_lineage(states, root_b)
    states.update_dependencies(root_a_index, [])
    states.update_dependencies(root_b_index, [])

    try:
        snapshot = SpellSystemAdjacencyBuilder.build(states)
        blueprints = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)
        index = _build_index(snapshot, states)
        system = SpellSystemValidationSystem([GraphConsistencyStrategy()])
        try:
            result = system.validate(
                index=index,
                blueprints=blueprints,
                phase4_results={root_a: object(), root_b: object()},
                broken_spell_ids=set(),
                spell_system_states=states,
                conduit_id="cid",
            )
        finally:
            system.cleanup()

        assert result.is_valid is True
        assert result.errors == []
        conduit_state = states.get_conduit_resolution_state("cid")
        assert conduit_state is not None
        assert conduit_state.get_spell_validity(root_a) is SpellValidity.valid
        assert conduit_state.get_spell_validity(root_b) is SpellValidity.valid
    finally:
        frame.cleanup()
