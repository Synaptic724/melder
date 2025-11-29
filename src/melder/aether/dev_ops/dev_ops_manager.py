from __future__ import annotations
from threading import RLock
# Melder Imports
from melder.aether.dev_ops.change_control_manager.change_control_manager import ChangeControlManager
from melder.aether.dev_ops.incident_manager.incident_manager import IncidentManager
from melder.utilities.general_base.cleanable import Cleanable


class DevOpsManager(Cleanable):
    """
    Aetheric Frame DevOps hub.

    Owns:
      - IncidentManager        (descriptive: what went wrong, where)
      - ChangeControlManager   (process-level view of pending changes / releases)
      - SpellSystemStates      (graph + dirty/impact state)

    This is the place higher-level tools / AI consult when they want to
    understand or manipulate the health and changes of a frame.
    """

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_spell_system_states",
        "_incident_manager",
        "_change_control_manager",
    ]

    def __init__(self, spell_system_states: 'SpellSystemStates') -> None:
        super().__init__()
        if spell_system_states is None:
            raise ValueError("spell_system_states cannot be None")

        self._lock: RLock = RLock()
        self._spell_system_states: 'SpellSystemStates' = spell_system_states
        self._incident_manager: IncidentManager = IncidentManager()
        self._change_control_manager: ChangeControlManager = ChangeControlManager(
            spell_system_states=spell_system_states
        )

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

            if self._spell_system_states is not None:
                self._spell_system_states.cleanup()
                self._spell_system_states = None

        self._lock = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    @property
    def incident_manager(self) -> IncidentManager:
        self.check_cleaned()
        # Read-only exposure; no structural mutation, but still guard with lock
        with self._lock:
            return self._incident_manager

    @property
    def change_control_manager(self) -> ChangeControlManager:
        self.check_cleaned()
        with self._lock:
            return self._change_control_manager

    @property
    def spell_system_states(self) -> 'SpellSystemStates':
        """
        Expose the underlying SpellSystemStates for callers that want
        direct graph/dirty-state access through the DevOpsManager.
        """
        self.check_cleaned()
        with self._lock:
            return self._spell_system_states
