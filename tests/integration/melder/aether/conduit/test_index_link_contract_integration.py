"""
Integration tests -- index-link contract (the SpellIndex-contract model), area F.

HARNESS-VALIDATION TEMPLATE (first integration tranche). These exercise the real
cross-conduit wiring: two dynamic spellbooks, `link`, and the NEW
`add_index_to_contract` / guard surface. They are modeled exactly on
`tests/component/melder/aether/conduit/test_conduit_component_spell_contracts.py`.

Runtime: Python 3.14t. The sandbox that authored these is 3.10 and CANNOT run
them (no pytest + modules need 3.14 deferred annotations), so they are authored
against the real API and executed by the user. Validate THIS file on 3.14t before
the remaining F/A-E integration tranches are written, to shake out any harness or
API mismatch once rather than across ~80 blind tests.

Covers: F1 (link records the IndexDetail + per-member Detail + borrower tracking),
F2 (permission fan-through), F6 (removal guard), F7 (permission guard), F8 (unlink
removes index + member details).
"""

import contextlib
from typing import Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.contract_classes import ContractServicePrimary
from tests.mocks.spellbook.protocols import IService

from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_index_link_integration() -> None:
    """Start each test with a clean Aether singleton and rebind the class refs."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _make_spellbook() -> Spellbook:
    """Build a dynamic spellbook (mirrors the component-test helper)."""
    config = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(config)
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(configuration=config)


def _bind_service(book: Spellbook, binding_name: str = "primary") -> str:
    """Bind a service spell and return its spell_id."""
    return book.bind(
        spell=ContractServicePrimary,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name=binding_name,
    )


@contextlib.contextmanager
def _linked_pair() -> Iterator[tuple]:
    """
    Build owner+borrower dynamic conduits with the owner holding one bound
    service index, `link` them, and yield the assembled fixture tuple:
    (owner_book, borrower_book, owner, borrower, service_id, index).
    """
    owner_book = _make_spellbook()
    borrower_book = _make_spellbook()
    service_id = _bind_service(owner_book)
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    owner.link(borrower)
    index = owner_book.find_spell_by_id(service_id).spell_index
    try:
        yield (owner_book, borrower_book, owner, borrower, service_id, index)
    finally:
        borrower.cleanup()
        owner.cleanup()


def _link_index(borrower: Conduit, owner: Conduit, index, permissions: str) -> None:
    """Link `index` (owned by `owner`) into the contract at `permissions`."""
    with borrower.transaction("link", conduits=[borrower, owner]):
        assert borrower.add_index_to_contract(
            index=index,
            conduit=owner,
            permissions=permissions,
        )


def test_link_index_records_index_detail():
    with _linked_pair() as (owner_book, borrower_book, owner, borrower, service_id, index):
        _link_index(borrower, owner, index, "read")
        contract = borrower._conduit_ward._find_contract_by_id(owner._id)
        assert contract._check_index_exists(owner._conduit_ward, index.id) is True


def test_link_index_generates_per_member_detail():
    with _linked_pair() as (owner_book, borrower_book, owner, borrower, service_id, index):
        _link_index(borrower, owner, index, "read")
        contract = borrower._conduit_ward._find_contract_by_id(owner._id)
        # The single member's per-member spell Detail is auto-generated.
        assert contract._check_if_exists(owner._conduit_ward, service_id) is True


def test_link_index_tracks_borrower_contracted_index():
    with _linked_pair() as (owner_book, borrower_book, owner, borrower, service_id, index):
        _link_index(borrower, owner, index, "read")
        assert index.id in borrower_book._contracted_indexes


def test_link_index_gives_borrower_active_contracted_member():
    with _linked_pair() as (owner_book, borrower_book, owner, borrower, service_id, index):
        _link_index(borrower, owner, index, "read")
        # The active member is a live borrowed copy keyed under the owner conduit.
        active_by_id = borrower_book._contracted_spells_by_id.get(owner._id, {})
        assert service_id in active_by_id


def test_member_detail_permission_matches_index_link():
    with _linked_pair() as (owner_book, borrower_book, owner, borrower, service_id, index):
        from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
        _link_index(borrower, owner, index, "read")
        contract = borrower._conduit_ward._find_contract_by_id(owner._id)
        detail = contract._get_detail_map(owner._conduit_ward)[service_id]
        assert detail.permissions is Permissions.read


def test_removal_guard_blocks_index_member_spell():
    with _linked_pair() as (owner_book, borrower_book, owner, borrower, service_id, index):
        _link_index(borrower, owner, index, "read")
        # A member of a linked index is contract-locked: removing it individually raises.
        with pytest.raises(RuntimeError):
            with borrower.transaction("link", conduits=[borrower, owner]):
                borrower.remove_spell_from_contract(spell_id=service_id, conduit=owner)


def test_permission_guard_defers_same_permission():
    with _linked_pair() as (owner_book, borrower_book, owner, borrower, service_id, index):
        _link_index(borrower, owner, index, "read")
        # Re-adding the member at the SAME permission defers to the index (no-op, True).
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=service_id, conduit=owner, permissions="read",
            ) is True


def test_permission_guard_raises_on_different_permission():
    with _linked_pair() as (owner_book, borrower_book, owner, borrower, service_id, index):
        _link_index(borrower, owner, index, "read")
        # Trying to re-permission an index-member individually is refused.
        with pytest.raises(RuntimeError):
            with borrower.transaction("link", conduits=[borrower, owner]):
                borrower.add_spell_to_contract(
                    spell_id=service_id, conduit=owner, permissions="create",
                )


def test_unlink_index_removes_index_and_member_details():
    with _linked_pair() as (owner_book, borrower_book, owner, borrower, service_id, index):
        _link_index(borrower, owner, index, "read")
        with borrower.transaction("link", conduits=[borrower, owner]):
            borrower.remove_index_from_contract(index=index, conduit=owner)
        contract = borrower._conduit_ward._find_contract_by_id(owner._id)
        assert contract._check_index_exists(owner._conduit_ward, index.id) is False
        assert contract._check_if_exists(owner._conduit_ward, service_id) is False
        assert index.id not in borrower_book._contracted_indexes
