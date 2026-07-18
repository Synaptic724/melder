"""Regression: BUG-279 (2026-07-17 audit) - Nexus same-sink refresh ownership.

Symptom:
    Refreshing Nexus with the same raw sink created a new SafeLogger wrapper,
    compared WRAPPER identities, and cleaned the prior wrapper - which
    terminally cleaned the raw sink the replacement wrapper still owned. The
    replacement reported attached but its next log call died on the cleaned
    sink. Reproduced 20/20 in the audit.

Contract under test:
    Alias detection happens at raw-sink identity: a same-sink refresh reuses
    the existing wrapper and never tears the shared sink down; a
    different-sink refresh still retires the displaced wrapper exactly once.
"""

import logging
from typing import Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.nexus.nexus import Nexus


class CleanupTrackingLogger(logging.Logger):
    """Stdlib logger double that records lifecycle cleanup calls.

    Contract:
        - Passes SafeLogger's isinstance gate (it IS a logging.Logger).
        - Counts ``cleanup()`` invocations so tests can assert exactly when
          ownership retirement happens.
    """

    def __init__(self, name: str) -> None:
        """Create the tracking logger with a zeroed cleanup counter."""
        super().__init__(name)
        self.cleanup_calls: int = 0

    def cleanup(self) -> None:
        """Record one ownership-retirement call."""
        self.cleanup_calls += 1


@pytest.fixture(autouse=True)
def fresh_singletons() -> Iterator[None]:
    """Reset the Aether/Nexus/utility singletons around each test.

    Contract:
        - Discards any pre-existing singleton state before the test body runs.
        - Restores clean singleton state afterwards so later tests are not
          coupled to this module's logger arrangements.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    yield
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()


def test_same_sink_refresh_reuses_wrapper_and_preserves_the_sink() -> None:
    """The audited repro: refresh with the identical raw sink twice.

    Contract assertions:
        - The refresh never cleans the raw sink the live wrapper owns
          (old code cleaned it once per same-sink refresh).
        - The wrapper still references the sink and stays usable: a log call
          after the refresh reaches the healthy sink without raising.
    """
    Aether()
    sink = CleanupTrackingLogger("melder.tests.bug279.sink_same")
    sink.addHandler(logging.NullHandler())

    nexus = Nexus(logger=sink)
    assert nexus._logger._logger is sink
    assert sink.cleanup_calls == 0

    refreshed = Nexus(logger=sink)

    assert refreshed is nexus
    assert sink.cleanup_calls == 0, (
        "same-sink refresh cleaned the raw sink retained by the replacement "
        "wrapper (the audited BUG-279 symptom)"
    )
    assert nexus._logger._logger is sink
    assert nexus._logger.is_attached is True
    # The post-refresh wrapper must still be able to log through the sink.
    nexus._logger.error("post-refresh log", "test_method", exc_info=False)


def test_repeated_same_sink_refreshes_stay_ownership_neutral() -> None:
    """Many same-sink refreshes accumulate zero teardown calls.

    Contract assertions:
        - N refreshes with one sink leave its cleanup counter at zero and
          the wrapper attached.
    """
    Aether()
    sink = CleanupTrackingLogger("melder.tests.bug279.sink_repeat")

    nexus = Nexus(logger=sink)
    for _ in range(5):
        Nexus(logger=sink)

    assert sink.cleanup_calls == 0
    assert nexus._logger._logger is sink


def test_different_sink_refresh_still_retires_the_displaced_wrapper() -> None:
    """Replacement semantics are unchanged when the sinks genuinely differ.

    Contract assertions:
        - Refreshing with a different sink retires the displaced wrapper
          (its sink is cleaned exactly once).
        - The new sink is installed, untouched, and usable.
    """
    Aether()
    sink_a = CleanupTrackingLogger("melder.tests.bug279.sink_a")
    sink_b = CleanupTrackingLogger("melder.tests.bug279.sink_b")

    nexus = Nexus(logger=sink_a)
    Nexus(logger=sink_b)

    assert sink_a.cleanup_calls == 1, (
        "a genuinely displaced wrapper must still be retired exactly once"
    )
    assert sink_b.cleanup_calls == 0
    assert nexus._logger._logger is sink_b
