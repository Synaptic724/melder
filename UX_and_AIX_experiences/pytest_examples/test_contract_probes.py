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


def test_probe_bind_swallows_unknown_kwargs_silently():
    """
    PROVEN (run 2): bind(**kwargs) is the hook channel, and UNKNOWN keys
    are accepted silently - env="production" binds without error and the
    value goes nowhere. FLAGGED as a fail-fast design question: a typo'd
    kwarg vanishes instead of raising.
    """
    book = md.Spellbook()
    spell_id = book.bind(spell=Probe, existence="unique", env="production")
    assert isinstance(spell_id, str)
    conduit = book.conjure()
    probe = conduit.meld(spell=Probe)
    assert probe.tag == "default"  # env= never reached the constructor
    print("unknown bind kwarg silently ignored; ctor untouched")


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


def test_probe_meld_by_binding_name_alone_is_refused():
    """PROVEN: binding_name is a sub-key, never an address by itself."""
    book = md.Spellbook()
    book.bind(spell=Probe, existence="unique", binding_name="the-probe")
    conduit = book.conjure()
    with pytest.raises(ValueError):
        conduit.meld(binding_name="the-probe")
    assert conduit.meld(spell_name="Probe") is not None


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
def _make_potato(marker: str):
    """Build a distinct class NAMED Potato with differing internals."""
    class Potato:
        flavor = marker

        def describe(self) -> str:
            return "potato:" + marker
    return Potato


def test_probe_same_name_different_internals_currently_refused():
    """
    DIVERGENCE FLAG (runs 1-2): owner design intent says spells are
    SHA256 content-matched and same-name/different-internals passes WITH
    binding names. The runtime REFUSES it: DuplicateSpellNameStrategy
    keys on the bare name and ignores the binding_name/spellframe
    disambiguation its own error message recommends. This probe pins
    CURRENT behavior; flip it to the pass-assertion when the strategy is
    fixed (tracked on the UX/AIX beginner epic as a runtime bug).
    """
    book = md.Spellbook()
    book.bind(spell=_make_potato("russet"), existence="unique",
              binding_name="russet")
    book.bind(spell=_make_potato("yukon"), existence="many",
              binding_name="yukon")
    with pytest.raises(md.SpellbookValidationError):
        book.conjure()
    print("same-name diff-SHA with binding names: REFUSED (intent: pass)")


def test_probe_same_class_rebind_without_frames_fails_conjure():
    """
    The observed run truth: the SAME class (same SHA) bound twice with
    only binding_names to tell them apart dies at conjure with
    DUPLICATE_SPELL_NAME.
    """
    book = md.Spellbook()
    book.bind(spell=Probe, existence="unique", binding_name="first")
    book.bind(spell=Probe, existence="many", binding_name="second")
    with pytest.raises(md.SpellbookValidationError):
        book.conjure()
    print("same-SHA rebind without frames: conjure refused (as observed)")


def test_probe_same_class_rebind_with_distinct_frames():
    """
    ANSWERED (run 2): frame separation does NOT legalize same-name
    rebinds - the name strategy ignores frames entirely. Part of the
    same divergence flag as the potato probe.
    """
    book = md.Spellbook()
    book.bind(spell=Probe, existence="unique",
              spellframe="pool-a", binding_name="first")
    book.bind(spell=Probe, existence="many",
              spellframe="pool-b", binding_name="second")
    with pytest.raises(md.SpellbookValidationError):
        book.conjure()
    print("same-SHA rebind across frames: REFUSED (frames do not "
          "disambiguate the name strategy either - same divergence flag)")
