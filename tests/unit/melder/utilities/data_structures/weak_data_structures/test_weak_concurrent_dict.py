import gc
import threading
import time
from copy import deepcopy

import pytest

from melder.utilities.data_structures.weak_data_structures.weak_concurrent_dict import (
    WeakConcurrentDict,
)
from melder.utilities.custom_exceptions.dead_reference_error import DeadReferenceError


class Dummy:
    def __init__(self, value):
        self.value = value

    def inc(self):
        self.value += 1
        return self.value

    def __repr__(self):
        return f"Dummy({self.value})"


class NonWeak:
    __slots__ = ("value",)

    def __init__(self, value):
        self.value = value


def _new_dummy(val, keep: list) -> Dummy:
    obj = Dummy(val)
    keep.append(obj)
    return obj


def _force_gc():
    gc.collect()
    time.sleep(0.01)
    gc.collect()


def test_init_from_mapping_and_get_setitem():
    keep = []
    a = _new_dummy(1, keep); b = _new_dummy(2, keep)
    d = WeakConcurrentDict({"a": a, "b": b})
    assert len(d) == 2
    assert d["a"].value == 1
    c = _new_dummy(3, keep)
    d["c"] = c
    assert d["c"].value == 3


def test_init_from_iterable_and_get_set_del():
    keep = []
    x = _new_dummy(10, keep); y = _new_dummy(20, keep)
    items = [("x", x), ("y", y)]
    d = WeakConcurrentDict(items)
    assert d["x"].value == 10
    del d["x"]
    assert "x" not in d
    with pytest.raises(KeyError):
        _ = d["x"]


def test_non_weakrefable_raises_on_init_and_set():
    with pytest.raises(TypeError):
        WeakConcurrentDict({"a": NonWeak(1)})
    d = WeakConcurrentDict()
    with pytest.raises(TypeError):
        d["a"] = NonWeak(1)


def test_get_with_default_and_missing():
    d = WeakConcurrentDict()
    assert d.get("missing") is None
    assert d.get("missing", 5) == 5


def test_pop_and_pop_default():
    keep = []
    a = _new_dummy(1, keep)
    d = WeakConcurrentDict({"a": a})
    assert d.pop("a").value == 1
    assert "a" not in d
    with pytest.raises(KeyError):
        d.pop("a")
    b = _new_dummy(2, keep)
    assert d.pop("a", b).value == 2


def test_popitem_removes_entry():
    keep = []
    a = _new_dummy(1, keep); b = _new_dummy(2, keep)
    d = WeakConcurrentDict({"a": a, "b": b})
    key, val = d.popitem()
    assert key in ("a", "b")
    assert isinstance(val, Dummy)
    assert len(d) == 1
    d.popitem()
    with pytest.raises(KeyError):
        d.popitem()


def test_len_bool_keys_values_items_to_dict():
    keep = []
    a = _new_dummy(1, keep); b = _new_dummy(2, keep)
    d = WeakConcurrentDict({"a": a, "b": b})
    assert bool(d) is True
    keys_view = d.keys()
    assert set(keys_view) == {"a", "b"}
    assert keys_view & {"a"} == {"a"}
    assert keys_view | {"c"} == {"a", "b", "c"}
    assert keys_view - {"b"} == {"a"}
    assert keys_view ^ {"b", "c"} == {"a", "c"}
    values_view = d.values()
    assert sorted([v.value for v in values_view]) == [1, 2]
    items_view = d.items()
    dict_items = dict(items_view)
    assert dict_items["a"].value == 1
    assert d.to_dict()["b"].value == 2
    assert "a" in keys_view
    assert (("a", dict_items["a"]) in items_view)
    assert dict_items["a"] in values_view
    # items view set-like operations
    pair = ("a", dict_items["a"])
    assert items_view & {pair} == {pair}
    assert items_view | {("c", _new_dummy(3, keep))} >= {pair}
    assert items_view - {pair} != items_view
    assert items_view ^ {pair} != set()


def test_clear_removes_all():
    d = WeakConcurrentDict({"a": Dummy(1), "b": Dummy(2)})
    d.clear()
    assert len(d) == 0
    assert list(d.keys()) == []


def test_freeze_prevents_mutation_and_unfreeze_restores():
    keep = []
    a = _new_dummy(1, keep)
    d = WeakConcurrentDict({"a": a})
    d.freeze()
    with pytest.raises(TypeError):
        d["b"] = Dummy(2)
    d.unfreeze()
    b = _new_dummy(2, keep)
    d["b"] = b
    assert "b" in d


def test_auto_prune_removes_dead_on_len_and_gc():
    a = Dummy(1)
    d = WeakConcurrentDict({"a": a}, auto_prune=True)
    del a
    _force_gc()
    # len triggers pruning when auto_prune True
    assert len(d) == 0


def test_manual_prune_removes_dead():
    a = Dummy(1)
    d = WeakConcurrentDict({"a": a}, auto_prune=False)
    del a
    _force_gc()
    # dead still present until prune
    with pytest.raises(DeadReferenceError):
        _ = d["a"]
    d.prune()
    assert "a" not in d


def test_contains_checks_deadness():
    a = Dummy(1)
    d = WeakConcurrentDict({"a": a})
    assert "a" in d
    del a
    _force_gc()
    assert ("a" in d) is False


def test_setdefault_existing_and_missing():
    keep = []
    a = _new_dummy(1, keep)
    d = WeakConcurrentDict({"a": a})
    assert d.setdefault("a", Dummy(2)).value == 1
    b = _new_dummy(3, keep)
    assert d.setdefault("b", b).value == 3
    assert "b" in d
    d2 = WeakConcurrentDict()
    with pytest.raises(TypeError):
        d2.setdefault("x")  # default None is not weakrefable


def test_update_with_mapping_iterable_and_kwargs():
    keep = []
    a = _new_dummy(1, keep)
    d = WeakConcurrentDict({"a": a})
    b = _new_dummy(2, keep); c = _new_dummy(3, keep); dval = _new_dummy(4, keep)
    d.update({"b": b}, c=c)
    d.update([("d", dval)])
    assert set(d.keys()) == {"a", "b", "c", "d"}
    assert d["c"].value == 3


def test_batch_update_rebuilds_from_strong_snapshot():
    keep = []
    a = _new_dummy(1, keep); b = _new_dummy(2, keep)
    d = WeakConcurrentDict({"a": a, "b": b})

    def mutate(values: dict):
        values.pop("a")
        values["c"] = _new_dummy(3, keep)

    d.batch_update(mutate)
    assert set(d.keys()) == {"b", "c"}
    # keep strong ref to new value
    cv = d["c"]; keep.append(cv)
    assert cv.value == 3


def test_map_filter_reduce():
    keep = []
    a = _new_dummy(1, keep); b = _new_dummy(2, keep)
    d = WeakConcurrentDict({"a": a, "b": b})
    mapped_keep = []
    mapped = d.map(lambda k, v: (k.upper(), _new_dummy(v.value + 1, mapped_keep)))
    assert mapped["A"].value == 2
    filtered = d.filter(lambda k, v: v.value == 1)
    assert list(filtered.keys()) == ["a"]
    total = d.reduce(lambda acc, kv: acc + kv[1].value, initial=0)
    assert total == 3
    with pytest.raises(TypeError):
        WeakConcurrentDict().reduce(lambda acc, kv: acc, None)


def test_copy_and_deepcopy():
    keep = []
    a = _new_dummy(1, keep)
    d = WeakConcurrentDict({"a": a})
    c = d.copy()
    assert c is not d
    val_c = c["a"]; keep.append(val_c)
    assert val_c.value == 1
    # keep a strong snapshot of original before deepcopy to avoid GC during copy
    orig = d["a"]; keep.append(orig)
    dd = deepcopy(d)
    try:
        val_dd = dd["a"]; keep.append(val_dd)
        assert val_dd.value == 1
    except DeadReferenceError:
        dd.prune()
        assert len(dd) == 0
    # inplace merge | and |= compatibility
    merged = d | {"b": _new_dummy(2, keep)}
    assert merged["b"].value == 2
    d |= {"c": _new_dummy(3, keep)}
    assert d["c"].value == 3


def test_ror_with_plain_dict_left_operand():
    keep = []
    base = WeakConcurrentDict({"b": _new_dummy(2, keep)})
    merged = {"a": _new_dummy(1, keep)} | base  # __ror__ on WeakConcurrentDict
    assert isinstance(merged, WeakConcurrentDict)
    assert set(merged.keys()) == {"a", "b"}
    # right-hand side wins on conflict
    base_conflict = WeakConcurrentDict({"x": _new_dummy(10, keep)})
    left = {"x": _new_dummy(1, keep)}
    merged_conflict = left | base_conflict
    assert merged_conflict["x"].value == 10


def test_repr_and_str_include_values_and_dead_marker():
    a = Dummy(1)
    d = WeakConcurrentDict({"a": a})
    text = repr(d)
    assert "WeakConcurrentDict" in text
    del a
    _force_gc()
    d.auto_prune = True
    # snapshot should render dead as <dead>
    text2 = repr(d)
    assert ("<dead>" in text2) or text2.endswith("({})")
    # __str__ uses to_dict (may prune dead)
    try:
        str(d)
    except DeadReferenceError:
        # if dead not pruned yet, ensure prune then stringify
        d.prune()
        str(d)

def test_equality_with_dead_entries_requires_prune():
    keep = []
    a = _new_dummy(1, keep)
    d1 = WeakConcurrentDict({"a": a})
    d2 = WeakConcurrentDict({"a": a})
    assert d1 == d2
    del keep[:]
    del a
    _force_gc()
    # before prune, equality should not claim equal (may raise if dead)
    with pytest.raises(DeadReferenceError):
        _ = d1 == d2
    d1.prune(); d2.prune()
    assert d1 == d2 == WeakConcurrentDict()


def test_ror_typeerror_on_non_weakrefable_conflict():
    d = WeakConcurrentDict()
    with pytest.raises(TypeError):
        _ = {"x": 1} | d


def test_freeze_blocks_merge_and_update():
    keep = []
    d = WeakConcurrentDict({"a": _new_dummy(1, keep)})
    d.freeze()
    with pytest.raises(TypeError):
        d |= {"b": _new_dummy(2, keep)}
    with pytest.raises(TypeError):
        d.update({"c": _new_dummy(3, keep)})


def test_deepcopy_cleaned_stays_cleaned():
    d = WeakConcurrentDict({"a": Dummy(1)})
    d.cleanup()
    with pytest.raises(RuntimeError):
        deepcopy(d)


def test_eq_with_dict_and_ne():
    a = Dummy(1)
    d = WeakConcurrentDict({"a": a})
    assert d == {"a": a}
    assert d != {"b": Dummy(2)}


def test_context_manager_acquires_lock_and_releases():
    d = WeakConcurrentDict()
    with d as locked:
        x = Dummy(1)
        locked["x"] = x
        assert locked._lock._is_owned()  # type: ignore[attr-defined]
    assert "x" in d


def test_cleanup_idempotent_and_blocks_further_use():
    d = WeakConcurrentDict({"a": Dummy(1)})
    d.cleanup()
    d.cleanup()
    with pytest.raises(RuntimeError):
        d.check_cleaned()
    with pytest.raises(RuntimeError):
        len(d)


# ---------------- Concurrency tests ---------------- #


def test_concurrent_sets_and_gets():
    d = WeakConcurrentDict()
    keep = []
    def worker(idx):
        obj = Dummy(idx)
        keep.append(obj)
        d[f"k{idx}"] = obj
        assert d[f"k{idx}"].value == idx

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
    for t in threads: t.start()
    for t in threads: t.join(timeout=5)
    assert len(d) == 10


def test_concurrent_updates_same_key_last_wins():
    base = Dummy(0)
    keep = [base]
    d = WeakConcurrentDict({"k": base})
    def worker(val):
        obj = Dummy(val)
        keep.append(obj)
        d["k"] = obj
    threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
    for t in threads: t.start()
    for t in threads: t.join(timeout=5)
    assert d["k"].value in range(5)


def test_concurrent_prune_with_auto_prune():
    d = WeakConcurrentDict(auto_prune=True)
    a = Dummy(1)
    d["a"] = a
    del a
    _force_gc()
    def reader():
        # len may trigger prune
        len(d)
    threads = [threading.Thread(target=reader) for _ in range(3)]
    for t in threads: t.start()
    for t in threads: t.join(timeout=5)
    assert "a" not in d


def test_concurrent_clear_and_set():
    a = Dummy(1)
    d = WeakConcurrentDict({"a": a})
    def clearer():
        d.clear()
    def setter():
        b = Dummy(2)
        d["b"] = b
    t1 = threading.Thread(target=clearer)
    t2 = threading.Thread(target=setter)
    t1.start(); t2.start()
    t1.join(timeout=5); t2.join(timeout=5)
    # after concurrent clear/set, either b survived or dict was cleared
    if "b" in d:
        assert d["b"].value == 2
    else:
        d.prune()
        assert len(d) == 0


def test_concurrent_batch_update():
    keep = []
    a = _new_dummy(1, keep); b = _new_dummy(2, keep)
    d = WeakConcurrentDict({"a": a, "b": b})
    def mutate():
        d.batch_update(lambda strong: strong.update({"c": _new_dummy(3, keep)}))
    threads = [threading.Thread(target=mutate) for _ in range(3)]
    for t in threads: t.start()
    for t in threads: t.join(timeout=5)
    assert "c" in d


def test_fromkeys_basic():
    keys = ["a", "b", "c"]
    val = Dummy(1)
    d = WeakConcurrentDict.fromkeys(keys, val)
    assert set(d.keys()) == set(keys)
    assert all(d[k] is val for k in keys)


def test_fromkeys_auto_prune_propagates():
    d = WeakConcurrentDict.fromkeys(["x"], Dummy(2), auto_prune=True)
    assert d.auto_prune is True


def test_fromkeys_raises_for_non_weakrefable():
    with pytest.raises(TypeError):
        WeakConcurrentDict.fromkeys(["a"], NonWeak(1))


def test_fromkeys_and_reversed():
    keep = []
    val = _new_dummy(9, keep)
    d = WeakConcurrentDict.fromkeys(["x", "y"], val)
    assert list(d) == ["x", "y"]
    assert list(reversed(d)) == ["y", "x"]
    assert d["x"] is val


def test_concurrent_pop_and_reads():
    keep = []
    d = WeakConcurrentDict({f"k{i}": _new_dummy(i, keep) for i in range(5)})
    errors = []

    def popper():
        try:
            for i in range(5):
                d.pop(f"k{i}", None)
        except Exception as exc:
            errors.append(exc)

    def reader():
        try:
            for _ in range(5):
                list(d.keys())
                list(d.values()) if d else None
        except Exception as exc:
            errors.append(exc)

    t1 = threading.Thread(target=popper)
    t2 = threading.Thread(target=reader)
    t1.start(); t2.start()
    t1.join(timeout=5); t2.join(timeout=5)
    assert not errors
    d.prune()
    assert len(d) == 0


def test_concurrent_freeze_unfreeze_and_mutations():
    keep = []
    d = WeakConcurrentDict({"a": _new_dummy(1, keep)})
    errors = []

    def freezer():
        for _ in range(5):
            d.freeze()
            time.sleep(0.005)
            d.unfreeze()

    def mutator():
        for i in range(5):
            try:
                d[f"b{i}"] = _new_dummy(i, keep)
            except TypeError:
                # expected when frozen
                pass

    t1 = threading.Thread(target=freezer)
    t2 = threading.Thread(target=mutator)
    t1.start(); t2.start()
    t1.join(timeout=5); t2.join(timeout=5)
    d.prune()
    # At least original key should remain; some mutations may have succeeded
    assert "a" in d


def test_concurrent_auto_prune_heavy():
    keep = []
    d = WeakConcurrentDict(auto_prune=True)
    # preload some
    for i in range(10):
        d[f"k{i}"] = _new_dummy(i, keep)

    def churn(idx):
        for j in range(5):
            key = f"k{idx}_{j}"
            d[key] = _new_dummy(idx * 10 + j, keep)
            # drop reference immediately to allow GC
            del keep[:]
            _force_gc()
            len(d)

    threads = [threading.Thread(target=churn, args=(i,)) for i in range(5)]
    for t in threads: t.start()
    for t in threads: t.join(timeout=5)
    # Dictionary should remain usable
    len(d)


def test_concurrent_copy_and_to_dict_snapshot_safety():
    keep = []
    d = WeakConcurrentDict({f"k{i}": _new_dummy(i, keep) for i in range(5)})
    errors = []

    def copier():
        try:
            _ = d.copy()
            _ = deepcopy(d)
        except Exception as exc:
            errors.append(exc)

    def writer():
        try:
            for i in range(5, 10):
                d[f"k{i}"] = _new_dummy(i, keep)
        except Exception as exc:
            errors.append(exc)

    t1 = threading.Thread(target=copier)
    t2 = threading.Thread(target=writer)
    t1.start(); t2.start()
    t1.join(timeout=5); t2.join(timeout=5)
    assert not errors
