"""
Component tests: the notch seam checks its incoming version before anything moves.

WHY THIS EXISTS. TASK-2026-10-16-notch_seam_checks_incoming_before_parking (GitHub #254), on the owner's word of
2026-11-08. `Spellbook._apply_notch` parked the index's outgoing version, and cleaned its creation context, before
`_reactivate_owned_spell` checked that the incoming version was parked in the Book. `Conduit.notch_spell` checks its
target before the notch transaction and again inside the held window (0.2.8249), but `cleanup_spell` takes no
transaction, so a disposal of the target can land between that check and the seam's Book lock: the seam then raised
"Owned spell_id not parked for reactivation" with the outgoing version already parked, and the index had no active
version until a notch back. A version parked in another index of the Book passed the old check and was promoted
under the wrong index. Since 0.2.8285 the seam refuses both before its address claim or anything else moves.

Each test runs in a fresh Aether with its own dynamic frame and caching off, and asserts through public calls and the
frame's claim surface; the second test hands the seam its target directly, as an internal caller would.
"""
from typing import Any, Callable, Dict, Protocol, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spellbook import Spellbook


class Greeter(Protocol):
    """The contract every greeter version implements."""

    def greet(self) -> str:
        """Return a greeting."""
        ...


class EnglishGreeter:
    """Version 1 of the greeter index."""

    def greet(self) -> str:
        """Return the English greeting."""
        return "hello"


class FrenchGreeter:
    """Version 2 of the greeter index."""

    def greet(self) -> str:
        """Return the French greeting."""
        return "bonjour"


@pytest.fixture(autouse=True)
def reset_aether_for_notch_seam() -> Any:
    """
    Purpose:
        Give each test a clean Aether singleton and frame registry.

    Contract:
        - Resets before and after, so no frame claim or Book leaks between tests.

    Returns:
        Any: The generator pytest drives (yields None).
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _greeter_world(frame_name: str) -> Tuple[Spellbook, Conduit, Spell, str]:
    """
    Purpose:
        EnglishGreeter active under (Greeter, 'english') in a conjured dynamic Book, FrenchGreeter staged on its index.

    Args:
        frame_name (str): The frame the Book lives on.

    Returns:
        Tuple[Spellbook, Conduit, Spell, str]: The Book, its root conduit, the active English version and French's
            spell_id.
    """
    book = Spellbook(aetheric_frame=frame_name, configuration=SpellbookConfiguration(frame_name).with_defaults())
    book.configure_aether_frame(
        system_state="dynamic",
        disposal=None,
        disposal_method_names=None,
        system_caching_enabled=False,
    )
    english_id = book.bind(spell=EnglishGreeter, spellframe=Greeter, binding_name="english", existence=Existence.many)
    root = book.conjure(dynamic=True, name=f"{frame_name}-root")
    english = book.find_spell_by_spell_id(english_id)
    assert english is not None
    french_id = root.bind_inactive(
        spell=FrenchGreeter, spell_index=english.spell_index, spellframe=Greeter, binding_name="english",
        existence=Existence.many,
    )
    return book, root, english, french_id


def _assert_english_still_serves(book: Spellbook, root: Conduit, english: Spell) -> None:
    """
    Purpose:
        Assert nothing moved on English's index: it selects English, English holds the frame claim of the
        index's address, and a meld by that address builds English.

    Args:
        book (Spellbook): The Book that owns the index.
        root (Conduit): Its root conduit.
        english (Spell): The version that must still be active.

    Returns:
        None.
    """
    index = english.spell_index
    assert index.selected_spell_id == english.spell_id
    assert root.get_spell_by_index_id(index.id) is english
    assert book._aetheric_frame.get_lookup(english._key) == english.spell_id
    assert root.meld(spellframe=Greeter, binding_name="english").greet() == "hello"


def test_notch_whose_target_is_disposed_after_the_conduits_check_keeps_the_active_version(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        A notch whose target is disposed between the conduit's in-window check and the seam is refused, and the
        index keeps its active version - the race `cleanup_spell`, which takes no transaction, can open.

    Contract:
        - `Conduit.notch_spell` raises RuntimeError naming the disposed spell_id and the version still active.
        - Nothing moved: English is selected, holds the frame claim and serves a meld by address.
        - Before the fix the seam parked English first and then raised "Owned spell_id not parked for
          reactivation", leaving the index with no active version.

    Returns:
        None.
    """
    book, root, english, french_id = _greeter_world("seam-race")
    french = book.find_spell_by_spell_id(french_id)
    assert french is not None
    seam: Callable[..., Spell] = Spellbook._apply_notch

    def _dispose_then_notch(self: Spellbook, **kwargs: Any) -> Spell:
        """Dispose the target where the race lands it: after the conduit's in-window check, before the seam."""
        monkeypatch.setattr(Spellbook, "_apply_notch", seam)
        root.cleanup_spell(spell=french)
        return seam(self, **kwargs)

    monkeypatch.setattr(Spellbook, "_apply_notch", _dispose_then_notch)

    with pytest.raises(RuntimeError, match=f"spell_id '{french_id}' is not a version parked in this Spellbook") as e:
        root.notch_spell(spell_index=english.spell_index, spell_id=french_id)

    assert f"'EnglishGreeter' (spell_id {english.spell_id}) is still the active version of the index" in str(e.value)
    assert book.find_spell_by_spell_id(french_id) is None
    _assert_english_still_serves(book, root, english)


def test_notch_landing_while_cleanup_spell_disposes_its_target_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Purpose:
        A notch that lands while `cleanup_spell` is disposing its target - after the disposal's decision, before the
        version leaves the Book - is refused, and the disposal completes.

    Contract:
        - `cleanup_spell` decides under the Book lock, then releases the version from the root ward's contracts with
          no Book lock held; a notch run in that window (driven here from the release itself) raises RuntimeError
          saying the version is being disposed, and nothing moves.
        - The disposal completes: the version is gone; English is still selected, holds the frame claim and serves a
          meld by address.
        - Before the fix the seam found the version still parked and promoted it; the disposal then removed and
          cleaned the version the index selected.

    Returns:
        None.
    """
    book, root, english, french_id = _greeter_world("seam-disposing")
    french = book.find_spell_by_spell_id(french_id)
    assert french is not None
    ward_type = type(root._conduit_ward)
    release: Callable[..., None] = ward_type._emit_spell_disposed
    outcome: Dict[str, str] = {}

    def _notch_during_release(self: Any, *args: Any, **kwargs: Any) -> None:
        """Notch to the version while its disposal releases it from the contracts, then let the release run."""
        try:
            root.notch_spell(spell_index=english.spell_index, spell_id=french_id)
            outcome["notch"] = "stood"
        except RuntimeError as error:
            outcome["notch"] = str(error)
        release(self, *args, **kwargs)

    monkeypatch.setattr(ward_type, "_emit_spell_disposed", _notch_during_release)

    root.cleanup_spell(spell=french)

    assert f"'FrenchGreeter' (spell_id {french_id}) is being disposed by cleanup_spell" in outcome["notch"]
    assert book.find_spell_by_spell_id(french_id) is None
    _assert_english_still_serves(book, root, english)


def test_notch_seam_refuses_a_version_parked_in_another_index_and_moves_nothing() -> None:
    """
    Purpose:
        The seam refuses a version parked in another index of the Book before anything moves.

    Contract:
        - French, split off English's index into one of its own, handed to the seam for English's index, raises
          RuntimeError naming both indexes; French stays parked and selected by its own index.
        - Nothing moved on English's index: English is selected, holds the frame claim and serves a meld.
        - Before the fix French passed the seam's check and English's index selected it.

    Returns:
        None.
    """
    book, root, english, french_id = _greeter_world("seam-index")
    index = english.spell_index
    root.remove_from_spell_index(spell_id=french_id, source_index=index)
    french = book.find_spell_by_spell_id(french_id)
    assert french is not None
    french_index = french.spell_index
    assert french_index is not index

    with pytest.raises(RuntimeError, match=f"is parked in SpellIndex {french_index.id}, not in SpellIndex {index.id}"):
        book._apply_notch(spell_index=index, spell=french)

    assert french_index.selected_spell_id == french_id
    assert book._spells.get(french_index) is None
    _assert_english_still_serves(book, root, english)


def test_notch_still_moves_the_index_to_a_version_parked_on_it() -> None:
    """
    Purpose:
        Control: the seam's new check admits a version staged on the index, and the notch stands.

    Contract:
        - `Conduit.notch_spell` to French makes it the index's active version; a meld by address builds French.

    Returns:
        None.
    """
    book, root, english, french_id = _greeter_world("seam-control")
    index = english.spell_index

    root.notch_spell(spell_index=index, spell_id=french_id)

    assert index.selected_spell_id == french_id
    assert root.get_spell_by_index_id(index.id) is book.find_spell_by_spell_id(french_id)
    assert root.meld(spellframe=Greeter, binding_name="english").greet() == "bonjour"
