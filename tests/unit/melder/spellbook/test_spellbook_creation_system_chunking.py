from types import SimpleNamespace
from typing import Any, List

import pytest

from melder.aether.spellbook.spellbook_creation_system import SpellbookCreationSystem
from melder.utilities.custom_exceptions.operation_cancelled_error import (
    OperationCancelledError,
)
from melder.utilities.synchronization.cancellation_event_signal import (
    CancellationEventSignal,
)
from melder.utilities.synchronization.phase_scheduler import PhaseScheduler


class _SchedulerConfig:
    """Minimal configuration stub satisfying PhaseScheduler property reads."""

    def __init__(self, workers: int = 3, timeout_ms: int = 2000) -> None:
        """Store the two scheduler-facing property values."""
        self._values = {
            "phase_scheduler_workers_per_spellbook": workers,
            "phase_scheduler_barrier_timeout_milliseconds": timeout_ms,
        }

    def get_property(self, key: str) -> Any:
        """Return one stored property value by key."""
        return self._values[key]


def _spell_stubs(count: int) -> List[SimpleNamespace]:
    """Build ordered spell stubs exposing only `spell_id`."""
    return [SimpleNamespace(spell_id=f"spell-{index}") for index in range(count)]


def test_chunk_spells_even_split_preserves_order():
    spells = _spell_stubs(6)
    chunks = SpellbookCreationSystem._chunk_spells(spells, 3)
    assert [len(chunk) for chunk in chunks] == [2, 2, 2]
    flattened = [spell for chunk in chunks for spell in chunk]
    assert flattened == spells


def test_chunk_spells_distributes_remainder_to_leading_chunks():
    spells = _spell_stubs(7)
    chunks = SpellbookCreationSystem._chunk_spells(spells, 3)
    assert [len(chunk) for chunk in chunks] == [3, 2, 2]
    flattened = [spell for chunk in chunks for spell in chunk]
    assert flattened == spells


def test_chunk_spells_never_returns_empty_chunks():
    spells = _spell_stubs(2)
    chunks = SpellbookCreationSystem._chunk_spells(spells, 5)
    assert [len(chunk) for chunk in chunks] == [1, 1]


def test_run_spell_chunk_executes_in_order():
    executed: List[str] = []
    chunk = tuple(_spell_stubs(3))
    SpellbookCreationSystem._run_spell_chunk(
        lambda spell: executed.append(spell.spell_id),
        chunk,
        None,
        "phase-x",
    )
    assert executed == ["spell-0", "spell-1", "spell-2"]


def test_run_spell_chunk_raises_first_original_exception_and_stops():
    executed: List[str] = []
    err = ValueError("spell-1 exploded")

    def _runner(spell: SimpleNamespace) -> None:
        if spell.spell_id == "spell-1":
            raise err
        executed.append(spell.spell_id)

    with pytest.raises(ValueError) as excinfo:
        SpellbookCreationSystem._run_spell_chunk(
            _runner,
            tuple(_spell_stubs(3)),
            None,
            "phase-x",
        )
    # Original exception, unwrapped; later spells in the chunk never ran.
    assert excinfo.value is err
    assert executed == ["spell-0"]


def test_run_spell_chunk_observes_cancellation_between_spells():
    signal = CancellationEventSignal()
    executed: List[str] = []

    def _runner(spell: SimpleNamespace) -> None:
        executed.append(spell.spell_id)
        signal.cancel()

    with pytest.raises(OperationCancelledError):
        SpellbookCreationSystem._run_spell_chunk(
            _runner,
            tuple(_spell_stubs(3)),
            signal.event,
            "phase-x",
        )
    assert executed == ["spell-0"]


def test_build_chunked_phase_units_shape_and_full_coverage():
    scheduler = PhaseScheduler(
        spellbook=object(),
        configuration=_SchedulerConfig(workers=3),
    )
    try:
        spells = _spell_stubs(7)
        executed: List[str] = []
        units = SpellbookCreationSystem._build_chunked_phase_units(
            scheduler=scheduler,
            phase_name="phase-x",
            spells=spells,
            spell_runner=lambda spell: executed.append(spell.spell_id),
        )
        assert len(units) == 3
        assert [unit.label for unit in units] == [
            "phase-x:chunk0",
            "phase-x:chunk1",
            "phase-x:chunk2",
        ]
        covered = [
            spell_id
            for unit in units
            for spell_id in unit.metadata["spell_ids"]
        ]
        assert covered == [spell.spell_id for spell in spells]
        # Executing the chunk units runs every spell exactly once, in order.
        for unit in units:
            unit.run_synchronously()
        assert executed == [spell.spell_id for spell in spells]
    finally:
        scheduler.cleanup()


def test_build_chunked_phase_units_empty_batch_returns_empty():
    scheduler = PhaseScheduler(
        spellbook=object(),
        configuration=_SchedulerConfig(workers=3),
    )
    try:
        units = SpellbookCreationSystem._build_chunked_phase_units(
            scheduler=scheduler,
            phase_name="phase-x",
            spells=[],
            spell_runner=lambda spell: None,
        )
        assert units == []
    finally:
        scheduler.cleanup()
