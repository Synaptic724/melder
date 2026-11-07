"""
Component tests: a consumer waiting on a provider picks it up when the provider arrives, however the provider is bound.

EPIC-2026-10-25-dependency_watchers_listen_for_names, S1 (STORY-2026-10-25-map_dependency_watchers_and_announcers);
the owner's direction, chat 2026-11-07: "make regressions because my test suite should be catching this kinda stuff".

A consumer that compiles while nothing provides one of its parameters records that parameter as waiting - an
UNRESOLVED_INPUT socket, an OVERRIDE_REQUIRED socket whose only match is a non-resolvable definition, or an empty
`list[...]` - and is watched under the name its annotation uses: `greeter: English` is watched as "english". A later
bind, notch or contract grant marks the watchers of the provider's ADDRESS: its spellframe ("langs", "greeter"), else
its own name. Phase 3 matches by kind, not by address - a class annotation finds the class wherever it is filed - so
the two agree only where the address happens to be the annotated name: a provider bound bare, a Protocol consumer with
a provider under that Protocol, a collection by label. Everywhere else the consumer keeps the plan it compiled with
nothing to inject, on every meld, until it is disposed and bound again.

What these tests pin (cell ids of the S1 matrix probe, context_compass/artifacts/dependency_watchers_20261107/):
    - Strict xfails, OPEN until the epic's fix lands: a provider bound after conjure under a category or a Protocol
      frame, as a class or an existing object (A2, A3, A5), for a string annotation (A8, A9) and a list (B2, B3); the
      owner's original report, a notch away and back on an index under a Protocol frame (C1), and under a category
      (C2), for a list too (C4); a notch to a version staged under a category (I2); a contract grant of a provider
      under a frame (G2, G3); an override-only consumer once a real provider arrives under a category (F2).
    - Passing, and they must keep passing: the same events where the names agree (A1, A4, A6, A7, B1, B4, B5, F1, G1).

Each test proves its own world before its assertion: a late twin of the consumer - the same annotation, bound after
the event - must resolve the provider, so an xfail is always a missed notification, never a provider the consumer
cannot match. Preconditions raise RuntimeError, not AssertionError, so a strict xfail (raises=AssertionError) never
absorbs a world that was not set up as the test says. Every meld goes through the class door, `meld(Consumer)`; by
spell_id and by name a stuck consumer behaves the same.
"""

from collections.abc import Iterator
from typing import Any, Dict, List, Protocol

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook

STUCK = pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=(
        "OPEN: a consumer that compiled with nothing to inject is watched under its annotation's name, while a "
        "bind, notch or contract grant marks the watchers of the provider's address (its spellframe, else its own "
        "name), so a provider filed under a category or a Protocol never wakes it - "
        "EPIC-2026-10-25-dependency_watchers_listen_for_names. STRICT ON PURPOSE: when the fix lands this test "
        "passes, xfail(strict) turns that into a FAILURE, and whoever fixed it deletes this marker. Do NOT loosen "
        "the assertion to make it green."
    ),
)


class Greeter(Protocol):
    """The contract a provider filed under a Protocol frame is checked against."""

    def greet(self) -> str:
        """Return a greeting."""
        ...


class English:
    """The provider every consumer names."""

    def greet(self) -> str:
        """Return the English greeting."""
        return "hello"


class French:
    """The other version a notch moves to; it never matches `English`."""

    def greet(self) -> str:
        """Return the French greeting."""
        return "bonjour"


class Edited:
    """Holds a second class named `English`: another spell_id, the same type key."""

    class English:
        """An edited English: the same name, other code."""

        def greet(self) -> str:
            """Return the edited greeting."""
            return "hello again"


class ByClass:
    """Waits on `English` by class annotation."""

    def __init__(self, greeter: English) -> None:
        """Keep the injected greeter."""
        self.greeter = greeter


class LateByClass:
    """The late twin of `ByClass`: the same annotation, bound after the event."""

    def __init__(self, greeter: English) -> None:
        """Keep the injected greeter."""
        self.greeter = greeter


class ByName:
    """Waits on `English` by a string annotation, as a TYPE_CHECKING-only import leaves it."""

    def __init__(self, greeter: "English") -> None:
        """Keep the injected greeter."""
        self.greeter = greeter


class LateByName:
    """The late twin of `ByName`."""

    def __init__(self, greeter: "English") -> None:
        """Keep the injected greeter."""
        self.greeter = greeter


class ByProtocol:
    """Waits on whatever is bound under `Greeter`."""

    def __init__(self, greeter: Greeter) -> None:
        """Keep the injected greeter."""
        self.greeter = greeter


class LateByProtocol:
    """The late twin of `ByProtocol`."""

    def __init__(self, greeter: Greeter) -> None:
        """Keep the injected greeter."""
        self.greeter = greeter


class ListByClass:
    """Gathers every `English`."""

    def __init__(self, greeters: list[English]) -> None:
        """Keep the gathered greeters."""
        self.greeters = greeters


class LateListByClass:
    """The late twin of `ListByClass`."""

    def __init__(self, greeters: list[English]) -> None:
        """Keep the gathered greeters."""
        self.greeters = greeters


class ListByProtocol:
    """Gathers everything bound under `Greeter`."""

    def __init__(self, greeters: list[Greeter]) -> None:
        """Keep the gathered greeters."""
        self.greeters = greeters


class LateListByProtocol:
    """The late twin of `ListByProtocol`."""

    def __init__(self, greeters: list[Greeter]) -> None:
        """Keep the gathered greeters."""
        self.greeters = greeters


class ListByLabel:
    """Gathers the members of the category "langs"."""

    def __init__(self, greeters: list["langs"]) -> None:
        """Keep the gathered greeters."""
        self.greeters = greeters


class LateListByLabel:
    """The late twin of `ListByLabel`."""

    def __init__(self, greeters: list["langs"]) -> None:
        """Keep the gathered greeters."""
        self.greeters = greeters


SHAPES: Dict[str, Dict[str, Any]] = {
    "bare": {},
    "category": {"spellframe": "langs"},
    "protocol": {"spellframe": Greeter, "binding_name": "greeter"},
}
LATE: Dict[type, type] = {
    ByClass: LateByClass,
    ByName: LateByName,
    ByProtocol: LateByProtocol,
    ListByClass: LateListByClass,
    ListByProtocol: LateListByProtocol,
    ListByLabel: LateListByLabel,
}


def _reset_aether() -> None:
    """Install a fresh Aether singleton for Spellbook and Conduit."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def fresh_aether() -> Iterator[None]:
    """Give each test a fresh Aether and reset it again afterwards."""
    _reset_aether()
    yield
    _reset_aether()


def _book(frame: str, *, first: bool = True) -> Spellbook:
    """
    Return a Book on `frame`, not conjured.

    Args:
        frame: The frame name; each test uses its own.
        first: True for the frame's first Book, which settles the frame dynamic with creation caching off; a later
            Book of the same frame inherits that posture.

    Returns:
        Spellbook: The Book.
    """
    book = Spellbook(aetheric_frame=frame)
    if first:
        book.configure_aether_frame(system_state="dynamic", system_caching_enabled=False,
                                    disposal=None, disposal_method_names=None)
    return book


def _bind(target: Any, spell: Any, shape: str = "bare", existence: Existence = Existence.many,
          **options: Any) -> str:
    """
    Bind `spell` at the address `shape` names.

    Args:
        target: A Book before conjure, or a conduit after it.
        spell: The class or existing object to bind.
        shape: "bare", "category" ("langs") or "protocol" (`Greeter`, binding name "greeter").
        existence: The existence to bind it under.
        **options: Further bind options (`resolvable`).

    Returns:
        str: The spell_id `bind` returned.
    """
    return target.bind(spell=spell, existence=existence, permissions="create", **SHAPES[shape], **options)


def _held(root: Conduit, consumer: type) -> str:
    """
    Meld a single-socket consumer through the class door and name the greeter it was built with.

    Returns:
        str: The greeter's qualname, or "raises <Type>" for the RuntimeError (UnresolvedInputError and
        SpellbookValidationError are RuntimeErrors) or TypeError the meld raised.
    """
    try:
        return type(root.meld(consumer).greeter).__qualname__
    except (RuntimeError, TypeError) as error:
        return f"raises {type(error).__name__}"


def _gathered(root: Conduit, consumer: type) -> List[str]:
    """Meld a collection consumer through the class door and name the greeters it gathered, sorted."""
    return sorted(type(each).__qualname__ for each in root.meld(consumer).greeters)


def _given(observed: Any, expected: Any, what: str) -> None:
    """
    Check a precondition of the world under test.

    Raises:
        RuntimeError: When `observed` is not `expected` - never AssertionError, so a strict xfail cannot absorb it.
    """
    if observed != expected:
        raise RuntimeError(f"precondition failed - {what}: expected {expected!r}, got {observed!r}")


def _late_twin_resolves(root: Conduit, consumer: type, expected: Any) -> None:
    """Bind the consumer's late twin now and require it to resolve `expected`: the provider is matchable."""
    late = LATE[consumer]
    _bind(root, late)
    observed = _gathered(root, late) if consumer.__name__.startswith("List") else _held(root, late)
    _given(observed, expected, f"{late.__name__}, bound after the event")


@pytest.mark.parametrize(
    ("provider", "shape", "existence"),
    [
        pytest.param(English, "bare", Existence.many, id="A1-class-bare"),
        pytest.param(English, "category", Existence.many, id="A2-class-category", marks=STUCK),
        pytest.param(English, "protocol", Existence.many, id="A3-class-protocol", marks=STUCK),
        pytest.param(English(), "bare", Existence.unique, id="A4-object-bare"),
        pytest.param(English(), "category", Existence.unique, id="A5-object-category", marks=STUCK),
    ],
)
def test_waiting_consumer_picks_up_a_provider_bound_after_conjure(provider: Any, shape: str,
                                                                 existence: Existence) -> None:
    """
    A1-A5: `ByClass` compiled with no `English` bound; `English`, a class or an existing object, arrives by `bind`.

    Contract: before the bind the meld raises UnresolvedInputError; after it the meld builds `ByClass` with the
        English just bound, wherever that English is filed.
    """
    book = _book(f"arrival-{shape}-{existence.name}")
    _bind(book, ByClass)
    root = book.conjure(dynamic=True, name="root")
    _given(_held(root, ByClass), "raises UnresolvedInputError", "ByClass before English is bound")
    _bind(root, provider, shape, existence)
    _late_twin_resolves(root, ByClass, "English")
    held = _held(root, ByClass)
    assert held == "English", f"ByClass melds {held} although English is live at the {shape} address"


@pytest.mark.parametrize(
    "shape",
    [
        pytest.param("bare", id="A7-name-bare"),
        pytest.param("category", id="A8-name-category", marks=STUCK),
        pytest.param("protocol", id="A9-name-protocol", marks=STUCK),
    ],
)
def test_consumer_waiting_by_name_picks_up_a_provider_bound_after_conjure(shape: str) -> None:
    """
    A7-A9: `ByName` (annotation "English", a string) compiled with no `English` bound; `English` arrives by `bind`.

    Contract: the string selects the type by name, as the class does, so the meld builds `ByName` with the English
        just bound, wherever it is filed.
    """
    book = _book(f"name-{shape}")
    _bind(book, ByName)
    root = book.conjure(dynamic=True, name="root")
    _given(_held(root, ByName), "raises UnresolvedInputError", "ByName before English is bound")
    _bind(root, English, shape)
    _late_twin_resolves(root, ByName, "English")
    held = _held(root, ByName)
    assert held == "English", f"ByName melds {held} although English is live at the {shape} address"


def test_protocol_consumer_picks_up_a_provider_bound_under_its_protocol_after_conjure() -> None:
    """
    A6: `ByProtocol` compiled with nothing under `Greeter`; `English` arrives under `Greeter`.

    Contract: the watcher ("greeter") and the provider's address ("greeter") agree, so the meld builds `ByProtocol`
        with English. Passing today; it must keep passing.
    """
    book = _book("protocol-consumer")
    _bind(book, ByProtocol)
    root = book.conjure(dynamic=True, name="root")
    _given(_held(root, ByProtocol), "raises UnresolvedInputError", "ByProtocol before English is bound")
    _bind(root, English, "protocol")
    _late_twin_resolves(root, ByProtocol, "English")
    assert _held(root, ByProtocol) == "English"


@pytest.mark.parametrize(
    ("consumer", "shape"),
    [
        pytest.param(ListByClass, "bare", id="B1-list-class-bare"),
        pytest.param(ListByClass, "category", id="B2-list-class-category", marks=STUCK),
        pytest.param(ListByClass, "protocol", id="B3-list-class-protocol", marks=STUCK),
        pytest.param(ListByProtocol, "protocol", id="B4-list-protocol-protocol"),
        pytest.param(ListByLabel, "category", id="B5-list-label-category"),
    ],
)
def test_waiting_list_gathers_a_provider_bound_after_conjure(consumer: type, shape: str) -> None:
    """
    B1-B5: a collection consumer compiled with nothing to gather; `English` arrives by `bind`.

    Contract: before the bind the meld gathers nothing; after it the list holds the English just bound when the
        annotation matches it - a class list by type, a Protocol list by contract, a label list by category.
    """
    book = _book(f"list-{consumer.__name__}-{shape}")
    _bind(book, consumer)
    root = book.conjure(dynamic=True, name="root")
    _given(_gathered(root, consumer), [], f"{consumer.__name__} before English is bound")
    _bind(root, English, shape)
    _late_twin_resolves(root, consumer, ["English"])
    gathered = _gathered(root, consumer)
    assert gathered == ["English"], f"{consumer.__name__} gathers {gathered} although English is live at {shape}"


@pytest.mark.parametrize(
    "shape",
    [
        pytest.param("protocol", id="C1-protocol-index", marks=STUCK),
        pytest.param("category", id="C2-category-index", marks=STUCK),
    ],
)
def test_waiting_consumer_follows_a_notch_back_to_its_provider(shape: str) -> None:
    """
    C1 (the owner's original report), C2: `ByClass` melds English, loses it when the index is notched to French
        and must get it back when the index is notched back to English.

    Contract: with French active the meld raises UnresolvedInputError (correct: nothing provides English); after
        the notch back it builds `ByClass` with English again.
    """
    frame = f"notch-back-{shape}"
    book = _book(frame)
    english_id = _bind(book, English, shape)
    _bind(book, ByClass)
    root = book.conjure(dynamic=True, name="root")
    index = root.get_spell_by_spell_id(english_id, frame).spell_index
    french_id = root.bind_inactive(spell=French, spell_index=index, existence=Existence.many,
                                   permissions="create", **SHAPES[shape])
    _given(_held(root, ByClass), "English", "ByClass with English active")
    root.notch_spell(spell_index=index, spell_id=french_id)
    _given(_held(root, ByClass), "raises UnresolvedInputError", "ByClass with French active")
    root.notch_spell(spell_index=index, spell_id=english_id)
    _late_twin_resolves(root, ByClass, "English")
    held = _held(root, ByClass)
    assert held == "English", f"ByClass melds {held} after the notch back to English at the {shape} address"


@STUCK
def test_waiting_list_follows_a_notch_back_to_its_provider() -> None:
    """
    C4: `ListByClass` gathers English, gathers nothing once the "langs" index is notched to French, and must
        gather English again after the notch back.
    """
    frame = "list-notch-back"
    book = _book(frame)
    english_id = _bind(book, English, "category")
    _bind(book, ListByClass)
    root = book.conjure(dynamic=True, name="root")
    index = root.get_spell_by_spell_id(english_id, frame).spell_index
    french_id = root.bind_inactive(spell=French, spell_index=index, existence=Existence.many,
                                   permissions="create", spellframe="langs")
    _given(_gathered(root, ListByClass), ["English"], "ListByClass with English active")
    root.notch_spell(spell_index=index, spell_id=french_id)
    _given(_gathered(root, ListByClass), [], "ListByClass with French active")
    root.notch_spell(spell_index=index, spell_id=english_id)
    _late_twin_resolves(root, ListByClass, ["English"])
    gathered = _gathered(root, ListByClass)
    assert gathered == ["English"], f"ListByClass gathers {gathered} after the notch back to English"


@STUCK
def test_waiting_consumer_picks_up_a_version_notched_in_under_a_category() -> None:
    """
    I2: French is active under "langs" and `ByClass` waits for English; English is staged on that index with
        `bind_inactive` and notched in.

    Contract: staging alone changes nothing (a parked version is not resolvable); after the notch the meld builds
        `ByClass` with English.
    """
    frame = "notch-in"
    book = _book(frame)
    french_id = _bind(book, French, "category")
    _bind(book, ByClass)
    root = book.conjure(dynamic=True, name="root")
    index = root.get_spell_by_spell_id(french_id, frame).spell_index
    english_id = root.bind_inactive(spell=English, spell_index=index, existence=Existence.many,
                                    permissions="create", spellframe="langs")
    _given(_held(root, ByClass), "raises UnresolvedInputError", "ByClass with English parked")
    root.notch_spell(spell_index=index, spell_id=english_id)
    _late_twin_resolves(root, ByClass, "English")
    held = _held(root, ByClass)
    assert held == "English", f"ByClass melds {held} after English was notched in under 'langs'"


@pytest.mark.parametrize(
    ("definition", "consumer", "provider", "shape", "expected"),
    [
        pytest.param(Greeter, ByProtocol, English, "protocol", "English", id="F1-protocol-definition"),
        pytest.param(English, ByClass, Edited.English, "category", "Edited.English", id="F2-class-definition",
                     marks=STUCK),
    ],
)
def test_override_only_consumer_uses_a_real_provider_once_one_arrives(definition: type, consumer: type,
                                                                     provider: type, shape: str,
                                                                     expected: str) -> None:
    """
    F1, F2: the consumer's only match is a definition bound resolvable=False, so it compiled an OVERRIDE_REQUIRED
        socket; then a real provider of that type arrives by `bind`.

    Contract: without an override the meld fails while only the definition matches (the constructor misses its
        argument); once a resolvable provider is bound the meld builds the consumer with it.
    """
    book = _book(f"override-{consumer.__name__}")
    _bind(book, definition, resolvable=False)
    _bind(book, consumer)
    root = book.conjure(dynamic=True, name="root")
    _given(_held(root, consumer), "raises TypeError", f"{consumer.__name__} with only the definition bound")
    _bind(root, provider, shape)
    _late_twin_resolves(root, consumer, expected)
    held = _held(root, consumer)
    assert held == expected, f"{consumer.__name__} melds {held} although {expected} is live at the {shape} address"


@pytest.mark.parametrize(
    "shape",
    [
        pytest.param("bare", id="G1-bare"),
        pytest.param("protocol", id="G2-protocol", marks=STUCK),
        pytest.param("category", id="G3-category", marks=STUCK),
    ],
)
def test_waiting_borrower_picks_up_a_provider_granted_by_contract(shape: str) -> None:
    """
    G1-G3: `ByClass` waits in a borrower root; the owner root's English is granted to it by link and
        `add_spell_to_contract`.

    Contract: after the grant the borrower's meld builds `ByClass` with the borrowed English, wherever the owner
        filed it.
    """
    frame = f"grant-{shape}"
    owner_book = _book(frame)
    english_id = _bind(owner_book, English, shape)
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower_book = _book(frame, first=False)
    _bind(borrower_book, ByClass)
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    _given(_held(borrower, ByClass), "raises UnresolvedInputError", "ByClass in the borrower before the grant")
    _given(owner.link(borrower), True, "owner.link(borrower)")
    _given(borrower.add_spell_to_contract(spell_id=english_id, conduit=owner, permissions="create"), True,
           "the grant of English")
    _late_twin_resolves(borrower, ByClass, "English")
    held = _held(borrower, ByClass)
    assert held == "English", f"the borrower's ByClass melds {held} although English is granted ({shape})"
