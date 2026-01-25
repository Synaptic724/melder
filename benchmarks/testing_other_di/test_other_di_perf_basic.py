from __future__ import annotations

import time

import pytest

from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from tests.mocks.spellbook.protocols import IConfig
from tests.mocks.spellbook.protocols import ILogger
from tests.mocks.spellbook.protocols import IService


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
        - Resolves config via SpellContract (Melder usage).
        - Precomputes some deterministic formatting data.
    Notes:
        - For other DI frameworks we will inject config explicitly (via provider
          factories) to avoid relying on SpellContract defaults.
    """

    def __init__(self, config: IConfig = SpellContract(spellframe=IConfig)) -> None:
        self.config = config
        self.levels = {"DEBUG": 10, "INFO": 20, "WARN": 30, "ERROR": 40}
        self.prefix_cache = [f"[{i:04d}]" for i in range(2000)]


class PerfService:
    """
    Purpose:
        Provide a service that depends on both logger + config.
    Contract:
        - Resolves dependencies via SpellContract (Melder usage).
        - Builds a deterministic routing table in __init__.
    Notes:
        - For other DI frameworks we will inject explicitly (via provider
          factories) to avoid relying on SpellContract defaults.
    """

    def __init__(
            self,
            logger: ILogger = SpellContract(spellframe=ILogger),
            config: IConfig = SpellContract(spellframe=IConfig),
    ) -> None:
        self.logger = logger
        self.config = config
        self.routing = {f"route{i}": (i % 17, i % 23) for i in range(5000)}


def _ms(seconds: float) -> float:
    return seconds * 1000.0


def _us(seconds: float) -> float:
    return seconds * 1_000_000.0


def _print_row(
        *,
        name: str,
        build_s: float,
        get_config_s: float,
        get_logger_s: float,
        get_logger_2nd_s: float,
        get_service_s: float,
) -> None:
    print(
        f"{name} timings: "
        f"build={_ms(build_s):.3f}ms, "
        f"get_config={_ms(get_config_s):.3f}ms, "
        f"get_logger={_ms(get_logger_s):.3f}ms, "
        f"get_logger_2nd={_us(get_logger_2nd_s):.2f}us, "
        f"get_service={_ms(get_service_s):.3f}ms"
    )


def test_perf_competitors_small_graph_singletons() -> None:
    """
    Purpose:
        Compare several DI frameworks using the same object graph:
            PerfService -> (PerfLogger, PerfConfig)
    Contract:
        - Each framework is configured to behave like "singleton / unique".
        - We time:
            - container build/config step (framework-specific)
            - first resolve of config/logger/service (cold)
            - second resolve of logger (warm hit)
    Notes:
        - Run with: pytest -s -k test_perf_competitors_small_graph_singletons
        - No thresholds asserted; prints numbers for local comparison.
    """

    # -------------------------
    # Dependency Injector
    # -------------------------
    dependency_injector = pytest.importorskip(
        "dependency_injector",
        reason="dependency-injector is not installed",
    )
    from dependency_injector import containers, providers  # type: ignore[import-not-found]

    class _DIContainer(containers.DeclarativeContainer):
        """
        Purpose:
            Provide singleton providers for PerfConfig/PerfLogger/PerfService.
        Notes:
            We inject explicitly here (no reliance on PerfLogger defaults).
        """

        config = providers.Singleton(PerfConfig)
        logger = providers.Singleton(PerfLogger, config=config)
        service = providers.Singleton(PerfService, logger=logger, config=config)

    t0 = time.perf_counter()
    di_container = _DIContainer()
    di_build_s = time.perf_counter() - t0

    t0 = time.perf_counter()
    di_cfg = di_container.config()
    di_get_config_s = time.perf_counter() - t0
    assert isinstance(di_cfg, PerfConfig)

    t0 = time.perf_counter()
    di_log = di_container.logger()
    di_get_logger_s = time.perf_counter() - t0
    assert isinstance(di_log, PerfLogger)

    t0 = time.perf_counter()
    di_log2 = di_container.logger()
    di_get_logger_2nd_s = time.perf_counter() - t0
    assert di_log is di_log2

    t0 = time.perf_counter()
    di_svc = di_container.service()
    di_get_service_s = time.perf_counter() - t0
    assert isinstance(di_svc, PerfService)

    _print_row(
        name="dependency-injector",
        build_s=di_build_s,
        get_config_s=di_get_config_s,
        get_logger_s=di_get_logger_s,
        get_logger_2nd_s=di_get_logger_2nd_s,
        get_service_s=di_get_service_s,
    )

    # -------------------------
    # Lagom
    # -------------------------
    pytest.importorskip("lagom", reason="lagom is not installed")
    from lagom import Container as LagomContainer  # type: ignore[import-not-found]
    from lagom import Singleton as LagomSingleton  # type: ignore[import-not-found]

    def _lagom_build_logger(container: LagomContainer) -> ILogger:
        cfg = container[IConfig]
        return PerfLogger(config=cfg)

    def _lagom_build_service(container: LagomContainer) -> IService:
        log = container[ILogger]
        cfg = container[IConfig]
        return PerfService(logger=log, config=cfg)

    t0 = time.perf_counter()
    lagom_container = LagomContainer()
    lagom_container[IConfig] = LagomSingleton(PerfConfig)
    lagom_container[ILogger] = LagomSingleton(_lagom_build_logger)
    lagom_container[IService] = LagomSingleton(_lagom_build_service)
    lagom_build_s = time.perf_counter() - t0

    t0 = time.perf_counter()
    lagom_cfg = lagom_container[IConfig]
    lagom_get_config_s = time.perf_counter() - t0
    assert isinstance(lagom_cfg, PerfConfig)

    t0 = time.perf_counter()
    lagom_log = lagom_container[ILogger]
    lagom_get_logger_s = time.perf_counter() - t0
    assert isinstance(lagom_log, PerfLogger)

    t0 = time.perf_counter()
    lagom_log2 = lagom_container[ILogger]
    lagom_get_logger_2nd_s = time.perf_counter() - t0
    assert lagom_log is lagom_log2

    t0 = time.perf_counter()
    lagom_svc = lagom_container[IService]
    lagom_get_service_s = time.perf_counter() - t0
    assert isinstance(lagom_svc, PerfService)

    _print_row(
        name="lagom",
        build_s=lagom_build_s,
        get_config_s=lagom_get_config_s,
        get_logger_s=lagom_get_logger_s,
        get_logger_2nd_s=lagom_get_logger_2nd_s,
        get_service_s=lagom_get_service_s,
    )
    # -------------------------
    # Injector (python-injector)
    # -------------------------
    pytest.importorskip("injector", reason="injector is not installed")
    from injector import Injector as PyInjector
    from injector import Module, provider, singleton


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


    t0 = time.perf_counter()
    injector = PyInjector(_PerfModule())
    injector_build_s = time.perf_counter() - t0

    t0 = time.perf_counter()
    inj_cfg = injector.get(IConfig)
    injector_get_config_s = time.perf_counter() - t0
    assert isinstance(inj_cfg, PerfConfig)

    t0 = time.perf_counter()
    inj_log = injector.get(ILogger)
    injector_get_logger_s = time.perf_counter() - t0
    assert isinstance(inj_log, PerfLogger)

    t0 = time.perf_counter()
    inj_log2 = injector.get(ILogger)
    injector_get_logger_2nd_s = time.perf_counter() - t0
    assert inj_log is inj_log2

    t0 = time.perf_counter()
    inj_svc = injector.get(IService)
    injector_get_service_s = time.perf_counter() - t0
    assert isinstance(inj_svc, PerfService)

    _print_row(
        name="injector",
        build_s=injector_build_s,
        get_config_s=injector_get_config_s,
        get_logger_s=injector_get_logger_s,
        get_logger_2nd_s=injector_get_logger_2nd_s,
        get_service_s=injector_get_service_s,
    )


    # -------------------------
    # Dishka
    # -------------------------
    pytest.importorskip("dishka", reason="dishka is not installed")
    from dishka import Provider, Scope, make_container, provide  # type: ignore[import-not-found]

    class _DishkaProvider(Provider):
        """
        Purpose:
            Provide APP-scoped cached instances for the perf objects.
        Notes:
            We define explicit factories with typed params so we don't rely on
            SpellContract defaults.
        """

        scope = Scope.APP

        @provide
        def get_config(self) -> IConfig:
            return PerfConfig()

        @provide
        def get_logger(self, config: IConfig) -> ILogger:
            return PerfLogger(config=config)

        @provide
        def get_service(self, logger: ILogger, config: IConfig) -> IService:
            return PerfService(logger=logger, config=config)

    t0 = time.perf_counter()
    dishka_container = make_container(_DishkaProvider())
    dishka_build_s = time.perf_counter() - t0

    try:
        t0 = time.perf_counter()
        d_cfg = dishka_container.get(IConfig)
        dishka_get_config_s = time.perf_counter() - t0
        assert isinstance(d_cfg, PerfConfig)

        t0 = time.perf_counter()
        d_log = dishka_container.get(ILogger)
        dishka_get_logger_s = time.perf_counter() - t0
        assert isinstance(d_log, PerfLogger)

        t0 = time.perf_counter()
        d_log2 = dishka_container.get(ILogger)
        dishka_get_logger_2nd_s = time.perf_counter() - t0
        assert d_log is d_log2

        t0 = time.perf_counter()
        d_svc = dishka_container.get(IService)
        dishka_get_service_s = time.perf_counter() - t0
        assert isinstance(d_svc, PerfService)

        _print_row(
            name="dishka",
            build_s=dishka_build_s,
            get_config_s=dishka_get_config_s,
            get_logger_s=dishka_get_logger_s,
            get_logger_2nd_s=dishka_get_logger_2nd_s,
            get_service_s=dishka_get_service_s,
        )
    finally:
        # Dishka APP container isn't a context manager; close explicitly.
        dishka_container.close()
