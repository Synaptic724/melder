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
    Frame-level ownership root for DevOps and admission-control subsystems.

    `DevOpsManager` is the operational facade over the frame's health and
    control-plane services. It owns and exposes the managers that describe
    incidents, track dirty/pending change state, assess risk, and govern
    conduit creation-gate admission.

    Owned subsystems:
    - `IncidentManager`: descriptive incident recording
    - `ChangeControlManager`: pending-change and dirty-root coordination
    - `RiskManager`: risk posture tied back into spell-system state
    - `CreationGateController`: conduit and lineage admission governance
    - `SpellSystemStates`: frame-local state registry surfaced through this hub

    Contract:
    - One `DevOpsManager` owns one coherent set of frame-local operational
      managers.
    - The manager is the intended boundary for higher-level tools or AI agents
      that need to inspect or manipulate frame health.
    - Cleanup is responsible for tearing down the owned manager graph in a
      deterministic order.
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
        Return the owned `IncidentManager`.

        This property exposes the frame's incident-recording surface through the
        DevOps ownership boundary instead of requiring callers to reach into
        lower-level frame internals directly.

        Returns:
            IncidentManager: The incident manager owned by this DevOps root.
        """
        self.check_cleaned()
        with self._lock:
            return self._incident_manager

    @property
    def change_control_manager(self) -> ChangeControlManager:
        """
        Return the owned `ChangeControlManager`.

        This is the frame-local process/control surface for pending changes,
        dirty roots, and revalidation coordination.

        Returns:
            ChangeControlManager: The change-control manager owned by this
            DevOps root.
        """
        self.check_cleaned()
        with self._lock:
            return self._change_control_manager

    @property
    def risk_manager(self) -> RiskManager:
        """
        Return the owned `RiskManager`.

        This exposes the frame-local risk surface that feeds back into
        spell-system validity and gating behavior.

        Returns:
            RiskManager: The risk manager owned by this DevOps root.
        """
        self.check_cleaned()
        with self._lock:
            return self._risk_manager

    @property
    def creation_gate_controller(self) -> CreationGateController:
        """
        Read-only exposure of the per-frame CreationGateController.

        This is the admission-governance surface for conduit and lineage gates.

        Returns:
            CreationGateController: The gate controller owned by this DevOps
            root.
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
        Trigger dirty-root revalidation for one conduit scope.

        This is the DevOps-owned facade for the frame's change-control
        revalidation path. It keeps callers at the manager boundary while still
        letting them force revalidation for a specific conduit.

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
        Expose the underlying `SpellSystemStates` for direct state inspection.

        This keeps the frame's spell-system state reachable through the same
        ownership hub as the other operational managers.

        Returns:
            ISpellSystemStates: The frame-local spell-system state registry
            owned by this DevOps root.
        """
        self.check_cleaned()
        with self._lock:
            return self._spell_system_states
