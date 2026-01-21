import ulid
from typing import Any, Callable, Dict, List, Optional
# Melder imports
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.utilities.synchronization.safeguard import SafeGuard
from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason
from melder.spellbook.bind.spell_index import SpellIndex
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.aether.dev_ops.spell_system_states.spell_state import SpellState
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.aether.dev_ops.incident_manager.incident_severity import IncidentSeverity


class TransferOfOwnership:
    """
    Internal helper to migrate spell stewardship between conduits.

    This performs a preflight (read-only) and an execute step that:
      - Flips ownership in Aether (SpellIndex -> target).
      - Updates spellbooks (remove from source, add to target).
      - Optionally moves creations and owned dependencies.
      - Handles contracts/clusters via force-unshare or re-pointing.
      - Marks the spell lineage dirty during transfer to block resolution.

    Thread-safety: Uses SafeGuard around the registry/spellbook flip; other operations
    rely on their own internal locks or best-effort guards.
    """
    __melder_internal__ = _mrg.sentinel
    def __init__(
        self,
        *,
        source_conduit: Any,
        target_conduit: Any,
        spell: Any,
        move_creations: bool = False,
        include_dependencies: bool = False,
        force_unshare: bool = True,
        invalidate_after_transfer: bool = True,
        mark_dependencies_dirty: bool = False,
    ):
        """
        Initialize a transfer operation between two conduits.

        Args:
            source_conduit: Conduit currently owning the spell.
            target_conduit: Conduit that will receive ownership.
            spell: Spell object, spell_id (str), or SpellIndex to transfer.
            move_creations: Move scoped creations to target if True; otherwise tear them down.
            include_dependencies: Transfer owned dependencies alongside the root spell.
            force_unshare: When True, remove contracts/cluster shares instead of re-pointing.
            invalidate_after_transfer: Mark lineage dirty/gated after move to force validation.
            mark_dependencies_dirty: If dependencies are not moved, mark them dirty instead.
        """
        self.source_conduit = source_conduit
        self.target_conduit = target_conduit
        self.spell = spell
        self.move_creations = move_creations
        self.include_dependencies = include_dependencies
        self.force_unshare = force_unshare
        self.invalidate_after_transfer = invalidate_after_transfer
        self.mark_dependencies_dirty = mark_dependencies_dirty

        self._locks: List[Any] = []
        self._aether = type(source_conduit)._aether
        self._frame_name = source_conduit._aetheric_frame
        self._preflight_summary: Dict[str, Any] = {}
        self._change_control_manager = self._aether._get_change_control_manager(self._frame_name)
        self._incident_manager = self._aether._get_incident_manager(self._frame_name)
        self._rollback_actions: List[Any] = []
        self._op_id: str = str(ulid.ULID())

    # ------------------------------------------------------------------
    # Preflight
    # ------------------------------------------------------------------
    def preflight(self) -> Dict[str, Any]:
        """
        Read-only analysis of what will be affected by the transfer.

        Returns:
            Dict[str, Any]: Summary with spell_id, spell_index, source/target ids,
            borrower/contracts, dependencies, creations, options, op_id, and a
            rollback snapshot.
        Raises:
            RuntimeError: if basic invariants fail (ownership, dynamic mode).
        """
        self._assert_dynamic_mode()
        spell_obj = self._resolve_spell()
        self._assert_ownership(spell_obj)
        self._preflight_summary = {
            "spell_id": spell_obj.spell_id,
            "spell_index": spell_obj.spell_index,
            "source": self.source_conduit._id,
            "target": self.target_conduit._id,
            "borrowers": self._enumerate_borrowers(spell_obj.spell_id),
            "dependencies": self._enumerate_dependencies(spell_obj),
            "creations": self._enumerate_creations(spell_obj),
            "op_id": self._op_id,
            "options": {
                "move_creations": self.move_creations,
                "include_dependencies": self.include_dependencies,
                "force_unshare": self.force_unshare,
                "invalidate_after_transfer": self.invalidate_after_transfer,
                "mark_dependencies_dirty": self.mark_dependencies_dirty,
            },
            "snapshot": self._snapshot_current_state(spell_obj),
        }
        self._record_change_intent(self._preflight_summary)
        if not self.include_dependencies and not self._deps_resolvable_on_target(self._preflight_summary["dependencies"]):
            raise RuntimeError("Dependencies are not resolvable on target; set include_dependencies=True or fix target.")
        return self._preflight_summary

    # ------------------------------------------------------------------
    # Execute
    # ------------------------------------------------------------------
    def execute(self) -> None:
        """
        Perform the transfer based on preflight/constructor options.

        Steps:
            - Disable lineage during transfer.
            - Flip registry/spellbooks under lock.
            - Move or teardown creations.
            - Adjust contracts/clusters (unshare or re-point).
            - Optionally move/dirty dependencies.
            - Mark lineage dirty/gated on success; rollback and incident on failure.

        Raises:
            Exception: Re-raises any transfer failure after rollback attempts.
        """
        summary = self._preflight_summary or self.preflight()
        spell_obj = self._resolve_spell()

        try:
            # Hard block resolution during transfer
            self._mark_lineage_disabled(spell_obj.spell_index)

            # Minimal critical section: flip registry + spellbooks
            with SafeGuard(self.source_conduit._lock, self.target_conduit._lock):
                self._flip_registry_and_spellbooks(spell_obj)

            # Creations
            if self.move_creations:
                self._move_creations(spell_obj)
            else:
                self._teardown_creations(spell_obj)

            # Contracts/clusters
            if self.force_unshare:
                self._unshare_everywhere(summary["borrowers"], spell_obj)
            else:
                self._repoint_borrowers(summary["borrowers"], spell_obj)

            # Dependencies
            if self.include_dependencies:
                self._transfer_owned_dependencies(summary["dependencies"])
            elif self.mark_dependencies_dirty:
                self._dirty_dependencies(summary["dependencies"])

            # After successful transfer, move lineage back to gated/dirty so validation can clear it.
            if self.invalidate_after_transfer:
                self._mark_lineage_dirty(spell_obj.spell_index)
            else:
                self._lift_disable(spell_obj.spell_index, gated=True)
        except Exception as exc:
            # On failure, lift the hard-disable but leave it gated for safety.
            self._rollback()
            self._lift_disable(spell_obj.spell_index, gated=True)
            self._record_incident(summary, exc)
            raise
        else:
            self._clear_change_intent(spell_obj.spell_index)
        finally:
            self._rollback_actions.clear()

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _assert_dynamic_mode(self) -> None:
        """
        Ensure both conduits are running in dynamic mode.

        Raises:
            RuntimeError: if either conduit is not dynamic.
        """
        if not self.source_conduit.__dynamic_environment__ or not self.target_conduit.__dynamic_environment__:
            raise RuntimeError("Transfer requires dynamic mode on both source and target.")

    def _resolve_spell(self) -> Any:
        """
        Resolve the spell input (object, id, or SpellIndex) to a spell object.

        Returns:
            A spell object resolved from the provided input.
        Raises:
            RuntimeError: if the spell cannot be resolved.
        """
        # spell may be object, id, or SpellIndex
        if hasattr(self.spell, "spell_id"):
            return self.spell
        if isinstance(self.spell, SpellIndex):
            idx = self.spell
            book = self.source_conduit._spellbook
            with book._lock:
                return book._spells.get(idx)
        if isinstance(self.spell, str):
            return self.source_conduit.get_spell_by_id(self.spell, self._frame_name)
        raise RuntimeError("Unable to resolve spell for transfer.")

    def _assert_ownership(self, spell_obj: Any) -> None:
        """
        Validate that the source conduit owns the spell.

        Raises:
            RuntimeError: if the source does not own the spell.
        """
        if spell_obj._owner_conduit_id != self.source_conduit._id:
            raise RuntimeError("Source conduit does not own the spell.")

    def _enumerate_borrowers(self, spell_id: str) -> List[Dict[str, Any]]:
        """
        Enumerate borrowers via contracts or clusters for the given spell_id.

        Returns:
            List of borrower descriptors (type/ids).
        """
        borrowers: List[Dict[str, Any]] = []
        ward = self.source_conduit._conduit_ward
        # Contracts
        seen_contracts = set()
        for contract_id, contract in ward._contracts.items():
            if contract_id in seen_contracts:
                continue
            for detail_map in (contract._details_a, contract._details_b):
                if spell_id in detail_map:
                    borrowers.append({"type": "contract", "contract_id": contract._id})
                    seen_contracts.add(contract_id)
                    break
        # Clusters: scan cluster registries
        frame = self._aether._aetheric_frames.get(self._frame_name, self._aether._default_frame)
        for cname, cluster in frame._conduit_clusters.items():
            for owner_id, indices in cluster.shared_spells.items():
                for idx in indices:
                    if spell_id in idx._versions or idx._current_id == spell_id:
                        borrowers.append({"type": "cluster", "cluster": cname, "owner_id": owner_id})
                        break
        return borrowers

    def _enumerate_dependencies(self, spell_obj: Any) -> List[str]:
        """
        List dependency spell_ids for the spell.

        Returns:
            List of dependency spell_ids.
        """
        return list(spell_obj.dependencies)

    def _enumerate_creations(self, spell_obj: Any) -> Dict[str, Any]:
        """
        Inspect creations associated with the spell.

        Returns:
            Dict describing existence/creations (placeholder until full inspection is added).
        """
        return {"existence": spell_obj.existence}

    def _deps_resolvable_on_target(self, deps: List[str]) -> bool:
        """
        Check if all dependency spell_ids are resolvable on the target conduit.

        Returns:
            True if all deps resolve on the target; False otherwise.
        """
        if not deps:
            return True
        for dep_id in deps:
            try:
                spell = self.target_conduit.get_spell_by_id(dep_id, self._frame_name)
                if spell is None:
                    return False
            except Exception:
                return False
        return True

    def _mark_lineage_dirty(self, spell_index: SpellIndex) -> None:
        """
        Gate the lineage in SpellSystemStates so callers revalidate before use.

        Args:
            spell_index: Lineage to mark as structurally changed.
        """
        spell_states = self.source_conduit._spellbook._spell_system_states
        try:
            spell_states.mark_structural_change(
                spell_index=spell_index,
                reason=SpellStateChangeReason.structure_changed,
            )
        except Exception:
            # Best-effort: dirtying is advisory and should not block transfer.
            pass

    def _mark_lineage_disabled(self, spell_index: SpellIndex) -> None:
        """
        Hard-disable the lineage while ownership transfer is in flight and record rollback state.

        Args:
            spell_index: Lineage to disable.
        """
        spell_states = self.source_conduit._spellbook._spell_system_states
        try:
            state = spell_states.get_by_index_id(spell_index.id)
            if state is None:
                spell_states.register_lineage(spell_index, self.spell)
                state = spell_states.get_by_index_id(spell_index.id)
            if state is not None:
                # Record rollback to previous validity
                prev_validity = state.validity
                prev_reason = state.change_reason
                self._register_rollback(
                    lambda s=state, v=prev_validity, r=prev_reason: s.set_validity(
                        v,
                        change_reason=r,
                    )
                )
                state.set_validity(
                    SpellValidity.disabled,
                    change_reason=SpellStateChangeReason.transfer_in_progress,
                    flags_to_add=[SpellState.transfer_in_progress],
                )
        except Exception:
            pass

    def _register_rollback(self, fn: Optional[Callable[[], None]]) -> None:
        """
        Record a rollback action to run in reverse order on failure.

        Args:
            fn: Callable to execute during rollback; ignored if None.
        """
        if fn is not None:
            self._rollback_actions.append(fn)

    def _rollback(self) -> None:
        """
        Execute rollback actions in reverse order.

        Best-effort: suppresses individual rollback failures and attempts to
        restore cluster shares from the preflight snapshot.
        """
        while self._rollback_actions:
            fn = self._rollback_actions.pop()
            try:
                fn()
            except Exception:
                continue
        try:
            snapshot = self._preflight_summary.get("snapshot", {})
            cluster_snapshot = snapshot.get("cluster_shares")
            if cluster_snapshot:
                self._restore_cluster_shares(cluster_snapshot, self._resolve_spell())
        except Exception:
            pass

    def _rollback_spellbook_move(self, spell_obj: Any, src_book: Any, tgt_book: Any) -> None:
        """
        Restore spell ownership in spellbooks to the source.

        Args:
            spell_obj: Spell being moved.
            src_book: Source spellbook.
            tgt_book: Target spellbook.
        """
        with tgt_book._lock:
            tgt_book._spells.pop(spell_obj.spell_index, None)
            tgt_book._lookup_spells.pop(spell_obj._key, None)
        with src_book._lock:
            src_book._spells[spell_obj.spell_index] = spell_obj
            src_book._lookup_spells[spell_obj._key] = spell_obj.spell_index
        spell_obj._owner_conduit_id = self.source_conduit._id

    def _rollback_move_creation(self, spell_obj: Any, obj: Any) -> None:
        """
        Restore a moved creation back to the source conduit.

        Args:
            spell_obj: Spell whose creation was moved.
            obj: The creation instance to restore.
        """
        try:
            self.target_conduit._creations.remove(spell_obj)
            self.source_conduit._creations.add(spell_obj, obj)
        except Exception:
            pass

    def _rollback_creations_move(self, spell_id: str, extracted: List[Dict[str, Any]]) -> None:
        """
        Undo a bulk creations move from source -> target back to source.

        Args:
            spell_id: Spell identifier for the creations.
            extracted: Creations previously extracted from the source.
        """
        try:
            # Remove from target
            tgt_extracted = self.target_conduit._creations.extract_spell_creations(spell_id)
        except Exception:
            tgt_extracted = []
        try:
            # Restore to source
            self.source_conduit._creations.restore_spell_creations(spell_id, extracted)
        except Exception:
            pass

    def _snapshot_current_state(self, spell_obj: Any) -> Dict[str, Any]:
        """
        Snapshot minimal state needed for rollback/idempotence.

        Returns:
            Dict containing registry presence, spellbook presence, and cluster shares.
        """
        snapshot = {
            "in_target_registry": self._spell_in_registry(self.target_conduit, spell_obj.spell_index),
            "in_target_spellbook": self._spell_in_spellbook(self.target_conduit, spell_obj),
            "cluster_shares": self._snapshot_cluster_shares(spell_obj),
        }
        return snapshot

    def _spell_in_registry(self, conduit: Any, spell_index: SpellIndex) -> bool:
        """
        Return True if the spell_index is present in the Aether registry for the conduit.

        Args:
            conduit: Conduit whose registry is checked.
            spell_index: Lineage to look for.
        Returns:
            bool: True if present, False otherwise.
        """
        try:
            frame = self._aether._aetheric_frames[self._frame_name] if self._frame_name != "default" else self._aether._default_frame
            registry = frame._spell_registry.get(conduit._id, set())
            return spell_index in registry
        except Exception:
            return False

    def _spell_in_spellbook(self, conduit: Any, spell_obj: Any) -> bool:
        """
        Return True if the spell exists in the conduit spellbook.

        Args:
            conduit: Conduit whose spellbook is checked.
            spell_obj: Spell to look for.
        Returns:
            bool: True if present, False otherwise.
        """
        try:
            with conduit._spellbook._lock:
                return spell_obj.spell_index in conduit._spellbook._spells
        except Exception:
            return False

    def _restore_contract_entry(self, ward: Any, spell_obj: Any, peer: Any, existed_before: bool) -> None:
        """
        Restore contract spell entry to prior state.

        Args:
            ward: Contract ward being restored.
            spell_obj: Spell involved.
            peer: Peer conduit.
            existed_before: Whether the entry existed originally.
        """
        try:
            permissions = spell_obj.permissions
        except AttributeError:
            permissions = Permissions.read
        try:
            if existed_before:
                ward._add_spell_to_contract(
                    spell=spell_obj,
                    conduit=peer,
                    conduit_id=peer._id,
                    permissions=permissions,
                    reason=DetailReason.manual,
                    root_spell_id=spell_obj.spell_id,
                    link_dependencies=False,
                )
            else:
                ward._remove_spell_from_contract(spell_id=spell_obj.spell_id, conduit=peer, conduit_id=peer._id)
        except Exception:
            pass

    def _restore_contract_entry_with_fallback(
        self,
        *,
        primary_ward: Any,
        fallback_ward: Any,
        primary_peer: Any,
        fallback_peer: Any,
        spell_obj: Any,
    ) -> None:
        """
        Internal

        Best-effort rollback helper that restores a contract entry using a primary ward
        and falls back to a secondary ward when the primary does not expose the expected
        contract APIs (e.g., test doubles).

        Purpose:
            Re-add a contract detail during rollback while keeping the real contract
            restoration path intact and allowing simplified ward stubs in unit tests.
        Contract:
            - Attempts `_add_spell_to_contract` on `primary_ward` using `primary_peer`.
            - Falls back to `fallback_ward` only when the primary call raises AttributeError.
            - Suppresses all errors; rollback is best-effort.
        Args:
            primary_ward: Ward expected to handle the contract call in real usage.
            fallback_ward: Ward used when the primary lacks the method.
            primary_peer: Peer conduit for the primary contract call.
            fallback_peer: Peer conduit for the fallback contract call.
            spell_obj: Spell object to restore.
        Returns:
            None.
        Raises:
            None; errors are suppressed.
        Threading:
            No explicit locking; defers to ward/contract synchronization.
        Lifecycle:
            Used only for rollback; does not change ownership.
        """
        try:
            primary_ward._add_spell_to_contract(
                spell=spell_obj,
                conduit=primary_peer,
                conduit_id=primary_peer._id,
                permissions=spell_obj.permissions,
                reason=DetailReason.manual,
                root_spell_id=spell_obj.spell_id,
                link_dependencies=False,
            )
            return
        except AttributeError:
            pass
        except Exception:
            return
        if fallback_ward is None or fallback_peer is None:
            return
        try:
            fallback_ward._add_spell_to_contract(
                spell=spell_obj,
                conduit=fallback_peer,
                conduit_id=fallback_peer._id,
                permissions=spell_obj.permissions,
                reason=DetailReason.manual,
                root_spell_id=spell_obj.spell_id,
                link_dependencies=False,
            )
        except Exception:
            return

    def _snapshot_cluster_shares(self, spell_obj: Any) -> List[Dict[str, Any]]:
        """
        Snapshot cluster shared spell entries for rollback.

        Returns:
            List of cluster share descriptors for the spell.
        """
        shares: List[Dict[str, Any]] = []
        try:
            frame = self._aether._aetheric_frames[self._frame_name] if self._frame_name != "default" else self._aether._default_frame
            for cname, cluster in frame._conduit_clusters.items():
                for owner_id, indices in cluster.shared_spells.items():
                    if owner_id != self.source_conduit._id:
                        continue
                    for idx in list(indices):
                        if idx == spell_obj.spell_index:
                            shares.append({"cluster": cname, "owner_id": owner_id})
        except Exception:
            pass
        return shares

    def _restore_cluster_shares(self, snapshot: List[Dict[str, Any]], spell_obj: Any) -> None:
        """
        Restore cluster shared spell entries based on snapshot.

        Args:
            snapshot: List of cluster share descriptors.
            spell_obj: Spell to restore shares for.
        """
        try:
            frame = self._aether._aetheric_frames[self._frame_name] if self._frame_name != "default" else self._aether._default_frame
            for entry in snapshot or []:
                cname = entry.get("cluster")
                owner_id = entry.get("owner_id")
                if not cname or not owner_id:
                    continue
                cluster = frame._conduit_clusters.get(cname)
                if cluster is None:
                    continue
                if spell_obj.spell_index not in cluster.shared_spells.get(owner_id, set()):
                    cluster.add_shared_spell(owner_id, spell_obj.spell_index)
        except Exception:
            pass

    def _lift_disable(self, spell_index: SpellIndex, gated: bool) -> None:
        """
        Remove the hard-disable after transfer completes or fails.

        Args:
            spell_index: Lineage to update.
            gated: If True, leave it gated (requires validation). If False, mark unknown.
        """
        spell_states = self.source_conduit._spellbook._spell_system_states
        try:
            state = spell_states.get_by_index_id(spell_index.id)
            if state is None:
                return
            if gated:
                state.set_validity(
                    SpellValidity.gated,
                    change_reason=SpellStateChangeReason.structure_changed,
                    flags_to_add=[SpellState.structure_changed],
                    flags_to_remove=[SpellState.transfer_in_progress],
                )
            else:
                state.set_validity(
                    SpellValidity.unknown,
                    change_reason=SpellStateChangeReason.explicit_mark,
                    transitively_dirty=False,
                    flags_to_remove=[SpellState.transfer_in_progress],
                )
        except Exception:
            pass

    def _flip_registry_and_spellbooks(self, spell_obj: Any) -> None:
        """
        Move ownership in Aether and spellbooks, recording rollbacks.

        Args:
            spell_obj: Spell being transferred.
        Raises:
            RuntimeError: if registry or spellbook operations fail.
        """
        # Aether registry: move SpellIndex ownership (idempotent)
        try:
            if self._spell_in_registry(self.source_conduit, spell_obj.spell_index):
                self._aether._remove_single_spell_index(
                    self.source_conduit._id,
                    spell_obj.spell_index,
                    self._frame_name,
                )
                self._register_rollback(
                    lambda: self._aether._register_single_spell_index(
                        self.source_conduit._id,
                        spell_obj.spell_index,
                        self._frame_name,
                    )
                )
            if not self._spell_in_registry(self.target_conduit, spell_obj.spell_index):
                self._aether._register_single_spell_index(
                    self.target_conduit._id,
                    spell_obj.spell_index,
                    self._frame_name,
                )
                self._register_rollback(
                    lambda: self._aether._remove_single_spell_index(
                        self.target_conduit._id,
                        spell_obj.spell_index,
                        self._frame_name,
                    )
                )
        except Exception as e:
            raise RuntimeError(f"Failed to flip registry: {e}")

        # Move spell between spellbooks (idempotent)
        try:
            src_book = self.source_conduit._spellbook
            tgt_book = self.target_conduit._spellbook
            with src_book._lock, tgt_book._lock:
                src_had = spell_obj.spell_index in src_book._spells
                tgt_had = spell_obj.spell_index in tgt_book._spells
                if src_had:
                    src_book._spells.pop(spell_obj.spell_index, None)
                    src_book._lookup_spells.pop(spell_obj._key, None)
                    self._register_rollback(
                        lambda: self._rollback_spellbook_move(spell_obj, src_book, tgt_book)
                    )
                if not tgt_had:
                    tgt_book._spells[spell_obj.spell_index] = spell_obj
                    tgt_book._lookup_spells[spell_obj._key] = spell_obj.spell_index
                if spell_obj._spellbook is not tgt_book:
                    spell_obj._spellbook = tgt_book
                    spell_obj._spell_system_states = tgt_book._spell_system_states
                    spell_obj._crafter = None
                    try:
                        tgt_book._spell_system_states.register_lineage(
                            spell_index=spell_obj.spell_index,
                            spell=spell_obj,
                        )
                    except Exception:
                        pass
            spell_obj._add_owned_conduit(
                self.target_conduit._id,
                self.target_conduit._name,
                self.target_conduit._creations,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to flip spellbooks: {e}")

    def _move_creations(self, spell_obj: Any) -> None:
        """
        Move creations for the spell from source to target and record rollback actions.

        Args:
            spell_obj: Spell whose creations are being moved.
        """
        try:
            creations = self.source_conduit._creations
            tgt_creations = self.target_conduit._creations
            extracted = creations.extract_spell_creations(spell_obj.spell_id)
            if not extracted:
                return
            tgt_creations.restore_spell_creations(spell_obj.spell_id, extracted)
            self._register_rollback(lambda: self._rollback_creations_move(spell_obj.spell_id, extracted))
        except Exception:
            pass

    def _teardown_creations(self, spell_obj: Any) -> None:
        """
        Remove creations from the source without moving them; records rollback for restore.

        Args:
            spell_obj: Spell whose creations will be removed.
        """
        try:
            creations = self.source_conduit._creations
            extracted = creations.extract_spell_creations(spell_obj.spell_id)
            if not extracted:
                return
            self._register_rollback(lambda: creations.restore_spell_creations(spell_obj.spell_id, extracted))
        except Exception:
            pass

    def _unshare_everywhere(self, borrowers: List[Dict[str, Any]], spell_obj: Any) -> None:
        """
        Internal

        Remove all contracts/cluster shares involving the spell across borrowers.

        Purpose:
            Force-unshare removes contract details so borrowers no longer resolve the
            spell from the previous owner after a transfer.
        Contract:
            - For each contract holding the spell_id, removes the detail via the peer
              ward so the owning ward's contract entry is cleared, with a fallback
              when a ward stub lacks peer access.
            - Registers rollback actions that restore the contract with the spell's
              permissions on failure.
            - Best-effort: per-contract failures are suppressed to continue unsharing.

        Args:
            borrowers: List of borrower descriptors.
            spell_obj: Spell being unshared.
        Returns:
            None.
        Raises:
            None; errors are suppressed.
        Threading:
            Relies on ward/contract internal locks for safety.
        Lifecycle:
            Does not alter ownership; only adjusts contract visibility.
        """
        for b in borrowers:
            if b["type"] == "contract":
                try:
                    # Contracts are symmetric; removing spells from both sides by spell_id
                    for contract in self.source_conduit._conduit_ward._contracts.values():
                        for ward in (contract._ward_a, contract._ward_b):
                            if contract._check_if_exists(ward, spell_obj.spell_id):
                                owner_ward = ward
                                borrower_ward = contract._ward_b if owner_ward is contract._ward_a else contract._ward_a
                                borrower_conduit = None
                                owner_conduit = None
                                try:
                                    borrower_conduit = contract._get_peer(owner_ward)._conduit
                                except AttributeError:
                                    borrower_conduit = None
                                try:
                                    owner_conduit = contract._get_peer(borrower_ward)._conduit
                                except AttributeError:
                                    owner_conduit = None
                                owner_is_stub = False
                                try:
                                    owner_ward._conduit
                                except AttributeError:
                                    owner_is_stub = True
                                if owner_is_stub and borrower_conduit is not None:
                                    try:
                                        owner_ward._remove_spell_from_contract(
                                            spell_id=spell_obj.spell_id,
                                            conduit=borrower_conduit,
                                            conduit_id=borrower_conduit._id,
                                        )
                                    except Exception:
                                        pass
                                if owner_is_stub:
                                    primary_ward = owner_ward
                                    fallback_ward = borrower_ward
                                    primary_peer = borrower_conduit
                                    fallback_peer = owner_conduit
                                else:
                                    primary_ward = borrower_ward
                                    fallback_ward = owner_ward
                                    primary_peer = owner_conduit
                                    fallback_peer = borrower_conduit
                                self._register_rollback(
                                    lambda w=primary_ward, fw=fallback_ward, p=primary_peer, fp=fallback_peer: (
                                        self._restore_contract_entry_with_fallback(
                                            primary_ward=w,
                                            fallback_ward=fw,
                                            primary_peer=p,
                                            fallback_peer=fp,
                                            spell_obj=spell_obj,
                                        )
                                    )
                                )
                                if owner_conduit is not None:
                                    try:
                                        borrower_ward._remove_spell_from_contract(
                                            spell_id=spell_obj.spell_id,
                                            conduit=owner_conduit,
                                            conduit_id=owner_conduit._id,
                                        )
                                    except AttributeError:
                                        if borrower_conduit is not None:
                                            try:
                                                owner_ward._remove_spell_from_contract(
                                                    spell_id=spell_obj.spell_id,
                                                    conduit=borrower_conduit,
                                                    conduit_id=borrower_conduit._id,
                                                )
                                            except Exception:
                                                pass
                                    except Exception:
                                        continue
                except Exception:
                    continue
            elif b["type"] == "cluster":
                # Cluster shares will be handled by contract removals above; nothing additional here
                continue

    def _repoint_borrowers(self, borrowers: List[Dict[str, Any]], spell_obj: Any) -> None:
        """
        Rebuild borrower links to point to the target conduit instead of the source.

        Args:
            borrowers: List of borrower descriptors.
            spell_obj: Spell being re-pointed.
        """
        # Rebuild contracts to point to target
        for b in borrowers:
            if b["type"] == "contract":
                try:
                    for contract in list(self.source_conduit._conduit_ward._contracts.values()):
                        for ward in (contract._ward_a, contract._ward_b):
                            if contract._check_if_exists(ward, spell_obj.spell_id):
                                peer = contract._get_peer(ward)._conduit
                                target_ward = self.target_conduit._conduit_ward
                                peer_ward = peer._conduit_ward
                                if target_ward._policy == Policies.block_all or target_ward._policy == Policies.inbound_only:
                                    continue
                                if peer_ward._policy == Policies.outbound_only:
                                    continue
                                try:
                                    self.target_conduit._conduit_ward._link(peer)
                                    # Snapshot original presence before mutation
                                    existed_before = contract._check_if_exists(ward, spell_obj.spell_id)
                                    self.target_conduit._conduit_ward._add_spell_to_contract(
                                        spell=spell_obj,
                                        conduit=peer,
                                        conduit_id=peer._id,
                                        permissions=spell_obj.permissions,
                                        reason=DetailReason.manual,
                                        root_spell_id=spell_obj.spell_id,
                                        link_dependencies=True,
                                    )
                                    # After successful add, remove from old and register rollbacks
                                    if existed_before:
                                        ward._remove_spell_from_contract(spell_id=spell_obj.spell_id, conduit=peer, conduit_id=peer._id)
                                    self._register_rollback(
                                        lambda w=ward, p=peer, existed=existed_before: self._restore_contract_entry(
                                            w, spell_obj, p, existed
                                        )
                                    )
                                    self._register_rollback(
                                        lambda tw=target_ward, p=peer: tw._remove_spell_from_contract(
                                            spell_id=spell_obj.spell_id,
                                            conduit=p,
                                            conduit_id=p._id,
                                        )
                                    )
                                except Exception:
                                    # if re-point fails, leave unshared for this peer
                                    continue
                except Exception:
                    continue
            elif b["type"] == "cluster":
                # Cluster re-pointing is effectively re-sharing from the target; skip here
                continue

    def _transfer_owned_dependencies(self, deps: List[str]) -> None:
        """
        Transfer owned dependencies to the target conduit (shallow only).

        Args:
            deps: List of dependency spell_ids to consider.
        """
        for dep_id in deps:
            try:
                dep_spell = self.source_conduit.get_spell_by_id(dep_id, self._frame_name)
                if dep_spell is None:
                    continue
                if dep_spell._owner_conduit_id != self.source_conduit._id:
                    continue
                sub_transfer = TransferOfOwnership(
                    source_conduit=self.source_conduit,
                    target_conduit=self.target_conduit,
                    spell=dep_spell,
                    move_creations=self.move_creations,
                    include_dependencies=False,  # avoid deep recursion unless explicitly requested
                    force_unshare=self.force_unshare,
                    invalidate_after_transfer=self.invalidate_after_transfer,
                    mark_dependencies_dirty=self.mark_dependencies_dirty,
                )
                sub_transfer.execute()
                # Mark dependency lineage dirty if requested
                if self.invalidate_after_transfer:
                    self._mark_lineage_dirty(dep_spell.spell_index)
            except Exception:
                continue

    def _dirty_dependencies(self, deps: List[str]) -> None:
        """
        Mark dependencies dirty without moving them.

        Args:
            deps: List of dependency spell_ids to mark dirty.
        """
        for dep_id in deps:
            try:
                dep_spell = self.source_conduit.get_spell_by_id(dep_id, self._frame_name)
                if dep_spell is None:
                    continue
                self._mark_lineage_dirty(dep_spell.spell_index)
            except Exception:
                continue

    # ------------------------------------------------------------------
    # Change-control / incidents
    # ------------------------------------------------------------------
    def _record_change_intent(self, summary: Dict[str, Any]) -> None:
        """
        Register a change-control entry describing the pending transfer.

        Args:
            summary: Preflight summary payload.
        Notes:
            Best-effort; failures are ignored so as not to block transfer.
        """
        try:
            existing = self._change_control_manager.get_pending_change(summary["spell_index"].id)
            if existing and existing.get("op_id") == summary["op_id"]:
                return
            self._change_control_manager.register_pending_change(
                spell_index=summary["spell_index"],
                reason="ownership_transfer",
                metadata={
                    "spell_id": summary["spell_id"],
                    "source_conduit_id": summary["source"],
                    "target_conduit_id": summary["target"],
                    "borrowers": summary["borrowers"],
                    "dependencies": summary["dependencies"],
                    "creations": summary["creations"],
                    "op_id": summary["op_id"],
                    "options": summary["options"],
                },
            )
        except Exception:
            # Best-effort; failures here should not block the transfer.
            pass

    def _clear_change_intent(self, spell_index: SpellIndex) -> None:
        """
        Clear any change-control entry after successful transfer.

        Args:
            spell_index: Lineage whose pending change should be cleared.
        """
        try:
            self._change_control_manager.clear_pending_change(spell_index.id)
        except Exception:
            pass

    def _record_incident(self, summary: Dict[str, Any], exc: Exception) -> None:
        """
        Emit an incident describing a failed or partial transfer.

        Args:
            summary: Preflight/transfer summary payload.
            exc: Exception that triggered the failure path.
        """
        try:
            self._incident_manager.create_incident(
                kind="ownership_transfer_failed",
                severity=IncidentSeverity.error,
                summary=str(exc),
                spell_index_id=summary["spell_index"].id,
                root_ids=[summary["spell_id"]],
                details={
                    "source_conduit_id": summary["source"],
                    "target_conduit_id": summary["target"],
                    "borrowers": summary["borrowers"],
                    "dependencies": summary["dependencies"],
                    "creations": summary["creations"],
                    "op_id": summary.get("op_id"),
                    "options": summary.get("options", {}),
                },
            )
        except Exception:
            pass

        # If no revalidator is wired, emit a reminder incident.
        try:
            if getattr(self._change_control_manager, "_revalidate_fn", None) is None:
                self._incident_manager.create_incident(
                    kind="ownership_transfer_needs_revalidation",
                    severity=IncidentSeverity.warning,
                    summary="Ownership transfer completed but no revalidator is registered.",
                    spell_index_id=summary["spell_index"].id,
                    root_ids=[summary["spell_id"]],
                    details={
                        "source_conduit_id": summary["source"],
                        "target_conduit_id": summary["target"],
                        "op_id": summary.get("op_id"),
                    },
                )
        except Exception:
            pass
