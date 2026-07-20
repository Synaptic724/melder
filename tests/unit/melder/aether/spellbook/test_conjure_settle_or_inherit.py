"""
Unit tests: conjure settle-then-inherit (owner ruling 2026-07-20).
Unsettled world: dynamic=True settles it. Settled world: conjure
inherits; the flag never polices. Runs on 3.14t.
"""
import pytest

from melder import Aether, AethericFrameConfiguration, Conduit, SystemState
from melder.aether.spellbook.spellbook import Spellbook


@pytest.fixture(autouse=True)
def reset_aether_world() -> None:
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


def _book() -> Spellbook:
    book = Spellbook()
    book.bind(spell=Service, existence="unique")
    return book


def test_unsettled_world_dynamic_flag_settles_and_conjures():
    """Fresh world + dynamic=True: the flag IS the setting now."""
    conduit = _book().conjure(dynamic=True, name="settler")
    borrower = Spellbook().conjure(dynamic=True, name="borrower")
    assert conduit.link(borrower) is True  # dynamic machinery is live


def test_unsettled_world_plain_conjure_stays_static():
    """Fresh world + plain conjure: static conduit; dynamic verbs fail
    at their own gates, on purpose."""
    conduit = _book().conjure()
    other = Spellbook().conjure(name="peer")
    with pytest.raises(Exception):
        conduit.link(other)


def test_settled_automatic_world_ignores_the_flag():
    """Explicitly configured automatic: conjure(dynamic=True) INHERITS
    automatic - no policing throw; failure moves to link's own gate."""
    frame = Aether()._ensure_frame("default")
    frame.bind_frame_configuration(AethericFrameConfiguration(
        origin_spellbook_id=None, system_state=SystemState.automatic,
        ai_native_enabled=False, rift_enabled=False,
    ))
    conduit = _book().conjure(dynamic=True, name="asks-dynamic")
    other = Spellbook().conjure(name="peer")
    with pytest.raises(Exception):
        conduit.link(other)


def test_settled_dynamic_world_plain_conjure_inherits():
    """Configured dynamic: plain conjure() births a dynamic conduit."""
    frame = Aether()._ensure_frame("default")
    frame.bind_frame_configuration(AethericFrameConfiguration(
        origin_spellbook_id=None, system_state=SystemState.dynamic,
        ai_native_enabled=False, rift_enabled=False,
    ))
    conduit = _book().conjure(name="inheritor")
    borrower = Spellbook().conjure(name="borrower-too")
    assert conduit.link(borrower) is True
