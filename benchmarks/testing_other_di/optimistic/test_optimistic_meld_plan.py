"""
Purpose:
    Provide optimistic plan execution benchmarks that bypass meld runtime
    overhead and measure a minimal compiled-plan style loop.
Contract:
    - Uses only mocked Creations and a Conduit-like wrapper.
    - Builds a precomputed plan from constructor annotations.
    - Skips storage for many/transient existences to lower overhead.
    - Prints timing results; no performance thresholds are asserted.
"""

import inspect
import time
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import pytest

from tests.mocks.spellbook.deep_layers import (
    get_depth_3_classes,
    get_depth_5_classes,
    get_depth_9_classes,
)


class CreationsMock:
    """
    Purpose:
        Provide a minimal creations-like store for optimistic plan execution.
    Contract:
        - Stores the latest instance per key when invoked.
        - Does not perform reuse checks or cleanup.
    """
    __slots__ = ("_store",)

    def __init__(self) -> None:
        """
        Purpose:
            Initialize the internal store.
        Contract:
            - Starts with an empty store.
        """
        self._store: Dict[object, object] = {}

    def store(self, key: object, value: object) -> None:
        """
        Purpose:
            Store an instance under a key.
        Contract:
            - Overwrites any prior value for the same key.
        Args:
            key: Storage key (typically a class/type).
            value: Instance to store.
        Returns:
            None.
        """
        self._store[key] = value


class ConduitMock:
    """
    Purpose:
        Provide a minimal conduit-like wrapper that owns Creations.
    Contract:
        - Delegates execution to an OptimisticPlan using its Creations.
    """
    __slots__ = ("_creations",)

    def __init__(self, creations: CreationsMock) -> None:
        """
        Purpose:
            Capture a CreationsMock instance.
        Contract:
            - Stores the provided creations reference.
        Args:
            creations: Creations-like store used during execution.
        """
        self._creations = creations

    def execute_plan(self, plan: "OptimisticPlan") -> object:
        """
        Purpose:
            Execute a precompiled plan using this conduit's creations.
        Contract:
            - Returns the root instance produced by the plan.
        Args:
            plan: OptimisticPlan to execute.
        Returns:
            object: Root instance.
        """
        return plan.execute(self._creations)


class OptimisticPlan:
    """
    Purpose:
        Execute a precomputed plan in topological order with minimal overhead.
    Contract:
        - Executes steps sequentially and stores when requested.
        - Returns the root instance at root_index.
    """
    __slots__ = (
        "_call_targets",
        "_dep_a",
        "_dep_b",
        "_store_flags",
        "_root_index",
        "_scratch",
    )

    def __init__(
        self,
        call_targets: Sequence[Callable[..., object]],
        dep_a: Sequence[int],
        dep_b: Sequence[int],
        store_flags: Sequence[bool],
        root_index: int,
    ) -> None:
        """
        Purpose:
            Capture the compiled plan arrays and root index.
        Contract:
            - call_targets/dep arrays must be in dependency-safe order.
            - root_index must point into call_targets.
            - Arrays must be of equal length.
        Args:
            call_targets: Ordered call targets for each step.
            dep_a: First dependency index per step (-1 for none).
            dep_b: Second dependency index per step (-1 for none).
            store_flags: Store flag per step (True to store).
            root_index: Index of the root step in call_targets.
        """
        if call_targets is None:
            raise ValueError("call_targets must not be None.")
        step_count = len(call_targets)
        if step_count == 0:
            raise ValueError("call_targets must not be empty.")
        if len(dep_a) != step_count or len(dep_b) != step_count:
            raise ValueError("Dependency arrays must match call target count.")
        if len(store_flags) != step_count:
            raise ValueError("Store flags must match call target count.")
        if root_index < 0 or root_index >= step_count:
            raise ValueError("root_index is out of bounds.")
        self._call_targets = list(call_targets)
        self._dep_a = list(dep_a)
        self._dep_b = list(dep_b)
        self._store_flags = list(store_flags)
        self._root_index = root_index
        self._scratch = [None] * step_count

    def execute(self, creations: CreationsMock) -> object:
        """
        Purpose:
            Execute the plan and return the root instance.
        Contract:
            - Creates instances in order without reuse checks.
            - Stores instances only when store flags are enabled.
            - Reuses an internal scratch list (single-threaded).
        Args:
            creations: Creations-like store for instances.
        Returns:
            object: Root instance.
        """
        call_targets = self._call_targets
        dep_a = self._dep_a
        dep_b = self._dep_b
        store_flags = self._store_flags
        values = self._scratch
        store = creations._store
        step_count = len(call_targets)

        for idx in range(step_count):
            target = call_targets[idx]
            first = dep_a[idx]
            if first < 0:
                instance = target()
            else:
                second = dep_b[idx]
                if second < 0:
                    instance = target(values[first])
                else:
                    instance = target(values[first], values[second])
            values[idx] = instance
            if store_flags[idx]:
                store[target] = instance

        return values[self._root_index]


def _dependency_types(cls: type) -> Tuple[type, ...]:
    """
    Purpose:
        Extract constructor dependency types from annotations.
    Contract:
        - Ignores "self"/"cls" and var-arg parameters.
        - Requires concrete annotations for all dependencies.
    Args:
        cls: Class whose __init__ signature is inspected.
    Returns:
        Tuple[type, ...]: Dependency types in parameter order.
    Raises:
        ValueError: If a dependency annotation is missing.
    """
    signature = inspect.signature(cls.__init__)
    dependencies: List[type] = []

    for name, parameter in signature.parameters.items():
        if name in ("self", "cls"):
            continue
        if parameter.kind in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        ):
            continue
        annotation = parameter.annotation
        if annotation is inspect.Parameter.empty:
            raise ValueError(f"Missing annotation for {cls.__name__}.{name}.")
        dependencies.append(annotation)

    return tuple(dependencies)


def _normalize_existence_label(existence: object) -> str:
    """
    Purpose:
        Normalize an existence label to lowercase text.
    Contract:
        - Falls back to "unique" when missing.
    Args:
        existence: Label or enum value describing existence.
    Returns:
        str: Normalized existence label.
    """
    if existence is None:
        return "unique"
    label = str(existence).strip().lower()
    if not label:
        return "unique"
    return label


def _should_store(existence: object) -> bool:
    """
    Purpose:
        Decide whether a creation should be stored.
    Contract:
        - Skips storage for "many" or "transient" existences.
    Args:
        existence: Label or enum describing existence.
    Returns:
        bool: True if creation should be stored.
    """
    label = _normalize_existence_label(existence)
    return label not in ("many", "transient")


def _build_many_existence_map(classes: Sequence[type]) -> Dict[type, str]:
    """
    Purpose:
        Mark every class as many/transient for optimistic execution.
    Contract:
        - Returns a mapping for all provided classes.
    Args:
        classes: Classes to mark as many/transient.
    Returns:
        Dict[type, str]: Existence map keyed by class.
    """
    existence_by_class: Dict[type, str] = {}
    for cls in classes:
        existence_by_class[cls] = "many"
    return existence_by_class


def _build_plan(
    classes: Sequence[type],
    existence_by_class: Optional[Dict[type, object]] = None,
) -> OptimisticPlan:
    """
    Purpose:
        Build an OptimisticPlan from dependency-ordered classes.
    Contract:
        - classes must be ordered leaves-to-root.
        - All dependency annotations must refer to classes in the list.
        - Supports up to two dependencies per class for fast-path execution.
    Args:
        classes: Dependency-ordered classes.
        existence_by_class: Optional existence labels per class.
    Returns:
        OptimisticPlan: Compiled plan for execution.
    Raises:
        ValueError: If a dependency class is not in the plan.
    """
    if not classes:
        raise ValueError("classes must not be empty.")

    if existence_by_class is None:
        existence_by_class = {}

    class_to_index: Dict[type, int] = {
        cls: idx for idx, cls in enumerate(classes)
    }
    call_targets: List[Callable[..., object]] = []
    dep_a: List[int] = []
    dep_b: List[int] = []
    store_flags: List[bool] = []

    for cls in classes:
        dep_types = _dependency_types(cls)
        if len(dep_types) > 2:
            raise ValueError(
                f"Optimistic plan only supports up to 2 deps, got {cls.__name__}."
            )
        if len(dep_types) == 0:
            dep_a.append(-1)
            dep_b.append(-1)
        elif len(dep_types) == 1:
            dep = dep_types[0]
            if dep not in class_to_index:
                raise ValueError(
                    f"Dependency {dep} for {cls.__name__} is not in the plan."
                )
            dep_a.append(class_to_index[dep])
            dep_b.append(-1)
        else:
            first_dep = dep_types[0]
            second_dep = dep_types[1]
            if first_dep not in class_to_index:
                raise ValueError(
                    f"Dependency {first_dep} for {cls.__name__} is not in the plan."
                )
            if second_dep not in class_to_index:
                raise ValueError(
                    f"Dependency {second_dep} for {cls.__name__} is not in the plan."
                )
            dep_a.append(class_to_index[first_dep])
            dep_b.append(class_to_index[second_dep])
        call_targets.append(cls)
        store_flags.append(_should_store(existence_by_class.get(cls)))

    return OptimisticPlan(
        call_targets=call_targets,
        dep_a=dep_a,
        dep_b=dep_b,
        store_flags=store_flags,
        root_index=len(call_targets) - 1,
    )


def _ms(seconds: float) -> float:
    """
    Purpose:
        Convert seconds to milliseconds.
    Args:
        seconds: Duration in seconds.
    Returns:
        float: Duration in milliseconds.
    """
    return seconds * 1000.0


def _us(seconds: float) -> float:
    """
    Purpose:
        Convert seconds to microseconds.
    Args:
        seconds: Duration in seconds.
    Returns:
        float: Duration in microseconds.
    """
    return seconds * 1_000_000.0


@pytest.mark.parametrize(
    "label, classes, iterations",
    (
        ("depth3", get_depth_3_classes(), 200000),
        ("depth5", get_depth_5_classes(), 100000),
        ("depth9", get_depth_9_classes(), 50000),
    ),
)
def test_optimistic_plan_execution_depths(
    label: str,
    classes: Sequence[type],
    iterations: int,
) -> None:
    """
    Purpose:
        Benchmark an optimistic compiled-plan execution loop for deep graphs.
    Contract:
        - Uses a single ConduitMock and CreationsMock per case.
        - Prints average execution time per iteration.
        - Does not enforce timing thresholds.
    Args:
        label: Depth label used in printed output.
        classes: Dependency-ordered class list for the plan.
        iterations: Loop count for timing.
    """
    existence_by_class = _build_many_existence_map(classes)
    plan = _build_plan(classes, existence_by_class=existence_by_class)
    creations = CreationsMock()
    conduit = ConduitMock(creations)

    # Warm up interpreter caches and plan execution.
    root = conduit.execute_plan(plan)
    assert isinstance(root, classes[-1])

    execute = conduit.execute_plan
    t0 = time.perf_counter()
    for _ in range(iterations):
        root = execute(plan)
    total_s = time.perf_counter() - t0

    assert isinstance(root, classes[-1])

    print(
        f"Optimistic plan {label}: iterations={iterations}, "
        f"avg_ms={_ms(total_s) / iterations:.6f}, "
        f"avg_us={_us(total_s) / iterations:.3f}"
    )
