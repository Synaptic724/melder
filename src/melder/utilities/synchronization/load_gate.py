import threading
import time
from typing import ClassVar, Dict, Optional, Union


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
          caller pairing bug, not a wait condition.
        - "release()" reopens the gate and wakes all waiters. Only the holder
          thread may release.
        - "wait_for_passage(timeout)" is the mediator-side check: it returns
          immediately when the gate is open OR the caller IS the holder, and
          otherwise blocks on the internal condition until release, raising
          RuntimeError at the deadline.

    Threading:
        - All state transitions are guarded by one "Lock" wrapped in a
          "Condition"; waiters park on the condition and are notified on
          release and on cleanup.
        - Hosted once per Aether, constructed BEFORE any AethericFrame can
          exist, so frames born mid-load inherit coverage unconditionally.

    Lifecycle:
        - "cleanup()" terminally opens the gate and wakes all waiters. Holder
          slots become None TOMBSTONES (documented; not del) so late waiters
          exit cleanly; `wait_for_passage` after cleanup passes immediately.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_condition",
        "_holder_thread_id",
        "_holder_label",
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
            # re-check these after waking, so no del posture here.
            self._holder_thread_id = None
            self._holder_label = None
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
            - Otherwise waits on the condition until release/cleanup, raising
              at the deadline with the holder label in the message.

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
                if self._holder_thread_id == threading.get_ident():
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

    def describe(self) -> Dict[str, Union[str, int, None]]:
        """
        Public API

        Return a diagnostic snapshot of gate state.

        Purpose:
            Teach-grade observability: who holds the system and under what
            label, without exposing mutation surfaces.

        Returns:
            Dict[str, Union[str, int, None]]:
                Keys "holder_thread_id" (int or None) and "holder_label"
                (str or None).
        """
        with self._condition:
            return {
                "holder_thread_id": self._holder_thread_id,
                "holder_label": self._holder_label,
            }
