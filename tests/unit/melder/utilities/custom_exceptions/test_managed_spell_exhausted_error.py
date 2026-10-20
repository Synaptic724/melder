"""
Unit tests of ManagedSpellExhaustedError (STORY-2026-10-15-managed_quantity_pool, S3).

The error a managed pool raises before anything is built: limited_quantity at its limit, queue at its timeout. It
is a MeldExecutionError, so code that catches resolution failures keeps catching it.
"""
import pytest

from melder.utilities.custom_exceptions.managed_spell_exhausted_error import ManagedSpellExhaustedError
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError


def test_limited_names_the_spell_its_limit_and_the_two_ways_out() -> None:
    """The limited text says every object is out and how to get one back or allow more."""
    error = ManagedSpellExhaustedError.limited(spell_id="sid-1", spell_name="Logger", limit=4)
    assert isinstance(error, MeldExecutionError)
    assert (error.spell_id, error.spell_name, error.mode, error.limit, error.timeout_seconds) == (
        "sid-1", "Logger", "limited_quantity", 4, None,
    )
    assert (
        "Managed spell 'Logger' (limited_quantity, limit 4) has all 4 objects out. Release one with "
        "ReleaseManagedSpell().release(obj) before melding another, or bind it with a higher managed_spell_limit."
    ) in str(error)


def test_queue_names_the_timeout_it_waited() -> None:
    """The queue text names the limit and the timeout, printed without trailing zeros."""
    error = ManagedSpellExhaustedError.queue(spell_id="sid-2", spell_name="Parser", limit=8, timeout_seconds=2.0)
    assert (error.mode, error.limit, error.timeout_seconds) == ("queue", 8, 2.0)
    assert (
        "Managed spell 'Parser' (queue, limit 8) had no object free within 2 s. Release one with "
        "ReleaseManagedSpell().release(obj), or bind it with a higher managed_spell_limit or "
        "managed_spell_timeout_seconds."
    ) in str(error)


def test_queue_keeps_a_fractional_timeout() -> None:
    """A fractional timeout is printed as written."""
    error = ManagedSpellExhaustedError.queue(spell_id="sid", spell_name="P", limit=1, timeout_seconds=0.25)
    assert "within 0.25 s." in str(error)


def test_the_error_is_caught_as_a_meld_failure() -> None:
    """`except MeldExecutionError` catches an exhausted pool."""
    with pytest.raises(MeldExecutionError):
        raise ManagedSpellExhaustedError.limited(spell_id="sid", spell_name="P", limit=1)


def test_the_error_carries_no_inner_cause() -> None:
    """Nothing was called when it is raised: no node, parameter or inner exception."""
    error = ManagedSpellExhaustedError.limited(spell_id="sid", spell_name="P", limit=1)
    assert (error.node_id, error.param_name, error.inner) == (None, None, None)
