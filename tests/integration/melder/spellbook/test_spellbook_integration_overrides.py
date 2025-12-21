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


def test_meld_overrides_dict_applies_kwargs() -> None:
    """
    Purpose:
        Validate dictionary overrides are applied as keyword arguments.
    Contract:
        - spell_override dict maps onto constructor kwargs.
        - Instance fields reflect the provided override values.
    Returns:
        None.
    Raises:
        AssertionError: If override values are not applied.
    """
    class _Service:
        """
        Purpose:
            Provide a class spell with keyword-configured fields.
        Contract:
            Stores the provided value and label on the instance.
        """
        def __init__(self, value: int, label: str) -> None:
            """
            Purpose:
                Capture override arguments for assertions.
            Contract:
                Sets value and label fields from arguments.
            Args:
                value: Required numeric value.
                label: Required label string.
            Returns:
                None.
            """
            self.value = value
            self.label = label

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
        instance = conduit.meld(
            spell=spell_id,
            spell_override={"value": 7, "label": "dict"},
        )
        assert instance.value == 7
        assert instance.label == "dict"
    finally:
        conduit.cleanup()


def test_meld_overrides_list_applies_args() -> None:
    """
    Purpose:
        Validate list overrides are applied as positional arguments.
    Contract:
        - spell_override list maps onto constructor positional args.
        - Instance fields reflect the provided positional values.
    Returns:
        None.
    Raises:
        AssertionError: If positional overrides are not applied.
    """
    class _Service:
        """
        Purpose:
            Provide a class spell with positional parameters.
        Contract:
            Stores the provided value and label on the instance.
        """
        def __init__(self, value: int, label: str) -> None:
            """
            Purpose:
                Capture positional arguments for assertions.
            Contract:
                Sets value and label fields from arguments.
            Args:
                value: Required numeric value.
                label: Required label string.
            Returns:
                None.
            """
            self.value = value
            self.label = label

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
        instance = conduit.meld(
            spell=spell_id,
            spell_override=[13, "list"],
        )
        assert instance.value == 13
        assert instance.label == "list"
    finally:
        conduit.cleanup()
