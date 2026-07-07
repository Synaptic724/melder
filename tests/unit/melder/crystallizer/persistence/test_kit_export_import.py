"""
Unit tests for the profile-scoped checkpoint cache (owner ruling: the
cache IS the transport - profile folders under __crystallizer_cache__,
FIFO file retention without a DB emitter, and reload_profile_from_cache
as the "import a world" verb). Supersedes the removed kit layer.

Runs only on 3.14t (melder package root import chain).
"""
import pytest

from melder.crystallizer.persistence.persistence_system import (
    PersistenceSystem,
)
from melder.crystallizer.persistence.recorded_unit_state import (
    RecordedUnitState,
)


@pytest.fixture()
def cache_root(tmp_path, monkeypatch):
    """
    Route the crystallizer cache into a per-test directory.

    Returns:
        Path: The isolated cache root.
    """
    from melder.crystallizer.persistence import crystallizer_cache

    root = tmp_path / "__melder_cache__" / "__crystallizer_cache__"
    monkeypatch.setattr(
        crystallizer_cache.CrystallizerCache,
        "resolve_cache_root_path",
        staticmethod(lambda: root),
    )
    return root


def _system_with_journal_driver():
    """
    Build one persistence system plus a cheap journal driver.

    Returns:
        tuple: (system, emit) where emit() journals exactly one entry into
        the active profile (a nexus state flip needs no twin construction).
    """
    system = PersistenceSystem()

    def emit() -> None:
        system.record_nexus_state(RecordedUnitState.enabled)

    return system, emit


def test_flush_stores_checkpoints_under_their_profile_folder(cache_root):
    """
    Contract: cached checkpoints land at
    __crystallizer_cache__/{profile}/{checkpoint_id}.json - a profile
    name with checkpoints under it, nothing else.
    """
    system, emit = _system_with_journal_driver()
    emit()
    checkpoint_id = system.create_checkpoint()
    system.flush_checkpoint_to_cache(checkpoint_id)
    expected = cache_root / "default" / "{0}.json".format(checkpoint_id)
    assert expected.is_file()
    assert system._crystallizer_cache.list_cached_item_ids_for_profile(
        "default"
    ) == [checkpoint_id]
    system.cleanup()


def test_cache_files_follow_the_checkpoint_limit(cache_root):
    """
    Contract: without a DB emitter the cache follows the checkpoint
    limit - flushing past max_persistence_crystals FIFO-deletes the
    oldest cached files (durability beyond the cap is the user's DB
    opt-in).
    """
    system, emit = _system_with_journal_driver()
    system.set_checkpoint_retention(2)
    flushed_ids = []
    for _round in range(3):
        emit()
        checkpoint_id = system.create_checkpoint()
        system.flush_checkpoint_to_cache(checkpoint_id)
        flushed_ids.append(checkpoint_id)
    cached = system._crystallizer_cache.list_cached_item_ids_for_profile(
        "default"
    )
    assert len(cached) == 2
    assert flushed_ids[0] not in cached
    assert flushed_ids[1] in cached and flushed_ids[2] in cached
    system.cleanup()


def test_reload_profile_from_cache_imports_a_world_idempotently(cache_root):
    """
    Contract: copying a profile folder + reload_profile_from_cache IS the
    import lane - every cached checkpoint inserts, re-running skips all,
    and the reloaded chain verifies intact.
    """
    source, emit = _system_with_journal_driver()
    for _round in range(2):
        emit()
        source.create_checkpoint()
    source.flush_checkpoint_to_cache()
    source.cleanup()

    target = PersistenceSystem()
    first = target.reload_profile_from_cache("default")
    assert first["profile_name"] == "default"
    assert len(first["inserted"]) == 2
    assert first["skipped_existing"] == []
    second = target.reload_profile_from_cache("default")
    assert second["inserted"] == []
    assert len(second["skipped_existing"]) == 2
    report = target.verify_checkpoint_chain()
    assert report["verdict"] == "intact"
    assert report["ledger_count"] == 2
    target.cleanup()


def test_reload_profile_refuses_an_unknown_profile_loudly(cache_root):
    """
    Contract: a profile with no cached checkpoints raises an expressive
    KeyError instead of silently importing nothing.
    """
    system, _emit = _system_with_journal_driver()
    with pytest.raises(KeyError, match="No cached checkpoints"):
        system.reload_profile_from_cache("ghost_profile")
    system.cleanup()
