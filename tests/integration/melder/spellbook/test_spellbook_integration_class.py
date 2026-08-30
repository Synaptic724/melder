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


def test_bind_conjure_and_meld_class_spell_unique() -> None:
    """
    Purpose:
        Validate bind -> conjure -> meld for a class spell using unique existence.
    Contract:
        - Binding registers a spell id for the class.
        - Conjure resolves the spell successfully.
        - Unique existence reuses the same instance within the conduit.
    Returns:
        None.
    Raises:
        AssertionError: If instance reuse or binding fails.
    """
    class _Service:
        """
        Purpose:
            Provide a simple class spell for integration binding.
        Contract:
            Constructs without arguments and exposes a stable marker.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the service with a stable marker.
            Contract:
                Sets a marker value for assertions.
            Returns:
                None.
            """
            self.marker = "alpha"

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spell_id = spellbook.bind(
        spell=_Service,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld(spell_id=spell_id)
        second = conduit.meld(spell_id=spell_id)
        assert isinstance(first, _Service)
        assert first.marker == "alpha"
        assert first is second
    finally:
        conduit.cleanup()
