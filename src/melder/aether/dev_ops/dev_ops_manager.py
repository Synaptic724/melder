from threading import RLock
from typing import Optional
# Melder Imports
from melder.aether.dev_ops.change_control_manager.change_control_manager import ChangeControlManager
from melder.aether.dev_ops.incident_manager.incident_manager import IncidentManager
from melder.aether.dev_ops.risk_manager.risk_manager import RiskManager
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import IDevOpsManager, ISpellSystemStates
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class DevOpsManager(Cleanable, IDevOpsManager):
    """
    Aetheric Frame DevOps hub.

    Owns:
      - IncidentManager        (descriptive: what went wrong, where)
      - ChangeControlManager   (process-level view of pending changes / releases)
      - SpellSystemStates      (graph + dirty/impact state)

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
    ]

    def __init__(self, spell_system_states: ISpellSystemStates) -> None:
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
        spell_system_states.set_risk_manager(self._risk_manager)

    def cleanup(self) -> None:
        """
        Idempotent cleanup.

        Cleans up owned managers and SpellSystemStates, then nulls references
        and the lock for GC friendliness.

        After cleanup():
        - All public methods / properties will raise via check_cleaned().
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return

            self._cleaned = True

            if self._incident_manager is not None:
                self._incident_manager.cleanup()
                self._incident_manager = None

            if self._change_control_manager is not None:
                self._change_control_manager.cleanup()
                self._change_control_manager = None

            if self._risk_manager is not None:
                self._risk_manager.cleanup()
                self._risk_manager = None

            if self._spell_system_states is not None:
                self._spell_system_states.cleanup()
                self._spell_system_states = None

        self._lock = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    @property
    def incident_manager(self) -> Optional[IncidentManager]:
        self.check_cleaned()
        # Read-only exposure; no structural mutation, but still guard with lock
        with self._lock:
            return self._incident_manager

    @property
    def change_control_manager(self) -> Optional[ChangeControlManager]:
        self.check_cleaned()
        with self._lock:
            return self._change_control_manager

    @property
    def risk_manager(self) -> Optional[RiskManager]:
        self.check_cleaned()
        with self._lock:
            return self._risk_manager

    def revalidate_dirty_roots(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Trigger revalidation for dirty roots within a conduit scope.
        """
        self.check_cleaned()
        if not conduit_id:
            raise ValueError("conduit_id cannot be empty.")
        with self._lock:
            ccm = self._change_control_manager
        if ccm is None:
            return
        ccm.revalidate_dirty_roots(conduit_id, cancel_event=cancel_event)

    @property
    def spell_system_states(self) -> Optional[ISpellSystemStates]:
        """
        Expose the underlying SpellSystemStates for callers that want
        direct graph/dirty-state access through the DevOpsManager.
        """
        self.check_cleaned()
        with self._lock:
            return self._spell_system_states
