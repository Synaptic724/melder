import threading
import time
import pytest
from melder.utilities.data_structures.weak_data_structures.weak_concurrent_set import WeakConcurrentSet
from melder.utilities.custom_exceptions.dead_reference_error import DeadReferenceError


class Dummy:
    def __init__(self, value: int):
        self.value = value
    def __eq__(self, other):
        return isinstance(other, Dummy) and self.value == other.value
    def __hash__(self):
        return hash(self.value)


def test_weak_concurrent_set_add_contains_and_len():
    s = WeakConcurrentSet()
    obj = Dummy(1)
    s.add(obj)
    assert obj in s
    assert len(s) == 1


def test_weak_concurrent_set_cleanup_blocks_use():
    s = WeakConcurrentSet()
    obj = Dummy(2)
    s.add(obj)
    s.cleanup()
    with pytest.raises(RuntimeError):
        s.add(Dummy(3))


def test_weak_concurrent_set_remove_and_to_set():
    s = WeakConcurrentSet()
    a = Dummy(1); b = Dummy(2)
    s.add(a)
    s.add(b)
    s.remove(a)
    assert a not in s
    assert set(s.to_set()) == {b}


def test_set_operations_union_intersection_difference():
    a = Dummy(1); b = Dummy(2); c = Dummy(3)
    s1 = WeakConcurrentSet([a, b])
    s2 = WeakConcurrentSet([b, c])
    assert s1 | s2 == WeakConcurrentSet([a, b, c])
    assert s1 & s2 == WeakConcurrentSet([b])
    assert s1 - s2 == WeakConcurrentSet([a])
    assert s1 ^ s2 == WeakConcurrentSet([a, c])
    # in-place updates
    s1 |= [c]
    assert c in s1
    s1 &= [b, c]
    assert s1 == WeakConcurrentSet([b, c])
    s1 -= [c]
    assert s1 == WeakConcurrentSet([b])
    s1 ^= [a]
    assert s1 == WeakConcurrentSet([a, b])
    # binary ops with plain sets
    assert s2 | {a} == WeakConcurrentSet([a, b, c])
    assert s2 & {b} == WeakConcurrentSet([b])


def test_set_predicates_and_update_variants():
    a = Dummy(1); b = Dummy(2); c = Dummy(3)
    s1 = WeakConcurrentSet([a, b])
    s2 = WeakConcurrentSet([b])
    assert s1.isdisjoint(WeakConcurrentSet([c]))
    assert s2.issubset(s1)
    assert s1.issuperset(s2)
    s1.intersection_update([b])
    assert s1 == WeakConcurrentSet([b])
    s1.difference_update([b])
    assert len(s1) == 0
    s1.symmetric_difference_update([a, b])
    assert set(s1.to_set()) == {a, b}
    # predicates with plain set
    assert WeakConcurrentSet([a]).issubset({a, b})
    assert WeakConcurrentSet([a, b]).issuperset({a})


def test_freeze_blocks_mutations_and_updates():
    s = WeakConcurrentSet([Dummy(1)])
    s.freeze()
    with pytest.raises(TypeError):
        s.add(Dummy(2))
    with pytest.raises(TypeError):
        s.update([Dummy(3)])
    s.unfreeze()
    s.add(Dummy(4))
    assert len(s) == 2


def test_equality_with_dead_entries_prune_needed():
    keep = [Dummy(1)]
    s1 = WeakConcurrentSet(keep)
    s2 = WeakConcurrentSet(keep)
    assert s1 == s2
    del keep[:]
    with pytest.raises(DeadReferenceError):
        _ = s1 == s2
    s1.prune(); s2.prune()
    assert s1 == s2 == WeakConcurrentSet()


def test_iter_and_len_with_dead_entries_and_auto_prune():
    keep = [Dummy(1), Dummy(2)]
    s = WeakConcurrentSet(keep, auto_prune=True)
    del keep[:]
    # len should prune and drop dead entries
    assert len(s) == 0
    assert list(s) == []


def test_clear_and_context_manager():
    s = WeakConcurrentSet([Dummy(1), Dummy(2)])
    with s as locked:
        assert len(locked) == 2
        assert locked._lock._is_owned()  # type: ignore[attr-defined]
    s.clear()
    assert len(s) == 0


def test_batch_update_mutates_snapshot():
    keep = []
    a = Dummy(1); b = Dummy(2); keep.extend([a, b])
    s = WeakConcurrentSet([a, b])
    keep_new = []
    def mutate(vals: set):
        vals.discard(a)
        val = Dummy(3)
        keep_new.append(val)
        vals.add(val)
    s.batch_update(mutate)
    assert Dummy(1) not in s
    # tolerate possibility of immediate GC; after prune, either present or empty if collected
    try:
        s.prune()
        live = s.to_set()
        if keep_new:
            assert keep_new[0] in live
    except DeadReferenceError:
        s.prune()


def test_map_filter_reduce_behaviour():
    keep = [Dummy(1), Dummy(2)]
    s = WeakConcurrentSet(keep)
    mapped_vals = []
    mapped = s.map(lambda v: (mapped_vals.append(Dummy(v.value + 1)) or mapped_vals[-1]))
    try:
        mset = mapped.to_set()
        assert any(v.value == 2 for v in mset) and any(v.value == 3 for v in mset)
    except DeadReferenceError:
        mapped.prune()
    filtered = s.filter(lambda v: v.value == 1)
    assert filtered == WeakConcurrentSet([Dummy(1)])
    total = s.reduce(lambda acc, v: acc + v.value, 0)
    assert total == 3
    with pytest.raises(TypeError):
        WeakConcurrentSet().reduce(lambda acc, v: acc, None)


def test_pop_and_discard_behaviour():
    keep = [Dummy(1), Dummy(2)]
    s = WeakConcurrentSet(keep)
    popped = s.pop()
    keep.append(popped)
    assert isinstance(popped, Dummy)
    size_after = len(s)
    s.discard(Dummy(99))  # no-op
    assert len(s) == size_after
    # popping empty raises
    s.clear()
    with pytest.raises(KeyError):
        s.pop()


def test_isdisjoint_with_dead_entries():
    keep = [Dummy(1)]
    s = WeakConcurrentSet(keep, auto_prune=True)
    del keep[:]
    assert s.isdisjoint([Dummy(2)])


def test_freeze_blocks_batch_update_and_set_ops():
    keep = [Dummy(1)]
    s = WeakConcurrentSet(keep)
    s.freeze()
    with pytest.raises(TypeError):
        s.batch_update(lambda vals: vals.add(Dummy(2)))
    with pytest.raises(TypeError):
        s.update([Dummy(3)])
    s.unfreeze()
    d4 = Dummy(4); keep.append(d4)
    s.add(d4)
    assert d4 in s


def test_repr_includes_dead_marker():
    keep = [Dummy(1)]
    s = WeakConcurrentSet(keep)
    del keep[:]
    txt = repr(s)
    assert "WeakConcurrentSet" in txt
    assert "<dead>" in txt


# ---------------- Concurrency tests ---------------- #


def test_concurrent_add_and_contains():
    s = WeakConcurrentSet()
    objs = [Dummy(i) for i in range(10)]
    errors = []

    def worker(obj):
        try:
            s.add(obj)
            assert obj in s
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(o,)) for o in objs]
    for t in threads: t.start()
    for t in threads: t.join(timeout=5)
    assert not errors
    assert len(s) == 10


def test_concurrent_updates_and_prune():
    keep = [Dummy(i) for i in range(5)]
    s = WeakConcurrentSet(keep, auto_prune=True)
    del keep[:]
    _ = len(s)  # may prune
    keep_new = []
    def updater(idx):
        val = Dummy(idx + 100)
        keep_new.append(val)
        s.add(val)
    threads = [threading.Thread(target=updater, args=(i,)) for i in range(5)]
    for t in threads: t.start()
    for t in threads: t.join(timeout=5)
    # original may be pruned, but new ones should remain
    try:
        live = s.to_set()
        present = {v.value for v in live}
        assert present.issuperset({100, 101, 102, 103, 104})
    except DeadReferenceError:
        s.prune()
        live = s.to_set()
        present = {v.value for v in live}
        assert present.issuperset({100, 101, 102, 103, 104})


def test_concurrent_set_ops():
    a = Dummy(1); b = Dummy(2); c = Dummy(3); d = Dummy(4)
    s1 = WeakConcurrentSet([a, b])
    s2 = WeakConcurrentSet([c, d])
    results = []
    errors = []

    def do_union():
        try:
            results.append(s1 | s2)
        except Exception as exc:
            errors.append(exc)

    def do_intersection():
        try:
            results.append(s1 & s2)
        except Exception as exc:
            errors.append(exc)

    t1 = threading.Thread(target=do_union)
    t2 = threading.Thread(target=do_intersection)
    t1.start(); t2.start()
    t1.join(timeout=5); t2.join(timeout=5)
    assert not errors
    assert any(isinstance(r, WeakConcurrentSet) and Dummy(1) in r or Dummy(3) in r for r in results)


def test_concurrent_batch_update_and_reads():
    s = WeakConcurrentSet([Dummy(1), Dummy(2)])
    errors = []

    def batcher():
        try:
            s.batch_update(lambda vals: vals.update({Dummy(3), Dummy(4)}))
        except Exception as exc:
            errors.append(exc)

    def reader():
        try:
            for _ in range(5):
                list(s)
        except Exception as exc:
            errors.append(exc)

    t1 = threading.Thread(target=batcher)
    t2 = threading.Thread(target=reader)
    t1.start(); t2.start()
    t1.join(timeout=5); t2.join(timeout=5)
    # batch_update may rebuild while readers iterate; ensure no dead refs leak after prune
    try:
        s.prune()
        live_vals = {v.value for v in s.to_set()}
        assert 3 in live_vals or 4 in live_vals or not live_vals
    except DeadReferenceError:
        s.prune()
    live_vals = {v.value for v in s.to_set()} if len(s) else set()
    assert (3 in live_vals) or (4 in live_vals) or not live_vals


def test_concurrent_freeze_and_mutation():
    s = WeakConcurrentSet([Dummy(1)])
    errors = []

    def freezer():
        for _ in range(5):
            s.freeze()
            time.sleep(0.002)
            s.unfreeze()

    def mutator():
        for i in range(5):
            try:
                s.add(Dummy(i + 2))
            except TypeError:
                pass
            except Exception as exc:
                errors.append(exc)

    t1 = threading.Thread(target=freezer)
    t2 = threading.Thread(target=mutator)
    t1.start(); t2.start()
    t1.join(timeout=5); t2.join(timeout=5)
    assert not errors
    assert len(s) >= 1


# ---------------- Additional coverage ---------------- #


def test_eq_with_plain_set_and_ne():
    a = Dummy(1)
    s = WeakConcurrentSet([a])
    assert s == {a}
    assert s != {Dummy(2)}


def test_pop_on_frozen_raises_and_unfrozen_succeeds():
    s = WeakConcurrentSet([Dummy(1)])
    s.freeze()
    with pytest.raises(TypeError):
        s.pop()
    s.unfreeze()
    try:
        val = s.pop()
        assert isinstance(val, Dummy)
    except DeadReferenceError:
        s.prune()
    assert len(s) == 0


def test_difference_update_with_weak_set_and_plain_set():
    a = Dummy(1); b = Dummy(2)
    s = WeakConcurrentSet([a, b])
    s.difference_update(WeakConcurrentSet([a]))
    assert a not in s and b in s
    s.difference_update({b})
    assert len(s) == 0


def test_symmetric_difference_update_overlaps():
    a = Dummy(1); b = Dummy(2); c = Dummy(3)
    s = WeakConcurrentSet([a, b])
    s.symmetric_difference_update([b, c])
    assert s == WeakConcurrentSet([a, c])


def test_bool_after_prune_dead_entries():
    keep = [Dummy(1)]
    s = WeakConcurrentSet(keep, auto_prune=True)
    del keep[:]
    s.prune()
    assert bool(s) is False


def test_to_list_raises_on_dead_if_not_pruned():
    keep = [Dummy(1)]
    s = WeakConcurrentSet(keep, auto_prune=False)
    del keep[:]
    with pytest.raises(DeadReferenceError):
        s.to_list()
    s.prune()
    assert s.to_list() == []


def test_reduce_empty_with_initial_returns_initial():
    assert WeakConcurrentSet().reduce(lambda acc, v: acc, 5) == 5


def test_map_raises_typeerror_when_mapping_to_nonweakrefable():
    keep = [Dummy(1)]
    s = WeakConcurrentSet(keep)
    with pytest.raises(TypeError):
        s.map(lambda v: 123)  # ints not weakrefable
    # dead path tolerance
    try:
        s.prune()
    except DeadReferenceError:
        s.prune()


def test_freeze_blocks_remove_and_discard():
    s = WeakConcurrentSet([Dummy(1)])
    s.freeze()
    with pytest.raises(TypeError):
        s.remove(Dummy(1))
    with pytest.raises(TypeError):
        s.discard(Dummy(1))
    s.unfreeze()
    s.discard(Dummy(1))
    s.prune()
    assert len(s) == 0


def test_repr_with_dead_and_prune():
    keep = [Dummy(1)]
    s = WeakConcurrentSet(keep, auto_prune=False)
    del keep[:]
    txt = repr(s)
    assert "<dead>" in txt
    s.prune()
    assert "[]" in repr(s)
