"""Integration coverage for human and machine identities on public meld facades."""

import melder as md
import pytest


class MyService:
    """Minimal service resolved through human and machine identity lanes."""


@pytest.fixture(autouse=True)
def reset_runtime_singletons() -> None:
    """Reset and rebind the shared runtime before and after this test module."""
    md.Aether._reset_singleton_for_tests()
    aether = md.Aether()
    md.Spellbook._aether = aether
    md.Conduit._aether = aether
    yield
    md.Aether._reset_singleton_for_tests()
    aether = md.Aether()
    md.Spellbook._aether = aether
    md.Conduit._aether = aether


def test_conduit_meld_separates_human_name_and_machine_id() -> None:
    """
    Verify human SpellNames and explicit SHA identities resolve one registration.

    Contract:
        Positional and `spell=` strings are human names, `spell_id=` is the
        machine lane, and the two identity inputs cannot be combined.
    """
    book = md.Spellbook(aetheric_frame="human-meld-identity-integration")
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

        assert isinstance(positional, MyService)
        assert positional is keyword is machine
        with pytest.raises(ValueError, match="either `spell` or `spell_id`"):
            conduit.meld("MyService", spell_id=spell_id)
    finally:
        conduit.cleanup()
        book.cleanup()
