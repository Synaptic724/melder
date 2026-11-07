"""
Unit contracts for `UnresolvedInputError`'s text: "nothing registered provides it" only when nothing does; when the
expected class is bound only under a spellframe or a binding name, the error names each address and the lookup that
reaches it, found live in the consumer's pool (patch hidden_provider_2026_11_07).
"""
from types import SimpleNamespace
from typing import Any, Dict, Optional, Protocol

import pytest

from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import (
    SpellLocalTopology,
    SpellSocketDescriptor,
)
from melder.aether.spellbook.spell_types.spell_types import SpellType
from melder.aether.spellbook.spellframe_kind.spellframe_kind import SpellframeKind
from melder.utilities.custom_exceptions.unresolved_input_error import UnresolvedInputError


class Greeter(Protocol):
    """A Protocol frame and a Protocol annotation."""

    def greet(self) -> str: ...


class English:
    """The class the consumer asks for."""


class Host:
    """Consumer asking for English by class and for a second, unregistered value."""

    def __init__(self, greeter: English, extra: int) -> None:
        """Hold both."""
        self.greeter = greeter
        self.extra = extra


class ByProtocol:
    """Consumer asking by the Protocol: a contract lookup, never a class lookup."""

    def __init__(self, greeter: Greeter) -> None:
        """Hold it."""
        self.greeter = greeter


def _pooled(spell_id: str, spellframe: Any, binding_name: Optional[str], *, spell_name: str = "English",
            spell_type: SpellType = SpellType.SPELL) -> SimpleNamespace:
    """A pooled spell stub with the bind-time fields the failure path reads."""
    if spellframe is None:
        kind = SpellframeKind.none
    elif isinstance(spellframe, str):
        kind = SpellframeKind.category
    else:
        kind = SpellframeKind.contract
    return SimpleNamespace(spell=English, spell_name=spell_name, spellframe=spellframe, spellframe_kind=kind,
                           binding_name=binding_name, spell_type=spell_type,
                           spell_index=SimpleNamespace(selected_spell_id=spell_id))


def _consumer(consumer: type, pool: Dict[str, Any], *params: str) -> SimpleNamespace:
    """A consumer spell whose topology marks `params` UNRESOLVED_INPUT, over the given pool."""
    sockets = [
        SpellSocketDescriptor(
            spell_id="consumer", param_name=name, position=position, socket_kind=SocketKind.UNRESOLVED_INPUT,
            is_collection=False, is_optional=False, target_spell_ids=(), dependency_key=(name, "__default__"),
        )
        for position, name in enumerate(params)
    ]
    topology = SpellLocalTopology("consumer", sockets)
    return SimpleNamespace(
        spell=consumer,
        spell_name=consumer.__name__,
        spell_index=SimpleNamespace(selected_spell_id="consumer"),
        _spell_system_states=SimpleNamespace(get_local_topology=lambda index: topology),
        _spellbook=SimpleNamespace(_spell_id_pool=pool),
    )


def test_unregistered_class_keeps_the_nothing_registered_text() -> None:
    """Nothing of the class anywhere: today's text, no hidden ids."""
    error = UnresolvedInputError.for_unsupplied(_consumer(Host, {}, "greeter"), ["greeter"])
    assert str(error).endswith(
        "Host.greeter expects English, but nothing registered provides it and this meld did not supply it. Supply it "
        "with override={'greeter': ...} when melding Host, a path key ending in '>greeter' (or '**greeter') when Host "
        "is built as a dependency, or bind a provider for English."
    )
    assert error.hidden_spell_ids == ()


def test_class_bound_only_under_a_frame_is_named_instead_of_nothing_registered() -> None:
    """
    Regression (patch hidden_provider_2026_11_07): English IS registered - under the Protocol frame Greeter - so
    "nothing registered provides it" misled; the error names the address and the SpellMap that reaches it, and keeps
    the override paths. A method spell named English is never a candidate for a class.
    """
    pool = {
        "english-sid": _pooled("english-sid", Greeter, "english"),
        "factory-sid": _pooled("factory-sid", "greeters", None, spell_type=SpellType.METHOD),
    }
    error = UnresolvedInputError.for_unsupplied(_consumer(Host, pool, "greeter"), ["greeter"])
    assert str(error).endswith(
        "Host.greeter expects English, but this meld did not supply it and a class lookup reaches English only where "
        "it is bound bare (no spellframe, the default binding), while English is bound only under a spellframe: "
        "English at (spellframe='Greeter', binding_name='english') - use SpellMap(spellframe=Greeter, "
        "binding_name='english'). Supply it with override={'greeter': ...} when melding Host, a path key ending in "
        "'>greeter' (or '**greeter') when Host is built as a dependency, ask for it where it is bound, as shown, or "
        "bind English bare."
    )
    assert error.hidden_spell_ids == ("english-sid",)
    assert error.expected_type == "English"


def test_bare_named_class_reads_under_a_binding_name_and_lists_the_other_missing_inputs() -> None:
    """A bare English under a binding name, and a second missing parameter still listed after the text."""
    pool = {"english-sid": _pooled("english-sid", None, "v1")}
    error = UnresolvedInputError.for_unsupplied(_consumer(Host, pool, "greeter", "extra"), ["greeter", "extra"])
    text = str(error)
    assert "English is bound only under a binding name: English at (spellframe=None, binding_name='v1') - use " \
           "SpellMap(English, binding_name='v1')." in text
    assert text.endswith(" Also not supplied: 'extra'.")
    assert error.unresolved_params == ("greeter", "extra")


def test_protocol_annotation_is_no_class_lookup_and_keeps_the_nothing_registered_text() -> None:
    """A Protocol parameter is a contract lookup: a framed spell named like it is no hidden candidate."""
    pool = {"greeter-sid": _pooled("greeter-sid", "langs", None, spell_name="Greeter")}
    error = UnresolvedInputError.for_unsupplied(_consumer(ByProtocol, pool, "greeter"), ["greeter"])
    assert "nothing registered provides it" in str(error)
    assert error.hidden_spell_ids == ()


def test_stale_plan_still_raises_runtime_error() -> None:
    """Asking for a parameter the topology does not mark unresolved is a stale plan, as before."""
    with pytest.raises(RuntimeError, match="its plan is stale"):
        UnresolvedInputError.for_unsupplied(_consumer(Host, {}, "greeter"), ["missing"])
