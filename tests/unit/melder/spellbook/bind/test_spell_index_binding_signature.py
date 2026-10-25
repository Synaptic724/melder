"""
Unit tests: a SpellIndex keeps its first version's binding and admits only a version bound the same way.

WHY THIS EXISTS. STORY-2026-10-17-notch_moves_signature_by_incoming_key_only, on the owner's go of 2026-10-25 ("if
you want to use notch you gotta use the signature that was used originally and spell_index would retain that
validation check"). The binding is the kind of spellframe (none, a string category or a Protocol) and the
case-insensitive address it gives; `check_admits` is the check `bind_inactive` and `add_to_spell_index` run.
"""

from types import SimpleNamespace
from typing import Any, Protocol

import pytest

from melder.aether.spellbook.bind.spell_index import SpellIndex


class Greeter(Protocol):
    """A Protocol spellframe."""

    def greet(self) -> str:
        """Return a greeting."""
        ...


def _spell(spellframe: Any, spell_name: str, binding_name: Any, spell_id: str = "sid-staged") -> Any:
    """
    Purpose:
        A stand-in carrying the four Spell fields `check_admits` reads.

    Args:
        spellframe (Any): The version's spellframe (None, a string or a Protocol).
        spell_name (str): Its name.
        binding_name (Any): Its binding name, or None.
        spell_id (str): Its spell_id.

    Returns:
        Any: An object with `spellframe`, `spell_name`, `binding_name` and `spell_id`.
    """
    return SimpleNamespace(spellframe=spellframe, spell_name=spell_name, binding_name=binding_name, spell_id=spell_id)


@pytest.mark.parametrize(
    "spellframe, spell_name, binding_name, expected",
    [
        (None, "Report", None, ("none", "report", "__default__")),
        (None, "Report", "Main", ("none", "report", "main")),
        ("Reports", "Report", "Main", ("category", "reports", "main")),
        (Greeter, "EnglishGreeter", "English", ("contract", "greeter", "english")),
    ],
    ids=["bare", "bare_named_binding", "category", "protocol"],
)
def test_signature_of_gives_the_kind_and_the_normalized_address(
        spellframe: Any, spell_name: str, binding_name: Any, expected: Any,
) -> None:
    """
    Purpose:
        The signature is the spellframe's kind and the address `Spell._key` normalizes to.

    Returns:
        None.
    """
    assert SpellIndex.signature_of(spellframe=spellframe, spell_name=spell_name, binding_name=binding_name) == expected


def test_for_binding_records_the_signature_and_the_first_member() -> None:
    """
    Purpose:
        An index built for a binding keeps that binding's signature and starts with its first member selected.

    Returns:
        None.
    """
    index = SpellIndex.for_binding("sid-first", spellframe=Greeter, spell_name="EnglishGreeter", binding_name="english")

    assert index.binding_signature == ("contract", "greeter", "english")
    assert index.selected_spell_id == "sid-first"
    assert index.spells_in_index() == {"sid-first"}


@pytest.mark.parametrize(
    "spellframe, spell_name, binding_name",
    [(Greeter, "FrenchGreeter", "ENGLISH"), (Greeter, "FrenchGreeter", "english")],
    ids=["other_case", "same_case"],
)
def test_check_admits_a_version_bound_the_same_way(spellframe: Any, spell_name: str, binding_name: Any) -> None:
    """
    Purpose:
        A version with the index's kind and address is admitted, the case of its names aside.

    Returns:
        None.
    """
    index = SpellIndex.for_binding("sid-first", spellframe=Greeter, spell_name="EnglishGreeter", binding_name="english")

    index.check_admits(_spell(spellframe, spell_name, binding_name), verb="bind_inactive")


@pytest.mark.parametrize(
    "spellframe, spell_name, binding_name, shown",
    [
        (Greeter, "FrenchGreeter", "french", "binding_name 'french'"),
        ("Greeter", "FrenchGreeter", "english", "the string spellframe 'Greeter'"),
        (None, "Greeter", "english", "no spellframe"),
    ],
    ids=["binding_name", "category_kind", "bare_kind"],
)
def test_check_admits_refuses_a_version_bound_another_way(
        spellframe: Any, spell_name: str, binding_name: Any, shown: str,
) -> None:
    """
    Purpose:
        A version with another address or another kind of spellframe is refused with a ValueError that names the
        verb, both bindings and the remedy.

    Returns:
        None.
    """
    index = SpellIndex.for_binding("sid-first", spellframe=Greeter, spell_name="EnglishGreeter", binding_name="english")

    with pytest.raises(ValueError) as refused:
        index.check_admits(_spell(spellframe, spell_name, binding_name), verb="add_to_spell_index")

    message = str(refused.value)
    assert message.startswith("add_to_spell_index refused: SpellIndex ")
    assert "keeps the binding its first version was bound with" in message
    assert "the Protocol spellframe Greeter and binding_name 'english'" in message
    assert shown in message
    assert "is a new spell" in message


def test_check_admits_refuses_on_an_index_built_without_a_binding() -> None:
    """
    Purpose:
        An index built directly, without a binding, admits nothing: Melder builds every index it stages onto with
        one, so reaching this is a Melder bug.

    Returns:
        None.
    """
    index = SpellIndex("sid-first")

    assert index.binding_signature is None
    with pytest.raises(RuntimeError, match="records no binding"):
        index.check_admits(_spell(None, "Report", None), verb="bind_inactive")
