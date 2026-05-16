from __future__ import annotations

from threading import Barrier, Lock, Thread

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.spell_space_scope_error import SpellSpaceScopeError
from tests.mocks.spellbook.core_classes import BasicService


from tests._frame_posture_test_support import (
    apply_automatic_defaults_for_spellbook_configuration,
    apply_dynamic_defaults_for_spellbook_configuration,
    build_aetheric_frame_configuration_for_spellbook_configuration,
    set_frame_ai_native_for_spellbook_configuration,
    set_frame_rift_enabled_for_spellbook_configuration,
    set_frame_system_state_for_spellbook_configuration,
    set_shared_framewide_spellbook_configuration_for_spellbook_configuration,
)
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


def _make_dynamic_configuration(*, workers: int = 2) -> SpellbookConfiguration:
    """
    Purpose:
        Create a dynamic configuration for linking and concurrency coverage.
    Contract:
        - system_state is dynamic.
        - phase_scheduler_workers_per_spellbook is set to > 1 when requested.
    Args:
        workers: Worker count for the phase scheduler.
    Returns:
        SpellbookConfiguration: Configured dynamic configuration.
    """
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", workers)
    return configuration


def test_conduit_spellspace_context_isolation_across_threads() -> None:
    """
    Purpose:
        Validate spellspace activation is isolated across threads.
    Contract:
        - Each thread gets its own active spellspace context.
        - unique_per_spell_space yields distinct instances per thread.
        - The main thread has no active spellspace after worker completion.
    Returns:
        None.
    Raises:
        AssertionError: If spellspace context leaks across threads.
    """
    configuration = _make_dynamic_configuration(workers=4)
    spellbook = Spellbook(configuration=configuration)
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique_per_spell_space,
        permissions="create",
    )
    conduit = spellbook.conjure(automatic=False, name="root")
    barrier = Barrier(2)
    lock = Lock()
    instances: list[object] = []
    errors: list[Exception] = []

    def worker() -> None:
        """
        Purpose:
            Meld inside a spellspace and record the instance.
        Contract:
            - The active spellspace is visible only within this thread.
            - Any errors are captured for assertions.
        Returns:
            None.
        """
        try:
            with conduit.enter_spellspace() as space:
                barrier.wait(timeout=5)
                instance = space.meld(spell=spell_id)
                assert conduit.get_active_spellspace() is space
            with lock:
                instances.append(instance)
        except Exception as exc:
            with lock:
                errors.append(exc)

    threads = [Thread(target=worker) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    try:
        assert errors == []
        assert len(instances) == 2
        assert instances[0] is not instances[1]
        assert conduit.get_active_spellspace() is None
    finally:
        conduit.cleanup()


def test_conduit_spellspace_enforces_active_scope_between_nested_spaces() -> None:
    """
    Purpose:
        Verify only the active spellspace can be used for meld operations.
    Contract:
        - Outer spellspace cannot meld while an inner spellspace is active.
        - After inner exit, the outer spellspace can meld again.
    Returns:
        None.
    Raises:
        AssertionError: If scope enforcement fails for nested spellspaces.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique_per_spell_space,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        with conduit.enter_spellspace() as outer:
            outer_instance = outer.meld(spell=spell_id)
            with conduit.enter_spellspace() as inner:
                inner_instance = inner.meld(spell=spell_id)
                assert inner_instance is not outer_instance
                with pytest.raises(SpellSpaceScopeError, match="active scope"):
                    outer.meld(spell=spell_id)
            outer_after = outer.meld(spell=spell_id)
            assert outer_after is outer_instance
    finally:
        conduit.cleanup()


def test_conduit_spellspace_isolation_between_root_and_lesser() -> None:
    """
    Purpose:
        Ensure spellspace-scoped instances are isolated across conduits.
    Contract:
        - Root and lesser conduits maintain independent spellspace scopes.
        - Each conduit reuses its own instance within its active spellspace.
    Returns:
        None.
    Raises:
        AssertionError: If spellspace instances leak across conduits.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique_per_spell_space,
        permissions="create",
    )
    root = spellbook.conjure(name="root")
    lesser = root.create_lesser_conduit()
    try:
        with root.enter_spellspace() as root_space:
            root_instance = root_space.meld(spell=spell_id)
            with lesser.enter_spellspace() as lesser_space:
                lesser_instance = lesser_space.meld(spell=spell_id)
                assert root.get_active_spellspace() is root_space
                assert lesser.get_active_spellspace() is lesser_space
                assert lesser_instance is not root_instance
            root_again = root_space.meld(spell=spell_id)
            assert root_again is root_instance
    finally:
        lesser.cleanup()
        root.cleanup()


def test_conduit_spellspace_contract_isolation_between_owner_and_borrower() -> None:
    """
    Purpose:
        Validate spellspace scoping when melding contracted spells.
    Contract:
        - Borrower reuses its spellspace instance within a scope.
        - Owner and borrower do not share spellspace-scoped instances.
        - New borrower spellspaces create new instances.
    Returns:
        None.
    Raises:
        AssertionError: If contracted spellspace scoping breaks.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    borrower_book = Spellbook(configuration=configuration)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique_per_spell_space,
        permissions="create",
    )

    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        assert owner.link(borrower) is True
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=spell_id,
                conduit=owner,
                permissions="create",
            ) is True

        with owner.enter_spellspace() as owner_space:
            owner_instance = owner_space.meld(spell=spell_id)
            with borrower.enter_spellspace() as borrower_space:
                borrower_instance = borrower_space.meld(spell=spell_id)
                borrower_again = borrower_space.meld(spell=spell_id)
                assert borrower_again is borrower_instance
                assert borrower_instance is not owner_instance

        with borrower.enter_spellspace() as borrower_space:
            borrower_new = borrower_space.meld(spell=spell_id)
            assert borrower_new is not borrower_instance
    finally:
        borrower.cleanup()
        owner.cleanup()
