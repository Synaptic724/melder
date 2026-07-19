"""
Component tests for the restore-policy activation wiring
(parallel_restore_ulid_identity S4 + REOPEN 2026-07-19): real hosted boot -
Aether hosts the Crystallizer, activation reads the three defaulted restore
knobs through their typed configuration properties and installs the
loader-owned PhaseScheduler. No checkpoint or filesystem I/O; this is the
facade wiring slice between the config unit suite and the restore
integration arcs.

The headline row IS the red-run fixture shape: a configuration built
WITHOUT with_defaults() (roots only) activating the crystallizer - the
exact path that KeyError'd before activate() moved onto the typed
defaulted properties.

Runs only on 3.14t (melder package root import chain).
"""
import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.crystallizer.configuration.crystallizer_configuration import (
    CrystallizerConfiguration,
)
from melder.crystallizer.crystallizer import Crystallizer
from melder.nexus.nexus import Nexus


@pytest.fixture(autouse=True)
def reset_crystallizer_singleton():
    """
    Reset the world singletons and boot a hosting Aether around each test.

    Contract:
        First-time Crystallizer initialization REQUIRES the hosting
        Aether; Aether() constructs the hosted crystallizer, so the later
        Crystallizer() call returns it.

    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    Aether()
    yield
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()


def _restore_pool(crystallizer):
    """
    Read the loader-owned restore pool slot (lifecycle surface).

    The pool has no public read by design; the slot is the documented
    lifecycle signal for these wiring rows.

    Returns:
        Optional[PhaseScheduler]: The owned pool, or None.
    """
    return crystallizer._crystal_loader_system._restore_scheduler


def test_roots_only_configuration_activates_and_installs_the_parallel_pool():
    """
    Purpose:
        Headline REOPEN regression at the failing site: activation over a
        configuration that never set the restore knobs (the shape ~120
        fixtures activate) must succeed and wire the schema-default
        parallel pool.
    Contract:
        - activate() raises nothing (the old code KeyError'd here).
        - The loader owns one live scheduler (restore_parallel_enabled
          defaults True: parallel is the driver).
    Returns:
        None.
    Raises:
        AssertionError: If activation fails or no pool is wired.
    """
    configuration = CrystallizerConfiguration().with_user_source_root_paths(
        (".",)
    ).activate()
    crystallizer = Crystallizer()
    crystallizer.activate(configuration)
    assert crystallizer.activated is True
    pool = _restore_pool(crystallizer)
    assert pool is not None
    assert pool.cleaned is False


def test_disabled_parallel_knob_wires_the_sequential_driver():
    """
    Purpose:
        Verify the owner polarity ruling end to end: explicit False on
        restore_parallel_enabled selects the sequential fallback - the
        loader owns no pool.
    Contract:
        Activation succeeds and the loader pool slot is None.
    Returns:
        None.
    Raises:
        AssertionError: If a pool is wired despite the False selector.
    """
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.set_property("restore_parallel_enabled", False)
    configuration.activate()
    crystallizer = Crystallizer()
    crystallizer.activate(configuration)
    assert crystallizer.activated is True
    assert _restore_pool(crystallizer) is None


def test_explicit_scheduler_knobs_reach_the_loader_pool():
    """
    Purpose:
        Verify explicit worker/timeout knobs travel config -> activate ->
        loader -> scheduler (the S2 explicit construction lane).
    Contract:
        The wired pool reports the configured values through its public
        `workers` / `barrier_timeout_ms` properties.
    Returns:
        None.
    Raises:
        AssertionError: If an explicit knob is lost in the wiring.
    """
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.set_property("restore_scheduler_workers", 2)
    configuration.set_property(
        "restore_scheduler_barrier_timeout_milliseconds", 9000
    )
    configuration.activate()
    crystallizer = Crystallizer()
    crystallizer.activate(configuration)
    pool = _restore_pool(crystallizer)
    assert pool is not None
    assert pool.workers == 2
    assert pool.barrier_timeout_ms == 9000


def test_deactivate_keeps_the_pool_and_reactivation_replaces_it():
    """
    Purpose:
        Verify the activation lifecycle over the pool: deactivate() is
        reversible (not teardown - the pool survives), and re-activation
        replaces the pool under the reconfiguration law (old pool cleaned,
        new pool distinct).
    Contract:
        - After deactivate(): same live pool object remains owned.
        - After activate() again: prior pool cleaned, different live pool.
    Returns:
        None.
    Raises:
        AssertionError: If deactivation tears the pool down or
            re-activation leaks the prior pool.
    """
    configuration = CrystallizerConfiguration().with_defaults().activate()
    crystallizer = Crystallizer()
    crystallizer.activate(configuration)
    first = _restore_pool(crystallizer)
    assert first is not None

    crystallizer.deactivate()
    assert _restore_pool(crystallizer) is first
    assert first.cleaned is False

    crystallizer.activate()
    second = _restore_pool(crystallizer)
    assert first.cleaned is True
    assert second is not first
    assert second.cleaned is False
