from threading import RLock
from typing import Optional, Any, Dict, Union, Set, Callable
# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import ISpellIndex, IChangeControlManager  # for identity / lineage
from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import RootResolutionBlueprint
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class ChangeControlManager(Cleanable):
    """
    High-level change/release tracker for an Aetheric Frame.

    This is *not* the hot-path resolution guard. It is the DevOps-facing layer
    that knows about:
      - which spell lineages (SpellIndex.id) have pending changes or promotions,
      - lightweight, structured metadata about those changes.

    It does not apply changes or run policies itself; it's a registry that
    higher-level tools (AI agents, DevOps flows, IncidentManager) can inspect
    and update.

    Internal state:
        _pending_changes:
            ConcurrentDict[str, ConcurrentDict[str, Any]]

        - Outer key  : SpellIndex.id (lineage id)
        - Inner dict : free-form metadata for that lineage's pending change
                       (e.g. "reason", "ticket_id", "workspace_id", etc.)
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_spell_system_states",
        "_pending_changes",
        "_component_of",
        "_dirty_spells",
        "_dirty_roots",
        "_monitor_active",
        "_revalidate_fn",
    ]

    def __init__(self, spell_system_states: "SpellSystemStates") -> None:
        if spell_system_states is None:
            raise ValueError("spell_system_states cannot be None")

        Cleanable.__init__(self)

        self._lock: RLock = RLock()
        self._spell_system_states: "SpellSystemStates" = spell_system_states

        # spell_index_id -> Dict[str, Any]
        self._pending_changes: Dict[str, Dict[str, Any]] = {}
        # spell_id (version) -> set[root_id]
        self._component_of: Dict[str, Set[str]] = {}
        self._dirty_spells: Set[str] = set()
        self._dirty_roots: Set[str] = set()
        self._monitor_active: bool = False
        self._revalidate_fn: Optional[Callable[[Set[str], Optional[CancellationEvent]], None]] = None
    # ----------------------------------------------------------------------
    # Cleanup
    # ----------------------------------------------------------------------
    def cleanup(self) -> None:
        """
        Idempotent cleanup.

        - Marks this manager as cleaned.
        - Cleans and nulls the internal ConcurrentDict.
        - Releases references to SpellSystemStates and lock.

        After this, the object must not be used.
        """
        if self._cleaned:
            return

        # Normal pattern: lock while mutating internal fields.
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True

            if self._pending_changes is not None:
                self._pending_changes.clear()
                self._pending_changes = None

            if self._component_of is not None:
                for roots in self._component_of.values():
                    roots.clear()
                self._component_of.clear()
                self._component_of = None

            if self._dirty_spells is not None:
                self._dirty_spells.clear()
                self._dirty_spells = None

            if self._dirty_roots is not None:
                self._dirty_roots.clear()
                self._dirty_roots = None

            self._monitor_active = False
            self._revalidate_fn = None

            # We do *not* own spell_system_states' lifecycle here; that will
            # be cleaned by the Aetheric Frame / DevOpsManager. We only drop
            # our reference so GC can do its job.
            self._spell_system_states = None

        # Drop the lock last.
        self._lock = None

    # ----------------------------------------------------------------------
    # Registration / updates
    # ----------------------------------------------------------------------
    def register_pending_change(
            self,
            spell_index: ISpellIndex,
            reason: str,
            metadata: Optional[
                Union[Dict[str, Any], Dict[str, Any]]
            ] = None,
    ) -> None:
        """
        Record that a given lineage has a pending change (mutation candidate,
        promotion proposal, config swap, etc.).

        This is *bookkeeping only* – it does not apply the change, it just
        surfaces it for DevOps / AI tooling.

        Args:
            spell_index:
                The SpellIndex for the lineage we're tracking.
            reason:
                Short, machine-/human-readable reason code
                (e.g. "mutation_candidate", "rebinding", "config_change").
            metadata:
                Optional free-form metadata. Can be a plain dict or a
                Dict; in both cases we wrap it into a new
                Dict instance so internal state is always nested
        """
        self.check_cleaned()
        if spell_index is None:
            raise ValueError("spell_index cannot be None")
        if not reason:
            raise ValueError("reason cannot be empty")

        index_id = spell_index.id

        # Wrap metadata into a ConcurrentDict without manual iteration here.
        # ConcurrentDict supports being constructed from any Mapping.
        details = metadata if metadata is not None else {}
        details["reason"] = reason

        with self._lock:
            # Last-write-wins semantics; we don't try to merge old/new metadata.
            self._pending_changes[index_id] = details

    # ----------------------------------------------------------------------
    # Introspection
    # ----------------------------------------------------------------------
    def get_pending_change(
            self,
            spell_index_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get a *snapshot* of the pending-change metadata for a specific lineage.

        Returns:
            A plain dict copy of the inner ConcurrentDict metadata if present,
            or None if no pending change exists for that lineage.
        """
        self.check_cleaned()
        if not spell_index_id:
            raise ValueError("spell_index_id cannot be empty")

        with self._lock:
            entry = self._pending_changes.get(spell_index_id)
            if entry is None:
                return None
            # Snapshot to plain dict for external consumption; this is
            # DevOps-side, not hot path.
            return dict(entry)

    def list_pending_changes(self) -> Dict[str, Dict[str, Any]]:
        """
        Return a snapshot of all pending changes:

            {
              spell_index_id: { ...metadata... },
              ...
            }

        This is intended for DevOps / AI tooling – not for hot-path use.
        """
        self.check_cleaned()
        snapshot: Dict[str, Dict[str, Any]] = {}
        with self._lock:
            for index_id, meta in self._pending_changes.items():
                snapshot[index_id] = dict(meta)
        return snapshot

    # ----------------------------------------------------------------------
    # Clearing
    # ----------------------------------------------------------------------
    def clear_pending_change(self, spell_index_id: str) -> None:
        """
        Remove the pending-change entry for the given lineage, if any.

        This is typically called after a release is either:
          - successfully applied, or
          - explicitly cancelled/abandoned.
        """
        self.check_cleaned()
        if not spell_index_id:
            raise ValueError("spell_index_id cannot be empty")

        with self._lock:
            # ConcurrentDict supports pop-like semantics via del / get+del
            if spell_index_id in self._pending_changes:
                del self._pending_changes[spell_index_id]

    # ----------------------------------------------------------------------
    # Change-control (component-of / dirty tracking)
    # ----------------------------------------------------------------------
    def set_revalidator(
            self,
            fn: Callable[[Set[str], Optional[CancellationEvent]], None],
    ) -> None:
        """
        Register a callable that performs revalidation for the supplied dirty roots.

        Signature: fn(dirty_roots: Set[str], cancel_event: Optional[CancellationEvent]) -> None
        """
        self.check_cleaned()
        if fn is None:
            raise ValueError("revalidator fn must not be None.")
        with self._lock:
            self._revalidate_fn = fn

    def rebuild_component_of(
            self,
            root_blueprints: Dict[str, RootResolutionBlueprint],
    ) -> None:
        """
        Rebuild the component-of index (spell_id -> root_ids) from deep root blueprints.
        """
        self.check_cleaned()
        if root_blueprints is None:
            raise ValueError("root_blueprints must not be None.")

        with self._lock:
            self._component_of.clear()
            for root_id, blueprint in root_blueprints.items():
                dag = blueprint.dag
                for node_id in dag.nodes.keys():
                    self._component_of.setdefault(node_id, set()).add(root_id)
                # Ensure root is present in its own set.
                self._component_of.setdefault(root_id, set()).add(root_id)

            self._dirty_spells.clear()
            self._dirty_roots.clear()
            self._monitor_active = False

    def notify_spell_changed(self, spell_id: str) -> None:
        """
        Mark a spell as changed and flag dependent roots as dirty.
        """
        self.check_cleaned()
        if not spell_id:
            raise ValueError("spell_id cannot be empty")

        with self._lock:
            self._dirty_spells.add(spell_id)
            affected_roots = self._component_of.get(spell_id, ())
            self._dirty_roots.update(affected_roots)
            self._monitor_active = True

    def notify_provider_changed(self, spell_id: str) -> None:
        """
        Alias for provider changes; currently identical to notify_spell_changed.
        """
        self.notify_spell_changed(spell_id)

    def revalidate_dirty_roots(self, cancel_event: Optional["CancellationEvent"] = None) -> None:
        """
        Invoke the registered revalidator for current dirty roots.

        On success, clears dirty flags; on failure, dirty sets remain.
        """
        self.check_cleaned()
        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()
        with self._lock:
            if not self._dirty_roots or self._revalidate_fn is None:
                return
            dirty_roots = set(self._dirty_roots)
        # Call outside the lock to avoid deadlocks.
        self._revalidate_fn(dirty_roots, cancel_event)
        with self._lock:
            self._dirty_roots.difference_update(dirty_roots)
            if not self._dirty_roots:
                self._dirty_spells.clear()
                self._monitor_active = False

    # ----------------------------------------------------------------------
    # Introspection helpers
    # ----------------------------------------------------------------------
    def is_root_dirty(self, root_id: str) -> bool:
        """
        Return True if the supplied root spell_id is currently marked dirty
        under change control and monitoring is active.
        """
        self.check_cleaned()
        if not root_id:
            return False
        with self._lock:
            if not self._monitor_active:
                return False
            return root_id in self._dirty_roots

    def describe(self) -> Dict[str, Any]:
        """
        Diagnostic snapshot of change-control state.
        """
        self.check_cleaned()
        with self._lock:
            return {
                "pending_changes": dict(self._pending_changes),
                "dirty_spells": set(self._dirty_spells),
                "dirty_roots": set(self._dirty_roots),
                "component_of": {k: set(v) for k, v in self._component_of.items()},
                "monitor_active": self._monitor_active,
                "revalidator_registered": self._revalidate_fn is not None,
            }
