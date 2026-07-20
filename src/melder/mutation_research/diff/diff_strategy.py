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

    Registration:
        BASE CLASS - DELIBERATELY UNGUARDED. Do NOT add `__melder_internal__`
        to this class.

        The registration guard resolves its sentinel through `getattr`, which
        walks the MRO, so tagging this base would tag every strategy derived
        from it - including one a USER writes. That matters more here than
        almost anywhere else in the codebase: this family is explicitly
        open/closed, and `DiffEngine.register_strategy()` exists so callers can
        add their own comparison. Guarding the base would make user strategies
        unbindable in the user's own spellbook. The three Melder-owned concrete
        strategies carry the sentinel individually.

    Subsystem Context:
        The extension point of the spell-grain diff family in
        `mutation_research/diff/`. `DiffEngine` dispatches; the three shipped
        implementations - `SourceDiffStrategy` (whole-module text),
        `StructuralDiffStrategy` (AST shape), `PartDiffStrategy` (per-part code)
        - are the grain choices an agent picks between. `GroupDiffStrategy` in
        `group_diff/` is the deliberate MIRROR of this contract for composition
        material rather than spell material.

    System Context:
        Diffs are a READ over the research record and are never stored: version
        records are full objects, and "what changed" is derived on demand from
        crystallizer custody material. That is why a strategy must never retain
        or mutate what it is handed - retaining material would quietly turn a
        derived answer into a second, divergent copy of the record.
    """
    _ast_helper_access: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Base contract for one derived-diff computation over version material. "
        "Melder kernel machinery: read it to understand the runtime, do not drive it directly."
    )

    __slots__ = Cleanable.__slots__

    def __init__(self) -> None:
        """
        Initialize the strategy lifecycle flag.

        Returns:
            None.
        """
        super().__init__()

    def cleanup(self) -> None:
        """
        Mark the strategy cleaned.

        Contract:
            - Idempotent; strategies own no releasable state by default.

        Returns:
            None.
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
