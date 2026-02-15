import contextlib
import gc
import os
import time
from typing import Any, Optional

import pytest

from benchmarks.testing_other_di.test_shallow_all import (
    ShallowLeafA,
    ShallowLeafB,
    ShallowLeafC,
    ShallowRootAB,
    ShallowRootC,
    ShallowSpaceLeaf,
    ShallowSpaceRoot,
)


def _env_int(name: str, default: int) -> int:
    """
    Resolve an integer environment variable with a fallback default.

    Contract:
        - Empty/unset values resolve to `default`.
        - Non-integer values raise `ValueError`.
    """
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


def _env_int_nonneg(name: str, default: int) -> int:
    """
    Resolve a non-negative integer environment variable.

    Contract:
        - Delegates parsing to `_env_int`.
        - Negative values are clamped to `0`.
    """
    value = _env_int(name, default)
    return value if value >= 0 else 0


def _env_bool(name: str, default: bool) -> bool:
    """
    Resolve a boolean environment variable with common truthy/falsy values.

    Contract:
        - Empty/unset values resolve to `default`.
        - Unknown string values resolve to `default`.
    """
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    value = raw.strip().lower()
    if value in ("1", "true", "yes", "y", "on"):
        return True
    if value in ("0", "false", "no", "n", "off"):
        return False
    return default


def _percentile_ns(samples_ns: list[int], percentile: float) -> float:
    """
    Compute a nearest-rank percentile for nanosecond samples.

    Contract:
        - `samples_ns` must not be empty.
        - `percentile` is clamped to `[0.0, 100.0]`.
        - Returns a value in nanoseconds as `float`.
    """
    if not samples_ns:
        raise AssertionError("samples_ns must not be empty")

    clamped = max(0.0, min(100.0, percentile))
    ordered = sorted(samples_ns)
    if len(ordered) == 1:
        return float(ordered[0])

    index = int(round((clamped / 100.0) * (len(ordered) - 1)))
    return float(ordered[index])


def _bind_shallow_components(spellbook: Any, existence: Any) -> None:
    """
    Bind shallow benchmark components into a spellbook using explicit class groups.

    Purpose:
        Build a dedicated JIT/AOT conjure benchmark setup that uses shallow
        component classes directly and does not rely on GraphFactory helpers.
    """
    root_classes = (
        ShallowLeafA,
        ShallowLeafB,
        ShallowRootAB,
        ShallowLeafC,
        ShallowRootC,
    )
    for cls in root_classes:
        spellbook.bind(spell=cls, existence=existence.many, permissions="create")

    spellbook.bind(
        spell=ShallowSpaceLeaf,
        existence=existence.unique_per_spell_space,
        permissions="create",
    )
    spellbook.bind(
        spell=ShallowSpaceRoot,
        existence=existence.unique_per_spell_space,
        permissions="create",
    )


def _conjure_once_ns(full_aot: bool, iteration: int) -> int:
    """
    Build a fresh Melder runtime and return conjure duration in nanoseconds.

    Contract:
        - Uses a fresh Aether singleton each call.
        - Measures only `spellbook.conjure(...)`.
        - Always attempts cleanup/reset for deterministic iterations.
    """
    pytest.importorskip("melder")
    from melder.aether.aether import Aether
    from melder.aether.conduit.conduit import Conduit
    from melder.spellbook.existence.existence import Existence
    from melder.spellbook.spellbook import Spellbook

    conduit: Optional[Any] = None
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    spellbook = Spellbook(aetheric_frame="jit-aot-shallow-conjure-bench")

    try:
        cfg = spellbook.get_configuration()
        cfg.set_property("phase_scheduler_workers_per_spellbook", 1)
        cfg.set_property("full_ahead_of_time_compilation", full_aot)
        _bind_shallow_components(spellbook, Existence)

        started_ns = time.perf_counter_ns()
        conduit = spellbook.conjure(name=f"jit-aot-shallow-conjure-bench-{iteration}")
        return time.perf_counter_ns() - started_ns
    finally:
        if conduit is not None:
            with contextlib.suppress(Exception):
                conduit.cleanup()
        Aether._reset_singleton_for_tests()
        aether2 = Aether()
        Spellbook._aether = aether2
        Conduit._aether = aether2
        gc.collect()


def _measure_conjure_samples_ns(full_aot: bool, measure_iters: int, warmup_iters: int) -> list[int]:
    """
    Collect conjure timing samples for one compilation mode.

    Contract:
        - Runs `warmup_iters` unrecorded iterations first.
        - Records exactly `measure_iters` samples.
    """
    if measure_iters <= 0:
        raise AssertionError("measure_iters must be > 0")
    if warmup_iters < 0:
        raise AssertionError("warmup_iters must be >= 0")

    total_iters = warmup_iters + measure_iters
    samples_ns: list[int] = []
    for idx in range(total_iters):
        elapsed_ns = _conjure_once_ns(full_aot=full_aot, iteration=idx)
        if idx >= warmup_iters:
            samples_ns.append(elapsed_ns)
    return samples_ns


def test_melder_jit_aot_shallow_component_conjure_timings() -> None:
    """
    Gauge Melder shallow-component conjure performance for JIT vs full AOT.

    Purpose:
        Provide a dedicated JIT/AOT benchmark test that uses shallow component
        classes directly and reports timing deltas in a reproducible format.

    Environment knobs:
        - `DI_RUN_MELDER_JIT_AOT_CONJURE` (default: true)
        - `DI_MELDER_JIT_AOT_CONJURE_MEASURE_ITERS` (default: 12)
        - `DI_MELDER_JIT_AOT_CONJURE_WARMUP_ITERS` (default: 3)
    """
    if not _env_bool("DI_RUN_MELDER_JIT_AOT_CONJURE", True):
        pytest.skip("DI_RUN_MELDER_JIT_AOT_CONJURE disabled")

    measure_iters = _env_int_nonneg("DI_MELDER_JIT_AOT_CONJURE_MEASURE_ITERS", 12)
    warmup_iters = _env_int_nonneg("DI_MELDER_JIT_AOT_CONJURE_WARMUP_ITERS", 3)
    if measure_iters <= 0:
        raise AssertionError("DI_MELDER_JIT_AOT_CONJURE_MEASURE_ITERS must be > 0")

    jit_samples_ns = _measure_conjure_samples_ns(
        full_aot=False,
        measure_iters=measure_iters,
        warmup_iters=warmup_iters,
    )
    aot_samples_ns = _measure_conjure_samples_ns(
        full_aot=True,
        measure_iters=measure_iters,
        warmup_iters=warmup_iters,
    )

    assert len(jit_samples_ns) == measure_iters
    assert len(aot_samples_ns) == measure_iters
    assert all(value > 0 for value in jit_samples_ns)
    assert all(value > 0 for value in aot_samples_ns)

    jit_avg_ns = sum(jit_samples_ns) / float(len(jit_samples_ns))
    aot_avg_ns = sum(aot_samples_ns) / float(len(aot_samples_ns))
    ratio = aot_avg_ns / jit_avg_ns if jit_avg_ns > 0 else float("inf")

    print(
        "[melder] jit-vs-aot shallow-components conjure "
        f"JIT avg={jit_avg_ns/1_000_000.0:.3f}ms "
        f"p50={_percentile_ns(jit_samples_ns, 50.0)/1_000_000.0:.3f}ms "
        f"p95={_percentile_ns(jit_samples_ns, 95.0)/1_000_000.0:.3f}ms | "
        f"AOT avg={aot_avg_ns/1_000_000.0:.3f}ms "
        f"p50={_percentile_ns(aot_samples_ns, 50.0)/1_000_000.0:.3f}ms "
        f"p95={_percentile_ns(aot_samples_ns, 95.0)/1_000_000.0:.3f}ms | "
        f"AOT/JIT avg_ratio={ratio:.3f}x "
        f"(iters={measure_iters}, warmup={warmup_iters})"
    )
