from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration() -> None:
    """
    Purpose:
        Ensure integration tests start with a clean Aether singleton.
    Contract:
        - Resets the Aether singleton before the test runs.
        - Rebinds Spellbook._aether and Conduit._aether to the new instance.
        - Resets the singleton again after the test for isolation.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def test_bind_conjure_and_meld_existing_creation() -> None:
    """
    Purpose:
        Validate the bind → conjure → meld integration path for an existing object.
    Contract:
        - Binding an existing instance registers a spell id.
        - Conjuring stamps owner metadata onto the bound spell.
        - Meld returns the original instance for an EXISTING_CREATION spell.
    Returns:
        None.
    Raises:
        AssertionError: If the integration flow does not behave as expected.
    """
    class _Service:
        """
        Purpose:
            Provide a simple existing object for integration binding.
        Contract:
            Holds a stable attribute to distinguish instances.
        """
        def __init__(self, value: str) -> None:
            """
            Purpose:
                Initialize the service with a stable value.
            Contract:
                Stores the provided value on the instance.
            Args:
                value: Value to store on the service.
            Returns:
                None.
            """
            self.value = value

    service = _Service("alpha")
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spell_id = spellbook.bind(
        spell=service,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        assert conduit.check_spell_id(spell_id) is True

        spell = conduit.get_spell_by_id(spell_id)
        assert spell is not None
        assert spell.owner_conduit_info == (conduit.id, conduit.name)

        resolved = conduit.meld(spell_id=spell_id)
        assert resolved is service
        assert resolved.value == "alpha"
    finally:
        conduit.cleanup()
