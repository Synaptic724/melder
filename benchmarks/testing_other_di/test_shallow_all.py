from __future__ import annotations

import contextlib
import contextvars
import gc
import inspect
import os
import random
import sys
import threading
import time
import typing
from dataclasses import dataclass
from typing import Any, Callable, Optional

import pytest

from tests.mocks.spellbook.deep_layers import (
    Depth3Root,
    Depth7Root,
    Depth9Root,
    get_depth_3_classes,
    get_depth_7_classes,
    get_depth_9_classes,
)
def _env_int_nonneg(name: str, default: int) -> int:
    v = _env_int(name, default)
    return v if v >= 0 else 0


def _warmup_ops(ops: _RuntimeOps, *, iters: int) -> None:
    """
    Warm up a single-graph ops object to exclude lazy-first-resolve work from timed runs.
    """
    if iters <= 0:
        return

    # Warm roots
    for _ in range(iters):
        ops.get_root_a()
        ops.get_root_b()

    # Warm spellspace path at least once
    ops.spellspace_cycle()


def _warmup_rotation_ops(ops: _RotationOps, *, iters: int) -> None:
    """
    Warm up a rotation ops object for every graph index.
    """
    if iters <= 0:
        return

    gcount = len(ops.graphs)
    for gix in range(gcount):
        for _ in range(iters):
            ops.get_root_a(gix)
            ops.get_root_b(gix)
        ops.spellspace_cycle(gix)


def _average_call_ns(call: Callable[[], Any], *, iters: int) -> float:
    """
    Measure average call cost for one lane over N iterations.

    Contract:
        - Executes `call` exactly `iters` times.
        - Returns average nanoseconds per call as a float.
        - Caller controls warmup separately.
    """
    if iters <= 0:
        raise AssertionError("iters must be > 0")
    t0 = time.perf_counter_ns()
    for _ in range(iters):
        call()
    total = time.perf_counter_ns() - t0
    return total / float(iters)


def _average_spellspace_metrics_ns(
        *,
        enter_scope: Callable[[], Any],
        resolve_in_scope: Callable[[Any], Any],
        exit_scope: Callable[[Any], None],
        iters: int,
) -> tuple[float, float, float, float, float]:
    """
    Measure split spellspace metrics over N iterations.

    Contract:
        - Measures scope-build time separately from resolve time.
        - Measures first and cached meld time separately inside the
          already-active scope.
        - Measures scope-exit time separately from meld time.
        - Measures total time across build + two resolves + teardown.
    """
    if iters <= 0:
        raise AssertionError("iters must be > 0")
    build_total = 0
    first_total = 0
    cached_total = 0
    exit_total = 0
    whole_total = 0

    for _ in range(iters):
        t0 = time.perf_counter_ns()
        scope_handle = enter_scope()
        t1 = time.perf_counter_ns()
        try:
            resolve_in_scope(scope_handle)
            t2 = time.perf_counter_ns()
            resolve_in_scope(scope_handle)
            t3 = time.perf_counter_ns()
        finally:
            exit_scope(scope_handle)
        t4 = time.perf_counter_ns()

        build_total += t1 - t0
        first_total += t2 - t1
        cached_total += t3 - t2
        exit_total += t4 - t3
        whole_total += t4 - t0

    avg_build = build_total / float(iters)
    avg_first = first_total / float(iters)
    avg_cached = cached_total / float(iters)
    avg_exit = exit_total / float(iters)
    avg_total = whole_total / float(iters)
    return avg_build, avg_first, avg_cached, avg_exit, avg_total

# ======================================================================================
# Synthetic graphs: solo / shallow / wide / diamond
#
# IMPORTANT FIX:
#   Any class without an explicit __init__ inherits object.__init__(*args, **kwargs).
#   Reflection-based wiring then sees params named "args"/"kwargs" with no annotations,
#   which breaks the competitors and injector.inject patching.
#
#   We fix that by inheriting _NoDeps for all leaf/no-deps nodes so they have __init__(self)->None.
# ======================================================================================


class _NoDeps:
    """
    Purpose:
        Marker base for synthetic benchmark nodes with no dependencies.

    Contract:
        - Provides an explicit zero-arg __init__ so reflection-based DI wiring does not
          see object.__init__(*args, **kwargs) and explode.
    """
    __slots__ = ()

    def __init__(self) -> None:
        return None


# ---- SOLO (no dependencies) ---------------------------------------------------------


class SoloRootA(_NoDeps):
    __slots__ = ()


class SoloRootB(_NoDeps):
    __slots__ = ()


class SoloSpaceRoot(_NoDeps):
    __slots__ = ()


# ---- SHALLOW (depth-2: root -> leaves) ----------------------------------------------


class ShallowLeafA(_NoDeps):
    __slots__ = ()


class ShallowLeafB(_NoDeps):
    __slots__ = ()


class ShallowRootAB:
    __slots__ = ("a", "b")

    def __init__(self, a: ShallowLeafA, b: ShallowLeafB) -> None:
        self.a = a
        self.b = b


class ShallowLeafC(_NoDeps):
    __slots__ = ()


class ShallowRootC:
    __slots__ = ("c",)

    def __init__(self, c: ShallowLeafC) -> None:
        self.c = c


class ShallowSpaceLeaf(_NoDeps):
    __slots__ = ()


class ShallowSpaceRoot:
    __slots__ = ("leaf",)

    def __init__(self, leaf: ShallowSpaceLeaf) -> None:
        self.leaf = leaf


# ---- WIDE (one root has many inputs) ------------------------------------------------


class Wide8Leaf0(_NoDeps):
    __slots__ = ()


class Wide8Leaf1(_NoDeps):
    __slots__ = ()


class Wide8Leaf2(_NoDeps):
    __slots__ = ()


class Wide8Leaf3(_NoDeps):
    __slots__ = ()


class Wide8Leaf4(_NoDeps):
    __slots__ = ()


class Wide8Leaf5(_NoDeps):
    __slots__ = ()


class Wide8Leaf6(_NoDeps):
    __slots__ = ()


class Wide8Leaf7(_NoDeps):
    __slots__ = ()


class Wide8Root:
    __slots__ = ("leaves",)

    def __init__(
            self,
            l0: Wide8Leaf0,
            l1: Wide8Leaf1,
            l2: Wide8Leaf2,
            l3: Wide8Leaf3,
            l4: Wide8Leaf4,
            l5: Wide8Leaf5,
            l6: Wide8Leaf6,
            l7: Wide8Leaf7,
    ) -> None:
        self.leaves = (l0, l1, l2, l3, l4, l5, l6, l7)


class Wide9Leaf0(_NoDeps):
    __slots__ = ()


class Wide9Leaf1(_NoDeps):
    __slots__ = ()


class Wide9Leaf2(_NoDeps):
    __slots__ = ()


class Wide9Leaf3(_NoDeps):
    __slots__ = ()


class Wide9Leaf4(_NoDeps):
    __slots__ = ()


class Wide9Leaf5(_NoDeps):
    __slots__ = ()


class Wide9Leaf6(_NoDeps):
    __slots__ = ()


class Wide9Leaf7(_NoDeps):
    __slots__ = ()


class Wide9Leaf8(_NoDeps):
    __slots__ = ()


class Wide9Group0:
    __slots__ = ("a", "b", "c")

    def __init__(self, a: Wide9Leaf0, b: Wide9Leaf1, c: Wide9Leaf2) -> None:
        self.a = a
        self.b = b
        self.c = c


class Wide9Group1:
    __slots__ = ("a", "b", "c")

    def __init__(self, a: Wide9Leaf3, b: Wide9Leaf4, c: Wide9Leaf5) -> None:
        self.a = a
        self.b = b
        self.c = c


class Wide9Group2:
    __slots__ = ("a", "b", "c")

    def __init__(self, a: Wide9Leaf6, b: Wide9Leaf7, c: Wide9Leaf8) -> None:
        self.a = a
        self.b = b
        self.c = c


class Wide9Root:
    __slots__ = ("g0", "g1", "g2")

    def __init__(self, g0: Wide9Group0, g1: Wide9Group1, g2: Wide9Group2) -> None:
        self.g0 = g0
        self.g1 = g1
        self.g2 = g2


class WideSpaceLeaf(_NoDeps):
    __slots__ = ()


class WideSpaceRoot:
    __slots__ = ("leaf",)

    def __init__(self, leaf: WideSpaceLeaf) -> None:
        self.leaf = leaf


# ---- DIAMOND (shared dependency requested multiple times) ----------------------------
# This detects within-resolve dedupe on transients.


class DiamondSharedLeaf(_NoDeps):
    __slots__ = ()


class DiamondLeft:
    __slots__ = ("leaf",)

    def __init__(self, leaf: DiamondSharedLeaf) -> None:
        self.leaf = leaf


class DiamondRight:
    __slots__ = ("leaf",)

    def __init__(self, leaf: DiamondSharedLeaf) -> None:
        self.leaf = leaf


class DiamondRoot:
    __slots__ = ("left", "right")

    def __init__(self, left: DiamondLeft, right: DiamondRight) -> None:
        self.left = left
        self.right = right


class DiamondSpaceLeaf(_NoDeps):
    __slots__ = ()


class DiamondSpaceRoot:
    __slots__ = ("leaf",)

    def __init__(self, leaf: DiamondSpaceLeaf) -> None:
        self.leaf = leaf


# ======================================================================================
# Shared helpers
# ======================================================================================


def _env_str(name: str, default: str) -> str:
    raw = os.getenv(name)
    if raw is None:
        return default
    s = raw.strip()
    return s if s else default


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


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    s = raw.strip().lower()
    if s in ("1", "true", "yes", "y", "on"):
        return True
    if s in ("0", "false", "no", "n", "off"):
        return False
    return default


def _parse_csv(value: str) -> list[str]:
    parts = [p.strip() for p in value.split(",")]
    return [p for p in parts if p]


def _maybe_print_gil_status(prefix: str) -> None:
    if not _env_bool("DI_PRINT_GIL", False):
        return
    flag = getattr(sys, "_is_gil_enabled", None)
    if flag is None:
        print(f"[{prefix}] GIL enabled? (sys._is_gil_enabled not available)")
        return
    try:
        print(f"[{prefix}] GIL enabled? {flag()}")
    except Exception:
        print(f"[{prefix}] GIL enabled? (error calling sys._is_gil_enabled)")


def _ctor_param_types(cls: type) -> tuple[tuple[str, type], ...]:
    """
    Extract typed constructor parameters for a class.

    Contract:
        - Treats object.__init__ / varargs-only __init__ as "no deps".
        - Resolves string annotations via typing.get_type_hints.
        - Raises AssertionError if a real parameter lacks a concrete type annotation.
    """
    init = cls.__init__
    sig = inspect.signature(init)
    params = list(sig.parameters.values())[1:]  # skip self

    # If __init__ is effectively "(*args, **kwargs)" treat as no-deps leaf.
    if params and all(p.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD) for p in params):
        return ()

    try:
        hints = typing.get_type_hints(init, include_extras=True)
    except Exception:
        hints = getattr(init, "__annotations__", {}) or {}

    out: list[tuple[str, type]] = []
    for p in params:
        ann = hints.get(p.name, p.annotation)
        if ann is inspect._empty or ann is None:
            raise AssertionError(f"{cls.__name__}.__init__ param '{p.name}' missing annotation")
        if not isinstance(ann, type):
            raise AssertionError(f"{cls.__name__}.__init__ param '{p.name}' has non-type annotation: {ann!r}")
        out.append((p.name, ann))
    return tuple(out)


# ======================================================================================
# Graph Specs
# ======================================================================================


@dataclass(frozen=True)
class _GraphSpec:
    """
    Purpose:
        Describe a benchmark graph orientation.

    Contract:
        - *_classes must be topologically ordered (deps before dependents).
        - transient_probe: across-resolve anti-cache (optional).
        - within_resolve_probe: within-resolve anti-dedupe (optional).
    """
    name: str
    root_a: type
    root_b: type
    spellspace_root: type
    root_a_classes: tuple[type, ...]
    root_b_classes: tuple[type, ...]
    spellspace_classes: tuple[type, ...]
    transient_probe: Optional[Callable[[Any], tuple[object, object]]]
    within_resolve_probe: Optional[Callable[[Any], tuple[object, object]]]
    within_resolve_expect_distinct: bool


class _GraphFactory:
    """
    Supported shapes:
        solo     - no dependencies
        shallow  - depth-2 roots
        wide     - wide arity root + grouped-wide root
        diamond  - shared dependency requested twice inside same resolve
        deep     - existing deep_layers (Depth9 vs Depth7 + spellspace Depth3)
    """
    @staticmethod
    def solo() -> _GraphSpec:
        return _GraphSpec(
            name="solo",
            root_a=SoloRootA,
            root_b=SoloRootB,
            spellspace_root=SoloSpaceRoot,
            root_a_classes=(SoloRootA,),
            root_b_classes=(SoloRootB,),
            spellspace_classes=(SoloSpaceRoot,),
            transient_probe=None,
            within_resolve_probe=None,
            within_resolve_expect_distinct=True,
        )

    @staticmethod
    def shallow() -> _GraphSpec:
        def _probe(root: Any) -> tuple[object, object]:
            return root.a, root.b

        return _GraphSpec(
            name="shallow",
            root_a=ShallowRootAB,
            root_b=ShallowRootC,
            spellspace_root=ShallowSpaceRoot,
            root_a_classes=(ShallowLeafA, ShallowLeafB, ShallowRootAB),
            root_b_classes=(ShallowLeafC, ShallowRootC),
            spellspace_classes=(ShallowSpaceLeaf, ShallowSpaceRoot),
            transient_probe=_probe,
            within_resolve_probe=None,
            within_resolve_expect_distinct=True,
        )

    @staticmethod
    def wide() -> _GraphSpec:
        def _probe(root: Any) -> tuple[object, object]:
            return root.leaves[0], root.leaves[1]

        return _GraphSpec(
            name="wide",
            root_a=Wide8Root,
            root_b=Wide9Root,
            spellspace_root=WideSpaceRoot,
            root_a_classes=(
                Wide8Leaf0, Wide8Leaf1, Wide8Leaf2, Wide8Leaf3,
                Wide8Leaf4, Wide8Leaf5, Wide8Leaf6, Wide8Leaf7,
                Wide8Root,
            ),
            root_b_classes=(
                Wide9Leaf0, Wide9Leaf1, Wide9Leaf2,
                Wide9Leaf3, Wide9Leaf4, Wide9Leaf5,
                Wide9Leaf6, Wide9Leaf7, Wide9Leaf8,
                Wide9Group0, Wide9Group1, Wide9Group2,
                Wide9Root,
            ),
            spellspace_classes=(WideSpaceLeaf, WideSpaceRoot),
            transient_probe=_probe,
            within_resolve_probe=None,
            within_resolve_expect_distinct=True,
        )

    @staticmethod
    def diamond() -> _GraphSpec:
        def _within(root: Any) -> tuple[object, object]:
            return root.left.leaf, root.right.leaf

        return _GraphSpec(
            name="diamond",
            root_a=DiamondRoot,
            root_b=ShallowRootAB,
            spellspace_root=DiamondSpaceRoot,
            root_a_classes=(DiamondSharedLeaf, DiamondLeft, DiamondRight, DiamondRoot),
            root_b_classes=(ShallowLeafA, ShallowLeafB, ShallowRootAB),
            spellspace_classes=(DiamondSpaceLeaf, DiamondSpaceRoot),
            transient_probe=None,
            within_resolve_probe=_within,
            within_resolve_expect_distinct=True,
        )

    @staticmethod
    def deep_layers() -> _GraphSpec:
        def _probe_depth9(root: Any) -> tuple[object, object]:
            layer2 = root.left
            layer3 = layer2.left
            layer4 = layer3.left
            layer5 = layer4.left
            layer6 = layer5.left
            layer7 = layer6.left
            layer8 = layer7.left
            leaf_a = layer8.left
            leaf_b = layer8.right
            return leaf_a, leaf_b

        return _GraphSpec(
            name="deep",
            root_a=Depth9Root,
            root_b=Depth7Root,
            spellspace_root=Depth3Root,
            root_a_classes=get_depth_9_classes(),
            root_b_classes=get_depth_7_classes(),
            spellspace_classes=get_depth_3_classes(),
            transient_probe=_probe_depth9,
            within_resolve_probe=None,
            within_resolve_expect_distinct=True,
        )


def _all_graphs() -> list[_GraphSpec]:
    return [
        _GraphFactory.solo(),
        _GraphFactory.shallow(),
        _GraphFactory.wide(),
        _GraphFactory.diamond(),
        _GraphFactory.deep_layers(),
    ]


def _selected_graphs() -> list[_GraphSpec]:
    """
    Env:
        DI_GRAPHS: comma-separated list (default runs everything)
    """
    default = "solo,shallow,wide,diamond,deep"
    want = _parse_csv(_env_str("DI_GRAPHS", default))
    graphs_by_name = {g.name: g for g in _all_graphs()}
    out: list[_GraphSpec] = []
    for name in want:
        g = graphs_by_name.get(name)
        if g is None:
            raise AssertionError(f"Unknown graph '{name}'. Supported: {list(graphs_by_name.keys())}")
        out.append(g)
    return out


def _selected_libs() -> tuple[str, ...]:
    supported = ("dependency-injector", "dishka", "melder")
    raw = _env_str("DI_LIBS", ",".join(supported))
    want = tuple(_parse_csv(raw))
    for lib in want:
        if lib not in supported:
            raise AssertionError(f"Unknown lib '{lib}'. Supported: {supported}")
    return want


def _union_classes(graphs: list[_GraphSpec]) -> list[type]:
    """
    Union all classes across graphs in a stable order (deps before dependents within each graph).
    Graphs are independent, so concatenation + de-dupe is enough.
    """
    out: list[type] = []
    seen: set[type] = set()
    for g in graphs:
        for cls in g.root_a_classes + g.root_b_classes + g.spellspace_classes:
            if cls in seen:
                continue
            out.append(cls)
            seen.add(cls)
    return out


def _union_spellspace_types(graphs: list[_GraphSpec]) -> set[type]:
    out: set[type] = set()
    for g in graphs:
        out.update(g.spellspace_classes)
    return out


# ======================================================================================
# Stress config
# ======================================================================================


@dataclass(frozen=True)
class _StressConfig:
    """
    Controls (env vars):
        DI_THREADS                  default 1
        DI_DURATION_S               default 15.0
        DI_PATTERN                  alternating | burst | ratio | random (default alternating)
        DI_BURST_LEN                default 64
        DI_RATIO_P                  default 0.5
        DI_RANDOM_SEED              default 1337

        DI_SPELLSPACE_EVERY         default 20
        DI_GC_EVERY                 default 2000
        DI_GC_MODE                  periodic | disabled | none (default periodic)

        DI_VALIDATE_TRANSIENT_EVERY default 0 (off)
        DI_VALIDATE_WITHIN_EVERY    default 0 (off)

    Additional toggles:
        DI_RUN_ROTATION             default 1
        DI_RUN_PER_GRAPH            default 0
    """
    threads: int
    duration_s: float
    pattern: str
    burst_len: int
    ratio_p: float
    random_seed: int
    spellspace_every: int
    gc_every: int
    gc_mode: str
    validate_transient_every: int
    validate_within_every: int
    warmup_iters: int

    @staticmethod
    def from_env() -> _StressConfig:
        return _StressConfig(
            warmup_iters=_env_int_nonneg("DI_WARMUP_ITERS", 50),
            threads=_env_int("DI_THREADS", 1),
            duration_s=_env_float("DI_DURATION_S", 15.0),
            pattern=_env_str("DI_PATTERN", "alternating").lower(),
            burst_len=_env_int("DI_BURST_LEN", 64),
            ratio_p=_env_float("DI_RATIO_P", 0.5),
            random_seed=_env_int("DI_RANDOM_SEED", 1337),
            spellspace_every=_env_int("DI_SPELLSPACE_EVERY", 20),
            gc_every=_env_int("DI_GC_EVERY", 2000),
            gc_mode=_env_str("DI_GC_MODE", "periodic").lower(),
            validate_transient_every=_env_int("DI_VALIDATE_TRANSIENT_EVERY", 0),
            validate_within_every=_env_int("DI_VALIDATE_WITHIN_EVERY", 0),
        )


@dataclass
class _ThreadStats:
    steps: int = 0
    errors: int = 0
    spellspaces: int = 0
    # Per-graph counts (allocated by caller)
    g_steps: Optional[list[int]] = None
    g_a: Optional[list[int]] = None
    g_b: Optional[list[int]] = None


@dataclass(frozen=True)
class _RuntimeOps:
    name: str
    get_root_a: Callable[[], Any]
    get_root_b: Callable[[], Any]
    spellspace_cycle: Callable[[], None]
    spellspace_enter: Callable[[], Any]
    spellspace_resolve: Callable[[Any], Any]
    spellspace_exit: Callable[[Any], None]
    cleanup: Callable[[], None]


@dataclass(frozen=True)
class _RotationOps:
    name: str
    graphs: list[_GraphSpec]
    get_root_a: Callable[[int], Any]
    get_root_b: Callable[[int], Any]
    spellspace_cycle: Callable[[int], None]
    cleanup: Callable[[], None]


class _WorkSelector:
    __slots__ = ("pattern", "burst_len", "ratio_p", "rng")

    def __init__(self, *, pattern: str, burst_len: int, ratio_p: float, rng: Optional[random.Random]) -> None:
        self.pattern = pattern
        self.burst_len = burst_len
        self.ratio_p = ratio_p
        self.rng = rng

    def choose_a(self, i: int) -> bool:
        if self.pattern == "alternating":
            return (i & 1) == 0
        if self.pattern == "burst":
            block = (i // self.burst_len) & 1
            return block == 0
        if self.pattern == "ratio":
            r = random.random() if self.rng is None else self.rng.random()
            return r < self.ratio_p
        if self.pattern == "random":
            if self.rng is None:
                raise AssertionError("random pattern requires rng")
            return self.rng.random() < 0.5
        raise AssertionError(f"Unknown DI_PATTERN: {self.pattern}")


# ======================================================================================
# Per-graph runtime builders per lib (unchanged semantics)
# ======================================================================================


def _build_runtime_dependency_injector(g: _GraphSpec) -> _RuntimeOps:
    pytest.importorskip("dependency_injector")
    from dependency_injector import providers

    space_types = set(g.spellspace_classes)

    all_classes: list[type] = []
    seen: set[type] = set()
    for cls in g.root_a_classes + g.root_b_classes + g.spellspace_classes:
        if cls not in seen:
            all_classes.append(cls)
            seen.add(cls)

    providers_by_type: dict[type, Any] = {}

    for cls in all_classes:
        param_specs = _ctor_param_types(cls)
        kwargs: dict[str, Any] = {}
        for pname, ptype in param_specs:
            dep = providers_by_type.get(ptype)
            if dep is None:
                raise AssertionError(f"DI wiring error: {cls.__name__} depends on {ptype.__name__} before registered")
            kwargs[pname] = dep

        if cls in space_types:
            prov = providers.ContextLocalSingleton(cls, **kwargs)
        else:
            prov = providers.Factory(cls, **kwargs)

        providers_by_type[cls] = prov

    def get_root_a() -> Any:
        root = providers_by_type[g.root_a]()
        if not isinstance(root, g.root_a):
            raise AssertionError("Dependency Injector: root_a resolve returned wrong type")
        return root

    def get_root_b() -> Any:
        root = providers_by_type[g.root_b]()
        if not isinstance(root, g.root_b):
            raise AssertionError("Dependency Injector: root_b resolve returned wrong type")
        return root

    def spellspace_cycle() -> None:
        ctx = contextvars.Context()

        def run() -> None:
            r1 = providers_by_type[g.spellspace_root]()
            r2 = providers_by_type[g.spellspace_root]()
            if not isinstance(r1, g.spellspace_root):
                raise AssertionError("Dependency Injector: spellspace root resolve returned wrong type")
            if r1 is not r2:
                raise AssertionError("Dependency Injector: spellspace root not cached within spellspace")

        ctx.run(run)

    def spellspace_enter() -> Any:
        return contextvars.Context()

    def spellspace_resolve(ctx: Any) -> Any:
        root = ctx.run(lambda: providers_by_type[g.spellspace_root]())
        if not isinstance(root, g.spellspace_root):
            raise AssertionError("Dependency Injector: spellspace root resolve returned wrong type")
        return root

    def spellspace_exit(ctx: Any) -> None:
        return None

    def cleanup() -> None:
        for prov in providers_by_type.values():
            reset = getattr(prov, "reset", None)
            if reset is not None:
                reset()
        gc.collect()

    return _RuntimeOps(
        name="dependency-injector",
        get_root_a=get_root_a,
        get_root_b=get_root_b,
        spellspace_cycle=spellspace_cycle,
        spellspace_enter=spellspace_enter,
        spellspace_resolve=spellspace_resolve,
        spellspace_exit=spellspace_exit,
        cleanup=cleanup,
    )


def _build_runtime_lagom(g: _GraphSpec) -> _RuntimeOps:
    pytest.importorskip("lagom")
    from lagom import Container

    container = Container()

    def _make_leaf_factory(_cls: type) -> Callable[[], Any]:
        def factory() -> Any:
            return _cls()
        return factory

    def _make_factory(_cls: type, _specs: tuple[tuple[str, type], ...]) -> Callable[[Any], Any]:
        def factory(c: Any) -> Any:
            kwargs = {pname: c[ptype] for pname, ptype in _specs}
            return _cls(**kwargs)
        return factory

    all_classes: list[type] = []
    seen: set[type] = set()
    for cls in g.root_a_classes + g.root_b_classes + g.spellspace_classes:
        if cls not in seen:
            all_classes.append(cls)
            seen.add(cls)

    for cls in all_classes:
        specs = _ctor_param_types(cls)
        if not specs:
            container[cls] = _make_leaf_factory(cls)
        else:
            container[cls] = _make_factory(cls, specs)

    def get_root_a() -> Any:
        root = container[g.root_a]
        if not isinstance(root, g.root_a):
            raise AssertionError("Lagom: root_a resolve returned wrong type")
        return root

    def get_root_b() -> Any:
        root = container[g.root_b]
        if not isinstance(root, g.root_b):
            raise AssertionError("Lagom: root_b resolve returned wrong type")
        return root

    def spellspace_cycle() -> None:
        with container.temporary_singletons(list(g.spellspace_classes)) as space:
            r1 = space[g.spellspace_root]
            r2 = space[g.spellspace_root]
            if not isinstance(r1, g.spellspace_root):
                raise AssertionError("Lagom: spellspace root resolve returned wrong type")
            if r1 is not r2:
                raise AssertionError("Lagom: spellspace root not cached within spellspace")

    def spellspace_enter() -> Any:
        ctx = container.temporary_singletons(list(g.spellspace_classes))
        scope = ctx.__enter__()
        return ctx, scope

    def spellspace_resolve(handle: Any) -> Any:
        _, space = handle
        root = space[g.spellspace_root]
        if not isinstance(root, g.spellspace_root):
            raise AssertionError("Lagom: spellspace root resolve returned wrong type")
        return root

    def spellspace_exit(handle: Any) -> None:
        ctx, _ = handle
        ctx.__exit__(None, None, None)

    def cleanup() -> None:
        gc.collect()

    return _RuntimeOps(
        name="lagom",
        get_root_a=get_root_a,
        get_root_b=get_root_b,
        spellspace_cycle=spellspace_cycle,
        spellspace_enter=spellspace_enter,
        spellspace_resolve=spellspace_resolve,
        spellspace_exit=spellspace_exit,
        cleanup=cleanup,
    )


@dataclass
class _InjectorState:
    injector: Any
    spellspace_scope_type: type
    original_inits: dict[type, Any]


def _build_runtime_injector(g: _GraphSpec) -> _RuntimeOps:
    pytest.importorskip("injector")
    from injector import Binder, Injector, Module, Scope, ScopeDecorator, InstanceProvider, inject

    all_classes: list[type] = []
    seen: set[type] = set()
    for cls in g.root_a_classes + g.root_b_classes + g.spellspace_classes:
        if cls not in seen:
            all_classes.append(cls)
            seen.add(cls)

    original_inits: dict[type, Any] = {}
    for cls in all_classes:
        original_inits[cls] = cls.__init__
        cls.__init__ = inject(cls.__init__)

    cache_var: contextvars.ContextVar[dict[Any, Any] | None] = contextvars.ContextVar(
        "di_thread_spellspace_cache", default=None
    )

    class SpellspaceScope(Scope):
        @contextlib.contextmanager
        def enter(self) -> Any:
            token = cache_var.set({})
            try:
                yield
            finally:
                cache_var.reset(token)

        def get(self, key: Any, provider: Any) -> Any:
            cache = cache_var.get()
            if cache is None:
                return provider
            existing = cache.get(key)
            if existing is not None:
                return existing
            instance = provider.get(self.injector)
            wrapped = InstanceProvider(instance)
            cache[key] = wrapped
            return wrapped

    spellspace = ScopeDecorator(SpellspaceScope)
    space_types = set(g.spellspace_classes)

    class PerfModule(Module):
        def configure(self, binder: Binder) -> None:
            for cls in all_classes:
                if cls in space_types:
                    binder.bind(cls, to=cls, scope=spellspace)
                else:
                    binder.bind(cls, to=cls)

    injector = Injector([PerfModule()])

    state = _InjectorState(
        injector=injector,
        spellspace_scope_type=SpellspaceScope,
        original_inits=original_inits,
    )

    def get_root_a() -> Any:
        root = state.injector.get(g.root_a)
        if not isinstance(root, g.root_a):
            raise AssertionError("Injector: root_a resolve returned wrong type")
        return root

    def get_root_b() -> Any:
        root = state.injector.get(g.root_b)
        if not isinstance(root, g.root_b):
            raise AssertionError("Injector: root_b resolve returned wrong type")
        return root

    def spellspace_cycle() -> None:
        scope = state.injector.get(state.spellspace_scope_type)
        with scope.enter():
            r1 = state.injector.get(g.spellspace_root)
            r2 = state.injector.get(g.spellspace_root)
            if not isinstance(r1, g.spellspace_root):
                raise AssertionError("Injector: spellspace root resolve returned wrong type")
            if r1 is not r2:
                raise AssertionError("Injector: spellspace root not cached within spellspace")

    def spellspace_enter() -> Any:
        scope = state.injector.get(state.spellspace_scope_type)
        ctx = scope.enter()
        ctx.__enter__()
        return ctx

    def spellspace_resolve(handle: Any) -> Any:
        root = state.injector.get(g.spellspace_root)
        if not isinstance(root, g.spellspace_root):
            raise AssertionError("Injector: spellspace root resolve returned wrong type")
        return root

    def spellspace_exit(handle: Any) -> None:
        handle.__exit__(None, None, None)

    def cleanup() -> None:
        for cls, orig in state.original_inits.items():
            cls.__init__ = orig
        gc.collect()

    return _RuntimeOps(
        name="injector",
        get_root_a=get_root_a,
        get_root_b=get_root_b,
        spellspace_cycle=spellspace_cycle,
        spellspace_enter=spellspace_enter,
        spellspace_resolve=spellspace_resolve,
        spellspace_exit=spellspace_exit,
        cleanup=cleanup,
    )


def _build_runtime_dishka(g: _GraphSpec) -> _RuntimeOps:
    pytest.importorskip("dishka")
    from dishka import Provider, Scope, make_container

    all_classes: list[type] = []
    seen: set[type] = set()
    for cls in g.root_a_classes + g.root_b_classes + g.spellspace_classes:
        if cls not in seen:
            all_classes.append(cls)
            seen.add(cls)

    provider = Provider()
    space_types = set(g.spellspace_classes)

    for cls in all_classes:
        if cls in space_types:
            provider.provide(cls, scope=Scope.REQUEST, cache=True)
        else:
            provider.provide(cls, scope=Scope.APP, cache=False)

    container = make_container(provider)

    def get_root_a() -> Any:
        root = container.get(g.root_a)
        if not isinstance(root, g.root_a):
            raise AssertionError("Dishka: root_a resolve returned wrong type")
        return root

    def get_root_b() -> Any:
        root = container.get(g.root_b)
        if not isinstance(root, g.root_b):
            raise AssertionError("Dishka: root_b resolve returned wrong type")
        return root

    def spellspace_cycle() -> None:
        with container() as request_container:
            r1 = request_container.get(g.spellspace_root)
            r2 = request_container.get(g.spellspace_root)
            if not isinstance(r1, g.spellspace_root):
                raise AssertionError("Dishka: spellspace root resolve returned wrong type")
            if r1 is not r2:
                raise AssertionError("Dishka: spellspace root not cached within spellspace")

    def spellspace_enter() -> Any:
        ctx = container()
        request_container = ctx.__enter__()
        return ctx, request_container

    def spellspace_resolve(handle: Any) -> Any:
        _, request_container = handle
        root = request_container.get(g.spellspace_root)
        if not isinstance(root, g.spellspace_root):
            raise AssertionError("Dishka: spellspace root resolve returned wrong type")
        return root

    def spellspace_exit(handle: Any) -> None:
        ctx, _ = handle
        ctx.__exit__(None, None, None)

    def cleanup() -> None:
        container.close()
        gc.collect()

    return _RuntimeOps(
        name="dishka",
        get_root_a=get_root_a,
        get_root_b=get_root_b,
        spellspace_cycle=spellspace_cycle,
        spellspace_enter=spellspace_enter,
        spellspace_resolve=spellspace_resolve,
        spellspace_exit=spellspace_exit,
        cleanup=cleanup,
    )


def _build_runtime_melder(g: _GraphSpec) -> _RuntimeOps:
    from melder import Aether, Conduit, Existence, Spellbook

    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether

    spellbook = Spellbook(aetheric_frame="threaded-di-stress")
    cfg = spellbook.get_configuration()
    cfg.set_property("phase_scheduler_workers_per_spellbook", 1)

    ids_a: dict[type, str] = {}
    for cls in g.root_a_classes:
        ids_a[cls] = spellbook.bind(spell=cls, existence=Existence.many, permissions="create")

    ids_b: dict[type, str] = {}
    for cls in g.root_b_classes:
        if cls in ids_a:
            continue
        ids_b[cls] = spellbook.bind(spell=cls, existence=Existence.many, permissions="create")

    ids_space: dict[type, str] = {}
    for cls in g.spellspace_classes:
        if cls in ids_a or cls in ids_b:
            continue
        ids_space[cls] = spellbook.bind(
            spell=cls,
            existence=Existence.unique_per_spell_space,
            permissions="create",
        )

    root_a_id = ids_a.get(g.root_a)
    if root_a_id is None:
        raise AssertionError("Melder: missing root_a id")

    root_b_id = ids_b.get(g.root_b) or ids_a.get(g.root_b)
    if root_b_id is None:
        raise AssertionError("Melder: missing root_b id")

    root_space_id = ids_space.get(g.spellspace_root) or ids_a.get(g.spellspace_root) or ids_b.get(g.spellspace_root)
    if root_space_id is None:
        raise AssertionError("Melder: missing spellspace root id")

    conduit = spellbook.conjure(name="threaded-di-stress")

    def get_root_a() -> Any:
        root = conduit.meld(spell=root_a_id)
        if not isinstance(root, g.root_a):
            raise AssertionError("Melder: root_a meld returned wrong type")
        return root

    def get_root_b() -> Any:
        root = conduit.meld(spell=root_b_id)
        if not isinstance(root, g.root_b):
            raise AssertionError("Melder: root_b meld returned wrong type")
        return root

    def spellspace_cycle() -> None:
        with conduit.enter_spellspace() as space:
            r1 = space.meld(spell=root_space_id)
            r2 = space.meld(spell=root_space_id)
            if not isinstance(r1, g.spellspace_root):
                raise AssertionError("Melder: spellspace root meld returned wrong type")
            if r1 is not r2:
                raise AssertionError("Melder: spellspace root not cached within spellspace")

    def spellspace_enter() -> Any:
        ctx = conduit.enter_spellspace()
        space = ctx.__enter__()
        return ctx, space

    def spellspace_resolve(handle: Any) -> Any:
        _, space = handle
        root = space.meld(spell=root_space_id)
        if not isinstance(root, g.spellspace_root):
            raise AssertionError("Melder: spellspace root meld returned wrong type")
        return root

    def spellspace_exit(handle: Any) -> None:
        ctx, _ = handle
        ctx.__exit__(None, None, None)

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
        get_root_a=get_root_a,
        get_root_b=get_root_b,
        spellspace_cycle=spellspace_cycle,
        spellspace_enter=spellspace_enter,
        spellspace_resolve=spellspace_resolve,
        spellspace_exit=spellspace_exit,
        cleanup=cleanup,
    )


def _build_ops(lib: str, g: _GraphSpec) -> _RuntimeOps:
    if lib == "dependency-injector":
        return _build_runtime_dependency_injector(g)
    if lib == "lagom":
        return _build_runtime_lagom(g)
    if lib == "injector":
        return _build_runtime_injector(g)
    if lib == "dishka":
        return _build_runtime_dishka(g)
    if lib == "melder":
        return _build_runtime_melder(g)
    raise AssertionError(f"Unknown lib: {lib}")


# ======================================================================================
# Rotation runtime builders (one container per lib, union of all graphs)
# ======================================================================================


def _build_rotation_dependency_injector(graphs: list[_GraphSpec]) -> _RotationOps:
    pytest.importorskip("dependency_injector")
    from dependency_injector import providers

    all_classes = _union_classes(graphs)
    space_types = _union_spellspace_types(graphs)

    providers_by_type: dict[type, Any] = {}

    for cls in all_classes:
        param_specs = _ctor_param_types(cls)
        kwargs: dict[str, Any] = {}
        for pname, ptype in param_specs:
            dep = providers_by_type.get(ptype)
            if dep is None:
                raise AssertionError(f"DI wiring error: {cls.__name__} depends on {ptype.__name__} before registered")
            kwargs[pname] = dep

        if cls in space_types:
            prov = providers.ContextLocalSingleton(cls, **kwargs)
        else:
            prov = providers.Factory(cls, **kwargs)

        providers_by_type[cls] = prov

    def get_root_a(ix: int) -> Any:
        g = graphs[ix]
        root = providers_by_type[g.root_a]()
        if not isinstance(root, g.root_a):
            raise AssertionError("Dependency Injector: root_a resolve returned wrong type")
        return root

    def get_root_b(ix: int) -> Any:
        g = graphs[ix]
        root = providers_by_type[g.root_b]()
        if not isinstance(root, g.root_b):
            raise AssertionError("Dependency Injector: root_b resolve returned wrong type")
        return root

    def spellspace_cycle(ix: int) -> None:
        g = graphs[ix]
        ctx = contextvars.Context()

        def run() -> None:
            r1 = providers_by_type[g.spellspace_root]()
            r2 = providers_by_type[g.spellspace_root]()
            if not isinstance(r1, g.spellspace_root):
                raise AssertionError("Dependency Injector: spellspace root resolve returned wrong type")
            if r1 is not r2:
                raise AssertionError("Dependency Injector: spellspace root not cached within spellspace")

        ctx.run(run)

    def cleanup() -> None:
        for prov in providers_by_type.values():
            reset = getattr(prov, "reset", None)
            if reset is not None:
                reset()
        gc.collect()

    return _RotationOps(
        name="dependency-injector",
        graphs=graphs,
        get_root_a=get_root_a,
        get_root_b=get_root_b,
        spellspace_cycle=spellspace_cycle,
        cleanup=cleanup,
    )


def _build_rotation_lagom(graphs: list[_GraphSpec]) -> _RotationOps:
    pytest.importorskip("lagom")
    from lagom import Container

    container = Container()
    all_classes = _union_classes(graphs)

    def _make_leaf_factory(_cls: type) -> Callable[[], Any]:
        def factory() -> Any:
            return _cls()
        return factory

    def _make_factory(_cls: type, _specs: tuple[tuple[str, type], ...]) -> Callable[[Any], Any]:
        def factory(c: Any) -> Any:
            kwargs = {pname: c[ptype] for pname, ptype in _specs}
            return _cls(**kwargs)
        return factory

    for cls in all_classes:
        specs = _ctor_param_types(cls)
        if not specs:
            container[cls] = _make_leaf_factory(cls)
        else:
            container[cls] = _make_factory(cls, specs)

    def get_root_a(ix: int) -> Any:
        g = graphs[ix]
        root = container[g.root_a]
        if not isinstance(root, g.root_a):
            raise AssertionError("Lagom: root_a resolve returned wrong type")
        return root

    def get_root_b(ix: int) -> Any:
        g = graphs[ix]
        root = container[g.root_b]
        if not isinstance(root, g.root_b):
            raise AssertionError("Lagom: root_b resolve returned wrong type")
        return root

    def spellspace_cycle(ix: int) -> None:
        g = graphs[ix]
        with container.temporary_singletons(list(g.spellspace_classes)) as space:
            r1 = space[g.spellspace_root]
            r2 = space[g.spellspace_root]
            if not isinstance(r1, g.spellspace_root):
                raise AssertionError("Lagom: spellspace root resolve returned wrong type")
            if r1 is not r2:
                raise AssertionError("Lagom: spellspace root not cached within spellspace")

    def cleanup() -> None:
        gc.collect()

    return _RotationOps(
        name="lagom",
        graphs=graphs,
        get_root_a=get_root_a,
        get_root_b=get_root_b,
        spellspace_cycle=spellspace_cycle,
        cleanup=cleanup,
    )


def _build_rotation_injector(graphs: list[_GraphSpec]) -> _RotationOps:
    pytest.importorskip("injector")
    from injector import Binder, Injector, Module, Scope, ScopeDecorator, InstanceProvider, inject

    all_classes = _union_classes(graphs)
    space_types = _union_spellspace_types(graphs)

    # Patch constructors so Injector performs ctor injection.
    original_inits: dict[type, Any] = {}
    for cls in all_classes:
        original_inits[cls] = cls.__init__
        cls.__init__ = inject(cls.__init__)

    cache_var: contextvars.ContextVar[dict[Any, Any] | None] = contextvars.ContextVar(
        "di_thread_spellspace_cache", default=None
    )

    class SpellspaceScope(Scope):
        @contextlib.contextmanager
        def enter(self) -> Any:
            token = cache_var.set({})
            try:
                yield
            finally:
                cache_var.reset(token)

        def get(self, key: Any, provider: Any) -> Any:
            cache = cache_var.get()
            if cache is None:
                return provider
            existing = cache.get(key)
            if existing is not None:
                return existing
            instance = provider.get(self.injector)
            wrapped = InstanceProvider(instance)
            cache[key] = wrapped
            return wrapped

    spellspace = ScopeDecorator(SpellspaceScope)

    class PerfModule(Module):
        def configure(self, binder: Binder) -> None:
            for cls in all_classes:
                if cls in space_types:
                    binder.bind(cls, to=cls, scope=spellspace)
                else:
                    binder.bind(cls, to=cls)

    injector = Injector([PerfModule()])

    def get_root_a(ix: int) -> Any:
        g = graphs[ix]
        root = injector.get(g.root_a)
        if not isinstance(root, g.root_a):
            raise AssertionError("Injector: root_a resolve returned wrong type")
        return root

    def get_root_b(ix: int) -> Any:
        g = graphs[ix]
        root = injector.get(g.root_b)
        if not isinstance(root, g.root_b):
            raise AssertionError("Injector: root_b resolve returned wrong type")
        return root

    def spellspace_cycle(ix: int) -> None:
        g = graphs[ix]
        scope = injector.get(SpellspaceScope)
        with scope.enter():
            r1 = injector.get(g.spellspace_root)
            r2 = injector.get(g.spellspace_root)
            if not isinstance(r1, g.spellspace_root):
                raise AssertionError("Injector: spellspace root resolve returned wrong type")
            if r1 is not r2:
                raise AssertionError("Injector: spellspace root not cached within spellspace")

    def cleanup() -> None:
        for cls, orig in original_inits.items():
            cls.__init__ = orig
        gc.collect()

    return _RotationOps(
        name="injector",
        graphs=graphs,
        get_root_a=get_root_a,
        get_root_b=get_root_b,
        spellspace_cycle=spellspace_cycle,
        cleanup=cleanup,
    )


def _build_rotation_dishka(graphs: list[_GraphSpec]) -> _RotationOps:
    pytest.importorskip("dishka")
    from dishka import Provider, Scope, make_container

    all_classes = _union_classes(graphs)
    space_types = _union_spellspace_types(graphs)

    provider = Provider()
    for cls in all_classes:
        if cls in space_types:
            provider.provide(cls, scope=Scope.REQUEST, cache=True)
        else:
            provider.provide(cls, scope=Scope.APP, cache=False)

    container = make_container(provider)

    def get_root_a(ix: int) -> Any:
        g = graphs[ix]
        root = container.get(g.root_a)
        if not isinstance(root, g.root_a):
            raise AssertionError("Dishka: root_a resolve returned wrong type")
        return root

    def get_root_b(ix: int) -> Any:
        g = graphs[ix]
        root = container.get(g.root_b)
        if not isinstance(root, g.root_b):
            raise AssertionError("Dishka: root_b resolve returned wrong type")
        return root

    def spellspace_cycle(ix: int) -> None:
        g = graphs[ix]
        with container() as request_container:
            r1 = request_container.get(g.spellspace_root)
            r2 = request_container.get(g.spellspace_root)
            if not isinstance(r1, g.spellspace_root):
                raise AssertionError("Dishka: spellspace root resolve returned wrong type")
            if r1 is not r2:
                raise AssertionError("Dishka: spellspace root not cached within spellspace")

    def cleanup() -> None:
        container.close()
        gc.collect()

    return _RotationOps(
        name="dishka",
        graphs=graphs,
        get_root_a=get_root_a,
        get_root_b=get_root_b,
        spellspace_cycle=spellspace_cycle,
        cleanup=cleanup,
    )


def _build_rotation_melder(graphs: list[_GraphSpec]) -> _RotationOps:
    from melder import Aether, Conduit, Existence, Spellbook

    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether

    spellbook = Spellbook(aetheric_frame="threaded-di-stress-rotation")
    cfg = spellbook.get_configuration()
    cfg.set_property("phase_scheduler_workers_per_spellbook", 1)

    # Bind everything once
    all_classes = _union_classes(graphs)
    space_types = _union_spellspace_types(graphs)

    spell_ids: dict[type, str] = {}

    # Bind spellspace-scoped first
    for cls in all_classes:
        if cls not in space_types:
            continue
        spell_ids[cls] = spellbook.bind(
            spell=cls,
            existence=Existence.unique_per_spell_space,
            permissions="create",
        )

    # Bind transient rest
    for cls in all_classes:
        if cls in spell_ids:
            continue
        spell_ids[cls] = spellbook.bind(
            spell=cls,
            existence=Existence.many,
            permissions="create",
        )

    # Resolve root ids per graph
    root_a_ids: list[str] = []
    root_b_ids: list[str] = []
    space_root_ids: list[str] = []

    for g in graphs:
        ra = spell_ids.get(g.root_a)
        rb = spell_ids.get(g.root_b)
        rs = spell_ids.get(g.spellspace_root)
        if ra is None or rb is None or rs is None:
            raise AssertionError("Melder rotation: missing spell ids for graph")
        root_a_ids.append(ra)
        root_b_ids.append(rb)
        space_root_ids.append(rs)

    conduit = spellbook.conjure(name="threaded-di-stress-rotation")

    def get_root_a(ix: int) -> Any:
        g = graphs[ix]
        root = conduit.meld(spell=root_a_ids[ix])
        if not isinstance(root, g.root_a):
            raise AssertionError("Melder: root_a meld returned wrong type")
        return root

    def get_root_b(ix: int) -> Any:
        g = graphs[ix]
        root = conduit.meld(spell=root_b_ids[ix])
        if not isinstance(root, g.root_b):
            raise AssertionError("Melder: root_b meld returned wrong type")
        return root

    def spellspace_cycle(ix: int) -> None:
        g = graphs[ix]
        with conduit.enter_spellspace() as space:
            r1 = space.meld(spell=space_root_ids[ix])
            r2 = space.meld(spell=space_root_ids[ix])
            if not isinstance(r1, g.spellspace_root):
                raise AssertionError("Melder: spellspace root meld returned wrong type")
            if r1 is not r2:
                raise AssertionError("Melder: spellspace root not cached within spellspace")

    def cleanup() -> None:
        try:
            conduit.cleanup()
        finally:
            Aether._reset_singleton_for_tests()
            aether2 = Aether()
            Spellbook._aether = aether2
            Conduit._aether = aether2
        gc.collect()

    return _RotationOps(
        name="melder",
        graphs=graphs,
        get_root_a=get_root_a,
        get_root_b=get_root_b,
        spellspace_cycle=spellspace_cycle,
        cleanup=cleanup,
    )


def _build_rotation_ops(lib: str, graphs: list[_GraphSpec]) -> _RotationOps:
    if lib == "dependency-injector":
        return _build_rotation_dependency_injector(graphs)
    if lib == "lagom":
        return _build_rotation_lagom(graphs)
    if lib == "injector":
        return _build_rotation_injector(graphs)
    if lib == "dishka":
        return _build_rotation_dishka(graphs)
    if lib == "melder":
        return _build_rotation_melder(graphs)
    raise AssertionError(f"Unknown lib: {lib}")


# ======================================================================================
# Smoke + single resolve tests
# ======================================================================================


@pytest.mark.parametrize("graph", [g.name for g in _selected_graphs()])
@pytest.mark.parametrize("lib", _selected_libs())
def test_single_resolve_smoke(graph: str, lib: str) -> None:
    gspecs = {g.name: g for g in _selected_graphs()}
    g = gspecs[graph]
    ops = _build_ops(lib, g)
    _maybe_print_gil_status(f"{ops.name}/smoke")
    try:
        r1 = ops.get_root_a()
        r2 = ops.get_root_b()
        assert isinstance(r1, g.root_a)
        assert isinstance(r2, g.root_b)
        ops.spellspace_cycle()
    finally:
        ops.cleanup()


@pytest.mark.parametrize("graph", [g.name for g in _selected_graphs()])
@pytest.mark.parametrize("lib", _selected_libs())
def test_single_resolve_timings(graph: str, lib: str) -> None:
    if not _env_bool("DI_RUN_SINGLE", True):
        pytest.skip("DI_RUN_SINGLE not enabled")

    gspecs = {g.name: g for g in _selected_graphs()}
    g = gspecs[graph]
    ops = _build_ops(lib, g)
    _maybe_print_gil_status(f"{ops.name}/single")
    avg_iters = _env_int_nonneg("DI_SINGLE_AVG_ITERS", 1000)
    warmup_iters = _env_int_nonneg("DI_SINGLE_AVG_WARMUP_ITERS", 100)
    if avg_iters <= 0:
        raise AssertionError("DI_SINGLE_AVG_ITERS must be > 0")

    try:
        for _ in range(warmup_iters):
            ops.get_root_a()
            ops.get_root_b()
            ops.spellspace_cycle()

        avg_a_ns = _average_call_ns(ops.get_root_a, iters=avg_iters)
        avg_b_ns = _average_call_ns(ops.get_root_b, iters=avg_iters)
        avg_spellspace_build_ns, avg_spellspace_first_ns, avg_spellspace_cached_ns, avg_spellspace_exit_ns, avg_spellspace_total_ns = (
            _average_spellspace_metrics_ns(
                enter_scope=ops.spellspace_enter,
                resolve_in_scope=ops.spellspace_resolve,
                exit_scope=ops.spellspace_exit,
                iters=avg_iters,
            )
        )

        print(
            f"[{ops.name}] single ({g.name}) "
            f"A avg({avg_iters})={avg_a_ns/1_000.0:.2f}us | "
            f"B avg({avg_iters})={avg_b_ns/1_000.0:.2f}us | "
            f"build avg({avg_iters})={avg_spellspace_build_ns/1_000.0:.2f}us | "
            f"spellspace first meld avg({avg_iters})={avg_spellspace_first_ns/1_000.0:.2f}us | "
            f"spellspace cached meld avg({avg_iters})={avg_spellspace_cached_ns/1_000.0:.2f}us | "
            f"exit avg({avg_iters})={avg_spellspace_exit_ns/1_000.0:.2f}us | "
            f"total avg({avg_iters})={avg_spellspace_total_ns/1_000.0:.2f}us"
        )
    finally:
        ops.cleanup()


# ======================================================================================
# Rotation stress (DEFAULT)
# ======================================================================================


@pytest.mark.timeout(420)
@pytest.mark.parametrize("lib", _selected_libs())
def test_threaded_di_stress_rotation_all_graphs(lib: str) -> None:
    """
    Runs ALL selected graphs in a single rotation loop per lib.

    This is what you asked for: one run that cycles solo/shallow/wide/diamond/deep continuously.
    """
    if not _env_bool("DI_RUN_ROTATION", True):
        pytest.skip("DI_RUN_ROTATION disabled")

    graphs = _selected_graphs()
    if not graphs:
        raise AssertionError("No graphs selected")

    cfg = _StressConfig.from_env()

    if cfg.threads <= 0:
        raise AssertionError("DI_THREADS must be > 0")
    if cfg.duration_s <= 0:
        raise AssertionError("DI_DURATION_S must be > 0")
    if cfg.spellspace_every <= 0:
        raise AssertionError("DI_SPELLSPACE_EVERY must be > 0")
    if cfg.gc_every <= 0:
        raise AssertionError("DI_GC_EVERY must be > 0")
    if cfg.pattern not in ("alternating", "burst", "ratio", "random"):
        raise AssertionError("DI_PATTERN must be: alternating|burst|ratio|random")
    if cfg.gc_mode not in ("periodic", "disabled", "none"):
        raise AssertionError("DI_GC_MODE must be: periodic|disabled|none")
    if not (0.0 <= cfg.ratio_p <= 1.0):
        raise AssertionError("DI_RATIO_P must be between 0 and 1")

    ops = _build_rotation_ops(lib, graphs)
    _warmup_rotation_ops(ops, iters=cfg.warmup_iters)
    _maybe_print_gil_status(ops.name)

    gcount = len(graphs)
    stats: list[_ThreadStats] = [
        _ThreadStats(g_steps=[0] * gcount, g_a=[0] * gcount, g_b=[0] * gcount)
        for _ in range(cfg.threads)
    ]
    errors: list[BaseException] = []
    stop_event = threading.Event()
    start_barrier = threading.Barrier(cfg.threads + 1)
    stop_time_holder: list[float] = [0.0]
    selector_seed = cfg.random_seed

    def worker(ix: int) -> None:
        try:
            was_enabled = gc.isenabled()
            if cfg.gc_mode == "disabled" and was_enabled:
                gc.deactivate()

            try:
                start_barrier.wait()
                stop_at = stop_time_holder[0]

                local_i = 0
                local_stats = stats[ix]

                rng: Optional[random.Random]
                if cfg.pattern in ("ratio", "random"):
                    rng = random.Random(selector_seed + ix)
                else:
                    rng = None

                selector = _WorkSelector(
                    pattern=cfg.pattern,
                    burst_len=cfg.burst_len,
                    ratio_p=cfg.ratio_p,
                    rng=rng,
                )

                while not stop_event.is_set() and time.perf_counter() < stop_at:
                    gix = local_i % gcount
                    g = graphs[gix]
                    do_a = selector.choose_a(local_i)

                    if do_a:
                        root = ops.get_root_a(gix)
                        if not isinstance(root, g.root_a):
                            raise AssertionError("Rotation: resolved root_a wrong type")
                        local_stats.g_a[gix] += 1
                    else:
                        root = ops.get_root_b(gix)
                        if not isinstance(root, g.root_b):
                            raise AssertionError("Rotation: resolved root_b wrong type")
                        local_stats.g_b[gix] += 1

                    local_stats.steps += 1
                    local_stats.g_steps[gix] += 1
                    local_i += 1

                    if (local_i % cfg.spellspace_every) == 0:
                        ops.spellspace_cycle(gix)
                        local_stats.spellspaces += 1

                    # Across-resolve transient anti-cache (only for graphs that supply transient_probe)
                    if cfg.validate_transient_every > 0 and g.transient_probe is not None:
                        if (local_i % cfg.validate_transient_every) == 0:
                            r1 = ops.get_root_a(gix)
                            r2 = ops.get_root_a(gix)
                            o11, o12 = g.transient_probe(r1)
                            o21, o22 = g.transient_probe(r2)
                            if o11 is o21 or o12 is o22:
                                raise AssertionError("Rotation transient probe failed: cached transient subtree detected")

                    # Within-resolve transient anti-dedupe (diamond-style)
                    if cfg.validate_within_every > 0 and g.within_resolve_probe is not None:
                        if (local_i % cfg.validate_within_every) == 0:
                            r = ops.get_root_a(gix)
                            x, y = g.within_resolve_probe(r)
                            if g.within_resolve_expect_distinct and (x is y):
                                raise AssertionError("Rotation within-resolve probe failed: transient dedupe detected")

                    if cfg.gc_mode == "periodic":
                        if (local_i % cfg.gc_every) == 0:
                            gc.collect()

            finally:
                if cfg.gc_mode == "disabled" and was_enabled:
                    gc.activate()

        except BaseException as e:
            local_stats = stats[ix]
            local_stats.errors += 1
            errors.append(e)
            stop_event.set()

    threads_list: list[threading.Thread] = []
    for i in range(cfg.threads):
        t = threading.Thread(target=worker, args=(i,), daemon=True)
        threads_list.append(t)
        t.start()

    start_barrier.wait()
    start_t = time.perf_counter()
    stop_time_holder[0] = start_t + cfg.duration_s

    for t in threads_list:
        t.join()

    elapsed_s = time.perf_counter() - start_t
    try:
        if errors:
            raise errors[0]

        total_steps = sum(s.steps for s in stats)
        total_spaces = sum(s.spellspaces for s in stats)
        total_err = sum(s.errors for s in stats)
        steps_per_s = total_steps / elapsed_s if elapsed_s > 0 else 0.0

        per_graph_steps = [0] * gcount
        per_graph_a = [0] * gcount
        per_graph_b = [0] * gcount
        for s in stats:
            for i in range(gcount):
                per_graph_steps[i] += s.g_steps[i]
                per_graph_a[i] += s.g_a[i]
                per_graph_b[i] += s.g_b[i]

        per_graph_summary = ", ".join(
            f"{graphs[i].name}:{per_graph_steps[i]}"
            for i in range(gcount)
        )

        print(
            f"[{ops.name}] ROTATION: "
            f"threads={cfg.threads}, duration={elapsed_s:.2f}s, "
            f"steps={total_steps}, steps/s={steps_per_s:,.0f}, "
            f"spellspaces={total_spaces}, errors={total_err}, "
            f"per_graph=({per_graph_summary})"
        )

    finally:
        ops.cleanup()


# ======================================================================================
# Per-graph stress (optional)
# ======================================================================================


@pytest.mark.timeout(420)
@pytest.mark.parametrize("graph", [g.name for g in _selected_graphs()])
@pytest.mark.parametrize("lib", _selected_libs())
def test_threaded_di_stress_per_graph(graph: str, lib: str) -> None:
    """
    Old per-graph run, still available.

    Enable with:
        DI_RUN_PER_GRAPH=1
    """
    if not _env_bool("DI_RUN_PER_GRAPH", True):
        pytest.skip("DI_RUN_PER_GRAPH disabled")

    gspecs = {g.name: g for g in _selected_graphs()}
    g = gspecs[graph]
    cfg = _StressConfig.from_env()

    ops = _build_ops(lib, g)
    _warmup_ops(ops, iters=cfg.warmup_iters)
    _maybe_print_gil_status(ops.name)

    stats: list[_ThreadStats] = [_ThreadStats() for _ in range(cfg.threads)]
    errors: list[BaseException] = []
    stop_event = threading.Event()
    start_barrier = threading.Barrier(cfg.threads + 1)
    stop_time_holder: list[float] = [0.0]
    selector_seed = cfg.random_seed

    def worker(ix: int) -> None:
        try:
            was_enabled = gc.isenabled()
            if cfg.gc_mode == "disabled" and was_enabled:
                gc.deactivate()

            try:
                start_barrier.wait()
                stop_at = stop_time_holder[0]

                local_i = 0
                local_stats = stats[ix]

                rng: Optional[random.Random]
                if cfg.pattern in ("ratio", "random"):
                    rng = random.Random(selector_seed + ix)
                else:
                    rng = None

                selector = _WorkSelector(
                    pattern=cfg.pattern,
                    burst_len=cfg.burst_len,
                    ratio_p=cfg.ratio_p,
                    rng=rng,
                )

                while not stop_event.is_set() and time.perf_counter() < stop_at:
                    do_a = selector.choose_a(local_i)

                    if do_a:
                        root = ops.get_root_a()
                        if not isinstance(root, g.root_a):
                            raise AssertionError("Resolved root_a returned wrong type")
                    else:
                        root = ops.get_root_b()
                        if not isinstance(root, g.root_b):
                            raise AssertionError("Resolved root_b returned wrong type")

                    local_stats.steps += 1
                    local_i += 1

                    if (local_i % cfg.spellspace_every) == 0:
                        ops.spellspace_cycle()
                        local_stats.spellspaces += 1

                    if cfg.gc_mode == "periodic":
                        if (local_i % cfg.gc_every) == 0:
                            gc.collect()

            finally:
                if cfg.gc_mode == "disabled" and was_enabled:
                    gc.activate()

        except BaseException as e:
            stats[ix].errors += 1
            errors.append(e)
            stop_event.set()

    threads_list: list[threading.Thread] = []
    for i in range(cfg.threads):
        t = threading.Thread(target=worker, args=(i,), daemon=True)
        threads_list.append(t)
        t.start()

    start_barrier.wait()
    start_t = time.perf_counter()
    stop_time_holder[0] = start_t + cfg.duration_s

    for t in threads_list:
        t.join()

    elapsed_s = time.perf_counter() - start_t
    try:
        if errors:
            raise errors[0]

        total_steps = sum(s.steps for s in stats)
        total_spaces = sum(s.spellspaces for s in stats)
        total_err = sum(s.errors for s in stats)
        steps_per_s = total_steps / elapsed_s if elapsed_s > 0 else 0.0

        print(
            f"[{ops.name}] per-graph ({g.name}): "
            f"threads={cfg.threads}, duration={elapsed_s:.2f}s, "
            f"steps={total_steps}, steps/s={steps_per_s:,.0f}, "
            f"spellspaces={total_spaces}, errors={total_err}"
        )
    finally:
        ops.cleanup()
