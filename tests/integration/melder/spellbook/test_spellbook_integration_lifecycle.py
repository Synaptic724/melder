from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
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


def test_spellbook_conjure_sets_name_and_rejects_second_conjure() -> None:
    """
    Purpose:
        Validate conjure sets a name and prevents a second conjure.
    Contract:
        - Conduit name matches the requested name.
        - A second conjure raises RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If name is missing or double conjure succeeds.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    conduit = spellbook.conjure(name="root")
    try:
        assert conduit.name == "root"
        with pytest.raises(RuntimeError, match="already conjured"):
            spellbook.conjure(name="second")
    finally:
        conduit.cleanup()


def test_spellbook_context_manager_allows_binding_and_meld() -> None:
    """
    Purpose:
        Validate context manager usage does not block binding or melding.
    Contract:
        - Binding works within the Spellbook context manager.
        - Conjure and meld still function after context exit.
    Returns:
        None.
    Raises:
        AssertionError: If binding or meld fails after context use.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    with spellbook as context_spellbook:
        spell_id = context_spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=spell_id)
        assert isinstance(instance, BasicService)
    finally:
        conduit.cleanup()


def test_spellbook_cleanup_is_idempotent_and_blocks_new_binder() -> None:
    """
    Purpose:
        Validate cleanup is idempotent and blocks new binders.
    Contract:
        - cleanup can be called multiple times safely.
        - create_binder raises after cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup is not idempotent or binder still works.
    """
    spellbook = Spellbook()
    spellbook.cleanup()
    spellbook.cleanup()

    with pytest.raises(RuntimeError, match="already been cleaned"):
        spellbook.create_binder()
