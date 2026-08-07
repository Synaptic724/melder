"""Regression: `_attempt_cleanup` invoked only the FIRST disposal method.

Symptom:
    `Creations._attempt_cleanup` iterated `method_names`, but both branches of
    its `try` returned inside the first iteration - `return None` on success and
    `return RuntimeError(...)` on failure. No control path reached the bottom of
    the loop body, so a second iteration was unreachable and the `for` was
    decorative. A creation declaring `disposal_methods=["close", "flush"]` had
    `close` invoked and `flush` silently skipped.

    The skip was invisible at every declaration site: the parameter is plural,
    the `StoredDisposalEntry` alias is `Tuple[object, List[str]]`, and the
    configuration surface accepts a list. Nothing raised, nothing logged, and
    the object still left the registry - so an undisposed resource looked
    exactly like a disposed one.

Contract under test:
    Every declared disposal method is invoked, in DECLARED order, for both
    singleton (`add_creation`) and `many` (`add_many_creations`) entries.

    The failure posture is pinned in its own test rather than assumed: the first
    failing method currently ends disposal for that entry and surfaces one
    error. That is the accepted current behaviour, not a guarantee - if disposal
    later aggregates per-method failures the way
    `_dispose_disposable_registry` already aggregates per-entry ones, the
    failure test is the one to update.
"""

from typing import List

import pytest

from melder.aether.conduit.creations.creations import Creations


class MultiMethodDisposalProbe:
    """Creation double that records the order of its disposal invocations.

    Purpose:
        Prove that every declared disposal method runs, and that they run in
        declaration order rather than definition or alphabetical order.

    Contract:
        - Each disposal method appends its own name to `calls`.
        - `calls` is therefore the exact invocation sequence the store drove.
    """

    def __init__(self) -> None:
        """Create the probe with an empty invocation log."""
        self.calls: List[str] = []

    def close(self) -> None:
        """Record one `close` invocation."""
        self.calls.append("close")

    def flush(self) -> None:
        """Record one `flush` invocation."""
        self.calls.append("flush")

    def release(self) -> None:
        """Record one `release` invocation."""
        self.calls.append("release")


class FailingFirstDisposalProbe:
    """Creation double whose FIRST declared disposal method raises.

    Purpose:
        Pin the current failure posture: disposal of one entry stops at the
        first raising method rather than continuing through the remainder.

    Contract:
        - `close()` records the call and then raises.
        - `flush()` records the call; reaching it would prove the posture
          changed.
    """

    def __init__(self) -> None:
        """Create the probe with an empty invocation log."""
        self.calls: List[str] = []

    def close(self) -> None:
        """Record one `close` invocation, then fail."""
        self.calls.append("close")
        raise RuntimeError("close failed")

    def flush(self) -> None:
        """Record one `flush` invocation."""
        self.calls.append("flush")


def _build_store() -> Creations:
    """Return one empty scoped creations store for a single test.

    Returns:
        Creations: A fresh store bound to fixed test-only scope identifiers.
    """
    return Creations(
        owner_conduit_id="conduit-under-test",
        id="scope-under-test",
    )


def test_every_declared_disposal_method_is_invoked() -> None:
    """Three declared methods must all run; the broken code ran only the first.

    Contract assertions:
        - All three declared methods are invoked.
        - They are invoked exactly once each.
    """
    probe = MultiMethodDisposalProbe()
    store = _build_store()
    store.add_creation(
        "spell-all-methods",
        probe,
        has_disposal_methods=True,
        disposal_methods=["close", "flush", "release"],
    )

    store.cleanup()

    assert probe.calls == ["close", "flush", "release"], (
        "expected every declared disposal method to run in order; "
        f"got {probe.calls}"
    )


def test_disposal_follows_declared_order_not_definition_order() -> None:
    """Declaration order drives invocation, not the order methods are defined.

    The probe defines `close`, `flush`, `release` in that order; this test
    declares them reversed, so a pass proves the store replays the declared
    sequence rather than the class body.
    """
    probe = MultiMethodDisposalProbe()
    store = _build_store()
    store.add_creation(
        "spell-declared-order",
        probe,
        has_disposal_methods=True,
        disposal_methods=["release", "close", "flush"],
    )

    store.cleanup()

    assert probe.calls == ["release", "close", "flush"], (
        f"expected declared order to be preserved; got {probe.calls}"
    )


def test_many_bucket_entries_each_invoke_every_declared_method() -> None:
    """The `many` lane routes through the same helper and must behave the same.

    Contract assertions:
        - Both bucket members are disposed.
        - Each member runs its full declared method list, not just the first.
    """
    first = MultiMethodDisposalProbe()
    second = MultiMethodDisposalProbe()
    store = _build_store()
    for probe in (first, second):
        store.add_many_creations(
            "spell-many-methods",
            probe,
            has_disposal_methods=True,
            disposal_methods=["close", "flush"],
        )

    store.cleanup()

    assert first.calls == ["close", "flush"], (
        f"first many-bucket member skipped a method; got {first.calls}"
    )
    assert second.calls == ["close", "flush"], (
        f"second many-bucket member skipped a method; got {second.calls}"
    )


def test_first_failing_method_ends_disposal_for_that_entry() -> None:
    """PINS CURRENT POSTURE - not a guarantee.

    Disposal of one entry stops at the first raising method and surfaces one
    error through the aggregated `ExceptionGroup`. If per-method failures are
    later collected the way per-entry failures already are, THIS is the test to
    update - the three above stay valid either way.

    Contract assertions:
        - The failing method ran.
        - The method declared after it did not.
        - Exactly one error reached the caller for this entry.
    """
    probe = FailingFirstDisposalProbe()
    store = _build_store()
    store.add_creation(
        "spell-failing-first",
        probe,
        has_disposal_methods=True,
        disposal_methods=["close", "flush"],
    )

    with pytest.raises(ExceptionGroup) as raised:
        store.cleanup()

    assert probe.calls == ["close"], (
        "expected disposal to stop at the first failing method; "
        f"got {probe.calls}"
    )
    assert len(raised.value.exceptions) == 1, (
        "expected exactly one aggregated disposal error; "
        f"got {len(raised.value.exceptions)}"
    )
