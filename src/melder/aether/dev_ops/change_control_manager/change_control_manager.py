from __future__ import annotations

from threading import RLock
from typing import Optional, Any, Dict, Union

# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.data_structures.concurrent_dict import ConcurrentDict
from melder.utilities.interfaces.interfaces import ISpellIndex  # for identity / lineage


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

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_spell_system_states",
        "_pending_changes",
    ]

    def __init__(self, spell_system_states: "SpellSystemStates") -> None:
        if spell_system_states is None:
            raise ValueError("spell_system_states cannot be None")

        super().__init__()

        self._lock: RLock = RLock()
        self._spell_system_states: "SpellSystemStates" = spell_system_states

        # spell_index_id -> ConcurrentDict[str, Any]
        self._pending_changes: ConcurrentDict[str, ConcurrentDict[str, Any]]
        self._pending_changes = ConcurrentDict()
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
                self._pending_changes.cleanup()
                self._pending_changes = None

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
                Union[Dict[str, Any], ConcurrentDict[str, Any]]
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
                ConcurrentDict; in both cases we wrap it into a new
                ConcurrentDict instance so internal state is always nested
                ConcurrentDict -> ConcurrentDict.
        """
        self.check_cleaned()
        if spell_index is None:
            raise ValueError("spell_index cannot be None")
        if not reason:
            raise ValueError("reason cannot be empty")

        index_id = spell_index.id

        # Wrap metadata into a ConcurrentDict without manual iteration here.
        # ConcurrentDict supports being constructed from any Mapping.
        base = metadata if metadata is not None else {}
        details = ConcurrentDict(base)
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