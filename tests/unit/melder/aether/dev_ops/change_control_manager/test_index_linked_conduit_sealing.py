from typing import Tuple

import pytest

from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.notch_transaction_strategy import (
    NotchTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.add_to_index_transaction_strategy import (
    AddToIndexTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.remove_from_index_transaction_strategy import (
    RemoveFromIndexTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_manager import (
    ChangeControlTransactionManager,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.embargo_manager.embargo_manager import (
    ChangeControlEmbargoManager,
    ClaimMode,
)
from melder.aether.aetheric_frame.dev_ops.devops_identity import DevopsIdentity
from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
    DevopsInformationRegistry,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _manager_and_registry() -> Tuple[ChangeControlTransactionManager, DevopsInformationRegistry]:
    """Return a fresh transaction manager + registry for one frame."""
    return ChangeControlTransactionManager(), DevopsInformationRegistry("frame-1")


def _conduit_identity(conduit_id: str) -> DevopsIdentity:
    """Build a conduit identity that supports the three index transactions."""
    return DevopsIdentity(
        owner_kind="conduit",
        owner_id=conduit_id,
        aetheric_frame_name="frame-1",
        metadata={},
        available_transactions=("notch", "add_to_index", "remove_from_index"),
    )


@pytest.fixture
def embargo():
    """Provide a fresh embargo manager with deterministic teardown."""
    manager = ChangeControlEmbargoManager()
    yield manager
    if not manager.cleaned:
        manager.cleanup()


def _notch_plan(transaction_manager, registry, *, acting_conduit_id):
    """Build a notch plan for `acting_conduit_id` against the live registry topology."""
    identity = _conduit_identity(acting_conduit_id)
    registry.register_identity(identity)
    return NotchTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={
            "spellbook_id": "spellbook-1",
            "owner_conduit_id": acting_conduit_id,
            "binding_key": ("frame-1", "lookup-A"),
        },
    )


# ---------------------------------------------------------------------------
# Part 1 -- index ops seal the conduits linked to the acting conduit
# ---------------------------------------------------------------------------
def test_notch_seals_acting_conduit_and_its_linked_conduits() -> None:
    """
    Purpose:
        Verify a notch seals the acting conduit plus every conduit linked to it
        -- both its borrowers and its providers -- all EXCLUSIVE.
    Contract:
        - acting conduit-A, its borrower conduit-B, and its provider conduit-C
          are each claimed EXCLUSIVE.
    Returns:
        None.
    Raises:
        AssertionError: If a linked conduit is not sealed.
    """
    transaction_manager, registry = _manager_and_registry()
    # conduit-A provides to conduit-B (B borrows from A); conduit-C provides to A.
    registry.register_conduit_link(provider_conduit_id="conduit-A", borrower_conduit_id="conduit-B")
    registry.register_conduit_link(provider_conduit_id="conduit-C", borrower_conduit_id="conduit-A")

    plan = _notch_plan(transaction_manager, registry, acting_conduit_id="conduit-A")
    scope_claims = dict(plan["scope_claims"])

    assert scope_claims["scope:conduit:conduit-A"] == ClaimMode.EXCLUSIVE.value
    assert scope_claims["scope:conduit:conduit-B"] == ClaimMode.EXCLUSIVE.value
    assert scope_claims["scope:conduit:conduit-C"] == ClaimMode.EXCLUSIVE.value


def test_add_to_index_seals_linked_conduits() -> None:
    """
    Purpose:
        Verify an add-to-index seals the acting conduit's linked conduits too.
    Contract:
        - The borrower conduit-B of acting conduit-A is claimed EXCLUSIVE.
    Returns:
        None.
    Raises:
        AssertionError: If the linked conduit is not sealed.
    """
    transaction_manager, registry = _manager_and_registry()
    registry.register_conduit_link(provider_conduit_id="conduit-A", borrower_conduit_id="conduit-B")
    identity = _conduit_identity("conduit-A")
    registry.register_identity(identity)

    plan = AddToIndexTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={"spellbook_id": "spellbook-1", "owner_conduit_id": "conduit-A"},
    )
    scope_claims = dict(plan["scope_claims"])

    assert scope_claims["scope:conduit:conduit-A"] == ClaimMode.EXCLUSIVE.value
    assert scope_claims["scope:conduit:conduit-B"] == ClaimMode.EXCLUSIVE.value


def test_remove_from_index_seals_linked_conduits() -> None:
    """
    Purpose:
        Verify a remove-from-index seals the acting conduit's linked conduits too.
    Contract:
        - The provider conduit-C of acting conduit-A is claimed EXCLUSIVE.
    Returns:
        None.
    Raises:
        AssertionError: If the linked conduit is not sealed.
    """
    transaction_manager, registry = _manager_and_registry()
    registry.register_conduit_link(provider_conduit_id="conduit-C", borrower_conduit_id="conduit-A")
    identity = _conduit_identity("conduit-A")
    registry.register_identity(identity)

    plan = RemoveFromIndexTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={"spellbook_id": "spellbook-1", "owner_conduit_id": "conduit-A"},
    )
    scope_claims = dict(plan["scope_claims"])

    assert scope_claims["scope:conduit:conduit-A"] == ClaimMode.EXCLUSIVE.value
    assert scope_claims["scope:conduit:conduit-C"] == ClaimMode.EXCLUSIVE.value


# ---------------------------------------------------------------------------
# Part 2 -- the seal mutually blocks link/bind/transfer on a linked conduit
# ---------------------------------------------------------------------------
def test_notch_blocks_structural_work_on_a_linked_conduit(embargo) -> None:
    """
    Purpose:
        Verify a held notch blocks new link/bind/transfer work on a conduit
        linked to the acting one (not just the acting conduit itself).
    Contract:
        - The notch acquires its full seal (acting + linked conduits).
        - An EXCLUSIVE claim on the linked conduit (as link/bind/transfer would
          make) is refused while the notch holds it.
    Returns:
        None.
    Raises:
        AssertionError: If structural work on the linked conduit is not blocked.
    """
    transaction_manager, registry = _manager_and_registry()
    registry.register_conduit_link(provider_conduit_id="conduit-A", borrower_conduit_id="conduit-B")
    plan = _notch_plan(transaction_manager, registry, acting_conduit_id="conduit-A")

    assert embargo.try_acquire(
        owner_request_id="tx-notch",
        claims=plan["scope_claims"],
        reason_tag="notch",
    ).acquired is True

    blocked = embargo.try_acquire(
        owner_request_id="tx-link",
        claims=[("scope:conduit:conduit-B", ClaimMode.EXCLUSIVE)],
        reason_tag="link",
    )
    assert blocked.acquired is False
    assert any(block[0] == "scope:conduit:conduit-B" for block in blocked.blocking)


def test_link_in_flight_on_a_linked_conduit_blocks_a_notch(embargo) -> None:
    """
    Purpose:
        Verify the reverse direction -- a link/unlink/bind already holding a
        linked conduit blocks a notch that would seal it.
    Contract:
        - A held EXCLUSIVE claim on conduit-B refuses the notch on conduit-A,
          because the notch's seal includes its borrower conduit-B.
    Returns:
        None.
    Raises:
        AssertionError: If the notch is not blocked by the in-flight link.
    """
    transaction_manager, registry = _manager_and_registry()
    registry.register_conduit_link(provider_conduit_id="conduit-A", borrower_conduit_id="conduit-B")
    plan = _notch_plan(transaction_manager, registry, acting_conduit_id="conduit-A")

    assert embargo.try_acquire(
        owner_request_id="tx-link",
        claims=[("scope:conduit:conduit-B", ClaimMode.EXCLUSIVE)],
        reason_tag="link",
    ).acquired is True

    blocked = embargo.try_acquire(
        owner_request_id="tx-notch",
        claims=plan["scope_claims"],
        reason_tag="notch",
    )
    assert blocked.acquired is False


def test_notch_leaves_unlinked_conduits_free(embargo) -> None:
    """
    Purpose:
        Verify a notch with no linked conduits seals only its own surfaces and
        does not block structural work on an unrelated conduit.
    Contract:
        - With no registered links, the notch claims do not include any other
          conduit, so an EXCLUSIVE claim on an unrelated conduit still admits.
    Returns:
        None.
    Raises:
        AssertionError: If an unrelated conduit is wrongly blocked.
    """
    transaction_manager, registry = _manager_and_registry()
    plan = _notch_plan(transaction_manager, registry, acting_conduit_id="conduit-A")

    assert embargo.try_acquire(
        owner_request_id="tx-notch",
        claims=plan["scope_claims"],
        reason_tag="notch",
    ).acquired is True

    assert embargo.try_acquire(
        owner_request_id="tx-link-elsewhere",
        claims=[("scope:conduit:conduit-Z", ClaimMode.EXCLUSIVE)],
        reason_tag="link",
    ).acquired is True
