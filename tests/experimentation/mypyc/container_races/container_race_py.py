from __future__ import annotations

import threading
from collections import deque
from typing import Any

from mypy_extensions import mypyc_attr


@mypyc_attr(native_class=True)
class UnlockedListAppendOnly:
    __slots__ = ("items",)

    items: list[int]

    def __init__(self) -> None:
        self.items = []

    def prepare(self, total_operations: int) -> None:
        self.items = []

    def worker(self, thread_id: int, iterations: int) -> None:
        base = thread_id * iterations

        for i in range(iterations):
            self.items.append(base + i)

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class LockedListAppendOnly:
    __slots__ = ("items", "lock")

    items: list[int]
    lock: Any

    def __init__(self) -> None:
        self.items = []
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = []

    def worker(self, thread_id: int, iterations: int) -> None:
        base = thread_id * iterations

        for i in range(iterations):
            self.lock.acquire()

            try:
                self.items.append(base + i)
            finally:
                self.lock.release()

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class UnlockedListPopOnly:
    __slots__ = ("items",)

    items: list[int]

    def __init__(self) -> None:
        self.items = []

    def prepare(self, total_operations: int) -> None:
        self.items = [0] * total_operations

    def worker(self, thread_id: int, iterations: int) -> None:
        for _ in range(iterations):
            self.items.pop()

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class LockedListPopOnly:
    __slots__ = ("items", "lock")

    items: list[int]
    lock: Any

    def __init__(self) -> None:
        self.items = []
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = [0] * total_operations

    def worker(self, thread_id: int, iterations: int) -> None:
        for _ in range(iterations):
            self.lock.acquire()

            try:
                self.items.pop()
            finally:
                self.lock.release()

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class UnlockedDequeAppendOnly:
    __slots__ = ("items",)

    items: deque[int]

    def __init__(self) -> None:
        self.items = deque()

    def prepare(self, total_operations: int) -> None:
        self.items = deque()

    def worker(self, thread_id: int, iterations: int) -> None:
        base = thread_id * iterations

        for i in range(iterations):
            self.items.append(base + i)

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class LockedDequeAppendOnly:
    __slots__ = ("items", "lock")

    items: deque[int]
    lock: Any

    def __init__(self) -> None:
        self.items = deque()
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = deque()

    def worker(self, thread_id: int, iterations: int) -> None:
        base = thread_id * iterations

        for i in range(iterations):
            self.lock.acquire()

            try:
                self.items.append(base + i)
            finally:
                self.lock.release()

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class UnlockedDequePopOnly:
    __slots__ = ("items",)

    items: deque[int]

    def __init__(self) -> None:
        self.items = deque()

    def prepare(self, total_operations: int) -> None:
        self.items = deque(range(total_operations))

    def worker(self, thread_id: int, iterations: int) -> None:
        for _ in range(iterations):
            self.items.popleft()

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class LockedDequePopOnly:
    __slots__ = ("items", "lock")

    items: deque[int]
    lock: Any

    def __init__(self) -> None:
        self.items = deque()
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = deque(range(total_operations))

    def worker(self, thread_id: int, iterations: int) -> None:
        for _ in range(iterations):
            self.lock.acquire()

            try:
                self.items.popleft()
            finally:
                self.lock.release()

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class UnlockedDictSetOnly:
    __slots__ = ("items",)

    items: dict[int, int]

    def __init__(self) -> None:
        self.items = {}

    def prepare(self, total_operations: int) -> None:
        self.items = {}

    def worker(self, thread_id: int, iterations: int) -> None:
        base = thread_id * iterations

        for i in range(iterations):
            key = base + i
            self.items[key] = key

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class LockedDictSetOnly:
    __slots__ = ("items", "lock")

    items: dict[int, int]
    lock: Any

    def __init__(self) -> None:
        self.items = {}
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = {}

    def worker(self, thread_id: int, iterations: int) -> None:
        base = thread_id * iterations

        for i in range(iterations):
            key = base + i

            self.lock.acquire()

            try:
                self.items[key] = key
            finally:
                self.lock.release()

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class UnlockedDictPopOnly:
    __slots__ = ("items",)

    items: dict[int, int]

    def __init__(self) -> None:
        self.items = {}

    def prepare(self, total_operations: int) -> None:
        self.items = {i: i for i in range(total_operations)}

    def worker(self, thread_id: int, iterations: int) -> None:
        base = thread_id * iterations

        for i in range(iterations):
            self.items.pop(base + i)

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class LockedDictPopOnly:
    __slots__ = ("items", "lock")

    items: dict[int, int]
    lock: Any

    def __init__(self) -> None:
        self.items = {}
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = {i: i for i in range(total_operations)}

    def worker(self, thread_id: int, iterations: int) -> None:
        base = thread_id * iterations

        for i in range(iterations):
            self.lock.acquire()

            try:
                self.items.pop(base + i)
            finally:
                self.lock.release()

    def final_size(self) -> int:
        return len(self.items)