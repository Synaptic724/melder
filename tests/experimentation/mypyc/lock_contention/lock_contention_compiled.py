from __future__ import annotations

import threading
from typing import Any

from mypy_extensions import mypyc_attr


@mypyc_attr(native_class=True)
class LockCounter:
    """
    Shared counter protected by threading.Lock.
    """

    __slots__ = ("lock", "counter")

    lock: Any
    counter: int

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.counter = 0

    def increment_once(self) -> None:
        self.lock.acquire()

        try:
            self.counter += 1
        finally:
            self.lock.release()

    def increment_many(self, iterations: int) -> None:
        for _ in range(iterations):
            self.increment_once()

    def current_value(self) -> int:
        self.lock.acquire()

        try:
            return self.counter
        finally:
            self.lock.release()


@mypyc_attr(native_class=True)
class RLockCounter:
    """
    Shared counter protected by threading.RLock.
    """

    __slots__ = ("lock", "counter")

    lock: Any
    counter: int

    def __init__(self) -> None:
        self.lock = threading.RLock()
        self.counter = 0

    def increment_once(self) -> None:
        self.lock.acquire()

        try:
            self.counter += 1
        finally:
            self.lock.release()

    def increment_many(self, iterations: int) -> None:
        for _ in range(iterations):
            self.increment_once()

    def current_value(self) -> int:
        self.lock.acquire()

        try:
            return self.counter
        finally:
            self.lock.release()