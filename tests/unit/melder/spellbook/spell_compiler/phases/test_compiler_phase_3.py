"""Unit tests for current-surface compiler phase 3 local DAG build."""

import typing
from types import SimpleNamespace
from typing import Any, Optional, Union

import pytest

import melder.aether.spellbook.spell_compiler.phases.compiler_phase_3 as compiler_phase_3_module
from melder.aether.spellbook.spell_compiler.phases.compiler_phase_3 import (
    CompilerPhase3,
)
from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.aether.spellbook.spell_compiler.symbolic_graph.spell_symbolic_dependency import (
    SpellSymbolicDependency,
)
from melder.aether.spellbook.spell_compiler.symbolic_graph.spell_symbolic_graph import (
    SpellSymbolicGraph,
)
from melder.aether.spellbook.spell_types.spell_types import SpellType


class _CancelStub:
    """Minimal cancellation stub for compiler phase tests."""

    def __init__(self, is_set: bool) -> None:
        """Store the initial cancellation posture."""
        self.is_set = is_set
        self.throw_calls = 0

    def throw_if_set(self) -> None:
        """Record cancellation and raise the expected runtime error."""
        self.throw_calls += 1
        raise RuntimeError("cancelled")


class _SpellSystemStatesStub:
    """Record dependency and topology updates published by Phase 3."""

    def __init__(self) -> None:
        """Initialize empty call capture lists."""
        self.dependencies_calls: list[tuple[Any, list[str]]] = []
        self.topology_calls: list[tuple[Any, Any]] = []

    def update_dependencies(self, spell_index: Any, dependency_spell_ids: list[str]) -> None:
        """Record direct dependency publication."""
        self.dependencies_calls.append((spell_index, dependency_spell_ids))

    def register_local_topology(self, spell_index: Any, topology: Any) -> None:
        """Record local topology publication."""
        self.topology_calls.append((spell_index, topology))


class _SpellIndexStub:
    """Hashable SpellIndex stand-in for Phase 3 map/set behavior."""

    __slots__ = [
        "current",
        "id",
    ]

    def __init__(self, spell_id: str) -> None:
        """Store the current and lineage ids."""
        self.current = spell_id
        self.id = "lineage-{0}".format(spell_id)

    def __hash__(self) -> int:
        """Keep the stub usable as a dictionary key like real SpellIndex."""
        return hash((self.current, self.id))


def _make_spell_stub(
        spell_id: str,
        *,
        spell_obj: Any,
        spellframe: Any,
        spell_name: str,
        binding_name: Optional[str] = None,
        spell_type: SpellType = SpellType.SPELL,
) -> Any:
    """Build a minimal spell stub for Phase 3 matching and run tests."""
    build_details: list[dict[str, Any]] = []

    def _add_build_details(*, dag: Any, dependencies: list[str]) -> None:
        build_details.append(
            {
                "dag": dag,
                "dependencies": dependencies,
            }
        )

    return SimpleNamespace(
        spell_id=spell_id,
        spell=spell_obj,
        spellframe=spellframe,
        spell_name=spell_name,
        binding_name=binding_name,
        spell_type=spell_type,
        spell_index=_SpellIndexStub(spell_id),
        _add_build_details=_add_build_details,
        _build_details_calls=build_details,
    )


def _make_dependency(
        *,
        spell_version_id: str,
        param_name: str,
        position: int,
        di_shape: ParameterDIShape,
        target_annotation: Any = None,
        is_collection: bool = False,
        spellmap_default: Any = None,
        is_optional: bool = False,
) -> SpellSymbolicDependency:
    """Build one symbolic dependency instance for Phase 3 tests."""
    return SpellSymbolicDependency(
        spell_version_id=spell_version_id,
        param_name=param_name,
        position=position,
        di_shape=di_shape,
        is_optional=is_optional,
        target_annotation=target_annotation,
        is_collection=is_collection,
        spellmap_default=spellmap_default,
    )


def _patch_phase2_5_capture(monkeypatch: pytest.MonkeyPatch) -> None:
    """Disable shared IR capture for focused Phase 3 unit tests."""
    monkeypatch.setattr(
        compiler_phase_3_module.SharedCompilerExecutions,
        "capture_phase2_5_codegen_ir",
        lambda _spell, _artifact: None,
    )


def test_iter_all_spells_uses_live_spell_id_pool_order() -> None:
    """Phase 3 iteration should proxy the live spell_id_pool order."""
    phase = CompilerPhase3()
    first = _make_spell_stub(
        "first",
        spell_obj=object(),
        spellframe=None,
        spell_name="FirstSpell",
    )
    second = _make_spell_stub(
        "second",
        spell_obj=object(),
        spellframe=None,
        spell_name="SecondSpell",
    )
    spellbook = SimpleNamespace(
        _spell_id_pool={
            "first": first,
            "second": second,
        }
    )

    pairs = list(phase._iter_all_spells(spellbook))

    assert pairs == [
        (first.spell_index, first),
        (second.spell_index, second),
    ]


@pytest.mark.parametrize(
    ("spell_type", "annotation_kind", "binding_name", "candidate_binding_name", "require_class_spell", "expected"),
    [
        (SpellType.SPELL, "spell", None, None, True, True),
        (SpellType.SPELL, "spell", "alpha", "beta", True, False),
        (SpellType.SPELL, "frame", None, None, True, True),
        (SpellType.SPELL, "frame_eq", None, None, True, True),
        (SpellType.METHOD, "spell", None, None, True, False),
        (SpellType.METHOD, "spell", None, None, False, True),
    ],
)
def test_matches_annotation_cases(
        spell_type: SpellType,
        annotation_kind: str,
        binding_name: Optional[str],
        candidate_binding_name: Optional[str],
        require_class_spell: bool,
        expected: bool,
) -> None:
    """Phase 3 annotation matching should honor type, frame, and binding filters."""
    phase = CompilerPhase3()

    class _FrameType:
        pass

    spell_obj = object()
    spellframe = _FrameType
    annotation: Any
    if annotation_kind == "spell":
        annotation = spell_obj
    elif annotation_kind == "frame":
        annotation = spellframe
    else:
        annotation = _FrameType

    candidate = _make_spell_stub(
        "candidate",
        spell_obj=spell_obj,
        spellframe=spellframe,
        spell_name="CandidateSpell",
        binding_name=candidate_binding_name,
        spell_type=spell_type,
    )

    assert phase._matches_annotation(
        annotation,
        binding_name,
        candidate,
        require_class_spell=require_class_spell,
    ) is expected


def test_matches_annotation_rejects_binding_mismatch_on_frame() -> None:
    """Phase 3 should reject frame matches when binding names differ."""
    phase = CompilerPhase3()

    class _FrameType:
        pass

    candidate = _make_spell_stub(
        "candidate",
        spell_obj=object(),
        spellframe=_FrameType,
        spell_name="CandidateSpell",
        binding_name="secondary",
    )

    assert phase._matches_annotation(
        _FrameType,
        "primary",
        candidate,
        require_class_spell=True,
    ) is False


def test_normalize_annotation_for_matching_handles_forward_refs_and_optional_union() -> None:
    """Phase 3 should unwrap ForwardRef and Optional-style unions."""
    phase = CompilerPhase3()

    assert phase._normalize_annotation_for_matching(
        typing.ForwardRef("MyType")
    ) == "MyType"
    assert phase._normalize_annotation_for_matching(
        Union[int, None]
    ) is int


def test_matches_annotation_supports_forward_ref_strings_and_frame_class_names() -> None:
    """Phase 3 should match string forward refs against spell names and frame names."""
    phase = CompilerPhase3()

    class _FrameType:
        pass

    candidate = _make_spell_stub(
        "candidate",
        spell_obj=object(),
        spellframe=_FrameType,
        spell_name="CandidateSpell",
    )

    assert phase._matches_annotation(
        "CandidateSpell",
        None,
        candidate,
        require_class_spell=True,
    ) is True
    assert phase._matches_annotation(
        "_FrameType",
        None,
        candidate,
        require_class_spell=True,
    ) is True


@pytest.mark.parametrize(
    ("drop_spell_id", "expected_message"),
    [
        (True, "bound spell current id"),
    ],
)
def test_build_local_topology_requires_bound_spell_id(
        drop_spell_id: bool,
        expected_message: str,
) -> None:
    """Phase 3 local topology should require a bound current spell id."""
    phase = CompilerPhase3()
    root_spell = _make_spell_stub(
        "root",
        spell_obj=object(),
        spellframe=None,
        spell_name="RootSpell",
    )
    if drop_spell_id:
        root_spell.spell_index.current = None
    graph = SpellSymbolicGraph(
        spell_version_id="root",
        dependencies=[],
    )

    with pytest.raises(RuntimeError, match=expected_message):
        phase._build_local_topology(root_spell, graph, {})


def test_build_local_topology_builds_descriptors() -> None:
    """Phase 3 local topology should preserve socket metadata and targets."""
    phase = CompilerPhase3()
    root_spell = _make_spell_stub(
        "root",
        spell_obj=object(),
        spellframe=None,
        spell_name="RootSpell",
    )
    dep_normal = _make_dependency(
        spell_version_id="root",
        param_name="alpha",
        position=0,
        di_shape=ParameterDIShape.SINGLE_BY_ANNOTATION,
        is_optional=False,
    )
    dep_contract = _make_dependency(
        spell_version_id="root",
        param_name="beta",
        position=1,
        di_shape=ParameterDIShape.SPELL_CONTRACT,
        is_optional=True,
    )
    graph = SpellSymbolicGraph(
        spell_version_id="root",
        dependencies=[dep_normal, dep_contract],
    )
    socket_targets = {("alpha", 0): ["dep1", "dep2"]}

    topology = phase._build_local_topology(root_spell, graph, socket_targets)

    assert topology.spell_id == "root"
    assert len(topology.sockets) == 2
    alpha_socket = topology.get_sockets_for_param("alpha")[0]
    beta_socket = topology.get_sockets_for_param("beta")[0]

    assert alpha_socket.param_name == "alpha"
    assert alpha_socket.position == 0
    assert alpha_socket.socket_kind.name == "NORMAL"
    assert alpha_socket.is_collection is False
    assert alpha_socket.is_optional is False
    assert alpha_socket.target_spell_ids == ("dep1", "dep2")

    assert beta_socket.param_name == "beta"
    assert beta_socket.position == 1
    assert beta_socket.socket_kind.name == "SPELL_CONTRACT"
    assert beta_socket.is_collection is False
    assert beta_socket.is_optional is True
    assert beta_socket.target_spell_ids == ()


@pytest.mark.parametrize(
    ("drop_requirements", "drop_graph", "expected_message"),
    [
        (True, False, "requirements must not be None"),
        (False, True, "graph must not be None"),
    ],
)
def test_build_local_frame_dag_requires_inputs(
        drop_requirements: bool,
        drop_graph: bool,
        expected_message: str,
) -> None:
    """Phase 3 local DAG build should reject missing requirements or graph."""
    phase = CompilerPhase3()
    root_spell = _make_spell_stub(
        "root",
        spell_obj=object(),
        spellframe=None,
        spell_name="RootSpell",
    )
    requirements: Any = object()
    graph: Any = SpellSymbolicGraph(spell_version_id="root", dependencies=[])

    if drop_requirements:
        requirements = None
    if drop_graph:
        graph = None

    with pytest.raises(ValueError, match=expected_message):
        phase._build_local_frame_dag(
            spell=root_spell,
            spellbook=SimpleNamespace(_spell_id_pool={}),
            spell_system_states=_SpellSystemStatesStub(),
            requirements=requirements,
            graph=graph,
            cancellation_event=_CancelStub(is_set=False),
        )


def test_build_local_frame_dag_requires_bound_spell_index() -> None:
    """Phase 3 local DAG build should require a bound current spell id."""
    phase = CompilerPhase3()
    root_spell = _make_spell_stub(
        "root",
        spell_obj=object(),
        spellframe=None,
        spell_name="RootSpell",
    )
    root_spell.spell_index.current = None

    with pytest.raises(RuntimeError, match="bound spell current id"):
        phase._build_local_frame_dag(
            spell=root_spell,
            spellbook=SimpleNamespace(_spell_id_pool={}),
            spell_system_states=_SpellSystemStatesStub(),
            requirements=object(),
            graph=SpellSymbolicGraph(spell_version_id="root", dependencies=[]),
            cancellation_event=_CancelStub(is_set=False),
        )


def test_resolve_single_by_annotation_returns_exact_match() -> None:
    """Phase 3 should resolve a single-annotation socket to one candidate."""
    phase = CompilerPhase3()

    class _ServiceFrame:
        pass

    root_spell = _make_spell_stub(
        "root",
        spell_obj=object(),
        spellframe=None,
        spell_name="RootSpell",
    )
    candidate = _make_spell_stub(
        "dep",
        spell_obj=object(),
        spellframe=_ServiceFrame,
        spell_name="DepSpell",
    )
    spellbook = SimpleNamespace(_spell_id_pool={"dep": candidate})
    dep = _make_dependency(
        spell_version_id="root",
        param_name="service",
        position=0,
        di_shape=ParameterDIShape.SINGLE_BY_ANNOTATION,
        target_annotation=_ServiceFrame,
    )

    resolved = phase._resolve_single_by_annotation(root_spell, spellbook, dep)

    assert list(resolved.values()) == [candidate]


@pytest.mark.parametrize(
    "method_only",
    [
        False,
        True,
    ],
)
def test_resolve_single_by_annotation_no_candidates(method_only: bool) -> None:
    """Phase 3 single-resolution should fail when no valid class candidate exists."""
    phase = CompilerPhase3()

    class _ServiceFrame:
        pass

    root_spell = _make_spell_stub(
        "root",
        spell_obj=object(),
        spellframe=None,
        spell_name="RootSpell",
    )
    spellbook = SimpleNamespace(_spell_id_pool={})
    if method_only:
        spellbook = SimpleNamespace(
            _spell_id_pool={
                "method": _make_spell_stub(
                    "method",
                    spell_obj=object(),
                    spellframe=_ServiceFrame,
                    spell_name="MethodOnly",
                    spell_type=SpellType.METHOD,
                )
            }
        )
    dep = _make_dependency(
        spell_version_id="root",
        param_name="service",
        position=0,
        di_shape=ParameterDIShape.SINGLE_BY_ANNOTATION,
        target_annotation=_ServiceFrame,
    )

    with pytest.raises(RuntimeError, match="no DI candidate found"):
        phase._resolve_single_by_annotation(root_spell, spellbook, dep)


def test_resolve_single_by_annotation_raises_on_multiple_matches() -> None:
    """Phase 3 should fail fast when a single socket matches multiple spells."""
    phase = CompilerPhase3()

    class _ServiceFrame:
        pass

    root_spell = _make_spell_stub(
        "root",
        spell_obj=object(),
        spellframe=None,
        spell_name="RootSpell",
    )
    first = _make_spell_stub(
        "dep-a",
        spell_obj=object(),
        spellframe=_ServiceFrame,
        spell_name="DepA",
    )
    second = _make_spell_stub(
        "dep-b",
        spell_obj=object(),
        spellframe=_ServiceFrame,
        spell_name="DepB",
    )
    spellbook = SimpleNamespace(_spell_id_pool={"a": first, "b": second})
    dep = _make_dependency(
        spell_version_id="root",
        param_name="service",
        position=0,
        di_shape=ParameterDIShape.SINGLE_BY_ANNOTATION,
        target_annotation=_ServiceFrame,
    )

    with pytest.raises(RuntimeError, match="multiple DI candidates found"):
        phase._resolve_single_by_annotation(root_spell, spellbook, dep)


def test_resolve_collection_by_annotation_returns_all_matches() -> None:
    """Phase 3 collection DI should keep both class and method matches."""
    phase = CompilerPhase3()

    class _ServiceFrame:
        pass

    class_spell = _make_spell_stub(
        "dep-class",
        spell_obj=object(),
        spellframe=_ServiceFrame,
        spell_name="ClassDep",
    )
    method_spell = _make_spell_stub(
        "dep-method",
        spell_obj=object(),
        spellframe=_ServiceFrame,
        spell_name="MethodDep",
        spell_type=SpellType.METHOD,
    )
    spellbook = SimpleNamespace(
        _spell_id_pool={
            "class": class_spell,
            "method": method_spell,
        }
    )
    dep = _make_dependency(
        spell_version_id="root",
        param_name="services",
        position=0,
        di_shape=ParameterDIShape.COLLECTION_BY_ANNOTATION,
        target_annotation=_ServiceFrame,
        is_collection=True,
    )

    resolved = phase._resolve_collection_by_annotation(spellbook, dep)

    assert sorted(
        candidate.spell_name for candidate in resolved.values()
    ) == ["ClassDep", "MethodDep"]


def test_resolve_collection_by_annotation_empty_returns_empty() -> None:
    """Phase 3 collection-resolution should allow an empty candidate set."""
    phase = CompilerPhase3()

    class _ServiceFrame:
        pass

    dep = _make_dependency(
        spell_version_id="root",
        param_name="services",
        position=0,
        di_shape=ParameterDIShape.COLLECTION_BY_ANNOTATION,
        target_annotation=_ServiceFrame,
        is_collection=True,
    )

    resolved = phase._resolve_collection_by_annotation(
        SimpleNamespace(_spell_id_pool={}),
        dep,
    )

    assert resolved == {}


def test_resolve_spellmap_default_none_returns_empty() -> None:
    """Phase 3 SpellMap-default resolution should accept a missing default."""
    phase = CompilerPhase3()
    root_spell = _make_spell_stub(
        "root",
        spell_obj=object(),
        spellframe=None,
        spell_name="RootSpell",
    )
    dep = _make_dependency(
        spell_version_id="root",
        param_name="service",
        position=0,
        di_shape=ParameterDIShape.SPELLMAP_DEFAULT,
        spellmap_default=None,
    )

    assert phase._resolve_spellmap_default(
        root_spell,
        SimpleNamespace(_spell_id_pool={}),
        dep,
    ) == {}


def test_resolve_spellmap_default_explicit_spell_success() -> None:
    """Phase 3 SpellMap defaults should resolve explicit spell targets."""
    phase = CompilerPhase3()
    explicit = object()
    root_spell = _make_spell_stub(
        "root",
        spell_obj=object(),
        spellframe=None,
        spell_name="RootSpell",
    )
    candidate = _make_spell_stub(
        "candidate",
        spell_obj=explicit,
        spellframe=None,
        spell_name="CandidateSpell",
    )
    dep = _make_dependency(
        spell_version_id="root",
        param_name="service",
        position=0,
        di_shape=ParameterDIShape.SPELLMAP_DEFAULT,
        spellmap_default=SimpleNamespace(
            spell=explicit,
            spellframe=None,
            binding_name=None,
            canonical_key=("__none__", "__default__"),
        ),
    )

    resolved = phase._resolve_spellmap_default(
        root_spell,
        SimpleNamespace(_spell_id_pool={"candidate": candidate}),
        dep,
    )

    assert list(resolved.values()) == [candidate]


def test_resolve_spellmap_default_explicit_spell_mismatch_raises() -> None:
    """Phase 3 SpellMap defaults should fail when the explicit spell is absent."""
    phase = CompilerPhase3()
    explicit = object()
    root_spell = _make_spell_stub(
        "root",
        spell_obj=object(),
        spellframe=None,
        spell_name="RootSpell",
    )
    dep = _make_dependency(
        spell_version_id="root",
        param_name="service",
        position=0,
        di_shape=ParameterDIShape.SPELLMAP_DEFAULT,
        spellmap_default=SimpleNamespace(
            spell=explicit,
            spellframe=None,
            binding_name=None,
            canonical_key=("__none__", "__default__"),
        ),
    )

    with pytest.raises(RuntimeError, match="could not be resolved"):
        phase._resolve_spellmap_default(
            root_spell,
            SimpleNamespace(_spell_id_pool={}),
            dep,
        )


def test_resolve_spellmap_default_frame_binding_success() -> None:
    """Phase 3 SpellMap defaults should resolve frame-plus-binding targets."""
    phase = CompilerPhase3()
    root_spell = _make_spell_stub(
        "root",
        spell_obj=object(),
        spellframe=None,
        spell_name="RootSpell",
    )
    candidate = _make_spell_stub(
        "candidate",
        spell_obj=object(),
        spellframe="ServiceFrame",
        spell_name="CandidateSpell",
        binding_name="primary",
    )
    dep = _make_dependency(
        spell_version_id="root",
        param_name="service",
        position=0,
        di_shape=ParameterDIShape.SPELLMAP_DEFAULT,
        spellmap_default=SimpleNamespace(
            spell=None,
            spellframe="ServiceFrame",
            binding_name="primary",
            canonical_key=("ServiceFrame", "primary"),
        ),
    )

    resolved = phase._resolve_spellmap_default(
        root_spell,
        SimpleNamespace(_spell_id_pool={"candidate": candidate}),
        dep,
    )

    assert list(resolved.values()) == [candidate]


def test_resolve_spellmap_default_frame_binding_empty_raises() -> None:
    """Phase 3 SpellMap frame-plus-binding defaults should fail on no match."""
    phase = CompilerPhase3()
    root_spell = _make_spell_stub(
        "root",
        spell_obj=object(),
        spellframe=None,
        spell_name="RootSpell",
    )
    dep = _make_dependency(
        spell_version_id="root",
        param_name="service",
        position=0,
        di_shape=ParameterDIShape.SPELLMAP_DEFAULT,
        spellmap_default=SimpleNamespace(
            spell=None,
            spellframe="ServiceFrame",
            binding_name="primary",
            canonical_key=("ServiceFrame", "primary"),
        ),
    )

    with pytest.raises(RuntimeError, match="could not be resolved"):
        phase._resolve_spellmap_default(
            root_spell,
            SimpleNamespace(_spell_id_pool={}),
            dep,
        )


def test_resolve_spellmap_default_raises_on_ambiguous_match() -> None:
    """Phase 3 should reject ambiguous SpellMap defaults."""
    phase = CompilerPhase3()
    root_spell = _make_spell_stub(
        "root",
        spell_obj=object(),
        spellframe=None,
        spell_name="RootSpell",
    )
    first = _make_spell_stub(
        "dep-a",
        spell_obj=object(),
        spellframe="ServiceFrame",
        spell_name="DepA",
        binding_name="primary",
    )
    second = _make_spell_stub(
        "dep-b",
        spell_obj=object(),
        spellframe="ServiceFrame",
        spell_name="DepB",
        binding_name="primary",
    )
    spellbook = SimpleNamespace(_spell_id_pool={"a": first, "b": second})
    dep = _make_dependency(
        spell_version_id="root",
        param_name="service",
        position=0,
        di_shape=ParameterDIShape.SPELLMAP_DEFAULT,
        spellmap_default=SimpleNamespace(
            spell=None,
            spellframe="ServiceFrame",
            binding_name="primary",
            canonical_key=("ServiceFrame", "primary"),
        ),
    )

    with pytest.raises(RuntimeError, match="resolved to multiple candidates"):
        phase._resolve_spellmap_default(root_spell, spellbook, dep)


def test_build_local_frame_dag_skips_unresolved_collection() -> None:
    """Phase 3 local DAG build should leave collections empty when unresolved."""
    phase = CompilerPhase3()
    root_spell = _make_spell_stub(
        "root",
        spell_obj=object(),
        spellframe=None,
        spell_name="RootSpell",
    )
    spell_system_states = _SpellSystemStatesStub()
    graph = SpellSymbolicGraph(
        spell_version_id="root",
        dependencies=[
            _make_dependency(
                spell_version_id="root",
                param_name="dep",
                position=0,
                di_shape=ParameterDIShape.COLLECTION_BY_ANNOTATION,
                target_annotation=object(),
                is_collection=True,
            )
        ],
    )

    dag = phase._build_local_frame_dag(
        spell=root_spell,
        spellbook=SimpleNamespace(_spell_id_pool={}),
        spell_system_states=spell_system_states,
        requirements=object(),
        graph=graph,
        cancellation_event=_CancelStub(is_set=False),
    )

    assert dag.collect_dependency_ids() == ["root"]
    assert spell_system_states.dependencies_calls == [
        (root_spell.spell_index, [])
    ]


def test_build_local_frame_dag_handles_spellmap_default_success() -> None:
    """Phase 3 local DAG build should create edges for resolved SpellMap defaults."""
    phase = CompilerPhase3()
    explicit = object()
    root_spell = _make_spell_stub(
        "root",
        spell_obj=object(),
        spellframe=None,
        spell_name="RootSpell",
    )
    dependency_spell = _make_spell_stub(
        "dep-id",
        spell_obj=explicit,
        spellframe=None,
        spell_name="DependencySpell",
    )
    spell_system_states = _SpellSystemStatesStub()
    graph = SpellSymbolicGraph(
        spell_version_id="root",
        dependencies=[
            _make_dependency(
                spell_version_id="root",
                param_name="dep",
                position=0,
                di_shape=ParameterDIShape.SPELLMAP_DEFAULT,
                spellmap_default=SimpleNamespace(
                    spell=explicit,
                    spellframe=None,
                    binding_name=None,
                    canonical_key=("__none__", "__default__"),
                ),
            )
        ],
    )

    dag = phase._build_local_frame_dag(
        spell=root_spell,
        spellbook=SimpleNamespace(_spell_id_pool={"dep": dependency_spell}),
        spell_system_states=spell_system_states,
        requirements=object(),
        graph=graph,
        cancellation_event=_CancelStub(is_set=False),
    )

    assert "dep-id" in dag.collect_dependency_ids()
    assert spell_system_states.dependencies_calls == [
        (root_spell.spell_index, ["dep-id"])
    ]


def test_build_local_frame_dag_ignores_contract_shapes() -> None:
    """Phase 3 local DAG build should not create edges for contract sockets."""
    phase = CompilerPhase3()
    root_spell = _make_spell_stub(
        "root",
        spell_obj=object(),
        spellframe=None,
        spell_name="RootSpell",
    )
    spell_system_states = _SpellSystemStatesStub()
    graph = SpellSymbolicGraph(
        spell_version_id="root",
        dependencies=[
            _make_dependency(
                spell_version_id="root",
                param_name="contract",
                position=0,
                di_shape=ParameterDIShape.SPELL_CONTRACT,
                target_annotation=object(),
            ),
            _make_dependency(
                spell_version_id="root",
                param_name="mutation",
                position=1,
                di_shape=ParameterDIShape.MUTATION_CONTRACT,
                target_annotation=object(),
            ),
        ],
    )

    dag = phase._build_local_frame_dag(
        spell=root_spell,
        spellbook=SimpleNamespace(_spell_id_pool={}),
        spell_system_states=spell_system_states,
        requirements=object(),
        graph=graph,
        cancellation_event=_CancelStub(is_set=False),
    )

    assert dag.collect_dependency_ids() == ["root"]
    assert spell_system_states.dependencies_calls == [
        (root_spell.spell_index, [])
    ]
    topology = spell_system_states.topology_calls[0][1]
    assert [socket.socket_kind.name for socket in topology.sockets] == [
        "SPELL_CONTRACT",
        "MUTATION_CONTRACT",
    ]


def test_run_phase_local_frame_requires_prior_phases() -> None:
    """Phase 3 entrypoint should require both requirements and symbolic graph."""
    phase = CompilerPhase3()
    root_spell = _make_spell_stub(
        "root",
        spell_obj=object(),
        spellframe=None,
        spell_name="RootSpell",
    )
    artifact = SpellCompilerArtifact("root")

    with pytest.raises(RuntimeError, match="Phase 3"):
        phase.run(
            root_spell,
            artifact,
            SimpleNamespace(_spell_id_pool={}),
            _SpellSystemStatesStub(),
        )


def test_run_phase_local_frame_requires_spell_system_states() -> None:
    """Phase 3 entrypoint should require a live SpellSystemStates surface."""
    phase = CompilerPhase3()
    root_spell = _make_spell_stub(
        "root",
        spell_obj=object(),
        spellframe=None,
        spell_name="RootSpell",
    )
    artifact = SpellCompilerArtifact("root")
    artifact._requirements = SimpleNamespace()
    artifact._symbolic_graph = SpellSymbolicGraph(
        spell_version_id="root",
        dependencies=[],
    )

    with pytest.raises(RuntimeError, match="live SpellSystemStates surface"):
        phase.run(
            root_spell,
            artifact,
            SimpleNamespace(_spell_id_pool={}),
            None,
        )


def test_run_builds_resolution_frame_and_updates_topology(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Phase 3 should store the local frame and publish dependencies/topology."""
    phase = CompilerPhase3()

    class _ServiceFrame:
        pass

    root_spell = _make_spell_stub(
        "root",
        spell_obj=object(),
        spellframe=None,
        spell_name="RootSpell",
    )
    dependency_spell = _make_spell_stub(
        "dep",
        spell_obj=object(),
        spellframe=_ServiceFrame,
        spell_name="DependencySpell",
    )
    spellbook = SimpleNamespace(_spell_id_pool={"dep": dependency_spell})
    spell_system_states = _SpellSystemStatesStub()
    artifact = SpellCompilerArtifact("root")
    artifact._requirements = SimpleNamespace()
    artifact._symbolic_graph = SpellSymbolicGraph(
        spell_version_id="root",
        dependencies=[
            _make_dependency(
                spell_version_id="root",
                param_name="service",
                position=0,
                di_shape=ParameterDIShape.SINGLE_BY_ANNOTATION,
                target_annotation=_ServiceFrame,
            )
        ],
    )
    _patch_phase2_5_capture(monkeypatch)

    phase.run(root_spell, artifact, spellbook, spell_system_states)

    assert artifact._resolution_frame is not None
    assert artifact._resolution_frame.spell_id == "root"
    assert artifact._resolution_frame.ordered_node_ids[-1] == "root"
    assert "dep" in artifact._resolution_frame.ordered_node_ids

    assert len(root_spell._build_details_calls) == 1
    assert root_spell._build_details_calls[0]["dependencies"] == ["dep"]

    assert len(spell_system_states.dependencies_calls) == 1
    assert spell_system_states.dependencies_calls[0][1] == ["dep"]
    assert len(spell_system_states.topology_calls) == 1
    topology = spell_system_states.topology_calls[0][1]
    assert topology.spell_id == "root"
    assert len(topology.sockets) == 1
    assert topology.sockets[0].target_spell_ids == ("dep",)


@pytest.mark.parametrize(
    ("di_shape", "expected_kind_name"),
    [
        (ParameterDIShape.PLAIN, "NORMAL"),
        (ParameterDIShape.SINGLE_BY_ANNOTATION, "NORMAL"),
        (ParameterDIShape.COLLECTION_BY_ANNOTATION, "NORMAL"),
        (ParameterDIShape.SPELLMAP_DEFAULT, "NORMAL"),
        (ParameterDIShape.SPELL_CONTRACT, "SPELL_CONTRACT"),
        (ParameterDIShape.MUTATION_CONTRACT, "MUTATION_CONTRACT"),
    ],
)
def test_socket_kind_for_dep_mapping(
        di_shape: ParameterDIShape,
        expected_kind_name: str,
) -> None:
    """Phase 3 socket-kind mapping should classify all supported DI shapes."""
    phase = CompilerPhase3()
    dep = _make_dependency(
        spell_version_id="root",
        param_name="dep",
        position=0,
        di_shape=di_shape,
    )

    assert phase._socket_kind_for_dep(dep).name == expected_kind_name


def test_run_honors_cancellation_before_local_dag_build() -> None:
    """Phase 3 should abort before local DAG work when cancelled."""
    phase = CompilerPhase3()
    root_spell = _make_spell_stub(
        "root",
        spell_obj=object(),
        spellframe=None,
        spell_name="RootSpell",
    )
    artifact = SpellCompilerArtifact("root")
    artifact._requirements = SimpleNamespace()
    artifact._symbolic_graph = SpellSymbolicGraph(
        spell_version_id="root",
        dependencies=[],
    )
    cancel_event = _CancelStub(is_set=True)

    with pytest.raises(RuntimeError, match="cancelled"):
        phase.run(
            root_spell,
            artifact,
            SimpleNamespace(_spell_id_pool={}),
            _SpellSystemStatesStub(),
            cancel_event=cancel_event,
        )

    assert cancel_event.throw_calls == 1
