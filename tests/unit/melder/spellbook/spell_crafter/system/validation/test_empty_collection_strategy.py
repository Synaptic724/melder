"""
Unit contracts for `EmptyCollectionStrategy`'s texts: an empty required `list[Class]` whose class is bound only under a
spellframe or a binding name names where (patch hidden_provider_2026_11_07), at the severity its Book's mode decides;
without hidden candidates the texts stay byte for byte as before.
"""
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Protocol

import pytest

from melder.aether.spellbook.configuration.system_state import SystemState
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.aether.spellbook.spell_compiler.system.validation.empty_collection_strategy import (
    EmptyCollectionStrategy,
)
from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import (
    SpellLocalTopology,
    SpellSocketDescriptor,
)
from melder.aether.spellbook.spellframe_kind.spellframe_kind import SpellframeKind


class Greeter(Protocol):
    """The Protocol frame English is bound under."""

    def greet(self) -> str: ...


def _consumer(system_state: SystemState) -> SimpleNamespace:
    """The consumer spell, its Book configured in the given mode."""
    book = SimpleNamespace(_aetheric_frame_configuration=SimpleNamespace(system_state=system_state))
    return SimpleNamespace(spell_name="Host", _spellbook=book)


def _framed_english() -> SimpleNamespace:
    """English bound under the Protocol frame Greeter as 'english'."""
    return SimpleNamespace(spell_name="English", spellframe=Greeter, spellframe_kind=SpellframeKind.contract,
                           binding_name="english")


def _run(system_state: SystemState, hidden: tuple, lookup_extra: Optional[Dict[str, Any]] = None) -> SystemDiagnostic:
    """Run the strategy over one consumer whose required `greeters` collection wired nothing."""
    topology = SpellLocalTopology("consumer", [SpellSocketDescriptor(
        spell_id="consumer", param_name="greeters", position=0, socket_kind=SocketKind.NORMAL, is_collection=True,
        is_optional=False, target_spell_ids=(), dependency_key=("english", "__default__"), hidden_spell_ids=hidden,
    )])
    spell_lookup: Dict[str, Any] = {"consumer": _consumer(system_state)}
    spell_lookup.update(lookup_extra or {})
    diagnostics: List[SystemDiagnostic] = []
    EmptyCollectionStrategy().run(
        index=SimpleNamespace(nodes={"consumer": object()}),
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=SimpleNamespace(get_local_topology_by_id=lambda spell_id: topology),
        spell_lookup=spell_lookup,
        diagnostics=diagnostics,
        cancel_event=None,
    )
    diagnostic, = diagnostics
    return diagnostic


@pytest.mark.parametrize(
    ("system_state", "severity", "expected"),
    [
        pytest.param(SystemState.automatic, SystemDiagnosticSeverity.ERROR, (
            "Spell 'Host' parameter 'greeters' is a required list[...] dependency, but no provider is wired into it. "
            "Bind at least one implementation under its frame, make the parameter optional, or run the book in "
            "dynamic mode if members arrive via contracts."
        ), id="automatic"),
        pytest.param(SystemState.dynamic, SystemDiagnosticSeverity.WARNING, (
            "Spell 'Host' parameter 'greeters' is a required list[...] dependency, but no provider is wired into it. "
            "An empty list will be injected at construction; bind implementations under its frame or add them via a "
            "post-conjure contract to populate it."
        ), id="dynamic"),
    ],
)
def test_empty_collection_without_hidden_candidates_keeps_its_text(system_state: SystemState,
                                                                    severity: SystemDiagnosticSeverity,
                                                                    expected: str) -> None:
    """Nothing bound anywhere: the texts and details are exactly those before 2026-11-07."""
    diagnostic = _run(system_state, ())
    assert diagnostic.code == "collection_socket_no_providers"
    assert diagnostic.severity is severity
    assert diagnostic.message == expected
    assert diagnostic.details == {"spell_id": "consumer", "param_name": "greeters"}


@pytest.mark.parametrize(
    ("system_state", "severity", "tail"),
    [
        pytest.param(SystemState.automatic, SystemDiagnosticSeverity.ERROR,
                     " Gather it where it is bound, as shown, bind English bare, or make the parameter optional.",
                     id="automatic"),
        pytest.param(SystemState.dynamic, SystemDiagnosticSeverity.WARNING,
                     " An empty list will be injected at construction; gather it where it is bound, as shown, or bind "
                     "English bare to populate it.", id="dynamic"),
    ],
)
def test_empty_class_list_names_where_its_class_is_bound(system_state: SystemState,
                                                          severity: SystemDiagnosticSeverity, tail: str) -> None:
    """
    Regression (patch hidden_provider_2026_11_07): "Bind at least one implementation under its frame" sent the user
    the wrong way when the class IS bound - under a spellframe, where `list[Class]` does not gather it. The text now
    names the address and the list that gathers it, at the mode's severity (D3: dynamic stays WARNING and `[]`).
    """
    diagnostic = _run(system_state, ("english-sid",), {"english-sid": _framed_english()})
    assert diagnostic.severity is severity
    assert diagnostic.message == (
        "Spell 'Host' parameter 'greeters' is a required list[...] dependency, but no provider is wired into it: "
        "list[English] gathers English only where it is bound bare (no spellframe, the default binding), and English "
        "is bound only under a spellframe: English at (spellframe='Greeter', binding_name='english') - use "
        "list[Greeter]." + tail
    )
    assert diagnostic.details["hidden_candidates"] == [{
        "spell_id": "english-sid", "spell_name": "English", "spellframe": "Greeter", "spellframe_kind": "contract",
        "binding_name": "english", "use": "list[Greeter]",
    }]


def test_hidden_candidate_outside_the_lookup_keeps_the_plain_text() -> None:
    """A recorded id the scope's spell lookup does not hold names nothing, so the text stays the plain one."""
    diagnostic = _run(SystemState.automatic, ("gone-sid",))
    assert "Bind at least one implementation under its frame" in diagnostic.message
    assert "hidden_candidates" not in diagnostic.details
