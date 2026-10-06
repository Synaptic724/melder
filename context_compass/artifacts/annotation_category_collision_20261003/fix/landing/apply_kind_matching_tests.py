"""
Test-side edits for patch annotation_kind_matching_2026_10_04: the regression module's markers come off and
its guards follow the ruling; the Phase 3 and Bind unit files pin the kind rule.

Usage: python apply_kind_matching_tests.py <repo_root>
"""
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]).resolve()


def read(rel: str):
    path = ROOT / rel
    raw = path.read_bytes()
    nl = "\r\n" if b"\r\n" in raw else "\n"
    return path, raw.decode("utf-8"), nl


def replace_once(text: str, old: str, new: str, nl: str, label: str) -> str:
    old_n = old.replace("\n", nl)
    new_n = new.replace("\n", nl)
    count = text.count(old_n)
    assert count == 1, f"{label}: anchor found {count} times"
    return text.replace(old_n, new_n)


# ---------------------------------------------------------------------------
# A. the regression module: markers off, guards per the ruling, new guards
# ---------------------------------------------------------------------------
path, text, nl = read("tests/integration/melder/aether/conduit/test_annotation_category_collision_integration.py")
text = replace_once(text, '''"""Integration regressions: a type annotation selects type providers; a spellframe is a category.

Reported 2026-10-03 (MelderOps, EPIC-2026-10-03-annotation_category_provider_collision): since 0.2.8218 Phase 3
matches a constructor annotation by its lowercased name against each spell's spellframe key as well as its
type key, so a category named like a type ("spectrum" holding 14 framework services) makes every member a
candidate provider for `spectrum: Spectrum` - an ambiguity when the real provider is also bound, and a silent
wrong-type injection when it is not. Owner ruling (recorded in the epic): a spellframe is a category, not a
spell; a type annotation must not make every member of a same-named category a provider.

The cases marked xfail(strict=True) state the ruled behaviour and fail today; the marker comes off with the
repair, and pytest fails loudly (XPASS strict) if the defect disappears while a marker is still in place.
The unmarked cases are guards for behaviour the repair must keep.
"""
''', '''"""Integration regressions: annotations match by kind; a spellframe is a category or a Protocol contract.

Reported 2026-10-03 (MelderOps, EPIC-2026-10-03-annotation_category_provider_collision): since 0.2.8218 Phase 3
matched a constructor annotation by its lowercased name against each spell's spellframe key as well as its
type key, so a category named like a type ("spectrum" holding 14 framework services) made every member a
candidate provider for `spectrum: Spectrum` - an ambiguity when the real provider was also bound, and a silent
wrong-type injection when it was not. Owner rulings (2026-10-03): a spellframe is a label; a string frame is a
category and satisfies no annotation; a Protocol frame is a category AND a contract, and a Protocol-typed
parameter resolves to the spells bound under it; a concrete class is not a valid spellframe; the binding
records the kind (`Spell.spellframe_kind`) so Phase 3 reads it instead of inferring a meaning from a name.

Repaired 2026-10-04 (annotation_kind_matching): the four defect cases below ran under xfail(strict=True) until
then; the guards pin what the repair must keep, and the new cases pin the ruled contract and collection rules.
"""
''', nl, "regression docstring")
text = replace_once(text, '''import sys
import types
from collections.abc import Iterator
from typing import Any, Type

import pytest
''', '''import sys
import types
from collections.abc import Iterator
from typing import Any, Protocol, Type

import pytest
''', nl, "regression imports")
text = replace_once(text, '''class IService:
    """A type used as a spellframe object: a shape label, not a string category."""
''', '''class IService(Protocol):
    """A Protocol used as a spellframe: a category label AND the contract its members are checked against."""


class ServiceShape:
    """A concrete class: not a valid spellframe since 2026-10-04 (neither a string nor a Protocol)."""
''', nl, "regression IService")
text = replace_once(text, '''class Client(Cleanable):
    """Consumer annotated with the shape label."""
''', '''class Client(Cleanable):
    """Consumer annotated with the Protocol contract."""
''', nl, "regression Client doc")
text = replace_once(text, '''_EPIC = "EPIC-2026-10-03-annotation_category_provider_collision: a same-named spellframe category is read as a provider set"


@pytest.mark.parametrize("annotation", ["class", "string"])
@pytest.mark.parametrize(
    "shared_category",
    [
        False,
        pytest.param(True, marks=pytest.mark.xfail(strict=True, reason=_EPIC)),
    ],
''', '''def _consumer_with_unbound_annotation(class_name: str, param_name: str, annotation_text: str) -> Type[Any]:
    """
    Build a consumer class in its own module whose one parameter carries an UNBOUND string annotation.

    The module never imports the named type, so when Phase 3 reads the annotation (Python 3.14 evaluates
    annotations lazily) it gets the string itself - the shape a `TYPE_CHECKING`-only import leaves at runtime.
    """
    source = (
        "from melder import Cleanable\\n"
        "class {cls}(Cleanable):\\n"
        "    def __init__(self, *, {param}: '{annotation}') -> None:\\n"
        "        super().__init__()\\n"
        "        self.{param} = {param}\\n"
        "    def cleanup(self) -> None:\\n"
        "        if self._cleaned:\\n"
        "            return\\n"
        "        self._cleaned = True\\n"
        "        del self.{param}\\n"
    ).format(cls=class_name, param=param_name, annotation=annotation_text)
    module_name = "melder_tests_unbound_{0}".format(class_name.lower())
    module = types.ModuleType(module_name)
    sys.modules[module_name] = module
    exec(compile(source, "<{0}>".format(module_name), "exec"), module.__dict__)
    return module.__dict__[class_name]


@pytest.mark.parametrize("annotation", ["class", "string"])
@pytest.mark.parametrize(
    "shared_category",
    [
        False,
        True,
    ],
''', nl, "regression matrix markers")
text = replace_once(text, '''@pytest.mark.xfail(strict=True, reason=_EPIC)
def test_type_checking_only_string_annotation_selects_the_spectrum_provider() -> None:
''', '''def test_type_checking_only_string_annotation_selects_the_spectrum_provider() -> None:
''', nl, "regression marker 2")
text = replace_once(text, '''@pytest.mark.xfail(strict=True, reason=_EPIC + " (silent wrong-type injection)")
def test_lone_category_member_is_not_injected_for_a_type_annotation() -> None:
''', '''def test_lone_category_member_is_not_injected_for_a_type_annotation() -> None:
''', nl, "regression marker 3")
text = replace_once(text, '''def test_guard_class_object_frame_is_a_shape_label_that_resolves_its_annotation() -> None:
    """GUARD: an implementation bound under a type used as its spellframe satisfies that type's annotation."""
    root = _dynamic_root("annotation-category-shape-label")
    try:
        root.bind(spell=Impl, existence="unique_per_conduit", spellframe=IService,
                  disposal_method_names=["cleanup"])
        root.bind(spell=Client, existence="many", spellframe="clients", binding_name="client",
                  disposal_method_names=["cleanup"])
        client = root.meld(spellframe="clients", binding_name="client")
        assert isinstance(client.svc, Impl)
    finally:
        root.cleanup()
''', '''def test_guard_protocol_frame_is_a_contract_that_resolves_its_annotation() -> None:
    """GUARD: an implementation bound under a Protocol spellframe satisfies a parameter annotated with it."""
    root = _dynamic_root("annotation-category-contract")
    try:
        root.bind(spell=Impl, existence="unique_per_conduit", spellframe=IService,
                  disposal_method_names=["cleanup"])
        root.bind(spell=Client, existence="many", spellframe="clients", binding_name="client",
                  disposal_method_names=["cleanup"])
        client = root.meld(spellframe="clients", binding_name="client")
        assert isinstance(client.svc, Impl)
    finally:
        root.cleanup()


def test_type_checking_only_string_naming_a_protocol_resolves_the_contract() -> None:
    """A consumer annotated `svc: "IService"` with the name unbound at runtime resolves the Protocol's member."""
    root = _dynamic_root("annotation-category-contract-string")
    try:
        root.bind(spell=Impl, existence="unique_per_conduit", spellframe=IService,
                  disposal_method_names=["cleanup"])
        consumer = _consumer_with_unbound_annotation("ClientUnbound", "svc", "IService")
        root.bind(spell=consumer, existence="many", spellframe="clients", binding_name="client",
                  disposal_method_names=["cleanup"])
        client = root.meld(spellframe="clients", binding_name="client")
        assert isinstance(client.svc, Impl)
    finally:
        root.cleanup()


def test_concrete_class_spellframe_is_refused_at_bind() -> None:
    """A spellframe must be a string category or a Protocol contract; a concrete class is refused with the remedy."""
    root = _dynamic_root("annotation-category-refusal")
    try:
        with pytest.raises(TypeError, match="string category or a Protocol contract") as caught:
            root.bind(spell=Impl, existence="unique_per_conduit", spellframe=ServiceShape,
                      disposal_method_names=["cleanup"])
        assert "ServiceShape" in str(caught.value)
        assert "spellframe='ServiceShape'" in str(caught.value)
        with pytest.raises(TypeError, match="string category or a Protocol contract"):
            root.bind(spell=Impl, existence="unique_per_conduit", spellframe=42,
                      disposal_method_names=["cleanup"])
    finally:
        root.cleanup()


def test_string_annotation_naming_a_category_does_not_select_a_single_provider() -> None:
    """`tool: "tooling"` names no type and no contract: the lone member of category "tooling" is not injected."""
    root = _dynamic_root("annotation-category-string-label")
    try:
        root.bind(spell=Toolbox, existence="unique_per_conduit", spellframe="tooling", binding_name="Toolbox",
                  disposal_method_names=["cleanup"])
        consumer = _consumer_with_unbound_annotation("ToolUser", "tool", "tooling")
        root.bind(spell=consumer, existence="many", spellframe="consumers", binding_name="user",
                  disposal_method_names=["cleanup"])
        with pytest.raises(UnresolvedInputError):
            root.meld(spellframe="consumers", binding_name="user")
        tool = root.meld(spellframe="tooling", binding_name="Toolbox")
        user = root.meld(spellframe="consumers", binding_name="user", override={"tool": tool})
        assert user.tool is tool
    finally:
        root.cleanup()


class Gatherer(Cleanable):
    """Consumer of three collections: a class, a string label and a Protocol."""

    def __init__(self, *, spectra: list[Spectrum], members: list["spectrum"], services: list[IService]) -> None:
        """Hold the three groups."""
        super().__init__()
        self.spectra = spectra
        self.members = members
        self.services = services

    def cleanup(self) -> None:
        """Retire once."""
        if self._cleaned:
            return
        self._cleaned = True
        del self.spectra
        del self.members
        del self.services


def test_collection_annotations_gather_the_group_their_kind_names() -> None:
    """`list[Spectrum]` gathers that class, `list["spectrum"]` the category's members, `list[IService]` the contract's."""
    root = _dynamic_root("annotation-category-collections")
    try:
        root.bind(spell=Spectrum, existence="unique_per_conduit", spellframe="spectrum",
                  binding_name="Spectrum", disposal_method_names=["cleanup"])
        root.bind(spell=Toolbox, existence="unique_per_conduit", spellframe="spectrum",
                  binding_name="Toolbox", disposal_method_names=["cleanup"])
        root.bind(spell=Impl, existence="unique_per_conduit", spellframe=IService,
                  disposal_method_names=["cleanup"])
        root.bind(spell=Gatherer, existence="many", spellframe="consumers", binding_name="gatherer",
                  disposal_method_names=["cleanup"])
        gatherer = root.meld(spellframe="consumers", binding_name="gatherer")
        assert [type(item).__name__ for item in gatherer.spectra] == ["Spectrum"]
        assert sorted(type(item).__name__ for item in gatherer.members) == ["Spectrum", "Toolbox"]
        assert [type(item).__name__ for item in gatherer.services] == ["Impl"]
    finally:
        root.cleanup()
''', nl, "regression guards")
path.write_bytes(text.encode("utf-8"))
print("A. regression module edited")

# ---------------------------------------------------------------------------
# B. test_compiler_phase_3.py: stubs carry the kind; the matcher tests pin the kind rule
# ---------------------------------------------------------------------------
path, text, nl = read("tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_3.py")
text = replace_once(text, '''import inspect
import typing
from types import SimpleNamespace
from typing import Any, Optional, Union
''', '''import inspect
import typing
from types import SimpleNamespace
from typing import Any, Optional, Protocol, Union
''', nl, "p3 imports")
text = replace_once(text, '''from melder.aether.spellbook.spell_types.spell_types import SpellType
''', '''from melder.aether.spellbook.spell_types.spell_types import SpellType
from melder.aether.spellbook.spellframe_kind.spellframe_kind import SpellframeKind
from melder.utilities.helpers.general_helpers import SpellInputUtils
''', nl, "p3 kind imports")
text = replace_once(text, '''    """Build a minimal spell stub for Phase 3 matching and run tests."""
    build_details: list[dict[str, Any]] = []

    def _add_build_details(*, dependencies: list[str]) -> None:
        build_details.append(
            {
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
        resolvable=resolvable,
        spell_index=_SpellIndexStub(spell_id),
        _add_build_details=_add_build_details,
        _build_details_calls=build_details,
    )
''', '''    """
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
''', nl, "p3 stub")

# matrix + the four hand-written matcher tests, replaced as one span
start_anchor = ("@pytest.mark.parametrize(" + nl + '    ("spell_type", "annotation_kind", "binding_name", "candidate_binding_name", "require_class_spell", "expected"),')
end_anchor = ("    assert indexed == scanned" + nl + '    assert set(index) == {"by_key"}' + nl + '    assert sorted(index["by_key"]) == ["other", "service"]' + nl)
start = text.index(start_anchor)
end = text.index(end_anchor, start) + len(end_anchor)
assert text.count(start_anchor) == 1 and text.count(end_anchor) == 1
NEW_TESTS = '''@pytest.mark.parametrize(
    ("spell_type", "annotation_kind", "binding_name", "candidate_binding_name", "require_class_spell", "expected"),
    [
        (SpellType.SPELL, "type", None, None, True, True),
        (SpellType.SPELL, "type", "alpha", "beta", True, False),
        (SpellType.SPELL, "contract", None, None, True, True),
        (SpellType.SPELL, "type_name", None, None, True, True),
        (SpellType.SPELL, "contract_name", None, None, True, True),
        (SpellType.SPELL, "other", None, None, True, False),
        (SpellType.SPELL, "other_name", None, None, True, False),
        (SpellType.METHOD, "type", None, None, True, False),
        (SpellType.METHOD, "type", None, None, False, True),
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
    """A single socket matches a contract-framed spell by its type, by its Protocol, or by either name."""
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
    """A string names the spell's type or its Protocol contract, never a different name."""
    phase = CompilerPhase3()

    class _FrameContract(Protocol):
        pass

    candidate = _make_spell_stub(
        "candidate",
        spell_obj=object(),
        spellframe=_FrameContract,
        spell_name="CandidateSpell",
    )

    assert phase._matches_annotation("CandidateSpell", None, candidate, require_class_spell=True) is True
    assert phase._matches_annotation("_FrameContract", None, candidate, require_class_spell=True) is True
    assert phase._matches_annotation(typing.ForwardRef("_FrameContract"), None, candidate, require_class_spell=True) is True
    assert phase._matches_annotation("Unrelated", None, candidate, require_class_spell=True) is False


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
    """A spell under a string category answers to its own type; the category's name reaches it only as a collection label."""
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
    # single socket: the type, by object or by name - never the category
    assert phase._matches_annotation(Impl, None, candidate, require_class_spell=True) is True
    assert phase._matches_annotation("Impl", None, candidate, require_class_spell=True) is True
    assert phase._matches_annotation(Service, None, candidate, require_class_spell=True) is False
    assert phase._matches_annotation("service", None, candidate, require_class_spell=True) is False
    # collection: the label by name, the type by class - not the category by a class spelled like it
    assert phase._matches_annotation("service", None, candidate, require_class_spell=False, collection=True) is True
    assert phase._matches_annotation(Impl, None, candidate, require_class_spell=False, collection=True) is True
    assert phase._matches_annotation(Service, None, candidate, require_class_spell=False, collection=True) is False
    assert phase._matches_annotation("impl", None, candidate, require_class_spell=False, collection=True) is False


def test_matches_annotation_contract_spell_is_reached_by_type_contract_and_their_names() -> None:
    """A spell under a Protocol answers to its type, to the Protocol (object or name), and as a collection to both groups."""
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
    for annotation in (Impl, "Impl", IService, "IService"):
        assert phase._matches_annotation(annotation, None, candidate, require_class_spell=True) is True, annotation
    assert phase._matches_annotation(Other, None, candidate, require_class_spell=True) is False
    for annotation in (IService, "iservice", Impl):
        assert phase._matches_annotation(annotation, None, candidate, require_class_spell=False, collection=True) is True, annotation
    assert phase._matches_annotation("impl", None, candidate, require_class_spell=False, collection=True) is False


@pytest.mark.parametrize(
    ("annotation_name", "collection", "expected"),
    [
        ("Impl", False, ["Impl"]),
        ("IService", False, ["Impl"]),
        ("Spectrum", False, ["Spectrum"]),
        ("Toolbox", False, ["Toolbox"]),
        ("spectrum_label", False, []),
        ("Spectrum", True, ["Spectrum"]),
        ("spectrum_label", True, ["Spectrum", "Toolbox"]),
        ("IService", True, ["Impl"]),
        ("Impl", True, ["Impl"]),
    ],
)
def test_indexed_candidates_equal_the_scan_for_every_kind(annotation_name: str, collection: bool, expected: list[str]) -> None:
    """The three-bucket index returns exactly what the scan returns, in pool order, for every annotation and socket kind."""
    phase = CompilerPhase3()

    class IService(Protocol):
        pass

    class Impl:
        pass

    class Spectrum:
        pass

    class Toolbox:
        pass

    objects = {"Impl": Impl, "IService": IService, "Spectrum": Spectrum, "Toolbox": Toolbox}
    annotation: Any = objects.get(annotation_name, annotation_name)
    root_spell = _make_spell_stub("root", spell_obj=object(), spellframe=None, spell_name="RootSpell")
    pool = {
        "spectrum": _make_spell_stub("spectrum", spell_obj=Spectrum, spellframe="spectrum_label", spell_name="Spectrum", binding_name="Spectrum"),
        "toolbox": _make_spell_stub("toolbox", spell_obj=Toolbox, spellframe="spectrum_label", spell_name="Toolbox", binding_name="Toolbox"),
        "impl": _make_spell_stub("impl", spell_obj=Impl, spellframe=IService, spell_name="Impl"),
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
    assert sorted(index["by_type"]) == ["impl", "spectrum", "toolbox"]
    assert sorted(index["by_label"]) == ["iservice", "spectrum_label"]
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
'''.replace("\n", nl)
text = text[:start] + NEW_TESTS + text[end:]

# the resolver tests used a concrete class as a frame; they describe a contract, so the frame is a Protocol
for old_class in ("    class _ServiceFrame:" + nl + "        pass",):
    count = text.count(old_class)
    assert count == 6, f"_ServiceFrame definitions: {count}"
    text = text.replace(old_class, "    class _ServiceFrame(Protocol):" + nl + "        pass")
for name in ("_FrameA", "_FrameB", "_RootFrame"):
    old_class = "    class " + name + ":" + nl + "        pass"
    count = text.count(old_class)
    assert count == 1, f"{name} definitions: {count}"
    text = text.replace(old_class, "    class " + name + "(Protocol):" + nl + "        pass")
path.write_bytes(text.encode("utf-8"))
print("B. test_compiler_phase_3 edited")

# ---------------------------------------------------------------------------
# C. test_bind.py: the refusal and the recorded kinds
# ---------------------------------------------------------------------------
path, text, nl = read("tests/unit/melder/spellbook/bind/test_bind.py")
text = replace_once(text, '''def test_nonclass_noncallable_spellframe(monkeypatch):
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(class_profile()))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto, spellframe=123)
    assert spell.kwargs["spellframe"] == 123
''', '''def test_nonclass_noncallable_spellframe_is_refused(monkeypatch):
    """A spellframe that is neither a string nor a Protocol - here an int - is refused before any profile work."""
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(class_profile()))
    b = Bind(StubSpellbook())
    with pytest.raises(TypeError, match="string category or a Protocol contract") as caught:
        b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto, spellframe=123)
    assert "an object of type 'int'" in str(caught.value)


def test_concrete_class_spellframe_is_refused_with_the_remedy(monkeypatch):
    """A concrete class used as a spellframe is refused and the message names the string and Protocol remedies."""
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(class_profile()))
    b = Bind(StubSpellbook())

    class ServiceShape:
        pass

    with pytest.raises(TypeError, match="string category or a Protocol contract") as caught:
        b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto, spellframe=ServiceShape)
    message = str(caught.value)
    assert "the concrete class 'ServiceShape'" in message
    assert "spellframe='ServiceShape'" in message
    assert "typing.Protocol" in message


def test_string_spellframe_is_recorded_as_a_category(monkeypatch):
    """A string frame records SpellframeKind.category and no implemented Protocols."""
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(class_profile()))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto, spellframe="services")
    assert spell.kwargs["spellframe"] == "services"
    assert spell.kwargs["spellframe_kind"] is SpellframeKind.category
    assert spell.kwargs["implemented_protocols"] == ()


def test_protocol_spellframe_is_recorded_as_a_contract(monkeypatch):
    """A Protocol frame records SpellframeKind.contract with the Protocol as the implemented contract."""
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(class_profile()))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto, spellframe=ProtoWithFoo)
    assert spell.kwargs["spellframe"] is ProtoWithFoo
    assert spell.kwargs["spellframe_kind"] is SpellframeKind.contract
    assert spell.kwargs["implemented_protocols"] == (ProtoWithFoo,)


def test_bare_binding_is_recorded_as_kind_none(monkeypatch):
    """No frame records SpellframeKind.none and no implemented Protocols."""
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(class_profile()))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto)
    assert spell.kwargs["spellframe"] is None
    assert spell.kwargs["spellframe_kind"] is SpellframeKind.none
    assert spell.kwargs["implemented_protocols"] == ()


def test_classify_spellframe_table():
    """The classifier's table: None -> none, str -> category, Protocol -> contract, anything else refused."""
    assert Bind._classify_spellframe(None) == (SpellframeKind.none, ())
    assert Bind._classify_spellframe("label") == (SpellframeKind.category, ())
    assert Bind._classify_spellframe(ProtoWithFoo) == (SpellframeKind.contract, (ProtoWithFoo,))
    with pytest.raises(TypeError, match="string category or a Protocol contract"):
        Bind._classify_spellframe(RealClassImplementingProto)
    with pytest.raises(TypeError, match="string category or a Protocol contract"):
        Bind._classify_spellframe(object())
''', nl, "bind refusal tests")
text = replace_once(text, '''from melder.aether.spellbook.existence.existence import Existence
''', '''from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellframe_kind.spellframe_kind import SpellframeKind
''', nl, "bind test import")
path.write_bytes(text.encode("utf-8"))
print("C. test_bind edited")

# ---------------------------------------------------------------------------
# D. crystallizer test doubles carry the kind; crystal tests pin the new fields
# ---------------------------------------------------------------------------
for rel in ("tests/mocks/crystallizer/spell_crystal_harness.py", "tests/unit/melder/crystallizer/test_crystallizer.py"):
    path, text, nl = read(rel)
    text = replace_once(text, '''        self.spellframe = None
        self.existence = SimpleNamespace(name="present")
''', '''        self.spellframe = None
        # Frame kind (record 4.1.0): SpellCrystal reads the enum member's name.
        self.spellframe_kind = SpellframeKind.none
        self.implemented_protocols = ()
        self.existence = SimpleNamespace(name="present")
''', nl, rel + " double")
    # add the enum import after the first `from melder` import of the file
    import re as _re
    m = _re.search(r"^from melder[^\r\n]*", text, _re.M)
    assert m is not None, rel + ": no melder import"
    first_import_line = m.group(0)
    text = text.replace(first_import_line, "from melder.aether.spellbook.spellframe_kind.spellframe_kind import SpellframeKind" + nl + first_import_line, 1)
    path.write_bytes(text.encode("utf-8"))

path, text, nl = read("tests/unit/melder/crystallizer/test_spell_crystal.py")
text = replace_once(text, '''@pytest.fixture(params=SYNTHETIC_CASES, ids=synthetic_case_id)
def synthetic_case_crystal(request):
''', '''def test_spell_crystal_records_the_frame_kind_and_a_contracts_coordinates() -> None:
    """
    The crystal carries `spellframe_kind` and, for a contract, the Protocol's module and qualname (record 4.1.0).

    A bare binding records "none" with no coordinates; a string category records "category" and the label; a
    Protocol frame records "contract" with the coordinates a loader hydrates it from.
    """
    from typing import Protocol

    from melder.aether.spellbook.spellframe_kind.spellframe_kind import SpellframeKind

    class IRepo(Protocol):
        def fetch(self) -> None: ...

    crystallizer = _create_activated_crystallizer()
    bare = DummySpell("bare-spell", type("BareService", (), {"__module__": __name__}))
    category = DummySpell("category-spell", type("CategoryService", (), {"__module__": __name__}))
    category.spellframe = "storage"
    category.spellframe_kind = SpellframeKind.category
    contract = DummySpell("contract-spell", type("ContractService", (), {"__module__": __name__}))
    contract.spellframe = IRepo
    contract.spellframe_kind = SpellframeKind.contract
    contract.implemented_protocols = (IRepo,)
    crystals = []
    try:
        for spell in (bare, category, contract):
            crystals.append(crystallizer.create_spell_crystal(spell))
        bare_crystal, category_crystal, contract_crystal = crystals
        assert bare_crystal.spellframe_kind == "none"
        assert bare_crystal.spellframe_module is None and bare_crystal.spellframe_qualname is None
        assert category_crystal.spellframe_kind == "category"
        assert category_crystal.spellframe_name == "storage"
        assert category_crystal.spellframe_module is None and category_crystal.spellframe_qualname is None
        assert contract_crystal.spellframe_kind == "contract"
        assert contract_crystal.spellframe_name == "IRepo"
        assert contract_crystal.spellframe_module == IRepo.__module__
        assert contract_crystal.spellframe_qualname == IRepo.__qualname__
        payload = contract_crystal.describe()
        assert payload["spellframe_kind"] == "contract"
        assert payload["spellframe_module"] == IRepo.__module__
        assert payload["spellframe_qualname"] == IRepo.__qualname__
    finally:
        for crystal in crystals:
            crystal.cleanup()


@pytest.fixture(params=SYNTHETIC_CASES, ids=synthetic_case_id)
def synthetic_case_crystal(request):
''', nl, "crystal kind test")
path.write_bytes(text.encode("utf-8"))
print("D. crystallizer doubles and crystal test edited")

# ---------------------------------------------------------------------------
# E. the sweep: plain-class frames become Protocols or labels, per file; the two retired idioms convert
# ---------------------------------------------------------------------------
def class_to_protocol(rel: str, class_line: str, *, add_import: bool) -> None:
    path, text, nl = read(rel)
    old = class_line + nl
    new = class_line[:-1] + "(Protocol):" + nl
    count = text.count(old)
    assert count == 1, f"{rel}: {class_line!r} found {count} times"
    text = text.replace(old, new)
    if add_import:
        import re as _re
        m = _re.search(r"^from typing import ([^\r\n]*)", text, _re.M)
        assert m is not None, rel + ": no typing import"
        names = [n.strip() for n in m.group(1).split(",")]
        if "Protocol" not in names:
            names.append("Protocol")
            text = text.replace(m.group(0), "from typing import " + ", ".join(sorted(names)), 1)
    path.write_bytes(text.encode("utf-8"))


# the matcher unit file: a descriptive Protocol definition is a candidate for its own annotation
path, text, nl = read("tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_3.py")
text = replace_once(text, '''    assert sorted(index["by_label"]) == ["other", "service"]
    assert index["by_contract"] == {}
''', '''    assert sorted(index["by_label"]) == ["other", "service"]
    assert index["by_contract"] == {}


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
''', nl, "p3 definition test")
path.write_bytes(text.encode("utf-8"))

# component: contract markers
class_to_protocol("tests/component/melder/spellbook/test_spellbook_component_override_required.py", "class Definition:", add_import=True)
class_to_protocol("tests/component/melder/spellbook/test_spellbook_component_collection_many_instances.py", "class IMember:", add_import=True)
class_to_protocol("tests/component/melder/spellbook/test_spellbook_component_override_key_set_plans.py", "class IMember:", add_import=True)
class_to_protocol("tests/component/melder/spellbook/test_spellbook_component_unresolved_input.py", "class Unregistered:", add_import=True)
class_to_protocol("tests/component/melder/spellbook/test_spellbook_component_signature_release_on_removal.py", "class ISignatureFrame:", add_import=True)
# integration: contract markers for list DI
class_to_protocol("tests/integration/melder/spellbook/test_spellbook_integration_future_annotations.py", "class _FutureFrame:", add_import=False)
class_to_protocol("tests/integration/melder/spellbook/test_spellbook_integration_future_annotations.py", "    class _LocalFrame:", add_import=False)
class_to_protocol("tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract.py", "    class _Frame:", add_import=False)
class_to_protocol("tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract.py", "    class _TypingFrame:", add_import=False)

# component: a grouping key that is only a label becomes the label
path, text, nl = read("tests/component/melder/aether/conduit/test_conduit_component_non_resolvable_admission.py")
text = replace_once(text, '''        spell=RuntimeProvider, spellframe=RuntimeDefinition, binding_name="runtime", existence="unique",
''', '''        spell=RuntimeProvider, spellframe="RuntimeDefinition", binding_name="runtime", existence="unique",
''', nl, "non_resolvable label")
path.write_bytes(text.encode("utf-8"))

path, text, nl = read("tests/integration/melder/spellbook/test_spellbook_integration_public_api.py")
text = replace_once(text, '''                spellframe=BasicConfig,
                binding_name="secondary",
''', '''                spellframe="BasicConfig",
                binding_name="secondary",
''', nl, "public_api label")
path.write_bytes(text.encode("utf-8"))

path, text, nl = read("tests/integration/melder/spellbook/test_spellbook_integration_resolution_break_matrix.py")
text = replace_once(text, '''    """C1 characterization: list[Engine] over a concrete element resolves the bound engine(s)."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create", spellframe=Engine)
''', '''    """C1 characterization: list[Engine] over a concrete element gathers the spells of that class."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
''', nl, "break_matrix bare engine")
path.write_bytes(text.encode("utf-8"))

# component: the eq-risky pool is made by a bound OBJECT now (frames are strings or Protocols)
path, text, nl = read("tests/component/melder/spellbook/test_spellbook_component_structural_snapshot_capture.py")
text = replace_once(text, '''    Contract: One spellframe with a custom __eq__ makes both payloads carry replayable False.
    """
''', '''    Contract: One bound object with a custom __eq__ makes both payloads carry replayable False
        (a spellframe can no longer carry one: it is a string or a Protocol since 2026-10-04).
    """
''', nl, "snapshot doc")
text = replace_once(text, '''    book.bind(spell=Frame, spellframe=Frame(), existence="unique", permissions="create")
''', '''    book.bind(spell=Frame(), existence="unique", permissions="create")
''', nl, "snapshot bind")
path.write_bytes(text.encode("utf-8"))

# component: the existing-instance admission file - the concrete-frame variant becomes the refusal
path, text, nl = read("tests/component/melder/spellbook/test_existing_instance_protocol_admission.py")
text = replace_once(text, '''class GroupingFrame:
    """Act as a concrete grouping key, with no declared Protocol semantics."""
''', '''class GroupingFrame:
    """A concrete class: refused as a spellframe since 2026-10-04 (a frame is a string or a Protocol)."""
''', nl, "admission GroupingFrame doc")
text = replace_once(text, '''@pytest.mark.parametrize("existing", [False, True], ids=["class", "instance"])
@pytest.mark.parametrize("frame", [GroupingFrame, "reader-group"], ids=["concrete", "string"])
def test_non_protocol_frames_keep_grouping_semantics(
        instance_book: Spellbook,
        existing: bool,
        frame: object,
) -> None:
    """Keep non-Protocol frame grouping independent of nominal class inheritance checks."""
    supplied = ValidReader()
    target = supplied if existing else ValidReader
    spell_id = instance_book.bind(spell=target, existence="unique", spellframe=frame)
    root = instance_book.conjure(dynamic=True)
    resolved = root.meld(spell_id=spell_id)
    assert resolved.read() == "supplied-reader"
    if existing:
        assert resolved is supplied
''', '''@pytest.mark.parametrize("existing", [False, True], ids=["class", "instance"])
def test_string_frames_keep_grouping_semantics(
        instance_book: Spellbook,
        existing: bool,
) -> None:
    """A string category groups without any structural check, for class and existing-object targets alike."""
    supplied = ValidReader()
    target = supplied if existing else ValidReader
    spell_id = instance_book.bind(spell=target, existence="unique", spellframe="reader-group")
    root = instance_book.conjure(dynamic=True)
    resolved = root.meld(spell_id=spell_id)
    assert resolved.read() == "supplied-reader"
    if existing:
        assert resolved is supplied


@pytest.mark.parametrize("existing", [False, True], ids=["class", "instance"])
def test_concrete_class_frame_is_refused_for_class_and_instance_targets(
        instance_book: Spellbook,
        existing: bool,
) -> None:
    """A concrete class is neither a category nor a contract: bind refuses it with the two accepted forms."""
    supplied = ValidReader()
    target = supplied if existing else ValidReader
    with pytest.raises(TypeError, match="string category or a Protocol contract"):
        instance_book.bind(spell=target, existence="unique", spellframe=GroupingFrame)
''', nl, "admission concrete test")
path.write_bytes(text.encode("utf-8"))

# component: a function provider of a type is bound under a Protocol contract
path, text, nl = read("tests/component/melder/spellbook/test_conjure_cache_restage.py")
text = replace_once(text, '''from typing import Callable, Iterator, Tuple
''', '''from typing import Callable, Iterator, Protocol, Tuple
''', nl, "restage import")
text = replace_once(text, '''def _function_world(frame: str, cache_fragment: Path, factory: Callable[..., object]) -> Tuple[Spellbook, type]:
    """Bind a function provider (spellframe = its product type) and a class consumer, then conjure."""
    product = factory.__annotations__["return"]

    class Consumer:
        def __init__(self, product: product) -> None:
            self.product = product

    Consumer.__qualname__ = "Consumer"
    book = _new_world_book(frame, cache_fragment)
    book.bind(spell=factory, spellframe=product, existence="unique", permissions="create")
    book.bind(spell=Consumer, existence="many", permissions="create")
    book.conjure(name="root")
    return book, Consumer


class _Product:
    """Product built by the function provider."""
''', '''def _function_world(frame: str, cache_fragment: Path, factory: Callable[..., object]) -> Tuple[Spellbook, type]:
    """
    Bind a function provider under the product's Protocol contract and a class consumer, then conjure.

    A function spell has no type of its own that a consumer annotation could name, so the contract it
    provides is declared as its spellframe (a concrete class is not a valid frame since 2026-10-04).
    """

    class Consumer:
        def __init__(self, product: IProduct) -> None:
            self.product = product

    Consumer.__qualname__ = "Consumer"
    book = _new_world_book(frame, cache_fragment)
    book.bind(spell=factory, spellframe=IProduct, existence="unique", permissions="create")
    book.bind(spell=Consumer, existence="many", permissions="create")
    book.conjure(name="root")
    return book, Consumer


class IProduct(Protocol):
    """The contract a function provider is bound under; consumers ask for it by annotation."""


class _Product:
    """Product built by the function provider."""
''', nl, "restage function world")
path.write_bytes(text.encode("utf-8"))

# integration: existing instances framed under a Protocol contract instead of their own class
path, text, nl = read("tests/integration/melder/spellbook/test_existing_instance_planning.py")
text = replace_once(text, '''from typing import Union
''', '''from typing import Protocol, Union
''', nl, "planning import")
text = replace_once(text, '''class ExistingValue:
    """A deliberately non-callable supplied object, not a constructor request."""
''', '''class IExistingValue(Protocol):
    """The contract an existing value is framed under (a concrete class is not a valid frame since 2026-10-04)."""


class ExistingValue:
    """A deliberately non-callable supplied object, not a constructor request."""
''', nl, "planning protocol")
count = text.count("spellframe=ExistingValue")
assert count == 5, f"planning spellframe=ExistingValue: {count}"
text = replace_once(text, '''    def __init__(self, values: list[ExistingValue]) -> None:
''', '''    def __init__(self, values: list[IExistingValue]) -> None:
''', nl, "planning collection consumer gathers the contract")
text = text.replace("spellframe=ExistingValue", "spellframe=IExistingValue")
path.write_bytes(text.encode("utf-8"))

path, text, nl = read("tests/integration/melder/spellbook/test_existing_instance_additional_regressions.py")
text = replace_once(text, '''from tests.integration.melder.spellbook.test_existing_instance_planning import (
    ExistingValue as SuppliedValue,
)
''', '''from tests.integration.melder.spellbook.test_existing_instance_planning import (
    ExistingValue as SuppliedValue,
)
from tests.integration.melder.spellbook.test_existing_instance_planning import (
    IExistingValue,
)
''', nl, "regressions import")
count = text.count("spellframe=SuppliedValue")
assert count == 8, f"regressions spellframe=SuppliedValue: {count}"
text = text.replace("spellframe=SuppliedValue", "spellframe=IExistingValue")
path.write_bytes(text.encode("utf-8"))

# integration: the cache schema pin
path, text, nl = read("tests/integration/melder/spellbook/test_cache_schema_version_integration.py")
text = replace_once(text, '''    19: "executor_world_stamp",
}
''', '''    19: "executor_world_stamp",
    20: "annotation_kind_matching",
}
''', nl, "cache schema pin")
path.write_bytes(text.encode("utf-8"))

# integration: the retired string-literal category annotation becomes its explicit form
path, text, nl = read("tests/integration/melder/spellbook/test_spellbook_integration_future_annotations_more.py")
start_anchor = "def test_future_annotations_string_literal_frame_annotation_resolves_single() -> None:" + nl
end_anchor = "        assert instance.repo.marker == \"primary\"" + nl + "    finally:" + nl + "        conduit.cleanup()" + nl
start = text.index(start_anchor)
end = text.index(end_anchor, start) + len(end_anchor)
assert text.count(start_anchor) == 1
NEW_EXTRA_FRAME = '''def test_future_annotations_string_literal_category_annotation_is_an_unresolved_input() -> None:
    """
    Purpose:
        A string-literal annotation naming a string CATEGORY selects no single provider (2026-10-04): a
        category is a label, not a type or a contract. The explicit form - a SpellMap default addressing
        the category - resolves it.
    Contract:
        - `repo: "extra_frame"` compiles as an unresolved input; melding without an override raises
          UnresolvedInputError.
        - `repo: _FramePrimaryRepo = SpellMap(spellframe="extra_frame")` resolves the bound member.
    Returns:
        None.
    Raises:
        AssertionError: If either half of the contract fails.
    """
    from melder.aether.conduit.meld.contracts.spell_map import SpellMap
    from melder.utilities.custom_exceptions.unresolved_input_error import UnresolvedInputError

    class _StringFrameService:
        """
        Purpose:
            Name a string category in a single annotation (retired idiom).
        Contract:
            Stores whatever the meld supplies.
        """
        def __init__(self, repo: "extra_frame") -> None:
            """
            Purpose:
                Capture the supplied repository.
            Args:
                repo: Supplied repository instance.
            Returns:
                None.
            """
            self.repo = repo

    class _MappedFrameService:
        """
        Purpose:
            Address the category explicitly through a SpellMap default.
        Contract:
            Stores the injected repository instance.
        """
        def __init__(self, repo: _FramePrimaryRepo = SpellMap(spellframe="extra_frame")) -> None:
            """
            Purpose:
                Capture the injected repository.
            Args:
                repo: Injected repository instance.
            Returns:
                None.
            """
            self.repo = repo

    spellbook = _make_spellbook()
    spellbook.bind(
        spell=_FramePrimaryRepo,
        existence=Existence.unique,
        permissions="create",
        spellframe="extra_frame",
    )
    unresolved_id = spellbook.bind(
        spell=_StringFrameService,
        existence=Existence.many,
        permissions="create",
    )
    mapped_id = spellbook.bind(
        spell=_MappedFrameService,
        existence=Existence.many,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        with pytest.raises(UnresolvedInputError):
            conduit.meld(spell_id=unresolved_id)
        instance = conduit.meld(spell_id=mapped_id)
        assert isinstance(instance.repo, _FramePrimaryRepo)
        assert instance.repo.marker == "primary"
    finally:
        conduit.cleanup()
'''.replace("\n", nl)
text = text[:start] + NEW_EXTRA_FRAME + text[end:]
path.write_bytes(text.encode("utf-8"))

# integration: the rebind M2 guard swaps an implementation under a Protocol contract
path, text, nl = read("tests/integration/melder/aether/conduit/test_rebind_after_first_meld_integration.py")
text = replace_once(text, '''from collections.abc import Iterator

import pytest
''', '''from collections.abc import Iterator
from typing import Protocol

import pytest
''', nl, "rebind import")
text = replace_once(text, '''class Consumer(Cleanable):
    """Depends on the provider address by annotation."""
''', '''class IProvider(Protocol):
    """The contract both provider classes are bound under when one replaces the other (M2)."""

    generation: int


class ContractConsumer(Cleanable):
    """Depends on the provider CONTRACT by annotation, so a replacement implementation satisfies it."""

    def __init__(self, p: IProvider) -> None:
        """Hold the injected provider."""
        super().__init__()
        self.p = p

    def cleanup(self) -> None:
        """Retire once."""
        if self._cleaned:
            return
        self._cleaned = True
        del self.p


class Consumer(Cleanable):
    """Depends on the provider class by annotation."""
''', nl, "rebind contract consumer")
text = replace_once(text, '''def test_dependent_consumer_is_rebuilt_against_the_replacement_class() -> None:
    """GUARD (green before the repair): a consumer compiled against the first provider rebuilds its plan."""
    frame = "rebind-matrix-m2"
    book, root, peer, scope = _world(frame)
    try:
        provider_id = root.bind(spell=Provider, existence="many", spellframe="provider",
                                disposal_method_names=["cleanup"])
        root.bind(spell=Consumer, existence="many", spellframe="consumers",
                  binding_name="consumer", disposal_method_names=["cleanup"])
        first = scope.meld(spellframe="consumers", binding_name="consumer")
        assert first.p.generation == 1
        definition = root.get_spell_by_id(provider_id, frame)
        root.cleanup_spell(spell=definition)
        root.bind(spell=ProviderV2, existence="many", spellframe="provider",
                  disposal_method_names=["cleanup"])
        second = scope.meld(spellframe="consumers", binding_name="consumer")
''', '''def test_dependent_consumer_is_rebuilt_against_the_replacement_class() -> None:
    """
    GUARD (green before the repair): a consumer compiled against the first provider rebuilds its plan.

    The consumer asks for the Protocol contract both providers are bound under (2026-10-04: a class
    annotation names one type, so swapping implementations is a contract's job).
    """
    frame = "rebind-matrix-m2"
    book, root, peer, scope = _world(frame)
    try:
        provider_id = root.bind(spell=Provider, existence="many", spellframe=IProvider,
                                disposal_method_names=["cleanup"])
        root.bind(spell=ContractConsumer, existence="many", spellframe="consumers",
                  binding_name="consumer", disposal_method_names=["cleanup"])
        first = scope.meld(spellframe="consumers", binding_name="consumer")
        assert first.p.generation == 1
        definition = root.get_spell_by_id(provider_id, frame)
        root.cleanup_spell(spell=definition)
        root.bind(spell=ProviderV2, existence="many", spellframe=IProvider,
                  disposal_method_names=["cleanup"])
        second = scope.meld(spellframe="consumers", binding_name="consumer")
''', nl, "rebind M2")
path.write_bytes(text.encode("utf-8"))

# component: the notch-from-definition case notches an implementer in (a Protocol cannot be a concrete spell)
path, text, nl = read("tests/component/melder/spellbook/test_spellbook_component_override_required.py")
text = replace_once(text, '''    """Switching the selected capability must rebuild a consumer that had only a descriptive reference."""
    compiler_book._aetheric_frame_configuration.with_system_caching_enabled(False)
    definition_id = compiler_book.bind(spell=Definition, existence="unique", resolvable=False)
    consumer_id = compiler_book.bind(spell=consumer_type, existence="many")
    index = _selected(compiler_book, definition_id).spell_index
    conduit = compiler_book.conjure(dynamic=True, name="notch-required-input")
    provider_id = conduit.bind_inactive(spell=Definition, spell_index=index, existence="unique")
    provider = compiler_book._inactive_spells[provider_id]
    conduit.notch_spell(spell_index=index, spell=provider)
    result = conduit.meld(spell=consumer_type)
    assert isinstance(result.value, Definition)
''', '''    """
    Switching the selected capability must rebuild a consumer that had only a descriptive reference.

    The descriptive version is the Protocol itself (bound resolvable=False); the notched-in version is a
    concrete implementer bound under the Protocol contract (2026-10-04: a Protocol cannot be bound as a
    concrete spell, so the resolvable version at the same address is an implementer, not the Protocol).
    """
    compiler_book._aetheric_frame_configuration.with_system_caching_enabled(False)
    definition_id = compiler_book.bind(spell=Definition, existence="unique", resolvable=False)
    consumer_id = compiler_book.bind(spell=consumer_type, existence="many")
    index = _selected(compiler_book, definition_id).spell_index
    conduit = compiler_book.conjure(dynamic=True, name="notch-required-input")
    provider_id = conduit.bind_inactive(
        spell=Implementation, spell_index=index, spellframe=Definition, existence="unique",
    )
    provider = compiler_book._inactive_spells[provider_id]
    conduit.notch_spell(spell_index=index, spell=provider)
    result = conduit.meld(spell=consumer_type)
    assert isinstance(result.value, Implementation)
''', nl, "override_required notch case")
path.write_bytes(text.encode("utf-8"))

# integration: the public-lookup case binds bare for the object lookup (an address names the binding)
path, text, nl = read("tests/integration/melder/spellbook/test_existing_instance_additional_regressions.py")
text = replace_once(text, '''    """Keep actual object/frame lookup covered independently of the machine-ID controls."""
    supplied = SuppliedValue("lookup-input")
    instance_book.bind(spell=supplied, existence="unique", spellframe=IExistingValue)
    root = instance_book.conjure(dynamic=True)
    found = root.meld(spell=supplied) if lookup == "instance" else root.meld(spellframe=IExistingValue)
''', '''    """
    Keep actual object/frame lookup covered independently of the machine-ID controls.

    A lookup addresses the binding: `meld(spell=obj)` finds an object bound bare (at its class's address),
    `meld(spellframe=IExistingValue)` one bound under that contract.
    """
    supplied = SuppliedValue("lookup-input")
    instance_book.bind(spell=supplied, existence="unique", spellframe=None if lookup == "instance" else IExistingValue)
    root = instance_book.conjure(dynamic=True)
    found = root.meld(spell=supplied) if lookup == "instance" else root.meld(spellframe=IExistingValue)
''', nl, "regressions lookup case")
path.write_bytes(text.encode("utf-8"))

# experimentation: existing-instance experiments frame under the contract, not the class
path, text, nl = read("tests/experimentation/test_existing_instance_gap_experiment.py")
text = replace_once(text, '''from tests.integration.melder.spellbook.test_existing_instance_planning import (
    ExistingValue as SuppliedValue,
)
''', '''from tests.integration.melder.spellbook.test_existing_instance_planning import (
    ExistingValue as SuppliedValue,
)
from tests.integration.melder.spellbook.test_existing_instance_planning import (
    IExistingValue,
)
''', nl, "gap import")
count = text.count("spellframe=SuppliedValue")
assert count == 6, f"gap spellframe=SuppliedValue: {count}"
text = text.replace("spellframe=SuppliedValue", "spellframe=IExistingValue")
count = text.count("else SuppliedValue")
assert count == 2, f"gap else SuppliedValue: {count}"
text = text.replace("else SuppliedValue", "else IExistingValue")
path.write_bytes(text.encode("utf-8"))

path, text, nl = read("tests/experimentation/test_existing_instance_injection_experiment.py")
text = replace_once(text, '''from tests.integration.melder.spellbook.test_existing_instance_planning import (
    CollectionValueConsumer,
    ExistingValue,
''', '''from tests.integration.melder.spellbook.test_existing_instance_planning import (
    CollectionValueConsumer,
    ExistingValue,
    IExistingValue,
''', nl, "injection import")
text = replace_once(text, '''        spellframe="named-values" if named else ExistingValue if typed else None,
''', '''        spellframe="named-values" if named else IExistingValue if typed else None,
''', nl, "injection typed frame")
path.write_bytes(text.encode("utf-8"))

class_to_protocol("tests/experimentation/test_meld_instance_reference_discovery_experiment.py", "class ReferenceFrame:", add_import=True)
# mixed line endings in this file: anchor on the class line without its terminator
path, text, nl = read("tests/experimentation/test_meld_human_spell_name_string_experiment.py")
assert text.count("class ServiceFrame:") == 1
text = text.replace("class ServiceFrame:", "class ServiceFrame(Protocol):")
import re as _re
m = _re.search(r"^from typing import ([^\r\n]*)", text, _re.M)
names = [n.strip() for n in m.group(1).split(",")]
if "Protocol" not in names:
    names.append("Protocol")
    text = text.replace(m.group(0), "from typing import " + ", ".join(sorted(names)), 1)
path.write_bytes(text.encode("utf-8"))

# the (uncollected) shape probe: the existing object is grouped under the label, not its class
path, text, nl = read("tests/experimentation/commandops_shape_probe.py")
count = text.count("spellframe=Config")
assert count == 2, f"probe spellframe=Config: {count}"
text = text.replace("spellframe=Config", 'spellframe="Config"')
text = text.replace("Existing object bound as an instance under `spellframe=Config`.", 'Existing object bound as an instance under the label "Config".')
path.write_bytes(text.encode("utf-8"))
print("E. sweep applied")
