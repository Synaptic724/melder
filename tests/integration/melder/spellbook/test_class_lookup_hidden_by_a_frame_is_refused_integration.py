"""
Integration regressions (patch hidden_provider_2026_11_07; TASK-2026-11-07-spellframe_ambiguity_validation_check part
(a); EPIC-2026-11-07-spellframe_hides_the_concrete_class): a class lookup whose class is bound only under a
spellframe or a binding name is refused with HIDDEN_PROVIDER, an error naming each address the class is bound at and
the lookup that reaches it.

The probe matrix of the design (context_compass/artifacts/hidden_provider_20261107/probes/hidden_class_probe.py), as
regressions with whole texts: placements (a Protocol frame with and without a binding name, a category with and
without one, bare under a binding name, two frames) x consumers (a class, a string, `Optional[Class]` without a
default, `list[Class]`, `SpellMap(Class)`, `SpellMap(Class, binding_name=...)`) x postures (automatic, dynamic with
the consumer bound before conjure, dynamic with the consumer bound after it). Then the controls (bare, bare beside a
framed version, nothing bound), which keep their earlier behaviour; the re-gate paths 6a (a version bound bare), 6b (a
notch of the hidden provider's index) and 6c with the ORDER cases (a provider bound after the consumer compiled, D1 =
B); UnresolvedInputError's naming text on a stale plan; and the departure paths of the patch's UNKNOWN as measured at
0.2.8281. A notch re-gates a refused consumer. The contract and link departures - `remove_spell_from_contract`,
`remove_index_from_contract`, `sever_link` - announce no frame key, so the refused consumer keeps a refusal its fresh
twin no longer gives: strict xfails on EPIC-2026-10-25-dependency_watchers_listen_for_names (GitHub #210) until a
departure announces. `cleanup_spell` of the only hidden provider - in the consumer's Book, or by the lender of a
granted copy - leaves the consumer refused in the same way while a fresh twin melds as an unresolved input, and that
is accepted behaviour: the owner's ruling (chat 2026-11-07, recorded on #221 as cell D3) leaves what a cleaned spell's
consumers meet to the agent using the meld, so two passing tests pin it, not tied to #210. Two more strict xfails on
#210 pin the intended LIVE = FRESH outcome of findings a and d (STEP 3 of the patch): a consumer waiting in the root a
`transfer_spell_ownership` brings its class into, framed (S1 matrix cell H2), and a dependent melded while its
dependency was refused, once the refusal lifts.

Every world is a fresh Aether (autouse fixture) with creation caching off; preconditions raise RuntimeError
(`_given`), so a strict xfail never absorbs a world that was not set up as the test says.
"""
from collections.abc import Iterator
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Protocol, Tuple

import pytest

from melder import Aether, Conduit, Spellbook, SpellMap
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.system.system_diagnostic import SystemDiagnosticSeverity
from melder.utilities.custom_exceptions.phase_execution_error import PhaseExecutionError
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError
from melder.utilities.custom_exceptions.unresolved_input_error import UnresolvedInputError
from tests._spell_identity_test_support import version_of


class Greeter(Protocol):
    """The Protocol frame a framed English is checked against."""

    def greet(self) -> str:
        """Return a greeting."""
        ...


class English:
    """The class every consumer asks for."""

    def greet(self) -> str:
        """Return the English greeting."""
        return "hello"


class French:
    """Another class: the version a notch moves the hidden provider's index to."""

    def greet(self) -> str:
        """Return the French greeting."""
        return "bonjour"


# A version of English: its name, qualname and module, other code - English to a class lookup, another spell_id.
ENGLISH_V2 = version_of(English, version=2)


class SingleClass:
    """`greeter: English` - a class lookup."""

    def __init__(self, greeter: English) -> None:
        """Keep the greeter."""
        self.greeter = greeter


class LateSingleClass:
    """The fresh twin of `SingleClass`: the same annotation, bound after the event."""

    def __init__(self, greeter: English) -> None:
        """Keep the greeter."""
        self.greeter = greeter


class Upper:
    """Depends on `SingleClass`: a dependent of the consumer a class lookup refuses (finding d)."""

    def __init__(self, single: SingleClass) -> None:
        """Keep the dependency."""
        self.single = single


class LateUpper:
    """The fresh twin of `Upper`: the same dependency, bound after the event."""

    def __init__(self, single: SingleClass) -> None:
        """Keep the dependency."""
        self.single = single


class SingleString:
    """`greeter: "English"` - the string's type part is a class lookup."""

    def __init__(self, greeter: "English") -> None:
        """Keep the greeter."""
        self.greeter = greeter


class SingleOptional:
    """`greeter: Optional[English]` without a default - looked up like the class (D5)."""

    def __init__(self, greeter: Optional[English]) -> None:
        """Keep the greeter."""
        self.greeter = greeter


class ListClass:
    """`greeters: list[English]`, required - gathers English bound bare."""

    def __init__(self, greeters: list[English]) -> None:
        """Keep the gathered greeters."""
        self.greeters = greeters


class SpellMapClass:
    """`greeter = SpellMap(English)` - the class lookup under the default binding."""

    def __init__(self, greeter: Any = SpellMap(English)) -> None:
        """Keep the greeter."""
        self.greeter = greeter


class SpellMapNamed:
    """`greeter = SpellMap(English, binding_name="english")` - the class lookup under that binding name."""

    def __init__(self, greeter: Any = SpellMap(English, binding_name="english")) -> None:
        """Keep the greeter."""
        self.greeter = greeter


class Placement(NamedTuple):
    """
    Where a world binds English, and how HIDDEN_PROVIDER words it.

    Fields:
        binds: The bind keyword sets, in order.
        where: "under a spellframe" or "under a binding name".
        rows: One (address, SpellMap that reaches it, list that gathers it, is English itself) per framed spell,
            in the report's order. A `SpellMap(English)` names one class, so it lists English's own rows only.
        protocol: Whether a Protocol frame is among the addresses (the report offers its annotation).
    """

    binds: Tuple[Dict[str, Any], ...]
    where: str
    rows: Tuple[Tuple[str, str, str, bool], ...]
    protocol: bool


GREETER_NAMED = ("(spellframe='Greeter', binding_name='english')",
                 "SpellMap(spellframe=Greeter, binding_name='english')", "list[Greeter]")
GREETERS_NAMED = ("(spellframe='greeters', binding_name='english')",
                  "SpellMap(spellframe='greeters', binding_name='english')", "list['greeters']")
PLACEMENTS: Dict[str, Placement] = {
    "protocol": Placement(
        ({"spell": English, "spellframe": Greeter},), "under a spellframe",
        (("(spellframe='Greeter', binding_name=None)", "SpellMap(spellframe=Greeter)", "list[Greeter]", True),), True),
    "protocol_named": Placement(
        ({"spell": English, "spellframe": Greeter, "binding_name": "english"},), "under a spellframe",
        (GREETER_NAMED + (True,),), True),
    "category": Placement(
        ({"spell": English, "spellframe": "greeters"},), "under a spellframe",
        (("(spellframe='greeters', binding_name=None)", "SpellMap(spellframe='greeters')", "list['greeters']",
          True),), False),
    "category_named": Placement(
        ({"spell": English, "spellframe": "greeters", "binding_name": "english"},), "under a spellframe",
        (GREETERS_NAMED + (True,),), False),
    "bare_named": Placement(
        ({"spell": English, "binding_name": "english"},), "under a binding name",
        (("(spellframe=None, binding_name='english')", "SpellMap(English, binding_name='english')", "list['English']",
          True),), False),
    "two_frames": Placement(
        ({"spell": English, "spellframe": Greeter, "binding_name": "english"},
         {"spell": ENGLISH_V2, "spellframe": "greeters", "binding_name": "english"}), "under a spellframe",
        (GREETER_NAMED + (True,), GREETERS_NAMED + (False,)), True),
}
SINGLE_CONSUMERS: Dict[str, type] = {"class": SingleClass, "string": SingleString, "optional": SingleOptional}
# The single-socket cells of the matrix: every placement for the class, string and Optional consumers and for
# SpellMap(English); SpellMap(English, binding_name="english") where a framed English carries that name (bare under
# it, the named SpellMap reaches English: a control).
SINGLE_CELLS: List[Tuple[str, str]] = (
    [(placement, consumer) for placement in PLACEMENTS for consumer in (*SINGLE_CONSUMERS, "spellmap")]
    + [("protocol_named", "spellmap_named"), ("category_named", "spellmap_named")]
)
CONSUMER_CLASSES: Dict[str, type] = {**SINGLE_CONSUMERS, "spellmap": SpellMapClass, "spellmap_named": SpellMapNamed}


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


def _book(frame: str, mode: str = "dynamic", *, first: bool = True) -> Spellbook:
    """
    A Book on `frame`, one phase worker, not conjured.

    Args:
        frame: The frame name; each world uses its own.
        mode: "dynamic" or "automatic" - the frame's posture, set by its first Book.
        first: False for a later Book of the same frame, which inherits the posture.

    Returns:
        Spellbook: The Book.
    """
    book = Spellbook(aetheric_frame=frame)
    book.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    if first:
        book.configure_aether_frame(system_state=mode, system_caching_enabled=False, disposal=None,
                                    disposal_method_names=None)
    return book


def _bind_placement(target: Any, placement: str) -> List[str]:
    """Bind the placement's English spells on a Book or a conduit; return their spell_ids in bind order."""
    return [target.bind(existence="many", permissions="create", **spec) for spec in PLACEMENTS[placement].binds]


def _given(observed: Any, expected: Any, what: str) -> None:
    """
    Check a precondition of the world under test.

    Raises:
        RuntimeError: When `observed` is not `expected` - never AssertionError, so a strict xfail never absorbs a world
            that was not set up as the test says.
    """
    if observed != expected:
        raise RuntimeError(f"precondition failed - {what}: expected {expected!r}, got {observed!r}")


def _refusal(action: Callable[[], Any]) -> str:
    """
    Run a bind, meld or conjure that must be refused and return what it raised.

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
    Meld a single-socket consumer that must miss its greeter; return its UnresolvedInputError's sentence.

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


def _names_where_english_is_bound(consumer: str) -> str:
    """
    UnresolvedInputError's sentence for a consumer whose `greeter: English` is bound only under Greeter as 'english'.

    Args:
        consumer: The consumer's name.

    Returns:
        str: The text after "(parameter 'greeter'): " - the address and the SpellMap that reaches it, then the
        override paths and the ways out (patch hidden_provider_2026_11_07).
    """
    return (
        f"{consumer}.greeter expects English, but this meld did not supply it and a class lookup reaches English only "
        "where it is bound bare (no spellframe, the default binding), while English is bound only under a spellframe: "
        "English at (spellframe='Greeter', binding_name='english') - use SpellMap(spellframe=Greeter, "
        f"binding_name='english'). Supply it with override={{'greeter': ...}} when melding {consumer}, a path key "
        f"ending in '>greeter' (or '**greeter') when {consumer} is built as a dependency, ask for it where it is "
        "bound, as shown, or bind English bare."
    )


def _entries(placement: str, column: int, *, own_only: bool = False) -> str:
    """The report's entries for a placement: "English at <address> - use <lookup>", column 1 SpellMap, 2 list."""
    rows = [row for row in PLACEMENTS[placement].rows if row[3] or not own_only]
    return "; ".join(f"English at {row[0]} - use {row[column]}" for row in rows)


def _hidden_message(consumer: str, placement: str) -> str:
    """HIDDEN_PROVIDER's message for a class, string or Optional consumer of `greeter: English` (the patch's form 1)."""
    spec = PLACEMENTS[placement]
    which = "the SpellMap shown" if len(spec.rows) == 1 else "the SpellMap of the one it needs"
    protocol = ", or a Greeter annotation while that spell is the only one bound under Greeter" if spec.protocol else ""
    return (
        f"Parameter 'greeter' on spell '{consumer}' expects English, but a class lookup reaches English only where it "
        f"is bound bare (no spellframe, the default binding), and English is bound only {spec.where}: "
        f"{_entries(placement, 1)}. Ask for it where it is bound - {which}, as the parameter's default{protocol} - or "
        "bind English bare."
    )


def _spellmap_message(consumer: str, placement: str, binding_name: Optional[str]) -> str:
    """HIDDEN_PROVIDER's message for a `SpellMap(English[, binding_name=...])` default (the patch's form 2)."""
    written = "SpellMap(English)" if binding_name is None else f"SpellMap(English, binding_name={binding_name!r})"
    reach = "the default binding" if binding_name is None else f"the binding name {binding_name!r}"
    tail = "" if binding_name is None else f" under the binding name {binding_name!r}"
    return (
        f"Parameter 'greeter' on spell '{consumer}' has the default {written}, a class lookup that reaches English "
        f"only where it is bound bare under {reach}, but English is bound only where that lookup does not reach: "
        f"{_entries(placement, 1, own_only=True)}. Point the SpellMap at the address it means, as shown, or bind "
        f"English bare{tail}."
    )


def _collection_message(placement: str, dynamic: bool) -> str:
    """Phase 6's `collection_socket_no_providers` message for ListClass, naming the bindings (D3)."""
    head = (
        "Spell 'ListClass' parameter 'greeters' is a required list[...] dependency, but no provider is wired into it: "
        "list[English] gathers English only where it is bound bare (no spellframe, the default binding), and English "
        f"is bound only {PLACEMENTS[placement].where}: {_entries(placement, 2)}."
    )
    if dynamic:
        return head + (" An empty list will be injected at construction; gather it where it is bound, as shown, or "
                       "bind English bare to populate it.")
    return head + " Gather it where it is bound, as shown, bind English bare, or make the parameter optional."


def _report(consumer: str, message: str, code: str = "HIDDEN_PROVIDER") -> str:
    """The whole SpellbookValidationError text refusing one spell with one error."""
    return f"Spellbook validation failed. Broken spells: {consumer}.\n{consumer}:\n  - {message} [{code}]"


def _cell_report(placement: str, consumer: str) -> str:
    """The report refusing a single-socket matrix cell's consumer."""
    name = CONSUMER_CLASSES[consumer].__name__
    if consumer == "spellmap":
        return _report(name, _spellmap_message(name, placement, None))
    if consumer == "spellmap_named":
        return _report(name, _spellmap_message(name, placement, "english"))
    return _report(name, _hidden_message(name, placement))


def _collection_warning(root: Conduit) -> Tuple[Any, str, Any]:
    """The one `collection_socket_no_providers` diagnostic `validate_resolution` holds: (severity, message, details)."""
    state = root.validate_resolution()
    found = [diag for diag in state.list_diagnostics() if diag.code == "collection_socket_no_providers"]
    _given(len(found), 1, "collection_socket_no_providers diagnostics after validate_resolution")
    return found[0].severity, found[0].message, found[0].details


@pytest.mark.parametrize("mode", ["automatic", "dynamic"])
@pytest.mark.parametrize(("placement", "consumer"), SINGLE_CELLS)
def test_class_lookup_of_a_class_bound_only_under_a_frame_or_a_name_refuses_conjure(placement: str, consumer: str,
                                                                                    mode: str) -> None:
    """
    The consumer bound beside the placement before conjure, automatic and dynamic alike: conjure is refused with one
    HIDDEN_PROVIDER error naming every address of English and the lookup that reaches it - nothing is constructed.
    """
    book = _book(f"conjure-{placement}-{consumer}-{mode}", mode)
    _bind_placement(book, placement)
    book.bind(spell=CONSUMER_CLASSES[consumer], existence="many", permissions="create")
    refused = _refusal(lambda: book.conjure(name="root", dynamic=(mode == "dynamic")))
    assert refused == _cell_report(placement, consumer), f"{consumer} beside English ({placement}) conjured in {mode}"


@pytest.mark.parametrize(("placement", "consumer"), SINGLE_CELLS)
def test_late_bound_class_consumer_is_refused_at_bind_and_at_every_meld_with_or_without_override(placement: str,
                                                                                                 consumer: str) -> None:
    """
    A dynamic world conjured with the placement; the consumer bound after conjure. Its bind raises the report (the
    late bind runs phases 1-4) and it stays registered; every meld then raises the same report, an override as well
    (D2: an override no longer rescues a class bound only under a frame or a name).
    """
    book = _book(f"late-{placement}-{consumer}")
    _bind_placement(book, placement)
    root = book.conjure(name="root", dynamic=True)
    consumer_cls = CONSUMER_CLASSES[consumer]
    expected = _cell_report(placement, consumer)
    assert _refusal(lambda: root.bind(spell=consumer_cls, existence="many", permissions="create")) == expected
    assert _refusal(lambda: root.meld(consumer_cls)) == expected
    assert _refusal(lambda: root.meld(consumer_cls, override={"greeter": English()})) == expected


@pytest.mark.parametrize("placement", list(PLACEMENTS))
def test_empty_required_class_list_refuses_an_automatic_conjure_naming_where_its_class_is_bound(placement: str) -> None:
    """
    `list[English]` with English bound only under a frame or a name gathers nothing; in an automatic world conjure is
    refused with Phase 6's ERROR naming the bindings and the list that gathers each.
    """
    book = _book(f"list-auto-{placement}", "automatic")
    _bind_placement(book, placement)
    book.bind(spell=ListClass, existence="many", permissions="create")
    assert _refusal(lambda: book.conjure(name="root")) == _report(
        "ListClass", _collection_message(placement, False), "collection_socket_no_providers")


@pytest.mark.parametrize("late", [False, True], ids=["bound-before-conjure", "bound-after-conjure"])
@pytest.mark.parametrize("placement", list(PLACEMENTS))
def test_empty_required_class_list_is_injected_empty_with_a_warning_naming_where_its_class_is_bound(placement: str,
                                                                                                    late: bool) -> None:
    """
    Dynamic (D3): `list[English]`, bound before conjure or after it, is built with [] while English is bound only
    under a frame or a name, and `validate_resolution` holds Phase 6's WARNING naming the bindings and the list that
    gathers each, with those lists in its details.
    """
    book = _book(f"list-dynamic-{placement}-{late}")
    _bind_placement(book, placement)
    if not late:
        book.bind(spell=ListClass, existence="many", permissions="create")
    root = book.conjure(name="root", dynamic=True)
    if late:
        root.bind(spell=ListClass, existence="many", permissions="create")
    assert root.meld(ListClass).greeters == [], f"ListClass gathered a framed English ({placement})"
    severity, message, details = _collection_warning(root)
    assert severity is SystemDiagnosticSeverity.WARNING
    assert message == _collection_message(placement, True)
    assert [entry["use"] for entry in details["hidden_candidates"]] == [row[2] for row in PLACEMENTS[placement].rows]


@pytest.mark.parametrize("control", ["bare", "bare_and_framed"])
@pytest.mark.parametrize("mode", ["automatic", "dynamic"])
def test_class_bound_bare_is_found_by_every_class_lookup_beside_a_framed_version(control: str, mode: str) -> None:
    """
    Controls: English bound bare - alone, or beside ENGLISH_V2 under Greeter - is found by the class, string and
    Optional consumers, `SpellMap(English)` and `list[English]` exactly as before the patch; nothing is refused.
    """
    book = _book(f"control-{control}-{mode}", mode)
    book.bind(spell=English, existence="many", permissions="create")
    if control == "bare_and_framed":
        book.bind(spell=ENGLISH_V2, existence="many", permissions="create", spellframe=Greeter)
    for consumer in (*SINGLE_CONSUMERS.values(), SpellMapClass, ListClass):
        book.bind(spell=consumer, existence="many", permissions="create")
    root = book.conjure(name="root", dynamic=(mode == "dynamic"))
    for consumer in (*SINGLE_CONSUMERS.values(), SpellMapClass):
        assert type(root.meld(consumer).greeter) is English, f"{consumer.__name__} missed the bare English"
    assert [type(each) for each in root.meld(ListClass).greeters] == [English]


def test_named_spellmap_reaches_the_class_bound_bare_under_that_name() -> None:
    """
    Control: English bound bare under the binding name "english" is reached by `SpellMap(English,
    binding_name="english")` - the named class lookup - and is no hidden provider for it; the unnamed
    `SpellMap(English)` beside it is refused (the matrix's bare_named cells).
    """
    book = _book("control-bare-named-spellmap", "automatic")
    _bind_placement(book, "bare_named")
    book.bind(spell=SpellMapNamed, existence="many", permissions="create")
    root = book.conjure(name="root")
    assert type(root.meld(SpellMapNamed).greeter) is English


def test_class_bound_nowhere_keeps_the_unresolved_input_and_the_earlier_failures() -> None:
    """
    Control: nothing of English bound. The single consumers conjure and their meld raises UnresolvedInputError saying
    nothing registered provides English (an override supplies it); `list[English]` keeps Phase 6's earlier text
    byte for byte; `SpellMap(English)` still fails Phase 3 (D4: a SpellMap miss with its class bound nowhere).
    """
    book = _book("control-none", "automatic")
    for consumer in SINGLE_CONSUMERS.values():
        book.bind(spell=consumer, existence="many", permissions="create")
    root = book.conjure(name="root")
    for consumer in SINGLE_CONSUMERS.values():
        assert _unsupplied(root, consumer) == _nothing_provides(consumer.__name__)
        assert type(root.meld(consumer, override={"greeter": English()}).greeter) is English
    listing = _book("control-none-list", "automatic")
    listing.bind(spell=ListClass, existence="many", permissions="create")
    assert _refusal(lambda: listing.conjure(name="root")) == _report(
        "ListClass", "Spell 'ListClass' parameter 'greeters' is a required list[...] dependency, but no provider is "
        "wired into it. Bind at least one implementation under its frame, make the parameter optional, or run the book "
        "in dynamic mode if members arrive via contracts.", "collection_socket_no_providers")
    mapping = _book("control-none-spellmap", "automatic")
    mapping.bind(spell=SpellMapClass, existence="many", permissions="create")
    with pytest.raises(PhaseExecutionError, match="SpellMap default could not be resolved for parameter 'greeter' on "
                                                  "spell 'SpellMapClass'"):
        mapping.conjure(name="root")


def test_refused_consumer_melds_a_version_of_its_class_bound_bare_after_the_refusal() -> None:
    """
    Re-gate path 6a: SingleClass is refused at its late bind (English under Greeter); ENGLISH_V2 is then bound bare.
    The bare bind announces "english", the refused consumer's own key, so its next meld reruns phases 1-4, finds the
    bare version - no hidden candidate is recorded beside a class found bare - and builds with it.
    """
    book = _book("regate-6a")
    _bind_placement(book, "protocol_named")
    root = book.conjure(name="root", dynamic=True)
    _given(_refusal(lambda: root.bind(spell=SingleClass, existence="many", permissions="create")),
           _cell_report("protocol_named", "class"), "SingleClass's late bind")
    root.bind(spell=ENGLISH_V2, existence="many", permissions="create")
    assert type(root.meld(SingleClass).greeter) is ENGLISH_V2, "the version bound bare did not lift the refusal"


def test_refused_consumer_is_released_by_a_notch_of_its_hidden_provider_to_another_class() -> None:
    """
    Re-gate path 6b: SingleClass is refused at its late bind; English's index under Greeter is notched to ENGLISH_V2,
    then to French. The refused consumer watches its hidden candidates' address, which a notch announces: a version of
    the same name keeps it refused (English to a class lookup); another class releases it into an unresolved input -
    nothing registered provides English, and an override supplies it.
    """
    book = _book("regate-6b")
    english_id, = _bind_placement(book, "protocol_named")
    root = book.conjure(name="root", dynamic=True)
    index = root.get_spell_by_spell_id(english_id, "regate-6b").spell_index
    v2_id = root.bind_inactive(spell=ENGLISH_V2, spell_index=index, existence=Existence.many, permissions="create",
                               spellframe=Greeter, binding_name="english")
    french_id = root.bind_inactive(spell=French, spell_index=index, existence=Existence.many, permissions="create",
                                   spellframe=Greeter, binding_name="english")
    report = _cell_report("protocol_named", "class")
    _given(_refusal(lambda: root.bind(spell=SingleClass, existence="many", permissions="create")), report,
           "SingleClass's late bind")
    root.notch_spell(spell_index=index, spell_id=v2_id)
    assert _refusal(lambda: root.meld(SingleClass)) == report, "a same-named version released SingleClass"
    root.notch_spell(spell_index=index, spell_id=french_id)
    assert _unsupplied(root, SingleClass) == _nothing_provides("SingleClass"), (
        "the notch to French did not release SingleClass into an unresolved input"
    )
    assert type(root.meld(SingleClass, override={"greeter": English()}).greeter) is English


@pytest.mark.parametrize("placement", ["protocol_named", "category", "bare_named"])
def test_consumer_compiled_before_its_class_was_bound_is_refused_once_the_class_arrives_hidden(placement: str) -> None:
    """
    Re-gate path 6c, the ORDER cases (D1 = B): SingleClass compiled as an unresolved input with nothing bound; English
    then arrives framed under Greeter, under the category "greeters", or bare under a binding name. The bind announces
    English's name, so the waiting consumer is refused at its next meld with the report its fresh twin gets at its
    bind - with an override as well.
    """
    book = _book(f"order-{placement}")
    book.bind(spell=SingleClass, existence="many", permissions="create")
    root = book.conjure(name="root", dynamic=True)
    _given(_unsupplied(root, SingleClass), _nothing_provides("SingleClass"), "SingleClass before English is bound")
    _bind_placement(root, placement)
    expected = _cell_report(placement, "class")
    assert _refusal(lambda: root.meld(SingleClass)) == expected, "the waiting consumer was not refused: a key split"
    assert _refusal(lambda: root.meld(SingleClass, override={"greeter": English()})) == expected
    late = _refusal(lambda: root.bind(spell=LateSingleClass, existence="many", permissions="create"))
    assert late == _report("LateSingleClass", _hidden_message("LateSingleClass", placement))


def test_consumer_compiled_before_its_class_was_bound_wakes_when_the_class_arrives_bare() -> None:
    """The ORDER control: English bound bare after the consumer compiled - the consumer wakes and builds with it."""
    book = _book("order-bare")
    book.bind(spell=SingleClass, existence="many", permissions="create")
    root = book.conjure(name="root", dynamic=True)
    _given(_unsupplied(root, SingleClass), _nothing_provides("SingleClass"), "SingleClass before English is bound")
    root.bind(spell=English, existence="many", permissions="create")
    assert type(root.meld(SingleClass).greeter) is English


def test_unresolved_input_error_on_a_stale_plan_names_where_the_class_is_bound() -> None:
    """
    UnresolvedInputError's safety net: right after English is bound under Greeter the consumer's compiled plan still
    holds an unresolved input with no hidden candidates (its gated meld has not rerun phases 1-4), and the error that
    plan raises computes the candidates live from the pool - naming English's address instead of "nothing registered
    provides it" (white-box call of `for_unsupplied`).
    """
    book = _book("stale-plan")
    consumer_id = book.bind(spell=SingleClass, existence="many", permissions="create")
    root = book.conjure(name="root", dynamic=True)
    english_id, = _bind_placement(root, "protocol_named")
    spell = root.get_spell_by_spell_id(consumer_id, "stale-plan")
    error = UnresolvedInputError.for_unsupplied(spell, ["greeter"])
    assert str(error).split("(parameter 'greeter'): ", 1)[-1] == _names_where_english_is_bound("SingleClass")
    assert error.hidden_spell_ids == (english_id,)


def _transferred_into_a_waiting_root(frame: str) -> Conduit:
    """
    The world of S1 matrix cell H2: SingleClass waits in a target root, compiled while nothing provided English; the
    owner root then moves English, filed under Greeter as 'english', into the target with `transfer_spell_ownership`,
    and a fresh twin bound after the transfer is refused at its bind (HIDDEN_PROVIDER).

    Args:
        frame: The frame both Books share; this world's own.

    Returns:
        Conduit: The target root.

    Raises:
        RuntimeError: Through `_given`, when the world is not the one described.
    """
    owner_book = _book(frame)
    english_id, = _bind_placement(owner_book, "protocol_named")
    target_book = _book(frame, first=False)
    target_book.bind(spell=SingleClass, existence="many", permissions="create")
    owner = owner_book.conjure(name="owner", dynamic=True)
    target = target_book.conjure(name="target", dynamic=True)
    _given(_unsupplied(target, SingleClass), _nothing_provides("SingleClass"), "SingleClass before the transfer")
    owner.transfer_spell_ownership(spell=english_id, target_conduit=target)
    _given(_refusal(lambda: target.bind(spell=LateSingleClass, existence="many", permissions="create")),
           _report("LateSingleClass", _hidden_message("LateSingleClass", "protocol_named")),
           "the fresh twin bound after the transfer")
    return target


def test_consumer_a_transfer_leaves_ungated_raises_an_error_naming_where_its_class_is_bound() -> None:
    """
    UnresolvedInputError's safety net on a production arrival path that does not announce English's name (S1 matrix
    cell H2, finding a, measured 0.2.8281): SingleClass waits in the target root, and the owner root moves English,
    filed under Greeter, into it with `transfer_spell_ownership`. The transfer's commit resolves its staged binding
    keys in the source Book, which no longer holds English, so it announces only the frame key and the waiting
    consumer is not re-gated: it melds as an unresolved input while its fresh twin is refused at bind. Its error names
    where English now is instead of "nothing registered provides it". The intended answer - refused like its twin - is
    the strict xfail `test_consumer_waiting_in_the_target_is_refused_once_a_transfer_brings_its_class_in_framed`;
    when the transfer announces the class name, that xfail passes and this test changes with it.
    """
    target = _transferred_into_a_waiting_root("transfer-arrival")
    assert _unsupplied(target, SingleClass) == _names_where_english_is_bound("SingleClass")


TRANSFER_ARRIVAL_GAP = (
    "EPIC-2026-10-25-dependency_watchers_listen_for_names (GitHub #210): transfer_spell_ownership announces only the "
    "arriving spell's frame key - its commit resolves the staged binding keys in the source Book, which no longer "
    "holds the spell - so the waiting consumer is never re-gated and melds as an unresolved input where its fresh twin "
    "is refused (measured 0.2.8281; finding a of patch hidden_provider_2026_11_07, S1 matrix cell H2)"
)


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=TRANSFER_ARRIVAL_GAP)
def test_consumer_waiting_in_the_target_is_refused_once_a_transfer_brings_its_class_in_framed() -> None:
    """
    Finding a, the intended outcome (LIVE = FRESH): after the transfer of S1 cell H2 brings English, filed under
    Greeter, into the root where SingleClass waits, SingleClass is refused at its next meld with the HIDDEN_PROVIDER
    report its fresh twin got at its bind - as it is when English arrives by bind, notch or contract grant (D1 = B).
    """
    target = _transferred_into_a_waiting_root("transfer-arrival-refused")
    assert _refusal(lambda: target.meld(SingleClass)) == _cell_report("protocol_named", "class"), (
        "the waiting consumer melds as an unresolved input while its fresh twin is refused: a key split"
    )


DEPENDENT_GAP = (
    "EPIC-2026-10-25-dependency_watchers_listen_for_names (GitHub #210): a dependent melded while its dependency was "
    "refused is left invalid (broken_spell_in_dag) and nothing re-gates it when the refusal lifts, so it keeps a "
    "refusal its fresh twin no longer gives - after AMBIGUOUS_PROVIDER as after HIDDEN_PROVIDER, and before this "
    "patch (measured 0.2.8281 and on 0733b3b65; finding d of patch hidden_provider_2026_11_07)"
)


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=DEPENDENT_GAP)
def test_dependent_melded_during_a_refusal_melds_as_its_fresh_twin_once_the_refusal_lifts() -> None:
    """
    Finding d, the intended outcome (LIVE = FRESH): SingleClass is refused at its late bind (English under Greeter);
    Upper, which depends on it, is bound and melded during the refusal - its meld fails, SingleClass being broken.
    English's index is then notched to French, which releases SingleClass into an unresolved input (re-gate path 6b).
    A fresh twin of Upper bound then melds into SingleClass's UnresolvedInputError; Upper should give that answer. It
    keeps "No validation error was recorded for this spell" instead - as a dependent does after an AMBIGUOUS_PROVIDER
    refusal lifts, before this patch too (probes/dependent_after_refusal_probe.py).
    """
    book = _book("dependent-after-refusal")
    english_id, = _bind_placement(book, "protocol_named")
    root = book.conjure(name="root", dynamic=True)
    index = root.get_spell_by_spell_id(english_id, "dependent-after-refusal").spell_index
    french_id = root.bind_inactive(spell=French, spell_index=index, existence=Existence.many, permissions="create",
                                   spellframe=Greeter, binding_name="english")
    _given(_refusal(lambda: root.bind(spell=SingleClass, existence="many", permissions="create")),
           _cell_report("protocol_named", "class"), "SingleClass's late bind")
    root.bind(spell=Upper, existence="many", permissions="create")
    during = _refusal(lambda: root.meld(Upper))
    _given("[broken_spell_in_dag]" in during, True, f"Upper melded during the refusal ({during!r})")
    root.notch_spell(spell_index=index, spell_id=french_id)
    _given(_unsupplied(root, SingleClass), _nothing_provides("SingleClass"), "SingleClass released by the notch")
    root.bind(spell=LateUpper, existence="many", permissions="create")
    fresh = _unsupplied(root, LateUpper)
    _given(fresh, _nothing_provides("SingleClass"), "the fresh twin of Upper, bound after the notch")
    assert _unsupplied(root, Upper) == fresh, "Upper keeps the refusal its fresh twin no longer gives"


DEPARTURE_GAP = (
    "EPIC-2026-10-25-dependency_watchers_listen_for_names (GitHub #210): this departure announces no frame key, so the "
    "refused consumer is never re-gated and keeps a refusal its fresh twin no longer gives (measured 0.2.8281; the "
    "departure UNKNOWN of patch hidden_provider_2026_11_07)"
)


def test_refused_consumer_keeps_its_refusal_after_cleanup_spell_disposes_its_only_hidden_provider() -> None:
    """
    Accepted behaviour, pinned as such - the owner's ruling (chat 2026-11-07, recorded on #221 as cell D3): a spell
    that is cleaned up is gone, and what its consumers meet afterwards is not a defect but the meld user's - an
    agent's - to handle. Not tied to #210.

    SingleClass is refused at its late bind (English under Greeter); English is then disposed with `cleanup_spell`,
    which announces nothing. SingleClass keeps its HIDDEN_PROVIDER refusal - the report it was refused with, still
    naming the disposed English - at every meld, with an override as well, while a fresh twin bound after the cleanup
    binds and melds as an unresolved input (the agent's way out: dispose the consumer and bind it again).
    """
    book = _book("cleanup-own-book")
    english_id, = _bind_placement(book, "protocol_named")
    root = book.conjure(name="root", dynamic=True)
    report = _cell_report("protocol_named", "class")
    _given(_refusal(lambda: root.bind(spell=SingleClass, existence="many", permissions="create")), report,
           "SingleClass's late bind")
    root.cleanup_spell(spell=root.get_spell_by_spell_id(english_id, "cleanup-own-book"))
    assert _refusal(lambda: root.meld(SingleClass)) == report, "SingleClass lost its refusal at the cleanup"
    assert _refusal(lambda: root.meld(SingleClass, override={"greeter": English()})) == report
    root.bind(spell=LateSingleClass, existence="many", permissions="create")
    assert _unsupplied(root, LateSingleClass) == _nothing_provides("LateSingleClass"), (
        "the fresh twin bound after the cleanup does not meld as an unresolved input"
    )


def _refused_borrower(frame: str, *, index_link: bool) -> Tuple[Conduit, Conduit, str, Any]:
    """
    An owner root lends English (under Greeter as 'english') to a borrower root whose SingleClass waited since conjure
    and is refused at its next meld once the grant - a version grant or an index link - announced English's name.

    Args:
        frame: The frame both Books share; this world's own.
        index_link: True to lend English's index (`add_index_to_contract`), False to grant the version.

    Returns:
        Tuple[Conduit, Conduit, str, Any]: (owner, borrower, English's spell_id, English's index).

    Raises:
        RuntimeError: Through `_given`, when the borrower's SingleClass is not refused with the report naming the lent
            English's address (a borrowed candidate renders as an owned one since STEP 3 of the patch).
    """
    owner_book = _book(frame)
    english_id, = _bind_placement(owner_book, "protocol_named")
    owner = owner_book.conjure(name="owner", dynamic=True)
    borrower_book = _book(frame, first=False)
    borrower_book.bind(spell=SingleClass, existence="many", permissions="create")
    borrower = borrower_book.conjure(name="borrower", dynamic=True)
    _given(owner.link(borrower), True, "owner.link(borrower)")
    index = owner_book.find_spell_by_spell_id(english_id).spell_index
    with borrower.transaction("link", conduits=[borrower, owner]):
        if index_link:
            _given(borrower.add_index_to_contract(index=index, conduit=owner, permissions="create"), True,
                   "the index link")
        else:
            _given(borrower.add_spell_to_contract(spell_id=english_id, conduit=owner, permissions="create"), True,
                   "the version grant")
    _given(_refusal(lambda: borrower.meld(SingleClass)), _cell_report("protocol_named", "class"),
           "the borrower's SingleClass refused after the grant")
    return owner, borrower, english_id, index


def _depart(departure: str, owner: Conduit, borrower: Conduit, english_id: str, index: Any) -> None:
    """
    Take the lent English away from the borrower by one contract or link path.

    Args:
        departure: "remove_spell_from_contract", "remove_index_from_contract" or "sever_link".
        owner: The lending root.
        borrower: The borrowing root.
        english_id: English's spell_id.
        index: English's index.
    """
    if departure == "remove_spell_from_contract":
        with borrower.transaction("link", conduits=[borrower, owner]):
            _given(borrower.remove_spell_from_contract(spell_id=english_id, conduit=owner), True, departure)
    elif departure == "remove_index_from_contract":
        borrower.remove_index_from_contract(index_id=index.id, conduit=owner)
    else:
        _given(owner.sever_link(borrower), True, departure)


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=DEPARTURE_GAP)
@pytest.mark.parametrize(("departure", "index_link"), [
    ("remove_spell_from_contract", False),
    ("remove_index_from_contract", True),
    ("sever_link", False),
])
def test_refused_borrower_is_released_when_its_only_hidden_provider_leaves_the_contract(departure: str,
                                                                                       index_link: bool) -> None:
    """
    The borrower's SingleClass is refused once English, filed under Greeter, is lent to it; the lent English then
    leaves the borrower - its grant or index link removed, or the link severed. A fresh twin then binds and melds as an
    unresolved input; the refused consumer should give that answer (LIVE = FRESH, #210). English disposed by its lender
    is the accepted behaviour of
    `test_refused_borrower_keeps_its_refusal_after_the_lender_cleans_up_its_only_hidden_provider`.
    """
    frame = f"departure-{departure}"
    owner, borrower, english_id, index = _refused_borrower(frame, index_link=index_link)
    _depart(departure, owner, borrower, english_id, index)
    borrower.bind(spell=LateSingleClass, existence="many", permissions="create")
    _given(_unsupplied(borrower, LateSingleClass), _nothing_provides("LateSingleClass"), "the fresh twin")
    assert _unsupplied(borrower, SingleClass) == _nothing_provides("SingleClass"), "the refusal outlived the lending"


def test_refused_borrower_keeps_its_refusal_after_the_lender_cleans_up_its_only_hidden_provider() -> None:
    """
    Accepted behaviour, pinned as such - the owner's ruling (chat 2026-11-07, recorded on #221 as cell D3): a spell
    that is cleaned up is gone, and what its consumers meet afterwards is not a defect but the meld user's - an
    agent's - to handle. Not tied to #210.

    The borrower's SingleClass is refused once English, filed under Greeter, is granted to it; the lender then disposes
    English with `cleanup_spell`, which first releases every contract holding the version and announces nothing. The
    borrower's SingleClass keeps its HIDDEN_PROVIDER refusal - the report naming the lent English's address - at every
    meld, with an override as well, while a fresh twin bound in the borrower after the cleanup melds as an unresolved
    input (the agent's way out: dispose the consumer and bind it again).
    """
    frame = "cleanup-lender"
    owner, borrower, english_id, _ = _refused_borrower(frame, index_link=False)
    report = _cell_report("protocol_named", "class")
    owner.cleanup_spell(spell=owner.get_spell_by_spell_id(english_id, frame))
    assert _refusal(lambda: borrower.meld(SingleClass)) == report, "SingleClass lost its refusal at the cleanup"
    assert _refusal(lambda: borrower.meld(SingleClass, override={"greeter": English()})) == report
    borrower.bind(spell=LateSingleClass, existence="many", permissions="create")
    assert _unsupplied(borrower, LateSingleClass) == _nothing_provides("LateSingleClass"), (
        "the fresh twin bound in the borrower after the cleanup does not meld as an unresolved input"
    )
