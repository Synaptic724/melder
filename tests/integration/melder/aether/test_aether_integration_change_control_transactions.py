from __future__ import annotations

import hashlib

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService


from tests._frame_posture_test_support import (
    apply_automatic_defaults_for_spellbook_configuration,
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


def _make_configuration(
    *,
    aether_frame: str,
    dynamic: bool,
    workers: int = 1,
) -> SpellbookConfiguration:
    """
    Purpose:
        Build a configuration for change-control integration tests.
    Contract:
        - system_state is set to automatic or dynamic defaults.
        - phase_scheduler_workers_per_spellbook is configured.
    Args:
        aether_frame: Target frame name.
        dynamic: Whether to enable dynamic defaults.
        workers: Scheduler worker count per spellbook.
    Returns:
        SpellbookConfiguration: Configured instance.
    """
    configuration = SpellbookConfiguration(aether_frame=aether_frame)
    if dynamic:
        apply_dynamic_defaults_for_spellbook_configuration(configuration)
    else:
        apply_automatic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", workers)
    return configuration


def test_change_control_bind_transaction_opens_and_closes_embargoes() -> None:
    """
    Purpose:
        Validate bind transactions open implicit embargo scopes and close on end.
    Contract:
        - Embargo scopes include spellbook and binding keys.
        - In-flight request is cleared after end_transaction.
    Returns:
        None.
    Raises:
        AssertionError: If embargo or in-flight state is incorrect.
    """
    frame_name = "frame-cc-bind"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    spellbook = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    conduit = spellbook.conjure(automatic=False, name="root")
    change_control = Aether()._get_change_control_manager(frame_name)
    embargo_manager = change_control.embargo_manager()
    transaction_manager = change_control.transaction_manager()
    binding_key = ("frame", "__default__")

    spellbook.begin_transaction(
        "bind",
        binding_keys=[binding_key],
        scope_keys=["scope:custom"],
    )
    try:
        in_flight = transaction_manager.list_in_flight()
        assert len(in_flight) == 1
        assert in_flight[0].request_type is ChangeTransactionType.BIND
        embargoed = embargo_manager.describe()["embargoed_scopes"]
        assert f"scope:spellbook:{spellbook._id}" in embargoed
        assert f"binding:{binding_key[0]}:{binding_key[1]}" in embargoed
        assert "scope:custom" in embargoed
    finally:
        spellbook.end_transaction("bind")

    assert transaction_manager.list_in_flight() == []
    assert embargo_manager.describe()["embargo_count"] == 0
    conduit.cleanup()
    spellbook.cleanup()


def test_change_control_update_staged_request_extends_embargo_scopes() -> None:
    """
    Purpose:
        Validate staged updates extend embargo scopes for admitted requests.
    Contract:
        - Initial embargoes omit binding scopes when none are supplied.
        - update_staged_request adds binding scope embargoes.
    Returns:
        None.
    Raises:
        AssertionError: If staged updates do not extend embargo scopes.
    """
    frame_name = "frame-cc-staged"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    spellbook = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    conduit = spellbook.conjure(automatic=False, name="root")
    change_control = Aether()._get_change_control_manager(frame_name)
    embargo_manager = change_control.embargo_manager()
    transaction_manager = change_control.transaction_manager()
    binding_key = ("svc", "primary")

    spellbook.begin_transaction("bind")
    try:
        request = transaction_manager.list_in_flight()[0]
        embargoed_before = embargo_manager.describe()["embargoed_scopes"]
        assert not any(scope.startswith("binding:") for scope in embargoed_before)

        assert change_control.update_staged_request(
            request.request_id,
            binding_keys=[binding_key],
        )
        embargoed_after = embargo_manager.describe()["embargoed_scopes"]
        assert f"binding:{binding_key[0]}:{binding_key[1]}" in embargoed_after
    finally:
        spellbook.end_transaction("bind")

    conduit.cleanup()
    spellbook.cleanup()


def test_change_control_disable_allows_overlapping_requests() -> None:
    """
    Purpose:
        Validate disabled change-control stops conflict rejection.
    Contract:
        - Overlapping scope keys do not cause admission failure when
          change-control is disabled.
        - Strategy-owned same-thread bind starts still join the active root
          session instead of creating a second independent root request.
    Returns:
        None.
    Raises:
        AssertionError: If overlapping requests are rejected when disabled.
    """
    frame_name = "frame-cc-disabled"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    spellbook_a = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    spellbook_b = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    conduit_a = spellbook_a.conjure(automatic=False, name="root-a")
    conduit_b = spellbook_b.conjure(automatic=False, name="root-b")
    change_control = Aether()._get_change_control_manager(frame_name)
    change_control.disable_change_control()

    spellbook_a.begin_transaction("bind", scope_keys=["scope-shared"])
    spellbook_b.begin_transaction("bind", scope_keys=["scope-shared"])
    transaction_manager = change_control.transaction_manager()
    assert len(transaction_manager.list_in_flight()) == 1
    spellbook_a.end_transaction("bind")
    spellbook_b.end_transaction("bind")
    assert transaction_manager.list_in_flight() == []

    conduit_a.cleanup()
    conduit_b.cleanup()
    spellbook_a.cleanup()
    spellbook_b.cleanup()


def test_change_control_scope_hash_conflict_rejects_overlap() -> None:
    """
    Purpose:
        Validate same-thread bind starts join before conflict admission.
    Contract:
        - A second same-thread bind start does not open a second root request.
        - The active bind root remains the single in-flight request.
    Returns:
        None.
    Raises:
        AssertionError: If the second bind opens another root request.
    """
    frame_name = "frame-cc-hash"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    spellbook_a = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    spellbook_b = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    conduit_a = spellbook_a.conjure(automatic=False, name="root-a")
    conduit_b = spellbook_b.conjure(automatic=False, name="root-b")
    scope_hash = hashlib.sha256("shared-scope".encode("utf-8")).hexdigest()

    spellbook_a.begin_transaction("bind", scope_hashes=[scope_hash])
    try:
        spellbook_b.begin_transaction("bind", scope_hashes=[scope_hash])
        assert len(
            Aether()._get_change_control_manager(frame_name).transaction_manager().list_in_flight()
        ) == 1
    finally:
        spellbook_a.end_transaction("bind")
        spellbook_b.end_transaction("bind")

    conduit_a.cleanup()
    conduit_b.cleanup()
    spellbook_a.cleanup()
    spellbook_b.cleanup()


def test_change_control_link_transaction_embargoes_conduit_scopes() -> None:
    """
    Purpose:
        Validate link transactions embargo both borrower and peer conduits.
    Contract:
        - Embargo scopes include borrower and peer conduit ids.
        - Embargoes and in-flight requests clear on end_transaction.
    Returns:
        None.
    Raises:
        AssertionError: If conduit scope embargoes are missing.
    """
    frame_name = "frame-cc-link"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    owner_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    borrower_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    change_control = Aether()._get_change_control_manager(frame_name)
    embargo_manager = change_control.embargo_manager()
    transaction_manager = change_control.transaction_manager()

    borrower.begin_transaction("link", conduits=[borrower, owner])
    try:
        embargoed = embargo_manager.describe()["embargoed_scopes"]
        assert f"scope:conduit:{borrower.id}" in embargoed
        assert f"scope:conduit:{owner.id}" in embargoed
        assert len(transaction_manager.list_in_flight()) == 1
    finally:
        borrower.end_transaction("link")

    assert transaction_manager.list_in_flight() == []
    assert embargo_manager.describe()["embargo_count"] == 0
    owner.cleanup()
    borrower.cleanup()


def test_change_control_link_contract_registers_link_mirror() -> None:
    """
    Purpose:
        Validate link contracts register borrower/provider link mirrors.
    Contract:
        - Contracting a spell registers borrower ids in the link mirror.
    Returns:
        None.
    Raises:
        AssertionError: If link mirror registration is missing.
    """
    frame_name = "frame-cc-link-mirror"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    owner_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    borrower_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    change_control = Aether()._get_change_control_manager(frame_name)
    transaction_manager = change_control.transaction_manager()
    try:
        assert owner.link(borrower) is True
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=spell_id,
                conduit=owner,
                permissions="create",
                aetheric_frame=frame_name,
            )
        registry = change_control.devops_information_registry()
        assert registry is not None
        assert borrower.id in registry.list_borrowers_for_provider(owner.id)
    finally:
        owner.cleanup()
        borrower.cleanup()
