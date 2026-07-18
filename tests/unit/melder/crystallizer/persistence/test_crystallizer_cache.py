"""
Unit + component tests for the LOCAL crystallizer cache: atomic JSON
storage of checkpoint cached-items, the flush / reload verbs, and history
recovery across PersistenceSystem instances (the cache's whole purpose).

All tests redirect the cache root to a pytest tmp_path - the real root
under src/melder/__melder_cache__ is never touched.
"""
import json
import pytest

from melder.crystallizer.crystals.aether_crystal import AetherCrystal
from melder.crystallizer.asset_management.crystallizer_cache import CrystallizerCache
from melder.crystallizer.persistence.persistence_system import PersistenceSystem


@pytest.fixture()
def cache_root(tmp_path, monkeypatch):
    """
    Redirect the cache root to an isolated temporary directory.

    Returns:
        Path: The redirected root.
    """
    root = tmp_path / "__melder_cache__" / "__crystallizer_cache__"
    monkeypatch.setattr(
        CrystallizerCache,
        "resolve_cache_root_path",
        staticmethod(lambda: root),
    )
    return root


def test_store_load_round_trip_and_listing(cache_root):
    """
    Purpose:
        Verify the cache's basic storage contract.
    Contract:
        A stored cached-item loads back EQUAL; ids list sorted; the root
        directory is created on demand.
    Returns:
        None.
    Raises:
        AssertionError: If the round trip loses or reshapes data.
    """
    cache = CrystallizerCache()
    item = {"checkpoint_id": "01B", "sequence_range": [1, 3], "n": 2}
    cache.store_cached_item("01B", item)
    cache.store_cached_item("01A", {"checkpoint_id": "01A"})
    assert cache.load_cached_item("01B") == item
    assert cache.list_cached_item_ids() == ["01A", "01B"]
    assert cache_root.is_dir()


def test_missing_item_raises_teaching_keyerror(cache_root):
    """
    Purpose:
        Verify the miss contract.
    Contract:
        Loading an unflushed id raises KeyError naming the id; an empty
        cache lists [].
    Returns:
        None.
    Raises:
        AssertionError: If misses are silent.
    """
    cache = CrystallizerCache()
    assert cache.list_cached_item_ids() == []
    with pytest.raises(KeyError, match="ghost"):
        cache.load_cached_item("ghost")


def test_restore_overwrites_and_guards(cache_root):
    """
    Purpose:
        Verify overwrite semantics and input guards.
    Contract:
        Re-storing an id replaces its payload (atomically); an empty id
        raises ValueError; a cleaned cache raises RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If overwrite or guard behavior drifts.
    """
    cache = CrystallizerCache()
    cache.store_cached_item("01A", {"v": 1})
    cache.store_cached_item("01A", {"v": 2})
    assert cache.load_cached_item("01A") == {"v": 2}
    with pytest.raises(ValueError, match="non-empty"):
        cache.store_cached_item("", {})
    cache.cleanup()
    with pytest.raises(RuntimeError):
        cache.list_cached_item_ids()


def test_flush_and_reload_recover_history_across_systems(cache_root):
    """
    Purpose:
        Verify the cache's actual job: checkpoint history survives the
        process.
    Contract:
        System A seals + flushes; a FRESH System B (empty ledger) reloads
        the id from cache and describes the identical checkpoint;
        reloading an id already in the ledger keeps the live crystal
        (insert-if-absent).
    Returns:
        None.
    Raises:
        AssertionError: If history fails to survive the instance boundary.
    """
    # RE-HOMED (S-test): the cache lanes live on AssetManagementSystem
    # over a borrowed record since S3.
    from melder.crystallizer.asset_management.asset_management_system import (
        AssetManagementSystem,
    )

    system_a = PersistenceSystem()
    assets_a = AssetManagementSystem(system_a)
    system_a.record(AetherCrystal())
    checkpoint_id = system_a.create_checkpoint(description="durable")
    flushed = assets_a.flush_checkpoint(checkpoint_id)
    assert flushed == [checkpoint_id]
    original = system_a.describe_checkpoint(checkpoint_id)

    system_b = PersistenceSystem()
    assets_b = AssetManagementSystem(system_b)
    assert assets_b.list_cached_checkpoint_ids() == [checkpoint_id]
    with pytest.raises(KeyError):
        system_b.describe_checkpoint(checkpoint_id)
    reloaded = assets_b.reload_checkpoint_from_cache(checkpoint_id)
    assert reloaded == original
    assert system_b.describe_checkpoint(checkpoint_id) == original
    # Insert-if-absent: a second reload returns the LIVE crystal untouched.
    assert assets_b.reload_checkpoint_from_cache(checkpoint_id) == original
    assets_b.cleanup()
    assets_a.cleanup()


def test_flush_all_ships_the_whole_ledger(cache_root):
    """
    Purpose:
        Verify the flush-everything convenience.
    Contract:
        flush_checkpoint(None) ships every ledger crystal and returns
        their ids; the cache lists all of them. (RE-HOMED: asset verb.)
    Returns:
        None.
    Raises:
        AssertionError: If any ledger crystal is skipped.
    """
    from melder.crystallizer.asset_management.asset_management_system import (
        AssetManagementSystem,
    )

    system = PersistenceSystem()
    assets = AssetManagementSystem(system)
    first = system.create_checkpoint()
    second = system.create_checkpoint()
    flushed = assets.flush_checkpoint(None)
    assert set(flushed) == {first, second}
    assert set(assets.list_cached_checkpoint_ids()) == {first, second}
    assets.cleanup()


def test_bug160_non_object_json_is_reclaimed_not_crash(cache_root):
    """
    BUG-160 regression: a structurally invalid but parseable JSON file (a
    list, null, or scalar - not an object) must sort as dead weight and be
    reclaimed, never crash retention with AttributeError on `.get()`. One such
    file used to permanently block FIFO cleanup for its profile.
    """
    profile_directory = cache_root / "prof"
    profile_directory.mkdir(parents=True)
    (profile_directory / "01VALID.json").write_text(
        json.dumps({"checkpoint_number": 1, "checkpoint_id": "01VALID"}),
        encoding="utf-8",
    )
    (profile_directory / "BAD.json").write_text("[]", encoding="utf-8")

    cache = CrystallizerCache()
    removed = cache.enforce_cache_retention("prof", 1)

    # The non-object dead weight reclaims first; the valid checkpoint survives.
    assert "BAD" in removed
    remaining = sorted(p.name for p in profile_directory.glob("*.json"))
    assert remaining == ["01VALID.json"]
    cache.cleanup()
