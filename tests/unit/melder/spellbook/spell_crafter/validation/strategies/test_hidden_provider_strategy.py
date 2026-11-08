"""
Unit tests for `HiddenProviderStrategy` (patch hidden_provider_2026_11_07): the Phase-4 refusal of a class lookup
whose class is bound only under a spellframe or a binding name, driven from the UNRESOLVED_INPUT sockets Phase 3
records with hidden candidates.
"""
from types import SimpleNamespace
from typing import Any, List, Optional, Protocol

import pytest

from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import ParameterDIShape
from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import (
    SpellLocalTopology,
    SpellSocketDescriptor,
)
from melder.aether.spellbook.spell_compiler.validation.spell_validation_context import SpellValidationContext
from melder.aether.spellbook.spell_compiler.validation.spell_validation_issue import SpellValidationIssue
from melder.aether.spellbook.spell_compiler.validation.strategies.hidden_provider_strategy import (
    HiddenProviderStrategy,
)
from melder.aether.spellbook.spellframe_kind.spellframe_kind import SpellframeKind


class Greeter(Protocol):
    """The Protocol frame English is bound under."""

    def greet(self) -> str: ...


class English:
    """The class the consumer asks for."""


class _StatesStub:
    """Hands back one fixed topology for any index."""

    def __init__(self, topology: Optional[SpellLocalTopology]) -> None:
        """Hold the topology to return."""
        self._topology = topology

    def get_local_topology(self, spell_index: Any) -> Optional[SpellLocalTopology]:
        """Return the held topology."""
        return self._topology


class _SpellStub:
    """A consumer spell with a name, an id, an index and a states registry."""

    def __init__(self, topology: Optional[SpellLocalTopology], spell_name: str = "Host") -> None:
        """Wire the stub."""
        self.spell_id = "consumer"
        self.spell_name = spell_name
        self.spell_index = SimpleNamespace(selected_spell_id="consumer")
        self._spell_system_states = _StatesStub(topology)


class _BookStub:
    """
    A spellbook that answers for its own spells and for the copies it borrows, as the Book does.

    `find_spell_by_spell_id` reads the own spells; `_contracted_spells` keys the peers whose copies the Book holds and
    `_find_contracted_spell_by_id(spell_id, conduit_id)` answers one peer's copy - the two surfaces the strategy reads.
    """

    def __init__(self, spells: dict, borrowed: Optional[dict] = None) -> None:
        """Hold the own spells by id and the borrowed copies as {peer conduit id: {spell id: copy}}."""
        self._spells = spells
        self._borrowed = borrowed or {}
        self._contracted_spells = {conduit_id: {} for conduit_id in self._borrowed}

    def find_spell_by_spell_id(self, spell_id: str) -> Any:
        """Return the own spell or None; a borrowed copy is not an own spell."""
        return self._spells.get(spell_id)

    def _find_contracted_spell_by_id(self, spell_id: str, conduit_id: str) -> Any:
        """Return the copy borrowed from `conduit_id` under `spell_id`, or None."""
        return self._borrowed.get(conduit_id, {}).get(spell_id)


def _candidate(spellframe: Any, binding_name: Optional[str]) -> SimpleNamespace:
    """An English spell stub at one address, its frame kind derived as Bind records it."""
    if spellframe is None:
        kind = SpellframeKind.none
    elif isinstance(spellframe, str):
        kind = SpellframeKind.category
    else:
        kind = SpellframeKind.contract
    return SimpleNamespace(spell_name="English", spellframe=spellframe, spellframe_kind=kind,
                           binding_name=binding_name)


def _socket(kind: SocketKind, hidden: tuple = (), *, param_name: str = "greeter", position: int = 0,
            collection: bool = False) -> SpellSocketDescriptor:
    """One socket of the given kind with the hidden candidates Phase 3 would record."""
    return SpellSocketDescriptor(
        spell_id="consumer", param_name=param_name, position=position, socket_kind=kind, is_collection=collection,
        is_optional=False, target_spell_ids=(), dependency_key=("english", "__default__"),
        hidden_spell_ids=hidden, hidden_frame_keys=("greeter",) if hidden else (),
    )


def _requirements(*params: SimpleNamespace) -> SimpleNamespace:
    """Phase-1 requirements listing the given parameters."""
    return SimpleNamespace(parameters=list(params))


def _annotated(name: str = "greeter", annotation: Any = English) -> SimpleNamespace:
    """A SINGLE_BY_ANNOTATION parameter."""
    return SimpleNamespace(name=name, annotation=annotation, di_shape=ParameterDIShape.SINGLE_BY_ANNOTATION,
                           spellmap_default=None)


def _context(topology: Optional[SpellLocalTopology], spellbook: Any, issues: List[SpellValidationIssue],
             requirements: Any = None, cancel_event: Any = None) -> SpellValidationContext:
    """Build a validation context around the stubs."""
    return SpellValidationContext(
        spell=_SpellStub(topology), spellbook=spellbook, requirements=requirements, symbolic_graph=None,
        resolution_frame=None, cancel_event=cancel_event, issues=issues,
    )


def test_init_sets_name_and_description() -> None:
    """The strategy publishes a stable name."""
    strategy = HiddenProviderStrategy()
    assert strategy.name == "hidden_provider"
    assert "spellframe or a binding name" in strategy.description


def test_no_topology_emits_nothing() -> None:
    """A spell without a Phase-3 topology (a stand-in) yields no issue."""
    issues: List[SpellValidationIssue] = []
    HiddenProviderStrategy().validate(_context(None, None, issues))
    assert issues == []


def test_sockets_without_hidden_candidates_or_of_another_kind_emit_nothing() -> None:
    """
    An UNRESOLVED_INPUT with no hidden candidates (nothing registered) and an empty class list are not refused here.
    """
    topology = SpellLocalTopology("consumer", [
        _socket(SocketKind.UNRESOLVED_INPUT),
        _socket(SocketKind.NORMAL, ("english-sid",), param_name="greeters", position=1, collection=True),
        _socket(SocketKind.AMBIGUOUS_INPUT, param_name="other", position=2),
    ])
    issues: List[SpellValidationIssue] = []
    HiddenProviderStrategy().validate(_context(topology, _BookStub({}), issues, _requirements(_annotated())))
    assert issues == []


def test_class_bound_only_under_a_protocol_frame_is_refused_naming_the_address_and_the_lookup() -> None:
    """One HIDDEN_PROVIDER error: the exact text, the error severity and the details payload."""
    topology = SpellLocalTopology("consumer", [_socket(SocketKind.UNRESOLVED_INPUT, ("english-sid",))])
    book = _BookStub({"english-sid": _candidate(Greeter, "english")})
    issues: List[SpellValidationIssue] = []
    HiddenProviderStrategy().validate(_context(topology, book, issues, _requirements(_annotated())))

    assert len(issues) == 1
    issue = issues[0]
    assert issue.severity == "error" and issue.code == "HIDDEN_PROVIDER"
    assert issue.message == (
        "Parameter 'greeter' on spell 'Host' expects English, but a class lookup reaches English only where it is "
        "bound bare (no spellframe, the default binding), and English is bound only under a spellframe: English at "
        "(spellframe='Greeter', binding_name='english') - use SpellMap(spellframe=Greeter, binding_name='english'). "
        "Ask for it where it is bound - the SpellMap shown, as the parameter's default, or a Greeter annotation while "
        "that spell is the only one bound under Greeter - or bind English bare."
    )
    assert issue.details["lookup"] == "annotation"
    assert issue.details["expected_type"] == "English"
    assert issue.details["dependency_key"] == ("english", "__default__")
    assert issue.details["candidates"] == [{
        "spell_id": "english-sid", "spell_name": "English", "spellframe": "Greeter", "spellframe_kind": "contract",
        "binding_name": "english", "use": "SpellMap(spellframe=Greeter, binding_name='english')",
    }]


def test_spellmap_class_lookup_miss_is_refused_in_the_spellmap_form() -> None:
    """A SPELLMAP_DEFAULT parameter reads the SpellMap as written and the address it should point at."""
    topology = SpellLocalTopology("consumer", [_socket(SocketKind.UNRESOLVED_INPUT, ("english-sid",))])
    book = _BookStub({"english-sid": _candidate("greeters", "english")})
    param = SimpleNamespace(name="greeter", annotation=None, di_shape=ParameterDIShape.SPELLMAP_DEFAULT,
                            spellmap_default=SpellMap(English, binding_name="english"))
    issues: List[SpellValidationIssue] = []
    HiddenProviderStrategy().validate(_context(topology, book, issues, _requirements(param)))

    issue, = issues
    assert issue.code == "HIDDEN_PROVIDER"
    assert issue.message == (
        "Parameter 'greeter' on spell 'Host' has the default SpellMap(English, binding_name='english'), a class lookup "
        "that reaches English only where it is bound bare under the binding name 'english', but English is bound only "
        "where that lookup does not reach: English at (spellframe='greeters', binding_name='english') - use "
        "SpellMap(spellframe='greeters', binding_name='english'). Point the SpellMap at the address it means, as "
        "shown, or bind English bare under the binding name 'english'."
    )
    assert issue.details["lookup"] == "spellmap"
    assert issue.details["spellmap"] == "SpellMap(English, binding_name='english')"


def test_borrowed_candidate_is_named_with_its_address_and_spellmap_as_an_owned_one_is() -> None:
    """
    Regression (STEP 3 of patch hidden_provider_2026_11_07): a hidden candidate that is a copy the Book borrows from a
    peer conduit - in the pool Phase 3 reads, but not among the own spells `find_spell_by_spell_id` answers for - was
    rendered `spell id <id>`, with no address and no SpellMap. It is found among the borrowed copies, peer by peer,
    and the report reads exactly as it does for the same English owned by the Book.
    """
    topology = SpellLocalTopology("consumer", [_socket(SocketKind.UNRESOLVED_INPUT, ("english-sid",))])
    owning = _BookStub({"english-sid": _candidate(Greeter, "english")})
    borrowing = _BookStub({}, borrowed={"peer-a": {}, "peer-b": {"english-sid": _candidate(Greeter, "english")}})
    reports = []
    for book in (owning, borrowing):
        issues: List[SpellValidationIssue] = []
        HiddenProviderStrategy().validate(_context(topology, book, issues, _requirements(_annotated())))
        issue, = issues
        reports.append((issue.message, issue.details["candidates"]))
    assert reports[1] == reports[0]
    assert reports[1][0] == (
        "Parameter 'greeter' on spell 'Host' expects English, but a class lookup reaches English only where it is "
        "bound bare (no spellframe, the default binding), and English is bound only under a spellframe: English at "
        "(spellframe='Greeter', binding_name='english') - use SpellMap(spellframe=Greeter, binding_name='english'). "
        "Ask for it where it is bound - the SpellMap shown, as the parameter's default, or a Greeter annotation while "
        "that spell is the only one bound under Greeter - or bind English bare."
    )


@pytest.mark.parametrize("in_a_book", [True, False], ids=["book-without-the-id", "stand-in-without-a-book"])
def test_candidate_found_nowhere_renders_by_id_and_the_remedy_names_no_spellmap(in_a_book: bool) -> None:
    """
    Regression (STEP 3 of patch hidden_provider_2026_11_07): a candidate neither the Book's own spells nor its
    borrowed copies hold (removed between phases) renders `spell id <id>` with no lookup, and never raises. With no
    entry showing a SpellMap the remedy no longer points at "the SpellMap shown" - in the annotation form or, without
    "as shown", in the SpellMap form.
    """
    topology = SpellLocalTopology("consumer", [_socket(SocketKind.UNRESOLVED_INPUT, ("gone-sid",))])
    book = _BookStub({}, borrowed={"peer": {}}) if in_a_book else None
    spellmap = SimpleNamespace(name="greeter", annotation=None, di_shape=ParameterDIShape.SPELLMAP_DEFAULT,
                               spellmap_default=SpellMap(English))
    messages = []
    for param in (_annotated(), spellmap):
        issues: List[SpellValidationIssue] = []
        HiddenProviderStrategy().validate(_context(topology, book, issues, _requirements(param)))
        issue, = issues
        messages.append(issue.message)
    assert messages == [
        "Parameter 'greeter' on spell 'Host' expects English, but a class lookup reaches English only where it is "
        "bound bare (no spellframe, the default binding), and English is bound only under a spellframe or a binding "
        "name: spell id gone-sid. Ask for it where it is bound, or bind English bare.",
        "Parameter 'greeter' on spell 'Host' has the default SpellMap(English), a class lookup that reaches English "
        "only where it is bound bare under the default binding, but English is bound only where that lookup does not "
        "reach: spell id gone-sid. Point the SpellMap at the address it means, or bind English bare.",
    ]


def test_candidate_found_nowhere_beside_a_found_one_renders_by_id_and_the_remedy_counts_the_shown_spellmap() -> None:
    """
    A removed candidate beside a found one: the removed one reads `spell id <id>` (first - None sorts first), the
    found one its address and SpellMap, and the remedy points at the one SpellMap shown.
    """
    topology = SpellLocalTopology("consumer", [_socket(SocketKind.UNRESOLVED_INPUT, ("gone-sid", "english-sid"))])
    book = _BookStub({"english-sid": _candidate(None, "v1")})
    issues: List[SpellValidationIssue] = []
    HiddenProviderStrategy().validate(_context(topology, book, issues, _requirements(_annotated())))
    issue, = issues
    assert issue.message == (
        "Parameter 'greeter' on spell 'Host' expects English, but a class lookup reaches English only where it is "
        "bound bare (no spellframe, the default binding), and English is bound only under a binding name: spell id "
        "gone-sid; English at (spellframe=None, binding_name='v1') - use SpellMap(English, binding_name='v1'). Ask "
        "for it where it is bound - the SpellMap shown, as the parameter's default - or bind English bare."
    )


def test_missing_requirements_render_the_parameter_name_as_the_type() -> None:
    """Without Phase-1 requirements the annotation form names the parameter instead of failing."""
    topology = SpellLocalTopology("consumer", [_socket(SocketKind.UNRESOLVED_INPUT, ("english-sid",))])
    issues: List[SpellValidationIssue] = []
    HiddenProviderStrategy().validate(_context(topology, _BookStub({"english-sid": _candidate("greeters", None)}),
                                               issues, None))
    assert issues[0].message.startswith("Parameter 'greeter' on spell 'Host' expects greeter, but a class lookup")


def test_one_issue_per_refused_socket_in_socket_order() -> None:
    """Two hidden sockets give two errors, the second for its own parameter."""
    topology = SpellLocalTopology("consumer", [
        _socket(SocketKind.UNRESOLVED_INPUT, ("english-sid",)),
        _socket(SocketKind.UNRESOLVED_INPUT, ("english-sid",), param_name="backup", position=1),
    ])
    book = _BookStub({"english-sid": _candidate("greeters", None)})
    issues: List[SpellValidationIssue] = []
    HiddenProviderStrategy().validate(_context(topology, book, issues,
                                               _requirements(_annotated(), _annotated("backup"))))
    assert [issue.details["parameter_name"] for issue in issues] == ["greeter", "backup"]


def test_cancelled_context_raises_before_reading() -> None:
    """A set cancellation event stops the strategy."""
    class _Cancel:
        is_set = True

        def throw_if_set(self) -> None:
            raise RuntimeError("cancelled")

    issues: List[SpellValidationIssue] = []
    with pytest.raises(RuntimeError, match="cancelled"):
        HiddenProviderStrategy().validate(_context(None, None, issues, cancel_event=_Cancel()))
