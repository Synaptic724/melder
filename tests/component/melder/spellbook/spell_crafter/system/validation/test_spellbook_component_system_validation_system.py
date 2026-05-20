from __future__ import annotations

from typing import Iterable

import pytest

from melder.aether.aether import Aether
from melder.aether.aetheric_frame.aetheric_frame import AethericFrame
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.aether.spellbook.spell_crafter.dag.dag_index import DagIndex, SocketRef
from melder.aether.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.aether.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.aether.spellbook.spell_crafter.system.spell_system_node import SpellSystemNode
from melder.aether.spellbook.spell_crafter.system.spell_system_validation_system import (
    SpellSystemValidationSystem,
)
from melder.aether.spellbook.spell_crafter.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.aether.spellbook.spell_crafter.system.validation.broken_spell_in_dag_strategy import (
    BrokenSpellInDagStrategy,
)
from melder.aether.spellbook.spell_crafter.system.validation.cycle_detection_strategy import (
    CycleDetectionStrategy,
)
from melder.aether.spellbook.spell_crafter.system.validation.graph_consistency_strategy import (
    GraphConsistencyStrategy,
)
from melder.aether.spellbook.spell_crafter.system.validation.missing_phase4_strategy import (
    MissingPhase4Strategy,
)
from melder.aether.spellbook.spell_crafter.system.validation.root_viability_strategy import (
    RootViabilityStrategy,
)
from melder.aether.spellbook.spell_crafter.system.validation.socket_ref_sanity_strategy import (
    SocketRefSanityStrategy,
)
from melder.aether.spellbook.spell_crafter.system.validation.strategy_base import (
    SpellSystemValidationStrategy,
)
from melder.utilities.custom_exceptions.operation_cancelled_error import (
    OperationCancelledError,
)
from melder.utilities.synchronization.cancellation_event_signal import (
    CancellationEventSignal,
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
    return AethericFrame(Aether(), name)


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
        blueprint.ensure_dag_index_built()
        path_registry = blueprint.path_registry
        path_id = path_registry.extend_path(path_registry.root_path_id, "dependency")
        socket = SocketRef(
            node_id=root_id,
            param_name="dependency",
            param_path_id=path_id,
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
    root_index = _register_index(states, root_id)
    dependency_index = _register_index(states, dependency_id)
    states.update_dependencies(root_index, [dependency_id])
    return frame, states, root_index, dependency_index


class _DiagnosticEmitter(SpellSystemValidationStrategy):
    """
    Purpose:
        Emit a single configured SystemDiagnostic for component tests.
    Contract:
        - Appends the diagnostic to the shared diagnostics list.
    Args:
        diagnostic: SystemDiagnostic to append.
    """

    def __init__(self, diagnostic: SystemDiagnostic) -> None:
        """
        Purpose:
            Capture the diagnostic for later emission.
        Contract:
            - Stores the diagnostic for run().
        Args:
            diagnostic: SystemDiagnostic instance to append.
        """
        self._diagnostic = diagnostic

    def run(
        self,
        *,
        index: SpellSystemIndex,
        blueprints: dict[str, RootResolutionBlueprint],
        phase4_results: dict[str, object],
        broken_spell_ids: set[str],
        spell_system_states: object,
        spell_lookup: dict[str, object],
        diagnostics: list[SystemDiagnostic],
        cancel_event,
    ) -> None:
        """
        Purpose:
            Append the configured diagnostic.
        Contract:
            - Adds the diagnostic to the list without mutation.
        Args:
            index: System index for the frame.
            blueprints: Root blueprints for the frame.
            phase4_results: Phase-4 result map.
            broken_spell_ids: Broken spell ids.
            spell_system_states: SpellSystemStates instance.
            spell_lookup: Mapping of spell ids to spell objects.
            diagnostics: Shared diagnostics list.
            cancel_event: Optional cancellation signal.
        Returns:
            None.
        """
        diagnostics.append(self._diagnostic)


class _RecordingStrategy(SpellSystemValidationStrategy):
    """
    Purpose:
        Track whether a validation strategy was executed.
    Contract:
        - Records each run invocation.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize a call-tracking strategy.
        Contract:
            - Starts with an empty call list.
        """
        self.calls: list[tuple[SpellSystemIndex, dict[str, RootResolutionBlueprint]]] = []

    def run(
        self,
        *,
        index: SpellSystemIndex,
        blueprints: dict[str, RootResolutionBlueprint],
        phase4_results: dict[str, object],
        broken_spell_ids: set[str],
        spell_system_states: object,
        spell_lookup: dict[str, object],
        diagnostics: list[SystemDiagnostic],
        cancel_event,
    ) -> None:
        """
        Purpose:
            Record the run call for validation assertions.
        Contract:
            - Appends the index and blueprint mapping to calls.
        Args:
            index: System index for the frame.
            blueprints: Root blueprints for the frame.
            phase4_results: Phase-4 result map.
            broken_spell_ids: Broken spell ids.
            spell_system_states: SpellSystemStates instance.
            spell_lookup: Mapping of spell ids to spell objects.
            diagnostics: Shared diagnostics list.
            cancel_event: Optional cancellation signal.
        Returns:
            None.
        """
        self.calls.append((index, blueprints))


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


def test_component_system_validation_missing_phase4_marks_root_not_viable() -> None:
    """
    Purpose:
        Validate missing Phase-4 results trigger root viability errors.
    Contract:
        - missing_phase4_validation is emitted for the missing node.
        - root_not_viable is emitted for the root blueprint.
        - Conduit resolution validity is invalid for indexed nodes.
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
                conduit_id="cid",
            )
        finally:
            system.cleanup()

        codes = {diag.code for diag in result.errors}
        assert "missing_phase4_validation" in codes
        assert "root_not_viable" in codes

        conduit_state = states.get_conduit_resolution_state("cid")
        assert conduit_state is not None
        assert conduit_state.get_spell_validity(root_id) is SpellValidity.invalid
        assert conduit_state.get_spell_validity(dep_id) is SpellValidity.invalid
    finally:
        frame.cleanup()


def test_component_system_validation_broken_spell_in_dag_gates_states() -> None:
    """
    Purpose:
        Validate broken spells in a root DAG invalidate conduit resolution.
    Contract:
        - broken_spell_in_dag is emitted for the dependency.
        - root_not_viable is emitted for the root.
        - Conduit resolution validity is invalid for indexed nodes.
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
                conduit_id="cid",
            )
        finally:
            system.cleanup()

        codes = {diag.code for diag in result.errors}
        assert "broken_spell_in_dag" in codes
        assert "root_not_viable" in codes

        conduit_state = states.get_conduit_resolution_state("cid")
        assert conduit_state is not None
        assert conduit_state.get_spell_validity(root_id) is SpellValidity.invalid
        assert conduit_state.get_spell_validity(dep_id) is SpellValidity.invalid
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
                conduit_id="cid",
            )
        finally:
            system.cleanup()

        codes = {diag.code for diag in result.errors}
        assert "cycle_detected" in codes
        assert "edge_missing_from_blueprint" in codes

        conduit_state = states.get_conduit_resolution_state("cid")
        assert conduit_state is not None
        assert conduit_state.get_spell_validity(root_id) is SpellValidity.invalid
        assert conduit_state.get_spell_validity(dep_id) is SpellValidity.invalid
    finally:
        frame.cleanup()


def test_component_system_validation_socket_ref_index_missing_entries() -> None:
    """
    Purpose:
        Validate socket refs missing from the DagIndex are reported.
    Contract:
        - socket_ref_missing_in_index is emitted.
        - socket_ref_missing_in_index_name is emitted.
        - Conduit resolution validity is invalid for indexed nodes.
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
        blueprint.replace_dag_index(DagIndex(path_registry=blueprint.path_registry))
        blueprint.dag_index.rebuild([])

        system = SpellSystemValidationSystem([SocketRefSanityStrategy()])
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
        assert "socket_ref_missing_in_index" in codes
        assert "socket_ref_missing_in_index_name" in codes

        conduit_state = states.get_conduit_resolution_state("cid")
        assert conduit_state is not None
        assert conduit_state.get_spell_validity(root_id) is SpellValidity.invalid
        assert conduit_state.get_spell_validity(dep_id) is SpellValidity.invalid
    finally:
        frame.cleanup()


def test_component_system_validation_detects_orphan_dag_index_socket() -> None:
    """
    Purpose:
        Validate DagIndex sockets missing from socket_refs are reported.
    Contract:
        - dag_index_orphan_socket is emitted.
        - Conduit resolution validity is invalid for indexed nodes.
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
        path_registry = blueprint.path_registry
        orphan_path_id = path_registry.extend_path(path_registry.root_path_id, "orphan")
        orphan = SocketRef(
            node_id=root_id,
            param_name="orphan",
            param_path_id=orphan_path_id,
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
                conduit_id="cid",
            )
        finally:
            system.cleanup()

        codes = {diag.code for diag in result.errors}
        assert "dag_index_orphan_socket" in codes

        conduit_state = states.get_conduit_resolution_state("cid")
        assert conduit_state is not None
        assert conduit_state.get_spell_validity(root_id) is SpellValidity.invalid
        assert conduit_state.get_spell_validity(dep_id) is SpellValidity.invalid
    finally:
        frame.cleanup()


def test_component_system_validation_warning_does_not_gate_states() -> None:
    """
    Purpose:
        Validate warning-only diagnostics do not invalidate conduit resolution.
    Contract:
        - Warning diagnostics appear in the validation state.
        - Conduit resolution validity is set to valid.
    Returns:
        None.
    Raises:
        AssertionError: If warnings invalidate conduit resolution validity.
    """
    root_id = "root-warning-only"
    frame = _make_frame("component-system-warning-only")
    states = frame._spell_system_states
    root_index = _register_index(states, root_id)
    states.update_dependencies(root_index, [])

    try:
        index = SpellSystemIndex()
        index.upsert_node(
            SpellSystemNode(
                spell_id=root_id,
                lineage_id=root_index.id,
                is_root=True,
            )
        )
        warning = SystemDiagnostic(
            code="warn_only",
            message="warning only",
            severity=SystemDiagnosticSeverity.WARNING,
            spell_id=root_id,
            root_id=root_id,
        )
        system = SpellSystemValidationSystem([_DiagnosticEmitter(warning)])
        try:
            result = system.validate(
                index=index,
                blueprints={},
                phase4_results={},
                broken_spell_ids=set(),
                spell_system_states=states,
                conduit_id="cid",
            )
        finally:
            system.cleanup()

        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == [warning]
        conduit_state = states.get_conduit_resolution_state("cid")
        assert conduit_state is not None
        assert conduit_state.get_spell_validity(root_id) is SpellValidity.valid
    finally:
        frame.cleanup()


def test_component_system_validation_skips_missing_state() -> None:
    """
    Purpose:
        Validate index nodes without registered states are skipped.
    Contract:
        - Validation succeeds without raising for missing states.
        - Conduit resolution validity is marked valid for indexed nodes.
    Returns:
        None.
    Raises:
        AssertionError: If missing states disrupt validation.
    """
    frame = _make_frame("component-system-missing-state")
    states = frame._spell_system_states
    root_id = "root-missing-state"
    root_index = _register_index(states, root_id)
    states.update_dependencies(root_index, [])

    try:
        index = SpellSystemIndex()
        index.upsert_node(
            SpellSystemNode(
                spell_id=root_id,
                lineage_id=root_index.id,
                is_root=True,
            )
        )
        index.upsert_node(
            SpellSystemNode(
                spell_id="orphan-node",
                lineage_id="lineage-orphan",
            )
        )
        system = SpellSystemValidationSystem([])
        try:
            result = system.validate(
                index=index,
                blueprints={},
                phase4_results={},
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
        assert states.get_by_spell_id("orphan-node") is None
    finally:
        frame.cleanup()


def test_component_system_validation_only_updates_index_nodes() -> None:
    """
    Purpose:
        Validate validation updates only the nodes present in the index.
    Contract:
        - Indexed nodes are marked valid.
        - Non-indexed lineages retain their prior validity in conduit state.
    Returns:
        None.
    Raises:
        AssertionError: If non-indexed conduit validity is modified.
    """
    frame = _make_frame("component-system-index-only")
    states = frame._spell_system_states
    root_id = "root-index-only"
    extra_id = "extra-index-only"
    root_index = _register_index(states, root_id)
    extra_index = _register_index(states, extra_id)
    states.update_dependencies(root_index, [])
    states.update_dependencies(extra_index, [])

    try:
        index = SpellSystemIndex()
        index.upsert_node(
            SpellSystemNode(
                spell_id=root_id,
                lineage_id=root_index.id,
                is_root=True,
            )
        )
        system = SpellSystemValidationSystem([])
        try:
            result = system.validate(
                index=index,
                blueprints={},
                phase4_results={},
                broken_spell_ids=set(),
                spell_system_states=states,
                conduit_id="cid",
            )
        finally:
            system.cleanup()

        assert result.is_valid is True
        conduit_state = states.get_conduit_resolution_state("cid")
        assert conduit_state is not None
        assert conduit_state.get_spell_validity(root_id) is SpellValidity.valid
        assert conduit_state.get_spell_validity(extra_id) is SpellValidity.unknown
    finally:
        frame.cleanup()


def test_component_system_validation_cancels_before_strategies() -> None:
    """
    Purpose:
        Validate cancellation prevents strategies from executing.
    Contract:
        - Cancellation raises OperationCancelledError.
        - Strategies are not invoked after cancellation is set.
    Returns:
        None.
    Raises:
        AssertionError: If strategies execute after cancellation.
    """
    frame = _make_frame("component-system-cancel")
    states = frame._spell_system_states
    root_id = "root-cancel"
    root_index = _register_index(states, root_id)
    states.update_dependencies(root_index, [])

    cancel_signal = CancellationEventSignal()
    cancel_signal.cancel()
    strategy = _RecordingStrategy()

    try:
        index = SpellSystemIndex()
        index.upsert_node(
            SpellSystemNode(
                spell_id=root_id,
                lineage_id=root_index.id,
                is_root=True,
            )
        )
        system = SpellSystemValidationSystem([strategy])
        try:
            with pytest.raises(OperationCancelledError):
                system.validate(
                    index=index,
                    blueprints={},
                    phase4_results={},
                    broken_spell_ids=set(),
                    spell_system_states=states,
                    conduit_id="cid",
                    cancel_event=cancel_signal.event,
                )
        finally:
            system.cleanup()

        assert strategy.calls == []
    finally:
        cancel_signal.cleanup()
        frame.cleanup()


def test_component_system_validation_collects_multiple_errors() -> None:
    """
    Purpose:
        Validate multiple error diagnostics are returned and invalidate resolution.
    Contract:
        - Error diagnostics are returned in the validation state.
        - Conduit resolution validity is invalid.
    Returns:
        None.
    Raises:
        AssertionError: If errors are missing or resolution validity is not invalid.
    """
    root_id = "root-multi-error"
    frame = _make_frame("component-system-multi-error")
    states = frame._spell_system_states
    root_index = _register_index(states, root_id)
    states.update_dependencies(root_index, [])

    try:
        index = SpellSystemIndex()
        index.upsert_node(
            SpellSystemNode(
                spell_id=root_id,
                lineage_id=root_index.id,
                is_root=True,
            )
        )
        error_a = SystemDiagnostic(
            code="error_a",
            message="error a",
            severity=SystemDiagnosticSeverity.ERROR,
            spell_id=root_id,
            root_id=root_id,
        )
        error_b = SystemDiagnostic(
            code="error_b",
            message="error b",
            severity=SystemDiagnosticSeverity.ERROR,
            spell_id=root_id,
            root_id=root_id,
        )
        system = SpellSystemValidationSystem(
            [_DiagnosticEmitter(error_a), _DiagnosticEmitter(error_b)]
        )
        try:
            result = system.validate(
                index=index,
                blueprints={},
                phase4_results={},
                broken_spell_ids=set(),
                spell_system_states=states,
                conduit_id="cid",
            )
        finally:
            system.cleanup()

        codes = {diag.code for diag in result.errors}
        assert codes == {"error_a", "error_b"}
        assert result.is_valid is False
        conduit_state = states.get_conduit_resolution_state("cid")
        assert conduit_state is not None
        assert conduit_state.get_spell_validity(root_id) is SpellValidity.invalid
    finally:
        frame.cleanup()



