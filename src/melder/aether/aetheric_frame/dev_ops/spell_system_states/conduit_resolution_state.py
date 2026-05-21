import threading
from typing import TYPE_CHECKING, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from mypy_extensions import mypyc_attr

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.aether.spellbook.spell_compiler.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.utilities.general_base.cleanable import Cleanable
if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import (
        SpellStateChangeReason,
    )
    from melder.aether.aetheric_frame.dev_ops.risk_manager.risk_manager import RiskManager


def _get_resolution_risk_manager_callback(
        risk_manager: Optional[RiskManager],
) -> Optional[Callable[[str, str, Optional[SpellValidity]], None]]:
    """
    Return the resolution-validity callback when the collaborator exposes it.

    Contract:
        - Accepts the current loose collaborator surface (`RiskManager | None`).
        - Returns a callable only when the collaborator exposes a callable
          `on_resolution_validity_change(...)` attribute.
        - Leaves plain objects and missing callbacks as `None`.
    """
    if risk_manager is None:
        return None
    callback = getattr(risk_manager, "on_resolution_validity_change", None)
    if not callable(callback):
        return None
    return callback

@mypyc_attr(native_class=True)
class ConduitResolutionState(Cleanable):
    """
    Per-conduit resolution validity container.

    This object tracks Phase 5-7 resolution validity for a single Conduit.
    It does not replace SpellSystemState; structural validity remains global.

    Identity
    --------
    - conduit_id:
        Unique identifier of the Conduit this state represents.

    Validity
    --------
    - spell validity:
        Per-spell resolution verdicts keyed by spell_id (version id).
    - root validity:
        Per-root resolution verdicts keyed by root_id (version id).

    Diagnostics
    -----------
    - diagnostics:
        System-level validation diagnostics scoped to this conduit.

    Dirty Tracking
    --------------
    - dirty:
        Indicates whether the resolution state has changed since the
        last successful validation.
    - last_validated_at:
        Timestamp (seconds) when the last successful resolution validation
        completed for this conduit.
    - last_change_reason:
        Optional SpellStateChangeReason describing the last change.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_conduit_id",
        "_lock",
        "_spell_validity",
        "_root_validity",
        "_diagnostics",
        "_dirty",
        "_last_validated_at",
        "_last_change_reason",
        "_initial_validity",
        "_risk_manager",
    ]

    def __init__(
            self,
            conduit_id: str,
            *,
            initial_validity: SpellValidity = SpellValidity.unknown,
    ) -> None:
        """
        Initialize a ConduitResolutionState.

        Args:
            conduit_id:
                Unique identifier of the conduit this state represents.
            initial_validity:
                Default validity returned when no explicit entry exists.
        Contract:
            - Starts with empty spell/root verdict maps and no diagnostics.
            - Starts clean; callers must explicitly mark or mutate the state
              before it reports pending validation work.
            - Uses `initial_validity` as the fallback verdict for unknown spell
              and root ids until concrete results are published.
            - Starts without a `RiskManager`; risk propagation is enabled later
              when the owning registry wires one in.

        Raises:
            ValueError:
                If conduit_id is empty or initial_validity is None.
        """
        super().__init__()

        if not conduit_id:
            raise ValueError("conduit_id cannot be empty.")
        if initial_validity is None:
            raise ValueError("initial_validity cannot be None.")

        self._conduit_id: str = conduit_id
        self._lock: threading.RLock = threading.RLock()
        self._spell_validity: Dict[str, SpellValidity] = {}
        self._root_validity: Dict[str, SpellValidity] = {}
        self._diagnostics: List[SystemDiagnostic] = []
        self._dirty: bool = False
        self._last_validated_at: Optional[float] = None
        self._last_change_reason: Optional[SpellStateChangeReason] = None
        self._initial_validity: SpellValidity = initial_validity
        self._risk_manager: Optional[RiskManager] = None

    # ------------------------------------------------------------------ #
    # Validity accessors                                                  #
    # ------------------------------------------------------------------ #
    def get_spell_validity(self, spell_id: str) -> Optional[SpellValidity]:
        """
        Get the resolution validity for a spell id.

        Args:
            spell_id:
                Versioned spell id to query.

        Returns:
            SpellValidity:
                The stored validity for the spell, or the initial_validity
                if no entry exists.
        """
        self.check_cleaned()
        if not spell_id:
            return None
        with self._lock:
            return self._spell_validity.get(spell_id, self._initial_validity)

    def snapshot_spell_validity(self) -> Dict[str, SpellValidity]:
        """
        Return a snapshot copy of per-spell resolution validity.

        Purpose:
            Provide a stable view of spell-level resolution validity for callers
            that need to clone or transfer state without mutating the source.
        Contract:
            - Returns a shallow copy; callers cannot mutate internal state.
            - Snapshot reflects the state at the time of call.
        Returns:
            Dict[str, SpellValidity]:
                Mapping of spell_id -> SpellValidity.
        Raises:
            RuntimeError: If this state has been cleaned.
        Threading:
            Acquires the internal lock while copying.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._spell_validity)

    def set_spell_validity(
            self,
            spell_id: str,
            validity: SpellValidity,
            *,
            change_reason: Optional[SpellStateChangeReason] = None,
    ) -> None:
        """
        Publish one spell-level resolution verdict for this conduit.

        Args:
            spell_id:
                Versioned spell id to update.
            validity:
                New validity to assign.
            change_reason:
                Optional reason describing the update.
        Contract:
            - Overwrites the stored verdict for the spell id.
            - Marks the conduit state dirty only when the effective verdict
              actually changes.
            - Forwards changed verdicts to the attached `RiskManager`, if any,
              so conduit-local risk stays aligned with the published state.
            - If the verdict is unchanged but `change_reason` is supplied, the
              change reason is still refreshed for later introspection.

        Raises:
            ValueError:
                If spell_id is empty or validity is None.
        """
        self.check_cleaned()
        if not spell_id:
            raise ValueError("spell_id cannot be empty.")
        if validity is None:
            raise ValueError("validity cannot be None.")

        changed = False
        with self._lock:
            had_entry = spell_id in self._spell_validity
            previous = self._spell_validity.get(spell_id, self._initial_validity)
            self._spell_validity[spell_id] = validity
            if (not had_entry) or (previous is not validity):
                self.mark_dirty(change_reason=change_reason)
                changed = True
            elif change_reason is not None:
                self._last_change_reason = change_reason
        callback = _get_resolution_risk_manager_callback(self._risk_manager)
        if changed and callback is not None:
            try:
                callback(self._conduit_id, spell_id, validity)
            except Exception:
                pass

    def bulk_set_spell_validity(
            self,
            validity_map: Mapping[str, SpellValidity],
            *,
            change_reason: Optional[SpellStateChangeReason] = None,
    ) -> None:
        """
        Publish a batch of spell-level resolution verdicts.

        Args:
            validity_map:
                Mapping of spell_id -> SpellValidity to apply.
            change_reason:
                Optional reason to store if any value changes.
        Contract:
            - Applies each supplied verdict into the owned spell-validity map.
            - Ignores empty spell ids and None validity entries rather than
              publishing partial garbage into the registry.
            - Marks the conduit state dirty once if any effective verdict
              changes.
            - Forwards only changed entries to the attached `RiskManager`.

        Raises:
            ValueError:
                If validity_map is None.
        """
        self.check_cleaned()
        if validity_map is None:
            raise ValueError("validity_map cannot be None.")

        changed = False
        changed_entries: List[Tuple[str, SpellValidity]] = []
        with self._lock:
            for spell_id, validity in validity_map.items():
                if not spell_id or validity is None:
                    continue
                previous = self._spell_validity.get(spell_id, self._initial_validity)
                if spell_id not in self._spell_validity or previous is not validity:
                    changed = True
                    changed_entries.append((spell_id, validity))
                self._spell_validity[spell_id] = validity
            if changed:
                self.mark_dirty(change_reason=change_reason)
            elif change_reason is not None:
                self._last_change_reason = change_reason
        callback = _get_resolution_risk_manager_callback(self._risk_manager)
        if changed_entries and callback is not None:
            for spell_id, validity in changed_entries:
                try:
                    callback(
                        self._conduit_id,
                        spell_id,
                        validity,
                    )
                except Exception:
                    pass

    def get_root_validity(self, root_id: str) -> Optional[SpellValidity]:
        """
        Get the resolution validity for a root spell id.

        Args:
            root_id:
                Root spell id to query.

        Returns:
            SpellValidity:
                The stored validity for the root, or the initial_validity
                if no entry exists.
        """
        self.check_cleaned()
        if not root_id:
            return None
        with self._lock:
            return self._root_validity.get(root_id, self._initial_validity)

    def snapshot_root_validity(self) -> Dict[str, SpellValidity]:
        """
        Return a snapshot copy of per-root resolution validity.

        Purpose:
            Provide a stable view of root-level resolution validity for callers
            that need to clone or transfer state without mutating the source.
        Contract:
            - Returns a shallow copy; callers cannot mutate internal state.
            - Snapshot reflects the state at the time of call.
        Returns:
            Dict[str, SpellValidity]:
                Mapping of root_id -> SpellValidity.
        Raises:
            RuntimeError: If this state has been cleaned.
        Threading:
            Acquires the internal lock while copying.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._root_validity)

    def set_root_validity(
            self,
            root_id: str,
            validity: SpellValidity,
            *,
            change_reason: Optional[SpellStateChangeReason] = None,
    ) -> None:
        """
        Publish one root-level resolution verdict for this conduit.

        Args:
            root_id:
                Root spell id to update.
            validity:
                New validity to assign.
            change_reason:
                Optional reason describing the update.
        Contract:
            - Overwrites the stored root verdict for the root id.
            - Marks the conduit state dirty only when the effective verdict
              actually changes.
            - Forwards changed root verdicts to the attached `RiskManager`, if
              any, using the same conduit-local propagation path as spell
              verdicts.
            - If the verdict is unchanged but `change_reason` is supplied, the
              change reason is still refreshed for later introspection.

        Raises:
            ValueError:
                If root_id is empty or validity is None.
        """
        self.check_cleaned()
        if not root_id:
            raise ValueError("root_id cannot be empty.")
        if validity is None:
            raise ValueError("validity cannot be None.")

        changed = False
        with self._lock:
            had_entry = root_id in self._root_validity
            previous = self._root_validity.get(root_id, self._initial_validity)
            self._root_validity[root_id] = validity
            if (not had_entry) or (previous is not validity):
                self.mark_dirty(change_reason=change_reason)
                changed = True
            elif change_reason is not None:
                self._last_change_reason = change_reason
        callback = _get_resolution_risk_manager_callback(self._risk_manager)
        if changed and callback is not None:
            try:
                callback(self._conduit_id, root_id, validity)
            except Exception:
                pass

    def bulk_set_root_validity(
            self,
            validity_map: Mapping[str, SpellValidity],
            *,
            change_reason: Optional[SpellStateChangeReason] = None,
    ) -> None:
        """
        Publish a batch of root-level resolution verdicts.

        Args:
            validity_map:
                Mapping of root_id -> SpellValidity to apply.
            change_reason:
                Optional reason to store if any value changes.
        Contract:
            - Applies each supplied verdict into the owned root-validity map.
            - Ignores empty root ids and None validity entries rather than
              polluting the registry with unusable keys.
            - Marks the conduit state dirty once if any effective verdict
              changes.
            - Forwards only changed entries to the attached `RiskManager`.

        Raises:
            ValueError:
                If validity_map is None.
        """
        self.check_cleaned()
        if validity_map is None:
            raise ValueError("validity_map cannot be None.")

        changed = False
        changed_entries: List[Tuple[str, SpellValidity]] = []
        with self._lock:
            for root_id, validity in validity_map.items():
                if not root_id or validity is None:
                    continue
                previous = self._root_validity.get(root_id, self._initial_validity)
                if root_id not in self._root_validity or previous is not validity:
                    changed = True
                    changed_entries.append((root_id, validity))
                self._root_validity[root_id] = validity
            if changed:
                self.mark_dirty(change_reason=change_reason)
            elif change_reason is not None:
                self._last_change_reason = change_reason
        callback = _get_resolution_risk_manager_callback(self._risk_manager)
        if changed_entries and callback is not None:
            for root_id, validity in changed_entries:
                try:
                    callback(
                        self._conduit_id,
                        root_id,
                        validity,
                    )
                except Exception:
                    pass

    # ------------------------------------------------------------------ #
    # Diagnostics                                                        #
    # ------------------------------------------------------------------ #
    def record_diagnostics(self, diagnostics: Sequence[SystemDiagnostic]) -> None:
        """
        Replace diagnostics if the incoming set differs by signature.

        Purpose:
            Persist conduit-scoped diagnostics while decoupling from external
            cleanup lifecycles (e.g., validation state teardown).
        Contract:
            - Stores cloned diagnostics so later cleanup of the input list
              does not invalidate this state.
            - Incoming diagnostics are never cleaned by this method.
            - If the incoming diagnostics are signature-identical to the
              current snapshot, this method leaves the state unchanged and does
              not create dirty churn.

        Args:
            diagnostics:
                New diagnostics to store.

        Raises:
            ValueError:
                If diagnostics is None.
        """
        self.check_cleaned()
        if diagnostics is None:
            raise ValueError("diagnostics cannot be None.")

        new_sig = self._diagnostics_signature(diagnostics)
        with self._lock:
            old_sig = self._diagnostics_signature(self._diagnostics)
            if new_sig == old_sig:
                return
            self._cleanup_diagnostics_locked()
            self._diagnostics = self._clone_diagnostics(diagnostics)
            self.mark_dirty()

    def clear_diagnostics(self) -> None:
        """
        Drop every owned diagnostic from this conduit state.

        Contract:
            - Cleans each stored diagnostic before discarding it.
            - Leaves the conduit state alive and reusable; only the diagnostic
              snapshot is reset.
            - Safe to call repeatedly when no diagnostics are stored.
        """
        self.check_cleaned()
        with self._lock:
            self._cleanup_diagnostics_locked()
            self._diagnostics = []

    def list_diagnostics(self) -> List[SystemDiagnostic]:
        """
        Return a snapshot list of stored diagnostics.

        Contract:
            - Returns a new list container so callers cannot mutate the
              internal diagnostics list directly.
            - The contained diagnostics remain the owned cloned instances held
              by this state.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._diagnostics)

    def has_errors(self) -> bool:
        """
        Return True if any stored diagnostic has ERROR severity.

        This is the quick "hard failure present?" probe used by higher-level
        validation surfaces when they do not need the full diagnostic payload.
        """
        self.check_cleaned()
        with self._lock:
            return any(
                diag.severity is SystemDiagnosticSeverity.ERROR
                for diag in self._diagnostics
            )

    def has_warnings(self) -> bool:
        """
        Return True if any stored diagnostic has WARNING severity.

        This is the quick "non-fatal issue present?" probe used by higher-level
        validation surfaces when they do not need the full diagnostic payload.
        """
        self.check_cleaned()
        with self._lock:
            return any(
                diag.severity is SystemDiagnosticSeverity.WARNING
                for diag in self._diagnostics
            )

    def is_dirty(self) -> bool:
        """
        Return True when resolution validity has changed since last validation.

        Purpose:
            Surface whether this conduit needs revalidation.
        Contract:
            - True indicates a change occurred after the last successful validation.
        Returns:
            bool:
                True if dirty, False otherwise.
        Raises:
            RuntimeError: If this state has been cleaned.
        Threading:
            Uses the current dirty flag without taking the lock.
        """
        self.check_cleaned()
        return bool(self._dirty)

    # ------------------------------------------------------------------ #
    # Dirty tracking                                                     #
    # ------------------------------------------------------------------ #
    def mark_dirty(
            self,
            change_reason: Optional[SpellStateChangeReason] = None,
    ) -> None:
        """
        Mark this resolution state as dirty.

        Args:
            change_reason:
                Optional reason describing why the state became dirty.
        Contract:
            - Sets the dirty flag immediately.
            - Preserves the previous `last_validated_at` timestamp so callers
              can still see when the last successful validation happened.
            - Updates `last_change_reason` only when an explicit reason is
              supplied.
        """
        self.check_cleaned()
        self._dirty = True
        if change_reason is not None:
            self._last_change_reason = change_reason

    def clear_dirty(self, validated_at: float) -> None:
        """
        Mark this resolution state as clean after validation.

        Args:
            validated_at:
                Timestamp (seconds) of successful validation.
        Contract:
            - Clears the dirty flag.
            - Records the validation timestamp as the new
              `last_validated_at` value.
            - Resets `last_change_reason` because the current state is now the
              validated baseline.
        """
        self.check_cleaned()
        self._dirty = False
        self._last_validated_at = validated_at
        self._last_change_reason = None

    def last_validated_at(self) -> Optional[float]:
        """
        Return the timestamp of the last successful validation.

        Returns:
            Optional[float]:
                Seconds timestamp for the most recent successful validation, or
                None if this conduit state has never been validated cleanly.
        """
        self.check_cleaned()
        return self._last_validated_at

    # ------------------------------------------------------------------ #
    # Cleanup                                                            #
    # ------------------------------------------------------------------ #
    def cleanup(self) -> None:
        """
        Deterministically tear down this resolution state.

        Contract:
            - Idempotent and lock-guarded.
            - Cleans owned diagnostic clones before dropping references.
            - Clears spell/root verdict maps and resets dirty/validation
              markers.
            - Nulls owned references so later callers fail through
              `check_cleaned()`.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return

            self._cleaned = True

            self._spell_validity.clear()
            self._root_validity.clear()
            self._cleanup_diagnostics_locked()
            self._dirty = False

            del self._spell_validity
            del self._root_validity
            del self._diagnostics
            del self._last_validated_at
            del self._last_change_reason
            del self._conduit_id
            del self._initial_validity
            del self._risk_manager
        del self._lock

    def _set_risk_manager(self, risk_manager: Optional[RiskManager]) -> None:
        """
        Attach or detach the `RiskManager` callback reference.

        This is a wiring helper used by the owning registry. It does not
        replay historical verdicts; it only controls where future changed
        verdicts are published.
        """
        self._risk_manager = risk_manager

    # ------------------------------------------------------------------ #
    # Internal helpers                                                   #
    # ------------------------------------------------------------------ #
    def _cleanup_diagnostics_locked(self) -> None:
        """
        Cleanup all owned diagnostics while the caller already holds `_lock`.

        Contract:
            - Cleans each owned diagnostic best-effort.
            - Clears the internal diagnostics list before returning.
            - Caller is responsible for lock discipline; this helper does not
              acquire `_lock` on its own.
        """
        if not self._diagnostics:
            return
        for diag in list(self._diagnostics):
            try:
                diag.cleanup()
            except Exception:
                pass
        self._diagnostics.clear()

    def _diagnostics_signature(
            self,
            diagnostics: Sequence[SystemDiagnostic],
    ) -> Tuple[Tuple[object, ...], ...]:
        """
        Build a stable signature for diagnostics comparison.

        The signature intentionally ignores object identity so repeated
        validation runs that produce equivalent diagnostics do not churn the
        conduit state or mark it dirty again unnecessarily.
        """
        signatures: List[Tuple[object, ...]] = []
        for diag in diagnostics:
            if diag is None:
                continue
            details = self._details_signature(diag.details)
            signatures.append(
                (
                    diag.code,
                    diag.message,
                    diag.severity,
                    diag.spell_id,
                    diag.root_id,
                    diag.source,
                    details,
                )
            )
        return tuple(signatures)

    def _clone_diagnostics(
            self,
            diagnostics: Sequence[SystemDiagnostic],
    ) -> List[SystemDiagnostic]:
        """
        Clone diagnostics to preserve them beyond external cleanup lifecycles.

        Purpose:
            Prevent shared diagnostics from being invalidated when upstream
            validation state objects are cleaned.
        Contract:
            - Returns a new list of SystemDiagnostic instances.
            - Copies all primary fields and details payloads.
            - Skips None entries.
        Args:
            diagnostics:
                Diagnostics to clone.
        Returns:
            List[SystemDiagnostic]:
                Cloned diagnostics with independent lifecycle ownership.
        """
        clones: List[SystemDiagnostic] = []
        for diag in diagnostics:
            if diag is None:
                continue
            clones.append(
                SystemDiagnostic(
                    code=diag.code,
                    message=diag.message,
                    severity=diag.severity,
                    spell_id=diag.spell_id,
                    root_id=diag.root_id,
                    source=diag.source,
                    details=diag.details,
                )
            )
        return clones

    def _details_signature(
            self,
            details: Optional[Dict[str, object]],
    ) -> Optional[Tuple[Tuple[str, str], ...]]:
        """
        Normalize diagnostic details into a stable signature tuple.

        Contract:
            - Returns None when the diagnostic carries no details payload.
            - Sorts keys so equivalent dictionaries compare identically.
            - Falls back to `"<unrepr>"` when a detail value cannot be safely
              represented.
        """
        if details is None:
            return None
        items = []
        for key in sorted(details.keys()):
            try:
                value_repr = repr(details[key])
            except Exception:
                value_repr = "<unrepr>"
            items.append((str(key), value_repr))
        return tuple(items)
