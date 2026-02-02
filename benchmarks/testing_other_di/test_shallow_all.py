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

# ======================================================================================
# Extra shallow/wide/diamond graphs (local mocks)
# ======================================================================================


# ---- SOLO (no dependencies) ---------------------------------------------------------


class SoloRootA:
    __slots__ = ()


class SoloRootB:
    __slots__ = ()


class SoloSpaceRoot:
    __slots__ = ()


# ---- SHALLOW (depth-2: root -> leaves) ----------------------------------------------


class ShallowLeafA:
    __slots__ = ()


class ShallowLeafB:
    __slots__ = ()


class ShallowRootAB:
    __slots__ = ("a", "b")

    def __init__(self, a: ShallowLeafA, b: ShallowLeafB) -> None:
        self.a = a
        self.b = b


class ShallowLeafC:
    __slots__ = ()


class ShallowRootC:
    __slots__ = ("c",)

    def __init__(self, c: ShallowLeafC) -> None:
        self.c = c


class ShallowSpaceLeaf:
    __slots__ = ()


class ShallowSpaceRoot:
    __slots__ = ("leaf",)

    def __init__(self, leaf: ShallowSpaceLeaf) -> None:
        self.leaf = leaf


# ---- WIDE (one root has many inputs) ------------------------------------------------
# Wide8 is intentionally "wide shallow": root has 8 leaf params (arity > CALL3)
# Wide9 is intentionally "wide grouped": 3 groups of 3 leaves (arity <= CALL3 everywhere)


class Wide8Leaf0:
    __slots__ = ()


class Wide8Leaf1:
    __slots__ = ()


class Wide8Leaf2:
    __slots__ = ()


class Wide8Leaf3:
    __slots__ = ()


class Wide8Leaf4:
    __slots__ = ()


class Wide8Leaf5:
    __slots__ = ()


class Wide8Leaf6:
    __slots__ = ()


class Wide8Leaf7:
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


class Wide9Leaf0:
    __slots__ = ()


class Wide9Leaf1:
    __slots__ = ()


class Wide9Leaf2:
    __slots__ = ()


class Wide9Leaf3:
    __slots__ = ()


class Wide9Leaf4:
    __slots__ = ()


class Wide9Leaf5:
    __slots__ = ()


class Wide9Leaf6:
    __slots__ = ()


class Wide9Leaf7:
    __slots__ = ()


class Wide9Leaf8:
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


class WideSpaceLeaf:
    __slots__ = ()


class WideSpaceRoot:
    __slots__ = ("leaf",)

    def __init__(self, leaf: WideSpaceLeaf) -> None:
        self.leaf = leaf


# ---- DIAMOND (shared dependency requested multiple times) ----------------------------
# This is the one that can reveal "within-resolve dedupe" for transients.


class DiamondSharedLeaf:
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


class DiamondSpaceLeaf:
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
        - Must work even when annotations are deferred/strings (free-threading builds, future annotations, etc.)
        - Raises AssertionError if any parameter lacks a resolvable concrete type.
    """
    sig = inspect.signature(cls.__init__)
    params = list(sig.parameters.values())[1:]  # skip self

    try:
        hints = typing.get_type_hints(cls.__init__, include_extras=True)
    except Exception:
        hints = getattr(cls.__init__, "__annotations__", {}) or {}

    out: list[tuple[str, type]] = []
    for p in params:
        ann = hints.get(p.name, p.annotation)
        if ann is inspect._empty or ann is None:
            raise AssertionError(f"{cls.__name__}.__init__ param '{p.name}' missing annotation")
        if not isinstance(ann, type):
            raise AssertionError(
                f"{cls.__name__}.__init__ param '{p.name}' has non-type annotation: {ann!r}"
            )
        out.append((p.name, ann))
    return tuple(out)


@dataclass(frozen=True)
class _GraphSpec:
    """
    Purpose:
        Describe a benchmark graph orientation.

    Contract:
        - root_a / root_b: main resolve roots for throughput loop
        - spellspace_root: must be cached within a spellspace cycle
        - *_classes must be topologically ordered (deps before dependents)
        - transient_probe:
            returns (obj1, obj2) from a resolved root to validate "no transient caching across resolves"
        - within_resolve_probe:
            returns (obj1, obj2) from the SAME resolved root to validate "no within-resolve dedupe" if enabled
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
    Builds graph specs. Extend here for new shapes.

    Supported names:
        deep     - existing deep_layers (Depth9 vs Depth7 + spellspace Depth3)
        solo     - no dependencies
        shallow  - depth-2 roots
        wide     - one wide arity root + one grouped-wide root
        diamond  - shared dependency requested twice inside same resolve
    """
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
            # root_a is ShallowRootAB
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
            # root_a is Wide8Root
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
            # Expect distinct transient leaves within the same resolve if semantics are "pure transient"
            return root.left.leaf, root.right.leaf

        return _GraphSpec(
            name="diamond",
            root_a=DiamondRoot,
            root_b=ShallowRootAB,  # mix a different shape to avoid overfitting
            spellspace_root=DiamondSpaceRoot,
            root_a_classes=(DiamondSharedLeaf, DiamondLeft, DiamondRight, DiamondRoot),
            root_b_classes=(ShallowLeafA, ShallowLeafB, ShallowRootAB),
            spellspace_classes=(DiamondSpaceLeaf, DiamondSpaceRoot),
            transient_probe=None,
            within_resolve_probe=_within,
            within_resolve_expect_distinct=True,
        )


def _selected_graphs() -> list[_GraphSpec]:
    """
    Env:
        DI_GRAPHS: comma-separated list of graph shapes to run.
            Supported: deep, solo, shallow, wide, diamond
        Default: deep
    """
    want = _parse_csv(_env_str("DI_GRAPHS", "deep"))
    out: list[_GraphSpec] = []
    for name in want:
        if name == "deep":
            out.append(_GraphFactory.deep_layers())
        elif name == "solo":
            out.append(_GraphFactory.solo())
        elif name == "shallow":
            out.append(_GraphFactory.shallow())
        elif name == "wide":
            out.append(_GraphFactory.wide())
        elif name == "diamond":
            out.append(_GraphFactory.diamond())
        else:
            raise AssertionError("Unknown graph '{0}'. Supported: deep,solo,shallow,wide,diamond".format(name))
    return out


def _selected_libs() -> tuple[str, ...]:
    """
    Env:
        DI_LIBS: comma-separated list of libs to run.
                 Supported: dependency-injector, lagom, injector, dishka, melder
        Default: all
    """
    supported = ("dependency-injector", "lagom", "injector", "dishka", "melder")
    raw = _env_str("DI_LIBS", ",".join(supported))
    want = tuple(_parse_csv(raw))
    for lib in want:
        if lib not in supported:
            raise AssertionError("Unknown lib '{0}'. Supported: {1}".format(lib, supported))
    return want


# ======================================================================================
# Controls
# ======================================================================================


@dataclass(frozen=True)
class _StressConfig:
    """
    Controls (env vars):
        DI_THREADS                  default 10
        DI_DURATION_S               default 60.0
        DI_PATTERN                  alternating | burst | ratio | random (default alternating)
        DI_BURST_LEN                default 64
        DI_RATIO_P                  default 0.5
        DI_RANDOM_SEED              default 1337

        DI_SPELLSPACE_EVERY         default 20
        DI_GC_EVERY                 default 2000
        DI_GC_MODE                  periodic | disabled | none (default periodic)

        DI_VALIDATE_TRANSIENT_EVERY default 0 (off)
            - if > 0 and transient_probe present:
              every N ops, take two consecutive root_a resolves and assert probe objects differ.

        DI_VALIDATE_WITHIN_EVERY    default 0 (off)
            - if > 0 and within_resolve_probe present:
              every N ops, resolve root_a once and assert probe pair is distinct (if expected).

        DI_PRINT_GIL                default false
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

    @staticmethod
    def from_env() -> _StressConfig:
        return _StressConfig(
            threads=_env_int("DI_THREADS", 10),
            duration_s=_env_float("DI_DURATION_S", 25.0),
            pattern=_env_str("DI_PATTERN", "alternating").lower(),
            burst_len=_env_int("DI_BURST_LEN", 64),
            ratio_p=_env_float("DI_RATIO_P", 0.5),
            random_seed=_env_int("DI_RANDOM_SEED", 1337),
            spellspace_every=_env_int("DI_SPELLSPACE_EVERY", 20),
            gc_every=_env_int("DI_GC_EVERY", 2000),
            gc_mode=_env_str("DI_GC_MODE", "periodic").lower(),
            validate_transient_every=_env_int("DI_VALIDATE_TRANSIENT_EVERY", 1),
            validate_within_every=_env_int("DI_VALIDATE_WITHIN_EVERY", 1),
        )


@dataclass
class _ThreadStats:
    steps: int = 0
    a: int = 0
    b: int = 0
    spellspaces: int = 0
    errors: int = 0


@dataclass(frozen=True)
class _RuntimeOps:
    """
    Per-library operations for the stress run.

    Contract:
        - get_root_a/get_root_b return the resolved root instance
        - spellspace_cycle validates caching semantics within a spellspace context
        - cleanup callable once after threads finish
    """
    name: str
    get_root_a: Callable[[], Any]
    get_root_b: Callable[[], Any]
    spellspace_cycle: Callable[[], None]
    cleanup: Callable[[], None]


# ======================================================================================
# Workload selector
# ======================================================================================


class _WorkSelector:
    """
    Supported patterns:
        alternating:  A, B, A, B, ...
        burst:        A x burst_len, B x burst_len, repeat
        ratio:        choose A with probability ratio_p else B
        random:       pseudo-random A/B choices with a per-thread RNG
    """
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
        raise AssertionError("Unknown DI_PATTERN: {0}".format(self.pattern))


# ======================================================================================
# Runtime builders (per lib)
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
                raise AssertionError("DI wiring error: {0} depends on {1} before registered".format(cls, ptype))
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

    def cleanup() -> None:
        gc.collect()

    return _RuntimeOps(
        name="lagom",
        get_root_a=get_root_a,
        get_root_b=get_root_b,
        spellspace_cycle=spellspace_cycle,
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

    def cleanup() -> None:
        for cls, orig in state.original_inits.items():
            cls.__init__ = orig
        gc.collect()

    return _RuntimeOps(
        name="injector",
        get_root_a=get_root_a,
        get_root_b=get_root_b,
        spellspace_cycle=spellspace_cycle,
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

    def cleanup() -> None:
        container.close()
        gc.collect()

    return _RuntimeOps(
        name="dishka",
        get_root_a=get_root_a,
        get_root_b=get_root_b,
        spellspace_cycle=spellspace_cycle,
        cleanup=cleanup,
    )


def _build_runtime_melder(g: _GraphSpec) -> _RuntimeOps:
    from melder.aether.aether import Aether
    from melder.aether.conduit.conduit import Conduit
    from melder.spellbook.existence.existence import Existence
    from melder.spellbook.spellbook import Spellbook

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
    raise AssertionError("Unknown lib: {0}".format(lib))


# ======================================================================================
# Smoke + single-resolve tests (fast)
# ======================================================================================


@pytest.mark.parametrize("lib", _selected_libs())
@pytest.mark.parametrize("graph", [g.name for g in _selected_graphs()])
def test_single_resolve_smoke(lib: str, graph: str) -> None:
    """
    Fast sanity test:
      - build runtime ops
      - resolve root_a once
      - resolve root_b once
      - run spellspace cycle once
    """
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


@pytest.mark.parametrize("lib", _selected_libs())
@pytest.mark.parametrize("graph", [g.name for g in _selected_graphs()])
def test_single_resolve_timings(lib: str, graph: str) -> None:
    """
    Optional single-resolve timing prints (cold/second).

    Enable with:
        DI_RUN_SINGLE=1
    """
    if not _env_bool("DI_RUN_SINGLE", True):
        pytest.skip("DI_RUN_SINGLE not enabled")

    gspecs = {g.name: g for g in _selected_graphs()}
    g = gspecs[graph]
    ops = _build_ops(lib, g)
    _maybe_print_gil_status(f"{ops.name}/single")

    try:
        t0 = time.perf_counter_ns()
        _ = ops.get_root_a()
        cold_a = time.perf_counter_ns() - t0

        t0 = time.perf_counter_ns()
        _ = ops.get_root_a()
        second_a = time.perf_counter_ns() - t0

        t0 = time.perf_counter_ns()
        _ = ops.get_root_b()
        cold_b = time.perf_counter_ns() - t0

        t0 = time.perf_counter_ns()
        _ = ops.get_root_b()
        second_b = time.perf_counter_ns() - t0

        print(
            f"[{ops.name}] single ({g.name}) "
            f"A cold={cold_a/1_000.0:.2f}us second={second_a/1_000.0:.2f}us | "
            f"B cold={cold_b/1_000.0:.2f}us second={second_b/1_000.0:.2f}us"
        )
    finally:
        ops.cleanup()


# ======================================================================================
# Throughput / contention stress test
# ======================================================================================


@pytest.mark.timeout(420)
@pytest.mark.parametrize("lib", _selected_libs())
@pytest.mark.parametrize("graph", [g.name for g in _selected_graphs()])
def test_threaded_di_stress(lib: str, graph: str) -> None:
    """
    Throughput/lock-contention stress benchmark.

    Default behavior matches your old test:
        DI_THREADS=10
        DI_DURATION_S=60
        DI_PATTERN=alternating
        DI_SPELLSPACE_EVERY=20
        DI_GC_MODE=periodic (collect every DI_GC_EVERY=2000)

    Set:
        DI_GRAPHS=deep,solo,shallow,wide,diamond
    to run all shapes.
    """
    gspecs = {g.name: g for g in _selected_graphs()}
    g = gspecs[graph]

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

    ops = _build_ops(lib, g)
    _maybe_print_gil_status(ops.name)

    stats: list[_ThreadStats] = [_ThreadStats() for _ in range(cfg.threads)]
    errors: list[BaseException] = []
    stop_event = threading.Event()
    start_barrier = threading.Barrier(cfg.threads + 1)
    stop_time_holder: list[float] = [0.0]

    def worker(ix: int) -> None:
        try:
            was_enabled = gc.isenabled()
            if cfg.gc_mode == "disabled" and was_enabled:
                gc.disable()

            try:
                start_barrier.wait()
                stop_at = stop_time_holder[0]

                local_i = 0
                local_stats = stats[ix]

                rng: Optional[random.Random]
                if cfg.pattern in ("ratio", "random"):
                    rng = random.Random(cfg.random_seed + ix)
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
                        local_stats.a += 1
                    else:
                        root = ops.get_root_b()
                        if not isinstance(root, g.root_b):
                            raise AssertionError("Resolved root_b returned wrong type")
                        local_stats.b += 1

                    local_stats.steps += 1
                    local_i += 1

                    # Spellspace correctness
                    if (local_i % cfg.spellspace_every) == 0:
                        ops.spellspace_cycle()
                        local_stats.spellspaces += 1

                    # Transient anti-cache: across resolves
                    if cfg.validate_transient_every > 0 and g.transient_probe is not None:
                        if (local_i % cfg.validate_transient_every) == 0:
                            r1 = ops.get_root_a()
                            r2 = ops.get_root_a()
                            o11, o12 = g.transient_probe(r1)
                            o21, o22 = g.transient_probe(r2)
                            if o11 is o21 or o12 is o22:
                                raise AssertionError("Transient probe failed: cached transient subtree detected")

                    # Transient anti-dedupe: within a resolve (diamond-style)
                    if cfg.validate_within_every > 0 and g.within_resolve_probe is not None:
                        if (local_i % cfg.validate_within_every) == 0:
                            r = ops.get_root_a()
                            x, y = g.within_resolve_probe(r)
                            if g.within_resolve_expect_distinct and (x is y):
                                raise AssertionError("Within-resolve probe failed: transient dedupe detected")

                    # GC policy
                    if cfg.gc_mode == "periodic":
                        if (local_i % cfg.gc_every) == 0:
                            gc.collect()

            finally:
                if cfg.gc_mode == "disabled" and was_enabled:
                    gc.enable()

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
        total_a = sum(s.a for s in stats)
        total_b = sum(s.b for s in stats)
        total_spaces = sum(s.spellspaces for s in stats)
        total_err = sum(s.errors for s in stats)

        steps_per_s = total_steps / elapsed_s if elapsed_s > 0 else 0.0

        print(
            f"[{ops.name}] threaded stress ({g.name}): "
            f"threads={cfg.threads}, duration={elapsed_s:.2f}s, "
            f"steps={total_steps}, steps/s={steps_per_s:,.0f}, "
            f"a={total_a}, b={total_b}, spellspaces={total_spaces}, errors={total_err}"
        )
    finally:
        ops.cleanup()
