import threading
from typing import Callable, Dict, List, Optional

from melder.mutation_research.diff.diff_strategy import DiffStrategy
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
        - `material_resolver(spell_sha)` returns the detached material
          payload `{"spell_sha", "sources", "fingerprints"}`; resolver
          errors propagate untouched (unknown identities stay loud).
        - `SourceDiffStrategy` (text transport) and `StructuralDiffStrategy`
          (AST reasoning layer) register by default; further strategies
          extend the family via `register_strategy()` (open/closed - the
          engine never changes to gain one).
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
    """

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

    def cleanup(self) -> None:
        """
        Cascade cleanup into registered strategies and mark cleaned.

        Contract:
            - Idempotent; del posture (no tombstones); lock last.
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

        Returns:
            List[str]: Sorted registry keys.
        """
        self.check_cleaned()
        with self._lock:
            return sorted(self._strategies_by_name.keys())

    def diff(
            self,
            left_sha: str,
            right_sha: str,
            *,
            strategy: str = "source",
    ) -> Dict[str, object]:
        """
        Compute one derived diff between two version identities.

        Args:
            left_sha:
                Left version identity (binding-signature SHA256).
            right_sha:
                Right version identity.
            strategy:
                Registered strategy name; "source" by default.

        Returns:
            Dict[str, object]:
                Detached verdict: `left_sha`, `right_sha`, `strategy`, and
                the strategy's `result` payload.

        Raises:
            ValueError:
                If either identity is empty.
            KeyError:
                If the strategy name is unknown (the error names the known
                strategies); resolver lookup failures propagate as raised.
        """
        self.check_cleaned()
        if not isinstance(left_sha, str) or not left_sha:
            raise ValueError("left_sha must be a non-empty string.")
        if not isinstance(right_sha, str) or not right_sha:
            raise ValueError("right_sha must be a non-empty string.")
        with self._lock:
            resolved = self._strategies_by_name.get(strategy)
            if resolved is None:
                known = sorted(self._strategies_by_name.keys())
                raise KeyError(
                    f"DiffEngine has no strategy '{strategy}'. Known "
                    f"strategies: {known}."
                )
            resolver = self._material_resolver
        left_material = resolver(left_sha)
        right_material = resolver(right_sha)
        return {
            "left_sha": left_sha,
            "right_sha": right_sha,
            "strategy": strategy,
            "result": resolved.diff(left_material, right_material),
        }
