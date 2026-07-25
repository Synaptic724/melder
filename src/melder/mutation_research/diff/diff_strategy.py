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
        Your subclasses bind normally: manifest lookup is an EXACT
        `(module, qualname)` match and does not inherit. That matters more here
        than almost anywhere else: the family is explicitly open/closed and
        `DiffEngine.register_strategy()` exists so callers can add their own.

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
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Base contract for one derived-diff computation over version material. "
        "Melder kernel machinery: read it to understand the runtime, do not drive it directly."
    )

    __slots__ = Cleanable.__slots__

    def __init__(self) -> None:
        """
        Initialize the strategy lifecycle flag.

        Contract:
            - Owns no releasable state beyond the inherited `Cleanable`
              flag; concrete strategies are stateless comparison functions
              and add no fields of their own, which is why instances are
              safe to share once registered.

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

        Contract:
            - Abstract; every concrete strategy returns a fixed lowercase
              key (for example "source"). This exact string is what
              `DiffEngine` registers the strategy under and resolves it by,
              so it must be stable for the strategy's life and unique within
              one engine.

        Returns:
            str:
                Registry key (e.g. "source").

        Raises:
            NotImplementedError:
                Always on the base; concrete strategies override it.
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

        Contract:
            - READ-ONLY: an implementation must return a fresh, value-typed
              verdict and must NEVER retain or mutate either material.
              Retaining custody material would fork the record into a
              second, drifting copy of a version.
            - Orientation is preserved left -> right, so the verdict is
              directional: it describes what changed going FROM the left
              version TO the right one.

        Args:
            left_material:
                Resolver material for the left version
                (`{"spell_id", "sources", "fingerprints"}`).
            right_material:
                Resolver material for the right version, same shape.

        Returns:
            Dict[str, object]:
                Detached, value-typed verdict payload.

        Raises:
            NotImplementedError:
                Always on the base; concrete strategies override it.
        """
        raise NotImplementedError("Subclasses must implement diff().")
