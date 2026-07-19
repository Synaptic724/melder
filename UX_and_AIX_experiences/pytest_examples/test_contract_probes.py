"""
Contract probes - each row documents ONE behavior the examples lean on
that source reading could not fully settle. Failures here mean an
example teaches the wrong thing: report the failing row, not the file.

    pytest UX_and_AIX_experiences/pytest_examples -v
"""
import melder as md
import pytest


class Probe:
    def __init__(self, tag: str = "default") -> None:
        self.tag = tag


class Disposable:
    events: list = []

    def close(self) -> None:
        Disposable.events.append("closed")


def test_probe_bind_kwargs_are_hooks_not_ctor_args():
    """bind(**kwargs) feeds _add_hooks_to_spell - env= must be REFUSED."""
    book = md.Spellbook()
    with pytest.raises(Exception) as err:
        book.bind(spell=Probe, existence="unique", env="production")
    print("bind(env=...) refused with:", err.typename)


def test_probe_spell_override_delivers_ctor_kwargs():
    """meld(spell_override=dict) is the documented ctor-override lane."""
    book = md.Spellbook()
    book.bind(spell=Probe, existence="many")
    conduit = book.conjure()
    probe = conduit.meld(spell=Probe, spell_override={"tag": "overridden"})
    assert probe is not None
    assert probe.tag == "overridden"


def test_probe_with_book_is_lock_only_not_cleanup():
    """__exit__ releases the lock; the book must remain USABLE after."""
    book = md.Spellbook()
    with book:
        book.bind(spell=Probe, existence="unique")
    # if the with-block had cleaned the book, this second bind would raise
    second = book.bind(spell=Probe, existence="many", binding_name="again")
    assert isinstance(second, str)


def test_probe_meld_by_binding_name_alone():
    book = md.Spellbook()
    book.bind(spell=Probe, existence="unique", binding_name="the-probe")
    conduit = book.conjure()
    assert conduit.meld(binding_name="the-probe") is not None


def test_probe_meld_by_spell_name_form():
    """27 prints this contract; the probe records the exact behavior."""
    book = md.Spellbook()
    book.bind(spell=Probe, existence="unique")
    conduit = book.conjure()
    try:
        result = conduit.meld(spell_name="Probe")
        print("meld(spell_name=...) ->", type(result).__name__)
    except Exception as err:
        print("meld(spell_name=...) raised:", type(err).__name__)


def test_probe_unregistered_meld_outcome():
    """07/40 handle both lanes; the probe pins which one is real."""
    book = md.Spellbook()
    book.bind(spell=Probe, existence="unique")
    conduit = book.conjure()

    class Stranger:
        pass

    try:
        outcome = conduit.meld(spell=Stranger)
        print("unregistered meld answered:", outcome)
    except Exception as err:
        print("unregistered meld raised:", type(err).__name__)


def test_probe_double_bind_same_class_no_names():
    try:
        book = md.Spellbook()
        first = book.bind(spell=Probe, existence="unique")
        second = book.bind(spell=Probe, existence="many")
        print("double bind accepted; ids differ:", first != second)
    except Exception as err:
        print("double bind refused:", type(err).__name__)


def test_probe_disposal_fires_and_when():
    """13/35/40 stage-print this; the probe asserts it fires AT ALL."""
    Disposable.events.clear()
    book = md.Spellbook()
    book.bind(spell=Disposable, existence="unique",
              disposal_method_names=["close"])
    conduit = book.conjure()
    conduit.meld(spell=Disposable)
    conduit.cleanup()
    after_conduit = list(Disposable.events)
    book.cleanup()
    print("disposal after conduit.cleanup():", after_conduit,
          "| after book.cleanup():", Disposable.events)
    assert Disposable.events, "close() never fired through teardown"
