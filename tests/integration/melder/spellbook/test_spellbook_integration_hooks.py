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


def test_hooks_execute_and_activation_runs_once_for_unique() -> None:
    """
    Purpose:
        Validate lifecycle hook execution for a unique spell.
    Contract:
        - pre/post hooks run on every meld call.
        - activation hooks run only when a new instance is created.
    Returns:
        None.
    Raises:
        AssertionError: If hook counts do not match lifecycle expectations.
    """
    pre_calls: list[str] = []
    post_calls: list[str] = []
    activation_calls: list[object] = []

    class _Service:
        """
        Purpose:
            Provide a simple class spell for hook verification.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the service with a marker.
            Contract:
                Sets marker to "hooks".
            Returns:
                None.
            """
            self.marker = "hooks"

    def pre_hook() -> None:
        """
        Purpose:
            Track pre-cast hook execution.
        Contract:
            Appends a marker to pre_calls.
        Returns:
            None.
        """
        pre_calls.append("pre")

    def post_hook() -> None:
        """
        Purpose:
            Track post-cast hook execution.
        Contract:
            Appends a marker to post_calls.
        Returns:
            None.
        """
        post_calls.append("post")

    def activation_hook(instance: object) -> None:
        """
        Purpose:
            Track activation hook execution.
        Contract:
            Appends the activated instance to activation_calls.
        Args:
            instance: Newly created instance being activated.
        Returns:
            None.
        """
        activation_calls.append(instance)

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spell_id = spellbook.bind(
        spell=_Service,
        existence=Existence.unique,
        permissions="create",
        pre_hooks=[pre_hook],
        activation_hooks=[activation_hook],
        post_hooks=[post_hook],
    )

    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld(spell=spell_id)
        second = conduit.meld(spell=spell_id)
        assert first is second
        assert pre_calls == ["pre", "pre"]
        assert post_calls == ["post", "post"]
        assert activation_calls == [first]
    finally:
        conduit.cleanup()
