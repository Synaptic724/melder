"""Admission reason exact values and historical evidence compatibility."""

import hashlib
import json
import pickle
from enum import StrEnum

import pytest

from melder.aether.aetheric_mediator.admission_result import AdmissionReason, AdmissionResult


@pytest.mark.parametrize(
    ("reason", "legacy"),
    [
        (AdmissionReason.SCOPE_CONTENDED, "scope_contended"),
        (AdmissionReason.WAIT_TIMEOUT, "wait_timeout"),
        (AdmissionReason.PLANE_CLEANED, "plane_cleaned"),
        (AdmissionReason.NO_STRATEGY, "no_strategy"),
        (AdmissionReason.INVALID_REQUEST, "invalid_request"),
    ],
)
def test_reason_values_match_names_and_accept_historical_tokens(
    reason: AdmissionReason, legacy: str,
) -> None:
    """Canonical string output matches the name while old tokens stay readable."""
    assert reason.value == reason.name
    assert str(reason) == reason.name
    assert json.loads(json.dumps(reason)) == reason.name
    assert AdmissionReason(reason.name) is reason
    assert AdmissionReason(legacy) is reason


def test_legacy_lookup_rejects_foreign_enum_without_claiming_canonical_separation() -> None:
    """Only the missing-value reader enforces the family boundary."""
    class ForeignReason(StrEnum):
        legacy = "scope_contended"
        canonical = "SCOPE_CONTENDED"

    with pytest.raises(ValueError):
        AdmissionReason(ForeignReason.legacy)
    assert AdmissionReason(ForeignReason.canonical) is AdmissionReason.SCOPE_CONTENDED

@pytest.mark.parametrize("invalid", ["Scope_Contended", " wait_timeout ", "unknown", "", 42, None])
def test_unknown_or_mixed_case_reason_values_remain_invalid(invalid: object) -> None:
    """Only the exact historical spellings are admitted."""
    with pytest.raises(ValueError):
        AdmissionReason(invalid)


@pytest.mark.parametrize(
    ("reason", "legacy"),
    [
        (AdmissionReason.SCOPE_CONTENDED, "scope_contended"),
        (AdmissionReason.WAIT_TIMEOUT, "wait_timeout"),
        (AdmissionReason.PLANE_CLEANED, "plane_cleaned"),
        (AdmissionReason.NO_STRATEGY, "no_strategy"),
        (AdmissionReason.INVALID_REQUEST, "invalid_request"),
    ],
)
def test_verdict_keeps_historical_diagnostic_code(
    reason: AdmissionReason, legacy: str,
) -> None:
    """The real verdict retains its detached lower-case machine-readable code."""
    verdict = AdmissionResult.refused(reasons=(reason,), evidence=("held",))
    try:
        assert verdict.describe() == f"refused [{legacy}]: held"
        assert verdict.reasons == (reason,)
    finally:
        verdict.cleanup()


def test_pre_migration_protocol_four_pickles_still_load() -> None:
    """Read all five actual old payloads through the original enum module."""
    snapshots = (
        (
            AdmissionReason.SCOPE_CONTENDED,
            "8004955e000000000000008c306d656c6465722e6165746865722e61657468657269635f6d"
            "65646961746f722e61646d697373696f6e5f726573756c74948c0f41646d697373696f6e52"
            "6561736f6e9493948c0f73636f70655f636f6e74656e64656494859452942e",
        ),
        (
            AdmissionReason.WAIT_TIMEOUT,
            "8004955b000000000000008c306d656c6465722e6165746865722e61657468657269635f6d"
            "65646961746f722e61646d697373696f6e5f726573756c74948c0f41646d697373696f6e52"
            "6561736f6e9493948c0c776169745f74696d656f757494859452942e",
        ),
        (
            AdmissionReason.PLANE_CLEANED,
            "8004955c000000000000008c306d656c6465722e6165746865722e61657468657269635f6d"
            "65646961746f722e61646d697373696f6e5f726573756c74948c0f41646d697373696f6e52"
            "6561736f6e9493948c0d706c616e655f636c65616e656494859452942e",
        ),
        (
            AdmissionReason.NO_STRATEGY,
            "8004955a000000000000008c306d656c6465722e6165746865722e61657468657269635f6d"
            "65646961746f722e61646d697373696f6e5f726573756c74948c0f41646d697373696f6e52"
            "6561736f6e9493948c0b6e6f5f737472617465677994859452942e",
        ),
        (
            AdmissionReason.INVALID_REQUEST,
            "8004955e000000000000008c306d656c6465722e6165746865722e61657468657269635f6d"
            "65646961746f722e61646d697373696f6e5f726573756c74948c0f41646d697373696f6e52"
            "6561736f6e9493948c0f696e76616c69645f7265717565737494859452942e",
        ),
    )
    payloads = [bytes.fromhex(encoded) for _, encoded in snapshots]
    assert hashlib.sha256(b"".join(payloads)).hexdigest() == (
        "4701d1feac434947da1b32e9abc420ae6bd68ade89dcbd8d06927df6e93b1148"
    )
    for (expected, _), payload in zip(snapshots, payloads):
        assert pickle.loads(payload) is expected
