from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.spellbook import Spellbook


from tests._frame_posture_test_support import (
    apply_automatic_defaults_for_spellbook_configuration,
    apply_dynamic_defaults_for_spellbook_configuration,
)
@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_transactions() -> None:
    """
    Purpose:
        Ensure component transaction tests start with a clean Aether singleton.
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


def _make_spellbook(*, dynamic: bool) -> Spellbook:
    """
    Purpose:
        Build a spellbook for conduit transaction component tests.
    Contract:
        - system_state defaults to automatic or dynamic.
        - phase_scheduler_workers_per_spellbook is set.
    Args:
        dynamic: Whether to enable dynamic defaults.
    Returns:
        Spellbook: Configured spellbook.
    """
    config = SpellbookConfiguration()
    if dynamic:
        apply_dynamic_defaults_for_spellbook_configuration(config)
    else:
        apply_automatic_defaults_for_spellbook_configuration(config)
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(configuration=config)


def test_component_conduit_begin_transaction_link_requires_dynamic_mode() -> None:
    """
    Purpose:
        Validate link transactions are rejected in automatic mode.
    Contract:
        - begin_transaction("link") raises when conduit is not dynamic.
    Returns:
        None.
    Raises:
        AssertionError: If link admission does not enforce dynamic mode.
    """
    owner_book = _make_spellbook(dynamic=False)
    peer_book = _make_spellbook(dynamic=False)
    owner = owner_book.conjure(name="owner")
    peer = peer_book.conjure(name="peer")
    try:
        with pytest.raises(RuntimeError, match="dynamic mode"):
            owner.begin_transaction("link", conduits=[owner, peer])
    finally:
        owner.cleanup()
        peer.cleanup()


def test_component_conduit_begin_transaction_link_registers_in_flight() -> None:
    """
    Purpose:
        Validate link transactions register in-flight requests.
    Contract:
        - In-flight request includes borrower and peer conduit ids.
        - Request scope keys include the borrower conduit scope.
    Returns:
        None.
    Raises:
        AssertionError: If in-flight registration is incorrect.
    """
    owner_book = _make_spellbook(dynamic=True)
    borrower_book = _make_spellbook(dynamic=True)
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    change_control = Aether()._get_change_control_manager("default")
    try:
        borrower.begin_transaction("link", conduits=[borrower, owner])
        in_flight = change_control.transaction_manager().list_in_flight()
        assert len(in_flight) == 1
        request = in_flight[0]
        assert request.request_type is ChangeTransactionType.LINK
        assert borrower.id in request.conduit_ids
        assert owner.id in request.conduit_ids
        assert f"scope:conduit:{borrower.id}" in request.scope_keys
    finally:
        borrower.end_transaction("link")
        owner.cleanup()
        borrower.cleanup()


def test_component_conduit_transaction_context_closes_in_flight() -> None:
    """
    Purpose:
        Validate transaction context manager clears in-flight requests.
    Contract:
        - In-flight request exists inside the context.
        - In-flight registry is cleared after context exit.
    Returns:
        None.
    Raises:
        AssertionError: If context does not clear in-flight state.
    """
    owner_book = _make_spellbook(dynamic=True)
    borrower_book = _make_spellbook(dynamic=True)
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    change_control = Aether()._get_change_control_manager("default")
    try:
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert len(change_control.transaction_manager().list_in_flight()) == 1
        assert change_control.transaction_manager().list_in_flight() == []
    finally:
        owner.cleanup()
        borrower.cleanup()
