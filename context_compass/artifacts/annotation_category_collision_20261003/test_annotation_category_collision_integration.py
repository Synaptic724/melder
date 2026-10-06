"""Integration regressions: a type annotation selects type providers; a spellframe is a category.

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

import sys
import types
from collections.abc import Iterator
from typing import Any, Type

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


class IService:
    """A type used as a spellframe object: a shape label, not a string category."""


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
    """Consumer annotated with the shape label."""

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


_EPIC = "EPIC-2026-10-03-annotation_category_provider_collision: a same-named spellframe category is read as a provider set"


@pytest.mark.parametrize("annotation", ["class", "string"])
@pytest.mark.parametrize(
    "shared_category",
    [
        False,
        pytest.param(True, marks=pytest.mark.xfail(strict=True, reason=_EPIC)),
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


@pytest.mark.xfail(strict=True, reason=_EPIC)
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


@pytest.mark.xfail(strict=True, reason=_EPIC + " (silent wrong-type injection)")
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


def test_guard_class_object_frame_is_a_shape_label_that_resolves_its_annotation() -> None:
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
