"""Regression coverage for exact DevOps claim names and legacy claim tokens."""

import base64
import pickle

import pytest

from melder.aether.aetheric_frame.dev_ops.change_control_manager.embargo_manager.embargo_manager import (
    ChangeControlEmbargoManager,
    ClaimMode,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.conjure_transaction_strategy import (
    ConjureTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_manager import (
    ChangeControlTransactionManager,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)
from melder.aether.aetheric_frame.dev_ops.devops_identity import DevopsIdentity


@pytest.mark.parametrize("member,old", ((ClaimMode.EXCLUSIVE, "x"), (ClaimMode.SHARED, "s"), (ClaimMode.INTENT, "ix")))
def test_claim_value_is_exact_member_name(member: ClaimMode, old: str) -> None:
    """Values match names while the original wire strings remain readable."""
    assert member.value == member.name
    assert str(member) == member.name
    assert ClaimMode(member.name) is member
    assert ClaimMode(old) is member


@pytest.mark.parametrize(
    "payload,expected",
    (
        ("gASVdQAAAAAAAACMW21lbGRlci5hZXRoZXIuYWV0aGVyaWNfZnJhbWUuZGV2X29wcy5jaGFuZ2VfY29udHJvbF9tYW5hZ2VyLmVtYmFyZ29fbWFuYWdlci5lbWJhcmdvX21hbmFnZXKUjAlDbGFpbU1vZGWUk5SMAXiUhZRSlC4=", ClaimMode.EXCLUSIVE),
        ("gASVdQAAAAAAAACMW21lbGRlci5hZXRoZXIuYWV0aGVyaWNfZnJhbWUuZGV2X29wcy5jaGFuZ2VfY29udHJvbF9tYW5hZ2VyLmVtYmFyZ29fbWFuYWdlci5lbWJhcmdvX21hbmFnZXKUjAlDbGFpbU1vZGWUk5SMAXOUhZRSlC4=", ClaimMode.SHARED),
        ("gASVdgAAAAAAAACMW21lbGRlci5hZXRoZXIuYWV0aGVyaWNfZnJhbWUuZGV2X29wcy5jaGFuZ2VfY29udHJvbF9tYW5hZ2VyLmVtYmFyZ29fbWFuYWdlci5lbWJhcmdvX21hbmFnZXKUjAlDbGFpbU1vZGWUk5SMAml4lIWUUpQu", ClaimMode.INTENT),
    ),
)
def test_original_pickles_remain_readable(payload: str, expected: ClaimMode) -> None:
    """Previously serialized short codes reconstruct the same mode."""
    assert pickle.loads(base64.b64decode(payload)) is expected


@pytest.mark.parametrize("bad", ("X", "Ix", "exclusive", "unknown", ""))
def test_unknown_claim_spellings_are_rejected(bad: str) -> None:
    """Only original tokens and exact canonical values are accepted."""
    with pytest.raises(ValueError):
        ClaimMode(bad)


def test_request_and_blocking_evidence_keep_original_tokens() -> None:
    """Actual request and contention surfaces retain x/s/ix strings."""
    manager = ChangeControlTransactionManager()
    embargo = ChangeControlEmbargoManager()
    try:
        request = manager.build_request(
            request_type=ChangeTransactionType.BIND,
            initiator_conduit_id="owner",
            scope_claims=(("shared", ClaimMode.SHARED), ("intent", "ix")),
        )
        assert request.scope_claims == (("shared", "s"), ("intent", "ix"))
        assert embargo.try_acquire(
            owner_request_id="one", claims=request.scope_claims, reason_tag="bind"
        ).acquired
        blocked = embargo.try_acquire(
            owner_request_id="two", claims=(("shared", ClaimMode.EXCLUSIVE),), reason_tag="bind"
        )
        assert blocked.blocking == (("shared", "one", "s"),)
        assert not blocked.acquired
    finally:
        embargo.cleanup()
        manager.cleanup()


def test_real_conjure_plan_retains_exclusive_token() -> None:
    """A plan and its request retain the original exclusive scope code."""
    manager = ChangeControlTransactionManager()
    identity = DevopsIdentity(
        owner_kind="spellbook", owner_id="book", aetheric_frame_name="frame",
        metadata={}, available_transactions=("conjure",),
    )
    try:
        plan = ConjureTransactionStrategy.build_start_plan(
            transaction_manager=manager, devops_information_registry=None,
            identity=identity, metadata={},
        )
        assert plan["scope_claims"] == (("scope:spellbook:book", "x"),)
        request = manager.build_request(
            request_type=ChangeTransactionType.CONJURE,
            initiator_conduit_id=plan["initiator_conduit_id"],
            scope_claims=plan["scope_claims"],
        )
        assert request.scope_claims == (("scope:spellbook:book", "x"),)
    finally:
        identity.cleanup()
        manager.cleanup()
