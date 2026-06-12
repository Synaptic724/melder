"""Unit ring for the scope-acquisition control plane.

Covers the patch-lane contracts from
`system_docs/patches/active/devops_scope_acquisition_2026_06_12/`:

- claim-mode compatibility matrix truth table
- atomic all-or-nothing acquisition with blocking evidence
- same-owner re-entrance and sole-holder upgrade
- orchestrator admission via acquisition (scope_conflict evidence, release on
  commit)
- mediator scope-local pending: wake-on-release admission and bounded timeout
- strategy commit deltas stamping registry fact baselines
- registry fact-record report/get/list and generation increments
"""

import threading
import time

import pytest
from unittest.mock import MagicMock

from melder.aether.aetheric_frame.dev_ops.change_control_manager.conflict_manager.conflict_manager import (
    ChangeControlConflictManager,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.embargo_manager.embargo_manager import (
    AcquisitionDecision,
    ChangeControlEmbargoManager,
    ClaimMode,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.orchestrator.orchestrator import (
    ChangeControlOrchestrator,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_manager import (
    ChangeControlTransactionManager,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_mediator import (
    TransactionMediator,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)
from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
    DevopsInformationRegistry,
)


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------

@pytest.fixture
def embargo_manager():
    manager = ChangeControlEmbargoManager()
    yield manager
    if not manager.cleaned:
        manager.cleanup()


@pytest.fixture
def transaction_manager():
    manager = ChangeControlTransactionManager()
    yield manager
    if not manager.cleaned:
        manager.cleanup()


@pytest.fixture
def orchestrator():
    orchestrator = ChangeControlOrchestrator()
    yield orchestrator
    if not orchestrator.cleaned:
        orchestrator.cleanup()


@pytest.fixture
def conflict_manager():
    manager = ChangeControlConflictManager()
    yield manager
    if not manager.cleaned:
        manager.cleanup()


@pytest.fixture
def registry():
    registry = DevopsInformationRegistry("frame-1")
    yield registry
    if not registry.cleaned:
        registry.cleanup()


def _make_identity(owner_id="conduit-A", owner_kind="conduit"):
    identity = MagicMock()
    identity.owner_id = owner_id
    identity.owner_kind = owner_kind
    identity.supports_transaction.return_value = True
    identity.describe.return_value = {"owner_id": owner_id, "owner_kind": owner_kind}
    identity.metadata = {}
    return identity


def _make_mediator(
        transaction_manager,
        conflict_manager,
        embargo_manager,
        orchestrator,
        *,
        registry=None,
        max_wait=30.0,
):
    return TransactionMediator(
        transaction_manager=transaction_manager,
        conflict_manager=conflict_manager,
        embargo_manager=embargo_manager,
        orchestrator=orchestrator,
        devops_information_registry=registry,
        max_transaction_wait_time_in_seconds=max_wait,
    )


# ----------------------------------------------------------------------
# 1. Compatibility matrix truth table
# ----------------------------------------------------------------------

@pytest.mark.parametrize(
    "held, requested, expected",
    [
        (ClaimMode.EXCLUSIVE, ClaimMode.EXCLUSIVE, False),
        (ClaimMode.EXCLUSIVE, ClaimMode.SHARED, False),
        (ClaimMode.EXCLUSIVE, ClaimMode.INTENT, False),
        (ClaimMode.SHARED, ClaimMode.EXCLUSIVE, False),
        (ClaimMode.SHARED, ClaimMode.SHARED, True),
        (ClaimMode.SHARED, ClaimMode.INTENT, False),
        (ClaimMode.INTENT, ClaimMode.EXCLUSIVE, False),
        (ClaimMode.INTENT, ClaimMode.SHARED, False),
        (ClaimMode.INTENT, ClaimMode.INTENT, True),
    ],
)
def test_mode_compatibility_matrix(held, requested, expected):
    assert (
        ChangeControlEmbargoManager._modes_compatible(held, requested) is expected
    )


# ----------------------------------------------------------------------
# 2. Acquisition semantics
# ----------------------------------------------------------------------

def test_disjoint_owners_acquire_in_parallel(embargo_manager):
    first = embargo_manager.try_acquire(
        owner_request_id="tx-1",
        claims=[("scope:conduit:A", ClaimMode.EXCLUSIVE)],
        reason_tag="bind",
    )
    second = embargo_manager.try_acquire(
        owner_request_id="tx-2",
        claims=[("scope:conduit:B", ClaimMode.EXCLUSIVE)],
        reason_tag="bind",
    )
    assert first.acquired and second.acquired


def test_shared_claims_coexist_on_same_scope(embargo_manager):
    first = embargo_manager.try_acquire(
        owner_request_id="tx-1",
        claims=[("scope:spellbook:S", ClaimMode.SHARED)],
        reason_tag="bind",
    )
    second = embargo_manager.try_acquire(
        owner_request_id="tx-2",
        claims=[("scope:spellbook:S", ClaimMode.SHARED)],
        reason_tag="bind",
    )
    assert first.acquired and second.acquired


def test_intent_claims_coexist_but_block_shared_and_exclusive(embargo_manager):
    assert embargo_manager.try_acquire(
        owner_request_id="tx-1",
        claims=[("scope:frame:default", ClaimMode.INTENT)],
        reason_tag="bind",
    ).acquired
    assert embargo_manager.try_acquire(
        owner_request_id="tx-2",
        claims=[("scope:frame:default", ClaimMode.INTENT)],
        reason_tag="bind",
    ).acquired
    blocked_shared = embargo_manager.try_acquire(
        owner_request_id="tx-3",
        claims=[("scope:frame:default", ClaimMode.SHARED)],
        reason_tag="bind",
    )
    blocked_exclusive = embargo_manager.try_acquire(
        owner_request_id="tx-4",
        claims=[("scope:frame:default", ClaimMode.EXCLUSIVE)],
        reason_tag="teardown",
    )
    assert not blocked_shared.acquired
    assert not blocked_exclusive.acquired


def test_exclusive_collision_reports_holder_evidence(embargo_manager):
    embargo_manager.try_acquire(
        owner_request_id="tx-1",
        claims=[("scope:conduit:A", ClaimMode.EXCLUSIVE)],
        reason_tag="transfer_ownership",
    )
    decision = embargo_manager.try_acquire(
        owner_request_id="tx-2",
        claims=[("scope:conduit:A", ClaimMode.EXCLUSIVE)],
        reason_tag="bind",
    )
    assert decision == AcquisitionDecision(
        acquired=False,
        blocking=(("scope:conduit:A", "tx-1", "x"),),
    )


def test_failed_multi_claim_acquires_nothing(embargo_manager):
    embargo_manager.try_acquire(
        owner_request_id="tx-1",
        claims=[("scope:conduit:B", ClaimMode.EXCLUSIVE)],
        reason_tag="bind",
    )
    decision = embargo_manager.try_acquire(
        owner_request_id="tx-2",
        claims=[
            ("scope:conduit:A", ClaimMode.EXCLUSIVE),
            ("scope:conduit:B", ClaimMode.EXCLUSIVE),
        ],
        reason_tag="link",
    )
    assert not decision.acquired
    # scope:conduit:A must not have been claimed by the failed attempt.
    follow_up = embargo_manager.try_acquire(
        owner_request_id="tx-3",
        claims=[("scope:conduit:A", ClaimMode.EXCLUSIVE)],
        reason_tag="bind",
    )
    assert follow_up.acquired


def test_same_owner_reentrance_and_sole_holder_upgrade(embargo_manager):
    assert embargo_manager.try_acquire(
        owner_request_id="tx-1",
        claims=[("scope:spellbook:S", ClaimMode.SHARED)],
        reason_tag="bind",
    ).acquired
    # Re-request of a held key never blocks the owner.
    assert embargo_manager.try_acquire(
        owner_request_id="tx-1",
        claims=[("scope:spellbook:S", ClaimMode.SHARED)],
        reason_tag="bind",
    ).acquired
    # Sole holder may upgrade SHARED -> EXCLUSIVE.
    assert embargo_manager.try_acquire(
        owner_request_id="tx-1",
        claims=[("scope:spellbook:S", ClaimMode.EXCLUSIVE)],
        reason_tag="bind",
    ).acquired
    # The upgraded claim now blocks other shared requesters.
    assert not embargo_manager.try_acquire(
        owner_request_id="tx-2",
        claims=[("scope:spellbook:S", ClaimMode.SHARED)],
        reason_tag="bind",
    ).acquired


def test_upgrade_blocked_while_second_shared_holder_exists(embargo_manager):
    embargo_manager.try_acquire(
        owner_request_id="tx-1",
        claims=[("scope:spellbook:S", ClaimMode.SHARED)],
        reason_tag="bind",
    )
    embargo_manager.try_acquire(
        owner_request_id="tx-2",
        claims=[("scope:spellbook:S", ClaimMode.SHARED)],
        reason_tag="bind",
    )
    decision = embargo_manager.try_acquire(
        owner_request_id="tx-1",
        claims=[("scope:spellbook:S", ClaimMode.EXCLUSIVE)],
        reason_tag="bind",
    )
    assert not decision.acquired
    assert decision.blocking == (("scope:spellbook:S", "tx-2", "s"),)


def test_release_owner_is_idempotent_and_frees_scopes(embargo_manager):
    embargo_manager.try_acquire(
        owner_request_id="tx-1",
        claims=[("scope:conduit:A", ClaimMode.EXCLUSIVE)],
        reason_tag="bind",
    )
    embargo_manager.release_owner("tx-1")
    embargo_manager.release_owner("tx-1")
    embargo_manager.release_owner("tx-unknown")
    assert embargo_manager.try_acquire(
        owner_request_id="tx-2",
        claims=[("scope:conduit:A", ClaimMode.EXCLUSIVE)],
        reason_tag="bind",
    ).acquired


def test_release_wakes_blocked_acquirer(embargo_manager):
    embargo_manager.try_acquire(
        owner_request_id="tx-1",
        claims=[("scope:conduit:A", ClaimMode.EXCLUSIVE)],
        reason_tag="bind",
    )
    admitted = threading.Event()

    def blocked_acquirer():
        deadline = time.monotonic() + 5.0
        while time.monotonic() < deadline:
            decision = embargo_manager.try_acquire(
                owner_request_id="tx-2",
                claims=[("scope:conduit:A", ClaimMode.EXCLUSIVE)],
                reason_tag="bind",
            )
            if decision.acquired:
                admitted.set()
                return
            embargo_manager.wait_for_release(timeout=deadline - time.monotonic())

    worker = threading.Thread(target=blocked_acquirer)
    worker.start()
    time.sleep(0.05)
    assert not admitted.is_set()
    embargo_manager.release_owner("tx-1")
    worker.join(timeout=5.0)
    assert admitted.is_set()


# ----------------------------------------------------------------------
# 3. Orchestrator admission via acquisition
# ----------------------------------------------------------------------

def test_admission_acquires_and_overlap_rejects_with_evidence(
        orchestrator,
        transaction_manager,
        conflict_manager,
        embargo_manager,
):
    first = transaction_manager.build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-A",
        spellbook_id="sb-1",
        conduit_ids=("conduit-A",),
    )
    result = orchestrator.admit_request(
        first,
        transaction_manager=transaction_manager,
        conflict_manager=conflict_manager,
        embargo_manager=embargo_manager,
    )
    assert result.admitted
    assert transaction_manager.get_in_flight(first.request_id) is first
    assert orchestrator.get_staged(first.request_id) is not None

    second = transaction_manager.build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-A",
        spellbook_id="sb-1",
        conduit_ids=("conduit-A",),
    )
    rejection = orchestrator.admit_request(
        second,
        transaction_manager=transaction_manager,
        conflict_manager=conflict_manager,
        embargo_manager=embargo_manager,
    )
    assert not rejection.admitted
    assert rejection.reasons == ("scope_conflict",)
    assert first.request_id in rejection.conflicts
    assert "scope:spellbook:sb-1" in rejection.embargoes
    assert transaction_manager.get_in_flight(second.request_id) is None

    orchestrator.commit_request(
        first.request_id,
        transaction_manager=transaction_manager,
        embargo_manager=embargo_manager,
    )
    retried = orchestrator.admit_request(
        second,
        transaction_manager=transaction_manager,
        conflict_manager=conflict_manager,
        embargo_manager=embargo_manager,
    )
    assert retried.admitted


def test_disjoint_requests_admit_in_parallel(
        orchestrator,
        transaction_manager,
        conflict_manager,
        embargo_manager,
):
    for index in range(5):
        request = transaction_manager.build_request(
            request_type=ChangeTransactionType.BIND,
            initiator_conduit_id=f"conduit-{index}",
            spellbook_id=f"sb-{index}",
            conduit_ids=(f"conduit-{index}",),
        )
        assert orchestrator.admit_request(
            request,
            transaction_manager=transaction_manager,
            conflict_manager=conflict_manager,
            embargo_manager=embargo_manager,
        ).admitted


def test_build_request_validates_scope_claim_modes(transaction_manager):
    request = transaction_manager.build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-A",
        scope_keys=("scope:spellbook:sb-1",),
        scope_claims=(("scope:spellbook:sb-1", "s"),),
    )
    assert request.scope_claims == (("scope:spellbook:sb-1", "s"),)
    with pytest.raises(ValueError):
        transaction_manager.build_request(
            request_type=ChangeTransactionType.BIND,
            initiator_conduit_id="conduit-A",
            scope_claims=(("scope:spellbook:sb-1", "broken-mode"),),
        )


def test_explicit_shared_claims_admit_concurrent_requests(
        orchestrator,
        transaction_manager,
        conflict_manager,
        embargo_manager,
):
    def build_shared():
        return transaction_manager.build_request(
            request_type=ChangeTransactionType.BIND,
            initiator_conduit_id="conduit-A",
            scope_keys=("scope:spellbook:sb-1",),
            scope_claims=(("scope:spellbook:sb-1", "s"),),
        )

    first = build_shared()
    second = build_shared()
    assert orchestrator.admit_request(
        first,
        transaction_manager=transaction_manager,
        conflict_manager=conflict_manager,
        embargo_manager=embargo_manager,
    ).admitted
    assert orchestrator.admit_request(
        second,
        transaction_manager=transaction_manager,
        conflict_manager=conflict_manager,
        embargo_manager=embargo_manager,
    ).admitted


# ----------------------------------------------------------------------
# 4. Mediator scope-local pending
# ----------------------------------------------------------------------

def test_mediator_blocked_start_admits_after_holder_ends(
        transaction_manager,
        conflict_manager,
        embargo_manager,
        orchestrator,
):
    mediator = _make_mediator(
        transaction_manager,
        conflict_manager,
        embargo_manager,
        orchestrator,
    )
    holder_started = threading.Event()
    release_holder = threading.Event()
    waiter_admitted = threading.Event()
    shared_scope = ("scope:conduit:shared",)

    def holder():
        identity = _make_identity(owner_id="conduit-H")
        session = mediator.begin_transaction(
            identity=identity,
            transaction_type=ChangeTransactionType.BIND,
            scope_keys=shared_scope,
        )
        holder_started.set()
        release_holder.wait(timeout=5.0)
        mediator.end_transaction_by_request_id(session.request.request_id)

    def waiter():
        holder_started.wait(timeout=5.0)
        identity = _make_identity(owner_id="conduit-W")
        session = mediator.begin_transaction(
            identity=identity,
            transaction_type=ChangeTransactionType.BIND,
            scope_keys=shared_scope,
        )
        waiter_admitted.set()
        mediator.end_transaction_by_request_id(session.request.request_id)

    holder_thread = threading.Thread(target=holder)
    waiter_thread = threading.Thread(target=waiter)
    holder_thread.start()
    waiter_thread.start()
    time.sleep(0.1)
    assert not waiter_admitted.is_set()
    release_holder.set()
    waiter_thread.join(timeout=5.0)
    holder_thread.join(timeout=5.0)
    assert waiter_admitted.is_set()
    mediator.cleanup()


def test_mediator_scope_wait_times_out_with_blocking_evidence(
        transaction_manager,
        conflict_manager,
        embargo_manager,
        orchestrator,
):
    mediator = _make_mediator(
        transaction_manager,
        conflict_manager,
        embargo_manager,
        orchestrator,
        max_wait=0.2,
    )
    shared_scope = ("scope:conduit:shared",)
    holder_identity = _make_identity(owner_id="conduit-H")
    holder_session = mediator.begin_transaction(
        identity=holder_identity,
        transaction_type=ChangeTransactionType.BIND,
        scope_keys=shared_scope,
    )

    failure: list = []

    def waiter():
        identity = _make_identity(owner_id="conduit-W")
        try:
            mediator.begin_transaction(
                identity=identity,
                transaction_type=ChangeTransactionType.BIND,
                scope_keys=shared_scope,
            )
        except RuntimeError as exc:
            failure.append(str(exc))

    waiter_thread = threading.Thread(target=waiter)
    waiter_thread.start()
    waiter_thread.join(timeout=5.0)
    assert failure, "waiter should time out while the holder keeps its claims"
    assert "Timed out waiting for blocked scopes" in failure[0]
    assert holder_session.request.request_id in failure[0]
    mediator.end_transaction_by_request_id(holder_session.request.request_id)
    mediator.cleanup()


# ----------------------------------------------------------------------
# 5. Strategy commit deltas and fact records
# ----------------------------------------------------------------------

def test_commit_applies_strategy_delta_fact_stamps(
        transaction_manager,
        conflict_manager,
        embargo_manager,
        orchestrator,
        registry,
):
    mediator = _make_mediator(
        transaction_manager,
        conflict_manager,
        embargo_manager,
        orchestrator,
        registry=registry,
    )
    identity = _make_identity(owner_id="conduit-A")
    session = mediator.begin_transaction(
        identity=identity,
        transaction_type=ChangeTransactionType.BIND,
        spellbook_id="sb-1",
        conduit_ids=("conduit-A",),
    )
    request_id = session.request.request_id
    mediator.end_transaction_by_request_id(request_id)

    spellbook_fact = registry.get_fact_record(
        fact_family="bind",
        region="spellbook:sb-1",
    )
    conduit_fact = registry.get_fact_record(
        fact_family="bind",
        region="conduit:conduit-A",
    )
    assert spellbook_fact is not None
    assert conduit_fact is not None
    assert spellbook_fact.last_reporter == request_id
    assert spellbook_fact.generation == 1
    mediator.cleanup()


def test_aborted_transaction_applies_no_delta(
        transaction_manager,
        conflict_manager,
        embargo_manager,
        orchestrator,
        registry,
):
    mediator = _make_mediator(
        transaction_manager,
        conflict_manager,
        embargo_manager,
        orchestrator,
        registry=registry,
    )
    identity = _make_identity(owner_id="conduit-A")
    session = mediator.begin_transaction(
        identity=identity,
        transaction_type=ChangeTransactionType.BIND,
        spellbook_id="sb-1",
        conduit_ids=("conduit-A",),
    )
    session.mark_abort_only("test abort")
    mediator.end_transaction_by_request_id(
        session.request.request_id,
        success=False,
    )
    assert registry.get_fact_record(
        fact_family="bind",
        region="spellbook:sb-1",
    ) is None
    mediator.cleanup()


def test_fact_record_report_get_list_and_generation(registry):
    first = registry.report_fact(
        fact_family="bind",
        region="conduit:C1",
        reporter="tx-1",
    )
    second = registry.report_fact(
        fact_family="bind",
        region="conduit:C1",
        reporter="tx-2",
    )
    assert first.generation == 1
    assert second.generation == 2
    assert second.last_reporter == "tx-2"

    current = registry.get_fact_record(fact_family="bind", region="conduit:C1")
    assert current == second

    registry.report_fact(fact_family="link", region="conduit:C2", reporter="tx-3")
    all_records = registry.list_fact_records()
    assert len(all_records) == 2
    only_c1 = registry.list_fact_records(region="conduit:C1")
    assert len(only_c1) == 1
    assert only_c1[0].region == "conduit:C1"

    with pytest.raises(ValueError):
        registry.report_fact(fact_family="", region="conduit:C1", reporter="tx-4")
