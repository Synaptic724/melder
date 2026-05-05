from typing import Optional, Protocol, runtime_checkable
import threading
from melder.utilities.interfaces.assets.icleanable import ICleanable
from melder.utilities.interfaces.assets.ispellsystemstates import ISpellSystemStates

@runtime_checkable
class IDevOpsManager(ICleanable, Protocol):
    """
    Aetheric Frame DevOps hub protocol.

    This interface defines the contract for the hub that owns:
      - IncidentManager        (descriptive: what went wrong, where)
      - ChangeControlManager   (process-level view of pending changes / releases)
      - SpellSystemStates      (graph + dirty/impact state)

    This is the place higher-level tools / AI consult when they want to
    understand or manipulate the health and changes of a frame.
    """
    _lock: threading.RLock
    _spell_system_states: ISpellSystemStates
    _incident_manager: 'IncidentManager'
    _change_control_manager: 'ChangeControlManager'
    _risk_manager: object
    _creation_gate_controller: object
    # ------------------------------------------------------------------
    # Public API Properties
    # ------------------------------------------------------------------
    @property
    def incident_manager(self) -> Optional['IncidentManager']:
        """
        Read-only exposure of the IncidentManager (descriptive: what went wrong, where).
        """
        ...

    @property
    def change_control_manager(self) -> Optional['ChangeControlManager']:
        """
        Read-only exposure of the ChangeControlManager (process-level view of pending changes / releases).
        """
        ...

    @property
    def risk_manager(self) -> Optional[object]:
        """
        Read-only exposure of the RiskManager (validation gating state).
        """
        ...

    @property
    def creation_gate_controller(self) -> Optional[object]:
        """
        Read-only exposure of the CreationGateController used for gate governance.
        """
        ...

    def enable_conduit_gate(self, conduit_id: str) -> None:
        """
        Open one conduit-scoped creation gate by conduit id.
        """
        ...

    def disable_conduit_gate(self, conduit_id: str) -> None:
        """
        Close one conduit-scoped creation gate by conduit id.
        """
        ...

    def close_and_wait_conduit(
            self,
            conduit_id: str,
            timeout: float = 30.0,
            interval: float = 0.1,
    ) -> None:
        """
        Terminally close one conduit-scoped gate and wait for drain.
        """
        ...

    def enable_conduit_lineage(self, root_conduit_id: str) -> None:
        """
        Open all conduit-scoped gates under one root lineage id.
        """
        ...

    def disable_conduit_lineage(self, root_conduit_id: str) -> None:
        """
        Close all conduit-scoped gates under one root lineage id.
        """
        ...

    def close_and_wait_conduit_lineage(
            self,
            root_conduit_id: str,
            timeout: float = 30.0,
            interval: float = 0.1,
    ) -> None:
        """
        Terminally close all conduit gates under one root lineage and wait for drain.
        """
        ...

    @property
    def spell_system_states(self) -> Optional['ISpellSystemStates']:
        """
        Expose the underlying SpellSystemStates for callers that want
        direct graph/dirty-state access through the DevOpsManager.
        """
        ...
