from abc import abstractmethod
from typing import Dict

from melder.utilities.general_base.cleanable import Cleanable


class GroupDiffStrategy(Cleanable):
    """
    Base contract for one derived-diff computation over COMPOSITION material.

    Purpose:
        The grouped mirror of `DiffStrategy` (owner ruling 2026-07-11:
        GroupedResearchNodes get their OWN strategy system beside the
        normal one; duplication between the families is accepted - both
        options stay first-class). Composition diffs are READS: group
        nodes are full composition records, and understanding what changed
        between two of them is computed on demand from the record.

    Contract:
        - `name` is the stable registry key strategies are resolved by.
        - `diff(left_material, right_material)` receives the detached
          composition materials produced by the engine's injected
          resolver: `{"group_id": str, "member_spell_ids": List[str],
          "parent_group_ids": List[str],
          "members": Dict[spell_id, {"lane_id", "lane_name",
          "lane_state", "lane_type", "lane_tip"}]}` (the members join may
          be empty when residence truth is unavailable to the resolver).
        - Strategies return detached, value-typed verdict payloads and
          never retain or mutate the material.
        - New strategies extend the family by registration on the engine
          (open/closed): the engine is never edited to add one.

    Threading:
        Strategies hold no mutable state beyond construction; instances
        are safe to share once registered.

    Lifecycle:
        Owned by exactly one `GroupDiffEngine`; `cleanup()` marks the
        strategy cleaned; idempotent.

    Registration:
        BASE CLASS - DELIBERATELY UNGUARDED. Do NOT add `__melder_internal__`
        to this class, for the same reason as `DiffStrategy`: the sentinel
        resolves through `getattr` and walks the MRO, so tagging this base would
        tag every derived strategy including a user's own. The family is
        open/closed by design - `GroupDiffEngine.register_strategy()` exists
        precisely so callers can add comparisons. `MemberDiffStrategy`, the
        shipped implementation, carries the sentinel individually.

    Subsystem Context:
        The extension point of the COMPOSITION-grain diff family in
        `mutation_research/group_diff/`, deliberately mirroring
        `diff/DiffStrategy` rather than sharing with it. The duplication between
        the two families is an accepted owner ruling: compositions are their own
        node kind, so they get their own strategy system and both stay
        first-class. `MemberDiffStrategy` ("members") is the default, pairing
        added and removed members with lane-EVIDENCED version moves rather than
        guessing at them.

    System Context:
        Composition diffs are READS over the record, same as spell diffs -
        `GroupedResearchNode` records are full compositions and "what changed"
        is derived on demand. The grain distinction is what makes two families
        worth having: a spell diff compares module text, a composition diff
        compares ROSTERS, and collapsing them would force one grain to pretend
        to be the other.
    """

    __slots__ = Cleanable.__slots__

    def __init__(self) -> None:
        """
        Initialize the strategy lifecycle flag.
        """
        super().__init__()

    def cleanup(self) -> None:
        """
        Mark the strategy cleaned.

        Contract:
            - Idempotent; strategies own no releasable state by default.
        """
        if self._cleaned:
            return
        self._cleaned = True

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Return the stable registry name of this strategy.

        Returns:
            str:
                Registry key (e.g. "members").
        """
        raise NotImplementedError("Subclasses must implement name.")

    @abstractmethod
    def diff(
            self,
            left_material: Dict[str, object],
            right_material: Dict[str, object],
    ) -> Dict[str, object]:
        """
        Compute one detached diff verdict between two composition materials.

        Args:
            left_material:
                Resolver material for the left composition.
            right_material:
                Resolver material for the right composition.

        Returns:
            Dict[str, object]:
                Detached, value-typed verdict payload.
        """
        raise NotImplementedError("Subclasses must implement diff().")
