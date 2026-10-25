"""
Integration: a notch whose incoming version fails its structural check is refused with nothing moved
(STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers; patch failed_notch_refusal_2026_10_18).

Phases 1-4 of a version that was never compiled run when it is notched in. Until the story's fix they ran at the
transaction's commit, after the switch, and nothing undid the switch: `notch_spell` raised SpellbookValidationError
while the lender's index selected the broken version, its borrowers kept the old one, and the lender could not meld
the index by address (measured on 0.2.8255, and on 0.2.8260, where a spell_id is the hash of the object's code).
With the fix the notch runs the check inside its window and, when the check fails, puts the structure back before
it raises: the owner's answer (a), "refuse it and throw and move on". Until it lands these tests fail.

Two broken versions are used. `SelfMade`'s constructor takes its own class (SELF_DEPENDENCY at Phase 4).
`TimedGreeter`'s constructor needs a `Clock` while two are registered (AMBIGUOUS_PROVIDER): nothing in it loops, so
it shows the half-switch follows any failing check, not recursion. Each is only checked once it is active, because
a parked version is not in the pool Phase 3 resolves against.

Worlds follow probe N1-N3 (artifacts/correctness_defects_20261017/probes/probe_failed_notch_commit.py): a dynamic
frame with caching off, English active on the lender's index and, when a borrower is asked for, a second Book that
links and contracts the whole index. Every version is staged under English's binding (Greeter, 'greeter'): every
version of an index is bound the way its first version was (2026-10-25).
"""
import contextlib
from typing import Any, Iterator, List, Optional, Protocol, Set, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError

pytestmark = pytest.mark.integration


class Greeter(Protocol):
    """The contract every version implements."""

    def greet(self) -> str:
        """Return a greeting."""
        ...


class English:
    """The version bound active."""

    def greet(self) -> str:
        """Return the English greeting."""
        return "hello"


class French:
    """A sound version staged beside it."""

    def greet(self) -> str:
        """Return the French greeting."""
        return "bonjour"


class SelfMade:
    """A broken version: its constructor takes its own class (SELF_DEPENDENCY once it is active)."""

    def __init__(self, other: SelfMade) -> None:
        """
        Keep the other instance.

        Args:
            other: Another instance of this class; no meld can supply one.
        """
        self.other = other

    def greet(self) -> str:
        """Return a greeting."""
        return "hi"


class Speaker:
    """The borrower Book's consumer of the lender's index."""

    def __init__(self, greeter: Greeter) -> None:
        """
        Keep the greeter the borrower resolves.

        Args:
            greeter: The version the borrower's contracted copy of the index makes active.
        """
        self.greeter = greeter


class Clock(Protocol):
    """What `TimedGreeter` needs; a world built with `clocks=True` registers two providers of it."""

    def now(self) -> str:
        """Return the time of day."""
        ...


class UtcClock:
    """One registered provider of `Clock`."""

    def now(self) -> str:
        """Return the time in UTC."""
        return "12:00 UTC"


class LocalClock:
    """A second registered provider of `Clock`, so a single `Clock` parameter has two candidates."""

    def now(self) -> str:
        """Return the local time."""
        return "06:00 local"


class TimedGreeter:
    """
    A broken version with no recursion: its constructor needs a `Clock` and two are registered
    (AMBIGUOUS_PROVIDER once it is active).
    """

    def __init__(self, clock: Clock) -> None:
        """
        Keep the clock.

        Args:
            clock: The clock to read; with `UtcClock` and `LocalClock` both registered no meld can pick one.
        """
        self.clock = clock

    def greet(self) -> str:
        """Return a greeting with the time."""
        return "hello at " + self.clock.now()


def _reset_world() -> None:
    """Fresh utility, Nexus and Aether singletons, rebound on Spellbook and Conduit."""
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def fresh_world() -> Iterator[None]:
    """Isolate each test behind fresh singletons."""
    _reset_world()
    yield
    _reset_world()


def _make_spellbook(frame: str, *, configure_frame: bool, rift_enabled: bool = False) -> Spellbook:
    """
    A Book in `frame`; the first Book of a frame also sets the frame's posture.

    Args:
        frame: The frame the Book lives in.
        configure_frame: Set the frame dynamic with caching off (probe N1-N3's posture); only the first Book does.
        rift_enabled: Make the frame publish into passive Nexus records.

    Returns:
        Spellbook: A new Book.
    """
    book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    if configure_frame:
        book.configure_aether_frame(
            system_state="dynamic", disposal=None, disposal_method_names=None, system_caching_enabled=False,
            rift_enabled=rift_enabled,
        )
    return book


class _World:
    """Handles of one lender and, when one was built, its index-linked borrower."""

    def __init__(self, book: Spellbook, lender: Conduit, index: SpellIndex, english_id: str, frame: str) -> None:
        """
        Keep the lender's handles; `_world` sets the borrower's when it builds one.

        Args:
            book: The lender's Book.
            lender: The lender's root conduit.
            index: The index English is active on.
            english_id: English's spell_id.
            frame: The frame the Books live in.
        """
        self.book = book
        self.lender = lender
        self.index = index
        self.english_id = english_id
        self.frame = frame
        self.borrower_book: Optional[Spellbook] = None
        self.borrower: Optional[Conduit] = None
        self.speaker_id: Optional[str] = None

    def stage(self, spell: type, binding_name: str = "greeter") -> str:
        """
        Stage `spell` on the lender's index through the lender.

        Args:
            spell: The class to stage.
            binding_name: The address it is staged at.

        Returns:
            str: The staged version's spell_id.
        """
        return self.lender.bind_inactive(
            spell=spell, spell_index=self.index, spellframe=Greeter, binding_name=binding_name,
            existence=Existence.many, permissions="create",
        )

    def frame_claim(self, key: Tuple[str, str]) -> Optional[str]:
        """
        The spell_id the frame's lookup holds for `key`, or None.

        Args:
            key: A binding signature `(frame_key, bind_key)`.

        Returns:
            Optional[str]: The claiming spell_id.
        """
        return Aether().get_frame(self.frame).get_lookup(key)

    def borrower_copies(self) -> Tuple[Set[str], Set[str]]:
        """
        The borrower's active and parked copies of the lender's versions, by spell_id.

        Returns:
            Tuple[Set[str], Set[str]]: (active spell_ids, parked spell_ids).
        """
        assert self.borrower_book is not None
        active = set(self.borrower_book._contracted_spells_by_id.get(self.lender._id, {}))
        parked = set(self.borrower_book._inactive_contracted_spells.get(self.lender._id, {}))
        return active, parked

    def nexus_spell_records(self) -> Set[Tuple[str, str]]:
        """
        The passive Nexus spell-record keys of the frame, `(spellbook id, spell_id)`.

        Returns:
            Set[Tuple[str, str]]: The published keys.
        """
        return set(Nexus()._get_required_frame_descriptor(self.frame).spell_records_by_key)


@contextlib.contextmanager
def _world(
    frame: str, *, borrower: bool = False, rift_enabled: bool = False, clocks: bool = False,
) -> Iterator[_World]:
    """
    English active on the lender's index; optionally a borrower that contracts the whole index.

    Args:
        frame: The frame for both Books.
        borrower: Build an index-linked borrower Book with a consumer (`Speaker`) of the index.
        rift_enabled: Make the frame publish passive Nexus records.
        clocks: Register `UtcClock` and `LocalClock` as `Clock` providers in the lender's Book, so `TimedGreeter`'s
            `clock` parameter has two candidates.

    Yields:
        _World: The handles; both roots are torn down on exit.
    """
    book = _make_spellbook(frame, configure_frame=True, rift_enabled=rift_enabled)
    borrower_book = _make_spellbook(frame, configure_frame=False) if borrower else None
    english_id = book.bind(
        spell=English, spellframe=Greeter, binding_name="greeter", existence=Existence.many, permissions="create",
    )
    if clocks:
        book.bind(
            spell=UtcClock, spellframe=Clock, binding_name="utc", existence=Existence.many, permissions="create",
        )
        book.bind(
            spell=LocalClock, spellframe=Clock, binding_name="local", existence=Existence.many, permissions="create",
        )
    speaker_id = None
    if borrower_book is not None:
        speaker_id = borrower_book.bind(spell=Speaker, existence=Existence.many, permissions="create")
    lender = book.conjure(dynamic=True, name="lender")
    world = _World(book, lender, book.find_spell_by_spell_id(english_id).spell_index, english_id, frame)
    try:
        if borrower_book is not None:
            world.borrower_book = borrower_book
            world.borrower = borrower_book.conjure(dynamic=True, name="borrower")
            world.speaker_id = speaker_id
            lender.link(world.borrower)
            with world.borrower.transaction("link", conduits=[world.borrower, lender]):
                assert world.borrower.add_index_to_contract(index=world.index, conduit=lender, permissions="create")
        yield world
    finally:
        if world.borrower is not None:
            world.borrower.cleanup()
        lender.cleanup()


def _refused_notch(world: _World, spell_id: str, index: Optional[SpellIndex] = None) -> SpellbookValidationError:
    """
    Notch to `spell_id` and return the SpellbookValidationError it must raise.

    Args:
        world: The handles.
        spell_id: The broken version's spell_id.
        index: The index to notch; the world's index when None.

    Returns:
        SpellbookValidationError: The refusal.
    """
    with pytest.raises(SpellbookValidationError) as refused:
        world.lender.notch_spell(spell_index=world.index if index is None else index, spell_id=spell_id)
    return refused.value


def _assert_english_stands(world: _World, broken_id: str) -> None:
    """
    Assert the lender is as before the refused notch: English selected, active, claimed and routed; the broken
    version parked and unchecked.

    Args:
        world: The handles.
        broken_id: The refused version's spell_id.
    """
    english = world.book.find_spell_by_spell_id(world.english_id)
    assert world.index.selected_spell_id == world.english_id
    assert world.index.spells_in_index() >= {world.english_id, broken_id}
    assert world.frame_claim(english.key) == world.english_id
    # The Book's address lookup and active map are the structure a meld by address reads.
    assert world.book._lookup_spells[english.key] is world.index
    assert world.english_id in world.book._spells_by_id
    assert broken_id in world.book._inactive_spells
    assert world.book.find_spell_by_spell_id(broken_id).validation_result_phase4 is None
    assert isinstance(world.lender.meld(spellframe=Greeter, binding_name="greeter"), English)
    assert isinstance(world.lender.meld(spell_id=world.english_id), English)
    with pytest.raises(KeyError):
        world.lender.meld(spell_id=broken_id)


def test_a_notch_refused_at_commit_leaves_the_old_version_active() -> None:
    """
    Regression (probe N2): the lender used to select the broken version after the error.

    Contract:
        - The index selects English, English is active and holds its claim and address, SelfMade is parked with no
          Phase-4 result, and English melds by address and by spell_id.
    """
    with _world("refused_old_version") as world:
        broken_id = world.stage(SelfMade)

        _refused_notch(world, broken_id)

        _assert_english_stands(world, broken_id)


def test_a_notch_refused_at_commit_says_it_did_not_happen() -> None:
    """The error's first line says the notch did not happen and names the version still active; the report follows."""
    with _world("refused_message") as world:
        broken_id = world.stage(SelfMade)

        error = _refused_notch(world, broken_id)

        lines = str(error).splitlines()
        assert lines[0] == (
            f"notch_spell refused: 'SelfMade' (spell_id {broken_id}) failed its structural check, so the notch did "
            f"not happen; 'English' (spell_id {world.english_id}) is still the active version of the index."
        )
        assert lines[1] == "Spellbook validation failed. Broken spells: SelfMade."
        assert "[SELF_DEPENDENCY]" in str(error)
        assert isinstance(error.__cause__, SpellbookValidationError)


def test_a_refused_notch_is_checked_again_when_retried() -> None:
    """A retry of the refused notch runs the check again and is refused again; the lender stays on English."""
    with _world("refused_retry") as world:
        broken_id = world.stage(SelfMade)

        _refused_notch(world, broken_id)
        _refused_notch(world, broken_id)

        _assert_english_stands(world, broken_id)


def test_a_version_cannot_be_staged_at_another_address_of_the_index() -> None:
    """
    The case a refused notch once had to undo at another address - a version staged there, whose frame claim the
    switch took (fixed in 0.2.8262) - cannot arise: every version of an index is bound the way its first version was
    (2026-10-25), so the staging is refused before anything is registered or claimed.

    Contract:
        - `bind_inactive` under another binding name raises ValueError naming both bindings; that address stays
          unclaimed and unrouted.
        - Nothing of SelfMade stays registered, so staging it under the index's binding is admitted (no spell_id
          collision); a notch to it is then refused with nothing moved, and English keeps its claim.
    """
    with _world("refused_other_address") as world:
        other_key = ("greeter", "greeter_v2")
        with pytest.raises(ValueError, match="keeps the binding its first version was bound with"):
            world.stage(SelfMade, binding_name="greeter_v2")
        assert world.frame_claim(other_key) is None
        assert other_key not in world.book._lookup_spells

        broken_id = world.stage(SelfMade)
        _refused_notch(world, broken_id)

        assert world.frame_claim(other_key) is None
        _assert_english_stands(world, broken_id)


def test_a_notch_refused_at_commit_leaves_borrowers_on_the_lenders_version() -> None:
    """
    Regression (probe N2): the borrower kept English while the lender selected SelfMade.

    Contract:
        - The borrower's copies are as before (English active, SelfMade parked), its consumer melds English, and the
          lender is on English too.
    """
    with _world("refused_borrower", borrower=True) as world:
        broken_id = world.stage(SelfMade)
        before = world.borrower_copies()

        _refused_notch(world, broken_id)

        assert world.borrower_copies() == before == ({world.english_id}, {broken_id})
        assert world.borrower is not None
        assert isinstance(world.borrower.meld(spell_id=world.speaker_id).greeter, English)
        _assert_english_stands(world, broken_id)


def test_a_notch_refused_for_an_ambiguous_provider_leaves_the_old_version_active() -> None:
    """
    Regression: the half-switch is not about recursion. TimedGreeter needs a Clock and two are registered, so its
    check fails with AMBIGUOUS_PROVIDER, and the lender then selected TimedGreeter and could not meld English.

    Contract:
        - The refusal names the real reason ([AMBIGUOUS_PROVIDER]); afterwards the index selects English, English
          is active and holds its claim and address, TimedGreeter is parked with no Phase-4 result, and English
          melds by address and by spell_id.
    """
    with _world("refused_ambiguous", clocks=True) as world:
        broken_id = world.stage(TimedGreeter)

        error = _refused_notch(world, broken_id)

        assert "[AMBIGUOUS_PROVIDER]" in str(error)
        _assert_english_stands(world, broken_id)


def test_a_notch_refused_for_an_ambiguous_provider_leaves_borrowers_on_the_lenders_version() -> None:
    """
    Regression: the borrower's consumer of the index (`Speaker`) was refused at its meld after the refused notch,
    while the borrower still held English active.

    Contract:
        - The borrower's copies are as before (English active, TimedGreeter parked), its consumer melds English and
          greets "hello", and the lender is on English too.
    """
    with _world("refused_ambiguous_borrower", borrower=True, clocks=True) as world:
        broken_id = world.stage(TimedGreeter)
        before = world.borrower_copies()

        _refused_notch(world, broken_id)

        assert world.borrower_copies() == before == ({world.english_id}, {broken_id})
        assert world.borrower is not None
        assert world.borrower.meld(spell_id=world.speaker_id).greeter.greet() == "hello"
        _assert_english_stands(world, broken_id)


def test_a_notch_back_after_a_refusal_changes_nothing() -> None:
    """Probe N3: after the refusal English is active, so a notch to it is a no-op on both sides."""
    with _world("refused_notch_back", borrower=True) as world:
        broken_id = world.stage(SelfMade)
        _refused_notch(world, broken_id)

        result = world.lender.notch_spell(spell_index=world.index, spell_id=world.english_id)

        assert result.spell_id == world.english_id
        assert world.borrower_copies() == ({world.english_id}, {broken_id})
        _assert_english_stands(world, broken_id)


def test_a_sound_notch_after_a_refusal_moves_owner_and_borrower() -> None:
    """Probe N1 after a refusal: a sound version notched in is followed by the borrower, as always."""
    with _world("refused_then_sound", borrower=True) as world:
        broken_id = world.stage(SelfMade)
        french_id = world.stage(French)
        _refused_notch(world, broken_id)

        world.lender.notch_spell(spell_index=world.index, spell_id=french_id)

        assert world.index.selected_spell_id == french_id
        assert isinstance(world.lender.meld(spellframe=Greeter, binding_name="greeter"), French)
        active, parked = world.borrower_copies()
        assert active == {french_id}
        assert parked == {world.english_id, broken_id}


def test_a_refused_notch_leaves_the_nexus_record_on_the_old_version() -> None:
    """On a frame that publishes into Nexus, the refusal leaves English's record published and none for SelfMade."""
    with _world("refused_nexus", rift_enabled=True) as world:
        broken_id = world.stage(SelfMade)
        assert (world.book.id, world.english_id) in world.nexus_spell_records()

        _refused_notch(world, broken_id)

        records = world.nexus_spell_records()
        assert (world.book.id, world.english_id) in records
        assert (world.book.id, broken_id) not in records


def test_a_refused_activation_of_a_minted_index_leaves_it_parked_and_unregistered() -> None:
    """
    A version split into its own index (`remove_from_spell_index`) has no active version; activating it takes a
    notch. Refused, it stays parked, its index is not tracked, published or claimed.

    The split version keeps its binding, English's, so its index goes active only once English no longer holds the
    address (2026-10-25): the first notch is refused for the address with nothing moved, and the structural refusal
    comes once English is disposed.
    """
    with _world("refused_minted", rift_enabled=True) as world:
        broken_id = world.stage(SelfMade)
        world.lender.remove_from_spell_index(spell_id=broken_id, source_index=world.index)
        minted = world.book.find_spell_by_spell_id(broken_id).spell_index
        broken_key = world.book.find_spell_by_spell_id(broken_id).key
        assert minted is not world.index
        assert world.book._spell_system_states.get_by_index_id(minted.id) is None
        with pytest.raises(RuntimeError, match=f"is held by spell_id '{world.english_id}'"):
            world.lender.notch_spell(spell_index=minted, spell_id=broken_id)
        assert world.frame_claim(broken_key) == world.english_id
        assert isinstance(world.lender.meld(spellframe=Greeter, binding_name="greeter"), English)
        world.lender.cleanup_spell(spell=world.book.find_spell_by_spell_id(world.english_id))

        _refused_notch(world, broken_id, index=minted)

        assert minted.selected_spell_id == broken_id
        assert minted not in world.book._spells
        assert broken_id in world.book._inactive_spells
        assert world.book._spell_system_states.get_by_index_id(minted.id) is None
        assert world.book.find_spell_by_spell_id(broken_id).validation_result_phase4 is None
        assert world.frame_claim(broken_key) is None
        assert broken_key not in world.book._lookup_spells
        assert (world.book.id, broken_id) not in world.nexus_spell_records()


def test_after_a_refusal_the_book_flag_falls_once_english_melds() -> None:
    """The refusal leaves English gated like any notch back; one meld recompiles it and the Book flag falls."""
    with _world("refused_flag") as world:
        broken_id = world.stage(SelfMade)
        _refused_notch(world, broken_id)

        world.lender.meld(spell_id=world.english_id)

        assert world.book._spellbook_validation_required is False


def _research_acts(spell_id: str) -> List[str]:
    """
    The acts the default research set journaled for `spell_id`.

    Args:
        spell_id: A version's spell_id.

    Returns:
        List[str]: The journaled acts, oldest first.
    """
    history = Aether().mutation_research.research_set().history(spell_id)
    return [entry["act"] for entry in history["transitions"]]


@contextlib.contextmanager
def _research_active() -> Iterator[Any]:
    """
    MutationResearch activated for one test.

    Yields:
        Any: The hosted MutationResearch root.
    """
    root = Aether().mutation_research
    root.configure(root.create_configuration().with_defaults().activate())
    root.activate(hydrate_from_record=False)
    try:
        yield root
    finally:
        root.deactivate()


def test_a_refused_notch_journals_no_promotion() -> None:
    """
    Regression: the research journal kept a promotion of SelfMade although the notch raised.

    Contract:
        - With MutationResearch active, neither version's history gains an act from the refused notch.
    """
    with _research_active():
        with _world("refused_journal") as world:
            broken_id = world.stage(SelfMade)
            before = (_research_acts(broken_id), _research_acts(world.english_id))

            _refused_notch(world, broken_id)

            assert (_research_acts(broken_id), _research_acts(world.english_id)) == before


def test_a_standing_notch_journals_its_promotion_once() -> None:
    """Control: a sound notch journals one promotion for the incoming version, after its check passed."""
    with _research_active():
        with _world("standing_journal") as world:
            french_id = world.stage(French)
            before = _research_acts(french_id)

            world.lender.notch_spell(spell_index=world.index, spell_id=french_id)

            assert _research_acts(french_id) == before + ["promoted"]
