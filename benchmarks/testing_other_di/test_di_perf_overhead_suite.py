from __future__ import annotations

import gc
import time
from dataclasses import dataclass
from typing import Callable, Optional, Protocol

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook


# ======================================================================================
# Purpose:
#     A fairer DI performance suite with two scenarios:
#         1) "lite" constructors  -> exposes DI overhead (tiny work per object)
#         2) "heavy" constructors -> realistic object build cost (DI mostly hidden)
#
# Contract:
#     - Uses the same 3-node graph shape for all frameworks:
#           Service -> Logger -> Config
#     - Measures:
#           build time (registration + container creation; imports excluded)
#           resolve avg (Config, Logger, Service)
#     - No perf assertions (prints tables; sanity asserts only).
#
# Fairness Fixes (IMPORTANT):
#     - All frameworks are timed through an equivalent Python wrapper function:
#           def get_x(): return <framework resolve>
#       This removes the prior "some frameworks pass a raw callable, others use lambdas"
#       distortion (dependency-injector was getting a free win).
#     - Melder tries positional meld calls once (NOT timed) and uses positional if supported;
#       otherwise it uses keyword-only calls. This avoids benchmarking keyword parsing when
#       it isn't required by the API.
# ======================================================================================


# ======================================================================================
# Scenario: LITE constructors (DI overhead is visible)
# ======================================================================================


class LiteConfig:
    __slots__ = ("value",)

    def __init__(self) -> None:
        self.value = 123


class LiteLogger:
    __slots__ = ("config", "level")

    def __init__(self, config: LiteConfig) -> None:
        self.config = config
        self.level = 20


class LiteService:
    __slots__ = ("logger", "routing")

    def __init__(self, logger: LiteLogger) -> None:
        self.logger = logger
        # keep a tiny structure so service isn't a total no-op
        self.routing = (logger.level, logger.config.value)


# ======================================================================================
# Scenario: HEAVY constructors (realistic object build dominates)
# ======================================================================================


class HeavyConfig:
    __slots__ = ("table", "values")

    def __init__(self) -> None:
        self.table = {f"key{i}": i for i in range(2000)}
        self.values = [i * 3 for i in range(2000)]


class HeavyLogger:
    __slots__ = ("config", "levels", "prefix_cache")

    def __init__(self, config: HeavyConfig) -> None:
        self.config = config
        self.levels = {"DEBUG": 10, "INFO": 20, "WARN": 30, "ERROR": 40}
        self.prefix_cache = [f"[{i:04d}]" for i in range(2000)]


class HeavyService:
    __slots__ = ("logger", "routing")

    def __init__(self, logger: HeavyLogger) -> None:
        self.logger = logger
        self.routing = {f"route{i}": (i % 17, i % 23) for i in range(5000)}


# ======================================================================================
# Protocols (optional: stable “interfaces”; not used as DI keys in this suite)
# ======================================================================================


class IConfig(Protocol):
    ...


class ILogger(Protocol):
    ...


class IService(Protocol):
    ...


# ======================================================================================
# Aether singleton reset (Melder isolation)
# ======================================================================================


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration() -> None:
    """
    Purpose:
        Ensure integration tests start with a clean Aether singleton.

    Contract:
        - Resets the Aether singleton before the test runs.
        - Rebinds Spellbook._aether and Conduit._aether to the new instance.
        - Resets the singleton again after the test for isolation.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


# ======================================================================================
# Timing helpers
# ======================================================================================


def _ns() -> int:
    return time.perf_counter_ns()


def _ms_from_ns(ns: int) -> float:
    return ns / 1_000_000.0


def _us_from_ns(ns: int) -> float:
    return ns / 1_000.0


@dataclass(frozen=True)
class PerfSettings:
    """
    In-file configuration for perf loops.
    """
    __slots__ = ("tries", "warmup", "gc_disable_during_timing")

    tries: int
    warmup: int
    gc_disable_during_timing: bool


@dataclass(frozen=True)
class PerfScenario:
    """
    Scenario definition for a 3-node graph.

    Graph:
        Service -> Logger -> Config
    """
    __slots__ = ("name", "config_cls", "logger_cls", "service_cls", "settings")

    name: str
    config_cls: type
    logger_cls: type
    service_cls: type
    settings: PerfSettings


@dataclass(frozen=True)
class PerfRow:
    name: str
    scenario: str
    mode: str  # "singleton" | "transient"
    build_ns: int
    cfg_total_ns: int
    log_total_ns: int
    svc_total_ns: int
    cfg_avg_us: float
    log_avg_us: float
    svc_avg_us: float
    logger_is_cached: Optional[bool]  # only checked for singleton


def _time_loop(getter: Callable[[], object], *, warmup: int, tries: int, gc_disable: bool) -> int:
    """
    Time `tries` calls to getter(), after `warmup` un-timed calls.
    Returns total time in ns for the timed section.
    """
    g = getter

    for _ in range(warmup):
        g()

    was_enabled = gc.isenabled()
    if gc_disable and was_enabled:
        gc.disable()

    try:
        t0 = _ns()
        for _ in range(tries):
            g()
        return _ns() - t0
    finally:
        if gc_disable and was_enabled:
            gc.enable()


def _format_row(r: PerfRow, *, tries: int, warmup: int) -> str:
    cache = "n/a" if r.logger_is_cached is None else ("yes" if r.logger_is_cached else "no")
    return (
        f"{r.name:<20} | {r.mode:<9} | "
        f"build={_ms_from_ns(r.build_ns):>8.3f}ms | "
        f"cfg={r.cfg_avg_us:>8.2f}us | "
        f"log={r.log_avg_us:>8.2f}us | "
        f"svc={r.svc_avg_us:>8.2f}us | "
        f"(tries={tries}, warmup={warmup}) | "
        f"log_cached={cache}"
    )


def _print_table(title: str, rows: list[PerfRow], *, tries: int, warmup: int) -> None:
    print("\n" + "=" * 118)
    print(title)
    print("-" * 118)
    print(
        f"{'framework':<20} | {'mode':<9} | "
        f"{'build':>14} | {'cfg avg':>12} | {'log avg':>12} | {'svc avg':>12} | "
        f"{'loop':>20} | {'log_cached':>12}"
    )
    print("-" * 118)
    for r in rows:
        print(_format_row(r, tries=tries, warmup=warmup))
    print("=" * 118 + "\n")


# ======================================================================================
# Melder runner
# ======================================================================================

def _melder_run(s: PerfScenario, mode: str) -> PerfRow:
    if mode not in ("singleton", "transient"):
        raise AssertionError(f"Unknown mode: {mode}")

    cfg = Configuration()
    cfg.dynamic_defaults()
    cfg.set_property("phase_scheduler_workers_per_spellbook", 1)
    cfg.set_property("full_ahead_of_time_compilation", True)  # compile everything at bind time to exclude JIT from timing

    existence = Existence.unique if mode == "singleton" else Existence.many

    t0 = _ns()
    spellbook = Spellbook(configuration=cfg)
    config_id = spellbook.bind(spell=s.config_cls, existence=existence, permissions="create")
    logger_id = spellbook.bind(spell=s.logger_cls, existence=existence, permissions="create")
    service_id = spellbook.bind(spell=s.service_cls, existence=existence, permissions="create")
    conduit = spellbook.conjure(name=f"perf-{s.name}-{mode}", automatic=True)
    build_ns = _ns() - t0

    try:
        meld = conduit.meld

        # --- sanity (NOT timed) ---
        cfg1 = meld(spell=config_id)
        cfg2 = meld(spell=config_id)
        assert isinstance(cfg1, s.config_cls)
        assert isinstance(cfg2, s.config_cls)

        log1 = meld(spell=logger_id)
        log2 = meld(spell=logger_id)
        assert isinstance(log1, s.logger_cls)
        assert isinstance(log2, s.logger_cls)

        svc1 = meld(spell=service_id)
        assert isinstance(svc1, s.service_cls)

        if mode == "singleton":
            logger_is_cached: Optional[bool] = (log1 is log2)
            assert logger_is_cached
        else:
            logger_is_cached = None

        # --- WRAPPER GETTERS (fair, explicit, stable) ---
        def get_cfg() -> object:
            return meld(spell=config_id)

        def get_log() -> object:
            return meld(spell=logger_id)

        def get_svc() -> object:
            return meld(spell=service_id)

        tries = s.settings.tries
        warmup = s.settings.warmup
        gc_disable = s.settings.gc_disable_during_timing

        gc.collect()

        cfg_total_ns = _time_loop(get_cfg, warmup=warmup, tries=tries, gc_disable=gc_disable)
        log_total_ns = _time_loop(get_log, warmup=warmup, tries=tries, gc_disable=gc_disable)
        svc_total_ns = _time_loop(get_svc, warmup=warmup, tries=tries, gc_disable=gc_disable)

        return PerfRow(
            name="melder",
            scenario=s.name,
            mode=mode,
            build_ns=build_ns,
            cfg_total_ns=cfg_total_ns,
            log_total_ns=log_total_ns,
            svc_total_ns=svc_total_ns,
            cfg_avg_us=_us_from_ns(cfg_total_ns) / tries,
            log_avg_us=_us_from_ns(log_total_ns) / tries,
            svc_avg_us=_us_from_ns(svc_total_ns) / tries,
            logger_is_cached=logger_is_cached,
        )
    finally:
        conduit.cleanup()



# ======================================================================================
# dependency-injector runner
# ======================================================================================


def _dependency_injector_run(s: PerfScenario, mode: str) -> PerfRow:
    pytest.importorskip("dependency_injector", reason="dependency-injector is not installed")
    from dependency_injector import containers, providers

    if mode not in ("singleton", "transient"):
        raise AssertionError(f"Unknown mode: {mode}")

    t0 = _ns()

    if mode == "singleton":

        class _DIContainer(containers.DeclarativeContainer):
            cfg = providers.Singleton(s.config_cls)
            log = providers.Singleton(s.logger_cls, config=cfg)
            svc = providers.Singleton(s.service_cls, logger=log)

    else:

        class _DIContainer(containers.DeclarativeContainer):
            cfg = providers.Factory(s.config_cls)
            log = providers.Factory(s.logger_cls, config=cfg)
            svc = providers.Factory(s.service_cls, logger=log)

    di_container = _DIContainer()
    build_ns = _ns() - t0

    # sanity (NOT timed)
    cfg1 = di_container.cfg()
    cfg2 = di_container.cfg()
    assert isinstance(cfg1, s.config_cls)
    assert isinstance(cfg2, s.config_cls)

    log1 = di_container.log()
    log2 = di_container.log()
    assert isinstance(log1, s.logger_cls)
    assert isinstance(log2, s.logger_cls)

    svc1 = di_container.svc()
    assert isinstance(svc1, s.service_cls)

    if mode == "singleton":
        logger_is_cached: Optional[bool] = (log1 is log2)
        assert logger_is_cached
    else:
        logger_is_cached = None

    # Wrapper getters (fairness).
    def get_cfg() -> object:
        return di_container.cfg()

    def get_log() -> object:
        return di_container.log()

    def get_svc() -> object:
        return di_container.svc()

    tries = s.settings.tries
    warmup = s.settings.warmup
    gc_disable = s.settings.gc_disable_during_timing

    gc.collect()

    cfg_total_ns = _time_loop(get_cfg, warmup=warmup, tries=tries, gc_disable=gc_disable)
    log_total_ns = _time_loop(get_log, warmup=warmup, tries=tries, gc_disable=gc_disable)
    svc_total_ns = _time_loop(get_svc, warmup=warmup, tries=tries, gc_disable=gc_disable)

    return PerfRow(
        name="dependency-injector",
        scenario=s.name,
        mode=mode,
        build_ns=build_ns,
        cfg_total_ns=cfg_total_ns,
        log_total_ns=log_total_ns,
        svc_total_ns=svc_total_ns,
        cfg_avg_us=_us_from_ns(cfg_total_ns) / tries,
        log_avg_us=_us_from_ns(log_total_ns) / tries,
        svc_avg_us=_us_from_ns(svc_total_ns) / tries,
        logger_is_cached=logger_is_cached,
    )


# ======================================================================================
# Lagom runner
# ======================================================================================


def _lagom_run(s: PerfScenario, mode: str) -> PerfRow:
    pytest.importorskip("lagom", reason="lagom is not installed")
    from lagom import Container as LagomContainer
    from lagom import Singleton as LagomSingleton

    if mode not in ("singleton", "transient"):
        raise AssertionError(f"Unknown mode: {mode}")

    def _build_logger(container: LagomContainer):
        cfg_obj = container[s.config_cls]
        return s.logger_cls(config=cfg_obj)

    def _build_service(container: LagomContainer):
        log_obj = container[s.logger_cls]
        return s.service_cls(logger=log_obj)

    t0 = _ns()
    lagom_container = LagomContainer()
    if mode == "singleton":
        lagom_container[s.config_cls] = LagomSingleton(s.config_cls)
        lagom_container[s.logger_cls] = LagomSingleton(_build_logger)
        lagom_container[s.service_cls] = LagomSingleton(_build_service)
    else:
        lagom_container[s.config_cls] = s.config_cls
        lagom_container[s.logger_cls] = _build_logger
        lagom_container[s.service_cls] = _build_service
    build_ns = _ns() - t0

    # sanity (NOT timed)
    cfg1 = lagom_container[s.config_cls]
    cfg2 = lagom_container[s.config_cls]
    assert isinstance(cfg1, s.config_cls)
    assert isinstance(cfg2, s.config_cls)

    log1 = lagom_container[s.logger_cls]
    log2 = lagom_container[s.logger_cls]
    assert isinstance(log1, s.logger_cls)
    assert isinstance(log2, s.logger_cls)

    svc1 = lagom_container[s.service_cls]
    assert isinstance(svc1, s.service_cls)

    if mode == "singleton":
        logger_is_cached: Optional[bool] = (log1 is log2)
        assert logger_is_cached
    else:
        logger_is_cached = None

    # Wrapper getters (fairness).
    def get_cfg() -> object:
        return lagom_container[s.config_cls]

    def get_log() -> object:
        return lagom_container[s.logger_cls]

    def get_svc() -> object:
        return lagom_container[s.service_cls]

    tries = s.settings.tries
    warmup = s.settings.warmup
    gc_disable = s.settings.gc_disable_during_timing

    gc.collect()

    cfg_total_ns = _time_loop(get_cfg, warmup=warmup, tries=tries, gc_disable=gc_disable)
    log_total_ns = _time_loop(get_log, warmup=warmup, tries=tries, gc_disable=gc_disable)
    svc_total_ns = _time_loop(get_svc, warmup=warmup, tries=tries, gc_disable=gc_disable)

    return PerfRow(
        name="lagom",
        scenario=s.name,
        mode=mode,
        build_ns=build_ns,
        cfg_total_ns=cfg_total_ns,
        log_total_ns=log_total_ns,
        svc_total_ns=svc_total_ns,
        cfg_avg_us=_us_from_ns(cfg_total_ns) / tries,
        log_avg_us=_us_from_ns(log_total_ns) / tries,
        svc_avg_us=_us_from_ns(svc_total_ns) / tries,
        logger_is_cached=logger_is_cached,
    )


# ======================================================================================
# Injector (python-injector) runner
# ======================================================================================


def _injector_run(s: PerfScenario, mode: str) -> PerfRow:
    """
    Injector (python-injector) runner.

    Notes:
        - We do NOT use @provider methods here because injector requires a concrete
          return type annotation to register providers, and our scenario classes
          are selected dynamically (s.config_cls / s.logger_cls / s.service_cls).
        - Instead we:
            1) Patch __init__ with injector.inject(...) so constructor injection works.
            2) Bind each class to itself via binder.bind(...), optionally with singleton scope.
            3) Use injector.get(Class) for resolution.

    Contract:
        - Build time includes constructor patching + binding registration + Injector creation.
        - Restores patched __init__ methods before returning.
    """
    pytest.importorskip("injector", reason="injector is not installed")
    from injector import Binder, Injector as PyInjector, Module, inject, singleton

    if mode not in ("singleton", "transient"):
        raise AssertionError(f"Unknown mode: {mode}")

    classes = (s.config_cls, s.logger_cls, s.service_cls)

    # Build-time includes patching + binding + injector creation for fairness.
    t0 = _ns()

    original_inits: dict[type, object] = {}
    for cls in classes:
        original_inits[cls] = cls.__init__
        cls.__init__ = inject(cls.__init__)

    class _PerfModule(Module):
        """
        Injector module used for perf.

        Contract:
            - Binds config/logger/service classes to themselves.
            - Applies singleton scope only when mode == "singleton".
        """

        def configure(self, binder: Binder) -> None:
            if mode == "singleton":
                binder.bind(s.config_cls, to=s.config_cls, scope=singleton)
                binder.bind(s.logger_cls, to=s.logger_cls, scope=singleton)
                binder.bind(s.service_cls, to=s.service_cls, scope=singleton)
            else:
                binder.bind(s.config_cls, to=s.config_cls)
                binder.bind(s.logger_cls, to=s.logger_cls)
                binder.bind(s.service_cls, to=s.service_cls)

    injector = PyInjector([_PerfModule()])
    build_ns = _ns() - t0

    try:
        # sanity (NOT timed)
        cfg1 = injector.get(s.config_cls)
        cfg2 = injector.get(s.config_cls)
        assert isinstance(cfg1, s.config_cls)
        assert isinstance(cfg2, s.config_cls)

        log1 = injector.get(s.logger_cls)
        log2 = injector.get(s.logger_cls)
        assert isinstance(log1, s.logger_cls)
        assert isinstance(log2, s.logger_cls)

        svc1 = injector.get(s.service_cls)
        assert isinstance(svc1, s.service_cls)

        if mode == "singleton":
            logger_is_cached: Optional[bool] = (log1 is log2)
            assert logger_is_cached
        else:
            logger_is_cached = None

        # Wrapper getters (fairness).
        def get_cfg() -> object:
            return injector.get(s.config_cls)

        def get_log() -> object:
            return injector.get(s.logger_cls)

        def get_svc() -> object:
            return injector.get(s.service_cls)

        tries = s.settings.tries
        warmup = s.settings.warmup
        gc_disable = s.settings.gc_disable_during_timing

        gc.collect()

        cfg_total_ns = _time_loop(get_cfg, warmup=warmup, tries=tries, gc_disable=gc_disable)
        log_total_ns = _time_loop(get_log, warmup=warmup, tries=tries, gc_disable=gc_disable)
        svc_total_ns = _time_loop(get_svc, warmup=warmup, tries=tries, gc_disable=gc_disable)

        return PerfRow(
            name="injector",
            scenario=s.name,
            mode=mode,
            build_ns=build_ns,
            cfg_total_ns=cfg_total_ns,
            log_total_ns=log_total_ns,
            svc_total_ns=svc_total_ns,
            cfg_avg_us=_us_from_ns(cfg_total_ns) / tries,
            log_avg_us=_us_from_ns(log_total_ns) / tries,
            svc_avg_us=_us_from_ns(svc_total_ns) / tries,
            logger_is_cached=logger_is_cached,
        )
    finally:
        # Restore patched constructors to avoid cross-test contamination.
        for cls in classes:
            cls.__init__ = original_inits[cls]


# ======================================================================================
# Dishka runner
# ======================================================================================


def _dishka_run(s: PerfScenario, mode: str) -> PerfRow:
    pytest.importorskip("dishka", reason="dishka is not installed")
    from dishka import Provider, Scope, make_container

    if mode not in ("singleton", "transient"):
        raise AssertionError(f"Unknown mode: {mode}")

    t0 = _ns()
    provider = Provider(scope=Scope.APP)
    if mode == "singleton":
        provider.provide(s.config_cls)
        provider.provide(s.logger_cls)
        provider.provide(s.service_cls)
    else:
        provider.provide(s.config_cls, cache=False)
        provider.provide(s.logger_cls, cache=False)
        provider.provide(s.service_cls, cache=False)
    dishka_container = make_container(provider)
    build_ns = _ns() - t0

    try:
        # sanity (NOT timed)
        cfg1 = dishka_container.get(s.config_cls)
        cfg2 = dishka_container.get(s.config_cls)
        assert isinstance(cfg1, s.config_cls)
        assert isinstance(cfg2, s.config_cls)

        log1 = dishka_container.get(s.logger_cls)
        log2 = dishka_container.get(s.logger_cls)
        assert isinstance(log1, s.logger_cls)
        assert isinstance(log2, s.logger_cls)

        svc1 = dishka_container.get(s.service_cls)
        assert isinstance(svc1, s.service_cls)

        if mode == "singleton":
            logger_is_cached: Optional[bool] = (log1 is log2)
            assert logger_is_cached
        else:
            logger_is_cached = None

        # Wrapper getters (fairness).
        def get_cfg() -> object:
            return dishka_container.get(s.config_cls)

        def get_log() -> object:
            return dishka_container.get(s.logger_cls)

        def get_svc() -> object:
            return dishka_container.get(s.service_cls)

        tries = s.settings.tries
        warmup = s.settings.warmup
        gc_disable = s.settings.gc_disable_during_timing

        gc.collect()

        cfg_total_ns = _time_loop(get_cfg, warmup=warmup, tries=tries, gc_disable=gc_disable)
        log_total_ns = _time_loop(get_log, warmup=warmup, tries=tries, gc_disable=gc_disable)
        svc_total_ns = _time_loop(get_svc, warmup=warmup, tries=tries, gc_disable=gc_disable)

        return PerfRow(
            name="dishka",
            scenario=s.name,
            mode=mode,
            build_ns=build_ns,
            cfg_total_ns=cfg_total_ns,
            log_total_ns=log_total_ns,
            svc_total_ns=svc_total_ns,
            cfg_avg_us=_us_from_ns(cfg_total_ns) / tries,
            log_avg_us=_us_from_ns(log_total_ns) / tries,
            svc_avg_us=_us_from_ns(svc_total_ns) / tries,
            logger_is_cached=logger_is_cached,
        )
    finally:
        dishka_container.close()


# ======================================================================================
# Unified run
# ======================================================================================


def _run_all_frameworks(s: PerfScenario, mode: str) -> list[PerfRow]:
    rows: list[PerfRow] = []
    rows.append(_melder_run(s, mode))
    rows.append(_dependency_injector_run(s, mode))
    rows.append(_lagom_run(s, mode))
    rows.append(_injector_run(s, mode))
    rows.append(_dishka_run(s, mode))
    return rows


# ======================================================================================
# Scenarios
# ======================================================================================


def _lite_settings() -> PerfSettings:
    # Large iteration count so sub-micro overhead shows up clearly.
    return PerfSettings(tries=50_000, warmup=500, gc_disable_during_timing=True)


def _heavy_settings() -> PerfSettings:
    # Smaller iteration count because constructors dominate.
    return PerfSettings(tries=1_000, warmup=50, gc_disable_during_timing=False)


def _lite_scenario() -> PerfScenario:
    return PerfScenario(
        name="lite",
        config_cls=LiteConfig,
        logger_cls=LiteLogger,
        service_cls=LiteService,
        settings=_lite_settings(),
    )


def _heavy_scenario() -> PerfScenario:
    return PerfScenario(
        name="heavy",
        config_cls=HeavyConfig,
        logger_cls=HeavyLogger,
        service_cls=HeavyService,
        settings=_heavy_settings(),
    )


# ======================================================================================
# Tests
# ======================================================================================


def test_perf_overhead_lite_graph_singletons_all_frameworks() -> None:
    s = _lite_scenario()
    rows = _run_all_frameworks(s, mode="singleton")
    _print_table(
        "LITE graph perf (SINGLETON / UNIQUE semantics) — DI overhead is visible",
        rows,
        tries=s.settings.tries,
        warmup=s.settings.warmup,
    )


def test_perf_overhead_lite_graph_transient_all_frameworks() -> None:
    s = _lite_scenario()
    rows = _run_all_frameworks(s, mode="transient")
    _print_table(
        "LITE graph perf (TRANSIENT / MANY semantics) — DI overhead is visible",
        rows,
        tries=s.settings.tries,
        warmup=s.settings.warmup,
    )


def test_perf_realistic_heavy_graph_singletons_all_frameworks() -> None:
    s = _heavy_scenario()
    rows = _run_all_frameworks(s, mode="singleton")
    _print_table(
        "HEAVY graph perf (SINGLETON / UNIQUE semantics) — constructors dominate only on first resolve (excluded)",
        rows,
        tries=s.settings.tries,
        warmup=s.settings.warmup,
    )


def test_perf_realistic_heavy_graph_transient_all_frameworks() -> None:
    s = _heavy_scenario()
    rows = _run_all_frameworks(s, mode="transient")
    _print_table(
        "HEAVY graph perf (TRANSIENT / MANY semantics) — constructors dominate (DI mostly hidden)",
        rows,
        tries=s.settings.tries,
        warmup=s.settings.warmup,
    )
