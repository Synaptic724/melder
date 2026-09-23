"""Named conduit removal, pooled-id chronology and detached ancestry in sealed records."""

from collections.abc import Iterator

import pytest

from melder.crystallizer.crystals.conduit_crystal import ConduitCrystal
from melder.crystallizer.crystals.spellbook_crystal import SpellbookCrystal
from melder.crystallizer.crystal_loader_system.restore_engine import RestoreEngine
from melder.crystallizer.persistence.persistence_crystal import PersistenceCrystal
from melder.crystallizer.persistence.persistence_profile import PersistenceProfile
from melder.crystallizer.persistence.record_version import RecordVersion


def _configuration() -> dict[str, object]:
    """Return detached value-only ancestry for one named child under an unnamed parent."""
    return {
        "conduit_state": "lesser",
        "root_conduit_id": "root",
        "parent_conduit_id": "support",
        "lineage_ancestors": [
            {"conduit_id": "root", "parent_conduit_id": None, "conduit_name": "owner", "policy_name": "default"},
            {"conduit_id": "support", "parent_conduit_id": "root", "conduit_name": None, "policy_name": "default"},
        ],
    }


def _child(name: str = "request") -> ConduitCrystal:
    """Create the same pooled identity with the current requested name and ancestry."""
    return ConduitCrystal("child", "book", name, "default", True, configuration_payload=_configuration())


@pytest.fixture
def profile() -> Iterator[PersistenceProfile]:
    """Own a recorded Book/root so child retirement can prove that their records survive."""
    record = PersistenceProfile("default")
    record.record(SpellbookCrystal(spellbook_id="book", frame_name="frame"))
    record.record(ConduitCrystal("root", "book", "owner", "default", True))
    try:
        yield record
    finally:
        record.cleanup()


def _seal(profile: PersistenceProfile, mark: int, number: int) -> PersistenceCrystal:
    """Construct an immutable checkpoint from the real profile capture contract."""
    payloads, journal, bounds = profile.capture_segment_since(mark)
    return PersistenceCrystal(
        checkpoint_id=f"checkpoint-{number}", profile_name="default", checkpoint_number=number,
        description=None, journal_segment=journal, captured_payloads=payloads, sequence_range=bounds,
        created_at="2026-09-23T00:00:00Z",
    )


def test_conduit_removal_keeps_shared_book_and_root(profile: PersistenceProfile) -> None:
    """Retiring a named lesser must not use whole-Book eviction as a substitute."""
    child = _child()
    profile.record(child)
    profile.remove_conduit_crystal("child")
    profile.remove_conduit_crystal("child")
    assert child.cleaned
    assert profile.describe()["spellbook_count"] == 1
    assert profile.describe()["conduit_count"] == 1
    payloads, _journal, _bounds = profile.capture_segment_since(0)
    assert payloads["conduit_removed"]["child"] == {"conduit_id": "child", "removed": True}
    assert set(payloads["conduit"]) == {"root"}


@pytest.mark.parametrize("split_windows", [False, True])
@pytest.mark.parametrize("remove_final", [False, True])
def test_same_id_emit_remove_emit_folds_to_final_scope(
    profile: PersistenceProfile, split_windows: bool, remove_final: bool,
) -> None:
    """Pooled reuse must restore only the final retained scope, within or across checkpoint windows."""
    profile.record(_child("A"))
    earlier = _seal(profile, 0, 1)
    mark = earlier.sequence_range[1] if split_windows else 0
    profile.remove_conduit_crystal("child")
    profile.record(_child("B"))
    if remove_final:
        profile.remove_conduit_crystal("child")
    latest = _seal(profile, mark, 2)
    checkpoints = [earlier, latest] if split_windows else [latest]
    engine = RestoreEngine(
        "default", [checkpoint.id for checkpoint in checkpoints],
        [checkpoint.replay_data() for checkpoint in checkpoints],
    )
    try:
        engine._fold_chain()
        if remove_final:
            assert set(engine._conduits) == {"root"}
        else:
            assert engine._conduits["child"]["conduit_name"] == "B"
        assert engine._report.describe()["shortfalls"] == []
        assert earlier.replay_data()["payloads"]["conduit"]["child"]["conduit_name"] == "A"
    finally:
        engine.cleanup()
        earlier.cleanup()
        latest.cleanup()


def test_conduit_twin_recursively_detaches_ancestry() -> None:
    """Caller-owned and returned ancestor rows cannot mutate a held immutable twin."""
    configuration = _configuration()
    twin = ConduitCrystal("child", "book", "request", "default", True, configuration_payload=configuration)
    try:
        configuration["lineage_ancestors"][1]["conduit_id"] = "changed-input"
        exposed = twin.configuration_payload
        exposed["lineage_ancestors"][0]["conduit_id"] = "changed-property"
        described = twin.describe()
        described["configuration_payload"]["lineage_ancestors"].clear()
        assert twin.configuration_payload == _configuration()
    finally:
        twin.cleanup()


@pytest.mark.parametrize("cached_form", [False, True], ids=["replay", "cached-item"])
def test_checkpoint_exports_cannot_mutate_sealed_ancestry(profile: PersistenceProfile, cached_form: bool) -> None:
    """The externally visible checkpoint shape must be detached at every nested value boundary."""
    profile.record(_child())
    checkpoint = _seal(profile, 0, 1)
    try:
        exported = checkpoint.to_cached_item() if cached_form else checkpoint.replay_data()
        payload_key = "captured_payloads" if cached_form else "payloads"
        exported[payload_key]["conduit"]["child"]["configuration_payload"]["lineage_ancestors"].clear()
        assert checkpoint.replay_data()["payloads"]["conduit"]["child"]["configuration_payload"] == _configuration()
    finally:
        checkpoint.cleanup()


def test_imported_cached_item_cannot_mutate_rehydrated_ancestry(profile: PersistenceProfile) -> None:
    """Rehydration owns nested values even when an adapter retains and mutates its source dictionary."""
    profile.record(_child())
    checkpoint = _seal(profile, 0, 1)
    exported = checkpoint.to_cached_item()
    restored = PersistenceCrystal.from_cached_item(exported)
    try:
        exported["captured_payloads"]["conduit"]["child"]["configuration_payload"]["lineage_ancestors"].clear()
        assert restored.replay_data()["payloads"]["conduit"]["child"]["configuration_payload"] == _configuration()
    finally:
        restored.cleanup()
        checkpoint.cleanup()


def test_root_only_reader_refuses_new_hierarchy_record(
    profile: PersistenceProfile, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Major-2 readers must not silently interpret a named child as an additional Book root."""
    profile.record(_child())
    checkpoint = _seal(profile, 0, 1)
    try:
        exported = checkpoint.to_cached_item()
        monkeypatch.setattr(RecordVersion, "CURRENT", "2.0.0")
        with pytest.raises(ValueError, match="upgrade melder"):
            PersistenceCrystal.from_cached_item(exported)
    finally:
        checkpoint.cleanup()
