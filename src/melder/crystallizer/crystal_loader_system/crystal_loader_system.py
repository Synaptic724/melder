"""
The unfold owner: durable load state over the mediated boot pipeline.

CrystalLoaderSystem is the child Crystallizer talks to for every load. It
borrows the record, owns the LoadAdmission plane (renamed from BootMediator
2026-07-11), drives plan -> gated engine -> adjudication, and REMEMBERS: for
the first time, "what did we last load" has an owner (detached last-load
payload + admission view).

Lane: EPIC-2026-07-09-crystallizer-subsystem-decomposition, story S4.
"""

import threading
from typing import Dict, Optional, TYPE_CHECKING

from melder.utilities.general_base.cleanable import Cleanable
from melder.crystallizer.crystal_loader_system.load_admission import (
    LoadAdmission,
)
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

if TYPE_CHECKING:
    from melder.aether.aether import Aether
    from melder.crystallizer.persistence.persistence_system import (
        PersistenceSystem,
    )
    from melder.utilities.synchronization.phase_scheduler import (
        PhaseScheduler,
    )


class CrystalLoaderSystem(Cleanable):
    """
    Own the crystallizer's load lanes and their durable state.

    Purpose:
        One concrete owner for the unfold (V3 identity): checkpoint
        world loads and scoped formation loads run through the owned
        LoadAdmission plane's pipeline, and the loader retains the
        last load's detached payload for diagnostics and re-entry.

    Contract:
        - BORROWS the record (chain detachment through public verbs);
          never cleans it.
        - OWNS the LoadAdmission plane and the durable last-load state.
        - Every load is gated: the engine refuses "blockers" verdicts
          before any replay (standard admission).
        - Returned payloads are the engine report's describe() plus the
          additive "admission" scope view.

    Threading:
        One instance RLock serializes load verbs and last-load state.
        Lock order is one-way (loader lock -> record public verbs); the
        record never calls the loader.

    Lifecycle / Cleanup:
        Owned by exactly one Crystallizer and cleaned BEFORE the record
        (borrower-before-owner). cleanup(): mediator first, then owned
        state, borrowed deref, lock last; idempotent.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_persistence_system",
        "_load_admission",
        "_last_load",
        "_aether",
        "_restore_scheduler",
    ]

    def __init__(
            self,
            persistence_system: PersistenceSystem,
            aether: Optional["Aether"] = None,
    ) -> None:
        """
        Initialize the loader over one borrowed record.

        Args:
            persistence_system:
                The crystallizer's record. Borrowed collaborator: used
                and stored, never owned or cleaned here.
            aether:
                Optional borrowed Aether singleton. When supplied, every
                load verb claims system-wide load authority through
                `acquire_load_authority` for its span ("the loading
                thread has all control"): foreign root transactions park
                at the LoadGate until release. None runs loads ungated
                (unit-test posture over bare records).

        Returns:
            None.

        Raises:
            TypeError: If `persistence_system` is None.
        """
        super().__init__()
        if persistence_system is None:
            raise TypeError("persistence_system cannot be None.")
        self._lock: threading.RLock = threading.RLock()
        self._persistence_system: PersistenceSystem = persistence_system
        self._aether: Optional["Aether"] = aether
        self._load_admission: LoadAdmission = LoadAdmission(
            persistence_system, aether=aether
        )
        # Durable load state: the last load's detached payload (report +
        # admission view). None until the first load completes.
        self._last_load: Optional[Dict[str, object]] = None
        # OWNED restore execution pool (S4, parallel_restore_ulid_identity):
        # installed by the crystallizer at activate() from the frozen
        # configuration (parallel is the driver; None = sequential
        # fallback selected by configuration). Worker threads stay lazy
        # inside the scheduler until the first load runs.
        self._restore_scheduler: Optional[PhaseScheduler] = None

    def cleanup(self) -> None:
        """
        Clean the owned admission plane, release state and references.

        Contract:
            - Idempotent and terminal; cleans the owned admission plane before
              releasing last-load state and borrowed collaborators.
            - The persistence record and optional `Aether` host are
              dereferenced, never cleaned.
            - Does not tear down any world built by an earlier successful load.
              Runtime ownership transferred through normal public verbs.

        Threading:
            Serialized by the loader lock; no load-authority span or plan
            execution may still be active.

        Lifecycle / Cleanup:
            Called by the crystallizer before the asset system and persistence
            record, preserving borrower-before-record order.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            if not self._load_admission.cleaned:
                self._load_admission.cleanup()
            # Owned pool: sentinel-and-join the workers deterministically
            # (scheduler cleanup law) before dropping references.
            if (
                    self._restore_scheduler is not None
                    and not self._restore_scheduler.cleaned
            ):
                self._restore_scheduler.cleanup()
        del self._load_admission
        del self._restore_scheduler
        del self._last_load
        del self._persistence_system
        del self._aether
        del self._lock

    def configure_restore_scheduler(
            self,
            *,
            parallel_enabled: bool,
            worker_count: int,
            barrier_timeout_ms: int,
    ) -> None:
        """
        Install the restore execution policy from the frozen configuration.

        Purpose:
            The crystallizer's activate() seat for S4
            (parallel_restore_ulid_identity): parallel is the driver -
            when enabled, this loader owns one persistent PhaseScheduler
            (explicit construction lane) whose levels execute every load;
            disabled selects the sequential fallback driver.

        Contract:
            - Reconfiguration replaces the pool: an existing scheduler is
              cleaned (workers sentinelled + joined) before the new policy
              installs, so no orphan pool survives a policy change.
            - Worker threads remain lazy inside the scheduler until the
              first load needs them.

        Args:
            parallel_enabled:
                True installs the parallel pool; False selects the
                sequential driver (no pool owned).
            worker_count:
                Explicit pool size (positive int; scheduler-validated).
            barrier_timeout_ms:
                Explicit per-level barrier bound in milliseconds
                (positive int; scheduler-validated).

        Returns:
            None.

        Raises:
            RuntimeError: If the loader has been cleaned.
            ValueError: If an explicit value is invalid (scheduler law).

        Threading:
            Serialized by the loader lock; no load may be in flight.
        """
        self.check_cleaned()
        with self._lock:
            if (
                    self._restore_scheduler is not None
                    and not self._restore_scheduler.cleaned
            ):
                self._restore_scheduler.cleanup()
            self._restore_scheduler = None
            if parallel_enabled:
                from melder.utilities.synchronization.phase_scheduler import (
                    PhaseScheduler,
                )

                self._restore_scheduler = PhaseScheduler(
                    spellbook=None,
                    configuration=None,
                    worker_count=worker_count,
                    barrier_timeout_ms=barrier_timeout_ms,
                )

    def _enroll_restore_cohort(self) -> None:
        """
        Enroll the owned pool's workers into the CURRENT load span.

        Contract:
            - NO-OP without a pool or without an Aether host (bare-record
              posture has no gate to park anyone).
            - Withdrawal is not performed per-load: `release()` clears the
              whole cohort unconditionally (the S3 gate law "no membership
              survives a span"), so explicit withdrawal is reserved for
              mid-span worker retirement, which this loader never does.

        Returns:
            None.

        Raises:
            RuntimeError: If enrollment is attempted outside a held span
                (gate law; the caller acquires authority first).
        """
        if self._restore_scheduler is None or self._aether is None:
            return
        for ident in self._restore_scheduler.worker_thread_idents():
            self._aether.enroll_load_worker(ident)

    def load_checkpoint(self, checkpoint_id: str) -> Dict[str, object]:
        """
        Unfold one checkpoint's world through the admission pipeline.

        Purpose:
            The boot verb's owner-side seat: plan (detached chain) ->
            gated engine (blockers refuse pre-replay) -> adjudicated
            payload -> remembered as the last load.

        Args:
            checkpoint_id:
                ULID identity of the checkpoint to load.

        Returns:
            Dict[str, object]:
                The detached RestoreReport payload + the additive
                "admission" view.

        Raises:
            RuntimeError:
                If the loader has been cleaned, admission refused the
                load, or a replay stage failed (after teardown; cause
                chained).
            KeyError:
                If no checkpoint exists under `checkpoint_id`.
        """
        self.check_cleaned()
        with self._lock:
            # Load authority span: claim the Aether LoadGate (drain first)
            # so this thread holds the whole system for the replay; always
            # released, success or failure.
            if self._aether is not None:
                self._aether.acquire_load_authority(
                    f"checkpoint_load:{checkpoint_id}"
                )
            try:
                # S4: the span holder names its pool threads so restore
                # units pass the gate; release clears the cohort.
                self._enroll_restore_cohort()
                plan = self._load_admission.plan_checkpoint_load(
                    checkpoint_id
                )
                try:
                    payload = self._load_admission.execute_plan(
                        plan, scheduler=self._restore_scheduler
                    )
                finally:
                    if not plan.cleaned:
                        plan.cleanup()
                self._last_load = dict(payload)
                return payload
            finally:
                if self._aether is not None:
                    self._aether.release_load_authority()

    def restore_formation_record(
            self,
            formation_record: Dict[str, object],
            target_frame_name: Optional[str] = None,
            skip_existing: bool = False,
    ) -> Dict[str, object]:
        """
        Rebuild one loaded formation record through the admission pipeline.

        Purpose:
            The scoped-restore lane's owner-side seat: the asset system
            loads the record (facade-orchestrated), the admission plane
            mints the synthetic window and derives the scope, the gated
            engine replays it, and the adjudicated payload is remembered.
            S1 load-scope maturity: the load can RETARGET onto another
            frame and can SKIP host name collisions instead of refusing.

        Args:
            formation_record:
                A stored formation record (payloads + metadata).
            target_frame_name:
                Optional frame the formation should compose into instead
                of its recorded frame (rewrite happens in the detached
                window only).
            skip_existing:
                When True, host name-collision blockers downgrade to
                "skipped_existing" and the engine runs its skip lanes
                (unnamed conjure fallback, cluster reuse).

        Returns:
            Dict[str, object]:
                The detached RestoreReport payload + the additive
                "admission" view (scope-aware: expected frame-posture
                warnings reclassify).

        Raises:
            RuntimeError:
                If the loader has been cleaned, admission refused the
                load, or a replay stage failed (after teardown; cause
                chained).
            KeyError:
                If the record lacks its required keys.
        """
        self.check_cleaned()
        with self._lock:
            # Load authority span: claim the Aether LoadGate (drain first)
            # so this thread holds the whole system for the replay; always
            # released, success or failure.
            if self._aether is not None:
                self._aether.acquire_load_authority("formation_load")
            try:
                # S4: the span holder names its pool threads so restore
                # units pass the gate; release clears the cohort.
                self._enroll_restore_cohort()
                plan = self._load_admission.plan_formation_load(
                    formation_record,
                    target_frame_name=target_frame_name,
                    skip_existing=skip_existing,
                )
                try:
                    payload = self._load_admission.execute_plan(
                        plan, scheduler=self._restore_scheduler
                    )
                finally:
                    if not plan.cleaned:
                        plan.cleanup()
                self._last_load = dict(payload)
                return payload
            finally:
                if self._aether is not None:
                    self._aether.release_load_authority()

    def describe_last_load(self) -> Dict[str, object]:
        """
        Return the last load's detached payload (durable load state).

        Returns:
            Dict[str, object]:
                {"loaded": False} before any load; otherwise
                {"loaded": True, "payload": <last load payload copy>}.

        Raises:
            RuntimeError: If the loader has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            if self._last_load is None:
                return {"loaded": False}
            return {"loaded": True, "payload": dict(self._last_load)}
