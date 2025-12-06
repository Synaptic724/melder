import gc
import threading
import time

import pytest

from melder.utilities.synchronization.sync_weak_ref import SyncWeakRef


class Dummy:
    def __init__(self, value):
        self.value = value

    def inc(self):
        self.value += 1
        return self.value

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        if isinstance(other, Dummy):
            return self.value == other.value
        return False


def _force_collect():
    gc.collect()
    time.sleep(0.01)
    gc.collect()


def test_basic_get_try_get_is_alive():
    target = Dummy(1)
    ref = SyncWeakRef(target)
    assert ref.is_alive() is True
    assert ref.try_get() is target
    assert ref.get() is target


def test_cleanup_idempotent_and_check_cleaned():
    ref = SyncWeakRef(Dummy(1))
    ref.cleanup()
    ref.cleanup()
    assert ref.cleaned is True
    with pytest.raises(RuntimeError):
        ref.check_cleaned()
    with pytest.raises(RuntimeError):
        ref.is_alive()


def test_get_after_cleanup_raises():
    ref = SyncWeakRef(Dummy(1))
    ref.cleanup()
    with pytest.raises(RuntimeError):
        ref.get()


def test_get_raises_reference_error_when_dead():
    ref = SyncWeakRef(Dummy(2))
    obj = ref.get()
    del obj
    _force_collect()
    with pytest.raises(ReferenceError):
        ref.get()


def test_try_get_returns_none_when_dead():
    ref = SyncWeakRef(Dummy(3))
    obj = ref.try_get()
    del obj
    _force_collect()
    assert ref.try_get() is None


def test_transform_and_map_apply_function():
    ref = SyncWeakRef(Dummy(5))
    assert ref.transform(lambda d: d.value * 2) == 10
    assert ref.map(lambda d: d.inc()) == 6


def test_set_replaces_target():
    a = Dummy(1)
    b = Dummy(2)
    ref = SyncWeakRef(a)
    assert ref.get() is a
    ref.set(b)
    assert ref.get() is b


def test_cas_succeeds_and_fails_by_identity():
    a = Dummy(1)
    b = Dummy(2)
    c = Dummy(3)
    ref = SyncWeakRef(a)
    assert ref.cas(a, b) is True
    assert ref.get() is b
    assert ref.cas(c, a) is False
    assert ref.get() is b


def test_swap_returns_previous_if_alive():
    a = Dummy(1)
    b = Dummy(2)
    ref = SyncWeakRef(a)
    prev = ref.swap(b)
    assert prev is a
    assert ref.get() is b


def test_locked_yields_object_with_lock_held():
    ref = SyncWeakRef(Dummy(1))
    with ref.locked() as obj:
        assert obj is ref.get()


def test_repr_contains_state_and_id():
    ref = SyncWeakRef(Dummy(1))
    text = repr(ref)
    assert "SyncWeakRef" in text
    assert "alive" in text
    ref.cleanup()
    assert "cleaned" in repr(ref)


def test_eq_and_hash_behaviour():
    a = Dummy(10)
    ref = SyncWeakRef(a)
    other = SyncWeakRef(a)
    assert ref == other
    assert ref == a
    assert isinstance(hash(ref), int)


def test_register_on_collect_and_has_fired():
    fired = []

    def on_collect(r):
        fired.append("x")

    def make_ref():
        obj = Dummy(1)
        r = SyncWeakRef(obj, on_collect=on_collect, auto_cleanup=False)
        return r

    ref = make_ref()
    obj = ref.get()
    del obj
    _force_collect()
    # Weakref callbacks may be asynchronous; poll briefly
    for _ in range(10):
        if ref.has_fired:
            break
        time.sleep(0.01)
        _force_collect()
    assert ref.has_fired is True
    assert fired


def test_auto_cleanup_triggers_on_collect():
    def make_ref():
        obj = Dummy(2)
        return SyncWeakRef(obj, auto_cleanup=True)

    ref = make_ref()
    obj = ref.get()
    del obj
    _force_collect()
    for _ in range(10):
        if ref.cleaned:
            break
        time.sleep(0.01)
        _force_collect()
    assert ref.cleaned is True


def test_enable_disable_auto_cleanup():
    ref = SyncWeakRef(Dummy(1))
    ref.enable_auto_cleanup()
    assert ref._auto_cleanup is True
    ref.disable_auto_cleanup()
    assert ref._auto_cleanup is False


def test_register_on_collect_replaces_callback():
    calls = []

    def cb1(r):
        calls.append("1")

    def cb2(r):
        calls.append("2")

    ref = SyncWeakRef(Dummy(1))
    ref.register_on_collect(cb1)
    ref.register_on_collect(cb2)
    obj = ref.get()
    del obj
    _force_collect()
    for _ in range(10):
        if calls:
            break
        time.sleep(0.01)
        _force_collect()
    assert calls == ["2"]


def test_has_fired_set_on_callback_without_auto_cleanup():
    ref = SyncWeakRef(Dummy(5))
    obj = ref.get()
    del obj
    _force_collect()
    for _ in range(10):
        if ref.has_fired:
            break
        time.sleep(0.01)
        _force_collect()
    assert ref.has_fired is True
    assert ref.cleaned is False


def test_cleanup_inside_on_collect_safe():
    cleaned = []

    def on_collect(r):
        r.cleanup()
        cleaned.append(True)

    ref = SyncWeakRef(Dummy(1), on_collect=on_collect)
    obj = ref.get()
    del obj
    _force_collect()
    for _ in range(10):
        if cleaned:
            break
        time.sleep(0.01)
        _force_collect()
    assert cleaned
    assert ref.cleaned is True


def test_cas_with_dead_target_returns_false():
    ref = SyncWeakRef(Dummy(1))
    target = ref.get()
    del target
    _force_collect()
    assert ref.cas(Dummy(1), Dummy(2)) is False


def test_swap_with_dead_target_returns_none():
    ref = SyncWeakRef(Dummy(1))
    target = ref.get()
    del target
    _force_collect()
    prev = ref.swap(Dummy(2))
    assert prev is None
    assert ref.get().value == 2


def test_try_get_after_cleanup_raises():
    ref = SyncWeakRef(Dummy(1))
    ref.cleanup()
    with pytest.raises(RuntimeError):
        ref.try_get()


def test_transform_raises_reference_error_when_dead():
    ref = SyncWeakRef(Dummy(7))
    obj = ref.get()
    del obj
    _force_collect()
    with pytest.raises(ReferenceError):
        ref.transform(lambda x: x.value)


def test_locked_raises_when_cleaned():
    ref = SyncWeakRef(Dummy(1))
    ref.cleanup()
    with pytest.raises(RuntimeError):
        with ref.locked():
            pass

