from abc import abstractmethod
from typing import Dict

from melder.utilities.general_base.cleanable import Cleanable


class DiffStrategy(Cleanable):
    """
    Base contract for one derived-diff computation over version material.

    Purpose:
        Diffs are a READ feature of the research record, never storage:
        version records are full objects, and understanding what changed
        between two of them is computed on demand from custody material.
        Each strategy owns one way of comparing two material payloads.

    Contract:
        - `name` is the stable registry key strategies are resolved by.
        - `diff(left_material, right_material)` receives the detached
          material payloads produced by the engine's injected resolver:
          `{"spell_id": str, "sources": Dict[module_name, source_text],
          "fingerprints": Dict[module_name, sha256]}`.
        - Strategies return detached, value-typed verdict payloads and never
          retain or mutate the material.
        - New strategies extend the family by registration on the engine
          (open/closed): the engine is never edited to add one.

    Threading:
        Strategies hold no mutable state beyond construction; instances are
        safe to share once registered.

    Lifecycle:
        Owned by exactly one `DiffEngine`; `cleanup()` marks the strategy
        cleaned; idempotent.
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
                Registry key (e.g. "source").
        """
        raise NotImplementedError("Subclasses must implement name.")

    @abstractmethod
    def diff(
            self,
            left_material: Dict[str, object],
            right_material: Dict[str, object],
    ) -> Dict[str, object]:
        """
        Compute one detached diff verdict between two material payloads.

        Args:
            left_material:
                Resolver material for the left version.
            right_material:
                Resolver material for the right version.

        Returns:
            Dict[str, object]:
                Detached, value-typed verdict payload.
        """
        raise NotImplementedError("Subclasses must implement diff().")
