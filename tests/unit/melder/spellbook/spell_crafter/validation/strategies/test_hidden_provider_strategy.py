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
    """A spellbook that answers `find_spell_by_spell_id` from a dict, as the Book does for its own spells."""

    def __init__(self, spells: dict) -> None:
        """Hold the lookup."""
        self._spells = spells

    def find_spell_by_spell_id(self, spell_id: str) -> Any:
        """Return the candidate or None."""
        return self._spells.get(spell_id)


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
    """An UNRESOLVED_INPUT with no hidden candidates (nothing registered) and an empty class list are not refused here."""
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


def test_candidate_the_book_cannot_find_renders_by_id_and_never_raises() -> None:
    """A removed spell or a borrowed copy (which find_spell_by_spell_id does not consult) renders `spell id <id>`."""
    topology = SpellLocalTopology("consumer", [_socket(SocketKind.UNRESOLVED_INPUT, ("borrowed-sid", "english-sid"))])
    book = _BookStub({"english-sid": _candidate(None, "v1")})
    issues: List[SpellValidationIssue] = []
    HiddenProviderStrategy().validate(_context(topology, book, issues, _requirements(_annotated())))
    issue, = issues
    assert "spell id borrowed-sid; English at (spellframe=None, binding_name='v1') - use SpellMap(English, " \
           "binding_name='v1')" in issue.message
    issues.clear()
    HiddenProviderStrategy().validate(_context(topology, None, issues, _requirements(_annotated())))
    assert issues[0].message.count("spell id ") == 2


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
