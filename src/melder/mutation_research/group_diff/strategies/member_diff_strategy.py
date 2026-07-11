from typing import Dict, List, Optional, Tuple

from melder.mutation_research.group_diff.group_diff_strategy import (
    GroupDiffStrategy,
)


class MemberDiffStrategy(GroupDiffStrategy):
    """
    Roster comparison between two composition materials.

    Purpose:
        The default grouped strategy: answer "what changed between these
        two subsystem compositions" at MEMBER grain - who joined, who
        left, and (the semantic win over raw set math) which members are
        the SAME OBJECT at a DIFFERENT VERSION. A member that "left" and a
        member that "joined" who share a lane are one object whose version
        moved; the verdict pairs them so the agent can descend that pair
        into the normal per-spell grains (source / structural / parts).

    Contract:
        - Version movement is lane-evidenced, never guessed: two identities
          pair as `version_moved` ONLY when the resolver's members join
          places them in the SAME lane. Without residence truth in the
          material, they honestly report as removed + added.
        - Result is detached and value-typed: `identical`,
          `added_members`, `removed_members`, `version_moved`
          (`{"lane_id", "lane_name", "from_spell_id", "to_spell_id"}`
          rows), `unchanged_members`, and `ancestry_related` (whether one
          composition's parent chain names the other - the walk-vs-jump
          signal).

    Threading:
        Stateless beyond the base lifecycle flag; safe to share.

    Lifecycle:
        Owned by exactly one `GroupDiffEngine`.
    """

    __slots__ = GroupDiffStrategy.__slots__

    @property
    def name(self) -> str:
        """
        Return the stable registry name of this strategy.

        Returns:
            str:
                "members".
        """
        self.check_cleaned()
        return "members"

    def diff(
            self,
            left_material: Dict[str, object],
            right_material: Dict[str, object],
    ) -> Dict[str, object]:
        """
        Compare two composition rosters, pairing lane-evidenced moves.

        Args:
            left_material:
                Resolver material for the left composition.
            right_material:
                Resolver material for the right composition.

        Returns:
            Dict[str, object]:
                Detached verdict (see class contract).
        """
        self.check_cleaned()
        left_members = self._member_set(left_material)
        right_members = self._member_set(right_material)
        unchanged = sorted(left_members & right_members)
        raw_removed = left_members - right_members
        raw_added = right_members - left_members

        left_lanes = self._lane_join(left_material, raw_removed)
        right_lanes = self._lane_join(right_material, raw_added)
        version_moved: List[Dict[str, object]] = []
        moved_from: set = set()
        moved_to: set = set()
        for lane_id, from_spell_id, lane_name in left_lanes:
            match = next(
                (
                    (r_lane_id, to_spell_id)
                    for r_lane_id, to_spell_id, _ in right_lanes
                    if r_lane_id == lane_id and to_spell_id not in moved_to
                ),
                None,
            )
            if match is None:
                continue
            version_moved.append({
                "lane_id": lane_id,
                "lane_name": lane_name,
                "from_spell_id": from_spell_id,
                "to_spell_id": match[1],
            })
            moved_from.add(from_spell_id)
            moved_to.add(match[1])

        added = sorted(raw_added - moved_to)
        removed = sorted(raw_removed - moved_from)
        left_id = str(left_material.get("group_id"))
        right_id = str(right_material.get("group_id"))
        left_parents = [
            str(parent)
            for parent in list(left_material.get("parent_group_ids", []))
        ]
        right_parents = [
            str(parent)
            for parent in list(right_material.get("parent_group_ids", []))
        ]
        return {
            "identical": left_members == right_members,
            "added_members": added,
            "removed_members": removed,
            "version_moved": version_moved,
            "unchanged_members": unchanged,
            "ancestry_related": (
                left_id in right_parents or right_id in left_parents
            ),
        }

    @staticmethod
    def _member_set(material: Dict[str, object]) -> set:
        """
        Extract the member identity set from one material payload.

        Args:
            material:
                Resolver material payload.

        Returns:
            set:
                Member identities.
        """
        members = (
            material.get("member_spell_ids")
            if isinstance(material, dict) else None
        )
        if not isinstance(members, list):
            return set()
        return {str(member) for member in members}

    @staticmethod
    def _lane_join(
            material: Dict[str, object],
            identities: set,
    ) -> List[Tuple[str, str, Optional[str]]]:
        """
        Return (lane_id, spell_id, lane_name) rows for joined identities.

        Args:
            material:
                Resolver material payload (carries the members join when
                residence truth was available).
            identities:
                Identities to look up.

        Returns:
            List[Tuple[str, str, Optional[str]]]:
                Lane-evidenced rows; identities without a join drop out
                (they report as plain added/removed - never guessed).
        """
        join = material.get("members") if isinstance(material, dict) else None
        if not isinstance(join, dict):
            return []
        rows: List[Tuple[str, str, Optional[str]]] = []
        for spell_id in sorted(identities):
            entry = join.get(spell_id)
            if isinstance(entry, dict):
                lane_id = entry.get("lane_id")
                if isinstance(lane_id, str) and lane_id:
                    rows.append(
                        (lane_id, spell_id, entry.get("lane_name")),
                    )
        return rows
