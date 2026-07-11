
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
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel

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

        described_lane_ids = set()
        held_lane_by_sha: Dict[str, str] = {}
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
                node_sha = str(dict(node_payload).get("spell_sha"))
                held_lane_by_sha[node_sha] = lane_id

        lane_id_by_sha = dict(residence.get("lane_id_by_sha", {}))
        for sha, lane_id in held_lane_by_sha.items():
            resident_lane = lane_id_by_sha.get(sha)
            if resident_lane is None:
                findings.append(self._row(
                    "warning", set_name,
                    "lane-held sha {0}... is not resident in the "
                    "residence partition".format(sha[:12]),
                ))
            elif str(resident_lane) != lane_id:
                findings.append(self._row(
                    "warning", set_name,
                    "sha {0}... is held by lane {1} but resident under "
                    "lane {2}".format(sha[:12], lane_id, resident_lane),
                ))
        for sha, lane_id in lane_id_by_sha.items():
            if str(lane_id) not in described_lane_ids:
                findings.append(self._row(
                    "warning", set_name,
                    "residence points sha {0}... at lane {1}, which the "
                    "organization does not describe".format(
                        str(sha)[:12], lane_id
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
