from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook


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


def test_bind_conjure_and_meld_method_spell_many() -> None:
    """
    Purpose:
        Validate bind -> conjure -> meld for a bound method spell.
    Contract:
        - The bound method is invoked for each meld call.
        - Existence.many returns a new object per invocation.
    Returns:
        None.
    Raises:
        AssertionError: If method calls or instance creation is incorrect.
    """
    class _Service:
        """
        Purpose:
            Provide a class with a bound method for integration binding.
        Contract:
            The method returns a new object each call and tracks call count.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the service call counter.
            Contract:
                Starts the call count at zero.
            Returns:
                None.
            """
            self.calls: int = 0

        def build(self) -> object:
            """
            Purpose:
                Produce a new object instance for each call.
            Contract:
                Increments call count and returns a unique object.
            Returns:
                object: Newly created object instance.
            """
            self.calls += 1
            return object()

    service = _Service()

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spell_id = spellbook.bind(
        spell=service.build,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld(spell=spell_id)
        second = conduit.meld(spell=spell_id)
        assert first is not second
        assert service.calls == 2
    finally:
        conduit.cleanup()
