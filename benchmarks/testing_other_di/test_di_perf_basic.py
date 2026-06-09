from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional, Protocol

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration as Configuration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


# ======================================================================================
# Protocols (stable “interfaces” used across all frameworks)
# ======================================================================================


class IConfig(Protocol):
    ...


class ILogger(Protocol):
    ...


class IService(Protocol):
    ...


# ======================================================================================
# Shared test graph
#   PerfService -> (PerfLogger, PerfConfig)
#
# Notes:
#   - __init__ defaults use SpellMap only for Melder.
#   - Competitor frameworks explicitly pass dependencies so they do not rely on defaults.
# ======================================================================================


class PerfConfig:
    """
    Purpose:
        Provide a moderately "heavy" config object to time DI resolution.
    Contract:
        - Builds deterministic in-memory structures in __init__.
    """

    def __init__(self) -> None:
        self.table = {f"key{i}": i for i in range(2000)}
        self.values = [i * 3 for i in range(2000)]


class PerfLogger:
    """
    Purpose:
        Provide a logger that depends on config.
    Contract:
        - Resolves config via SpellMap (Melder usage).
        - Precomputes some deterministic formatting data.
    Notes:
        - For other DI frameworks we inject config explicitly (via provider factories)
          to avoid relying on SpellMap defaults.
    """

    def __init__(self, config: IConfig = SpellMap(spellframe=IConfig)) -> None:
        self.config = config
        self.levels = {"DEBUG": 10, "INFO": 20, "WARN": 30, "ERROR": 40}
        self.prefix_cache = [f"[{i:04d}]" for i in range(2000)]


class PerfService:
    """
    Purpose:
        Provide a service that depends on both logger + config.
    Contract:
        - Resolves dependencies via SpellMap (Melder usage).
        - Builds a deterministic routing table in __init__.
    Notes:
        - For other DI frameworks we inject explicitly (via provider factories)
          to avoid relying on SpellMap defaults.
    """

    def __init__(
            self,
            logger: ILogger = SpellMap(spellframe=ILogger),
            config: IConfig = SpellMap(spellframe=IConfig),
    ) -> None:
        self.logger = logger
        self.config = config
        self.routing = {f"route{i}": (i % 17, i % 23) for i in range(5000)}


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


TRIES: int = 1000
WARMUP: int = 50


def _ns() -> int:
    return time.perf_counter_ns()


def _ms_from_ns(ns: int) -> float:
    return ns / 1_000_000.0


def _us_from_ns(ns: int) -> float:
    return ns / 1_000.0


def _time_loop(getter, *, warmup: int, tries: int) -> int:
    """
    Time `tries` calls to getter(), after `warmup` un-timed calls.
    Returns total time in ns for the timed section.
    """
    for _ in range(warmup):
        getter()

    t0 = _ns()
    for _ in range(tries):
        getter()
    return _ns() - t0


@dataclass(frozen=True)
class _PerfRow:
    name: str
    mode: str  # "singleton" | "transient"
    build_ns: int
    cfg_total_ns: int
    log_total_ns: int
    svc_total_ns: int
    cfg_avg_us: float
    log_avg_us: float
    svc_avg_us: float
    logger_is_cached: Optional[bool]  # only checked for singleton


def _format_row(r: _PerfRow) -> str:
    cache = "n/a" if r.logger_is_cached is None else ("yes" if r.logger_is_cached else "no")
    return (
        f"{r.name:<20} | {r.mode:<9} | "
        f"build={_ms_from_ns(r.build_ns):>8.3f}ms | "
        f"cfg={r.cfg_avg_us:>8.2f}us | "
        f"log={r.log_avg_us:>8.2f}us | "
        f"svc={r.svc_avg_us:>8.2f}us | "
        f"(tries={TRIES}, warmup={WARMUP}) | "
        f"log_cached={cache}"
    )


def _print_table(title: str, rows: list[_PerfRow]) -> None:
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
        print(_format_row(r))
    print("=" * 118 + "\n")


# ======================================================================================
# Melder runner
# ======================================================================================


def _melder_run(mode: str) -> _PerfRow:
    if mode not in ("singleton", "transient"):
        raise AssertionError(f"Unknown mode: {mode}")

    cfg = Configuration()
    cfg.with_defaults()
    cfg.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook = Spellbook(configuration=cfg)
    existence = Existence.unique if mode == "singleton" else Existence.many

    config_id = spellbook.bind(
        spell=PerfConfig,
        existence=existence,
        permissions="create",
        spellframe=IConfig,
    )
    logger_id = spellbook.bind(
        spell=PerfLogger,
        existence=existence,
        permissions="create",
        spellframe=ILogger,
    )
    service_id = spellbook.bind(
        spell=PerfService,
        existence=existence,
        permissions="create",
        spellframe=IService,
    )

    t0 = _ns()
    conduit = spellbook.conjure(name=f"perf-{mode}", dynamic=False)
    build_ns = _ns() - t0

    try:
        # “cold” sanity resolves (NOT timed)
        cfg_obj = conduit.meld(spell=config_id)
        assert isinstance(cfg_obj, PerfConfig)
        log1 = conduit.meld(spell=logger_id)
        assert isinstance(log1, PerfLogger)
        log2 = conduit.meld(spell=logger_id)
        assert isinstance(log2, PerfLogger)

        logger_is_cached: Optional[bool]
        if mode == "singleton":
            logger_is_cached = (log1 is log2)
            assert logger_is_cached
        else:
            logger_is_cached = None

        svc_obj = conduit.meld(spell=service_id)
        assert isinstance(svc_obj, PerfService)

        cfg_total_ns = _time_loop(lambda: conduit.meld(spell=config_id), warmup=WARMUP, tries=TRIES)
        log_total_ns = _time_loop(lambda: conduit.meld(spell=logger_id), warmup=WARMUP, tries=TRIES)
        svc_total_ns = _time_loop(lambda: conduit.meld(spell=service_id), warmup=WARMUP, tries=TRIES)

        return _PerfRow(
            name="melder",
            mode=mode,
            build_ns=build_ns,
            cfg_total_ns=cfg_total_ns,
            log_total_ns=log_total_ns,
            svc_total_ns=svc_total_ns,
            cfg_avg_us=_us_from_ns(cfg_total_ns) / TRIES,
            log_avg_us=_us_from_ns(log_total_ns) / TRIES,
            svc_avg_us=_us_from_ns(svc_total_ns) / TRIES,
            logger_is_cached=logger_is_cached,
        )
    finally:
        conduit.cleanup()


# ======================================================================================
# Dependency Injector runner
# ======================================================================================


def _dependency_injector_run(mode: str) -> _PerfRow:
    pytest.importorskip("dependency_injector", reason="dependency-injector is not installed")
    from dependency_injector import containers, providers

    if mode == "singleton":

        class _DIContainer(containers.DeclarativeContainer):
            config = providers.Singleton(PerfConfig)
            logger = providers.Singleton(PerfLogger, config=config)
            service = providers.Singleton(PerfService, logger=logger, config=config)

    elif mode == "transient":

        class _DIContainer(containers.DeclarativeContainer):
            config = providers.Factory(PerfConfig)
            logger = providers.Factory(PerfLogger, config=config)
            service = providers.Factory(PerfService, logger=logger, config=config)

    else:
        raise AssertionError(f"Unknown mode: {mode}")

    t0 = _ns()
    di_container = _DIContainer()
    build_ns = _ns() - t0

    # sanity (NOT timed)
    cfg_obj = di_container.config()
    assert isinstance(cfg_obj, PerfConfig)
    log1 = di_container.logger()
    assert isinstance(log1, PerfLogger)
    log2 = di_container.logger()
    assert isinstance(log2, PerfLogger)

    logger_is_cached: Optional[bool]
    if mode == "singleton":
        logger_is_cached = (log1 is log2)
        assert logger_is_cached
    else:
        logger_is_cached = None

    svc_obj = di_container.service()
    assert isinstance(svc_obj, PerfService)

    cfg_total_ns = _time_loop(di_container.config, warmup=WARMUP, tries=TRIES)
    log_total_ns = _time_loop(di_container.logger, warmup=WARMUP, tries=TRIES)
    svc_total_ns = _time_loop(di_container.service, warmup=WARMUP, tries=TRIES)

    return _PerfRow(
        name="dependency-injector",
        mode=mode,
        build_ns=build_ns,
        cfg_total_ns=cfg_total_ns,
        log_total_ns=log_total_ns,
        svc_total_ns=svc_total_ns,
        cfg_avg_us=_us_from_ns(cfg_total_ns) / TRIES,
        log_avg_us=_us_from_ns(log_total_ns) / TRIES,
        svc_avg_us=_us_from_ns(svc_total_ns) / TRIES,
        logger_is_cached=logger_is_cached,
    )


# ======================================================================================
# Lagom runner
# ======================================================================================


def _lagom_run(mode: str) -> _PerfRow:
    pytest.importorskip("lagom", reason="lagom is not installed")
    from lagom import Container as LagomContainer
    from lagom import Singleton as LagomSingleton

    lagom_container = LagomContainer()

    def _lagom_build_logger(container: LagomContainer) -> ILogger:
        cfg_obj = container[IConfig]
        return PerfLogger(config=cfg_obj)

    def _lagom_build_service(container: LagomContainer) -> IService:
        log_obj = container[ILogger]
        cfg_obj = container[IConfig]
        return PerfService(logger=log_obj, config=cfg_obj)

    t0 = _ns()
    if mode == "singleton":
        lagom_container[IConfig] = LagomSingleton(PerfConfig)
        lagom_container[ILogger] = LagomSingleton(_lagom_build_logger)
        lagom_container[IService] = LagomSingleton(_lagom_build_service)
    elif mode == "transient":
        lagom_container[IConfig] = PerfConfig
        lagom_container[ILogger] = _lagom_build_logger
        lagom_container[IService] = _lagom_build_service
    else:
        raise AssertionError(f"Unknown mode: {mode}")
    build_ns = _ns() - t0

    # sanity (NOT timed)
    cfg_obj = lagom_container[IConfig]
    assert isinstance(cfg_obj, PerfConfig)
    log1 = lagom_container[ILogger]
    assert isinstance(log1, PerfLogger)
    log2 = lagom_container[ILogger]
    assert isinstance(log2, PerfLogger)

    logger_is_cached: Optional[bool]
    if mode == "singleton":
        logger_is_cached = (log1 is log2)
        assert logger_is_cached
    else:
        logger_is_cached = None

    svc_obj = lagom_container[IService]
    assert isinstance(svc_obj, PerfService)

    cfg_total_ns = _time_loop(lambda: lagom_container[IConfig], warmup=WARMUP, tries=TRIES)
    log_total_ns = _time_loop(lambda: lagom_container[ILogger], warmup=WARMUP, tries=TRIES)
    svc_total_ns = _time_loop(lambda: lagom_container[IService], warmup=WARMUP, tries=TRIES)

    return _PerfRow(
        name="lagom",
        mode=mode,
        build_ns=build_ns,
        cfg_total_ns=cfg_total_ns,
        log_total_ns=log_total_ns,
        svc_total_ns=svc_total_ns,
        cfg_avg_us=_us_from_ns(cfg_total_ns) / TRIES,
        log_avg_us=_us_from_ns(log_total_ns) / TRIES,
        svc_avg_us=_us_from_ns(svc_total_ns) / TRIES,
        logger_is_cached=logger_is_cached,
    )


# ======================================================================================
# Injector (python-injector) runner
# ======================================================================================


def _injector_run(mode: str) -> _PerfRow:
    pytest.importorskip("injector", reason="injector is not installed")
    from injector import Injector as PyInjector
    from injector import Module, provider, singleton

    if mode == "singleton":

        class _PerfModule(Module):
            @provider
            @singleton
            def provide_config(self) -> IConfig:
                return PerfConfig()

            @provider
            @singleton
            def provide_logger(self, config: IConfig) -> ILogger:
                return PerfLogger(config=config)

            @provider
            @singleton
            def provide_service(self, logger: ILogger, config: IConfig) -> IService:
                return PerfService(logger=logger, config=config)

    elif mode == "transient":

        class _PerfModule(Module):
            @provider
            def provide_config(self) -> IConfig:
                return PerfConfig()

            @provider
            def provide_logger(self, config: IConfig) -> ILogger:
                return PerfLogger(config=config)

            @provider
            def provide_service(self, logger: ILogger, config: IConfig) -> IService:
                return PerfService(logger=logger, config=config)

    else:
        raise AssertionError(f"Unknown mode: {mode}")

    t0 = _ns()
    injector = PyInjector(_PerfModule())
    build_ns = _ns() - t0

    # sanity (NOT timed)
    cfg_obj = injector.get(IConfig)
    assert isinstance(cfg_obj, PerfConfig)
    log1 = injector.get(ILogger)
    assert isinstance(log1, PerfLogger)
    log2 = injector.get(ILogger)
    assert isinstance(log2, PerfLogger)

    logger_is_cached: Optional[bool]
    if mode == "singleton":
        logger_is_cached = (log1 is log2)
        assert logger_is_cached
    else:
        logger_is_cached = None

    svc_obj = injector.get(IService)
    assert isinstance(svc_obj, PerfService)

    cfg_total_ns = _time_loop(lambda: injector.get(IConfig), warmup=WARMUP, tries=TRIES)
    log_total_ns = _time_loop(lambda: injector.get(ILogger), warmup=WARMUP, tries=TRIES)
    svc_total_ns = _time_loop(lambda: injector.get(IService), warmup=WARMUP, tries=TRIES)

    return _PerfRow(
        name="injector",
        mode=mode,
        build_ns=build_ns,
        cfg_total_ns=cfg_total_ns,
        log_total_ns=log_total_ns,
        svc_total_ns=svc_total_ns,
        cfg_avg_us=_us_from_ns(cfg_total_ns) / TRIES,
        log_avg_us=_us_from_ns(log_total_ns) / TRIES,
        svc_avg_us=_us_from_ns(svc_total_ns) / TRIES,
        logger_is_cached=logger_is_cached,
    )


# ======================================================================================
# Dishka runner
# ======================================================================================


def _dishka_run(mode: str) -> _PerfRow:
    pytest.importorskip("dishka", reason="dishka is not installed")
    from dishka import Provider, Scope, make_container

    if mode not in ("singleton", "transient"):
        raise AssertionError(f"Unknown mode: {mode}")

    provider = Provider(scope=Scope.APP)
    if mode == "singleton":
        provider.provide(PerfConfig, provides=IConfig)
        provider.provide(PerfLogger, provides=ILogger)
        provider.provide(PerfService, provides=IService)
    else:
        provider.provide(PerfConfig, provides=IConfig, cache=False)
        provider.provide(PerfLogger, provides=ILogger, cache=False)
        provider.provide(PerfService, provides=IService, cache=False)

    t0 = _ns()
    dishka_container = make_container(provider)
    build_ns = _ns() - t0

    try:
        # sanity (NOT timed)
        cfg_obj = dishka_container.get(IConfig)
        assert isinstance(cfg_obj, PerfConfig)
        log1 = dishka_container.get(ILogger)
        assert isinstance(log1, PerfLogger)
        log2 = dishka_container.get(ILogger)
        assert isinstance(log2, PerfLogger)

        logger_is_cached: Optional[bool]
        if mode == "singleton":
            logger_is_cached = (log1 is log2)
            assert logger_is_cached
        else:
            logger_is_cached = None

        svc_obj = dishka_container.get(IService)
        assert isinstance(svc_obj, PerfService)

        cfg_total_ns = _time_loop(lambda: dishka_container.get(IConfig), warmup=WARMUP, tries=TRIES)
        log_total_ns = _time_loop(lambda: dishka_container.get(ILogger), warmup=WARMUP, tries=TRIES)
        svc_total_ns = _time_loop(lambda: dishka_container.get(IService), warmup=WARMUP, tries=TRIES)

        return _PerfRow(
            name="dishka",
            mode=mode,
            build_ns=build_ns,
            cfg_total_ns=cfg_total_ns,
            log_total_ns=log_total_ns,
            svc_total_ns=svc_total_ns,
            cfg_avg_us=_us_from_ns(cfg_total_ns) / TRIES,
            log_avg_us=_us_from_ns(log_total_ns) / TRIES,
            svc_avg_us=_us_from_ns(svc_total_ns) / TRIES,
            logger_is_cached=logger_is_cached,
        )
    finally:
        dishka_container.close()


# ======================================================================================
# Unified tests
# ======================================================================================


def _run_all_frameworks(mode: str) -> list[_PerfRow]:
    rows: list[_PerfRow] = []
    rows.append(_melder_run(mode))
    rows.append(_dependency_injector_run(mode))
    rows.append(_lagom_run(mode))
    rows.append(_injector_run(mode))
    rows.append(_dishka_run(mode))
    return rows


def test_perf_small_graph_singletons_all_frameworks() -> None:
    rows = _run_all_frameworks(mode="singleton")
    _print_table("Small graph perf (SINGLETON / UNIQUE semantics) — avg over many resolves (build excluded)", rows)


def test_perf_small_graph_transient_all_frameworks() -> None:
    rows = _run_all_frameworks(mode="transient")
    _print_table("Small graph perf (TRANSIENT / MANY semantics) — avg over many resolves (build excluded)", rows)

