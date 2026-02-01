from __future__ import annotations

from typing import Dict

from melder.aether.conduit.meld.meld_gate import MeldGate
from melder.utilities.general_base.cleanable import Cleanable


class MeldGateController(Cleanable):
    """
    Controller and registry for conduit-local MeldGate instances.

    Purpose:
        Provide a single control point for a normal conduit to manage and
        broadcast enable/disable operations across every MeldGate registered
        to its lineage (normal + lesser conduits).

    Contract:
        - Maintains a registry keyed by conduit_id.
        - create_gate() registers a new gate for a conduit_id.
        - register_gate() attaches an existing gate to the registry.
        - enable_all()/disable_all() fan out to all registered gates.
        - count_active_threads() reports per-gate active ticket counts.
        - count_active_threads_lineage() aggregates active tickets across gates.
        - close_and_wait_until_free() closes a gate and waits for tickets to drain.
        - cleanup() clears the registry and marks the controller as cleaned.

    Threading:
        - This controller does not add locks; callers manage concurrency.
    """

    __slots__ = ("_meld_gates",)

    def __init__(self) -> None:
        """
        Public API

        Initialize an empty MeldGate registry.
        """
        super().__init__()
        self._meld_gates: Dict[str, MeldGate] = {}

    def cleanup(self) -> None:
        """
        Public API

        Idempotently clear the gate registry and mark the controller as cleaned.
        """
        if self._cleaned:
            return
        self._meld_gates.clear()
        self._cleaned = True

    def create_gate(self, conduit_id: str) -> MeldGate:
        """
        Public API

        Create and register a new MeldGate for a conduit.

        Args:
            conduit_id: Unique conduit identifier used as the registry key.

        Returns:
            MeldGate: The newly created gate registered under conduit_id.

        Raises:
            RuntimeError: If the controller is cleaned.
            ValueError: If conduit_id is empty or already registered.
        """
        self.check_cleaned()
        if not conduit_id:
            raise ValueError("conduit_id cannot be empty.")
        if conduit_id in self._meld_gates:
            raise ValueError(f"MeldGate already registered for conduit_id={conduit_id}.")
        gate = MeldGate()
        self._meld_gates[conduit_id] = gate
        return gate

    def register_gate(self, conduit_id: str, gate: MeldGate) -> None:
        """
        Public API

        Register an existing MeldGate for a conduit.

        Args:
            conduit_id: Unique conduit identifier used as the registry key.
            gate: The MeldGate instance to register.

        Raises:
            RuntimeError: If the controller is cleaned.
            ValueError: If conduit_id is empty or already registered.
        """
        self.check_cleaned()
        if not conduit_id:
            raise ValueError("conduit_id cannot be empty.")
        if conduit_id in self._meld_gates:
            raise ValueError(f"MeldGate already registered for conduit_id={conduit_id}.")
        self._meld_gates[conduit_id] = gate

    def unregister_gate(self, conduit_id: str) -> None:
        """
        Public API

        Remove a MeldGate registration by conduit_id.

        Args:
            conduit_id: Unique conduit identifier used as the registry key.

        Raises:
            RuntimeError: If the controller is cleaned.
        """
        self.check_cleaned()
        self._meld_gates.pop(conduit_id, None)

    def get_gate(self, conduit_id: str) -> MeldGate | None:
        """
        Public API

        Fetch the MeldGate registered for a conduit id.

        Args:
            conduit_id: Unique conduit identifier used as the registry key.

        Returns:
            MeldGate | None: The registered gate if present; otherwise None.
        """
        self.check_cleaned()
        return self._meld_gates.get(conduit_id)

    def count_active_threads(self, conduit_id: str) -> int:
        """
        Public API

        Return the active ticket count for a single conduit gate.

        Args:
            conduit_id: Unique conduit identifier used as the registry key.

        Returns:
            int: Active ticket count for the conduit gate (0 if not found).
        """
        self.check_cleaned()
        gate = self._meld_gates.get(conduit_id)
        if gate is None:
            return 0
        return gate.active_ticket_count()

    def count_active_threads_lineage(self) -> int:
        """
        Public API

        Return the total active ticket count across all registered gates.

        Returns:
            int: Sum of active tickets for every registered gate.
        """
        self.check_cleaned()
        return sum(gate.active_ticket_count() for gate in self._meld_gates.values())

    def close_and_wait_until_free(self, conduit_id: str) -> None:
        """
        Public API

        Close a conduit gate and wait until its active tickets drain.

        Args:
            conduit_id: Unique conduit identifier used as the registry key.

        Raises:
            RuntimeError: If the controller is cleaned.
        """
        self.check_cleaned()
        gate = self._meld_gates.get(conduit_id)
        if gate is None:
            return
        gate.close_and_wait_until_free()

    def enable_all(self) -> None:
        """
        Public API

        Enable all registered meld gates.
        """
        self.check_cleaned()
        for gate in self._meld_gates.values():
            gate.enable()

    def disable_all(self) -> None:
        """
        Public API

        Disable all registered meld gates.
        """
        self.check_cleaned()
        for gate in self._meld_gates.values():
            gate.disable()
