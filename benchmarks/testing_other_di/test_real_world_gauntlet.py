from __future__ import annotations

import contextvars
import gc
import os
import random
import statistics
import subprocess
import sys
import threading
import time
import typing
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import pytest


# Keep this `True` so the shared gauntlet always runs through a standalone
# `-X gil=0` subprocess when launched from pytest. Set to `False` only if you
# explicitly want the wrapper to use the current interpreter mode instead.
REAL_WORLD_GAUNTLET_FORCE_NOGIL = True


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


def _ms(ns: int | float) -> float:
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
)
_REQUEST_SCOPE_TRANSIENT_TYPES: tuple[type, ...] = (
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
_WORKER_A_JOBS_DEFAULT = 25
_WORKER_B_JOBS_DEFAULT = 30
_BOOTSTRAP_FANOUT_PER_SINGLETON = 5
_VARIANT_COUNT = 3
_LIB_SEEDS = {
    "dependency-injector": 110_003,
    "dishka": 220_007,
    "melder": 330_011,
}


@dataclass(frozen=True)
class _GauntletConfig:
    iterations: int
    threads: int
    request_scope_runs: int
    worker_a_jobs: int
    worker_b_jobs: int

    @staticmethod
    def from_env() -> _GauntletConfig:
        cfg = _GauntletConfig(
            iterations=_env_int("DI_GAUNTLET_ITERS", 6000),
            threads=_env_int("DI_GAUNTLET_THREADS", 3),
            request_scope_runs=_env_int("DI_GAUNTLET_REQUEST_SCOPES", _REQUEST_SCOPE_RUNS_DEFAULT),
            worker_a_jobs=_env_int("DI_GAUNTLET_WORKER_A_JOBS", _WORKER_A_JOBS_DEFAULT),
            worker_b_jobs=_env_int("DI_GAUNTLET_WORKER_B_JOBS", _WORKER_B_JOBS_DEFAULT),
        )
        if cfg.iterations <= 0:
            raise AssertionError("DI_GAUNTLET_ITERS must be > 0")
        if cfg.threads <= 0 or cfg.threads > 3:
            raise AssertionError("DI_GAUNTLET_THREADS must be between 1 and 3")
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
    request_scope_cycle: Callable[[int], "_ScopeCycleMetrics"]
    worker_a_scope_cycle: Callable[[int], "_ScopeCycleMetrics"]
    worker_b_scope_cycle: Callable[[int], "_ScopeCycleMetrics"]
    cleanup: Callable[[], None]


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
    outer_create_ns: list[int]
    outer_cleanup_ns: list[int]
    outer_total_ns: list[int]
    request_create_ns: list[int]
    request_cleanup_ns: list[int]
    request_total_ns: list[int]


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

    return _RuntimeOps(
        name="dependency-injector",
        spawn_singletons=spawn_singletons,
        bootstrap_fanout=bootstrap_fanout,
        request_scope_cycle=request_scope_cycle,
        worker_a_scope_cycle=worker_a_scope_cycle,
        worker_b_scope_cycle=worker_b_scope_cycle,
        cleanup=cleanup,
    )


def _build_runtime_dishka() -> _RuntimeOps:
    pytest.importorskip("dishka")
    from dishka import Provider, Scope, make_container

    singleton_types = set(_SINGLETON_TYPES)
    outer_scoped_types = set(_OUTER_SCOPED_TYPES)
    request_scoped_types = set(_REQUEST_SCOPED_TYPES)
    request_scope_transients = set(_REQUEST_SCOPE_TRANSIENT_TYPES)

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

        return _run_in_session_and_request_scopes(
            outer_cls=WorkerBSession,
            request_marker_cls=WorkerBScopeMarker,
            variant_call=variant_call,
            variant_error_prefix="worker B lane",
        )

    def cleanup() -> None:
        container.close()
        gc.collect()

    return _RuntimeOps(
        name="dishka",
        spawn_singletons=spawn_singletons,
        bootstrap_fanout=bootstrap_fanout,
        request_scope_cycle=request_scope_cycle,
        worker_a_scope_cycle=worker_a_scope_cycle,
        worker_b_scope_cycle=worker_b_scope_cycle,
        cleanup=cleanup,
    )


def _build_runtime_melder() -> _RuntimeOps:
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
    spellbook.configure_aether_frame(
        system_state=None,
        disposal=None,
        disposal_method_names=None,
        system_caching_enabled=True,
    )
    cfg.set_property("phase_scheduler_workers_per_spellbook", 3)

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
        root = conduit.meld(spell=spell_ids[cls])
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
            outer1 = lesser.meld(spell=spell_ids[outer_cls])
            outer2 = lesser.meld(spell=spell_ids[outer_cls])
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
                marker1 = space.meld(spell=spell_ids[request_marker_cls])
                marker2 = space.meld(spell=spell_ids[request_marker_cls])
                if not isinstance(marker1, request_marker_cls):
                    raise AssertionError(f"Melder: {variant_error_prefix} request marker wrong type")
                if marker1 is not marker2:
                    raise AssertionError(f"Melder: {variant_error_prefix} request scope marker not cached")
                inherited = space.meld(spell=spell_ids[outer_cls])
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
                root = space.meld(spell=spell_ids[RequestRoot])
                if not isinstance(root, RequestRoot):
                    raise AssertionError("Melder: request root resolve returned wrong type")
            elif variant == 1:
                group = space.meld(spell=spell_ids[RequestGroup])
                root = space.meld(spell=spell_ids[RequestRoot])
                if not isinstance(group, RequestGroup) or not isinstance(root, RequestRoot):
                    raise AssertionError("Melder: request scope variant returned wrong type")
            else:
                root1 = space.meld(spell=spell_ids[RequestRoot])
                root2 = space.meld(spell=spell_ids[RequestRoot])
                if not isinstance(root1, RequestRoot) or not isinstance(root2, RequestRoot):
                    raise AssertionError("Melder: request scope variant returned wrong type")

        return _run_in_lesser_and_spellspace(
            outer_cls=RequestSession,
            request_marker_cls=RequestScopeMarker,
            variant_call=variant_call,
            variant_error_prefix="request lane",
        )

    def worker_a_scope_cycle(variant: int) -> _ScopeCycleMetrics:
        def variant_call(space: Any) -> None:
            if variant == 0:
                root = space.meld(spell=spell_ids[WorkerAJobRoot])
                if not isinstance(root, WorkerAJobRoot):
                    raise AssertionError("Melder: worker A resolve returned wrong type")
            elif variant == 1:
                group = space.meld(spell=spell_ids[WorkerAGroup])
                root = space.meld(spell=spell_ids[WorkerAJobRoot])
                if not isinstance(group, WorkerAGroup) or not isinstance(root, WorkerAJobRoot):
                    raise AssertionError("Melder: worker A scope variant returned wrong type")
            else:
                root1 = space.meld(spell=spell_ids[WorkerAJobRoot])
                root2 = space.meld(spell=spell_ids[WorkerAJobRoot])
                if not isinstance(root1, WorkerAJobRoot) or not isinstance(root2, WorkerAJobRoot):
                    raise AssertionError("Melder: worker A scope variant returned wrong type")

        return _run_in_lesser_and_spellspace(
            outer_cls=WorkerASession,
            request_marker_cls=WorkerAScopeMarker,
            variant_call=variant_call,
            variant_error_prefix="worker A lane",
        )

    def worker_b_scope_cycle(variant: int) -> _ScopeCycleMetrics:
        def variant_call(space: Any) -> None:
            if variant == 0:
                root = space.meld(spell=spell_ids[WorkerBJobRoot])
                if not isinstance(root, WorkerBJobRoot):
                    raise AssertionError("Melder: worker B resolve returned wrong type")
            elif variant == 1:
                group = space.meld(spell=spell_ids[WorkerBGroup])
                root = space.meld(spell=spell_ids[WorkerBJobRoot])
                if not isinstance(group, WorkerBGroup) or not isinstance(root, WorkerBJobRoot):
                    raise AssertionError("Melder: worker B scope variant returned wrong type")
            else:
                root1 = space.meld(spell=spell_ids[WorkerBJobRoot])
                root2 = space.meld(spell=spell_ids[WorkerBJobRoot])
                if not isinstance(root1, WorkerBJobRoot) or not isinstance(root2, WorkerBJobRoot):
                    raise AssertionError("Melder: worker B scope variant returned wrong type")

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

    return _RuntimeOps(
        name="melder",
        spawn_singletons=spawn_singletons,
        bootstrap_fanout=bootstrap_fanout,
        request_scope_cycle=request_scope_cycle,
        worker_a_scope_cycle=worker_a_scope_cycle,
        worker_b_scope_cycle=worker_b_scope_cycle,
        cleanup=cleanup,
    )


def _build_ops(lib: str) -> _RuntimeOps:
    if lib == "dependency-injector":
        return _build_runtime_dependency_injector()
    if lib == "dishka":
        return _build_runtime_dishka()
    if lib == "melder":
        from benchmarks.testing_other_di import test_melder_gauntlet as melder_gauntlet

        return melder_gauntlet._build_runtime_melder()
    raise AssertionError(f"Unknown lib: {lib}")


def _lane_objects_per_cycle(name: str) -> int:
    if name == "request":
        return _REQUEST_OBJECTS_PER_ROOT
    if name == "worker_a":
        return _WORKER_A_OBJECTS_PER_ROOT
    if name == "worker_b":
        return _WORKER_B_OBJECTS_PER_ROOT
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


def _variant_counts_tuple(values: list[int]) -> tuple[int, ...]:
    return tuple(values)


def _run_gauntlet_once(ops: _RuntimeOps, cfg: _GauntletConfig, iteration_ix: int) -> _IterationResult:
    """
    Time one full gauntlet iteration from fresh container build through cleanup.
    """
    t0 = time.perf_counter_ns()
    bootstrap_t0 = time.perf_counter_ns()
    ops.bootstrap_fanout()
    bootstrap_ns = time.perf_counter_ns() - bootstrap_t0

    lane_counts = {
        "request": 0,
        "worker_a": 0,
        "worker_b": 0,
    }
    lane_metrics = {
        "request": _new_lane_metric_samples(),
        "worker_a": _new_lane_metric_samples(),
        "worker_b": _new_lane_metric_samples(),
    }
    lane_variant_counts = {
        "request": [0] * _VARIANT_COUNT,
        "worker_a": [0] * _VARIANT_COUNT,
        "worker_b": [0] * _VARIANT_COUNT,
    }
    errors: list[BaseException] = []
    stop_event = threading.Event()
    active_lanes: list[tuple[str, Callable[[int], None], int, int]] = [
        ("request", ops.request_scope_cycle, cfg.request_scope_runs, 17),
    ]
    if cfg.threads >= 2:
        active_lanes.append(("worker_a", ops.worker_a_scope_cycle, cfg.worker_a_jobs, 29))
    if cfg.threads >= 3:
        active_lanes.append(("worker_b", ops.worker_b_scope_cycle, cfg.worker_b_jobs, 41))

    ready_barrier = threading.Barrier(len(active_lanes) + 1)
    start_event = threading.Event()

    def make_worker(
            name: str,
            call: Callable[[int], None],
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

    if lane_counts["request"] != cfg.request_scope_runs:
        raise AssertionError("Request lane did not complete expected scope cycles")
    if cfg.threads >= 2 and lane_counts["worker_a"] != cfg.worker_a_jobs:
        raise AssertionError("Worker A lane did not complete expected scope cycles")
    if cfg.threads >= 3 and lane_counts["worker_b"] != cfg.worker_b_jobs:
        raise AssertionError("Worker B lane did not complete expected scope cycles")
    return _IterationResult(
        total_ns=time.perf_counter_ns() - t0,
        bootstrap_ns=bootstrap_ns,
        threaded_ns=threaded_ns,
        lane_metrics=lane_metrics,
        lane_variant_counts=lane_variant_counts,
    )


def _summarize(samples: list[int]) -> _Summary:
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
) -> _LaneSummary:
    outer_total_summary = _summarize(metric_samples.outer_total_ns)
    request_total_summary = _summarize(metric_samples.request_total_ns)
    objects_min = len(metric_samples.outer_total_ns) * _lane_objects_per_cycle(name)
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


def _run_gauntlet_benchmark(lib: str, cfg: _GauntletConfig) -> _BenchmarkResult:
    min_request_objects = cfg.request_scope_runs * _REQUEST_OBJECTS_PER_ROOT
    min_worker_a_objects = cfg.worker_a_jobs * _WORKER_A_OBJECTS_PER_ROOT if cfg.threads >= 2 else 0
    min_worker_b_objects = cfg.worker_b_jobs * _WORKER_B_OBJECTS_PER_ROOT if cfg.threads >= 3 else 0
    bootstrap_objects = len(_BOOTSTRAP_TYPES) * _BOOTSTRAP_FANOUT_PER_SINGLETON
    hot_objects_per_iter_min = bootstrap_objects + min_request_objects + min_worker_a_objects + min_worker_b_objects
    setup_singletons = len(_SINGLETON_TYPES)

    setup_t0 = time.perf_counter_ns()
    ops = _build_ops(lib)
    result_payload: dict[str, Any] = {}
    cleanup_ns = 0
    try:
        ops.spawn_singletons()
        setup_ns = time.perf_counter_ns() - setup_t0

        iteration_samples: list[int] = []
        bootstrap_samples: list[int] = []
        threaded_samples: list[int] = []
        lane_metric_samples = {
            "request": _new_lane_metric_samples(),
            "worker_a": _new_lane_metric_samples(),
            "worker_b": _new_lane_metric_samples(),
        }
        lane_variant_counts = {
            "request": [0] * _VARIANT_COUNT,
            "worker_a": [0] * _VARIANT_COUNT,
            "worker_b": [0] * _VARIANT_COUNT,
        }

        for iteration_ix in range(cfg.iterations):
            iteration = _run_gauntlet_once(ops, cfg, iteration_ix)
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
                for i, count in enumerate(counts):
                    lane_variant_counts[lane_name][i] += count

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
            )

        combined_outer_create = []
        combined_outer_cleanup = []
        combined_outer_total = []
        combined_request_create = []
        combined_request_cleanup = []
        combined_request_total = []
        for metric_samples in lane_metric_samples.values():
            combined_outer_create.extend(metric_samples.outer_create_ns)
            combined_outer_cleanup.extend(metric_samples.outer_cleanup_ns)
            combined_outer_total.extend(metric_samples.outer_total_ns)
            combined_request_create.extend(metric_samples.request_create_ns)
            combined_request_cleanup.extend(metric_samples.request_cleanup_ns)
            combined_request_total.extend(metric_samples.request_total_ns)

        total_hot_scopes = sum(summary.cycles for summary in lane_summaries.values())
        hot_seconds = iteration_summary.total_ns / 1_000_000_000.0 if iteration_summary.total_ns > 0 else 0.0
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
        }
    finally:
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
            f"outer_create[{_format_summary_ms(lane.outer_create_summary)}], "
            f"outer_cleanup[{_format_summary_ms(lane.outer_cleanup_summary)}], "
            f"outer_total[{_format_summary_ms(lane.outer_total_summary)}], "
            f"request_create[{_format_summary_ms(lane.request_create_summary)}], "
            f"request_cleanup[{_format_summary_ms(lane.request_cleanup_summary)}], "
            f"request_total[{_format_summary_ms(lane.request_total_summary)}]"
        )


@pytest.mark.timeout(3600)
def test_real_world_gauntlet() -> None:
    """
    Run the shared real-world gauntlet through the standalone runner.

    Contract:
        - Uses the same standalone runner pattern as the working Melder-only
          benchmark/cProfile wrappers.
        - Forces `-X gil=0` when `REAL_WORLD_GAUNTLET_FORCE_NOGIL` is true.
        - Streams child stdout/stderr back into pytest output for direct
          visibility in IDE runs.
        - Fails if the standalone runner exits non-zero.
    """
    command = [sys.executable]
    if REAL_WORLD_GAUNTLET_FORCE_NOGIL:
        command.extend(["-X", "gil=0"])
    command.append(str(_runner_path()))

    completed = subprocess.run(
        command,
        cwd=str(_repo_root()),
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        check=False,
    )

    if completed.stdout:
        print(completed.stdout, end="" if completed.stdout.endswith("\n") else "\n")
    if completed.stderr:
        print(completed.stderr, end="" if completed.stderr.endswith("\n") else "\n")

    if completed.returncode != 0:
        raise AssertionError(
            "Shared real-world gauntlet runner failed with exit code "
            f"{completed.returncode}."
        )

