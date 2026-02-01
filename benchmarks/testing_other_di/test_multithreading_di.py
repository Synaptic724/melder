from __future__ import annotations

import contextlib
import contextvars
import gc
import inspect
import os
import threading
import time
from dataclasses import dataclass
from typing import Any, Callable

import pytest

from tests.mocks.spellbook.deep_layers import (
    Depth3Root,
    Depth7Root,
    Depth9LeafA,
    Depth9LeafB,
    Depth9Root,
    get_depth_3_classes,
    get_depth_7_classes,
    get_depth_9_classes,
)


# ======================================================================================
# Shared helpers
# ======================================================================================


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


def _depth9_leaf_ids(root: Depth9Root) -> tuple[int, int]:
    """
    NOTE:
        Kept for potential debugging / future assertions, but the current benchmark configuration
        explicitly avoids singleton-style leaf caching across resolves.
    """
    layer2 = root.left
    layer3 = layer2.left
    layer4 = layer3.left
    layer5 = layer4.left
    layer6 = layer5.left
    layer7 = layer6.left
    layer8 = layer7.left
    leaf_a = layer8.left
    leaf_b = layer8.right
    return id(leaf_a), id(leaf_b)


def _ctor_param_types(cls: type) -> tuple[tuple[str, type], ...]:
    sig = inspect.signature(cls.__init__)
    params = list(sig.parameters.values())[1:]  # skip self
    out: list[tuple[str, type]] = []
    for p in params:
        if p.annotation is inspect._empty:
            raise AssertionError(f"{cls.__name__}.__init__ param '{p.name}' missing annotation")
        if not isinstance(p.annotation, type):
            raise AssertionError(
                f"{cls.__name__}.__init__ param '{p.name}' has non-type annotation: {p.annotation!r}"
            )
        out.append((p.name, p.annotation))
    return tuple(out)


@dataclass
class _ThreadStats:
    steps: int = 0
    depth9: int = 0
    depth7: int = 0
    spellspaces: int = 0
    errors: int = 0


@dataclass(frozen=True)
class _RuntimeOps:
    """
    Purpose:
        Per-library operations for the threaded stress run.
    Contract:
        - All callables must be thread-safe under concurrent calls.
        - cleanup() must be callable once after all threads finish.
    """
    name: str
    resolve_depth9: Callable[[], None]
    resolve_depth7: Callable[[], None]
    spellspace_cycle: Callable[[], None]
    cleanup: Callable[[], None]


# ======================================================================================
# Dependency Injector runtime (uses ContextLocalSingleton for spellspace semantics)
# ======================================================================================


def _build_runtime_dependency_injector() -> _RuntimeOps:
    dependency_injector = pytest.importorskip("dependency_injector")
    from dependency_injector import providers  # noqa: F401

    depth9_classes = get_depth_9_classes()
    depth7_classes = get_depth_7_classes()
    depth3_classes = get_depth_3_classes()

    depth3_types = set(depth3_classes)

    # Build a single provider graph for all classes
    all_classes: list[type] = []
    seen: set[type] = set()
    for cls in depth9_classes + depth7_classes + depth3_classes:
        if cls not in seen:
            all_classes.append(cls)
            seen.add(cls)

    providers_by_type: dict[type, Any] = {}

    # Provider selection:
    # - Depth3 graph: ContextLocalSingleton (per spellspace contextvars.Context())
    # - Everything else (including Depth9 leaves): Factory (transient)
    #
    # This benchmark is intentionally configured to avoid singleton-style caching across resolves.
    for cls in all_classes:
        param_specs = _ctor_param_types(cls)
        kwargs: dict[str, Any] = {}
        for pname, ptype in param_specs:
            dep = providers_by_type.get(ptype)
            if dep is None:
                raise AssertionError(f"DI wiring error: {cls.__name__} depends on {ptype.__name__} before registered")
            kwargs[pname] = dep

        if cls in depth3_types:
            prov = providers.ContextLocalSingleton(cls, **kwargs)
        else:
            prov = providers.Factory(cls, **kwargs)

        providers_by_type[cls] = prov

    def resolve_depth9() -> None:
        root = providers_by_type[Depth9Root]()
        if not isinstance(root, Depth9Root):
            raise AssertionError("Dependency Injector: Depth9Root resolve returned wrong type")

    def resolve_depth7() -> None:
        root = providers_by_type[Depth7Root]()
        if not isinstance(root, Depth7Root):
            raise AssertionError("Dependency Injector: Depth7Root resolve returned wrong type")

    def spellspace_cycle() -> None:
        # New spellspace = new Context()
        ctx = contextvars.Context()

        def run() -> None:
            r1 = providers_by_type[Depth3Root]()
            r2 = providers_by_type[Depth3Root]()
            if not isinstance(r1, Depth3Root):
                raise AssertionError("Dependency Injector: Depth3Root resolve returned wrong type")
            if r1 is not r2:
                raise AssertionError("Dependency Injector: Depth3Root not cached within spellspace")

        ctx.run(run)

    def cleanup() -> None:
        # Best-effort resets
        for _, prov in providers_by_type.items():
            # Only singleton-ish providers have reset()
            reset = getattr(prov, "reset", None)
            if reset is not None:
                reset()
        gc.collect()

    return _RuntimeOps(
        name="dependency-injector",
        resolve_depth9=resolve_depth9,
        resolve_depth7=resolve_depth7,
        spellspace_cycle=spellspace_cycle,
        cleanup=cleanup,
    )


# ======================================================================================
# Lagom runtime (uses temporary_singletons for spellspace semantics)
# ======================================================================================


def _build_runtime_lagom() -> _RuntimeOps:
    pytest.importorskip("lagom")
    from lagom import Container

    depth9_classes = get_depth_9_classes()
    depth7_classes = get_depth_7_classes()
    depth3_classes = get_depth_3_classes()

    # Build one base container:
    # - Everything: transient factory
    #
    # NOTE:
    #   This benchmark is intentionally configured to avoid singleton-style caching across resolves.
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
    for cls in depth9_classes + depth7_classes + depth3_classes:
        if cls not in seen:
            all_classes.append(cls)
            seen.add(cls)

    for cls in all_classes:
        specs = _ctor_param_types(cls)
        if not specs:
            container[cls] = _make_leaf_factory(cls)
            continue

        factory = _make_factory(cls, specs)
        container[cls] = factory

    def resolve_depth9() -> None:
        root = container[Depth9Root]
        if not isinstance(root, Depth9Root):
            raise AssertionError("Lagom: Depth9Root resolve returned wrong type")

    def resolve_depth7() -> None:
        root = container[Depth7Root]
        if not isinstance(root, Depth7Root):
            raise AssertionError("Lagom: Depth7Root resolve returned wrong type")

    def spellspace_cycle() -> None:
        # New spellspace = new temporary_singletons context
        with container.temporary_singletons(list(depth3_classes)) as space:
            r1 = space[Depth3Root]
            r2 = space[Depth3Root]
            if not isinstance(r1, Depth3Root):
                raise AssertionError("Lagom: Depth3Root resolve returned wrong type")
            if r1 is not r2:
                raise AssertionError("Lagom: Depth3Root not cached within spellspace")

    def cleanup() -> None:
        gc.collect()

    return _RuntimeOps(
        name="lagom",
        resolve_depth9=resolve_depth9,
        resolve_depth7=resolve_depth7,
        spellspace_cycle=spellspace_cycle,
        cleanup=cleanup,
    )


# ======================================================================================
# Injector runtime (custom SpellspaceScope + @inject patched constructors)
# ======================================================================================


@dataclass
class _InjectorState:
    injector: Any
    spellspace_scope_type: type
    original_inits: dict[type, Any]


def _build_runtime_injector() -> _RuntimeOps:
    pytest.importorskip("injector")
    from injector import Binder, Injector, Module, Scope, ScopeDecorator, InstanceProvider, inject

    depth9_classes = get_depth_9_classes()
    depth7_classes = get_depth_7_classes()
    depth3_classes = get_depth_3_classes()

    all_classes: list[type] = []
    seen: set[type] = set()
    for cls in depth9_classes + depth7_classes + depth3_classes:
        if cls not in seen:
            all_classes.append(cls)
            seen.add(cls)

    # Patch constructors so Injector actually performs ctor injection.
    original_inits: dict[type, Any] = {}
    for cls in all_classes:
        original_inits[cls] = cls.__init__
        cls.__init__ = inject(cls.__init__)  # type: ignore[method-assign]

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
                if cls in depth3_classes:
                    binder.bind(cls, to=cls, scope=spellspace)
                else:
                    # Everything else: transient (no singleton scope)
                    binder.bind(cls, to=cls)

    injector = Injector([PerfModule()])

    state = _InjectorState(injector=injector, spellspace_scope_type=SpellspaceScope, original_inits=original_inits)

    def resolve_depth9() -> None:
        root = state.injector.get(Depth9Root)
        if not isinstance(root, Depth9Root):
            raise AssertionError("Injector: Depth9Root resolve returned wrong type")

    def resolve_depth7() -> None:
        root = state.injector.get(Depth7Root)
        if not isinstance(root, Depth7Root):
            raise AssertionError("Injector: Depth7Root resolve returned wrong type")

    def spellspace_cycle() -> None:
        scope = state.injector.get(state.spellspace_scope_type)
        with scope.enter():
            r1 = state.injector.get(Depth3Root)
            r2 = state.injector.get(Depth3Root)
            if not isinstance(r1, Depth3Root):
                raise AssertionError("Injector: Depth3Root resolve returned wrong type")
            if r1 is not r2:
                raise AssertionError("Injector: Depth3Root not cached within spellspace")

    def cleanup() -> None:
        for cls, orig in state.original_inits.items():
            cls.__init__ = orig  # type: ignore[method-assign]
        gc.collect()

    return _RuntimeOps(
        name="injector",
        resolve_depth9=resolve_depth9,
        resolve_depth7=resolve_depth7,
        spellspace_cycle=spellspace_cycle,
        cleanup=cleanup,
    )


# ======================================================================================
# Dishka runtime (REQUEST scope as spellspace)
# ======================================================================================


def _build_runtime_dishka() -> _RuntimeOps:
    pytest.importorskip("dishka")
    from dishka import Provider, Scope, make_container

    depth9_classes = get_depth_9_classes()
    depth7_classes = get_depth_7_classes()
    depth3_classes = get_depth_3_classes()

    all_classes: list[type] = []
    seen: set[type] = set()
    for cls in depth9_classes + depth7_classes + depth3_classes:
        if cls not in seen:
            all_classes.append(cls)
            seen.add(cls)

    provider = Provider()
    for cls in all_classes:
        if cls in depth3_classes:
            provider.provide(cls, scope=Scope.REQUEST, cache=True)
        else:
            # Everything else: transient (no APP cache)
            provider.provide(cls, scope=Scope.APP, cache=False)

    container = make_container(provider)

    def resolve_depth9() -> None:
        root = container.get(Depth9Root)
        if not isinstance(root, Depth9Root):
            raise AssertionError("Dishka: Depth9Root resolve returned wrong type")

    def resolve_depth7() -> None:
        root = container.get(Depth7Root)
        if not isinstance(root, Depth7Root):
            raise AssertionError("Dishka: Depth7Root resolve returned wrong type")

    def spellspace_cycle() -> None:
        with container() as request_container:
            r1 = request_container.get(Depth3Root)
            r2 = request_container.get(Depth3Root)
            if not isinstance(r1, Depth3Root):
                raise AssertionError("Dishka: Depth3Root resolve returned wrong type")
            if r1 is not r2:
                raise AssertionError("Dishka: Depth3Root not cached within spellspace")

    def cleanup() -> None:
        container.close()
        gc.collect()

    return _RuntimeOps(
        name="dishka",
        resolve_depth9=resolve_depth9,
        resolve_depth7=resolve_depth7,
        spellspace_cycle=spellspace_cycle,
        cleanup=cleanup,
    )


# ======================================================================================
# Melder runtime (Conduit + spellspace)
# ======================================================================================


def _build_runtime_melder() -> _RuntimeOps:
    # Local import so competitor-only runs don't pay import cost up front.
    from melder.aether.aether import Aether
    from melder.aether.conduit.conduit import Conduit
    from melder.spellbook.existence.existence import Existence
    from melder.spellbook.spellbook import Spellbook

    # Reset Aether singleton for isolation (same contract you used in integration tests).
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether

    depth9_classes = get_depth_9_classes()
    depth7_classes = get_depth_7_classes()
    depth3_classes = get_depth_3_classes()

    spellbook = Spellbook(aetheric_frame="threaded-di-stress")
    cfg = spellbook.get_configuration()
    cfg.set_property("phase_scheduler_workers_per_spellbook", 1)

    # Bind depth9:
    # - everything: many (transient)
    #
    # This benchmark is intentionally configured to avoid singleton-style leaf caching across resolves.
    spell_ids_9: dict[type, str] = {}
    for cls in depth9_classes:
        spell_ids_9[cls] = spellbook.bind(spell=cls, existence=Existence.many, permissions="create")

    # Depth7: many
    spell_ids_7: dict[type, str] = {}
    for cls in depth7_classes:
        spell_ids_7[cls] = spellbook.bind(spell=cls, existence=Existence.many, permissions="create")

    # Depth3: unique per spellspace
    spell_ids_3: dict[type, str] = {}
    for cls in depth3_classes:
        spell_ids_3[cls] = spellbook.bind(spell=cls, existence=Existence.unique_per_spell_space, permissions="create")

    root9_id = spell_ids_9[Depth9Root]
    root7_id = spell_ids_7[Depth7Root]
    root3_id = spell_ids_3[Depth3Root]

    conduit = spellbook.conjure(name="threaded-di-stress")

    def resolve_depth9() -> None:
        root = conduit.meld(spell=root9_id)
        if not isinstance(root, Depth9Root):
            raise AssertionError("Melder: Depth9Root meld returned wrong type")

    def resolve_depth7() -> None:
        root = conduit.meld(spell=root7_id)
        if not isinstance(root, Depth7Root):
            raise AssertionError("Melder: Depth7Root meld returned wrong type")

    def spellspace_cycle() -> None:
        with conduit.enter_spellspace() as space:
            r1 = space.meld(spell=root3_id)
            r2 = space.meld(spell=root3_id)
            if not isinstance(r1, Depth3Root):
                raise AssertionError("Melder: Depth3Root meld returned wrong type")
            if r1 is not r2:
                raise AssertionError("Melder: Depth3Root not cached within spellspace")

    def cleanup() -> None:
        try:
            conduit.cleanup()
        finally:
            # Reset again after test
            Aether._reset_singleton_for_tests()
            aether2 = Aether()
            Spellbook._aether = aether2
            Conduit._aether = aether2
        gc.collect()

    return _RuntimeOps(
        name="melder",
        resolve_depth9=resolve_depth9,
        resolve_depth7=resolve_depth7,
        spellspace_cycle=spellspace_cycle,
        cleanup=cleanup,
    )


# ======================================================================================
# Stress runner
# ======================================================================================


def _build_ops(lib: str) -> _RuntimeOps:
    if lib == "dependency-injector":
        return _build_runtime_dependency_injector()
    if lib == "lagom":
        return _build_runtime_lagom()
    if lib == "injector":
        return _build_runtime_injector()
    if lib == "dishka":
        return _build_runtime_dishka()
    if lib == "melder":
        return _build_runtime_melder()
    raise AssertionError(f"Unknown lib: {lib}")


@pytest.mark.timeout(420)
@pytest.mark.parametrize("lib", ("dependency-injector", "lagom", "injector", "dishka", "melder"))
def test_threaded_di_stress_10_threads_60s(lib: str) -> None:
    """
    Purpose:
        Multi-threaded stress benchmark (shared runtime per lib):
          - 10 threads
          - ~60 seconds per lib (configurable)
          - alternating Depth9Root/Depth7Root resolves
          - periodic spellspace cycle resolving Depth3Root twice and verifying scoped caching
    Controls (env vars):
        - DI_THREADS (default 10)
        - DI_DURATION_S (default 60)
        - DI_SPELLSPACE_EVERY (default 20)
        - DI_GC_EVERY (default 2000)
    Notes:
        - This is a throughput/lock-contention stress test, not a microbenchmark.
        - It prints totals and ops/sec; it asserts only on correctness invariants.
        - It is intentionally configured to avoid singleton-style caching for Depth9 leaves across resolves.
          (Spellspace caching for Depth3 is still validated within a single spellspace cycle.)
    """
    threads = _env_int("DI_THREADS", 1)
    duration_s = _env_float("DI_DURATION_S", 60.0)
    spellspace_every = _env_int("DI_SPELLSPACE_EVERY", 20)
    gc_every = _env_int("DI_GC_EVERY", 2000)

    ops = _build_ops(lib)

    stats: list[_ThreadStats] = [_ThreadStats() for _ in range(threads)]
    errors: list[BaseException] = []
    stop_event = threading.Event()
    start_barrier = threading.Barrier(threads + 1)

    stop_time_holder: list[float] = [0.0]

    def worker(ix: int) -> None:
        try:
            start_barrier.wait()
            stop_at = stop_time_holder[0]
            local_i = 0
            local_stats = stats[ix]

            while not stop_event.is_set() and time.perf_counter() < stop_at:
                if (local_i & 1) == 0:
                    ops.resolve_depth9()
                    local_stats.depth9 += 1
                else:
                    ops.resolve_depth7()
                    local_stats.depth7 += 1

                local_stats.steps += 1
                local_i += 1

                if (local_i % spellspace_every) == 0:
                    ops.spellspace_cycle()
                    local_stats.spellspaces += 1

                if (local_i % gc_every) == 0:
                    gc.collect()

        except BaseException as e:
            stats[ix].errors += 1
            errors.append(e)
            stop_event.set()

    threads_list: list[threading.Thread] = []
    for i in range(threads):
        t = threading.Thread(target=worker, args=(i,), daemon=True)
        threads_list.append(t)
        t.start()

    # Start all threads together, then set stop time.
    start_barrier.wait()
    start_t = time.perf_counter()
    stop_time_holder[0] = start_t + duration_s

    for t in threads_list:
        t.join()

    elapsed_s = time.perf_counter() - start_t
    try:
        if errors:
            raise errors[0]

        total_steps = sum(s.steps for s in stats)
        total_d9 = sum(s.depth9 for s in stats)
        total_d7 = sum(s.depth7 for s in stats)
        total_spaces = sum(s.spellspaces for s in stats)
        total_err = sum(s.errors for s in stats)

        steps_per_s = total_steps / elapsed_s if elapsed_s > 0 else 0.0

        print(
            f"[{ops.name}] threaded stress: "
            f"threads={threads}, duration={elapsed_s:.2f}s, "
            f"steps={total_steps}, steps/s={steps_per_s:,.0f}, "
            f"d9={total_d9}, d7={total_d7}, spellspaces={total_spaces}, errors={total_err}"
        )
    finally:
        ops.cleanup()
