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


def test_bind_conjure_and_meld_class_spell_many() -> None:
    """
    Purpose:
        Validate bind -> conjure -> meld for a class spell using many existence.
    Contract:
        - Each meld call constructs a fresh instance.
        - Existence.many does not reuse instances across melds.
    Returns:
        None.
    Raises:
        AssertionError: If instances are reused or constructors are not invoked.
    """
    init_calls: list[str] = []

    class _Service:
        """
        Purpose:
            Provide a class spell that records construction.
        Contract:
            Appends a marker on each initialization.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Record construction for integration assertions.
            Contract:
                Appends a marker to init_calls.
            Returns:
                None.
            """
            init_calls.append("init")

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
        assert init_calls == ["init", "init"]
    finally:
        conduit.cleanup()
