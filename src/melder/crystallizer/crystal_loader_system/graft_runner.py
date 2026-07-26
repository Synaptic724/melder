"""
The spell-index graft runner (spell_index_graft 2026-07-12).

A graft re-integrates ONE captured index - all members, custody,
selection - into a LIVE host book through the normal verbs only: the
selected member binds ACTIVE (bind creates the fresh index and selects
it), parked members ride conduit.bind_inactive onto that new index.
Fresh-index-only is the DEFAULT; existing indexes are never touched
through internals. The opt-in MERGE MODE (finishing slice 3,
2026-07-11, dial owner-delegated + decided) grows a caller-named live
index instead - still exclusively through its own public verbs
(bind_inactive to park, notch_spell to optionally adopt the recorded
selection). Historical note: the original "no index merging, ever" law
protected the then-unfinished index-ops seams; those seams shipped
(conduit.py:4003/:4075), which is what made a safe merge lane possible.
Resident members refuse by default or skip with a shortfall under
skip_resident, identically in both modes. Grafts are user-verb activity
(per-verb transactions), not world replays - no LoadGate span.
"""

import importlib
from typing import Any, Dict, List, Optional, Tuple

from melder.utilities.general_base.cleanable import Cleanable
from melder.crystallizer.persistence.record_version import RecordVersion


class GraftRunner(Cleanable):
    """
    Re-integrate one captured spell_index into a live host book.

    Purpose:
        The finer-than-conduit restore grain: replay one captured index's
        membership, custody, and selection into a live host spellbook through
        ordinary public bind/notch verbs.

    Guidance:
        Prefer `Crystallizer.graft_index(...)` instead of constructing this
        runner directly. Choose the default fresh-index mode when the captured
        membership should arrive as an independent index. Supply
        `merge_into_index` only when intentionally growing an existing live
        index; `adopt_recorded_selection` controls whether that merge also moves
        its active member. A graft is a sequence of admitted public mutations,
        not a world-load transaction, so inspect `shortfalls` and do not assume
        graft-wide atomicity.

    Contract:
        - Single-use; run() executes once and returns the detached
          report (never raises for per-member problems - shortfalls
          carry them; only structural refusals raise: version gate,
          unconjured host, resident member without skip_resident).
        - INDEX IDENTITY IS DISPOSABLE (owner ruling 2026-07-11: "the
          index_id doesn't matter, it's just about what spells are in
          it"): a graft's contract is MEMBERSHIP placement, never index
          identity preservation. The report's recorded/live index ids
          are traceability only; fresh ids mint freely (the
          never-rehydrate-ULIDs law applied to indexes).
        - EVERY structural write rides the owner's mediator: the runner
          only ever calls the self-admitting public verbs
          (bind / bind_inactive / notch_spell -> the bind and notch
          transaction families). Grafts are per-verb transactions by
          design - each member entry is its own admission; there is no
          umbrella claim spanning the graft (graft-level atomicity
          against concurrent structural ops is a recorded future
          decision, not an improvised bypass).
        - THE OVERLAP RULE (conservative resolution of the pinned open
          question): a member already resident anywhere in the host
          FRAME refuses the whole graft by default; skip_resident=True
          skips that member with the shortfall
          "member_resident_in_host_skipped". Applies identically in
          merge mode. Index internals are never touched in either mode
          (merge grows the target through its own public verbs only).
        - Hydration uses the normal import lane first. When the target is
          absent and retained user-source text exists, the shared
          `user_world_rebuild` lane rebuilds missing modules parents-first and
          retries the import exactly once; live files always win.

    Threading:
        Thread-confined to the calling thread (the host book's verbs run
        their own per-verb transactions).

    Lifecycle / Cleanup:
        cleanup() releases the carried record and host references (del
        posture); idempotent.

    Registration:
        MELDER KERNEL - guarded (internal manifest). A single-use runner reached
        through `Crystallizer.graft_index(...)`; not directly user-constructed or bound.
        access=internal.

    Subsystem Context:
        The finer-than-conduit restore grain of THE UNFOLD: it replays one captured spell_index
        (membership, custody, selection) into a LIVE host spellbook through ordinary public
        bind / bind_inactive / notch verbs. Unlike a world load it is NOT one transaction - each
        member entry is its own self-admitting per-verb transaction; only structural refusals
        raise, per-member problems ride `shortfalls`.

    System Context:
        Crystallizer layer (position 2). Index identity is disposable (owner ruling: a graft's
        contract is MEMBERSHIP placement, never index-id preservation - fresh ids mint freely,
        the never-rehydrate-ULIDs law applied to indexes), and every structural write rides the
        host's own mediator, so a graft is admitted work rather than an engine bypass.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Re-integrate one captured spell_index into a live host book. Melder
        kernel machinery: read it to understand the runtime, do not drive it directly.
    """

    __slots__ = Cleanable.__slots__ + [
        "_record",
        "_host_book",
        "_skip_resident",
        "_merge_into_index",
        "_adopt_recorded_selection",
        "_consumed",
    ]

    def __init__(
            self,
            graft_record: Dict[str, object],
            host_spellbook: Any,
            skip_resident: bool = False,
            merge_into_index: Optional[Any] = None,
            adopt_recorded_selection: bool = False,
    ) -> None:
        """
        Initialize one single-use runner.

        Args:
            graft_record:
                The versioned record from capture_index_graft.
            host_spellbook:
                The LIVE book receiving the graft (must be conjured
                before run()).
            skip_resident:
                True skips members already resident in the host frame
                (shortfall per member); False refuses the whole graft on
                the first resident member.
            merge_into_index:
                MERGE MODE (finishing slice 3, dial decided 2026-07-11):
                a LIVE SpellIndex object in the host frame. When given,
                NO fresh index is created - every graftable member
                parks onto this existing index through the public
                bind_inactive verb (the target's own selection stays
                active). Live-object parameter by the graft_index
                facade precedent; fresh-index-only remains the DEFAULT.
            adopt_recorded_selection:
                Merge-mode only: when True and the record's selected
                member grafts in, notch it active on the target index
                through the public conduit notch_spell verb. Default
                False (the target index keeps its current selection).

        Returns:
            None.

        Raises:
            TypeError: If the record is not a dict or the host is None.
            ValueError: If the record is not a spell_index graft, was
                written by a newer record major (RecordVersion gate),
                or adopt_recorded_selection is set without a merge
                target (selection adoption is a merge-mode concept).
        """
        super().__init__()
        if not isinstance(graft_record, dict):
            raise TypeError("graft_record must be a dict.")
        if host_spellbook is None:
            raise TypeError("host_spellbook cannot be None.")
        if adopt_recorded_selection and merge_into_index is None:
            raise ValueError(
                "adopt_recorded_selection requires merge_into_index; a "
                "fresh-index graft always selects the recorded member "
                "already."
            )
        RecordVersion.check_readable(
            graft_record,
            "index graft {0!r}".format(graft_record.get("index_id")),
        )
        if str(graft_record.get("graft_kind")) != "spell_index":
            raise ValueError(
                "graft_record carries graft_kind {0!r}; this runner "
                "grafts spell_index records only.".format(
                    graft_record.get("graft_kind")
                )
            )
        self._record: Dict[str, object] = dict(graft_record)
        self._host_book: Any = host_spellbook
        self._skip_resident: bool = bool(skip_resident)
        self._merge_into_index: Optional[Any] = merge_into_index
        self._adopt_recorded_selection: bool = bool(
            adopt_recorded_selection
        )
        self._consumed: bool = False

    def cleanup(self) -> None:
        """
        Idempotently release the carried record and host references.

        Contract:
            Terminal for this runner. Cleanup releases only the detached graft
            record and borrowed live references; it does not undo completed
            binds, parked members, selection changes, or rebuilt modules.

        Returns:
            None.

        Threading:
            Must run on the owning thread after `run()` has returned or raised.

        Lifecycle / Cleanup:
            The facade constructs one runner per graft request and cleans it in
            `finally`; successful runtime mutations have already transferred to
            their normal owners.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._record
        del self._host_book
        del self._skip_resident
        del self._merge_into_index
        del self._adopt_recorded_selection
        del self._consumed

    def run(self) -> Dict[str, object]:
        """
        Execute the graft against the live host book.

        Guidance:
            Treat structural exceptions as a refused graft. A `complete` report
            may still contain member-level shortfalls; inspect them before
            considering the requested membership fully reconstructed.

        Contract:
            Consumes the runner before host validation, so any return or error
            makes the instance non-reusable. Per-member hydration failures are
            reported as shortfalls; structural refusals raise. Fresh-index and
            merge modes both mutate only through public transaction-admitting
            verbs and return newly allocated report containers.

        Returns:
            Dict[str, object]:
                {"status": "complete", "recorded_index_id",
                 "live_index_id", "members_bound", "members_parked",
                 "skipped_resident": [ids], "shortfalls": [rows]}.

        Raises:
            RuntimeError: If cleaned, already consumed, the host book is
                not conjured, or a resident member is met without
                skip_resident.
            ValueError: If the record carries no selected member with
                custody (nothing to anchor the fresh index on).
        """
        self.check_cleaned()
        if self._consumed:
            raise RuntimeError(
                "GraftRunner is single-use; capture a fresh record and "
                "construct a new runner."
            )
        self._consumed = True

        host_conduit = self._host_book.conduit
        if host_conduit is None:
            raise RuntimeError(
                "The host spellbook has not conjured; graft after "
                "conjure so parked members have a live conduit."
            )
        index_payload = dict(self._record.get("index_payload", {}))
        members = dict(self._record.get("members", {}))
        selected_id = index_payload.get("selected_spell_id")
        shortfalls: List[Dict[str, object]] = []
        skipped: List[str] = []
        for missing_id in list(
                self._record.get("members_without_custody", [])
        ):
            shortfalls.append({
                "member": str(missing_id),
                "reason": "captured_without_custody_not_graftable",
            })

        self._refuse_or_skip_residents(members, skipped, shortfalls)

        # MERGE MODE (finishing slice 3): every graftable member parks
        # onto the caller's existing live index through the public
        # verbs; no fresh index, no anchor requirement, the target's
        # selection stands unless adoption was requested.
        if self._merge_into_index is not None:
            parked, selection_adopted = self._merge_members(
                selected_id, members, host_conduit, shortfalls
            )
            return {
                "status": "complete",
                "recorded_index_id": str(self._record.get("index_id")),
                "live_index_id": str(self._merge_into_index.id),
                "merged_into_existing": True,
                "selection_adopted": selection_adopted,
                "members_bound": 0,
                "members_parked": parked,
                "skipped_resident": skipped,
                "shortfalls": shortfalls,
            }

        if selected_id is None or str(selected_id) not in members:
            raise ValueError(
                "The graft record carries no graftable SELECTED member; "
                "a fresh index needs its anchor bind."
            )

        live_index_id, bound = self._bind_selected(
            str(selected_id), members, shortfalls
        )
        parked = self._park_members(
            str(selected_id), members, host_conduit, shortfalls
        )
        return {
            "status": "complete",
            "recorded_index_id": str(self._record.get("index_id")),
            "live_index_id": live_index_id,
            "merged_into_existing": False,
            "selection_adopted": True,
            "members_bound": bound,
            "members_parked": parked,
            "skipped_resident": skipped,
            "shortfalls": shortfalls,
        }

    def _refuse_or_skip_residents(
            self,
            members: Dict[str, Dict[str, object]],
            skipped: List[str],
            shortfalls: List[Dict[str, object]],
    ) -> None:
        """
        Apply the overlap rule over the host frame's residence.

        Contract:
            - Mutates `members` (skipped entries removed), `skipped`,
              and `shortfalls` in place.

        Args:
            members:
                spell_id -> member entry map (graftable set).
            skipped:
                Collector for skipped member ids.
            shortfalls:
                Collector for honest rows.

        Raises:
            RuntimeError: On the first resident member when
                skip_resident is False.
        """
        host_frame = self._host_book._aetheric_frame
        for spell_id in list(members.keys()):
            if host_frame.find_index_for_spell(spell_id) is None:
                continue
            if not self._skip_resident:
                raise RuntimeError(
                    "Member {0!r} is already resident in the host frame; "
                    "grafting never mutates existing indexes. Pass "
                    "skip_resident=True to graft the remaining "
                    "members.".format(spell_id)
                )
            members.pop(spell_id)
            skipped.append(spell_id)
            shortfalls.append({
                "member": spell_id,
                "reason": "member_resident_in_host_skipped",
            })

    def _bind_selected(
            self,
            selected_id: str,
            members: Dict[str, Dict[str, object]],
            shortfalls: List[Dict[str, object]],
    ) -> tuple:
        """
        Bind the selected member ACTIVE - the fresh index's anchor.

        Args:
            selected_id:
                The recorded selection.
            members:
                Graftable member map.
            shortfalls:
                Collector for honest rows.

        Returns:
            tuple: (live_index_id or None, members_bound count).

        Raises:
            ValueError: If the selected member's target cannot hydrate
                (the anchor bind is structural - no anchor, no graft).
        """
        crystal = dict(members[selected_id].get("payload", {}))
        target = self._hydrate(selected_id, crystal, shortfalls)
        if target is None:
            raise ValueError(
                "The selected member {0!r} could not hydrate; the graft "
                "has no anchor (see shortfalls for the cause).".format(
                    selected_id
                )
            )
        new_spell_id = self._host_book.bind(
            spell=target,
            existence=str(crystal.get("existence_name", "unique")),
            permissions=str(crystal.get("permissions_name", "create")),
            spellframe=crystal.get("spellframe_name"),
            binding_name=crystal.get("binding_name"),
            disposal_method_names=list(
                crystal.get("disposal_method_names", [])
            ) or None,
            profile=str(crystal.get("profile_family", "general")),
        )
        live_spell = self._host_book.find_spell_by_id(new_spell_id)
        live_index_id = (
            live_spell.spell_index.id if live_spell is not None else None
        )
        return live_index_id, 1

    def _park_members(
            self,
            selected_id: str,
            members: Dict[str, Dict[str, object]],
            host_conduit: Any,
            shortfalls: List[Dict[str, object]],
    ) -> int:
        """
        Park every non-selected member onto the fresh live index.

        Args:
            selected_id:
                The already-bound anchor member.
            members:
                Graftable member map.
            host_conduit:
                The host book's live conduit (bind_inactive host).
            shortfalls:
                Collector for honest rows.

        Returns:
            int: Members parked.
        """
        anchor_spell = self._host_book.find_spell_by_id(selected_id)
        anchor_index = (
            anchor_spell.spell_index if anchor_spell is not None else None
        )
        parked = 0
        for spell_id, entry in members.items():
            if spell_id == selected_id:
                continue
            crystal = dict(entry.get("payload", {}))
            target = self._hydrate(spell_id, crystal, shortfalls)
            if target is None:
                continue
            if anchor_index is None:
                shortfalls.append({
                    "member": spell_id,
                    "reason": "anchor_index_unresolvable_member_skipped",
                })
                continue
            host_conduit.bind_inactive(
                spell=target,
                spell_index=anchor_index,
                existence=str(crystal.get("existence_name", "unique")),
                permissions=str(crystal.get("permissions_name", "create")),
                spellframe=crystal.get("spellframe_name"),
                binding_name=crystal.get("binding_name"),
                profile=str(crystal.get("profile_family", "general")),
            )
            parked += 1
        return parked

    def _merge_members(
            self,
            selected_id: Optional[object],
            members: Dict[str, Dict[str, object]],
            host_conduit: Any,
            shortfalls: List[Dict[str, object]],
    ) -> Tuple[int, bool]:
        """
        Park every graftable member onto the existing merge target.

        Purpose:
            The merge lane (finishing slice 3): existing-index growth
            through the SAME public verbs the fresh lane uses -
            bind_inactive parks each member onto the caller's live
            index; notch_spell optionally adopts the recorded
            selection. Index internals stay untouched.

        Contract:
            - Spell SHAs are content-derived and stable, so the
              recorded selected id addresses the freshly parked live
              spell directly for the adoption notch.
            - Adoption is honest: requested-but-ungrafted selection
              lands a shortfall instead of a silent no-op.

        Args:
            selected_id:
                The record's selected member id (adoption target).
            members:
                Graftable member map (residents already removed).
            host_conduit:
                The host book's live conduit (public-verb host).
            shortfalls:
                Collector for honest rows.

        Returns:
            Tuple[int, bool]: (members parked, selection adopted).
        """
        parked = 0
        for spell_id, entry in members.items():
            crystal = dict(entry.get("payload", {}))
            target = self._hydrate(spell_id, crystal, shortfalls)
            if target is None:
                continue
            host_conduit.bind_inactive(
                spell=target,
                spell_index=self._merge_into_index,
                existence=str(crystal.get("existence_name", "unique")),
                permissions=str(crystal.get("permissions_name", "create")),
                spellframe=crystal.get("spellframe_name"),
                binding_name=crystal.get("binding_name"),
                profile=str(crystal.get("profile_family", "general")),
            )
            parked += 1
        selection_adopted = False
        if self._adopt_recorded_selection:
            # TRIAGE (2026-07-12): the first cut resolved the adoptee via
            # find_spell_by_id, which returns the index's ACTIVE spell
            # for ANY member id (spellbook.py:1852-1855) - so adoption
            # notched the target's own current selection (a self-notch)
            # and the selection never moved. _get_owned_spell is the
            # member-resolution seam the notch harness itself uses: it
            # returns the owned spell active OR PARKED (the merged
            # member is parked by construction). Read-only seam; the
            # mediated write remains the public notch verb below.
            adopted_spell = (
                self._host_book._get_owned_spell(str(selected_id))
                if selected_id is not None
                else None
            )
            if adopted_spell is None:
                shortfalls.append({
                    "member": str(selected_id),
                    "reason": "recorded_selection_not_grafted_not_adopted",
                })
            else:
                host_conduit.notch_spell(
                    spell_index=self._merge_into_index,
                    spell=adopted_spell,
                )
                selection_adopted = True
        return parked, selection_adopted

    def _hydrate(
            self,
            spell_id: str,
            crystal: Dict[str, object],
            shortfalls: List[Dict[str, object]],
    ) -> Optional[Any]:
        """
        Hydrate one member's bind target through the normal import lane.

        Contract:
            - The normal import lane first; on failure, ABSENT retained
              user modules rebuild through the shared user-world lane
              (live files always win) and the import retries exactly
              once - the S2 custody law, identical to the engine's.
              Grafted synthetic modules persist as normal user activity
              (no all-or-nothing stack: a graft is user-verb work).
            - Every failure is an honest shortfall, never a raise.

        Args:
            spell_id:
                The member's custody identity (shortfall anchor).
            crystal:
                The member's custody payload.
            shortfalls:
                Collector for honest rows.

        Returns:
            Optional[Any]: The live target, or None (shortfall filed).
        """
        from melder.crystallizer.crystal_loader_system.user_world_rebuild import (
            rebuild_absent_user_modules,
        )

        if str(crystal.get("rebindability")) != "hydratable":
            shortfalls.append({
                "member": spell_id,
                "reason": "replay_required_target_kind: {0}".format(
                    crystal.get("root_target_kind")
                ),
            })
            return None
        module_name = str(crystal.get("root_module_name"))
        qualname = str(crystal.get("root_target_qualname"))
        try:
            return self._import_target(module_name, qualname)
        except Exception as error:
            rebuilt = rebuild_absent_user_modules(
                spell_id,
                crystal,
                lambda module: None,
                lambda reason: shortfalls.append(
                    {"member": spell_id, "reason": reason}
                ),
            )
            if rebuilt:
                try:
                    return self._import_target(module_name, qualname)
                except Exception as retry_error:
                    error = retry_error
            shortfalls.append({
                "member": spell_id,
                "reason": "hydration_failed ({0}.{1}): {2}".format(
                    module_name, qualname, error
                ),
            })
            return None

    @staticmethod
    def _import_target(module_name: str, qualname: str) -> Any:
        """
        Import one module and walk the qualname to the bind target.

        Args:
            module_name:
                Canonical module to import.
            qualname:
                Dotted attribute path to the target.

        Returns:
            Any: The live class/function target.

        Raises:
            Exception: Any import or attribute-walk failure (the caller
                owns shortfall reporting and the retained-source retry).
        """
        module = importlib.import_module(module_name)
        target: Any = module
        for part in qualname.split("."):
            target = getattr(target, part)
        return target
