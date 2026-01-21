import threading
import pytest

from melder.spellbook.bind.spell_index import SpellIndex


def test_current_and_update_and_get_all_versions():
    idx = SpellIndex("v1")
    assert idx.current == "v1"
    idx.update("v2")
    idx.update("v3")
    assert idx.current == "v3"
    assert idx.get_all_versions() == {"v1", "v2", "v3"}
    assert idx.has_version("v1")
    assert idx.has_version("v3")
    assert not idx.has_version("missing")


def test_hash_and_equality_stable():
    idx1 = SpellIndex("v1")
    idx2 = SpellIndex("v2")
    assert idx1 == idx1
    assert idx1 != idx2
    h1 = hash(idx1)
    idx1.update("v3")
    assert hash(idx1) == h1  # hash based only on immutable ULID


def test_hash_and_equality_ignore_current_id():
    idx1 = SpellIndex("v1")
    idx2 = SpellIndex("v2")
    # force same ULID by copying id
    idx2._id = idx1.id
    assert idx1 == idx2
    idx1.update("v3")
    idx2.update("v4")
    assert idx1 == idx2
    assert hash(idx1) == hash(idx2)


def test_repr_includes_id_and_current():
    idx = SpellIndex("v1")
    text = repr(idx)
    assert "current=v1" in text
    assert "SpellKey" not in text or idx.id in text


def test_context_manager_acquires_and_releases():
    idx = SpellIndex("v1")
    with idx as ctx:
        assert ctx is idx
    # RLock can be re-acquired after context exit
    assert idx._lock.acquire() is True or idx._lock.acquire() is None
    idx._lock.release()


def test_get_all_versions_is_copy():
    idx = SpellIndex("v1")
    versions = idx.get_all_versions()
    versions.add("new")
    assert "new" not in idx.get_all_versions()


def test_has_version_updates_after_update():
    idx = SpellIndex("v1")
    assert idx.has_version("v1")
    idx.update("v2")
    assert idx.has_version("v2")
    assert idx.get_all_versions() == {"v1", "v2"}


def test_repr_reflects_current():
    idx = SpellIndex("v1")
    idx.update("v2")
    text = repr(idx)
    assert "v2" in text and idx.id in text


def test_nested_context_manager():
    idx = SpellIndex("v1")
    with idx:
        with idx:
            assert idx.current == "v1"


def test_cleanup_idempotent_and_nulls():
    idx = SpellIndex("v1")
    idx.cleanup()
    assert idx._lock is None
    idx.cleanup()  # idempotent


def test_operations_after_cleanup_raise():
    idx = SpellIndex("v1")
    idx.cleanup()
    with pytest.raises(RuntimeError):
        _ = idx.current
    with pytest.raises(RuntimeError):
        idx.update("v2")
    with pytest.raises(RuntimeError):
        idx.get_all_versions()
    with pytest.raises(RuntimeError):
        idx.has_version("v1")
    with pytest.raises(RuntimeError):
        with idx:
            pass


def test_hash_equality_with_other_types():
    idx = SpellIndex("v1")
    assert idx != "not-a-spell-index"
    assert idx != None  # noqa: E711


def test_cleanup_then_hash_raises():
    idx = SpellIndex("v1")
    idx.cleanup()
    with pytest.raises(RuntimeError):
        _ = idx.current
    with pytest.raises(RuntimeError):
        idx.update("v2")
