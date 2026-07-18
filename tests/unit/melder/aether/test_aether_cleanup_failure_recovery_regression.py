"""Regression: BUG-149 (2026-07-17 audit) - Aether survives failed teardown.

Symptom:
    ``Aether.cleanup()`` marked the instance cleaned before cascading child
    cleanup but reset the singleton bookkeeping (``_instance`` /
    ``_initialized``) only after every child succeeded. One child cleanup
    failure re-raised before the reset, so a subsequent ``Aether()`` returned
    the same cleaned husk forever: every public call died on the cleaned-state
    guard and Melder's global runtime was permanently disabled for the rest of
    the interpreter process.

Contract under test:
    Singleton bookkeeping resets in a ``finally``: the child error is logged
    and re-raised, but the cleaned instance is never republished and a later
    ``Aether()`` constructs a fresh root.
"""

from typing import Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.nexus.nexus import Nexus


@pytest.fixture(autouse=True)
def fresh_singletons() -> Iterator[None]:
    """Reset the Aether/Nexus/utility singletons around each test.

    Contract:
        - Discards any pre-existing singleton state before the test body runs
          so the test exercises a true first construction.
        - Restores clean singleton state afterwards so later tests are not
          coupled to this module's torn-down instances.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    yield
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()


def test_failed_child_cleanup_does_not_brick_the_singleton() -> None:
    """One failing child teardown must leave ``Aether()`` reconstructible.

    Choreography (mirrors the audit repro):
        1. Boot the singleton, then inject a ``Nexus.cleanup`` failure.
        2. ``Aether.cleanup()`` raises the injected error (fail-fast cascade
           semantics are unchanged).
        3. On the broken code, ``Aether()`` afterwards returned the same
           object with ``cleaned=True``; under the fixed contract the
           bookkeeping reset ran in the ``finally``, so a fresh root boots.

    Contract assertions:
        - The injected child error propagates to the cleanup caller.
        - Singleton bookkeeping is reset despite the failure.
        - The failed instance stays terminally cleaned but is never
          republished: the next ``Aether()`` is a fresh, live root.
    """
    aether = Aether()
    original_nexus_cleanup = Nexus.cleanup

    def failing_nexus_cleanup(self: Nexus) -> None:
        """Injected child teardown failure (raises before any teardown)."""
        raise RuntimeError("injected nexus teardown failure")

    Nexus.cleanup = failing_nexus_cleanup
    try:
        with pytest.raises(RuntimeError, match="injected nexus teardown failure"):
            aether.cleanup()
    finally:
        Nexus.cleanup = original_nexus_cleanup

    assert aether.cleaned is True, (
        "the failed instance must stay terminally cleaned"
    )
    assert Aether._instance is None, (
        "singleton identity must reset even when a child cleanup fails "
        "(the audited BUG-149 symptom: the cleaned husk stayed published)"
    )
    assert Aether._initialized is False, (
        "the initialized latch must reset even when a child cleanup fails"
    )

    fresh = Aether()
    assert fresh is not aether, (
        "Aether() republished the cleaned husk instead of constructing a "
        "fresh root"
    )
    assert fresh.cleaned is False
    assert Aether._initialized is True


def test_successful_cleanup_still_resets_and_allows_reboot() -> None:
    """The healthy teardown lane must be unchanged by the finally move.

    Contract assertions:
        - A clean teardown marks the instance cleaned and resets the
          singleton bookkeeping exactly as before.
        - A subsequent ``Aether()`` boots a fresh, live root.
    """
    aether = Aether()
    aether.cleanup()

    assert aether.cleaned is True
    assert Aether._instance is None
    assert Aether._initialized is False

    fresh = Aether()
    assert fresh is not aether
    assert fresh.cleaned is False
    assert Aether._initialized is True
