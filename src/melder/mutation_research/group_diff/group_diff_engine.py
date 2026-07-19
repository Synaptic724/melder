import threading
from typing import Callable, Dict, List, ClassVar

from melder.mutation_research.group_diff.group_diff_strategy import (
    GroupDiffStrategy,
)
from melder.mutation_research.group_diff.strategies.member_diff_strategy import (
    MemberDiffStrategy,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class GroupDiffEngine(Cleanable):
    """
    Strategy-dispatched derived-diff computation over composition material.

    Purpose:
        The grouped MIRROR of `DiffEngine` (owner ruling 2026-07-11: the
        new node type gets its own strategy system; duplication between
        the families is accepted - both options stay first-class). The
        engine resolves each composition's material through an injected
        resolver (the MutationResearch root supplies one backed by the
        research record; tests supply fakes) and dispatches the comparison
        to a registered strategy. Nothing is stored - composition records
        stay the only storage; diffs are always derived.

    Contract:
        - `material_resolver(group_id)` returns the detached composition
          material `{"group_id", "member_spell_ids", "parent_group_ids",
          "members"}`; resolver errors propagate untouched (unknown
          identities stay loud).
        - `MemberDiffStrategy` ("members") registers by default; further
          strategies extend the family via `register_strategy()`
          (open/closed - the engine never changes to gain one).
        - Duplicate strategy names are refused; resolution failures name
          the known strategies.
        - Verdicts are detached payloads stamped with both identities and
          the strategy name.

    Threading:
        Instance `RLock` serializes registry mutation; dispatch reads
        under the same lock discipline.

    Lifecycle:
        Owned by its creator (the MutationResearch root or a test);
        `cleanup()` cascades into registered strategies; idempotent; lock
        released last.

    Registration:
        MELDER KERNEL - guarded. Constructed by the research root; the caller's
        extension point is `register_strategy()`, not binding an engine.

    Subsystem Context:
        The composition-grain dispatcher, structurally identical to `DiffEngine`
        and deliberately kept separate rather than generalized. The two families
        differ in what their material IS - module sources versus member rosters
        - and forcing one engine to serve both would make its resolver contract
        a union type that neither side fully satisfies.

    System Context:
        The members join in its material payload can legitimately be EMPTY when
        residence truth is unavailable to the resolver. That is why
        `MemberDiffStrategy` requires evidence before pairing a removal with an
        addition as a version move: the engine cannot promise the join is
        populated, so the strategy must degrade honestly rather than infer.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel

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
        Initialize one engine over an injected composition resolver.

        Args:
            material_resolver:
                Callable mapping one group_id to its detached composition
                material payload.
            register_defaults:
                Register the built-in strategy family (`members`) when
                True.

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
        self._strategies_by_name: Dict[str, GroupDiffStrategy] = {}
        self._lock: threading.RLock = threading.RLock()
        if register_defaults:
            self.register_strategy(MemberDiffStrategy())

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

    def register_strategy(self, strategy: GroupDiffStrategy) -> None:
        """
        Register one additional grouped strategy by its stable name.

        Args:
            strategy:
                Strategy instance to own.

        Raises:
            TypeError:
                If the object is not a GroupDiffStrategy.
            ValueError:
                If the name is already registered.
        """
        self.check_cleaned()
        if not isinstance(strategy, GroupDiffStrategy):
            raise TypeError(
                "strategy must be a GroupDiffStrategy instance."
            )
        with self._lock:
            name = strategy.name
            if name in self._strategies_by_name:
                raise ValueError(
                    f"GroupDiffEngine already owns a strategy named "
                    f"'{name}'."
                )
            self._strategies_by_name[name] = strategy

    def list_strategy_names(self) -> List[str]:
        """
        Return every registered strategy name, sorted.

        Returns:
            List[str]:
                Sorted registry keys.
        """
        self.check_cleaned()
        with self._lock:
            return sorted(self._strategies_by_name.keys())

    def diff(
            self,
            left_group_id: str,
            right_group_id: str,
            *,
            strategy: str = "members",
    ) -> Dict[str, object]:
        """
        Compute one derived diff between two composition identities.

        Args:
            left_group_id:
                Left composition identity (content-addressed SHA256).
            right_group_id:
                Right composition identity.
            strategy:
                Registered strategy name; "members" by default.

        Returns:
            Dict[str, object]:
                Detached verdict: `left_group_id`, `right_group_id`,
                `strategy`, and the strategy's `result` payload.

        Raises:
            ValueError:
                If either identity is empty.
            KeyError:
                If the strategy name is unknown (the error names the known
                strategies); resolver lookup failures propagate as raised.
        """
        self.check_cleaned()
        if not isinstance(left_group_id, str) or not left_group_id:
            raise ValueError("left_group_id must be a non-empty string.")
        if not isinstance(right_group_id, str) or not right_group_id:
            raise ValueError("right_group_id must be a non-empty string.")
        with self._lock:
            resolved = self._strategies_by_name.get(strategy)
            if resolved is None:
                known = sorted(self._strategies_by_name.keys())
                raise KeyError(
                    f"GroupDiffEngine has no strategy '{strategy}'. Known "
                    f"strategies: {known}."
                )
            resolver = self._material_resolver
        left_material = resolver(left_group_id)
        right_material = resolver(right_group_id)
        return {
            "left_group_id": left_group_id,
            "right_group_id": right_group_id,
            "strategy": strategy,
            "result": resolved.diff(left_material, right_material),
        }
