import pytest
from melder.utilities.data_structures.weak_data_structures.weak_concurrent_dict import WeakConcurrentDict
from melder.utilities.custom_exceptions.dead_reference_error import DeadReferenceError


def test_weak_concurrent_dict_basic_put_get_and_len():
    d = WeakConcurrentDict()
    d.put("k", "v")
    assert d.get("k") == "v"
    assert "k" in d
    assert len(d) == 1
    assert list(d.keys()) == ["k"]
    assert list(d.values()) == ["v"]


def test_weak_concurrent_dict_remove_and_clear():
    d = WeakConcurrentDict()
    d.put("a", "1")
    d.put("b", "2")
    d.remove("a")
    assert d.get("a") is None
    d.clear()
    assert len(d) == 0


def test_weak_concurrent_dict_dead_reference_error_after_cleanup():
    d = WeakConcurrentDict()
    d.put("x", "y")
    d.cleanup()
    with pytest.raises(RuntimeError):
        d.get("x")


def test_weak_concurrent_dict_freeze_unfreeze():
    d = WeakConcurrentDict()
    d.put("a", "b")
    d.freeze()
    with pytest.raises(TypeError):
        d.put("c", "d")
    d.unfreeze()
    d.put("c", "d")
    assert d.get("c") == "d"


def test_weak_concurrent_dict_pop_and_popitem():
    d = WeakConcurrentDict()
    d.put("a", 1)
    d.put("b", 2)
    assert d.pop("a") == 1
    assert "a" not in d
    key, val = d.popitem()
    assert key == "b" and val == 2
    with pytest.raises(KeyError):
        d.popitem()


def test_weak_concurrent_dict_setdefault_update_and_map_filter_reduce():
    d = WeakConcurrentDict()
    assert d.setdefault("a", 1) == 1
    assert d.setdefault("a", 2) == 1
    d.update({"b": 2})
    assert d["b"] == 2

    mapped = d.map(lambda k, v: (k, v + 1))
    assert mapped["a"] == 2
    filtered = d.filter(lambda k, v: v > 1)
    assert "a" in filtered and "b" in filtered
    reduced = d.reduce(lambda acc, kv: acc + kv[1], 0)
    assert reduced == 3


def test_weak_concurrent_dict_context_manager_copy_and_eq():
    d = WeakConcurrentDict()
    d["x"] = 1
    with d as ctx:
        assert ctx["x"] == 1
    copy_d = d.copy()
    assert copy_d == d
    assert repr(d)
