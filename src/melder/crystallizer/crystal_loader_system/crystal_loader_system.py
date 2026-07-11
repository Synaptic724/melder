"""
The unfold owner: durable load state over the mediated boot pipeline.

CrystalLoaderSystem is the child Crystallizer talks to for every load. It
borrows the record, owns the BootMediator, drives plan -> gated engine ->
adjudication, and REMEMBERS: for the first time, "what did we last load"
has an owner (detached last-load payload + admission view).

Lane: EPIC-2026-07-09-crystallizer-subsystem-decomposition, story S4.
"""

import threading
from typing import Dict, Optional, TYPE_CHECKING

from melder.utilities.general_base.cleanable import Cleanable
from melder.crystallizer.crystal_loader_system.boot_mediator import (
    BootMediator,
)

if TYPE_CHECKING:
    from melder.crystallizer.persistence.persistence_system import (
        PersistenceSystem,
    )


class CrystalLoaderSystem(Cleanable):
    """
    Own the crystallizer's load lanes and their durable state.

    Purpose:
        One concrete owner for the unfold (V3 identity): checkpoint
        world loads and scoped formation loads run through the owned
        BootMediator's admission pipeline, and the loader retains the
        last load's detached payload for diagnostics and re-entry.

    Contract:
        - BORROWS the record (chain detachment through public verbs);
          never cleans it.
        - OWNS the BootMediator and the durable last-load state.
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

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_persistence_system",
        "_boot_mediator",
        "_last_load",
    ]

    def __init__(self, persistence_system: PersistenceSystem) -> None:
        """
        Initialize the loader over one borrowed record.

        Args:
            persistence_system:
                The crystallizer's record. Borrowed collaborator: used
                and stored, never owned or cleaned here.

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
        self._boot_mediator: BootMediator = BootMediator(persistence_system)
        # Durable load state: the last load's detached payload (report +
        # admission view). None until the first load completes.
        self._last_load: Optional[Dict[str, object]] = None

    def cleanup(self) -> None:
        """
        Clean the owned mediator, release state and references.

        Contract:
            - Idempotent; del posture; lock deleted last.
            - The borrowed record is dereferenced, never cleaned.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            if not self._boot_mediator.cleaned:
                self._boot_mediator.cleanup()
        del self._boot_mediator
        del self._last_load
        del self._persistence_system
        del self._lock

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
            plan = self._boot_mediator.plan_checkpoint_load(checkpoint_id)
            try:
                payload = self._boot_mediator.execute_plan(plan)
            finally:
                if not plan.cleaned:
                    plan.cleanup()
            self._last_load = dict(payload)
            return payload

    def restore_formation_record(
            self,
            formation_record: Dict[str, object],
    ) -> Dict[str, object]:
        """
        Rebuild one loaded formation record through the admission pipeline.

        Purpose:
            The scoped-restore lane's owner-side seat: the asset system
            loads the record (facade-orchestrated), the mediator mints
            the synthetic window and derives the scope, the gated engine
            replays it, and the adjudicated payload is remembered.

        Args:
            formation_record:
                A stored formation record (payloads + metadata).

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
            plan = self._boot_mediator.plan_formation_load(formation_record)
            try:
                payload = self._boot_mediator.execute_plan(plan)
            finally:
                if not plan.cleaned:
                    plan.cleanup()
            self._last_load = dict(payload)
            return payload

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
