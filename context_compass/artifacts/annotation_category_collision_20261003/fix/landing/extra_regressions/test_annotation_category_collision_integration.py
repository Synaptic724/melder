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
"""

import sys
import types
from collections.abc import Iterator
from typing import Any, Protocol, Type

import pytest

from melder import Aether, Cleanable, Conduit, Spellbook
from melder.utilities.custom_exceptions.unresolved_input_error import UnresolvedInputError


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
    """The host object a consumer annotates; bound as a unique at ("spectrum", "Spectrum")."""

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
    """The reported four-case matrix: Spectrum resolves whether or not Toolbox shares the "spectrum" category."""
    root = _dynamic_root("annotation-category-matrix")
    try:
        root.bind(spell=Spectrum, existence="unique_per_conduit", spellframe="spectrum",
                  binding_name="Spectrum", disposal_method_names=["cleanup"])
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
    """A string annotation whose name is unbound at runtime resolves exactly as the class object does."""
    root = _dynamic_root("annotation-category-unbound-string")
    try:
        root.bind(spell=Spectrum, existence="unique_per_conduit", spellframe="spectrum",
                  binding_name="Spectrum", disposal_method_names=["cleanup"])
        root.bind(spell=Toolbox, existence="unique_per_conduit", spellframe="spectrum",
                  binding_name="Toolbox", disposal_method_names=["cleanup"])
        root.bind(spell=_center_with_unbound_string_annotation(), existence="many",
                  spellframe="command_center", binding_name="center", disposal_method_names=["cleanup"])
        center = root.meld(spellframe="command_center", binding_name="center")
        assert isinstance(center.spectrum, Spectrum)
    finally:
        root.cleanup()


def test_lone_category_member_is_not_injected_for_a_type_annotation() -> None:
    """With no Spectrum bound, a Toolbox in category "spectrum" is NOT handed to `spectrum: Spectrum`.

    The parameter is an unresolved input: the meld refuses without an override and takes the supplied
    object with one. Today the Toolbox is injected silently.
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


def test_guard_two_providers_of_the_annotated_type_still_raise_ambiguity() -> None:
    """GUARD: two spells of the annotated TYPE at distinct addresses are a real ambiguity, reported by Phase 3."""
    root = _dynamic_root("annotation-category-type-ambiguity")
    try:
        root.bind(spell=Spectrum, existence="unique_per_conduit", spellframe="spectrum",
                  binding_name="primary", disposal_method_names=["cleanup"])
        root.bind(spell=Spectrum, existence="unique_per_conduit", spellframe="mirror",
                  binding_name="secondary", disposal_method_names=["cleanup"])
        with pytest.raises(RuntimeError, match="multiple DI candidates"):
            root.bind(spell=CenterWithClass, existence="many", spellframe="command_center",
                      binding_name="center", disposal_method_names=["cleanup"])
    finally:
        root.cleanup()


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


def test_many_category_members_never_become_providers_for_the_type() -> None:
    """
    MelderOps shape: the host class, two named existing objects, two managers and a function spell all live in
    the "spectrum" category; `CommandCenter.spectrum: Spectrum` resolves the host alone, the managers' typed
    inputs resolve the existing objects by their classes, and melding the center with the host supplied by
    override (as Spectrum.configure does) injects exactly that object.
    """
    root = _dynamic_root("annotation-category-melderops-shape")
    try:
        spectrum_config = SpectrumConfig("spectrum-config")
        iris = IrisConfig("iris")
        root.bind(spell=Spectrum, existence="unique_per_conduit", spellframe="spectrum",
                  binding_name="Spectrum", disposal_method_names=["cleanup"])
        root.bind(spell=spectrum_config, existence="unique", spellframe="spectrum", binding_name="SpectrumConfig")
        root.bind(spell=iris, existence="unique", spellframe="spectrum", binding_name="IrisConfig")
        root.bind(spell=ManagerA, existence="unique_per_conduit", spellframe="spectrum",
                  binding_name="ManagerA", disposal_method_names=["cleanup"])
        root.bind(spell=ManagerB, existence="unique_per_conduit", spellframe="spectrum",
                  binding_name="ManagerB", disposal_method_names=["cleanup"])
        root.bind(spell=make_report, existence="unique", spellframe="spectrum", binding_name="make_report")
        root.bind(spell=CommandCenter, existence="many", spellframe="command_center",
                  binding_name="center", disposal_method_names=["cleanup"])
        host = root.meld(spellframe="spectrum", binding_name="Spectrum")
        center = root.meld(spellframe="command_center", binding_name="center", override={"spectrum": host})
        assert center.spectrum is host
        assert isinstance(center.manager, ManagerA)
        assert center.manager.spectrum_config is spectrum_config
        assert center.manager.iris is iris
        # without the override the host still resolves by its type, not by the category
        second = root.meld(spellframe="command_center", binding_name="center")
        assert isinstance(second.spectrum, Spectrum)
        assert second.manager is center.manager
    finally:
        root.cleanup()
