import inspect
import typing
from typing import Dict, List, Sequence, Set, Tuple

import pytest

import benchmarks.testing_other_di.test_shallow_all as shallow_graphs


class _MetricsAccumulator:
    """
    Purpose:
        Accumulate transient graph metrics during dependency expansion.
    Contract:
        - max_depth uses root depth = 0.
        - max_dependency_count records the maximum constructor arity.
        - has_calln is True when any node exceeds 8 dependencies.
    """
    __slots__ = ("max_depth", "max_dependency_count", "has_calln")

    def __init__(self) -> None:
        """
        Purpose:
            Initialize accumulator fields.
        Returns:
            None.
        """
        self.max_depth = 0
        self.max_dependency_count = 0
        self.has_calln = False


class _ExecutionPlanMetrics:
    """
    Purpose:
        Phase 11-style metrics for a transient-only graph.
    Contract:
        - preferred_route follows SpellCrafter Phase 11 thresholds.
        - fast_transient_candidate is True when no CALLN is required.
    """
    __slots__ = (
        "step_count",
        "unique_spell_count",
        "max_occurrence_depth",
        "max_dependency_count",
        "has_calln",
        "fast_transient_candidate",
        "preferred_route",
    )

    def __init__(
        self,
        *,
        step_count: int,
        unique_spell_count: int,
        max_occurrence_depth: int,
        max_dependency_count: int,
        has_calln: bool,
        fast_transient_candidate: bool,
        preferred_route: str,
    ) -> None:
        """
        Purpose:
            Store derived Phase 11-style metrics.
        Args:
            step_count: Total transient occurrences.
            unique_spell_count: Unique class count.
            max_occurrence_depth: Maximum depth (root depth = 0).
            max_dependency_count: Maximum constructor dependency count.
            has_calln: True when any node requires CALLN.
            fast_transient_candidate: True when CALLN-free.
            preferred_route: Preferred routing tier label.
        Returns:
            None.
        """
        self.step_count = step_count
        self.unique_spell_count = unique_spell_count
        self.max_occurrence_depth = max_occurrence_depth
        self.max_dependency_count = max_dependency_count
        self.has_calln = has_calln
        self.fast_transient_candidate = fast_transient_candidate
        self.preferred_route = preferred_route


def _ctor_param_types(cls: type) -> Tuple[type, ...]:
    """
    Purpose:
        Extract typed constructor dependencies for a class.
    Contract:
        - Treats object.__init__ / varargs-only __init__ as no dependencies.
        - Uses typing.get_type_hints when available.
        - Raises AssertionError when a param lacks a concrete type annotation.
    Args:
        cls: Class to inspect.
    Returns:
        Tuple[type, ...]: Dependency types in parameter order.
    """
    init = cls.__init__
    sig = inspect.signature(init)
    params = list(sig.parameters.values())[1:]

    if params and all(
        p.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
        for p in params
    ):
        return ()

    try:
        hints = typing.get_type_hints(init, include_extras=True)
    except Exception:
        hints = getattr(init, "__annotations__", {}) or {}

    out: List[type] = []
    for p in params:
        ann = hints.get(p.name, p.annotation)
        if ann is inspect._empty or ann is None:
            raise AssertionError(f"{cls.__name__}.__init__ param '{p.name}' missing annotation")
        if not isinstance(ann, type):
            raise AssertionError(
                f"{cls.__name__}.__init__ param '{p.name}' has non-type annotation: {ann!r}"
            )
        out.append(ann)
    return tuple(out)


def _count_transient_occurrences(
    *,
    root_cls: type,
    accumulator: _MetricsAccumulator,
    unique_types: Set[type],
    depth: int,
) -> int:
    """
    Purpose:
        Recursively expand a transient graph and update metrics.
    Contract:
        - Each dependency occurrence is counted independently.
        - Root depth is zero.
    Args:
        root_cls: Class to expand.
        accumulator: Mutable accumulator for depth/arity metrics.
        unique_types: Set tracking unique classes.
        depth: Current depth for this node.
    Returns:
        int: Total occurrence count for this subtree.
    """
    unique_types.add(root_cls)
    deps = _ctor_param_types(root_cls)
    dep_count = len(deps)
    accumulator.max_depth = max(accumulator.max_depth, depth)
    accumulator.max_dependency_count = max(accumulator.max_dependency_count, dep_count)
    if dep_count > 8:
        accumulator.has_calln = True

    step_count = 1
    for dep in deps:
        step_count += _count_transient_occurrences(
            root_cls=dep,
            accumulator=accumulator,
            unique_types=unique_types,
            depth=depth + 1,
        )
    return step_count


def _preferred_route(
    *,
    step_count: int,
    max_depth: int,
    max_dependency_count: int,
    fast_transient_candidate: bool,
) -> str:
    """
    Purpose:
        Mirror SpellCrafter Phase 11 preferred-route thresholds.
    Contract:
        - Returns ENGINE when thresholds are not met or fast candidate is False.
    Args:
        step_count: Total transient occurrences.
        max_depth: Maximum depth with root at 0.
        max_dependency_count: Max constructor dependency count.
        fast_transient_candidate: True when CALLN-free.
    Returns:
        str: Preferred route label.
    """
    preferred_route = "ENGINE"
    if fast_transient_candidate:
        if max_depth <= 3 and step_count <= 8:
            preferred_route = "FAST_TRANSIENT_TIER_0"
        elif max_depth <= 6 and step_count <= 16 and max_dependency_count <= 8:
            preferred_route = "FAST_TRANSIENT_TIER_1"
        elif max_depth <= 8 and step_count <= 24 and max_dependency_count <= 8:
            preferred_route = "FAST_TRANSIENT_TIER_2"
        elif max_depth <= 9 and step_count <= 32 and max_dependency_count <= 10:
            preferred_route = "FAST_TRANSIENT_TIER_3"
    return preferred_route


def _compute_metrics(root_cls: type) -> _ExecutionPlanMetrics:
    """
    Purpose:
        Compute Phase 11-style metrics for a transient-only graph.
    Contract:
        - Uses constructor annotations for dependency expansion.
        - Assumes no overrides and no existing-creation nodes.
    Args:
        root_cls: Root class for the graph.
    Returns:
        _ExecutionPlanMetrics: Derived metrics.
    """
    accumulator = _MetricsAccumulator()
    unique_types: Set[type] = set()
    step_count = _count_transient_occurrences(
        root_cls=root_cls,
        accumulator=accumulator,
        unique_types=unique_types,
        depth=0,
    )
    fast_transient_candidate = not accumulator.has_calln
    preferred_route = _preferred_route(
        step_count=step_count,
        max_depth=accumulator.max_depth,
        max_dependency_count=accumulator.max_dependency_count,
        fast_transient_candidate=fast_transient_candidate,
    )
    return _ExecutionPlanMetrics(
        step_count=step_count,
        unique_spell_count=len(unique_types),
        max_occurrence_depth=accumulator.max_depth,
        max_dependency_count=accumulator.max_dependency_count,
        has_calln=accumulator.has_calln,
        fast_transient_candidate=fast_transient_candidate,
        preferred_route=preferred_route,
    )


def _expected_metrics() -> Dict[Tuple[str, str], Tuple[int, int, int, int, bool, str]]:
    """
    Purpose:
        Provide expected metrics for each benchmark graph root.
    Returns:
        Dict mapping (graph_name, root_label) to:
            (step_count, unique_count, max_depth, max_dep_count, has_calln, preferred_route)
    """
    return {
        ("solo", "A"): (1, 1, 0, 0, False, "FAST_TRANSIENT_TIER_0"),
        ("solo", "B"): (1, 1, 0, 0, False, "FAST_TRANSIENT_TIER_0"),
        ("shallow", "A"): (3, 3, 1, 2, False, "FAST_TRANSIENT_TIER_0"),
        ("shallow", "B"): (2, 2, 1, 1, False, "FAST_TRANSIENT_TIER_0"),
        ("wide", "A"): (9, 9, 1, 8, False, "FAST_TRANSIENT_TIER_1"),
        ("wide", "B"): (13, 13, 2, 3, False, "FAST_TRANSIENT_TIER_1"),
        ("diamond", "A"): (5, 4, 2, 2, False, "FAST_TRANSIENT_TIER_0"),
        ("diamond", "B"): (3, 3, 1, 2, False, "FAST_TRANSIENT_TIER_0"),
        ("deep", "A"): (511, 17, 8, 2, False, "ENGINE"),
        ("deep", "B"): (127, 13, 6, 2, False, "ENGINE"),
    }


def _print_metrics(
    graph_name: str,
    root_label: str,
    metrics: _ExecutionPlanMetrics,
) -> None:
    """
    Purpose:
        Print a compact metrics row for diagnostics.
    Args:
        graph_name: Graph shape label.
        root_label: Root label (A/B).
        metrics: Metrics to print.
    Returns:
        None.
    """
    print(
        f"{graph_name:7} {root_label:4} "
        f"{metrics.step_count:5d} {metrics.unique_spell_count:6d} "
        f"{metrics.max_occurrence_depth:9d} {metrics.max_dependency_count:8d} "
        f"{str(metrics.has_calln):5} {str(metrics.fast_transient_candidate):4} "
        f"{metrics.preferred_route}"
    )


@pytest.mark.parametrize("graph", shallow_graphs._all_graphs())
def test_shallow_graph_phase11_diagnostics(graph: object) -> None:
    """
    Purpose:
        Print Phase 11-style metrics for shallow benchmark graph roots.
    Contract:
        - Uses transient occurrence expansion without caching.
        - Asserts expected metrics for each root.
    Args:
        graph: GraphSpec from test_shallow_all.
    Returns:
        None.
    """
    graph_name = graph.name
    metrics_a = _compute_metrics(graph.root_a)
    metrics_b = _compute_metrics(graph.root_b)

    print("graph   root steps unique max_depth max_deps calln fast route")
    _print_metrics(graph_name, "A", metrics_a)
    _print_metrics(graph_name, "B", metrics_b)

    expected = _expected_metrics()
    for label, metrics in (("A", metrics_a), ("B", metrics_b)):
        key = (graph_name, label)
        if key not in expected:
            raise AssertionError(f"Missing expected metrics for {graph_name} {label}")
        exp_step, exp_unique, exp_depth, exp_max_dep, exp_calln, exp_route = expected[key]
        assert metrics.step_count == exp_step
        assert metrics.unique_spell_count == exp_unique
        assert metrics.max_occurrence_depth == exp_depth
        assert metrics.max_dependency_count == exp_max_dep
        assert metrics.has_calln is exp_calln
        assert metrics.preferred_route == exp_route
