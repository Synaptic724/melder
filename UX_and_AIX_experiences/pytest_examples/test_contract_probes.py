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
    """meld(override=dict) is the documented constructor-override lane."""
    book = md.Spellbook()
    book.bind(spell=Probe, existence="many")
    conduit = book.conjure()
    probe = conduit.meld(spell=Probe, override={"tag": "overridden"})
    assert probe is not None
    assert probe.tag == "overridden"


def test_probe_with_book_is_lock_only_not_cleanup():
    """__exit__ releases the lock; the book must remain USABLE after."""
    class AfterWith:
        """A second spell for the book. Probe again would be refused
        whether or not the book was cleaned: one class registers once,
        because its spell_id is the SHA256 of its code (0.2.8257)."""

    book = md.Spellbook()
    with book:
        book.bind(spell=Probe, existence="unique")
    # if the with-block had cleaned the book, this second bind would raise
    second = book.bind(spell=AfterWith, existence="many", binding_name="again")
    assert isinstance(second, str)


def test_probe_meld_by_binding_name_alone_is_refused():
    """PROVEN: binding_name is a sub-key, never an address by itself."""
    book = md.Spellbook()
    book.bind(spell=Probe, existence="unique", binding_name="the-probe")
    conduit = book.conjure()
    with pytest.raises(ValueError):
        conduit.meld(binding_name="the-probe")
    # the bind placed the spell at ("probe", "the-probe") - so the name
    # form must carry the binding_name to construct the same key
    assert conduit.meld(spell="Probe", binding_name="the-probe") is not None
    with pytest.raises(KeyError):
        conduit.meld(spell="Probe")  # default slot is empty


def test_probe_meld_by_spell_name_form():
    """27 prints this contract; the probe records the exact behavior."""
    book = md.Spellbook()
    book.bind(spell=Probe, existence="unique")
    conduit = book.conjure()
    try:
        result = conduit.meld(spell="Probe")
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


def test_probe_same_name_different_internals_are_two_spells():
    """
    FLIPPED (0.2.8206, 0.2.8257): two classes NAMED Potato with different
    internals are two spells, each at its own address. A spell_id is the
    SHA256 of each class's code - here a different class-level value and
    a different closure value - so the ids differ, and since 0.2.8206
    Phase 4 checks the full (spellframe, binding_name) address instead of
    the bare name, so conjure accepts both.

    This row used to pin the refusal under a DIVERGENCE FLAG: owner design
    intent said spells are SHA256 content-matched and same-name/different-
    internals passes WITH binding names, while DuplicateSpellNameStrategy
    keyed on the bare name. The intent is the behavior now; the flag is
    closed.
    """
    book = md.Spellbook()
    book.bind(spell=_make_potato("russet"), existence="unique",
              binding_name="russet")
    book.bind(spell=_make_potato("yukon"), existence="many",
              binding_name="yukon")
    conduit = book.conjure()
    russet = conduit.meld(spell="Potato", binding_name="russet")
    yukon = conduit.meld(spell="Potato", binding_name="yukon")
    assert russet.describe() == "potato:russet"
    assert yukon.describe() == "potato:yukon"
    print("same-name diff-SHA with binding names: two spells (the intent)")


def test_probe_same_class_rebind_is_refused_at_bind():
    """
    The SAME class bound twice in one book, told apart only by
    binding_name, is refused at the second BIND (0.2.8257): a spell_id is
    the SHA256 of the class's code and of nothing from the bind call, so
    both binds name one spell, and one object registers once. This row
    used to pin the observed run truth before that - the binding_name made
    a second spell_id and conjure refused the pair with
    DUPLICATE_SPELL_NAME.
    """
    book = md.Spellbook()
    book.bind(spell=Probe, existence="unique", binding_name="first")
    with pytest.raises(RuntimeError, match="Spell ID collision"):
        book.bind(spell=Probe, existence="many", binding_name="second")
    print("same class rebound by binding_name: refused at bind")


def test_probe_same_class_rebind_across_spellframes_is_refused_at_bind():
    """
    ANSWERED (0.2.8257): another spellframe does not make the same class
    a second spell either. The spell_id is the class's code, so the
    second bind is refused whatever spellframe or binding_name it names.
    This row used to pin a conjure refusal from the name strategy, which
    ignored frames (run 2) - part of the potato row's divergence flag,
    now closed.
    """
    book = md.Spellbook()
    book.bind(spell=Probe, existence="unique",
              spellframe="pool-a", binding_name="first")
    with pytest.raises(RuntimeError, match="Spell ID collision"):
        book.bind(spell=Probe, existence="many",
                  spellframe="pool-b", binding_name="second")
    print("same class rebound in another spellframe: refused at bind")
