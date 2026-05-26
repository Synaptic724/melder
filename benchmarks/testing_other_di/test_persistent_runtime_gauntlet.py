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
    PERSISTENT_APP_WORK_NS=0
    PERSISTENT_BURST_ACTIVE_MS=2000
    PERSISTENT_BURST_IDLE_MS=1000
    PERSISTENT_BURST_REQUEST_WEIGHT=60
    PERSISTENT_BURST_WORKER_A_WEIGHT=25
    PERSISTENT_BURST_WORKER_B_WEIGHT=15
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

    @staticmethod
    def from_env(scenario: str) -> "PersistentConfig":
        cfg = PersistentConfig(
            scenario=scenario,
            duration_s=_env_float("PERSISTENT_GAUNTLET_SECONDS", 1200.0),
            warmup_s=_env_float("PERSISTENT_GAUNTLET_WARMUP_SECONDS", 10.0),
            threads=_env_int("PERSISTENT_GAUNTLET_THREADS", 10),
            sample_every=max(1, _env_int("PERSISTENT_GAUNTLET_SAMPLE_EVERY", 1000)),
            app_work_ns=max(0, _env_int("PERSISTENT_APP_WORK_NS", 0)),
            burst_active_ms=max(1, _env_int("PERSISTENT_BURST_ACTIVE_MS", 2000)),
            burst_idle_ms=max(0, _env_int("PERSISTENT_BURST_IDLE_MS", 1000)),
            burst_request_weight=max(0, _env_int("PERSISTENT_BURST_REQUEST_WEIGHT", 60)),
            burst_worker_a_weight=max(0, _env_int("PERSISTENT_BURST_WORKER_A_WEIGHT", 25)),
            burst_worker_b_weight=max(0, _env_int("PERSISTENT_BURST_WORKER_B_WEIGHT", 15)),
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

    def merge(self, other: "WorkerStats") -> None:
        self.active_ns += other.active_ns
        self.idle_ns += other.idle_ns
        for lane_name, lane_stats in other.lanes.items():
            self.lanes[lane_name].merge(lane_stats)


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
) -> None:
    call = _lane_call(ops, lane_name)
    t0 = time.perf_counter_ns()
    metrics = call(variant)
    _burn_cpu_ns(cfg.app_work_ns)
    cycle_ns = time.perf_counter_ns() - t0
    if record:
        stats.active_ns += cycle_ns
        stats.lanes[lane_name].add_cycle(variant, cycle_ns, metrics, take_sample=take_sample)


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
        )
    except Exception:
        # Best-effort cleanup if benchmark fails.
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


_LIBS = _env_list("PERSISTENT_GAUNTLET_LIBS", ("dependency-injector", "dishka", "melder"))
_SCENARIOS = _env_list("PERSISTENT_GAUNTLET_SCENARIOS", ("fastapi_steady", "bursty_app"))


@pytest.mark.timeout(720000)
@pytest.mark.parametrize("scenario", _SCENARIOS)
@pytest.mark.parametrize("lib", _LIBS)
def test_persistent_runtime_gauntlet(lib: str, scenario: str) -> None:
    cfg = PersistentConfig.from_env(scenario)
    result = run_persistent_benchmark_with_cleanup(lib, cfg)
    _print_result(result)
