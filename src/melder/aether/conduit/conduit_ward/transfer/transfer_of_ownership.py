import threading
from functools import partial
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    cast,
    ClassVar,
)



# Melder imports
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.utilities.general_base.cleanable import Cleanable
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.existence.existence import Existence
from melder.utilities.helpers.ulid_factory import new_ulid
from melder.utilities.synchronization.safeguard import SafeGuard
from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state import SpellState
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.aether.aetheric_frame.dev_ops.incident_manager.incident_severity import IncidentSeverity
if TYPE_CHECKING:
    from melder.aether.conduit.conduit import Conduit
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.change_control_manager import ChangeControlManager
    from melder.aether.aether import Aether
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spellbook import Spellbook
    from melder.aether.aetheric_frame.conduit_cloud import ConduitCloud
    from melder.aether.aetheric_frame.dev_ops.incident_manager.incident_manager import IncidentManager


class TransferOfOwnership(Cleanable):
    """
    Control-plane helper that migrates a spell lineage between conduit owners.

    This class is the implementation behind dynamic spell ownership transfer.
    It keeps the high-risk parts of the move in one place so the runtime can
    treat transfer as an explicit control-plane operation rather than an ad hoc
    series of spellbook edits.

    The transfer lifecycle has two phases:

    - `preflight()` performs a read-only inventory of the lineage, its
      borrowers, its dependent spell ids, and any creation/existence state that
      will be affected.
    - `execute()` performs the actual migration by temporarily disabling the
      lineage, flipping the canonical registry/spellbook ownership under lock,
      reconciling contracts/clusters, and then leaving the impacted state
      gated/dirty so later validation phases can rebuild a truthful runtime
      view.

    Accepted spellspace boundary:
    - Transfer moves canonical lineage ownership plus conduit-owned runtime
      state only.
    - Live spellspace-local request objects are intentionally excluded.
    - If a spellspace-scoped lineage is transferred while an old source
      `SpellSpace` still exists, that old request object may become stale and
      must be cleaned as request-local state; ownership transfer does not try
      to preserve or rehome it.

    The object also owns rollback bookkeeping, change-intent registration, and
    incident reporting so transfer failures do not silently strand the runtime
    in a half-moved state.

    Thread-safety:
        The registry/spellbook ownership flip is protected by `SafeGuard`.
        Broader cleanup and post-flip repair flows rely on the locks and
        invariants provided by the subsystems they call into.

    Threading:
        The canonical flip runs under `SafeGuard` so no resolver can observe a
        half-moved registry. Everything outside that window delegates to the
        locks of the subsystems it calls; this class adds no second lock order
        of its own, which is what keeps it free of deadlock risk against
        `ConduitWard` and the change-control plane.

    Lifecycle / Cleanup:
        Single-use and Cleanable: one instance drives one transfer. It owns
        rollback bookkeeping for the duration, so it must not be reused across
        transfers - a second run would inherit the first run's undo state.

    Registration:
        MELDER KERNEL - guarded. Constructed by `Conduit.transfer_spell_ownership(...)`;
        never user-instantiated and never bindable.

    Subsystem Context:
        The heaviest control-plane operation in the conduit package and the
        only one that rewrites OWNERSHIP rather than relationships.
        `ConduitWard` grants and revokes access to a lineage someone else owns;
        this class changes who the owner IS. That is why it reconciles wards,
        clusters, and creations rather than living inside any one of them.

    System Context:
        The two-phase shape is the whole safety argument. `preflight()` is
        strictly read-only, so the full blast radius - borrowers, dependent
        spell ids, affected creations - is known BEFORE anything mutates. Only
        then does `execute()` disable the lineage, flip ownership under guard,
        and leave the impacted state gated/dirty so later validation phases
        rebuild a truthful view rather than trusting a mid-move snapshot.
        Leaving state DIRTY on purpose is the counterintuitive part: the
        transfer deliberately does not repair the resolution graph itself,
        because it cannot know which consumers are mid-resolution. It marks and
        defers, and meld-time lazy revalidation does the rebuild under the
        per-spell lock.
        The spellspace exclusion documented above follows the same honesty
        rule as `ConduitMeld`'s refusal: a live request-local object CANNOT be
        rehomed correctly, so the contract says plainly that it goes stale and
        must be cleaned as request state, rather than pretending to move it.
        Transfer is dynamic-mode only - like linking, severing, and upgrade, it
        rewires the graph after conjure, which an automatic-mode world forbids.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Control-plane helper that migrates a spell lineage between conduit "
        "owners. Melder kernel machinery: read it to understand the runtime, do not drive it "
        "directly."
    )
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_source_spellbook",
        "_target_spellbook",
        "_aether",
        "_frame_name",
        "_preflight_summary",
        "source_conduit",
        "target_conduit",
        "spell",
        "move_creations",
        "include_dependencies",
        "force_unshare",
        "invalidate_after_transfer",
        "mark_dependencies_dirty",
        "_change_control_manager",
        "_incident_manager",
        "_rollback_actions",
        "_op_id",
    ]

    def __init__(
        self,
        *,
        source_conduit: Conduit,
        target_conduit: Conduit,
        spell: Spell,
        move_creations: bool = False,
        include_dependencies: bool = False,
        force_unshare: bool = True,
        invalidate_after_transfer: bool = True,
        mark_dependencies_dirty: bool = False,
    ):
        """
        Initialize one ownership-transfer operation.

        The constructor captures both the source/target endpoints and the
        policy choices that define how aggressive the move should be. Those
        options decide whether creations are carried forward or torn down,
        whether owned dependencies move with the root lineage, whether existing
        shares are force-unshared or repointed, and whether impacted lineages
        should remain gated after the move so validation reruns before normal
        resolution resumes.

        Args:
            source_conduit: Conduit that currently owns the root lineage.
            target_conduit: Conduit that should become the new owner.
            spell: Spell object, spell id, or `SpellIndex` identifying the
                lineage to move.
            move_creations: When true, transfer creation-side state to the
                target instead of tearing it down.
            include_dependencies: When true, transfer owned dependency lineages
                with the root instead of requiring the target side to resolve
                them independently.
            force_unshare: When true, remove outward shares/borrowers instead of
                trying to repoint them at the new owner.
            invalidate_after_transfer: When true, leave the moved lineage and
                impacted conduits gated/dirty so the runtime revalidates phases
                before reuse.
            mark_dependencies_dirty: If dependencies are not moved, mark their
                lineages dirty so stale downstream state is not reused.

        Returns:
            None.
        """
        super().__init__()
        self.source_conduit: Conduit = source_conduit
        self.target_conduit: Conduit = target_conduit
        self.spell: Spell = spell
        self.move_creations: bool = move_creations
        self.include_dependencies: bool = include_dependencies
        self.force_unshare: bool = force_unshare
        self.invalidate_after_transfer: bool = invalidate_after_transfer
        self.mark_dependencies_dirty: bool = mark_dependencies_dirty

        self._lock: threading.RLock = threading.RLock()
        self._source_spellbook: Spellbook = self.source_conduit._spellbook
        self._target_spellbook: Spellbook = self.target_conduit._spellbook
        self._aether: Aether = self._source_spellbook._aether
        self._frame_name: str = self.source_conduit._aetheric_frame_name
        self._preflight_summary: Dict[str, Any] = {}
        change_control_manager = self._aether._get_change_control_manager(
            self._frame_name
        )
        if change_control_manager is None:
            raise RuntimeError(
                "Aether did not provide a ChangeControlManager for ownership transfer."
            )
        self._change_control_manager: ChangeControlManager = change_control_manager
        self._incident_manager: IncidentManager = self._aether._get_incident_manager(self._frame_name)
        self._rollback_actions: List[Callable[[], object]] = []
        self._op_id: str = new_ulid()


    def cleanup(self) -> None:
        """
        Release transfer-owned runtime references and permanently retire this helper.

        Contract:
            - Idempotent: repeated calls are safe after `_cleaned` flips.
            - Clears mutable rollback/preflight containers under the transfer
              lock first, then drops high-level references afterward.
            - Does not cleanup source/target conduits or managers because this
              helper only borrows them.

        Returns:
            None.
        """
        if self.is_cleaned:
            return

        with self._lock:
            if self.is_cleaned:
                return
            self._cleaned = True
            self._cleanup_components()

        self._cleanup_core()

    def _cleanup_components(self) -> None:
        """
        Clear mutable transfer bookkeeping under the helper lock.
        """
        if self._preflight_summary is not None:
            self._preflight_summary.clear()
        if self._rollback_actions is not None:
            self._rollback_actions.clear()

    def _cleanup_core(self) -> None:
        """
        Drop high-level borrowed references after cleanup bookkeeping completes.
        """
        del self.source_conduit
        del self.target_conduit
        del self.spell
        del self.move_creations
        del self.include_dependencies
        del self.force_unshare
        del self.invalidate_after_transfer
        del self.mark_dependencies_dirty
        del self._aether
        del self._frame_name
        del self._source_spellbook
        del self._target_spellbook
        del self._preflight_summary
        del self._change_control_manager
        del self._incident_manager
        del self._rollback_actions
        del self._op_id
        del self._lock


    # ------------------------------------------------------------------
    # Preflight
    # ------------------------------------------------------------------
    def preflight(self) -> Dict[str, Any]:
        """
        Build a read-only transfer plan for the requested lineage.

        Preflight does not mutate ownership. Its job is to prove the basic
        invariants first, then capture the runtime surface that `execute()`
        will have to reconcile: borrowers, dependencies, creations, and the
        rollback snapshot needed to unwind a partially completed move.

        Returns:
            Dict[str, Any]: Structured summary containing the resolved spell
            identity, source/target conduit ids, borrower descriptors,
            dependency spell ids, creation/existence details, transfer options,
            operation id, and the rollback snapshot captured from the current
            runtime state.
        Raises:
            RuntimeError: If dynamic-mode or ownership invariants fail, or if
                the transfer was requested without dependency migration even
                though the target side cannot resolve the current dependencies.
        """
        self.check_cleaned()
        self._assert_dynamic_mode()
        spell_obj = self._resolve_spell()
        self._assert_ownership(spell_obj)
        self._preflight_summary = self._build_preflight_summary(spell_obj)
        self._record_change_intent(self._preflight_summary)
        if not self.include_dependencies and not self._deps_resolvable_on_target(self._preflight_summary["dependencies"]):
            raise RuntimeError("Dependencies are not resolvable on target; set include_dependencies=True or fix target.")
        return self._preflight_summary

    def _build_preflight_summary(self, spell_obj: Any) -> Dict[str, Any]:
        """
        Build the pure preflight summary for one transfer candidate.

        Purpose:
            Produce the structured transfer plan payload without mutating any
            external control-plane state. This is the planning-only helper used
            both by `preflight()` and by transaction strategies that need the
            same participant/dependency/creation inventory before admission.

        Contract:
            - Does not record pending-change intent.
            - Does not emit incidents.
            - Does not mutate spellbooks, conduits, contracts, clusters, or
              registry state.
            - Returns the same structural shape later persisted into
              `self._preflight_summary` by `preflight()`.

        Args:
            spell_obj:
                Resolved live spell object owned by the source conduit.

        Returns:
            Dict[str, Any]:
                Structured pure preflight summary for the candidate transfer.
        """
        self.check_cleaned()
        return {
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

    # ------------------------------------------------------------------
    # Execute
    # ------------------------------------------------------------------
    def execute(self) -> None:
        """
        Perform the ownership migration described by the current preflight.

        The method intentionally separates the minimal ownership flip from the
        larger cleanup/repair surface:

        1. disable the lineage so callers cannot resolve it mid-transfer
        2. pre-clean contract state if `force_unshare` requires it
        3. flip the canonical registry and spellbook ownership under lock
        4. reconcile conduit-owned creations, contracts/clusters, and dependency
           handling
        5. leave the lineage gated/dirty or simply re-enable it according to
           the constructor options

        Scope note:
            Step 4 does not move spellspace-local request objects. Those remain
            owned by any already-live source `SpellSpace` surfaces and are
            intentionally outside ownership-transfer continuity.

        If any step fails, rollback handlers attempt to restore a coherent
        runtime view, the lineage is lifted back to a safe gated state, and the
        incident/change-control systems are notified.

        Raises:
            Exception: Re-raises the underlying transfer failure after rollback
                and incident recording have been attempted.

        Returns:
            None.
        """
        self.check_cleaned()
        summary = self._preflight_summary or self.preflight()
        spell_obj = self._resolve_spell()

        try:
            # Hard block resolution during transfer
            self._mark_lineage_disabled(spell_obj.spell_index)

            # If the target is currently contracted, remove that entry before the flip.
            if self.force_unshare:
                with SafeGuard(self.source_conduit._lock, self.target_conduit._lock):
                    self._unshare_target_conduit_contract(spell_obj)

            # Minimal critical section: flip registry + spellbooks
            with SafeGuard(self.source_conduit._lock, self.target_conduit._lock):
                self._flip_registry_and_spellbooks(spell_obj)
                self._migrate_inactive_members(spell_obj)

            # Creations. unique_per_conduit_lineage instances are resolver-relative:
            # one per lineage root, stored in the RESOLVING conduit's creations
            # (`caller_creations._root_creations`), never the binding owner's. They
            # are not the owner's to move, so ownership transfer flips only the
            # canonical binding and leaves every per-root instance where it was
            # resolved (the source keeps its instance; the target builds its own on
            # first resolve). The move/teardown helpers assume owner-bound storage,
            # so they are skipped for lineage regardless of `move_creations`.
            if spell_obj.existence is Existence.unique_per_conduit_lineage:
                pass
            elif self.move_creations:
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
                self._gate_transfer_impacts(spell_obj=spell_obj, summary=summary)
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
            # Record re-anchor: ownership transfer moved the index and its
            # members to the target spellbook, so every custody crystal's
            # spellbook parent edge is stale. Re-emit the membership twin
            # under the new owner plus fresh custody for every member
            # (replace-on-emit displaces the stale source-book crystals).
            target_spellbook = self.target_conduit._spellbook
            crystallizer = target_spellbook._crystallizer
            if crystallizer.activated:
                crystallizer.emit(
                    crystallizer.create_spell_index_crystal(
                        spell_obj.spell_index, target_spellbook._id
                    )
                )
                for member_id in set(spell_obj.spell_index._spells_in_index):
                    member = target_spellbook._spells_by_id.get(member_id)
                    member_is_active = member is not None
                    if member is None:
                        member = target_spellbook._inactive_spells.get(
                            member_id
                        )
                    if member is None:
                        continue
                    crystallizer.emit_spell_crystal(
                        crystallizer.create_spell_crystal(
                            member, spellbook_id=target_spellbook._id
                        ),
                        active=member_is_active,
                    )
                # Borrower repoint bypasses the public contract verbs
                # (_repoint_borrowers drives ward._link /
                # ward._add_spell_to_contract directly), so re-record every
                # contract the TARGET now participates in - one snapshot
                # covers both wards' views; severed old-side contracts were
                # already evicted by the _remove_contract seam.
                target_ward = self.target_conduit._conduit_ward
                for record_contract in list(target_ward._contracts.values()):
                    target_ward._emit_contract_record(record_contract)
                # SOURCE-side survivors: peers that still borrow OTHER
                # spells from the source keep their contract with the
                # transferred spell's detail removed (again via ward
                # internals) - re-record every surviving source contract so
                # no stale detail lingers; fully-emptied contracts were
                # already evicted at the _remove_contract seam.
                source_ward = self.source_conduit._conduit_ward
                for record_contract in list(source_ward._contracts.values()):
                    source_ward._emit_contract_record(record_contract)
                # Both ends' outbound topology may have changed (repointed
                # links on the target; severed links on the source).
                self.target_conduit._emit_conduit_twin()
                self.source_conduit._emit_conduit_twin()
        finally:
            self._rollback_actions.clear()

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _assert_dynamic_mode(self) -> None:
        """
        Enforce the runtime precondition for ownership transfer.

        Ownership transfer is only supported in the dynamic environment because
        the move depends on runtime contract teardown/repointing and lineage
        invalidation flows that do not exist in the static model.

        Raises:
            RuntimeError: If either endpoint conduit is not running in dynamic
                mode.
        """
        self.check_cleaned()
        if not self.source_conduit.__dynamic_environment__ or not self.target_conduit.__dynamic_environment__:
            raise RuntimeError("Transfer requires dynamic mode on both source and target.")

    def _resolve_spell(self) -> Any:
        """
        Normalize the caller-provided spell handle into the live spell object.

        Transfer entrypoints allow several spell identifiers for convenience,
        but the transfer machinery itself operates on the concrete spell object
        so it can inspect ownership, dependencies, creations, and lineage
        state.

        Returns:
            The resolved spell object owned by the source conduit's spellbook.
        Raises:
            RuntimeError: If the provided spell reference cannot be resolved
                into a live spell object.
        """
        self.check_cleaned()
        # spell may be object, id, or SpellIndex
        if hasattr(self.spell, "spell_id"):
            return self.spell
        if isinstance(self.spell, SpellIndex):
            idx = self.spell
            book = self._source_spellbook
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
        self.check_cleaned()
        if spell_obj._owner_conduit_id != self.source_conduit._id:
            raise RuntimeError("Source conduit does not own the spell.")

    def _enumerate_borrowers(self, spell_id: str) -> List[Dict[str, Any]]:
        """
        Enumerate downstream runtime surfaces currently borrowing this lineage.

        Borrowers can come from direct ward contracts or conduit-cluster share
        tables. `execute()` uses this inventory to decide whether those surfaces
        should be force-unshared or repointed after the ownership flip.

        Returns:
            List[Dict[str, Any]]: Borrower descriptors tagged by borrowing
            mechanism (`contract` or `cluster`) plus the ids needed for later
            reconciliation.
        """
        self.check_cleaned()
        borrowers: List[Dict[str, Any]] = []
        ward = self.source_conduit._conduit_ward
        # Contracts
        seen_contracts = set()
        for contract_id, contract in ward._contracts.items():
            if contract_id in seen_contracts:
                continue
            for detail_map in (contract._details_a, contract._details_b):
                if spell_id in detail_map:
                    borrower_conduit_id = None
                    try:
                        borrower_conduit_id = contract._get_peer(ward)._conduit._id
                    except Exception:
                        borrower_conduit_id = None
                    borrowers.append(
                        {
                            "type": "contract",
                            "contract_id": contract._id,
                            "borrower_conduit_id": borrower_conduit_id,
                        }
                    )
                    seen_contracts.add(contract_id)
                    break
        # Clusters: scan cluster registries
        conduit_cloud = self._get_source_conduit_cloud()
        cluster_names = conduit_cloud.get_clusters_for_conduit(
            self.source_conduit._id
        )
        for cname in cluster_names:
            cluster = conduit_cloud.get_cluster(cname)
            for owner_id, indices in cluster.get_shared_spells().items():
                for idx in indices:
                    if idx.has_spell(spell_id) or idx.selected_spell_id == spell_id:
                        borrowers.append(
                            {
                                "type": "cluster",
                                "cluster": cname,
                                "cluster_id": getattr(cluster, "id", cname),
                                "owner_id": owner_id,
                                "member_conduit_ids": tuple(sorted(cluster.get_members())),
                            }
                        )
                        break
        return borrowers

    def _enumerate_dependencies(self, spell_obj: Any) -> List[str]:
        """
        List dependency spell_ids for the spell.

        Returns:
            List of dependency spell_ids.
        """
        self.check_cleaned()
        return list(spell_obj.dependencies)

    def _enumerate_creations(self, spell_obj: Any) -> Dict[str, Any]:
        """
        Capture the creation/existence surface currently attached to the spell.

        The current implementation only records the existence handle because
        that is the minimum state needed by the present transfer flow. The
        return shape is already dictionary-based so fuller creation inspection
        can be added later without changing the preflight contract shape.

        Returns:
            Dict[str, Any]: Creation/existence snapshot for preflight and
            rollback planning.
        """
        self.check_cleaned()
        return {"existence": spell_obj.existence}

    def _get_source_conduit_cloud(self) -> ConduitCloud:
        """
        Return the source conduit's frame-local cloud service.

        Returns:
            ConduitCloud: The source conduit's cloud service.

        Raises:
            RuntimeError: If the source conduit does not expose a valid cloud.
        """
        conduit_cloud: ConduitCloud = self._aether.get_conduit_cloud(
            self.source_conduit._aetheric_frame_name
        )
        if conduit_cloud is None:
            raise RuntimeError("Source conduit did not return a valid ConduitCloud.")
        return conduit_cloud

    def _deps_resolvable_on_target(self, deps: List[str]) -> bool:
        """
        Check whether the target conduit can already resolve the dependency set.

        This is the safety gate for transfers that do not move owned
        dependencies. If the target side cannot already resolve the dependency
        ids, the root lineage would arrive in a knowingly broken state.

        Returns:
            bool: `True` when every dependency id resolves on the target side,
            otherwise `False`.
        """
        self.check_cleaned()
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

    def _mark_lineage_dirty(self, spell: Any) -> None:
        """
        Record a structural-change gate for one lineage in `SpellSystemStates`.

        This is the lighter-weight post-transfer invalidation path. Instead of
        hard-disabling the lineage, it marks the lineage as structurally changed
        so later spell-crafter phases rerun before callers trust the lineage
        again.

        Args:
            spell_index: Lineage whose spell-system state should be marked dirty.
        """
        self.check_cleaned()
        spellbook = spell._spellbook
        if spellbook is None:
            raise RuntimeError(
                "Cannot mark a spell dirty without an attached owner Spellbook."
            )
        spell_states = spellbook._spell_system_states
        if spell_states is None:
            raise RuntimeError("Owner Spellbook has no SpellSystemStates.")
        spell_states.mark_structural_change(
            spell_index=spell.spell_index,
            reason=SpellStateChangeReason.structure_changed,
        )

    def _gate_transfer_impacts(
            self,
            *,
            spell_obj: Any,
            summary: Dict[str, Any],
    ) -> None:
        """
        Dirty the moved lineage and every conduit that may now see changed
        transfer fallout.

        The root lineage itself is structurally changed by the ownership flip,
        but the runtime impact is wider than that one spell. Borrowers,
        peers, cluster members, and any conduit currently holding an impacted
        lineage may all need to rerun later spell-crafter phases before their
        local view is trustworthy again.
        """
        self.check_cleaned()
        spell_index = spell_obj.spell_index
        spell_states = spell_obj._spell_system_states
        if spell_states is None:
            raise RuntimeError("Transferred spell is missing SpellSystemStates.")

        spell_states.mark_structural_change(
            spell_index=spell_index,
            reason=SpellStateChangeReason.structure_changed,
        )

        impacted_lineages = spell_states.compute_impact_closure([spell_index.id])

        conduit_ids = self._collect_impacted_conduit_ids(
            impacted_lineages=impacted_lineages,
            summary=summary,
        )
        for conduit_id in conduit_ids:
            spell_states.mark_conduit_dirty(
                conduit_id=conduit_id,
                change_reason=SpellStateChangeReason.structure_changed,
            )

    def _collect_impacted_conduit_ids(
            self,
            *,
            impacted_lineages: Set[str],
            summary: Dict[str, Any],
    ) -> Set[str]:
        """
        Collect every conduit whose local resolution view may be invalidated by
        the transfer.

        The set intentionally combines several sources of truth:

        - the source and target owners
        - currently contracted peers
        - cluster members surfaced by the borrower inventory
        - any conduit whose owned or contracted spellbook already contains one
          of the impacted lineages

        That broader closure is what lets the transfer leave the runtime in a
        safe gated state instead of assuming only the two owners were touched.
        """
        self.check_cleaned()
        conduit_ids: Set[str] = set()
        if self.source_conduit._id:
            conduit_ids.add(self.source_conduit._id)
        if self.target_conduit._id:
            conduit_ids.add(self.target_conduit._id)

        for conduit in (self.source_conduit, self.target_conduit):
            peers = conduit._conduit_ward._get_contracted_conduits()
            if peers:
                for _peer_id, peer in peers:
                    if peer is not None and peer._id:
                        conduit_ids.add(peer._id)

        borrowers = summary.get("borrowers", []) if summary else []
        for borrower in borrowers:
            if borrower.get("type") != "cluster":
                continue
            cluster_name = borrower.get("cluster")
            if not cluster_name:
                continue
            cluster = self._get_source_conduit_cloud().get_cluster(cluster_name)
            cluster_members = list(cluster.get_members())
            if cluster_members:
                conduit_ids.update([cid for cid in cluster_members if cid])

        for conduit_id in self._aether.list_conduit_ids(self._frame_name):
            if not conduit_id:
                continue
            try:
                conduit = self._aether.get_conduit_by_id(
                    conduit_id,
                    self._frame_name,
                )
            except Exception:
                continue
            if conduit is None or not conduit._id:
                continue
            if self._conduit_has_impacted_lineage(conduit, impacted_lineages):
                conduit_ids.add(conduit._id)

        return conduit_ids

    def _conduit_has_impacted_lineage(
            self,
            conduit: Any,
            impacted_lineages: Set[str],
    ) -> bool:
        """
        Check whether a conduit currently holds any lineage in the impacted
        closure.

        Both owned and contracted spell maps are considered because transfer
        fallout is not limited to direct ownership; a borrower can also carry a
        stale view that needs revalidation.
        """
        self.check_cleaned()
        if conduit is None or not impacted_lineages:
            return False
        spellbook = conduit._spellbook
        if spellbook is None:
            return False
        owned = spellbook._spells or {}
        for spell_index in owned.keys():
            if spell_index is not None and spell_index.id in impacted_lineages:
                return True
        contracted = spellbook._contracted_spells or {}
        for spell_map in contracted.values():
            for spell_index in spell_map.keys():
                if spell_index is not None and spell_index.id in impacted_lineages:
                    return True
        return False

    def _mark_lineage_disabled(self, spell_index: SpellIndex) -> None:
        """
        Hard-disable the lineage while the ownership flip is actively in flight.

        This is stronger than the later dirty/gated state used after a
        successful move. During the critical transfer window the lineage should
        not resolve at all, because ownership, contract state, and creation
        bookkeeping may be temporarily inconsistent. The previous validity state
        is captured as a rollback action before the disable is applied.

        Args:
            spell_index: Lineage being moved between conduit owners.
        """
        self.check_cleaned()
        spell_states = self._source_spellbook._spell_system_states
        state = spell_states.get_by_index_id(spell_index.id)
        if state is None:
            spell_states.register_index(spell_index)
            state = spell_states.get_by_index_id(spell_index.id)
        if state is None:
            raise RuntimeError("Failed to register lineage for transfer disable.")

        # Record rollback to previous validity
        prev_validity = state.validity
        prev_reason = state.change_reason
        self._register_rollback(
            partial(
                state.set_validity,
                prev_validity,
                change_reason=prev_reason,
            )
        )
        state.set_validity(
            SpellValidity.disabled,
            change_reason=SpellStateChangeReason.transfer_in_progress,
            flags_to_add=[SpellState.transfer_in_progress],
        )

    def _register_rollback(self, fn: Optional[Callable[[], object]]) -> None:
        """
        Register one failure-recovery action for the current transfer.

        Rollback handlers are accumulated as the transfer crosses irreversible
        boundaries. They are later executed in reverse order so the recovery
        path unwinds ownership, contract, and state transitions from newest to
        oldest, matching the order in which the transfer mutated the runtime.

        Args:
            fn: Callable to execute during rollback. `None` is ignored so call
                sites can register handlers conditionally without branching.
        """
        self.check_cleaned()
        if fn is not None:
            self._rollback_actions.append(fn)

    def _rollback(self) -> None:
        """
        Execute the accumulated rollback stack after transfer failure.

        Recovery is intentionally best-effort. Each handler is allowed to fail
        independently so one broken undo step does not prevent later handlers
        from repairing other parts of the runtime. After the explicit rollback
        stack is drained, the method also attempts to rebuild cluster-sharing
        state from the preflight snapshot because cluster exposure lives partly
        outside the spellbook/registry flip itself.
        """
        self.check_cleaned()
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
        Restore the spellbook-side ownership flip back to the source conduit.

        This rollback step repairs the local spell registries after a failed
        transfer that already crossed the critical ownership-flip boundary. It
        moves the spell record back into the source spellbook, removes the
        partially moved target-side entries, restores lineage ownership pointers
        on the spell and `SpellIndex`, and re-registers the spell with the
        source-side risk/validation surfaces.

        The intent is not only to put the spell back in the right dictionary.
        It is to restore one coherent owner view so later validation,
        risk-management, and resolution logic all agree on which conduit owns
        the lineage after the failed move.

        Args:
            spell_obj: Live spell object whose ownership flip is being undone.
            src_book: Original owner spellbook that should regain the lineage.
            tgt_book: Partially updated target spellbook that must release the
                lineage.
        """
        self.check_cleaned()
        spell_id = spell_obj.spell_index.selected_spell_id
        with SafeGuard(tgt_book._lock, src_book._lock):
            tgt_book._spells.pop(spell_obj.spell_index, None)
            tgt_book._lookup_spells.pop(spell_obj._key, None)
            if tgt_book._spells_by_id is not None:
                tgt_book._spells_by_id.pop(spell_id, None)
            if tgt_book._spell_id_pool is not None:
                tgt_book._spell_id_pool.pop(spell_id, None)
            src_book._spells[spell_obj.spell_index] = spell_obj
            src_book._lookup_spells[spell_obj._key] = spell_obj.spell_index
            if src_book._spells_by_id is not None:
                existing = src_book._spells_by_id.get(spell_id)
                if existing is None or existing is spell_obj:
                    src_book._spells_by_id[spell_id] = spell_obj
            if src_book._spell_id_pool is not None:
                existing_pool = src_book._spell_id_pool.get(spell_id)
                if existing_pool is None or existing_pool is spell_obj:
                    src_book._spell_id_pool[spell_id] = spell_obj
            spell_obj._spellbook = src_book
            spell_obj._spell_system_states = src_book._spell_system_states
            spell_obj._cleanup_creation_context()
            spell_obj._compiler_artifact.cleanup_phase_artifacts()
            spell_obj._compiler_artifact.clear_phase5_artifacts()
            spell_obj.requires_spellspace_request = False
            tgt_book._unregister_spell_with_risk_manager(self.target_conduit._id, spell_obj)
            src_book._register_spell_with_risk_manager(self.source_conduit._id, spell_obj)
        # Ownership lives on the spell (its _spellbook / _owner_conduit_id, set
        # above); the SpellIndex no longer records an owner.
        try:
            spell_obj._owner_conduit_id = self.source_conduit._id
        except Exception:
            pass
        # Compilation is always full/eager (AOT/JIT knob removed). Post-transfer
        # recompilation is guaranteed by resolution_complete=False plus the
        # cleared phase artifacts, not by a deferred-resolution flag.
        spell_obj.resolution_required = False
        spell_obj.resolution_complete = False
        src_states = src_book._spell_system_states
        tgt_states = tgt_book._spell_system_states
        if src_states is None:
            raise RuntimeError("Source Spellbook has no SpellSystemStates.")
        if tgt_states is not None and tgt_states is not src_states:
            tgt_states.unregister_index(spell_obj.spell_index)
        src_states.register_index(spell_obj.spell_index)

    def _unshare_target_conduit_contract(self, spell_obj: Any) -> None:
        """
        Remove the target-side borrowed contract entry before the ownership flip.

        This is the pre-flip safety step for the case where the target conduit
        already sees the spell through a contract with the source. If that
        borrowed entry is left in place during the flip, later contract cleanup
        can accidentally remove the newly owned spell-id mapping from the
        target's spellbook after ownership has already changed.

        The helper therefore removes the borrowed contract view first and
        registers a rollback action that can restore it if the transfer aborts.
        Recovery is best-effort because failure to pre-clean this surface
        should not by itself prevent the larger ownership move from attempting
        rollback.

        Args:
            spell_obj: Spell whose borrowed target-side contract entry may need
                to be removed temporarily.
        """
        self.check_cleaned()
        try:
            target_ward = self.target_conduit._conduit_ward
            contract = target_ward._find_contract_by_id(self.source_conduit._id)
            if contract is None:
                return
            with contract._lock:
                existed_before = (
                    contract._check_if_exists(target_ward, spell_obj.spell_id)
                    or contract._check_if_exists(self.source_conduit._conduit_ward, spell_obj.spell_id)
                )
            if not existed_before:
                return
            target_ward._remove_spell_from_contract(
                spell_id=spell_obj.spell_id,
                conduit=self.source_conduit,
                conduit_id=self.source_conduit._id,
                aetheric_frame=self._frame_name,
            )
            self._register_rollback(
                lambda: self._restore_contract_entry(
                    target_ward,
                    spell_obj,
                    self.source_conduit,
                    existed_before,
                )
            )
        except Exception:
            pass

    def _rollback_move_creation(self, spell_obj: Any, obj: Any) -> None:
        """
        Move one already-transferred creation back to the source conduit.

        This handler is used when a single creation instance has already been
        rehomed on the target before the overall transfer fails. It restores
        the previous ownership of that runtime object so the failed transfer
        does not strand live creation state on the wrong conduit.

        Args:
            spell_obj: Spell whose creation ownership is being restored.
            obj: Creation instance that must be reattached to the source.
        """
        self.check_cleaned()
        try:
            self.target_conduit._creations.extract_spell_creations(
                spell_obj.spell_id
            )
            self.source_conduit._creations.restore_spell_creations(
                spell_obj.spell_id,
                [obj],
            )
        except Exception:
            pass

    def _rollback_creations_move(self, spell_id: str, extracted: List[Dict[str, Any]]) -> None:
        """
        Restore a bulk-extracted creation payload back to the source conduit.

        Some transfer paths move creation state in batches rather than one
        object at a time. This rollback step first tries to drain any partial
        target-side creations for the lineage, then restores the original
        extracted payload to the source so ownership and disposal state line up
        with the pre-transfer world again.

        Args:
            spell_id: Spell identifier whose creation payload is being restored.
            extracted: Bulk creation snapshot previously extracted from the
                source conduit.
        """
        self.check_cleaned()
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
        Capture the minimal transfer-recovery snapshot for this lineage.

        The snapshot intentionally stays small. It records only the pieces of
        state needed to detect partial progress and rebuild cluster exposure
        safely if rollback is required: target registry presence, target
        spellbook presence, and cluster-share state.

        Returns:
            Dict[str, Any]: Minimal rollback/idempotence snapshot for the
            current transfer target.
        """
        self.check_cleaned()
        snapshot = {
            "in_target_registry": self._spell_in_registry(self.target_conduit, spell_obj.spell_index),
            "in_target_spellbook": self._spell_in_spellbook(self.target_conduit, spell_obj),
            "cluster_shares": self._snapshot_cluster_shares(spell_obj),
        }
        return snapshot

    def _spell_in_registry(self, conduit: Any, spell_index: SpellIndex) -> bool:
        """
        Check whether Aether already records this lineage under the conduit.

        This is used for rollback/idempotence bookkeeping rather than ordinary
        resolution. The transfer logic needs to know whether a target-side
        registry insert actually happened so it can distinguish "nothing was
        changed" from "partial progress must be undone."

        Args:
            conduit: Conduit whose frame-level Aether registry is being checked.
            spell_index: Lineage key to look for in that registry.
        Returns:
            bool: `True` when the lineage is already registered for the conduit.
        """
        self.check_cleaned()
        try:
            if conduit is None or not conduit._id:
                return False
            frame_name = conduit._aetheric_frame_name or self._frame_name
            frame = self._aether._get_existing_frame(frame_name)
            spell_registry = frame._spell_registry
            conduit_registry = spell_registry.get(conduit._id)
            if conduit_registry is None:
                return False
            return spell_index in conduit_registry
        except Exception:
            return False

    def _spell_in_spellbook(self, conduit: Any, spell_obj: Any) -> bool:
        """
        Check whether the conduit spellbook already owns the spell object.

        Together with `_spell_in_registry`, this lets the transfer distinguish
        spellbook-side progress from registry-side progress when deciding how
        much rollback work is still required.

        Args:
            conduit: Conduit whose spellbook ownership map is being checked.
            spell_obj: Spell object whose local ownership presence is being
                tested.
        Returns:
            bool: `True` when the spellbook currently contains the lineage.
        """
        self.check_cleaned()
        try:
            spellbook = conduit._spellbook
            with spellbook._lock:
                return spell_obj.spell_index in spellbook._spells
        except Exception:
            return False

    def _restore_contract_entry(self, ward: Any, spell_obj: Any, peer: Any, existed_before: bool) -> None:
        """
        Restore one contract entry to the state captured before pre-cleanup.

        This is the inverse of `_unshare_target_conduit_contract`. If the
        transfer fails after removing a borrowed entry, rollback uses this
        helper to either recreate the original contract detail or remove the
        temporary entry again so the ward returns to its pre-transfer contract
        shape.

        Args:
            ward: Ward whose contract detail map is being restored.
            spell_obj: Spell whose contract visibility is being repaired.
            peer: Peer conduit that participates in the contract relationship.
            existed_before: Whether the entry existed before pre-cleanup began.
        """
        self.check_cleaned()
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
        Restore a removed contract entry, with a test-double fallback path.

        In real runtime use the primary ward should always handle the restore.
        The fallback path exists so rollback can still exercise simplified test
        doubles that do not expose the full ward API shape. This keeps the
        production recovery path authoritative while avoiding brittle test-only
        branching at call sites.

        Recovery remains best-effort. If neither ward can restore the detail,
        rollback continues so other ownership/state repair handlers still run.

        Args:
            primary_ward: Real ward expected to own contract restoration.
            fallback_ward: Secondary ward used only when the primary does not
                expose the needed restore method.
            primary_peer: Peer conduit for the real restoration path.
            fallback_peer: Peer conduit paired with the fallback ward.
            spell_obj: Spell whose contract visibility is being restored.
        """
        self.check_cleaned()
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
        Capture cluster-share membership that depends on source ownership.

        Cluster sharing is orthogonal to the direct spellbook/registry flip, so
        rollback needs a small side snapshot to know whether the source-owned
        lineage was exposed through any conduit clusters before transfer began.

        Returns:
            List[Dict[str, Any]]: Cluster-share descriptors sufficient to
            restore source-owned sharing if rollback is required.
        """
        self.check_cleaned()
        shares: List[Dict[str, Any]] = []
        try:
            conduit_cloud = self._get_source_conduit_cloud()
            cluster_names = conduit_cloud.get_clusters_for_conduit(
                self.source_conduit._id
            )
            for cname in cluster_names:
                cluster = conduit_cloud.get_cluster(cname)
                for owner_id, indices in cluster.get_shared_spells().items():
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
        Rebuild cluster-share exposure from the preflight snapshot.

        This is the cluster-side companion to spellbook/registry rollback.
        When transfer failure happens after cluster unsharing, the snapshot lets
        rollback re-add only the shares that truly existed before the move
        instead of re-sharing blindly.

        Args:
            snapshot: Cluster-share descriptors captured before transfer.
            spell_obj: Spell whose source-owned cluster exposure is being
                restored.
        """
        self.check_cleaned()
        try:
            conduit_cloud = self._get_source_conduit_cloud()
            for entry in snapshot or []:
                cname = str(entry.get("cluster"))
                owner_id = entry.get("owner_id")
                if not cname or not owner_id:
                    continue
                try:
                    cluster = conduit_cloud.get_cluster(cname)
                except Exception:
                    continue
                shared_spells = cluster.get_shared_spells()
                if spell_obj.spell_index not in shared_spells.get(owner_id, set()):
                    cluster.add_shared_spell(owner_id, spell_obj.spell_index)
        except Exception:
            pass

    def _lift_disable(self, spell_index: SpellIndex, gated: bool) -> None:
        """
        Exit the hard-disabled in-flight state after transfer success or
        failure.

        The method does not "return to normal" blindly. It converts the lineage
        from the temporary transfer-in-progress state into either:

        - `gated`, when the runtime should force later validation before the
          lineage is trusted again, or
        - `unknown`, when the caller wants the disable removed without
          immediately asserting the stronger gated posture

        In both cases the explicit `transfer_in_progress` flag is removed so the
        lineage no longer looks mid-flight to downstream readers.

        Args:
            spell_index: Lineage leaving the hard-disabled transfer state.
            gated: Whether the lineage should remain blocked behind validation
                (`True`) or return to the weaker unknown state (`False`).
        """
        self.check_cleaned()
        spell_states = self._source_spellbook._spell_system_states
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
        Perform the critical ownership flip across Aether and both spellbooks.

        This is the transfer's main irreversible boundary. Before this step the
        source conduit is still the canonical owner everywhere. After this step,
        registry state, spellbook state, spell ownership pointers, and
        spell-system/risk registrations all need to agree that the target owns
        the lineage.

        The helper therefore stages rollback handlers around both layers of the
        move:

        - frame-level Aether registry membership for the `SpellIndex`
        - spellbook-local ownership maps and lineage/risk registrations

        If any sub-step fails, the caller treats the whole ownership flip as
        failed and runs the accumulated rollback stack to rebuild one coherent
        owner view.

        Args:
            spell_obj: Spell whose canonical owner is moving from source to
                target.
        Raises:
            RuntimeError: If either the frame-level registry move or the
                spellbook/risk-state move cannot be completed coherently.
        """
        self.check_cleaned()
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
            src_book = self._source_spellbook
            tgt_book = self._target_spellbook
            spell_id = spell_obj.spell_index.selected_spell_id
            src_states = src_book._spell_system_states
            tgt_states = tgt_book._spell_system_states
            if src_states is None or tgt_states is None:
                raise RuntimeError("Spellbook missing SpellSystemStates during transfer.")
            with SafeGuard(src_book._lock, tgt_book._lock):
                src_had = spell_obj.spell_index in src_book._spells
                tgt_had = spell_obj.spell_index in tgt_book._spells
                if src_had:
                    src_book._spells.pop(spell_obj.spell_index, None)
                    src_book._lookup_spells.pop(spell_obj._key, None)
                    src_book._unregister_owned_spell_id(spell_id, spell_obj)
                    src_states.unregister_index(spell_obj.spell_index)
                    self._register_rollback(
                        lambda: self._rollback_spellbook_move(spell_obj, src_book, tgt_book)
                    )
                if not tgt_had:
                    tgt_book._spells[spell_obj.spell_index] = spell_obj
                    tgt_book._lookup_spells[spell_obj._key] = spell_obj.spell_index
                if tgt_book._spells_by_id is not None:
                    existing = tgt_book._spells_by_id.get(spell_id)
                    if existing is not None and existing is not spell_obj:
                        raise RuntimeError(
                            f"Owned spell_id collision on target (spell_id={spell_id})"
                        )
                    tgt_book._spells_by_id[spell_id] = spell_obj
                if tgt_book._spell_id_pool is not None:
                    existing_pool = tgt_book._spell_id_pool.get(spell_id)
                    if existing_pool is not None and existing_pool is not spell_obj:
                        raise RuntimeError(
                            f"spell_id_pool collision on target (spell_id={spell_id})"
                        )
                    tgt_book._spell_id_pool[spell_id] = spell_obj
                if spell_obj._spellbook is not tgt_book:
                    spell_obj._spellbook = tgt_book
                    spell_obj._spell_system_states = tgt_book._spell_system_states
                    spell_obj._cleanup_creation_context()
                    spell_obj._compiler_artifact.cleanup_phase_artifacts()
                    spell_obj._compiler_artifact.clear_phase5_artifacts()
                    spell_obj.requires_spellspace_request = False
                tgt_states.register_index(
                    spell_index=spell_obj.spell_index,
                    owner_spellbook_id=tgt_book._id,
                )
                src_book._unregister_spell_with_risk_manager(self.source_conduit._id, spell_obj)
                tgt_book._register_spell_with_risk_manager(self.target_conduit._id, spell_obj)
            # SpellIndex no longer records an owner; the spell's _spellbook
            # (set above) and _owner_conduit_id (set here) are the record.
            spell_obj._owner_conduit_id = self.target_conduit._id
            caching_enabled = tgt_book._resolve_system_caching_enabled()
            spell_obj._add_owned_conduit(
                self.target_conduit._id,
                self.target_conduit._name,
                self.target_conduit._creations,
                dynamic_environment=self.target_conduit.__dynamic_environment__,
                creation_gate_controller=self.target_conduit._creation_gate_controller,
                caching_enabled=caching_enabled,
            )
            # Same contract as the source-side rollback path: eager compilation
            # everywhere, recompile driven by resolution_complete=False.
            spell_obj.resolution_required = False
            spell_obj.resolution_complete = False
            tgt_book._publish_spell_record_to_nexus(spell_obj)
        except Exception as e:
            raise RuntimeError(f"Failed to flip spellbooks: {e}")

    def _move_creations(self, spell_obj: Any) -> None:
        """
        Rehome existing creation state onto the target conduit.

        This branch preserves runtime object continuity across ownership
        transfer. Instead of destroying existing creations and forcing the new
        owner to rebuild them later, it extracts the lineage's creation payload
        from the source and restores that payload into the target conduit's
        `Creations` store. This applies only to conduit-owned creation state;
        spellspace-local request objects are intentionally excluded because
        their lifetime is owned by the source spellspace request surface, not
        by conduit ownership transfer. A rollback handler is then registered so
        the payload can be put back if a later transfer step fails.

        Args:
            spell_obj: Spell whose existing creations should follow the new
                owner.
        """
        self.check_cleaned()
        creations = self.source_conduit._creations
        tgt_creations = self.target_conduit._creations
        # Migrate creations for every member of the lineage (active + inactive),
        # best-effort and per-member: a member with no extractable creations is
        # skipped. The whole index changes owners, so all members' creations follow.
        for member_id in spell_obj.spell_index.spells_in_index():
            try:
                extracted = creations.extract_spell_creations(member_id)
                if not extracted:
                    continue
                tgt_creations.restore_spell_creations(member_id, extracted)
                self._register_rollback(
                    partial(
                        self._rollback_creations_move,
                        member_id,
                        extracted,
                    )
                )
            except Exception:
                continue

    def _teardown_creations(self, spell_obj: Any) -> None:
        """
        Remove source-side creation state instead of preserving it on the
        target.

        This is the destructive transfer posture. It is used when the caller
        wants ownership to move but does not want live creation objects to be
        carried across with it. The extracted payload is still kept for rollback
        so a failed transfer can restore the pre-transfer runtime state.

        Args:
            spell_obj: Spell whose current creations should be torn down rather
                than migrated.
        """
        self.check_cleaned()
        try:
            creations = self.source_conduit._creations
            extracted = creations.extract_spell_creations(spell_obj.spell_id)
            if not extracted:
                return
            self._register_rollback(
                partial(
                    creations.restore_spell_creations,
                    spell_obj.spell_id,
                    extracted,
                )
            )
        except Exception:
            pass

    def _migrate_inactive_members(self, spell_obj: Any) -> None:
        """
        Carry the lineage's INACTIVE members to the target spellbook.

        Transfer of ownership moves an index (lineage). `_flip_registry_and_spellbooks`
        moves only the active/selected member through the active maps; this helper
        carries every other member that is parked in the source spellbook's
        `_inactive_spells` so the whole index ends up owned by the target. Each parked
        member is moved `src._inactive_spells -> tgt._inactive_spells` (plus the
        `_spell_ids` existence set) and has its `_spellbook` / `_spell_system_states`
        / `_owner_conduit_id` repointed to the target. The active map, `_spell_id_pool`,
        and risk manager are intentionally untouched -- inactive members stay off
        resolution. A single rollback handler reverses the whole batch on failure.

        Args:
            spell_obj: The active spell whose index is changing owners.
        """
        self.check_cleaned()
        src_book = self._source_spellbook
        tgt_book = self._target_spellbook
        tgt_states = tgt_book._spell_system_states
        spell_index = spell_obj.spell_index
        selected_id = spell_index.selected_spell_id
        target_conduit_id = self.target_conduit._id
        moved: List[Any] = []
        with SafeGuard(src_book._lock, tgt_book._lock):
            for member_id in spell_index.spells_in_index():
                if member_id == selected_id:
                    continue
                inactive_spell = src_book._inactive_spells.get(member_id)
                if inactive_spell is None:
                    continue
                src_book._inactive_spells.pop(member_id, None)
                src_book._spell_ids.discard(member_id)
                tgt_book._inactive_spells[member_id] = inactive_spell
                tgt_book._spell_ids.add(member_id)
                inactive_spell._spellbook = tgt_book
                inactive_spell._spell_system_states = tgt_states
                inactive_spell._owner_conduit_id = target_conduit_id
                moved.append((inactive_spell, member_id))
        if moved:
            self._register_rollback(
                partial(self._rollback_inactive_members, moved, src_book, tgt_book)
            )

    def _rollback_inactive_members(
            self,
            moved: List[Any],
            src_book: Any,
            tgt_book: Any,
    ) -> None:
        """
        Reverse a batch of inactive-member moves performed by
        `_migrate_inactive_members` when a later transfer step fails.

        Args:
            moved: List of (inactive_spell, member_id) pairs that were moved.
            src_book: The original (source) spellbook to move them back into.
            tgt_book: The target spellbook to remove them from.
        """
        try:
            src_states = src_book._spell_system_states
            source_conduit_id = self.source_conduit._id
            with SafeGuard(src_book._lock, tgt_book._lock):
                for inactive_spell, member_id in moved:
                    tgt_book._inactive_spells.pop(member_id, None)
                    tgt_book._spell_ids.discard(member_id)
                    src_book._inactive_spells[member_id] = inactive_spell
                    src_book._spell_ids.add(member_id)
                    inactive_spell._spellbook = src_book
                    inactive_spell._spell_system_states = src_states
                    inactive_spell._owner_conduit_id = source_conduit_id
        except Exception:
            pass

    def _unshare_everywhere(self, borrowers: List[Dict[str, Any]], spell_obj: Any) -> None:
        """
        Remove downstream borrower visibility instead of migrating it.

        This is the conservative borrower strategy used when `force_unshare`
        is enabled. After the root lineage changes owners, peers that used to
        borrow it from the source should stop resolving it entirely until they
        explicitly relink or are re-exposed by some later operation.

        The helper therefore walks every borrower contract that currently
        exposes the spell, removes the detail, and records rollback handlers
        that can rebuild the prior contract surface if the transfer fails.
        Cluster borrowers are treated as already covered by the underlying
        contract removals.

        Args:
            borrowers: Borrower descriptors collected during preflight.
            spell_obj: Spell whose downstream borrowed visibility is being
                removed.
        """
        self.check_cleaned()
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
                                    partial(
                                        self._restore_contract_entry_with_fallback,
                                        primary_ward=primary_ward,
                                        fallback_ward=fallback_ward,
                                        primary_peer=primary_peer,
                                        fallback_peer=fallback_peer,
                                        spell_obj=spell_obj,
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
        Rebuild borrower relationships so they now resolve from the target
        conduit.

        This is the continuity-preserving alternative to `_unshare_everywhere`.
        Instead of cutting borrowers loose, it recreates contract visibility on
        the target owner and then removes the old source-side contract detail.
        If repointing a given borrower fails, the method deliberately leaves
        that borrower unshared rather than faking success.

        Args:
            borrowers: Borrower descriptors collected during preflight.
            spell_obj: Spell whose borrowers should be migrated to the new
                owner.
        """
        self.check_cleaned()
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
                                        partial(
                                            self._restore_contract_entry,
                                            ward,
                                            spell_obj,
                                            peer,
                                            existed_before,
                                        )
                                    )
                                    self._register_rollback(
                                        partial(
                                            target_ward._remove_spell_from_contract,
                                            spell_id=spell_obj.spell_id,
                                            conduit=peer,
                                            conduit_id=peer._id,
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
        Transfer source-owned dependency lineages alongside the root lineage.

        This is the ownership-preserving dependency strategy. Each dependency is
        transferred with a nested `TransferOfOwnership`, but the recursion is
        deliberately shallow for this pass: nested transfers do not continue
        pulling their own dependencies unless a higher-level caller explicitly
        requests that behavior.

        Args:
            deps: Dependency spell ids discovered during preflight.
        """
        self.check_cleaned()
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
                    if isinstance(dep_spell.spell_index, SpellIndex):
                        self._mark_lineage_dirty(dep_spell)
            except Exception:
                continue

    def _dirty_dependencies(self, deps: List[str]) -> None:
        """
        Leave dependencies in place but force their lineages back through
        validation.

        This is the lightweight dependency strategy used when the transfer
        should not migrate dependency ownership. Rather than moving those
        lineages, it marks them dirty so downstream runtime state is not
        trusted blindly after the root transfer changes ownership/topology.

        Args:
            deps: Dependency spell ids whose lineages should be marked dirty.
        """
        self.check_cleaned()
        for dep_id in deps:
            try:
                dep_spell = self.source_conduit.get_spell_by_id(dep_id, self._frame_name)
                if dep_spell is None:
                    continue
                if isinstance(dep_spell.spell_index, SpellIndex):
                    self._mark_lineage_dirty(dep_spell)
            except Exception:
                continue

    # ------------------------------------------------------------------
    # Change-control / incidents
    # ------------------------------------------------------------------
    def _record_change_intent(self, summary: Dict[str, Any]) -> None:
        """
        Publish a pending-change record before the transfer mutates ownership.

        This is the change-control breadcrumb for the operation. It tells the
        surrounding governance layer that a lineage is about to undergo an
        ownership rewrite and records enough metadata for later diagnostics or
        manual inspection if the transfer fails mid-flight.

        The write is intentionally idempotent for a given `op_id`, and it is
        best-effort so observability failures do not block the runtime from
        attempting the actual ownership move.

        Args:
            summary: Preflight payload that describes the lineage, endpoints,
                borrowers, dependencies, creations, and transfer options.
        """
        self.check_cleaned()
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
        Remove the pending-change record after a successful transfer.

        Once ownership has been moved and the operation reaches its success
        path, the transfer should no longer appear as an in-flight control-plane
        rewrite. Clearing the pending-change entry is the bookkeeping step that
        closes that loop.

        Args:
            spell_index: Lineage whose pending transfer record should be
                cleared.
        """
        self.check_cleaned()
        try:
            self._change_control_manager.clear_pending_change(spell_index.id)
        except Exception:
            pass

    def _record_incident(self, summary: Dict[str, Any], exc: Exception) -> None:
        """
        Emit incident records for transfer failure or missing revalidation
        support.

        Incident emission is deliberately secondary to runtime recovery. The
        transfer first tries to restore a coherent lineage state; this helper
        then records what failed so operators or future automation can inspect
        the partial move with the same preflight metadata that informed the
        transfer itself.

        Args:
            summary: Preflight/transfer summary payload describing the affected
                lineage and participants.
            exc: Exception that triggered the failure path.
        """
        self.check_cleaned()
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

        # If no revalidator is wired for any conduit, emit a reminder incident.
        try:
            if not self._change_control_manager.has_registered_revalidators():
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
