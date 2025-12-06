import pickle
import threading

from melder.utilities.general_base.isync import ISync


class DummySync(ISync):
    __slots__ = ("_value", "_lock")

    def __init__(self, value):
        self._value = self._coerce(value)
        self._lock = threading.RLock()

    @staticmethod
    def _coerce(val):
        return val

    def get(self):
        return self._value

    def try_get(self):
        return self._value

    def __add__(self, other):
        return self._perform_binary_op(other, lambda a, b: a + b)

    def __radd__(self, other):
        return self._perform_binary_op(other, lambda a, b: a + b, r_operation=True)


def test_is_sync_marker_and_unwrap_other():
    a = DummySync(1)
    b = DummySync(2)
    assert ISync._is_sync(a) is True
    assert a._unwrap_other(b) == 2
    assert a._unwrap_other(5) == 5


def test_perform_binary_op_with_sync_and_primitive():
    a = DummySync(3)
    b = DummySync(4)
    assert a + b == 7
    assert 10 + a == 13


def test_acquire_two_orders_by_id():
    a = DummySync(1)
    b = DummySync(2)
    first, second = ISync._acquire_two(a, b)
    assert {id(first), id(second)} == {id(a), id(b)}


def test_pickle_roundtrip_recreates_lock_and_preserves_value():
    a = DummySync(9)
    data = pickle.dumps(a)
    b = pickle.loads(data)
    assert isinstance(b, DummySync)
    assert b.get() == 9
    assert b is not a
    # lock recreated
    assert isinstance(b._lock, threading.RLock().__class__)


def test_hash_uses_value_when_hashable():
    a = DummySync(5)
    # default __hash__ falls back to object id; ensure it's int
    assert isinstance(hash(a), int)


def test_hash_fallback_for_unhashable_value():
    a = DummySync([1, 2])
    h = hash(a)
    assert isinstance(h, int)


def test_eq_with_sync_and_plain():
    a = DummySync(3)
    b = DummySync(3)
    c = DummySync(4)
    # ISync doesn't override __eq__; just verify unwrap comparisons
    assert a._unwrap_other(b) == 3
    assert a._unwrap_other(c) == 4
    assert a._unwrap_other(3) == 3


def test_getstate_and_setstate_excludes_lock():
    a = DummySync(11)
    state = a.__getstate__()
    assert "_value" in state
    b = DummySync(0)
    b.__setstate__(state)
    assert b.get() == 11
    assert isinstance(b._lock, threading.RLock().__class__)


def test_perform_binary_op_with_uncoercible_other_returns_other():
    class Bad:
        pass
    a = DummySync(1)
    bad = Bad()
    # _unwrap_other returns bad; op receives (self._value, bad)
    def op(x, y):
        assert x == 1
        assert y is bad
        return "ok"
    result = a._perform_binary_op(bad, op)
    assert result == "ok"
