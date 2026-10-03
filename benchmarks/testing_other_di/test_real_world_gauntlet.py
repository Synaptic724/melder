from __future__ import annotations

import contextvars
import csv
import gc
import json
import os
import random
import statistics
import subprocess
import sys
import tempfile
import threading
import time
import typing
from array import array
from collections.abc import Callable, MutableSequence, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import pytest

# Every measured library runs in a fresh child with -X gil=0 and PYTHON_GIL=0.
# The measurement entry point also refuses a process whose GIL is enabled.

# EDIT THESE SETTINGS, then run test_real_world_gauntlet through pytest.
# Every library/thread-count/round runs in a fresh GIL-off process automatically.
REAL_WORLD_GAUNTLET_ITERATION_COUNTS: list[int] = [5_000, 10_000, 15_000, 25_000, 50_000]
REAL_WORLD_GAUNTLET_THREAD_COUNTS: list[int] = [3, 5, 7, 9]
REAL_WORLD_GAUNTLET_ROUNDS: int = 1


def _runner_path() -> Path:
    """
    Resolve the standalone shared-gauntlet runner.
    """
    return Path(__file__).resolve().with_name("real_world_gauntlet_gil_runner.py")


def _repo_root() -> Path:
    """
    Resolve the repository root for standalone runner execution.
    """
    return Path(__file__).resolve().parents[2]


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


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


def _gil_status() -> str:
    flag = getattr(sys, "_is_gil_enabled", None)
    if flag is None:
        return "unknown"
    try:
        return "enabled" if flag() else "disabled"
    except Exception:
        return "unknown"


def _ctor_param_types(cls: type) -> tuple[tuple[str, type], ...]:
    """
    Extract typed constructor params for class wiring.
    """
    inspect_mod = typing.cast(Any, __import__("inspect"))
    init = cls.__init__
    sig = inspect_mod.signature(init)
    params = list(sig.parameters.values())[1:]
    try:
        hints = typing.get_type_hints(init, include_extras=True)
    except Exception:
        hints = getattr(init, "__annotations__", {}) or {}

    out: list[tuple[str, type]] = []
    for p in params:
        ann = hints.get(p.name, p.annotation)
        if ann is inspect_mod._empty or ann is None:
            raise AssertionError(f"{cls.__name__}.__init__ param '{p.name}' missing annotation")
        if not isinstance(ann, type):
            raise AssertionError(f"{cls.__name__}.__init__ param '{p.name}' has non-type annotation: {ann!r}")
        out.append((p.name, ann))
    return tuple(out)


def _pctl_ns(sorted_values: list[int], q: float) -> int:
    if not sorted_values:
        raise AssertionError("No samples recorded")
    ix = max(0, min(len(sorted_values) - 1, int((len(sorted_values) - 1) * q)))
    return sorted_values[ix]


def _ms(ns: float) -> float:
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
    __slots__ = ("branch", "prior")

    def __init__(self, prior: Layer1Scope, branch: AppSingletonB) -> None:
        self.prior = prior
        self.branch = branch


class Layer3Scope:
    __slots__ = ("branch", "prior")

    def __init__(self, prior: Layer2Scope, branch: AppSingletonC) -> None:
        self.prior = prior
        self.branch = branch


class Layer4Scope:
    __slots__ = ("branch", "prior")

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
    __slots__ = ("leaves", "session")

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
    __slots__ = ("groups", "session")

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
    __slots__ = ("leaves", "session")

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
    __slots__ = ("groups", "session")

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
    __slots__ = ("leaves", "session")

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
    __slots__ = ("groups", "session", "shared")

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


_SINGLETON_TYPES: tuple[type, ...] = (
    AppSingletonA,
    AppSingletonB,
    AppSingletonC,
    AppSingletonD,
    AppSingletonE,
)
_BOOTSTRAP_TYPES: tuple[type, ...] = (
    BootstrapAObject,
    BootstrapBObject,
    BootstrapCObject,
    BootstrapDObject,
    BootstrapEObject,
)
_OUTER_SCOPED_TYPES: tuple[type, ...] = (
    RequestSession,
    WorkerASession,
    WorkerBSession,
)
_REQUEST_SCOPED_TYPES: tuple[type, ...] = (
    RequestScopeMarker,
    WorkerAScopeMarker,
    WorkerBScopeMarker,
    # Per-request roots are request types: request-scoped, not transient.
    # Mirrors the melder gauntlet binding so the comparison stays
    # apples-to-apples across every framework, and matches the rule that a
    # transient (many) must not capture a request-scoped instance.
    RequestRoot,
    WorkerAJobRoot,
    WorkerBJobRoot,
)
_REQUEST_SCOPE_TRANSIENT_TYPES: tuple[type, ...] = (
    RequestLeaf,
    RequestGroup,
    WorkerALeaf,
    WorkerAGroup,
    WorkerBLeaf,
    WorkerBGroup,
)
_ALL_CLASSES: tuple[type, ...] = (
    *_SINGLETON_TYPES,
    *_BOOTSTRAP_TYPES,
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

_REQUEST_OBJECTS_PER_ROOT = 63
_REQUEST_SCOPE_RUNS_DEFAULT = 10
_WORKER_A_OBJECTS_PER_ROOT = 25
_WORKER_B_OBJECTS_PER_ROOT = 20
# Objects built INSIDE the request phase of one cycle (variant 0): the whole-cycle
# minimum minus the outer-scope objects (session + its transient helper chain).
# request: 63 - (RequestSession, Layer4..Layer1, BootstrapAObject) = 57
# worker_a: 25 - (WorkerASession, BootstrapBObject) = 23
# worker_b: 20 - (WorkerBSession, BootstrapCObject) = 18
_REQUEST_INNER_OBJECTS_PER_ROOT = 57
_WORKER_A_INNER_OBJECTS_PER_ROOT = 23
_WORKER_B_INNER_OBJECTS_PER_ROOT = 18
_WORKER_A_JOBS_DEFAULT = 25
_WORKER_B_JOBS_DEFAULT = 30
_BOOTSTRAP_FANOUT_PER_SINGLETON = 5
_VARIANT_COUNT = 3
_LIB_SEEDS = {
    "dishka": 220_007,
    "melder": 330_011,
    "dependency-injector": 110_003,
}


@dataclass(frozen=True)
class _GauntletConfig:
    """Scalar workload settings for one measured process.

    The pytest wrapper selects each thread count from the editable relay.
    Environment inputs support CI and existing single-count tools; ordinary
    pytest use needs only the configuration block at the top of this file.
    """
    iterations: int
    threads: int
    request_scope_runs: int
    worker_a_jobs: int
    worker_b_jobs: int

    @staticmethod
    def from_env() -> _GauntletConfig:
        """Read optional overrides over file defaults and reject empty workloads.

        Counts must be positive; each request workload still creates at least
        500 objects. Conversion errors and invalid counts propagate before
        a library container or worker thread is created.
        """
        cfg = _GauntletConfig(
            iterations=_env_int("DI_GAUNTLET_ITERS", _gauntlet_iteration_counts()[0]),
            threads=_env_int("DI_GAUNTLET_THREADS", 3),
            request_scope_runs=_env_int("DI_GAUNTLET_REQUEST_SCOPES", _REQUEST_SCOPE_RUNS_DEFAULT),
            worker_a_jobs=_env_int("DI_GAUNTLET_WORKER_A_JOBS", _WORKER_A_JOBS_DEFAULT),
            worker_b_jobs=_env_int("DI_GAUNTLET_WORKER_B_JOBS", _WORKER_B_JOBS_DEFAULT),
        )
        if cfg.iterations <= 0:
            raise AssertionError("DI_GAUNTLET_ITERS must be > 0")
        if cfg.threads <= 0:
            raise AssertionError("DI_GAUNTLET_THREADS must be > 0")
        if cfg.request_scope_runs <= 0:
            raise AssertionError("DI_GAUNTLET_REQUEST_SCOPES must be > 0")
        if cfg.worker_a_jobs <= 0:
            raise AssertionError("DI_GAUNTLET_WORKER_A_JOBS must be > 0")
        if cfg.worker_b_jobs <= 0:
            raise AssertionError("DI_GAUNTLET_WORKER_B_JOBS must be > 0")
        if cfg.request_scope_runs * _REQUEST_OBJECTS_PER_ROOT < 500:
            raise AssertionError("Request spellspace must create at least 500 objects total")
        return cfg


@dataclass(frozen=True)
class _RuntimeOps:
    name: str
    spawn_singletons: Callable[[], None]
    bootstrap_fanout: Callable[[], None]
    request_scope_cycle: Callable[[int], _ScopeCycleMetrics]
    worker_a_scope_cycle: Callable[[int], _ScopeCycleMetrics]
    worker_b_scope_cycle: Callable[[int], _ScopeCycleMetrics]
    cleanup: Callable[[], None]
    # Untimed: resolve the request lane's objects through two outer scopes and
    # two requests so `verify_scope_semantics` can check identities. Never
    # called from a timed path.
    probe_scopes: Callable[[], dict[str, Any]] | None = None
    # False when the adapter has no scope teardown to time: its cleanup
    # fields are zero because nothing is measured there, not because
    # teardown is free (dependency-injector leaves scope garbage to the GC).
    cleanup_timed: bool = True


@dataclass(frozen=True)
class _Summary:
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
class _ScopeCycleMetrics:
    outer_create_ns: int
    outer_cleanup_ns: int
    outer_total_ns: int
    request_create_ns: int
    request_cleanup_ns: int
    request_total_ns: int


@dataclass
class _LaneMetricSamples:
    """
    Per-lane scope-cycle timings in nanoseconds, one entry per cycle.

    Two storage kinds share this shape, and the split is deliberate:

    - One iteration's samples are plain lists (`_new_lane_metric_samples`). The
      short-lived worker threads append to them; list appends stay safe when
      several workers share a lane, and the lists die with the iteration.
    - The run-long accumulation is packed `array("q")` storage
      (`_new_lane_metric_storage`), extended on the main thread. It holds values, not int
      objects. Keeping the workers' int objects for the whole leg (the former
      list storage) retained objects allocated by threads that had exited, and
      on free-threaded CPython 3.14 that made every later scope cycle
      progressively more expensive: 2-2.5x slower over 40k iterations for
      Melder and dishka alike, with zero garbage collections. The attribution
      test in test_melder_long_run_retention.py reproduces it.

    Values, ordering and every summary computed from them are unchanged.
    """

    outer_create_ns: MutableSequence[int]
    outer_cleanup_ns: MutableSequence[int]
    outer_total_ns: MutableSequence[int]
    request_create_ns: MutableSequence[int]
    request_cleanup_ns: MutableSequence[int]
    request_total_ns: MutableSequence[int]


@dataclass(frozen=True)
class _LaneSummary:
    name: str
    cycles: int
    objects_min: int
    wall_cycles_per_s: float
    wall_objects_per_s_min: float
    active_cycles_per_s: float
    active_objects_per_s_min: float
    variant_counts: tuple[int, ...]
    outer_create_summary: _Summary
    outer_cleanup_summary: _Summary
    outer_total_summary: _Summary
    request_create_summary: _Summary
    request_cleanup_summary: _Summary
    request_total_summary: _Summary


@dataclass
class _IterationResult:
    total_ns: int
    bootstrap_ns: int
    threaded_ns: int
    lane_metrics: dict[str, _LaneMetricSamples]
    lane_variant_counts: dict[str, list[int]]


@dataclass(frozen=True)
class _BenchmarkResult:
    lib: str
    cfg: _GauntletConfig
    gil_status: str
    setup_singletons: int
    request_objects_min: int
    hot_objects_per_iter_min: int
    setup_ns: int
    cleanup_ns: int
    iteration_summary: _Summary
    bootstrap_summary: _Summary
    threaded_summary: _Summary
    total_hot_scopes: int
    hot_scope_cycles_per_s: float
    hot_objects_per_s_min: float
    outer_scope_create_summary: _Summary
    outer_scope_cleanup_summary: _Summary
    outer_scope_total_summary: _Summary
    request_scope_create_summary: _Summary
    request_scope_cleanup_summary: _Summary
    request_scope_total_summary: _Summary
    lane_summaries: dict[str, _LaneSummary]
    # Every-turn rows for CSV export: (turn, total_ns, bootstrap_ns,
    # threaded_ns, gc_during, gen0_live). Empty unless GAUNTLET_PER_TURN_CSV.
    per_turn_rows: tuple = ()


def _build_runtime_dependency_injector() -> _RuntimeOps:
    pytest.importorskip("dependency_injector")
    from dependency_injector import providers

    singleton_types = set(_SINGLETON_TYPES)
    outer_scoped_types = set(_OUTER_SCOPED_TYPES)
    request_scoped_types = set(_REQUEST_SCOPED_TYPES)
    providers_by_type: dict[type, Any] = {}

    for cls in _ALL_CLASSES:
        param_specs = _ctor_param_types(cls)
        kwargs: dict[str, Any] = {}
        for pname, ptype in param_specs:
            dep = providers_by_type.get(ptype)
            if dep is None:
                raise AssertionError(f"DI wiring error: {cls.__name__} depends on {ptype.__name__} before registration")
            kwargs[pname] = dep

        if cls in singleton_types:
            prov = providers.Singleton(cls, **kwargs)
        elif cls in outer_scoped_types or cls in request_scoped_types:
            prov = providers.ContextLocalSingleton(cls, **kwargs)
        else:
            prov = providers.Factory(cls, **kwargs)
        providers_by_type[cls] = prov

    def _get(cls: type) -> Any:
        return providers_by_type[cls]()

    def spawn_singletons() -> None:
        for cls in _SINGLETON_TYPES:
            left = _get(cls)
            right = _get(cls)
            if not isinstance(left, cls):
                raise AssertionError("Dependency Injector: singleton resolve returned wrong type")
            if left is not right:
                raise AssertionError("Dependency Injector: singleton is not cached")

    def bootstrap_fanout() -> None:
        for cls in _BOOTSTRAP_TYPES:
            for _ in range(_BOOTSTRAP_FANOUT_PER_SINGLETON):
                obj = _get(cls)
                if not isinstance(obj, cls):
                    raise AssertionError("Dependency Injector: bootstrap resolve returned wrong type")

    def _run_in_two_context_scopes(
            *,
            outer_cls: type,
            request_marker_cls: type,
            variant_call: Callable[[], None],
            variant_error_prefix: str,
    ) -> _ScopeCycleMetrics:
        outer_total_t0 = time.perf_counter_ns()
        outer_create_t0 = time.perf_counter_ns()
        outer_ctx = contextvars.Context()
        outer_create_ns = time.perf_counter_ns() - outer_create_t0

        request_metrics: dict[str, int] = {
            "request_create_ns": 0,
            "request_cleanup_ns": 0,
            "request_total_ns": 0,
        }

        def outer_run() -> None:
            outer1 = _get(outer_cls)
            outer2 = _get(outer_cls)
            if not isinstance(outer1, outer_cls):
                raise AssertionError(f"Dependency Injector: {variant_error_prefix} outer resolve returned wrong type")
            if outer1 is not outer2:
                raise AssertionError(f"Dependency Injector: {variant_error_prefix} outer scope object not cached")

            request_total_t0 = time.perf_counter_ns()
            request_create_t0 = time.perf_counter_ns()
            request_ctx = contextvars.copy_context()
            request_metrics["request_create_ns"] = time.perf_counter_ns() - request_create_t0

            def request_run() -> None:
                marker1 = _get(request_marker_cls)
                marker2 = _get(request_marker_cls)
                if not isinstance(marker1, request_marker_cls):
                    raise AssertionError(f"Dependency Injector: {variant_error_prefix} request marker wrong type")
                if marker1 is not marker2:
                    raise AssertionError(f"Dependency Injector: {variant_error_prefix} request scope marker not cached")
                inherited = _get(outer_cls)
                if inherited is not outer1:
                    raise AssertionError(f"Dependency Injector: {variant_error_prefix} outer scope did not propagate into request")
                variant_call()

            request_ctx.run(request_run)
            request_metrics["request_total_ns"] = time.perf_counter_ns() - request_total_t0

        outer_ctx.run(outer_run)
        outer_total_ns = time.perf_counter_ns() - outer_total_t0
        return _ScopeCycleMetrics(
            outer_create_ns=outer_create_ns,
            outer_cleanup_ns=0,
            outer_total_ns=outer_total_ns,
            request_create_ns=request_metrics["request_create_ns"],
            request_cleanup_ns=request_metrics["request_cleanup_ns"],
            request_total_ns=request_metrics["request_total_ns"],
        )

    def request_scope_cycle(variant: int) -> _ScopeCycleMetrics:
        def variant_call() -> None:
            if variant == 0:
                root = _get(RequestRoot)
                if not isinstance(root, RequestRoot):
                    raise AssertionError("Dependency Injector: request root resolve returned wrong type")
            elif variant == 1:
                group = _get(RequestGroup)
                root = _get(RequestRoot)
                if not isinstance(group, RequestGroup) or not isinstance(root, RequestRoot):
                    raise AssertionError("Dependency Injector: request scope variant returned wrong type")
            else:
                root1 = _get(RequestRoot)
                root2 = _get(RequestRoot)
                if not isinstance(root1, RequestRoot) or not isinstance(root2, RequestRoot):
                    raise AssertionError("Dependency Injector: request scope variant returned wrong type")
                if root1 is not root2:
                    raise AssertionError("Dependency Injector: request-scoped root not cached within the request")

        return _run_in_two_context_scopes(
            outer_cls=RequestSession,
            request_marker_cls=RequestScopeMarker,
            variant_call=variant_call,
            variant_error_prefix="request lane",
        )

    def worker_a_scope_cycle(variant: int) -> _ScopeCycleMetrics:
        def variant_call() -> None:
            if variant == 0:
                root = _get(WorkerAJobRoot)
                if not isinstance(root, WorkerAJobRoot):
                    raise AssertionError("Dependency Injector: worker A resolve returned wrong type")
            elif variant == 1:
                group = _get(WorkerAGroup)
                root = _get(WorkerAJobRoot)
                if not isinstance(group, WorkerAGroup) or not isinstance(root, WorkerAJobRoot):
                    raise AssertionError("Dependency Injector: worker A scope variant returned wrong type")
            else:
                root1 = _get(WorkerAJobRoot)
                root2 = _get(WorkerAJobRoot)
                if not isinstance(root1, WorkerAJobRoot) or not isinstance(root2, WorkerAJobRoot):
                    raise AssertionError("Dependency Injector: worker A scope variant returned wrong type")
                if root1 is not root2:
                    raise AssertionError("Dependency Injector: worker A root not cached within the request")

        return _run_in_two_context_scopes(
            outer_cls=WorkerASession,
            request_marker_cls=WorkerAScopeMarker,
            variant_call=variant_call,
            variant_error_prefix="worker A lane",
        )

    def worker_b_scope_cycle(variant: int) -> _ScopeCycleMetrics:
        def variant_call() -> None:
            if variant == 0:
                root = _get(WorkerBJobRoot)
                if not isinstance(root, WorkerBJobRoot):
                    raise AssertionError("Dependency Injector: worker B resolve returned wrong type")
            elif variant == 1:
                group = _get(WorkerBGroup)
                root = _get(WorkerBJobRoot)
                if not isinstance(group, WorkerBGroup) or not isinstance(root, WorkerBJobRoot):
                    raise AssertionError("Dependency Injector: worker B scope variant returned wrong type")
            else:
                root1 = _get(WorkerBJobRoot)
                root2 = _get(WorkerBJobRoot)
                if not isinstance(root1, WorkerBJobRoot) or not isinstance(root2, WorkerBJobRoot):
                    raise AssertionError("Dependency Injector: worker B scope variant returned wrong type")
                if root1 is not root2:
                    raise AssertionError("Dependency Injector: worker B root not cached within the request")

        return _run_in_two_context_scopes(
            outer_cls=WorkerBSession,
            request_marker_cls=WorkerBScopeMarker,
            variant_call=variant_call,
            variant_error_prefix="worker B lane",
        )

    def cleanup() -> None:
        for prov in providers_by_type.values():
            reset = getattr(prov, "reset", None)
            if reset is not None:
                reset()
        gc.collect()

    def probe_scopes() -> dict[str, Any]:
        probe: dict[str, Any] = {"shared": _get(AppSingletonE)}

        def outer_run(tag: str) -> None:
            probe[f"session_{tag}"] = _get(RequestSession)
            probe[f"session_{tag}_again"] = _get(RequestSession)

            def request_run() -> None:
                probe[f"root_{tag}"] = _get(RequestRoot)
                probe[f"root_{tag}_again"] = _get(RequestRoot)
                probe[f"marker_{tag}"] = _get(RequestScopeMarker)
                probe[f"group_{tag}"] = _get(RequestGroup)

            def request_run_2() -> None:
                probe[f"root_{tag}_request2"] = _get(RequestRoot)

            contextvars.copy_context().run(request_run)
            contextvars.copy_context().run(request_run_2)

        for tag in ("a", "b"):
            contextvars.Context().run(outer_run, tag)
        return probe

    return _RuntimeOps(
        name="dependency-injector",
        spawn_singletons=spawn_singletons,
        bootstrap_fanout=bootstrap_fanout,
        request_scope_cycle=request_scope_cycle,
        worker_a_scope_cycle=worker_a_scope_cycle,
        worker_b_scope_cycle=worker_b_scope_cycle,
        cleanup=cleanup,
        probe_scopes=probe_scopes,
        cleanup_timed=False,
    )


def _build_runtime_dishka() -> _RuntimeOps:
    pytest.importorskip("dishka")
    from dishka import Provider, Scope, make_container

    singleton_types = set(_SINGLETON_TYPES)
    outer_scoped_types = set(_OUTER_SCOPED_TYPES)
    request_scoped_types = set(_REQUEST_SCOPED_TYPES)
    request_scope_transients = set(_REQUEST_SCOPE_TRANSIENT_TYPES)

    # GAUNTLET_DISHKA_LAYER_SCOPE selects where the transient Layer1-4Scope
    # helpers live (they stay `cache=False`, the `Existence.many` equivalent):
    #   app     - original mapping: Scope.APP, resolved through the root
    #             container (and therefore under its lock) from every session;
    #   session - Scope.SESSION, constructed inside the session container that
    #             uses them. Bootstrap objects stay at Scope.APP either way
    #             because `bootstrap_fanout` resolves them from the root.
    layer_scope_name = _dishka_layer_scope_name()
    layer_scope = Scope.SESSION if layer_scope_name == "session" else Scope.APP
    layer_types = {Layer1Scope, Layer2Scope, Layer3Scope, Layer4Scope}

    provider = Provider()
    for cls in _ALL_CLASSES:
        if cls in singleton_types:
            provider.provide(cls, scope=Scope.APP, cache=True)
        elif cls in outer_scoped_types:
            provider.provide(cls, scope=Scope.SESSION, cache=True)
        elif cls in request_scoped_types:
            provider.provide(cls, scope=Scope.REQUEST, cache=True)
        elif cls in request_scope_transients:
            provider.provide(cls, scope=Scope.REQUEST, cache=False)
        elif cls in layer_types:
            provider.provide(cls, scope=layer_scope, cache=False)
        else:
            provider.provide(cls, scope=Scope.APP, cache=False)

    container = make_container(provider)

    def spawn_singletons() -> None:
        for cls in _SINGLETON_TYPES:
            left = container.get(cls)
            right = container.get(cls)
            if not isinstance(left, cls):
                raise AssertionError("Dishka: singleton resolve returned wrong type")
            if left is not right:
                raise AssertionError("Dishka: singleton is not cached")

    def bootstrap_fanout() -> None:
        for cls in _BOOTSTRAP_TYPES:
            for _ in range(_BOOTSTRAP_FANOUT_PER_SINGLETON):
                obj = container.get(cls)
                if not isinstance(obj, cls):
                    raise AssertionError("Dishka: bootstrap resolve returned wrong type")

    def _run_in_session_and_request_scopes(
            *,
            outer_cls: type,
            request_marker_cls: type,
            variant_call: Callable[[Any], None],
            variant_error_prefix: str,
    ) -> _ScopeCycleMetrics:
        outer_total_t0 = time.perf_counter_ns()
        outer_create_t0 = time.perf_counter_ns()
        outer_cm = container(scope=Scope.SESSION)
        outer_container = outer_cm.__enter__()
        outer_create_ns = time.perf_counter_ns() - outer_create_t0
        try:
            outer1 = outer_container.get(outer_cls)
            outer2 = outer_container.get(outer_cls)
            if not isinstance(outer1, outer_cls):
                raise AssertionError(f"Dishka: {variant_error_prefix} outer resolve returned wrong type")
            if outer1 is not outer2:
                raise AssertionError(f"Dishka: {variant_error_prefix} outer scope object not cached")

            request_total_t0 = time.perf_counter_ns()
            request_create_t0 = time.perf_counter_ns()
            request_cm = outer_container(scope=Scope.REQUEST)
            request_container = request_cm.__enter__()
            request_create_ns = time.perf_counter_ns() - request_create_t0
            try:
                marker1 = request_container.get(request_marker_cls)
                marker2 = request_container.get(request_marker_cls)
                if not isinstance(marker1, request_marker_cls):
                    raise AssertionError(f"Dishka: {variant_error_prefix} request marker wrong type")
                if marker1 is not marker2:
                    raise AssertionError(f"Dishka: {variant_error_prefix} request scope marker not cached")
                inherited = request_container.get(outer_cls)
                if inherited is not outer1:
                    raise AssertionError(f"Dishka: {variant_error_prefix} outer scope did not propagate into request")
                variant_call(request_container)
            finally:
                request_cleanup_t0 = time.perf_counter_ns()
                request_cm.__exit__(None, None, None)
                request_cleanup_ns = time.perf_counter_ns() - request_cleanup_t0
            request_total_ns = time.perf_counter_ns() - request_total_t0
        finally:
            outer_cleanup_t0 = time.perf_counter_ns()
            outer_cm.__exit__(None, None, None)
            outer_cleanup_ns = time.perf_counter_ns() - outer_cleanup_t0

        return _ScopeCycleMetrics(
            outer_create_ns=outer_create_ns,
            outer_cleanup_ns=outer_cleanup_ns,
            outer_total_ns=time.perf_counter_ns() - outer_total_t0,
            request_create_ns=request_create_ns,
            request_cleanup_ns=request_cleanup_ns,
            request_total_ns=request_total_ns,
        )

    def request_scope_cycle(variant: int) -> _ScopeCycleMetrics:
        def variant_call(request_container: Any) -> None:
            if variant == 0:
                root = request_container.get(RequestRoot)
                if not isinstance(root, RequestRoot):
                    raise AssertionError("Dishka: request root resolve returned wrong type")
            elif variant == 1:
                group = request_container.get(RequestGroup)
                root = request_container.get(RequestRoot)
                if not isinstance(group, RequestGroup) or not isinstance(root, RequestRoot):
                    raise AssertionError("Dishka: request scope variant returned wrong type")
            else:
                root1 = request_container.get(RequestRoot)
                root2 = request_container.get(RequestRoot)
                if not isinstance(root1, RequestRoot) or not isinstance(root2, RequestRoot):
                    raise AssertionError("Dishka: request scope variant returned wrong type")
                if root1 is not root2:
                    raise AssertionError("Dishka: request scope root not cached within the request")

        return _run_in_session_and_request_scopes(
            outer_cls=RequestSession,
            request_marker_cls=RequestScopeMarker,
            variant_call=variant_call,
            variant_error_prefix="request lane",
        )

    def worker_a_scope_cycle(variant: int) -> _ScopeCycleMetrics:
        def variant_call(request_container: Any) -> None:
            if variant == 0:
                root = request_container.get(WorkerAJobRoot)
                if not isinstance(root, WorkerAJobRoot):
                    raise AssertionError("Dishka: worker A resolve returned wrong type")
            elif variant == 1:
                group = request_container.get(WorkerAGroup)
                root = request_container.get(WorkerAJobRoot)
                if not isinstance(group, WorkerAGroup) or not isinstance(root, WorkerAJobRoot):
                    raise AssertionError("Dishka: worker A scope variant returned wrong type")
            else:
                root1 = request_container.get(WorkerAJobRoot)
                root2 = request_container.get(WorkerAJobRoot)
                if not isinstance(root1, WorkerAJobRoot) or not isinstance(root2, WorkerAJobRoot):
                    raise AssertionError("Dishka: worker A scope variant returned wrong type")
                if root1 is not root2:
                    raise AssertionError("Dishka: worker A scope root not cached within the request")

        return _run_in_session_and_request_scopes(
            outer_cls=WorkerASession,
            request_marker_cls=WorkerAScopeMarker,
            variant_call=variant_call,
            variant_error_prefix="worker A lane",
        )

    def worker_b_scope_cycle(variant: int) -> _ScopeCycleMetrics:
        def variant_call(request_container: Any) -> None:
            if variant == 0:
                root = request_container.get(WorkerBJobRoot)
                if not isinstance(root, WorkerBJobRoot):
                    raise AssertionError("Dishka: worker B resolve returned wrong type")
            elif variant == 1:
                group = request_container.get(WorkerBGroup)
                root = request_container.get(WorkerBJobRoot)
                if not isinstance(group, WorkerBGroup) or not isinstance(root, WorkerBJobRoot):
                    raise AssertionError("Dishka: worker B scope variant returned wrong type")
            else:
                root1 = request_container.get(WorkerBJobRoot)
                root2 = request_container.get(WorkerBJobRoot)
                if not isinstance(root1, WorkerBJobRoot) or not isinstance(root2, WorkerBJobRoot):
                    raise AssertionError("Dishka: worker B scope variant returned wrong type")
                if root1 is not root2:
                    raise AssertionError("Dishka: worker B scope root not cached within the request")

        return _run_in_session_and_request_scopes(
            outer_cls=WorkerBSession,
            request_marker_cls=WorkerBScopeMarker,
            variant_call=variant_call,
            variant_error_prefix="worker B lane",
        )

    def cleanup() -> None:
        container.close()
        gc.collect()

    def probe_scopes() -> dict[str, Any]:
        probe: dict[str, Any] = {"shared": container.get(AppSingletonE)}
        for tag in ("a", "b"):
            with container(scope=Scope.SESSION) as outer_container:
                probe[f"session_{tag}"] = outer_container.get(RequestSession)
                probe[f"session_{tag}_again"] = outer_container.get(RequestSession)
                with outer_container(scope=Scope.REQUEST) as request_container:
                    probe[f"root_{tag}"] = request_container.get(RequestRoot)
                    probe[f"root_{tag}_again"] = request_container.get(RequestRoot)
                    probe[f"marker_{tag}"] = request_container.get(RequestScopeMarker)
                    probe[f"group_{tag}"] = request_container.get(RequestGroup)
                with outer_container(scope=Scope.REQUEST) as request_container:
                    probe[f"root_{tag}_request2"] = request_container.get(RequestRoot)
        return probe

    return _RuntimeOps(
        name="dishka",
        spawn_singletons=spawn_singletons,
        bootstrap_fanout=bootstrap_fanout,
        request_scope_cycle=request_scope_cycle,
        worker_a_scope_cycle=worker_a_scope_cycle,
        worker_b_scope_cycle=worker_b_scope_cycle,
        cleanup=cleanup,
        probe_scopes=probe_scopes,
    )


def _build_runtime_melder() -> _RuntimeOps:
    """
    Build the shared gauntlet's Melder lane over this module's class graph.

    Contract:
        - Uses the same classes as the dependency-injector and dishka lanes in
          this module, so all three libraries resolve the identical graph.
        - Setup MUST stay identical to the Melder-only gauntlet
          (`test_melder_gauntlet._build_runtime_melder`): same frame and conduit
          names, one phase-scheduler worker, no frame-posture overrides, the
          same existence per class, `permissions="create"`, `dynamic=False`.
          The two builders are separate code on purpose - tuning the
          Melder-only benchmark cannot change this shared comparison - and
          `test_gauntlet_melder_lane_parity.py` fails if their setup diverges.
        - Resets the Aether singleton before building and again in cleanup.

    Returns:
        _RuntimeOps: The Melder lane callables for `_run_gauntlet_once`.
    """
    from melder.aether.aether import Aether
    from melder.aether.conduit.conduit import Conduit
    from melder.aether.spellbook.existence.existence import Existence
    from melder.aether.spellbook.spellbook import Spellbook

    singleton_types = set(_SINGLETON_TYPES)
    outer_scoped_types = set(_OUTER_SCOPED_TYPES)
    request_scoped_types = set(_REQUEST_SCOPED_TYPES)

    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether

    spellbook = Spellbook(aetheric_frame="real-world-gauntlet")
    cfg = spellbook.get_configuration()
    # Matches the Melder-only gauntlet exactly: one phase-scheduler worker and no
    # frame-posture overrides (system caching is already on by frame default).
    # This builder previously called configure_aether_frame(...) first, which
    # freezes the configuration, so the set_property below raised and the shared
    # gauntlet had been borrowing the Melder-only builder instead.
    cfg.set_property("phase_scheduler_workers_per_spellbook", 1)

    spell_ids: dict[type, str] = {}
    for cls in _ALL_CLASSES:
        if cls in singleton_types:
            existence = Existence.unique
        elif cls in outer_scoped_types:
            existence = Existence.unique_per_conduit
        elif cls in request_scoped_types:
            existence = Existence.unique_per_spell_space
        else:
            existence = Existence.many
        spell_ids[cls] = spellbook.bind(spell=cls, existence=existence, permissions="create")

    conduit = spellbook.conjure(name="real-world-gauntlet", dynamic=False)

    def _get(cls: type) -> Any:
        root = conduit.meld(spell_id=spell_ids[cls])
        if not isinstance(root, cls):
            raise AssertionError("Melder: resolve returned wrong type")
        return root

    def spawn_singletons() -> None:
        for cls in _SINGLETON_TYPES:
            left = _get(cls)
            right = _get(cls)
            if left is not right:
                raise AssertionError("Melder: singleton is not cached")

    def bootstrap_fanout() -> None:
        for cls in _BOOTSTRAP_TYPES:
            for _ in range(_BOOTSTRAP_FANOUT_PER_SINGLETON):
                _get(cls)

    def _run_in_lesser_and_spellspace(
            *,
            outer_cls: type,
            request_marker_cls: type,
            variant_call: Callable[[Any], None],
            variant_error_prefix: str,
    ) -> _ScopeCycleMetrics:
        outer_total_t0 = time.perf_counter_ns()
        outer_create_t0 = time.perf_counter_ns()
        lesser = conduit.create_lesser_conduit()
        outer_create_ns = time.perf_counter_ns() - outer_create_t0
        try:
            outer1 = lesser.meld(spell_id=spell_ids[outer_cls])
            outer2 = lesser.meld(spell_id=spell_ids[outer_cls])
            if not isinstance(outer1, outer_cls):
                raise AssertionError(f"Melder: {variant_error_prefix} outer resolve returned wrong type")
            if outer1 is not outer2:
                raise AssertionError(f"Melder: {variant_error_prefix} outer scope object not cached")

            request_total_t0 = time.perf_counter_ns()
            request_create_t0 = time.perf_counter_ns()
            request_cm = lesser.enter_spellspace()
            space = request_cm.__enter__()
            request_create_ns = time.perf_counter_ns() - request_create_t0
            try:
                marker1 = space.meld(spell_id=spell_ids[request_marker_cls])
                marker2 = space.meld(spell_id=spell_ids[request_marker_cls])
                if not isinstance(marker1, request_marker_cls):
                    raise AssertionError(f"Melder: {variant_error_prefix} request marker wrong type")
                if marker1 is not marker2:
                    raise AssertionError(f"Melder: {variant_error_prefix} request scope marker not cached")
                inherited = space.meld(spell_id=spell_ids[outer_cls])
                if inherited is not outer1:
                    raise AssertionError(f"Melder: {variant_error_prefix} outer scope did not propagate into request")
                variant_call(space)
            finally:
                request_cleanup_t0 = time.perf_counter_ns()
                request_cm.__exit__(None, None, None)
                request_cleanup_ns = time.perf_counter_ns() - request_cleanup_t0
            request_total_ns = time.perf_counter_ns() - request_total_t0
        finally:
            outer_cleanup_t0 = time.perf_counter_ns()
            lesser.cleanup()
            outer_cleanup_ns = time.perf_counter_ns() - outer_cleanup_t0

        return _ScopeCycleMetrics(
            outer_create_ns=outer_create_ns,
            outer_cleanup_ns=outer_cleanup_ns,
            outer_total_ns=time.perf_counter_ns() - outer_total_t0,
            request_create_ns=request_create_ns,
            request_cleanup_ns=request_cleanup_ns,
            request_total_ns=request_total_ns,
        )

    def request_scope_cycle(variant: int) -> _ScopeCycleMetrics:
        def variant_call(space: Any) -> None:
            if variant == 0:
                root = space.meld(spell_id=spell_ids[RequestRoot])
                if not isinstance(root, RequestRoot):
                    raise AssertionError("Melder: request root resolve returned wrong type")
            elif variant == 1:
                group = space.meld(spell_id=spell_ids[RequestGroup])
                root = space.meld(spell_id=spell_ids[RequestRoot])
                if not isinstance(group, RequestGroup) or not isinstance(root, RequestRoot):
                    raise AssertionError("Melder: request scope variant returned wrong type")
            else:
                root1 = space.meld(spell_id=spell_ids[RequestRoot])
                root2 = space.meld(spell_id=spell_ids[RequestRoot])
                if not isinstance(root1, RequestRoot) or not isinstance(root2, RequestRoot):
                    raise AssertionError("Melder: request scope variant returned wrong type")
                if root1 is not root2:
                    raise AssertionError("Melder: request scope root not cached within the request")

        return _run_in_lesser_and_spellspace(
            outer_cls=RequestSession,
            request_marker_cls=RequestScopeMarker,
            variant_call=variant_call,
            variant_error_prefix="request lane",
        )

    def worker_a_scope_cycle(variant: int) -> _ScopeCycleMetrics:
        def variant_call(space: Any) -> None:
            if variant == 0:
                root = space.meld(spell_id=spell_ids[WorkerAJobRoot])
                if not isinstance(root, WorkerAJobRoot):
                    raise AssertionError("Melder: worker A resolve returned wrong type")
            elif variant == 1:
                group = space.meld(spell_id=spell_ids[WorkerAGroup])
                root = space.meld(spell_id=spell_ids[WorkerAJobRoot])
                if not isinstance(group, WorkerAGroup) or not isinstance(root, WorkerAJobRoot):
                    raise AssertionError("Melder: worker A scope variant returned wrong type")
            else:
                root1 = space.meld(spell_id=spell_ids[WorkerAJobRoot])
                root2 = space.meld(spell_id=spell_ids[WorkerAJobRoot])
                if not isinstance(root1, WorkerAJobRoot) or not isinstance(root2, WorkerAJobRoot):
                    raise AssertionError("Melder: worker A scope variant returned wrong type")
                if root1 is not root2:
                    raise AssertionError("Melder: worker A scope root not cached within the request")

        return _run_in_lesser_and_spellspace(
            outer_cls=WorkerASession,
            request_marker_cls=WorkerAScopeMarker,
            variant_call=variant_call,
            variant_error_prefix="worker A lane",
        )

    def worker_b_scope_cycle(variant: int) -> _ScopeCycleMetrics:
        def variant_call(space: Any) -> None:
            if variant == 0:
                root = space.meld(spell_id=spell_ids[WorkerBJobRoot])
                if not isinstance(root, WorkerBJobRoot):
                    raise AssertionError("Melder: worker B resolve returned wrong type")
            elif variant == 1:
                group = space.meld(spell_id=spell_ids[WorkerBGroup])
                root = space.meld(spell_id=spell_ids[WorkerBJobRoot])
                if not isinstance(group, WorkerBGroup) or not isinstance(root, WorkerBJobRoot):
                    raise AssertionError("Melder: worker B scope variant returned wrong type")
            else:
                root1 = space.meld(spell_id=spell_ids[WorkerBJobRoot])
                root2 = space.meld(spell_id=spell_ids[WorkerBJobRoot])
                if not isinstance(root1, WorkerBJobRoot) or not isinstance(root2, WorkerBJobRoot):
                    raise AssertionError("Melder: worker B scope variant returned wrong type")
                if root1 is not root2:
                    raise AssertionError("Melder: worker B scope root not cached within the request")

        return _run_in_lesser_and_spellspace(
            outer_cls=WorkerBSession,
            request_marker_cls=WorkerBScopeMarker,
            variant_call=variant_call,
            variant_error_prefix="worker B lane",
        )

    def cleanup() -> None:
        try:
            conduit.cleanup()
        finally:
            Aether._reset_singleton_for_tests()
            aether2 = Aether()
            Spellbook._aether = aether2
            Conduit._aether = aether2
        gc.collect()

    def probe_scopes() -> dict[str, Any]:
        probe: dict[str, Any] = {"shared": _get(AppSingletonE)}
        for tag in ("a", "b"):
            lesser = conduit.create_lesser_conduit()
            try:
                probe[f"session_{tag}"] = lesser.meld(spell_id=spell_ids[RequestSession])
                probe[f"session_{tag}_again"] = lesser.meld(spell_id=spell_ids[RequestSession])
                with lesser.enter_spellspace() as space:
                    probe[f"root_{tag}"] = space.meld(spell_id=spell_ids[RequestRoot])
                    probe[f"root_{tag}_again"] = space.meld(spell_id=spell_ids[RequestRoot])
                    probe[f"marker_{tag}"] = space.meld(spell_id=spell_ids[RequestScopeMarker])
                    probe[f"group_{tag}"] = space.meld(spell_id=spell_ids[RequestGroup])
                with lesser.enter_spellspace() as space:
                    probe[f"root_{tag}_request2"] = space.meld(spell_id=spell_ids[RequestRoot])
            finally:
                lesser.cleanup()
        return probe

    return _RuntimeOps(
        name="melder",
        spawn_singletons=spawn_singletons,
        bootstrap_fanout=bootstrap_fanout,
        request_scope_cycle=request_scope_cycle,
        worker_a_scope_cycle=worker_a_scope_cycle,
        worker_b_scope_cycle=worker_b_scope_cycle,
        cleanup=cleanup,
        probe_scopes=probe_scopes,
    )


def _dishka_layer_scope_name() -> str:
    """
    Read GAUNTLET_DISHKA_LAYER_SCOPE (app|session; default app = the original mapping).
    """
    raw = (os.getenv("GAUNTLET_DISHKA_LAYER_SCOPE") or "app").strip().lower()
    if raw not in {"app", "session"}:
        raise AssertionError(f"GAUNTLET_DISHKA_LAYER_SCOPE must be app or session, got {raw!r}")
    return raw


def _layer_chain(session: Any) -> tuple[Any, ...]:
    """
    Return (Layer4, Layer3, Layer2, Layer1, BootstrapAObject) as reached from a RequestSession.
    """
    layer4 = session.scope
    layer3 = layer4.prior
    layer2 = layer3.prior
    layer1 = layer2.prior
    return layer4, layer3, layer2, layer1, layer1.entry


def verify_scope_semantics(ops: _RuntimeOps) -> int:
    """
    Untimed correctness phase shared by every library: prove the adapter delivers the declared lifetimes.

    Checks (request lane, two outer scopes "a"/"b", two requests inside "a"):
        - session objects are cached within an outer scope and distinct across outer scopes;
        - the transient Layer1-4Scope chain and BootstrapAObject are built fresh per session (never cached);
        - request-scoped objects (root, marker) are cached within a request and distinct across requests,
          including a second request inside the same session;
        - app singletons are one object everywhere (root container, sessions, layer branches);
        - dependency identities hold: roots and markers reference their session, every group references the
          session, the five groups and fifty leaves of a root are distinct objects, the extra transient group
          is not one of the root's groups and shares no leaf with it.

    Returns:
        int: number of assertions performed (for the report line).

    Raises:
        AssertionError: naming the library and the failed contract.
    """
    if ops.probe_scopes is None:
        raise AssertionError(f"{ops.name}: adapter has no probe_scopes")
    probe = ops.probe_scopes()
    checks = 0

    def expect(condition: bool, contract: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            raise AssertionError(f"{ops.name}: scope semantics violated - {contract}")

    shared = probe["shared"]
    expect(isinstance(shared, AppSingletonE), "root container resolves AppSingletonE")
    for tag in ("a", "b"):
        session = probe[f"session_{tag}"]
        expect(isinstance(session, RequestSession), f"session_{tag} type")
        expect(session is probe[f"session_{tag}_again"], f"session_{tag} cached within its outer scope")
        expect(session.shared is shared, f"session_{tag}.shared is the app singleton")
        root = probe[f"root_{tag}"]
        expect(root is probe[f"root_{tag}_again"], f"root_{tag} cached within its request")
        expect(root.session is session, f"root_{tag}.session is its session")
        marker = probe[f"marker_{tag}"]
        expect(marker.session is session, f"marker_{tag}.session is its session")
        root2 = probe[f"root_{tag}_request2"]
        expect(root2 is not root, f"root_{tag} differs across two requests of one session")
        expect(root2.session is session, f"root_{tag}_request2 still references the shared session")
        groups = root.groups
        expect(len(groups) == 5 and len({id(group) for group in groups}) == 5, f"root_{tag} has 5 distinct groups")
        leaves = [leaf for group in groups for leaf in group.leaves]
        expect(len(leaves) == 50 and len({id(leaf) for leaf in leaves}) == 50, f"root_{tag} has 50 distinct leaves")
        for group in groups:
            expect(group.session is session, f"root_{tag} groups reference the session")
        extra = probe[f"group_{tag}"]
        expect(extra.session is session, f"group_{tag}.session is its session")
        expect(all(extra is not group for group in groups), f"group_{tag} is not one of the root's groups")
        leaf_ids = {id(leaf) for leaf in leaves}
        expect(all(id(leaf) not in leaf_ids for leaf in extra.leaves), f"group_{tag} shares no leaf with the root")
        layer4, layer3, layer2, layer1, bootstrap = _layer_chain(session)
        expect(isinstance(layer4, Layer4Scope) and isinstance(bootstrap, BootstrapAObject), f"layer chain of session_{tag}")
        expect(layer1.shared is shared, f"Layer1Scope.shared of session_{tag} is the app singleton")
        expect(isinstance(bootstrap.root, AppSingletonA), f"BootstrapAObject.root of session_{tag}")

    expect(probe["session_a"] is not probe["session_b"], "sessions differ across outer scopes")
    expect(probe["root_a"] is not probe["root_b"], "roots differ across outer scopes")
    chain_a = _layer_chain(probe["session_a"])
    chain_b = _layer_chain(probe["session_b"])
    for index, name in enumerate(("Layer4Scope", "Layer3Scope", "Layer2Scope", "Layer1Scope", "BootstrapAObject")):
        expect(chain_a[index] is not chain_b[index], f"{name} is transient (fresh per session)")
    expect(chain_a[4].root is chain_b[4].root, "AppSingletonA shared through both bootstrap objects")
    expect(chain_a[2].branch is chain_b[2].branch, "AppSingletonB shared through both Layer2Scope branches")
    expect(chain_a[1].branch is chain_b[1].branch, "AppSingletonC shared through both Layer3Scope branches")
    expect(chain_a[0].branch is chain_b[0].branch, "AppSingletonD shared through both Layer4Scope branches")
    return checks


def _gauntlet_libraries() -> tuple[str, ...]:
    """
    Return the libraries the shared gauntlet compares, in their printed order.

    Contract:
        - The order the standalone runner has always used: dependency-injector,
          dishka, melder. Every name is accepted by `_build_ops`.
        - Pure: returns the same constant names on every call.

    Returns:
        tuple[str, ...]: The three library names.
    """
    return ("dependency-injector", "dishka", "melder")


def _gauntlet_rounds() -> int:
    """
    Read how many times the pytest wrapper measures every library.

    Contract:
        - `REAL_WORLD_GAUNTLET_ROUNDS` unset or blank uses the editable default; any other
          value must be a positive integer.
        - Each round runs every library once, each in its own process.

    Returns:
        int: The number of rounds, at least 1.

    Raises:
        AssertionError: When the variable is set to zero or a negative number.
        ValueError: When the variable is not an integer.
    """
    rounds = _env_int("REAL_WORLD_GAUNTLET_ROUNDS", REAL_WORLD_GAUNTLET_ROUNDS)
    if rounds <= 0:
        raise AssertionError("REAL_WORLD_GAUNTLET_ROUNDS must be > 0")
    return rounds


def _isolated_order(round_ix: int) -> tuple[str, ...]:
    """
    Return the library order for one round of the one-process-per-library wrapper.

    Contract:
        - Round 0 is the printed order of `_gauntlet_libraries()`; each later round
          rotates it by one, so over three rounds every library runs once in every
          slot.
        - Every library runs in a fresh process whatever its slot, so the rotation
          does not remove the order effect (the separate processes do); it spreads
          machine drift over a session (heat, background load) across the libraries.

    Args:
        round_ix: Zero-based round index.

    Returns:
        tuple[str, ...]: The three library names in this round's order.

    Raises:
        AssertionError: When `round_ix` is negative.
    """
    if round_ix < 0:
        raise AssertionError("round_ix must be >= 0")
    libraries = _gauntlet_libraries()
    shift = round_ix % len(libraries)
    return libraries[shift:] + libraries[:shift]


def _build_ops(lib: str) -> _RuntimeOps:
    if lib == "dependency-injector":
        return _build_runtime_dependency_injector()
    if lib == "dishka":
        return _build_runtime_dishka()
    if lib == "melder":
        # This module's own Melder lane: isolated from the Melder-only gauntlet,
        # kept equal to it by test_gauntlet_melder_lane_parity.py.
        return _build_runtime_melder()
    raise AssertionError(f"Unknown lib: {lib}")


def _gauntlet_iteration_counts() -> tuple[int, ...]:
    """Select the ordered iteration-count relay from the editable configuration.

    REAL_WORLD_GAUNTLET_ITERATION_COUNTS may also be supplied as comma-separated
    environment input. Without it, DI_GAUNTLET_ITERS selects one count for existing
    profiling tools; otherwise the file's list is used. Counts must be distinct
    positive integers, and a fresh child measures each count/thread/library/round.
    """
    series = os.getenv("REAL_WORLD_GAUNTLET_ITERATION_COUNTS", "").strip()
    single = os.getenv("DI_GAUNTLET_ITERS", "").strip()
    counts = ([int(value.strip()) for value in series.split(",")] if series
              else [int(single)] if single else list(REAL_WORLD_GAUNTLET_ITERATION_COUNTS))
    if not counts or any(type(value) is not int or value <= 0 for value in counts):
        raise ValueError("Gauntlet iteration counts must be a nonempty list of positive integers")
    if len(counts) != len(set(counts)):
        raise ValueError("Gauntlet iteration counts must be distinct; use rounds for repetition")
    return tuple(counts)


def _gauntlet_thread_counts() -> tuple[int, ...]:
    """Select the ordered thread-count relay without changing parent process state.

    Edit REAL_WORLD_GAUNTLET_THREAD_COUNTS for the normal run. An optional
    comma-separated environment variable of the same name overrides that list;
    otherwise DI_GAUNTLET_THREADS selects one count for existing single-run tools.
    Counts must be distinct positive integers. Each library/count/round receives
    a fresh process, and summaries never combine different thread counts.
    """
    series = os.getenv("REAL_WORLD_GAUNTLET_THREAD_COUNTS", "").strip()
    single = os.getenv("DI_GAUNTLET_THREADS", "").strip()
    counts = ([int(value.strip()) for value in series.split(",")] if series
              else [int(single)] if single else list(REAL_WORLD_GAUNTLET_THREAD_COUNTS))
    if not counts or any(type(value) is not int or value <= 0 for value in counts):
        raise ValueError("Gauntlet thread counts must be a nonempty list of positive integers")
    if len(counts) != len(set(counts)):
        raise ValueError("Gauntlet thread counts must be distinct; use rounds for repetition")
    return tuple(counts)


def _lane_layout(cfg: _GauntletConfig) -> tuple[tuple[str, str, int, int], ...]:
    """Describe every thread's name, workload family, cycle count and random seed offset.

    Repeat request, worker A and worker B workloads across positive N threads.
    The first three names remain request, worker_a and worker_b. Later threads
    are worker_c, worker_d and onward through worker_z, worker_aa, etc. Each
    name receives its own counters and samples; no two threads mutate one lane.
    A repeated workload uses that family's configured cycle count and class graph.

    Args:
        cfg: Run configuration with a positive thread count.

    Returns:
        Tuples in launch/report order. Existing 1-3-thread seeds are preserved.

    Raises:
        AssertionError: The requested thread count is not positive.
    """
    if cfg.threads <= 0:
        raise AssertionError("DI_GAUNTLET_THREADS must be > 0")
    patterns = (("request", cfg.request_scope_runs),
                ("worker_a", cfg.worker_a_jobs), ("worker_b", cfg.worker_b_jobs))
    lanes: list[tuple[str, str, int, int]] = []
    for index in range(cfg.threads):
        name = "request"
        if index:
            ordinal = index
            label = ""
            while ordinal:
                ordinal, letter = divmod(ordinal - 1, 26)
                label = chr(ord("a") + letter) + label
            name = f"worker_{label}"
        workload, cycles = patterns[index % len(patterns)]
        lanes.append((name, workload, cycles, 17 + 12 * index))
    return tuple(lanes)


def _require_gil_disabled() -> None:
    """Refuse measurement unless this process is actually running without the GIL.

    The subprocess wrapper selects -X gil=0 and PYTHON_GIL=0 before startup.
    Direct runner/profile invocations must select a free-threaded interpreter
    themselves; changing an environment variable after startup is insufficient.

    Raises:
        RuntimeError: The interpreter reports an enabled or unknown GIL state.
    """
    if _gil_status() != "disabled":
        raise RuntimeError(
            "The real-world gauntlet requires the GIL disabled in the measured process. "
            "Run free-threaded Python with -X gil=0 or PYTHON_GIL=0 before process startup."
        )


def _lane_objects_per_cycle(name: str) -> int:
    if name == "request":
        return _REQUEST_OBJECTS_PER_ROOT
    if name == "worker_a":
        return _WORKER_A_OBJECTS_PER_ROOT
    if name == "worker_b":
        return _WORKER_B_OBJECTS_PER_ROOT
    raise AssertionError(f"Unknown lane: {name}")


def _lane_inner_objects_per_cycle(name: str) -> int:
    """
    Objects built inside the request phase of one cycle (variant 0 minimum); see the constants.
    """
    if name == "request":
        return _REQUEST_INNER_OBJECTS_PER_ROOT
    if name == "worker_a":
        return _WORKER_A_INNER_OBJECTS_PER_ROOT
    if name == "worker_b":
        return _WORKER_B_INNER_OBJECTS_PER_ROOT
    raise AssertionError(f"Unknown lane: {name}")


def _new_lane_metric_samples() -> _LaneMetricSamples:
    return _LaneMetricSamples(
        outer_create_ns=[],
        outer_cleanup_ns=[],
        outer_total_ns=[],
        request_create_ns=[],
        request_cleanup_ns=[],
        request_total_ns=[],
    )


def _new_lane_metric_storage() -> _LaneMetricSamples:
    """
    Return empty run-long sample storage: six signed 64-bit `array("q")`.

    Contract:
        - Used only for accumulation across iterations on the main thread.
        - `extend(...)` copies values out of an iteration's lists, so no int
          object created on a worker thread outlives that iteration. See
          `_LaneMetricSamples` for why this matters on free-threaded CPython.
    """
    return _LaneMetricSamples(
        outer_create_ns=array("q"),
        outer_cleanup_ns=array("q"),
        outer_total_ns=array("q"),
        request_create_ns=array("q"),
        request_cleanup_ns=array("q"),
        request_total_ns=array("q"),
    )


def _variant_counts_tuple(values: list[int]) -> tuple[int, ...]:
    return tuple(values)


def _run_gauntlet_once(ops: _RuntimeOps, cfg: _GauntletConfig, iteration_ix: int) -> _IterationResult:
    """Time one synchronized burst against the already-built library container.

    Bootstrap work runs on the parent, then N fresh threads wait at a readiness
    barrier and start together. Each repeats its assigned workload in independent
    scopes and writes only its own named metrics. The parent joins every thread
    before inspecting counters or propagating a worker error. No work queue or
    producer/consumer handoff exists. Total time includes thread startup and
    joining; threaded time begins after readiness. Container setup and terminal
    cleanup are measured separately by _run_gauntlet_benchmark.
    """
    t0 = time.perf_counter_ns()
    bootstrap_t0 = time.perf_counter_ns()
    ops.bootstrap_fanout()
    bootstrap_ns = time.perf_counter_ns() - bootstrap_t0

    layout = _lane_layout(cfg)
    lane_counts = {name: 0 for name, _, _, _ in layout}
    lane_metrics = {name: _new_lane_metric_samples() for name, _, _, _ in layout}
    lane_variant_counts = {name: [0] * _VARIANT_COUNT for name, _, _, _ in layout}
    errors: list[BaseException] = []
    stop_event = threading.Event()
    scope_cycles = {
        "request": ops.request_scope_cycle,
        "worker_a": ops.worker_a_scope_cycle,
        "worker_b": ops.worker_b_scope_cycle,
    }
    active_lanes = [(name, scope_cycles[workload], reps, offset)
                    for name, workload, reps, offset in layout]

    ready_barrier = threading.Barrier(len(active_lanes) + 1)
    start_event = threading.Event()

    def make_worker(
            name: str,
            call: Callable[[int], _ScopeCycleMetrics],
            reps: int,
            seed_offset: int,
    ) -> Callable[[], None]:
        def worker() -> None:
            try:
                rng = random.Random(_LIB_SEEDS[ops.name] + iteration_ix * 101 + seed_offset)
                ready_barrier.wait()
                start_event.wait()
                for _ in range(reps):
                    if stop_event.is_set():
                        return
                    variant = rng.randrange(_VARIANT_COUNT)
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

    threads_list: list[threading.Thread] = []
    for lane_name, lane_call, reps, seed_offset in active_lanes:
        t = threading.Thread(
            target=make_worker(lane_name, lane_call, reps, seed_offset),
            daemon=True,
        )
        threads_list.append(t)
        t.start()

    ready_barrier.wait()
    threaded_t0 = time.perf_counter_ns()
    start_event.set()

    for t in threads_list:
        t.join()
    threaded_ns = time.perf_counter_ns() - threaded_t0

    if errors:
        raise errors[0]

    for name, _, reps, _ in layout:
        if lane_counts[name] != reps:
            raise AssertionError(f"{name} did not complete expected scope cycles")
    return _IterationResult(
        total_ns=time.perf_counter_ns() - t0,
        bootstrap_ns=bootstrap_ns,
        threaded_ns=threaded_ns,
        lane_metrics=lane_metrics,
        lane_variant_counts=lane_variant_counts,
    )


def _summarize(samples: Sequence[int]) -> _Summary:
    ordered = sorted(samples)
    stdev_ns = statistics.pstdev(samples) if len(samples) > 1 else 0.0
    avg_ns = float(sum(samples)) / float(len(samples))
    return _Summary(
        total_ns=sum(samples),
        avg_ns=avg_ns,
        median_ns=statistics.median(samples),
        p95_ns=_pctl_ns(ordered, 0.95),
        p99_ns=_pctl_ns(ordered, 0.99),
        min_ns=ordered[0],
        max_ns=ordered[-1],
        stdev_ns=stdev_ns,
        cv=(stdev_ns / avg_ns) if avg_ns > 0 else 0.0,
    )


def _format_summary_ms(summary: _Summary) -> str:
    return (
        f"avg={_ms(summary.avg_ns):.3f}ms | "
        f"median={_ms(summary.median_ns):.3f}ms | "
        f"p95={_ms(summary.p95_ns):.3f}ms | "
        f"p99={_ms(summary.p99_ns):.3f}ms | "
        f"min={_ms(summary.min_ns):.3f}ms | "
        f"max={_ms(summary.max_ns):.3f}ms | "
        f"stdev={_ms(summary.stdev_ns):.3f}ms | "
        f"cv={summary.cv:.1%}"
    )


def _summarize_lane(
        *,
        name: str,
        metric_samples: _LaneMetricSamples,
        variant_counts: list[int],
        wall_total_ns: int,
        workload: Optional[str] = None,
) -> _LaneSummary:
    """Summarize one named thread using its repeated workload family for object counts.

    workload defaults to name for the original three lanes. Repeated lanes
    supply their original family; their samples and output names stay separate.
    """
    outer_total_summary = _summarize(metric_samples.outer_total_ns)
    request_total_summary = _summarize(metric_samples.request_total_ns)
    objects_min = len(metric_samples.outer_total_ns) * _lane_objects_per_cycle(
        name if workload is None else workload)
    active_seconds = request_total_summary.total_ns / 1_000_000_000.0 if request_total_summary.total_ns > 0 else 0.0
    wall_seconds = wall_total_ns / 1_000_000_000.0 if wall_total_ns > 0 else 0.0
    return _LaneSummary(
        name=name,
        cycles=len(metric_samples.outer_total_ns),
        objects_min=objects_min,
        wall_cycles_per_s=(len(metric_samples.outer_total_ns) / wall_seconds) if wall_seconds > 0 else 0.0,
        wall_objects_per_s_min=(objects_min / wall_seconds) if wall_seconds > 0 else 0.0,
        active_cycles_per_s=(len(metric_samples.outer_total_ns) / active_seconds) if active_seconds > 0 else 0.0,
        active_objects_per_s_min=(objects_min / active_seconds) if active_seconds > 0 else 0.0,
        variant_counts=_variant_counts_tuple(variant_counts),
        outer_create_summary=_summarize(metric_samples.outer_create_ns),
        outer_cleanup_summary=_summarize(metric_samples.outer_cleanup_ns),
        outer_total_summary=outer_total_summary,
        request_create_summary=_summarize(metric_samples.request_create_ns),
        request_cleanup_summary=_summarize(metric_samples.request_cleanup_ns),
        request_total_summary=request_total_summary,
    )


class _GcPauseProbe:
    """
    Opt-in gc.callbacks recorder for attributing tail-latency spikes to GC.

    Purpose:
        Diagnostic instrument for the churn gauntlet. It records garbage
        collection pause durations during the measured loop so a per-cycle
        max spike can be compared against the largest GC pause and attributed
        to (or cleared of) collection activity.

    Contract:
        - Off unless explicitly installed; installing appends one gc.callbacks
          hook and uninstalling removes it. Both are safe to call once.
        - Aggregates in-callback (counts/sums/max only); it never retains an
          unbounded event list, so a multi-million-cycle run stays bounded.
        - Free-threaded safe: under a no-GIL build the callback fires on the
          thread that triggered the collection, so start timestamps are kept
          per-thread and the merged totals are guarded by a lock.
        - Records pause timing and collected-object counts only; no object
          identity or references are held.

    Threading:
        `_callback` may run concurrently on multiple threads; all shared
        counters are mutated under `self._lock`. `_start_by_thread` is keyed by
        thread id and each key is written and consumed only by its own thread.

    Lifecycle:
        Create -> install() before the measured loop -> uninstall() in a
        finally. No resources require teardown beyond removing the callback.
    """

    def __init__(self) -> None:
        """Initialize empty pause/collection accumulators and the merge lock."""
        self._lock = threading.Lock()
        self._start_by_thread: dict[int, int] = {}
        self.collections_by_gen: dict[int, int] = {}
        self.collected_objects: int = 0
        self.pause_total_ns: int = 0
        self.pause_max_ns: int = 0
        # Flat integer mirror of the total collection count. A single int read is
        # atomic, so a per-iteration "did GC fire this turn" check can poll it
        # without locking or risking a dict-changed-size race against callbacks.
        self.collections_total: int = 0

    def _callback(self, phase: str, info: dict) -> None:
        """
        gc.callbacks hook: time one collection and fold it into the totals.

        Args:
            phase: "start" or "stop" as supplied by the collector.
            info: collector-supplied mapping; "generation" and "collected"
                are read when present.

        Contract:
            On "start" the per-thread start timestamp is recorded; on "stop"
            the elapsed pause is added to the totals and the per-generation
            count. A "stop" with no matching "start" (probe installed
            mid-collection) is ignored.
        """
        thread_id = threading.get_ident()
        if phase == "start":
            self._start_by_thread[thread_id] = time.perf_counter_ns()
            return
        start_ns = self._start_by_thread.pop(thread_id, None)
        if start_ns is None:
            return
        pause_ns = time.perf_counter_ns() - start_ns
        generation = int(info.get("generation", -1))
        collected = int(info.get("collected", 0))
        with self._lock:
            self.collections_by_gen[generation] = (
                self.collections_by_gen.get(generation, 0) + 1
            )
            self.collections_total += 1
            self.collected_objects += collected
            self.pause_total_ns += pause_ns
            self.pause_max_ns = max(self.pause_max_ns, pause_ns)

    def install(self) -> None:
        """Append the pause-recording hook to gc.callbacks."""
        gc.callbacks.append(self._callback)

    def uninstall(self) -> None:
        """Remove the pause-recording hook; a no-op if already absent."""
        if self._callback in gc.callbacks:
            gc.callbacks.remove(self._callback)

    @property
    def collections(self) -> int:
        """Total collections observed across all generations."""
        return sum(self.collections_by_gen.values())

    def summary(self) -> str:
        """Render a one-line per-generation / pause_total / pause_max summary."""
        if not self.collections_by_gen:
            gens = "(none)"
        else:
            gens = "(" + ", ".join(
                f"g{gen}={count}"
                for gen, count in sorted(self.collections_by_gen.items())
            ) + ")"
        return (
            f"collections={self.collections} {gens}, "
            f"collected={self.collected_objects:,}, "
            f"pause_total={_ms(self.pause_total_ns):.3f}ms, "
            f"pause_max={_ms(self.pause_max_ns):.3f}ms"
        )


def _gc_stats_delta_text(before: list, after: list) -> str:
    """
    Render the per-generation collection-count delta from gc.get_stats().

    Args:
        before: per-generation cumulative `collections` counts captured before
            the measured loop (empty when instrumentation is off).
        after: the same counts captured after the loop.

    Returns:
        A one-line `total=+N (g0=+a, g1=+b, g2=+c)` string. These counts are the
        interpreter's own collector tally, independent of the gc.callbacks
        probe, so a reader can confirm the two readings agree (or do not).
    """
    if not before and not after:
        return "n/a"
    pairs = []
    total = 0
    for gen, after_count in enumerate(after):
        before_count = before[gen] if gen < len(before) else 0
        delta = after_count - before_count
        total += delta
        pairs.append(f"g{gen}=+{delta}")
    return f"total=+{total} (" + ", ".join(pairs) + ")"


def _run_gauntlet_benchmark(lib: str, cfg: _GauntletConfig) -> _BenchmarkResult:
    """Measure one library with GIL-off checks before setup, after imports and after the run.

    Build one container, reuse it across synchronized N-thread iterations, and
    retire it in finally. Each repeated workload has independent lane storage;
    throughput and object minima include every configured thread. Existing GC
    instrumentation and its restoration remain local to this library's run.
    """
    _require_gil_disabled()
    layout = _lane_layout(cfg)
    lane_workloads = {name: workload for name, workload, _, _ in layout}
    # Optional, off-by-default GC instrumentation. When enabled it is applied
    # symmetrically to every library so the comparison stays fair; when off,
    # the measured path below is byte-for-byte the original benchmark.
    gc_probe_enabled = os.getenv("GAUNTLET_GC_PROBE", "").strip().lower() in {"1", "true", "yes", "on"}
    gc_mode = os.getenv("GAUNTLET_GC_MODE", "normal").strip().lower()
    # Per-turn GC/heap attribution: capture each iteration's collection
    # incidence and gen0 live count so the actual slow turns can be dissected,
    # instead of inferring a single-iteration spike's cause from whole-run or
    # per-window aggregates.
    per_turn_gc = os.getenv("GAUNTLET_PER_TURN_GC", "").strip().lower() in {"1", "true", "yes", "on"}
    per_turn_slowest = _env_int("GAUNTLET_PER_TURN_SLOWEST", 15)
    # CSV export of every single turn (all libraries into one file). Implies
    # per-turn capture so the gc_during/gen0_live columns are populated.
    per_turn_csv = os.getenv("GAUNTLET_PER_TURN_CSV", "").strip().lower() in {"1", "true", "yes", "on"}
    capture_per_turn = per_turn_gc or per_turn_csv
    gc_probe = _GcPauseProbe() if (gc_probe_enabled or capture_per_turn) else None
    gc_was_enabled = gc.isenabled()
    gc_frozen_here = False
    gc_instrumented = gc_probe is not None or gc_mode != "normal"
    # Per-window time-series sampling. When > 0 the run is split into this many
    # equal windows; at each window boundary GC collection counts and heap
    # pressure are snapshotted DURING the loop, and per-window latency is
    # aggregated after, so degradation across the run is visible instead of
    # being flattened into order-independent whole-run percentiles.
    trend_windows = _env_int("GAUNTLET_TREND_WINDOWS", 0)
    min_request_objects = sum(reps * _REQUEST_OBJECTS_PER_ROOT
                              for _, workload, reps, _ in layout if workload == "request")
    bootstrap_objects = len(_BOOTSTRAP_TYPES) * _BOOTSTRAP_FANOUT_PER_SINGLETON
    hot_objects_per_iter_min = bootstrap_objects + sum(
        reps * _lane_objects_per_cycle(workload) for _, workload, reps, _ in layout)
    setup_singletons = len(_SINGLETON_TYPES)

    setup_t0 = time.perf_counter_ns()
    ops = _build_ops(lib)
    result_payload: dict[str, Any] = {}
    cleanup_ns = 0
    try:
        _require_gil_disabled()
        ops.spawn_singletons()
        setup_ns = time.perf_counter_ns() - setup_t0

        # Apply the requested GC posture around the measured loop only, after
        # setup so the stable singleton/runtime graph is in place before any
        # freeze. State is restored per-library in the finally below so it
        # cannot leak across the three libraries sharing this process.
        if gc_probe is not None:
            gc_probe.install()
        if gc_mode == "disabled":
            gc.disable()
        elif gc_mode == "frozen":
            gc.collect()
            gc.freeze()
            gc_frozen_here = True

        # Callback-free cross-check: snapshot CPython's own per-generation
        # collection counters (gc.get_stats()) around the measured loop. The
        # before/after delta is maintained by the interpreter, not the probe,
        # so comparing it to the probe's gc.callbacks count catches any
        # collection the hook could miss -- including worker-thread collections
        # under a no-GIL build. Two independent readings of zero == GC idle.
        gc_stats_before: list = (
            [int(s.get("collections", 0)) for s in gc.get_stats()]
            if gc_instrumented
            else []
        )

        iteration_samples: list[int] = []
        bootstrap_samples: list[int] = []
        threaded_samples: list[int] = []
        lane_metric_samples = {name: _new_lane_metric_storage() for name, _, _, _ in layout}
        lane_variant_counts = {name: [0] * _VARIANT_COUNT for name, _, _, _ in layout}

        # Time-series state: sample at each window boundary inside the loop so
        # the cause of any drift is captured as it happens, not inferred from
        # endpoints. gc.get_stats()/gc.get_count() are cheap and run once per
        # window (e.g. 10x over 25k iters), so they do not perturb the loop.
        trend_on = trend_windows > 0 and cfg.iterations >= trend_windows
        trend_window_size = (cfg.iterations // trend_windows) if trend_on else 0
        trend_marks: list = []
        trend_coll_base = (
            sum(int(s.get("collections", 0)) for s in gc.get_stats()) if trend_on else 0
        )
        trend_loop_start_ns = time.perf_counter_ns()

        # Per-turn capture: gen0 live count per iteration and the indices of any
        # iterations during which a collection actually fired.
        per_turn_count0: list = []
        per_turn_gc_iters: list = []

        for iteration_ix in range(cfg.iterations):
            coll_before = gc_probe.collections_total if capture_per_turn else 0
            iteration = _run_gauntlet_once(ops, cfg, iteration_ix)
            iteration_samples.append(iteration.total_ns)
            bootstrap_samples.append(iteration.bootstrap_ns)
            threaded_samples.append(iteration.threaded_ns)
            if capture_per_turn:
                if gc_probe.collections_total > coll_before:
                    per_turn_gc_iters.append(iteration_ix)
                per_turn_count0.append(gc.get_count()[0])
            for lane_name, values in iteration.lane_metrics.items():
                lane_metric_samples[lane_name].outer_create_ns.extend(values.outer_create_ns)
                lane_metric_samples[lane_name].outer_cleanup_ns.extend(values.outer_cleanup_ns)
                lane_metric_samples[lane_name].outer_total_ns.extend(values.outer_total_ns)
                lane_metric_samples[lane_name].request_create_ns.extend(values.request_create_ns)
                lane_metric_samples[lane_name].request_cleanup_ns.extend(values.request_cleanup_ns)
                lane_metric_samples[lane_name].request_total_ns.extend(values.request_total_ns)
            for lane_name, counts in iteration.lane_variant_counts.items():
                for i, count in enumerate(counts):
                    lane_variant_counts[lane_name][i] += count
            if (
                trend_on
                and (iteration_ix + 1) % trend_window_size == 0
                and len(trend_marks) < trend_windows
            ):
                trend_marks.append((
                    iteration_ix + 1,
                    sum(int(s.get("collections", 0)) for s in gc.get_stats()),
                    tuple(gc.get_count()),
                    time.perf_counter_ns(),
                ))

        if gc_instrumented:
            gc_stats_after = [int(s.get("collections", 0)) for s in gc.get_stats()]
            stats_delta = _gc_stats_delta_text(gc_stats_before, gc_stats_after)
            probe_txt = gc_probe.summary() if gc_probe is not None else "probe=off"
            print(
                f"[{lib}] gc probe (mode={gc_mode}, gc_enabled={gc.isenabled()}) "
                f"| {probe_txt} | gc.get_stats delta: {stats_delta}"
            )

        if trend_on and trend_marks:
            # Force the final window to cover any remainder iterations.
            trend_marks[-1] = (
                len(iteration_samples),
                trend_marks[-1][1],
                trend_marks[-1][2],
                trend_marks[-1][3],
            )
            print(
                f"[{lib}] trend over run ({len(trend_marks)} windows, "
                f"gc_enabled={gc.isenabled()}):"
            )
            prev_end = 0
            prev_coll = trend_coll_base
            prev_t = trend_loop_start_ns
            for w_ix, (end_ix, coll_total, count_tuple, t_ns) in enumerate(
                trend_marks, start=1
            ):
                window = iteration_samples[prev_end:end_ix]
                thr_window = threaded_samples[prev_end:end_ix]
                if not window:
                    continue
                w = _summarize(window)
                tw = _summarize(thr_window)
                print(
                    f"  w{w_ix:02d} iters {prev_end + 1}-{end_ix} | "
                    f"iter med={_ms(w.median_ns):.3f} p99={_ms(w.p99_ns):.3f} "
                    f"max={_ms(w.max_ns):.3f}ms | "
                    f"thr p99={_ms(tw.p99_ns):.3f} max={_ms(tw.max_ns):.3f}ms | "
                    f"gc_coll=+{coll_total - prev_coll} | live={count_tuple} | "
                    f"wall={_ms(t_ns - prev_t):.1f}ms"
                )
                prev_end = end_ix
                prev_coll = coll_total
                prev_t = t_ns

        if per_turn_gc and iteration_samples:
            n = len(iteration_samples)
            k = min(per_turn_slowest, n)
            gc_iter_set = set(per_turn_gc_iters)
            slow_idx = sorted(
                range(n), key=lambda i: iteration_samples[i], reverse=True
            )[:k]
            slow_idx.sort()  # display in turn (time) order so bursts are visible
            print(
                f"[{lib}] per-turn GC attribution | "
                f"turns_with_collection={len(per_turn_gc_iters)}/{n} | "
                f"slowest {k} turns, time-ordered (turn | total | threaded | gc_during | gen0_live):"
            )
            for i in slow_idx:
                c0 = per_turn_count0[i] if i < len(per_turn_count0) else -1
                during = "YES" if i in gc_iter_set else "no"
                print(
                    f"    turn {i:6d} | total={_ms(iteration_samples[i]):8.3f}ms | "
                    f"thr={_ms(threaded_samples[i]):8.3f}ms | "
                    f"gc_during={during:>3} | gen0_live={c0}"
                )
            if per_turn_count0:
                seg = max(1, n // 10)
                print(
                    f"[{lib}] per-turn heap pressure gen0_live | "
                    f"first10%_avg={statistics.fmean(per_turn_count0[:seg]):.1f} | "
                    f"last10%_avg={statistics.fmean(per_turn_count0[-seg:]):.1f} | "
                    f"min={min(per_turn_count0)} | max={max(per_turn_count0)}"
                )

        per_turn_rows_data: tuple = ()
        if per_turn_csv:
            gc_iter_set_csv = set(per_turn_gc_iters)
            per_turn_rows_data = tuple(
                (
                    i,
                    iteration_samples[i],
                    bootstrap_samples[i],
                    threaded_samples[i],
                    i in gc_iter_set_csv,
                    per_turn_count0[i] if i < len(per_turn_count0) else -1,
                )
                for i in range(len(iteration_samples))
            )

        iteration_summary = _summarize(iteration_samples)
        bootstrap_summary = _summarize(bootstrap_samples)
        threaded_summary = _summarize(threaded_samples)
        lane_summaries: dict[str, _LaneSummary] = {}
        for lane_name, metric_samples in lane_metric_samples.items():
            if not metric_samples.outer_total_ns:
                continue
            lane_summaries[lane_name] = _summarize_lane(
                name=lane_name,
                metric_samples=metric_samples,
                variant_counts=lane_variant_counts[lane_name],
                wall_total_ns=threaded_summary.total_ns,
                workload=lane_workloads[lane_name],
            )

        # Packed like the run-long lane storage, so combining multi-million-entry
        # lanes does not materialize an int object per sample before summarizing.
        combined_outer_create: array[int] = array("q")
        combined_outer_cleanup: array[int] = array("q")
        combined_outer_total: array[int] = array("q")
        combined_request_create: array[int] = array("q")
        combined_request_cleanup: array[int] = array("q")
        combined_request_total: array[int] = array("q")
        for metric_samples in lane_metric_samples.values():
            combined_outer_create.extend(metric_samples.outer_create_ns)
            combined_outer_cleanup.extend(metric_samples.outer_cleanup_ns)
            combined_outer_total.extend(metric_samples.outer_total_ns)
            combined_request_create.extend(metric_samples.request_create_ns)
            combined_request_cleanup.extend(metric_samples.request_cleanup_ns)
            combined_request_total.extend(metric_samples.request_total_ns)

        total_hot_scopes = sum(summary.cycles for summary in lane_summaries.values())
        hot_seconds = iteration_summary.total_ns / 1_000_000_000.0 if iteration_summary.total_ns > 0 else 0.0
        _require_gil_disabled()
        result_payload = {
            "lib": lib,
            "cfg": cfg,
            "gil_status": _gil_status(),
            "setup_singletons": setup_singletons,
            "request_objects_min": min_request_objects,
            "hot_objects_per_iter_min": hot_objects_per_iter_min,
            "setup_ns": setup_ns,
            "iteration_summary": iteration_summary,
            "bootstrap_summary": bootstrap_summary,
            "threaded_summary": threaded_summary,
            "total_hot_scopes": total_hot_scopes,
            "hot_scope_cycles_per_s": (total_hot_scopes / hot_seconds) if hot_seconds > 0 else 0.0,
            "hot_objects_per_s_min": ((hot_objects_per_iter_min * cfg.iterations) / hot_seconds) if hot_seconds > 0 else 0.0,
            "outer_scope_create_summary": _summarize(combined_outer_create),
            "outer_scope_cleanup_summary": _summarize(combined_outer_cleanup),
            "outer_scope_total_summary": _summarize(combined_outer_total),
            "request_scope_create_summary": _summarize(combined_request_create),
            "request_scope_cleanup_summary": _summarize(combined_request_cleanup),
            "request_scope_total_summary": _summarize(combined_request_total),
            "lane_summaries": lane_summaries,
            "per_turn_rows": per_turn_rows_data,
        }
    finally:
        # Restore GC posture before the next library runs in this same process.
        if gc_mode == "disabled" and gc_was_enabled and not gc.isenabled():
            gc.enable()
        if gc_frozen_here:
            gc.unfreeze()
        if gc_probe is not None:
            gc_probe.uninstall()
        cleanup_t0 = time.perf_counter_ns()
        ops.cleanup()
        cleanup_ns = time.perf_counter_ns() - cleanup_t0

    return _BenchmarkResult(
        lib=result_payload["lib"],
        cfg=result_payload["cfg"],
        gil_status=result_payload["gil_status"],
        setup_singletons=result_payload["setup_singletons"],
        request_objects_min=result_payload["request_objects_min"],
        hot_objects_per_iter_min=result_payload["hot_objects_per_iter_min"],
        setup_ns=result_payload["setup_ns"],
        cleanup_ns=cleanup_ns,
        iteration_summary=result_payload["iteration_summary"],
        bootstrap_summary=result_payload["bootstrap_summary"],
        threaded_summary=result_payload["threaded_summary"],
        total_hot_scopes=result_payload["total_hot_scopes"],
        hot_scope_cycles_per_s=result_payload["hot_scope_cycles_per_s"],
        hot_objects_per_s_min=result_payload["hot_objects_per_s_min"],
        outer_scope_create_summary=result_payload["outer_scope_create_summary"],
        outer_scope_cleanup_summary=result_payload["outer_scope_cleanup_summary"],
        outer_scope_total_summary=result_payload["outer_scope_total_summary"],
        request_scope_create_summary=result_payload["request_scope_create_summary"],
        request_scope_cleanup_summary=result_payload["request_scope_cleanup_summary"],
        request_scope_total_summary=result_payload["request_scope_total_summary"],
        lane_summaries=result_payload["lane_summaries"],
        per_turn_rows=result_payload.get("per_turn_rows", ()),
    )


def _per_turn_csv_enabled() -> bool:
    """
    Report whether `GAUNTLET_PER_TURN_CSV` asks for the per-turn CSV.

    Returns:
        bool: True for "1", "true", "yes" or "on", in any case and with
            surrounding spaces ignored; False otherwise or when unset.
    """
    return os.getenv("GAUNTLET_PER_TURN_CSV", "").strip().lower() in {
        "1", "true", "yes", "on"
    }


def _per_turn_csv_path() -> Path:
    """
    Resolve the per-turn CSV file written next to this module.

    Returns:
        Path: `real_world_gauntlet_per_turn<suffix>.csv`, where the suffix is
            `GAUNTLET_PER_TURN_CSV_SUFFIX` (empty by default).
    """
    suffix = os.getenv("GAUNTLET_PER_TURN_CSV_SUFFIX", "").strip()
    return Path(__file__).resolve().with_name(
        f"real_world_gauntlet_per_turn{suffix}.csv"
    )


def _per_turn_csv_header() -> list[str]:
    """
    Return the per-turn CSV columns both writers share.

    Returns:
        list[str]: Library, turn, the three timings in ms, GC incidence and the
            gen0 live count.
    """
    return [
        "DI Container",
        "Turn",
        "Total (ms)",
        "Bootstrap (ms)",
        "Threaded (ms)",
        "GC During",
        "Gen0 Live",
    ]


def _per_turn_csv_row(lib: str, row: Sequence[Any]) -> list[Any]:
    """
    Format one captured turn as a per-turn CSV row.

    Args:
        lib: Library name for the "DI Container" column.
        row: `(turn, total_ns, bootstrap_ns, threaded_ns, gc_during, gen0_live)`
            as captured in `_BenchmarkResult.per_turn_rows` (a list after a JSON
            round trip).

    Returns:
        list[Any]: The row, with the three timings in milliseconds to four
            decimals and GC incidence as "yes"/"no".
    """
    turn, total_ns, bootstrap_ns, threaded_ns, gc_during, gen0_live = row
    return [
        lib,
        turn,
        f"{total_ns / 1_000_000:.4f}",
        f"{bootstrap_ns / 1_000_000:.4f}",
        f"{threaded_ns / 1_000_000:.4f}",
        "yes" if gc_during else "no",
        gen0_live,
    ]


def _maybe_write_per_turn_csv(results: list) -> None:
    """
    Write one CSV with every single turn for all libraries, if enabled.

    Off unless GAUNTLET_PER_TURN_CSV is truthy. Produces a single file next to
    this test module, one row per iteration per library, tagged with a
    "DI Container" column so all three libraries live in the same sheet.
    Used by the runner's all-in-one mode and by `--lib` when run by hand; the
    one-process-per-library wrapper writes the same file through
    `_write_isolated_per_turn_csv`, which adds Round, Threads and Iterations columns.
    """
    if not _per_turn_csv_enabled():
        return
    path = _per_turn_csv_path()
    written = 0
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(_per_turn_csv_header())
        for result in results:
            for row in result.per_turn_rows:
                writer.writerow(_per_turn_csv_row(result.lib, row))
                written += 1
    print(
        f"[per-turn csv] wrote {written} rows for {len(results)} libraries -> {path}"
    )


def _write_isolated_per_turn_csv(payloads: Sequence[dict[str, Any]]) -> None:
    """
    Write the one-process-per-library wrapper's per-turn CSV, if enabled.

    Contract:
        - Off unless `GAUNTLET_PER_TURN_CSV` is truthy. Same file as
          `_maybe_write_per_turn_csv`, overwritten.
        - One row per turn per library per round, in the order the processes ran,
          with the same columns plus a trailing "Round" column (1-based), since
          more than one round repeats every library. Threads and Iterations
          columns distinguish every configured measurement combination.
        - The rows come from the payloads the per-library processes handed back
          (`_result_payload`); those processes do not write the CSV themselves.

    Args:
        payloads: One `_result_payload` dict per library process, in run order.
    """
    if not _per_turn_csv_enabled():
        return
    path = _per_turn_csv_path()
    written = 0
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([*_per_turn_csv_header(), "Round", "Threads", "Iterations"])
        for payload in payloads:
            for row in payload["per_turn_rows"]:
                writer.writerow([*_per_turn_csv_row(payload["lib"], row), payload["round"], payload["threads"], payload["iterations"]])
                written += 1
    print(
        f"[per-turn csv] wrote {written} rows for {len(payloads)} library runs -> {path}"
    )


def _print_benchmark_result(result: _BenchmarkResult) -> None:
    print(
        f"[{result.lib}] gauntlet config: "
        f"gil={result.gil_status}, "
        f"setup_singletons={result.setup_singletons}, "
        f"iterations={result.cfg.iterations}, "
        f"threads={result.cfg.threads}, "
        f"request_scopes={result.cfg.request_scope_runs}, "
        f"worker_a_scopes={result.cfg.worker_a_jobs if result.cfg.threads >= 2 else 0}, "
        f"worker_b_scopes={result.cfg.worker_b_jobs if result.cfg.threads >= 3 else 0}, "
        f"request_objects_min={result.request_objects_min}, "
        f"hot_objects_per_iter_min={result.hot_objects_per_iter_min}, "
        f"setup={_ms(result.setup_ns):.3f}ms"
    )
    print(
        f"[{result.lib}] gauntlet total({result.cfg.iterations})={_ms(result.iteration_summary.total_ns):.2f}ms | "
        f"{_format_summary_ms(result.iteration_summary)}"
    )
    print(
        f"[{result.lib}] gauntlet bootstrap per-iter | "
        f"{_format_summary_ms(result.bootstrap_summary)}"
    )
    print(
        f"[{result.lib}] gauntlet threaded phase per-iter | "
        f"{_format_summary_ms(result.threaded_summary)}"
    )
    print(
        f"[{result.lib}] outer-scope create | "
        f"{_format_summary_ms(result.outer_scope_create_summary)}"
    )
    print(
        f"[{result.lib}] outer-scope cleanup | "
        f"{_format_summary_ms(result.outer_scope_cleanup_summary)}"
    )
    print(
        f"[{result.lib}] outer-scope whole-cycle | "
        f"{_format_summary_ms(result.outer_scope_total_summary)}"
    )
    print(
        f"[{result.lib}] request-scope create | "
        f"{_format_summary_ms(result.request_scope_create_summary)}"
    )
    print(
        f"[{result.lib}] request-scope cleanup | "
        f"{_format_summary_ms(result.request_scope_cleanup_summary)}"
    )
    print(
        f"[{result.lib}] request-scope whole-cycle | "
        f"{_format_summary_ms(result.request_scope_total_summary)}"
    )
    print(
        f"[{result.lib}] gauntlet throughput | "
        f"hot_scopes={result.total_hot_scopes}, "
        f"hot_scopes/s={result.hot_scope_cycles_per_s:,.0f}, "
        f"hot_objects/s_min={result.hot_objects_per_s_min:,.0f}, "
        f"cleanup={_ms(result.cleanup_ns):.3f}ms"
    )
    for lane in result.lane_summaries.values():
        print(
            f"[{result.lib}] lane={lane.name} | "
            f"cycles={lane.cycles}, "
            f"objects_min={lane.objects_min}, "
            f"variants={lane.variant_counts}, "
            f"wall_cycles/s={lane.wall_cycles_per_s:,.0f}, "
            f"wall_objects/s_min={lane.wall_objects_per_s_min:,.0f}, "
            f"active_cycles/s={lane.active_cycles_per_s:,.0f}, "
            f"active_objects/s_min={lane.active_objects_per_s_min:,.0f}, "
            f"outer_create[{_format_summary_ms(lane.outer_create_summary)}], "
            f"outer_cleanup[{_format_summary_ms(lane.outer_cleanup_summary)}], "
            f"outer_total[{_format_summary_ms(lane.outer_total_summary)}], "
            f"request_create[{_format_summary_ms(lane.request_create_summary)}], "
            f"request_cleanup[{_format_summary_ms(lane.request_cleanup_summary)}], "
            f"request_total[{_format_summary_ms(lane.request_total_summary)}]"
        )


def _result_payload(result: _BenchmarkResult, round_number: int) -> dict[str, Any]:
    """
    Reduce one library's result to the JSON payload a per-library process hands back.

    Contract:
        - JSON values only, including named lane cycle/variant dictionaries, so `json.dumps`
          accepts it and the parent needs nothing else from the child process.
        - Carries what the wrapper summarizes across rounds - setup, the loop total
          and per-iteration statistics, the threaded and bootstrap averages,
          throughput - and the per-turn rows, which stay empty unless
          `GAUNTLET_PER_TURN_CSV` is set.

    Args:
        result: The library's `_BenchmarkResult`.
        round_number: 1-based round this run belongs to.

    Returns:
        dict[str, Any]: The payload; times in milliseconds.
    """
    return {
        "lib": result.lib,
        "round": round_number,
        "iterations": result.cfg.iterations,
        "threads": result.cfg.threads,
        "gil_status": result.gil_status,
        "setup_ms": _ms(result.setup_ns),
        "cleanup_ms": _ms(result.cleanup_ns),
        "total_ms": _ms(result.iteration_summary.total_ns),
        "avg_ms": _ms(result.iteration_summary.avg_ns),
        "median_ms": _ms(result.iteration_summary.median_ns),
        "p95_ms": _ms(result.iteration_summary.p95_ns),
        "p99_ms": _ms(result.iteration_summary.p99_ns),
        "max_ms": _ms(result.iteration_summary.max_ns),
        "threaded_avg_ms": _ms(result.threaded_summary.avg_ns),
        "bootstrap_avg_ms": _ms(result.bootstrap_summary.avg_ns),
        "hot_scopes_per_s": result.hot_scope_cycles_per_s,
        "total_hot_scopes": result.total_hot_scopes,
        "hot_objects_per_iter_min": result.hot_objects_per_iter_min,
        "lane_cycles": {name: lane.cycles for name, lane in result.lane_summaries.items()},
        "lane_variants": {name: list(lane.variant_counts) for name, lane in result.lane_summaries.items()},
        "per_turn_rows": [list(row) for row in result.per_turn_rows],
    }


def _isolated_median_lines(payloads: Sequence[dict[str, Any]]) -> list[str]:
    """
    Summarize each library across the wrapper's rounds as one median line.

    Contract:
        - One line per library/iteration-count/thread-count combination, in first-seen order and
          `_gauntlet_libraries()` order; a pair with no payloads is skipped.
        - Every value is the median over that library's runs; the loop total also
          shows its min and max, so run-to-run spread stays visible.

    Args:
        payloads: `_result_payload` dicts from the library processes.

    Returns:
        list[str]: The lines to print.
    """
    lines: list[str] = []
    settings = dict.fromkeys((payload["iterations"], payload["threads"]) for payload in payloads)
    for iterations, threads in settings:
        for lib in _gauntlet_libraries():
            runs = [payload for payload in payloads
                    if (payload["lib"], payload["iterations"], payload["threads"]) == (lib, iterations, threads)]
            if not runs:
                continue
            totals = [run["total_ms"] for run in runs]
            noun = "round" if len(runs) == 1 else "rounds"
            lines.append(
                f"[{lib}] isolated median over {len(runs)} {noun} | iterations={iterations} | threads={threads} | "
                f"total={statistics.median(totals):.2f}ms (min={min(totals):.2f}, max={max(totals):.2f}) | "
                f"avg={statistics.median([run['avg_ms'] for run in runs]):.3f}ms | "
                f"p99={statistics.median([run['p99_ms'] for run in runs]):.3f}ms | "
                f"threaded avg={statistics.median([run['threaded_avg_ms'] for run in runs]):.3f}ms | "
                f"hot_scopes/s={statistics.median([run['hot_scopes_per_s'] for run in runs]):,.0f} | "
                f"setup={statistics.median([run['setup_ms'] for run in runs]):.3f}ms"
            )
    return lines


def _run_isolated_library(
        lib: str,
        round_number: int,
        result_path: Path,
        *, threads: Optional[int] = None, iterations: Optional[int] = None,
) -> subprocess.CompletedProcess[str]:
    """
    Run one library of the shared gauntlet in a fresh interpreter process.

    Contract:
        - Starts `real_world_gauntlet_gil_runner.py --lib <lib>` with this
          interpreter with `-X gil=0`, from the repository root. A copied
          child environment forces PYTHON_GIL=0 even when the parent has 1;
          the parent environment itself is unchanged.
        - The child loads and runs only that library, prints its result and writes
          its `_result_payload` JSON to `result_path`.
        - Never raises for a failing child: the caller checks `returncode`.

    Args:
        lib: A name from `_gauntlet_libraries()`.
        round_number: 1-based round, recorded in the payload.
        result_path: Where the child writes its JSON payload.
        threads: This child's thread count; None preserves the inherited setting.
        iterations: This child's workload iterations; None preserves the inherited setting.

    Returns:
        subprocess.CompletedProcess[str]: The finished child, with stdout and stderr
            captured as text.
    """
    command = [sys.executable, "-X", "gil=0"]
    child_env = os.environ.copy()
    child_env["PYTHON_GIL"] = "0"
    if threads is not None:
        child_env["DI_GAUNTLET_THREADS"] = str(threads)
    if iterations is not None:
        child_env["DI_GAUNTLET_ITERS"] = str(iterations)
    command.extend([
        str(_runner_path()),
        "--lib",
        lib,
        "--round",
        str(round_number),
        "--result-json",
        str(result_path),
    ])
    return subprocess.run(
        command,
        cwd=str(_repo_root()),
        env=child_env,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.timeout(21_600)
def test_real_world_gauntlet() -> None:
    """
    Run the shared real-world gauntlet with every library in its own process.

    Contract:
        - Uses the same standalone runner pattern as the Melder-only benchmark and
          cProfile wrappers, once per library.
        - Each library runs in a fresh interpreter (`real_world_gauntlet_gil_runner.py
          --lib`), so no library's result depends on the libraries that ran before
          it. Running all three in one process, as this test did before 2026-09-30,
          made a library 5-12% slower when it ran second or third: on free-threaded
          CPython each library's run leaves starting and joining threads slower, and
          the gauntlet starts three threads per iteration. The runner with no
          arguments still runs that layout, to reproduce earlier baselines.
        - Forces `-X gil=0` and PYTHON_GIL=0 in every measured child process.
        - The editable REAL_WORLD_GAUNTLET_THREAD_COUNTS list defaults to 3,5,7,9.
          The editable iteration-count list defaults to 5k,10k,15k,25k,50k.
          Every iteration-count/thread-count/library/round gets a fresh process.
        - DI_GAUNTLET_THREADS accepts positive N; request/A/B workloads repeat
          under distinct request, worker_a, worker_b, worker_c, ... lane names.
        - `REAL_WORLD_GAUNTLET_ROUNDS` (default 1) repeats every library that many
          times, rotating the order each round (`_isolated_order`), and then prints
          one median line per library.
        - Streams each process's stdout/stderr into pytest output as soon as that
          process finishes, for direct visibility in IDE runs, and writes the
          per-turn CSV at the end when `GAUNTLET_PER_TURN_CSV` is set.
        - Fails, naming the library and round, if a process exits non-zero.
    """
    rounds = _gauntlet_rounds()
    iteration_counts = _gauntlet_iteration_counts()
    thread_counts = _gauntlet_thread_counts()
    print(f"[gauntlet] thread counts: {list(thread_counts)}", flush=True)
    print(f"[gauntlet] iteration counts: {list(iteration_counts)}", flush=True)
    payloads: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="real_world_gauntlet_") as scratch:
        for iterations in iteration_counts:
            for threads in thread_counts:
                for round_ix in range(rounds):
                    round_number = round_ix + 1
                    for lib in _isolated_order(round_ix):
                        result_path = Path(scratch) / f"iters{iterations}_threads{threads}_round{round_number}_{lib}.json"
                        print(f"[gauntlet] iterations={iterations}, threads={threads}, round {round_number}/{rounds}: {lib} in its own process")
                        completed = _run_isolated_library(
                            lib, round_number, result_path, threads=threads, iterations=iterations)
                        if completed.stdout:
                            print(completed.stdout, end="" if completed.stdout.endswith("\n") else "\n")
                        if completed.stderr:
                            print(completed.stderr, end="" if completed.stderr.endswith("\n") else "\n")
                        if completed.returncode != 0:
                            raise AssertionError(
                                f"Shared real-world gauntlet runner failed for {lib}, iterations={iterations}, "
                                f"threads={threads}, round {round_number}, exit code {completed.returncode}."
                            )
                        payload = json.loads(result_path.read_text(encoding="utf-8"))
                        if (payload["lib"], payload["iterations"], payload["threads"], payload["round"], payload["gil_status"]) != (
                                lib, iterations, threads, round_number, "disabled"):
                            raise AssertionError("Gauntlet child returned mismatched iteration/thread/library/round/GIL identity")
                        payloads.append(payload)
    if rounds > 1 or len(thread_counts) > 1 or len(iteration_counts) > 1:
        for line in _isolated_median_lines(payloads):
            print(line)
    _write_isolated_per_turn_csv(payloads)
