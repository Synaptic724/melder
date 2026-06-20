from __future__ import annotations

"""
Persistent runtime gauntlet for DI/IoC containers and Melder.

Place this file next to `test_real_world_gauntlet.py` in:

    benchmarks/testing_other_di/test_persistent_runtime_gauntlet.py

Why this exists:
    The existing gauntlet creates worker threads every iteration. That is a useful
    scope-churn torture test, but it does not model a FastAPI-style process or a
    CommandOps-style long-running runtime. This file builds each container once,
    starts persistent worker threads once, warms the runtime, and then measures
    steady-state work for a fixed duration.

Default runtime:
    300 seconds per (library, scenario), 10 persistent worker threads.

Scenarios:
    fastapi_steady
        Saturated 10-thread request handling. Each worker repeatedly executes the
        request-scope workload. This models a no-GIL FastAPI-like service using
        threads instead of processes.

    bursty_app
        Long-running worker app with synchronized active/idle bursts. Active
        windows execute a weighted mix of request, worker_a, and worker_b jobs;
        idle windows sleep. This models a normal app with bursts of traffic/work.

Useful env vars:
    PERSISTENT_GAUNTLET_SECONDS=300
    PERSISTENT_GAUNTLET_WARMUP_SECONDS=10
    PERSISTENT_GAUNTLET_THREADS=10
    PERSISTENT_GAUNTLET_LIBS=dependency-injector,dishka,melder
    PERSISTENT_GAUNTLET_SCENARIOS=fastapi_steady,bursty_app
    PERSISTENT_GAUNTLET_SAMPLE_EVERY=1000
    PERSISTENT_GAUNTLET_BUCKET_SECONDS=0
    PERSISTENT_APP_WORK_NS=0
    PERSISTENT_BURST_ACTIVE_MS=2000
    PERSISTENT_BURST_IDLE_MS=1000
    PERSISTENT_BURST_REQUEST_WEIGHT=60
    PERSISTENT_BURST_WORKER_A_WEIGHT=25
    PERSISTENT_BURST_WORKER_B_WEIGHT=15

Degradation mode:
    Setting PERSISTENT_GAUNTLET_BUCKET_SECONDS > 0 turns on time-bucketed
    reporting: per-bucket cycles/s, sampled p50/p95/p99/max, GC collection
    counts, and GC pause totals (gc.callbacks based), plus a first-vs-last
    bucket drift summary. This is the long-horizon instrument: GC-dependent
    containers drift as heap pressure accumulates while deterministic
    cleanup stays flat. The 300s summary alone averages that story away.

    Recommended 20-minute degradation run:
        PERSISTENT_GAUNTLET_SECONDS=1200 \
        PERSISTENT_GAUNTLET_BUCKET_SECONDS=60 \
        pytest benchmarks/testing_other_di/test_persistent_runtime_gauntlet.py -s

    Default output is unchanged when the bucket env is unset/0.
"""

import gc
import os
import random
import statistics
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import pytest


def _ensure_local_paths() -> None:
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parents[1]
    src_dir = project_root / "src"
    for path in (src_dir, current_dir):
        path_s = str(path)
        if path_s not in sys.path:
            sys.path.insert(0, path_s)


_ensure_local_paths()

# Reuse the existing all-libs benchmark wiring and workload graph.
# This file should live beside test_real_world_gauntlet.py.
import test_real_world_gauntlet as base


_ONE_BILLION = 1_000_000_000
_VARIANT_COUNT = getattr(base, "_VARIANT_COUNT", 3)


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return float(raw)


def _env_list(name: str, default: tuple[str, ...]) -> tuple[str, ...]:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    values = tuple(part.strip() for part in raw.split(",") if part.strip())
    return values or default


def _gil_status() -> str:
    flag = getattr(sys, "_is_gil_enabled", None)
    if flag is None:
        return "unknown"
    try:
        return "enabled" if flag() else "disabled"
    except Exception:
        return "unknown"


def _ms(ns: int | float) -> float:
    return float(ns) / 1_000_000.0


def _pctl(sorted_values: list[int], q: float) -> int:
    if not sorted_values:
        return 0
    ix = max(0, min(len(sorted_values) - 1, int((len(sorted_values) - 1) * q)))
    return sorted_values[ix]


@dataclass(frozen=True)
class PersistentConfig:
    scenario: str
    duration_s: float
    warmup_s: float
    threads: int
    sample_every: int
    app_work_ns: int
    burst_active_ms: int
    burst_idle_ms: int
    burst_request_weight: int
    burst_worker_a_weight: int
    burst_worker_b_weight: int
    bucket_s: float = 0.0

    @property
    def bucket_ns(self) -> int:
        """Bucket width in ns; 0 disables degradation bucketing."""
        return int(self.bucket_s * _ONE_BILLION) if self.bucket_s > 0 else 0

    @staticmethod
    def from_env(scenario: str) -> "PersistentConfig":
        cfg = PersistentConfig(
            scenario=scenario,
            duration_s=_env_float("PERSISTENT_GAUNTLET_SECONDS", 300.0),
            warmup_s=_env_float("PERSISTENT_GAUNTLET_WARMUP_SECONDS", 10.0),
            threads=_env_int("PERSISTENT_GAUNTLET_THREADS", 3),
            sample_every=max(1, _env_int("PERSISTENT_GAUNTLET_SAMPLE_EVERY", 1000)),
            app_work_ns=max(0, _env_int("PERSISTENT_APP_WORK_NS", 0)),
            burst_active_ms=max(1, _env_int("PERSISTENT_BURST_ACTIVE_MS", 2000)),
            burst_idle_ms=max(0, _env_int("PERSISTENT_BURST_IDLE_MS", 1000)),
            burst_request_weight=max(0, _env_int("PERSISTENT_BURST_REQUEST_WEIGHT", 60)),
            burst_worker_a_weight=max(0, _env_int("PERSISTENT_BURST_WORKER_A_WEIGHT", 25)),
            burst_worker_b_weight=max(0, _env_int("PERSISTENT_BURST_WORKER_B_WEIGHT", 15)),
            bucket_s=max(0.0, _env_float("PERSISTENT_GAUNTLET_BUCKET_SECONDS", 0.0)),
        )
        if cfg.duration_s <= 0:
            raise AssertionError("PERSISTENT_GAUNTLET_SECONDS must be > 0")
        if cfg.warmup_s < 0:
            raise AssertionError("PERSISTENT_GAUNTLET_WARMUP_SECONDS must be >= 0")
        if cfg.threads <= 0:
            raise AssertionError("PERSISTENT_GAUNTLET_THREADS must be > 0")
        if scenario not in {"fastapi_steady", "bursty_app"}:
            raise AssertionError(f"Unknown scenario: {scenario}")
        if scenario == "bursty_app":
            weight_sum = cfg.burst_request_weight + cfg.burst_worker_a_weight + cfg.burst_worker_b_weight
            if weight_sum <= 0:
                raise AssertionError("At least one burst lane weight must be > 0")
        return cfg


@dataclass
class SampledTimer:
    count: int = 0
    total_ns: int = 0
    min_ns: int = field(default_factory=lambda: 2**63 - 1)
    max_ns: int = 0
    samples: list[int] = field(default_factory=list)

    def add(self, ns: int, *, take_sample: bool) -> None:
        self.count += 1
        self.total_ns += ns
        if ns < self.min_ns:
            self.min_ns = ns
        if ns > self.max_ns:
            self.max_ns = ns
        if take_sample:
            self.samples.append(ns)

    def merge(self, other: "SampledTimer") -> None:
        self.count += other.count
        self.total_ns += other.total_ns
        self.min_ns = min(self.min_ns, other.min_ns)
        self.max_ns = max(self.max_ns, other.max_ns)
        self.samples.extend(other.samples)

    def avg_ns(self) -> float:
        return float(self.total_ns) / float(self.count) if self.count else 0.0

    def sampled_summary(self) -> str:
        if not self.samples:
            min_ns = 0 if self.min_ns == 2**63 - 1 else self.min_ns
            return (
                f"count={self.count:,}, avg={_ms(self.avg_ns()):.3f}ms, "
                f"min={_ms(min_ns):.3f}ms, max={_ms(self.max_ns):.3f}ms, samples=0"
            )
        ordered = sorted(self.samples)
        p50 = statistics.median(ordered)
        p95 = _pctl(ordered, 0.95)
        p99 = _pctl(ordered, 0.99)
        stdev = statistics.pstdev(ordered) if len(ordered) > 1 else 0.0
        min_ns = 0 if self.min_ns == 2**63 - 1 else self.min_ns
        return (
            f"count={self.count:,}, avg={_ms(self.avg_ns()):.3f}ms, "
            f"sample_median={_ms(p50):.3f}ms, sample_p95={_ms(p95):.3f}ms, "
            f"sample_p99={_ms(p99):.3f}ms, min={_ms(min_ns):.3f}ms, "
            f"max={_ms(self.max_ns):.3f}ms, sample_stdev={_ms(stdev):.3f}ms, samples={len(self.samples):,}"
        )


@dataclass
class BucketStats:
    """
    One degradation bucket: cycles, active time, and sampled latencies.
    """

    cycles: int = 0
    active_ns: int = 0
    samples: list[int] = field(default_factory=list)
    max_ns: int = 0

    def add(self, cycle_ns: int, *, take_sample: bool) -> None:
        self.cycles += 1
        self.active_ns += cycle_ns
        if cycle_ns > self.max_ns:
            self.max_ns = cycle_ns
        if take_sample:
            self.samples.append(cycle_ns)

    def merge(self, other: "BucketStats") -> None:
        self.cycles += other.cycles
        self.active_ns += other.active_ns
        self.max_ns = max(self.max_ns, other.max_ns)
        self.samples.extend(other.samples)


@dataclass
class GcBucketStats:
    """
    GC activity attributed to one degradation bucket.
    """

    collections_by_gen: dict[int, int] = field(default_factory=dict)
    collected_objects: int = 0
    pause_total_ns: int = 0
    pause_max_ns: int = 0

    def add(self, *, generation: int, collected: int, pause_ns: int) -> None:
        self.collections_by_gen[generation] = (
            self.collections_by_gen.get(generation, 0) + 1
        )
        self.collected_objects += collected
        self.pause_total_ns += pause_ns
        if pause_ns > self.pause_max_ns:
            self.pause_max_ns = pause_ns

    @property
    def collections(self) -> int:
        return sum(self.collections_by_gen.values())


class GcBucketMonitor:
    """
    gc.callbacks hook that aggregates collection pauses into time buckets.

    Contract:
        - Aggregates in-callback (counts/sums only) so a 20-minute run does
          not accumulate an unbounded event list and callback overhead stays
          trivial next to the collection pass it wraps.
        - Pauses are attributed to the bucket of their START timestamp;
          events outside [measure_start_ns, end_ns) are dropped (warmup,
          teardown).
        - Collections do not nest, but on the free-threaded build the
          callback fires on whichever thread triggered the collection, so
          start timestamps are tracked per-thread and totals merge under a
          lock on the stop phase.
    """

    def __init__(self, *, measure_start_ns: int, end_ns: int, bucket_ns: int) -> None:
        self._measure_start_ns = measure_start_ns
        self._end_ns = end_ns
        self._bucket_ns = bucket_ns
        self._lock = threading.Lock()
        self._start_by_thread: dict[int, int] = {}
        self.buckets: dict[int, GcBucketStats] = {}
        self.total = GcBucketStats()

    def _callback(self, phase: str, info: dict) -> None:
        thread_id = threading.get_ident()
        if phase == "start":
            self._start_by_thread[thread_id] = time.perf_counter_ns()
            return
        start_ns = self._start_by_thread.pop(thread_id, None)
        if start_ns is None:
            return
        pause_ns = time.perf_counter_ns() - start_ns
        if start_ns < self._measure_start_ns or start_ns >= self._end_ns:
            return
        generation = int(info.get("generation", -1))
        collected = int(info.get("collected", 0))
        bucket_ix = (
            (start_ns - self._measure_start_ns) // self._bucket_ns
            if self._bucket_ns > 0
            else 0
        )
        with self._lock:
            self.total.add(
                generation=generation, collected=collected, pause_ns=pause_ns,
            )
            bucket = self.buckets.get(bucket_ix)
            if bucket is None:
                bucket = GcBucketStats()
                self.buckets[bucket_ix] = bucket
            bucket.add(generation=generation, collected=collected, pause_ns=pause_ns)

    def install(self) -> None:
        gc.callbacks.append(self._callback)

    def uninstall(self) -> None:
        try:
            gc.callbacks.remove(self._callback)
        except ValueError:
            pass


@dataclass
class LaneStats:
    name: str
    cycles: int = 0
    objects_min: int = 0
    variant_counts: list[int] = field(default_factory=lambda: [0] * _VARIANT_COUNT)
    cycle_timer: SampledTimer = field(default_factory=SampledTimer)
    outer_create: SampledTimer = field(default_factory=SampledTimer)
    outer_cleanup: SampledTimer = field(default_factory=SampledTimer)
    outer_total: SampledTimer = field(default_factory=SampledTimer)
    request_create: SampledTimer = field(default_factory=SampledTimer)
    request_cleanup: SampledTimer = field(default_factory=SampledTimer)
    request_total: SampledTimer = field(default_factory=SampledTimer)

    def add_cycle(self, variant: int, cycle_ns: int, metrics: Any, *, take_sample: bool) -> None:
        self.cycles += 1
        self.objects_min += base._lane_objects_per_cycle(self.name)
        self.variant_counts[variant] += 1
        self.cycle_timer.add(cycle_ns, take_sample=take_sample)
        self.outer_create.add(metrics.outer_create_ns, take_sample=take_sample)
        self.outer_cleanup.add(metrics.outer_cleanup_ns, take_sample=take_sample)
        self.outer_total.add(metrics.outer_total_ns, take_sample=take_sample)
        self.request_create.add(metrics.request_create_ns, take_sample=take_sample)
        self.request_cleanup.add(metrics.request_cleanup_ns, take_sample=take_sample)
        self.request_total.add(metrics.request_total_ns, take_sample=take_sample)

    def merge(self, other: "LaneStats") -> None:
        self.cycles += other.cycles
        self.objects_min += other.objects_min
        for i, value in enumerate(other.variant_counts):
            self.variant_counts[i] += value
        self.cycle_timer.merge(other.cycle_timer)
        self.outer_create.merge(other.outer_create)
        self.outer_cleanup.merge(other.outer_cleanup)
        self.outer_total.merge(other.outer_total)
        self.request_create.merge(other.request_create)
        self.request_cleanup.merge(other.request_cleanup)
        self.request_total.merge(other.request_total)


@dataclass
class WorkerStats:
    active_ns: int = 0
    idle_ns: int = 0
    lanes: dict[str, LaneStats] = field(
        default_factory=lambda: {
            "request": LaneStats("request"),
            "worker_a": LaneStats("worker_a"),
            "worker_b": LaneStats("worker_b"),
        }
    )
    buckets: dict[int, BucketStats] = field(default_factory=dict)

    def add_to_bucket(self, bucket_ix: int, cycle_ns: int, *, take_sample: bool) -> None:
        bucket = self.buckets.get(bucket_ix)
        if bucket is None:
            bucket = BucketStats()
            self.buckets[bucket_ix] = bucket
        bucket.add(cycle_ns, take_sample=take_sample)

    def merge(self, other: "WorkerStats") -> None:
        self.active_ns += other.active_ns
        self.idle_ns += other.idle_ns
        for lane_name, lane_stats in other.lanes.items():
            self.lanes[lane_name].merge(lane_stats)
        for bucket_ix, bucket in other.buckets.items():
            mine = self.buckets.get(bucket_ix)
            if mine is None:
                self.buckets[bucket_ix] = bucket
            else:
                mine.merge(bucket)


@dataclass(frozen=True)
class PersistentResult:
    lib: str
    cfg: PersistentConfig
    gil_status: str
    setup_ns: int
    warmup_ns: int
    measured_ns: int
    cleanup_ns: int
    worker_stats: WorkerStats
    gc_buckets: dict[int, GcBucketStats] | None = None
    gc_total: GcBucketStats | None = None


def _burn_cpu_ns(target_ns: int) -> None:
    if target_ns <= 0:
        return
    start = time.perf_counter_ns()
    # Tiny deterministic busy loop. The exact result does not matter; it just
    # makes per-request work denser without sleeping or doing IO.
    x = 0x12345678
    while (time.perf_counter_ns() - start) < target_ns:
        x = ((x << 5) ^ (x >> 2) ^ 0x9E3779B9) & 0xFFFFFFFF
    if x == -1:  # unreachable; prevents overly aggressive dead-code assumptions
        raise AssertionError("unreachable")


def _choose_burst_lane(rng: random.Random, cfg: PersistentConfig) -> str:
    total = cfg.burst_request_weight + cfg.burst_worker_a_weight + cfg.burst_worker_b_weight
    roll = rng.randrange(total)
    if roll < cfg.burst_request_weight:
        return "request"
    roll -= cfg.burst_request_weight
    if roll < cfg.burst_worker_a_weight:
        return "worker_a"
    return "worker_b"


def _lane_call(ops: Any, lane_name: str) -> Callable[[int], Any]:
    if lane_name == "request":
        return ops.request_scope_cycle
    if lane_name == "worker_a":
        return ops.worker_a_scope_cycle
    if lane_name == "worker_b":
        return ops.worker_b_scope_cycle
    raise AssertionError(f"Unknown lane: {lane_name}")


def _run_one_cycle(
    *,
    ops: Any,
    lane_name: str,
    variant: int,
    cfg: PersistentConfig,
    stats: WorkerStats,
    record: bool,
    take_sample: bool,
    bucket_ns: int = 0,
    measure_start_ns: int = 0,
) -> None:
    call = _lane_call(ops, lane_name)
    t0 = time.perf_counter_ns()
    metrics = call(variant)
    _burn_cpu_ns(cfg.app_work_ns)
    cycle_ns = time.perf_counter_ns() - t0
    if record:
        stats.active_ns += cycle_ns
        stats.lanes[lane_name].add_cycle(variant, cycle_ns, metrics, take_sample=take_sample)
        if bucket_ns > 0:
            bucket_ix = (t0 - measure_start_ns) // bucket_ns
            if bucket_ix >= 0:
                stats.add_to_bucket(int(bucket_ix), cycle_ns, take_sample=take_sample)


def _is_burst_active(now_ns: int, measure_start_ns: int, cfg: PersistentConfig) -> bool:
    active_ns = cfg.burst_active_ms * 1_000_000
    idle_ns = cfg.burst_idle_ms * 1_000_000
    period_ns = active_ns + idle_ns
    if period_ns <= active_ns:
        return True
    offset = (now_ns - measure_start_ns) % period_ns
    return offset < active_ns


def _worker_loop(
    *,
    worker_ix: int,
    ops: Any,
    cfg: PersistentConfig,
    ready: threading.Barrier,
    start_event: threading.Event,
    stop_event: threading.Event,
    warmup_deadline_ns: int,
    measure_start_ns: int,
    end_ns: int,
    out_stats: list[WorkerStats],
    errors: list[BaseException],
) -> None:
    stats = WorkerStats()
    seed_base = getattr(base, "_LIB_SEEDS", {}).get(ops.name, 900_001)
    scenario_offset = 10_000 if cfg.scenario == "fastapi_steady" else 20_000
    rng = random.Random(seed_base + scenario_offset + worker_ix * 9973)
    local_counter = 0

    try:
        ready.wait()
        start_event.wait()
        while not stop_event.is_set():
            now_ns = time.perf_counter_ns()
            if now_ns >= end_ns:
                return

            record = now_ns >= measure_start_ns
            take_sample = record and (local_counter % cfg.sample_every == 0)

            if cfg.scenario == "fastapi_steady":
                lane_name = "request"
            else:
                if not _is_burst_active(now_ns, measure_start_ns, cfg):
                    idle_t0 = time.perf_counter_ns()
                    time.sleep(0.001)
                    idle_ns = time.perf_counter_ns() - idle_t0
                    if record:
                        stats.idle_ns += idle_ns
                    continue
                lane_name = _choose_burst_lane(rng, cfg)

            variant = rng.randrange(_VARIANT_COUNT)
            _run_one_cycle(
                ops=ops,
                lane_name=lane_name,
                variant=variant,
                cfg=cfg,
                stats=stats,
                record=record,
                take_sample=take_sample,
                bucket_ns=cfg.bucket_ns,
                measure_start_ns=measure_start_ns,
            )
            local_counter += 1
    except BaseException as exc:
        errors.append(exc)
        stop_event.set()
    finally:
        out_stats[worker_ix] = stats


def run_persistent_benchmark_with_cleanup(lib: str, cfg: PersistentConfig) -> PersistentResult:
    setup_t0 = time.perf_counter_ns()
    ops = base._build_ops(lib)
    try:
        ops.spawn_singletons()
        ops.bootstrap_fanout()
        setup_ns = time.perf_counter_ns() - setup_t0

        ready = threading.Barrier(cfg.threads + 1)
        start_event = threading.Event()
        stop_event = threading.Event()
        errors: list[BaseException] = []
        worker_stats: list[WorkerStats] = [WorkerStats() for _ in range(cfg.threads)]

        now_ns = time.perf_counter_ns()
        warmup_deadline_ns = now_ns + int(cfg.warmup_s * _ONE_BILLION)
        measure_start_ns = warmup_deadline_ns
        end_ns = measure_start_ns + int(cfg.duration_s * _ONE_BILLION)

        gc_monitor: GcBucketMonitor | None = None
        if cfg.bucket_ns > 0:
            gc_monitor = GcBucketMonitor(
                measure_start_ns=measure_start_ns,
                end_ns=end_ns,
                bucket_ns=cfg.bucket_ns,
            )
            gc_monitor.install()

        threads: list[threading.Thread] = []
        for worker_ix in range(cfg.threads):
            thread = threading.Thread(
                target=_worker_loop,
                kwargs={
                    "worker_ix": worker_ix,
                    "ops": ops,
                    "cfg": cfg,
                    "ready": ready,
                    "start_event": start_event,
                    "stop_event": stop_event,
                    "warmup_deadline_ns": warmup_deadline_ns,
                    "measure_start_ns": measure_start_ns,
                    "end_ns": end_ns,
                    "out_stats": worker_stats,
                    "errors": errors,
                },
                daemon=True,
                name=f"persistent-gauntlet-{lib}-{cfg.scenario}-{worker_ix}",
            )
            threads.append(thread)
            thread.start()

        ready.wait()
        actual_start_ns = time.perf_counter_ns()
        start_event.set()
        sleep_seconds = max(0.0, (end_ns - time.perf_counter_ns()) / _ONE_BILLION)
        if sleep_seconds > 0:
            time.sleep(sleep_seconds)
        stop_event.set()
        for thread in threads:
            thread.join()
        actual_end_ns = time.perf_counter_ns()

        if gc_monitor is not None:
            gc_monitor.uninstall()

        if errors:
            raise errors[0]

        merged = WorkerStats()
        for stats in worker_stats:
            merged.merge(stats)

        cleanup_t0 = time.perf_counter_ns()
        ops.cleanup()
        cleanup_ns = time.perf_counter_ns() - cleanup_t0
        gc.collect()

        return PersistentResult(
            lib=lib,
            cfg=cfg,
            gil_status=_gil_status(),
            setup_ns=setup_ns,
            warmup_ns=max(0, measure_start_ns - actual_start_ns),
            measured_ns=max(0, actual_end_ns - measure_start_ns),
            cleanup_ns=cleanup_ns,
            worker_stats=merged,
            gc_buckets=gc_monitor.buckets if gc_monitor is not None else None,
            gc_total=gc_monitor.total if gc_monitor is not None else None,
        )
    except Exception:
        # Best-effort cleanup if benchmark fails.
        try:
            if "gc_monitor" in locals() and gc_monitor is not None:
                gc_monitor.uninstall()
        finally:
            try:
                ops.cleanup()
            finally:
                gc.collect()
        raise


def _print_result(result: PersistentResult) -> None:
    cfg = result.cfg
    stats = result.worker_stats
    measured_s = result.measured_ns / _ONE_BILLION if result.measured_ns > 0 else 0.0
    active_s = stats.active_ns / _ONE_BILLION if stats.active_ns > 0 else 0.0
    idle_s = stats.idle_ns / _ONE_BILLION if stats.idle_ns > 0 else 0.0
    total_cycles = sum(lane.cycles for lane in stats.lanes.values())
    total_objects_min = sum(lane.objects_min for lane in stats.lanes.values())

    print(
        f"[{result.lib}] persistent config: "
        f"scenario={cfg.scenario}, gil={result.gil_status}, duration={cfg.duration_s:.1f}s, "
        f"warmup={cfg.warmup_s:.1f}s, threads={cfg.threads}, sample_every={cfg.sample_every}, "
        f"app_work_ns={cfg.app_work_ns}, setup={_ms(result.setup_ns):.3f}ms, "
        f"cleanup={_ms(result.cleanup_ns):.3f}ms"
    )
    print(
        f"[{result.lib}] persistent summary | "
        f"measured={measured_s:.3f}s, worker_active={active_s:.3f}s, worker_idle={idle_s:.3f}s, "
        f"cycles={total_cycles:,}, objects_min={total_objects_min:,}, "
        f"cycles/s_wall={(total_cycles / measured_s) if measured_s > 0 else 0.0:,.0f}, "
        f"objects/s_wall_min={(total_objects_min / measured_s) if measured_s > 0 else 0.0:,.0f}, "
        f"cycles/s_worker_active={(total_cycles / active_s) if active_s > 0 else 0.0:,.0f}, "
        f"objects/s_worker_active_min={(total_objects_min / active_s) if active_s > 0 else 0.0:,.0f}"
    )

    for lane_name in ("request", "worker_a", "worker_b"):
        lane = stats.lanes[lane_name]
        if lane.cycles <= 0:
            continue
        lane_cycle_wall_s = measured_s
        lane_request_active_s = lane.request_total.total_ns / _ONE_BILLION if lane.request_total.total_ns > 0 else 0.0
        print(
            f"[{result.lib}] persistent lane={lane_name} | "
            f"cycles={lane.cycles:,}, objects_min={lane.objects_min:,}, variants={tuple(lane.variant_counts)}, "
            f"cycles/s_wall={(lane.cycles / lane_cycle_wall_s) if lane_cycle_wall_s > 0 else 0.0:,.0f}, "
            f"objects/s_wall_min={(lane.objects_min / lane_cycle_wall_s) if lane_cycle_wall_s > 0 else 0.0:,.0f}, "
            f"cycles/s_request_active={(lane.cycles / lane_request_active_s) if lane_request_active_s > 0 else 0.0:,.0f}, "
            f"objects/s_request_active_min={(lane.objects_min / lane_request_active_s) if lane_request_active_s > 0 else 0.0:,.0f}"
        )
        print(f"[{result.lib}] lane={lane_name} cycle_total | {lane.cycle_timer.sampled_summary()}")
        print(f"[{result.lib}] lane={lane_name} outer_total | {lane.outer_total.sampled_summary()}")
        print(f"[{result.lib}] lane={lane_name} request_total | {lane.request_total.sampled_summary()}")
        print(f"[{result.lib}] lane={lane_name} outer_create | {lane.outer_create.sampled_summary()}")
        print(f"[{result.lib}] lane={lane_name} outer_cleanup | {lane.outer_cleanup.sampled_summary()}")
        print(f"[{result.lib}] lane={lane_name} request_create | {lane.request_create.sampled_summary()}")
        print(f"[{result.lib}] lane={lane_name} request_cleanup | {lane.request_cleanup.sampled_summary()}")


def _gc_gen_summary(bucket: GcBucketStats) -> str:
    """
    Render per-generation collection counts compactly, e.g. (g0=8,g1=3,g2=1).
    """
    if not bucket.collections_by_gen:
        return "(none)"
    parts = ", ".join(
        f"g{gen}={count}"
        for gen, count in sorted(bucket.collections_by_gen.items())
    )
    return f"({parts})"


def _print_degradation(result: PersistentResult) -> None:
    """
    Print per-bucket throughput/latency/GC lines plus a drift summary.

    Contract:
        - The final bucket is tagged `(partial)` and excluded from drift math
          when the measured window does not fill it.
        - Drift compares the FIRST complete bucket against the LAST complete
          bucket: cycles/s, sampled p99, and GC pause per bucket. Flat lines
          mean the runtime does not degrade with heap age; drifting lines are
          the GC-pressure signature this mode exists to expose.
    """
    cfg = result.cfg
    if cfg.bucket_ns <= 0 or not result.worker_stats.buckets:
        return

    bucket_s = cfg.bucket_s
    measured_s = result.measured_ns / _ONE_BILLION
    complete_bucket_count = int(measured_s // bucket_s)
    gc_buckets = result.gc_buckets or {}
    empty_gc = GcBucketStats()

    print(
        f"[{result.lib}] degradation buckets | bucket={bucket_s:.0f}s, "
        f"complete={complete_bucket_count}, scenario={cfg.scenario}"
    )

    ordered = sorted(result.worker_stats.buckets.items())
    for bucket_ix, bucket in ordered:
        is_partial = bucket_ix >= complete_bucket_count
        span_s = bucket_s if not is_partial else max(
            0.000001, measured_s - bucket_ix * bucket_s,
        )
        samples = sorted(bucket.samples)
        p50 = statistics.median(samples) if samples else 0
        p95 = _pctl(samples, 0.95)
        p99 = _pctl(samples, 0.99)
        gc_bucket = gc_buckets.get(bucket_ix, empty_gc)
        partial_tag = " (partial)" if is_partial else ""
        print(
            f"[{result.lib}] bucket {bucket_ix:03d}{partial_tag} | "
            f"cycles={bucket.cycles:,}, cycles/s={bucket.cycles / span_s:,.0f}, "
            f"p50={_ms(p50):.3f}ms, p95={_ms(p95):.3f}ms, p99={_ms(p99):.3f}ms, "
            f"max={_ms(bucket.max_ns):.3f}ms, samples={len(samples):,} | "
            f"gc: collections={gc_bucket.collections} {_gc_gen_summary(gc_bucket)}, "
            f"collected={gc_bucket.collected_objects:,}, "
            f"pause_total={_ms(gc_bucket.pause_total_ns):.3f}ms, "
            f"pause_max={_ms(gc_bucket.pause_max_ns):.3f}ms"
        )

    complete = [
        (bucket_ix, bucket)
        for bucket_ix, bucket in ordered
        if bucket_ix < complete_bucket_count and bucket.cycles > 0
    ]
    if len(complete) >= 2:
        first_ix, first = complete[0]
        last_ix, last = complete[-1]
        first_thr = first.cycles / bucket_s
        last_thr = last.cycles / bucket_s
        first_p99 = _pctl(sorted(first.samples), 0.99)
        last_p99 = _pctl(sorted(last.samples), 0.99)
        first_gc = gc_buckets.get(first_ix, empty_gc)
        last_gc = gc_buckets.get(last_ix, empty_gc)
        thr_pct = ((last_thr / first_thr) - 1.0) * 100.0 if first_thr > 0 else 0.0
        p99_pct = ((last_p99 / first_p99) - 1.0) * 100.0 if first_p99 > 0 else 0.0
        print(
            f"[{result.lib}] degradation drift (bucket {first_ix:03d} -> {last_ix:03d}) | "
            f"cycles/s: {first_thr:,.0f} -> {last_thr:,.0f} ({thr_pct:+.1f}%), "
            f"p99: {_ms(first_p99):.3f}ms -> {_ms(last_p99):.3f}ms ({p99_pct:+.1f}%), "
            f"gc_pause/bucket: {_ms(first_gc.pause_total_ns):.3f}ms -> "
            f"{_ms(last_gc.pause_total_ns):.3f}ms"
        )
    if result.gc_total is not None:
        total = result.gc_total
        pause_pct = (
            (total.pause_total_ns / result.measured_ns) * 100.0
            if result.measured_ns > 0
            else 0.0
        )
        print(
            f"[{result.lib}] gc totals | collections={total.collections} "
            f"{_gc_gen_summary(total)}, collected={total.collected_objects:,}, "
            f"pause_total={_ms(total.pause_total_ns):.3f}ms "
            f"({pause_pct:.3f}% of measured wall), "
            f"pause_max={_ms(total.pause_max_ns):.3f}ms"
        )


_LIBS = _env_list("PERSISTENT_GAUNTLET_LIBS", ("melder","dependency-injector", "dishka"))
_SCENARIOS = _env_list("PERSISTENT_GAUNTLET_SCENARIOS", ("fastapi_steady", "bursty_app"))


@pytest.mark.timeout(720000)
@pytest.mark.parametrize("scenario", _SCENARIOS)
@pytest.mark.parametrize("lib", _LIBS)
def test_persistent_runtime_gauntlet(lib: str, scenario: str) -> None:
    cfg = PersistentConfig.from_env(scenario)
    result = run_persistent_benchmark_with_cleanup(lib, cfg)
    _print_result(result)
    _print_degradation(result)
