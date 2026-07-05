"""
Unit contract tests for PersistenceCrystal, the checkpoint snapshot artifact:
plain-data immutability, detached describe surfaces, and the REAL
to_cached_item / from_cached_item round trip the persistence epic rides.
"""
import pytest

from melder.crystallizer.persistence.persistence_crystal import PersistenceCrystal


def _crystal(description="window"):
    """Build one representative sealed-checkpoint artifact."""
    return PersistenceCrystal(
        checkpoint_id="01TESTULID0000000000000000",
        profile_name="default",
        checkpoint_number=3,
        description=description,
        journal_segment=[(4, "spell_crystal", "sha-a"), (5, "spell_removed", "sha-b")],
        captured_payloads={
            "spell_crystal": {"sha-a": {"spell_id": "sha-a"}},
            "spell_removed": {"sha-b": {"spell_id": "sha-b", "removed": True}},
        },
        sequence_range=(4, 5),
    )


def test_identity_and_number_properties():
    """
    Purpose:
        Verify the artifact's identity surface.
    Contract:
        id returns the ULID; checkpoint_number the per-profile ordinal.
    Returns:
        None.
    Raises:
        AssertionError: If identity properties drift.
    """
    crystal = _crystal()
    assert crystal.id == "01TESTULID0000000000000000"
    assert crystal.checkpoint_number == 3


def test_describe_reports_window_and_capture_counts():
    """
    Purpose:
        Verify the metadata summary contract.
    Contract:
        describe() reports profile, number, description, sequence window,
        journal entry count, and per-kind captured counts.
    Returns:
        None.
    Raises:
        AssertionError: If summary fields drift.
    """
    described = _crystal().describe()
    assert described["checkpoint_id"] == "01TESTULID0000000000000000"
    assert described["profile_name"] == "default"
    assert described["checkpoint_number"] == 3
    assert described["description"] == "window"
    assert described["sequence_range"] == [4, 5]
    assert described["journal_entry_count"] == 2
    assert described["captured_counts"] == {
        "spell_crystal": 1, "spell_removed": 1,
    }


def test_describe_output_is_detached():
    """
    Purpose:
        Verify describe() hands out detached data.
    Contract:
        Mutating the returned summary does not affect later describes.
    Returns:
        None.
    Raises:
        AssertionError: If the summary shares internal state.
    """
    crystal = _crystal()
    described = crystal.describe()
    described["sequence_range"].append(99)
    described["captured_counts"]["spell_crystal"] = 42
    fresh = crystal.describe()
    assert fresh["sequence_range"] == [4, 5]
    assert fresh["captured_counts"]["spell_crystal"] == 1


def test_replay_data_exposes_window_and_detaches():
    """
    Purpose:
        Verify the restore engine's read surface.
    Contract:
        replay_data() returns the ordered journal window and per-kind
        payload maps, fully detached (mutation never reaches the crystal),
        and matches the cached-item's segment content.
    Returns:
        None.
    Raises:
        AssertionError: If the replay surface drifts or shares state.
    """
    crystal = _crystal()
    replay = crystal.replay_data()
    assert replay["journal"] == [
        [4, "spell_crystal", "sha-a"], [5, "spell_removed", "sha-b"],
    ]
    assert replay["payloads"]["spell_removed"]["sha-b"] == {
        "spell_id": "sha-b", "removed": True,
    }
    replay["journal"].append([9, "x", "y"])
    replay["payloads"]["spell_crystal"]["sha-a"]["spell_id"] = "mutated"
    fresh = crystal.replay_data()
    assert len(fresh["journal"]) == 2
    assert fresh["payloads"]["spell_crystal"]["sha-a"]["spell_id"] == "sha-a"
    cached = crystal.to_cached_item()
    assert cached["journal_segment"] == fresh["journal"]
    assert cached["captured_payloads"] == fresh["payloads"]


def test_cached_item_round_trip_restores_the_artifact():
    """
    Purpose:
        Verify the cache round trip the persistence layer rides.
    Contract:
        from_cached_item(to_cached_item()) rebuilds an artifact whose
        describe() equals the original's (identity, window, captures).
    Returns:
        None.
    Raises:
        AssertionError: If the round trip loses or reshapes state.
    """
    original = _crystal()
    restored = PersistenceCrystal.from_cached_item(original.to_cached_item())
    assert restored.describe() == original.describe()
    assert restored.id == original.id


def test_cached_item_is_detached_from_the_source_artifact():
    """
    Purpose:
        Verify the exported cached-item is a detached payload.
    Contract:
        Mutating the exported dict does not corrupt a later export.
    Returns:
        None.
    Raises:
        AssertionError: If exports share internal containers.
    """
    crystal = _crystal()
    exported = crystal.to_cached_item()
    exported_second = crystal.to_cached_item()
    assert exported == exported_second
    for value in exported.values():
        if isinstance(value, dict):
            value.clear()
    assert crystal.to_cached_item() == exported_second


def test_wipe_is_cleanup_and_blocks_further_use():
    """
    Purpose:
        Verify wipe semantics (wipe = cleanup per the owner model).
    Contract:
        cleanup() is idempotent; describe/to_cached_item afterwards raise
        RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If a wiped artifact stays readable.
    """
    crystal = _crystal()
    crystal.cleanup()
    crystal.cleanup()
    assert crystal.cleaned is True
    with pytest.raises(RuntimeError):
        crystal.describe()
    with pytest.raises(RuntimeError):
        crystal.to_cached_item()
