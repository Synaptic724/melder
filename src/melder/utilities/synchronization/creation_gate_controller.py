import threading
from typing import Dict, Optional, ClassVar
from mypy_extensions import mypyc_attr
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.synchronization.creation_gate import CreationGate
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
@mypyc_attr(native_class=True)
class CreationGateController(Cleanable):
    """
    Central registry and control plane for CreationGate instances.

    Purpose:
        Provide one orchestration surface for creation gates across two scopes:

        - Conduit-scope gates indexed by
          root_conduit_id -> conduit_id -> CreationGate and a reverse
          conduit_id -> root_conduit_id map.
        - Spell-index gates keyed by index_id.

        This split allows the same gate primitive to be reused for both
        conduit-level meld entry control and spell-level creation-context
        lifecycle control while keeping independent registries.

    Contract:
        - Each registry key must be non-empty and unique within its registry.
        - Missing-key lookups return None.
        - Missing-key count/drain operations are no-ops returning zero/None.
        - enable_all / disable_all fan out to both registries.
        - All public methods enforce check_cleaned().

    Threading:
        - The controller uses an internal RLock to make teardown
          deterministic under concurrent access.
        - Callers should still serialize concurrent registry mutations.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_conduit_creation_gates",
        "_conduit_creation_gates_by_root",
        "_conduit_root_by_conduit",
        "_spell_index_creation_gates",
    ]
    __deletable__: ClassVar[list[str]] = [
        "_lock",
        "_conduit_creation_gates",
        "_conduit_creation_gates_by_root",
        "_conduit_root_by_conduit",
        "_spell_index_creation_gates",
    ]

    def __init__(self) -> None:
        """
        Public API

        Initialize empty conduit and spell-index gate registries.

        Purpose:
            Construct a frame-level gate registry that can govern both
            conduit lineage entry control and spell-index creation control.

        Contract:
            - All registries start empty.
            - _lock is initialized for deterministic cleanup sequencing.

        Registry layout:
            - _lock:
                Internal synchronization lock used by cleanup paths.
            - _conduit_creation_gates:
                Flat index for O(1) lookup by conduit_id.
            - _conduit_creation_gates_by_root:
                Hierarchical index for lineage operations:
                root_conduit_id -> conduit_id -> gate.
            - _conduit_root_by_conduit:
                Reverse index for O(1) root lookup by conduit_id.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        self._conduit_creation_gates: Dict[str, CreationGate] = {}
        self._conduit_creation_gates_by_root: Dict[str, Dict[str, CreationGate]] = {}
        self._conduit_root_by_conduit: Dict[str, str] = {}
        self._spell_index_creation_gates: Dict[str, CreationGate] = {}

    def cleanup(self) -> None:
        """
        Public API

        Idempotently tear down all registered gates and clear controller state.

        Purpose:
            Deterministically dispose every owned gate reference and invalidate
            the controller instance for further use.

        Contract:
            - Calls cleanup() on all unique registered gates.
            - Deduplicates gates that appear in both conduit flat/root indexes
              before cleanup so shared gate instances are only cleaned once.
            - Clears and nulls all registries/indexes.
            - Marks the controller cleaned.
            - Leaves the object unusable for all guarded API calls.

        Threading:
            - Cleanup is lock-guarded and re-checks cleaned state inside lock.

        Returns:
            None.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return
            gates = set(self._conduit_creation_gates.values())
            gates.update(self._spell_index_creation_gates.values())
            for gate in gates:
                gate.cleanup()
            self._conduit_creation_gates.clear()
            self._conduit_creation_gates_by_root.clear()
            self._conduit_root_by_conduit.clear()
            self._spell_index_creation_gates.clear()
            self._cleaned = True

            del self._conduit_creation_gates
            del self._conduit_creation_gates_by_root
            del self._conduit_root_by_conduit
            del self._spell_index_creation_gates

        del self._lock

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _require_key(key: str, key_name: str) -> None:
        """
        Internal

        Validate a registry key is non-empty.

        Args:
            key:
                Candidate registry key.
            key_name:
                Human-readable key label used in error messaging.

        Raises:
            ValueError:
                If key is empty.

        Returns:
            None.
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

        Args:
            registry:
                Target registry map for uniqueness enforcement.
            key:
                Candidate key to reserve.
            key_name:
                Human-readable key label used in error messaging.

        Raises:
            ValueError:
                If key already exists in registry.

        Returns:
            None.
        """
        if key in registry:
            raise ValueError(f"CreationGate already registered for {key_name}={key}.")

    @staticmethod
    def _count_active(registry: Dict[str, CreationGate], key: str) -> int:
        """
        Internal

        Return active tickets for one gate key or zero when missing.

        Args:
            registry:
                Registry map to query.
            key:
                Gate lookup key.

        Returns:
            int:
                Active ticket count for key, or 0 when key is missing.
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

        Args:
            registry:
                Registry map to query.
            key:
                Gate lookup key.
            timeout:
                Maximum seconds to wait for drain.
            interval:
                Poll interval in seconds while draining.

        Raises:
            RuntimeError:
                Propagated from gate drain timeout.

        Returns:
            None.
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

        Purpose:
            Provide one canonical root id used by both flat and nested
            conduit registries.

        Contract:
            - When no explicit root is provided, root defaults to conduit_id.

        Args:
            conduit_id:
                Conduit identifier being registered.
            root_conduit_id:
                Optional explicit lineage root id.

        Returns:
            str:
                Normalized lineage root id.
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

        Purpose:
            Allocate a new gate for one conduit and index it in both the
            conduit flat map and root-lineage map.

        Contract:
            - conduit_id must be unique in conduit registry.
            - Root map and reverse root index are updated atomically within
              this call.
            - Returns the same gate instance stored in controller registries.

        Args:
            conduit_id:
                Unique conduit key for the flat conduit index.
            root_conduit_id:
                Optional lineage root key. When omitted, defaults to
                conduit_id (single-node lineage).

        Returns:
            CreationGate:
                Newly created and registered gate instance.

        Raises:
            RuntimeError:
                If called after cleanup().
            ValueError:
                If conduit_id or normalized root id is empty, or if
                conduit_id is already registered.
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

        Purpose:
            Attach an externally created gate instance to conduit/root indices.

        Contract:
            - conduit_id must be unique in conduit registry.
            - Provided gate is stored by reference.
            - Root map and reverse root index are updated atomically within
              this call.

        Args:
            conduit_id:
                Unique conduit key for the flat conduit index.
            gate:
                Existing gate instance to attach.
            root_conduit_id:
                Optional lineage root key. When omitted, defaults to
                conduit_id (single-node lineage).

        Returns:
            None.

        Raises:
            RuntimeError:
                If called after cleanup().
            ValueError:
                If conduit_id or normalized root id is empty, or if
                conduit_id is already registered.
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

        Purpose:
            Remove one conduit gate from flat, nested, and reverse indices.

        Contract:
            - Missing conduit id is a no-op.
            - Empty root buckets are pruned.
            - Does not cleanup the gate instance; it only detaches registry
              ownership.

        Args:
            conduit_id:
                Conduit key to unregister.

        Returns:
            None.

        Raises:
            RuntimeError:
                If called after cleanup().
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

        Args:
            conduit_id:
                Conduit key to resolve.

        Returns:
            Optional[CreationGate]:
                Registered gate instance when present; otherwise None.

        Raises:
            RuntimeError:
                If called after cleanup().
        """
        self.check_cleaned()
        return self._conduit_creation_gates.get(conduit_id)

    def get_root_conduit_id_for_conduit(self, conduit_id: str) -> Optional[str]:
        """
        Public API

        Return lineage root id for a conduit id, or None when missing.

        Args:
            conduit_id:
                Conduit key to resolve.

        Returns:
            Optional[str]:
                Root lineage id when present; otherwise None.

        Raises:
            RuntimeError:
                If called after cleanup().
        """
        self.check_cleaned()
        return self._conduit_root_by_conduit.get(conduit_id)

    def get_conduit_lineage_gates(self, root_conduit_id: str) -> Dict[str, CreationGate]:
        """
        Public API

        Return a detached conduit->gate map for one root lineage.

        Purpose:
            Provide a snapshot view for lineage-scoped orchestration without
            exposing mutable registry internals.

        Args:
            root_conduit_id:
                Root lineage key.

        Returns:
            Dict[str, CreationGate]:
                Detached snapshot map for the lineage. Empty if root missing.
                The returned dict is detached, but the gate objects inside it
                are the live registered instances.

        Raises:
            RuntimeError:
                If called after cleanup().
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

        Args:
            conduit_id:
                Conduit key to resolve.

        Returns:
            int:
                Active ticket count for the conduit gate, or 0 when missing.

        Raises:
            RuntimeError:
                If called after cleanup().
        """
        self.check_cleaned()
        return self._count_active(self._conduit_creation_gates, conduit_id)

    def count_active_threads_conduits(self) -> int:
        """
        Public API

        Return active ticket count summed across all conduit gates.

        Returns:
            int:
                Sum of active tickets across conduit registry.

        Raises:
            RuntimeError:
                If called after cleanup().
        """
        self.check_cleaned()
        return sum(gate.active_ticket_count() for gate in self._conduit_creation_gates.values())

    def count_active_threads_for_conduit_lineage(self, root_conduit_id: str) -> int:
        """
        Public API

        Return active ticket count summed across one root lineage.

        Args:
            root_conduit_id:
                Root lineage key.

        Returns:
            int:
                Sum of active tickets for gates under root_conduit_id;
                returns 0 when root is missing.

        Raises:
            RuntimeError:
                If called after cleanup().
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

        Purpose:
            Seal one conduit gate and wait for in-flight ticket drain.

        Args:
            conduit_id:
                Conduit key to resolve.
            timeout:
                Maximum seconds to wait for ticket drain.
            interval:
                Poll interval in seconds while draining.

        Returns:
            None.

        Raises:
            RuntimeError:
                If called after cleanup() or if the underlying gate drain
                times out.
        """
        self.check_cleaned()
        self._close_and_wait(
            self._conduit_creation_gates,
            conduit_id,
            timeout,
            interval,
        )

    def close_and_wait_until_conduit_lineage_free(
        self,
        root_conduit_id: str,
        timeout: float = 30.0,
        interval: float = 0.1,
    ) -> None:
        """
        Public API

        Terminally close and drain all conduit gates under one lineage root.

        Purpose:
            Seal entry across an entire conduit lineage and wait for all
            in-flight lineage tickets to exit before returning.

        Contract:
            - Uses a detached lineage snapshot from the root index.
            - Missing or empty root_conduit_id is a no-op.
            - Calls close_and_wait_until_free(...) on each lineage gate.
            - Does not unregister or cleanup gates; it only performs close+drain.

        Args:
            root_conduit_id:
                Root lineage key used to select conduit gates.
            timeout:
                Maximum seconds to wait per gate for ticket drain.
            interval:
                Poll interval in seconds while draining each gate.

        Returns:
            None.

        Raises:
            RuntimeError:
                If called after cleanup() or if any lineage gate drain
                times out.
        """
        self.check_cleaned()
        if not root_conduit_id:
            return
        lineage_map = self.get_conduit_lineage_gates(root_conduit_id)
        for gate in lineage_map.values():
            gate.close_and_wait_until_free(timeout=timeout, interval=interval)

    def enable_all_conduit_gates(self) -> None:
        """
        Public API

        Open every conduit-scope gate.

        Contract:
            - Invokes open() on each registered conduit gate.
            - No-op when registry is empty.

        Returns:
            None.

        Raises:
            RuntimeError:
                If called after cleanup().
        """
        self.check_cleaned()
        for gate in self._conduit_creation_gates.values():
            gate.open()

    def disable_all_conduit_gates(self) -> None:
        """
        Public API

        Close every conduit-scope gate.

        Contract:
            - Invokes close() on each registered conduit gate.
            - No-op when registry is empty.

        Returns:
            None.

        Raises:
            RuntimeError:
                If called after cleanup().
        """
        self.check_cleaned()
        for gate in self._conduit_creation_gates.values():
            gate.close()

    # ------------------------------------------------------------------
    # Spell-index registry
    # ------------------------------------------------------------------
    def create_spell_index_gate(self, index_id: str) -> CreationGate:
        """
        Public API

        Create and register a spell-index CreationGate.

        Purpose:
            Allocate a new gate for one spell index id.

        Contract:
            - index_id must be unique in spell-index registry.
            - Returns the same gate instance stored in registry.

        Args:
            index_id:
                Spell index key.

        Returns:
            CreationGate:
                Newly created and registered gate instance.

        Raises:
            RuntimeError:
                If called after cleanup().
            ValueError:
                If index_id is empty or already registered.
        """
        self.check_cleaned()
        self._require_key(index_id, "index_id")
        self._ensure_absent(self._spell_index_creation_gates, index_id, "index_id")
        gate = CreationGate()
        self._spell_index_creation_gates[index_id] = gate
        return gate

    def register_spell_index_gate(self, index_id: str, gate: CreationGate) -> None:
        """
        Public API

        Register an existing spell-index CreationGate.

        Purpose:
            Attach an externally created gate instance to spell-index registry.

        Contract:
            - index_id must be unique in spell-index registry.
            - Provided gate is stored by reference.

        Args:
            index_id:
                Spell index key.
            gate:
                Existing gate instance to register.

        Returns:
            None.

        Raises:
            RuntimeError:
                If called after cleanup().
            ValueError:
                If index_id is empty or already registered.
        """
        self.check_cleaned()
        self._require_key(index_id, "index_id")
        self._ensure_absent(self._spell_index_creation_gates, index_id, "index_id")
        self._spell_index_creation_gates[index_id] = gate

    def unregister_spell_index_gate(self, index_id: str) -> None:
        """
        Public API

        Remove spell-index registration by key.

        Contract:
            - Missing index id is a no-op.
            - Does not cleanup the gate instance; it only detaches registry
              ownership.

        Args:
            index_id:
                Spell index key to unregister.

        Returns:
            None.

        Raises:
            RuntimeError:
                If called after cleanup().
        """
        self.check_cleaned()
        self._spell_index_creation_gates.pop(index_id, None)

    def get_spell_index_gate(self, index_id: str) -> Optional[CreationGate]:
        """
        Public API

        Return spell-index gate by key, or None when missing.

        Args:
            index_id:
                Spell index key.

        Returns:
            Optional[CreationGate]:
                Registered gate instance when present; otherwise None.

        Raises:
            RuntimeError:
                If called after cleanup().
        """
        self.check_cleaned()
        return self._spell_index_creation_gates.get(index_id)

    def count_active_threads_for_spell_index(self, index_id: str) -> int:
        """
        Public API

        Return active ticket count for one spell-index gate.

        Args:
            index_id:
                Spell index key.

        Returns:
            int:
                Active ticket count for the spell-index gate, or 0 when missing.

        Raises:
            RuntimeError:
                If called after cleanup().
        """
        self.check_cleaned()
        return self._count_active(self._spell_index_creation_gates, index_id)

    def count_active_threads_spell_indexes(self) -> int:
        """
        Public API

        Return active ticket count summed across all spell-index gates.

        Returns:
            int:
                Sum of active tickets across spell-index registry.

        Raises:
            RuntimeError:
                If called after cleanup().
        """
        self.check_cleaned()
        return sum(
            gate.active_ticket_count() for gate in self._spell_index_creation_gates.values()
        )

    def close_and_wait_until_spell_index_free(
        self,
        index_id: str,
        timeout: float = 30.0,
        interval: float = 0.1,
    ) -> None:
        """
        Public API

        Terminally close and drain one spell-index gate.

        Purpose:
            Seal one spell-index gate and wait for in-flight ticket drain.

        Args:
            index_id:
                Spell index key.
            timeout:
                Maximum seconds to wait for ticket drain.
            interval:
                Poll interval in seconds while draining.

        Returns:
            None.

        Raises:
            RuntimeError:
                If called after cleanup() or if the underlying gate drain
                times out.
        """
        self.check_cleaned()
        self._close_and_wait(
            self._spell_index_creation_gates,
            index_id,
            timeout,
            interval,
        )

    def enable_all_spell_index_gates(self) -> None:
        """
        Public API

        Open every spell-index gate.

        Contract:
            - Invokes open() on each registered spell-index gate.
            - No-op when registry is empty.

        Returns:
            None.

        Raises:
            RuntimeError:
                If called after cleanup().
        """
        self.check_cleaned()
        for gate in self._spell_index_creation_gates.values():
            gate.open()

    def disable_all_spell_index_gates(self) -> None:
        """
        Public API

        Close every spell-index gate.

        Contract:
            - Invokes close() on each registered spell-index gate.
            - No-op when registry is empty.

        Returns:
            None.

        Raises:
            RuntimeError:
                If called after cleanup().
        """
        self.check_cleaned()
        for gate in self._spell_index_creation_gates.values():
            gate.close()

    # ------------------------------------------------------------------
    # Aggregate control
    # ------------------------------------------------------------------
    def count_active_threads_total(self) -> int:
        """
        Public API

        Return active tickets summed across both registries.

        Returns:
            int:
                Sum of active conduit and spell-index tickets.

        Raises:
            RuntimeError:
                If called after cleanup().

        Notes:
            This is an aggregate sum across the current conduit and spell-index
            registries, not a lock-held global snapshot of all gate activity.
        """
        self.check_cleaned()
        return (
            self.count_active_threads_conduits()
            + self.count_active_threads_spell_indexes()
        )

    def enable_all(self) -> None:
        """
        Public API

        Open every registered gate (conduit + spell index).

        Contract:
            - Delegates to conduit and lineage enable-all operations.
            - No-op when both registries are empty.

        Returns:
            None.

        Raises:
            RuntimeError:
                If called after cleanup().
        """
        self.check_cleaned()
        self.enable_all_conduit_gates()
        self.enable_all_spell_index_gates()

    def disable_all(self) -> None:
        """
        Public API

        Close every registered gate (conduit + spell index).

        Contract:
            - Delegates to conduit and lineage disable-all operations.
            - No-op when both registries are empty.

        Returns:
            None.

        Raises:
            RuntimeError:
                If called after cleanup().
        """
        self.check_cleaned()
        self.disable_all_conduit_gates()
        self.disable_all_spell_index_gates()

