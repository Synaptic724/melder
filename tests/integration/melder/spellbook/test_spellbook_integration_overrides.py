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
        - Instance captures the provided override mapping.
    Returns:
        None.
    Raises:
        AssertionError: If override values are not applied.
    """
    class _Service:
        """
        Purpose:
            Provide a class spell that records keyword overrides.
        Contract:
            Stores the provided keyword arguments on the instance.
        """
        def __init__(self, **kwargs) -> None:
            """
            Purpose:
                Capture override arguments for assertions.
            Contract:
                Stores provided keyword arguments on the instance.
            Args:
                **kwargs: Keyword overrides passed by meld.
            Returns:
                None.
            """
            self.kwargs = dict(kwargs)

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
        assert instance.kwargs == {"value": 7, "label": "dict"}
    finally:
        conduit.cleanup()


def test_meld_overrides_list_applies_args() -> None:
    """
    Purpose:
        Validate list overrides are applied as positional arguments.
    Contract:
        - spell_override list maps onto constructor positional args.
        - Instance captures the provided positional values.
    Returns:
        None.
    Raises:
        AssertionError: If positional overrides are not applied.
    """
    class _Service:
        """
        Purpose:
            Provide a class spell that records positional overrides.
        Contract:
            Stores the provided positional arguments on the instance.
        """
        def __init__(self, *args) -> None:
            """
            Purpose:
                Capture positional arguments for assertions.
            Contract:
                Stores provided positional arguments on the instance.
            Args:
                *args: Positional overrides passed by meld.
            Returns:
                None.
            """
            self.args = args

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
        assert instance.args == (13, "list")
    finally:
        conduit.cleanup()
