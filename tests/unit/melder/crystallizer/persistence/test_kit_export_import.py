"""
Unit tests for the profile-scoped checkpoint cache (owner ruling: the
cache IS the transport - profile folders under __crystallizer_cache__,
FIFO file retention without a DB emitter, and reload_profile_from_cache
as the "import a world" verb). Supersedes the removed kit layer.

RE-HOMED (S-test, decomposition epic): the cache lanes moved from
PersistenceSystem to AssetManagementSystem in S3 - these tests now drive
the asset system over a borrowed record instead of the old ledger verbs.

Runs only on 3.14t (melder package root import chain).
"""
import pytest

from melder.crystallizer.asset_management.asset_management_system import (
    AssetManagementSystem,
)
from melder.crystallizer.asset_management.crystallizer_cache import (
    CrystallizerCache,
)
from melder.crystallizer.persistence.persistence_system import (
    PersistenceSystem,
)
from melder.crystallizer.crystals.recorded_unit_state import (
    RecordedUnitState,
)


@pytest.fixture()
def cache_root(tmp_path, monkeypatch):
    """
    Route the crystallizer cache into a per-test directory.

    Returns:
        Path: The isolated cache root.
    """
    from melder.crystallizer.asset_management import crystallizer_cache

    root = tmp_path / "__melder_cache__" / "__crystallizer_cache__"
    monkeypatch.setattr(
        crystallizer_cache.CrystallizerCache,
        "resolve_cache_root_path",
        staticmethod(lambda: root),
    )
    return root


def _world_with_journal_driver():
    """
    Build one record + asset system pair plus a cheap journal driver.

    Returns:
        tuple: (system, assets, emit) where emit() journals exactly one
        entry into the active profile (a nexus state flip needs no twin
        construction).
    """
    system = PersistenceSystem()
    assets = AssetManagementSystem(system)

    def emit() -> None:
        system.record_nexus_state(RecordedUnitState.enabled)

    return system, assets, emit


def _teardown(assets, system) -> None:
    """
    Clean borrower-before-owner (asset system first, then the record).
    """
    assets.cleanup()
    system.cleanup()


def _cached_ids_for_profile(profile_name):
    """
    Probe the on-disk cache through a fresh public cache surface.
    """
    probe = CrystallizerCache()
    try:
        return probe.list_cached_item_ids_for_profile(profile_name)
    finally:
        probe.cleanup()


def test_flush_stores_checkpoints_under_their_profile_folder(cache_root):
    """
    Contract: cached checkpoints land at
    __crystallizer_cache__/{profile}/{checkpoint_id}.json - a profile
    name with checkpoints under it, nothing else.
    """
    system, assets, emit = _world_with_journal_driver()
    emit()
    checkpoint_id = system.create_checkpoint()
    assets.flush_checkpoint(checkpoint_id)
    expected = cache_root / "default" / "{0}.json".format(checkpoint_id)
    assert expected.is_file()
    assert _cached_ids_for_profile("default") == [checkpoint_id]
    _teardown(assets, system)


def test_cache_files_follow_the_checkpoint_limit(cache_root):
    """
    Contract: without a DB emitter the cache follows the checkpoint
    limit - flushing past max_persistence_crystals FIFO-deletes the
    oldest cached files (durability beyond the cap is the user's DB
    opt-in). The asset system reads the record's LIVE cap per flush.
    """
    system, assets, emit = _world_with_journal_driver()
    system.set_checkpoint_retention(2)
    flushed_ids = []
    for _round in range(3):
        emit()
        checkpoint_id = system.create_checkpoint()
        assets.flush_checkpoint(checkpoint_id)
        flushed_ids.append(checkpoint_id)
    cached = _cached_ids_for_profile("default")
    assert len(cached) == 2
    assert flushed_ids[0] not in cached
    assert flushed_ids[1] in cached and flushed_ids[2] in cached
    _teardown(assets, system)


def test_cache_retention_orders_by_checkpoint_number_not_ulid_name(cache_root):
    """
    Regression (owner-run flake, 2026-07-12): two checkpoints sealed
    within one millisecond share a ULID time component and order by
    their RANDOM tails, so filename order can invert true creation
    order and retention would evict the NEWER file. Retention must
    order by the recorded `checkpoint_number` (monotonic per profile);
    the filename only breaks ties. Reproduced deterministically here
    with an inverted name/number pair.
    """
    import json as _json

    profile_directory = cache_root / "default"
    profile_directory.mkdir(parents=True)
    # OLDER by number, but LARGER by name (the same-ms tail inversion).
    older_name = "01AAAAAAAAAAAAAAAAAAAAAAAB"
    newer_name = "01AAAAAAAAAAAAAAAAAAAAAAAA"
    (profile_directory / f"{older_name}.json").write_text(
        _json.dumps({"checkpoint_id": older_name, "checkpoint_number": 1}),
        encoding="utf-8",
    )
    (profile_directory / f"{newer_name}.json").write_text(
        _json.dumps({"checkpoint_id": newer_name, "checkpoint_number": 2}),
        encoding="utf-8",
    )

    probe = CrystallizerCache()
    try:
        removed = probe.enforce_cache_retention("default", 1)
    finally:
        probe.cleanup()

    assert removed == [older_name]
    assert _cached_ids_for_profile("default") == [newer_name]


def test_cache_retention_reclaims_unreadable_files_first(cache_root):
    """
    Contract: a cache file that cannot rehydrate (unreadable JSON) is
    dead weight - retention reclaims it before any numbered checkpoint.
    """
    import json as _json

    profile_directory = cache_root / "default"
    profile_directory.mkdir(parents=True)
    (profile_directory / "01ZZZZZZZZZZZZZZZZZZZZZZZZ.json").write_text(
        "{not json", encoding="utf-8",
    )
    (profile_directory / "01AAAAAAAAAAAAAAAAAAAAAAAA.json").write_text(
        _json.dumps({"checkpoint_number": 1}), encoding="utf-8",
    )
    (profile_directory / "01AAAAAAAAAAAAAAAAAAAAAAAB.json").write_text(
        _json.dumps({"checkpoint_number": 2}), encoding="utf-8",
    )

    probe = CrystallizerCache()
    try:
        removed = probe.enforce_cache_retention("default", 2)
    finally:
        probe.cleanup()

    assert removed == ["01ZZZZZZZZZZZZZZZZZZZZZZZZ"]


def test_reload_profile_from_cache_imports_a_world_idempotently(cache_root):
    """
    Contract: copying a profile folder + reload_profile_from_cache IS the
    import lane - every cached checkpoint inserts through the record's
    sink, re-running skips all, and the reloaded chain verifies intact.
    """
    source, source_assets, emit = _world_with_journal_driver()
    for _round in range(2):
        emit()
        source.create_checkpoint()
    source_assets.flush_checkpoint()
    _teardown(source_assets, source)

    target = PersistenceSystem()
    target_assets = AssetManagementSystem(target)
    first = target_assets.reload_profile_from_cache("default")
    assert first["profile_name"] == "default"
    assert len(first["inserted"]) == 2
    assert first["skipped_existing"] == []
    second = target_assets.reload_profile_from_cache("default")
    assert second["inserted"] == []
    assert len(second["skipped_existing"]) == 2
    report = target.verify_checkpoint_chain()
    assert report["verdict"] == "intact"
    assert report["ledger_count"] == 2
    _teardown(target_assets, target)


def test_reload_profile_refuses_an_unknown_profile_loudly(cache_root):
    """
    Contract: a profile with no cached checkpoints raises an expressive
    KeyError instead of silently importing nothing.
    """
    system, assets, _emit = _world_with_journal_driver()
    with pytest.raises(KeyError, match="No cached checkpoints"):
        assets.reload_profile_from_cache("ghost_profile")
    _teardown(assets, system)
