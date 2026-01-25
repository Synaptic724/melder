from __future__ import annotations

import time

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.protocols import IConfig
from tests.mocks.spellbook.protocols import ILogger
from tests.mocks.spellbook.protocols import IService


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
        - Resolves config via SpellContract.
        - Precomputes some deterministic formatting data.
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
        - Resolves dependencies via SpellContract.
        - Builds a deterministic routing table in __init__.
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


def test_conduit_perf_conjure_and_meld_timings() -> None:
    """
    Purpose:
        Time conjure + first-time meld for a small, dependency-linked graph.
    Notes:
        - Run with: pytest -s -k test_conduit_perf_conjure_and_meld_timings
        - This test does not assert on timing thresholds; it only prints timings.
    """
    cfg = Configuration()
    cfg.dynamic_defaults()
    cfg.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook = Spellbook(configuration=cfg)

    # Spellbook starts with an active binding transaction until conjure().
    config_id = spellbook.bind(
        spell=PerfConfig,
        existence=Existence.unique,
        permissions="create",
        spellframe=IConfig,
    )
    logger_id = spellbook.bind(
        spell=PerfLogger,
        existence=Existence.unique,
        permissions="create",
        spellframe=ILogger,
    )
    service_id = spellbook.bind(
        spell=PerfService,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
    )

    t0 = time.perf_counter()
    conduit = spellbook.conjure(name="perf-root", automatic=True)
    conjure_s = time.perf_counter() - t0
    try:
        t0 = time.perf_counter()
        cfg = conduit.meld(spell=config_id)
        cfg_s = time.perf_counter() - t0
        assert isinstance(cfg, PerfConfig)

        t0 = time.perf_counter()
        log = conduit.meld(spell=logger_id)
        log_2s = time.perf_counter() - t0
        assert isinstance(log, PerfLogger)

        t0 = time.perf_counter()
        log = conduit.meld(spell=logger_id)
        log_s = time.perf_counter() - t0
        assert isinstance(log, PerfLogger)

        t0 = time.perf_counter()
        svc = conduit.meld(spell=service_id)
        svc_s = time.perf_counter() - t0
        assert isinstance(svc, PerfService)

        print(
            "Perf timings (ms): "
            f"conjure={_ms(conjure_s):.3f}, "
            f"meld_config={_ms(cfg_s):.3f}, "
            f"meld_logger={_ms(log_2s):.3f}, "
            f"meld_logger_2nd={_ms(log_s):.3f}, "
            f"meld_service={_ms(svc_s):.3f}"
        )
    finally:
        conduit.cleanup()
