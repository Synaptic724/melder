from __future__ import annotations

import gc
import os
import random
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pytest

import benchmarks.testing_other_di.test_shallow_all as shallow_all


def _ensure_src_on_path() -> None:
    """
    Ensure the local src/ tree is importable when the benchmark is run directly.
    """
    project_root = Path(__file__).resolve().parents[2]
    src_path = project_root / "src"
    if not src_path.exists():
        return
    src_as_str = str(src_path)
    if src_as_str not in sys.path:
        sys.path.insert(0, src_as_str)


_ensure_src_on_path()


def _env_csv_ints(name: str, default: str) -> tuple[int, ...]:
    raw = os.getenv(name)
    value = default if raw is None or raw.strip() == "" else raw
    out: list[int] = []
    for part in value.split(","):
        s = part.strip()
        if not s:
            continue
        out.append(int(s))
    if not out:
        raise AssertionError(f"{name} must contain at least one integer")
    return tuple(out)


def _env_str(name: str, default: str) -> str:
    raw = os.getenv(name)
    if raw is None:
        return default
    s = raw.strip()
    return s if s else default


@dataclass(frozen=True)
class _ScalingConfig:
    """
    Controls for the threaded graph-mix benchmark.

    Defaults are intentionally sized for a small VM and a no-GIL scaling check.
    """

    duration_s: float
    spellspace_every: int
    gc_every: int
    gc_mode: str
    warmup_iters: int
    random_seed: int
    validate_transient_every: int
    validate_within_every: int
    root_pattern: str
    burst_len: int
    ratio_p: float
    graph_pattern: str
    thread_counts: tuple[int, ...]

    @staticmethod
    def from_env() -> _ScalingConfig:
        cfg = _ScalingConfig(
            duration_s=shallow_all._env_float("DI_DURATION_S", 15.0),
            spellspace_every=shallow_all._env_int("DI_SPELLSPACE_EVERY", 20),
            gc_every=shallow_all._env_int("DI_GC_EVERY", 2000),
            gc_mode=_env_str("DI_GC_MODE", "periodic").lower(),
            warmup_iters=shallow_all._env_int_nonneg("DI_WARMUP_ITERS", 50),
            random_seed=shallow_all._env_int("DI_RANDOM_SEED", 1337),
            validate_transient_every=shallow_all._env_int("DI_VALIDATE_TRANSIENT_EVERY", 0),
            validate_within_every=shallow_all._env_int("DI_VALIDATE_WITHIN_EVERY", 0),
            root_pattern=_env_str("DI_PATTERN", "alternating").lower(),
            burst_len=shallow_all._env_int("DI_BURST_LEN", 64),
            ratio_p=shallow_all._env_float("DI_RATIO_P", 0.5),
            graph_pattern=_env_str("DI_GRAPH_PATTERN", "random").lower(),
            thread_counts=_env_csv_ints("DI_THREAD_COUNTS", "1,2,3,4,5"),
        )

        if cfg.duration_s <= 0:
            raise AssertionError("DI_DURATION_S must be > 0")
        if cfg.spellspace_every <= 0:
            raise AssertionError("DI_SPELLSPACE_EVERY must be > 0")
        if cfg.gc_every <= 0:
            raise AssertionError("DI_GC_EVERY must be > 0")
        if cfg.gc_mode not in ("periodic", "disabled", "none"):
            raise AssertionError("DI_GC_MODE must be: periodic|disabled|none")
        if cfg.root_pattern not in ("alternating", "burst", "ratio", "random"):
            raise AssertionError("DI_PATTERN must be: alternating|burst|ratio|random")
        if cfg.graph_pattern not in ("random", "round_robin"):
            raise AssertionError("DI_GRAPH_PATTERN must be: random|round_robin")
        if not (0.0 <= cfg.ratio_p <= 1.0):
            raise AssertionError("DI_RATIO_P must be between 0 and 1")
        if any(t <= 0 for t in cfg.thread_counts):
            raise AssertionError("DI_THREAD_COUNTS values must be > 0")
        if any(t > 5 for t in cfg.thread_counts):
            raise AssertionError("DI_THREAD_COUNTS values must be <= 5 for this benchmark")
        return cfg


@dataclass
class _ThreadStats:
    steps: int
    spellspaces: int
    errors: int
    g_steps: list[int]
    g_a: list[int]
    g_b: list[int]


@dataclass(frozen=True)
class _RunResult:
    thread_count: int
    elapsed_s: float
    steps: int
    steps_per_s: float
    spellspaces: int
    errors: int
    per_graph_steps: tuple[int, ...]
    per_graph_a: tuple[int, ...]
    per_graph_b: tuple[int, ...]


def _gil_status() -> str:
    flag = getattr(sys, "_is_gil_enabled", None)
    if flag is None:
        return "unknown"
    try:
        return "enabled" if flag() else "disabled"
    except Exception:
        return "unknown"


def _run_graph_mix(
        *,
        lib: str,
        graphs: list[shallow_all._GraphSpec],
        cfg: _ScalingConfig,
        thread_count: int,
) -> _RunResult:
    """
    Execute one threaded graph-mix run.

    Important:
        Unlike test_shallow_all, workers do not read stop_at before the main thread
        publishes it. This avoids the zero-duration race observed in the older harness.
    """

    ops = shallow_all._build_rotation_ops(lib, graphs)
    shallow_all._warmup_rotation_ops(ops, iters=cfg.warmup_iters)

    gcount = len(graphs)
    stats: list[_ThreadStats] = [
        _ThreadStats(
            steps=0,
            spellspaces=0,
            errors=0,
            g_steps=[0] * gcount,
            g_a=[0] * gcount,
            g_b=[0] * gcount,
        )
        for _ in range(thread_count)
    ]
    errors: list[BaseException] = []
    stop_event = threading.Event()
    ready_barrier = threading.Barrier(thread_count + 1)
    start_event = threading.Event()
    stop_time_holder: list[float] = [0.0]

    def worker(ix: int) -> None:
        try:
            was_enabled = gc.isenabled()
            if cfg.gc_mode == "disabled" and was_enabled:
                gc.disable()

            try:
                rng = random.Random(cfg.random_seed + ix)
                selector = shallow_all._WorkSelector(
                    pattern=cfg.root_pattern,
                    burst_len=cfg.burst_len,
                    ratio_p=cfg.ratio_p,
                    rng=rng if cfg.root_pattern in ("ratio", "random") else None,
                )

                ready_barrier.wait()
                start_event.wait()
                stop_at = stop_time_holder[0]

                local_i = 0
                local_stats = stats[ix]

                while not stop_event.is_set() and time.perf_counter() < stop_at:
                    if cfg.graph_pattern == "random":
                        gix = rng.randrange(gcount)
                    else:
                        gix = local_i % gcount
                    g = graphs[gix]
                    do_a = selector.choose_a(local_i)

                    if do_a:
                        root = ops.get_root_a(gix)
                        if not isinstance(root, g.root_a):
                            raise AssertionError("Thread scaling: resolved root_a wrong type")
                        local_stats.g_a[gix] += 1
                    else:
                        root = ops.get_root_b(gix)
                        if not isinstance(root, g.root_b):
                            raise AssertionError("Thread scaling: resolved root_b wrong type")
                        local_stats.g_b[gix] += 1

                    local_stats.steps += 1
                    local_stats.g_steps[gix] += 1
                    local_i += 1

                    if (local_i % cfg.spellspace_every) == 0:
                        ops.spellspace_cycle(gix)
                        local_stats.spellspaces += 1

                    if cfg.validate_transient_every > 0 and g.transient_probe is not None:
                        if (local_i % cfg.validate_transient_every) == 0:
                            r1 = ops.get_root_a(gix)
                            r2 = ops.get_root_a(gix)
                            o11, o12 = g.transient_probe(r1)
                            o21, o22 = g.transient_probe(r2)
                            if o11 is o21 or o12 is o22:
                                raise AssertionError(
                                    "Thread scaling transient probe failed: cached transient subtree detected"
                                )

                    if cfg.validate_within_every > 0 and g.within_resolve_probe is not None:
                        if (local_i % cfg.validate_within_every) == 0:
                            r = ops.get_root_a(gix)
                            x, y = g.within_resolve_probe(r)
                            if g.within_resolve_expect_distinct and (x is y):
                                raise AssertionError(
                                    "Thread scaling within-resolve probe failed: transient dedupe detected"
                                )

                    if cfg.gc_mode == "periodic":
                        if (local_i % cfg.gc_every) == 0:
                            gc.collect()
            finally:
                if cfg.gc_mode == "disabled" and was_enabled:
                    gc.activate()
        except BaseException as exc:
            stats[ix].errors += 1
            errors.append(exc)
            stop_event.set()

    threads_list: list[threading.Thread] = []
    for i in range(thread_count):
        t = threading.Thread(target=worker, args=(i,), daemon=True)
        threads_list.append(t)
        t.start()

    ready_barrier.wait()
    start_t = time.perf_counter()
    stop_time_holder[0] = start_t + cfg.duration_s
    start_event.set()

    for t in threads_list:
        t.join()

    elapsed_s = time.perf_counter() - start_t

    try:
        if errors:
            raise errors[0]

        total_steps = sum(s.steps for s in stats)
        total_spaces = sum(s.spellspaces for s in stats)
        total_err = sum(s.errors for s in stats)
        per_graph_steps = [0] * gcount
        per_graph_a = [0] * gcount
        per_graph_b = [0] * gcount

        for s in stats:
            for i in range(gcount):
                per_graph_steps[i] += s.g_steps[i]
                per_graph_a[i] += s.g_a[i]
                per_graph_b[i] += s.g_b[i]

        steps_per_s = total_steps / elapsed_s if elapsed_s > 0 else 0.0
        return _RunResult(
            thread_count=thread_count,
            elapsed_s=elapsed_s,
            steps=total_steps,
            steps_per_s=steps_per_s,
            spellspaces=total_spaces,
            errors=total_err,
            per_graph_steps=tuple(per_graph_steps),
            per_graph_a=tuple(per_graph_a),
            per_graph_b=tuple(per_graph_b),
        )
    finally:
        ops.cleanup()


def _format_per_graph_summary(
        graphs: list[shallow_all._GraphSpec],
        result: _RunResult,
) -> str:
    parts: list[str] = []
    for i, graph in enumerate(graphs):
        parts.append(
            f"{graph.name}:{result.per_graph_steps[i]}"
            f"(A={result.per_graph_a[i]},B={result.per_graph_b[i]})"
        )
    return ", ".join(parts)


@pytest.mark.timeout(900)
@pytest.mark.parametrize("lib", shallow_all._selected_libs())
def test_threaded_shallow_all_graph_mix_scaling(lib: str) -> None:
    """
    Multi-threaded graph-mix scaling benchmark for the shallow_all graph set.

    Design:
        - Uses the same library runtime builders as test_shallow_all.
        - Runs 15 seconds per thread-count by default.
        - Scales from 1 to 5 threads by default.
        - Uses randomized graph selection by default so per-graph counts are not
          forced equal by construction.
        - Uses a start_event after publishing stop_at to avoid the zero-work race
          present in the older shallow_all threaded loops.
    """

    graphs = shallow_all._selected_graphs()
    cfg = _ScalingConfig.from_env()
    baseline_steps_per_s: Optional[float] = None

    print(
        f"[{lib}] graph-mix scaling config: "
        f"gil={_gil_status()}, "
        f"duration={cfg.duration_s:.2f}s, "
        f"threads={cfg.thread_counts}, "
        f"graph_pattern={cfg.graph_pattern}, "
        f"root_pattern={cfg.root_pattern}, "
        f"graphs={tuple(g.name for g in graphs)}"
    )

    for thread_count in cfg.thread_counts:
        result = _run_graph_mix(
            lib=lib,
            graphs=graphs,
            cfg=cfg,
            thread_count=thread_count,
        )
        if result.steps <= 0:
            raise AssertionError("Thread scaling benchmark produced zero work")
        if baseline_steps_per_s is None:
            baseline_steps_per_s = result.steps_per_s
        speedup = result.steps_per_s / baseline_steps_per_s if baseline_steps_per_s > 0 else 0.0
        efficiency = speedup / float(thread_count) if thread_count > 0 else 0.0
        per_graph_summary = _format_per_graph_summary(graphs, result)

        print(
            f"[{lib}] graph-mix scaling: "
            f"threads={thread_count}, duration={result.elapsed_s:.2f}s, "
            f"steps={result.steps}, steps/s={result.steps_per_s:,.0f}, "
            f"speedup_vs_1t={speedup:.2f}x, efficiency={efficiency:.1%}, "
            f"spellspaces={result.spellspaces}, errors={result.errors}, "
            f"per_graph=({per_graph_summary})"
        )
