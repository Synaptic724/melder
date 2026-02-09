from threading import RLock
from typing import Optional
# Melder Imports
from melder.aether.dev_ops.change_control_manager.change_control_manager import ChangeControlManager
from melder.aether.dev_ops.incident_manager.incident_manager import IncidentManager
from melder.aether.dev_ops.risk_manager.risk_manager import RiskManager
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import IDevOpsManager, ISpellSystemStates
from melder.utilities.synchronization.creation_gate_controller import CreationGateController
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class DevOpsManager(Cleanable, IDevOpsManager):
    """
    Aetheric Frame DevOps hub.

    Owns:
      - IncidentManager        (descriptive: what went wrong, where)
      - ChangeControlManager   (process-level view of pending changes / releases)
      - SpellSystemStates      (graph + dirty/impact state)
      - CreationGateController (conduit creation-gate governance)

    This is the place higher-level tools / AI consult when they want to
    understand or manipulate the health and changes of a frame.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_spell_system_states",
        "_incident_manager",
        "_change_control_manager",
        "_risk_manager",
        "_creation_gate_controller",
    ]

    def __init__(self, spell_system_states: ISpellSystemStates) -> None:
        """
        Public API

        Initialize the frame-level DevOps manager and owned subsystems.

        Purpose:
            Construct one ownership root for operational managers that must
            outlive frame runtime objects such as conduits.

        Contract:
            - All owned managers are created exactly once during init.
            - RiskManager is attached to SpellSystemStates via
              ``set_risk_manager(...)``.
            - ``spell_system_states`` must be provided.

        Args:
            spell_system_states:
                Frame-level spell system state registry.

        Returns:
            None.

        Raises:
            ValueError:
                If ``spell_system_states`` is ``None``.
        """
        super().__init__()
        if spell_system_states is None:
            raise ValueError("spell_system_states cannot be None")

        self._lock: RLock = RLock()
        self._spell_system_states: ISpellSystemStates = spell_system_states
        self._incident_manager: IncidentManager = IncidentManager()
        self._change_control_manager: ChangeControlManager = ChangeControlManager(
            spell_system_states=spell_system_states
        )
        self._risk_manager: RiskManager = RiskManager(spell_system_states)
        self._creation_gate_controller: CreationGateController = CreationGateController()
        spell_system_states.set_risk_manager(self._risk_manager)

    def cleanup(self) -> None:
        """
        Public API

        Idempotently cleanup all owned managers and clear references.

        Purpose:
            Deterministically tear down DevOps ownership graph for a frame.

        Contract:
            - Cleanup is idempotent.
            - Owned managers are cleaned in deterministic order.
            - Owned references and lock are nulled after cleanup.

        Returns:
            None.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return

            self._cleaned = True

            self._incident_manager.cleanup()
            self._change_control_manager.cleanup()
            self._risk_manager.cleanup()
            self._creation_gate_controller.cleanup()
            self._spell_system_states.cleanup()

            self._incident_manager = None
            self._change_control_manager = None
            self._risk_manager = None
            self._creation_gate_controller = None
            self._spell_system_states = None

        self._lock = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    @property
    def incident_manager(self) -> IncidentManager:
        """
        Public API

        Return the owned IncidentManager.
        """
        self.check_cleaned()
        with self._lock:
            return self._incident_manager

    @property
    def change_control_manager(self) -> ChangeControlManager:
        """
        Public API

        Return the owned ChangeControlManager.
        """
        self.check_cleaned()
        with self._lock:
            return self._change_control_manager

    @property
    def risk_manager(self) -> RiskManager:
        """
        Public API

        Return the owned RiskManager.
        """
        self.check_cleaned()
        with self._lock:
            return self._risk_manager

    @property
    def creation_gate_controller(self) -> CreationGateController:
        """
        Public API

        Read-only exposure of the per-frame CreationGateController.
        """
        self.check_cleaned()
        with self._lock:
            return self._creation_gate_controller

    def revalidate_dirty_roots(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Public API

        Trigger revalidation for dirty roots within a conduit scope.

        Args:
            conduit_id:
                Conduit id whose dirty roots should be revalidated.
            cancel_event:
                Optional cancellation signal forwarded to change-control
                revalidation.

        Returns:
            None.

        Raises:
            RuntimeError:
                If manager has been cleaned.
            ValueError:
                If ``conduit_id`` is empty.
        """
        self.check_cleaned()
        if not conduit_id:
            raise ValueError("conduit_id cannot be empty.")
        with self._lock:
            self._change_control_manager.revalidate_dirty_roots(
                conduit_id,
                cancel_event=cancel_event,
            )

    def enable_conduit_gate(self, conduit_id: str) -> None:
        """
        Public API

        Open one conduit-scoped CreationGate.

        Purpose:
            Provide a DevOps-owned facade for re-enabling admission on a
            specific conduit gate.

        Contract:
            - Resolves gate ownership through ``CreationGateController`` only.
            - Missing conduit gate is a no-op.
            - Does not mutate registry membership.

        Args:
            conduit_id:
                Conduit id whose gate should be opened.

        Returns:
            None.

        Raises:
            RuntimeError:
                If manager has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            gate = self._creation_gate_controller.get_conduit_gate(conduit_id)
            if gate is None:
                return
            gate.open()

    def disable_conduit_gate(self, conduit_id: str) -> None:
        """
        Public API

        Close one conduit-scoped CreationGate.

        Purpose:
            Provide a DevOps-owned facade for disabling admission on a
            specific conduit gate.

        Contract:
            - Resolves gate ownership through ``CreationGateController`` only.
            - Missing conduit gate is a no-op.
            - Does not mutate registry membership.

        Args:
            conduit_id:
                Conduit id whose gate should be closed.

        Returns:
            None.

        Raises:
            RuntimeError:
                If manager has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            gate = self._creation_gate_controller.get_conduit_gate(conduit_id)
            if gate is None:
                return
            gate.close()

    def close_and_wait_conduit(
            self,
            conduit_id: str,
            timeout: float = 30.0,
            interval: float = 0.1,
    ) -> None:
        """
        Public API

        Terminally close and drain one conduit-scoped CreationGate.

        Purpose:
            Seal one conduit gate and wait for all in-flight tickets to leave
            before returning.

        Contract:
            - Delegates to ``CreationGateController.close_and_wait_until_conduit_free``.
            - Missing conduit gate is a no-op by controller contract.

        Args:
            conduit_id:
                Conduit id whose gate should be drained.
            timeout:
                Maximum seconds to wait for drain.
            interval:
                Poll interval in seconds while draining.

        Returns:
            None.

        Raises:
            RuntimeError:
                If manager has been cleaned or the gate drain times out.
        """
        self.check_cleaned()
        with self._lock:
            self._creation_gate_controller.close_and_wait_until_conduit_free(
                conduit_id,
                timeout=timeout,
                interval=interval,
            )

    def enable_conduit_lineage(self, root_conduit_id: str) -> None:
        """
        Public API

        Open all conduit gates registered under one root lineage.

        Purpose:
            Provide top-down lineage admission enablement from the DevOps
            ownership boundary.

        Contract:
            - Uses detached lineage snapshot from controller.
            - Missing lineage root is a no-op.
            - Does not mutate registry membership.

        Args:
            root_conduit_id:
                Root conduit id that identifies the lineage bucket.

        Returns:
            None.

        Raises:
            RuntimeError:
                If manager has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            lineage_map = self._creation_gate_controller.get_conduit_lineage_gates(root_conduit_id)
            for gate in lineage_map.values():
                gate.open()

    def disable_conduit_lineage(self, root_conduit_id: str) -> None:
        """
        Public API

        Close all conduit gates registered under one root lineage.

        Purpose:
            Provide top-down lineage admission disablement from the DevOps
            ownership boundary.

        Contract:
            - Uses detached lineage snapshot from controller.
            - Missing lineage root is a no-op.
            - Does not mutate registry membership.

        Args:
            root_conduit_id:
                Root conduit id that identifies the lineage bucket.

        Returns:
            None.

        Raises:
            RuntimeError:
                If manager has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            lineage_map = self._creation_gate_controller.get_conduit_lineage_gates(root_conduit_id)
            for gate in lineage_map.values():
                gate.close()

    def close_and_wait_conduit_lineage(
            self,
            root_conduit_id: str,
            timeout: float = 30.0,
            interval: float = 0.1,
    ) -> None:
        """
        Public API

        Terminally close and drain all conduit gates under one lineage root.

        Purpose:
            Provide a single DevOps entrypoint to seal a lineage and wait for
            in-flight lineage work to complete.

        Contract:
            - Delegates to controller lineage close-and-drain API.
            - Missing lineage root is a no-op by controller contract.

        Args:
            root_conduit_id:
                Root conduit id that identifies the lineage bucket.
            timeout:
                Maximum seconds to wait per gate for drain.
            interval:
                Poll interval in seconds while draining each gate.

        Returns:
            None.

        Raises:
            RuntimeError:
                If manager has been cleaned or any lineage gate drain times out.
        """
        self.check_cleaned()
        with self._lock:
            self._creation_gate_controller.close_and_wait_until_conduit_lineage_free(
                root_conduit_id,
                timeout=timeout,
                interval=interval,
            )

    @property
    def spell_system_states(self) -> ISpellSystemStates:
        """
        Public API

        Expose the underlying SpellSystemStates for callers that want
        direct graph/dirty-state access through the DevOpsManager.
        """
        self.check_cleaned()
        with self._lock:
            return self._spell_system_states
