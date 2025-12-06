import pytest
from melder.utilities.data_structures.weak_data_structures.weak_concurrent_set import WeakConcurrentSet


def test_weak_concurrent_set_add_contains_and_len():
    s = WeakConcurrentSet()
    s.add("x")
    assert "x" in s
    assert len(s) == 1


def test_weak_concurrent_set_cleanup_blocks_use():
    s = WeakConcurrentSet()
    s.add("y")
    s.cleanup()
    with pytest.raises(RuntimeError):
        s.add("z")


def test_weak_concurrent_set_remove_and_to_set():
    s = WeakConcurrentSet()
    s.add("a")
    s.add("b")
    s.remove("a")
    assert "a" not in s
    assert set(s.to_set()) == {"b"}
