from __future__ import annotations

from typing import Iterable

import pytest

from melder.aether.aetheric_frame import AethericFrame
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.dag.dag_index import DagIndex, SocketRef
from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.spellbook.spell_crafter.system.spell_system_node import SpellSystemNode
from melder.spellbook.spell_crafter.system.spell_system_validation_system import (
    SpellSystemValidationSystem,
)
from melder.spellbook.spell_crafter.system.validation.broken_spell_in_dag_strategy import (
    BrokenSpellInDagStrategy,
)
from melder.spellbook.spell_crafter.system.validation.cycle_detection_strategy import (
    CycleDetectionStrategy,
)
from melder.spellbook.spell_crafter.system.validation.graph_consistency_strategy import (
    GraphConsistencyStrategy,
)
from melder.spellbook.spell_crafter.system.validation.missing_phase4_strategy import (
    MissingPhase4Strategy,
)
from melder.spellbook.spell_crafter.system.validation.root_viability_strategy import (
    RootViabilityStrategy,
)
from melder.spellbook.spell_crafter.system.validation.socket_ref_sanity_strategy import (
    SocketRefSanityStrategy,
)


def _make_frame(name: str = "frame-system-validation-component") -> AethericFrame:
    """
    Purpose:
        Provide a standalone AethericFrame for component validation tests.
    Contract:
        - Returns a new frame instance with SpellSystemStates attached.
    Args:
        name: Frame name for diagnostics.
    Returns:
        AethericFrame: A fresh AethericFrame instance.
    """
    return AethericFrame(name)


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


def _build_index(
    *,
    root_id: str,
    root_index: SpellIndex,
    dependency_id: str,
    dependency_index: SpellIndex,
    dependency_edges: Iterable[str],
) -> SpellSystemIndex:
    """
    Purpose:
        Build a SpellSystemIndex with root and dependency nodes.
    Contract:
        - Root node is marked as root.
        - Dependencies are assigned as provided.
    Args:
        root_id: Root spell id.
        root_index: SpellIndex for the root.
        dependency_id: Dependency spell id.
        dependency_index: SpellIndex for the dependency.
        dependency_edges: Iterable of dependency ids for the root.
    Returns:
        SpellSystemIndex: Populated system index.
    """
    index = SpellSystemIndex()
    root_node = SpellSystemNode(
        spell_id=root_id,
        lineage_id=root_index.id,
        dependencies=dependency_edges,
        is_root=True,
    )
    dependency_node = SpellSystemNode(
        spell_id=dependency_id,
        lineage_id=dependency_index.id,
    )
    index.upsert_node(root_node)
    index.upsert_node(dependency_node)
    return index


def _build_blueprint(
    *,
    root_id: str,
    dependency_id: str,
    add_socket: bool = True,
) -> RootResolutionBlueprint:
    """
    Purpose:
        Build a simple root blueprint with one dependency edge.
    Contract:
        - DAG contains root and dependency nodes.
        - Edge is dependency -> root.
        - Socket refs are populated when add_socket is True.
    Args:
        root_id: Root spell id.
        dependency_id: Dependency spell id.
        add_socket: Whether to add a socket ref for the dependency edge.
    Returns:
        RootResolutionBlueprint: The constructed blueprint.
    """
    dag = DirectedAcyclicWorkGraph()
    dag.add_node(root_id)
    dag.add_node(dependency_id)
    dag.add_dependency(
        parent_key=dependency_id,
        child_key=root_id,
        param_name="dependency",
        socket_kind=SocketKind.NORMAL,
    )
    blueprint = RootResolutionBlueprint(
        root_spell_id=root_id,
        root_lineage_id=None,
        dag=dag,
    )
    if add_socket:
        socket = SocketRef(
            node_id=root_id,
            param_name="dependency",
            param_path=("dependency",),
            socket_kind=SocketKind.NORMAL,
        )
        blueprint.add_socket_ref(socket)
    return blueprint


def _setup_states_with_dependency(
    *,
    root_id: str,
    dependency_id: str,
) -> tuple[AethericFrame, object, SpellIndex, SpellIndex]:
    """
    Purpose:
        Prepare SpellSystemStates with a root and dependency edge.
    Contract:
        - Both spell ids are registered.
        - Root dependency edge is recorded.
    Args:
        root_id: Root spell id.
        dependency_id: Dependency spell id.
    Returns:
        tuple: (frame, states, root_index, dependency_index).
    """
    frame = _make_frame()
    states = frame._spell_system_states
    root_index = _register_lineage(states, root_id)
    dependency_index = _register_lineage(states, dependency_id)
    states.update_dependencies(root_index, [dependency_id])
    return frame, states, root_index, dependency_index


def test_component_system_validation_clean_graph_marks_valid() -> None:
    """
    Purpose:
        Validate system validation reports no errors for clean artifacts.
    Contract:
        - No diagnostics are produced.
        - SpellSystemStates are marked valid for all index nodes.
    Returns:
        None.
    Raises:
        AssertionError: If validation flags or diagnostics are incorrect.
    """
    root_id = "root-clean"
    dep_id = "dep-clean"
    frame, states, root_index, dep_index = _setup_states_with_dependency(
        root_id=root_id,
        dependency_id=dep_id,
    )
    try:
        index = _build_index(
            root_id=root_id,
            root_index=root_index,
            dependency_id=dep_id,
            dependency_index=dep_index,
            dependency_edges=[dep_id],
        )
        blueprint = _build_blueprint(root_id=root_id, dependency_id=dep_id)
        strategies = [
            CycleDetectionStrategy(),
            BrokenSpellInDagStrategy(),
            GraphConsistencyStrategy(),
            MissingPhase4Strategy(),
            RootViabilityStrategy(),
            SocketRefSanityStrategy(),
        ]
        system = SpellSystemValidationSystem(strategies)
        try:
            result = system.validate(
                index=index,
                blueprints={root_id: blueprint},
                phase4_results={root_id: object(), dep_id: object()},
                broken_spell_ids=set(),
                spell_system_states=states,
            )
        finally:
            system.cleanup()

        assert result.is_valid is True
        assert result.errors == []

        root_state = states.get_by_spell_id(root_id)
        dep_state = states.get_by_spell_id(dep_id)
        assert root_state is not None
        assert dep_state is not None
        assert root_state.validity is SpellValidity.valid
        assert dep_state.validity is SpellValidity.valid
    finally:
        frame.cleanup()


def test_component_system_validation_missing_phase4_marks_root_not_viable() -> None:
    """
    Purpose:
        Validate missing Phase-4 results trigger root viability errors.
    Contract:
        - missing_phase4_validation is emitted for the missing node.
        - root_not_viable is emitted for the root blueprint.
        - SpellSystemStates are gated.
    Returns:
        None.
    Raises:
        AssertionError: If missing-phase4 diagnostics are absent.
    """
    root_id = "root-missing-phase4"
    dep_id = "dep-missing-phase4"
    frame, states, root_index, dep_index = _setup_states_with_dependency(
        root_id=root_id,
        dependency_id=dep_id,
    )
    try:
        index = _build_index(
            root_id=root_id,
            root_index=root_index,
            dependency_id=dep_id,
            dependency_index=dep_index,
            dependency_edges=[dep_id],
        )
        blueprint = _build_blueprint(root_id=root_id, dependency_id=dep_id)
        system = SpellSystemValidationSystem(
            [MissingPhase4Strategy(), RootViabilityStrategy()]
        )
        try:
            result = system.validate(
                index=index,
                blueprints={root_id: blueprint},
                phase4_results={root_id: object()},
                broken_spell_ids=set(),
                spell_system_states=states,
            )
        finally:
            system.cleanup()

        codes = {diag.code for diag in result.errors}
        assert "missing_phase4_validation" in codes
        assert "root_not_viable" in codes

        root_state = states.get_by_spell_id(root_id)
        dep_state = states.get_by_spell_id(dep_id)
        assert root_state is not None
        assert dep_state is not None
        assert root_state.validity is SpellValidity.gated
        assert dep_state.validity is SpellValidity.gated
    finally:
        frame.cleanup()


def test_component_system_validation_broken_spell_in_dag_gates_states() -> None:
    """
    Purpose:
        Validate broken spells in a root DAG gate system validity.
    Contract:
        - broken_spell_in_dag is emitted for the dependency.
        - root_not_viable is emitted for the root.
        - SpellSystemStates are gated.
    Returns:
        None.
    Raises:
        AssertionError: If broken-spell diagnostics are missing.
    """
    root_id = "root-broken"
    dep_id = "dep-broken"
    frame, states, root_index, dep_index = _setup_states_with_dependency(
        root_id=root_id,
        dependency_id=dep_id,
    )
    try:
        index = _build_index(
            root_id=root_id,
            root_index=root_index,
            dependency_id=dep_id,
            dependency_index=dep_index,
            dependency_edges=[dep_id],
        )
        blueprint = _build_blueprint(root_id=root_id, dependency_id=dep_id)
        system = SpellSystemValidationSystem(
            [BrokenSpellInDagStrategy(), RootViabilityStrategy()]
        )
        try:
            result = system.validate(
                index=index,
                blueprints={root_id: blueprint},
                phase4_results={root_id: object(), dep_id: object()},
                broken_spell_ids={dep_id},
                spell_system_states=states,
            )
        finally:
            system.cleanup()

        codes = {diag.code for diag in result.errors}
        assert "broken_spell_in_dag" in codes
        assert "root_not_viable" in codes

        root_state = states.get_by_spell_id(root_id)
        dep_state = states.get_by_spell_id(dep_id)
        assert root_state is not None
        assert dep_state is not None
        assert root_state.validity is SpellValidity.gated
        assert dep_state.validity is SpellValidity.gated
    finally:
        frame.cleanup()


def test_component_system_validation_cycle_and_graph_mismatch() -> None:
    """
    Purpose:
        Validate cycle detection and graph mismatch diagnostics.
    Contract:
        - cycle_detected is emitted for cyclic indexes.
        - edge_missing_from_blueprint is emitted for missing DAG edges.
    Returns:
        None.
    Raises:
        AssertionError: If expected diagnostics are missing.
    """
    root_id = "root-cycle"
    dep_id = "dep-cycle"
    frame, states, root_index, dep_index = _setup_states_with_dependency(
        root_id=root_id,
        dependency_id=dep_id,
    )
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
            dependencies={root_id},
        )
        index.upsert_node(root_node)
        index.upsert_node(dep_node)

        blueprint = _build_blueprint(root_id=root_id, dependency_id=dep_id)
        system = SpellSystemValidationSystem(
            [CycleDetectionStrategy(), GraphConsistencyStrategy()]
        )
        try:
            result = system.validate(
                index=index,
                blueprints={root_id: blueprint},
                phase4_results={root_id: object(), dep_id: object()},
                broken_spell_ids=set(),
                spell_system_states=states,
            )
        finally:
            system.cleanup()

        codes = {diag.code for diag in result.errors}
        assert "cycle_detected" in codes
        assert "edge_missing_from_blueprint" in codes

        root_state = states.get_by_spell_id(root_id)
        dep_state = states.get_by_spell_id(dep_id)
        assert root_state is not None
        assert dep_state is not None
        assert root_state.validity is SpellValidity.gated
        assert dep_state.validity is SpellValidity.gated
    finally:
        frame.cleanup()


def test_component_system_validation_socket_ref_index_missing_entries() -> None:
    """
    Purpose:
        Validate socket refs missing from the DagIndex are reported.
    Contract:
        - socket_ref_missing_in_index is emitted.
        - socket_ref_missing_in_index_name is emitted.
        - SpellSystemStates are gated.
    Returns:
        None.
    Raises:
        AssertionError: If socket ref diagnostics are missing.
    """
    root_id = "root-socket-missing"
    dep_id = "dep-socket-missing"
    frame, states, root_index, dep_index = _setup_states_with_dependency(
        root_id=root_id,
        dependency_id=dep_id,
    )
    try:
        index = _build_index(
            root_id=root_id,
            root_index=root_index,
            dependency_id=dep_id,
            dependency_index=dep_index,
            dependency_edges=[dep_id],
        )
        blueprint = _build_blueprint(root_id=root_id, dependency_id=dep_id)
        blueprint.replace_dag_index(DagIndex())

        system = SpellSystemValidationSystem([SocketRefSanityStrategy()])
        try:
            result = system.validate(
                index=index,
                blueprints={root_id: blueprint},
                phase4_results={root_id: object(), dep_id: object()},
                broken_spell_ids=set(),
                spell_system_states=states,
            )
        finally:
            system.cleanup()

        codes = {diag.code for diag in result.errors}
        assert "socket_ref_missing_in_index" in codes
        assert "socket_ref_missing_in_index_name" in codes

        root_state = states.get_by_spell_id(root_id)
        dep_state = states.get_by_spell_id(dep_id)
        assert root_state is not None
        assert dep_state is not None
        assert root_state.validity is SpellValidity.gated
        assert dep_state.validity is SpellValidity.gated
    finally:
        frame.cleanup()


def test_component_system_validation_detects_orphan_dag_index_socket() -> None:
    """
    Purpose:
        Validate DagIndex sockets missing from socket_refs are reported.
    Contract:
        - dag_index_orphan_socket is emitted.
        - SpellSystemStates are gated.
    Returns:
        None.
    Raises:
        AssertionError: If orphan socket diagnostics are missing.
    """
    root_id = "root-orphan-socket"
    dep_id = "dep-orphan-socket"
    frame, states, root_index, dep_index = _setup_states_with_dependency(
        root_id=root_id,
        dependency_id=dep_id,
    )
    try:
        index = _build_index(
            root_id=root_id,
            root_index=root_index,
            dependency_id=dep_id,
            dependency_index=dep_index,
            dependency_edges=[dep_id],
        )
        blueprint = _build_blueprint(root_id=root_id, dependency_id=dep_id)
        orphan = SocketRef(
            node_id=root_id,
            param_name="orphan",
            param_path=("orphan",),
            socket_kind=SocketKind.NORMAL,
        )
        blueprint.dag_index.add_socket(orphan)

        system = SpellSystemValidationSystem([SocketRefSanityStrategy()])
        try:
            result = system.validate(
                index=index,
                blueprints={root_id: blueprint},
                phase4_results={root_id: object(), dep_id: object()},
                broken_spell_ids=set(),
                spell_system_states=states,
            )
        finally:
            system.cleanup()

        codes = {diag.code for diag in result.errors}
        assert "dag_index_orphan_socket" in codes

        root_state = states.get_by_spell_id(root_id)
        dep_state = states.get_by_spell_id(dep_id)
        assert root_state is not None
        assert dep_state is not None
        assert root_state.validity is SpellValidity.gated
        assert dep_state.validity is SpellValidity.gated
    finally:
        frame.cleanup()
