from typing import Dict, List, Optional, Tuple, ClassVar

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
        member that "joined" who are the same object at two versions pair
        as a move; the verdict pairs them so the agent can descend that
        pair into the normal per-spell grains (source / structural / parts).

    Contract:
        - Version movement is evidenced twice, never guessed (BUG-046):
          two identities pair as `version_moved` ONLY when the resolver's
          members join places them in the SAME lane AND the pair is
          ancestry-related in either direction through the members'
          transitive `ancestor_spell_ids`. A shared catch-all lane alone
          never fabricates movement; without residence truth or a recorded
          version relation, identities honestly report as removed + added.
        - Result is detached and value-typed: `identical`,
          `added_members`, `removed_members`, `version_moved`
          (`{"lane_id", "lane_name", "from_spell_id", "to_spell_id"}`
          rows), `unchanged_members`, and `ancestry_related` (whether one
          composition's TRANSITIVE parent chain names the other - the
          walk-vs-jump signal; BUG-045).

    Threading:
        Stateless beyond the base lifecycle flag; safe to share.

    Lifecycle:
        Owned by exactly one `GroupDiffEngine`.

    Registration:
        MELDER KERNEL - guarded. Shipped implementation; the base
        `GroupDiffStrategy` is itself GUARDED, and user strategies remain bindable anyway:
        manifest lookup is an EXACT `(module, qualname)` match that does not
        inherit, so a user's own strategy carries its own identity, is absent from
        the manifest, and binds normally.

    Subsystem Context:
        The only shipped composition-grain strategy, mirroring the three
        spell-grain strategies in `diff/strategies/`. Its verdict is the bridge
        between grains: a `version_moved` pair names two spell identities, which
        an agent can then descend into `source` / `structural` / `parts` to see
        what actually changed inside the member.

    System Context:
        The evidence discipline is the whole design. Set math alone would report
        every version bump as a removal plus an addition, which reads as
        churn rather than evolution. Pairing them as a MOVE requires two
        independent facts - same lane in the residence join, and an ancestry
        relation through the transitive parent chain - and absent either one the
        strategy reports removed-plus-added honestly rather than guessing. A
        shared catch-all lane can never manufacture a move on its own.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Roster comparison between two composition materials. Melder kernel "
        "machinery: read it to understand the runtime, do not drive it directly."
    )

    __slots__ = GroupDiffStrategy.__slots__

    @property
    def name(self) -> str:
        """
        Return the stable registry name of this strategy.

        Contract:
            - Fixed key "members" - the name `GroupDiffEngine` registers this
              roster strategy under and resolves it by. It is also the
              engine's default, so an unqualified composition diff lands here.

        Returns:
            str:
                "members".

        Raises:
            RuntimeError:
                If the strategy has been cleaned.
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

        Contract:
            - Members present on both sides are `unchanged_members`; the set
              differences seed the raw removed and added pools.
            - A removal and an addition pair as `version_moved` ONLY on
              twofold evidence (BUG-046): the resolver's members join places
              both in the SAME lane AND the two identities are ancestry-
              related in either direction through the members' transitive
              `ancestor_spell_ids`. Each identity is consumed at most once; a
              shared catch-all lane alone never fabricates a move, and absent
              either fact the identities stay honest added/removed.
            - `ancestry_related` reports whether one composition's TRANSITIVE
              parent chain names the other (BUG-045: any recorded ancestor
              hop, with direct parents as the fallback for older detached
              payloads) - the walk-vs-jump signal.
            - READ-ONLY: neither material is retained or mutated; `identical`
              is the exact-roster rollup (equal member sets).

        Args:
            left_material:
                Resolver material for the left composition.
            right_material:
                Resolver material for the right composition.

        Returns:
            Dict[str, object]:
                Detached verdict (see class contract).

        Raises:
            RuntimeError:
                If the strategy has been cleaned.
        """
        self.check_cleaned()
        left_members = self._member_set(left_material)
        right_members = self._member_set(right_material)
        unchanged = sorted(left_members & right_members)
        raw_removed = left_members - right_members
        raw_added = right_members - left_members

        left_lanes = self._lane_join(left_material, raw_removed)
        right_lanes = self._lane_join(right_material, raw_added)
        left_ancestry = self._member_ancestry(left_material)
        right_ancestry = self._member_ancestry(right_material)
        version_moved: List[Dict[str, object]] = []
        moved_from: set = set()
        moved_to: set = set()
        for lane_id, from_spell_id, lane_name in left_lanes:
            match = next(
                (
                    (r_lane_id, to_spell_id)
                    for r_lane_id, to_spell_id, _ in right_lanes
                    if r_lane_id == lane_id
                    and to_spell_id not in moved_to
                    # Version truth (BUG-046): a move is the SAME object at
                    # another version - the pair must be ancestry-related
                    # in either direction. A shared catch-all lane alone
                    # never fabricates movement; unrelated identities stay
                    # honest additions/removals.
                    and (
                        from_spell_id
                        in right_ancestry.get(to_spell_id, ())
                        or to_spell_id
                        in left_ancestry.get(from_spell_id, ())
                    )
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
            # Transitive parent-chain truth (BUG-045): related through ANY
            # recorded ancestor hop, not only direct parents; the resolver
            # material carries the closure, direct parents remain the
            # fallback for detached older payloads.
            "ancestry_related": (
                left_id in right_parents
                or right_id in left_parents
                or left_id in self._group_ancestors(right_material)
                or right_id in self._group_ancestors(left_material)
            ),
        }


    @staticmethod
    def _member_ancestry(material: Dict[str, object]) -> Dict[str, set]:
        """
        Extract each member's transitive spell-ancestor set from material.

        Args:
            material:
                Resolver material payload.

        Returns:
            Dict[str, set]:
                member identity -> ancestor identity set; members without
                recorded ancestry map to an empty set.
        """
        join = material.get("members") if isinstance(material, dict) else None
        if not isinstance(join, dict):
            return {}
        ancestry: Dict[str, set] = {}
        for spell_id, entry in join.items():
            raw = (
                entry.get("ancestor_spell_ids")
                if isinstance(entry, dict)
                else None
            )
            ancestry[str(spell_id)] = (
                {str(item) for item in raw} if isinstance(raw, list) else set()
            )
        return ancestry

    @staticmethod
    def _group_ancestors(material: Dict[str, object]) -> set:
        """
        Extract one composition's transitive ancestor-id set from material.

        Args:
            material:
                Resolver material payload.

        Returns:
            set:
                Ancestor composition identities (empty when the payload
                carries none).
        """
        raw = (
            material.get("ancestor_group_ids")
            if isinstance(material, dict)
            else None
        )
        return {str(item) for item in raw} if isinstance(raw, list) else set()

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
