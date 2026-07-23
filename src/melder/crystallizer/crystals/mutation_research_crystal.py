

from typing import Dict, List, Optional

from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class MutationResearchCrystal(Cleanable):
    """
    Pure-data digital twin of the MutationResearch root's configured surface.

    Purpose:
        Carry the persistable truth of the MR root for one profile. Phase A
        recorded configuration/activation state only; Phase B (the P5 seam,
        landed with the ResearchSet build) additionally rides the research
        COMPOSITION on this same twin: research sets with their lanes,
        full-object version records, residence partition, bounded
        recent-transition windows, and retained network-snapshot addresses,
        exactly as emitted by
        `MutationResearch.describe_research_composition()`.

    Guidance:
        Interpret this twin together with the profile's
        `RecordedUnitState` for MutationResearch. The twin carries configured
        policy and composition; the later state switch decides whether restore
        leaves the rebuilt root enabled, disabled, or refuses resurrection after
        observed cleanup. Use the nested composition as hydration truth and the
        flat/grouped node rows as query-oriented projections of that same truth.

    Contract:
        - Value payload only; immutable after construction (replace-on-emit).
        - MR is codegen-lane-only at runtime, so this twin appears only in
          profiles emitted from dynamic-lane worlds.
        - `composition_payload` is optional so Phase-A emitters (the
          configuration activation seam) stay valid; None records as an
          empty composition.
        - EXPLICIT NODE OBJECTS (owner ruling 2026-07-12): the twin carries
          its research record as PROPER OBJECTS, not only as the nested
          composition blob - `research_nodes` and `grouped_research_nodes`
          are FLAT, value-typed, DB-storable rows (one per recorded node,
          each carrying its set/lane context), DERIVED from the
          composition payload at construction so the blob and the rows can
          never disagree. Storage handlers map these lists straight to
          tables; hydration keeps reading the composition (the proven
          loop); the rows are the record's queryable face.

    Threading:
        Immutable-after-init; the owning PersistenceProfile serializes
        replacement.

    Lifecycle / Cleanup:
        Owned by exactly one `PersistenceProfile`. Cleanup releases copied
        configuration/composition/node rows only and does not alter the hosted
        MutationResearch root or research sets.

    Registration:
        MELDER KERNEL - guarded. Emitted by the crystallizer's builders from live
        runtime truth and owned by one `PersistenceProfile`; never
        user-constructed or bound.

    Subsystem Context:
        One member of the crystal-twin family - the ROOT twin for MutationResearch
        - read WITH the profile's MR `RecordedUnitState`. It carries configured
        policy AND (Phase B) the research COMPOSITION emitted by
        `describe_research_composition()`: research sets with lanes, full-object
        version records, residence partition, bounded recent-transition windows,
        and retained network-snapshot addresses. Because MR is codegen-lane-only
        at runtime, this twin appears only in profiles emitted from dynamic-lane
        worlds.

    System Context:
        One node of the V3 crystallizer's serialize-then-restore model, and the
        one twin that keeps BOTH a nested hydration blob and flat derived rows.
        The nested `composition_payload` is the proven hydration loop restore
        reads; `research_nodes` / `grouped_research_nodes` are FLAT, value-typed,
        DB-storable rows DERIVED from that same blob at construction (owner ruling
        2026-07-12) so the two can never disagree. That dual shape is deliberate:
        storage handlers map the rows straight to tables (the record's queryable
        face) while hydration keeps reading the composition - one truth, two
        projections, generated together so a query can never see a node the
        rebuild loop won't.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Pure-data digital twin of the MutationResearch root's configured "
        "surface. Melder kernel machinery: read it to understand the runtime, do not drive it "
        "directly."
    )

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_activated",
        "_configuration_payload",
        "_composition_payload",
        "_research_node_rows",
        "_grouped_research_node_rows",
    ]

    def __init__(
            self,
            activated: bool,
            configuration_payload: Optional[Dict[str, object]] = None,
            composition_payload: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Initialize the MR twin from emitted root state.

        Args:
            activated:
                Whether the MR root was activated at emission time.
            configuration_payload:
                Value-typed mapping of the installed MR configuration surface.
                None is treated as an empty payload.
            composition_payload:
                Value-typed research composition (set name ->
                `ResearchSet.describe_composition()` payload). None is
                treated as an empty composition (Phase-A emitters).

        Returns:
            None.
        """
        super().__init__()
        self._activated: bool = activated
        self._configuration_payload: Dict[str, object] = (
            dict(configuration_payload) if configuration_payload else {}
        )
        self._composition_payload: Dict[str, object] = (
            dict(composition_payload) if composition_payload else {}
        )
        spell_rows, group_rows = MutationResearchCrystal._derive_node_rows(
            self._composition_payload,
        )
        self._research_node_rows: List[Dict[str, object]] = spell_rows
        self._grouped_research_node_rows: List[Dict[str, object]] = group_rows

    @staticmethod
    def _derive_node_rows(
            composition_payload: Dict[str, object],
    ) -> "tuple[List[Dict[str, object]], List[Dict[str, object]]]":
        """
        Flatten one composition into DB-storable node rows, per family.

        Contract:
            - Derivation is the agreement guarantee: rows are computed
              from the same payload the twin records, at construction -
              the blob and the objects cannot drift.
            - Best-effort over shape (isinstance guards): a twin must
              record whatever it was handed; malformed fragments simply
              contribute no rows.

        Args:
            composition_payload:
                Set name -> `describe_composition()` payload mapping.

        Returns:
            tuple[List[Dict[str, object]], List[Dict[str, object]]]:
                (research_node_rows, grouped_research_node_rows) - flat,
                value-typed, each row carrying its set/lane context.
        """
        spell_rows: List[Dict[str, object]] = []
        group_rows: List[Dict[str, object]] = []
        for set_name, set_payload in dict(composition_payload).items():
            if not isinstance(set_payload, dict):
                continue
            organization = set_payload.get("organization")
            if not isinstance(organization, dict):
                continue
            lanes = organization.get("lanes")
            if not isinstance(lanes, list):
                continue
            for lane_payload in lanes:
                if not isinstance(lane_payload, dict):
                    continue
                lane_context = {
                    "set_name": str(set_name),
                    "lane_id": lane_payload.get("lane_id"),
                    "lane_name": lane_payload.get("name"),
                    "lane_type": lane_payload.get("lane_type"),
                }
                for node in list(lane_payload.get("nodes", [])):
                    if not isinstance(node, dict):
                        continue
                    if node.get("node_type") == "group":
                        group_rows.append({
                            **lane_context,
                            "group_id": node.get("group_id"),
                            "member_spell_ids": list(
                                node.get("member_spell_ids", [])
                            ),
                            "parent_group_ids": list(
                                node.get("parent_group_ids", [])
                            ),
                            "author": node.get("author"),
                            "campaign": node.get("campaign"),
                            "reason": node.get("reason"),
                            "created_at": node.get("created_at"),
                        })
                    else:
                        spell_rows.append({
                            **lane_context,
                            "spell_id": node.get("spell_id"),
                            "module_source_sha256": node.get(
                                "module_source_sha256"
                            ),
                            "parent_spell_ids": list(
                                node.get("parent_spell_ids", [])
                            ),
                            "author": node.get("author"),
                            "campaign": node.get("campaign"),
                            "reason": node.get("reason"),
                            "created_at": node.get("created_at"),
                        })
        return spell_rows, group_rows

    def cleanup(self) -> None:
        """
        Release owned fields and mark the twin cleaned.

        Contract:
            - Idempotent; del posture (no tombstones).

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._activated
        del self._configuration_payload
        del self._composition_payload
        del self._research_node_rows
        del self._grouped_research_node_rows

    @property
    def activated(self) -> bool:
        """
        Return whether the MR root was activated at emission.

        Contract:
            - Emission-time activation flag; the profile's MR RecordedUnitState
              decides enabled/disabled/refuse-resurrection at restore.

        Returns:
            bool:
                Recorded activation flag.
        """
        self.check_cleaned()
        return self._activated

    @property
    def configuration_payload(self) -> Dict[str, object]:
        """
        Return a detached copy of the recorded MR configuration surface.

        Contract:
            - A FRESH copy of the installed MR configuration surface; mutating
              it never touches the twin.

        Returns:
            Dict[str, object]:
                Detached mapping of configured property name -> value.
        """
        self.check_cleaned()
        return dict(self._configuration_payload)

    @property
    def composition_payload(self) -> Dict[str, object]:
        """
        Return a detached copy of the recorded research composition.

        Contract:
            - A FRESH copy of the nested research composition - the HYDRATION
              carrier (the proven restore loop reads this, not the flat rows).

        Returns:
            Dict[str, object]:
                Detached mapping of set name -> composition payload
                (organization + bounded journal window + snapshot addresses).
        """
        self.check_cleaned()
        return dict(self._composition_payload)

    @property
    def research_nodes(self) -> List[Dict[str, object]]:
        """
        Return the recorded ResearchNodes as flat, DB-storable rows.

        Contract:
            - DERIVED from `composition_payload` at construction (blob and rows
              cannot disagree); returns detached row copies - the queryable,
              DB-storable face of the spell-version records.

        Returns:
            List[Dict[str, object]]:
                One row per spell version record: `{"set_name", "lane_id",
                "lane_name", "lane_type", "spell_id",
                "module_source_sha256", "parent_spell_ids", "author",
                "campaign", "reason", "created_at"}` (detached copies).
        """
        self.check_cleaned()
        return [dict(row) for row in self._research_node_rows]

    @property
    def grouped_research_nodes(self) -> List[Dict[str, object]]:
        """
        Return the recorded GroupedResearchNodes as flat, DB-storable rows.

        Contract:
            - DERIVED from `composition_payload` at construction; returns
              detached row copies - the DB-storable face of the composition
              records.

        Returns:
            List[Dict[str, object]]:
                One row per composition record: `{"set_name", "lane_id",
                "lane_name", "lane_type", "group_id", "member_spell_ids",
                "parent_group_ids", "author", "campaign", "reason",
                "created_at"}` (detached copies).
        """
        self.check_cleaned()
        return [dict(row) for row in self._grouped_research_node_rows]

    def describe(self) -> Dict[str, object]:
        """
        Return a detached, serialization-ready snapshot of this twin.

        Returns:
            Dict[str, object]:
                Plain-value payload (the cached-item form for this twin):
                the composition blob (the hydration carrier) PLUS the
                explicit per-family node rows (the DB-storable objects).

        Contract:
            - Detached cached-item form carrying `twin_kind:
              "mutation_research"`; blob and node rows are derived from one
              source so they cannot disagree.
        """
        self.check_cleaned()
        return {
            "twin_kind": "mutation_research",
            "activated": self._activated,
            "configuration_payload": dict(self._configuration_payload),
            "composition_payload": dict(self._composition_payload),
            "research_nodes": [
                dict(row) for row in self._research_node_rows
            ],
            "grouped_research_nodes": [
                dict(row) for row in self._grouped_research_node_rows
            ],
        }
