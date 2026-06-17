from threading import RLock
from typing import TYPE_CHECKING, ClassVar

from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

if TYPE_CHECKING:
    from melder.utilities.synchronization.creation_gate_controller import (
        CreationGateController,
    )


class ConduitLineageGateOps(Cleanable):
    """
    Narrow conduit-lineage creation-gate facade for coordinated strategies.

    Purpose:
        Expose only the conduit-lineage creation-gate operations a coordinated
        mediator transaction strategy needs -- drain, reopen, close, and a
        quiescence count -- over the frame's SINGLE `CreationGateController`
        (one per frame, owned by `DevOpsManager`). The controller already keys
        gates by `root_conduit_id`, so this one facade covers EVERY root in the
        frame; a call is simply scoped by the root id it is given.

    Contract:
        - Wraps the frame's single `CreationGateController` BY REFERENCE; it does
          not own the controller. `cleanup()` drops the borrowed reference only;
          it never cleans the controller (DevOpsManager owns that lifecycle).
        - Every operation is conduit-lineage scoped, keyed by `root_conduit_id`,
          and works for any root registered in the shared controller.
        - Missing/unknown lineage roots are no-ops (controller contract).
        - Public operations fail through `check_cleaned()` after teardown.

    Threading:
        - Owns an `RLock` guarding its own `_cleaned` / controller-reference
          state. Each operation captures the controller under the lock, then
          delegates OUTSIDE the lock, so a long blocking drain never holds this
          facade's lock.

    Lifecycle:
        - `cleanup()` is idempotent and lock-guarded; it drops the borrowed
          controller reference and retires the facade.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_creation_gate_controller",
    ]

    def __init__(self, creation_gate_controller: "CreationGateController") -> None:
        """
        Bind the facade to one frame-owned creation-gate controller.

        Args:
            creation_gate_controller:
                The frame's single `CreationGateController`, owned by
                `DevOpsManager`.

        Returns:
            None.

        Raises:
            ValueError:
                If `creation_gate_controller` is None.
        """
        super().__init__()
        if creation_gate_controller is None:
            raise ValueError("creation_gate_controller cannot be None.")
        self._lock: RLock = RLock()
        self._creation_gate_controller: "CreationGateController" = (
            creation_gate_controller
        )

    def cleanup(self) -> None:
        """
        Idempotently retire the facade and drop the borrowed controller reference.

        Contract:
            - Idempotent and lock-guarded; repeat calls become no-ops after
              `_cleaned` flips.
            - Drops ONLY the borrowed controller reference; never cleans the
              controller (its lifecycle is owned by `DevOpsManager`).
            - Drops the lock reference after the guarded section.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            del self._creation_gate_controller
        del self._lock

    def _controller(self) -> "CreationGateController":
        """
        Return the borrowed controller after a guarded cleaned-state check.

        Purpose:
            Centralize the `check_cleaned()` + lock-protected reference capture so
            each public operation can delegate to the controller OUTSIDE the lock.

        Returns:
            CreationGateController:
                The borrowed frame controller.

        Raises:
            RuntimeError:
                If the facade has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            self.check_cleaned()
            return self._creation_gate_controller

    def close_and_wait_conduit_lineage(
            self,
            root_conduit_id: str,
            *,
            timeout: float = 30.0,
            interval: float = 0.1,
    ) -> None:
        """
        Quiesce one root lineage: close every conduit gate under
        `root_conduit_id` and block until all in-flight creation tickets exit.

        Purpose:
            The drain primitive a coordinated strategy runs while its scopes are
            held, so no meld is mid-create against a store about to be unbound or
            disposed (a meld holds its gate ticket across the whole executor).

        Args:
            root_conduit_id:
                Lineage root whose conduit gates are drained.
            timeout:
                Maximum seconds to wait per gate for its tickets to drain.
            interval:
                Poll interval in seconds while draining each gate.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the facade or controller is cleaned, or a gate drain times out.
        """
        self._controller().close_and_wait_until_conduit_lineage_free(
            root_conduit_id,
            timeout=timeout,
            interval=interval,
        )

    def enable_conduit_lineage(self, root_conduit_id: str) -> None:
        """
        Reopen every conduit gate under one root lineage.

        Purpose:
            Restore admission after a coordinated window, on every exit path
            (commit, abort, or error), so a lineage is never left permanently
            gated.

        Args:
            root_conduit_id:
                Lineage root whose conduit gates are reopened.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the facade or controller is cleaned.
        """
        controller = self._controller()
        for gate in controller.get_conduit_lineage_gates(root_conduit_id).values():
            gate.open()

    def disable_conduit_lineage(self, root_conduit_id: str) -> None:
        """
        Close every conduit gate under one root lineage without draining.

        Purpose:
            Seal admission on a lineage when the caller does not need to wait for
            in-flight tickets (e.g. a fast inert transition).

        Args:
            root_conduit_id:
                Lineage root whose conduit gates are closed.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the facade or controller is cleaned.
        """
        controller = self._controller()
        for gate in controller.get_conduit_lineage_gates(root_conduit_id).values():
            gate.close()

    def count_active_tickets_for_conduit_lineage(self, root_conduit_id: str) -> int:
        """
        Return the summed in-flight creation tickets across one root lineage.

        Purpose:
            Cheap quiescence inspection (e.g. a debug assertion that an inert
            lineage truly has zero in-flight creates before an `elect`).

        Args:
            root_conduit_id:
                Lineage root to inspect.

        Returns:
            int:
                Sum of active creation tickets across the lineage's gates, or 0
                when the root is unknown.

        Raises:
            RuntimeError:
                If the facade or controller is cleaned.
        """
        return self._controller().count_active_threads_for_conduit_lineage(
            root_conduit_id,
        )
