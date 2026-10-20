"""
Unit tests - SpellIndex membership reads racing the index's cleanup (0.2.8230).

`SpellIndex.cleanup()` marks the index cleaned and deletes its member set under the index lock. These tests
pin the two reads that can meet that cleanup from another thread: `has_spell` repeats its cleaned check
under the lock, so a cleanup landing between its first check and its acquire raises the documented
RuntimeError instead of AttributeError; and `_has_spell_unless_cleaned`, the probe used by walks over
indexes the caller does not own, answers the lineage while the index is live and False once it is cleaned.
"""

import threading
from typing import Any

import pytest

from melder.aether.spellbook.bind.spell_index import SpellIndex


def test_has_spell_racing_cleanup_raises_the_documented_runtime_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Purpose:
        Pin the cleaned re-check `has_spell` makes under the index lock.
    Contract:
        A cleanup that lands after the caller's unlocked cleaned check and before it takes the index lock
        makes `has_spell` raise RuntimeError ("already been cleaned"), never AttributeError for the deleted
        member set.
    Raises:
        AssertionError: If the racing call returns, hangs, or raises anything but RuntimeError.
    """
    index = SpellIndex("v1")
    first_check_done = threading.Event()
    original_check = SpellIndex.check_cleaned

    def check_then_signal(self: SpellIndex) -> None:
        """Run the real check, then tell the test the racing caller has passed its first one."""
        original_check(self)
        if self is index and threading.current_thread() is caller and not first_check_done.is_set():
            first_check_done.set()

    monkeypatch.setattr(SpellIndex, "check_cleaned", check_then_signal)
    outcome: dict[str, Any] = {}

    def call_has_spell() -> None:
        """Ask for a member of the live lineage from another thread."""
        try:
            outcome["result"] = index.has_spell("v1")
        except BaseException as exc:
            outcome["error"] = exc

    caller = threading.Thread(target=call_has_spell, name="has-spell-caller")
    with index._lock:
        caller.start()
        assert first_check_done.wait(timeout=30), "the caller never reached has_spell"
        # The caller has passed its unlocked check and cannot take the lock this thread holds. Clean the index
        # under it (the lock is reentrant), as the owning Book's cleanup does from its own thread.
        index.cleanup()
    caller.join(timeout=30)

    assert not caller.is_alive()
    assert "result" not in outcome
    assert isinstance(outcome.get("error"), RuntimeError), outcome
    assert "already been cleaned" in str(outcome["error"])


def test_membership_probe_answers_the_whole_lineage_while_live() -> None:
    """
    Purpose:
        Pin the probe's membership semantics on a live index.
    Contract:
        `_has_spell_unless_cleaned` answers as `has_spell` does: every member of the lineage (the selected id
        and the parked ones) is True, any other id is False.
    Raises:
        AssertionError: If the probe disagrees with the lineage.
    """
    index = SpellIndex("v1")
    index.add_member("v2")

    assert index._has_spell_unless_cleaned("v1") is True
    assert index._has_spell_unless_cleaned("v2") is True
    assert index._has_spell_unless_cleaned("v3") is False
    assert index.has_spell("v2") is True


def test_membership_probe_answers_false_once_cleaned() -> None:
    """
    Purpose:
        Pin the probe's answer for an index its owner has cleaned.
    Contract:
        A cleaned index owns nothing: the probe returns False for a former member and does not raise, while
        `has_spell` keeps raising its documented RuntimeError.
    Raises:
        AssertionError: If the probe raises or answers True, or `has_spell` stops raising.
    """
    index = SpellIndex("v1")
    index.cleanup()

    assert index._has_spell_unless_cleaned("v1") is False
    with pytest.raises(RuntimeError, match="already been cleaned"):
        index.has_spell("v1")
