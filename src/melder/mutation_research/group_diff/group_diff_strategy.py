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
