from typing import Optional, Protocol, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iriftgate import IRiftGate

@runtime_checkable
class IRiftGateController(ICleanable, Protocol):
    """
    Interface for the Nexus-owned Rift-gate controller.
    """

    def create_rift_gate(self, rift_id: str) -> IRiftGate:
        """
        Create and register one Rift gate.
        """
        ...

    def register_rift_gate(self, rift_id: str, gate: IRiftGate) -> None:
        """
        Register one existing Rift gate by Rift id.
        """
        ...

    def unregister_rift_gate(self, rift_id: str) -> None:
        """
        Unregister one Rift gate by Rift id.
        """
        ...

    def get_rift_gate(self, rift_id: str) -> Optional[IRiftGate]:
        """
        Return the registered Rift gate for one Rift id, if present.
        """
        ...

    def count_active_threads_for_rift(self, rift_id: str) -> int:
        """
        Return active ticket count for one Rift gate.
        """
        ...

    def count_active_threads_total(self) -> int:
        """
        Return active ticket count summed across all registered Rift gates.
        """
        ...

    def close_and_wait_until_rift_free(
            self,
            rift_id: str,
            timeout: float = 30.0,
            interval: float = 0.1,
    ) -> None:
        """
        Terminally close and drain one Rift gate.
        """
        ...

    def enable_all_rift_gates(self) -> None:
        """
        Open every registered Rift gate.
        """
        ...

    def disable_all_rift_gates(self) -> None:
        """
        Close every registered Rift gate.
        """
        ...

    def enable_all(self) -> None:
        """
        Open every registered Rift gate.
        """
        ...

    def disable_all(self) -> None:
        """
        Close every registered Rift gate.
        """
        ...

    def set_rift_gate_entry_mode(self, rift_id: str, entry_mode: str) -> None:
        """
        Set the admission mode for one registered Rift gate.
        """
        ...

    def set_all_rift_gate_entry_mode(self, entry_mode: str) -> None:
        """
        Set the admission mode for every registered Rift gate.
        """
        ...
