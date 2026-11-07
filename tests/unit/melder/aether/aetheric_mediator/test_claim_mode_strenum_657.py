"""Mediator claim enum names and stable short-code request/evidence contracts."""

import base64
import pickle
from enum import StrEnum

import pytest

from melder.aether.aetheric_mediator.claim_mode import ClaimCompatibility, ClaimMode
from melder.aether.aetheric_mediator.claim_table import ClaimTable
from melder.aether.aetheric_mediator.identity import Identity
from melder.aether.aetheric_mediator.transaction_request import TransactionRequest
from melder.aether.aetheric_mediator.transaction_type import TransactionType


class ForeignMode(StrEnum):
    """A separate family with a canonical value equal to a mediator mode."""

    SHARED = "SHARED"


@pytest.mark.parametrize(
    ("member", "legacy"),
    ((ClaimMode.EXCLUSIVE, "x"), (ClaimMode.SHARED, "s"), (ClaimMode.INTENT, "ix")),
)
def test_claim_mode_value_is_exact_name_and_old_token_reads(member: ClaimMode, legacy: str) -> None:
    """The selected exact value and the historical input both identify one member."""
    assert member.value == member.name
    assert ClaimMode(member.name) is member
    assert ClaimMode(legacy) is member


@pytest.mark.parametrize(
    ("payload", "expected"),
    (
        ("gASVRAAAAAAAAACMKm1lbGRlci5hZXRoZXIuYWV0aGVyaWNfbWVkaWF0b3IuY2xhaW1fbW9kZZSMCUNsYWltTW9kZZSTlIwBeJSFlFKULg==", ClaimMode.EXCLUSIVE),
        ("gASVRAAAAAAAAACMKm1lbGRlci5hZXRoZXIuYWV0aGVyaWNfbWVkaWF0b3IuY2xhaW1fbW9kZZSMCUNsYWltTW9kZZSTlIwBc5SFlFKULg==", ClaimMode.SHARED),
        ("gASVRQAAAAAAAACMKm1lbGRlci5hZXRoZXIuYWV0aGVyaWNfbWVkaWF0b3IuY2xhaW1fbW9kZZSMCUNsYWltTW9kZZSTlIwCaXiUhZRSlC4=", ClaimMode.INTENT),
    ),
)
def test_old_claim_pickles_keep_member_identity(payload: str, expected: ClaimMode) -> None:
    """Captured old short-code pickles remain readable."""
    assert pickle.loads(base64.b64decode(payload)) is expected


def test_request_and_claim_evidence_keep_short_codes() -> None:
    """Real request and contention evidence keep x/s/ix wire strings."""
    holder = Identity(kind="agent", identity_id="holder")
    contender = Identity(kind="agent", identity_id="other")
    request = TransactionRequest.build(
        request_id="request-657", transaction_type=TransactionType.FRAME_CREATE,
        submitter=holder,
        scope_claims={"world": ClaimMode.INTENT, "frame:A": ClaimMode.EXCLUSIVE, "read": ClaimMode.SHARED},
        metadata={},
    )
    table = ClaimTable()
    try:
        assert request.scope_claims == (("frame:A", "x"), ("read", "s"), ("world", "ix"))
        assert request.claim_map() == {
            "frame:A": ClaimMode.EXCLUSIVE, "read": ClaimMode.SHARED, "world": ClaimMode.INTENT,
        }
        assert table.try_acquire(holder, {"scope": ClaimMode.EXCLUSIVE}) == ()
        assert table.describe()["scopes"]["scope"][0][1] == "x"
        blocks = table.try_acquire(contender, {"scope": ClaimMode.SHARED})
        assert len(blocks) == 1
        assert blocks[0].describe() == f"scope held x by {holder.describe()} (requested s)"
        blocks[0].cleanup()
    finally:
        table.cleanup()
        request.cleanup()
        holder.cleanup()
        contender.cleanup()


def test_compatibility_and_request_require_the_mediator_family() -> None:
    """Equal raw or foreign strings cannot become typed claims implicitly."""
    with pytest.raises(TypeError):
        ClaimCompatibility.permits(ForeignMode.SHARED, ClaimMode.SHARED)
    with pytest.raises(TypeError):
        ClaimCompatibility.permits("SHARED", ClaimMode.SHARED)
    holder = Identity(kind="agent", identity_id="holder")
    try:
        with pytest.raises(TypeError):
            TransactionRequest.build(
                request_id="request-657", transaction_type=TransactionType.FRAME_CREATE,
                submitter=holder, scope_claims={"scope": ForeignMode.SHARED}, metadata={},
            )
    finally:
        holder.cleanup()


@pytest.mark.parametrize("invalid", ("X", "exclusive", "unknown", None, []))
def test_unknown_claim_values_are_refused(invalid: object) -> None:
    """Only exact canonical and historical short codes are accepted."""
    with pytest.raises(ValueError):
        ClaimMode(invalid)
