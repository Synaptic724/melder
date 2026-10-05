"""Melder-only port of the epic's four-case public-API probe (annotation vs spellframe category).

Spectrum is bound as a unique at ("spectrum", "Spectrum"); Toolbox is bound either in the same category
"spectrum" or in another; a consumer annotates its dependency as the Spectrum class or as the string
"Spectrum" (a TYPE_CHECKING-only name at runtime). Expected per the owner's ruling: all four resolve the
Spectrum provider.
"""

from collections.abc import Iterator

import pytest
from melder import Aether, Cleanable, Conduit, Spellbook


@pytest.fixture(autouse=True)
def reset_melder() -> Iterator[None]:
    """Fresh cold Aether before and after every case."""
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
    """The host object a consumer annotates."""

    def __init__(self) -> None:
        super().__init__()

    def cleanup(self) -> None:
        if self._cleaned:
            return
        self._cleaned = True


class Toolbox(Cleanable):
    """An unrelated framework service that may share the host's category."""

    def __init__(self) -> None:
        super().__init__()

    def cleanup(self) -> None:
        if self._cleaned:
            return
        self._cleaned = True


class CenterWithClass(Cleanable):
    """Consumer annotated with the class object."""

    def __init__(self, *, spectrum: Spectrum) -> None:
        super().__init__()
        self.spectrum = spectrum

    def cleanup(self) -> None:
        if self._cleaned:
            return
        self._cleaned = True
        del self.spectrum


class CenterWithString(Cleanable):
    """Consumer annotated with the type's name as a string (TYPE_CHECKING-only shape)."""

    def __init__(self, *, spectrum: "Spectrum") -> None:
        super().__init__()
        self.spectrum = spectrum

    def cleanup(self) -> None:
        if self._cleaned:
            return
        self._cleaned = True
        del self.spectrum


@pytest.mark.parametrize("annotation", ["class", "string"])
@pytest.mark.parametrize("shared_category", [False, True])
def test_spectrum_annotation_selects_the_spectrum_provider(annotation: str, shared_category: bool) -> None:
    """A Spectrum annotation resolves the Spectrum spell whether or not Toolbox shares the category."""
    book = Spellbook(aetheric_frame="spectrum-probe")
    book.configure_aether_frame(system_state="dynamic", system_caching_enabled=False,
                                disposal=None, disposal_method_names=None)
    book.get_configuration().freeze()
    root = book.conjure(dynamic=True, name="host")
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
