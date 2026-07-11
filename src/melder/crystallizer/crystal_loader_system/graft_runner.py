"""
The spell-index graft runner (spell_index_graft 2026-07-12).

A graft re-integrates ONE captured index - all members, custody,
selection - into a LIVE host book through the normal verbs only: the
selected member binds ACTIVE (bind creates the fresh index and selects
it), parked members ride conduit.bind_inactive onto that new index.
Existing indexes are NEVER mutated (fresh-index-only law: the index-ops
seams belong to another lane); resident members refuse by default or
skip with a shortfall under skip_resident. Grafts are user-verb activity
(per-verb transactions), not world replays - no LoadGate span.
"""

import importlib
from typing import Any, Dict, List, Optional

from melder.utilities.general_base.cleanable import Cleanable
from melder.crystallizer.persistence.record_version import RecordVersion


class GraftRunner(Cleanable):
    """
    Re-integrate one captured spell_index into a live host book.

    Purpose:
        The finer-than-conduit restore grain (owner-approved lane): the
        graft record is the index twin's membership map plus per-member
        custody payloads; the runner replays it against a HOST the
        caller already owns.

    Contract:
        - Single-use; run() executes once and returns the detached
          report (never raises for per-member problems - shortfalls
          carry them; only structural refusals raise: version gate,
          unconjured host, resident member without skip_resident).
        - THE OVERLAP RULE (conservative resolution of the pinned open
          question): a member already resident anywhere in the host
          FRAME refuses the whole graft by default; skip_resident=True
          skips that member with the shortfall
          "member_resident_in_host_skipped". No index merging, ever.
        - Hydration v1 is the normal import lane only; retained-text
          rebuild for graft members is a flagged follow-up (the ticket
          carries it).

    Threading:
        Thread-confined to the calling thread (the host book's verbs run
        their own per-verb transactions).

    Lifecycle / Cleanup:
        cleanup() releases the carried record and host references (del
        posture); idempotent.
    """

    __slots__ = Cleanable.__slots__ + [
        "_record",
        "_host_book",
        "_skip_resident",
        "_consumed",
    ]

    def __init__(
            self,
            graft_record: Dict[str, object],
            host_spellbook: Any,
            skip_resident: bool = False,
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

        Returns:
            None.

        Raises:
            TypeError: If the record is not a dict or the host is None.
            ValueError: If the record is not a spell_index graft, or was
                written by a newer record major (RecordVersion gate).
        """
        super().__init__()
        if not isinstance(graft_record, dict):
            raise TypeError("graft_record must be a dict.")
        if host_spellbook is None:
            raise TypeError("host_spellbook cannot be None.")
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
        self._consumed: bool = False

    def cleanup(self) -> None:
        """
        Idempotently release the carried record and host references.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._record
        del self._host_book
        del self._skip_resident
        del self._consumed

    def run(self) -> Dict[str, object]:
        """
        Execute the graft against the live host book.

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
