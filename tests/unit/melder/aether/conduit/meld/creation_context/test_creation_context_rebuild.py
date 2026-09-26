"""Contract tests for CreationContextRebuild, the rare-path rebuild window (2026-09-26)."""
from threading import Event, RLock, Thread
from types import SimpleNamespace, TracebackType
from typing import Any, Optional, Self

import pytest

from melder.aether.conduit.meld.creation_context.creation_context_rebuild import (
    CreationContextRebuild,
)
from melder.utilities.synchronization.counter_switch import CounterSwitch
from melder.utilities.synchronization.creation_gate import CreationGate


class _FactoryStub:
    """Factory stub that publishes a context the way the real leader does."""

    def __init__(self) -> None:
        self.calls: list[Any] = []

    def get_or_build_for_spell(self, spell: Any) -> Any:
        """Publish a fresh context and open the switch."""
        self.calls.append(spell)
        spell._creation_context = SimpleNamespace(built_for=spell.spell_id)
        spell._creation_context_switch.advance(2 - spell._creation_context_switch.state)
        return spell._creation_context


class _SpellStub:
    """Spell stub carrying the fields the rebuild window reads and writes."""

    def __init__(
            self,
            index_id: str,
            *,
            gate: Optional[CreationGate] = None,
            plan_present: bool = True,
            context: Any = None,
    ) -> None:
        self.spell_id = f"spell-{index_id}"
        self.spell_index = SimpleNamespace(id=index_id)
        self._creation_gate = gate if gate is not None else CreationGate()
        self._creation_context = context
        self._creation_context_failure: Optional[BaseException] = RuntimeError("stale failure")
        self._creation_context_switch = CounterSwitch(state=2 if context is not None else 0)
        self._creation_context_factory = _FactoryStub()
        self.is_existing_creation = False
        self._compiler_artifact = SimpleNamespace(
            _spell_codegen_creation=object() if plan_present else None,
        )
        self.resolution_required = False
        self.resolution_complete = True


class _RecordingLock:
    """RLock stand-in recording the order of acquisitions across gates."""

    def __init__(self, name: str, log: list[str]) -> None:
        self._name = name
        self._log = log
        self._inner = RLock()

    def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
        """Record then acquire."""
        self._log.append(self._name)
        return self._inner.acquire(blocking, timeout)

    def release(self) -> None:
        """Release the inner lock."""
        self._inner.release()

    def __enter__(self) -> Self:
        self._inner.acquire()
        return self

    def __exit__(
            self,
            exc_type: Optional[type[BaseException]],
            exc_value: Optional[BaseException],
            traceback: Optional[TracebackType],
    ) -> None:
        _ = (exc_type, exc_value, traceback)
        self._inner.release()


def test_enter_waits_for_admitted_tickets_then_freezes_and_clears_failure() -> None:
    """Entering drains tickets already admitted, leaves the gate frozen and clears the old failure."""
    spell = _SpellStub("a")
    gate = spell._creation_gate
    gate.admit_ticket()
    entered = Event()
    leave = Event()
    errors: list[BaseException] = []

    def _produce() -> None:
        """Enter and leave the window on one worker thread, as producers do."""
        try:
            with CreationContextRebuild((spell,)):
                entered.set()
                if not leave.wait(timeout=5.0):
                    raise TimeoutError("test did not let the producer leave")
        except BaseException as error:
            errors.append(error)

    producer = Thread(target=_produce, name="producer")
    producer.start()
    try:
        # The admitted ticket keeps the producer draining; the gate is frozen.
        assert not entered.wait(timeout=0.2)
        assert gate.enabled is False
    finally:
        gate.unregister_ticket()
    assert entered.wait(timeout=5.0)
    assert spell._creation_context_failure is None
    assert gate.enabled is False
    leave.set()
    producer.join(timeout=5.0)
    assert not producer.is_alive()
    assert errors == []
    assert gate.enabled is True


def test_exit_publishes_context_from_present_plan_before_reopening() -> None:
    """A successful window publishes the rebuilt context, then reopens the gate."""
    spell = _SpellStub("a")
    with CreationContextRebuild((spell,)):
        assert spell._creation_gate.enabled is False
    assert spell._creation_context_factory.calls == [spell]
    assert spell._creation_context.built_for == "spell-a"
    assert spell._creation_context_switch.state == 2
    assert spell._creation_gate.enabled is True


def test_exit_leaves_spell_without_plan_unpublished_and_resolution_flags_alone() -> None:
    """No plan means no publication; resolution flags are not rewritten by the window."""
    spell = _SpellStub("a", plan_present=False)
    with CreationContextRebuild((spell,)):
        pass
    assert spell._creation_context_factory.calls == []
    assert spell._creation_context is None
    assert spell.resolution_required is False
    assert spell.resolution_complete is True


def test_exit_keeps_context_the_window_did_not_reset() -> None:
    """A spell still holding a context is not rebuilt."""
    existing = object()
    spell = _SpellStub("a", context=existing)
    with CreationContextRebuild((spell,)):
        pass
    assert spell._creation_context is existing
    assert spell._creation_context_factory.calls == []


def test_failure_inside_window_records_cause_resets_switch_and_reopens() -> None:
    """A producer failure is recorded on unpublished spells, the switch idles and the gate reopens."""
    spell = _SpellStub("a")
    spell._creation_context_switch.advance(1)
    error = RuntimeError("phase failed")
    with pytest.raises(RuntimeError, match="phase failed"):
        with CreationContextRebuild((spell,)):
            raise error
    assert spell._creation_context_failure is error
    assert spell._creation_context_switch.state == 0
    assert spell._creation_gate.enabled is True


def test_gate_frozen_before_the_window_stays_frozen_after_it() -> None:
    """The window restores the prior posture: a gate it found disabled is not reopened."""
    gate = CreationGate(enabled=False)
    spell = _SpellStub("a", gate=gate)
    with CreationContextRebuild((spell,)):
        pass
    assert gate.enabled is False


def test_gate_transition_locks_taken_in_index_order_and_released() -> None:
    """Overlapping producers serialize on gate locks taken in stable index-id order."""
    log: list[str] = []
    spell_b = _SpellStub("b")
    spell_a = _SpellStub("a")
    spell_b._creation_gate._lock = _RecordingLock("b", log)
    spell_a._creation_gate._lock = _RecordingLock("a", log)
    with CreationContextRebuild((spell_b, spell_a)):
        pass
    assert log[:2] == ["a", "b"]
    released: list[bool] = []

    def _probe() -> None:
        """Acquire both gate locks from another thread without blocking."""
        for spell in (spell_a, spell_b):
            got = spell._creation_gate._lock.acquire(blocking=False)
            released.append(got)
            if got:
                spell._creation_gate._lock.release()

    worker = Thread(target=_probe)
    worker.start()
    worker.join(timeout=5.0)
    assert released == [True, True]


def test_drain_failure_on_entry_unwinds_and_propagates(monkeypatch: pytest.MonkeyPatch) -> None:
    """A drain failure releases the gate lock, restores posture and raises the original error."""
    spell = _SpellStub("a")
    gate = spell._creation_gate

    def _failing_drain(
            target: CreationGate,
            timeout: float = 30.0,
            interval: float = 0.1,
    ) -> None:
        """Simulate a drain timeout (patched on the class: CreationGate uses slots)."""
        _ = (target, timeout, interval)
        raise RuntimeError("drain timed out")

    monkeypatch.setattr(CreationGate, "close_and_drain", _failing_drain)
    with pytest.raises(RuntimeError, match="drain timed out"):
        with CreationContextRebuild((spell,)):
            pytest.fail("window body must not run")
    assert gate.enabled is True
    acquired: list[bool] = []
    worker = Thread(target=lambda: acquired.append(gate._lock.acquire(blocking=False)))
    worker.start()
    worker.join(timeout=5.0)
    assert acquired == [True]
