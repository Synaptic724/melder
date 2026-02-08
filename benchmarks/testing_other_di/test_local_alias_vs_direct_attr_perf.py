import time
from typing import Any, Callable, List, Tuple


class _SharedDependencies:
    """
    Hold a fixed dependency payload for attribute-access micro-benchmarks.

    Contract:
        - Stores four integer dependency fields.
        - Exposes direct attribute access only.
    """

    __slots__ = ("dep1", "dep2", "dep3", "dep4")

    def __init__(self) -> None:
        """
        Initialize deterministic dependency values.
        """
        self.dep1 = 1
        self.dep2 = 2
        self.dep3 = 3
        self.dep4 = 4


class _ChainLevel4:
    """
    Provide depth-4 dependency payload fields.

    Contract:
        - Stores four integer dependency fields.
    """

    __slots__ = ("dep1", "dep2", "dep3", "dep4")

    def __init__(self) -> None:
        """
        Initialize deterministic dependency values.
        """
        self.dep1 = 1
        self.dep2 = 2
        self.dep3 = 3
        self.dep4 = 4


class _ChainLevel3:
    """
    Provide depth-3 dependency payload fields and link to level 4.

    Contract:
        - Stores four integer dependency fields.
        - Owns one level-4 child under ``l4``.
    """

    __slots__ = ("dep1", "dep2", "dep3", "dep4", "l4")

    def __init__(self) -> None:
        """
        Initialize deterministic dependency values and nested level-4 node.
        """
        self.dep1 = 1
        self.dep2 = 2
        self.dep3 = 3
        self.dep4 = 4
        self.l4 = _ChainLevel4()


class _ChainLevel2:
    """
    Provide depth-2 dependency payload fields and link to level 3.

    Contract:
        - Stores four integer dependency fields.
        - Owns one level-3 child under ``l3``.
    """

    __slots__ = ("dep1", "dep2", "dep3", "dep4", "l3")

    def __init__(self) -> None:
        """
        Initialize deterministic dependency values and nested level-3 node.
        """
        self.dep1 = 1
        self.dep2 = 2
        self.dep3 = 3
        self.dep4 = 4
        self.l3 = _ChainLevel3()


class _ChainRoot:
    """
    Root object for chain-depth attribute benchmarks.

    Contract:
        - Owns one level-2 child under ``l2``.
    """

    __slots__ = ("l2",)

    def __init__(self) -> None:
        """
        Initialize the chain root with deterministic nested children.
        """
        self.l2 = _ChainLevel2()


class _Owner:
    """
    Provide benchmark methods for direct and aliased attribute access.

    Contract:
        - Owns a single shared dependency object.
        - Each method runs a tight loop and returns an integer checksum.
        - No mutation occurs during benchmark loops.
    """

    __slots__ = ("_shared",)

    def __init__(self, shared: _SharedDependencies) -> None:
        """
        Initialize the owner with a shared dependency object.

        Args:
            shared: Shared dependency object used by benchmark methods.
        """
        self._shared = shared

    def run_direct(self, *, iterations: int, access_count: int) -> int:
        """
        Execute direct ``self._shared`` attribute access in a tight loop.

        Args:
            iterations: Loop iterations to execute.
            access_count: Number of dependency fields to read per iteration.

        Returns:
            int: Deterministic checksum for correctness validation.
        """
        total = 0
        if access_count == 1:
            for _ in range(iterations):
                total += self._shared.dep1
            return total
        if access_count == 2:
            for _ in range(iterations):
                total += self._shared.dep1 + self._shared.dep2
            return total
        if access_count == 3:
            for _ in range(iterations):
                total += self._shared.dep1 + self._shared.dep2 + self._shared.dep3
            return total
        if access_count == 4:
            for _ in range(iterations):
                total += (
                    self._shared.dep1
                    + self._shared.dep2
                    + self._shared.dep3
                    + self._shared.dep4
                )
            return total
        raise ValueError("access_count must be between 1 and 4.")

    def run_alias(self, *, iterations: int, access_count: int) -> int:
        """
        Execute local-alias attribute access in a tight loop.

        Args:
            iterations: Loop iterations to execute.
            access_count: Number of dependency fields to read per iteration.

        Returns:
            int: Deterministic checksum for correctness validation.
        """
        total = 0
        shared = self._shared
        if access_count == 1:
            for _ in range(iterations):
                total += shared.dep1
            return total
        if access_count == 2:
            for _ in range(iterations):
                total += shared.dep1 + shared.dep2
            return total
        if access_count == 3:
            for _ in range(iterations):
                total += shared.dep1 + shared.dep2 + shared.dep3
            return total
        if access_count == 4:
            for _ in range(iterations):
                total += (
                    shared.dep1
                    + shared.dep2
                    + shared.dep3
                    + shared.dep4
                )
            return total
        raise ValueError("access_count must be between 1 and 4.")


class _OwnerWithChain:
    """
    Provide benchmark methods for chained self-attribute access.

    Contract:
        - Owns one chain root object.
        - Compares direct chain traversal versus local alias to the leaf node.
        - Supports depth 2, 3, and 4 with access counts 1..4.
    """

    __slots__ = ("_chain_root",)

    def __init__(self, chain_root: _ChainRoot) -> None:
        """
        Initialize owner with a nested chain root object.

        Args:
            chain_root: Root object containing nested benchmark chain levels.
        """
        self._chain_root = chain_root

    def run_direct_chain(self, *, iterations: int, access_count: int, depth: int) -> int:
        """
        Execute direct chained self-attribute access in a tight loop.

        Args:
            iterations: Loop iterations to execute.
            access_count: Number of dependency fields to read per iteration.
            depth: Chain depth to resolve (2, 3, or 4).

        Returns:
            int: Deterministic checksum for correctness validation.
        """
        total = 0
        if depth == 2:
            if access_count == 1:
                for _ in range(iterations):
                    total += self._chain_root.l2.dep1
                return total
            if access_count == 2:
                for _ in range(iterations):
                    total += self._chain_root.l2.dep1 + self._chain_root.l2.dep2
                return total
            if access_count == 3:
                for _ in range(iterations):
                    total += (
                        self._chain_root.l2.dep1
                        + self._chain_root.l2.dep2
                        + self._chain_root.l2.dep3
                    )
                return total
            if access_count == 4:
                for _ in range(iterations):
                    total += (
                        self._chain_root.l2.dep1
                        + self._chain_root.l2.dep2
                        + self._chain_root.l2.dep3
                        + self._chain_root.l2.dep4
                    )
                return total
        if depth == 3:
            if access_count == 1:
                for _ in range(iterations):
                    total += self._chain_root.l2.l3.dep1
                return total
            if access_count == 2:
                for _ in range(iterations):
                    total += self._chain_root.l2.l3.dep1 + self._chain_root.l2.l3.dep2
                return total
            if access_count == 3:
                for _ in range(iterations):
                    total += (
                        self._chain_root.l2.l3.dep1
                        + self._chain_root.l2.l3.dep2
                        + self._chain_root.l2.l3.dep3
                    )
                return total
            if access_count == 4:
                for _ in range(iterations):
                    total += (
                        self._chain_root.l2.l3.dep1
                        + self._chain_root.l2.l3.dep2
                        + self._chain_root.l2.l3.dep3
                        + self._chain_root.l2.l3.dep4
                    )
                return total
        if depth == 4:
            if access_count == 1:
                for _ in range(iterations):
                    total += self._chain_root.l2.l3.l4.dep1
                return total
            if access_count == 2:
                for _ in range(iterations):
                    total += self._chain_root.l2.l3.l4.dep1 + self._chain_root.l2.l3.l4.dep2
                return total
            if access_count == 3:
                for _ in range(iterations):
                    total += (
                        self._chain_root.l2.l3.l4.dep1
                        + self._chain_root.l2.l3.l4.dep2
                        + self._chain_root.l2.l3.l4.dep3
                    )
                return total
            if access_count == 4:
                for _ in range(iterations):
                    total += (
                        self._chain_root.l2.l3.l4.dep1
                        + self._chain_root.l2.l3.l4.dep2
                        + self._chain_root.l2.l3.l4.dep3
                        + self._chain_root.l2.l3.l4.dep4
                    )
                return total
        raise ValueError("depth must be 2, 3, or 4 and access_count must be 1..4.")

    def run_alias_chain(self, *, iterations: int, access_count: int, depth: int) -> int:
        """
        Execute local-alias chained self-attribute access in a tight loop.

        Args:
            iterations: Loop iterations to execute.
            access_count: Number of dependency fields to read per iteration.
            depth: Chain depth to resolve (2, 3, or 4).

        Returns:
            int: Deterministic checksum for correctness validation.
        """
        if depth == 2:
            leaf = self._chain_root.l2
        elif depth == 3:
            leaf = self._chain_root.l2.l3
        elif depth == 4:
            leaf = self._chain_root.l2.l3.l4
        else:
            raise ValueError("depth must be 2, 3, or 4.")

        total = 0
        if access_count == 1:
            for _ in range(iterations):
                total += leaf.dep1
            return total
        if access_count == 2:
            for _ in range(iterations):
                total += leaf.dep1 + leaf.dep2
            return total
        if access_count == 3:
            for _ in range(iterations):
                total += leaf.dep1 + leaf.dep2 + leaf.dep3
            return total
        if access_count == 4:
            for _ in range(iterations):
                total += leaf.dep1 + leaf.dep2 + leaf.dep3 + leaf.dep4
            return total
        raise ValueError("access_count must be between 1 and 4.")


def _run_param_direct(*, shared: _SharedDependencies, iterations: int, access_count: int) -> int:
    """
    Execute direct parameter-attribute access in a tight loop.

    Args:
        shared: Dependency object passed as a method/function parameter.
        iterations: Loop iterations to execute.
        access_count: Number of dependency fields to read per iteration.

    Returns:
        int: Deterministic checksum for correctness validation.
    """
    total = 0
    if access_count == 1:
        for _ in range(iterations):
            total += shared.dep1
        return total
    if access_count == 2:
        for _ in range(iterations):
            total += shared.dep1 + shared.dep2
        return total
    if access_count == 3:
        for _ in range(iterations):
            total += shared.dep1 + shared.dep2 + shared.dep3
        return total
    if access_count == 4:
        for _ in range(iterations):
            total += shared.dep1 + shared.dep2 + shared.dep3 + shared.dep4
        return total
    raise ValueError("access_count must be between 1 and 4.")


def _run_param_alias(*, shared: _SharedDependencies, iterations: int, access_count: int) -> int:
    """
    Execute local-alias parameter-attribute access in a tight loop.

    Args:
        shared: Dependency object passed as a method/function parameter.
        iterations: Loop iterations to execute.
        access_count: Number of dependency fields to read per iteration.

    Returns:
        int: Deterministic checksum for correctness validation.
    """
    local_shared = shared
    total = 0
    if access_count == 1:
        for _ in range(iterations):
            total += local_shared.dep1
        return total
    if access_count == 2:
        for _ in range(iterations):
            total += local_shared.dep1 + local_shared.dep2
        return total
    if access_count == 3:
        for _ in range(iterations):
            total += local_shared.dep1 + local_shared.dep2 + local_shared.dep3
        return total
    if access_count == 4:
        for _ in range(iterations):
            total += (
                local_shared.dep1
                + local_shared.dep2
                + local_shared.dep3
                + local_shared.dep4
            )
        return total
    raise ValueError("access_count must be between 1 and 4.")


def _run_param_chain_direct(
        *,
        chain_root: _ChainRoot,
        iterations: int,
        access_count: int,
        depth: int,
) -> int:
    """
    Execute direct chained parameter-attribute access in a tight loop.

    Args:
        chain_root: Root object passed as a parameter.
        iterations: Loop iterations to execute.
        access_count: Number of dependency fields to read per iteration.
        depth: Chain depth to resolve (2, 3, or 4).

    Returns:
        int: Deterministic checksum for correctness validation.
    """
    total = 0
    if depth == 2:
        if access_count == 1:
            for _ in range(iterations):
                total += chain_root.l2.dep1
            return total
        if access_count == 2:
            for _ in range(iterations):
                total += chain_root.l2.dep1 + chain_root.l2.dep2
            return total
        if access_count == 3:
            for _ in range(iterations):
                total += chain_root.l2.dep1 + chain_root.l2.dep2 + chain_root.l2.dep3
            return total
        if access_count == 4:
            for _ in range(iterations):
                total += (
                    chain_root.l2.dep1
                    + chain_root.l2.dep2
                    + chain_root.l2.dep3
                    + chain_root.l2.dep4
                )
            return total
    if depth == 3:
        if access_count == 1:
            for _ in range(iterations):
                total += chain_root.l2.l3.dep1
            return total
        if access_count == 2:
            for _ in range(iterations):
                total += chain_root.l2.l3.dep1 + chain_root.l2.l3.dep2
            return total
        if access_count == 3:
            for _ in range(iterations):
                total += chain_root.l2.l3.dep1 + chain_root.l2.l3.dep2 + chain_root.l2.l3.dep3
            return total
        if access_count == 4:
            for _ in range(iterations):
                total += (
                    chain_root.l2.l3.dep1
                    + chain_root.l2.l3.dep2
                    + chain_root.l2.l3.dep3
                    + chain_root.l2.l3.dep4
                )
            return total
    if depth == 4:
        if access_count == 1:
            for _ in range(iterations):
                total += chain_root.l2.l3.l4.dep1
            return total
        if access_count == 2:
            for _ in range(iterations):
                total += chain_root.l2.l3.l4.dep1 + chain_root.l2.l3.l4.dep2
            return total
        if access_count == 3:
            for _ in range(iterations):
                total += (
                    chain_root.l2.l3.l4.dep1
                    + chain_root.l2.l3.l4.dep2
                    + chain_root.l2.l3.l4.dep3
                )
            return total
        if access_count == 4:
            for _ in range(iterations):
                total += (
                    chain_root.l2.l3.l4.dep1
                    + chain_root.l2.l3.l4.dep2
                    + chain_root.l2.l3.l4.dep3
                    + chain_root.l2.l3.l4.dep4
                )
            return total
    raise ValueError("depth must be 2, 3, or 4 and access_count must be 1..4.")


def _run_param_chain_alias(
        *,
        chain_root: _ChainRoot,
        iterations: int,
        access_count: int,
        depth: int,
) -> int:
    """
    Execute local-alias chained parameter-attribute access in a tight loop.

    Args:
        chain_root: Root object passed as a parameter.
        iterations: Loop iterations to execute.
        access_count: Number of dependency fields to read per iteration.
        depth: Chain depth to resolve (2, 3, or 4).

    Returns:
        int: Deterministic checksum for correctness validation.
    """
    if depth == 2:
        leaf = chain_root.l2
    elif depth == 3:
        leaf = chain_root.l2.l3
    elif depth == 4:
        leaf = chain_root.l2.l3.l4
    else:
        raise ValueError("depth must be 2, 3, or 4.")

    total = 0
    if access_count == 1:
        for _ in range(iterations):
            total += leaf.dep1
        return total
    if access_count == 2:
        for _ in range(iterations):
            total += leaf.dep1 + leaf.dep2
        return total
    if access_count == 3:
        for _ in range(iterations):
            total += leaf.dep1 + leaf.dep2 + leaf.dep3
        return total
    if access_count == 4:
        for _ in range(iterations):
            total += leaf.dep1 + leaf.dep2 + leaf.dep3 + leaf.dep4
        return total
    raise ValueError("access_count must be between 1 and 4.")


def _measure_ns(fn: Callable[..., int], *args: Any, **kwargs: Any) -> Tuple[int, int]:
    """
    Measure one callable execution in nanoseconds.

    Args:
        fn: Callable to execute.
        *args: Positional args passed to fn.
        **kwargs: Keyword args passed to fn.

    Returns:
        Tuple[int, int]: (elapsed_ns, fn_result).
    """
    start_ns = time.perf_counter_ns()
    result = fn(*args, **kwargs)
    end_ns = time.perf_counter_ns()
    return end_ns - start_ns, result


def _average_mode_ns(
        *,
        owner: _Owner,
        mode: str,
        iterations: int,
        access_count: int,
        repeats: int,
) -> Tuple[float, int]:
    """
    Measure average elapsed nanoseconds for one mode.

    Args:
        owner: Benchmark owner object.
        mode: Either ``"direct"`` or ``"alias"``.
        iterations: Loop iterations per run.
        access_count: Number of dependency accesses per iteration.
        repeats: Number of repeated timed runs to average.

    Returns:
        Tuple[float, int]: (average_total_ns, final_checksum_result).
    """
    elapsed_runs: List[int] = []
    final_result = 0
    for _ in range(repeats):
        if mode == "direct":
            elapsed_ns, result = _measure_ns(
                owner.run_direct,
                iterations=iterations,
                access_count=access_count,
            )
        elif mode == "alias":
            elapsed_ns, result = _measure_ns(
                owner.run_alias,
                iterations=iterations,
                access_count=access_count,
            )
        else:
            raise ValueError("mode must be either 'direct' or 'alias'.")
        elapsed_runs.append(elapsed_ns)
        final_result = result
    return sum(elapsed_runs) / float(repeats), final_result


def _average_param_mode_ns(
        *,
        shared: _SharedDependencies,
        mode: str,
        iterations: int,
        access_count: int,
        repeats: int,
) -> Tuple[float, int]:
    """
    Measure average elapsed nanoseconds for parameter-attribute modes.

    Args:
        shared: Dependency object passed into benchmark functions.
        mode: Either ``"direct"`` or ``"alias"``.
        iterations: Loop iterations per run.
        access_count: Number of dependency accesses per iteration.
        repeats: Number of repeated timed runs to average.

    Returns:
        Tuple[float, int]: (average_total_ns, final_checksum_result).
    """
    elapsed_runs: List[int] = []
    final_result = 0
    for _ in range(repeats):
        if mode == "direct":
            elapsed_ns, result = _measure_ns(
                _run_param_direct,
                shared=shared,
                iterations=iterations,
                access_count=access_count,
            )
        elif mode == "alias":
            elapsed_ns, result = _measure_ns(
                _run_param_alias,
                shared=shared,
                iterations=iterations,
                access_count=access_count,
            )
        else:
            raise ValueError("mode must be either 'direct' or 'alias'.")
        elapsed_runs.append(elapsed_ns)
        final_result = result
    return sum(elapsed_runs) / float(repeats), final_result


def _average_chain_self_mode_ns(
        *,
        owner: _OwnerWithChain,
        mode: str,
        iterations: int,
        access_count: int,
        depth: int,
        repeats: int,
) -> Tuple[float, int]:
    """
    Measure average elapsed nanoseconds for chained self-attribute modes.

    Args:
        owner: Benchmark owner object.
        mode: Either ``"direct"`` or ``"alias"``.
        iterations: Loop iterations per run.
        access_count: Number of dependency accesses per iteration.
        depth: Chain depth to resolve (2, 3, or 4).
        repeats: Number of repeated timed runs to average.

    Returns:
        Tuple[float, int]: (average_total_ns, final_checksum_result).
    """
    elapsed_runs: List[int] = []
    final_result = 0
    for _ in range(repeats):
        if mode == "direct":
            elapsed_ns, result = _measure_ns(
                owner.run_direct_chain,
                iterations=iterations,
                access_count=access_count,
                depth=depth,
            )
        elif mode == "alias":
            elapsed_ns, result = _measure_ns(
                owner.run_alias_chain,
                iterations=iterations,
                access_count=access_count,
                depth=depth,
            )
        else:
            raise ValueError("mode must be either 'direct' or 'alias'.")
        elapsed_runs.append(elapsed_ns)
        final_result = result
    return sum(elapsed_runs) / float(repeats), final_result


def _average_chain_param_mode_ns(
        *,
        chain_root: _ChainRoot,
        mode: str,
        iterations: int,
        access_count: int,
        depth: int,
        repeats: int,
) -> Tuple[float, int]:
    """
    Measure average elapsed nanoseconds for chained parameter-attribute modes.

    Args:
        chain_root: Root object passed into benchmark functions.
        mode: Either ``"direct"`` or ``"alias"``.
        iterations: Loop iterations per run.
        access_count: Number of dependency accesses per iteration.
        depth: Chain depth to resolve (2, 3, or 4).
        repeats: Number of repeated timed runs to average.

    Returns:
        Tuple[float, int]: (average_total_ns, final_checksum_result).
    """
    elapsed_runs: List[int] = []
    final_result = 0
    for _ in range(repeats):
        if mode == "direct":
            elapsed_ns, result = _measure_ns(
                _run_param_chain_direct,
                chain_root=chain_root,
                iterations=iterations,
                access_count=access_count,
                depth=depth,
            )
        elif mode == "alias":
            elapsed_ns, result = _measure_ns(
                _run_param_chain_alias,
                chain_root=chain_root,
                iterations=iterations,
                access_count=access_count,
                depth=depth,
            )
        else:
            raise ValueError("mode must be either 'direct' or 'alias'.")
        elapsed_runs.append(elapsed_ns)
        final_result = result
    return sum(elapsed_runs) / float(repeats), final_result


def _expected_checksum(*, iterations: int, access_count: int) -> int:
    """
    Return expected checksum for correctness validation.

    Args:
        iterations: Loop iterations to execute.
        access_count: Number of dependency fields used per iteration.

    Returns:
        int: Expected deterministic checksum value.
    """
    if access_count == 1:
        return iterations * 1
    if access_count == 2:
        return iterations * (1 + 2)
    if access_count == 3:
        return iterations * (1 + 2 + 3)
    if access_count == 4:
        return iterations * (1 + 2 + 3 + 4)
    raise ValueError("access_count must be between 1 and 4.")


def test_local_alias_vs_direct_attribute_access_perf() -> None:
    """
    Compare local aliasing versus direct ``self`` attribute access.

    Contract:
        - Uses exactly 1,000,000 iterations per scenario.
        - Measures access-count scenarios 1, 2, 3, and 4.
        - Prints average total time and average ns/iteration for each mode.
        - Validates checksums for both modes in every scenario.
    """
    iterations = 1_000_000
    repeats = 5
    owner = _Owner(_SharedDependencies())

    print(
        "[alias-vs-direct] iterations={0}, repeats={1}".format(
            iterations,
            repeats,
        )
    )
    print(
        "[alias-vs-direct] columns: accesses | direct_avg_total_ns | "
        "direct_avg_ns_per_iter | alias_avg_total_ns | alias_avg_ns_per_iter | "
        "alias_over_direct_ratio"
    )

    rows_emitted = 0
    for access_count in (1, 2, 3, 4):
        direct_avg_ns, direct_result = _average_mode_ns(
            owner=owner,
            mode="direct",
            iterations=iterations,
            access_count=access_count,
            repeats=repeats,
        )
        alias_avg_ns, alias_result = _average_mode_ns(
            owner=owner,
            mode="alias",
            iterations=iterations,
            access_count=access_count,
            repeats=repeats,
        )
        expected = _expected_checksum(
            iterations=iterations,
            access_count=access_count,
        )
        assert direct_result == expected
        assert alias_result == expected

        direct_avg_per_iter = direct_avg_ns / float(iterations)
        alias_avg_per_iter = alias_avg_ns / float(iterations)
        ratio = alias_avg_ns / direct_avg_ns
        print(
            "[alias-vs-direct] accesses={0} | direct_total_ns={1:.0f} | "
            "direct_ns_per_iter={2:.6f} | alias_total_ns={3:.0f} | "
            "alias_ns_per_iter={4:.6f} | ratio={5:.6f}".format(
                access_count,
                direct_avg_ns,
                direct_avg_per_iter,
                alias_avg_ns,
                alias_avg_per_iter,
                ratio,
            )
        )
        rows_emitted += 1

    assert rows_emitted == 4


def test_local_alias_vs_direct_parameter_attr_access_perf() -> None:
    """
    Compare local aliasing versus direct parameter-attribute access.

    Contract:
        - Uses exactly 1,000,000 iterations per scenario.
        - Measures access-count scenarios 1, 2, 3, and 4.
        - Prints average total time and average ns/iteration for each mode.
        - Validates checksums for both modes in every scenario.
    """
    iterations = 1_000_000
    repeats = 5
    shared = _SharedDependencies()

    print(
        "[param-alias-vs-direct] iterations={0}, repeats={1}".format(
            iterations,
            repeats,
        )
    )
    print(
        "[param-alias-vs-direct] columns: accesses | direct_avg_total_ns | "
        "direct_avg_ns_per_iter | alias_avg_total_ns | alias_avg_ns_per_iter | "
        "alias_over_direct_ratio"
    )

    rows_emitted = 0
    for access_count in (1, 2, 3, 4):
        direct_avg_ns, direct_result = _average_param_mode_ns(
            shared=shared,
            mode="direct",
            iterations=iterations,
            access_count=access_count,
            repeats=repeats,
        )
        alias_avg_ns, alias_result = _average_param_mode_ns(
            shared=shared,
            mode="alias",
            iterations=iterations,
            access_count=access_count,
            repeats=repeats,
        )
        expected = _expected_checksum(
            iterations=iterations,
            access_count=access_count,
        )
        assert direct_result == expected
        assert alias_result == expected

        direct_avg_per_iter = direct_avg_ns / float(iterations)
        alias_avg_per_iter = alias_avg_ns / float(iterations)
        ratio = alias_avg_ns / direct_avg_ns
        print(
            "[param-alias-vs-direct] accesses={0} | direct_total_ns={1:.0f} | "
            "direct_ns_per_iter={2:.6f} | alias_total_ns={3:.0f} | "
            "alias_ns_per_iter={4:.6f} | ratio={5:.6f}".format(
                access_count,
                direct_avg_ns,
                direct_avg_per_iter,
                alias_avg_ns,
                alias_avg_per_iter,
                ratio,
            )
        )
        rows_emitted += 1

    assert rows_emitted == 4


def test_local_alias_vs_direct_self_chained_attr_access_perf() -> None:
    """
    Compare direct versus aliased chained self-attribute access (depth 2..4).

    Contract:
        - Uses exactly 1,000,000 iterations per scenario.
        - Measures chain depth 2, 3, and 4.
        - Measures access-count scenarios 1, 2, 3, and 4.
        - Prints averaged timing rows for each (depth, access_count) pair.
        - Validates checksums for both modes in every scenario.
    """
    iterations = 1_000_000
    repeats = 3
    owner = _OwnerWithChain(_ChainRoot())

    print(
        "[self-chain-alias-vs-direct] iterations={0}, repeats={1}".format(
            iterations,
            repeats,
        )
    )
    print(
        "[self-chain-alias-vs-direct] columns: depth | accesses | "
        "direct_avg_total_ns | direct_avg_ns_per_iter | alias_avg_total_ns | "
        "alias_avg_ns_per_iter | alias_over_direct_ratio"
    )

    rows_emitted = 0
    for depth in (2, 3, 4):
        for access_count in (1, 2, 3, 4):
            direct_avg_ns, direct_result = _average_chain_self_mode_ns(
                owner=owner,
                mode="direct",
                iterations=iterations,
                access_count=access_count,
                depth=depth,
                repeats=repeats,
            )
            alias_avg_ns, alias_result = _average_chain_self_mode_ns(
                owner=owner,
                mode="alias",
                iterations=iterations,
                access_count=access_count,
                depth=depth,
                repeats=repeats,
            )
            expected = _expected_checksum(
                iterations=iterations,
                access_count=access_count,
            )
            assert direct_result == expected
            assert alias_result == expected

            direct_avg_per_iter = direct_avg_ns / float(iterations)
            alias_avg_per_iter = alias_avg_ns / float(iterations)
            ratio = alias_avg_ns / direct_avg_ns
            print(
                "[self-chain-alias-vs-direct] depth={0} | accesses={1} | "
                "direct_total_ns={2:.0f} | direct_ns_per_iter={3:.6f} | "
                "alias_total_ns={4:.0f} | alias_ns_per_iter={5:.6f} | "
                "ratio={6:.6f}".format(
                    depth,
                    access_count,
                    direct_avg_ns,
                    direct_avg_per_iter,
                    alias_avg_ns,
                    alias_avg_per_iter,
                    ratio,
                )
            )
            rows_emitted += 1

    assert rows_emitted == 12


def test_local_alias_vs_direct_parameter_chained_attr_access_perf() -> None:
    """
    Compare direct versus aliased chained parameter-attribute access (depth 2..4).

    Contract:
        - Uses exactly 1,000,000 iterations per scenario.
        - Measures chain depth 2, 3, and 4.
        - Measures access-count scenarios 1, 2, 3, and 4.
        - Prints averaged timing rows for each (depth, access_count) pair.
        - Validates checksums for both modes in every scenario.
    """
    iterations = 1_000_000
    repeats = 3
    chain_root = _ChainRoot()

    print(
        "[param-chain-alias-vs-direct] iterations={0}, repeats={1}".format(
            iterations,
            repeats,
        )
    )
    print(
        "[param-chain-alias-vs-direct] columns: depth | accesses | "
        "direct_avg_total_ns | direct_avg_ns_per_iter | alias_avg_total_ns | "
        "alias_avg_ns_per_iter | alias_over_direct_ratio"
    )

    rows_emitted = 0
    for depth in (2, 3, 4):
        for access_count in (1, 2, 3, 4):
            direct_avg_ns, direct_result = _average_chain_param_mode_ns(
                chain_root=chain_root,
                mode="direct",
                iterations=iterations,
                access_count=access_count,
                depth=depth,
                repeats=repeats,
            )
            alias_avg_ns, alias_result = _average_chain_param_mode_ns(
                chain_root=chain_root,
                mode="alias",
                iterations=iterations,
                access_count=access_count,
                depth=depth,
                repeats=repeats,
            )
            expected = _expected_checksum(
                iterations=iterations,
                access_count=access_count,
            )
            assert direct_result == expected
            assert alias_result == expected

            direct_avg_per_iter = direct_avg_ns / float(iterations)
            alias_avg_per_iter = alias_avg_ns / float(iterations)
            ratio = alias_avg_ns / direct_avg_ns
            print(
                "[param-chain-alias-vs-direct] depth={0} | accesses={1} | "
                "direct_total_ns={2:.0f} | direct_ns_per_iter={3:.6f} | "
                "alias_total_ns={4:.0f} | alias_ns_per_iter={5:.6f} | "
                "ratio={6:.6f}".format(
                    depth,
                    access_count,
                    direct_avg_ns,
                    direct_avg_per_iter,
                    alias_avg_ns,
                    alias_avg_per_iter,
                    ratio,
                )
            )
            rows_emitted += 1

    assert rows_emitted == 12
