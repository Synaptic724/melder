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


def test_bind_conjure_and_meld_unique_reuses_instance() -> None:
    """
    Purpose:
        Validate Existence.unique reuses the same instance across meld calls.
    Contract:
        - Two meld calls return the same instance for unique spells.
    Returns:
        None.
    Raises:
        AssertionError: If the instance is not reused.
    """
    class _Service:
        """
        Purpose:
            Provide a simple class spell for unique existence testing.
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
            self.marker = "unique"

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
        first = conduit.meld(spell=spell_id)
        second = conduit.meld(spell=spell_id)
        assert first is second
        assert first.marker == "unique"
    finally:
        conduit.cleanup()


def test_bind_conjure_and_meld_many_creates_new_instances() -> None:
    """
    Purpose:
        Validate Existence.many returns a new instance per meld call.
    Contract:
        - Two meld calls return different instances for many spells.
    Returns:
        None.
    Raises:
        AssertionError: If instances are reused.
    """
    class _Service:
        """
        Purpose:
            Provide a simple class spell for many existence testing.
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
            self.marker = "many"

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spell_id = spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld(spell=spell_id)
        second = conduit.meld(spell=spell_id)
        assert first is not second
        assert first.marker == "many"
        assert second.marker == "many"
    finally:
        conduit.cleanup()
