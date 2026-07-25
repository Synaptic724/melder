import threading
from typing import Callable, Dict, List, Optional, ClassVar

from melder.mutation_research.diff.diff_strategy import DiffStrategy
from melder.mutation_research.diff.strategies.part_diff_strategy import (
    PartDiffStrategy,
)
from melder.mutation_research.diff.strategies.source_diff_strategy import (
    SourceDiffStrategy,
)
from melder.mutation_research.diff.strategies.structural_diff_strategy import (
    StructuralDiffStrategy,
)
from melder.utilities.general_base.cleanable import Cleanable


class DiffEngine(Cleanable):
    """
    Strategy-dispatched derived-diff computation over custody material.

    Purpose:
        Answer "what changed between these two versions" as a READ over the
        record: the engine resolves each version's material through an
        injected resolver (the MutationResearch root supplies one backed by
        crystallizer custody; tests supply fakes) and dispatches the
        comparison to a registered strategy. Nothing is stored - full-object
        records stay the only storage; diffs are always derived.

    Contract:
        - `material_resolver(spell_id)` returns the detached material
          payload `{"spell_id", "sources", "fingerprints"}`; resolver
          errors propagate untouched (unknown identities stay loud).
        - `SourceDiffStrategy` (whole-module text), `StructuralDiffStrategy`
          (AST shape reports), and `PartDiffStrategy` (per-class/function
          code diffs - the agent's grain choice, owner ruling 2026-07-11)
          register by default; further strategies extend the family via
          `register_strategy()` (open/closed - the engine never changes to
          gain one).
        - Duplicate strategy names are refused; resolution failures name the
          known strategies.
        - Verdicts are detached payloads stamped with both identities and
          the strategy name.

    Threading:
        Instance `RLock` serializes registry mutation; dispatch reads under
        the same lock discipline.

    Lifecycle:
        Owned by its creator (the MutationResearch root or a test);
        `cleanup()` cascades into registered strategies; idempotent; lock
        released last.

    Registration:
        MELDER KERNEL - guarded. The engine is constructed by the research root;
        the extension point for callers is `register_strategy()`, not binding
        an engine.

    THE RESOLVER IS INJECTED, AND THAT IS WHY THIS IS TESTABLE:
        The engine never reaches into the crystallizer itself. It receives a
        `material_resolver(spell_id)` callable - the research root supplies one
        backed by custody, tests supply fakes - so the diff family can be
        exercised with synthetic material and no recorded world at all. It also
        means resolver errors propagate UNTOUCHED: an unknown identity stays
        loud rather than being softened into an empty diff.

    Subsystem Context:
        The dispatcher of the spell-grain diff family in
        `mutation_research/diff/`, holding the registry that `DiffStrategy`
        implementations join. `GroupDiffEngine` in `group_diff/` is its
        deliberate mirror for composition material.

    System Context:
        Diffs are DERIVED, never stored: version records are full objects, and
        "what changed" is computed on demand. That is why the engine is
        open/closed - adding a grain means registering a strategy, never editing
        this class - and why nothing it produces is written back into the
        record. A verdict is an answer, not a fact the system remembers.
    """
    __ast_helper_access__: str = "public"
    __agent_purpose__: str = (
        "access: public. Computes derived diffs over RECORDED custody material - never the live disk. "
        "Choose grain by strategy: source, structural, or parts. Obtain via "
        "MutationResearch.create_diff_engine()."
    )

    __slots__ = Cleanable.__slots__ + [
        "_material_resolver",
        "_strategies_by_name",
        "_lock",
    ]

    def __init__(
            self,
            material_resolver: Callable[[str], Dict[str, object]],
            *,
            register_defaults: bool = True,
    ) -> None:
        """
        Initialize one engine over an injected material resolver.

        Args:
            material_resolver:
                Callable mapping one spell SHA256 to its detached custody
                material payload.
            register_defaults:
                Register the built-in strategy family (`source`) when True.

        Raises:
            ValueError:
                If material_resolver is None.

        Returns:
            None.
        """
        super().__init__()
        if material_resolver is None:
            raise ValueError("material_resolver cannot be None.")
        self._material_resolver: Callable[[str], Dict[str, object]] = (
            material_resolver
        )
        self._strategies_by_name: Dict[str, DiffStrategy] = {}
        self._lock: threading.RLock = threading.RLock()
        if register_defaults:
            self.register_strategy(SourceDiffStrategy())
            self.register_strategy(StructuralDiffStrategy())
            self.register_strategy(PartDiffStrategy())

    def cleanup(self) -> None:
        """
        Cascade cleanup into registered strategies and mark cleaned.

        Contract:
            - Idempotent; del posture (no tombstones); lock last.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            for strategy in self._strategies_by_name.values():
                try:
                    strategy.cleanup()
                except Exception:
                    pass
            self._strategies_by_name.clear()
            del self._strategies_by_name
            del self._material_resolver
        del self._lock

    def register_strategy(self, strategy: DiffStrategy) -> None:
        """
        Register one additional diff strategy by its stable name.

        Args:
            strategy:
                Strategy instance to own.

        Raises:
            TypeError:
                If the object is not a DiffStrategy.
            ValueError:
                If the name is already registered.

        Returns:
            None.
        """
        self.check_cleaned()
        if not isinstance(strategy, DiffStrategy):
            raise TypeError("strategy must be a DiffStrategy instance.")
        with self._lock:
            name = strategy.name
            if name in self._strategies_by_name:
                raise ValueError(
                    f"DiffEngine already owns a strategy named '{name}'."
                )
            self._strategies_by_name[name] = strategy

    def list_strategy_names(self) -> List[str]:
        """
        Return every registered strategy name, sorted.

        Contract:
            - SORTED, so iteration order is deterministic across calls and processes.
            - Lists REGISTERED strategy names; a name absent here cannot be selected
              for a diff.

        Threading:
            Reads under `self._lock`, so the result is a coherent snapshot.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the object has been cleaned.

        Returns:
            List[str]: Sorted registry keys.
        """
        self.check_cleaned()
        with self._lock:
            return sorted(self._strategies_by_name.keys())

    def diff_materials(
            self,
            left_material: Dict[str, object],
            right_material: Dict[str, object],
            *,
            strategy: str = "source",
    ) -> Dict[str, object]:
        """
        Compute one derived diff between two pre-resolved materials.

        Purpose:
            The candidate-preview entry: when one side is not (yet) a
            recorded identity - e.g. unbound codegen output - the caller
            supplies both material payloads directly and the engine only
            dispatches the strategy. Recorded-identity diffs should keep
            using `diff()`, which resolves through custody.

        Args:
            left_material:
                Detached material payload
                (`{"spell_id", "sources", "fingerprints"}`).
            right_material:
                Detached material payload of the same shape.
            strategy:
                Registered strategy name; "source" by default.

        Returns:
            Dict[str, object]:
                Detached verdict: `left_spell_id`, `right_spell_id`
                (as carried by the materials), `strategy`, and the
                strategy's `result` payload.

        Raises:
            ValueError:
                If either material is not a dict.
            KeyError:
                If the strategy name is unknown (the error names the known
                strategies).
        """
        self.check_cleaned()
        if not isinstance(left_material, dict):
            raise ValueError("left_material must be a material dict.")
        if not isinstance(right_material, dict):
            raise ValueError("right_material must be a material dict.")
        with self._lock:
            resolved = self._strategies_by_name.get(strategy)
            if resolved is None:
                known = sorted(self._strategies_by_name.keys())
                raise KeyError(
                    f"DiffEngine has no strategy '{strategy}'. Known "
                    f"strategies: {known}."
                )
        return {
            "left_spell_id": str(left_material.get("spell_id")),
            "right_spell_id": str(right_material.get("spell_id")),
            "strategy": strategy,
            "result": resolved.diff(left_material, right_material),
        }

    def diff(
            self,
            left_spell_id: str,
            right_spell_id: str,
            *,
            strategy: str = "source",
    ) -> Dict[str, object]:
        """
        Compute one derived diff between two version identities.

        Args:
            left_spell_id:
                Left version identity (binding-signature SHA256).
            right_spell_id:
                Right version identity.
            strategy:
                Registered strategy name; "source" by default.

        Returns:
            Dict[str, object]:
                Detached verdict: `left_spell_id`, `right_spell_id`, `strategy`, and
                the strategy's `result` payload.

        Raises:
            ValueError:
                If either identity is empty.
            KeyError:
                If the strategy name is unknown (the error names the known
                strategies); resolver lookup failures propagate as raised.
        """
        self.check_cleaned()
        if not isinstance(left_spell_id, str) or not left_spell_id:
            raise ValueError("left_spell_id must be a non-empty string.")
        if not isinstance(right_spell_id, str) or not right_spell_id:
            raise ValueError("right_spell_id must be a non-empty string.")
        with self._lock:
            resolved = self._strategies_by_name.get(strategy)
            if resolved is None:
                known = sorted(self._strategies_by_name.keys())
                raise KeyError(
                    f"DiffEngine has no strategy '{strategy}'. Known "
                    f"strategies: {known}."
                )
            resolver = self._material_resolver
        left_material = resolver(left_spell_id)
        right_material = resolver(right_spell_id)
        return {
            "left_spell_id": left_spell_id,
            "right_spell_id": right_spell_id,
            "strategy": strategy,
            "result": resolved.diff(left_material, right_material),
        }
