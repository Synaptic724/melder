"""Prove human SpellName and explicit machine-ID public meld behavior."""

import melder as md


class MyService:
    """Minimal service whose class name is the human lookup value under test."""


def test_positional_human_spell_name_and_explicit_id_behavior() -> None:
    """
    Prove positional strings resolve names while `spell_id=` preserves IDs.

    Contract:
        Positional and `spell=` strings resolve the human name. The exact SHA
        returned by bind resolves only through explicit `spell_id=`.
    """
    book = md.Spellbook(aetheric_frame="meld-human-name-string-experiment")
    spell_id = book.bind(
        spell=MyService,
        existence="unique",
        binding_name="primary",
    )
    conduit = book.conjure()
    try:
        positional = conduit.meld("MyService", binding_name="primary")
        keyword = conduit.meld(spell="MyService", binding_name="primary")
        machine = conduit.meld(spell_id=spell_id)
        assert positional is keyword is machine
        print("human and machine identity lanes resolved one live service")
    finally:
        conduit.cleanup()
        book.cleanup()
