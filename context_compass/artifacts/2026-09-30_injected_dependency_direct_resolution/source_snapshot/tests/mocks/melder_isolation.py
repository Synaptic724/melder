"""Per-test Spectrum and Melder isolation shared by every test in the suite.

Owner rule (2026-09-27): every test that can reach Spectrum or Melder starts and ends with
no Spectrum and a fresh cold Aether. The autouse fixture below is defined once, here, and
registered by importing it into a conftest: tests/conftest.py applies it to every test, and
tests/component/spectrum/conftest.py imports it again so runs scoped with
--confcutdir=tests/component/spectrum keep it. Where both conftests apply, the nearer
definition wins, so each test runs it once.
"""

from collections.abc import Iterator
import importlib

import melder_ops
import melder_ops.command_center.spectrum.spectrum as spectrum_module
from melder import Aether, Conduit, Spellbook
import pytest


@pytest.fixture(autouse=True)
def reset_spectrum_and_melder() -> Iterator[None]:
    """Retire both runtime owners and refresh native class references around each test.

    Contract:
        Spectrum cleanup resets its singleton and published helper singletons.
        Melder's test reset retires Aether and its owned services - frames, books,
        roots and registrations included - so no spell one test registers can
        collide with, or be resolved by, another test. Rebind the imported
        Spellbook/Conduit class references exactly as Melder's integration fixtures
        do. Rebuild a cold world after teardown for neighboring tests.

    Cost:
        About 2.5 ms per test on Python 3.14.7t with Melder 0.2.77: both resets and
        the package reload, measured 2026-09-27.

    The public package is refreshed at entry because legacy Spectrum unit tests
    reload its implementation module. All test bodies still execute in this
    interpreter; no source strings or subprocess test runner are involved.
    """
    if spectrum_module.Spectrum._instance is not None:
        spectrum_module.Spectrum._instance.cleanup()
    Aether._reset_singleton_for_tests()
    world = Aether()
    Spellbook._aether = world
    Conduit._aether = world
    importlib.reload(melder_ops)
    try:
        yield
    finally:
        try:
            if spectrum_module.Spectrum._instance is not None:
                spectrum_module.Spectrum._instance.cleanup()
        finally:
            Aether._reset_singleton_for_tests()
            world = Aether()
            Spellbook._aether = world
            Conduit._aether = world
