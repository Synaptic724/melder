"""
Unit tests for `AmbiguousProviderStrategy` (2026-10-04): the Phase-4 refusal of a single typed parameter that
several registered spells provide, driven from the AMBIGUOUS_INPUT sockets Phase 3 records.
"""
from types import SimpleNamespace
from typing import Any, List, Optional

import pytest

from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import (
    SpellLocalTopology,
    SpellSocketDescriptor,
)
from melder.aether.spellbook.spell_compiler.validation.spell_validation_context import SpellValidationContext
from melder.aether.spellbook.spell_compiler.validation.spell_validation_issue import SpellValidationIssue
from melder.aether.spellbook.spell_compiler.validation.strategies.ambiguous_provider_strategy import (
    AmbiguousProviderStrategy,
)


class _Profile:
    """The annotated type of the consumer parameter."""


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

    def __init__(self, *, spell_id: str, spell_name: str, topology: Optional[SpellLocalTopology]) -> None:
        """Wire the stub."""
        self.spell_id = spell_id
        self.spell_name = spell_name
        self.spell_index = SimpleNamespace(selected_spell_id=spell_id)
        self._spell_system_states = _StatesStub(topology)


class _CandidateStub:
    """A provider spell as the spellbook returns it."""

    def __init__(self, spell_name: str, spellframe: Any, binding_name: Optional[str]) -> None:
        """Hold the address parts."""
        self.spell_name = spell_name
        self.spellframe = spellframe
        self.binding_name = binding_name


class _BookStub:
    """A spellbook that answers `find_spell_by_id` from a dict."""

    def __init__(self, spells: dict) -> None:
        """Hold the lookup."""
        self._spells = spells

    def find_spell_by_id(self, spell_id: str):
        """Return the candidate or None."""
        return self._spells.get(spell_id)


def _socket(kind: SocketKind, references: tuple = ()) -> SpellSocketDescriptor:
    """One `profile` socket of the given kind."""
    return SpellSocketDescriptor(
        spell_id="consumer", param_name="profile", position=0, socket_kind=kind, is_collection=False,
        is_optional=False, target_spell_ids=(), dependency_key=("profile", "__default__"),
        referenced_spell_ids=references,
    )


def _requirements() -> Any:
    """Phase-1 requirements naming `profile: _Profile`."""
    return SimpleNamespace(parameters=[SimpleNamespace(name="profile", annotation=_Profile)])


def _context(spell: _SpellStub, spellbook: Any, issues: List[SpellValidationIssue], requirements: Any = None) -> SpellValidationContext:
    """Build a validation context around the stubs."""
    return SpellValidationContext(
        spell=spell, spellbook=spellbook, requirements=requirements, symbolic_graph=None,
        resolution_frame=None, cancel_event=None, issues=issues,
    )


def test_init_sets_name_and_description() -> None:
    """The strategy publishes a stable name."""
    strategy = AmbiguousProviderStrategy()
    assert strategy.name == "ambiguous_provider"
    assert "several" in strategy.description


def test_no_topology_emits_nothing() -> None:
    """A spell without a Phase-3 topology (a stand-in) yields no issue."""
    issues: List[SpellValidationIssue] = []
    AmbiguousProviderStrategy().validate(_context(_SpellStub(spell_id="c", spell_name="C", topology=None), None, issues))
    assert issues == []


def test_other_socket_kinds_emit_nothing() -> None:
    """NORMAL, UNRESOLVED_INPUT and OVERRIDE_REQUIRED sockets are not this strategy's business."""
    topology = SpellLocalTopology(spell_id="consumer", sockets=[
        _socket(SocketKind.NORMAL), _socket(SocketKind.UNRESOLVED_INPUT), _socket(SocketKind.OVERRIDE_REQUIRED, ("x",)),
    ])
    issues: List[SpellValidationIssue] = []
    AmbiguousProviderStrategy().validate(_context(_SpellStub(spell_id="c", spell_name="C", topology=topology), None, issues))
    assert issues == []


def test_ambiguous_socket_names_every_candidate_address_and_the_remedies() -> None:
    """One AMBIGUOUS_PROVIDER error: parameter, expected type, both addresses (ordered), three remedies, details."""
    topology = SpellLocalTopology(spell_id="consumer", sockets=[_socket(SocketKind.AMBIGUOUS_INPUT, ("id-b", "id-a"))])
    book = _BookStub({
        "id-a": _CandidateStub("ScanProfile", "agents", "ScanProfile"),
        "id-b": _CandidateStub("ScanProfile", "artificial_intelligence_tools", "ScanProfile"),
    })
    issues: List[SpellValidationIssue] = []
    spell = _SpellStub(spell_id="consumer", spell_name="MCPScanner", topology=topology)
    AmbiguousProviderStrategy().validate(_context(spell, book, issues, requirements=_requirements()))

    assert len(issues) == 1
    issue = issues[0]
    assert issue.severity == "error" and issue.code == "AMBIGUOUS_PROVIDER"
    assert issue.message.startswith("Parameter 'profile' on spell 'MCPScanner' expects _Profile, but 2 registered spells provide it: ")
    assert issue.message.index("spellframe='agents'") < issue.message.index("spellframe='artificial_intelligence_tools'")
    assert "SpellMap(spellframe=..., binding_name=...)" in issue.message
    assert "override={'profile': ...}" in issue.message
    assert "bind only one provider of this type" in issue.message
    assert issue.details["spell_id"] == "consumer" and issue.details["parameter_name"] == "profile"
    assert issue.details["expected_type"] == "_Profile"
    assert [c["spell_id"] for c in issue.details["candidates"]] == ["id-a", "id-b"]
    assert issue.details["candidates"][0] == {
        "spell_id": "id-a", "spell_name": "ScanProfile", "spellframe": "agents", "binding_name": "ScanProfile",
    }


def test_protocol_frame_and_bare_binding_render_by_name_and_none() -> None:
    """A Protocol frame renders by `__name__`; a bare binding renders spellframe=None, binding_name=None."""
    class IRepo:
        """A frame."""
    topology = SpellLocalTopology(spell_id="consumer", sockets=[_socket(SocketKind.AMBIGUOUS_INPUT, ("one", "two"))])
    book = _BookStub({"one": _CandidateStub("RepoA", IRepo, None), "two": _CandidateStub("RepoB", None, None)})
    issues: List[SpellValidationIssue] = []
    AmbiguousProviderStrategy().validate(_context(_SpellStub(spell_id="consumer", spell_name="Svc", topology=topology), book, issues))
    message = issues[0].message
    assert "RepoA at (spellframe='IRepo', binding_name=None)" in message
    assert "RepoB at (spellframe=None, binding_name=None)" in message
    # without Phase-1 requirements the expected type falls back to the parameter name
    assert "expects profile," in message


def test_unknown_candidate_renders_by_id_and_does_not_raise() -> None:
    """A candidate the spellbook no longer finds is rendered by id; a missing spellbook renders all by id."""
    topology = SpellLocalTopology(spell_id="consumer", sockets=[_socket(SocketKind.AMBIGUOUS_INPUT, ("gone", "there"))])
    book = _BookStub({"there": _CandidateStub("Impl", "frame", "name")})
    issues: List[SpellValidationIssue] = []
    AmbiguousProviderStrategy().validate(_context(_SpellStub(spell_id="consumer", spell_name="Svc", topology=topology), book, issues))
    assert "spell id gone" in issues[0].message and "Impl at (spellframe='frame', binding_name='name')" in issues[0].message
    issues.clear()
    AmbiguousProviderStrategy().validate(_context(_SpellStub(spell_id="consumer", spell_name="Svc", topology=topology), None, issues))
    assert issues[0].message.count("spell id ") == 2


def test_cancelled_context_raises_before_reading() -> None:
    """A set cancellation event stops the strategy."""
    class _Cancel:
        is_set = True
        def throw_if_set(self) -> None:
            raise RuntimeError("cancelled")
    issues: List[SpellValidationIssue] = []
    context = SpellValidationContext(
        spell=_SpellStub(spell_id="c", spell_name="C", topology=None), spellbook=None, requirements=None,
        symbolic_graph=None, resolution_frame=None, cancel_event=_Cancel(), issues=issues,
    )
    with pytest.raises(RuntimeError, match="cancelled"):
        AmbiguousProviderStrategy().validate(context)


def test_socket_kind_member_exists_and_is_distinct() -> None:
    """The enum carries AMBIGUOUS_INPUT beside the other four kinds."""
    assert SocketKind.AMBIGUOUS_INPUT is not SocketKind.UNRESOLVED_INPUT
    assert {k.name for k in SocketKind} == {"NORMAL", "SPELL_CONTRACT", "OVERRIDE_REQUIRED", "UNRESOLVED_INPUT", "AMBIGUOUS_INPUT"}
