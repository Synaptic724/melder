import pytest
import pytest
from melder.utilities.data_structures.weak_data_structures.weak_concurrent_list import WeakConcurrentList


def test_weak_concurrent_list_append_and_iter_and_len():
    lst = WeakConcurrentList()
    lst.append("a")
    lst.append("b")
    assert list(lst) == ["a", "b"]
    assert len(lst) == 2


def test_weak_concurrent_list_cleanup_blocks_use():
    lst = WeakConcurrentList()
    lst.append("x")
    lst.cleanup()
    with pytest.raises(RuntimeError):
        lst.append("y")


def test_weak_concurrent_list_pop_and_insert_and_prune():
    lst = WeakConcurrentList()
    lst.append("a")
    lst.append("b")
    lst.insert(1, "c")
    assert list(lst) == ["a", "c", "b"]
    assert lst.pop() == "b"
    assert lst.pop(0) == "a"
    assert list(lst) == ["c"]
