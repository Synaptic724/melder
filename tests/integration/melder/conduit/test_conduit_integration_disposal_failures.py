"""Integration: a failing disposal method no longer stops an object's teardown.

Symptom:
    When one of a creation's disposal methods raised during conduit or
    spellspace teardown, `Creations` stopped disposing that object: every
    method declared after the failing one was skipped, so a resource whose
    `close` failed was never released.

Why these are integration tests:
    The disposal list here is the one melder builds at bind time from the
    book's `disposal_method_names`, and teardown is driven by real conduit
    cleanup and real spellspace exit, so the tests prove the public lifecycle
    rather than a hand-built store.

Contract under test:
    Every declared disposal method runs, in the book's declared order, even
    after an earlier one raised; conduit cleanup finishes its teardown and then
    raises the failure as an ExceptionGroup (since 0.2.8203; it used to only log
    it).
"""

from typing import List

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import (
    set_frame_system_state_for_spellbook_configuration,
)


class _Connection:
    """Resource whose `close` fails but whose `release` must still run.

    Contract:
        - `calls` records every disposal method melder invoked, in order.
    """

    def __init__(self) -> None:
        """Create the resource with an empty disposal log."""
        self.calls: List[str] = []

    def close(self) -> None:
        """Record the call, then fail the way a broken transport does.

        Raises:
            ConnectionError: Always.
        """
        self.calls.append("close")
        raise ConnectionError("peer already gone")

    def release(self) -> None:
        """Record the call; this is the step the old code skipped."""
        self.calls.append("release")


@pytest.fixture(autouse=True)
def reset_runtime_singletons() -> None:
    """Give each test a clean Aether singleton, matching the other conduit suites."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _configuration() -> SpellbookConfiguration:
    """Build a dynamic configuration whose book disposes with `close` then `release`.

    Returns:
        SpellbookConfiguration: Configuration ready to construct a Spellbook.
    """
    configuration = SpellbookConfiguration()
    set_frame_system_state_for_spellbook_configuration(configuration, "dynamic")
    configuration.set_property("disposal", True)
    configuration.set_property("disposal_method_names", ["close", "release"])
    configuration.load_default_dictionary()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def _leaves(error: BaseException) -> List[BaseException]:
    """Flatten nested exception groups to their leaf exceptions, in group order.

    Args:
        error: The raised exception or group.

    Returns:
        List[BaseException]: Every leaf exception.
    """
    if isinstance(error, BaseExceptionGroup):
        leaves: List[BaseException] = []
        for inner in error.exceptions:
            leaves.extend(_leaves(inner))
        return leaves
    return [error]


def test_conduit_cleanup_runs_every_disposal_method_after_one_fails() -> None:
    """Conduit teardown releases the connection even though its `close` raised, then reports it."""
    spellbook = Spellbook(configuration=_configuration())
    connection_id = spellbook.bind(
        spell=_Connection, existence=Existence.unique_per_conduit, permissions="create",
    )
    conduit = spellbook.conjure(dynamic=True, name="root")
    connection = conduit.meld(spell_id=connection_id)

    with pytest.raises(ExceptionGroup) as raised:
        conduit.cleanup()

    assert connection.calls == ["close", "release"]
    assert conduit.cleaned is True
    assert [type(leaf.__cause__) for leaf in _leaves(raised.value)] == [ConnectionError]


def test_spellspace_exit_runs_every_disposal_method_and_reports_the_failure() -> None:
    """Managed spellspace exit disposes fully and surfaces the failure as a group."""
    spellbook = Spellbook(configuration=_configuration())
    connection_id = spellbook.bind(
        spell=_Connection, existence=Existence.unique_per_spell_space, permissions="create",
    )
    conduit = spellbook.conjure(dynamic=True, name="root")
    try:
        with pytest.raises(ExceptionGroup) as raised:
            with conduit.enter_spellspace() as space:
                connection = space.meld(spell_id=connection_id)

        assert connection.calls == ["close", "release"]
        (error,) = raised.value.exceptions
        assert isinstance(error.__cause__, ConnectionError)
    finally:
        conduit.cleanup()
