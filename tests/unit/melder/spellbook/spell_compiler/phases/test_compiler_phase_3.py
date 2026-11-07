"""Unit tests for current-surface compiler phase 3 local DAG build."""

import inspect
import typing
from types import SimpleNamespace
from typing import Any, Optional, Protocol, Union

import pytest

import melder.aether.spellbook.spell_compiler.phases.compiler_phase_3 as compiler_phase_3_module
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
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
from melder.aether.spellbook.spellframe_kind.spellframe_kind import SpellframeKind
from melder.utilities.helpers.general_helpers import SpellInputUtils


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
        "selected_spell_id",
        "id",
    ]

    def __init__(self, spell_id: str) -> None:
        """Store the current and lineage ids."""
        self.selected_spell_id = spell_id
        self.id = "lineage-{0}".format(spell_id)

    def __hash__(self) -> int:
        """Keep the stub usable as a dictionary key like real SpellIndex."""
        return hash((self.selected_spell_id, self.id))


def _make_spell_stub(
        spell_id: str,
        *,
        spell_obj: Any,
        spellframe: Any,
        spell_name: str,
        binding_name: Optional[str] = None,
        spell_type: SpellType = SpellType.SPELL,
        resolvable: bool = True,
) -> Any:
    """
    Build a minimal spell stub for Phase 3 matching and run tests.

    The frame kind is derived exactly as Bind records it: None -> none, a string -> category, a Protocol ->
    contract with the Protocol in `implemented_protocols`. A concrete class is refused here as Bind refuses
    it, so a stub cannot describe a binding the runtime would not create.
    """
    build_details: list[dict[str, Any]] = []

    def _add_build_details(*, dependencies: list[str]) -> None:
        build_details.append(
            {
                "dependencies": dependencies,
            }
        )

    if spellframe is None:
        spellframe_kind = SpellframeKind.none
        implemented_protocols: tuple[type, ...] = ()
    elif isinstance(spellframe, str):
        spellframe_kind = SpellframeKind.category
        implemented_protocols = ()
    elif SpellInputUtils.is_protocol_type(spellframe):
        spellframe_kind = SpellframeKind.contract
        implemented_protocols = (spellframe,)
    else:
        raise TypeError("test stub: a spellframe is a string or a Protocol, as Bind enforces")

    return SimpleNamespace(
        spell_id=spell_id,
        spell=spell_obj,
        spellframe=spellframe,
        spellframe_kind=spellframe_kind,
        implemented_protocols=implemented_protocols,
        spell_name=spell_name,
        binding_name=binding_name,
        spell_type=spell_type,
        resolvable=resolvable,
        spell_index=_SpellIndexStub(spell_id),
        _add_build_details=_add_build_details,
        _build_details_calls=build_details,
    )


def _make_dependency(
        *,
        spell_id: str,
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
        spell_id=spell_id,
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
        (SpellType.SPELL, "type", None, None, True, False),
        (SpellType.SPELL, "contract", "alpha", "beta", True, False),
        (SpellType.SPELL, "contract", None, None, True, True),
        (SpellType.SPELL, "type_name", None, None, True, False),
        (SpellType.SPELL, "contract_name", None, None, True, True),
        (SpellType.SPELL, "other", None, None, True, False),
        (SpellType.SPELL, "other_name", None, None, True, False),
        (SpellType.METHOD, "contract", None, None, True, False),
        (SpellType.METHOD, "contract", None, None, False, True),
        (SpellType.METHOD, "type", None, None, False, False),
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
    """
    A single socket matches a contract-framed spell by its Protocol, as the class or by name, never by its type.

    The spellframe hides the concrete class from class lookups (2026-11-07, `_answers_class_lookup`): the type, as
    the class or by name, no longer selects the spell - before, it did. The binding-name filter and the
    `require_class_spell` exclusion of METHOD spells are shown on the Protocol match, which the frame keeps; a
    METHOD spell's type stays hidden even when methods are allowed.
    """
    phase = CompilerPhase3()

    class _FrameContract(Protocol):
        pass

    class CandidateSpell:
        pass

    class _Other:
        pass

    annotation: Any
    if annotation_kind == "type":
        annotation = CandidateSpell
    elif annotation_kind == "contract":
        annotation = _FrameContract
    elif annotation_kind == "type_name":
        annotation = "CandidateSpell"
    elif annotation_kind == "contract_name":
        annotation = "_FrameContract"
    elif annotation_kind == "other_name":
        annotation = "_Other"
    else:
        annotation = _Other

    candidate = _make_spell_stub(
        "candidate",
        spell_obj=CandidateSpell,
        spellframe=_FrameContract,
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
    """Phase 3 should reject contract matches when binding names differ."""
    phase = CompilerPhase3()

    class _FrameContract(Protocol):
        pass

    candidate = _make_spell_stub(
        "candidate",
        spell_obj=object(),
        spellframe=_FrameContract,
        spell_name="CandidateSpell",
        binding_name="secondary",
    )

    assert phase._matches_annotation(
        _FrameContract,
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


def test_annotation_kind_classifies_contracts_types_and_names() -> None:
    """A Protocol is a contract, any other class a type, a string or ForwardRef a name."""
    phase = CompilerPhase3()

    class _Contract(Protocol):
        pass

    class _Type:
        pass

    assert phase._annotation_kind(_Contract) == CompilerPhase3._KIND_CONTRACT
    assert phase._annotation_kind(_Type) == CompilerPhase3._KIND_TYPE
    assert phase._annotation_kind("_Type") == CompilerPhase3._KIND_NAME
    assert phase._annotation_kind(typing.ForwardRef("_Type")) == CompilerPhase3._KIND_NAME
    assert phase._annotation_kind(typing.Protocol) == CompilerPhase3._KIND_CONTRACT


def test_matches_annotation_supports_forward_ref_strings_and_contract_names() -> None:
    """
    A string, or a ForwardRef, names a framed spell's Protocol contract, never its type or a different name.

    A single string annotation's type part is a class lookup (2026-11-07, `_answers_class_lookup`): the spellframe
    hides the framed spell's type name, while its contract name still reaches it. The same type name, as a string or
    a ForwardRef, still reaches a spell of that name bound bare under the default binding.
    """
    phase = CompilerPhase3()

    class _FrameContract(Protocol):
        pass

    candidate = _make_spell_stub(
        "candidate",
        spell_obj=object(),
        spellframe=_FrameContract,
        spell_name="CandidateSpell",
    )
    bare = _make_spell_stub(
        "bare",
        spell_obj=object(),
        spellframe=None,
        spell_name="CandidateSpell",
    )

    assert phase._matches_annotation("CandidateSpell", None, candidate, require_class_spell=True) is False
    assert phase._matches_annotation(typing.ForwardRef("CandidateSpell"), None, candidate, require_class_spell=True) is False
    assert phase._matches_annotation("_FrameContract", None, candidate, require_class_spell=True) is True
    assert phase._matches_annotation(typing.ForwardRef("_FrameContract"), None, candidate, require_class_spell=True) is True
    assert phase._matches_annotation("Unrelated", None, candidate, require_class_spell=True) is False
    assert phase._matches_annotation("CandidateSpell", None, bare, require_class_spell=True) is True
    assert phase._matches_annotation(typing.ForwardRef("CandidateSpell"), None, bare, require_class_spell=True) is True


def test_matches_annotation_matches_an_existing_object_by_its_class_and_by_its_name() -> None:
    """A bare existing object answers to its class object and to its class name, and to nothing else."""
    phase = CompilerPhase3()

    class Service:
        pass

    class Other:
        pass

    candidate = _make_spell_stub(
        "service",
        spell_obj=Service(),
        spellframe=None,
        spell_name="Service",
    )

    assert phase._matches_annotation(Service, None, candidate, require_class_spell=True) is True
    assert phase._matches_annotation("Service", None, candidate, require_class_spell=True) is True
    assert phase._matches_annotation(Other, None, candidate, require_class_spell=True) is False
    assert phase._spell_type_key(candidate) == "service"
    assert phase._spell_label_key(candidate) == "service"
    assert phase._spell_contract_keys(candidate) == ()


def test_matches_annotation_never_reads_a_string_category_as_a_type_or_contract() -> None:
    """
    A spell under a string category is hidden from class lookups; the category's name reaches it only as a collection label.

    The category hides the spell's own type, as the class or by name, single socket or collection (2026-11-07,
    `_answers_class_lookup`; before, the type reached it). The category's name never makes it a provider of a
    class spelled the same way, and never reaches a single socket.
    """
    phase = CompilerPhase3()

    class Service:
        pass

    class Impl:
        pass

    candidate = _make_spell_stub(
        "impl",
        spell_obj=Impl,
        spellframe="service",
        spell_name="Impl",
    )

    assert candidate.spellframe_kind is SpellframeKind.category
    assert phase._spell_type_key(candidate) == "impl"
    assert phase._spell_label_key(candidate) == "service"
    assert phase._spell_contract_keys(candidate) == ()
    assert phase._answers_class_lookup(candidate) is False
    # single socket: neither the type, by object or by name (the category hides it), nor the category
    assert phase._matches_annotation(Impl, None, candidate, require_class_spell=True) is False
    assert phase._matches_annotation("Impl", None, candidate, require_class_spell=True) is False
    assert phase._matches_annotation(Service, None, candidate, require_class_spell=True) is False
    assert phase._matches_annotation("service", None, candidate, require_class_spell=True) is False
    # collection: the label by name only - not the type by class (hidden), not the category by a class spelled like it
    assert phase._matches_annotation("service", None, candidate, require_class_spell=False, collection=True) is True
    assert phase._matches_annotation(Impl, None, candidate, require_class_spell=False, collection=True) is False
    assert phase._matches_annotation(Service, None, candidate, require_class_spell=False, collection=True) is False
    assert phase._matches_annotation("impl", None, candidate, require_class_spell=False, collection=True) is False


def test_matches_annotation_contract_spell_is_reached_by_its_contract_never_by_its_type() -> None:
    """
    A spell under a Protocol answers to the Protocol (object or name), single or as a collection, never to its type.

    The Protocol spellframe hides the concrete class from class lookups (2026-11-07, `_answers_class_lookup`;
    Autofac's rule that a declared service hides the component's own type): `x: Impl`, `x: "Impl"` and
    `list[Impl]` no longer select it - before, they did - while `x: IService`, `x: "IService"`,
    `list[IService]` and `list["iservice"]` still do.
    """
    phase = CompilerPhase3()

    class IService(Protocol):
        pass

    class Impl:
        pass

    class Other(Protocol):
        pass

    candidate = _make_spell_stub("impl", spell_obj=Impl, spellframe=IService, spell_name="Impl")

    assert candidate.spellframe_kind is SpellframeKind.contract
    assert phase._spell_contract_keys(candidate) == ("iservice",)
    assert phase._spell_label_key(candidate) == "iservice"
    assert phase._answers_class_lookup(candidate) is False
    for annotation in (IService, "IService"):
        assert phase._matches_annotation(annotation, None, candidate, require_class_spell=True) is True, annotation
    for annotation in (Impl, "Impl"):
        assert phase._matches_annotation(annotation, None, candidate, require_class_spell=True) is False, annotation
    assert phase._matches_annotation(Other, None, candidate, require_class_spell=True) is False
    for annotation in (IService, "iservice"):
        assert phase._matches_annotation(annotation, None, candidate, require_class_spell=False, collection=True) is True, annotation
    for annotation in (Impl, "impl"):
        assert phase._matches_annotation(annotation, None, candidate, require_class_spell=False, collection=True) is False, annotation


@pytest.mark.parametrize(
    ("annotation_name", "collection", "expected"),
    [
        ("Impl", False, []),
        ("IService", False, ["Impl"]),
        ("Spectrum", False, []),
        ("Toolbox", False, []),
        ("spectrum_label", False, []),
        ("Spectrum", True, []),
        ("spectrum_label", True, ["Spectrum", "Toolbox"]),
        ("IService", True, ["Impl"]),
        ("Impl", True, []),
        ("impl", False, []),
        ("iservice", False, ["Impl"]),
        ("Plain", False, ["Plain"]),
        ("Plain", True, ["Plain"]),
        ("plain", False, ["Plain"]),
        ("Named", False, []),
        ("Named", True, []),
        ("named", False, []),
        ("named", True, ["Named"]),
    ],
)
def test_indexed_candidates_equal_the_scan_for_every_kind(annotation_name: str, collection: bool, expected: list[str]) -> None:
    """
    The three-bucket index returns exactly what the scan returns, in pool order, for every annotation and socket kind.

    Only Plain, bound bare under the default binding, answers a class lookup - a class, `list[Class]` or a single
    string's type part (2026-11-07, `_answers_class_lookup`): it alone is in `by_type`. Spectrum and Toolbox under
    a category, Impl under a Protocol and Named bound bare under a binding name are reached only through their
    Protocol (as the class or by name) or their label - before, their class reached them as well.
    """
    phase = CompilerPhase3()

    class IService(Protocol):
        pass

    class Impl:
        pass

    class Spectrum:
        pass

    class Toolbox:
        pass

    class Plain:
        """Bound bare under the default binding: the one spell here a class lookup reaches."""

    class Named:
        """Bound bare under a binding name: hidden from class lookups, still a member of its own label."""

    objects = {"Impl": Impl, "IService": IService, "Spectrum": Spectrum, "Toolbox": Toolbox, "Plain": Plain, "Named": Named}
    annotation: Any = objects.get(annotation_name, annotation_name)
    root_spell = _make_spell_stub("root", spell_obj=object(), spellframe=None, spell_name="RootSpell")
    pool = {
        "spectrum": _make_spell_stub("spectrum", spell_obj=Spectrum, spellframe="spectrum_label", spell_name="Spectrum", binding_name="Spectrum"),
        "toolbox": _make_spell_stub("toolbox", spell_obj=Toolbox, spellframe="spectrum_label", spell_name="Toolbox", binding_name="Toolbox"),
        "impl": _make_spell_stub("impl", spell_obj=Impl, spellframe=IService, spell_name="Impl"),
        "plain": _make_spell_stub("plain", spell_obj=Plain, spellframe=None, spell_name="Plain"),
        "named": _make_spell_stub("named", spell_obj=Named, spellframe=None, spell_name="Named", binding_name="v1"),
    }
    spellbook = SimpleNamespace(_spell_id_pool=pool)
    dep = _make_dependency(
        spell_id="root",
        param_name="dep",
        position=0,
        di_shape=ParameterDIShape.COLLECTION_BY_ANNOTATION if collection else ParameterDIShape.SINGLE_BY_ANNOTATION,
        target_annotation=annotation,
        is_collection=collection,
    )
    index = phase._build_candidate_index(spellbook)
    if collection:
        scanned = phase._resolve_collection_by_annotation(spellbook, dep)
        indexed = phase._resolve_collection_by_annotation(spellbook, dep, index)
    else:
        scanned = phase._resolve_single_by_annotation(root_spell, spellbook, dep)
        indexed = phase._resolve_single_by_annotation(root_spell, spellbook, dep, index)

    assert [candidate.spell_name for candidate in scanned.values()] == expected
    assert list(indexed.items()) == list(scanned.items())
    assert set(index) == {"by_type", "by_label", "by_contract", "by_definition"}
    assert sorted(index["by_type"]) == ["plain"]
    assert sorted(index["by_label"]) == ["iservice", "named", "plain", "spectrum_label"]
    assert sorted(index["by_contract"]) == ["iservice"]
    assert index["by_definition"] == {}


def test_indexed_candidates_equal_the_scan_for_an_existing_object() -> None:
    """The index resolves a bare existing object exactly as the scan does, with no equality gate."""
    phase = CompilerPhase3()

    class Service:
        pass

    class Other:
        pass

    root_spell = _make_spell_stub("root", spell_obj=object(), spellframe=None, spell_name="RootSpell")
    service = _make_spell_stub("svc", spell_obj=Service(), spellframe=None, spell_name="Service")
    other = _make_spell_stub("other", spell_obj=Other, spellframe=None, spell_name="Other")
    spellbook = SimpleNamespace(_spell_id_pool={"svc": service, "other": other})
    dep = _make_dependency(
        spell_id="root",
        param_name="service",
        position=0,
        di_shape=ParameterDIShape.SINGLE_BY_ANNOTATION,
        target_annotation=Service,
    )

    scanned = phase._resolve_single_by_annotation(root_spell, spellbook, dep)
    index = phase._build_candidate_index(spellbook)
    indexed = phase._resolve_single_by_annotation(root_spell, spellbook, dep, index)

    assert list(scanned.values()) == [service]
    assert indexed == scanned
    assert set(index) == {"by_type", "by_label", "by_contract", "by_definition"}
    assert sorted(index["by_type"]) == ["other", "service"]
    assert sorted(index["by_label"]) == ["other", "service"]
    assert index["by_contract"] == {}


@pytest.mark.parametrize("existing_object", [False, True])
@pytest.mark.parametrize(
    ("placement", "answers"),
    [
        ("bare", True),
        ("bare_empty_binding_name", True),
        ("bare_written_default_binding_name", True),
        ("bare_named", False),
        ("category", False),
        ("protocol", False),
    ],
)
def test_class_lookup_reaches_only_a_bare_default_binding_spell_on_scan_and_index(
        placement: str,
        answers: bool,
        existing_object: bool,
) -> None:
    """
    A class lookup reaches a spell only when it is bound bare: no spellframe and the default binding.

    The owner's rulings E1-E3 (2026-11-07; Autofac's rule that a declared service hides the component's own type):
    a class annotation, a single string annotation's type part and `list[Class]` all follow
    `_answers_class_lookup`, on the scan path (`_matches_annotation`) and the index path (`by_type`) alike, so
    both return the same candidates. None, "" and "__default__" all name the default binding, so those bare spells
    answer; a binding name, a string category or a Protocol hides the class, and the label bucket still holds the
    spell under its address label. An existing object follows the same rule through its class.
    """
    phase = CompilerPhase3()

    class IService(Protocol):
        pass

    class Service:
        """The class every lookup in this test names; bound, or its instance bound, at one placement."""

    spellframe: Any = None
    binding_name: Optional[str] = None
    if placement == "bare_empty_binding_name":
        binding_name = ""
    elif placement == "bare_written_default_binding_name":
        binding_name = SpellInputUtils.DEFAULT_BINDING_NAME
    elif placement == "bare_named":
        binding_name = "v1"
    elif placement == "category":
        spellframe = "services"
    elif placement == "protocol":
        spellframe = IService
    candidate = _make_spell_stub(
        "svc",
        spell_obj=Service() if existing_object else Service,
        spellframe=spellframe,
        spell_name="Service",
        binding_name=binding_name,
    )
    root_spell = _make_spell_stub("root", spell_obj=object(), spellframe=None, spell_name="RootSpell")
    spellbook = SimpleNamespace(_spell_id_pool={"svc": candidate})
    index = phase._build_candidate_index(spellbook)
    expected = [candidate] if answers else []

    assert phase._answers_class_lookup(candidate) is answers
    assert ("service" in index["by_type"]) is answers
    assert [entry[2] for entry in index["by_label"][phase._spell_label_key(candidate)]] == [candidate]
    assert phase._matches_annotation(Service, None, candidate, require_class_spell=True) is answers
    assert phase._matches_annotation("Service", None, candidate, require_class_spell=True) is answers
    assert phase._matches_annotation(Service, None, candidate, require_class_spell=False, collection=True) is answers
    for annotation, collection in ((Service, False), ("Service", False), (Service, True)):
        dep = _make_dependency(
            spell_id="root",
            param_name="service",
            position=0,
            di_shape=ParameterDIShape.COLLECTION_BY_ANNOTATION if collection else ParameterDIShape.SINGLE_BY_ANNOTATION,
            target_annotation=annotation,
            is_collection=collection,
        )
        if collection:
            scanned = phase._resolve_collection_by_annotation(spellbook, dep)
            indexed = phase._resolve_collection_by_annotation(spellbook, dep, index)
        else:
            scanned = phase._resolve_single_by_annotation(root_spell, spellbook, dep)
            indexed = phase._resolve_single_by_annotation(root_spell, spellbook, dep, index)
        assert list(scanned.values()) == expected, (annotation, collection)
        assert list(indexed.items()) == list(scanned.items()), (annotation, collection)


def test_protocol_definition_is_a_candidate_for_its_own_annotation_until_an_implementer_exists() -> None:
    """A Protocol bound resolvable=False matches `x: Proto` (OVERRIDE_REQUIRED); a recorded implementer wins over it."""
    phase = CompilerPhase3()

    class IRepo(Protocol):
        pass

    class Repo:
        pass

    root_spell = _make_spell_stub("root", spell_obj=object(), spellframe=None, spell_name="RootSpell")
    definition = _make_spell_stub("def", spell_obj=IRepo, spellframe=None, spell_name="IRepo", resolvable=False)
    implementer = _make_spell_stub("impl", spell_obj=Repo, spellframe=IRepo, spell_name="Repo")
    dep = _make_dependency(spell_id="root", param_name="repo", position=0,
                           di_shape=ParameterDIShape.SINGLE_BY_ANNOTATION, target_annotation=IRepo)

    assert phase._spell_definition_key(definition) == "irepo"
    assert phase._spell_definition_key(implementer) is None
    only_definition = SimpleNamespace(_spell_id_pool={"def": definition})
    index = phase._build_candidate_index(only_definition)
    assert sorted(index["by_definition"]) == ["irepo"]
    assert list(phase._resolve_single_by_annotation(root_spell, only_definition, dep).values()) == [definition]
    assert list(phase._resolve_single_by_annotation(root_spell, only_definition, dep, index).values()) == [definition]
    both = SimpleNamespace(_spell_id_pool={"def": definition, "impl": implementer})
    index = phase._build_candidate_index(both)
    assert list(phase._resolve_single_by_annotation(root_spell, both, dep).values()) == [implementer]
    assert list(phase._resolve_single_by_annotation(root_spell, both, dep, index).values()) == [implementer]
    # a string annotation reaches the definition through its type key too
    named = _make_dependency(spell_id="root", param_name="repo", position=0,
                             di_shape=ParameterDIShape.SINGLE_BY_ANNOTATION, target_annotation="IRepo")
    assert list(phase._resolve_single_by_annotation(root_spell, only_definition, named).values()) == [definition]


@pytest.mark.parametrize("placement", ["binding_name", "spellframe"])
def test_protocol_definition_hidden_from_class_lookups_is_still_a_candidate_for_its_protocol(placement: str) -> None:
    """
    The Protocol - as the class, a string or a ForwardRef - reaches its definition whatever the definition's binding.

    A Protocol bound resolvable=False under a binding name or under a spellframe offers no type key (2026-11-07,
    `_answers_class_lookup`), so it is absent from `by_type`. Its definition key is not gated by that rule: `x: Proto`
    reads it through `by_definition`, and a single socket naming the Protocol - `x: "Proto"`, or the ForwardRef a
    `TYPE_CHECKING`-only import leaves - is a contract lookup that finds the definition exactly as the Protocol object
    does, on the scan and the index path alike. Only a Protocol definition keeps that key on a name: a concrete class
    bound at the same placement is not found by its string name.
    """
    phase = CompilerPhase3()

    class IRepo(Protocol):
        pass

    class Repo:
        """A concrete class bound at the same placement: its name is a class lookup, which the placement hides."""

    spellframe: Optional[str] = "repos" if placement == "spellframe" else None
    binding_name: Optional[str] = "described" if placement == "binding_name" else None
    root_spell = _make_spell_stub("root", spell_obj=object(), spellframe=None, spell_name="RootSpell")
    definition = _make_spell_stub("def", spell_obj=IRepo, spellframe=spellframe, spell_name="IRepo",
                                  binding_name=binding_name, resolvable=False)
    concrete = _make_spell_stub("repo", spell_obj=Repo, spellframe=spellframe, spell_name="Repo",
                                binding_name=binding_name)
    spellbook = SimpleNamespace(_spell_id_pool={"def": definition, "repo": concrete})
    index = phase._build_candidate_index(spellbook)

    assert phase._answers_class_lookup(definition) is False
    assert phase._answers_class_lookup(concrete) is False
    assert index["by_type"] == {}
    assert sorted(index["by_definition"]) == ["irepo"]
    for annotation, expected in (
            (IRepo, [definition]),
            ("IRepo", [definition]),
            (typing.ForwardRef("IRepo"), [definition]),
            ("Repo", []),
            (typing.ForwardRef("Repo"), []),
    ):
        dep = _make_dependency(spell_id="root", param_name="repo", position=0,
                               di_shape=ParameterDIShape.SINGLE_BY_ANNOTATION, target_annotation=annotation)
        scanned = phase._resolve_single_by_annotation(root_spell, spellbook, dep)
        indexed = phase._resolve_single_by_annotation(root_spell, spellbook, dep, index)
        assert list(scanned.values()) == expected, annotation
        assert list(indexed.items()) == list(scanned.items()), annotation


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
        root_spell.spell_index.selected_spell_id = None
    graph = SpellSymbolicGraph(
        spell_id="root",
        dependencies=[],
    )

    with pytest.raises(RuntimeError, match=expected_message):
        phase._build_local_topology(
            root_spell, graph, {}, requirements=SimpleNamespace(parameters=[]), socket_references={},
        )


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
        spell_id="root",
        param_name="alpha",
        position=0,
        di_shape=ParameterDIShape.SINGLE_BY_ANNOTATION,
        is_optional=False,
    )
    dep_contract = _make_dependency(
        spell_id="root",
        param_name="beta",
        position=1,
        di_shape=ParameterDIShape.SPELL_CONTRACT,
        is_optional=True,
    )
    graph = SpellSymbolicGraph(
        spell_id="root",
        dependencies=[dep_normal, dep_contract],
    )
    socket_targets = {("alpha", 0): ["dep1", "dep2"]}

    topology = phase._build_local_topology(
        root_spell, graph, socket_targets,
        requirements=SimpleNamespace(parameters=[
            SimpleNamespace(name="alpha", kind=inspect.Parameter.POSITIONAL_ONLY),
            SimpleNamespace(name="beta", kind=inspect.Parameter.KEYWORD_ONLY),
        ]),
        socket_references={},
    )

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
    assert alpha_socket.parameter_kind == "POSITIONAL_ONLY"
    assert beta_socket.parameter_kind == "KEYWORD_ONLY"

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
    graph: Any = SpellSymbolicGraph(spell_id="root", dependencies=[])

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
    root_spell.spell_index.selected_spell_id = None

    with pytest.raises(RuntimeError, match="bound spell current id"):
        phase._build_local_frame_dag(
            spell=root_spell,
            spellbook=SimpleNamespace(_spell_id_pool={}),
            spell_system_states=_SpellSystemStatesStub(),
            requirements=SimpleNamespace(parameters=[]),
            graph=SpellSymbolicGraph(spell_id="root", dependencies=[]),
            cancellation_event=_CancelStub(is_set=False),
        )


def test_resolve_single_by_annotation_returns_exact_match() -> None:
    """Phase 3 should resolve a single-annotation socket to one candidate."""
    phase = CompilerPhase3()

    class _ServiceFrame(Protocol):
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
        spell_id="root",
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
    """
    No valid class candidate yields an empty mapping instead of an error.

    The caller records the parameter as an UNRESOLVED_INPUT socket that the
    constructing meld supplies (contract since 2026-09-26; ambiguity still raises).
    A method spell registered under the frame is not a class candidate.
    """
    phase = CompilerPhase3()

    class _ServiceFrame(Protocol):
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
        spell_id="root",
        param_name="service",
        position=0,
        di_shape=ParameterDIShape.SINGLE_BY_ANNOTATION,
        target_annotation=_ServiceFrame,
    )

    assert phase._resolve_single_by_annotation(root_spell, spellbook, dep) == {}


def test_resolve_single_by_annotation_raises_on_multiple_matches() -> None:
    """Phase 3 should fail fast when a single socket matches multiple spells."""
    phase = CompilerPhase3()

    class _ServiceFrame(Protocol):
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
        spell_id="root",
        param_name="service",
        position=0,
        di_shape=ParameterDIShape.SINGLE_BY_ANNOTATION,
        target_annotation=_ServiceFrame,
    )

    # 2026-10-04: ambiguity is no longer a Phase-3 raise; every candidate comes back and the DAG
    # builder records the socket as AMBIGUOUS_INPUT for Phase 4's AMBIGUOUS_PROVIDER report.
    resolved = phase._resolve_single_by_annotation(root_spell, spellbook, dep)
    assert {spell_obj.spell_name for spell_obj in resolved.values()} == {"DepA", "DepB"}


def test_resolve_collection_by_annotation_returns_all_matches() -> None:
    """Phase 3 collection DI should keep both class and method matches."""
    phase = CompilerPhase3()

    class _ServiceFrame(Protocol):
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
        spell_id="root",
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

    class _ServiceFrame(Protocol):
        pass

    dep = _make_dependency(
        spell_id="root",
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
        spell_id="root",
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
        spell_id="root",
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
        spell_id="root",
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
        spell_id="root",
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
        spell_id="root",
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
        spell_id="root",
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


def _scan_profile_pool(spell_obj: Any) -> tuple[Any, Any, Any]:
    """The reported pool: one ScanProfile under "agents", its namesake under another category."""
    agents = _make_spell_stub("agents", spell_obj=spell_obj, spellframe="agents", spell_name="ScanProfile",
                              binding_name="ScanProfile")
    tools = _make_spell_stub("tools", spell_obj=spell_obj, spellframe="artificial_intelligence_tools",
                             spell_name="ScanProfile", binding_name="ScanProfile")
    return agents, tools, SimpleNamespace(_spell_id_pool={"agents": agents, "tools": tools})


@pytest.mark.parametrize(("frame", "written"), [
    ("agents", "ScanProfile"), ("agents", "scanprofile"), ("Agents", "SCANPROFILE"),
])
def test_resolve_spellmap_default_capitalized_binding_name_no_longer_fails_to_resolve(frame: str,
                                                                                      written: str) -> None:
    """
    Regression (0.2.8226): a frame-only SpellMap keeps the binding name as written, as Bind does, and Phase 3
    compares names and string categories by their normalized keys, so every spelling selects the provider
    bound as ("agents", "ScanProfile") and never its namesake. Before, the SpellMap stored "scanprofile" and
    was compared with the raw "ScanProfile", raising "SpellMap default could not be resolved".
    """
    agents, _tools, spellbook = _scan_profile_pool(object())
    root_spell = _make_spell_stub("root", spell_obj=object(), spellframe=None, spell_name="MCPScanner")
    dep = _make_dependency(spell_id="root", param_name="profile", position=0,
                           di_shape=ParameterDIShape.SPELLMAP_DEFAULT,
                           spellmap_default=SpellMap(spellframe=frame, binding_name=written))
    resolved = CompilerPhase3()._resolve_spellmap_default(root_spell, spellbook, dep)
    assert list(resolved.values()) == [agents]


def test_resolve_spellmap_default_explicit_spell_matches_a_capitalized_binding_name() -> None:
    """The explicit-spell form filters frame and binding name by the same normalized keys."""
    provider = object()
    agents, _tools, spellbook = _scan_profile_pool(provider)
    root_spell = _make_spell_stub("root", spell_obj=object(), spellframe=None, spell_name="MCPScanner")
    dep = _make_dependency(spell_id="root", param_name="profile", position=0,
                           di_shape=ParameterDIShape.SPELLMAP_DEFAULT,
                           spellmap_default=SpellMap(provider, spellframe="AGENTS", binding_name="ScanProfile"))
    resolved = CompilerPhase3()._resolve_spellmap_default(root_spell, spellbook, dep)
    assert list(resolved.values()) == [agents]


@pytest.mark.parametrize("written", [None, ""])
def test_resolve_spellmap_default_none_and_empty_binding_name_select_the_default_binding(written: Any) -> None:
    """None and "" both name the default binding, as in the address key: a named sibling is not selected."""
    default = _make_spell_stub("default", spell_obj=object(), spellframe="agents", spell_name="ScanProfile")
    named = _make_spell_stub("named", spell_obj=object(), spellframe="agents", spell_name="ScanProfile",
                             binding_name="ScanProfile")
    root_spell = _make_spell_stub("root", spell_obj=object(), spellframe=None, spell_name="MCPScanner")
    dep = _make_dependency(spell_id="root", param_name="profile", position=0,
                           di_shape=ParameterDIShape.SPELLMAP_DEFAULT,
                           spellmap_default=SpellMap(spellframe="agents", binding_name=written))
    spellbook = SimpleNamespace(_spell_id_pool={"default": default, "named": named})
    resolved = CompilerPhase3()._resolve_spellmap_default(root_spell, spellbook, dep)
    assert list(resolved.values()) == [default]


def _class_lookup_spellmap_pool(provider: Any) -> tuple[dict[str, Any], Any]:
    """
    One provider at four addresses: bare and under the category "agents", each under the default binding and "v1".

    A stub-only pool (Bind registers one object once): it puts side by side every placement a `SpellMap(spell=...)`
    could reach, so a lookup that reached more than the one address it names would raise "resolved to multiple
    candidates" instead of returning a single stub.

    Args:
        provider: The object every stub binds, the `spell` a SpellMap names.

    Returns:
        tuple[dict[str, Any], Any]: The stubs by placement ("bare", "named", "framed", "framed_named") and a
        spellbook stand-in whose pool holds them in that order.
    """
    stubs = {
        "bare": _make_spell_stub("bare", spell_obj=provider, spellframe=None, spell_name="Provider"),
        "named": _make_spell_stub("named", spell_obj=provider, spellframe=None, spell_name="Provider",
                                  binding_name="v1"),
        "framed": _make_spell_stub("framed", spell_obj=provider, spellframe="agents", spell_name="Provider"),
        "framed_named": _make_spell_stub("framed_named", spell_obj=provider, spellframe="agents",
                                         spell_name="Provider", binding_name="v1"),
    }
    return stubs, SimpleNamespace(_spell_id_pool=dict(stubs))


@pytest.mark.parametrize(("written", "expected"), [
    (None, "bare"), ("", "bare"), ("v1", "named"), ("V1", "named"),
])
def test_resolve_spellmap_default_explicit_spell_without_a_spellframe_reaches_only_the_bare_spell(
        written: Optional[str],
        expected: str,
) -> None:
    """
    `SpellMap(spell=X)` with no spellframe is a class lookup: it reaches only X bound with no spellframe.

    The owner's rulings E2-E3 (2026-11-07): with no binding name (None or "") it selects X under the default
    binding; with `binding_name` it selects X bound bare under that name, compared case-insensitively. X under a
    spellframe is never selected, whatever its binding - it is reached through `SpellMap(X, spellframe=...)`.
    Before, X matched at every address here, and this pool raised "resolved to multiple candidates".
    """
    provider = object()
    stubs, spellbook = _class_lookup_spellmap_pool(provider)
    root_spell = _make_spell_stub("root", spell_obj=object(), spellframe=None, spell_name="Consumer")
    dep = _make_dependency(spell_id="root", param_name="provider", position=0,
                           di_shape=ParameterDIShape.SPELLMAP_DEFAULT,
                           spellmap_default=SpellMap(provider, binding_name=written))
    resolved = CompilerPhase3()._resolve_spellmap_default(root_spell, spellbook, dep)
    assert list(resolved.values()) == [stubs[expected]]


@pytest.mark.parametrize(("spellframe", "bound_as", "written"), [
    ("agents", None, None),
    ("agents", "v1", "v1"),
    ("IProvider", None, None),
    (None, "v1", None),
    (None, None, "v1"),
])
def test_resolve_spellmap_default_explicit_spell_without_a_spellframe_refuses_an_address_it_does_not_name(
        spellframe: Optional[str],
        bound_as: Optional[str],
        written: Optional[str],
) -> None:
    """
    `SpellMap(spell=X)` with no spellframe raises "could not be resolved" when X is bound only elsewhere.

    The owner's rulings E2-E3 (2026-11-07): X under a spellframe - a string category or a Protocol ("IProvider"
    stands for the Protocol defined here) - is refused whatever binding name the SpellMap writes, even the one X is
    bound under; X bound bare under a binding name is refused when the SpellMap writes none, and X under the
    default binding when it writes another name. Before, every case but the last resolved to X; the last raised
    then as it does now.
    """
    class IProvider(Protocol):
        """Contract frame."""

    provider = object()
    frame: Any = IProvider if spellframe == "IProvider" else spellframe
    only = _make_spell_stub("only", spell_obj=provider, spellframe=frame, spell_name="Provider",
                            binding_name=bound_as)
    root_spell = _make_spell_stub("root", spell_obj=object(), spellframe=None, spell_name="Consumer")
    dep = _make_dependency(spell_id="root", param_name="provider", position=0,
                           di_shape=ParameterDIShape.SPELLMAP_DEFAULT,
                           spellmap_default=SpellMap(provider, binding_name=written))
    with pytest.raises(RuntimeError, match="could not be resolved"):
        CompilerPhase3()._resolve_spellmap_default(root_spell, SimpleNamespace(_spell_id_pool={"only": only}), dep)


def test_resolve_spellmap_default_explicit_spell_with_its_spellframe_is_unchanged() -> None:
    """
    `SpellMap(spell=X, spellframe=F, ...)` names the frame, so the class-lookup rule (2026-11-07) leaves it as it was.

    It reaches X under F only - never X bound bare or under another frame: with a binding name, X at that name;
    with none, X under F at any binding, as before. The no-binding-name case matters here: the default-binding
    filter of the plain class lookup must not reach a SpellMap that names its frame.
    """
    class IProvider(Protocol):
        """Contract frame."""

    provider = object()
    bare = _make_spell_stub("bare", spell_obj=provider, spellframe=None, spell_name="Provider")
    named = _make_spell_stub("named", spell_obj=provider, spellframe=None, spell_name="Provider", binding_name="v1")
    framed_named = _make_spell_stub("framed_named", spell_obj=provider, spellframe="agents", spell_name="Provider",
                                    binding_name="v1")
    contract = _make_spell_stub("contract", spell_obj=provider, spellframe=IProvider, spell_name="Provider")
    spellbook = SimpleNamespace(_spell_id_pool={"bare": bare, "named": named, "framed_named": framed_named,
                                                "contract": contract})
    root_spell = _make_spell_stub("root", spell_obj=object(), spellframe=None, spell_name="Consumer")
    phase = CompilerPhase3()

    def _resolve(spellmap: SpellMap) -> list[Any]:
        """
        Resolve one SpellMap default over this test's pool through Phase 3's SPELLMAP_DEFAULT path.

        Args:
            spellmap: The descriptor the consumer's parameter carries.

        Returns:
            list[Any]: The selected stubs in pool order; Phase 3's RuntimeError propagates on a miss.
        """
        dep = _make_dependency(spell_id="root", param_name="provider", position=0,
                               di_shape=ParameterDIShape.SPELLMAP_DEFAULT, spellmap_default=spellmap)
        return list(phase._resolve_spellmap_default(root_spell, spellbook, dep).values())

    assert _resolve(SpellMap(provider, spellframe="agents", binding_name="v1")) == [framed_named]
    assert _resolve(SpellMap(provider, spellframe="Agents")) == [framed_named]
    assert _resolve(SpellMap(provider, spellframe=IProvider)) == [contract]
    with pytest.raises(RuntimeError, match="could not be resolved"):
        _resolve(SpellMap(provider, spellframe=IProvider, binding_name="v1"))


def test_spellmap_frame_matching_folds_case_for_categories_only() -> None:
    """String categories match case-insensitively; a Protocol frame matches only itself, never its name."""

    class IScanner(Protocol):
        """Contract frame."""

        def scan(self) -> None:
            """Scan once."""

    assert CompilerPhase3._spellmap_frame_matches("agents", "Agents")
    assert CompilerPhase3._spellmap_frame_matches("AGENTS", "agents")
    assert not CompilerPhase3._spellmap_frame_matches("agents", "tools")
    assert CompilerPhase3._spellmap_frame_matches(IScanner, IScanner)
    assert not CompilerPhase3._spellmap_frame_matches(IScanner, "IScanner")
    assert not CompilerPhase3._spellmap_frame_matches("IScanner", IScanner)
    assert not CompilerPhase3._spellmap_frame_matches(None, "agents")


def test_build_local_frame_dag_skips_unresolved_collection() -> None:
    """Phase 3 local frame build should leave collections empty when unresolved."""
    phase = CompilerPhase3()
    root_spell = _make_spell_stub(
        "root",
        spell_obj=object(),
        spellframe=None,
        spell_name="RootSpell",
    )
    spell_system_states = _SpellSystemStatesStub()
    graph = SpellSymbolicGraph(
        spell_id="root",
        dependencies=[
            _make_dependency(
                spell_id="root",
                param_name="dep",
                position=0,
                di_shape=ParameterDIShape.COLLECTION_BY_ANNOTATION,
                target_annotation=object(),
                is_collection=True,
            )
        ],
    )

    ordered_node_ids, dependency_spell_ids = phase._build_local_frame_dag(
        spell=root_spell,
        spellbook=SimpleNamespace(_spell_id_pool={}),
        spell_system_states=spell_system_states,
        requirements=SimpleNamespace(parameters=[]),
        graph=graph,
        cancellation_event=_CancelStub(is_set=False),
    )

    assert ordered_node_ids == ["root"]
    assert dependency_spell_ids == []
    assert spell_system_states.dependencies_calls == [
        (root_spell.spell_index, [])
    ]


def test_build_local_frame_dag_handles_spellmap_default_success() -> None:
    """Phase 3 local frame build should record resolved SpellMap defaults as dependencies."""
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
        spell_id="root",
        dependencies=[
            _make_dependency(
                spell_id="root",
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

    ordered_node_ids, dependency_spell_ids = phase._build_local_frame_dag(
        spell=root_spell,
        spellbook=SimpleNamespace(_spell_id_pool={"dep": dependency_spell}),
        spell_system_states=spell_system_states,
        requirements=SimpleNamespace(parameters=[]),
        graph=graph,
        cancellation_event=_CancelStub(is_set=False),
    )

    assert ordered_node_ids == ["dep-id", "root"]
    assert dependency_spell_ids == ["dep-id"]
    assert spell_system_states.dependencies_calls == [
        (root_spell.spell_index, ["dep-id"])
    ]


def test_build_local_frame_dag_ignores_contract_shapes() -> None:
    """Phase 3 local frame build should not record dependencies for SpellContract sockets."""
    phase = CompilerPhase3()
    root_spell = _make_spell_stub(
        "root",
        spell_obj=object(),
        spellframe=None,
        spell_name="RootSpell",
    )
    spell_system_states = _SpellSystemStatesStub()
    graph = SpellSymbolicGraph(
        spell_id="root",
        dependencies=[
            _make_dependency(
                spell_id="root",
                param_name="contract",
                position=0,
                di_shape=ParameterDIShape.SPELL_CONTRACT,
                target_annotation=object(),
            ),
        ],
    )

    ordered_node_ids, dependency_spell_ids = phase._build_local_frame_dag(
        spell=root_spell,
        spellbook=SimpleNamespace(_spell_id_pool={}),
        spell_system_states=spell_system_states,
        requirements=SimpleNamespace(parameters=[]),
        graph=graph,
        cancellation_event=_CancelStub(is_set=False),
    )

    assert ordered_node_ids == ["root"]
    assert dependency_spell_ids == []
    assert spell_system_states.dependencies_calls == [
        (root_spell.spell_index, [])
    ]
    topology = spell_system_states.topology_calls[0][1]
    assert [socket.socket_kind.name for socket in topology.sockets] == [
        "SPELL_CONTRACT",
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
    artifact._requirements = SimpleNamespace(parameters=[])
    artifact._symbolic_graph = SpellSymbolicGraph(
        spell_id="root",
        dependencies=[],
    )

    with pytest.raises(RuntimeError, match="live SpellSystemStates surface"):
        phase.run(
            root_spell,
            artifact,
            SimpleNamespace(_spell_id_pool={}),
            None,
        )


def test_build_local_frame_dag_orders_dependencies_by_id_then_root() -> None:
    """The local frame lists distinct dependencies ascending by id, then the root last."""
    phase = CompilerPhase3()

    class _FrameA(Protocol):
        pass

    class _FrameB(Protocol):
        pass

    root_spell = _make_spell_stub(
        "root",
        spell_obj=object(),
        spellframe=None,
        spell_name="RootSpell",
    )
    dep_a = _make_spell_stub("dep-a", spell_obj=object(), spellframe=_FrameA, spell_name="DepA")
    dep_b = _make_spell_stub("dep-b", spell_obj=object(), spellframe=_FrameB, spell_name="DepB")
    spell_system_states = _SpellSystemStatesStub()
    graph = SpellSymbolicGraph(
        spell_id="root",
        dependencies=[
            _make_dependency(
                spell_id="root",
                param_name="second",
                position=0,
                di_shape=ParameterDIShape.SINGLE_BY_ANNOTATION,
                target_annotation=_FrameB,
            ),
            _make_dependency(
                spell_id="root",
                param_name="first",
                position=1,
                di_shape=ParameterDIShape.SINGLE_BY_ANNOTATION,
                target_annotation=_FrameA,
            ),
            _make_dependency(
                spell_id="root",
                param_name="again",
                position=2,
                di_shape=ParameterDIShape.SINGLE_BY_ANNOTATION,
                target_annotation=_FrameB,
            ),
        ],
    )

    ordered_node_ids, dependency_spell_ids = phase._build_local_frame_dag(
        spell=root_spell,
        spellbook=SimpleNamespace(_spell_id_pool={"dep-a": dep_a, "dep-b": dep_b}),
        spell_system_states=spell_system_states,
        requirements=SimpleNamespace(parameters=[]),
        graph=graph,
        cancellation_event=_CancelStub(is_set=False),
    )

    # Resolution order is kept for the dependency ids (a spell reached through
    # two sockets appears twice); the frame order is the retired DAG's law.
    assert dependency_spell_ids == ["dep-b", "dep-a", "dep-b"]
    assert ordered_node_ids == ["dep-a", "dep-b", "root"]
    assert spell_system_states.dependencies_calls == [
        (root_spell.spell_index, ["dep-b", "dep-a", "dep-b"])
    ]
    topology = spell_system_states.topology_calls[0][1]
    assert [socket.target_spell_ids for socket in topology.sockets] == [
        ("dep-b",),
        ("dep-a",),
        ("dep-b",),
    ]


def test_build_local_frame_dag_records_self_dependency_out_of_the_frame() -> None:
    """A spell that resolves itself is recorded as its own dependency and stays out of the frame order."""
    phase = CompilerPhase3()

    class _RootFrame(Protocol):
        pass

    root_spell = _make_spell_stub(
        "root",
        spell_obj=object(),
        spellframe=_RootFrame,
        spell_name="RootSpell",
    )
    spell_system_states = _SpellSystemStatesStub()
    graph = SpellSymbolicGraph(
        spell_id="root",
        dependencies=[
            _make_dependency(
                spell_id="root",
                param_name="me",
                position=0,
                di_shape=ParameterDIShape.SINGLE_BY_ANNOTATION,
                target_annotation=_RootFrame,
            ),
        ],
    )

    ordered_node_ids, dependency_spell_ids = phase._build_local_frame_dag(
        spell=root_spell,
        spellbook=SimpleNamespace(_spell_id_pool={"root": root_spell}),
        spell_system_states=spell_system_states,
        requirements=SimpleNamespace(parameters=[]),
        graph=graph,
        cancellation_event=_CancelStub(is_set=False),
    )

    # Recorded everywhere Phase 4 looks; absent from the ordered frame (root once, last).
    assert dependency_spell_ids == ["root"]
    assert ordered_node_ids == ["root"]
    assert spell_system_states.dependencies_calls == [
        (root_spell.spell_index, ["root"])
    ]
    topology = spell_system_states.topology_calls[0][1]
    assert [socket.target_spell_ids for socket in topology.sockets] == [("root",)]


def test_run_builds_resolution_frame_and_updates_topology(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Phase 3 should store the local frame and publish dependencies/topology."""
    phase = CompilerPhase3()

    class _ServiceFrame(Protocol):
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
    spellbook = SimpleNamespace(_spell_id_pool={"dep": dependency_spell}, _nexus_publish_enabled=False)
    spell_system_states = _SpellSystemStatesStub()
    artifact = SpellCompilerArtifact("root")
    artifact._requirements = SimpleNamespace(parameters=[])
    artifact._symbolic_graph = SpellSymbolicGraph(
        spell_id="root",
        dependencies=[
            _make_dependency(
                spell_id="root",
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
    assert artifact._resolution_frame.ordered_node_ids == ["dep", "root"]

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
    ],
)
def test_socket_kind_for_dep_mapping(
        di_shape: ParameterDIShape,
        expected_kind_name: str,
) -> None:
    """Phase 3 socket-kind mapping should classify all supported DI shapes."""
    phase = CompilerPhase3()
    dep = _make_dependency(
        spell_id="root",
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
    artifact._requirements = SimpleNamespace(parameters=[])
    artifact._symbolic_graph = SpellSymbolicGraph(
        spell_id="root",
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
