"""
Unit contract tests for the CrystallizerCache placeholder: the pinned cache
root location and the honest NotImplementedError depth limits.
"""
import pytest

from melder.crystallizer.persistence.crystallizer_cache import CrystallizerCache


def test_cache_root_resolves_under_the_melder_cache_umbrella():
    """
    Purpose:
        Verify the pinned cache-root location contract.
    Contract:
        resolve_cache_root_path() ends with
        __melder_cache__/__crystallizer_cache__ (the restructured root).
    Returns:
        None.
    Raises:
        AssertionError: If the cache root moves.
    """
    root = CrystallizerCache.resolve_cache_root_path()
    assert root.name == "__crystallizer_cache__"
    assert root.parent.name == "__melder_cache__"


def test_storage_verbs_are_honest_placeholders():
    """
    Purpose:
        Verify the depth limits until the persistence epic lands.
    Contract:
        store/load/list raise NotImplementedError (never silent no-ops).
    Returns:
        None.
    Raises:
        AssertionError: If a placeholder pretends to work.
    """
    cache = CrystallizerCache()
    with pytest.raises(NotImplementedError):
        cache.store_cached_item("01ULID", {"checkpoint_id": "01ULID"})
    with pytest.raises(NotImplementedError):
        cache.load_cached_item("01ULID")
    with pytest.raises(NotImplementedError):
        cache.list_cached_item_ids()


def test_cache_cleanup_is_idempotent_and_terminal():
    """
    Purpose:
        Verify Cleanable discipline on the cache side item.
    Contract:
        cleanup() twice is safe; verbs afterwards raise RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If post-cleanup use is allowed.
    """
    cache = CrystallizerCache()
    cache.cleanup()
    cache.cleanup()
    with pytest.raises(RuntimeError):
        cache.list_cached_item_ids()
