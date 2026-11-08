"""Integration regressions: annotations match by kind; a spellframe is a category or a Protocol contract.

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

Narrowed 2026-11-07 (EPIC-2026-11-07-spellframe_hides_the_concrete_class, the owner's Autofac reading): a class
lookup - a class annotation, a string naming a class, `list[Class]`, `SpellMap(Class)` - reaches a spell only when it
is bound bare, with no spellframe and the default binding, existing objects alike; a spellframe or a binding name
hides the class, and the spell is reached through its frame (`list["label"]`, a Protocol annotation,
`SpellMap(spellframe=..., binding_name=...)`, `meld(spellframe=..., binding_name=...)`). So the collision guards bind
the real Spectrum bare, where a class lookup still finds it, and the cases built on the reported shape - a Spectrum,
a manager, a config or a ScanProfile filed under a category - pinned that the class consumer stayed unresolved (an
override supplied it), that two framed spells of one class are no ambiguity, and that the frame reaches each of them.

Refused 2026-11-07 (patch hidden_provider_2026_11_07, TASK-2026-11-07-spellframe_ambiguity_validation_check part (a),
0.2.8281): a class lookup whose class is bound only under a spellframe or a binding name is a HIDDEN_PROVIDER error
naming each address and the SpellMap that reaches it - at conjure, or at the consumer's late bind in a dynamic world,
where the consumer stays registered and every meld of it raises the same report, an override as well (D2). The cases
built on the reported shape now pin those refusals as whole texts; the frame still reaches each member.
"""

import sys
import types
from collections.abc import Iterator
from typing import Any, Callable, Protocol, Type

import pytest

from melder import Aether, Cleanable, Conduit, Spellbook, SpellMap
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError
from melder.utilities.custom_exceptions.unresolved_input_error import UnresolvedInputError
from tests._spell_identity_test_support import version_of


@pytest.fixture(autouse=True)
def reset_melder() -> Iterator[None]:
    """Fresh cold Aether before and after every case, exactly as Melder's integration fixtures do."""
    Aether._reset_singleton_for_tests()
    world = Aether()
    Spellbook._aether = world
    Conduit._aether = world
    try:
        yield
    finally:
        Aether._reset_singleton_for_tests()
        world = Aether()
        Spellbook._aether = world
        Conduit._aether = world


class Spectrum(Cleanable):
    """
    The host object a consumer annotates; bound as a unique at ("spectrum", "Spectrum") - the reported shape, which
    hides it from class lookups since 2026-11-07 - or bare, where a class lookup finds it.
    """

    def __init__(self) -> None:
        """No collaborators."""
        super().__init__()

    def cleanup(self) -> None:
        """Retire once."""
        if self._cleaned:
            return
        self._cleaned = True


class Toolbox(Cleanable):
    """An unrelated framework service that may share the host's category."""

    def __init__(self) -> None:
        """No collaborators."""
        super().__init__()

    def cleanup(self) -> None:
        """Retire once."""
        if self._cleaned:
            return
        self._cleaned = True


class CenterWithClass(Cleanable):
    """Consumer annotated with the class object."""

    def __init__(self, *, spectrum: Spectrum) -> None:
        """Hold the borrowed host."""
        super().__init__()
        self.spectrum = spectrum

    def cleanup(self) -> None:
        """Retire once."""
        if self._cleaned:
            return
        self._cleaned = True
        del self.spectrum


class CenterWithString(Cleanable):
    """Consumer annotated with the type's name as a quoted string that resolves in this module."""

    def __init__(self, *, spectrum: "Spectrum") -> None:
        """Hold the borrowed host."""
        super().__init__()
        self.spectrum = spectrum

    def cleanup(self) -> None:
        """Retire once."""
        if self._cleaned:
            return
        self._cleaned = True
        del self.spectrum


class CenterWithSpellMap(Cleanable):
    """
    Consumer that asks for the host by its address - the frame-addressed SpellMap through which a class filed under a
    category is injected since 2026-11-07, when the class annotation no longer reaches it.
    """

    def __init__(self, *, spectrum: Spectrum = SpellMap(spellframe="spectrum", binding_name="Spectrum")) -> None:
        """Hold the host found at ("spectrum", "Spectrum")."""
        super().__init__()
        self.spectrum = spectrum

    def cleanup(self) -> None:
        """Retire once."""
        if self._cleaned:
            return
        self._cleaned = True
        del self.spectrum


def _center_with_unbound_string_annotation() -> Type[Any]:
    """Build a consumer whose `spectrum: "Spectrum"` annotation names a type that is unbound at runtime.

    This is the `TYPE_CHECKING`-only shape: the class lives in a module of its own that never imports
    `Spectrum`, so the annotation stays the string "Spectrum" when Melder reads it, and Phase 3 sees the
    name, not the class object.
    """
    module_name = "melder_tests_unbound_spectrum_consumer"
    module = types.ModuleType(module_name)
    module.__dict__["Cleanable"] = Cleanable
    source = (
        "class CenterUnbound(Cleanable):\n"
        "    def __init__(self, *, spectrum: 'Spectrum') -> None:\n"
        "        super().__init__()\n"
        "        self.spectrum = spectrum\n"
        "    def cleanup(self) -> None:\n"
        "        if self._cleaned:\n"
        "            return\n"
        "        self._cleaned = True\n"
        "        del self.spectrum\n"
    )
    exec(source, module.__dict__)
    sys.modules[module_name] = module
    return module.__dict__["CenterUnbound"]


class IService(Protocol):
    """A Protocol used as a spellframe: a category label AND the contract its members are checked against."""


class ServiceShape:
    """A concrete class: not a valid spellframe since 2026-10-04 (neither a string nor a Protocol)."""


class Impl(Cleanable):
    """Implementation bound under the IService frame."""

    def __init__(self) -> None:
        """No collaborators."""
        super().__init__()

    def cleanup(self) -> None:
        """Retire once."""
        if self._cleaned:
            return
        self._cleaned = True


class Client(Cleanable):
    """Consumer annotated with the Protocol contract."""

    def __init__(self, *, svc: IService) -> None:
        """Hold the implementation."""
        super().__init__()
        self.svc = svc

    def cleanup(self) -> None:
        """Retire once."""
        if self._cleaned:
            return
        self._cleaned = True
        del self.svc


def _dynamic_root(frame: str) -> Conduit:
    """Conjure one dynamic root with caching off on a fresh frame."""
    book = Spellbook(aetheric_frame=frame)
    book.configure_aether_frame(system_state="dynamic", system_caching_enabled=False,
                                disposal=None, disposal_method_names=None)
    book.get_configuration().freeze()
    return book.conjure(dynamic=True, name="host")


def _refusal(action: Callable[[], Any]) -> str:
    """
    Run a bind, meld or conjure that must be refused and return what it raised.

    Args:
        action: The call to run.

    Returns:
        str: The SpellbookValidationError's message; otherwise "<Type>: <message>" for the RuntimeError or TypeError
        raised instead, or "no refusal" when the call returned - so a failed assertion shows what happened.
    """
    try:
        action()
    except SpellbookValidationError as error:
        return str(error)
    except (RuntimeError, TypeError) as error:
        return f"{type(error).__name__}: {error}"
    return "no refusal"


def _filed_at(name: str, spellframe: str, binding_name: str) -> str:
    """
    What follows "<Class> is bound only " in HIDDEN_PROVIDER for one class filed under a category with a binding name.

    Args:
        name: The class's spell name.
        spellframe: The category it is filed under.
        binding_name: Its binding name there.

    Returns:
        str: The where-words, the address with the SpellMap that reaches it, and the ways out.
    """
    return (
        f"under a spellframe: {name} at (spellframe={spellframe!r}, binding_name={binding_name!r}) - use "
        f"SpellMap(spellframe={spellframe!r}, binding_name={binding_name!r}). Ask for it where it is bound - the "
        f"SpellMap shown, as the parameter's default - or bind {name} bare."
    )


def _hidden_provider_line(consumer: str, param: str, expected: str, bound_at: str) -> str:
    """
    One HIDDEN_PROVIDER line of a SpellbookValidationError report.

    Args:
        consumer: The refused spell's name.
        param: The parameter whose class lookup is refused.
        expected: The expected type as the report renders it.
        bound_at: What follows "<expected> is bound only ".

    Returns:
        str: "  - <message> [HIDDEN_PROVIDER]".
    """
    return (
        f"  - Parameter {param!r} on spell {consumer!r} expects {expected}, but a class lookup reaches {expected} only "
        f"where it is bound bare (no spellframe, the default binding), and {expected} is bound only {bound_at} "
        "[HIDDEN_PROVIDER]"
    )


def _report(consumer: str, label: str, *lines: str) -> str:
    """The whole report refusing one spell: the header, its block label and its error lines."""
    return "\n".join([f"Spellbook validation failed. Broken spells: {consumer}.", f"{label}:", *lines])


def _consumer_with_unbound_annotation(class_name: str, param_name: str, annotation_text: str) -> Type[Any]:
    """
    Build a consumer class in its own module whose one parameter carries an UNBOUND string annotation.

    The module never imports the named type, so when Phase 3 reads the annotation (Python 3.14 evaluates
    annotations lazily) it gets the string itself - the shape a `TYPE_CHECKING`-only import leaves at runtime.
    """
    source = (
        "from melder import Cleanable\n"
        "class {cls}(Cleanable):\n"
        "    def __init__(self, *, {param}: '{annotation}') -> None:\n"
        "        super().__init__()\n"
        "        self.{param} = {param}\n"
        "    def cleanup(self) -> None:\n"
        "        if self._cleaned:\n"
        "            return\n"
        "        self._cleaned = True\n"
        "        del self.{param}\n"
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
)
def test_spectrum_annotation_selects_the_spectrum_provider(annotation: str, shared_category: bool) -> None:
    """
    The reported four-case matrix, with the real provider bound bare: Spectrum resolves whether or not Toolbox shares
    the "spectrum" category.

    Since 2026-11-07 a class lookup reaches Spectrum only when it is bound bare - no spellframe, the default binding -
    and its address frame is then "spectrum", the category's own name. The guard of the 2026-10-03 report (a category
    named like the type made every member a candidate: an ambiguity beside the real provider) therefore binds the
    real provider bare; the reported shape itself, Spectrum filed at ("spectrum", "Spectrum"), is pinned by
    `test_class_consumer_of_a_spectrum_filed_under_a_category_is_refused_naming_its_address`.
    """
    root = _dynamic_root("annotation-category-matrix")
    try:
        # bare: filed at ("spectrum", "Spectrum") it is hidden from the class lookup (2026-11-07)
        root.bind(spell=Spectrum, existence="unique_per_conduit", disposal_method_names=["cleanup"])
        root.bind(spell=Toolbox, existence="unique_per_conduit",
                  spellframe="spectrum" if shared_category else "tooling",
                  binding_name="Toolbox", disposal_method_names=["cleanup"])
        consumer = CenterWithClass if annotation == "class" else CenterWithString
        root.bind(spell=consumer, existence="many", spellframe="command_center",
                  binding_name="center", disposal_method_names=["cleanup"])
        center = root.meld(spellframe="command_center", binding_name="center")
        assert isinstance(center.spectrum, Spectrum)
    finally:
        root.cleanup()


def test_type_checking_only_string_annotation_selects_the_spectrum_provider() -> None:
    """
    A string annotation whose name is unbound at runtime resolves exactly as the class object does: Spectrum, bound
    bare, beside a Toolbox in the "spectrum" category.

    Bare since 2026-11-07, the one address a class lookup - the string's type part as much as the class object -
    reaches; filed under the category, Spectrum refuses the unbound string exactly as it refuses the class object
    (`test_class_consumer_of_a_spectrum_filed_under_a_category_is_refused_naming_its_address`).
    """
    root = _dynamic_root("annotation-category-unbound-string")
    try:
        root.bind(spell=Spectrum, existence="unique_per_conduit", disposal_method_names=["cleanup"])
        root.bind(spell=Toolbox, existence="unique_per_conduit", spellframe="spectrum",
                  binding_name="Toolbox", disposal_method_names=["cleanup"])
        root.bind(spell=_center_with_unbound_string_annotation(), existence="many",
                  spellframe="command_center", binding_name="center", disposal_method_names=["cleanup"])
        center = root.meld(spellframe="command_center", binding_name="center")
        assert isinstance(center.spectrum, Spectrum)
    finally:
        root.cleanup()


@pytest.mark.parametrize("annotation", ["class", "string", "unbound_string"])
@pytest.mark.parametrize(
    "shared_category",
    [
        False,
        True,
    ],
)
def test_class_consumer_of_a_spectrum_filed_under_a_category_is_refused_naming_its_address(
        annotation: str, shared_category: bool) -> None:
    """
    The reported shape under the class-lookup rule: Spectrum filed at ("spectrum", "Spectrum"), Toolbox in that
    category or in "tooling".

    Contract (patch hidden_provider_2026_11_07; from 2026-11-07 until then the socket was an unresolved input an
    override supplied):
        - `spectrum: Spectrum` - the class object, its name as a string, or a string unbound at runtime - is refused at
          the consumer's late bind with HIDDEN_PROVIDER, naming Spectrum's address and the SpellMap that reaches it;
          Toolbox, a member of a category spelled like the type, is no candidate. The consumer stays registered, and
          every meld of it raises the same report, with the host supplied by override as well (D2).
        - Spectrum is reached through its address: `meld(spellframe="spectrum", binding_name="Spectrum")` builds it,
          and a frame-addressed `SpellMap` (`CenterWithSpellMap`) injects that same unique.
    """
    root = _dynamic_root("annotation-category-reported-shape")
    try:
        root.bind(spell=Spectrum, existence="unique_per_conduit", spellframe="spectrum",
                  binding_name="Spectrum", disposal_method_names=["cleanup"])
        root.bind(spell=Toolbox, existence="unique_per_conduit",
                  spellframe="spectrum" if shared_category else "tooling",
                  binding_name="Toolbox", disposal_method_names=["cleanup"])
        if annotation == "class":
            consumer = CenterWithClass
        elif annotation == "string":
            consumer = CenterWithString
        else:
            consumer = _center_with_unbound_string_annotation()
        name = consumer.__name__
        expected = _report(name, f"{name} (frame 'command_center')", _hidden_provider_line(
            name, "spectrum", "Spectrum", _filed_at("Spectrum", "spectrum", "Spectrum")))
        refused = _refusal(lambda: root.bind(spell=consumer, existence="many", spellframe="command_center",
                                             binding_name="center", disposal_method_names=["cleanup"]))
        assert refused == expected, f"{name}'s late bind is not refused as HIDDEN_PROVIDER naming Spectrum's address"
        assert _refusal(lambda: root.meld(spellframe="command_center", binding_name="center")) == expected
        host = root.meld(spellframe="spectrum", binding_name="Spectrum")
        assert isinstance(host, Spectrum)
        overridden = _refusal(lambda: root.meld(spellframe="command_center", binding_name="center",
                                                override={"spectrum": host}))
        assert overridden == expected, f"an override let the refused {name} meld"
        root.bind(spell=CenterWithSpellMap, existence="many", spellframe="command_center",
                  binding_name="by_address", disposal_method_names=["cleanup"])
        assert root.meld(spellframe="command_center", binding_name="by_address").spectrum is host
    finally:
        root.cleanup()


def test_lone_category_member_is_not_injected_for_a_type_annotation() -> None:
    """With no Spectrum bound, a Toolbox in category "spectrum" is NOT handed to `spectrum: Spectrum`.

    The parameter is an unresolved input: the meld refuses without an override and takes the supplied
    object with one. Until 2026-10-04 the Toolbox was injected silently; since 2026-11-07 a class lookup
    reaches only a spell bound bare, so a category member is never a candidate for a type annotation.
    """
    root = _dynamic_root("annotation-category-lone-member")
    try:
        root.bind(spell=Toolbox, existence="unique_per_conduit", spellframe="spectrum",
                  binding_name="Toolbox", disposal_method_names=["cleanup"])
        root.bind(spell=CenterWithClass, existence="many", spellframe="command_center",
                  binding_name="center", disposal_method_names=["cleanup"])
        with pytest.raises(UnresolvedInputError):
            root.meld(spellframe="command_center", binding_name="center")
        host = Spectrum()
        center = root.meld(spellframe="command_center", binding_name="center", override={"spectrum": host})
        assert center.spectrum is host
    finally:
        root.cleanup()


def test_guard_protocol_frame_is_a_contract_that_resolves_its_annotation() -> None:
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
    """
    `list[Spectrum]` gathers that class bound bare, `list["spectrum"]` the category's members, `list[IService]` the
    contract's.

    Spectrum is filed under the category here, so since 2026-11-07 the class list gathers nothing - the category hides
    Spectrum from a class lookup, a collection as much as a single socket - and Spectrum is gathered through its
    category instead, beside Toolbox; neither list takes the other's group.
    """
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
        assert [type(item).__name__ for item in gatherer.spectra] == []
        assert sorted(type(item).__name__ for item in gatherer.members) == ["Spectrum", "Toolbox"]
        assert [type(item).__name__ for item in gatherer.services] == ["Impl"]
    finally:
        root.cleanup()


def test_two_framed_versions_of_the_annotated_class_refuse_the_class_consumer_naming_both_addresses() -> None:
    """
    Two spells of the annotated TYPE at distinct framed addresses - the second a version of Spectrum (its name, other
    code), since one class is one spell - are no ambiguity for `spectrum: Spectrum`: each spellframe hides its Spectrum
    from the class lookup, so neither is a candidate.

    From 2026-10-04 to 2026-11-07 the pair was a real ambiguity, refused through the readable validation report
    (AMBIGUOUS_PROVIDER) at the late bind in a dynamic world; from 2026-11-07 the consumer's socket was an unresolved
    input an override supplied. Since patch hidden_provider_2026_11_07 the late bind is refused again, with
    HIDDEN_PROVIDER naming both addresses - ordered by spellframe - and the SpellMap of the one it needs; every meld of
    the consumer raises that report, an override as well (D2), and each version is still reached through its own
    address. Two providers that both answer a class lookup would both be bound bare, at one address, which bind refuses
    (one active spell per signature per frame; TASK-2026-11-07-spellframe_ambiguity_validation_check part (b) checks
    the other paths); the AMBIGUOUS report itself stays pinned for a Protocol frame with two implementations
    (test_spellbook_integration_resolution_contract.py::test_type_hint_di_ambiguous_frame_raises).
    """
    root = _dynamic_root("annotation-category-type-ambiguity")
    try:
        mirror = version_of(Spectrum, mirror=True)
        root.bind(spell=Spectrum, existence="unique_per_conduit", spellframe="spectrum",
                  binding_name="primary", disposal_method_names=["cleanup"])
        root.bind(spell=mirror, existence="unique_per_conduit", spellframe="mirror",
                  binding_name="secondary", disposal_method_names=["cleanup"])
        expected = _report("CenterWithClass", "CenterWithClass (frame 'command_center')", _hidden_provider_line(
            "CenterWithClass", "spectrum", "Spectrum",
            "under a spellframe: Spectrum at (spellframe='mirror', binding_name='secondary') - use "
            "SpellMap(spellframe='mirror', binding_name='secondary'); Spectrum at (spellframe='spectrum', "
            "binding_name='primary') - use SpellMap(spellframe='spectrum', binding_name='primary'). Ask for it where "
            "it is bound - the SpellMap of the one it needs, as the parameter's default - or bind Spectrum bare."))
        refused = _refusal(lambda: root.bind(spell=CenterWithClass, existence="many", spellframe="command_center",
                                             binding_name="center", disposal_method_names=["cleanup"]))
        assert refused == expected, "the late bind is not refused naming both framed Spectrum versions"
        primary = root.meld(spellframe="spectrum", binding_name="primary")
        secondary = root.meld(spellframe="mirror", binding_name="secondary")
        assert type(primary) is Spectrum
        assert type(secondary) is mirror
        overridden = _refusal(lambda: root.meld(spellframe="command_center", binding_name="center",
                                                override={"spectrum": secondary}))
        assert overridden == expected, "an override let the refused CenterWithClass meld"
    finally:
        root.cleanup()


class ScanProfileFromAgents:
    """One of two unrelated classes a host happens to name alike (the MelderOps MCPScanner shape)."""

    def __init__(self) -> None:
        """No collaborators."""


class ScanProfileFromTools:
    """The other same-named class, bound in another category."""

    def __init__(self) -> None:
        """No collaborators."""


ScanProfileFromAgents.__name__ = ScanProfileFromTools.__name__ = "ScanProfile"


class MCPScanner:
    """Consumer typed with one of the two same-named classes."""

    def __init__(self, profile: ScanProfileFromTools) -> None:
        """Hold the profile."""
        self.profile = profile


class MCPScannerByAddress:
    """
    MCPScanner migrated as D2 directs (patch hidden_provider_2026_11_07): the profile is asked for at its address, with
    a frame-addressed SpellMap default, instead of being supplied by override.
    """

    def __init__(self, profile: ScanProfileFromTools = SpellMap(spellframe="artificial_intelligence_tools",
                                                              binding_name="ScanProfile")) -> None:
        """Hold the profile found at ("artificial_intelligence_tools", "ScanProfile")."""
        self.profile = profile


def test_two_same_named_classes_in_two_categories_refuse_the_class_consumer_at_conjure_naming_both() -> None:
    """
    The MelderOps composition: Agents' ScanProfile under "agents" and Utilities' ScanProfile under
    "artificial_intelligence_tools", and `MCPScanner.profile: ScanProfile`. A class annotation keys by the class NAME
    (so a TYPE_CHECKING string and the class object agree), so the two are one type key; until 2026-11-07 conjure
    refused MCPScanner through the readable report (AMBIGUOUS_PROVIDER), and from 2026-11-07 it conjured with an
    unresolved input that an override supplied.

    Since patch hidden_provider_2026_11_07 (TASK-2026-11-07-spellframe_ambiguity_validation_check part (a)) conjure
    refuses MCPScanner again, with HIDDEN_PROVIDER naming both addresses and the SpellMap of the one it needs. The
    expected type renders by qualname, as UNRESOLVED_INPUT always named it: ScanProfileFromTools here, where the
    stand-ins rename only `__name__`; the MelderOps classes are named ScanProfile in both modules. Migrated as D2
    directs - a frame-addressed SpellMap default - the scanner conjures and is built with the profile it names.
    """
    aether = Aether(); Spellbook._aether = aether; Conduit._aether = aether
    book = Spellbook(aetheric_frame="annotation-category-same-named-classes")
    book.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    book.bind(spell=ScanProfileFromAgents, existence="unique", spellframe="agents", binding_name="ScanProfile")
    book.bind(spell=ScanProfileFromTools, existence="unique", spellframe="artificial_intelligence_tools",
              binding_name="ScanProfile")
    book.bind(spell=MCPScanner, existence="many")
    expected = _report("MCPScanner", "MCPScanner", _hidden_provider_line(
        "MCPScanner", "profile", "ScanProfileFromTools",
        "under a spellframe: ScanProfile at (spellframe='agents', binding_name='ScanProfile') - use "
        "SpellMap(spellframe='agents', binding_name='ScanProfile'); ScanProfile at "
        "(spellframe='artificial_intelligence_tools', binding_name='ScanProfile') - use "
        "SpellMap(spellframe='artificial_intelligence_tools', binding_name='ScanProfile'). Ask for it where it is "
        "bound - the SpellMap of the one it needs, as the parameter's default - or bind ScanProfileFromTools bare."))
    try:
        refused = _refusal(lambda: book.conjure(name="root"))
        assert refused == expected, "conjure is not refused naming both ScanProfile addresses"
    finally:
        book.cleanup()
    migrated = Spellbook(aetheric_frame="annotation-category-same-named-classes-by-address")
    migrated.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    migrated.bind(spell=ScanProfileFromAgents, existence="unique", spellframe="agents", binding_name="ScanProfile")
    migrated.bind(spell=ScanProfileFromTools, existence="unique", spellframe="artificial_intelligence_tools",
                  binding_name="ScanProfile")
    migrated.bind(spell=MCPScannerByAddress, existence="many")
    root = migrated.conjure(name="root")
    try:
        scanner = root.meld(MCPScannerByAddress)
        assert type(scanner.profile) is ScanProfileFromTools
        assert scanner.profile is root.meld(spellframe="artificial_intelligence_tools", binding_name="ScanProfile")
    finally:
        root.cleanup()
        migrated.cleanup()


def test_guard_explicit_address_selection_is_unchanged() -> None:
    """GUARD: melding the category member by its address keeps working; the category is still addressable."""
    root = _dynamic_root("annotation-category-explicit-address")
    try:
        root.bind(spell=Spectrum, existence="unique_per_conduit", spellframe="spectrum",
                  binding_name="Spectrum", disposal_method_names=["cleanup"])
        root.bind(spell=Toolbox, existence="unique_per_conduit", spellframe="spectrum",
                  binding_name="Toolbox", disposal_method_names=["cleanup"])
        assert isinstance(root.meld(spellframe="spectrum", binding_name="Toolbox"), Toolbox)
        assert isinstance(root.meld(spellframe="spectrum", binding_name="Spectrum"), Spectrum)
    finally:
        root.cleanup()


class SpectrumConfig(Cleanable):
    """A framework input bound as a named existing object in the "spectrum" category (MelderOps shape)."""

    def __init__(self, label: str) -> None:
        """Hold a marker."""
        super().__init__()
        self.label = label

    def cleanup(self) -> None:
        """Retire once."""
        if self._cleaned:
            return
        self._cleaned = True


class IrisConfig(Cleanable):
    """A second framework input in the same category."""

    def __init__(self, label: str) -> None:
        """Hold a marker."""
        super().__init__()
        self.label = label

    def cleanup(self) -> None:
        """Retire once."""
        if self._cleaned:
            return
        self._cleaned = True


class ManagerA(Cleanable):
    """A framework manager in the category, typed with the category's existing-object inputs."""

    def __init__(self, *, spectrum_config: SpectrumConfig, iris: IrisConfig) -> None:
        """Hold both inputs."""
        super().__init__()
        self.spectrum_config = spectrum_config
        self.iris = iris

    def cleanup(self) -> None:
        """Retire once."""
        if self._cleaned:
            return
        self._cleaned = True
        del self.spectrum_config
        del self.iris


class ManagerB(Cleanable):
    """Another manager in the category; no inputs."""

    def __init__(self) -> None:
        """No collaborators."""
        super().__init__()

    def cleanup(self) -> None:
        """Retire once."""
        if self._cleaned:
            return
        self._cleaned = True


def make_report() -> dict:
    """A function spell grouped under the category (factory semantics)."""
    return {"report": True}


class CommandCenter(Cleanable):
    """The consumer of the epic: requires the host by type and is melded with it supplied."""

    def __init__(self, *, spectrum: Spectrum, manager: ManagerA) -> None:
        """Hold the host and one manager."""
        super().__init__()
        self.spectrum = spectrum
        self.manager = manager

    def cleanup(self) -> None:
        """Retire once."""
        if self._cleaned:
            return
        self._cleaned = True
        del self.spectrum
        del self.manager


def test_many_category_members_never_become_providers_and_their_class_consumers_are_refused() -> None:
    """
    MelderOps shape: the host class, two named existing objects, two managers and a function spell all live in
    the "spectrum" category. Since 2026-11-07 the category hides every member from the class lookup, existing
    objects alike, so no member is a provider for any class annotation - not for `CommandCenter.spectrum: Spectrum`
    or `CommandCenter.manager: ManagerA`, not for the managers' typed inputs, which until then resolved the existing
    objects by their classes. From 2026-11-07 those were unresolved inputs an override supplied (as
    Spectrum.configure supplies the host); since patch hidden_provider_2026_11_07 each is a HIDDEN_PROVIDER error
    naming the member's address: ManagerA is refused at its late bind for both inputs, CommandCenter for both of its,
    and every meld of either raises its report, with every input supplied by override as well (D2). Every other
    member is still reached through its address.
    """
    root = _dynamic_root("annotation-category-melderops-shape")
    try:
        spectrum_config = SpectrumConfig("spectrum-config")
        iris = IrisConfig("iris")
        root.bind(spell=Spectrum, existence="unique_per_conduit", spellframe="spectrum",
                  binding_name="Spectrum", disposal_method_names=["cleanup"])
        root.bind(spell=spectrum_config, existence="unique", spellframe="spectrum", binding_name="SpectrumConfig")
        root.bind(spell=iris, existence="unique", spellframe="spectrum", binding_name="IrisConfig")
        manager_report = _report(
            "ManagerA", "ManagerA (frame 'spectrum')",
            _hidden_provider_line("ManagerA", "spectrum_config", "SpectrumConfig",
                                  _filed_at("SpectrumConfig", "spectrum", "SpectrumConfig")),
            _hidden_provider_line("ManagerA", "iris", "IrisConfig", _filed_at("IrisConfig", "spectrum", "IrisConfig")),
        )
        # the manager's typed inputs are existing objects filed under the category: hidden from their classes
        assert _refusal(lambda: root.bind(spell=ManagerA, existence="unique_per_conduit", spellframe="spectrum",
                                          binding_name="ManagerA", disposal_method_names=["cleanup"])) == (
            manager_report), "ManagerA's late bind is not refused for both of its category-filed inputs"
        root.bind(spell=ManagerB, existence="unique_per_conduit", spellframe="spectrum",
                  binding_name="ManagerB", disposal_method_names=["cleanup"])
        root.bind(spell=make_report, existence="unique", spellframe="spectrum", binding_name="make_report")
        center_report = _report(
            "CommandCenter", "CommandCenter (frame 'command_center')",
            _hidden_provider_line("CommandCenter", "spectrum", "Spectrum",
                                  _filed_at("Spectrum", "spectrum", "Spectrum")),
            _hidden_provider_line("CommandCenter", "manager", "ManagerA",
                                  _filed_at("ManagerA", "spectrum", "ManagerA")),
        )
        assert _refusal(lambda: root.bind(spell=CommandCenter, existence="many", spellframe="command_center",
                                          binding_name="center", disposal_method_names=["cleanup"])) == (
            center_report), "CommandCenter's late bind is not refused for the host and the manager"
        host = root.meld(spellframe="spectrum", binding_name="Spectrum")
        assert isinstance(host, Spectrum)
        assert _refusal(lambda: root.meld(spellframe="spectrum", binding_name="ManagerA",
                                          override={"spectrum_config": spectrum_config, "iris": iris})) == (
            manager_report), "an override let the refused ManagerA meld"
        manager = ManagerA(spectrum_config=spectrum_config, iris=iris)
        assert _refusal(lambda: root.meld(spellframe="command_center", binding_name="center",
                                          override={"spectrum": host, "manager": manager})) == center_report, (
            "an override let the refused CommandCenter meld")
        manager.cleanup()
        # every other member is reached through its address
        assert isinstance(root.meld(spellframe="spectrum", binding_name="ManagerB"), ManagerB)
        assert root.meld(spellframe="spectrum", binding_name="make_report") == {"report": True}
        assert root.meld(spellframe="spectrum", binding_name="SpectrumConfig") is spectrum_config
        assert root.meld(spellframe="spectrum", binding_name="Spectrum") is host
    finally:
        root.cleanup()
