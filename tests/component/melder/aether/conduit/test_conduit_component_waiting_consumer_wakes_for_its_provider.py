"""
Component tests: a consumer waiting on a provider picks it up when a provider it matches arrives; a class or name
consumer matches no provider bound under a frame, so it is refused - HIDDEN_PROVIDER, naming where its class is bound -
whether it waited or was compiled after.

EPIC-2026-10-25-dependency_watchers_listen_for_names, S1 (STORY-2026-10-25-map_dependency_watchers_and_announcers);
the owner's direction, chat 2026-11-07: "make regressions because my test suite should be catching this kinda stuff".
The key-split cells were rewritten to the class-lookup rule of EPIC-2026-11-07-spellframe_hides_the_concrete_class
(TASK-2026-11-07-class_annotation_selects_only_bare_spells).

A consumer that compiles while nothing provides one of its parameters records that parameter as waiting - an
UNRESOLVED_INPUT socket, an OVERRIDE_REQUIRED socket whose only match is a non-resolvable definition, or an empty
`list[...]` - and is watched under the name its annotation uses: `greeter: English` is watched as "english". A later
bind, notch or contract grant marks the watchers of the provider's ADDRESS: its spellframe ("langs", "greeter"), else
its own name. Until 2026-11-07 Phase 3 matched by kind, not by address - a class annotation found the class wherever
it was filed - so the two agreed only where the address happened to be the annotated name: a provider bound bare, a
Protocol consumer with a provider under that Protocol, a collection by label. Everywhere else the consumer kept the
plan it compiled with nothing to inject, on every meld, until it was disposed and bound again, while the same
annotation compiled after the event resolved the provider: the key split.

The owner's ruling of 2026-11-07 - Autofac's rule that a declared service hides the component's own type - closes
the split from the matching side. A class lookup - a class annotation, a string naming a class, `list[Class]` -
reaches only a provider bound bare, with no spellframe and the default binding, existing objects alike. A provider
filed under a frame is reached through the frame - a Protocol annotation, `list[Protocol]`, `list["label"]`, a
frame-addressed SpellMap - and the frame is the key its bind, notch or grant announces. A waiting consumer and one
compiled after the event now give one answer in every cell below.

Since patch hidden_provider_2026_11_07 (TASK-2026-11-07-spellframe_ambiguity_validation_check part (a), 0.2.8281) that
answer, where the class is bound only under a frame, is a refusal rather than an unresolved input: Phase 4 reports
HIDDEN_PROVIDER, an error naming each address the class is bound at and the lookup that reaches it. The late twin is
refused at its bind (a dynamic late bind runs phases 1-4); the bind, notch or grant that files the class under a frame
also announces the class's own name (D1 = B), so the waiting consumer is re-gated and refused at its next meld, with an
override as without one (D2). A refused consumer watches the addresses of its hidden candidates too, so a notch of
that index to a version of another class releases it into an unresolved input again (re-gate path 6b).

What these tests pin (cell ids of the S1 matrix probe, context_compass/artifacts/dependency_watchers_20261107/):
    - The key-split cells - strict xfails written for a wake-up fix until 2026-11-07, then regressions of the
      class-lookup rule: a provider bound after conjure under a category or a Protocol frame, as a class or an
      existing object (A2, A3, A5), for a string annotation (A8, A9) and a list (B2, B3); the owner's original report,
      a notch away and back on an index under a Protocol frame (C1), and under a category (C2), for a list too (C4); a
      notch to a version staged under a category (I2); a contract grant of a provider under a frame (G2, G3); an
      override-only consumer once a real provider arrives under a category (F2). Since 0.2.8281 the single class or
      name consumer is refused with HIDDEN_PROVIDER while it waits (LIVE, at its next meld) and in its late twin
      (FRESH, at its bind) - one answer, no key split - and released by a notch of the framed index to another class
      (C1, C2); a list gathers nothing (B2, B3, C4: Phase 6 names the bindings) and F2 keeps only its definition,
      which is bound bare. The frame's own consumer, bound beside it (`Greeter`, `list[Greeter]` or
      `list["langs"]`), wakes with the provider, or follows it across a notch.
    - Passing, and they must keep passing: the same events where the names agree (A1, A4, A6, A7, B1, B4, B5, F1, G1).

Each test proves its own world before its assertion: a late twin of the consumer that must wake - the same
annotation, bound after the event - must resolve the provider, so an assertion on a waiting consumer is always about a
notification, never about a provider the consumer cannot match. In the framed cells the class or name consumer's own
late twin is part of the contract: it must give the waiting consumer's answer, and a refusal is asserted as its whole
text. Preconditions raise RuntimeError, not AssertionError - written so that a strict xfail (raises=AssertionError)
never absorbed a world that was not set up as the test says; the split still tells a world that was not set up from a
contract that does not hold. Every meld goes through the class door, `meld(Consumer)`; by spell_id and by name a
consumer stuck in the key split behaved the same.
"""

from collections.abc import Iterator
from typing import Any, Callable, Dict, List, Optional, Protocol, Union

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError
from melder.utilities.custom_exceptions.unresolved_input_error import UnresolvedInputError


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
    """Gathers every `English` bound bare: `list[English]` is a class lookup, which no framed English answers."""

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
# The frame's own consumer per framed shape - how a provider filed under that frame is reached (2026-11-07): the
# label list for the category "langs"; for the Protocol frame the `Greeter` annotation, a single socket beside a single
# class consumer (FRAME_CONSUMERS) and `list[Greeter]` beside `list[English]` (FRAME_LISTS).
FRAME_CONSUMERS: Dict[str, type] = {"category": ListByLabel, "protocol": ByProtocol}
FRAME_LISTS: Dict[str, type] = {"category": ListByLabel, "protocol": ListByProtocol}
# What follows "English is bound only " in the HIDDEN_PROVIDER error per framed shape (patch
# hidden_provider_2026_11_07): where English is bound, the SpellMap that reaches it, and the ways out.
HIDDEN_AT: Dict[str, str] = {
    "category": (
        "under a spellframe: English at (spellframe='langs', binding_name=None) - use SpellMap(spellframe='langs'). "
        "Ask for it where it is bound - the SpellMap shown, as the parameter's default - or bind English bare."
    ),
    "protocol": (
        "under a spellframe: English at (spellframe='Greeter', binding_name='greeter') - use "
        "SpellMap(spellframe=Greeter, binding_name='greeter'). Ask for it where it is bound - the SpellMap shown, as "
        "the parameter's default, or a Greeter annotation while that spell is the only one bound under Greeter - or "
        "bind English bare."
    ),
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


def _melded(root: Conduit, consumer: type) -> Union[str, List[str]]:
    """
    Meld any consumer of this module through the class door and name what it was built with.

    Args:
        root: The conduit to meld in.
        consumer: A single-socket consumer, a collection consumer (its name starts with "List") or a late twin of
            either (its name starts with "Late").

    Returns:
        Union[str, List[str]]: What `_gathered` names for a collection consumer; what `_held` names otherwise.
    """
    if consumer.__name__.startswith(("List", "LateList")):
        return _gathered(root, consumer)
    return _held(root, consumer)


def _frame_holds(frame_consumer: type, member: Optional[str]) -> Union[str, List[str]]:
    """
    Name what a frame's own consumer melds while `member` is the one live provider in the frame.

    Args:
        frame_consumer: A value of FRAME_CONSUMERS or FRAME_LISTS.
        member: The qualname of the frame's live provider, or None while the frame holds none.

    Returns:
        Union[str, List[str]]: For a collection consumer `[member]`, or [] with none; for a single socket the member,
        or "raises UnresolvedInputError" with none.
    """
    if frame_consumer.__name__.startswith("List"):
        return [] if member is None else [member]
    return "raises UnresolvedInputError" if member is None else member


def _given(observed: Any, expected: Any, what: str) -> None:
    """
    Check a precondition of the world under test.

    Raises:
        RuntimeError: When `observed` is not `expected` - never AssertionError, so a strict xfail could not absorb it
            while the file held strict xfails (until 2026-11-07), and a broken world still reads apart from a broken
            contract.
    """
    if observed != expected:
        raise RuntimeError(f"precondition failed - {what}: expected {expected!r}, got {observed!r}")


def _late_twin(root: Conduit, consumer: type) -> Union[str, List[str]]:
    """
    Bind the consumer's late twin now and meld it: FRESH, the same annotation compiled after the event.

    Args:
        root: The conduit to bind and meld in.
        consumer: A key of LATE.

    Returns:
        Union[str, List[str]]: What `_melded` names for the twin.
    """
    late = LATE[consumer]
    _bind(root, late)
    return _melded(root, late)


def _late_twin_resolves(root: Conduit, consumer: type, expected: Any) -> None:
    """
    Bind the consumer's late twin now and require it to resolve `expected`: the provider is matchable.

    Args:
        root: The conduit to bind and meld in.
        consumer: A key of LATE.
        expected: What `_melded` must name for the twin: the provider's qualname, or the list of the gathered ones.

    Raises:
        RuntimeError: Through `_given`, when the twin melds anything else - the world is not the one the test set up.
    """
    _given(_late_twin(root, consumer), expected, f"{LATE[consumer].__name__}, bound after the event")


def _hidden_provider_report(consumer: str, bound_at: str) -> str:
    """
    The whole SpellbookValidationError text that refuses `consumer`'s `greeter: English` with HIDDEN_PROVIDER.

    Args:
        consumer: The refused spell's name (`ByClass`, `LateByName`, ...).
        bound_at: What follows "English is bound only " - a value of HIDDEN_AT (owned and borrowed English alike).

    Returns:
        str: The header naming the spell, its block, and its one error line with the code.
    """
    return (
        f"Spellbook validation failed. Broken spells: {consumer}.\n{consumer}:\n"
        f"  - Parameter 'greeter' on spell '{consumer}' expects English, but a class lookup reaches English only "
        f"where it is bound bare (no spellframe, the default binding), and English is bound only {bound_at} "
        "[HIDDEN_PROVIDER]"
    )


def _refusal(action: Callable[[], Any]) -> str:
    """
    Run a bind, meld or conjure that must be refused and return what it raised.

    Args:
        action: The call to run.

    Returns:
        str: The SpellbookValidationError's message; otherwise "<Type>: <message>" for the RuntimeError or TypeError
        raised instead, or "no refusal" when the call returned - so a failed assertion shows what happened.
    """
    try:
        action()
    except SpellbookValidationError as error:
        return str(error)
    except (RuntimeError, TypeError) as error:
        return f"{type(error).__name__}: {error}"
    return "no refusal"


def _unsupplied(root: Conduit, consumer: type) -> str:
    """
    Meld a single-socket consumer that must miss its greeter and return the sentence its UnresolvedInputError says.

    Args:
        root: The conduit to meld in.
        consumer: A single-socket consumer of this module.

    Returns:
        str: The text after "(parameter 'greeter'): "; otherwise "<Type>: <message>" for another RuntimeError, or
        "no error" when the meld built the consumer.
    """
    try:
        root.meld(consumer)
    except UnresolvedInputError as error:
        return str(error).split("(parameter 'greeter'): ", 1)[-1]
    except RuntimeError as error:
        return f"{type(error).__name__}: {error}"
    return "no error"


def _nothing_provides(consumer: str) -> str:
    """The UnresolvedInputError sentence of a consumer whose `greeter: English` nothing registered provides."""
    return (
        f"{consumer}.greeter expects English, but nothing registered provides it and this meld did not supply it. "
        f"Supply it with override={{'greeter': ...}} when melding {consumer}, a path key ending in '>greeter' (or "
        f"'**greeter') when {consumer} is built as a dependency, or bind a provider for English."
    )


@pytest.mark.parametrize(
    ("provider", "shape", "existence"),
    [
        pytest.param(English, "bare", Existence.many, id="A1-class-bare"),
        pytest.param(English(), "bare", Existence.unique, id="A4-object-bare"),
    ],
)
def test_waiting_consumer_picks_up_a_provider_bound_after_conjure(provider: Any, shape: str,
                                                                 existence: Existence) -> None:
    """
    A1, A4: `ByClass` compiled with no `English` bound; `English`, a class or an existing object, arrives by `bind`,
        bound bare.

    Contract: before the bind the meld raises UnresolvedInputError; after it the meld builds `ByClass` with the
        English just bound - bare, the one address a class lookup reaches since 2026-11-07. A2, A3 and A5 file it
        under a frame: `test_waiting_class_consumer_is_refused_once_its_class_is_bound_under_a_frame`.
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
    ("provider", "shape", "existence"),
    [
        pytest.param(English, "category", Existence.many, id="A2-class-category"),
        pytest.param(English, "protocol", Existence.many, id="A3-class-protocol"),
        pytest.param(English(), "category", Existence.unique, id="A5-object-category"),
    ],
)
def test_waiting_class_consumer_is_refused_once_its_class_is_bound_under_a_frame(provider: Any, shape: str,
                                                                                 existence: Existence) -> None:
    """
    A2, A3, A5: `ByClass` and the frame's own consumer compiled with no `English` bound; `English`, a class or an
        existing object, arrives by `bind` under the category "langs" or the Protocol frame `Greeter`.

    Contract (patch hidden_provider_2026_11_07): the spellframe hides English from the class lookup, an existing
        object as much as a class, and the lookup is refused - HIDDEN_PROVIDER, naming English's address and the
        SpellMap that reaches it. The late twin is refused at its bind; the bind announced English's name, so the
        waiting `ByClass` is refused at its next meld with the same report, and an override does not rescue it - one
        answer, refused. The frame's own consumer (`list["langs"]`, `Greeter`), waiting beside `ByClass` since
        conjure, wakes with the English.
    """
    frame_consumer = FRAME_CONSUMERS[shape]
    book = _book(f"framed-arrival-{shape}-{existence.name}")
    _bind(book, ByClass)
    _bind(book, frame_consumer)
    root = book.conjure(dynamic=True, name="root")
    _given(_held(root, ByClass), "raises UnresolvedInputError", "ByClass before English is bound")
    _given(_melded(root, frame_consumer), _frame_holds(frame_consumer, None),
           f"{frame_consumer.__name__} before English is bound")
    _bind(root, provider, shape, existence)
    _late_twin_resolves(root, frame_consumer, _frame_holds(frame_consumer, "English"))
    late = _refusal(lambda: _bind(root, LateByClass))
    assert late == _hidden_provider_report("LateByClass", HIDDEN_AT[shape]), (
        f"LateByClass, bound after English was filed at the {shape} address, is not refused as HIDDEN_PROVIDER"
    )
    waiting = _refusal(lambda: root.meld(ByClass))
    assert waiting == _hidden_provider_report("ByClass", HIDDEN_AT[shape]), (
        "ByClass, waiting since conjure, is not refused at its next meld while its late twin is: a key split"
    )
    overridden = _refusal(lambda: root.meld(ByClass, override={"greeter": English()}))
    assert overridden == waiting, "an override let a refused ByClass meld"
    woken = _melded(root, frame_consumer)
    assert woken == _frame_holds(frame_consumer, "English"), (
        f"{frame_consumer.__name__} melds {woken} although English is live at the {shape} address"
    )


@pytest.mark.parametrize(
    "shape",
    [
        pytest.param("bare", id="A7-name-bare"),
    ],
)
def test_consumer_waiting_by_name_picks_up_a_provider_bound_after_conjure(shape: str) -> None:
    """
    A7: `ByName` (annotation "English", a string) compiled with no `English` bound; `English` arrives by `bind`,
        bound bare.

    Contract: the string selects the type by name, as the class does, so the meld builds `ByName` with the English
        just bound - bare, the one address the string's type part reaches since 2026-11-07. A8 and A9 file it under a
        frame: `test_waiting_name_consumer_is_refused_once_its_class_is_bound_under_a_frame`.
    """
    book = _book(f"name-{shape}")
    _bind(book, ByName)
    root = book.conjure(dynamic=True, name="root")
    _given(_held(root, ByName), "raises UnresolvedInputError", "ByName before English is bound")
    _bind(root, English, shape)
    _late_twin_resolves(root, ByName, "English")
    held = _held(root, ByName)
    assert held == "English", f"ByName melds {held} although English is live at the {shape} address"


@pytest.mark.parametrize(
    "shape",
    [
        pytest.param("category", id="A8-name-category"),
        pytest.param("protocol", id="A9-name-protocol"),
    ],
)
def test_waiting_name_consumer_is_refused_once_its_class_is_bound_under_a_frame(shape: str) -> None:
    """
    A8, A9: `ByName` (annotation "English", a string) and the frame's own consumer compiled with no `English` bound;
        `English` arrives by `bind` under the category "langs" or the Protocol frame `Greeter`.

    Contract (patch hidden_provider_2026_11_07): the string's type part is a class lookup, which no framed English
        answers, and neither frame records a contract named "English", so the lookup is refused with HIDDEN_PROVIDER
        exactly as the class object's is - the late twin at its bind, the waiting `ByName` at its next meld, an
        override or not. The frame's own consumer (`list["langs"]`, `Greeter`), waiting beside it since conjure,
        wakes with the English.
    """
    frame_consumer = FRAME_CONSUMERS[shape]
    book = _book(f"framed-name-{shape}")
    _bind(book, ByName)
    _bind(book, frame_consumer)
    root = book.conjure(dynamic=True, name="root")
    _given(_held(root, ByName), "raises UnresolvedInputError", "ByName before English is bound")
    _given(_melded(root, frame_consumer), _frame_holds(frame_consumer, None),
           f"{frame_consumer.__name__} before English is bound")
    _bind(root, English, shape)
    _late_twin_resolves(root, frame_consumer, _frame_holds(frame_consumer, "English"))
    late = _refusal(lambda: _bind(root, LateByName))
    assert late == _hidden_provider_report("LateByName", HIDDEN_AT[shape]), (
        f"LateByName, bound after English was filed at the {shape} address, is not refused as HIDDEN_PROVIDER"
    )
    waiting = _refusal(lambda: root.meld(ByName))
    assert waiting == _hidden_provider_report("ByName", HIDDEN_AT[shape]), (
        "ByName, waiting since conjure, is not refused at its next meld while its late twin is: a key split"
    )
    assert _refusal(lambda: root.meld(ByName, override={"greeter": English()})) == waiting, (
        "an override let a refused ByName meld"
    )
    woken = _melded(root, frame_consumer)
    assert woken == _frame_holds(frame_consumer, "English"), (
        f"{frame_consumer.__name__} melds {woken} although English is live at the {shape} address"
    )


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
        pytest.param(ListByProtocol, "protocol", id="B4-list-protocol-protocol"),
        pytest.param(ListByLabel, "category", id="B5-list-label-category"),
    ],
)
def test_waiting_list_gathers_a_provider_bound_after_conjure(consumer: type, shape: str) -> None:
    """
    B1, B4, B5: a collection consumer compiled with nothing to gather; `English` arrives by `bind`.

    Contract: before the bind the meld gathers nothing; after it the list holds the English just bound when the
        annotation matches it - a class list by type, of an English bound bare (2026-11-07), a Protocol list by
        contract, a label list by category. B2 and B3 file English under a frame for the class list:
        `test_waiting_list_gathers_nothing_from_a_provider_bound_under_a_frame`.
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
        pytest.param("category", id="B2-list-class-category"),
        pytest.param("protocol", id="B3-list-class-protocol"),
    ],
)
def test_waiting_list_gathers_nothing_from_a_provider_bound_under_a_frame(shape: str) -> None:
    """
    B2, B3: `ListByClass` and the frame's own list compiled with nothing to gather; `English` arrives by `bind` under
        the category "langs" or the Protocol frame `Greeter`.

    Contract (2026-11-07): `list[English]` is a class lookup and gathers only an English bound bare, so it gathers
        nothing while it waits (LIVE) and in its late twin (FRESH): no key split. The frame's own list
        (`list["langs"]`, `list[Greeter]`), waiting beside it since conjure, wakes with the English.
    """
    frame_list = FRAME_LISTS[shape]
    book = _book(f"framed-list-{shape}")
    _bind(book, ListByClass)
    _bind(book, frame_list)
    root = book.conjure(dynamic=True, name="root")
    _given(_gathered(root, ListByClass), [], "ListByClass before English is bound")
    _given(_gathered(root, frame_list), [], f"{frame_list.__name__} before English is bound")
    _bind(root, English, shape)
    _late_twin_resolves(root, frame_list, ["English"])
    fresh = _late_twin(root, ListByClass)
    assert fresh == [], f"LateListByClass gathers {fresh}: a class list reached English at the {shape} address"
    gathered = _gathered(root, ListByClass)
    assert gathered == [], f"ListByClass gathers {gathered} while its late twin gathers {fresh}: a key split"
    woken = _gathered(root, frame_list)
    assert woken == ["English"], f"{frame_list.__name__} gathers {woken} although English is live at {shape}"


@pytest.mark.parametrize(
    "shape",
    [
        pytest.param("protocol", id="C1-protocol-index"),
        pytest.param("category", id="C2-category-index"),
    ],
)
def test_class_consumer_refused_for_a_framed_index_is_released_by_a_notch_away_and_refused_after_the_notch_back(
        shape: str) -> None:
    """
    C1 (the owner's original report), C2: English is bound under the Protocol frame `Greeter` or the category "langs"
        beside the frame's own consumer; French is staged on English's index, the index is notched to French and back
        to English, then to `Edited.English`, another class named English.

    Contract (patch hidden_provider_2026_11_07): `ByClass` bound beside the framed English before conjure refuses the
        conjure - HIDDEN_PROVIDER, naming the address; bound after conjure it is refused at its bind and at its meld
        while English is active. The notch to French announces the index's frame, which the refused `ByClass` watches
        through its hidden candidate's address (re-gate path 6b): it melds as an unresolved input again - nothing
        registered provides English, and an override supplies it. The notch back announces English's name (D1 = B,
        path 6c): `ByClass` is refused again at its next meld, as its late twin is at its bind. `Edited.English`, the
        same name, keeps it refused. The frame's own consumer (`Greeter`, `list["langs"]`) follows the index
        throughout: English, French, English, Edited.English.
    """
    frame_consumer = FRAME_CONSUMERS[shape]
    report = _hidden_provider_report("ByClass", HIDDEN_AT[shape])
    beside = _book(f"notch-beside-{shape}")
    _bind(beside, English, shape)
    _bind(beside, ByClass)
    _bind(beside, frame_consumer)
    assert _refusal(lambda: beside.conjure(dynamic=True, name="root")) == report, (
        f"the conjure of ByClass beside English filed at the {shape} address is not refused as HIDDEN_PROVIDER"
    )
    frame = f"notch-back-{shape}"
    book = _book(frame)
    english_id = _bind(book, English, shape)
    _bind(book, frame_consumer)
    root = book.conjure(dynamic=True, name="root")
    index = root.get_spell_by_spell_id(english_id, frame).spell_index
    french_id = root.bind_inactive(spell=French, spell_index=index, existence=Existence.many,
                                   permissions="create", **SHAPES[shape])
    _given(_melded(root, frame_consumer), _frame_holds(frame_consumer, "English"),
           f"{frame_consumer.__name__} with English active")
    assert _refusal(lambda: _bind(root, ByClass)) == report, "ByClass is not refused at its bind"
    assert _refusal(lambda: root.meld(ByClass)) == report, "ByClass is not refused at its meld with English active"
    root.notch_spell(spell_index=index, spell_id=french_id)
    _given(_melded(root, frame_consumer), _frame_holds(frame_consumer, "French"),
           f"{frame_consumer.__name__} with French active")
    released = _unsupplied(root, ByClass)
    assert released == _nothing_provides("ByClass"), (
        "the notch of the hidden provider's index to French did not release ByClass into an unresolved input"
    )
    supplied = type(root.meld(ByClass, override={"greeter": English()}).greeter).__qualname__
    assert supplied == "English", f"the released ByClass melds {supplied} with English supplied"
    root.notch_spell(spell_index=index, spell_id=english_id)
    _late_twin_resolves(root, frame_consumer, _frame_holds(frame_consumer, "English"))
    assert _refusal(lambda: root.meld(ByClass)) == report, "ByClass is not refused again after the notch back"
    assert _refusal(lambda: _bind(root, LateByClass)) == _hidden_provider_report("LateByClass", HIDDEN_AT[shape]), (
        "LateByClass, bound after the notch back, is not refused at its bind"
    )
    edited_id = root.bind_inactive(spell=Edited.English, spell_index=index, existence=Existence.many,
                                   permissions="create", **SHAPES[shape])
    root.notch_spell(spell_index=index, spell_id=edited_id)
    _given(_melded(root, frame_consumer), _frame_holds(frame_consumer, "Edited.English"),
           f"{frame_consumer.__name__} with Edited.English active")
    assert _refusal(lambda: root.meld(ByClass)) == report, (
        "a version of the same name released ByClass: Edited.English is English to a class lookup"
    )


def test_waiting_list_gathers_nothing_across_a_notch_of_a_framed_provider() -> None:
    """
    C4: English is bound under the category "langs" before conjure, beside `ListByClass` and `ListByLabel`; the
        "langs" index is notched to French and back to English.

    Contract (2026-11-07): `list[English]` never gathers the framed English - it gathers nothing with English active,
        with French active and after the notch back, and its late twin compiled after the notch back agrees: no key
        split - while `list["langs"]` follows the index: [English], [French], [English]. Until the ruling
        `ListByClass` gathered the framed English and lost it for good at the notch to French.
    """
    frame = "list-notch-back"
    book = _book(frame)
    english_id = _bind(book, English, "category")
    _bind(book, ListByClass)
    _bind(book, ListByLabel)
    root = book.conjure(dynamic=True, name="root")
    index = root.get_spell_by_spell_id(english_id, frame).spell_index
    french_id = root.bind_inactive(spell=French, spell_index=index, existence=Existence.many,
                                   permissions="create", spellframe="langs")
    _given(_gathered(root, ListByLabel), ["English"], "ListByLabel with English active")
    with_english = _gathered(root, ListByClass)
    assert with_english == [], f"ListByClass gathers {with_english}: a class list reached English under 'langs'"
    root.notch_spell(spell_index=index, spell_id=french_id)
    _given(_gathered(root, ListByLabel), ["French"], "ListByLabel with French active")
    _given(_gathered(root, ListByClass), [], "ListByClass with French active")
    root.notch_spell(spell_index=index, spell_id=english_id)
    _late_twin_resolves(root, ListByLabel, ["English"])
    fresh = _late_twin(root, ListByClass)
    assert fresh == [], f"LateListByClass gathers {fresh}: a class list reached English under 'langs'"
    gathered = _gathered(root, ListByClass)
    assert gathered == [], f"ListByClass gathers {gathered} while its late twin gathers {fresh}: a key split"
    followed = _gathered(root, ListByLabel)
    assert followed == ["English"], f"ListByLabel gathers {followed} after the notch back to English"


def test_waiting_class_consumer_is_refused_once_its_class_is_notched_in_under_a_category() -> None:
    """
    I2: French is active under "langs" and `ByClass` waits for English beside `ListByLabel`; English is staged on that
        index with `bind_inactive` and notched in.

    Contract (patch hidden_provider_2026_11_07): staging alone changes nothing (a parked version is not resolvable,
        nor a hidden candidate); after the notch English is active under "langs", which hides it from the class
        lookup, and the notch announced English's name (D1 = B), so the waiting `ByClass` is refused at its next meld
        with HIDDEN_PROVIDER, as its late twin is at its bind - one answer - while `list["langs"]` moves from
        [French] to [English].
    """
    frame = "notch-in"
    book = _book(frame)
    french_id = _bind(book, French, "category")
    _bind(book, ByClass)
    _bind(book, ListByLabel)
    root = book.conjure(dynamic=True, name="root")
    index = root.get_spell_by_spell_id(french_id, frame).spell_index
    english_id = root.bind_inactive(spell=English, spell_index=index, existence=Existence.many,
                                    permissions="create", spellframe="langs")
    _given(_unsupplied(root, ByClass), _nothing_provides("ByClass"), "ByClass with English parked")
    _given(_gathered(root, ListByLabel), ["French"], "ListByLabel with English parked")
    root.notch_spell(spell_index=index, spell_id=english_id)
    _late_twin_resolves(root, ListByLabel, ["English"])
    late = _refusal(lambda: _bind(root, LateByClass))
    assert late == _hidden_provider_report("LateByClass", HIDDEN_AT["category"]), (
        "LateByClass, bound after English was notched in under 'langs', is not refused as HIDDEN_PROVIDER"
    )
    waiting = _refusal(lambda: root.meld(ByClass))
    assert waiting == _hidden_provider_report("ByClass", HIDDEN_AT["category"]), (
        "ByClass, waiting since conjure, is not refused at its next meld while its late twin is: a key split"
    )
    followed = _gathered(root, ListByLabel)
    assert followed == ["English"], f"ListByLabel gathers {followed} after English was notched in under 'langs'"


@pytest.mark.parametrize(
    ("definition", "consumer", "provider", "shape", "expected"),
    [
        pytest.param(Greeter, ByProtocol, English, "protocol", "English", id="F1-protocol-definition"),
    ],
)
def test_override_only_consumer_uses_a_real_provider_once_one_arrives(definition: type, consumer: type,
                                                                     provider: type, shape: str,
                                                                     expected: str) -> None:
    """
    F1: the consumer's only match is a definition bound resolvable=False, so it compiled an OVERRIDE_REQUIRED
        socket; then a real provider of that type arrives by `bind`.

    Contract: without an override the meld fails while only the definition matches (the constructor misses its
        argument); once a resolvable provider the consumer matches is bound the meld builds the consumer with it.
        F2's provider arrives under a frame its class consumer does not match:
        `test_override_only_consumer_keeps_its_definition_when_a_provider_arrives_under_a_frame`.
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


def test_override_only_consumer_keeps_its_definition_when_a_provider_arrives_under_a_frame() -> None:
    """
    F2: `ByClass`'s only match is the definition `English` bound bare with resolvable=False, so it compiled an
        OVERRIDE_REQUIRED socket; then `Edited.English` - the same type key, another spell_id - arrives by `bind`
        under the category "langs", beside a waiting `ListByLabel`.

    Contract (2026-11-07): the category hides Edited.English from the class lookup, so the definition stays
        `ByClass`'s only match and its meld still fails without an override (the constructor misses its argument),
        LIVE and FRESH alike - no key split - while `list["langs"]` wakes with Edited.English.
    """
    book = _book("override-ByClass-framed")
    _bind(book, English, resolvable=False)
    _bind(book, ByClass)
    _bind(book, ListByLabel)
    root = book.conjure(dynamic=True, name="root")
    _given(_held(root, ByClass), "raises TypeError", "ByClass with only the definition bound")
    _given(_gathered(root, ListByLabel), [], "ListByLabel before Edited.English is bound")
    _bind(root, Edited.English, "category")
    _late_twin_resolves(root, ListByLabel, ["Edited.English"])
    fresh = _late_twin(root, ByClass)
    assert fresh == "raises TypeError", (
        f"LateByClass melds {fresh}: a class lookup reached Edited.English under 'langs'"
    )
    held = _held(root, ByClass)
    assert held == "raises TypeError", f"ByClass melds {held} while its late twin melds {fresh}: a key split"
    woken = _gathered(root, ListByLabel)
    assert woken == ["Edited.English"], f"ListByLabel gathers {woken} although Edited.English is live under 'langs'"


@pytest.mark.parametrize(
    "shape",
    [
        pytest.param("bare", id="G1-bare"),
    ],
)
def test_waiting_borrower_picks_up_a_provider_granted_by_contract(shape: str) -> None:
    """
    G1: `ByClass` waits in a borrower root; the owner root's English, bound bare, is granted to it by link and
        `add_spell_to_contract`.

    Contract: after the grant the borrower's meld builds `ByClass` with the borrowed English - bare, the one address
        a class lookup reaches since 2026-11-07. G2 and G3 grant an English the owner filed under a frame:
        `test_waiting_borrower_is_refused_once_its_class_is_granted_from_under_a_frame`.
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


@pytest.mark.parametrize(
    "shape",
    [
        pytest.param("protocol", id="G2-protocol"),
        pytest.param("category", id="G3-category"),
    ],
)
def test_waiting_borrower_is_refused_once_its_class_is_granted_from_under_a_frame(shape: str) -> None:
    """
    G2, G3: `ByClass` and the frame's own consumer wait in a borrower root; the owner root's English, filed under the
        Protocol frame `Greeter` or the category "langs", is granted to it by link and `add_spell_to_contract`.

    Contract (patch hidden_provider_2026_11_07): the borrowed English keeps the owner's frame, which hides it from the
        class lookup; the grant announced English's name (D1 = B), so the borrower's waiting `ByClass` is refused at
        its next meld with HIDDEN_PROVIDER, as its late twin is at its bind - one answer - while the borrower's frame
        consumer (`Greeter`, `list["langs"]`) wakes with the borrowed English. The report names the borrowed copy as
        it names an owned one - its address and the SpellMap that reaches it. Until STEP 3 of the patch (0.2.8281) it
        read `spell id <id>` with no address, because candidates were found through `find_spell_by_spell_id` alone,
        which does not consult contracted copies; the strategy now falls back to the Book's borrowed copies.
    """
    frame = f"grant-{shape}"
    frame_consumer = FRAME_CONSUMERS[shape]
    owner_book = _book(frame)
    english_id = _bind(owner_book, English, shape)
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower_book = _book(frame, first=False)
    _bind(borrower_book, ByClass)
    _bind(borrower_book, frame_consumer)
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    _given(_held(borrower, ByClass), "raises UnresolvedInputError", "ByClass in the borrower before the grant")
    _given(_melded(borrower, frame_consumer), _frame_holds(frame_consumer, None),
           f"{frame_consumer.__name__} in the borrower before the grant")
    _given(owner.link(borrower), True, "owner.link(borrower)")
    _given(borrower.add_spell_to_contract(spell_id=english_id, conduit=owner, permissions="create"), True,
           "the grant of English")
    _late_twin_resolves(borrower, frame_consumer, _frame_holds(frame_consumer, "English"))
    late = _refusal(lambda: _bind(borrower, LateByClass))
    assert late == _hidden_provider_report("LateByClass", HIDDEN_AT[shape]), (
        f"the borrower's LateByClass, bound after the grant ({shape}), is not refused as HIDDEN_PROVIDER naming the "
        "borrowed English's address"
    )
    waiting = _refusal(lambda: borrower.meld(ByClass))
    assert waiting == _hidden_provider_report("ByClass", HIDDEN_AT[shape]), (
        f"the borrower's waiting ByClass is not refused at its next meld while its late twin is ({shape})"
    )
    woken = _melded(borrower, frame_consumer)
    assert woken == _frame_holds(frame_consumer, "English"), (
        f"the borrower's {frame_consumer.__name__} melds {woken} although English is granted ({shape})"
    )
