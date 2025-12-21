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


def test_bind_and_meld_resolves_by_spellframe_and_binding_name() -> None:
    """
    Purpose:
        Validate spellframe + binding_name resolution for multiple bindings.
    Contract:
        - Two bindings under the same frame resolve by binding name.
        - Existing-creation spells return the bound instances.
    Returns:
        None.
    Raises:
        AssertionError: If resolution returns the wrong instance.
    """
    class _ServiceA:
        """
        Purpose:
            Provide a class used for existing-object binding name "a".
        Contract:
            Stores a stable marker for verification.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the service with a marker.
            Contract:
                Sets marker to "A".
            Returns:
                None.
            """
            self.marker = "A"

    class _ServiceB:
        """
        Purpose:
            Provide a class used for existing-object binding name "b".
        Contract:
            Stores a stable marker for verification.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the service with a marker.
            Contract:
                Sets marker to "B".
            Returns:
                None.
            """
            self.marker = "B"

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    instance_a = _ServiceA()
    instance_b = _ServiceB()

    spellbook.bind(
        spell=instance_a,
        existence=Existence.unique,
        permissions="create",
        spellframe="svc",
        binding_name="a",
    )
    spellbook.bind(
        spell=instance_b,
        existence=Existence.unique,
        permissions="create",
        spellframe="svc",
        binding_name="b",
    )

    conduit = spellbook.conjure(name="root")
    try:
        resolved_a = conduit.meld(spellframe="svc", binding_name="a")
        resolved_b = conduit.meld(spellframe="svc", binding_name="b")
        assert resolved_a is instance_a
        assert resolved_b is instance_b
        assert resolved_a.marker == "A"
        assert resolved_b.marker == "B"
    finally:
        conduit.cleanup()
