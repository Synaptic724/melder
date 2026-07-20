import threading
from typing import Dict, Optional
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.nexus.rift.rift_gate.rift_gate import RiftGate
from melder.utilities.general_base.cleanable import Cleanable


class RiftGateController(Cleanable):
    """
    Central registry and control plane for `RiftGate` instances.

    Purpose:
        Provide one `Nexus`-owned orchestration surface for Rift-scoped gates so
        the Rift runtime can later coordinate pause, resume, and drain behavior
        under one control root.

    Contract:
        - Each Rift id must be non-empty and unique within the registry.
        - Missing-key lookups return None.
        - Missing-key count/drain operations are no-ops returning zero/None.
        - enable_all and disable_all fan out across every registered
          Rift gate.
        - All public methods enforce check_cleaned().

    Threading:
        - Uses one internal RLock so cleanup and registry mutation are
          deterministic under concurrent access.
        - Callers should still serialize higher-level lifecycle transitions.

    Registration:
        MELDER KERNEL - guarded. Owned by `Nexus`; users never construct or
        address it directly.

    Subsystem Context:
        The Nexus-owned control plane over per-Rift `RiftGate` instances. It is
        what makes a projection refresh a COORDINATED operation across many
        Rifts rather than a per-Rift concern.

    System Context:
        Centralizing the gates is what allows the ACL fan-out to work at all.
        When a frame's ACL chain bumps, `Nexus` computes the union of impacted
        Rifts by checking which ones carry that frame in their contract set,
        blocks each through its gate, drains in-flight tickets, refreshes each
        Rift once for its changed-frame subset, and reopens. Without one
        controller owning every gate, that sequence would have to be
        reimplemented per call site and could not be made atomic across Rifts.
        The tolerant lookup contract - missing keys return None, missing-key
        counts and drains are no-ops - is deliberate for fan-out code: a Rift
        may be torn down concurrently with a refresh, and raising on a
        disappeared id would turn a normal race into an error.
    """
    _ast_helper_access: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Central registry and control plane for `RiftGate` instances. Melder "
        "kernel machinery: read it to understand the runtime, do not drive it directly."
    )

    __melder_internal__ = _mrg.sentinel
    __slots__ = ("_lock", "_rift_gates_by_rift_id")

    def __init__(self) -> None:
        """
        Initialize an empty Rift-gate registry.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        self._rift_gates_by_rift_id: Dict[str, RiftGate] = {}

    def cleanup(self) -> None:
        """
        Idempotently tear down all registered gates and clear controller state.

        Returns:
            None.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return
            for gate in self._rift_gates_by_rift_id.values():
                gate.cleanup()
            self._rift_gates_by_rift_id.clear()
            self._cleaned = True

            del self._rift_gates_by_rift_id
        del self._lock

    @staticmethod
    def _require_rift_id(rift_id: str) -> None:
        """
        Validate a Rift id is non-empty.

        Args:
            rift_id:
                Candidate Rift id.

        Returns:
            None.
        """
        if not rift_id:
            raise ValueError("rift_id cannot be empty.")

    @staticmethod
    def _ensure_absent(registry: Dict[str, RiftGate], rift_id: str) -> None:
        """
        Ensure a Rift id is not already registered.

        Args:
            registry:
                Target registry map.
            rift_id:
                Candidate Rift id.

        Returns:
            None.
        """
        if rift_id in registry:
            raise ValueError(
                "RiftGate already registered for rift_id={0}.".format(rift_id)
            )

    def create_rift_gate(self, rift_id: str) -> RiftGate:
        """
        Create and register a Rift-scoped gate.

        Args:
            rift_id:
                Unique Rift id for the gate.

        Returns:
            RiftGate: Newly created and registered gate instance.
        """
        self.check_cleaned()
        self._require_rift_id(rift_id)
        with self._lock:
            self._ensure_absent(self._rift_gates_by_rift_id, rift_id)
            gate = RiftGate()
            self._rift_gates_by_rift_id[rift_id] = gate
            return gate

    def register_rift_gate(self, rift_id: str, gate: RiftGate) -> None:
        """
        Register an existing Rift-scoped gate.

        Args:
            rift_id:
                Unique Rift id for the gate.
            gate:
                Existing gate instance to register.

        Returns:
            None.
        """
        self.check_cleaned()
        self._require_rift_id(rift_id)
        with self._lock:
            self._ensure_absent(self._rift_gates_by_rift_id, rift_id)
            self._rift_gates_by_rift_id[rift_id] = gate

    def unregister_rift_gate(self, rift_id: str) -> None:
        """
        Remove Rift-gate registration by Rift id.

        Args:
            rift_id:
                Rift id to unregister.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._rift_gates_by_rift_id.pop(rift_id, None)

    def get_rift_gate(self, rift_id: str) -> Optional[RiftGate]:
        """
        Return the registered Rift gate for one Rift id.

        Args:
            rift_id:
                Rift id to resolve.

        Returns:
            Optional[RiftGate]: Registered gate when present; otherwise None.
        """
        self.check_cleaned()
        with self._lock:
            return self._rift_gates_by_rift_id.get(rift_id)

    def count_active_threads_for_rift(self, rift_id: str) -> int:
        """
        Return active ticket count for one Rift gate.

        Args:
            rift_id:
                Rift id to resolve.

        Returns:
            int: Active ticket count for the Rift gate, or 0 when missing.
        """
        self.check_cleaned()
        with self._lock:
            gate = self._rift_gates_by_rift_id.get(rift_id)
        if gate is None:
            return 0
        return gate.active_ticket_count()

    def count_active_threads_total(self) -> int:
        """
        Return active ticket count summed across all registered Rift gates.

        Returns:
            int: Sum of active tickets across the Rift registry.
        """
        self.check_cleaned()
        with self._lock:
            return sum(
                gate.active_ticket_count()
                for gate in self._rift_gates_by_rift_id.values()
            )

    def close_and_wait_until_rift_free(
        self,
        rift_id: str,
        timeout: float = 30.0,
        interval: float = 0.1,
    ) -> None:
        """
        Terminally close and drain one Rift gate.

        Args:
            rift_id:
                Rift id to resolve.
            timeout:
                Maximum seconds to wait for ticket drain.
            interval:
                Poll interval in seconds while draining.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            gate = self._rift_gates_by_rift_id.get(rift_id)
        if gate is None:
            return
        gate.close_and_wait_until_free(timeout=timeout, interval=interval)

    def enable_all_rift_gates(self) -> None:
        """
        Open every registered Rift gate.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            for gate in self._rift_gates_by_rift_id.values():
                gate.open()

    def disable_all_rift_gates(self) -> None:
        """
        Close every registered Rift gate.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            for gate in self._rift_gates_by_rift_id.values():
                gate.close()

    def enable_all(self) -> None:
        """
        Open every registered Rift gate.

        Returns:
            None.
        """
        self.check_cleaned()
        self.enable_all_rift_gates()

    def disable_all(self) -> None:
        """
        Close every registered Rift gate.

        Returns:
            None.
        """
        self.check_cleaned()
        self.disable_all_rift_gates()

    def set_rift_gate_entry_mode(self, rift_id: str, entry_mode: str) -> None:
        """
        Set the admission mode for one registered Rift gate.

        Args:
            rift_id:
                Rift id to resolve.
            entry_mode:
                Admission mode to apply.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            gate = self._rift_gates_by_rift_id.get(rift_id)
        if gate is None:
            return
        gate.set_entry_mode(entry_mode)

    def set_all_rift_gate_entry_mode(self, entry_mode: str) -> None:
        """
        Set the admission mode for every registered Rift gate.

        Args:
            entry_mode:
                Admission mode to apply.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            for gate in self._rift_gates_by_rift_id.values():
                gate.set_entry_mode(entry_mode)

