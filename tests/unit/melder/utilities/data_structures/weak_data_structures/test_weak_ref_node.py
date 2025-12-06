import gc
import time

import pytest

from melder.utilities.data_structures.weak_data_structures.weak_ref_node import WeakRefNode
from melder.utilities.custom_exceptions.dead_reference_error import DeadReferenceError


class Dummy:
    def __init__(self, value):
        self.value = value

    def inc(self):
        self.value += 1
        return self.value


class NonWeak:
    __slots__ = ("value",)
    def __init__(self, value):
        self.value = value


def _force_collect():
    gc.collect()
    time.sleep(0.01)
    gc.collect()


def test_init_and_liveness():
    obj = Dummy(1)
    node = WeakRefNode(obj)
    assert node.is_alive() is True
    assert node.dead is False
    assert node.try_get() is obj
    assert node.get() is obj


def test_init_raises_for_nonweakrefable():
    with pytest.raises(TypeError):
        WeakRefNode(NonWeak(1))


def test_get_raises_dead_reference_after_gc():
    obj = Dummy(2)
    node = WeakRefNode(obj)
    del obj
    _force_collect()
    assert node.dead is True
    with pytest.raises(DeadReferenceError):
        node.get()
    assert node.try_get() is None


def test_has_fired_after_gc():
    obj = Dummy(3)
    node = WeakRefNode(obj)
    del obj
    _force_collect()
    for _ in range(10):
        if node.has_fired:
            break
        time.sleep(0.01)
        _force_collect()
    assert node.has_fired is True


def test_on_collect_invoked_once():
    calls = []
    def on_collect(n):
        calls.append(n.id)
    obj = Dummy(4)
    node = WeakRefNode(obj, on_collect=on_collect)
    del obj
    _force_collect()
    for _ in range(10):
        if calls:
            break
        time.sleep(0.01)
        _force_collect()
    assert calls == [node.id]


def test_add_callback_and_fire_callbacks_manual():
    calls = []
    def extra(n):
        calls.append("extra")
    obj = Dummy(5)
    node = WeakRefNode(obj)
    node.add_callback(extra)
    node.fire_callbacks()
    assert calls == ["extra"]
    # callbacks cleared after firing
    node.fire_callbacks()
    assert calls == ["extra"]


def test_fire_callbacks_after_gc():
    calls = []
    def extra(n):
        calls.append(n.id)
    obj = Dummy(6)
    node = WeakRefNode(obj)
    node.add_callback(extra)
    del obj
    _force_collect()
    for _ in range(10):
        if calls:
            break
        time.sleep(0.01)
        _force_collect()
    assert calls == [node.id]


def test_set_replaces_target_and_resets_flags():
    a = Dummy(1)
    b = Dummy(2)
    node = WeakRefNode(a)
    assert node.get() is a
    node.set(b)
    assert node.get() is b
    assert node.dead is False
    assert node.has_fired is False


def test_set_raises_when_cleaned():
    node = WeakRefNode(Dummy(1))
    node.cleanup()
    with pytest.raises(RuntimeError):
        node.set(Dummy(2))


def test_swap_returns_old_value_if_alive():
    a = Dummy(1)
    b = Dummy(2)
    node = WeakRefNode(a)
    prev = node.swap(b)
    assert prev is a
    assert node.get() is b


def test_swap_returns_none_if_dead():
    obj = Dummy(3)
    node = WeakRefNode(obj)
    del obj
    _force_collect()
    new_obj = Dummy(4)
    prev = node.swap(new_obj)
    assert prev is None
    assert node.try_get() is new_obj


def test_cas_success_and_failure():
    a = Dummy(1)
    b = Dummy(2)
    c = Dummy(3)
    node = WeakRefNode(a)
    assert node.cas(a, b) is True
    assert node.get() is b
    assert node.cas(c, a) is False
    assert node.get() is b


def test_cas_raises_when_cleaned():
    node = WeakRefNode(Dummy(1))
    node.cleanup()
    with pytest.raises(RuntimeError):
        node.cas(Dummy(1), Dummy(2))


def test_transform_and_map_apply_function():
    obj = Dummy(5)
    node = WeakRefNode(obj)
    assert node.transform(lambda o: o.value * 2) == 10
    assert node.map(lambda o: o.inc()) == 6


def test_transform_raises_when_dead():
    obj = Dummy(6)
    node = WeakRefNode(obj)
    del obj
    _force_collect()
    with pytest.raises(DeadReferenceError):
        node.transform(lambda o: o.value)


def test_deref_strict_and_non_strict():
    obj = Dummy(7)
    node = WeakRefNode(obj)
    assert node.deref(strict=True) is obj
    del obj
    _force_collect()
    assert node.deref(strict=False) is None
    with pytest.raises(DeadReferenceError):
        node.deref(strict=True)


def test_cleanup_idempotent_and_marks_dead():
    node = WeakRefNode(Dummy(1))
    node.cleanup()
    node.cleanup()
    assert node.dead is True
    with pytest.raises(DeadReferenceError):
        node.get()


def test_add_callback_raises_when_cleaned():
    node = WeakRefNode(Dummy(1))
    node.cleanup()
    with pytest.raises(RuntimeError):
        node.add_callback(lambda n: None)


def test_repr_contains_state_and_phantom():
    obj = Dummy(8)
    node = WeakRefNode(obj)
    text = repr(node)
    assert "WeakRefNode" in text
    assert "alive" in text
    del obj
    _force_collect()
    text2 = repr(node)
    assert "dead" in text2


def test_eq_and_hash_based_on_id():
    obj = Dummy(9)
    node1 = WeakRefNode(obj)
    node2 = node1
    node3 = WeakRefNode(Dummy(9))
    assert node1 == node2
    assert node1 != node3
    assert hash(node1) == hash(node1.id)


def test_try_get_after_cleanup_returns_none():
    node = WeakRefNode(Dummy(1))
    node.cleanup()
    assert node.try_get() is None


def test_fire_callbacks_no_callbacks_is_noop():
    node = WeakRefNode(Dummy(1))
    node.fire_callbacks()  # should not raise


def test_phantom_fired_cleared_on_set():
    obj = Dummy(10)
    node = WeakRefNode(obj)
    del obj
    _force_collect()
    assert node.has_fired is True
    new_obj = Dummy(11)  # keep strong ref so it isn't GC'd immediately
    node.set(new_obj)
    # newly set clears phantom state
    assert node.has_fired is False


def test_callbacks_cleared_after_gc():
    calls = []
    obj = Dummy(12)
    node = WeakRefNode(obj)
    node.add_callback(lambda n: calls.append("x"))
    del obj
    _force_collect()
    for _ in range(10):
        if calls:
            break
        time.sleep(0.01)
        _force_collect()
    assert calls == ["x"]
    # further callbacks should not fire again
    calls.clear()
    node.fire_callbacks()
    assert calls == []


def test_set_with_non_weakrefable_raises():
    node = WeakRefNode(Dummy(1))
    with pytest.raises(TypeError):
        node.set(NonWeak(2))
