"""
Unit tests: bind kwargs thread into Spell's OWN kwargs channel
(spell.metadata) - owner design, 2026-07-19. Runs on 3.14t.
"""
import pytest

from melder import Aether, Conduit
from melder.aether.spellbook.spellbook import Spellbook


@pytest.fixture(autouse=True)
def reset_aether_world() -> None:
    """Fresh world per test (component-suite fixture pattern)."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


class Service:
    pass


def test_bind_kwargs_land_in_spell_metadata():
    """Leftover bind kwargs arrive in Spell.__init__ and store as metadata."""
    book = Spellbook()
    spell_id = book.bind(
        spell=Service, existence="unique",
        owner_team="payments", tier="gold",
        post_hooks=[lambda *a, **k: None],
    )
    spell = book.find_spell_by_id(spell_id)
    assert spell.metadata == {"owner_team": "payments", "tier": "gold"}


def test_hook_keys_never_leak_into_metadata():
    """The three hook transfers stay owned by bind's hook lane."""
    book = Spellbook()
    spell_id = book.bind(
        spell=Service, existence="unique",
        pre_hooks=[lambda *a, **k: None],
    )
    spell = book.find_spell_by_id(spell_id)
    assert spell.metadata == {}


def test_native_spell_params_stay_sovereign():
    """A kwarg colliding with a bind-filled Spell param fails LOUDLY from
    Spell's own signature (multiple values), never silently jacks it."""
    book = Spellbook()
    with pytest.raises(TypeError):
        book.bind(spell=Service, existence="unique", spell_id="jacked")
