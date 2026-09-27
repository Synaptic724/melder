"""Regression: one failing disposal method stopped the rest of an object's teardown.

Symptom:
    `Creations._attempt_cleanup` returned at the first disposal method that
    raised, so the object's later declared methods never ran: a creation
    declaring `["close", "release"]` whose `close` failed was never released.
    The error it returned was a new `RuntimeError` built from `str(ex)` only,
    so the original exception, its type and its traceback were lost. The same
    error text formatted the object with `str()` inside the exception handler,
    so an object whose `__str__` also raised made the helper itself raise:
    `cleanup()` then recorded that one error and skipped every remaining
    object, and `clear_all()` and `purge()` propagated it mid-loop.

Contract under test (owner decision, 2026-09-27):
    - Every declared disposal method runs, in declared order, even after an
      earlier one raised.
    - Each failing method contributes one `RuntimeError` to the raised
      `ExceptionGroup`, and that error's `__cause__` is the exception the
      method raised.
    - Reporting a failure never depends on the failing object's `__str__`, so
      one badly behaved object cannot strand the rest of the scope.
"""

from types import SimpleNamespace
from typing import Dict, List, Tuple

import pytest

from melder.aether.conduit.creations.creations import Creations
from melder.aether.spellbook.existence.existence import Existence


class _DisposalProbe:
    """Creation double whose disposal methods record calls and may raise.

    Purpose:
        Observe exactly which declared disposal methods the store invoked, in
        which order, and hand the test the exception each failing method raised
        so the reported error's cause can be checked by identity.

    Contract:
        - `close`, `flush` and `release` append their name to `calls`.
        - A method named in `failing` then raises a fresh `ValueError`, which is
          kept in `raised[name]`.
    """

    def __init__(self, failing: Tuple[str, ...] = ()) -> None:
        """Create a probe that fails the named methods.

        Args:
            failing: Names of the disposal methods that must raise.
        """
        self.calls: List[str] = []
        self.raised: Dict[str, ValueError] = {}
        self._failing = failing

    def _run(self, name: str) -> None:
        """Record one invocation and raise when the method is marked failing.

        Args:
            name: Disposal method being invoked.

        Raises:
            ValueError: When `name` is in `failing`.
        """
        self.calls.append(name)
        if name in self._failing:
            error = ValueError(f"{name} failed")
            self.raised[name] = error
            raise error

    def close(self) -> None:
        """Record `close`; raise when marked failing."""
        self._run("close")

    def flush(self) -> None:
        """Record `flush`; raise when marked failing."""
        self._run("flush")

    def release(self) -> None:
        """Record `release`; raise when marked failing."""
        self._run("release")


class _UnprintableProbe(_DisposalProbe):
    """Failing probe whose `__str__` raises, like an object that reads a closed resource."""

    def __str__(self) -> str:
        """Fail the way a half-disposed object's text can fail.

        Raises:
            RuntimeError: Always.
        """
        raise RuntimeError("str() read a closed resource")


def _store() -> Creations:
    """Return one empty scoped store with fixed test identifiers."""
    return Creations(owner_conduit_id="conduit-under-test", id="scope-under-test")


def test_later_methods_still_run_after_one_method_fails() -> None:
    """The methods declared after a failing one must still run."""
    probe = _DisposalProbe(failing=("close",))
    store = _store()
    store.add_creation(
        "spell-a", probe, has_disposal_methods=True, disposal_methods=["close", "flush", "release"],
    )

    with pytest.raises(ExceptionGroup) as raised:
        store.cleanup()

    assert probe.calls == ["close", "flush", "release"]
    assert len(raised.value.exceptions) == 1


def test_each_failing_method_reports_its_own_error_in_declared_order() -> None:
    """Two failing methods give two errors, in the order the methods were declared."""
    probe = _DisposalProbe(failing=("close", "release"))
    store = _store()
    store.add_creation(
        "spell-a", probe, has_disposal_methods=True, disposal_methods=["close", "flush", "release"],
    )

    with pytest.raises(ExceptionGroup) as raised:
        store.cleanup()

    errors = raised.value.exceptions
    assert probe.calls == ["close", "flush", "release"]
    assert len(errors) == 2
    assert all(isinstance(error, RuntimeError) for error in errors)
    assert "'close'" in str(errors[0])
    assert "'release'" in str(errors[1])


def test_disposal_error_keeps_the_raised_exception_as_its_cause() -> None:
    """The reported error must carry the original exception, not only its text."""
    probe = _DisposalProbe(failing=("close",))
    store = _store()
    store.add_creation("spell-a", probe, has_disposal_methods=True, disposal_methods=["close"])

    with pytest.raises(ExceptionGroup) as raised:
        store.cleanup()

    (error,) = raised.value.exceptions
    assert error.__cause__ is probe.raised["close"]


def test_missing_method_is_one_failure_and_the_rest_still_run() -> None:
    """A method the object lacks fails on its own; the methods around it still run."""
    probe = _DisposalProbe()
    store = _store()
    store.add_creation(
        "spell-a", probe, has_disposal_methods=True, disposal_methods=["close", "missing", "release"],
    )

    with pytest.raises(ExceptionGroup) as raised:
        store.cleanup()

    (error,) = raised.value.exceptions
    assert probe.calls == ["close", "release"]
    assert "'missing'" in str(error)
    assert isinstance(error.__cause__, AttributeError)


def test_unprintable_failing_object_does_not_strand_the_rest_of_cleanup() -> None:
    """A failing object whose `__str__` raises must not stop the other objects' disposal.

    The survivor is registered first, so reverse creation order disposes the
    unprintable object before it.
    """
    survivor = _DisposalProbe()
    unprintable = _UnprintableProbe(failing=("close",))
    store = _store()
    store.add_creation("spell-survivor", survivor, has_disposal_methods=True, disposal_methods=["close"])
    store.add_creation("spell-unprintable", unprintable, has_disposal_methods=True, disposal_methods=["close"])

    with pytest.raises(ExceptionGroup) as raised:
        store.cleanup()

    (error,) = raised.value.exceptions
    assert survivor.calls == ["close"]
    assert "str() raised RuntimeError" in str(error)
    assert error.__cause__ is unprintable.raised["close"]


def test_unprintable_failing_object_does_not_stop_clear_all() -> None:
    """The reusable clear reports the failure as a group and still disposes the rest."""
    survivor = _DisposalProbe()
    unprintable = _UnprintableProbe(failing=("close",))
    store = _store()
    store.add_creation("spell-survivor", survivor, has_disposal_methods=True, disposal_methods=["close"])
    store.add_creation("spell-unprintable", unprintable, has_disposal_methods=True, disposal_methods=["close"])

    with pytest.raises(ExceptionGroup) as raised:
        store.clear_all()

    assert len(raised.value.exceptions) == 1
    assert survivor.calls == ["close"]
    assert store.get_creation("spell-survivor") is None
    store.add_creation("spell-survivor", object())
    assert store.get_creation("spell-survivor") is not None


def test_purge_runs_every_method_of_each_many_member_and_reports_every_failure() -> None:
    """Targeted purge of a many bucket disposes every member fully and reports all failures."""
    older = _DisposalProbe(failing=("close",))
    newer = _DisposalProbe(failing=("close", "release"))
    store = _store()
    for probe in (older, newer):
        store.add_many_creations(
            "spell-m", probe, has_disposal_methods=True, disposal_methods=["close", "release"],
        )
    spell = SimpleNamespace(spell_id="spell-m", existence=Existence.many)

    with pytest.raises(ExceptionGroup) as raised:
        store.purge(spell)

    errors = raised.value.exceptions
    assert newer.calls == ["close", "release"]
    assert older.calls == ["close", "release"]
    assert len(errors) == 3
    assert [error.__cause__ for error in errors] == [
        newer.raised["close"], newer.raised["release"], older.raised["close"],
    ]
    assert store.get_creation("spell-m") is None


def test_refused_publication_chains_every_disposal_failure() -> None:
    """A late publication into a cleaned store runs every method and chains all failures."""
    probe = _DisposalProbe(failing=("close", "release"))
    store = _store()
    store.cleanup()

    with pytest.raises(RuntimeError, match="was cleaned while creation 'spell-a'") as raised:
        store.add_creation(
            "spell-a", probe, has_disposal_methods=True, disposal_methods=["close", "release"],
        )

    cause = raised.value.__cause__
    assert probe.calls == ["close", "release"]
    assert isinstance(cause, ExceptionGroup)
    assert [error.__cause__ for error in cause.exceptions] == [
        probe.raised["close"], probe.raised["release"],
    ]
