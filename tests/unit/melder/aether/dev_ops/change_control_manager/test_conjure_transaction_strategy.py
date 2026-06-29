from typing import Tuple

import pytest

from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.conjure_transaction_strategy import (
    ConjureTransactionStrategy,
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


def _spellbook_identity(owner_id: str) -> DevopsIdentity:
    """Build a pre-conjure spellbook identity that supports the conjure transaction."""
    return DevopsIdentity(
        owner_kind="spellbook",
        owner_id=owner_id,
        aetheric_frame_name="frame-1",
        metadata={"conjured": False, "conduit_id": None},
        available_transactions=("bind", "scan", "conjure"),
    )


# ---------------------------------------------------------------------------
# CONJURE
# ---------------------------------------------------------------------------
def test_conjure_seals_only_the_owning_spellbook_exclusive() -> None:
    """
    Purpose:
        Verify a conjure seals exactly the owning spellbook EXCLUSIVE and nothing
        else, because the root conduit does not exist yet at admission.
    Contract:
        - The spellbook scope is the sole claim and carries EXCLUSIVE.
        - No conduit, ward, cluster, or binding scope is claimed.
    Returns:
        None.
    Raises:
        AssertionError: If the conjure seal is not spellbook-only EXCLUSIVE.
    """
    transaction_manager, registry = _manager_and_registry()
    identity = _spellbook_identity("spellbook-1")
    registry.register_identity(identity)

    plan = ConjureTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={"spellbook_id": "spellbook-1"},
    )

    spellbook_scope = transaction_manager.make_scope_key_spellbook("spellbook-1")
    assert dict(plan["scope_claims"]) == {spellbook_scope: ClaimMode.EXCLUSIVE.value}
    assert plan["scope_keys"] == (spellbook_scope,)
    assert plan["conduit_ids"] == tuple()
    assert plan["binding_keys"] == tuple()
    assert plan["contract_keys"] == tuple()


def test_conjure_uses_spellbook_initiator_and_conjure_capabilities() -> None:
    """
    Purpose:
        Verify the conjure plan uses the spellbook pseudo-owner initiator and the
        conjure capability set, mirroring the pre-conjure bind plan.
    Contract:
        - initiator_conduit_id is `spellbook:<id>`.
        - granted and required capabilities are exactly ("conjure",).
        - the plan and its metadata carry the resolved spellbook id and the
          root-conduit conjure mode.
    Returns:
        None.
    Raises:
        AssertionError: If the initiator, capability, or metadata shape diverges.
    """
    transaction_manager, registry = _manager_and_registry()
    identity = _spellbook_identity("spellbook-7")
    registry.register_identity(identity)

    plan = ConjureTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={"spellbook_id": "spellbook-7"},
    )

    assert plan["initiator_conduit_id"] == "spellbook:spellbook-7"
    assert plan["spellbook_id"] == "spellbook-7"
    assert plan["granted_capabilities"] == ("conjure",)
    assert plan["required_capabilities"] == ("conjure",)
    assert plan["metadata"]["conjure_mode"] == "root_conduit"
    assert plan["metadata"]["spellbook_id"] == "spellbook-7"


def test_conjure_falls_back_to_identity_owner_when_metadata_omits_spellbook_id() -> None:
    """
    Purpose:
        Verify the strategy derives the spellbook id from the submitter identity
        when caller metadata omits it.
    Contract:
        - Empty caller metadata still seals the identity's owning spellbook.
    Returns:
        None.
    Raises:
        AssertionError: If the identity-owner fallback is not used.
    """
    transaction_manager, registry = _manager_and_registry()
    identity = _spellbook_identity("spellbook-fallback")
    registry.register_identity(identity)

    plan = ConjureTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={},
    )

    spellbook_scope = transaction_manager.make_scope_key_spellbook("spellbook-fallback")
    assert dict(plan["scope_claims"]) == {spellbook_scope: ClaimMode.EXCLUSIVE.value}
    assert plan["initiator_conduit_id"] == "spellbook:spellbook-fallback"


def test_conjure_on_start_and_on_end_are_envelope_noops() -> None:
    """
    Purpose:
        Verify the conjure strategy performs no start/end side effects; the
        creation pipeline owns the actual build inside the held window.
    Contract:
        - on_start and on_end return None and raise nothing.
    Returns:
        None.
    Raises:
        AssertionError: If either envelope hook returns a value.
    """
    transaction_manager, registry = _manager_and_registry()
    identity = _spellbook_identity("spellbook-1")
    registry.register_identity(identity)

    assert (
        ConjureTransactionStrategy.on_start(
            devops_information_registry=registry,
            identity=identity,
            metadata={},
        )
        is None
    )
    assert (
        ConjureTransactionStrategy.on_end(
            devops_information_registry=registry,
            identity=identity,
            metadata={},
        )
        is None
    )


# ---------------------------------------------------------------------------
# CONJURE serialization behavior (strategy claim -> embargo lock table)
# ---------------------------------------------------------------------------
@pytest.fixture
def embargo():
    """Provide a fresh embargo manager with deterministic teardown."""
    manager = ChangeControlEmbargoManager()
    yield manager
    if not manager.cleaned:
        manager.cleanup()


def _conjure_claims(
        transaction_manager: ChangeControlTransactionManager,
        registry: DevopsInformationRegistry,
        spellbook_id: str,
) -> Tuple[Tuple[str, str], ...]:
    """Return the conjure strategy's scope_claims for one spellbook id."""
    identity = _spellbook_identity(spellbook_id)
    registry.register_identity(identity)
    plan = ConjureTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={"spellbook_id": spellbook_id},
    )
    return plan["scope_claims"]


def test_conjure_claim_blocks_a_second_conjure_on_the_same_spellbook(embargo) -> None:
    """
    Purpose:
        Verify that once one conjure holds its spellbook claim, a second conjure
        on the same spellbook is refused -- one conjure per spellbook at a time.
    Contract:
        - The first acquisition succeeds; the second is blocked.
        - Blocking evidence names the spellbook scope and the holding request id.
    Returns:
        None.
    Raises:
        AssertionError: If the second conjure is not blocked by the first.
    """
    transaction_manager, registry = _manager_and_registry()
    claims = _conjure_claims(transaction_manager, registry, "spellbook-1")

    first = embargo.try_acquire(
        owner_request_id="tx-conjure-1",
        claims=claims,
        reason_tag="conjure",
    )
    assert first.acquired is True

    second = embargo.try_acquire(
        owner_request_id="tx-conjure-2",
        claims=claims,
        reason_tag="conjure",
    )
    assert second.acquired is False
    spellbook_scope = transaction_manager.make_scope_key_spellbook("spellbook-1")
    assert any(block[0] == spellbook_scope for block in second.blocking)
    assert any(block[1] == "tx-conjure-1" for block in second.blocking)


def test_conjure_claim_blocks_an_intent_claim_on_the_same_spellbook(embargo) -> None:
    """
    Purpose:
        Verify a held conjure (EXCLUSIVE) refuses a bind/link/cluster-shaped
        INTENT claim on the same spellbook for the duration.
    Contract:
        - The conjure acquisition succeeds.
        - A subsequent INTENT claim on the same spellbook scope is blocked,
          because EXCLUSIVE is incompatible with every other mode.
    Returns:
        None.
    Raises:
        AssertionError: If the INTENT claim is not blocked by the conjure.
    """
    transaction_manager, registry = _manager_and_registry()
    claims = _conjure_claims(transaction_manager, registry, "spellbook-1")
    assert embargo.try_acquire(
        owner_request_id="tx-conjure",
        claims=claims,
        reason_tag="conjure",
    ).acquired is True

    spellbook_scope = transaction_manager.make_scope_key_spellbook("spellbook-1")
    bind_like = embargo.try_acquire(
        owner_request_id="tx-bind",
        claims=[(spellbook_scope, ClaimMode.INTENT)],
        reason_tag="bind",
    )
    assert bind_like.acquired is False


def test_conjures_on_different_spellbooks_admit_in_parallel(embargo) -> None:
    """
    Purpose:
        Verify conjures of different spellbooks hold disjoint scopes and both
        admit, so spellbook-local sealing does not serialize the whole frame.
    Contract:
        - Two conjures keyed to different spellbooks both acquire.
    Returns:
        None.
    Raises:
        AssertionError: If disjoint-spellbook conjures block each other.
    """
    transaction_manager, registry = _manager_and_registry()
    claims_a = _conjure_claims(transaction_manager, registry, "spellbook-A")
    claims_b = _conjure_claims(transaction_manager, registry, "spellbook-B")

    assert embargo.try_acquire(
        owner_request_id="tx-a",
        claims=claims_a,
        reason_tag="conjure",
    ).acquired is True
    assert embargo.try_acquire(
        owner_request_id="tx-b",
        claims=claims_b,
        reason_tag="conjure",
    ).acquired is True


def test_second_conjure_admits_after_the_first_releases(embargo) -> None:
    """
    Purpose:
        Verify a blocked conjure admits once the holding conjure releases its
        spellbook claim -- the "delay other conjures, then proceed" behavior.
    Contract:
        - The second conjure is blocked while the first holds the claim, and
          admits after the first releases.
    Returns:
        None.
    Raises:
        AssertionError: If the second conjure does not admit after release.
    """
    transaction_manager, registry = _manager_and_registry()
    claims = _conjure_claims(transaction_manager, registry, "spellbook-1")

    assert embargo.try_acquire(
        owner_request_id="tx-conjure-1",
        claims=claims,
        reason_tag="conjure",
    ).acquired is True
    assert embargo.try_acquire(
        owner_request_id="tx-conjure-2",
        claims=claims,
        reason_tag="conjure",
    ).acquired is False

    embargo.release_owner("tx-conjure-1")

    assert embargo.try_acquire(
        owner_request_id="tx-conjure-2",
        claims=claims,
        reason_tag="conjure",
    ).acquired is True
