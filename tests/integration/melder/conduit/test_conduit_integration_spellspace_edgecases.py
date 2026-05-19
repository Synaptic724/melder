from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.spell_space_scope_error import SpellSpaceScopeError
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


def _make_spellbook_with_spellspace_spell() -> tuple[Spellbook, str]:
    """
    Purpose:
        Create a Spellbook with a spellspace-scoped spell.
    Contract:
        - phase_scheduler_workers_per_spellbook is set.
        - The bound spell uses Existence.unique_per_spell_space.
    Returns:
        tuple[Spellbook, str]: The Spellbook and bound spell_id.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique_per_spell_space,
        permissions="create",
    )
    return spellbook, spell_id


def test_conduit_enter_spellspace_cleans_on_exception() -> None:
    """
    Purpose:
        Ensure enter_spellspace cleans the SpellSpace on exceptions.
    Contract:
        - The SpellSpace is cleaned when an error is raised in the context.
        - The active spellspace stack is cleared after exit.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup or stack clearing fails.
    """
    spellbook, spell_id = _make_spellbook_with_spellspace_spell()
    conduit = spellbook.conjure(name="root")
    active_space = None
    try:
        with pytest.raises(RuntimeError, match="boom"):
            with conduit.enter_spellspace() as space:
                active_space = space
                assert conduit.get_active_spellspace() is space
                space.meld(spell=spell_id)
                raise RuntimeError("boom")
        assert active_space is not None
        assert active_space.cleaned is True
        with pytest.raises(RuntimeError, match="already been cleaned"):
            _ = active_space.owner_conduit
        assert conduit.get_active_spellspace() is None
    finally:
        conduit.cleanup()


def test_conduit_spellspace_cleanup_idempotent_and_blocks_use() -> None:
    """
    Purpose:
        Validate SpellSpace cleanup is idempotent and blocks later use.
    Contract:
        - cleanup is safe to call multiple times.
        - reset/meld raise after cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup is not idempotent or use is allowed.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    conduit = spellbook.conjure(name="root")
    try:
        space = conduit.create_spellspace()
        space_id = space.id
        space.cleanup()
        space.cleanup()
        assert space.cleaned is True
        with pytest.raises(RuntimeError, match="already been cleaned"):
            _ = space.owner_conduit
        with pytest.raises(RuntimeError, match="already been cleaned"):
            space.reset()
        with pytest.raises(RuntimeError, match="already been cleaned"):
            space.meld(spell="unused")
    finally:
        conduit.cleanup()


def test_conduit_enter_spellspace_detects_stack_corruption() -> None:
    """
    Purpose:
        Validate spellspace stack corruption is detected on exit.
    Contract:
        - Exiting a corrupted spellspace stack raises SpellSpaceScopeError.
    Returns:
        None.
    Raises:
        AssertionError: If corruption is not detected.
    """
    spellbook, _spell_id = _make_spellbook_with_spellspace_spell()
    conduit = spellbook.conjure(name="root")
    space = None
    try:
        with pytest.raises(SpellSpaceScopeError, match="stack corruption"):
            with conduit.enter_spellspace() as active:
                space = active
                conduit._spellspace_stack.set([])
        if space is not None and space.cleaned is False:
            space.cleanup()
        assert conduit.get_active_spellspace() is None
    finally:
        conduit.cleanup()


def test_conduit_cleanup_cleans_orphaned_spellspaces() -> None:
    """
    Purpose:
        Ensure conduit cleanup flushes spellspaces left on the stack.
    Contract:
        - cleanup calls SpellSpace.cleanup for orphaned entries.
        - Orphaned spellspaces drop their owner reference.
    Returns:
        None.
    Raises:
        AssertionError: If orphaned spellspaces are not cleaned.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    conduit = spellbook.conjure(name="root")
    space = conduit.create_spellspace()
    stack = list(conduit._spellspace_stack.get())
    stack.append(space)
    conduit._spellspace_stack.set(stack)

    conduit.cleanup()
    assert space.cleaned is True
    with pytest.raises(RuntimeError, match="already been cleaned"):
        _ = space.owner_conduit


def test_conduit_cleanup_cleans_registered_spellspaces() -> None:
    """
    Purpose:
        Ensure cleanup flushes spellspaces registered outside the stack.
    Contract:
        - cleanup calls SpellSpace.cleanup for registered spellspaces.
        - Registered spellspaces drop their owner reference.
    Returns:
        None.
    Raises:
        AssertionError: If registry cleanup does not clean spellspaces.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    conduit = spellbook.conjure(name="root")
    space = conduit.create_spellspace()

    conduit.cleanup()

    assert space.cleaned is True
    with pytest.raises(RuntimeError, match="already been cleaned"):
        _ = space.owner_conduit
