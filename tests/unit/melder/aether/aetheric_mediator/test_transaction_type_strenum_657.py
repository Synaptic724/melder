"""Regression coverage for exact mediator transaction names and old tokens."""

import base64
import pickle

import pytest

from melder.aether.aetheric_mediator.claim_mode import ClaimMode
from melder.aether.aetheric_mediator.identity import Identity
from melder.aether.aetheric_mediator.information_registry import InformationRegistry
from melder.aether.aetheric_mediator.staged_transaction import StagedTransaction
from melder.aether.aetheric_mediator.strategy_builder import StrategyBuilder
from melder.aether.aetheric_mediator.transaction_request import TransactionRequest
from melder.aether.aetheric_mediator.transaction_session import TransactionSession
from melder.aether.aetheric_mediator.transaction_strategy import TransactionStrategy
from melder.aether.aetheric_mediator.transaction_type import TransactionType


@pytest.mark.parametrize("member", tuple(TransactionType))
def test_transaction_type_value_is_exact_member_name(member: TransactionType) -> None:
    """Names are values while the old lowercase constructor remains valid."""
    assert member.value == member.name
    assert str(member) == member.name
    assert TransactionType(member.name) is member
    assert TransactionType(member.name.lower()) is member


@pytest.mark.parametrize(
    ("payload", "expected"),
    (
        ("gASVWwAAAAAAAACMMG1lbGRlci5hZXRoZXIuYWV0aGVyaWNfbWVkaWF0b3IudHJhbnNhY3Rpb25fdHlwZZSMD1RyYW5zYWN0aW9uVHlwZZSTlIwMZnJhbWVfY3JlYXRllIWUUpQu", TransactionType.FRAME_CREATE),
        ("gASVYQAAAAAAAACMMG1lbGRlci5hZXRoZXIuYWV0aGVyaWNfbWVkaWF0b3IudHJhbnNhY3Rpb25fdHlwZZSMD1RyYW5zYWN0aW9uVHlwZZSTlIwSc3Vic3lzdGVtX2FjdGl2YXRllIWUUpQu", TransactionType.SUBSYSTEM_ACTIVATE),
        ("gASVWwAAAAAAAACMMG1lbGRlci5hZXRoZXIuYWV0aGVyaWNfbWVkaWF0b3IudHJhbnNhY3Rpb25fdHlwZZSMD1RyYW5zYWN0aW9uVHlwZZSTlIwMYWdlbnRfcmVwYWlylIWUUpQu", TransactionType.AGENT_REPAIR),
    ),
)
def test_original_pickles_remain_readable(payload: str, expected: TransactionType) -> None:
    """Previously serialized lowercase values reconstruct their original member."""
    assert pickle.loads(base64.b64decode(payload)) is expected


@pytest.mark.parametrize("value", ("Frame_Create", "FRAME_create", "unknown", ""))
def test_unknown_spellings_are_not_normalized(value: str) -> None:
    """Only canonical and exact historical spellings are accepted."""
    with pytest.raises(ValueError):
        TransactionType(value)


@pytest.fixture(name="live_records")
def _live_records():
    """Create real request, staged, session and reporting objects with one owner."""
    holder = Identity(kind="worker", identity_id="one")
    request = TransactionRequest.build(
        request_id="req-1",
        transaction_type=TransactionType.FRAME_CREATE,
        submitter=holder,
        scope_claims={"world": ClaimMode.EXCLUSIVE},
        metadata={},
    )
    staged = StagedTransaction.from_request(request=request, admitted_at=1.0)
    session = TransactionSession(request=request, staged=staged, holder=holder)
    registry = InformationRegistry()
    registry.register_activity(staged)
    try:
        yield holder, request, staged, session, registry
    finally:
        registry.cleanup()
        session.cleanup()
        holder.cleanup()


def test_descriptions_and_fact_records_keep_original_tokens(live_records) -> None:
    """Established reporting boundaries continue to emit lowercase tokens."""
    holder, request, staged, session, registry = live_records
    assert request.describe().startswith("frame_create by ")
    assert staged.describe().startswith("frame_create by ")
    assert session.describe()["transaction_type"] == "frame_create"
    TransactionStrategy.apply_commit_delta(
        information_registry=registry, submitter=holder, staged=staged
    )
    assert registry.get_fact("world")["fact_family"] == "frame_create"


@pytest.mark.parametrize("query", ("frame_create", TransactionType.FRAME_CREATE))
def test_activity_accepts_old_string_and_member(live_records, query: str) -> None:
    """The existing filter accepts both its string token and enum member."""
    registry = live_records[-1]
    assert registry.activity_by_type(query) == ("req-1",)


def test_activity_accepts_exact_new_string(live_records) -> None:
    """The exact canonical enum value is also a usable activity filter."""
    registry = live_records[-1]
    assert registry.activity_by_type("FRAME_CREATE") == ("req-1",)
    assert registry.activity_by_type("unknown") == ()


def test_strategy_description_and_missing_error_keep_old_tokens() -> None:
    """Strategy reporting keeps its original keys and diagnostic spelling."""
    builder = StrategyBuilder()
    try:
        assert "frame_create" in builder.describe()
        builder._strategies.pop(TransactionType.AGENT_REPAIR)
        with pytest.raises(KeyError, match="agent_repair"):
            builder.resolve(TransactionType.AGENT_REPAIR)
    finally:
        builder.cleanup()
