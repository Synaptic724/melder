
from typing import ClassVar, Dict, List

from melder.__melder_registration_guard__ import (
    __melder_registration_guard__ as _mrg,
)
from melder.crystallizer.crystal_analysis.preflight.persistence_analysis_strategy import (
    PersistenceAnalysisStrategy,
)


class MutationResearchCompositionStrategy(PersistenceAnalysisStrategy):
    """
    Verify the folded MR composition's internal agreement before rebuild.

    Purpose:
        The MR build stage (mr_restore_build_stage_2026_07_11) hands the
        recorded composition to `load_recorded_composition` wholesale.
        This pass proves the payload is worth handing over: the shape
        parses, and each set's organization agrees with its residence
        partition (every lane-held spell SHA is resident under that lane;
        every residence entry points at a described lane).

    Contract:
        - BLOCKER only when the payload is UNPARSEABLE (composition/set/
          lanes/residence carry the wrong shapes) - rebuilding from a
          shape the seams cannot read would fail mid-stage.
        - Organization/residence disagreements are WARNINGS: the MR
          seams rebuild what the payload says; the disagreement is
          teach-grade drift evidence, not a refusal.
        - Absent/empty composition produces NO rows (pre-Phase-B worlds
          report through the stage's honest shortfall instead).
        - Read-only over the folded bundle (preflight law).

    Threading:
        Stateless - no instance state and no locks. One analyzer pass
        calls `analyze` once and the strategy retains nothing between
        calls, so a single instance is safe to reuse across bundles.

    Registration:
        MELDER KERNEL - guarded. Preflight strategies are constructed by
        `PersistenceAnalyzer`, never bound as spells.

    Subsystem Context:
        The NINTH default preflight row, added when the MR root joined
        the engine preflight bundle (mr_restore_build_stage_2026_07_11).
        Like `FramePostureStrategy` it is scope-blind and adjudicated
        afterwards: `LoadAdmission` reclassifies its findings as
        "expected_for_scope" on conduit-scoped and frame-scoped loads,
        because MutationResearch is a WORLD-scope root and a partial
        slice is expected not to carry it. Raw findings are never
        rewritten - the adjudication view is additive.

    System Context:
        MutationResearch is a BUILD STAGE of restore, not a passive twin:
        a checkpointed world unfolds WITH its research, and the stage
        hands the recorded composition to `load_recorded_composition`
        WHOLESALE rather than merging it key by key. That single
        handoff is what makes this pass necessary - once the payload is
        accepted there is no per-key gate downstream to catch a
        malformed shape, so an unreadable composition would fail
        mid-stage after other units are already built, forcing the
        all-or-nothing teardown.
        The severity split follows exactly from that: a shape the seams
        cannot PARSE blocks, because the handoff cannot even begin;
        organization/residence DISAGREEMENT only warns, because the
        seams will faithfully rebuild whatever the payload asserts - the
        disagreement is drift evidence for the user to read, not a
        reason to refuse their world.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Verify the folded MR composition's internal agreement before rebuild. "
        "Melder kernel machinery: read it to understand the runtime, do not drive it directly."
    )


    @property
    def name(self) -> str:
        """
        Return the strategy's stable report name.

        Returns:
            str: "mutation_research_composition".
        """
        return "mutation_research_composition"

    def analyze(
            self,
            payload_bundle: Dict[str, Dict[str, Dict[str, object]]],
    ) -> List[Dict[str, object]]:
        """
        Check every folded MR set for shape and residence agreement.

        Args:
            payload_bundle:
                {kind: {key: payload}} bundle under analysis.

        Returns:
            List[Dict[str, object]]: Blocker rows on unparseable shapes;
            warning rows on organization/residence disagreement.
        """
        findings: List[Dict[str, object]] = []
        for root_key, payload in dict(
                payload_bundle.get("mutation_research", {})
        ).items():
            composition = payload.get("composition_payload")
            if composition in (None, {}):
                continue
            if not isinstance(composition, dict):
                findings.append(self._row(
                    "blocker", root_key,
                    "composition_payload is not a dict of set payloads; "
                    "the rebuild seams cannot read it",
                ))
                continue
            for set_name, set_payload in composition.items():
                findings.extend(
                    self._check_set(str(set_name), set_payload)
                )
        return findings

    def _check_set(
            self,
            set_name: str,
            set_payload: object,
    ) -> List[Dict[str, object]]:
        """
        Validate one set payload's shape and residence agreement.

        Args:
            set_name:
                The composition key naming this set.
            set_payload:
                The recorded set organization payload.

        Returns:
            List[Dict[str, object]]: Finding rows for this set.
        """
        findings: List[Dict[str, object]] = []
        if not isinstance(set_payload, dict):
            findings.append(self._row(
                "blocker", set_name,
                "set payload is not a dict; the rebuild seams cannot "
                "read it",
            ))
            return findings
        # Shape source: ResearchSet.describe_composition() - the set
        # payload nests {organization, journal, network_snapshot_shas,
        # network_versioner}; lanes/residence live INSIDE organization.
        organization = set_payload.get("organization")
        if not isinstance(organization, dict):
            findings.append(self._row(
                "blocker", set_name,
                "set payload carries no organization dict; the rebuild "
                "seams cannot read it",
            ))
            return findings
        lanes = organization.get("lanes")
        residence = organization.get("residence")
        if not isinstance(lanes, list) or not isinstance(residence, dict):
            findings.append(self._row(
                "blocker", set_name,
                "organization lanes/residence carry the wrong shapes "
                "(expected list/dict)",
            ))
            return findings

        # Vocabulary sync 2026-07-11 (owner ruling: MR speaks spell_id):
        # NEW keys are authoritative; OLD keys (checkpoints sealed before
        # the sweep) are tolerated with a named warning - MR hydration
        # reads new keys only, so an old sealed world should reseal.
        # Node-family dispatch (GroupedResearchNode ruling 2026-07-11):
        # node_type="group" payloads identify by "group_id" - a
        # content-addressed COMPOSITION identity that claims residence
        # like any node but carries NO custody crystal by design (purely
        # informational); their pinned members are checked against the
        # residence partition below.
        legacy_keys_seen = False
        described_lane_ids = set()
        held_lane_by_spell_id: Dict[str, str] = {}
        members_by_group_id: Dict[str, List[str]] = {}
        for lane_payload in lanes:
            if not isinstance(lane_payload, dict):
                findings.append(self._row(
                    "blocker", set_name,
                    "a lane payload is not a dict; the rebuild seams "
                    "cannot read it",
                ))
                return findings
            lane_id = str(lane_payload.get("lane_id"))
            described_lane_ids.add(lane_id)
            for node_payload in list(lane_payload.get("nodes", [])):
                node = dict(node_payload)
                if node.get("node_type") == "group":
                    group_id = str(node.get("group_id"))
                    held_lane_by_spell_id[group_id] = lane_id
                    members = node.get("member_spell_ids")
                    members_by_group_id[group_id] = (
                        [str(member) for member in members]
                        if isinstance(members, list) else []
                    )
                    continue
                spell_id = node.get("spell_id")
                if spell_id is None and "spell_sha" in node:
                    spell_id = node.get("spell_sha")
                    legacy_keys_seen = True
                held_lane_by_spell_id[str(spell_id)] = lane_id

        residence_map = residence.get("lane_id_by_spell_id")
        if residence_map is None and "lane_id_by_sha" in residence:
            residence_map = residence.get("lane_id_by_sha")
            legacy_keys_seen = True
        lane_id_by_spell_id = dict(residence_map or {})
        if legacy_keys_seen:
            findings.append(self._row(
                "warning", set_name,
                "pre_vocabulary_sweep_payload: this set was sealed with "
                "the old spell_sha keys; MR hydration reads spell_id "
                "keys only - reseal the world to modernize the record",
            ))
        for spell_id, lane_id in held_lane_by_spell_id.items():
            resident_lane = lane_id_by_spell_id.get(spell_id)
            if resident_lane is None:
                findings.append(self._row(
                    "warning", set_name,
                    "lane-held spell id {0}... is not resident in the "
                    "residence partition".format(spell_id[:12]),
                ))
            elif str(resident_lane) != lane_id:
                findings.append(self._row(
                    "warning", set_name,
                    "spell id {0}... is held by lane {1} but resident "
                    "under lane {2}".format(
                        spell_id[:12], lane_id, resident_lane
                    ),
                ))
        for group_id, members in members_by_group_id.items():
            for member in members:
                if member not in lane_id_by_spell_id:
                    findings.append(self._row(
                        "warning", set_name,
                        "composition {0}... pins member {1}... that is "
                        "not resident in this set (the composition "
                        "identity itself is informational and rebuilds "
                        "fine; the missing member is drift "
                        "evidence)".format(group_id[:12], member[:12]),
                    ))
        for spell_id, lane_id in lane_id_by_spell_id.items():
            if str(lane_id) not in described_lane_ids:
                findings.append(self._row(
                    "warning", set_name,
                    "residence points spell id {0}... at lane {1}, which "
                    "the organization does not describe".format(
                        str(spell_id)[:12], lane_id
                    ),
                ))
        return findings

    def _row(
            self,
            severity: str,
            key: str,
            detail: str,
    ) -> Dict[str, object]:
        """
        Build one finding row in the shared preflight shape.

        Args:
            severity:
                "blocker" | "warning" per the class contract.
            key:
                Root or set anchor.
            detail:
                Human-facing explanation.

        Returns:
            Dict[str, object]: The finding row.
        """
        return {
            "strategy": self.name,
            "severity": severity,
            "kind": "mutation_research",
            "key": key,
            "detail": detail,
        }
