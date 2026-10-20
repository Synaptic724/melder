"""
Component tests: staging, moving or disposing a parked version keeps every other spell's binding signature.

WHY THIS EXISTS. STORY-2026-10-17-staged_version_releases_active_signature (EPIC-2026-10-17-correctness_defects,
sweep A1). `Spellbook._destroy_spell_index` destroys an index that a parked version left empty - the throwaway index
Bind mints for every `bind_inactive`, a source index `add_to_spell_index` empties, or the index a lone parked
version is disposed out of. Until 0.2.8263 it popped the Book's address route for the parked version's binding key
and released the frame's claim on that key by key, whoever held them. A parked version shares its key with the
active version it was staged beside, so the active version lost its claim and its route while it still served:
a meld by address raised KeyError, `find_spell_index` raised, and another Book could bind the signature. The seam
now drops the route only when it routes the key to the destroyed index and releases only the claim the departing
version holds (by spell_id), as `cleanup_and_remove_spell` already did.

Each test runs in a fresh Aether with its own dynamic frame and caching off, and asserts through the frame's claim
surface, the Book's address lookups and a meld by address - the answers an agent's calls get.
"""

from typing import Any, Optional, Protocol, Tuple

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
    """Version 1, bound active."""

    def greet(self) -> str:
        """Return the English greeting."""
        return "hello"


class FrenchGreeter:
    """Version 2, staged parked on the English version's index."""

    def greet(self) -> str:
        """Return the French greeting."""
        return "bonjour"


class SpanishGreeter:
    """Another Book's spell, bound active."""

    def greet(self) -> str:
        """Return the Spanish greeting."""
        return "hola"


class ItalianGreeter:
    """A third party trying to take a signature."""

    def greet(self) -> str:
        """Return the Italian greeting."""
        return "ciao"


@pytest.fixture(autouse=True)
def reset_aether_for_signature_claims() -> Any:
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


def _book(frame_name: str) -> Spellbook:
    """
    Purpose:
        Build a Spellbook on `frame_name` with its own default configuration.

    Args:
        frame_name (str): The aetheric frame the Spellbook belongs to.

    Returns:
        Spellbook: An unconjured Spellbook.
    """
    return Spellbook(aetheric_frame=frame_name, configuration=SpellbookConfiguration(frame_name).with_defaults())


def _settle_dynamic(spellbook: Spellbook) -> None:
    """
    Purpose:
        Settle the Spellbook's frame dynamic with caching off, so staging and index moves are allowed.

    Args:
        spellbook (Spellbook): A Spellbook whose frame is not yet settled.

    Returns:
        None.
    """
    spellbook.configure_aether_frame(
        system_state="dynamic",
        disposal=None,
        disposal_method_names=None,
        system_caching_enabled=False,
    )


def _bind(spellbook: Spellbook, cls: type, binding_name: str) -> str:
    """
    Purpose:
        Bind `cls` active under (Greeter, `binding_name`) as `many`.

    Args:
        spellbook (Spellbook): The Book to bind into.
        cls (type): The class to bind.
        binding_name (str): The binding name of the signature.

    Returns:
        str: The spell_id `bind` returned.
    """
    return spellbook.bind(
        spell=cls,
        spellframe=Greeter,
        binding_name=binding_name,
        existence=Existence.many,
        permissions="create",
    )


def _stage(owner: Any, cls: type, binding_name: str, spell_index: Any) -> str:
    """
    Purpose:
        Stage `cls` parked under (Greeter, `binding_name`) on `spell_index` through `owner`.

    Args:
        owner (Any): A Conduit or a Spellbook; both expose `bind_inactive`.
        cls (type): The class to stage.
        binding_name (str): The binding name of the signature.
        spell_index (Any): The owned SpellIndex the version joins.

    Returns:
        str: The spell_id `bind_inactive` returned.
    """
    return owner.bind_inactive(
        spell=cls,
        spell_index=spell_index,
        spellframe=Greeter,
        binding_name=binding_name,
        existence=Existence.many,
        permissions="create",
    )


def _english_world(frame_name: str) -> Tuple[Spellbook, Spellbook, Conduit, Spell]:
    """
    Purpose:
        English active on its index in a conjured dynamic Book, plus a second, unconjured Book on the same frame.

    Args:
        frame_name (str): The frame both Books live on.

    Returns:
        Tuple[Spellbook, Spellbook, Conduit, Spell]: The lender Book, the other Book, the lender's root conduit and
            the active English version.
    """
    lender_book = _book(frame_name)
    _settle_dynamic(lender_book)
    other_book = _book(frame_name)
    english_id = _bind(lender_book, EnglishGreeter, "greeter")
    lender = lender_book.conjure(dynamic=True, name=f"{frame_name}-lender")
    english = lender_book.find_spell_by_spell_id(english_id)
    assert english is not None
    return lender_book, other_book, lender, english


def _assert_english_keeps_its_signature(lender_book: Spellbook, lender: Conduit, english: Spell) -> None:
    """
    Purpose:
        Assert the active English version still holds its frame claim and its Book route, and that the agent's
        address lookups answer it.

    Args:
        lender_book (Spellbook): The Book that owns English.
        lender (Conduit): The Book's root conduit.
        english (Spell): The active English version.

    Returns:
        None.

    Raises:
        AssertionError: If the claim, the route, a meld by address or `find_spell_index` no longer answers English.
    """
    key = english._key
    assert lender_book._aetheric_frame.get_lookup(key) == english.spell_id
    assert lender_book.find_spell_index(Greeter, "EnglishGreeter", "greeter") is english.spell_index
    melded = lender.meld(spellframe=Greeter, binding_name="greeter")
    assert isinstance(melded, EnglishGreeter)


def _assert_bind_of_signature_refused(other_book: Spellbook, cls: type, binding_name: str) -> None:
    """
    Purpose:
        Assert another Book of the frame cannot bind a signature an active spell holds.

    Args:
        other_book (Spellbook): A second Book on the same frame.
        cls (type): The class it tries to bind.
        binding_name (str): The binding name of the held signature.

    Returns:
        None.

    Raises:
        AssertionError: If the bind is accepted.
    """
    with pytest.raises(RuntimeError, match="Binding signature already active in this frame"):
        _bind(other_book, cls, binding_name)


def test_bind_inactive_keeps_the_active_versions_binding_signature() -> None:
    """
    Purpose:
        Staging a version keyed like the active version leaves the active version's claim and route in place.

    Contract:
        - After `Conduit.bind_inactive(FrenchGreeter)` on English's index under English's key, English still holds
          the frame claim, `find_spell_index` returns its index, a meld by address builds English, and another Book's
          bind of the signature is refused. Until 0.2.8263 the claim and the route were gone, the meld raised
          KeyError and the other Book's bind was accepted.

    Returns:
        None.
    """
    lender_book, other_book, lender, english = _english_world("s1-stage-after-conjure")

    _stage(lender, FrenchGreeter, "greeter", english.spell_index)

    _assert_english_keeps_its_signature(lender_book, lender, english)
    _assert_bind_of_signature_refused(other_book, SpanishGreeter, "greeter")


def test_bind_inactive_before_conjure_keeps_the_active_versions_binding_signature() -> None:
    """
    Purpose:
        Staging before conjure leaves the active version addressable after conjure.

    Contract:
        - `Spellbook.bind_inactive(FrenchGreeter)` before `conjure`, under English's key: after conjure English holds
          the claim and a meld by address builds it. Until 0.2.8263 the first meld by address raised KeyError.

    Returns:
        None.
    """
    lender_book = _book("s1-stage-before-conjure")
    _settle_dynamic(lender_book)
    english_id = _bind(lender_book, EnglishGreeter, "greeter")
    english: Optional[Spell] = lender_book.find_spell_by_spell_id(english_id)
    assert english is not None

    _stage(lender_book, FrenchGreeter, "greeter", english.spell_index)
    lender = lender_book.conjure(dynamic=True, name="s1-stage-before-conjure-lender")

    _assert_english_keeps_its_signature(lender_book, lender, english)


def test_index_move_back_keeps_the_active_versions_binding_signature() -> None:
    """
    Purpose:
        Moving a parked version out of the index and back leaves the active version's claim and route in place.

    Contract:
        - With French parked beside English (under English's key), `remove_from_spell_index(French)` then
          `add_to_spell_index(French)` back - which empties and destroys the index the move minted - leaves English
          holding its claim and addressable, and another Book's bind of the signature refused. Until 0.2.8263 the
          destroy released English's claim and route.

    Returns:
        None.
    """
    lender_book, other_book, lender, english = _english_world("s1-move-back")
    index = english.spell_index
    french_id = _stage(lender, FrenchGreeter, "greeter", index)

    lender.remove_from_spell_index(spell_id=french_id, source_index=index)
    lender.add_to_spell_index(spell_id=french_id, target_index=index)

    _assert_english_keeps_its_signature(lender_book, lender, english)
    _assert_bind_of_signature_refused(other_book, SpanishGreeter, "greeter")
    assert lender_book.find_spell_by_spell_id(french_id).spell_index is index


def test_cleanup_of_a_lone_parked_version_keeps_the_siblings_binding_signature() -> None:
    """
    Purpose:
        Disposing a parked version alone in its own index leaves its former sibling's claim and route in place.

    Contract:
        - French, keyed like English, is moved into an index of its own and disposed with `cleanup_spell`, which
          destroys that index: English still holds its claim, is addressable, and another Book's bind of the
          signature is refused. Until 0.2.8263 the destroy released English's claim and route.

    Returns:
        None.
    """
    lender_book, other_book, lender, english = _english_world("s1-lone-cleanup")
    index = english.spell_index
    french_id = _stage(lender, FrenchGreeter, "greeter", index)
    lender.remove_from_spell_index(spell_id=french_id, source_index=index)

    lender.cleanup_spell(spell=lender_book.find_spell_by_spell_id(french_id))

    _assert_english_keeps_its_signature(lender_book, lender, english)
    _assert_bind_of_signature_refused(other_book, SpanishGreeter, "greeter")
    assert lender_book.find_spell_by_spell_id(french_id) is None


def test_staging_does_not_release_another_books_binding_signature() -> None:
    """
    Purpose:
        Staging in one Book a version keyed like another Book's active spell leaves that spell's claim in place.

    Contract:
        - Book O binds SpanishGreeter active as (Greeter, 'spanish'); Book L stages FrenchGreeter under the same
          signature on its own index. Book O's spell still holds the claim and a third Book's bind of the signature
          is refused. Until 0.2.8263 Book L's staging released Book O's claim.

    Returns:
        None.
    """
    lender_book, other_book, lender, english = _english_world("s1-other-book")
    spanish_id = _bind(other_book, SpanishGreeter, "spanish")
    spanish = other_book.find_spell_by_spell_id(spanish_id)
    assert spanish is not None

    _stage(lender, FrenchGreeter, "spanish", english.spell_index)

    assert lender_book._aetheric_frame.get_lookup(spanish._key) == spanish_id
    _assert_bind_of_signature_refused(_book("s1-other-book"), ItalianGreeter, "spanish")
    _assert_english_keeps_its_signature(lender_book, lender, english)


def test_parked_version_staged_under_its_own_key_claims_nothing() -> None:
    """
    Purpose:
        A version staged under a key no active spell holds claims nothing, before and after the throwaway index
        Bind minted for it is destroyed.

    Contract:
        - Staging FrenchGreeter as (Greeter, 'french') on English's index leaves ('greeter', 'french') unclaimed in
          the frame and unrouted in the Book, and English's own claim in place: a parked version holds no signature.

    Returns:
        None.
    """
    lender_book, _other_book, lender, english = _english_world("s1-own-key")

    french_id = _stage(lender, FrenchGreeter, "french", english.spell_index)
    french = lender_book.find_spell_by_spell_id(french_id)
    assert french is not None
    assert lender_book._aetheric_frame.get_lookup(french._key) is None
    assert french._key not in lender_book._lookup_spells
    _assert_english_keeps_its_signature(lender_book, lender, english)
