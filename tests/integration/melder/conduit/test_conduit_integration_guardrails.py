from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig
from tests.mocks.spellbook.core_classes import BasicService


from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
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


def _make_dynamic_configuration() -> SpellbookConfiguration:
    """
    Purpose:
        Create a dynamic configuration suitable for guardrail tests.
    Contract:
        - system_state is dynamic.
        - phase_scheduler_workers_per_spellbook is set.
    Returns:
        SpellbookConfiguration: Dynamic configuration instance.
    """
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def test_conduit_link_and_get_links_reject_automatic_mode() -> None:
    """
    Purpose:
        Validate automatic conduits reject dynamic link APIs.
    Contract:
        - link raises when dynamic environment is disabled.
        - get_links raises when dynamic environment is disabled.
    Returns:
        None.
    Raises:
        AssertionError: If guardrails do not fire.
    """
    spellbook = Spellbook()
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    owner = spellbook.conjure(name="owner")
    peer_book = Spellbook()
    peer = peer_book.conjure(name="peer")
    try:
        with pytest.raises(RuntimeError, match="Linking is disabled for the current frame posture|Dynamic environment is not enabled. Cannot manage link services."):
            owner.link(peer)
        with pytest.raises(RuntimeError, match="Dynamic environment is not enabled. Cannot manage link services."):
            owner.get_links()
    finally:
        owner.cleanup()
        peer.cleanup()


def test_conduit_link_rejects_self_and_lesser_targets() -> None:
    """
    Purpose:
        Validate link guardrails reject self-link and lesser targets.
    Contract:
        - linking a conduit to itself raises.
        - linking a lesser conduit raises.
    Returns:
        None.
    Raises:
        AssertionError: If guardrails do not fire.
    """
    configuration = _make_dynamic_configuration()
    spellbook = Spellbook(configuration=configuration)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    root = spellbook.conjure(automatic=False, name="root")
    lesser = root.create_lesser_conduit()
    try:
        with pytest.raises(RuntimeError, match="Cannot link a conduit to itself."):
            root.link(root)
        with pytest.raises(RuntimeError, match="Cannot link to a lesser conduit"):
            root.link(lesser)
    finally:
        lesser.cleanup()
        root.cleanup()


def test_conduit_link_rejects_outbound_only_target() -> None:
    """
    Purpose:
        Validate policy guardrails for inbound link rejection.
    Contract:
        - outbound_only target rejects inbound link requests.
    Returns:
        None.
    Raises:
        AssertionError: If policy guardrails do not fire.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    target_book = Spellbook(configuration=configuration)
    owner = owner_book.conjure(automatic=False, name="owner")
    target = target_book.conjure(automatic=False, name="target")
    try:
        target.set_new_policy(Policies.outbound_only.name)
        with pytest.raises(RuntimeError, match="outbound_only"):
            owner.link(target)
    finally:
        target.cleanup()
        owner.cleanup()


def test_conduit_set_new_policy_block_all_rejects_with_contracts() -> None:
    """
    Purpose:
        Validate policy guardrails reject block_all when contracts exist.
    Contract:
        - set_new_policy raises when block_all is requested with active contracts.
    Returns:
        None.
    Raises:
        AssertionError: If guardrails do not fire.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    service_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    borrower_book = Spellbook(configuration=configuration)
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        owner.link(borrower)
        with borrower.transaction("link", conduits=[borrower, owner]):
            borrower.add_spell_to_contract(
                spell_id=service_id,
                conduit=owner,
                permissions="create",
            )
        with pytest.raises(
            RuntimeError,
            match="Cannot set policy to 'block_all' or 'whitelist_all' when there are existing contracts.",
        ):
            borrower.set_new_policy(Policies.block_all.name)
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_conduit_set_new_policy_rejects_lesser() -> None:
    """
    Purpose:
        Validate lesser conduits cannot change policy.
    Contract:
        - set_new_policy on a lesser conduit raises.
    Returns:
        None.
    Raises:
        AssertionError: If guardrails do not fire.
    """
    configuration = _make_dynamic_configuration()
    spellbook = Spellbook(configuration=configuration)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    root = spellbook.conjure(automatic=False, name="root")
    lesser = root.create_lesser_conduit()
    try:
        with pytest.raises(RuntimeError, match="Cannot set policy on a lesser Conduit."):
            lesser.set_new_policy(Policies.default.name)
    finally:
        lesser.cleanup()
        root.cleanup()


def test_conduit_lookup_helpers_handle_missing_spells() -> None:
    """
    Purpose:
        Validate lookup helpers handle missing spell registrations.
    Contract:
        - check_spell_id returns False for unknown ids.
        - inspect_spell returns None for unregistered spells.
        - find_spell_id raises when spell not found.
        - find_spell_key raises when spell key not found.
        - get_spell_permissions raises when spell id missing.
    Returns:
        None.
    Raises:
        AssertionError: If guardrails do not fire.
    """
    spellbook = Spellbook()
    conduit = spellbook.conjure(name="owner")
    try:
        assert conduit.check_spell_id("missing-id") is False
        assert conduit.inspect_spell(BasicConfig) is None
        with pytest.raises(ValueError, match="Spell 'BasicConfig' not found in the spellbook."):
            conduit.find_spell_id(None, "BasicConfig", None)
        with pytest.raises(RuntimeError, match="Spell key not found in the spellbook."):
            conduit.find_spell_key(None, "BasicConfig", None)
        with pytest.raises(RuntimeError, match="Spell with ID missing-id not found in the spellbook."):
            conduit.get_spell_permissions("missing-id")
    finally:
        conduit.cleanup()
