from __future__ import annotations

from typing import Dict

from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.synchronization.creation_gate import CreationGate


class CreationGateController(Cleanable):
    """
    Central registry and control plane for CreationGate instances.

    Purpose:
        Provide one orchestration surface for creation gates across two scopes:

        - Conduit-scope gates keyed by ``conduit_id``.
        - Spell-lineage gates keyed by ``lineage_id``.

        This split allows the same gate primitive to be reused for both
        conduit-level meld entry control and spell-level creation-context
        lifecycle control while keeping independent registries.

    Contract:
        - Each registry key must be non-empty and unique within its registry.
        - Missing-key lookups return ``None``.
        - Missing-key count/drain operations are no-ops returning zero/None.
        - ``enable_all`` / ``disable_all`` fan out to both registries.
        - All public methods enforce ``check_cleaned()``.

    Threading:
        - The controller intentionally avoids internal locks to remain low
          overhead and composable; callers are expected to serialize registry
          mutation if concurrent writes are possible.
    """

    __slots__ = ("_conduit_creation_gates", "_spell_lineage_creation_gates")

    def __init__(self) -> None:
        """
        Public API

        Initialize empty conduit and spell-lineage gate registries.
        """
        super().__init__()
        self._conduit_creation_gates: Dict[str, CreationGate] = {}
        self._spell_lineage_creation_gates: Dict[str, CreationGate] = {}

    def cleanup(self) -> None:
        """
        Public API

        Idempotently clear both registries and mark the controller cleaned.
        """
        if self._cleaned:
            return
        self._conduit_creation_gates.clear()
        self._spell_lineage_creation_gates.clear()
        self._cleaned = True

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _require_key(key: str, key_name: str) -> None:
        """
        Internal

        Validate a registry key is non-empty.
        """
        if not key:
            raise ValueError(f"{key_name} cannot be empty.")

    @staticmethod
    def _ensure_absent(
        registry: Dict[str, CreationGate],
        key: str,
        key_name: str,
    ) -> None:
        """
        Internal

        Ensure a registry key is not already bound.
        """
        if key in registry:
            raise ValueError(f"CreationGate already registered for {key_name}={key}.")

    @staticmethod
    def _count_active(registry: Dict[str, CreationGate], key: str) -> int:
        """
        Internal

        Return active tickets for one gate key or zero when missing.
        """
        gate = registry.get(key)
        if gate is None:
            return 0
        return gate.active_ticket_count()

    @staticmethod
    def _close_and_wait(
        registry: Dict[str, CreationGate],
        key: str,
        timeout: float,
        interval: float,
    ) -> None:
        """
        Internal

        Close and drain one keyed gate; no-op when key is missing.
        """
        gate = registry.get(key)
        if gate is None:
            return
        gate.close_and_wait_until_free(timeout=timeout, interval=interval)

    # ------------------------------------------------------------------
    # Conduit-scope registry
    # ------------------------------------------------------------------
    def create_conduit_gate(self, conduit_id: str) -> CreationGate:
        """
        Public API

        Create and register a conduit-scope CreationGate.
        """
        self.check_cleaned()
        self._require_key(conduit_id, "conduit_id")
        self._ensure_absent(self._conduit_creation_gates, conduit_id, "conduit_id")
        gate = CreationGate()
        self._conduit_creation_gates[conduit_id] = gate
        return gate

    def register_conduit_gate(self, conduit_id: str, gate: CreationGate) -> None:
        """
        Public API

        Register an existing conduit-scope CreationGate.
        """
        self.check_cleaned()
        self._require_key(conduit_id, "conduit_id")
        self._ensure_absent(self._conduit_creation_gates, conduit_id, "conduit_id")
        self._conduit_creation_gates[conduit_id] = gate

    def unregister_conduit_gate(self, conduit_id: str) -> None:
        """
        Public API

        Remove conduit-scope registration by key.
        """
        self.check_cleaned()
        self._conduit_creation_gates.pop(conduit_id, None)

    def get_conduit_gate(self, conduit_id: str) -> CreationGate | None:
        """
        Public API

        Return conduit-scope gate by key, or None when missing.
        """
        self.check_cleaned()
        return self._conduit_creation_gates.get(conduit_id)

    def count_active_threads_for_conduit(self, conduit_id: str) -> int:
        """
        Public API

        Return active ticket count for one conduit gate.
        """
        self.check_cleaned()
        return self._count_active(self._conduit_creation_gates, conduit_id)

    def count_active_threads_conduits(self) -> int:
        """
        Public API

        Return active ticket count summed across all conduit gates.
        """
        self.check_cleaned()
        return sum(gate.active_ticket_count() for gate in self._conduit_creation_gates.values())

    def close_and_wait_until_conduit_free(
        self,
        conduit_id: str,
        timeout: float = 30.0,
        interval: float = 0.1,
    ) -> None:
        """
        Public API

        Terminally close and drain one conduit-scope gate.
        """
        self.check_cleaned()
        self._close_and_wait(
            self._conduit_creation_gates,
            conduit_id,
            timeout,
            interval,
        )

    def enable_all_conduit_gates(self) -> None:
        """
        Public API

        Open every conduit-scope gate.
        """
        self.check_cleaned()
        for gate in self._conduit_creation_gates.values():
            gate.open()

    def disable_all_conduit_gates(self) -> None:
        """
        Public API

        Close every conduit-scope gate.
        """
        self.check_cleaned()
        for gate in self._conduit_creation_gates.values():
            gate.close()

    # ------------------------------------------------------------------
    # Spell-lineage registry
    # ------------------------------------------------------------------
    def create_spell_lineage_gate(self, lineage_id: str) -> CreationGate:
        """
        Public API

        Create and register a spell-lineage CreationGate.
        """
        self.check_cleaned()
        self._require_key(lineage_id, "lineage_id")
        self._ensure_absent(self._spell_lineage_creation_gates, lineage_id, "lineage_id")
        gate = CreationGate()
        self._spell_lineage_creation_gates[lineage_id] = gate
        return gate

    def register_spell_lineage_gate(self, lineage_id: str, gate: CreationGate) -> None:
        """
        Public API

        Register an existing spell-lineage CreationGate.
        """
        self.check_cleaned()
        self._require_key(lineage_id, "lineage_id")
        self._ensure_absent(self._spell_lineage_creation_gates, lineage_id, "lineage_id")
        self._spell_lineage_creation_gates[lineage_id] = gate

    def unregister_spell_lineage_gate(self, lineage_id: str) -> None:
        """
        Public API

        Remove spell-lineage registration by key.
        """
        self.check_cleaned()
        self._spell_lineage_creation_gates.pop(lineage_id, None)

    def get_spell_lineage_gate(self, lineage_id: str) -> CreationGate | None:
        """
        Public API

        Return spell-lineage gate by key, or None when missing.
        """
        self.check_cleaned()
        return self._spell_lineage_creation_gates.get(lineage_id)

    def count_active_threads_for_spell_lineage(self, lineage_id: str) -> int:
        """
        Public API

        Return active ticket count for one spell-lineage gate.
        """
        self.check_cleaned()
        return self._count_active(self._spell_lineage_creation_gates, lineage_id)

    def count_active_threads_spell_lineages(self) -> int:
        """
        Public API

        Return active ticket count summed across all spell-lineage gates.
        """
        self.check_cleaned()
        return sum(
            gate.active_ticket_count() for gate in self._spell_lineage_creation_gates.values()
        )

    def close_and_wait_until_spell_lineage_free(
        self,
        lineage_id: str,
        timeout: float = 30.0,
        interval: float = 0.1,
    ) -> None:
        """
        Public API

        Terminally close and drain one spell-lineage gate.
        """
        self.check_cleaned()
        self._close_and_wait(
            self._spell_lineage_creation_gates,
            lineage_id,
            timeout,
            interval,
        )

    def enable_all_spell_lineage_gates(self) -> None:
        """
        Public API

        Open every spell-lineage gate.
        """
        self.check_cleaned()
        for gate in self._spell_lineage_creation_gates.values():
            gate.open()

    def disable_all_spell_lineage_gates(self) -> None:
        """
        Public API

        Close every spell-lineage gate.
        """
        self.check_cleaned()
        for gate in self._spell_lineage_creation_gates.values():
            gate.close()

    # ------------------------------------------------------------------
    # Aggregate control
    # ------------------------------------------------------------------
    def count_active_threads_total(self) -> int:
        """
        Public API

        Return active tickets summed across both registries.
        """
        self.check_cleaned()
        return (
            self.count_active_threads_conduits()
            + self.count_active_threads_spell_lineages()
        )

    def enable_all(self) -> None:
        """
        Public API

        Open every registered gate (conduit + spell lineage).
        """
        self.check_cleaned()
        self.enable_all_conduit_gates()
        self.enable_all_spell_lineage_gates()

    def disable_all(self) -> None:
        """
        Public API

        Close every registered gate (conduit + spell lineage).
        """
        self.check_cleaned()
        self.disable_all_conduit_gates()
        self.disable_all_spell_lineage_gates()

    # ------------------------------------------------------------------
    # Compatibility aliases for conduit-level meld replacement
    # ------------------------------------------------------------------
    def create_gate(self, conduit_id: str) -> CreationGate:
        """
        Public API

        Back-compat alias for conduit gate creation.
        """
        return self.create_conduit_gate(conduit_id)

    def register_gate(self, conduit_id: str, gate: CreationGate) -> None:
        """
        Public API

        Back-compat alias for conduit gate registration.
        """
        self.register_conduit_gate(conduit_id, gate)

    def unregister_gate(self, conduit_id: str) -> None:
        """
        Public API

        Back-compat alias for conduit gate unregistration.
        """
        self.unregister_conduit_gate(conduit_id)

    def get_gate(self, conduit_id: str) -> CreationGate | None:
        """
        Public API

        Back-compat alias for conduit gate lookup.
        """
        return self.get_conduit_gate(conduit_id)

    def count_active_threads(self, conduit_id: str) -> int:
        """
        Public API

        Back-compat alias for conduit gate active count.
        """
        return self.count_active_threads_for_conduit(conduit_id)

    def count_active_threads_lineage(self) -> int:
        """
        Public API

        Back-compat alias for summing conduit-scope active tickets.
        """
        return self.count_active_threads_conduits()

    def close_and_wait_until_free(
        self,
        conduit_id: str,
        timeout: float = 30.0,
        interval: float = 0.1,
    ) -> None:
        """
        Public API

        Back-compat alias for conduit gate close-and-drain.
        """
        self.close_and_wait_until_conduit_free(
            conduit_id=conduit_id,
            timeout=timeout,
            interval=interval,
        )
