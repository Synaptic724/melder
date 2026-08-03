import os
import random
import statistics
import sys
import threading
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Tuple, Union


def env_int(name: str, default: int) -> int:
    """
    Read one integer environment variable for the benchmark.

    Args:
        name:
            Environment variable name to read.
        default:
            Value returned when the variable is unset or empty.

    Returns:
        int:
            Parsed integer value.
    """
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


def gil_status() -> str:
    """
    Return the interpreter GIL status label for benchmark reporting.

    Returns:
        str:
            `"enabled"`, `"disabled"`, or `"unknown"`.
    """
    flag = getattr(sys, "_is_gil_enabled", None)
    if flag is None:
        return "unknown"
    try:
        return "enabled" if flag() else "disabled"
    except Exception:
        return "unknown"


def pctl_ns(sorted_values: List[int], quantile: float) -> int:
    """
    Return one percentile-like sample from a sorted nanosecond list.

    Args:
        sorted_values:
            Sorted timing samples.
        quantile:
            Fraction between `0.0` and `1.0`.

    Returns:
        int:
            Sample at the requested quantile index.
    """
    if not sorted_values:
        raise AssertionError("No samples recorded")
    index = max(0, min(len(sorted_values) - 1, int((len(sorted_values) - 1) * quantile)))
    return sorted_values[index]


def ms(ns: Union[int, float]) -> float:
    """
    Convert nanoseconds to milliseconds.

    Args:
        ns:
            Nanosecond duration.

    Returns:
        float:
            Millisecond duration.
    """
    return float(ns) / 1_000_000.0


class _NoDeps:
    __slots__ = ()

    def __init__(self) -> None:
        return None


class AppSingletonA(_NoDeps):
    __slots__ = ()


class AppSingletonB(_NoDeps):
    __slots__ = ()


class AppSingletonC(_NoDeps):
    __slots__ = ()


class AppSingletonD(_NoDeps):
    __slots__ = ()


class AppSingletonE(_NoDeps):
    __slots__ = ()


class BootstrapAObject:
    __slots__ = ("root",)

    def __init__(self, root: AppSingletonA) -> None:
        self.root = root


class BootstrapBObject:
    __slots__ = ("root",)

    def __init__(self, root: AppSingletonB) -> None:
        self.root = root


class BootstrapCObject:
    __slots__ = ("root",)

    def __init__(self, root: AppSingletonC) -> None:
        self.root = root


class BootstrapDObject:
    __slots__ = ("root",)

    def __init__(self, root: AppSingletonD) -> None:
        self.root = root


class BootstrapEObject:
    __slots__ = ("root",)

    def __init__(self, root: AppSingletonE) -> None:
        self.root = root


class Layer1Scope:
    __slots__ = ("entry", "shared")

    def __init__(self, entry: BootstrapAObject, shared: AppSingletonE) -> None:
        self.entry = entry
        self.shared = shared


class Layer2Scope:
    __slots__ = ("prior", "branch")

    def __init__(self, prior: Layer1Scope, branch: AppSingletonB) -> None:
        self.prior = prior
        self.branch = branch


class Layer3Scope:
    __slots__ = ("prior", "branch")

    def __init__(self, prior: Layer2Scope, branch: AppSingletonC) -> None:
        self.prior = prior
        self.branch = branch


class Layer4Scope:
    __slots__ = ("prior", "branch")

    def __init__(self, prior: Layer3Scope, branch: AppSingletonD) -> None:
        self.prior = prior
        self.branch = branch


class RequestLeaf(_NoDeps):
    __slots__ = ()


class RequestSession:
    __slots__ = ("scope", "shared")

    def __init__(self, scope: Layer4Scope, shared: AppSingletonE) -> None:
        self.scope = scope
        self.shared = shared


class RequestScopeMarker:
    __slots__ = ("session",)

    def __init__(self, session: RequestSession) -> None:
        self.session = session


class RequestGroup:
    __slots__ = ("session", "leaves")

    def __init__(
        self,
        session: RequestSession,
        leaf0: RequestLeaf,
        leaf1: RequestLeaf,
        leaf2: RequestLeaf,
        leaf3: RequestLeaf,
        leaf4: RequestLeaf,
        leaf5: RequestLeaf,
        leaf6: RequestLeaf,
        leaf7: RequestLeaf,
        leaf8: RequestLeaf,
        leaf9: RequestLeaf,
    ) -> None:
        self.session = session
        self.leaves = (leaf0, leaf1, leaf2, leaf3, leaf4, leaf5, leaf6, leaf7, leaf8, leaf9)


class RequestRoot:
    __slots__ = ("session", "groups")

    def __init__(
        self,
        session: RequestSession,
        marker: RequestScopeMarker,
        group0: RequestGroup,
        group1: RequestGroup,
        group2: RequestGroup,
        group3: RequestGroup,
        group4: RequestGroup,
    ) -> None:
        self.session = session
        self.groups = (group0, group1, group2, group3, group4)


class WorkerALeaf(_NoDeps):
    __slots__ = ()


class WorkerASession:
    __slots__ = ("entry", "shared")

    def __init__(self, entry: BootstrapBObject, shared: AppSingletonE) -> None:
        self.entry = entry
        self.shared = shared


class WorkerAScopeMarker:
    __slots__ = ("session",)

    def __init__(self, session: WorkerASession) -> None:
        self.session = session


class WorkerAGroup:
    __slots__ = ("session", "leaves")

    def __init__(
        self,
        session: WorkerASession,
        leaf0: WorkerALeaf,
        leaf1: WorkerALeaf,
        leaf2: WorkerALeaf,
        leaf3: WorkerALeaf,
        leaf4: WorkerALeaf,
        leaf5: WorkerALeaf,
    ) -> None:
        self.session = session
        self.leaves = (leaf0, leaf1, leaf2, leaf3, leaf4, leaf5)


class WorkerAJobRoot:
    __slots__ = ("session", "groups")

    def __init__(
        self,
        session: WorkerASession,
        marker: WorkerAScopeMarker,
        group0: WorkerAGroup,
        group1: WorkerAGroup,
        group2: WorkerAGroup,
    ) -> None:
        self.session = session
        self.groups = (group0, group1, group2)


class WorkerBLeaf(_NoDeps):
    __slots__ = ()


class WorkerBSession:
    __slots__ = ("entry", "peer")

    def __init__(self, entry: BootstrapCObject, peer: AppSingletonD) -> None:
        self.entry = entry
        self.peer = peer


class WorkerBScopeMarker:
    __slots__ = ("session",)

    def __init__(self, session: WorkerBSession) -> None:
        self.session = session


class WorkerBGroup:
    __slots__ = ("session", "leaves")

    def __init__(
        self,
        session: WorkerBSession,
        leaf0: WorkerBLeaf,
        leaf1: WorkerBLeaf,
        leaf2: WorkerBLeaf,
    ) -> None:
        self.session = session
        self.leaves = (leaf0, leaf1, leaf2)


class WorkerBJobRoot:
    __slots__ = ("session", "groups", "shared")

    def __init__(
        self,
        session: WorkerBSession,
        marker: WorkerBScopeMarker,
        group0: WorkerBGroup,
        group1: WorkerBGroup,
        group2: WorkerBGroup,
        group3: WorkerBGroup,
        shared: AppSingletonE,
    ) -> None:
        self.session = session
        self.groups = (group0, group1, group2, group3)
        self.shared = shared


SINGLETON_TYPES: Tuple[type, ...] = (
    AppSingletonA,
    AppSingletonB,
    AppSingletonC,
    AppSingletonD,
    AppSingletonE,
)
BOOTSTRAP_TYPES: Tuple[type, ...] = (
    BootstrapAObject,
    BootstrapBObject,
    BootstrapCObject,
    BootstrapDObject,
    BootstrapEObject,
)
OUTER_SCOPED_TYPES: Tuple[type, ...] = (
    RequestSession,
    WorkerASession,
    WorkerBSession,
)
REQUEST_SCOPED_TYPES: Tuple[type, ...] = (
    RequestScopeMarker,
    WorkerAScopeMarker,
    WorkerBScopeMarker,
)
REQUEST_SCOPE_TRANSIENT_TYPES: Tuple[type, ...] = (
    RequestLeaf,
    RequestGroup,
    RequestRoot,
    WorkerALeaf,
    WorkerAGroup,
    WorkerAJobRoot,
    WorkerBLeaf,
    WorkerBGroup,
    WorkerBJobRoot,
)
ALL_CLASSES: Tuple[type, ...] = (
    *SINGLETON_TYPES,
    *BOOTSTRAP_TYPES,
    Layer1Scope,
    Layer2Scope,
    Layer3Scope,
    Layer4Scope,
    RequestLeaf,
    RequestSession,
    RequestScopeMarker,
    RequestGroup,
    RequestRoot,
    WorkerALeaf,
    WorkerASession,
    WorkerAScopeMarker,
    WorkerAGroup,
    WorkerAJobRoot,
    WorkerBLeaf,
    WorkerBSession,
    WorkerBScopeMarker,
    WorkerBGroup,
    WorkerBJobRoot,
)

REQUEST_OBJECTS_PER_ROOT = 63
REQUEST_SCOPE_RUNS_DEFAULT = 10
WORKER_A_OBJECTS_PER_ROOT = 25
WORKER_B_OBJECTS_PER_ROOT = 20
WORKER_A_JOBS_DEFAULT = 25
WORKER_B_JOBS_DEFAULT = 30
BOOTSTRAP_FANOUT_PER_SINGLETON = 5
VARIANT_COUNT = 3
LIB_SEED = 330_011


@dataclass(frozen=True)
class GauntletConfig:
    iterations: int
    threads: int
    request_scope_runs: int
    worker_a_jobs: int
    worker_b_jobs: int


@dataclass(frozen=True)
class RuntimeOps:
    name: str
    spawn_singletons: Callable[[], None]
    bootstrap_fanout: Callable[[], None]
    request_scope_cycle: Callable[[int], "ScopeCycleMetrics"]
    worker_a_scope_cycle: Callable[[int], "ScopeCycleMetrics"]
    worker_b_scope_cycle: Callable[[int], "ScopeCycleMetrics"]
    cleanup: Callable[[], None]


@dataclass(frozen=True)
class Summary:
    total_ns: int
    avg_ns: float
    median_ns: float
    p95_ns: int
    p99_ns: int
    min_ns: int
    max_ns: int
    stdev_ns: float
    cv: float


@dataclass(frozen=True)
class ScopeCycleMetrics:
    outer_create_ns: int
    outer_cleanup_ns: int
    outer_total_ns: int
    request_create_ns: int
    request_cleanup_ns: int
    request_total_ns: int


@dataclass
class LaneMetricSamples:
    outer_create_ns: List[int]
    outer_cleanup_ns: List[int]
    outer_total_ns: List[int]
    request_create_ns: List[int]
    request_cleanup_ns: List[int]
    request_total_ns: List[int]


@dataclass(frozen=True)
class LaneSummary:
    name: str
    cycles: int
    objects_min: int
    wall_cycles_per_s: float
    wall_objects_per_s_min: float
    active_cycles_per_s: float
    active_objects_per_s_min: float
    variant_counts: Tuple[int, ...]
    outer_create_summary: Summary
    outer_cleanup_summary: Summary
    outer_total_summary: Summary
    request_create_summary: Summary
    request_cleanup_summary: Summary
    request_total_summary: Summary


@dataclass
class IterationResult:
    total_ns: int
    bootstrap_ns: int
    threaded_ns: int
    lane_metrics: Dict[str, LaneMetricSamples]
    lane_variant_counts: Dict[str, List[int]]


@dataclass(frozen=True)
class BenchmarkResult:
    lib: str
    cfg: GauntletConfig
    gil_status_label: str
    setup_singletons: int
    request_objects_min: int
    hot_objects_per_iter_min: int
    setup_ns: int
    cleanup_ns: int
    iteration_summary: Summary
    bootstrap_summary: Summary
    threaded_summary: Summary
    total_hot_scopes: int
    hot_scope_cycles_per_s: float
    hot_objects_per_s_min: float
    outer_scope_create_summary: Summary
    outer_scope_cleanup_summary: Summary
    outer_scope_total_summary: Summary
    request_scope_create_summary: Summary
    request_scope_cleanup_summary: Summary
    request_scope_total_summary: Summary
    lane_summaries: Dict[str, LaneSummary]


def new_lane_metric_samples() -> LaneMetricSamples:
    return LaneMetricSamples(
        outer_create_ns=[],
        outer_cleanup_ns=[],
        outer_total_ns=[],
        request_create_ns=[],
        request_cleanup_ns=[],
        request_total_ns=[],
    )


def lane_objects_per_cycle(name: str) -> int:
    if name == "request":
        return REQUEST_OBJECTS_PER_ROOT
    if name == "worker_a":
        return WORKER_A_OBJECTS_PER_ROOT
    if name == "worker_b":
        return WORKER_B_OBJECTS_PER_ROOT
    raise AssertionError(f"Unknown lane: {name}")


def summarize(samples: List[int]) -> Summary:
    ordered = sorted(samples)
    stdev_ns = statistics.pstdev(samples) if len(samples) > 1 else 0.0
    avg_ns = float(sum(samples)) / float(len(samples))
    return Summary(
        total_ns=sum(samples),
        avg_ns=avg_ns,
        median_ns=statistics.median(samples),
        p95_ns=pctl_ns(ordered, 0.95),
        p99_ns=pctl_ns(ordered, 0.99),
        min_ns=ordered[0],
        max_ns=ordered[-1],
        stdev_ns=stdev_ns,
        cv=(stdev_ns / avg_ns) if avg_ns > 0 else 0.0,
    )


def format_summary_ms(summary: Summary) -> str:
    return (
        f"avg={ms(summary.avg_ns):.3f}ms | "
        f"median={ms(summary.median_ns):.3f}ms | "
        f"p95={ms(summary.p95_ns):.3f}ms | "
        f"p99={ms(summary.p99_ns):.3f}ms | "
        f"min={ms(summary.min_ns):.3f}ms | "
        f"max={ms(summary.max_ns):.3f}ms | "
        f"stdev={ms(summary.stdev_ns):.3f}ms | "
        f"cv={summary.cv:.1%}"
    )


def summarize_lane(
    *,
    name: str,
    metric_samples: LaneMetricSamples,
    variant_counts: List[int],
    wall_total_ns: int,
) -> LaneSummary:
    outer_total_summary = summarize(metric_samples.outer_total_ns)
    request_total_summary = summarize(metric_samples.request_total_ns)
    objects_min = len(metric_samples.outer_total_ns) * lane_objects_per_cycle(name)
    active_seconds = request_total_summary.total_ns / 1_000_000_000.0 if request_total_summary.total_ns > 0 else 0.0
    wall_seconds = wall_total_ns / 1_000_000_000.0 if wall_total_ns > 0 else 0.0
    return LaneSummary(
        name=name,
        cycles=len(metric_samples.outer_total_ns),
        objects_min=objects_min,
        wall_cycles_per_s=(len(metric_samples.outer_total_ns) / wall_seconds) if wall_seconds > 0 else 0.0,
        wall_objects_per_s_min=(objects_min / wall_seconds) if wall_seconds > 0 else 0.0,
        active_cycles_per_s=(len(metric_samples.outer_total_ns) / active_seconds) if active_seconds > 0 else 0.0,
        active_objects_per_s_min=(objects_min / active_seconds) if active_seconds > 0 else 0.0,
        variant_counts=tuple(variant_counts),
        outer_create_summary=summarize(metric_samples.outer_create_ns),
        outer_cleanup_summary=summarize(metric_samples.outer_cleanup_ns),
        outer_total_summary=outer_total_summary,
        request_create_summary=summarize(metric_samples.request_create_ns),
        request_cleanup_summary=summarize(metric_samples.request_cleanup_ns),
        request_total_summary=request_total_summary,
    )


def run_gauntlet_once(ops: RuntimeOps, cfg: GauntletConfig, iteration_ix: int) -> IterationResult:
    """
    Time one full gauntlet iteration from fresh bootstrap through cleanup.
    """
    total_t0 = time.perf_counter_ns()
    bootstrap_t0 = time.perf_counter_ns()
    ops.bootstrap_fanout()
    bootstrap_ns = time.perf_counter_ns() - bootstrap_t0

    lane_counts = {"request": 0, "worker_a": 0, "worker_b": 0}
    lane_metrics = {
        "request": new_lane_metric_samples(),
        "worker_a": new_lane_metric_samples(),
        "worker_b": new_lane_metric_samples(),
    }
    lane_variant_counts = {
        "request": [0] * VARIANT_COUNT,
        "worker_a": [0] * VARIANT_COUNT,
        "worker_b": [0] * VARIANT_COUNT,
    }
    errors: List[BaseException] = []
    stop_event = threading.Event()
    active_lanes: List[Tuple[str, Callable[[int], ScopeCycleMetrics], int, int]] = []
    if cfg.threads <= 3:
        active_lanes.append(("request", ops.request_scope_cycle, cfg.request_scope_runs, 17))
        if cfg.threads >= 2:
            active_lanes.append(("worker_a", ops.worker_a_scope_cycle, cfg.worker_a_jobs, 29))
        if cfg.threads >= 3:
            active_lanes.append(("worker_b", ops.worker_b_scope_cycle, cfg.worker_b_jobs, 41))
    else:
        num_req = cfg.threads // 3 + (1 if cfg.threads % 3 > 0 else 0)
        num_a = cfg.threads // 3 + (1 if cfg.threads % 3 > 1 else 0)
        num_b = cfg.threads // 3
        for idx in range(num_req):
            active_lanes.append(("request", ops.request_scope_cycle, cfg.request_scope_runs, 17 + idx * 100))
        for idx in range(num_a):
            active_lanes.append(("worker_a", ops.worker_a_scope_cycle, cfg.worker_a_jobs, 29 + idx * 100))
        for idx in range(num_b):
            active_lanes.append(("worker_b", ops.worker_b_scope_cycle, cfg.worker_b_jobs, 41 + idx * 100))

    ready_barrier = threading.Barrier(len(active_lanes) + 1)
    start_event = threading.Event()

    def make_worker(
        name: str,
        call: Callable[[int], ScopeCycleMetrics],
        reps: int,
        seed_offset: int,
    ) -> Callable[[], None]:
        def worker() -> None:
            try:
                rng = random.Random(LIB_SEED + iteration_ix * 101 + seed_offset)
                ready_barrier.wait()
                start_event.wait()
                for _ in range(reps):
                    if stop_event.is_set():
                        return
                    variant = rng.randrange(VARIANT_COUNT)
                    metrics = call(variant)
                    lane_metrics[name].outer_create_ns.append(metrics.outer_create_ns)
                    lane_metrics[name].outer_cleanup_ns.append(metrics.outer_cleanup_ns)
                    lane_metrics[name].outer_total_ns.append(metrics.outer_total_ns)
                    lane_metrics[name].request_create_ns.append(metrics.request_create_ns)
                    lane_metrics[name].request_cleanup_ns.append(metrics.request_cleanup_ns)
                    lane_metrics[name].request_total_ns.append(metrics.request_total_ns)
                    lane_counts[name] += 1
                    lane_variant_counts[name][variant] += 1
            except BaseException as exc:
                errors.append(exc)
                stop_event.set()

        return worker

    thread_list: List[threading.Thread] = []
    for lane_name, lane_call, reps, seed_offset in active_lanes:
        thread_item = threading.Thread(
            target=make_worker(lane_name, lane_call, reps, seed_offset),
            daemon=True,
        )
        thread_list.append(thread_item)
        thread_item.start()

    ready_barrier.wait()
    threaded_t0 = time.perf_counter_ns()
    start_event.set()

    for thread_item in thread_list:
        thread_item.join()
    threaded_ns = time.perf_counter_ns() - threaded_t0

    if errors:
        raise errors[0]

    num_req = cfg.threads // 3 + (1 if cfg.threads % 3 > 0 else 0) if cfg.threads > 3 else (1 if cfg.threads >= 1 else 0)
    num_a = cfg.threads // 3 + (1 if cfg.threads % 3 > 1 else 0) if cfg.threads > 3 else (1 if cfg.threads >= 2 else 0)
    num_b = cfg.threads // 3 if cfg.threads > 3 else (1 if cfg.threads >= 3 else 0)

    if len(lane_metrics["request"].outer_create_ns) != cfg.request_scope_runs * num_req:
        raise AssertionError(f"Request lane did not complete expected scope cycles ({len(lane_metrics['request'].outer_create_ns)} vs {cfg.request_scope_runs * num_req})")
    if len(lane_metrics["worker_a"].outer_create_ns) != cfg.worker_a_jobs * num_a:
        raise AssertionError(f"Worker A lane did not complete expected scope cycles ({len(lane_metrics['worker_a'].outer_create_ns)} vs {cfg.worker_a_jobs * num_a})")
    if len(lane_metrics["worker_b"].outer_create_ns) != cfg.worker_b_jobs * num_b:
        raise AssertionError(f"Worker B lane did not complete expected scope cycles ({len(lane_metrics['worker_b'].outer_create_ns)} vs {cfg.worker_b_jobs * num_b})")

    return IterationResult(
        total_ns=time.perf_counter_ns() - total_t0,
        bootstrap_ns=bootstrap_ns,
        threaded_ns=threaded_ns,
        lane_metrics=lane_metrics,
        lane_variant_counts=lane_variant_counts,
    )


def run_gauntlet_benchmark(ops: RuntimeOps, cfg: GauntletConfig) -> BenchmarkResult:
    """
    Run the generic gauntlet harness for one already-built runtime surface.
    """
    min_request_objects = cfg.request_scope_runs * REQUEST_OBJECTS_PER_ROOT
    min_worker_a_objects = cfg.worker_a_jobs * WORKER_A_OBJECTS_PER_ROOT if cfg.threads >= 2 else 0
    min_worker_b_objects = cfg.worker_b_jobs * WORKER_B_OBJECTS_PER_ROOT if cfg.threads >= 3 else 0
    bootstrap_objects = len(BOOTSTRAP_TYPES) * BOOTSTRAP_FANOUT_PER_SINGLETON
    hot_objects_per_iter_min = bootstrap_objects + min_request_objects + min_worker_a_objects + min_worker_b_objects
    setup_singletons = len(SINGLETON_TYPES)

    setup_t0 = time.perf_counter_ns()
    cleanup_ns = 0
    try:
        ops.spawn_singletons()
        setup_ns = time.perf_counter_ns() - setup_t0

        iteration_samples: List[int] = []
        bootstrap_samples: List[int] = []
        threaded_samples: List[int] = []
        lane_metric_samples = {
            "request": new_lane_metric_samples(),
            "worker_a": new_lane_metric_samples(),
            "worker_b": new_lane_metric_samples(),
        }
        lane_variant_counts = {
            "request": [0] * VARIANT_COUNT,
            "worker_a": [0] * VARIANT_COUNT,
            "worker_b": [0] * VARIANT_COUNT,
        }

        for iteration_ix in range(cfg.iterations):
            iteration = run_gauntlet_once(ops, cfg, iteration_ix)
            iteration_samples.append(iteration.total_ns)
            bootstrap_samples.append(iteration.bootstrap_ns)
            threaded_samples.append(iteration.threaded_ns)
            for lane_name, values in iteration.lane_metrics.items():
                lane_metric_samples[lane_name].outer_create_ns.extend(values.outer_create_ns)
                lane_metric_samples[lane_name].outer_cleanup_ns.extend(values.outer_cleanup_ns)
                lane_metric_samples[lane_name].outer_total_ns.extend(values.outer_total_ns)
                lane_metric_samples[lane_name].request_create_ns.extend(values.request_create_ns)
                lane_metric_samples[lane_name].request_cleanup_ns.extend(values.request_cleanup_ns)
                lane_metric_samples[lane_name].request_total_ns.extend(values.request_total_ns)
            for lane_name, counts in iteration.lane_variant_counts.items():
                for index, count in enumerate(counts):
                    lane_variant_counts[lane_name][index] += count

        iteration_summary = summarize(iteration_samples)
        bootstrap_summary = summarize(bootstrap_samples)
        threaded_summary = summarize(threaded_samples)
        lane_summaries: Dict[str, LaneSummary] = {}
        for lane_name, metric_samples in lane_metric_samples.items():
            if not metric_samples.outer_total_ns:
                continue
            lane_summaries[lane_name] = summarize_lane(
                name=lane_name,
                metric_samples=metric_samples,
                variant_counts=lane_variant_counts[lane_name],
                wall_total_ns=threaded_summary.total_ns,
            )

        combined_outer_create: List[int] = []
        combined_outer_cleanup: List[int] = []
        combined_outer_total: List[int] = []
        combined_request_create: List[int] = []
        combined_request_cleanup: List[int] = []
        combined_request_total: List[int] = []
        for metric_samples in lane_metric_samples.values():
            combined_outer_create.extend(metric_samples.outer_create_ns)
            combined_outer_cleanup.extend(metric_samples.outer_cleanup_ns)
            combined_outer_total.extend(metric_samples.outer_total_ns)
            combined_request_create.extend(metric_samples.request_create_ns)
            combined_request_cleanup.extend(metric_samples.request_cleanup_ns)
            combined_request_total.extend(metric_samples.request_total_ns)

        total_hot_scopes = sum(summary.cycles for summary in lane_summaries.values())
        hot_seconds = iteration_summary.total_ns / 1_000_000_000.0 if iteration_summary.total_ns > 0 else 0.0
    finally:
        cleanup_t0 = time.perf_counter_ns()
        ops.cleanup()
        cleanup_ns = time.perf_counter_ns() - cleanup_t0

    return BenchmarkResult(
        lib=ops.name,
        cfg=cfg,
        gil_status_label=gil_status(),
        setup_singletons=setup_singletons,
        request_objects_min=min_request_objects,
        hot_objects_per_iter_min=hot_objects_per_iter_min,
        setup_ns=setup_ns,
        cleanup_ns=cleanup_ns,
        iteration_summary=iteration_summary,
        bootstrap_summary=bootstrap_summary,
        threaded_summary=threaded_summary,
        total_hot_scopes=total_hot_scopes,
        hot_scope_cycles_per_s=(total_hot_scopes / hot_seconds) if hot_seconds > 0 else 0.0,
        hot_objects_per_s_min=((hot_objects_per_iter_min * cfg.iterations) / hot_seconds) if hot_seconds > 0 else 0.0,
        outer_scope_create_summary=summarize(combined_outer_create),
        outer_scope_cleanup_summary=summarize(combined_outer_cleanup),
        outer_scope_total_summary=summarize(combined_outer_total),
        request_scope_create_summary=summarize(combined_request_create),
        request_scope_cleanup_summary=summarize(combined_request_cleanup),
        request_scope_total_summary=summarize(combined_request_total),
        lane_summaries=lane_summaries,
    )


def print_benchmark_result(result: BenchmarkResult) -> None:
    """
    Print one benchmark result in the gauntlet's human-readable format.
    """
    print(
        f"[{result.lib}] gauntlet config: "
        f"gil={result.gil_status_label}, "
        f"setup_singletons={result.setup_singletons}, "
        f"iterations={result.cfg.iterations}, "
        f"threads={result.cfg.threads}, "
        f"request_scopes={result.cfg.request_scope_runs}, "
        f"worker_a_scopes={result.cfg.worker_a_jobs if result.cfg.threads >= 2 else 0}, "
        f"worker_b_scopes={result.cfg.worker_b_jobs if result.cfg.threads >= 3 else 0}, "
        f"request_objects_min={result.request_objects_min}, "
        f"hot_objects_per_iter_min={result.hot_objects_per_iter_min}, "
        f"setup={ms(result.setup_ns):.3f}ms"
    )
    print(
        f"[{result.lib}] gauntlet total({result.cfg.iterations})={ms(result.iteration_summary.total_ns):.2f}ms | "
        f"{format_summary_ms(result.iteration_summary)}"
    )
    print(f"[{result.lib}] gauntlet bootstrap per-iter | {format_summary_ms(result.bootstrap_summary)}")
    print(f"[{result.lib}] gauntlet threaded phase per-iter | {format_summary_ms(result.threaded_summary)}")
    print(f"[{result.lib}] outer-scope create | {format_summary_ms(result.outer_scope_create_summary)}")
    print(f"[{result.lib}] outer-scope cleanup | {format_summary_ms(result.outer_scope_cleanup_summary)}")
    print(f"[{result.lib}] outer-scope whole-cycle | {format_summary_ms(result.outer_scope_total_summary)}")
    print(f"[{result.lib}] request-scope create | {format_summary_ms(result.request_scope_create_summary)}")
    print(f"[{result.lib}] request-scope cleanup | {format_summary_ms(result.request_scope_cleanup_summary)}")
    print(f"[{result.lib}] request-scope whole-cycle | {format_summary_ms(result.request_scope_total_summary)}")
    print(
        f"[{result.lib}] gauntlet throughput | "
        f"hot_scopes={result.total_hot_scopes}, "
        f"hot_scopes/s={result.hot_scope_cycles_per_s:,.0f}, "
        f"hot_objects/s_min={result.hot_objects_per_s_min:,.0f}, "
        f"cleanup={ms(result.cleanup_ns):.3f}ms"
    )
    for lane_name in ("request", "worker_a", "worker_b"):
        lane = result.lane_summaries.get(lane_name)
        if lane is None:
            continue
        print(
            f"[{result.lib}] lane={lane.name} | "
            f"cycles={lane.cycles}, "
            f"objects_min={lane.objects_min}, "
            f"variants={lane.variant_counts}, "
            f"wall_cycles/s={lane.wall_cycles_per_s:,.0f}, "
            f"wall_objects/s_min={lane.wall_objects_per_s_min:,.0f}, "
            f"active_cycles/s={lane.active_cycles_per_s:,.0f}, "
            f"active_objects/s_min={lane.active_objects_per_s_min:,.0f}, "
            f"outer_create[{format_summary_ms(lane.outer_create_summary)}], "
            f"outer_cleanup[{format_summary_ms(lane.outer_cleanup_summary)}], "
            f"outer_total[{format_summary_ms(lane.outer_total_summary)}], "
            f"request_create[{format_summary_ms(lane.request_create_summary)}], "
            f"request_cleanup[{format_summary_ms(lane.request_cleanup_summary)}], "
            f"request_total[{format_summary_ms(lane.request_total_summary)}]"
        )
