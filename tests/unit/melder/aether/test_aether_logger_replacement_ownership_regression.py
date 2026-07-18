"""Regression: BUG-278 (2026-07-17 audit) - Aether logger replacement ownership.

Symptoms:
    1. Direct attachment replaced ``_logger`` without retiring the previous
       wrapper: attach cleanup-capable A, attach B, clean Aether - B was
       cleaned once, A was never cleaned (orphaned owned sink).
    2. Automatic enable stored its result before validating it: a resolver
       returning None raised, but ``aether.logger`` had already become None -
       the working logger A was uncleaned and unreachable, and a failed
       enable destroyed working logging state.

Contracts under test:
    - Successful replacement retires the displaced owned wrapper.
    - Same-sink re-attachment never tears the shared sink down.
    - Failed automatic resolution preserves the existing working logger.
"""

import logging
from types import SimpleNamespace
from typing import Any, Iterator

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


def test_direct_replacement_retires_displaced_owned_sink() -> None:
    """The audited path 1: attach A, attach B - A must be retired.

    Contract assertions:
        - Attaching B cleans the displaced A exactly once.
        - The wrapper now owns B; final Aether cleanup reaches B.
        - A is not cleaned a second time by final teardown.
    """
    aether = Aether()
    sink_a = CleanupTrackingLogger("melder.tests.bug278.sink_a")
    sink_b = CleanupTrackingLogger("melder.tests.bug278.sink_b")

    aether.attach_logger(sink_a)
    assert aether.logger is sink_a
    assert sink_a.cleanup_calls == 0

    aether.attach_logger(sink_b)

    assert sink_a.cleanup_calls == 1, (
        "the displaced owned sink was orphaned by re-attachment "
        "(the audited BUG-278 symptom)"
    )
    assert aether.logger is sink_b

    aether.cleanup()
    assert sink_b.cleanup_calls == 1
    assert sink_a.cleanup_calls == 1


def test_same_sink_reattachment_never_tears_the_sink_down() -> None:
    """Re-attaching the sink the wrapper already owns must not clean it.

    Contract assertions:
        - Same-sink re-attachment is ownership-neutral (sink-identity
          aliasing law, mirrors BUG-279).
        - The attached logger remains the same sink and stays usable.
    """
    aether = Aether()
    sink_a = CleanupTrackingLogger("melder.tests.bug278.sink_same")

    aether.attach_logger(sink_a)
    aether.attach_logger(sink_a)

    assert sink_a.cleanup_calls == 0, (
        "same-sink re-attachment tore down the raw sink the replacement "
        "wrapper still owns"
    )
    assert aether.logger is sink_a
    aether.cleanup()
    assert sink_a.cleanup_calls == 1


def test_detach_to_null_retires_the_displaced_sink() -> None:
    """``attach_logger(None)`` detaches AND retires the working sink.

    Contract assertions:
        - Detaching back to the null wrapper cleans the displaced sink once.
        - The wrapper reports no attached raw logger afterwards.
    """
    aether = Aether()
    sink_a = CleanupTrackingLogger("melder.tests.bug278.sink_detach")

    aether.attach_logger(sink_a)
    aether.attach_logger(None)

    assert sink_a.cleanup_calls == 1
    assert aether.logger is None


def _arm_automatic_logging(aether: Aether, resolver: Any) -> None:
    """Arm the automatic logger path with one resolver double.

    Contract:
        - Satisfies every ``enable_logging()`` automatic-lane gate: activated
          root configuration with channel activation enabled, utility-system
          activation on, and a registered channel resolver.

    Args:
        aether:
            The live Aether under test.
        resolver:
            Channel-logger resolver callable installed on the hosted utility
            system.
    """
    aether._activated = True
    # The namespace carries a no-op cleanup so Aether teardown's
    # configuration-cleanup step stays green under the fixture reset.
    aether._configuration = SimpleNamespace(
        channel_logger_activation_enabled=True,
        cleanup=lambda: None,
    )
    utility_system = aether._aether_utility_system
    utility_system.set_channel_logger_activation_enabled(True)
    utility_system.register_channel_logger_resolver(resolver)


def test_failed_automatic_resolution_preserves_the_working_logger() -> None:
    """The audited path 2: a None-resolving enable must not destroy state.

    Contract assertions:
        - ``enable_logging()`` raises when resolution yields no logger.
        - The previously attached working logger is still installed and was
          never cleaned (old code: ``aether.logger`` became None and the
          working sink was orphaned).
    """
    aether = Aether()
    sink_a = CleanupTrackingLogger("melder.tests.bug278.sink_working")
    aether.attach_logger(sink_a)

    def none_resolver(**kwargs: Any) -> None:
        """Resolver double reproducing the audited None resolution."""
        return None

    _arm_automatic_logging(aether, none_resolver)

    with pytest.raises(RuntimeError, match="returned no logger"):
        aether.enable_logging()

    assert aether.logger is sink_a, (
        "a failed automatic enable destroyed the working logger "
        "(the audited BUG-278 symptom)"
    )
    assert sink_a.cleanup_calls == 0
    aether.cleanup()
    assert sink_a.cleanup_calls == 1


def test_successful_automatic_replacement_retires_the_displaced_sink() -> None:
    """A working automatic enable still retires the displaced owned wrapper.

    Contract assertions:
        - The resolver-provided sink becomes the attached logger.
        - The displaced explicit sink is cleaned exactly once.
    """
    aether = Aether()
    sink_a = CleanupTrackingLogger("melder.tests.bug278.sink_old")
    sink_auto = CleanupTrackingLogger("melder.tests.bug278.sink_auto")
    aether.attach_logger(sink_a)

    def sink_resolver(**kwargs: Any) -> CleanupTrackingLogger:
        """Resolver double returning one concrete automatic sink."""
        return sink_auto

    _arm_automatic_logging(aether, sink_resolver)

    aether.enable_logging()

    assert aether.logger is sink_auto
    assert sink_a.cleanup_calls == 1
    assert sink_auto.cleanup_calls == 0
