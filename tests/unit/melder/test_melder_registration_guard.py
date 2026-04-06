"""
Unit tests for MelderRegistrationGuard.

These tests pin the public contract described in melder/__melder_registration_guard__.py:

- Internal objects/classes are tagged via:
    __melder_internal__ is __melder_registration_guard__.sentinel

- Tagged candidates are rejected by assert_allowed() with InternalRegistrationError.
- Untagged candidates are allowed.
"""

from concurrent.futures import ThreadPoolExecutor
import threading

import pytest


def test_guard_is_singleton() -> None:
    # Import inside the test so failure modes are obvious to the user
    # (e.g., Python version gating, missing modules).
    from melder.__melder_registration_guard__ import MelderRegistrationGuard
    from melder.__melder_registration_guard__ import __melder_registration_guard__ as guard

    assert isinstance(guard, MelderRegistrationGuard)
    assert guard is MelderRegistrationGuard()
    assert MelderRegistrationGuard() is MelderRegistrationGuard()


def test_sentinel_is_stable_identity() -> None:
    from melder.__melder_registration_guard__ import __melder_registration_guard__ as guard

    s1 = guard.sentinel
    s2 = guard.sentinel
    assert s1 is s2


def test_guard_concurrent_construction_returns_one_instance() -> None:
    from melder.__melder_registration_guard__ import MelderRegistrationGuard

    worker_count = 16
    original_instance = MelderRegistrationGuard._instance
    start_barrier = threading.Barrier(worker_count)

    def build_instance_id() -> int:
        start_barrier.wait()
        return id(MelderRegistrationGuard())

    try:
        MelderRegistrationGuard._instance = None

        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            futures = [executor.submit(build_instance_id) for _ in range(worker_count)]
            instance_ids = [future.result() for future in futures]

        assert len(set(instance_ids)) == 1
        assert MelderRegistrationGuard._instance is not None
    finally:
        MelderRegistrationGuard._instance = original_instance


def test_is_internal_false_for_untagged_class_and_instance() -> None:
    from melder.__melder_registration_guard__ import __melder_registration_guard__ as guard

    class Untagged:
        pass

    assert guard.is_internal(Untagged) is False
    assert guard.is_internal(Untagged()) is False


def test_is_internal_true_for_tagged_class_and_instance() -> None:
    from melder.__melder_registration_guard__ import __melder_registration_guard__ as guard

    class Tagged:
        pass

    Tagged.__melder_internal__ = guard.sentinel

    assert guard.is_internal(Tagged) is True
    assert guard.is_internal(Tagged()) is True


def test_assert_allowed_allows_untagged_candidates() -> None:
    from melder.__melder_registration_guard__ import __melder_registration_guard__ as guard

    class Untagged:
        pass

    # Should not raise
    guard.assert_allowed(Untagged, context="bind")
    guard.assert_allowed(Untagged(), context="bind")


def test_assert_allowed_rejects_tagged_candidates_with_internal_registration_error() -> None:
    from melder.__melder_registration_guard__ import __melder_registration_guard__ as guard
    from melder.utilities.custom_exceptions.internal_registration_error import (
        InternalRegistrationError,
    )

    class Tagged:
        pass

    Tagged.__melder_internal__ = guard.sentinel

    with pytest.raises(InternalRegistrationError) as excinfo:
        guard.assert_allowed(Tagged, context="bind")

    msg = str(excinfo.value)

    # Pin useful diagnostics (type/module/context) without overfitting exact wording.
    assert "Registration blocked" in msg
    assert "type=" in msg
    assert "module=" in msg or "module" in msg
    assert "context='bind'" in msg or "context" in msg
