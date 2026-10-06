"""Ordinary in-process Spectrum integration fixtures with explicit singleton isolation.

The autouse reset, reset_spectrum_and_melder, is defined in tests/mocks/melder_isolation.py
and applied to every test by tests/conftest.py. It is imported here as well so runs scoped
with --confcutdir=tests/component/spectrum keep it; the nearer definition wins, so each
test runs it once.
"""

from typing import TYPE_CHECKING

import melder_ops.command_center.spectrum.spectrum as spectrum_module
import pytest

from tests.mocks.melder_isolation import reset_spectrum_and_melder

if TYPE_CHECKING:
    from melder_ops.command_center.spectrum.spectrum import Spectrum


@pytest.fixture
def spectrum() -> Spectrum:
    """Borrow the current Spectrum class's fresh singleton for one integration test.

    The autouse fixture owns cleanup. Resolve from the live implementation module
    so another suite's module reload cannot leave this fixture using an old class.
    """
    return spectrum_module.Spectrum.get_instance()
