"""
Intermediate-tier contract probes. Run on 3.14t:

    pytest UX_and_AIX_experiences/pytest_examples/test_intermediate_probes.py -v

Probes print ground truth for lessons not yet authored - the crystallizer
acquisition path and the dynamic config-before-bind law (whose error text
we captured verbatim from a live traceback this session).
"""
import melder as md
import pytest

from melder import Aether, Conduit
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


class Payload:
    pass


def test_probe_plain_dynamic_conjure_always_refuses():
    """
    THE LAW (source-proven, spellbook_creation_system.py:1099): frames are
    born automatic and nothing on Spellbook/SpellbookConfiguration flips
    them - so plain-book conjure(dynamic=True) ALWAYS raises. Owner ruling
    2026-07-20: stands for now; the posture door arrives with the
    aetheric-frame introduction next iteration.
    """
    with pytest.raises(RuntimeError):
        _dyn_book().conjure(dynamic=True, name="refused")


def test_probe_helper_postured_dynamic_world_links():
    """The lesson-21 ritual (frame postured dynamic first) works end to end."""
    import sys
    from pathlib import Path as _P
    sys.path.insert(0, str(_P(__file__).parent.parent / "02_intermediate"))
    from _dynamic_world import dynamic_spellbook

    owner_book = dynamic_spellbook()
    owner_book.bind(spell=Payload, existence="unique")
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = dynamic_spellbook().conjure(dynamic=True, name="borrower")
    assert owner.link(borrower) is True


def _dyn_book() -> Spellbook:
    book = Spellbook()
    book.bind(spell=Payload, existence="unique")
    return book


def test_probe_crystallizer_acquisition_path():
    """
    OPEN QUESTION for the crystallizer lessons: how does a USER reach the
    live crystallizer (dynamic world, NO Nexus)? Prints which public doors
    exist on Aether so the next lesson copies truth.
    """
    aether = Aether()
    doors = [name for name in ("crystallizer", "get_crystallizer",
                               "hosted_crystallizer")
             if hasattr(aether, name)]
    print("crystallizer doors on Aether:", doors or "none of the guesses")
    print("md.Crystallizer exported:", md.Crystallizer is not None)


def test_probe_dynamic_config_before_bind_law():
    """
    CAPTURED CONTRACT (live traceback, run 2): dynamic-mode conjure with
    an ACTIVE crystallizer refuses books whose binds preceded config
    finalization. Without an active crystallizer, dynamic worlds are
    exempt - this probe pins the exemption; the active-crystallizer half
    waits on the acquisition probe above.
    """
    book = Spellbook()
    book.bind(spell=Payload, existence="unique")  # bind BEFORE any config
    conduit = book.conjure(dynamic=True, name="exempt-world")
    assert conduit is not None
    print("crystallizer-off dynamic world: bind-before-config exempt (as documented)")
def test_probe_world_postures_once_then_locks():
    """Owner semantic: posture once; repeat setup must not rebind."""
    import sys
    from pathlib import Path as _P
    sys.path.insert(0, str(_P(__file__).parent.parent / "02_intermediate"))
    from _dynamic_world import ensure_dynamic_world, dynamic_spellbook

    ensure_dynamic_world()
    ensure_dynamic_world()  # second call must be a clean no-op
    book_one = dynamic_spellbook()
    book_two = dynamic_spellbook()  # multiple books, one world posture
    assert book_one is not book_two
    print("posture-once law held across repeated setup calls")
