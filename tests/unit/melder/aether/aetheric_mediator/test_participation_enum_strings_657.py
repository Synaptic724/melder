"""Participation state canonical values and legacy record compatibility."""

import hashlib
import json
import pickle
from enum import StrEnum

import pytest

from melder.aether.aetheric_mediator.information_registry import InformationRegistry
from melder.aether.aetheric_mediator.participation import ParticipationState


class ForeignState(StrEnum):
    """An unrelated family sharing the canonical active token."""

    ACTIVE = "ACTIVE"


@pytest.mark.parametrize(
    ("member", "legacy"),
    [
        (ParticipationState.REGISTERED, "registered"),
        (ParticipationState.CONFIGURED, "configured"),
        (ParticipationState.ACTIVE, "active"),
        (ParticipationState.INACTIVE, "inactive"),
    ],
)
def test_canonical_values_and_exact_legacy_inputs(
    member: ParticipationState, legacy: str,
) -> None:
    """Canonical values match names while exact historical tokens remain readable."""
    assert member.value == member.name
    assert str(member) == member.name
    assert json.loads(json.dumps(member)) == member.name
    assert ParticipationState(member.name) is member
    assert ParticipationState(legacy) is member


@pytest.mark.parametrize("invalid", ["Active", " active ", "unknown", "", 42, None])
def test_unknown_or_noncanonical_legacy_values_remain_invalid(invalid: object) -> None:
    """No general case folding, whitespace normalization or numeric mapping is added."""
    with pytest.raises(ValueError):
        ParticipationState(invalid)


@pytest.mark.parametrize(
    ("member", "legacy", "emits"),
    [
        (ParticipationState.REGISTERED, "registered", False),
        (ParticipationState.CONFIGURED, "configured", False),
        (ParticipationState.ACTIVE, "active", True),
        (ParticipationState.INACTIVE, "inactive", False),
    ],
)
def test_registry_rows_keep_plain_legacy_tokens_and_typed_state(
    member: ParticipationState, legacy: str, emits: bool,
) -> None:
    """Both registry views keep old row strings and enforce actual family identity."""
    registry = InformationRegistry()
    try:
        registry.set_participation(subsystem_name="demo", state=member, reporter="test")
        row = registry.describe_participants()[0]
        assert type(row["state"]) is str
        assert row["state"] == legacy
        assert row["emits"] is emits
        assert registry.is_participating("demo") is emits
        assert registry.describe()["participants"][0]["state"] == legacy
        assert registry.participants_in_state(member) == ("demo",)

        with pytest.raises(TypeError):
            registry.set_participation(subsystem_name="demo", state=legacy, reporter="test")
        with pytest.raises(TypeError):
            registry.set_participation(subsystem_name="demo", state=ForeignState.ACTIVE, reporter="test")
        with pytest.raises(TypeError):
            registry.participants_in_state(ForeignState.ACTIVE)
    finally:
        registry.cleanup()


def test_pre_migration_protocol_four_pickles_still_load() -> None:
    """All four actual old enum payloads resolve to their original members."""
    snapshots = (
        (
            ParticipationState.REGISTERED,
            "80049559000000000000008c2d6d656c6465722e6165746865722e61657468657269635f6d"
            "65646961746f722e70617274696369706174696f6e948c1250617274696369706174696f6e"
            "53746174659493948c0a7265676973746572656494859452942e",
        ),
        (
            ParticipationState.CONFIGURED,
            "80049559000000000000008c2d6d656c6465722e6165746865722e61657468657269635f6d"
            "65646961746f722e70617274696369706174696f6e948c1250617274696369706174696f6e"
            "53746174659493948c0a636f6e6669677572656494859452942e",
        ),
        (
            ParticipationState.ACTIVE,
            "80049555000000000000008c2d6d656c6465722e6165746865722e61657468657269635f6d"
            "65646961746f722e70617274696369706174696f6e948c1250617274696369706174696f6e"
            "53746174659493948c0661637469766594859452942e",
        ),
        (
            ParticipationState.INACTIVE,
            "80049557000000000000008c2d6d656c6465722e6165746865722e61657468657269635f6d"
            "65646961746f722e70617274696369706174696f6e948c1250617274696369706174696f6e"
            "53746174659493948c08696e61637469766594859452942e",
        ),
    )
    payloads = [bytes.fromhex(encoded) for _, encoded in snapshots]
    assert hashlib.sha256(b"".join(payloads)).hexdigest() == (
        "cf7575216f80f97ca14e7b408f20a8bc226b8e49a7b94fb6acddfbc0570761c4"
    )
    for (expected, _), payload in zip(snapshots, payloads):
        assert pickle.loads(payload) is expected
