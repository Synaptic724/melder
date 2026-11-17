

import threading
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.mutation_research.research_set.research_composition_view import (
        ResearchCompositionView,
    )

# The recorded composition and the rows derived from it: (composition payload, research node rows, grouped node
# rows).
MaterializedComposition = Tuple[Dict[str, object], List[Dict[str, object]], List[Dict[str, object]]]


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
        - TWO WAYS IN (#331, 0.2.8306): a `composition_payload` (the
          configuration docking path, tests) is copied and its rows derived
          at construction, as before; a `composition_view` (the root's
          emission after every mutating verb) is held as references and
          materialized - payload and rows - on the twin's FIRST READ, then
          dropped. Every read returns what a twin built from the materialized
          payload returns, so readers cannot tell the two apart; emitting
          costs nothing per recorded node.

    Threading:
        Immutable-after-init as a value; the first read of a view-built twin
        materializes under `_materialize_lock`, so concurrent first reads
        build it once. The owning PersistenceProfile serializes replacement.

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

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Pure-data digital twin of the MutationResearch root's configured
        surface. Melder kernel machinery: read it to understand the runtime, do not drive it
        directly.
    """

    __slots__ = Cleanable.__slots__ + [
        "_activated",
        "_configuration_payload",
        "_composition",
        "_composition_view",
        "_materialize_lock",
    ]

    def __init__(
            self,
            activated: bool,
            configuration_payload: Optional[Dict[str, object]] = None,
            composition_payload: Optional[Dict[str, object]] = None,
            *,
            composition_view: Optional[ResearchCompositionView] = None,
    ) -> None:
        """
        Initialize the MR twin from emitted root state.

        Contract:
            - At most one composition source: a payload is copied and its rows
              derived now; a view is held and materialized on the first read
              (#331). Neither records an empty composition.

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
            composition_view:
                The root's composition view (kernel-internal, the emission
                path); the twin takes ownership and cleans it.

        Raises:
            ValueError:
                If both `composition_payload` and `composition_view` are given.

        Returns:
            None.
        """
        super().__init__()
        if composition_payload is not None and composition_view is not None:
            raise ValueError(
                "MutationResearchCrystal takes a composition_payload or a composition_view, not both."
            )
        self._activated: bool = activated
        self._configuration_payload: Dict[str, object] = (
            dict(configuration_payload) if configuration_payload else {}
        )
        # The recorded composition and its rows; None until a view-built twin is first read (#331).
        self._composition: Optional[MaterializedComposition] = None
        self._composition_view: Optional[ResearchCompositionView] = composition_view
        self._materialize_lock: threading.Lock = threading.Lock()
        if composition_view is None:
            self._composition = MutationResearchCrystal._with_rows(
                dict(composition_payload) if composition_payload else {},
            )

    @staticmethod
    def _with_rows(composition_payload: Dict[str, object]) -> MaterializedComposition:
        """
        Pair one composition payload with the rows derived from it.

        Args:
            composition_payload:
                The detached composition (set name -> payload) a twin records.

        Returns:
            MaterializedComposition: (payload, research node rows, grouped node rows).
        """
        spell_rows, group_rows = MutationResearchCrystal._derive_node_rows(
            composition_payload,
        )
        return composition_payload, spell_rows, group_rows

    def _materialized(self) -> MaterializedComposition:
        """
        Return the composition payload and both row lists, materializing a held view once.

        Contract:
            - A view-built twin materializes on its first call (under
              `_materialize_lock`), derives its rows, then cleans and drops the
              view; later calls return the kept values. A payload-built twin
              returns its values at once.

        Threading:
            The view check and materialization run under `_materialize_lock`;
            the kept values are never replaced afterwards.

        Returns:
            MaterializedComposition:
                (composition payload, research node rows, grouped node rows),
                the twin's own objects - callers copy before handing them on.

        Raises:
            RuntimeError:
                If the twin holds neither a composition nor a view - a broken
                construction invariant, never a state a caller can reach.
        """
        with self._materialize_lock:
            if self._composition is None and self._composition_view is not None:
                self._composition = MutationResearchCrystal._with_rows(
                    self._composition_view.materialize(),
                )
                self._composition_view.cleanup()
                self._composition_view = None
            if self._composition is None:
                raise RuntimeError(
                    "MutationResearchCrystal holds neither a composition nor a composition view."
                )
            return self._composition

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
            - A view never materialized is cleaned here (#331); the research
              parts it referenced are not touched.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        with self._materialize_lock:
            if self._composition_view is not None:
                self._composition_view.cleanup()
            del self._composition_view
        del self._activated
        del self._configuration_payload
        del self._composition
        del self._materialize_lock

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
        composition_payload, _, _ = self._materialized()
        return dict(composition_payload)

    @property
    def research_nodes(self) -> List[Dict[str, object]]:
        """
        Return the recorded ResearchNodes as flat, DB-storable rows.

        Contract:
            - DERIVED from `composition_payload` at construction, or at the first
              read of a view-built twin (blob and rows cannot disagree); returns
              detached row copies - the queryable, DB-storable face of the
              spell-version records.

        Returns:
            List[Dict[str, object]]:
                One row per spell version record: `{"set_name", "lane_id",
                "lane_name", "lane_type", "spell_id",
                "module_source_sha256", "parent_spell_ids", "author",
                "campaign", "reason", "created_at"}` (detached copies).
        """
        self.check_cleaned()
        _, research_node_rows, _ = self._materialized()
        return [dict(row) for row in research_node_rows]

    @property
    def grouped_research_nodes(self) -> List[Dict[str, object]]:
        """
        Return the recorded GroupedResearchNodes as flat, DB-storable rows.

        Contract:
            - DERIVED from `composition_payload` at construction, or at the first
              read of a view-built twin; returns detached row copies - the
              DB-storable face of the composition records.

        Returns:
            List[Dict[str, object]]:
                One row per composition record: `{"set_name", "lane_id",
                "lane_name", "lane_type", "group_id", "member_spell_ids",
                "parent_group_ids", "author", "campaign", "reason",
                "created_at"}` (detached copies).
        """
        self.check_cleaned()
        _, _, grouped_research_node_rows = self._materialized()
        return [dict(row) for row in grouped_research_node_rows]

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
            - A view-built twin materializes on this first read (#331).
        """
        self.check_cleaned()
        composition_payload, research_node_rows, grouped_research_node_rows = self._materialized()
        return {
            "twin_kind": "mutation_research",
            "activated": self._activated,
            "configuration_payload": dict(self._configuration_payload),
            "composition_payload": dict(composition_payload),
            "research_nodes": [
                dict(row) for row in research_node_rows
            ],
            "grouped_research_nodes": [
                dict(row) for row in grouped_research_node_rows
            ],
        }
