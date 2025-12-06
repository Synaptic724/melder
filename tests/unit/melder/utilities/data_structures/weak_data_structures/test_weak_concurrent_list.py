import gc
import threading
import time
from copy import deepcopy

import pytest

from melder.utilities.data_structures.weak_data_structures.weak_concurrent_list import (
    WeakConcurrentList,
)
from melder.utilities.custom_exceptions.dead_reference_error import DeadReferenceError


class Dummy:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Dummy({self.value})"

    def __eq__(self, other):
        if isinstance(other, Dummy):
            return self.value == other.value
        return False


class NonWeak:
    __slots__ = ("value",)
    def __init__(self, value):
        self.value = value


def _force_gc():
    gc.collect()
    time.sleep(0.01)
    gc.collect()


def _new_dummy(val, keep: list) -> Dummy:
    obj = Dummy(val)
    keep.append(obj)
    return obj


def test_init_and_len_and_iter():
    keep = []
    lst = WeakConcurrentList([_new_dummy(1, keep), _new_dummy(2, keep)])
    assert len(lst) == 2
    assert [item.value for item in lst] == [1, 2]


def test_getitem_and_setitem():
    keep = []
    lst = WeakConcurrentList([_new_dummy(1, keep)])
    assert lst[0].value == 1
    lst[0] = _new_dummy(2, keep)
    assert lst[0].value == 2


def test_append_extend_insert():
    keep = []
    lst = WeakConcurrentList()
    lst.append(_new_dummy(1, keep))
    lst.extend([_new_dummy(2, keep), _new_dummy(3, keep)])
    lst.insert(1, _new_dummy(99, keep))
    assert [x.value for x in lst] == [1, 99, 2, 3]


def test_remove_and_pop():
    keep = []
    one = _new_dummy(1, keep)
    two = _new_dummy(2, keep)
    lst = WeakConcurrentList([one, two])
    lst.remove(one)
    assert len(lst) == 1
    val = lst.pop()
    assert val.value == 2
    assert len(lst) == 0
    with pytest.raises(IndexError):
        lst.pop()
    # reverse in place
    lst.extend([_new_dummy(3, keep), _new_dummy(4, keep)])
    lst.reverse()
    assert [x.value for x in lst] == [4, 3]


def test_contains_checks_deadness():
    keep = []
    obj = _new_dummy(1, keep)
    lst = WeakConcurrentList([obj])
    assert obj in lst
    del obj
    del keep[:]
    _force_gc()
    # ensure we no longer consider the dead value present
    with pytest.raises(DeadReferenceError):
        _ = lst.count(Dummy(1))
    lst.prune()
    assert len(lst) == 0


def test_dead_entries_raise_on_access():
    keep = []
    obj = _new_dummy(1, keep)
    lst = WeakConcurrentList([obj])
    del keep[:]
    del obj
    _force_gc()
    with pytest.raises(DeadReferenceError):
        _ = lst[0]
    with pytest.raises(DeadReferenceError):
        _ = lst.to_list()


def test_auto_prune_on_gc():
    keep = []
    obj = _new_dummy(1, keep)
    lst = WeakConcurrentList([obj], auto_prune=True)
    del keep[:]
    del obj
    _force_gc()
    # len triggers prune when auto_prune True
    assert len(lst) == 0


def test_manual_prune():
    keep = []
    obj = _new_dummy(1, keep)
    lst = WeakConcurrentList([obj], auto_prune=False)
    del keep[:]
    del obj
    _force_gc()
    with pytest.raises(DeadReferenceError):
        _ = lst[0]
    lst.prune()
    assert len(lst) == 0


def test_freeze_prevents_mutation():
    keep = []
    lst = WeakConcurrentList([_new_dummy(1, keep)])
    lst.freeze()
    with pytest.raises(TypeError):
        lst.append(_new_dummy(2, keep))
    lst.unfreeze()
    lst.append(_new_dummy(3, keep))
    assert len(lst) == 2


def test_clear_cleans_all():
    keep = []
    lst = WeakConcurrentList([_new_dummy(1, keep), _new_dummy(2, keep)])
    lst.clear()
    assert len(lst) == 0
    assert list(lst) == []


def test_index_and_count():
    keep = []
    a = _new_dummy(1, keep)
    b = _new_dummy(2, keep)
    lst = WeakConcurrentList([a, b, a])
    assert lst.index(a) == 0
    assert lst.count(a) == 2


def test_to_list_returns_strong_refs():
    keep = []
    lst = WeakConcurrentList([_new_dummy(1, keep), _new_dummy(2, keep)])
    strong = lst.to_list()
    assert [o.value for o in strong] == [1, 2]


def test_map_filter_reduce():
    keep = []
    lst = WeakConcurrentList([_new_dummy(1, keep), _new_dummy(2, keep)])
    mapped = lst.map(lambda v: _new_dummy(v.value + 1, keep))
    assert [o.value for o in mapped.to_list()] == [2, 3]
    filtered = lst.filter(lambda v: v.value == 1)
    assert [o.value for o in filtered.to_list()] == [1]
    total = lst.reduce(lambda acc, v: acc + v.value, 0)
    assert total == 3
    # empty reduce returns initial
    assert WeakConcurrentList().reduce(lambda acc, v: acc, None) is None


def test_reversed_iter():
    keep = []
    lst = WeakConcurrentList([_new_dummy(1, keep), _new_dummy(2, keep)])
    assert [v.value for v in reversed(lst)] == [2, 1]


def test_copy_and_deepcopy():
    keep = []
    lst = WeakConcurrentList([_new_dummy(1, keep)])
    cp = lst.copy()
    assert cp is not lst
    assert cp[0].value == 1
    dcp = deepcopy(lst)
    try:
        val = dcp[0]
        assert val.value == 1
        keep.append(val)
    except DeadReferenceError:
        dcp.prune()


def test_repr_and_str():
    keep = []
    lst = WeakConcurrentList([_new_dummy(1, keep)])
    text = repr(lst)
    assert "WeakConcurrentList" in text
    del keep[:]
    _force_gc()
    lst.auto_prune = True
    txt2 = repr(lst)
    assert ("<dead>" in txt2) or ("[]" in txt2)
    try:
        str(lst)
    except DeadReferenceError:
        lst.prune()
        str(lst)


def test_equality_with_dead_entries_requires_prune():
    keep = []
    lst1 = WeakConcurrentList([_new_dummy(1, keep)])
    lst2 = WeakConcurrentList([_new_dummy(1, keep)])
    assert lst1 == lst2
    del keep[:]
    _force_gc()
    assert lst1 != lst2
    lst1.prune(); lst2.prune()
    assert lst1 == lst2 == WeakConcurrentList()


def test_eq_and_ne():
    keep = []
    lst1 = WeakConcurrentList([_new_dummy(1, keep), _new_dummy(2, keep)])
    lst2 = WeakConcurrentList([_new_dummy(1, keep), _new_dummy(2, keep)])
    assert lst1 == lst2
    assert lst1 != WeakConcurrentList([_new_dummy(3, keep)])


def test_context_manager_locks():
    lst = WeakConcurrentList()
    with lst as locked:
        locked.append(Dummy(1))
        assert locked._lock._is_owned()  # type: ignore[attr-defined]
    assert len(lst) == 1


def test_cleanup_idempotent_and_blocks_use():
    lst = WeakConcurrentList([Dummy(1)])
    lst.cleanup()
    lst.cleanup()
    with pytest.raises(RuntimeError):
        len(lst)


def test_reverse_while_frozen_raises_and_after_prune_ok():
    keep = []
    lst = WeakConcurrentList([_new_dummy(1, keep), _new_dummy(2, keep)])
    lst.freeze()
    with pytest.raises(TypeError):
        lst.reverse()
    lst.unfreeze()
    lst.reverse()
    assert [v.value for v in lst] == [2, 1]


def test_reduce_exception_propagates():
    keep = []
    lst = WeakConcurrentList([_new_dummy(1, keep)])
    with pytest.raises(ZeroDivisionError):
        lst.reduce(lambda acc, v: acc / 0, 0)


def test_deepcopy_cleaned_stays_cleaned():
    lst = WeakConcurrentList([Dummy(1)])
    lst.cleanup()
    with pytest.raises(RuntimeError):
        deepcopy(lst)


# -------------- Concurrency tests -------------- #


def test_concurrent_appends():
    keep = []
    lst = WeakConcurrentList()
    def worker(i):
        lst.append(_new_dummy(i, keep))
    threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
    for t in threads: t.start()
    for t in threads: t.join(timeout=5)
    assert len(lst) == 10


def test_concurrent_remove_and_iter():
    keep = []
    objs = [_new_dummy(i, keep) for i in range(5)]
    lst = WeakConcurrentList(objs)
    errors = []

    def remover():
        try:
            for obj in list(objs):
                lst.remove(obj)
        except Exception as exc:
            errors.append(exc)

    def reader():
        try:
            for _ in range(5):
                list(lst)
        except Exception as exc:
            errors.append(exc)

    t1 = threading.Thread(target=remover)
    t2 = threading.Thread(target=reader)
    t1.start(); t2.start()
    t1.join(timeout=5); t2.join(timeout=5)
    errors = [e for e in errors if not isinstance(e, DeadReferenceError)]
    assert not errors
    lst.prune()
    assert len(lst) == 0


def test_concurrent_prune_with_auto_prune():
    keep = []
    lst = WeakConcurrentList(auto_prune=True)
    for i in range(5):
        lst.append(_new_dummy(i, keep))
    del keep[:]
    _force_gc()

    def reader():
        len(lst)  # may trigger prune

    threads = [threading.Thread(target=reader) for _ in range(3)]
    for t in threads: t.start()
    for t in threads: t.join(timeout=5)
    assert len(lst) == 0


def test_concurrent_freeze_unfreeze_and_append():
    keep = []
    lst = WeakConcurrentList([_new_dummy(1, keep)])
    def freezer():
        for _ in range(5):
            lst.freeze()
            time.sleep(0.005)
            lst.unfreeze()
    def appender():
        for i in range(5):
            try:
                lst.append(_new_dummy(i, keep))
            except TypeError:
                pass
    t1 = threading.Thread(target=freezer)
    t2 = threading.Thread(target=appender)
    t1.start(); t2.start()
    t1.join(timeout=5); t2.join(timeout=5)
    lst.prune()
    assert len(lst) >= 1  # original still present; some appends may succeed


def test_concurrent_copy_and_to_list():
    keep = []
    lst = WeakConcurrentList([_new_dummy(i, keep) for i in range(5)])
    errors = []

    def copier():
        try:
            _ = lst.copy()
            _ = deepcopy(lst)
        except Exception as exc:
            errors.append(exc)

    def writer():
        try:
            for i in range(5, 10):
                lst.append(_new_dummy(i, keep))
        except Exception as exc:
            errors.append(exc)

    t1 = threading.Thread(target=copier)
    t2 = threading.Thread(target=writer)
    t1.start(); t2.start()
    t1.join(timeout=5); t2.join(timeout=5)
    assert not errors
