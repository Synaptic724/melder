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


def test_bind_conjure_and_meld_function_spell_unique() -> None:
    """
    Purpose:
        Validate bind -> conjure -> meld for a function spell using unique existence.
    Contract:
        - The first meld call executes the function.
        - Existence.unique reuses the same instance on subsequent melds.
    Returns:
        None.
    Raises:
        AssertionError: If the function is not invoked or reuse fails.
    """
    calls: list[str] = []

    def _factory() -> object:
        """
        Purpose:
            Provide a function spell that creates a new object.
        Contract:
            Records each invocation and returns a unique object.
        Returns:
            object: Newly created object instance.
        """
        calls.append("called")
        return object()

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spell_id = spellbook.bind(
        spell=_factory,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld(spell=spell_id)
        second = conduit.meld(spell=spell_id)
        assert first is second
        assert calls == ["called"]
    finally:
        conduit.cleanup()
