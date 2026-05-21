from typing import Any, Dict, List, Optional, Set, Tuple
from types import SimpleNamespace

from melder.aether.aetheric_frame.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.aether.spellbook.spell_compiler.blueprints.injection_plan import (
    InjectionPlanBuilder,
)
from melder.aether.spellbook.spell_compiler.blueprints.occurrence_plan import (
    OccurrencePlan,
)
from melder.aether.spellbook.spell_compiler.blueprints.occurrence_plan import (
    OccurrencePlanBuilder,
)
from melder.aether.spellbook.spell_compiler.dag.dag_index import DagIndex, PathRegistry, SocketRef
from melder.aether.spellbook.spell_compiler.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import (
    SpellLocalTopology,
    SpellSocketDescriptor,
)
from melder.aether.spellbook.existence.existence import Existence


class _StubConfiguration:
    """
    Purpose:
        Provide the minimum Configuration surface used by occurrence planning.
    Contract:
        - Stores a fixed SystemState value.
        - get_property returns that value for any key.
    Lifecycle:
        - Test-only stub; no cleanup required.
    """

    def __init__(self, system_state: SystemState) -> None:
        """
        Purpose:
            Capture a fixed system_state value for test lookups.
        Contract:
            - Stores the provided system_state without validation.
            - Intended only for occurrence-plan unit tests.
        Args:
            system_state: SystemState enum to return from get_property.
        Returns:
            None.
        """
        self._system_state = system_state

    def get_property(self, name: str) -> SystemState:
        """
        Purpose:
            Provide a minimal configuration lookup for system_state.
        Contract:
            - Returns the stored system_state for any property name.
        Args:
            name: Configuration property key (ignored by this stub).
        Returns:
            SystemState: Stored system_state enum value.
        """
        return self._system_state


class _StubSpellbook:
    """
    Purpose:
        Provide the minimal Spellbook surface used during occurrence planning.
    Contract:
        - Exposes _configuration and empty contract maps.
        - Contract maps remain empty for these tests.
    Lifecycle:
        - Test-only stub; no cleanup required.
    """

    def __init__(self, system_state: SystemState) -> None:
        """
        Purpose:
            Provide the minimum Spellbook surface used by occurrence planning.
        Contract:
            - Exposes _configuration, _lookup_contracted_spells, _contracted_spells.
            - Contract maps are empty for these tests.
        Args:
            system_state: SystemState enum for configuration lookup.
        Returns:
            None.
        """
        self._configuration = _StubConfiguration(system_state)
        self._aetheric_frame_configuration = AethericFrameConfiguration(
            origin_spellbook_id="spellbook-stub",
            system_state=system_state,
            ai_native_enabled=False,
            rift_enabled=False,
        )
        self._lookup_contracted_spells: Dict[Any, Dict[Any, Any]] = {}
        self._contracted_spells: Dict[Any, Dict[Any, Any]] = {}


class _StubSpell:
    """
    Purpose:
        Provide a minimal Spell surface for occurrence planning.
    Contract:
        - Exposes spell_index.current, spell_name, spell callable, existence,
          and mutation_override.
        - The spell callable defines no SpellContract defaults.
    Lifecycle:
        - Test-only stub; no cleanup required.
    """

    def __init__(
            self,
            spell_id: str,
            spellbook: _StubSpellbook,
            *,
            existence: Existence,
            mutation_override: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Purpose:
            Provide a minimal Spell-like surface for occurrence planning.
        Contract:
            - Exposes spell_index.current, spell_name, spell callable, existence,
              and mutation_override (None).
            - The callable has no SpellContract defaults.
        Args:
            spell_id: Version id for the stub spell.
            spellbook: Owning spellbook stub.
            existence: Existence value for the stub spell.
            mutation_override:
                Optional mutation override payload. Empty or None means no override.
        Returns:
            None.
        """
        self.spell_index = type("SpellIndexStub", (), {"current": spell_id})()
        self.spell_name = spell_id

        def _callable() -> None:
            """
            Purpose:
                Provide a no-arg callable with no default parameters.
            Contract:
                - Returns None.
            Returns:
                None.
            """
            return None

        self.spell = _callable
        self.mutation_override = mutation_override or {}
        self.existence = existence
        self._spellbook = spellbook


class _StubSystemStates:
    """
    Purpose:
        Provide a minimal SpellSystemStates surface for local topology lookup.
    Contract:
        - Exposes _local_topologies keyed by spell_id.
    Lifecycle:
        - Test-only stub; no cleanup required.
    """

    def __init__(self, local_topologies: Dict[str, SpellLocalTopology]) -> None:
        """
        Purpose:
            Provide a minimal SpellSystemStates surface for local topology lookup.
        Contract:
            - Exposes _local_topologies mapping keyed by spell_id.
        Args:
            local_topologies:
                Mapping from spell_id to SpellLocalTopology instances.
        Returns:
            None.
        """
        self._local_topologies = local_topologies


def _path_id(path_registry: PathRegistry, path: Tuple[str, ...]) -> int:
    """
    Build a path id for the provided path segments using the registry.
    """
    path_id = path_registry.root_path_id
    for segment in path:
        path_id = path_registry.extend_path(path_id, segment)
    return path_id


def test_occurrence_plan_execution_order_linear_chain() -> None:
    """
    Purpose:
        Ensure execution order remains topologically correct for a simple chain.
    Contract:
        - Dependencies appear before dependents in the order output.
        - Linear chains preserve the only valid topological order.
    Returns:
        None.
    """
    path_registry = PathRegistry()
    root_path_id = path_registry.root_path_id
    occurrence_graph = {
        ("C", root_path_id): {"dep": [("B", root_path_id)]},
        ("B", root_path_id): {"dep": [("A", root_path_id)]},
        ("A", root_path_id): {},
    }

    order = OccurrencePlanBuilder._build_execution_order(
        occurrence_graph=occurrence_graph,
        fallback_order=[],
    )

    assert order == ["A", "B", "C"]


def test_occurrence_plan_execution_order_uses_lexical_tie_break() -> None:
    """
    Purpose:
        Ensure independent nodes use deterministic lexical ordering.
    Contract:
        - Unrelated zero-indegree nodes are ordered lexically.
    Returns:
        None.
    """
    path_registry = PathRegistry()
    root_path_id = path_registry.root_path_id
    occurrence_graph = {
        ("root", root_path_id): {"left": [("b", root_path_id)], "right": [("a", root_path_id)]},
        ("b", root_path_id): {},
        ("a", root_path_id): {},
    }

    order = OccurrencePlanBuilder._build_execution_order(
        occurrence_graph=occurrence_graph,
        fallback_order=[],
    )

    assert order == ["a", "b", "root"]


def test_dag_index_exact_path_lookup_accepts_list_and_tuple() -> None:
    """
    Purpose:
        Verify DagIndex exact-path lookups work with list and tuple inputs.
    Contract:
        - Tuple path and list path resolve to the same sockets.
        - Single-segment paths resolve as expected.
    Returns:
        None.
    """
    index = DagIndex()
    path_registry = index.path_registry
    deep_socket = SocketRef(
        node_id="root",
        param_name="repo",
        param_path_id=_path_id(path_registry, ("left", "repo")),
        socket_kind=SocketKind.NORMAL,
    )
    shallow_socket = SocketRef(
        node_id="root",
        param_name="left",
        param_path_id=_path_id(path_registry, ("left",)),
        socket_kind=SocketKind.NORMAL,
    )

    index.add_socket(deep_socket)
    index.add_socket(shallow_socket)

    tuple_matches = index.get_by_exact_path(("left", "repo"))
    list_matches = index.get_by_exact_path(["left", "repo"])
    shallow_matches = index.get_by_exact_path(["left"])

    assert deep_socket in tuple_matches
    assert deep_socket in list_matches
    assert shallow_socket in shallow_matches


def test_injection_plan_missing_contract_overrides_defaults_empty() -> None:
    """
    Purpose:
        Ensure InjectionPlanBuilder treats missing contract override entries as empty payloads.
    Contract:
        - Missing contract_overrides_by_occurrence entries resolve to None payloads.
        - InjectionPlan still builds for shared root occurrences.
    Returns:
        None.
    """
    path_registry = PathRegistry()
    root_path_id = path_registry.root_path_id
    occurrence_graph = {
        ("root", root_path_id): {},
    }
    execution_order = ["root"]
    instance_keys_by_spell_id = {"root": [("root", None)]}
    canonical_occurrences_by_spell_id = {"root": ("root", root_path_id)}
    root_instance_key = ("root", None)
    shared_spell_ids: Set[str] = {"root"}
    contract_overrides_by_occurrence: Dict[Tuple[str, int], Dict[str, Any]] = {}
    contract_overrides_by_spell_id: Dict[str, List[Tuple[Tuple[str, int], Dict[str, Any]]]] = {}

    plan = OccurrencePlan(
        root_spell_id="root",
        occurrence_graph=occurrence_graph,
        execution_order=execution_order,
        instance_keys_by_spell_id=instance_keys_by_spell_id,
        canonical_occurrences_by_spell_id=canonical_occurrences_by_spell_id,
        root_instance_key=root_instance_key,
        shared_spell_ids=shared_spell_ids,
        contract_overrides_by_occurrence=contract_overrides_by_occurrence,
        contract_overrides_by_spell_id=contract_overrides_by_spell_id,
        contract_dependencies_complete=True,
        path_registry=path_registry,
    )
    builder = InjectionPlanBuilder(occurrence_plan=plan)
    injection_plan = builder.build()

    injection_spec = injection_plan.instance_injections[root_instance_key]
    assert injection_spec.contract_payload is None


def test_occurrence_plan_topology_preferred_over_dag() -> None:
    """
    Purpose:
        Ensure local topology data suppresses DAG dependency fallback.
    Contract:
        - When topology is present, DAG metadata is not appended.
        - Dependencies reflect only topology targets.
    Returns:
        None.
    """
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency(parent_key="dag_parent", child_key="root", param_name="dep")

    socket = SpellSocketDescriptor(
        spell_id="root",
        param_name="dep",
        position=0,
        socket_kind=SocketKind.NORMAL,
        is_collection=False,
        is_optional=False,
        target_spell_ids=("topo_parent",),
        dependency_key=None,
        contract_key=None,
        contract_late_binding=None,
    )
    topology = SpellLocalTopology("root", [socket])

    system_states = _StubSystemStates({"root": topology})
    spellbook = _StubSpellbook(SystemState.dynamic)
    root_spell = _StubSpell(
        "root",
        spellbook,
        existence=Existence.unique,
    )
    path_registry = PathRegistry()

    builder = OccurrencePlanBuilder(
        root_spell=root_spell,
        blueprint=SimpleNamespace(path_registry=path_registry),
        spell_lookup={"root": root_spell},
        system_states=system_states,
    )
    dependencies = builder._collect_occurrence_dependencies(
        occurrence=("root", path_registry.root_path_id),
        dag=dag,
    )

    dep_path_id = _path_id(path_registry, ("dep",))
    assert dependencies == {"dep": [("topo_parent", dep_path_id)]}


def test_occurrence_plan_dag_fallback_when_topology_missing() -> None:
    """
    Purpose:
        Ensure DAG dependencies are used only when no topology is available.
    Contract:
        - Missing topology yields DAG-based dependencies.
        - DAG targets include the expected path segment.
    Returns:
        None.
    """
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency(parent_key="dag_parent", child_key="root", param_name="dep")

    system_states = _StubSystemStates({})
    spellbook = _StubSpellbook(SystemState.dynamic)
    root_spell = _StubSpell(
        "root",
        spellbook,
        existence=Existence.unique,
    )
    path_registry = PathRegistry()

    builder = OccurrencePlanBuilder(
        root_spell=root_spell,
        blueprint=SimpleNamespace(path_registry=path_registry),
        spell_lookup={"root": root_spell},
        system_states=system_states,
    )
    dependencies = builder._collect_occurrence_dependencies(
        occurrence=("root", path_registry.root_path_id),
        dag=dag,
    )

    dep_path_id = _path_id(path_registry, ("dep",))
    assert dependencies == {"dep": [("dag_parent", dep_path_id)]}


def test_occurrence_plan_collapses_shared_occurrences_without_mutation_overrides() -> None:
    """
    Purpose:
        Ensure shared-spell occurrences collapse when mutation overrides are absent.
    Contract:
        - Shared spell ids appear only once in the occurrence graph.
        - Dependency paths for non-shared spells remain path-aware.
    Returns:
        None.
    """
    root_socket_left = SpellSocketDescriptor(
        spell_id="root",
        param_name="left",
        position=0,
        socket_kind=SocketKind.NORMAL,
        is_collection=False,
        is_optional=False,
        target_spell_ids=("left",),
        dependency_key=None,
        contract_key=None,
        contract_late_binding=None,
    )
    root_socket_right = SpellSocketDescriptor(
        spell_id="root",
        param_name="right",
        position=1,
        socket_kind=SocketKind.NORMAL,
        is_collection=False,
        is_optional=False,
        target_spell_ids=("right",),
        dependency_key=None,
        contract_key=None,
        contract_late_binding=None,
    )
    left_socket = SpellSocketDescriptor(
        spell_id="left",
        param_name="dep",
        position=0,
        socket_kind=SocketKind.NORMAL,
        is_collection=False,
        is_optional=False,
        target_spell_ids=("shared",),
        dependency_key=None,
        contract_key=None,
        contract_late_binding=None,
    )
    right_socket = SpellSocketDescriptor(
        spell_id="right",
        param_name="dep",
        position=0,
        socket_kind=SocketKind.NORMAL,
        is_collection=False,
        is_optional=False,
        target_spell_ids=("shared",),
        dependency_key=None,
        contract_key=None,
        contract_late_binding=None,
    )

    system_states = _StubSystemStates(
        {
            "root": SpellLocalTopology("root", [root_socket_left, root_socket_right]),
            "left": SpellLocalTopology("left", [left_socket]),
            "right": SpellLocalTopology("right", [right_socket]),
            "shared": SpellLocalTopology("shared", []),
        }
    )
    spellbook = _StubSpellbook(SystemState.dynamic)
    spell_lookup = {
        "root": _StubSpell("root", spellbook, existence=Existence.unique),
        "left": _StubSpell("left", spellbook, existence=Existence.unique),
        "right": _StubSpell("right", spellbook, existence=Existence.unique),
        "shared": _StubSpell("shared", spellbook, existence=Existence.unique),
    }
    path_registry = PathRegistry()

    builder = OccurrencePlanBuilder(
        root_spell=spell_lookup["root"],
        blueprint=SimpleNamespace(path_registry=path_registry),
        spell_lookup=spell_lookup,
        system_states=system_states,
    )
    collapse_shared_occurrences = builder._should_collapse_shared_occurrences()
    occurrence_graph = builder._build_occurrence_graph(
        dag=None,
        root_spell_id="root",
        collapse_shared_occurrences=collapse_shared_occurrences,
    )

    shared_occurrences = [occ for occ in occurrence_graph if occ[0] == "shared"]
    assert len(shared_occurrences) == 1
    left_path_id = _path_id(path_registry, ("left",))
    left_dep_path_id = _path_id(path_registry, ("left", "dep"))
    right_path_id = _path_id(path_registry, ("right",))
    right_dep_path_id = _path_id(path_registry, ("right", "dep"))
    assert occurrence_graph[("left", left_path_id)]["dep"] == [("shared", left_dep_path_id)]
    assert occurrence_graph[("right", right_path_id)]["dep"] == [
        ("shared", right_dep_path_id)
    ]


def test_occurrence_plan_shared_occurrences_not_collapsed_with_mutation_override() -> None:
    """
    Purpose:
        Ensure shared-spell occurrences are not collapsed when mutation overrides exist.
    Contract:
        - Shared spell ids may appear multiple times in the occurrence graph.
        - Mutation override presence disables shared-occurrence collapse.
    Returns:
        None.
    """
    root_socket_left = SpellSocketDescriptor(
        spell_id="root",
        param_name="left",
        position=0,
        socket_kind=SocketKind.NORMAL,
        is_collection=False,
        is_optional=False,
        target_spell_ids=("left",),
        dependency_key=None,
        contract_key=None,
        contract_late_binding=None,
    )
    root_socket_right = SpellSocketDescriptor(
        spell_id="root",
        param_name="right",
        position=1,
        socket_kind=SocketKind.NORMAL,
        is_collection=False,
        is_optional=False,
        target_spell_ids=("right",),
        dependency_key=None,
        contract_key=None,
        contract_late_binding=None,
    )
    left_socket = SpellSocketDescriptor(
        spell_id="left",
        param_name="dep",
        position=0,
        socket_kind=SocketKind.NORMAL,
        is_collection=False,
        is_optional=False,
        target_spell_ids=("shared",),
        dependency_key=None,
        contract_key=None,
        contract_late_binding=None,
    )
    right_socket = SpellSocketDescriptor(
        spell_id="right",
        param_name="dep",
        position=0,
        socket_kind=SocketKind.NORMAL,
        is_collection=False,
        is_optional=False,
        target_spell_ids=("shared",),
        dependency_key=None,
        contract_key=None,
        contract_late_binding=None,
    )

    system_states = _StubSystemStates(
        {
            "root": SpellLocalTopology("root", [root_socket_left, root_socket_right]),
            "left": SpellLocalTopology("left", [left_socket]),
            "right": SpellLocalTopology("right", [right_socket]),
            "shared": SpellLocalTopology("shared", []),
        }
    )
    spellbook = _StubSpellbook(SystemState.dynamic)
    spell_lookup = {
        "root": _StubSpell("root", spellbook, existence=Existence.unique),
        "left": _StubSpell("left", spellbook, existence=Existence.unique),
        "right": _StubSpell("right", spellbook, existence=Existence.unique),
        "shared": _StubSpell("shared", spellbook, existence=Existence.unique),
        "mutator": _StubSpell(
            "mutator",
            spellbook,
            existence=Existence.unique,
            mutation_override={"*noop": "noop"},
        ),
    }
    path_registry = PathRegistry()

    builder = OccurrencePlanBuilder(
        root_spell=spell_lookup["root"],
        blueprint=SimpleNamespace(path_registry=path_registry),
        spell_lookup=spell_lookup,
        system_states=system_states,
    )
    collapse_shared_occurrences = builder._should_collapse_shared_occurrences()
    occurrence_graph = builder._build_occurrence_graph(
        dag=None,
        root_spell_id="root",
        collapse_shared_occurrences=collapse_shared_occurrences,
    )

    shared_occurrences = [occ for occ in occurrence_graph if occ[0] == "shared"]
    assert len(shared_occurrences) == 2
