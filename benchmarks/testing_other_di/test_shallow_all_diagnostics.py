import gc
import os
from pathlib import Path
import sys
import time
from typing import Any, Callable, Dict, Tuple

import pytest

import benchmarks.testing_other_di.test_shallow_all as shallow_all


def _ensure_src_on_path() -> None:
    """
    Purpose:
        Ensure the repository src/ directory is on sys.path for local imports.
    Contract:
        - Prepends src/ to sys.path if it exists and is not already present.
    Returns:
        None.
    """
    project_root = Path(__file__).resolve().parents[2]
    src_path = project_root / "src"
    if src_path.exists():
        src_as_str = str(src_path)
        if src_as_str not in sys.path:
            sys.path.insert(0, src_as_str)


_ensure_src_on_path()


def _env_int_nonneg(name: str, default: int) -> int:
    """
    Purpose:
        Read an env var as a non-negative int with a safe default.
    Contract:
        - Returns default when unset or empty.
        - Clamps negative values to 0.
        - Raises AssertionError on non-integer inputs.
    Args:
        name: Environment variable name.
        default: Default value when env var is missing.
    Returns:
        int: Parsed non-negative value.
    """
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise AssertionError(f"{name} must be an int, got: {raw!r}") from exc
    return value if value >= 0 else 0


def _build_melder_conduit(graph: object) -> Tuple[Any, str, str, Callable[[], None]]:
    """
    Purpose:
        Build a Melder Conduit wired to the test_shallow_all graph specs.
    Contract:
        - Mirrors the bind logic in test_shallow_all._build_runtime_melder.
        - Returns a cleanup callable that resets Aether/Spellbook globals.
    Args:
        graph: GraphSpec from test_shallow_all.
    Returns:
        Tuple[Any, str, str, Callable[[], None]]:
            (conduit, root_a_id, root_b_id, cleanup)
    """
    from melder.aether.aether import Aether
    from melder.aether.conduit.conduit import Conduit
    from melder.aether.spellbook.existence.existence import Existence
    from melder.aether.spellbook.spellbook import Spellbook

    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether

    spellbook = Spellbook(aetheric_frame="threaded-di-stress")
    cfg = spellbook.get_configuration()
    cfg.set_property("phase_scheduler_workers_per_spellbook", 1)

    ids_a: Dict[type, str] = {}
    for cls in graph.root_a_classes:
        ids_a[cls] = spellbook.bind(spell=cls, existence=Existence.many, permissions="create")

    ids_b: Dict[type, str] = {}
    for cls in graph.root_b_classes:
        if cls in ids_a:
            continue
        ids_b[cls] = spellbook.bind(spell=cls, existence=Existence.many, permissions="create")

    ids_space: Dict[type, str] = {}
    for cls in graph.spellspace_classes:
        if cls in ids_a or cls in ids_b:
            continue
        ids_space[cls] = spellbook.bind(
            spell=cls,
            existence=Existence.unique_per_spell_space,
            permissions="create",
        )

    root_a_id = ids_a.get(graph.root_a)
    if root_a_id is None:
        raise AssertionError("Melder diagnostics: missing root_a id")

    root_b_id = ids_b.get(graph.root_b) or ids_a.get(graph.root_b)
    if root_b_id is None:
        raise AssertionError("Melder diagnostics: missing root_b id")

    root_space_id = ids_space.get(graph.spellspace_root) or ids_a.get(graph.spellspace_root) or ids_b.get(
        graph.spellspace_root
    )
    if root_space_id is None:
        raise AssertionError("Melder diagnostics: missing spellspace root id")

    conduit = spellbook.conjure(name="threaded-di-stress")

    def cleanup() -> None:
        """
        Purpose:
            Clean up the conduit and reset Aether/Spellbook globals.
        Returns:
            None.
        """
        try:
            conduit.cleanup()
        finally:
            Aether._reset_singleton_for_tests()
            aether2 = Aether()
            Spellbook._aether = aether2
            Conduit._aether = aether2
        gc.collect()

    return conduit, root_a_id, root_b_id, cleanup


def _lookup_spell(meld: Any, spell_id: str) -> Any:
    """
    Purpose:
        Fetch a Spell object by spell_id from the Meld instance.
    Contract:
        - Raises AssertionError if the spell_id is missing.
    Args:
        meld: Conduit._meld instance.
        spell_id: Spell SHA256 identifier.
    Returns:
        Any: Spell instance for the given id.
    """
    spell = meld._spells_by_id.get(spell_id)
    if spell is None:
        raise AssertionError(f"Melder diagnostics: missing spell for id={spell_id}")
    return spell


def _install_runtime_route_tracer(
    runtime: Any,
    root_classes: Tuple[type, ...],
) -> Tuple[Dict[type, str], Dict[str, int], Callable[[], None]]:
    """
    Purpose:
        Wrap MeldRuntime methods to record which execution route is used.
    Contract:
        - Records routes for root classes only.
        - Raises AssertionError if a root flips routes within a test.
    Args:
        runtime: MeldRuntime instance to wrap.
        root_classes: Root classes to track.
    Returns:
        Tuple[Dict[type, str], Dict[str, int], Callable[[], None]]:
            (routes_by_root, route_counts, restore)
    """
    routes_by_root: Dict[type, str] = {}
    route_counts: Dict[str, int] = {}

    def _record(spell: Any, route: str) -> None:
        """
        Purpose:
            Record a route for a root spell and enforce stability.
        Args:
            spell: Spell instance passed to the runtime.
            route: Route label.
        Returns:
            None.
        """
        root_cls = spell.spell
        if root_cls in root_classes:
            prior = routes_by_root.get(root_cls)
            if prior is None:
                routes_by_root[root_cls] = route
            elif prior != route:
                raise AssertionError(f"Route changed for {root_cls.__name__}: {prior} -> {route}")
        route_counts[route] = route_counts.get(route, 0) + 1

    runtime_cls = runtime.__class__
    original_fast = runtime_cls.execute_fast_transient
    original_transient = runtime_cls.execute_transient_pooled
    original_shared = runtime_cls.execute_shared_pooled
    original_execute = runtime_cls.execute

    def execute_fast_transient(self: Any, *, spell: Any, conduit_id: Any) -> Any:
        """
        Purpose:
            Wrapper to record FAST_TRANSIENT route usage.
        Returns:
            Any: Result from the original runtime method.
        """
        _record(spell, "FAST_TRANSIENT")
        return original_fast(self, spell=spell, conduit_id=conduit_id)

    def execute_transient_pooled(
        self: Any,
        *,
        spell: Any,
        overrides: Any,
        caller_creations: Any,
        caller_creations_lock_held: bool,
        conduit_id: Any,
    ) -> Any:
        """
        Purpose:
            Wrapper to record TRANSIENT_POOLED route usage.
        Returns:
            Any: Result from the original runtime method.
        """
        _record(spell, "TRANSIENT_POOLED")
        return original_transient(
            self,
            spell=spell,
            overrides=overrides,
            caller_creations=caller_creations,
            caller_creations_lock_held=caller_creations_lock_held,
            conduit_id=conduit_id,
        )

    def execute_shared_pooled(
        self: Any,
        *,
        spell: Any,
        overrides: Any,
        caller_creations: Any,
        caller_creations_lock_held: bool,
        conduit_id: Any,
    ) -> Any:
        """
        Purpose:
            Wrapper to record SHARED_POOLED route usage.
        Returns:
            Any: Result from the original runtime method.
        """
        _record(spell, "SHARED_POOLED")
        return original_shared(
            self,
            spell=spell,
            overrides=overrides,
            caller_creations=caller_creations,
            caller_creations_lock_held=caller_creations_lock_held,
            conduit_id=conduit_id,
        )

    def execute(self: Any, context: Any) -> Any:
        """
        Purpose:
            Wrapper to record ENGINE route usage.
        Returns:
            Any: Result from the original runtime method.
        """
        root_spell = context.root_spell
        _record(root_spell, "ENGINE")
        return original_execute(self, context)

    runtime_cls.execute_fast_transient = execute_fast_transient
    runtime_cls.execute_transient_pooled = execute_transient_pooled
    runtime_cls.execute_shared_pooled = execute_shared_pooled
    runtime_cls.execute = execute

    def restore() -> None:
        """
        Purpose:
            Restore the original runtime methods after tracing.
        Returns:
            None.
        """
        runtime_cls.execute_fast_transient = original_fast
        runtime_cls.execute_transient_pooled = original_transient
        runtime_cls.execute_shared_pooled = original_shared
        runtime_cls.execute = original_execute

    return routes_by_root, route_counts, restore


def _expected_route(meld: Any, spell: Any) -> str:
    """
    Purpose:
        Compute the expected route based on Meld's public routing rules.
    Contract:
        - Assumes no overrides and no mutation overrides.
        - Mirrors the route selection order in Meld.meld.
    Args:
        meld: Conduit._meld instance.
        spell: Root spell to evaluate.
    Returns:
        str: Expected route label.
    """
    from melder.aether.spellbook.existence.existence import Existence

    if meld._should_use_fast_transient_shortcut(spell):
        return "FAST_TRANSIENT"
    if spell.existence is Existence.many:
        return "TRANSIENT_POOLED"
    preferred = spell.execution_plan_preferred_route
    if preferred and preferred.startswith("FAST_TRANSIENT"):
        return "SHARED_POOLED"
    return "ENGINE"


def _time_meld(conduit: Any, root_id: str, iterations: int) -> float:
    """
    Purpose:
        Measure average time per meld call for a root spell.
    Contract:
        - Returns 0.0 when iterations is 0.
    Args:
        conduit: Conduit instance.
        root_id: Spell id to resolve.
        iterations: Number of iterations to time.
    Returns:
        float: Average seconds per call.
    """
    if iterations <= 0:
        return 0.0
    start = time.perf_counter()
    for _ in range(iterations):
        conduit.meld(spell=root_id)
    elapsed = time.perf_counter() - start
    return elapsed / float(iterations)


def _fmt_int(value: Any) -> str:
    """
    Purpose:
        Format optional ints for compact diagnostic output.
    Args:
        value: Optional int-like value.
    Returns:
        str: Formatted value or '-' placeholder.
    """
    if value is None:
        return "-"
    return str(value)


def _print_header() -> None:
    """
    Purpose:
        Print the diagnostics table header.
    Returns:
        None.
    """
    print(
        "graph   root preferred_route         fast_plan shortcut actual_route       "
        "steps max_depth max_deps avg_us"
    )


def _print_row(
    *,
    graph_name: str,
    root_label: str,
    preferred_route: str,
    fast_plan: bool,
    shortcut: bool,
    actual_route: str,
    step_count: Any,
    max_depth: Any,
    max_deps: Any,
    avg_us: float,
) -> None:
    """
    Purpose:
        Print a single diagnostics row.
    Returns:
        None.
    """
    print(
        f"{graph_name:7} {root_label:4} {preferred_route:23} "
        f"{str(fast_plan):8} {str(shortcut):8} {actual_route:17} "
        f"{_fmt_int(step_count):5} {_fmt_int(max_depth):9} {_fmt_int(max_deps):8} "
        f"{avg_us:8.1f}"
    )


@pytest.mark.parametrize("graph", shallow_all._selected_graphs())
def test_shallow_all_melder_route_diagnostics(graph: object) -> None:
    """
    Purpose:
        Print actual Melder runtime route selection and timing for each graph root.
    Contract:
        - Uses real test_shallow_all bindings and Conduit meld calls.
        - Asserts actual runtime path matches Meld's routing rules.
    Args:
        graph: GraphSpec from test_shallow_all.
    Returns:
        None.
    """
    conduit = None
    cleanup: Callable[[], None] | None = None
    restore: Callable[[], None] | None = None

    try:
        conduit, root_a_id, root_b_id, cleanup = _build_melder_conduit(graph)
        meld = conduit._meld
        if meld is None:
            raise AssertionError("Melder diagnostics: Conduit missing Meld instance")

        runtime = meld._runtime
        routes_by_root, _route_counts, restore = _install_runtime_route_tracer(
            runtime,
            (graph.root_a, graph.root_b),
        )

        warmup_iters = _env_int_nonneg("DI_ROUTE_WARMUP", 1)
        if warmup_iters < 1:
            warmup_iters = 1
        time_iters = _env_int_nonneg("DI_ROUTE_ITERS", 50)

        _print_header()

        for label, root_id, root_cls in (
            ("A", root_a_id, graph.root_a),
            ("B", root_b_id, graph.root_b),
        ):
            for _ in range(warmup_iters):
                conduit.meld(spell=root_id)

            spell = _lookup_spell(meld, root_id)
            expected_route = _expected_route(meld, spell)
            actual_route = routes_by_root.get(root_cls, "UNKNOWN")

            avg_s = _time_meld(conduit, root_id, time_iters)
            avg_us = avg_s * 1_000_000.0

            crafter = spell._crafter
            plan = None if crafter is None else crafter.execution_plan_phase11_no_overrides
            fast_plan = plan is not None and plan.fast_transient_plan is not None

            preferred = spell.execution_plan_preferred_route or "-"
            step_count = spell.execution_plan_step_count
            max_depth = spell.execution_plan_max_occurrence_depth
            max_deps = spell.execution_plan_max_dependency_count
            shortcut = meld._should_use_fast_transient_shortcut(spell)

            _print_row(
                graph_name=graph.name,
                root_label=label,
                preferred_route=preferred,
                fast_plan=fast_plan,
                shortcut=shortcut,
                actual_route=actual_route,
                step_count=step_count,
                max_depth=max_depth,
                max_deps=max_deps,
                avg_us=avg_us,
            )

            assert actual_route == expected_route
    finally:
        if restore is not None:
            restore()
        if cleanup is not None:
            cleanup()
