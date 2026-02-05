from __future__ import annotations

import gc
import inspect
import os
import threading
import time
import typing
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import pytest

from tests.mocks.spellbook.deep_layers import Depth9LeafA, Depth9Root, get_depth_9_classes


# ======================================================================================
# Environment helpers
# ======================================================================================


def _env_str(name: str, default: str) -> str:
    v = os.getenv(name)
    return default if v is None or v == "" else v


def _env_int(name: str, default: int) -> int:
    v = os.getenv(name)
    if v is None or v == "":
        return default
    try:
        return int(v)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    v = os.getenv(name)
    if v is None or v == "":
        return default
    try:
        return float(v)
    except ValueError:
        return default


def _env_int_nonneg(name: str, default: int) -> int:
    value = _env_int(name, default)
    return value if value >= 0 else 0


def _env_bool(name: str, default: bool) -> bool:
    v = os.getenv(name)
    if v is None or v == "":
        return default
    return v.strip().lower() in ("1", "true", "yes", "y", "on")


def _parse_csv(value: str) -> list[str]:
    return [p.strip() for p in value.split(",") if p.strip()]


def _selected_libs() -> tuple[str, ...]:
    supported = ("dependency-injector", "lagom", "injector", "dishka", "melder")
    raw = _env_str("DI_LIBS", ",".join(supported))
    want = tuple(_parse_csv(raw))
    for lib in want:
        if lib not in supported:
            raise AssertionError(f"Unknown lib '{lib}'. Supported: {supported}")
    return want


def _selected_graphs() -> tuple[str, ...]:
    supported = ("solo", "shallow", "wide", "diamond", "deep")
    raw = _env_str("DI_GRAPHS", ",".join(supported))
    want = tuple(_parse_csv(raw))
    for name in want:
        if name not in supported:
            raise AssertionError(f"Unknown graph '{name}'. Supported: {supported}")
    return want


# ======================================================================================
# Graph nodes (subset from test_shallow_all)
# ======================================================================================


class _NoDeps:
    __slots__ = ()

    def __init__(self) -> None:
        return None


# ---- SOLO ---------------------------------------------------------------------------


class SoloRootA(_NoDeps):
    __slots__ = ()


# ---- SHALLOW ------------------------------------------------------------------------


class ShallowLeafA(_NoDeps):
    __slots__ = ()


class ShallowLeafB(_NoDeps):
    __slots__ = ()


class ShallowRootAB:
    __slots__ = ("a", "b")

    def __init__(self, a: ShallowLeafA, b: ShallowLeafB) -> None:
        self.a = a
        self.b = b


# ---- WIDE ---------------------------------------------------------------------------


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


# ---- DIAMOND ------------------------------------------------------------------------


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


# ======================================================================================
# Shared helpers
# ======================================================================================


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
    params = list(sig.parameters.values())[1:]

    if params and all(
        p.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
        for p in params
    ):
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


def _deep_left_leaf(root: Depth9Root) -> Depth9LeafA:
    node = root.left
    node = node.left
    node = node.left
    node = node.left
    node = node.left
    node = node.left
    node = node.left
    node = node.left
    return node


@dataclass(frozen=True)
class _OverrideGraphSpec:
    name: str
    root_type: type
    classes: tuple[type, ...]
    override_target: type
    override_accessor: Callable[[Any], tuple[Any, ...]]
    melder_override_key: str | None
    melder_override_mode: str


def _override_graphs() -> list[_OverrideGraphSpec]:
    return [
        _OverrideGraphSpec(
            name="solo",
            root_type=SoloRootA,
            classes=(SoloRootA,),
            override_target=SoloRootA,
            override_accessor=lambda root: (root,),
            melder_override_key=None,
            melder_override_mode="existing",
        ),
        _OverrideGraphSpec(
            name="shallow",
            root_type=ShallowRootAB,
            classes=(ShallowLeafA, ShallowLeafB, ShallowRootAB),
            override_target=ShallowLeafA,
            override_accessor=lambda root: (root.a,),
            melder_override_key="a",
            melder_override_mode="payload",
        ),
        _OverrideGraphSpec(
            name="wide",
            root_type=Wide8Root,
            classes=(
                Wide8Leaf0,
                Wide8Leaf1,
                Wide8Leaf2,
                Wide8Leaf3,
                Wide8Leaf4,
                Wide8Leaf5,
                Wide8Leaf6,
                Wide8Leaf7,
                Wide8Root,
            ),
            override_target=Wide8Leaf0,
            override_accessor=lambda root: (root.leaves[0],),
            melder_override_key="l0",
            melder_override_mode="payload",
        ),
        _OverrideGraphSpec(
            name="diamond",
            root_type=DiamondRoot,
            classes=(DiamondSharedLeaf, DiamondLeft, DiamondRight, DiamondRoot),
            override_target=DiamondSharedLeaf,
            override_accessor=lambda root: (root.left.leaf, root.right.leaf),
            melder_override_key="**leaf",
            melder_override_mode="payload",
        ),
        _OverrideGraphSpec(
            name="deep",
            root_type=Depth9Root,
            classes=tuple(get_depth_9_classes()),
            override_target=Depth9LeafA,
            override_accessor=lambda root: (_deep_left_leaf(root),),
            melder_override_key="left>left>left>left>left>left>left>left",
            melder_override_mode="payload",
        ),
    ]


@dataclass(frozen=True)
class _OverrideOps:
    name: str
    graph: _OverrideGraphSpec
    get_root: Callable[[], Any]
    cleanup: Callable[[], None]
    override_instance: Any


def _maybe_profile(name: str, fn: Callable[[], None]) -> None:
    if not _env_bool("DI_CPROFILE", False):
        fn()
        return

    import cProfile

    profile = cProfile.Profile()
    profile.enable()
    try:
        fn()
    finally:
        profile.disable()
        out_dir = Path(_env_str("DI_CPROFILE_DIR", "benchmarks/testing_other_di/optimistic"))
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"overrides_{name}.prof"
        profile.dump_stats(str(out_path))


# ======================================================================================
# Override runtime builders per library
# ======================================================================================


def _build_override_dependency_injector(g: _OverrideGraphSpec) -> _OverrideOps:
    pytest.importorskip("dependency_injector")
    from dependency_injector import providers

    providers_by_type: dict[type, Any] = {}
    for cls in g.classes:
        param_specs = _ctor_param_types(cls)
        kwargs: dict[str, Any] = {}
        for pname, ptype in param_specs:
            dep = providers_by_type.get(ptype)
            if dep is None:
                raise AssertionError(
                    f"DI wiring error: {cls.__name__} depends on {ptype.__name__} before registered"
                )
            kwargs[pname] = dep
        providers_by_type[cls] = providers.Factory(cls, **kwargs)

    override_instance = g.override_target()
    providers_by_type[g.override_target].override(providers.Object(override_instance))

    def get_root() -> Any:
        root = providers_by_type[g.root_type]()
        if not isinstance(root, g.root_type):
            raise AssertionError("Dependency Injector: root resolve returned wrong type")
        return root

    def cleanup() -> None:
        for prov in providers_by_type.values():
            reset = getattr(prov, "reset", None)
            if reset is not None:
                reset()
        gc.collect()

    return _OverrideOps(
        name="dependency-injector",
        graph=g,
        get_root=get_root,
        cleanup=cleanup,
        override_instance=override_instance,
    )


def _build_override_lagom(g: _OverrideGraphSpec) -> _OverrideOps:
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

    override_instance = g.override_target()

    def _override_factory() -> Any:
        return override_instance

    for cls in g.classes:
        if cls is g.override_target:
            # Use a zero-arg factory so lagom doesn't pass the container.
            container[cls] = _override_factory
            continue
        specs = _ctor_param_types(cls)
        if not specs:
            container[cls] = _make_leaf_factory(cls)
        else:
            container[cls] = _make_factory(cls, specs)

    def get_root() -> Any:
        root = container[g.root_type]
        if not isinstance(root, g.root_type):
            raise AssertionError("Lagom: root resolve returned wrong type")
        return root

    def cleanup() -> None:
        gc.collect()

    return _OverrideOps(
        name="lagom",
        graph=g,
        get_root=get_root,
        cleanup=cleanup,
        override_instance=override_instance,
    )


@dataclass
class _InjectorState:
    injector: Any
    original_inits: dict[type, Any]


def _build_override_injector(g: _OverrideGraphSpec) -> _OverrideOps:
    pytest.importorskip("injector")
    from injector import Binder, Injector, Module, InstanceProvider, inject

    original_inits: dict[type, Any] = {}
    for cls in g.classes:
        original_inits[cls] = cls.__init__
        cls.__init__ = inject(cls.__init__)

    override_instance = g.override_target()

    class PerfModule(Module):
        def configure(self, binder: Binder) -> None:
            binder.bind(g.override_target, to=InstanceProvider(override_instance))
            for cls in g.classes:
                if cls is g.override_target:
                    continue
                binder.bind(cls, to=cls)

    injector = Injector([PerfModule()])

    state = _InjectorState(
        injector=injector,
        original_inits=original_inits,
    )

    def get_root() -> Any:
        root = state.injector.get(g.root_type)
        if not isinstance(root, g.root_type):
            raise AssertionError("Injector: root resolve returned wrong type")
        return root

    def cleanup() -> None:
        for cls, orig in state.original_inits.items():
            cls.__init__ = orig
        gc.collect()

    return _OverrideOps(
        name="injector",
        graph=g,
        get_root=get_root,
        cleanup=cleanup,
        override_instance=override_instance,
    )


def _build_override_dishka(g: _OverrideGraphSpec) -> _OverrideOps:
    pytest.importorskip("dishka")
    from dishka import Provider, Scope, make_container

    provider = Provider()
    for cls in g.classes:
        provider.provide(cls, scope=Scope.APP, cache=False)

    override_instance = g.override_target()

    def _override_factory() -> Any:
        return override_instance

    provider.provide(
        _override_factory,
        provides=g.override_target,
        scope=Scope.APP,
        cache=True,
        override=True,
    )

    container = make_container(provider)

    def get_root() -> Any:
        root = container.get(g.root_type)
        if not isinstance(root, g.root_type):
            raise AssertionError("Dishka: root resolve returned wrong type")
        return root

    def cleanup() -> None:
        container.close()
        gc.collect()

    return _OverrideOps(
        name="dishka",
        graph=g,
        get_root=get_root,
        cleanup=cleanup,
        override_instance=override_instance,
    )


def _build_override_melder(g: _OverrideGraphSpec) -> _OverrideOps:
    from melder.aether.aether import Aether
    from melder.aether.conduit.conduit import Conduit
    from melder.spellbook.existence.existence import Existence
    from melder.spellbook.spellbook import Spellbook

    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether

    spellbook = Spellbook(aetheric_frame="di-overrides")
    cfg = spellbook.get_configuration()
    cfg.set_property("phase_scheduler_workers_per_spellbook", 1)

    override_instance = g.override_target()

    if g.melder_override_mode == "existing":
        root_id = spellbook.bind(spell=override_instance, existence=Existence.unique, permissions="create")
    else:
        ids: dict[type, str] = {}
        for cls in g.classes:
            ids[cls] = spellbook.bind(spell=cls, existence=Existence.many, permissions="create")
        root_id = ids[g.root_type]

    conduit = spellbook.conjure(name="di-overrides")

    def get_root() -> Any:
        if g.melder_override_mode == "existing":
            root = conduit.meld(spell=root_id)
        else:
            root = conduit.meld(spell=root_id, spell_override={g.melder_override_key: override_instance})
        if not isinstance(root, g.root_type):
            raise AssertionError("Melder: root resolve returned wrong type")
        return root

    def cleanup() -> None:
        try:
            conduit.cleanup()
        finally:
            Aether._reset_singleton_for_tests()
            aether2 = Aether()
            Spellbook._aether = aether2
            Conduit._aether = aether2
        gc.collect()

    return _OverrideOps(
        name="melder",
        graph=g,
        get_root=get_root,
        cleanup=cleanup,
        override_instance=override_instance,
    )


def _build_override_ops(lib: str, g: _OverrideGraphSpec) -> _OverrideOps:
    if lib == "dependency-injector":
        return _build_override_dependency_injector(g)
    if lib == "lagom":
        return _build_override_lagom(g)
    if lib == "injector":
        return _build_override_injector(g)
    if lib == "dishka":
        return _build_override_dishka(g)
    if lib == "melder":
        return _build_override_melder(g)
    raise AssertionError(f"Unknown lib: {lib}")


# ======================================================================================
# Stress config + tests (benchmark-style loop)
# ======================================================================================


@dataclass(frozen=True)
class _OverrideStressConfig:
    """
    Controls (env vars):
        DI_OVERRIDE_THREADS          default 1
        DI_OVERRIDE_DURATION_S       default 15.0
        DI_OVERRIDE_VALIDATE_EVERY   default 200 (0 disables)
        DI_OVERRIDE_WARMUP_ITERS     default 50
        DI_OVERRIDE_GC_EVERY         default 2000
        DI_OVERRIDE_GC_MODE          periodic | disabled | none (default periodic)
        DI_OVERRIDE_RUN_PER_GRAPH    default 1
    """
    threads: int
    duration_s: float
    validate_every: int
    warmup_iters: int
    gc_every: int
    gc_mode: str

    @staticmethod
    def from_env() -> _OverrideStressConfig:
        return _OverrideStressConfig(
            threads=_env_int("DI_OVERRIDE_THREADS", 1),
            duration_s=_env_float("DI_OVERRIDE_DURATION_S", 15.0),
            validate_every=_env_int_nonneg("DI_OVERRIDE_VALIDATE_EVERY", 200),
            warmup_iters=_env_int_nonneg("DI_OVERRIDE_WARMUP_ITERS", 50),
            gc_every=_env_int_nonneg("DI_OVERRIDE_GC_EVERY", 2000),
            gc_mode=_env_str("DI_OVERRIDE_GC_MODE", "periodic").lower(),
        )


@dataclass
class _OverrideThreadStats:
    steps: int = 0
    errors: int = 0


def _validate_override_once(ops: _OverrideOps) -> None:
    root = ops.get_root()
    observed = ops.graph.override_accessor(root)
    for value in observed:
        if value is not ops.override_instance:
            raise AssertionError(
                f"{ops.name}:{ops.graph.name} override did not apply ({value!r} is not override instance)"
            )


@pytest.mark.parametrize("lib", _selected_libs())
@pytest.mark.parametrize("graph_name", _selected_graphs())
def test_overrides_all(lib: str, graph_name: str) -> None:
    if not _env_bool("DI_OVERRIDE_RUN_PER_GRAPH", True):
        pytest.skip("DI_OVERRIDE_RUN_PER_GRAPH disabled")

    graphs = {g.name: g for g in _override_graphs()}
    g = graphs[graph_name]
    ops = _build_override_ops(lib, g)
    cfg = _OverrideStressConfig.from_env()

    if cfg.threads <= 0:
        raise AssertionError("DI_OVERRIDE_THREADS must be > 0")
    if cfg.duration_s <= 0:
        raise AssertionError("DI_OVERRIDE_DURATION_S must be > 0")
    if cfg.gc_mode not in ("periodic", "disabled", "none"):
        raise AssertionError("DI_OVERRIDE_GC_MODE must be: periodic|disabled|none")
    if _env_bool("DI_CPROFILE", False) and cfg.threads != 1:
        raise AssertionError("DI_CPROFILE requires DI_OVERRIDE_THREADS=1")

    for _ in range(max(1, cfg.warmup_iters)):
        _validate_override_once(ops)

    stats: list[_OverrideThreadStats] = [_OverrideThreadStats() for _ in range(cfg.threads)]
    errors: list[BaseException] = []
    stop_event = threading.Event()
    start_barrier = threading.Barrier(cfg.threads + 1)
    stop_time_holder: list[float] = [0.0]

    def _run_worker(ix: int) -> None:
        try:
            was_enabled = gc.isenabled()
            if cfg.gc_mode == "disabled" and was_enabled:
                gc.disable()

            try:
                start_barrier.wait()
                stop_at = stop_time_holder[0]
                local_i = 0
                local_stats = stats[ix]

                while not stop_event.is_set() and time.perf_counter() < stop_at:
                    root = ops.get_root()
                    local_stats.steps += 1
                    local_i += 1

                    if cfg.validate_every > 0 and (local_i % cfg.validate_every) == 0:
                        observed = g.override_accessor(root)
                        for value in observed:
                            if value is not ops.override_instance:
                                raise AssertionError(
                                    f"{ops.name}:{g.name} override did not apply "
                                    f"({value!r} is not override instance)"
                                )

                    if cfg.gc_mode == "periodic" and cfg.gc_every > 0:
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
        t = threading.Thread(target=_run_worker, args=(i,), daemon=True)
        threads_list.append(t)
        t.start()

    def _run_timed() -> None:
        start_barrier.wait()
        start_t = time.perf_counter()
        stop_time_holder[0] = start_t + cfg.duration_s

        for t in threads_list:
            t.join()

        elapsed_s = time.perf_counter() - start_t
        if errors:
            raise errors[0]

        total_steps = sum(s.steps for s in stats)
        total_err = sum(s.errors for s in stats)
        steps_per_s = total_steps / elapsed_s if elapsed_s > 0 else 0.0
        print(
            f"[{ops.name}] override-perf ({g.name}): "
            f"threads={cfg.threads}, duration={elapsed_s:.2f}s, "
            f"steps={total_steps}, steps/s={steps_per_s:,.0f}, "
            f"errors={total_err}"
        )

    try:
        _maybe_profile(f"{ops.name}_{g.name}", _run_timed)
    finally:
        ops.cleanup()
