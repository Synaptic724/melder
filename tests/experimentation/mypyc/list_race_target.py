from __future__ import annotations

import threading
from _thread import LockType

from mypy_extensions import mypyc_attr


@mypyc_attr(native_class=True)
class SharedListLimitRace:
    """
    Lock-protected shared-list race target.

    This protects the full invariant:

        if len(self.items) < self.limit:
            self.items.append(value)

    The lock must cover both the check and the append. Locking only append is
    not enough because the race happens between checking the length and mutating
    the list.
    """

    __slots__ = ("items", "limit", "spin_count", "lock")

    items: list[int]
    limit: int
    spin_count: int
    lock: LockType

    def __init__(self, limit: int, spin_count: int) -> None:
        self.items = []
        self.limit = limit
        self.spin_count = spin_count
        self.lock = threading.Lock()

    def spin(self, seed: int) -> int:
        value = seed

        for i in range(self.spin_count):
            value = (value * 1664525 + 1013904223 + i) & 0x7FFFFFFF

        return value

    def try_append_once(self, value: int) -> None:
        with self.lock:
            observed_length = len(self.items)

            if observed_length < self.limit:
                self.spin(value)
                self.items.append(value)

    def hammer_append(self, thread_id: int, iterations: int) -> None:
        base = thread_id * iterations

        for i in range(iterations):
            self.try_append_once(base + i)

    def current_length(self) -> int:
        with self.lock:
            return len(self.items)


@mypyc_attr(native_class=True)
class SharedListCounterRace:
    """
    Lock-protected list-backed counter.

    This protects the full read-modify-write sequence:

        value = self.items[0]
        self.items[0] = value + 1

    The lock must cover both the read and the write.
    """

    __slots__ = ("items", "spin_count", "lock")

    items: list[int]
    spin_count: int
    lock: threading.RLock

    def __init__(self, spin_count: int) -> None:
        self.items = [0]
        self.spin_count = spin_count
        self.lock = threading.RLock()

    def spin(self, seed: int) -> int:
        value = seed

        for i in range(self.spin_count):
            value = (value * 1103515245 + 12345 + i) & 0x7FFFFFFF

        return value

    def increment_once(self) -> None:
        with self.lock:
            value = self.items[0]
            self.spin(value)
            self.items[0] = value + 1

    def hammer_increment(self, iterations: int) -> None:
        for _ in range(iterations):
            self.increment_once()

    def current_value(self) -> int:
        with self.lock:
            return self.items[0]