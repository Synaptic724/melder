"""
The reporting surface for the mediator plane.

Dependency rule: standard library plus `melder.utilities` only.

Mirrors the reporting half of `DevopsInformationRegistry`, which is two
mechanisms rather than one:
  1. FACT BASELINES - what changed, when, and who reported it, so a reader can
     check a baseline instead of re-deriving state that has not moved.
  2. LIVE ACTIVITY INDEXES - what is in flight right now, along one axis.

Deliberately NOT ported: the DevOps relational mirrors (spellbook<->conduit
ownership, conduit links, cluster membership). Relational truth belongs to each
subsystem; duplicating it here would create a second place to be wrong.
"""

import threading
import time
from typing import Dict, List, Optional, Tuple

from melder.aether.aetheric_mediator.staged_transaction import StagedTransaction
from melder.utilities.general_base.cleanable import Cleanable


class FactRecord:
    """
    One "this region was last changed by this reporter at this time" baseline.

    Contract:
        Immutable. Replaced wholesale on each report rather than mutated, so a
        reader holding one never observes it change underneath.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Immutable freshness baseline for one region.
    """

    __slots__ = ["fact_family", "region", "reporter", "reported_at"]

    def __init__(
            self,
            *,
            fact_family: str,
            region: str,
            reporter: str,
            reported_at: float,
    ) -> None:
        """
        Build one immutable fact baseline.

        Args:
            fact_family: The transaction type that produced the change.
            region: The scope key the change applies to.
            reporter: The request id that reported it.
            reported_at: Unix timestamp of the report.

        Returns:
            None.
        """
        self.fact_family: str = fact_family
        self.region: str = region
        self.reporter: str = reporter
        self.reported_at: float = reported_at

    def age_seconds(self, now: Optional[float] = None) -> float:
        """
        Return how long ago this baseline was stamped.

        Args:
            now: Optional current time; defaults to the wall clock.

        Returns:
            float: Age in seconds, never negative.
        """
        current = time.time() if now is None else now
        return max(0.0, current - self.reported_at)

    def describe(self) -> Dict[str, object]:
        """
        Return a detached value-only view of this baseline.

        Returns:
            Dict[str, object]: Family, region, reporter, timestamp, age.
        """
        return {
            "fact_family": self.fact_family,
            "region": self.region,
            "reporter": self.reporter,
            "reported_at": self.reported_at,
            "age_seconds": self.age_seconds(),
        }


class InformationRegistry(Cleanable):
    """
    Fact baselines and live activity indexes for the plane.

    Purpose:
        Answer two questions cheaply and without touching live subsystem
        state: "what is happening right now" and "has this region changed
        since I last looked".

    Contract:
        - CALLER-PAID BY DESIGN. Nothing in the runtime invokes reporting
          automatically. A reader asks; the plane answers. This matches the
          DevOps information layer and keeps the admission hot path free of
          reporting cost.
        - RESULTS ARE DETACHED. Every read returns values and strings, never
          live `StagedTransaction`, `Identity`, or session references. That is
          what makes a result safe to log, ship, or retain after the
          transaction it describes has ended.
        - ONE BASELINE PER REGION. `report_fact` REPLACES rather than appends.
          The registry answers "when did this last change", not "everything
          that ever happened" - an unbounded history here would be a memory
          leak on the commit path.
        - ACTIVITY IS INDEXED THREE WAYS - by scope, by submitter, and by
          transaction type - because those are the three axes someone
          diagnosing a stall actually asks along.

    Owned State:
        `_facts` (region -> FactRecord), `_active` (request id -> staged), and
        one lock. No subsystem references.

    Threading:
        One `RLock`. Reads copy under the lock and return detached values, so
        a caller never holds a reference into live registry state.

    Registration:
        MELDER KERNEL - guarded. Constructed by the plane; never bound.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Plane reporting - fact baselines plus live activity
        indexes by scope, submitter, and type. Caller-paid, detached results.
    """

    __slots__ = Cleanable.__slots__ + ["_lock", "_facts", "_active"]

    def __init__(self) -> None:
        """
        Build one empty registry.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        self._facts: Dict[str, FactRecord] = {}
        self._active: Dict[str, StagedTransaction] = {}

    def cleanup(self) -> None:
        """
        Idempotently drop all baselines and activity.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            # Re-check under the lock; the outer check is a fast path only.
            if self._cleaned:
                return
            self._cleaned = True
            self._facts.clear()
            self._active.clear()
        del self._facts
        del self._active
        del self._lock

    def report_fact(
            self,
            *,
            fact_family: str,
            region: str,
            reporter: str,
    ) -> None:
        """
        Stamp the freshness baseline for one region.

        Contract:
            REPLACES any existing baseline for the region. Called from
            `apply_commit_delta` while claims are still held, which is what
            makes the stamp race-free against overlapping writers.

        Args:
            fact_family: The transaction type producing the change.
            region: The scope key that changed.
            reporter: The request id reporting it.

        Returns:
            None.

        Raises:
            RuntimeError: If the registry has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            self._facts[region] = FactRecord(
                fact_family=fact_family,
                region=region,
                reporter=reporter,
                reported_at=time.time(),
            )

    def get_fact(self, region: str) -> Optional[Dict[str, object]]:
        """
        Return the detached baseline for one region, if any.

        Args:
            region: The scope key to look up.

        Returns:
            Optional[Dict[str, object]]: Detached baseline, or None when the
                region has no baseline (never reported, or cold).

        Raises:
            RuntimeError: If the registry has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            record = self._facts.get(region)
            return None if record is None else record.describe()

    def stale_regions(
            self,
            *,
            regions: Tuple[str, ...],
            max_age_seconds: float,
    ) -> Tuple[str, ...]:
        """
        Return which of `regions` are stale or have no baseline at all.

        Contract:
            This is the control-plane economy in one call: check the baseline
            first, re-derive only what is cold or stale. A region with NO
            baseline counts as stale - never-reported and long-ago-reported
            are equally untrustworthy to a reader, and treating an absent
            baseline as fresh would be the dangerous direction.

        Args:
            regions: The scope keys to test.
            max_age_seconds: Age beyond which a baseline is stale.

        Returns:
            Tuple[str, ...]: The stale or unknown regions, sorted.

        Raises:
            RuntimeError: If the registry has been cleaned.
        """
        self.check_cleaned()
        now = time.time()
        stale: List[str] = []
        with self._lock:
            for region in regions:
                record = self._facts.get(region)
                if record is None or record.age_seconds(now) > max_age_seconds:
                    stale.append(region)
        return tuple(sorted(stale))

    def register_activity(self, staged: StagedTransaction) -> None:
        """
        Record one transaction as live.

        Args:
            staged: The admitted transaction.

        Returns:
            None.

        Raises:
            RuntimeError: If the registry has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            self._active[staged.request_id] = staged

    def unregister_activity(self, request_id: str) -> None:
        """
        Drop one transaction from the live set.

        Contract:
            Idempotent, so a `finally` may call it without checking.

        Args:
            request_id: The transaction to drop.

        Returns:
            None.

        Raises:
            RuntimeError: If the registry has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            self._active.pop(request_id, None)

    def activity_by_scope(self, scope_key: str) -> Tuple[str, ...]:
        """
        Return live request ids touching one scope key.

        Args:
            scope_key: The scope to query.

        Returns:
            Tuple[str, ...]: Live request ids, sorted.

        Raises:
            RuntimeError: If the registry has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return tuple(sorted(
                staged.request_id
                for staged in self._active.values()
                if scope_key in staged.granted_scopes
            ))

    def activity_by_submitter(
            self,
            *,
            submitter_kind: str,
            submitter_id: str,
    ) -> Tuple[str, ...]:
        """
        Return live request ids submitted by one identity.

        Args:
            submitter_kind: The submitter's family.
            submitter_id: The submitter's id within that family.

        Returns:
            Tuple[str, ...]: Live request ids, sorted.

        Raises:
            RuntimeError: If the registry has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return tuple(sorted(
                staged.request_id
                for staged in self._active.values()
                if staged.submitter_kind == submitter_kind
                and staged.submitter_id == submitter_id
            ))

    def activity_by_type(self, transaction_type: str) -> Tuple[str, ...]:
        """
        Return live request ids of one transaction type.

        Args:
            transaction_type: The type value to query.

        Returns:
            Tuple[str, ...]: Live request ids, sorted.

        Raises:
            RuntimeError: If the registry has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return tuple(sorted(
                staged.request_id
                for staged in self._active.values()
                if staged.transaction_type.value == transaction_type
            ))

    def describe(self) -> Dict[str, object]:
        """
        Return a detached snapshot of live activity and baselines.

        Returns:
            Dict[str, object]: Counts plus rendered activity and baselines.

        Raises:
            RuntimeError: If the registry has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return {
                "active_count": len(self._active),
                "fact_count": len(self._facts),
                "active": [
                    staged.describe()
                    for staged in sorted(
                        self._active.values(),
                        key=lambda item: item.admitted_at,
                    )
                ],
                "facts": [
                    self._facts[region].describe()
                    for region in sorted(self._facts.keys())
                ],
            }
