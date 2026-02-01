from __future__ import annotations

import pytest

from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.dag.dag_index import DagIndex, PathRegistry, SocketRef
from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.spellbook.spell_crafter.system.spell_system_node import SpellSystemNode
from melder.spellbook.spell_crafter.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
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
from melder.spellbook.spell_crafter.system.validation.dependency_type_sanity_strategy import (
    DependencyTypeSanityStrategy,
)
from melder.spellbook.spell_crafter.system.validation.index_coverage_strategy import (
    IndexCoverageStrategy,
)
from melder.spellbook.spell_crafter.system.validation.index_dependency_sanity_strategy import (
    IndexDependencySanityStrategy,
)
from melder.spellbook.spell_crafter.system.validation.lineage_alignment_strategy import (
    LineageAlignmentStrategy,
)
from melder.spellbook.spell_crafter.system.validation.lineage_version_conflict_strategy import (
    LineageVersionConflictStrategy,
)
from melder.spellbook.spell_crafter.system.validation.missing_phase4_strategy import (
    MissingPhase4Strategy,
)
from melder.spellbook.spell_crafter.system.validation.ownership_consistency_strategy import (
    OwnershipConsistencyStrategy,
)
from melder.spellbook.spell_crafter.system.validation.root_coverage_strategy import (
    RootCoverageStrategy,
)
from melder.spellbook.spell_crafter.system.validation.root_lineage_conflict_strategy import (
    RootLineageConflictStrategy,
)
from melder.spellbook.spell_crafter.system.validation.root_reachability_strategy import (
    RootReachabilityStrategy,
)
from melder.spellbook.spell_crafter.system.validation.root_scale_limit_strategy import (
    RootScaleLimitStrategy,
)
from melder.spellbook.spell_crafter.system.validation.root_viability_strategy import (
    RootViabilityStrategy,
)
from melder.spellbook.spell_crafter.system.validation.socket_ref_sanity_strategy import (
    SocketRefSanityStrategy,
)
from melder.spellbook.spell_types.spell_types import SpellType
from melder.utilities.custom_exceptions.operation_cancelled_error import (
    OperationCancelledError,
)
from melder.utilities.synchronization.cancellation_event_signal import (
    CancellationEventSignal,
)


def _make_index(
    nodes: dict[str, set[str]],
    *,
    root_ids: set[str] | None = None,
    lineage_map: dict[str, str] | None = None,
    spell_types: dict[str, SpellType] | None = None,
    conduit_ids: dict[str, str] | None = None,
) -> SpellSystemIndex:
    """
    Purpose:
        Build a SpellSystemIndex from a dependency map.
    Contract:
        - Each node is registered with its dependency set.
        - Root flags are applied when provided.
    Args:
        nodes: Mapping of spell_id -> dependency ids.
        root_ids: Optional set of root spell ids.
        lineage_map: Optional mapping of spell_id -> lineage id.
        spell_types: Optional mapping of spell_id -> SpellType.
        conduit_ids: Optional mapping of spell_id -> conduit id.
    Returns:
        SpellSystemIndex: Populated index.
    """
    index = SpellSystemIndex()
    roots = root_ids or set()
    for spell_id, deps in nodes.items():
        lineage_id = (
            lineage_map.get(spell_id)
            if lineage_map is not None and spell_id in lineage_map
            else f"lineage-{spell_id}"
        )
        node = SpellSystemNode(
            spell_id=spell_id,
            lineage_id=lineage_id,
            dependencies=deps,
            spell_type=spell_types.get(spell_id) if spell_types is not None else None,
            conduit_id=conduit_ids.get(spell_id) if conduit_ids is not None else None,
            is_root=spell_id in roots,
        )
        index.upsert_node(node)
    return index


def _make_blueprint(
    *,
    root_id: str,
    root_lineage_id: str | None = None,
    edges: dict[str, set[str]],
    extra_nodes: set[str] | None = None,
) -> RootResolutionBlueprint:
    """
    Purpose:
        Build a RootResolutionBlueprint with the supplied edges.
    Contract:
        - DAG nodes include edge endpoints and extra_nodes.
        - DAG edges connect parent -> child.
    Args:
        root_id: Root spell id for the blueprint.
        root_lineage_id: Optional lineage id for the root spell.
        edges: Mapping of child_id -> parent ids.
        extra_nodes: Optional extra node ids to include with no edges.
    Returns:
        RootResolutionBlueprint: The constructed blueprint.
    """
    node_ids: set[str] = set(extra_nodes or set())
    for child_id, parents in edges.items():
        node_ids.add(child_id)
        node_ids.update(parents)

    dag = DirectedAcyclicWorkGraph()
    for node_id in node_ids:
        dag.add_node(node_id)
    for child_id, parents in edges.items():
        for parent_id in parents:
            dag.add_dependency(parent_key=parent_id, child_key=child_id)

    return RootResolutionBlueprint(
        root_spell_id=root_id,
        root_lineage_id=root_lineage_id,
        dag=dag,
    )


def _path_id(path_registry: PathRegistry, path: tuple[str, ...]) -> int:
    path_id = path_registry.root_path_id
    for segment in path:
        path_id = path_registry.extend_path(path_id, segment)
    return path_id


def _make_socket_ref(
    *,
    node_id: str,
    name: str,
    path: tuple[str, ...],
    path_registry: PathRegistry,
) -> SocketRef:
    """
    Purpose:
        Build a simple SocketRef for socket sanity tests.
    Contract:
        - SocketRef uses SocketKind.NORMAL.
    Args:
        node_id: Owning node id.
        name: Socket param name.
        path: Socket param path.
    Returns:
        SocketRef: The constructed socket reference.
    """
    return SocketRef(
        node_id=node_id,
        param_name=name,
        param_path_id=_path_id(path_registry, path),
        socket_kind=SocketKind.NORMAL,
    )


def test_component_broken_spell_in_dag_no_broken_ids() -> None:
    """
    Purpose:
        Validate BrokenSpellInDagStrategy is a noop with no broken ids.
    Contract:
        - Diagnostics remain empty when broken_spell_ids is empty.
    Returns:
        None.
    """
    strategy = BrokenSpellInDagStrategy()
    blueprint = _make_blueprint(root_id="root", edges={"root": {"dep"}})
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index({"root": {"dep"}, "dep": set()}, root_ids={"root"}),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert diagnostics == []


def test_component_broken_spell_in_dag_reports_single_broken() -> None:
    """
    Purpose:
        Validate BrokenSpellInDagStrategy reports a broken spell in a root DAG.
    Contract:
        - A broken spell id in the DAG yields a broken_spell_in_dag diagnostic.
    Returns:
        None.
    """
    strategy = BrokenSpellInDagStrategy()
    blueprint = _make_blueprint(root_id="root", edges={"root": {"dep"}})
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index({"root": {"dep"}, "dep": set()}, root_ids={"root"}),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids={"dep"},
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert len(diagnostics) == 1
    assert diagnostics[0].code == "broken_spell_in_dag"
    assert diagnostics[0].spell_id == "dep"
    assert diagnostics[0].root_id == "root"


def test_component_broken_spell_in_dag_reports_multiple_broken() -> None:
    """
    Purpose:
        Validate BrokenSpellInDagStrategy reports each broken spell id.
    Contract:
        - Each broken spell id produces a diagnostic.
    Returns:
        None.
    """
    strategy = BrokenSpellInDagStrategy()
    blueprint = _make_blueprint(root_id="root", edges={"root": {"dep-a", "dep-b"}})
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index(
            {"root": {"dep-a", "dep-b"}, "dep-a": set(), "dep-b": set()},
            root_ids={"root"},
        ),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids={"dep-a", "dep-b"},
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    codes = {(diag.code, diag.spell_id) for diag in diagnostics}
    assert codes == {("broken_spell_in_dag", "dep-a"), ("broken_spell_in_dag", "dep-b")}


def test_component_broken_spell_in_dag_reports_across_roots() -> None:
    """
    Purpose:
        Validate BrokenSpellInDagStrategy reports broken spells per root.
    Contract:
        - The same broken spell id yields diagnostics for each root DAG.
    Returns:
        None.
    """
    strategy = BrokenSpellInDagStrategy()
    blueprint_a = _make_blueprint(root_id="root-a", edges={"root-a": {"dep"}})
    blueprint_b = _make_blueprint(root_id="root-b", edges={"root-b": {"dep"}})
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index(
            {"root-a": {"dep"}, "root-b": {"dep"}, "dep": set()},
            root_ids={"root-a", "root-b"},
        ),
        blueprints={"root-a": blueprint_a, "root-b": blueprint_b},
        phase4_results={},
        broken_spell_ids={"dep"},
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    roots = {diag.root_id for diag in diagnostics}
    assert roots == {"root-a", "root-b"}


def test_component_broken_spell_in_dag_honors_cancellation() -> None:
    """
    Purpose:
        Validate BrokenSpellInDagStrategy honors cancellation.
    Contract:
        - Cancellation raises OperationCancelledError.
    Returns:
        None.
    """
    strategy = BrokenSpellInDagStrategy()
    blueprint = _make_blueprint(root_id="root", edges={"root": {"dep"}})
    diagnostics: list[SystemDiagnostic] = []
    signal = CancellationEventSignal()
    signal.cancel()
    try:
        with pytest.raises(OperationCancelledError):
            strategy.run(
                index=_make_index({"root": {"dep"}, "dep": set()}, root_ids={"root"}),
                blueprints={"root": blueprint},
                phase4_results={},
                broken_spell_ids={"dep"},
                diagnostics=diagnostics,
                spell_system_states=None,
                spell_lookup={},
                cancel_event=signal.event,
            )
    finally:
        signal.cleanup()


def test_component_cycle_detection_no_cycle_is_noop() -> None:
    """
    Purpose:
        Validate CycleDetectionStrategy does not report acyclic graphs.
    Contract:
        - Diagnostics remain empty when no cycle exists.
    Returns:
        None.
    """
    strategy = CycleDetectionStrategy()
    index = _make_index({"root": {"dep"}, "dep": set()}, root_ids={"root"})
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=index,
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert diagnostics == []


def test_component_cycle_detection_reports_cycle() -> None:
    """
    Purpose:
        Validate CycleDetectionStrategy reports cycles.
    Contract:
        - cycle_detected is appended when a cycle exists.
    Returns:
        None.
    """
    strategy = CycleDetectionStrategy()
    index = _make_index({"a": {"b"}, "b": {"a"}}, root_ids={"a"})
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=index,
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert [diag.code for diag in diagnostics] == ["cycle_detected"]


def test_component_cycle_detection_disconnected_nodes_no_cycle() -> None:
    """
    Purpose:
        Validate CycleDetectionStrategy handles disconnected nodes.
    Contract:
        - No diagnostics are emitted for isolated nodes.
    Returns:
        None.
    """
    strategy = CycleDetectionStrategy()
    index = _make_index({"a": set(), "b": set()}, root_ids={"a", "b"})
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=index,
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert diagnostics == []


def test_component_cycle_detection_allows_unknown_dependency() -> None:
    """
    Purpose:
        Validate CycleDetectionStrategy tolerates unknown dependency ids.
    Contract:
        - A missing dependency id does not cause a cycle diagnostic.
    Returns:
        None.
    """
    strategy = CycleDetectionStrategy()
    index = _make_index({"root": {"ghost"}}, root_ids={"root"})
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=index,
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert diagnostics == []


def test_component_cycle_detection_honors_cancellation() -> None:
    """
    Purpose:
        Validate CycleDetectionStrategy honors cancellation.
    Contract:
        - Cancellation raises OperationCancelledError.
    Returns:
        None.
    """
    strategy = CycleDetectionStrategy()
    index = _make_index({"a": {"b"}, "b": set()}, root_ids={"a"})
    diagnostics: list[SystemDiagnostic] = []
    signal = CancellationEventSignal()
    signal.cancel()
    try:
        with pytest.raises(OperationCancelledError):
            strategy.run(
                index=index,
                blueprints={},
                phase4_results={},
                broken_spell_ids=set(),
                diagnostics=diagnostics,
                spell_system_states=None,
                spell_lookup={},
                cancel_event=signal.event,
            )
    finally:
        signal.cleanup()


def test_component_graph_consistency_no_diagnostics_for_match() -> None:
    """
    Purpose:
        Validate GraphConsistencyStrategy reports no issues for matching graphs.
    Contract:
        - No diagnostics are emitted when index and blueprint align.
    Returns:
        None.
    """
    strategy = GraphConsistencyStrategy()
    index = _make_index({"root": {"dep"}, "dep": set()}, root_ids={"root"})
    blueprint = _make_blueprint(root_id="root", edges={"root": {"dep"}})
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=index,
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert diagnostics == []


def test_component_graph_consistency_reports_missing_child_node() -> None:
    """
    Purpose:
        Validate GraphConsistencyStrategy reports blueprint nodes missing in index.
    Contract:
        - missing_index_node is emitted for the missing child node.
    Returns:
        None.
    """
    strategy = GraphConsistencyStrategy()
    index = _make_index({"root": set()}, root_ids={"root"})
    blueprint = _make_blueprint(
        root_id="root",
        edges={},
        extra_nodes={"root", "missing"},
    )
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=index,
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    codes = {diag.code for diag in diagnostics}
    assert codes == {"missing_index_node"}


def test_component_graph_consistency_reports_missing_parent_node() -> None:
    """
    Purpose:
        Validate GraphConsistencyStrategy reports missing parent nodes.
    Contract:
        - missing_index_node is emitted for a parent missing from the index.
    Returns:
        None.
    """
    strategy = GraphConsistencyStrategy()
    index = _make_index({"root": {"parent"}}, root_ids={"root"})
    blueprint = _make_blueprint(root_id="root", edges={"root": {"parent"}})
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=index,
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert {diag.code for diag in diagnostics} == {"missing_index_node"}


def test_component_graph_consistency_reports_edge_mismatch() -> None:
    """
    Purpose:
        Validate GraphConsistencyStrategy reports edge mismatch against index.
    Contract:
        - edge_mismatch_index is emitted when blueprint has an unexpected edge.
    Returns:
        None.
    """
    strategy = GraphConsistencyStrategy()
    index = _make_index({"root": set(), "dep": set()}, root_ids={"root"})
    blueprint = _make_blueprint(root_id="root", edges={"root": {"dep"}})
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=index,
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert {diag.code for diag in diagnostics} == {"edge_mismatch_index"}


def test_component_graph_consistency_reports_edge_missing_from_blueprint() -> None:
    """
    Purpose:
        Validate GraphConsistencyStrategy reports index edges missing from blueprints.
    Contract:
        - edge_missing_from_blueprint is emitted for unrepresented index edges.
    Returns:
        None.
    """
    strategy = GraphConsistencyStrategy()
    index = _make_index({"root": {"dep"}, "dep": set()}, root_ids={"root"})
    blueprint = _make_blueprint(
        root_id="root",
        edges={},
        extra_nodes={"root", "dep"},
    )
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=index,
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert {diag.code for diag in diagnostics} == {"edge_missing_from_blueprint"}


def test_component_missing_phase4_no_missing_results() -> None:
    """
    Purpose:
        Validate MissingPhase4Strategy reports no issues when results exist.
    Contract:
        - Diagnostics remain empty when all nodes have phase4 results.
    Returns:
        None.
    """
    strategy = MissingPhase4Strategy()
    blueprint = _make_blueprint(root_id="root", edges={"root": {"dep"}})
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index({"root": {"dep"}, "dep": set()}, root_ids={"root"}),
        blueprints={"root": blueprint},
        phase4_results={"root": object(), "dep": object()},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert diagnostics == []


def test_component_missing_phase4_reports_single_missing() -> None:
    """
    Purpose:
        Validate MissingPhase4Strategy reports a missing phase4 result.
    Contract:
        - missing_phase4_validation is emitted for the missing node.
    Returns:
        None.
    """
    strategy = MissingPhase4Strategy()
    blueprint = _make_blueprint(root_id="root", edges={"root": {"dep"}})
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index({"root": {"dep"}, "dep": set()}, root_ids={"root"}),
        blueprints={"root": blueprint},
        phase4_results={"root": object()},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert [diag.code for diag in diagnostics] == ["missing_phase4_validation"]
    assert diagnostics[0].spell_id == "dep"
    assert diagnostics[0].root_id == "root"


def test_component_missing_phase4_reports_multiple_missing() -> None:
    """
    Purpose:
        Validate MissingPhase4Strategy reports each missing node.
    Contract:
        - Diagnostics are emitted for all missing nodes in the DAG.
    Returns:
        None.
    """
    strategy = MissingPhase4Strategy()
    blueprint = _make_blueprint(
        root_id="root",
        edges={"root": {"dep-a", "dep-b"}},
    )
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index(
            {"root": {"dep-a", "dep-b"}, "dep-a": set(), "dep-b": set()},
            root_ids={"root"},
        ),
        blueprints={"root": blueprint},
        phase4_results={"root": object()},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert {diag.spell_id for diag in diagnostics} == {"dep-a", "dep-b"}


def test_component_missing_phase4_reports_missing_per_root() -> None:
    """
    Purpose:
        Validate MissingPhase4Strategy reports missing nodes for each root.
    Contract:
        - Missing nodes are reported once per root blueprint.
    Returns:
        None.
    """
    strategy = MissingPhase4Strategy()
    blueprint_a = _make_blueprint(root_id="root-a", edges={"root-a": {"dep"}})
    blueprint_b = _make_blueprint(root_id="root-b", edges={"root-b": {"dep"}})
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index(
            {"root-a": {"dep"}, "root-b": {"dep"}, "dep": set()},
            root_ids={"root-a", "root-b"},
        ),
        blueprints={"root-a": blueprint_a, "root-b": blueprint_b},
        phase4_results={"root-a": object(), "root-b": object()},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    roots = {diag.root_id for diag in diagnostics}
    assert roots == {"root-a", "root-b"}


def test_component_missing_phase4_honors_cancellation() -> None:
    """
    Purpose:
        Validate MissingPhase4Strategy honors cancellation.
    Contract:
        - Cancellation raises OperationCancelledError.
    Returns:
        None.
    """
    strategy = MissingPhase4Strategy()
    blueprint = _make_blueprint(root_id="root", edges={"root": {"dep"}})
    diagnostics: list[SystemDiagnostic] = []
    signal = CancellationEventSignal()
    signal.cancel()
    try:
        with pytest.raises(OperationCancelledError):
            strategy.run(
                index=_make_index({"root": {"dep"}, "dep": set()}, root_ids={"root"}),
                blueprints={"root": blueprint},
                phase4_results={"root": object()},
                broken_spell_ids=set(),
                diagnostics=diagnostics,
                spell_system_states=None,
                spell_lookup={},
                cancel_event=signal.event,
            )
    finally:
        signal.cleanup()


def test_component_root_viability_emits_for_root_error() -> None:
    """
    Purpose:
        Validate RootViabilityStrategy emits diagnostics for root-scoped errors.
    Contract:
        - root_not_viable is added for a root with existing errors.
    Returns:
        None.
    """
    strategy = RootViabilityStrategy()
    blueprint = _make_blueprint(root_id="root", edges={})
    diagnostics = [
        SystemDiagnostic(
            code="pre_error",
            message="pre error",
            severity=SystemDiagnosticSeverity.ERROR,
            root_id="root",
        )
    ]

    strategy.run(
        index=_make_index({"root": set()}, root_ids={"root"}),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    codes = [diag.code for diag in diagnostics]
    assert "root_not_viable" in codes


def test_component_root_viability_ignores_warnings() -> None:
    """
    Purpose:
        Validate RootViabilityStrategy ignores warning diagnostics.
    Contract:
        - root_not_viable is not emitted for warnings.
    Returns:
        None.
    """
    strategy = RootViabilityStrategy()
    blueprint = _make_blueprint(root_id="root", edges={})
    diagnostics = [
        SystemDiagnostic(
            code="pre_warning",
            message="pre warning",
            severity=SystemDiagnosticSeverity.WARNING,
            root_id="root",
        )
    ]

    strategy.run(
        index=_make_index({"root": set()}, root_ids={"root"}),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert {diag.code for diag in diagnostics} == {"pre_warning"}


def test_component_root_viability_ignores_unscoped_errors() -> None:
    """
    Purpose:
        Validate RootViabilityStrategy ignores unscoped errors.
    Contract:
        - root_not_viable is not emitted for errors without root_id.
    Returns:
        None.
    """
    strategy = RootViabilityStrategy()
    blueprint = _make_blueprint(root_id="root", edges={})
    diagnostics = [
        SystemDiagnostic(
            code="pre_error",
            message="pre error",
            severity=SystemDiagnosticSeverity.ERROR,
            root_id=None,
        )
    ]

    strategy.run(
        index=_make_index({"root": set()}, root_ids={"root"}),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert {diag.code for diag in diagnostics} == {"pre_error"}


def test_component_root_viability_emits_only_for_matching_root() -> None:
    """
    Purpose:
        Validate RootViabilityStrategy emits diagnostics for matching roots.
    Contract:
        - Only roots with existing errors receive root_not_viable.
    Returns:
        None.
    """
    strategy = RootViabilityStrategy()
    blueprint_a = _make_blueprint(root_id="root-a", edges={})
    blueprint_b = _make_blueprint(root_id="root-b", edges={})
    diagnostics = [
        SystemDiagnostic(
            code="pre_error",
            message="pre error",
            severity=SystemDiagnosticSeverity.ERROR,
            root_id="root-a",
        )
    ]

    strategy.run(
        index=_make_index({"root-a": set(), "root-b": set()}, root_ids={"root-a", "root-b"}),
        blueprints={"root-a": blueprint_a, "root-b": blueprint_b},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    root_not_viable = [diag for diag in diagnostics if diag.code == "root_not_viable"]
    assert len(root_not_viable) == 1
    assert root_not_viable[0].root_id == "root-a"


def test_component_root_viability_emits_once_per_root() -> None:
    """
    Purpose:
        Validate RootViabilityStrategy emits a single root_not_viable per root.
    Contract:
        - Multiple errors for the same root still produce one root_not_viable.
    Returns:
        None.
    """
    strategy = RootViabilityStrategy()
    blueprint = _make_blueprint(root_id="root", edges={})
    diagnostics = [
        SystemDiagnostic(
            code="pre_error_a",
            message="pre error a",
            severity=SystemDiagnosticSeverity.ERROR,
            root_id="root",
        ),
        SystemDiagnostic(
            code="pre_error_b",
            message="pre error b",
            severity=SystemDiagnosticSeverity.ERROR,
            root_id="root",
        ),
    ]

    strategy.run(
        index=_make_index({"root": set()}, root_ids={"root"}),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    root_not_viable = [diag for diag in diagnostics if diag.code == "root_not_viable"]
    assert len(root_not_viable) == 1


def test_component_socket_ref_sanity_no_issues_for_valid_index() -> None:
    """
    Purpose:
        Validate SocketRefSanityStrategy reports no issues for valid sockets.
    Contract:
        - Diagnostics remain empty for matching socket refs and DagIndex.
    Returns:
        None.
    """
    strategy = SocketRefSanityStrategy()
    blueprint = _make_blueprint(root_id="root", edges={"root": {"dep"}})
    socket = _make_socket_ref(
        node_id="root",
        name="service",
        path=("service",),
        path_registry=blueprint.path_registry,
    )
    blueprint.add_socket_ref(socket)
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index({"root": {"dep"}, "dep": set()}, root_ids={"root"}),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert diagnostics == []


def test_component_socket_ref_sanity_reports_duplicate_socket_ref() -> None:
    """
    Purpose:
        Validate SocketRefSanityStrategy reports duplicate socket refs.
    Contract:
        - socket_ref_duplicate is emitted for repeated SocketRefs.
    Returns:
        None.
    """
    strategy = SocketRefSanityStrategy()
    blueprint = _make_blueprint(root_id="root", edges={"root": {"dep"}})
    socket = _make_socket_ref(
        node_id="root",
        name="service",
        path=("service",),
        path_registry=blueprint.path_registry,
    )
    blueprint.add_socket_ref(socket)
    blueprint.add_socket_ref(socket)
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index({"root": {"dep"}, "dep": set()}, root_ids={"root"}),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert {diag.code for diag in diagnostics} == {"socket_ref_duplicate"}


def test_component_socket_ref_sanity_reports_missing_index_entries() -> None:
    """
    Purpose:
        Validate SocketRefSanityStrategy reports missing DagIndex entries.
    Contract:
        - socket_ref_missing_in_index and socket_ref_missing_in_index_name are emitted.
    Returns:
        None.
    """
    strategy = SocketRefSanityStrategy()
    blueprint = _make_blueprint(root_id="root", edges={"root": {"dep"}})
    path_registry = blueprint.path_registry
    socket = _make_socket_ref(
        node_id="root",
        name="service",
        path=("service",),
        path_registry=path_registry,
    )
    blueprint.add_socket_ref(socket)
    blueprint.replace_dag_index(DagIndex(path_registry=path_registry))
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index({"root": {"dep"}, "dep": set()}, root_ids={"root"}),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    codes = {diag.code for diag in diagnostics}
    assert "socket_ref_missing_in_index" in codes
    assert "socket_ref_missing_in_index_name" in codes


def test_component_socket_ref_sanity_reports_orphan_index_socket() -> None:
    """
    Purpose:
        Validate SocketRefSanityStrategy reports orphan DagIndex sockets.
    Contract:
        - dag_index_orphan_socket is emitted for index-only sockets.
    Returns:
        None.
    """
    strategy = SocketRefSanityStrategy()
    blueprint = _make_blueprint(root_id="root", edges={"root": {"dep"}})
    orphan = _make_socket_ref(
        node_id="root",
        name="orphan",
        path=("orphan",),
        path_registry=blueprint.path_registry,
    )
    blueprint.dag_index.add_socket(orphan)
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index({"root": {"dep"}, "dep": set()}, root_ids={"root"}),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert {diag.code for diag in diagnostics} == {"dag_index_orphan_socket"}


def test_component_socket_ref_sanity_scopes_diagnostics_to_root() -> None:
    """
    Purpose:
        Validate SocketRefSanityStrategy scopes diagnostics to the offending root.
    Contract:
        - Diagnostics reference only the root with socket issues.
    Returns:
        None.
    """
    strategy = SocketRefSanityStrategy()
    blueprint_a = _make_blueprint(root_id="root-a", edges={"root-a": {"dep"}})
    blueprint_b = _make_blueprint(root_id="root-b", edges={"root-b": {"dep"}})
    socket = _make_socket_ref(
        node_id="root-a",
        name="service",
        path=("service",),
        path_registry=blueprint_a.path_registry,
    )
    blueprint_a.add_socket_ref(socket)
    blueprint_a.add_socket_ref(socket)
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index(
            {"root-a": {"dep"}, "root-b": {"dep"}, "dep": set()},
            root_ids={"root-a", "root-b"},
        ),
        blueprints={"root-a": blueprint_a, "root-b": blueprint_b},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    roots = {diag.root_id for diag in diagnostics}
    assert roots == {"root-a"}


def test_component_root_reachability_no_orphans() -> None:
    """
    Purpose:
        Validate RootReachabilityStrategy reports no issues for reachable DAGs.
    Contract:
        - Diagnostics remain empty when all nodes are reachable from the root.
    Returns:
        None.
    """
    strategy = RootReachabilityStrategy()
    blueprint = _make_blueprint(root_id="root", edges={"root": {"dep"}})
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index({"root": {"dep"}, "dep": set()}, root_ids={"root"}),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert diagnostics == []


def test_component_root_reachability_reports_missing_root() -> None:
    """
    Purpose:
        Validate RootReachabilityStrategy reports a missing root in the DAG.
    Contract:
        - root_missing_in_dag is emitted when the root is not present.
    Returns:
        None.
    """
    strategy = RootReachabilityStrategy()
    blueprint = _make_blueprint(root_id="root", edges={}, extra_nodes={"orphan"})
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index({"orphan": set()}, root_ids=set()),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert [diag.code for diag in diagnostics] == ["root_missing_in_dag"]


def test_component_root_reachability_reports_orphan_nodes() -> None:
    """
    Purpose:
        Validate RootReachabilityStrategy reports orphan DAG nodes.
    Contract:
        - dag_orphan_node is emitted for nodes not reachable from the root.
    Returns:
        None.
    """
    strategy = RootReachabilityStrategy()
    blueprint = _make_blueprint(
        root_id="root",
        edges={"root": {"dep"}},
        extra_nodes={"orphan"},
    )
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index({"root": {"dep"}, "dep": set(), "orphan": set()}, root_ids={"root"}),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    codes = {diag.code for diag in diagnostics}
    assert codes == {"dag_orphan_node"}
    assert {diag.spell_id for diag in diagnostics} == {"orphan"}


def test_component_root_coverage_reports_missing_root_in_index() -> None:
    """
    Purpose:
        Validate RootCoverageStrategy reports missing root entries.
    Contract:
        - root_missing_in_index is emitted when a blueprint root is absent from the index.
    Returns:
        None.
    """
    strategy = RootCoverageStrategy()
    blueprint = _make_blueprint(root_id="root", edges={})
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index({"other": set()}, root_ids=set()),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert {diag.code for diag in diagnostics} == {"root_missing_in_index"}


def test_component_root_coverage_reports_unmarked_root() -> None:
    """
    Purpose:
        Validate RootCoverageStrategy reports roots not flagged in the index.
    Contract:
        - root_not_marked_in_index is emitted when the index node is not a root.
    Returns:
        None.
    """
    strategy = RootCoverageStrategy()
    blueprint = _make_blueprint(root_id="root", edges={})
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index({"root": set()}, root_ids=set()),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert {diag.code for diag in diagnostics} == {"root_not_marked_in_index"}


def test_component_root_coverage_reports_missing_blueprint() -> None:
    """
    Purpose:
        Validate RootCoverageStrategy reports roots missing blueprints.
    Contract:
        - missing_root_blueprint is emitted when the index marks a root without a blueprint.
    Returns:
        None.
    """
    strategy = RootCoverageStrategy()
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index({"root": set()}, root_ids={"root"}),
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert {diag.code for diag in diagnostics} == {"missing_root_blueprint"}


def test_component_index_dependency_sanity_reports_missing_dependency() -> None:
    """
    Purpose:
        Validate IndexDependencySanityStrategy reports missing dependencies.
    Contract:
        - missing_index_dependency is emitted when a dependency id is unknown.
    Returns:
        None.
    """
    strategy = IndexDependencySanityStrategy()
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index({"root": {"missing"}}, root_ids={"root"}),
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert {diag.code for diag in diagnostics} == {"missing_index_dependency"}


def test_component_index_dependency_sanity_no_missing_dependencies() -> None:
    """
    Purpose:
        Validate IndexDependencySanityStrategy ignores complete graphs.
    Contract:
        - Diagnostics remain empty when dependencies exist in the index.
    Returns:
        None.
    """
    strategy = IndexDependencySanityStrategy()
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index({"root": {"dep"}, "dep": set()}, root_ids={"root"}),
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert diagnostics == []


def test_component_lineage_alignment_reports_mismatch() -> None:
    """
    Purpose:
        Validate LineageAlignmentStrategy reports lineage mismatches.
    Contract:
        - root_lineage_mismatch is emitted when root lineage ids diverge.
    Returns:
        None.
    """
    strategy = LineageAlignmentStrategy()
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-other",
        edges={},
    )
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index({"root": set()}, root_ids={"root"}),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert {diag.code for diag in diagnostics} == {"root_lineage_mismatch"}


def test_component_lineage_alignment_ignores_missing_lineage() -> None:
    """
    Purpose:
        Validate LineageAlignmentStrategy skips roots without lineage metadata.
    Contract:
        - Diagnostics remain empty when root_lineage_id is None.
    Returns:
        None.
    """
    strategy = LineageAlignmentStrategy()
    blueprint = _make_blueprint(root_id="root", root_lineage_id=None, edges={})
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index({"root": set()}, root_ids={"root"}),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert diagnostics == []


def test_component_lineage_alignment_ignores_matching_lineage() -> None:
    """
    Purpose:
        Validate LineageAlignmentStrategy ignores matching lineage ids.
    Contract:
        - Diagnostics remain empty when lineage ids match.
    Returns:
        None.
    """
    strategy = LineageAlignmentStrategy()
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-root",
        edges={},
    )
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index({"root": set()}, root_ids={"root"}),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert diagnostics == []


def test_component_root_scale_limit_reports_node_limit() -> None:
    """
    Purpose:
        Validate RootScaleLimitStrategy reports node count limits.
    Contract:
        - root_dag_node_limit_exceeded is emitted for oversized DAGs.
    Returns:
        None.
    """
    strategy = RootScaleLimitStrategy(
        max_nodes=3,
        max_edges=100,
        max_depth=100,
        max_fan_out=100,
    )
    blueprint = _make_blueprint(
        root_id="root",
        edges={"root": {"svc-a", "svc-b"}, "svc-a": {"shared"}, "svc-b": {"shared"}},
    )
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index(
            {"root": {"svc-a", "svc-b"}, "svc-a": {"shared"}, "svc-b": {"shared"}, "shared": set()},
            root_ids={"root"},
        ),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert {diag.code for diag in diagnostics} == {"root_dag_node_limit_exceeded"}
    assert diagnostics[0].severity is SystemDiagnosticSeverity.WARNING


def test_component_root_scale_limit_reports_edge_limit() -> None:
    """
    Purpose:
        Validate RootScaleLimitStrategy reports edge count limits.
    Contract:
        - root_dag_edge_limit_exceeded is emitted when edges exceed the limit.
    Returns:
        None.
    """
    strategy = RootScaleLimitStrategy(
        max_nodes=100,
        max_edges=1,
        max_depth=100,
        max_fan_out=100,
    )
    blueprint = _make_blueprint(root_id="root", edges={"root": {"dep-a", "dep-b"}})
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index({"root": {"dep-a", "dep-b"}, "dep-a": set(), "dep-b": set()}, root_ids={"root"}),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert {diag.code for diag in diagnostics} == {"root_dag_edge_limit_exceeded"}


def test_component_root_scale_limit_reports_depth_limit() -> None:
    """
    Purpose:
        Validate RootScaleLimitStrategy reports depth limits.
    Contract:
        - root_dag_depth_limit_exceeded is emitted when depth exceeds the limit.
    Returns:
        None.
    """
    strategy = RootScaleLimitStrategy(
        max_nodes=100,
        max_edges=100,
        max_depth=2,
        max_fan_out=100,
    )
    blueprint = _make_blueprint(
        root_id="root",
        edges={"root": {"a"}, "a": {"b"}, "b": {"c"}},
    )
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index({"root": {"a"}, "a": {"b"}, "b": {"c"}, "c": set()}, root_ids={"root"}),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert {diag.code for diag in diagnostics} == {"root_dag_depth_limit_exceeded"}


def test_component_root_scale_limit_reports_fan_out_limit() -> None:
    """
    Purpose:
        Validate RootScaleLimitStrategy reports fan-out limits.
    Contract:
        - root_dag_fan_out_limit_exceeded is emitted when fan-out exceeds the limit.
    Returns:
        None.
    """
    strategy = RootScaleLimitStrategy(
        max_nodes=100,
        max_edges=100,
        max_depth=100,
        max_fan_out=1,
    )
    blueprint = _make_blueprint(
        root_id="root",
        edges={"root": {"svc-a", "svc-b"}, "svc-a": {"shared"}, "svc-b": {"shared"}},
    )
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index(
            {"root": {"svc-a", "svc-b"}, "svc-a": {"shared"}, "svc-b": {"shared"}, "shared": set()},
            root_ids={"root"},
        ),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert {diag.code for diag in diagnostics} == {"root_dag_fan_out_limit_exceeded"}


def test_component_index_coverage_reports_orphan_index_node() -> None:
    """
    Purpose:
        Validate IndexCoverageStrategy reports index nodes missing from blueprints.
    Contract:
        - index_node_missing_from_blueprints is emitted for orphan index nodes.
    Returns:
        None.
    """
    strategy = IndexCoverageStrategy()
    blueprint = _make_blueprint(root_id="root", edges={})
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index({"root": set(), "orphan": set()}, root_ids={"root"}),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert {diag.code for diag in diagnostics} == {"index_node_missing_from_blueprints"}


def test_component_root_lineage_conflict_reports_duplicates() -> None:
    """
    Purpose:
        Validate RootLineageConflictStrategy reports multiple roots per lineage.
    Contract:
        - root_lineage_conflict is emitted for each root sharing a lineage.
    Returns:
        None.
    """
    strategy = RootLineageConflictStrategy()
    blueprint_a = _make_blueprint(root_id="root-a", edges={})
    blueprint_b = _make_blueprint(root_id="root-b", edges={})
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index(
            {"root-a": set(), "root-b": set()},
            root_ids={"root-a", "root-b"},
            lineage_map={"root-a": "lineage-x", "root-b": "lineage-x"},
        ),
        blueprints={"root-a": blueprint_a, "root-b": blueprint_b},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert {diag.code for diag in diagnostics} == {"root_lineage_conflict"}
    assert {diag.root_id for diag in diagnostics} == {"root-a", "root-b"}


def test_component_lineage_version_conflict_reports_multiple_versions() -> None:
    """
    Purpose:
        Validate LineageVersionConflictStrategy reports multiple versions in a root DAG.
    Contract:
        - lineage_version_conflict is emitted when a lineage appears twice.
    Returns:
        None.
    """
    strategy = LineageVersionConflictStrategy()
    blueprint = _make_blueprint(root_id="root", edges={"root": {"v1", "v2"}})
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index(
            {"root": {"v1", "v2"}, "v1": set(), "v2": set()},
            root_ids={"root"},
            lineage_map={"root": "lineage-root", "v1": "lineage-shared", "v2": "lineage-shared"},
        ),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert {diag.code for diag in diagnostics} == {"lineage_version_conflict"}


def test_component_dependency_type_sanity_reports_callable_dependency() -> None:
    """
    Purpose:
        Validate DependencyTypeSanityStrategy warns on callable dependencies.
    Contract:
        - dependency_type_unexpected is emitted for method/lambda dependencies.
    Returns:
        None.
    """
    strategy = DependencyTypeSanityStrategy()
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index(
            {"root": {"dep"}, "dep": set()},
            root_ids={"root"},
            spell_types={"dep": SpellType.METHOD},
        ),
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert {diag.code for diag in diagnostics} == {"dependency_type_unexpected"}
    assert diagnostics[0].severity is SystemDiagnosticSeverity.WARNING


def test_component_ownership_consistency_reports_conflicts() -> None:
    """
    Purpose:
        Validate OwnershipConsistencyStrategy reports conflicting conduit owners.
    Contract:
        - lineage_conduit_conflict is emitted when multiple conduits share a lineage.
    Returns:
        None.
    """
    strategy = OwnershipConsistencyStrategy()
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index(
            {"v1": set(), "v2": set()},
            root_ids=set(),
            lineage_map={"v1": "lineage-a", "v2": "lineage-a"},
            conduit_ids={"v1": "conduit-a", "v2": "conduit-b"},
        ),
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert {diag.code for diag in diagnostics} == {"lineage_conduit_conflict"}


def test_component_ownership_consistency_ignores_unknown_conduit() -> None:
    """
    Purpose:
        Validate OwnershipConsistencyStrategy ignores unknown conduit ids.
    Contract:
        - Diagnostics remain empty when only one conduit id is known.
    Returns:
        None.
    """
    strategy = OwnershipConsistencyStrategy()
    diagnostics: list[SystemDiagnostic] = []

    strategy.run(
        index=_make_index(
            {"v1": set(), "v2": set()},
            root_ids=set(),
            lineage_map={"v1": "lineage-a", "v2": "lineage-a"},
            conduit_ids={"v1": "conduit-a"},
        ),
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        spell_system_states=None,
        spell_lookup={},
        cancel_event=None,
    )

    assert diagnostics == []


