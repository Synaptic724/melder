from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig, BasicService


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


def _make_dynamic_configuration() -> Configuration:
    """
    Purpose:
        Create a dynamic configuration for hook and spellspace tests.
    Contract:
        - system_state is dynamic.
        - phase_scheduler_workers_per_spellbook is set.
    Returns:
        Configuration: Dynamic configuration instance.
    """
    configuration = Configuration()
    configuration.dynamic_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def test_conduit_spellspace_nesting_and_reset() -> None:
    """
    Purpose:
        Validate SpellSpace nesting and reset behavior for unique_per_spell_space.
    Contract:
        - Nested spellspaces isolate instances.
        - Inner spellspace reuse is stable.
        - Outer spellspace reuse is preserved after inner exits.
        - Reset clears spellspace instances and bumps version.
    Returns:
        None.
    Raises:
        AssertionError: If spellspace isolation or reset behavior breaks.
    """
    configuration = _make_dynamic_configuration()
    spellbook = Spellbook(configuration=configuration)
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique_per_spell_space,
        permissions="create",
    )
    conduit = spellbook.conjure(automatic=False, name="root")
    try:
        assert conduit.get_active_spellspace() is None
        with conduit.enter_spellspace() as outer:
            outer_instance = outer.meld(spell=spell_id)
            outer_again = outer.meld(spell=spell_id)
            assert outer_again is outer_instance
            assert conduit.get_active_spellspace() is outer

            with conduit.enter_spellspace() as inner:
                inner_instance = inner.meld(spell=spell_id)
                inner_again = inner.meld(spell=spell_id)
                assert inner_again is inner_instance
                assert inner_instance is not outer_instance
                assert conduit.get_active_spellspace() is inner
                assert inner.id != outer.id

            assert conduit.get_active_spellspace() is outer
            outer_after_inner = outer.meld(spell=spell_id)
            assert outer_after_inner is outer_instance

            initial_version = outer.version
            outer.reset()
            assert outer.version == initial_version + 1
            outer_after_reset = outer.meld(spell=spell_id)
            assert outer_after_reset is not outer_instance

        assert conduit.get_active_spellspace() is None
    finally:
        conduit.cleanup()


def test_conduit_hooks_fire_for_meld_link_contract_and_cleanup() -> None:
    """
    Purpose:
        Validate Conduit hook wiring for meld, link/unlink, contracts, and cleanup.
    Contract:
        - Meld hooks fire for both Conduit and Meld layers.
        - Link/unlink hooks fire on the calling conduit.
        - Contract hooks fire on the contracting conduit.
        - Cleanup hooks fire on the conduit that registered them.
    Returns:
        None.
    Raises:
        AssertionError: If hooks are not fired as expected.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    borrower_book = Spellbook(configuration=configuration)

    meld_pre_calls: list[int] = []
    meld_post_calls: list[int] = []
    link_calls: list[int] = []
    unlink_calls: list[int] = []
    contract_created_calls: list[int] = []
    contract_removed_calls: list[int] = []
    cleanup_start_calls: list[int] = []
    cleanup_complete_calls: list[int] = []

    def on_meld_pre_resolve(*args: object) -> None:
        """
        Purpose:
            Record meld pre-resolve hook calls.
        Contract:
            Captures the number of args provided to the hook.
        Args:
            *args: Hook arguments supplied by Conduit or Meld.
        Returns:
            None.
        """
        meld_pre_calls.append(len(args))

    def on_meld_post_resolve(*args: object) -> None:
        """
        Purpose:
            Record meld post-resolve hook calls.
        Contract:
            Captures the number of args provided to the hook.
        Args:
            *args: Hook arguments supplied by Conduit or Meld.
        Returns:
            None.
        """
        meld_post_calls.append(len(args))

    def on_conduit_post_link(*args: object) -> None:
        """
        Purpose:
            Record conduit post-link hook calls.
        Contract:
            Captures the number of args provided to the hook.
        Args:
            *args: Hook arguments supplied by Conduit.
        Returns:
            None.
        """
        link_calls.append(len(args))

    def on_conduit_post_unlink(*args: object) -> None:
        """
        Purpose:
            Record conduit post-unlink hook calls.
        Contract:
            Captures the number of args provided to the hook.
        Args:
            *args: Hook arguments supplied by Conduit.
        Returns:
            None.
        """
        unlink_calls.append(len(args))

    def on_contract_created(*args: object) -> None:
        """
        Purpose:
            Record contract creation hook calls.
        Contract:
            Captures the number of args provided to the hook.
        Args:
            *args: Hook arguments supplied by Conduit.
        Returns:
            None.
        """
        contract_created_calls.append(len(args))

    def on_contract_removed(*args: object) -> None:
        """
        Purpose:
            Record contract removal hook calls.
        Contract:
            Captures the number of args provided to the hook.
        Args:
            *args: Hook arguments supplied by Conduit.
        Returns:
            None.
        """
        contract_removed_calls.append(len(args))

    def on_conduit_cleanup_start(*args: object) -> None:
        """
        Purpose:
            Record cleanup start hook calls.
        Contract:
            Captures the number of args provided to the hook.
        Args:
            *args: Hook arguments supplied by Conduit.
        Returns:
            None.
        """
        cleanup_start_calls.append(len(args))

    def on_conduit_cleanup_complete(*args: object) -> None:
        """
        Purpose:
            Record cleanup complete hook calls.
        Contract:
            Captures the number of args provided to the hook.
        Args:
            *args: Hook arguments supplied by Conduit.
        Returns:
            None.
        """
        cleanup_complete_calls.append(len(args))

    configuration.add_hook(owner_book.id, "on_meld_pre_resolve", on_meld_pre_resolve)
    configuration.add_hook(owner_book.id, "on_meld_post_resolve", on_meld_post_resolve)
    configuration.add_hook(owner_book.id, "on_conduit_post_link", on_conduit_post_link)
    configuration.add_hook(owner_book.id, "on_conduit_post_unlink", on_conduit_post_unlink)
    configuration.add_hook(owner_book.id, "on_conduit_cleanup_start", on_conduit_cleanup_start)
    configuration.add_hook(owner_book.id, "on_conduit_cleanup_complete", on_conduit_cleanup_complete)

    configuration.add_hook(borrower_book.id, "on_contract_created", on_contract_created)
    configuration.add_hook(borrower_book.id, "on_contract_removed", on_contract_removed)

    service_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    config_id = owner_book.bind(
        spell=BasicConfig,
        existence=Existence.unique,
        permissions="create",
    )
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        assert owner.link(borrower) is True
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spells_to_contract(
                spell_ids=[service_id, config_id],
                conduit=owner,
                permissions="create",
            ) == {service_id: True, config_id: True}
        assert owner.meld(spell=service_id) is not None
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.remove_spell_from_contract(spell_id=service_id, conduit=owner) is True
        assert owner.sever_link(borrower) is True
    finally:
        borrower.cleanup()
        owner.cleanup()

    assert len(meld_pre_calls) == 2
    assert len(meld_post_calls) == 2
    assert len(link_calls) == 1
    assert len(unlink_calls) == 1
    assert len(contract_created_calls) == 1
    assert len(contract_removed_calls) == 1
    assert len(cleanup_start_calls) == 1
    assert len(cleanup_complete_calls) == 1


def test_conduit_hooks_fire_for_lesser_conduit_creation() -> None:
    """
    Purpose:
        Validate lesser conduit creation hooks fire with expected arguments.
    Contract:
        - on_conduit_pre_created receives the parent conduit.
        - on_conduit_activated receives the new lesser conduit.
        - on_conduit_post_created receives parent and lesser conduits.
    Returns:
        None.
    Raises:
        AssertionError: If creation hooks are not fired as expected.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)

    pre_calls: list[tuple[object, ...]] = []
    activated_calls: list[tuple[object, ...]] = []
    post_calls: list[tuple[object, ...]] = []

    def on_conduit_pre_created(*args: object) -> None:
        """
        Purpose:
            Record pre-created hook calls.
        Contract:
            Captures the arguments for assertions.
        Args:
            *args: Hook arguments supplied by Conduit.
        Returns:
            None.
        """
        pre_calls.append(args)

    def on_conduit_activated(*args: object) -> None:
        """
        Purpose:
            Record activated hook calls.
        Contract:
            Captures the arguments for assertions.
        Args:
            *args: Hook arguments supplied by Conduit.
        Returns:
            None.
        """
        activated_calls.append(args)

    def on_conduit_post_created(*args: object) -> None:
        """
        Purpose:
            Record post-created hook calls.
        Contract:
            Captures the arguments for assertions.
        Args:
            *args: Hook arguments supplied by Conduit.
        Returns:
            None.
        """
        post_calls.append(args)

    configuration.add_hook(owner_book.id, "on_conduit_pre_created", on_conduit_pre_created)
    configuration.add_hook(owner_book.id, "on_conduit_activated", on_conduit_activated)
    configuration.add_hook(owner_book.id, "on_conduit_post_created", on_conduit_post_created)

    owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    owner = owner_book.conjure(automatic=False, name="owner")
    pre_calls.clear()
    activated_calls.clear()
    post_calls.clear()
    lesser = None
    try:
        lesser = owner.create_lesser_conduit()
        assert pre_calls == [(owner,)]
        assert activated_calls == [(lesser,)]
        assert post_calls == [(owner, lesser)]
    finally:
        if lesser is not None:
            lesser.cleanup()
        owner.cleanup()
