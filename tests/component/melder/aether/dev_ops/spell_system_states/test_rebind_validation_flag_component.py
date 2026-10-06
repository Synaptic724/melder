"""Component coverage: the Book's validation flag follows a same-id rebind (rebind-after-first-meld repair).

Real Spellbook, Conduit, SpellSystemStates and RiskManager wiring, no external IO. After `cleanup_spell`
and a rebind of the same class at the same address, `RiskManager.register_spell` recomputes resolution
risk from the live per-conduit verdict - now unknown because the registry retired the dead definition's
verdict - so the Book reports validation required until the replacement's meld revalidates it.
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


class FlagProbe(Cleanable):
    """Minimal tracked object with no collaborators."""

    def __init__(self, value: int = 1) -> None:
        """Store one scalar."""
        super().__init__()
        self.value: int = value

    def cleanup(self) -> None:
        """Retire once."""
        if self._cleaned:
            return
        self._cleaned = True
        del self.value


def _dynamic_root(frame: str) -> tuple[Spellbook, Conduit]:
    """Conjure one dynamic root with caching off on a fresh frame."""
    book = Spellbook(aetheric_frame=frame)
    book.configure_aether_frame(system_state="dynamic", system_caching_enabled=False,
                                disposal=None, disposal_method_names=None)
    book.get_configuration().freeze()
    root = book.conjure(dynamic=True, name="definitions")
    return book, root


def _bind(root: Conduit) -> str:
    """Late-bind the probe as a `many` definition."""
    return root.bind(spell=FlagProbe, existence="many", spellframe="flags", binding_name="probe",
                     disposal_method_names=["cleanup"])


def test_component_validation_flag_is_required_after_the_rebind_and_cleared_by_the_revalidating_meld() -> None:
    """True after the same-id rebind (unknown verdict), False once the replacement's meld revalidates."""
    book, root = _dynamic_root("rebind-flag-component")
    try:
        identifier = _bind(root)
        root.meld(spellframe="flags", binding_name="probe")
        assert book._spellbook_validation_required is False
        definition = root.get_spell_by_id(identifier, "rebind-flag-component")
        root.cleanup_spell(spell=definition)
        assert _bind(root) == identifier
        assert book._spellbook_validation_required is True
        assert root.meld(spellframe="flags", binding_name="probe", override={"value": 2}).value == 2
        assert book._spellbook_validation_required is False
    finally:
        root.cleanup()


def test_component_validation_flag_behaves_like_a_first_late_bind_for_the_replacement() -> None:
    """A rebind is reported exactly as a first-time late bind: required until the first meld."""
    book, root = _dynamic_root("rebind-flag-component-first")
    try:
        identifier = _bind(root)
        first_bind_flag = book._spellbook_validation_required
        root.meld(spellframe="flags", binding_name="probe")
        definition = root.get_spell_by_id(identifier, "rebind-flag-component-first")
        root.cleanup_spell(spell=definition)
        _bind(root)
        assert first_bind_flag is True
        assert book._spellbook_validation_required is True
    finally:
        root.cleanup()


def test_component_removed_definition_leaves_the_flag_clear_until_something_is_rebound() -> None:
    """Removal alone adds no risk: the owner conduit's lineage leaves the risk model with the definition."""
    book, root = _dynamic_root("rebind-flag-component-removal")
    try:
        identifier = _bind(root)
        root.meld(spellframe="flags", binding_name="probe")
        definition = root.get_spell_by_id(identifier, "rebind-flag-component-removal")
        root.cleanup_spell(spell=definition)
        assert book._spellbook_validation_required is False
    finally:
        root.cleanup()
