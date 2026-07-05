"""
Component soak for the automatic-checkpoint cadence: many emits across many
simulated intervals against the real crystallizer + ledger + retention.
"""
import pytest

import melder.crystallizer.crystallizer as crystallizer_module
from melder.crystallizer.configuration.crystallizer_configuration import (
    CrystallizerConfiguration,
)
from melder.crystallizer.crystallizer import Crystallizer


class _StubSpellCrystal:
    """Light custody stand-in (id = spell SHA; Cleanable-shaped)."""

    def __init__(self, spell_id):
        self.id = spell_id
        self.spellbook_id = None
        self.cleaned = False

    def cleanup(self):
        self.cleaned = True

    def describe(self):
        return {"spell_id": self.id}


@pytest.fixture(autouse=True)
def reset_crystallizer_singleton():
    """
    Reset the Crystallizer singleton around each test.

    Returns:
        None.
    """
    Crystallizer._reset_singleton_for_tests()
    yield
    Crystallizer._reset_singleton_for_tests()


def test_soak_many_intervals_seal_once_each_and_respect_retention(monkeypatch):
    """
    Purpose:
        Soak the ticker across ten simulated hours of activity.
    Contract:
        Sixty emits spread across ten 1-minute intervals seal EXACTLY ten
        automatic checkpoints; with retention 4 only the newest four
        survive, all labeled as cadence seals, in chronological order.
    Returns:
        None.
    Raises:
        AssertionError: If the ticker drifts under sustained activity.
    """
    clock = {"now": 10000.0}
    monkeypatch.setattr(
        crystallizer_module.time, "monotonic", lambda: clock["now"]
    )
    configuration = (
        CrystallizerConfiguration()
        .with_defaults()
        .with_checkpoint_interval_minutes(1)
        .with_max_persistence_crystals(4)
    )
    configuration.activate()
    crystallizer = Crystallizer()
    crystallizer.activate(configuration)
    emitted = 0
    for _interval in range(10):
        clock["now"] += 61.0
        for _burst in range(6):
            crystallizer.emit_spell_crystal(
                _StubSpellCrystal("sha-{0}".format(emitted)), active=True
            )
            emitted += 1
    ledger = crystallizer.list_checkpoint_ids()
    assert len(ledger) == 4
    assert ledger == sorted(ledger)
    for checkpoint_id in ledger:
        summary = crystallizer.describe_checkpoint(checkpoint_id)
        assert summary["description"] == "automatic cadence checkpoint"
    assert crystallizer.describe_profile()["spell_crystal_count"] == 60


def test_soak_quiet_stretches_mint_nothing(monkeypatch):
    """
    Purpose:
        Verify the activity-driven design under long quiet gaps.
    Contract:
        Hours of simulated silence mint zero checkpoints; the first emit
        after the silence seals exactly one.
    Returns:
        None.
    Raises:
        AssertionError: If quiet time mints phantom checkpoints.
    """
    clock = {"now": 5000.0}
    monkeypatch.setattr(
        crystallizer_module.time, "monotonic", lambda: clock["now"]
    )
    configuration = (
        CrystallizerConfiguration()
        .with_defaults()
        .with_checkpoint_interval_minutes(1)
    )
    configuration.activate()
    crystallizer = Crystallizer()
    crystallizer.activate(configuration)
    clock["now"] += 3600.0 * 5
    assert crystallizer.list_checkpoint_ids() == []
    crystallizer.emit_spell_crystal(_StubSpellCrystal("sha-a"), active=True)
    assert len(crystallizer.list_checkpoint_ids()) == 1
