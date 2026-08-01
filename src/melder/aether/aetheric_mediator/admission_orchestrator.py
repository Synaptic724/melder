"""
The serialized admission decision point for the mediator plane.

Dependency rule: standard library plus `melder.utilities` only. Never
`melder.aether`.

Mirrors `ChangeControlOrchestrator.admit_request`, whose shape is deliberate:
the decision is ONE atomic scope-claim acquisition taken under one admission
lock, and a refusal returns explicit blocking evidence while leaving the
in-flight registry and the claim table completely untouched.
"""

import threading
from typing import Dict, Optional, Tuple

from melder.aether.aetheric_mediator.admission_result import (
    AdmissionReason,
    AdmissionResult,
)
from melder.aether.aetheric_mediator.claim_table import ClaimTable
from melder.aether.aetheric_mediator.identity import Identity
from melder.aether.aetheric_mediator.transaction_request import TransactionRequest
from melder.utilities.general_base.cleanable import Cleanable


class AdmissionOrchestrator(Cleanable):
    """
    Serializes admission decisions and owns the in-flight request registry.

    Purpose:
        Be the ONE place a request becomes admitted, so "is this allowed to
        proceed" has a single answer arrived at a single way.

    Contract:
        - THE DECISION IS ONE ACQUISITION. Admission takes the admission lock
          for the ENTIRE decision path and performs exactly one atomic
          all-or-nothing `ClaimTable.try_acquire`. There is no second
          adjudication layer and no in-flight overlap scan; the claim table's
          moded matrix IS the decision.
        - REFUSAL LEAVES NO TRACE. A refused request touches neither the
          in-flight registry nor the claim table. A caller may retry without
          first cleaning anything up.
        - SUCCESS MEANS CLAIMS ARE ALREADY HELD. When `admit` returns an
          admitted verdict the scopes are acquired; the caller does NOT
          acquire them afterwards. Releasing is the caller's obligation via
          `release(...)`, normally from a `finally`.
        - ADMISSION COST IS O(requested scopes). One lock, dict operations
          proportional to the claim set, no scan over live transactions. This
          is a performance invariant carried over from DevOps deliberately;
          it is cheap to keep now and expensive to recover later.
        - READERS NEVER ENTER THIS PLANE. Nothing on a read path may call
          `admit`. The plane exists for structural mutation only.
        - IDENTITY INTEGRITY IS CHECKED. The holder passed to `admit` must
          match the request's recorded submitter, so evidence cannot name one
          claimant while the claim is taken by another.

    Owned State:
        The admission lock and `_in_flight` (request id -> frozen request).
        The claim table is BORROWED, never owned: it outlives individual
        admissions and is cleaned by whoever constructed it.

    Lifecycle / Cleanup:
        Idempotent. Cleanup drops the in-flight registry but does NOT release
        claims - the table is not ours to tear down, and silently releasing
        another component's claims during teardown would be a worse failure
        than leaving them for the table's own cleanup to wake waiters on.

    Threading:
        One `RLock` guards admission and the in-flight registry. The lock is
        held across the whole decision so two admissions cannot interleave
        between "check" and "acquire".

        LOCK ORDER FOR THE WHOLE PLANE - `orchestrator._lock` then
        `claim_table._condition`. This is the ONLY cross-object lock nesting
        that exists here: `admit` holds the admission lock while calling
        `ClaimTable.try_acquire`, which takes the table's condition. Nothing
        acquires them in the other order, because `ClaimTable` is a LEAF - it
        never calls the orchestrator, the mediator, the registry, or a session.

        ADMIT MUST NEVER WAIT. This is the law the whole design rests on and
        it is easy to break by accident. `try_acquire` is non-blocking on
        purpose: it returns blocking evidence rather than parking. Bounded
        waiting lives in `Mediator._admit_with_wait`, which parks on
        `ClaimTable.wait_for_change(...)` only AFTER `admit` has returned and
        this lock is released.

        If waiting were ever moved inside `admit`, a parked thread would hold
        the exact lock that `release(...)` must take to free the claims it is
        waiting for. The plane would deadlock on the first real contention -
        which is the only workload it exists to serve. Do not call any
        blocking table method from inside this lock; `ClaimTable.acquire` in
        particular is blocking and must never be reached from here.

        `release(...)` is deliberately asymmetric: it takes this lock, mutates
        `_in_flight`, RELEASES, and only then touches the table. So the
        release path never nests at all.

    Registration:
        MELDER KERNEL - guarded. Constructed by the plane root; never bound.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Serialized admission decision point. One atomic
        claim acquisition per request; refusals carry blocking evidence.
    """

    __slots__ = Cleanable.__slots__ + ["_lock", "_in_flight"]

    def __init__(self) -> None:
        """
        Build one empty orchestrator.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        self._in_flight: Dict[str, TransactionRequest] = {}

    def cleanup(self) -> None:
        """
        Idempotently drop the in-flight registry.

        Contract:
            Does NOT release claims held in the borrowed table. See the class
            lifecycle note: releasing another component's claims during our
            teardown is the more dangerous behaviour.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            # Re-check under the lock; the outer check is a fast path only.
            # Two threads passing it concurrently would both reach the
            # deletions below and the loser would raise AttributeError.
            if self._cleaned:
                return
            self._cleaned = True
            self._in_flight.clear()
        del self._in_flight
        del self._lock

    def admit(
            self,
            *,
            request: TransactionRequest,
            holder: Identity,
            claim_table: ClaimTable,
    ) -> AdmissionResult:
        """
        Decide admission for one request, acquiring its claims on success.

        Contract:
            One acquisition under one lock. On success the claims ARE HELD on
            return and the request is registered in flight. On refusal nothing
            is mutated anywhere.

        Args:
            request:
                The frozen pre-admission request.
            holder:
                The claiming identity. Must match the request's recorded
                submitter strings.
            claim_table:
                The borrowed claim table to acquire against.

        Returns:
            AdmissionResult:
                Admitted, or refused carrying reasons, contended scope keys,
                and rendered blocking evidence.

        Raises:
            RuntimeError: If the orchestrator has been cleaned.
            ValueError: If `holder` does not match the request's submitter.
        """
        self.check_cleaned()
        if (
            holder.kind != request.submitter_kind
            or holder.identity_id != request.submitter_id
        ):
            raise ValueError(
                "holder {0} does not match the request's recorded submitter "
                "{1}:{2}; evidence must never name a claimant other than the "
                "one taking the claim.".format(
                    holder.describe(),
                    request.submitter_kind,
                    request.submitter_id,
                )
            )
        with self._lock:
            if request.request_id in self._in_flight:
                return AdmissionResult.refused(
                    reasons=(AdmissionReason.INVALID_REQUEST,),
                    evidence=(
                        "request_id {0!r} is already in flight".format(
                            request.request_id
                        ),
                    ),
                )
            blocks = claim_table.try_acquire(holder, request.claim_map())
            if blocks:
                blocked_scopes = tuple(
                    sorted({block.scope_key for block in blocks})
                )
                return AdmissionResult.refused(
                    reasons=(AdmissionReason.SCOPE_CONTENDED,),
                    blocked_scopes=blocked_scopes,
                    evidence=tuple(block.describe() for block in blocks),
                )
            self._in_flight[request.request_id] = request
            return AdmissionResult.granted()

    def release(
            self,
            *,
            request_id: str,
            holder: Identity,
            claim_table: ClaimTable,
    ) -> bool:
        """
        Release one admitted request's claims and drop it from in flight.

        Contract:
            Idempotent: releasing an unknown request id is a no-op returning
            False, so a `finally` block may call this unconditionally without
            first checking whether admission succeeded.

        Args:
            request_id:
                The request to release.
            holder:
                The identity whose claims are released.
            claim_table:
                The borrowed claim table.

        Returns:
            bool: True when a live in-flight request was released.

        Raises:
            RuntimeError: If the orchestrator has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            if request_id not in self._in_flight:
                return False
            del self._in_flight[request_id]
        claim_table.release_holder(holder)
        return True

    def get_in_flight(self, request_id: str) -> Optional[TransactionRequest]:
        """
        Return one in-flight request, or None when it is not in flight.

        Args:
            request_id: The request id to look up.

        Returns:
            Optional[TransactionRequest]: The frozen request, or None.

        Raises:
            RuntimeError: If the orchestrator has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return self._in_flight.get(request_id)

    def list_in_flight(self) -> Tuple[TransactionRequest, ...]:
        """
        Return every in-flight request, ordered by creation time.

        Contract:
            Ordering is by `created_at` so the oldest live transaction reads
            first - which is what someone diagnosing a stall wants to see.

        Returns:
            Tuple[TransactionRequest, ...]: The live requests.

        Raises:
            RuntimeError: If the orchestrator has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return tuple(
                sorted(
                    self._in_flight.values(),
                    key=lambda request: request.created_at,
                )
            )

    def describe(self) -> Dict[str, object]:
        """
        Return a detached snapshot of live admission state.

        Contract:
            Detached: strings and ints only, no live request or identity
            references, so it is safe to log or ship.

        Returns:
            Dict[str, object]:
                `in_flight_count` plus one rendered line per live request.

        Raises:
            RuntimeError: If the orchestrator has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return {
                "in_flight_count": len(self._in_flight),
                "in_flight": [
                    request.describe()
                    for request in sorted(
                        self._in_flight.values(),
                        key=lambda item: item.created_at,
                    )
                ],
            }
