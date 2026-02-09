import threading
from typing import Dict, Optional

from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.synchronization.creation_gate import CreationGate


class CreationGateController(Cleanable):
    """
    Central registry and control plane for CreationGate instances.

    Purpose:
        Provide one orchestration surface for creation gates across two scopes:

        - Conduit-scope gates indexed by
          ``root_conduit_id -> conduit_id -> CreationGate`` and a reverse
          ``conduit_id -> root_conduit_id`` map.
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
        - The controller uses an internal ``RLock`` to make teardown
          deterministic under concurrent access.
        - Callers should still serialize concurrent registry mutations.
    """

    __slots__ = (
        "_lock",
        "_conduit_creation_gates",
        "_conduit_creation_gates_by_root",
        "_conduit_root_by_conduit",
        "_spell_lineage_creation_gates",
    )

    def __init__(self) -> None:
        """
        Public API

        Initialize empty conduit and spell-lineage gate registries.

        Registry layout:
            - ``_lock``:
                Internal synchronization lock used by cleanup paths.
            - ``_conduit_creation_gates``:
                Flat index for O(1) lookup by conduit_id.
            - ``_conduit_creation_gates_by_root``:
                Hierarchical index for lineage operations:
                ``root_conduit_id -> conduit_id -> gate``.
            - ``_conduit_root_by_conduit``:
                Reverse index for O(1) root lookup by conduit_id.
        """
        super().__init__()
        self._lock: Optional[threading.RLock] = threading.RLock()
        self._conduit_creation_gates: Dict[str, CreationGate] = {}
        self._conduit_creation_gates_by_root: Dict[str, Dict[str, CreationGate]] = {}
        self._conduit_root_by_conduit: Dict[str, str] = {}
        self._spell_lineage_creation_gates: Dict[str, CreationGate] = {}

    def cleanup(self) -> None:
        """
        Public API

        Idempotently tear down all registered gates and clear controller state.

        Contract:
            - Calls ``cleanup()`` on all unique registered gates.
            - Clears and nulls all registries/indexes.
            - Marks the controller cleaned.

        Threading:
            - Cleanup is lock-guarded and re-checks cleaned state inside lock.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return
            gates = set(self._conduit_creation_gates.values())
            gates.update(self._spell_lineage_creation_gates.values())
            for gate in gates:
                gate.cleanup()
            self._conduit_creation_gates.clear()
            self._conduit_creation_gates_by_root.clear()
            self._conduit_root_by_conduit.clear()
            self._spell_lineage_creation_gates.clear()
            self._cleaned = True
            self._conduit_creation_gates = None
            self._conduit_creation_gates_by_root = None
            self._conduit_root_by_conduit = None
            self._spell_lineage_creation_gates = None

        self._lock = None

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
    @staticmethod
    def _normalize_root_conduit_id(
        *,
        conduit_id: str,
        root_conduit_id: Optional[str],
    ) -> str:
        """
        Internal

        Normalize root id for conduit registration.

        Contract:
            - When no explicit root is provided, root defaults to conduit_id.
        """
        if root_conduit_id is None:
            return conduit_id
        return root_conduit_id

    def create_conduit_gate(
        self,
        conduit_id: str,
        *,
        root_conduit_id: Optional[str] = None,
    ) -> CreationGate:
        """
        Public API

        Create and register a conduit-scope CreationGate.

        Args:
            conduit_id:
                Unique conduit key for the flat conduit index.
            root_conduit_id:
                Optional lineage root key. When omitted, defaults to
                ``conduit_id`` (single-node lineage).
        """
        self.check_cleaned()
        self._require_key(conduit_id, "conduit_id")
        self._ensure_absent(self._conduit_creation_gates, conduit_id, "conduit_id")
        normalized_root = self._normalize_root_conduit_id(
            conduit_id=conduit_id,
            root_conduit_id=root_conduit_id,
        )
        self._require_key(normalized_root, "root_conduit_id")
        gate = CreationGate()
        self._conduit_creation_gates[conduit_id] = gate
        root_map = self._conduit_creation_gates_by_root.setdefault(normalized_root, {})
        root_map[conduit_id] = gate
        self._conduit_root_by_conduit[conduit_id] = normalized_root
        return gate

    def register_conduit_gate(
        self,
        conduit_id: str,
        gate: CreationGate,
        *,
        root_conduit_id: Optional[str] = None,
    ) -> None:
        """
        Public API

        Register an existing conduit-scope CreationGate.

        Args:
            conduit_id:
                Unique conduit key for the flat conduit index.
            gate:
                Existing gate instance to attach.
            root_conduit_id:
                Optional lineage root key. When omitted, defaults to
                ``conduit_id`` (single-node lineage).
        """
        self.check_cleaned()
        self._require_key(conduit_id, "conduit_id")
        self._ensure_absent(self._conduit_creation_gates, conduit_id, "conduit_id")
        normalized_root = self._normalize_root_conduit_id(
            conduit_id=conduit_id,
            root_conduit_id=root_conduit_id,
        )
        self._require_key(normalized_root, "root_conduit_id")
        self._conduit_creation_gates[conduit_id] = gate
        root_map = self._conduit_creation_gates_by_root.setdefault(normalized_root, {})
        root_map[conduit_id] = gate
        self._conduit_root_by_conduit[conduit_id] = normalized_root

    def unregister_conduit_gate(self, conduit_id: str) -> None:
        """
        Public API

        Remove conduit-scope registration by key.
        """
        self.check_cleaned()
        gate = self._conduit_creation_gates.pop(conduit_id, None)
        root_conduit_id = self._conduit_root_by_conduit.pop(conduit_id, None)
        if gate is None or root_conduit_id is None:
            return
        root_map = self._conduit_creation_gates_by_root.get(root_conduit_id)
        if root_map is None:
            return
        root_map.pop(conduit_id, None)
        if not root_map:
            self._conduit_creation_gates_by_root.pop(root_conduit_id, None)

    def get_conduit_gate(self, conduit_id: str) -> Optional[CreationGate]:
        """
        Public API

        Return conduit-scope gate by key, or None when missing.
        """
        self.check_cleaned()
        return self._conduit_creation_gates.get(conduit_id)

    def get_root_conduit_id_for_conduit(self, conduit_id: str) -> Optional[str]:
        """
        Public API

        Return lineage root id for a conduit id, or None when missing.
        """
        self.check_cleaned()
        return self._conduit_root_by_conduit.get(conduit_id)

    def get_conduit_lineage_gates(self, root_conduit_id: str) -> Dict[str, CreationGate]:
        """
        Public API

        Return a detached conduit->gate map for one root lineage.

        Args:
            root_conduit_id:
                Root lineage key.

        Returns:
            Dict[str, CreationGate]:
                Detached snapshot map for the lineage. Empty if root missing.
        """
        self.check_cleaned()
        if not root_conduit_id:
            return {}
        root_map = self._conduit_creation_gates_by_root.get(root_conduit_id)
        if not root_map:
            return {}
        return dict(root_map)

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

    def count_active_threads_for_conduit_lineage(self, root_conduit_id: str) -> int:
        """
        Public API

        Return active ticket count summed across one root lineage.
        """
        self.check_cleaned()
        if not root_conduit_id:
            return 0
        root_map = self._conduit_creation_gates_by_root.get(root_conduit_id)
        if not root_map:
            return 0
        return sum(gate.active_ticket_count() for gate in root_map.values())

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

    def get_spell_lineage_gate(self, lineage_id: str) -> Optional[CreationGate]:
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

