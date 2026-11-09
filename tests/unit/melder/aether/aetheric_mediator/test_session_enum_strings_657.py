"""Session enum canonical values with historical data and lifecycle contracts."""

import hashlib
import json
import pickle
from enum import Enum, StrEnum
from typing import Tuple, Type

import pytest

from melder.aether.aetheric_mediator.claim_mode import ClaimMode
from melder.aether.aetheric_mediator.identity import Identity
from melder.aether.aetheric_mediator.scope_keys import ScopeKey
from melder.aether.aetheric_mediator.staged_transaction import StagedTransaction
from melder.aether.aetheric_mediator.transaction_request import TransactionRequest
from melder.aether.aetheric_mediator.transaction_session import (
    OutcomePolicy, SessionStatus, TransactionSession,
)
from melder.aether.aetheric_mediator.transaction_type import TransactionType


class ForeignLegacy(StrEnum):
    """An unrelated family sharing old lower-case session values."""

    UNWIND = "unwind"
    BROKEN = "broken"


@pytest.mark.parametrize("family", [OutcomePolicy, SessionStatus])
def test_session_enums_use_names_and_accept_exact_old_tokens(family: Type[Enum]) -> None:
    """Canonical values match names while every historical string remains readable."""
    for member in family:
        assert member.value == member.name
        assert str(member) == member.name
        assert json.loads(json.dumps(member)) == member.name
        assert family(member.name) is member
        assert family(member.name.lower()) is member
        assert pickle.loads(pickle.dumps(member, protocol=4)) is member


@pytest.mark.parametrize(
    ("family", "invalid"),
    [
        (OutcomePolicy, "Unwind"),
        (OutcomePolicy, " unwind "),
        (OutcomePolicy, "unknown"),
        (OutcomePolicy, ForeignLegacy.UNWIND),
        (SessionStatus, "Broken"),
        (SessionStatus, " broken "),
        (SessionStatus, "unknown"),
        (SessionStatus, ForeignLegacy.BROKEN),
    ],
)
def test_invalid_and_foreign_legacy_inputs_are_rejected(
    family: Type[Enum], invalid: object,
) -> None:
    """The exact legacy mapping does not normalize unknown or foreign values."""
    with pytest.raises(ValueError):
        family(invalid)


def _session(policy: OutcomePolicy) -> Tuple[TransactionSession, Identity]:
    """Build one real session; the returned holder remains caller-owned."""
    holder = Identity(kind="probe", identity_id="one")
    request = TransactionRequest.build(
        request_id="probe",
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=holder,
        scope_claims={ScopeKey.frame("A"): ClaimMode.EXCLUSIVE},
        metadata={},
    )
    staged = StagedTransaction.from_request(request=request, admitted_at=0.0)
    return TransactionSession(
        request=request, staged=staged, holder=holder, outcome_policy=policy,
    ), holder


@pytest.mark.parametrize(
    ("policy", "legacy_policy", "terminal", "legacy_status", "runs_inverse"),
    [
        (OutcomePolicy.UNWIND, "unwind", SessionStatus.ABORTED, "aborted", True),
        (OutcomePolicy.LEAVE_BROKEN, "leave_broken", SessionStatus.BROKEN, "broken", False),
    ],
)
def test_session_snapshots_errors_and_rollback_keep_their_contract(
    policy: OutcomePolicy,
    legacy_policy: str,
    terminal: SessionStatus,
    legacy_status: str,
    runs_inverse: bool,
) -> None:
    """Real sessions retain old diagnostic strings and their distinct failure actions."""
    session, holder = _session(policy)
    called: list[str] = []
    try:
        assert session.describe()["status"] == "open"
        assert session.describe()["outcome_policy"] == legacy_policy
        session.register_rollback_action(action=lambda: called.append("ran"), description="undo")
        session.leave()
        status, residue = session.fail("probe")
        assert status is terminal
        assert called == (["ran"] if runs_inverse else [])
        assert residue == (() if runs_inverse else ("undo",))
        assert session.describe()["status"] == legacy_status
        assert session.describe()["outcome_policy"] == legacy_policy
        with pytest.raises(RuntimeError, match=f"status {legacy_status}"):
            session.fail("again")
    finally:
        session.cleanup()
        holder.cleanup()


def test_pre_migration_protocol_four_pickles_still_load() -> None:
    """All eight actual old session enum payloads retain their members."""
    snapshots = (
        (
            OutcomePolicy.UNWIND,
            "80049556000000000000008c336d656c6465722e6165746865722e61657468657269635f6d"
            "65646961746f722e7472616e73616374696f6e5f73657373696f6e948c0d4f7574636f6d65"
            "506f6c6963799493948c06756e77696e6494859452942e",
        ),
        (
            OutcomePolicy.LEAVE_BROKEN,
            "8004955c000000000000008c336d656c6465722e6165746865722e61657468657269635f6d"
            "65646961746f722e7472616e73616374696f6e5f73657373696f6e948c0d4f7574636f6d65"
            "506f6c6963799493948c0c6c656176655f62726f6b656e94859452942e",
        ),
        (
            SessionStatus.OPEN,
            "80049554000000000000008c336d656c6465722e6165746865722e61657468657269635f6d"
            "65646961746f722e7472616e73616374696f6e5f73657373696f6e948c0d53657373696f6e"
            "5374617475739493948c046f70656e94859452942e",
        ),
        (
            SessionStatus.COMMITTING,
            "8004955a000000000000008c336d656c6465722e6165746865722e61657468657269635f6d"
            "65646961746f722e7472616e73616374696f6e5f73657373696f6e948c0d53657373696f6e"
            "5374617475739493948c0a636f6d6d697474696e6794859452942e",
        ),
        (
            SessionStatus.COMMITTED,
            "80049559000000000000008c336d656c6465722e6165746865722e61657468657269635f6d"
            "65646961746f722e7472616e73616374696f6e5f73657373696f6e948c0d53657373696f6e"
            "5374617475739493948c09636f6d6d697474656494859452942e",
        ),
        (
            SessionStatus.ABORTING,
            "80049558000000000000008c336d656c6465722e6165746865722e61657468657269635f6d"
            "65646961746f722e7472616e73616374696f6e5f73657373696f6e948c0d53657373696f6e"
            "5374617475739493948c0861626f7274696e6794859452942e",
        ),
        (
            SessionStatus.ABORTED,
            "80049557000000000000008c336d656c6465722e6165746865722e61657468657269635f6d"
            "65646961746f722e7472616e73616374696f6e5f73657373696f6e948c0d53657373696f6e"
            "5374617475739493948c0761626f7274656494859452942e",
        ),
        (
            SessionStatus.BROKEN,
            "80049556000000000000008c336d656c6465722e6165746865722e61657468657269635f6d"
            "65646961746f722e7472616e73616374696f6e5f73657373696f6e948c0d53657373696f6e"
            "5374617475739493948c0662726f6b656e94859452942e",
        ),
    )
    payloads = [bytes.fromhex(encoded) for _, encoded in snapshots]
    assert hashlib.sha256(b"".join(payloads)).hexdigest() == (
        "bff8fb52c264285cc90d9e905ae86b249d0df7645d6b6c2287057f8beb7a22a7"
    )
    for (expected, _), payload in zip(snapshots, payloads):
        assert pickle.loads(payload) is expected
