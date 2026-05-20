from __future__ import annotations

from melder.aether.aether import Aether
from melder.aether.aetheric_frame.aetheric_frame import AethericFrame
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.aether.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.aether.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.aether.spellbook.spell_crafter.system.spell_system_node import SpellSystemNode
from melder.aether.spellbook.spell_crafter.system.spell_system_validation_system import (
    SpellSystemValidationSystem,
)
from melder.aether.spellbook.spell_crafter.system.validation.graph_consistency_strategy import (
    GraphConsistencyStrategy,
)
from melder.aether.spellbook.spell_crafter.system.validation.root_viability_strategy import (
    RootViabilityStrategy,
)


def _register_index(states, spell_id: str) -> SpellIndex:
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
    states.register_index(index)
    return index


def _build_blueprint(root_id: str, dependency_id: str) -> RootResolutionBlueprint:
    """
    Purpose:
        Build a basic root blueprint with a single dependency edge.
    Contract:
        - DAG contains root and dependency nodes.
        - Edge is dependency -> root.
    Args:
        root_id: Root spell id.
        dependency_id: Dependency spell id.
    Returns:
        RootResolutionBlueprint: The constructed blueprint.
    """
    dag = DirectedAcyclicWorkGraph()
    dag.add_node(root_id)
    dag.add_node(dependency_id)
    dag.add_dependency(parent_key=dependency_id, child_key=root_id)
    return RootResolutionBlueprint(root_spell_id=root_id, root_lineage_id=None, dag=dag)


def test_component_system_validation_reports_missing_index_node() -> None:
    """
    Purpose:
        Validate missing index nodes are surfaced via system validation.
    Contract:
        - missing_index_node is emitted for blueprint nodes absent from the index.
        - root_not_viable is emitted for the affected root.
        - Conduit resolution validity is invalid for indexed nodes.
    Returns:
        None.
    Raises:
        AssertionError: If diagnostics are missing.
    """
    root_id = "root-missing-index"
    dep_id = "dep-missing-index"
    frame = AethericFrame(Aether(), "component-graph-consistency-missing-index")
    states = frame._spell_system_states
    root_index = _register_index(states, root_id)
    _register_index(states, dep_id)
    states.update_dependencies(root_index, [dep_id])

    try:
        index = SpellSystemIndex()
        root_node = SpellSystemNode(
            spell_id=root_id,
            lineage_id=root_index.id,
            dependencies={dep_id},
            is_root=True,
        )
        index.upsert_node(root_node)
        blueprint = _build_blueprint(root_id, dep_id)
        system = SpellSystemValidationSystem(
            [GraphConsistencyStrategy(), RootViabilityStrategy()]
        )
        try:
            result = system.validate(
                index=index,
                blueprints={root_id: blueprint},
                phase4_results={root_id: object(), dep_id: object()},
                broken_spell_ids=set(),
                spell_system_states=states,
                conduit_id="cid",
            )
        finally:
            system.cleanup()

        codes = {diag.code for diag in result.errors}
        assert "missing_index_node" in codes
        assert "root_not_viable" in codes

        conduit_state = states.get_conduit_resolution_state("cid")
        assert conduit_state is not None
        assert conduit_state.get_spell_validity(root_id) is SpellValidity.invalid
    finally:
        frame.cleanup()


def test_component_system_validation_reports_edge_mismatch_index() -> None:
    """
    Purpose:
        Validate edge mismatches between blueprint and index are detected.
    Contract:
        - edge_mismatch_index is emitted for unexpected blueprint edges.
        - root_not_viable is emitted for the affected root.
        - Conduit resolution validity is invalid for indexed nodes.
    Returns:
        None.
    Raises:
        AssertionError: If diagnostics are missing.
    """
    root_id = "root-edge-mismatch"
    dep_id = "dep-edge-mismatch"
    frame = AethericFrame(Aether(), "component-graph-consistency-edge-mismatch")
    states = frame._spell_system_states
    root_index = _register_index(states, root_id)
    dep_index = _register_index(states, dep_id)
    states.update_dependencies(root_index, [dep_id])

    try:
        index = SpellSystemIndex()
        root_node = SpellSystemNode(
            spell_id=root_id,
            lineage_id=root_index.id,
            dependencies=set(),
            is_root=True,
        )
        dep_node = SpellSystemNode(
            spell_id=dep_id,
            lineage_id=dep_index.id,
            dependencies=set(),
        )
        index.upsert_node(root_node)
        index.upsert_node(dep_node)

        blueprint = _build_blueprint(root_id, dep_id)
        system = SpellSystemValidationSystem(
            [GraphConsistencyStrategy(), RootViabilityStrategy()]
        )
        try:
            result = system.validate(
                index=index,
                blueprints={root_id: blueprint},
                phase4_results={root_id: object(), dep_id: object()},
                broken_spell_ids=set(),
                spell_system_states=states,
                conduit_id="cid",
            )
        finally:
            system.cleanup()

        codes = {diag.code for diag in result.errors}
        assert "edge_mismatch_index" in codes
        assert "root_not_viable" in codes

        conduit_state = states.get_conduit_resolution_state("cid")
        assert conduit_state is not None
        assert conduit_state.get_spell_validity(root_id) is SpellValidity.invalid
        assert conduit_state.get_spell_validity(dep_id) is SpellValidity.invalid
    finally:
        frame.cleanup()


def test_component_system_validation_does_not_add_root_viability_for_unscoped_errors() -> None:
    """
    Purpose:
        Validate unscoped graph errors do not emit root viability diagnostics.
    Contract:
        - edge_missing_from_blueprint is emitted with no root_id.
        - root_not_viable is not emitted.
        - Conduit resolution validity is invalid due to existing errors.
    Returns:
        None.
    Raises:
        AssertionError: If unexpected diagnostics are emitted.
    """
    root_id = "root-unscoped"
    dep_id = "dep-unscoped"
    frame = AethericFrame(Aether(), "component-graph-consistency-unscoped")
    states = frame._spell_system_states
    root_index = _register_index(states, root_id)
    dep_index = _register_index(states, dep_id)
    states.update_dependencies(root_index, [dep_id])

    try:
        index = SpellSystemIndex()
        root_node = SpellSystemNode(
            spell_id=root_id,
            lineage_id=root_index.id,
            dependencies={dep_id},
            is_root=True,
        )
        dep_node = SpellSystemNode(
            spell_id=dep_id,
            lineage_id=dep_index.id,
            dependencies=set(),
        )
        index.upsert_node(root_node)
        index.upsert_node(dep_node)

        dag = DirectedAcyclicWorkGraph()
        dag.add_node(root_id)
        dag.add_node(dep_id)
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
                phase4_results={root_id: object(), dep_id: object()},
                broken_spell_ids=set(),
                spell_system_states=states,
                conduit_id="cid",
            )
        finally:
            system.cleanup()

        codes = {diag.code for diag in result.errors}
        assert "edge_missing_from_blueprint" in codes
        assert "root_not_viable" not in codes

        conduit_state = states.get_conduit_resolution_state("cid")
        assert conduit_state is not None
        assert conduit_state.get_spell_validity(root_id) is SpellValidity.invalid
        assert conduit_state.get_spell_validity(dep_id) is SpellValidity.invalid
    finally:
        frame.cleanup()



