from __future__ import annotations

from melder.aether.aetheric_frame import AethericFrame
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.spellbook.spell_crafter.system.spell_system_node import SpellSystemNode
from melder.spellbook.spell_crafter.system.spell_system_validation_system import (
    SpellSystemValidationSystem,
)
from melder.spellbook.spell_crafter.system.validation.graph_consistency_strategy import (
    GraphConsistencyStrategy,
)
from melder.spellbook.spell_crafter.system.validation.root_viability_strategy import (
    RootViabilityStrategy,
)
from melder.spellbook.spell_types.spell_types import SpellType


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


def test_component_node_metadata_roundtrip_in_validation_state() -> None:
    """
    Purpose:
        Validate node metadata survives validation state creation.
    Contract:
        - Existence and spell_type remain on nodes after validation.
    Returns:
        None.
    Raises:
        AssertionError: If node metadata is lost.
    """
    frame = AethericFrame("component-node-metadata")
    states = frame._spell_system_states
    root_id = "node-meta"
    root_index = _register_lineage(states, root_id)
    states.update_dependencies(root_index, [])

    try:
        index = SpellSystemIndex()
        node = SpellSystemNode(
            spell_id=root_id,
            lineage_id=root_index.id,
            existence=Existence.unique,
            spell_type=SpellType.SPELL,
            is_root=True,
        )
        index.upsert_node(node)

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
    finally:
        frame.cleanup()


def test_component_node_dependency_change_triggers_graph_mismatch() -> None:
    """
    Purpose:
        Validate node dependency changes surface as graph consistency errors.
    Contract:
        - edge_missing_from_blueprint is emitted for new index edges.
    Returns:
        None.
    Raises:
        AssertionError: If graph mismatch diagnostics are missing.
    """
    frame = AethericFrame("component-node-mismatch")
    states = frame._spell_system_states
    root_id = "node-root"
    dep_id = "node-dep"
    extra_id = "node-extra"
    root_index = _register_lineage(states, root_id)
    dep_index = _register_lineage(states, dep_id)
    _register_lineage(states, extra_id)
    states.update_dependencies(root_index, [dep_id])

    try:
        index = SpellSystemIndex()
        root_node = SpellSystemNode(
            spell_id=root_id,
            lineage_id=root_index.id,
            dependencies={dep_id, extra_id},
            is_root=True,
        )
        dep_node = SpellSystemNode(
            spell_id=dep_id,
            lineage_id=dep_index.id,
        )
        extra_node = SpellSystemNode(
            spell_id=extra_id,
            lineage_id=f"lineage-{extra_id}",
        )
        index.upsert_node(root_node)
        index.upsert_node(dep_node)
        index.upsert_node(extra_node)

        dag = DirectedAcyclicWorkGraph()
        dag.add_node(root_id)
        dag.add_node(dep_id)
        dag.add_dependency(parent_key=dep_id, child_key=root_id)
        blueprint = RootResolutionBlueprint(
            root_spell_id=root_id,
            root_lineage_id=None,
            dag=dag,
        )

        system = SpellSystemValidationSystem(
            [GraphConsistencyStrategy(), RootViabilityStrategy()]
        )
        try:
            result = system.validate(
                index=index,
                blueprints={root_id: blueprint},
                phase4_results={root_id: object(), dep_id: object(), extra_id: object()},
                broken_spell_ids=set(),
                spell_system_states=states,
            )
        finally:
            system.cleanup()

        codes = {diag.code for diag in result.errors}
        assert "edge_missing_from_blueprint" in codes
        root_state = states.get_by_spell_id(root_id)
        assert root_state is not None
        assert root_state.validity is SpellValidity.gated
    finally:
        frame.cleanup()


def test_component_node_survives_validation_state_cleanup() -> None:
    """
    Purpose:
        Validate validation state cleanup does not clean index nodes.
    Contract:
        - Nodes remain uncleaned after validation state cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If nodes are cleaned by validation state cleanup.
    """
    frame = AethericFrame("component-node-cleanup")
    states = frame._spell_system_states
    root_id = "node-cleanup"
    root_index = _register_lineage(states, root_id)
    states.update_dependencies(root_index, [])

    try:
        index = SpellSystemIndex()
        node = SpellSystemNode(
            spell_id=root_id,
            lineage_id=root_index.id,
            is_root=True,
        )
        index.upsert_node(node)

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

        result.cleanup()
        assert node.cleaned is False
    finally:
        frame.cleanup()
