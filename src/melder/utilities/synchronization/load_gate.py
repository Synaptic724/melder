import threading
import time
from typing import ClassVar, Dict, List, Optional, Set, Union


from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class LoadGate(Cleanable):
    """
    Exclusive system-wide gate granting one loading thread total authority.

    Purpose:
        Provide the single admission barrier consulted by every frame-local
        TransactionMediator at ROOT transaction starts. While a crystallizer
        load holds the gate, the loading thread passes freely (its per-verb
        replay transactions keep registry truth current) and every other
        thread waits until release or times out with a teach-grade error
        naming the load that holds the system.

    Control model:
        - "acquire(label)" claims exclusive authority for the calling thread.
          A second acquire - from any thread, including the holder - refuses:
          exactly one load may run at a time, and a nested acquire is a
          caller pairing bug, not a wait condition. Every span begins as a
          cohort of one (the holder) - byte-identical to the pre-cohort law.
        - Cohort (S3, parallel_restore_ulid_identity): the HOLDER may
          "enroll_worker(thread_ident)" its restore worker threads into the
          span; enrolled members pass the gate exactly like the holder while
          the span lasts. "withdraw_worker(thread_ident)" removes one member;
          "release()"/"cleanup()" clear the whole cohort unconditionally, so
          NO membership ever survives a span.
        - "release()" reopens the gate and wakes all waiters. Only the holder
          thread may release.
        - "wait_for_passage(timeout)" is the mediator-side check: it returns
          immediately when the gate is open, the caller IS the holder, OR the
          caller is an enrolled cohort member; otherwise it blocks on the
          internal condition until release, raising RuntimeError at the
          deadline. Foreign-thread park semantics are unchanged.

    Threading:
        - All state transitions are guarded by one "Lock" wrapped in a
          "Condition"; waiters park on the condition and are notified on
          release and on cleanup.
        - Hosted once per Aether, constructed BEFORE any AethericFrame can
          exist, so frames born mid-load inherit coverage unconditionally.

    Responsibilities:
        - Grant one loading thread exclusive system-wide authority for a span.
        - Let that holder enroll its worker threads into the span's cohort.
        - Park every other thread at root-transaction ingress until release.
        - Fail a parked thread loudly, naming the holding load, at its deadline.
        - Guarantee no cohort membership outlives its span.

    NO MEMBERSHIP SURVIVES A SPAN:
        The cohort is cleared at THREE points - `acquire()` (a fresh span always
        begins as a cohort of one), `release()`, and `cleanup()`. That is what
        keeps the single-thread law intact between loads: a stale ident from a
        previous span can never grant passage during the next one.

    AUTHORITY IS NOT DELEGATED:
        Only the holder may `enroll_worker` / `withdraw_worker` / `release`.
        Workers never self-enroll. If enrolment were open, any thread could
        write itself into the cohort and walk through the gate, which would
        defeat the entire barrier. Withdrawal takes effect at the withdrawn
        thread's NEXT passage check - a parked thread re-reads membership on
        every condition wake, so nothing is ever interrupted mid-flight.

    Owned State:
        - `_condition`: the one lock, wrapped as a Condition. All mutation and
          all parking happen under it.
        - `_holder_thread_id` / `_holder_label`: who holds the system and under
          what name. The label exists purely so a timeout can say WHICH load
          blocked the caller.
        - `_cohort_thread_ids`: idents the current holder enrolled.

    Threading:
        - All state transitions are guarded by one "Lock" wrapped in a
          "Condition"; waiters park on the condition and are notified on
          release and on cleanup.
        - Hosted once per Aether, constructed BEFORE any AethericFrame can
          exist, so frames born mid-load inherit coverage unconditionally.
        - Guarding is split by role. The four MUTATING verbs - `acquire`,
          `release`, `enroll_worker`, `withdraw_worker` - all call
          `check_cleaned()` and refuse on a torn-down gate. The three READ
          paths - `wait_for_passage`, `is_held`, `describe` - deliberately do
          not.
        - `wait_for_passage` skipping the guard is the load-bearing case: after
          cleanup the gate is terminally OPEN, so a late mediator call must PASS
          rather than raise. Teardown must never turn into a spurious admission
          failure. `is_held` and `describe` skip it for the milder reason that a
          probe should stay answerable during teardown.

    Lifecycle / Cleanup:
        - "cleanup()" terminally opens the gate and wakes all waiters. Holder
          slots become None TOMBSTONES (documented; not del) so late waiters
          exit cleanly; `wait_for_passage` after cleanup passes immediately.
        - The cohort set is cleared IN PLACE rather than released, for the same
          late-waiter safety reason: a waking thread must be able to re-read it.
        - This is the origin of the "LoadGate tombstone law" that sibling
          primitives cite. Note it is a CHOICE driven by who is expected to be
          parked at teardown: `CounterSwitch` faces the same question and
          answers it the other way (normal del posture), because its owner
          quiesces it before cleanup while this gate cannot assume that.

    Registration:
        MELDER KERNEL - guarded. System-wide load authority is Melder's; a user
        registering one would be claiming the right to bar the runtime's own
        transactions.

    Subsystem Context:
        The widest-scoped primitive in `utilities/synchronization/`. The other
        members coordinate WITHIN an operation - `PhaseLatch` a phase barrier,
        `CreationGate` one conduit's melds, `SafeGuard` a lock set. This one
        coordinates BETWEEN whole subsystems: it is the only gate whose scope is
        the entire process.

    System Context:
        Hosted by `Aether` and constructed before any frame can exist, so the
        coverage guarantee is unconditional. It reaches the mediators as an
        additive constructor kwarg threaded frame -> DevOpsManager ->
        ChangeControlManager -> TransactionMediator, and the mediator consults
        it at BOTH new-root ingresses. The crystallizer wraps each load verb in
        an authority span.

        Why it exists: a checkpoint restore replays a world through public
        verbs, so its own per-verb transactions must keep running while every
        foreign transaction waits - otherwise concurrent structural mutation
        would race a half-rebuilt world. The cohort extension exists because
        restore went parallel: the scheduler's restore workers are logically
        part of the load and must pass, while genuinely foreign threads keep
        parking exactly as before.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    _ast_helper_access: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Process-wide exclusive load authority. acquire(label) "
        "claims the system for one loading thread; enroll_worker() adds that "
        "span's workers so they pass too; every foreign thread parks at "
        "wait_for_passage() until release or times out naming the holding load. "
        "One load at a time - nested acquire is a pairing bug, not a wait."
    )
    __slots__ = Cleanable.__slots__ + [
        "_condition",
        "_holder_thread_id",
        "_holder_label",
        "_cohort_thread_ids",
    ]

    def __init__(self) -> None:
        """
        Public API

        Initialize an open gate with no holder.

        Purpose:
            Construct the single load-authority barrier for one Aether.

        Contract:
            - Gate starts open: no holder thread, no holder label.
            - The condition owns its lock; all mutation happens under it.

        Returns:
            None.
        """
        super().__init__()
        self._condition: threading.Condition = threading.Condition()
        self._holder_thread_id: Optional[int] = None
        self._holder_label: Optional[str] = None
        # Span cohort: worker thread idents the CURRENT holder enrolled.
        # Always empty while the gate is open; cleared on release/cleanup.
        self._cohort_thread_ids: Set[int] = set()

    def cleanup(self) -> None:
        """
        Public API

        Idempotently open and release the gate for teardown.

        Purpose:
            Deterministically terminate gate usage so no thread stays parked
            across Aether teardown.

        Contract:
            - Clears any holder and notifies all waiters.
            - DOCUMENTED TOMBSTONES (None, not del): a parked waiter may
              still be inside `wait_for_passage` when cleanup runs; it wakes,
              re-checks `_holder_thread_id`, observes the None tombstone, and
              exits cleanly. Deleting the attributes (normal del posture)
              would raise AttributeError inside that waiter, so the holder
              slots stay as None tombstones and `_condition` stays alive as
              the terminal-open surface.
            - Marks this instance cleaned; the gate is terminally OPEN: late
              `wait_for_passage` calls pass immediately.

        Threading:
            - Teardown runs under the condition lock; waiters are notified
              inside the lock so they release deterministically on exit.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._condition:
            if self._cleaned:
                return
            # None tombstones (see Contract): late waiters must be able to
            # re-check these after waking, so no del posture here. The
            # cohort set is cleared IN PLACE for the same late-waiter
            # safety rationale - membership must never outlive teardown.
            self._holder_thread_id = None
            self._holder_label = None
            self._cohort_thread_ids.clear()
            self._condition.notify_all()
            self._cleaned = True

    def acquire(self, label: str) -> None:
        """
        Public API

        Claim exclusive load authority for the calling thread.

        Purpose:
            Grant the loading thread total system authority for the span of
            one crystallizer load ("yo loader, you have all control").

        Contract:
            - Refuses when ANY holder exists (including the calling thread):
              one load at a time; nested acquire is a pairing bug.
            - Records the calling thread id and the human-readable load label
              used in waiter timeout diagnostics.

        Args:
            label:
                Load descriptor surfaced to blocked callers (typically the
                crystal source label).

        Raises:
            RuntimeError:
                If the gate is already held (message names the holder label),
                or the gate has been cleaned.
            ValueError:
                If label is falsy.

        Returns:
            None.
        """
        self.check_cleaned()
        if not label:
            raise ValueError("LoadGate.acquire requires a non-empty label.")
        with self._condition:
            if self._holder_thread_id is not None:
                raise RuntimeError(
                    "LoadGate is already held by load "
                    f"'{self._holder_label}'; one load may run at a time."
                )
            self._holder_thread_id = threading.get_ident()
            self._holder_label = label
            # Deterministic span start: a fresh span always begins as a
            # cohort of one (the holder), regardless of prior history.
            self._cohort_thread_ids.clear()

    def enroll_worker(self, thread_ident: int) -> None:
        """
        Public API

        Enroll one worker thread into the CURRENT load span's cohort.

        Purpose:
            Parallel restore admission (S3): the loading thread names its
            scheduler pool threads so restore units pass the gate while
            every foreign thread keeps parking exactly as before.

        Contract:
            - HOLDER-ONLY: only the thread that acquired the gate may
              enroll; workers never self-enroll (authority stays with the
              span owner).
            - Requires an active span; enrolling with no holder is a
              pairing bug and refuses loudly.
            - Set semantics: re-enrolling an ident is an idempotent no-op;
              enrolling the holder's own ident is a harmless no-op by
              construction (the holder already passes).

        Args:
            thread_ident:
                The worker thread's identity (threading.Thread.ident /
                threading.get_ident() value). Positive int; bools refuse.

        Raises:
            RuntimeError:
                If the gate has been cleaned, no load span is active, or
                the caller is not the holder thread.
            ValueError:
                If thread_ident is not a positive int (bools rejected).

        Threading:
            Mutates the cohort under the one gate condition lock; no new
            lock-order surface.

        Returns:
            None.
        """
        self.check_cleaned()
        if (
                isinstance(thread_ident, bool)
                or not isinstance(thread_ident, int)
                or thread_ident <= 0
        ):
            raise ValueError(
                "LoadGate.enroll_worker requires a positive int thread "
                f"ident (got {thread_ident!r})."
            )
        with self._condition:
            if self._holder_thread_id is None:
                raise RuntimeError(
                    "LoadGate.enroll_worker called with no active load "
                    "span; acquire the gate before enrolling workers."
                )
            if self._holder_thread_id != threading.get_ident():
                raise RuntimeError(
                    "LoadGate.enroll_worker must be called by the holder "
                    f"thread (load '{self._holder_label}'); workers never "
                    "self-enroll."
                )
            self._cohort_thread_ids.add(thread_ident)

    def withdraw_worker(self, thread_ident: int) -> None:
        """
        Public API

        Withdraw one worker thread from the CURRENT load span's cohort.

        Purpose:
            Let the span owner shrink its cohort (worker retirement or
            error lanes) before release.

        Contract:
            - HOLDER-ONLY, active-span-only (same refusals as enrollment).
            - Set-discard semantics: withdrawing a non-member is an
              idempotent no-op.
            - A withdrawn thread parks at its NEXT passage check; a parked
              thread re-checks membership on every condition wake, so
              withdrawal takes effect at the next wake, never by
              interruption.

        Args:
            thread_ident:
                The worker thread identity to remove. Positive int; bools
                refuse.

        Raises:
            RuntimeError:
                If the gate has been cleaned, no load span is active, or
                the caller is not the holder thread.
            ValueError:
                If thread_ident is not a positive int (bools rejected).

        Returns:
            None.
        """
        self.check_cleaned()
        if (
                isinstance(thread_ident, bool)
                or not isinstance(thread_ident, int)
                or thread_ident <= 0
        ):
            raise ValueError(
                "LoadGate.withdraw_worker requires a positive int thread "
                f"ident (got {thread_ident!r})."
            )
        with self._condition:
            if self._holder_thread_id is None:
                raise RuntimeError(
                    "LoadGate.withdraw_worker called with no active load "
                    "span; nothing to withdraw from."
                )
            if self._holder_thread_id != threading.get_ident():
                raise RuntimeError(
                    "LoadGate.withdraw_worker must be called by the holder "
                    f"thread (load '{self._holder_label}')."
                )
            self._cohort_thread_ids.discard(thread_ident)

    def release(self) -> None:
        """
        Public API

        Release load authority and wake all waiting threads.

        Purpose:
            End the exclusive load span so parked root-transaction starters
            resume admission.

        Contract:
            - Only the holder thread may release; anything else is a caller
              bug and refuses loudly.
            - Clears holder state and notifies all condition waiters.

        Raises:
            RuntimeError:
                If the gate is not held, held by a different thread, or the
                gate has been cleaned.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._condition:
            if self._holder_thread_id is None:
                raise RuntimeError("LoadGate.release called on an open gate.")
            if self._holder_thread_id != threading.get_ident():
                raise RuntimeError(
                    "LoadGate.release must be called by the holder thread "
                    f"(load '{self._holder_label}')."
                )
            self._holder_thread_id = None
            self._holder_label = None
            # No membership survives a span: the cohort clears with the
            # holder, restoring the single-thread law exactly as before.
            self._cohort_thread_ids.clear()
            self._condition.notify_all()

    def wait_for_passage(self, timeout: float = 30.0) -> None:
        """
        Public API

        Block until the gate opens, passing the holder thread immediately.

        Purpose:
            Mediator-side admission check at ROOT transaction starts: normal
            operation is a single lock-hop no-op; during a load, foreign
            threads park here instead of racing the replay.

        Contract:
            - Returns immediately when no holder exists.
            - Returns immediately when the CALLER is the holder thread (the
              loader's own per-verb transactions pass free).
            - Returns immediately when the caller is an enrolled cohort
              member (S3: the span's restore workers pass like the holder;
              membership is re-read under the lock on every wake).
            - Otherwise waits on the condition until release/cleanup, raising
              at the deadline with the holder label in the message -
              foreign-thread semantics are byte-identical to the
              pre-cohort gate.

        Args:
            timeout:
                Maximum seconds to wait for the gate to open.

        Raises:
            RuntimeError:
                If the gate does not open before "timeout".

        Notes:
            Deliberately does NOT check cleaned state: after cleanup the gate
            is terminally OPEN (tombstoned holder), so late mediator callers
            pass immediately instead of raising during teardown races.

        Returns:
            None.
        """
        deadline = time.monotonic() + timeout
        with self._condition:
            while self._holder_thread_id is not None:
                caller_ident = threading.get_ident()
                if self._holder_thread_id == caller_ident:
                    return
                if caller_ident in self._cohort_thread_ids:
                    return
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise RuntimeError(
                        "Timed out waiting for load "
                        f"'{self._holder_label}' to release the system; "
                        "root transactions are barred while a load holds "
                        "authority."
                    )
                self._condition.wait(remaining)

    def is_held(self) -> bool:
        """
        Public API

        Return True when a load currently holds the gate.

        Purpose:
            Low-cost state probe for drain loops, diagnostics, and tests.

        Returns:
            bool:
                True when a holder thread is recorded.
        """
        with self._condition:
            return self._holder_thread_id is not None

    def describe(self) -> Dict[str, Union[str, int, None, List[int]]]:
        """
        Public API

        Return a diagnostic snapshot of gate state.

        Purpose:
            Teach-grade observability: who holds the system and under what
            label, without exposing mutation surfaces.

        Returns:
            Dict[str, Union[str, int, None, List[int]]]:
                Keys "holder_thread_id" (int or None), "holder_label"
                (str or None), "cohort_size" (int), and
                "cohort_thread_ids" (detached sorted list).
        """
        with self._condition:
            return {
                "holder_thread_id": self._holder_thread_id,
                "holder_label": self._holder_label,
                "cohort_size": len(self._cohort_thread_ids),
                "cohort_thread_ids": sorted(self._cohort_thread_ids),
            }
