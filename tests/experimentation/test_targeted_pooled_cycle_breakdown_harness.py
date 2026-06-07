"""
Instrumented pooled-cycle breakdown harness for lesser conduits and spellspaces.

Purpose:
    Decompose the steady-state pooled lifecycle cost into internal sub-steps
    without changing production runtime code.

This is an experimentation surface, not production runtime code.
"""

import sys
import time
from contextlib import ExitStack, contextmanager
from typing import Any, Callable, Dict, Iterator, List, Sequence


def _ensure_src_on_path() -> None:
    """
    Ensure the local `src/` tree is importable for direct experiment execution.
    """
    if "src" not in sys.path:
        sys.path.insert(0, "src")
    if "." not in sys.path:
        sys.path.insert(0, ".")


_ensure_src_on_path()

from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_pool import ConduitPool
from melder.aether.conduit.conduit_ward.conduit_ward import ConduitWard
from melder.aether.conduit.creations.creations import Creations
from melder.aether.conduit.spell_space.spell_space import SpellSpace
from melder.aether.conduit.spell_space.spell_space_pool import SpellSpacePool
from melder.aether.conduit.spell_space.spell_space_thread_state import (
    SpellSpaceThreadState,
)
from melder.utilities.general_base.abstract_elastic_pool import AbstractElasticPool
from tests.experimentation.test_targeted_lesser_spellspace_meld_cycle_harness import (
    _build_runtime,
    _cleanup_runtime,
    _iterations,
    _prime_lesser_pool,
    _prime_spellspace_pool,
    _warmup_iterations,
)


@contextmanager
def _patch_method(
    cls: type,
    method_name: str,
    replacement_factory: Callable[[Callable[..., Any]], Callable[..., Any]],
) -> Iterator[None]:
    """
    Temporarily replace one class method for instrumented timing.
    """
    original = getattr(cls, method_name)
    setattr(cls, method_name, replacement_factory(original))
    try:
        yield
    finally:
        setattr(cls, method_name, original)


def _timed_call(
    totals: Dict[str, int],
    key: str,
    action: Callable[[], Any],
) -> Any:
    """
    Execute one action and accumulate its elapsed time in nanoseconds.
    """
    start_ns = time.perf_counter_ns()
    try:
        return action()
    finally:
        totals[key] += time.perf_counter_ns() - start_ns


def _format_breakdown_table(rows: Sequence[Dict[str, str]]) -> str:
    """
    Format one compact terminal table for pooled breakdown output.
    """
    headers = ("surface", "metric", "avg_ns", "note")
    widths: Dict[str, int] = {}
    for header in headers:
        widths[header] = len(header)
    for row in rows:
        for header in headers:
            widths[header] = max(widths[header], len(row[header]))

    def line(values: Dict[str, str]) -> str:
        return "| " + " | ".join(
            values[header].ljust(widths[header]) for header in headers
        ) + " |"

    separator = {}
    for header in headers:
        separator[header] = "-" * widths[header]
    lines = [line(dict((header, header) for header in headers)), line(separator)]
    for row in rows:
        lines.append(line(row))
    return "\n".join(lines)


def _build_rows(surface: str, metrics: Dict[str, float], notes: Dict[str, str]) -> List[Dict[str, str]]:
    """
    Convert one metric dictionary into printable table rows.
    """
    rows: List[Dict[str, str]] = []
    for key, value in metrics.items():
        rows.append(
            {
                "surface": surface,
                "metric": key,
                "avg_ns": f"{value:.3f}",
                "note": notes.get(key, ""),
            }
        )
    return rows


def _measure_pooled_lesser_breakdown(
    root_conduit: Conduit,
    *,
    iterations: int,
    warmup: int,
) -> Dict[str, float]:
    """
    Measure steady-state pooled lesser acquire/cleanup breakdown.
    """
    _prime_lesser_pool(root_conduit)
    root_id = root_conduit._id
    target_pool = root_conduit._conduit_pool
    target_ward = root_conduit._conduit_ward

    totals = {
        "acquire_total_ns": 0,
        "cleanup_total_ns": 0,
        "cycle_total_ns": 0,
        "pool_create_ns": 0,
        "ward_link_ns": 0,
        "prepare_for_pool_ns": 0,
        "cleanup_spellspaces_for_pool_ns": 0,
        "lesser_creations_reset_ns": 0,
        "ward_detach_ns": 0,
        "pool_return_ns": 0,
    }

    def is_target_lesser(conduit: Conduit) -> bool:
        return (
            conduit is not root_conduit
            and getattr(conduit, "_root_conduit_id", None) == root_id
        )

    def is_target_lesser_creations(creations: Creations) -> bool:
        owner_id = creations.owner_conduit_id
        scope_id = creations.id
        return owner_id != root_id and scope_id == owner_id

    def make_pool_create_wrapper(original: Callable[..., Any]) -> Callable[..., Any]:
        def wrapped(self: ConduitPool, *args: Any, **kwargs: Any) -> Any:
            if self is target_pool:
                return _timed_call(
                    totals,
                    "pool_create_ns",
                    lambda: original(self, *args, **kwargs),
                )
            return original(self, *args, **kwargs)

        return wrapped

    def make_link_wrapper(original: Callable[..., Any]) -> Callable[..., Any]:
        def wrapped(self: ConduitWard, lesser_conduit: Conduit) -> Any:
            if self is target_ward:
                return _timed_call(
                    totals,
                    "ward_link_ns",
                    lambda: original(self, lesser_conduit),
                )
            return original(self, lesser_conduit)

        return wrapped

    def make_prepare_wrapper(original: Callable[..., Any]) -> Callable[..., Any]:
        def wrapped(self: Conduit) -> Any:
            if is_target_lesser(self):
                return _timed_call(
                    totals,
                    "prepare_for_pool_ns",
                    lambda: original(self),
                )
            return original(self)

        return wrapped

    def make_cleanup_spellspaces_wrapper(original: Callable[..., Any]) -> Callable[..., Any]:
        def wrapped(self: Conduit) -> Any:
            if is_target_lesser(self):
                return _timed_call(
                    totals,
                    "cleanup_spellspaces_for_pool_ns",
                    lambda: original(self),
                )
            return original(self)

        return wrapped

    def make_creations_reset_wrapper(original: Callable[..., Any]) -> Callable[..., Any]:
        def wrapped(self: Creations) -> Any:
            if is_target_lesser_creations(self):
                return _timed_call(
                    totals,
                    "lesser_creations_reset_ns",
                    lambda: original(self),
                )
            return original(self)

        return wrapped

    def make_detach_wrapper(original: Callable[..., Any]) -> Callable[..., Any]:
        def wrapped(self: ConduitWard) -> Any:
            conduit = getattr(self, "_conduit", None)
            root_conduit_local = getattr(self, "_root_conduit", None)
            if conduit is not None and conduit is not root_conduit and root_conduit_local is root_conduit:
                return _timed_call(
                    totals,
                    "ward_detach_ns",
                    lambda: original(self),
                )
            return original(self)

        return wrapped

    def make_pool_return_wrapper(original: Callable[..., Any]) -> Callable[..., Any]:
        def wrapped(self: ConduitPool, conduit: Conduit) -> Any:
            if self is target_pool:
                return _timed_call(
                    totals,
                    "pool_return_ns",
                    lambda: original(self, conduit),
                )
            return original(self, conduit)

        return wrapped

    with ExitStack() as stack:
        stack.enter_context(_patch_method(ConduitPool, "create_object", make_pool_create_wrapper))
        stack.enter_context(_patch_method(ConduitWard, "_link_lesser_conduit", make_link_wrapper))
        stack.enter_context(_patch_method(Conduit, "_prepare_for_pool", make_prepare_wrapper))
        stack.enter_context(
            _patch_method(
                Conduit,
                "_cleanup_spellspaces_for_pool",
                make_cleanup_spellspaces_wrapper,
            )
        )
        stack.enter_context(_patch_method(Creations, "reset_for_pool", make_creations_reset_wrapper))
        stack.enter_context(_patch_method(ConduitWard, "_detach_for_pool", make_detach_wrapper))
        stack.enter_context(_patch_method(ConduitPool, "return_lesser_conduit", make_pool_return_wrapper))

        for _ in range(warmup):
            lesser = root_conduit.create_lesser_conduit()
            lesser.cleanup()

        for _ in range(iterations):
            cycle_t0 = time.perf_counter_ns()
            lesser = root_conduit.create_lesser_conduit()
            acquire_t1 = time.perf_counter_ns()
            lesser.cleanup()
            cleanup_t2 = time.perf_counter_ns()
            totals["acquire_total_ns"] += acquire_t1 - cycle_t0
            totals["cleanup_total_ns"] += cleanup_t2 - acquire_t1
            totals["cycle_total_ns"] += cleanup_t2 - cycle_t0

    acquire_residual = (
        totals["acquire_total_ns"]
        - totals["pool_create_ns"]
        - totals["ward_link_ns"]
    )
    cleanup_residual = (
        totals["cleanup_total_ns"]
        - totals["prepare_for_pool_ns"]
    )
    prepare_residual = (
        totals["prepare_for_pool_ns"]
        - totals["cleanup_spellspaces_for_pool_ns"]
        - totals["lesser_creations_reset_ns"]
        - totals["ward_detach_ns"]
        - totals["pool_return_ns"]
    )
    totals["acquire_residual_ns"] = max(0, acquire_residual)
    totals["cleanup_residual_ns"] = max(0, cleanup_residual)
    totals["prepare_residual_ns"] = max(0, prepare_residual)

    result: Dict[str, float] = {}
    for key, value in totals.items():
        result[key] = value / float(iterations)
    return result


def _measure_pooled_spellspace_breakdown(
    lesser: Conduit,
    *,
    iterations: int,
    warmup: int,
) -> Dict[str, float]:
    """
    Measure steady-state pooled spellspace enter/exit breakdown.
    """
    _prime_spellspace_pool(lesser)
    target_pool = lesser._spellspace_pool
    target_thread_state = lesser._spellspace_stack
    lesser_id = lesser._id

    totals = {
        "enter_total_ns": 0,
        "exit_total_ns": 0,
        "cycle_total_ns": 0,
        "pool_acquire_ns": 0,
        "pool_prepare_ns": 0,
        "stack_get_ns": 0,
        "stack_set_ns": 0,
        "spellspace_cleanup_total_ns": 0,
        "cleanup_for_pool_reuse_ns": 0,
        "spellspace_creations_reset_ns": 0,
        "pool_release_ns": 0,
    }

    def is_target_spellspace(space: SpellSpace) -> bool:
        return getattr(space, "owner_conduit_id", None) == lesser_id

    def is_target_spellspace_creations(creations: Creations) -> bool:
        return (
            creations.owner_conduit_id == lesser_id
            and creations.id != creations.owner_conduit_id
        )

    def make_pool_acquire_wrapper(original: Callable[..., Any]) -> Callable[..., Any]:
        def wrapped(self: AbstractElasticPool[Any], *args: Any, **kwargs: Any) -> Any:
            if self is target_pool:
                return _timed_call(
                    totals,
                    "pool_acquire_ns",
                    lambda: original(self, *args, **kwargs),
                )
            return original(self, *args, **kwargs)

        return wrapped

    def make_pool_prepare_wrapper(original: Callable[..., Any]) -> Callable[..., Any]:
        def wrapped(self: SpellSpacePool, obj: SpellSpace, *args: Any, **kwargs: Any) -> Any:
            if self is target_pool:
                return _timed_call(
                    totals,
                    "pool_prepare_ns",
                    lambda: original(self, obj, *args, **kwargs),
                )
            return original(self, obj, *args, **kwargs)

        return wrapped

    def make_stack_get_wrapper(original: Callable[..., Any]) -> Callable[..., Any]:
        def wrapped(self: SpellSpaceThreadState) -> Any:
            if self is target_thread_state:
                return _timed_call(
                    totals,
                    "stack_get_ns",
                    lambda: original(self),
                )
            return original(self)

        return wrapped

    def make_stack_set_wrapper(original: Callable[..., Any]) -> Callable[..., Any]:
        def wrapped(self: SpellSpaceThreadState, stack: List[Any]) -> Any:
            if self is target_thread_state:
                return _timed_call(
                    totals,
                    "stack_set_ns",
                    lambda: original(self, stack),
                )
            return original(self, stack)

        return wrapped

    def make_cleanup_wrapper(original: Callable[..., Any]) -> Callable[..., Any]:
        def wrapped(self: SpellSpace) -> Any:
            if is_target_spellspace(self):
                return _timed_call(
                    totals,
                    "spellspace_cleanup_total_ns",
                    lambda: original(self),
                )
            return original(self)

        return wrapped

    def make_cleanup_for_pool_reuse_wrapper(original: Callable[..., Any]) -> Callable[..., Any]:
        def wrapped(self: SpellSpace) -> Any:
            if is_target_spellspace(self):
                return _timed_call(
                    totals,
                    "cleanup_for_pool_reuse_ns",
                    lambda: original(self),
                )
            return original(self)

        return wrapped

    def make_creations_reset_wrapper(original: Callable[..., Any]) -> Callable[..., Any]:
        def wrapped(self: Creations) -> Any:
            if is_target_spellspace_creations(self):
                return _timed_call(
                    totals,
                    "spellspace_creations_reset_ns",
                    lambda: original(self),
                )
            return original(self)

        return wrapped

    def make_pool_release_wrapper(original: Callable[..., Any]) -> Callable[..., Any]:
        def wrapped(self: SpellSpacePool, obj: SpellSpace) -> Any:
            if self is target_pool:
                return _timed_call(
                    totals,
                    "pool_release_ns",
                    lambda: original(self, obj),
                )
            return original(self, obj)

        return wrapped

    with ExitStack() as stack:
        stack.enter_context(
            _patch_method(AbstractElasticPool, "acquire", make_pool_acquire_wrapper)
        )
        stack.enter_context(
            _patch_method(SpellSpacePool, "prepare_object", make_pool_prepare_wrapper)
        )
        stack.enter_context(
            _patch_method(SpellSpaceThreadState, "get", make_stack_get_wrapper)
        )
        stack.enter_context(
            _patch_method(SpellSpaceThreadState, "set", make_stack_set_wrapper)
        )
        stack.enter_context(_patch_method(SpellSpace, "cleanup", make_cleanup_wrapper))
        stack.enter_context(
            _patch_method(
                SpellSpace,
                "_cleanup_for_pool_reuse",
                make_cleanup_for_pool_reuse_wrapper,
            )
        )
        stack.enter_context(
            _patch_method(Creations, "reset_for_pool", make_creations_reset_wrapper)
        )
        stack.enter_context(
            _patch_method(SpellSpacePool, "release", make_pool_release_wrapper)
        )

        for _ in range(warmup):
            context_manager = lesser.enter_spellspace()
            context_manager.__enter__()
            context_manager.__exit__(None, None, None)

        for _ in range(iterations):
            cycle_t0 = time.perf_counter_ns()
            context_manager = lesser.enter_spellspace()
            context_manager.__enter__()
            enter_t1 = time.perf_counter_ns()
            context_manager.__exit__(None, None, None)
            exit_t2 = time.perf_counter_ns()
            totals["enter_total_ns"] += enter_t1 - cycle_t0
            totals["exit_total_ns"] += exit_t2 - enter_t1
            totals["cycle_total_ns"] += exit_t2 - cycle_t0

    enter_residual = (
        totals["enter_total_ns"]
        - totals["pool_acquire_ns"]
        - totals["stack_get_ns"]
        - totals["stack_set_ns"]
    )
    exit_residual = (
        totals["exit_total_ns"]
        - totals["spellspace_cleanup_total_ns"]
        - totals["stack_get_ns"]
        - totals["stack_set_ns"]
    )
    cleanup_residual = (
        totals["spellspace_cleanup_total_ns"]
        - totals["cleanup_for_pool_reuse_ns"]
        - totals["pool_release_ns"]
    )
    cleanup_for_pool_reuse_residual = (
        totals["cleanup_for_pool_reuse_ns"]
        - totals["spellspace_creations_reset_ns"]
    )
    totals["enter_residual_ns"] = max(0, enter_residual)
    totals["exit_residual_ns"] = max(0, exit_residual)
    totals["cleanup_residual_ns"] = max(0, cleanup_residual)
    totals["cleanup_for_pool_reuse_residual_ns"] = max(
        0,
        cleanup_for_pool_reuse_residual,
    )

    result: Dict[str, float] = {}
    for key, value in totals.items():
        result[key] = value / float(iterations)
    return result


def _run_pooled_breakdown_harness() -> List[Dict[str, str]]:
    """
    Execute the instrumented pooled-lifecycle breakdown harness.
    """
    iterations = _iterations()
    warmup = _warmup_iterations()
    spellbook, root_conduit, _, _ = _build_runtime()
    rows: List[Dict[str, str]] = []
    try:
        lesser_metrics = _measure_pooled_lesser_breakdown(
            root_conduit,
            iterations=iterations,
            warmup=warmup,
        )
        rows.extend(
            _build_rows(
                "pooled_lesser",
                lesser_metrics,
                {
                    "acquire_total_ns": "full create_lesser_conduit steady-state call",
                    "cleanup_total_ns": "full lesser.cleanup steady-state call",
                    "cycle_total_ns": "outer steady-state pooled lesser cycle",
                    "pool_create_ns": "ConduitPool.create_object",
                    "ward_link_ns": "ConduitWard._link_lesser_conduit",
                    "prepare_for_pool_ns": "Conduit._prepare_for_pool",
                    "cleanup_spellspaces_for_pool_ns": "Conduit._cleanup_spellspaces_for_pool",
                    "lesser_creations_reset_ns": "Creations.reset_for_pool on lesser",
                    "ward_detach_ns": "ConduitWard._detach_for_pool",
                    "pool_return_ns": "ConduitPool.return_lesser_conduit",
                    "acquire_residual_ns": "root/lock/state bookkeeping outside timed subcalls",
                    "cleanup_residual_ns": "Conduit.cleanup wrapper cost outside prepare_for_pool",
                    "prepare_residual_ns": "state flips / hook clearing inside prepare_for_pool",
                },
            )
        )

        persistent_lesser = root_conduit.create_lesser_conduit()
        try:
            spellspace_metrics = _measure_pooled_spellspace_breakdown(
                persistent_lesser,
                iterations=iterations,
                warmup=warmup,
            )
            rows.extend(
                _build_rows(
                    "pooled_spellspace",
                    spellspace_metrics,
                    {
                        "enter_total_ns": "full enter_spellspace steady-state enter",
                        "exit_total_ns": "full spellspace context exit",
                        "cycle_total_ns": "outer steady-state pooled spellspace cycle",
                        "pool_acquire_ns": "AbstractElasticPool.acquire on SpellSpacePool",
                        "pool_prepare_ns": "SpellSpacePool.prepare_object",
                        "stack_get_ns": "SpellSpaceThreadState.get",
                        "stack_set_ns": "SpellSpaceThreadState.set",
                        "spellspace_cleanup_total_ns": "SpellSpace.cleanup",
                        "cleanup_for_pool_reuse_ns": "SpellSpace._cleanup_for_pool_reuse",
                        "spellspace_creations_reset_ns": "Creations.reset_for_pool on spellspace",
                        "pool_release_ns": "SpellSpacePool.release",
                        "enter_residual_ns": "context-manager wrapper cost outside acquire/get/set",
                        "exit_residual_ns": "context-manager wrapper cost outside cleanup/get/set",
                        "cleanup_residual_ns": "SpellSpace.cleanup wrapper cost outside pool-reuse/release",
                        "cleanup_for_pool_reuse_residual_ns": "registry discard and local flag work",
                    },
                )
            )
        finally:
            persistent_lesser.cleanup()
    finally:
        _cleanup_runtime(spellbook, root_conduit)

    print("TARGETED_POOLED_BREAKDOWN_HARNESS")
    print(_format_breakdown_table(rows))
    return rows


def test_targeted_pooled_cycle_breakdown_harness() -> None:
    """
    Run the pooled-lifecycle breakdown harness and assert it produced usable rows.
    """
    rows = _run_pooled_breakdown_harness()
    by_key: Dict[tuple[str, str], Dict[str, str]] = {}
    for row in rows:
        by_key[(row["surface"], row["metric"])] = row

    expected_keys = (
        ("pooled_lesser", "acquire_total_ns"),
        ("pooled_lesser", "cleanup_total_ns"),
        ("pooled_lesser", "pool_create_ns"),
        ("pooled_lesser", "ward_link_ns"),
        ("pooled_lesser", "prepare_for_pool_ns"),
        ("pooled_lesser", "ward_detach_ns"),
        ("pooled_spellspace", "enter_total_ns"),
        ("pooled_spellspace", "exit_total_ns"),
        ("pooled_spellspace", "pool_acquire_ns"),
        ("pooled_spellspace", "spellspace_cleanup_total_ns"),
        ("pooled_spellspace", "spellspace_creations_reset_ns"),
        ("pooled_spellspace", "pool_release_ns"),
    )
    for key in expected_keys:
        if key not in by_key:
            raise AssertionError(f"Missing pooled breakdown metric: {key!r}")
        if float(by_key[key]["avg_ns"]) < 0.0:
            raise AssertionError(f"Pooled breakdown metric must be non-negative: {key!r}")
