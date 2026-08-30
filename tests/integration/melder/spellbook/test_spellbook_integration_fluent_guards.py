from __future__ import annotations

from melder import SpellBinder
import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService


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


def test_spellbinder_finalize_requires_active_bind() -> None:
    """
    Purpose:
        Validate SpellBinder.finalize requires an active bind.
    Contract:
        - finalize without bind raises RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If finalize succeeds without a bind.
    """
    spellbook = Spellbook()
    binder = SpellBinder(spellbook, )

    with pytest.raises(RuntimeError, match="no active spell"):
        binder.finalize()


def test_spellbinder_rejects_calls_after_cleanup() -> None:
    """
    Purpose:
        Validate SpellBinder rejects calls after cleanup.
    Contract:
        - bind after cleanup raises RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If bind succeeds after cleanup.
    """
    spellbook = Spellbook()
    binder = SpellBinder(spellbook, )
    binder.cleanup()

    with pytest.raises(RuntimeError, match="cleaned"):
        binder.bind(BasicService)


def test_spellbinder_singular_hooks_execute() -> None:
    """
    Purpose:
        Validate singular hook methods execute in order.
    Contract:
        - pre hooks run before activation and post hooks.
        - activation hooks run only when a new instance is created.
        - post hooks run after creation.
    Returns:
        None.
    Raises:
        AssertionError: If hooks do not execute in the expected order.
    """
    events: list[str] = []

    def pre_hook() -> None:
        """
        Purpose:
            Record pre-hook execution.
        Contract:
            Appends "pre" to events.
        Returns:
            None.
        """
        events.append("pre")

    def activation_hook(instance: object) -> None:
        """
        Purpose:
            Record activation hook execution.
        Contract:
            Appends "activation" to events.
        Args:
            instance: The created instance.
        Returns:
            None.
        """
        events.append("activation")

    def post_hook() -> None:
        """
        Purpose:
            Record post-hook execution.
        Contract:
            Appends "post" to events.
        Returns:
            None.
        """
        events.append("post")

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    binder = SpellBinder(spellbook, )
    spell_id = (
        binder.bind(BasicService)
        .as_unique()
        .with_pre_hook(pre_hook)
        .with_activation_hook(activation_hook)
        .with_post_hook(post_hook)
        .finalize()
    )

    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld(spell_id=spell_id)
        second = conduit.meld(spell_id=spell_id)
        assert first is second
        assert events == ["pre", "activation", "post", "pre", "post"]
    finally:
        conduit.cleanup()

