"""Disposal configuration survives real twin/profile/checkpoint serialization and sealed reload."""

import json
from typing import ClassVar, Optional

import pytest

import melder.aether.spellbook.configuration.spellbook_configuration as configuration_module
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.crystallizer.crystals.spellbook_crystal import SpellbookCrystal
from melder.crystallizer.persistence.persistence_crystal import PersistenceCrystal
from melder.crystallizer.persistence.persistence_profile import PersistenceProfile


class RecordingCrystallizerBoundary:
    """Replace only the global recorder lookup while real emitted twins enter a real profile."""

    _initialized: ClassVar[bool] = True
    activated: ClassVar[bool] = True

    def __init__(self) -> None:
        """Own one isolated persistence profile and its emitted twins; perform no external I/O."""
        self.profile = PersistenceProfile("disposal-transport")
        self.emission_count = 0
        self._cleaned = False

    def cleanup(self) -> None:
        """Idempotently dispose the profile/twins and drop owned references after value capture."""
        if self._cleaned:
            return
        self._cleaned = True
        self.profile.cleanup()
        del self.profile
        del self.emission_count

    def __call__(self) -> RecordingCrystallizerBoundary:
        """Provide the configuration emitter's existing no-argument singleton lookup contract."""
        return self

    def emit(self, twin: SpellbookCrystal) -> None:
        """Record the actual emitted book twin through the profile's typed dispatch."""
        self.profile.record(twin)
        self.emission_count += 1


@pytest.mark.parametrize("priority", [None, False, True])
@pytest.mark.parametrize("prefinalized", [False, True])
def test_disposal_configuration_survives_checkpoint_reload(
        monkeypatch: pytest.MonkeyPatch,
        priority: Optional[bool],
        prefinalized: bool,
) -> None:
    """First/re-freeze emissions round-trip both priorities, list order, and legacy default accounting."""
    recorder = RecordingCrystallizerBoundary()
    monkeypatch.setattr(configuration_module, "Crystallizer", recorder)
    configuration = SpellbookConfiguration("transport-frame")
    restored = SpellbookConfiguration("transport-frame")
    checkpoint = None
    reloaded_checkpoint = None
    try:
        configuration.with_disposal_method_names(["shutdown", "flush", "close"])
        if priority is not None:
            configuration.with_enforce_priority_disposal_methods(priority)
        configuration.with_defaults()
        if prefinalized:
            configuration.freeze()
            assert recorder.emission_count == 0
        configuration.freeze(
            origin_spellbook_id="recorded-book",
            origin_frame_name="transport-frame",
            origin_dynamic=True,
        )
        assert recorder.emission_count == 1
        payloads, journal, sequence_range = recorder.profile.capture_segment_since(0)
        emitted = payloads["spellbook"]["recorded-book"]["configuration_payload"]
        assert emitted["disposal_method_names"] == ["shutdown", "flush", "close"]
        assert emitted["enforce_priority_disposal_methods"] is (priority is True)
        if priority is None:
            # Model an older recorded payload, not a private live-configuration mutation.
            del emitted["enforce_priority_disposal_methods"]
        checkpoint = PersistenceCrystal(
            checkpoint_id="transport-checkpoint",
            profile_name="disposal-transport",
            checkpoint_number=1,
            description="ordered disposal configuration",
            journal_segment=journal,
            captured_payloads=payloads,
            sequence_range=sequence_range,
        )
        cached_item = json.loads(json.dumps(checkpoint.to_cached_item(), sort_keys=True))
        checkpoint.cleanup()
        recorder.cleanup()
        reloaded_checkpoint = PersistenceCrystal.from_cached_item(cached_item)
        recorded = reloaded_checkpoint.replay_data()["payloads"]["spellbook"]["recorded-book"]["configuration_payload"]
        outcome = restored.load_recorded_dictionary(recorded)
        assert outcome["rejected"] == []
        assert outcome["backfilled"] == (["enforce_priority_disposal_methods"] if priority is None else [])
        assert restored.get_property("enforce_priority_disposal_methods") is (priority is True)
        assert restored.get_property("disposal_method_names") == ["shutdown", "flush", "close"]
        with pytest.raises(RuntimeError, match="frozen"):
            restored.with_enforce_priority_disposal_methods()
    finally:
        if checkpoint is not None:
            checkpoint.cleanup()
        if reloaded_checkpoint is not None:
            reloaded_checkpoint.cleanup()
        recorder.cleanup()
        configuration.cleanup()
        restored.cleanup()
