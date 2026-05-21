from __future__ import annotations

import heapq
import queue
import threading
from array import array
from collections import OrderedDict, deque
from typing import Any

from mypy_extensions import mypyc_attr


@mypyc_attr(native_class=True)
class ListAppendOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: list[int]
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = []
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = []

    def worker(self, thread_id: int, iterations: int) -> None:
        base = thread_id * iterations

        for i in range(iterations):
            value = base + i

            if self.use_lock:
                self.lock.acquire()
                try:
                    self.items.append(value)
                finally:
                    self.lock.release()
            else:
                self.items.append(value)

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class ListPopEndOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: list[int]
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = []
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = [0] * total_operations

    def worker(self, thread_id: int, iterations: int) -> None:
        for _ in range(iterations):
            if self.use_lock:
                self.lock.acquire()
                try:
                    self.items.pop()
                finally:
                    self.lock.release()
            else:
                self.items.pop()

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class ListPopZeroOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: list[int]
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = []
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = [0] * total_operations

    def worker(self, thread_id: int, iterations: int) -> None:
        for _ in range(iterations):
            if self.use_lock:
                self.lock.acquire()
                try:
                    self.items.pop(0)
                finally:
                    self.lock.release()
            else:
                self.items.pop(0)

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class ListInsertZeroOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: list[int]
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = []
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = []

    def worker(self, thread_id: int, iterations: int) -> None:
        base = thread_id * iterations

        for i in range(iterations):
            value = base + i

            if self.use_lock:
                self.lock.acquire()
                try:
                    self.items.insert(0, value)
                finally:
                    self.lock.release()
            else:
                self.items.insert(0, value)

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class ListRemoveUniqueOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: list[int]
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = []
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = list(range(total_operations))

    def worker(self, thread_id: int, iterations: int) -> None:
        base = thread_id * iterations

        for i in range(iterations):
            value = base + i

            if self.use_lock:
                self.lock.acquire()
                try:
                    self.items.remove(value)
                finally:
                    self.lock.release()
            else:
                self.items.remove(value)

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class DequeAppendOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: deque[int]
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = deque()
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = deque()

    def worker(self, thread_id: int, iterations: int) -> None:
        base = thread_id * iterations

        for i in range(iterations):
            value = base + i

            if self.use_lock:
                self.lock.acquire()
                try:
                    self.items.append(value)
                finally:
                    self.lock.release()
            else:
                self.items.append(value)

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class DequeAppendLeftOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: deque[int]
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = deque()
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = deque()

    def worker(self, thread_id: int, iterations: int) -> None:
        base = thread_id * iterations

        for i in range(iterations):
            value = base + i

            if self.use_lock:
                self.lock.acquire()
                try:
                    self.items.appendleft(value)
                finally:
                    self.lock.release()
            else:
                self.items.appendleft(value)

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class DequePopOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: deque[int]
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = deque()
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = deque(range(total_operations))

    def worker(self, thread_id: int, iterations: int) -> None:
        for _ in range(iterations):
            if self.use_lock:
                self.lock.acquire()
                try:
                    self.items.pop()
                finally:
                    self.lock.release()
            else:
                self.items.pop()

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class DequePopleftOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: deque[int]
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = deque()
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = deque(range(total_operations))

    def worker(self, thread_id: int, iterations: int) -> None:
        for _ in range(iterations):
            if self.use_lock:
                self.lock.acquire()
                try:
                    self.items.popleft()
                finally:
                    self.lock.release()
            else:
                self.items.popleft()

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class DictSetOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: dict[int, int]
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = {}
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = {}

    def worker(self, thread_id: int, iterations: int) -> None:
        base = thread_id * iterations

        for i in range(iterations):
            key = base + i

            if self.use_lock:
                self.lock.acquire()
                try:
                    self.items[key] = key
                finally:
                    self.lock.release()
            else:
                self.items[key] = key

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class DictPopOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: dict[int, int]
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = {}
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = {i: i for i in range(total_operations)}

    def worker(self, thread_id: int, iterations: int) -> None:
        base = thread_id * iterations

        for i in range(iterations):
            key = base + i

            if self.use_lock:
                self.lock.acquire()
                try:
                    self.items.pop(key)
                finally:
                    self.lock.release()
            else:
                self.items.pop(key)

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class DictDelOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: dict[int, int]
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = {}
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = {i: i for i in range(total_operations)}

    def worker(self, thread_id: int, iterations: int) -> None:
        base = thread_id * iterations

        for i in range(iterations):
            key = base + i

            if self.use_lock:
                self.lock.acquire()
                try:
                    del self.items[key]
                finally:
                    self.lock.release()
            else:
                del self.items[key]

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class OrderedDictSetOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: Any
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = OrderedDict()
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = OrderedDict()

    def worker(self, thread_id: int, iterations: int) -> None:
        base = thread_id * iterations

        for i in range(iterations):
            key = base + i

            if self.use_lock:
                self.lock.acquire()
                try:
                    self.items[key] = key
                finally:
                    self.lock.release()
            else:
                self.items[key] = key

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class OrderedDictPopOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: Any
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = OrderedDict()
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = OrderedDict((i, i) for i in range(total_operations))

    def worker(self, thread_id: int, iterations: int) -> None:
        base = thread_id * iterations

        for i in range(iterations):
            key = base + i

            if self.use_lock:
                self.lock.acquire()
                try:
                    self.items.pop(key)
                finally:
                    self.lock.release()
            else:
                self.items.pop(key)

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class OrderedDictPopItemOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: Any
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = OrderedDict()
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = OrderedDict((i, i) for i in range(total_operations))

    def worker(self, thread_id: int, iterations: int) -> None:
        for _ in range(iterations):
            if self.use_lock:
                self.lock.acquire()
                try:
                    self.items.popitem()
                finally:
                    self.lock.release()
            else:
                self.items.popitem()

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class OrderedDictMoveToEndOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: Any
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = OrderedDict()
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = OrderedDict((i, i) for i in range(total_operations))

    def worker(self, thread_id: int, iterations: int) -> None:
        base = thread_id * iterations

        for i in range(iterations):
            key = base + i

            if self.use_lock:
                self.lock.acquire()
                try:
                    self.items.move_to_end(key)
                finally:
                    self.lock.release()
            else:
                self.items.move_to_end(key)

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class SetAddOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: set[int]
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = set()
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = set()

    def worker(self, thread_id: int, iterations: int) -> None:
        base = thread_id * iterations

        for i in range(iterations):
            value = base + i

            if self.use_lock:
                self.lock.acquire()
                try:
                    self.items.add(value)
                finally:
                    self.lock.release()
            else:
                self.items.add(value)

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class SetRemoveOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: set[int]
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = set()
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = set(range(total_operations))

    def worker(self, thread_id: int, iterations: int) -> None:
        base = thread_id * iterations

        for i in range(iterations):
            value = base + i

            if self.use_lock:
                self.lock.acquire()
                try:
                    self.items.remove(value)
                finally:
                    self.lock.release()
            else:
                self.items.remove(value)

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class SetDiscardOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: set[int]
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = set()
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = set(range(total_operations))

    def worker(self, thread_id: int, iterations: int) -> None:
        base = thread_id * iterations

        for i in range(iterations):
            value = base + i

            if self.use_lock:
                self.lock.acquire()
                try:
                    self.items.discard(value)
                finally:
                    self.lock.release()
            else:
                self.items.discard(value)

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class SetPopOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: set[int]
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = set()
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = set(range(total_operations))

    def worker(self, thread_id: int, iterations: int) -> None:
        for _ in range(iterations):
            if self.use_lock:
                self.lock.acquire()
                try:
                    self.items.pop()
                finally:
                    self.lock.release()
            else:
                self.items.pop()

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class HeapPushOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: list[int]
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = []
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = []

    def worker(self, thread_id: int, iterations: int) -> None:
        base = thread_id * iterations

        for i in range(iterations):
            value = base + i

            if self.use_lock:
                self.lock.acquire()
                try:
                    heapq.heappush(self.items, value)
                finally:
                    self.lock.release()
            else:
                heapq.heappush(self.items, value)

    def final_size(self) -> int:
        return len(self.items)

    def validation_error_count(self) -> int:
        errors = 0
        size = len(self.items)

        for index in range(size):
            left = index * 2 + 1
            right = index * 2 + 2

            if left < size and self.items[index] > self.items[left]:
                errors += 1

            if right < size and self.items[index] > self.items[right]:
                errors += 1

        return errors


@mypyc_attr(native_class=True)
class HeapPopOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: list[int]
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = []
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = list(range(total_operations))
        heapq.heapify(self.items)

    def worker(self, thread_id: int, iterations: int) -> None:
        for _ in range(iterations):
            if self.use_lock:
                self.lock.acquire()
                try:
                    heapq.heappop(self.items)
                finally:
                    self.lock.release()
            else:
                heapq.heappop(self.items)

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class ArrayAppendOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: Any
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = array("q")
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = array("q")

    def worker(self, thread_id: int, iterations: int) -> None:
        base = thread_id * iterations

        for i in range(iterations):
            value = base + i

            if self.use_lock:
                self.lock.acquire()
                try:
                    self.items.append(value)
                finally:
                    self.lock.release()
            else:
                self.items.append(value)

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class ArrayPopOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: Any
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = array("q")
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = array("q", range(total_operations))

    def worker(self, thread_id: int, iterations: int) -> None:
        for _ in range(iterations):
            if self.use_lock:
                self.lock.acquire()
                try:
                    self.items.pop()
                finally:
                    self.lock.release()
            else:
                self.items.pop()

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class BytearrayAppendOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: bytearray
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = bytearray()
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = bytearray()

    def worker(self, thread_id: int, iterations: int) -> None:
        for i in range(iterations):
            value = i & 255

            if self.use_lock:
                self.lock.acquire()
                try:
                    self.items.append(value)
                finally:
                    self.lock.release()
            else:
                self.items.append(value)

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class BytearrayPopOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: bytearray
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = bytearray()
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = bytearray(total_operations)

    def worker(self, thread_id: int, iterations: int) -> None:
        for _ in range(iterations):
            if self.use_lock:
                self.lock.acquire()
                try:
                    self.items.pop()
                finally:
                    self.lock.release()
            else:
                self.items.pop()

    def final_size(self) -> int:
        return len(self.items)


@mypyc_attr(native_class=True)
class SimpleQueuePutOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: Any
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = queue.SimpleQueue()
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = queue.SimpleQueue()

    def worker(self, thread_id: int, iterations: int) -> None:
        base = thread_id * iterations

        for i in range(iterations):
            value = base + i

            if self.use_lock:
                self.lock.acquire()
                try:
                    self.items.put(value)
                finally:
                    self.lock.release()
            else:
                self.items.put(value)

    def final_size(self) -> int:
        return self.items.qsize()


@mypyc_attr(native_class=True)
class SimpleQueueGetOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: Any
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = queue.SimpleQueue()
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = queue.SimpleQueue()

        for i in range(total_operations):
            self.items.put(i)

    def worker(self, thread_id: int, iterations: int) -> None:
        for _ in range(iterations):
            if self.use_lock:
                self.lock.acquire()
                try:
                    self.items.get()
                finally:
                    self.lock.release()
            else:
                self.items.get()

    def final_size(self) -> int:
        return self.items.qsize()


@mypyc_attr(native_class=True)
class QueuePutOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: Any
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = queue.Queue()
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = queue.Queue()

    def worker(self, thread_id: int, iterations: int) -> None:
        base = thread_id * iterations

        for i in range(iterations):
            value = base + i

            if self.use_lock:
                self.lock.acquire()
                try:
                    self.items.put(value)
                finally:
                    self.lock.release()
            else:
                self.items.put(value)

    def final_size(self) -> int:
        return self.items.qsize()


@mypyc_attr(native_class=True)
class QueueGetOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: Any
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = queue.Queue()
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = queue.Queue()

        for i in range(total_operations):
            self.items.put(i)

    def worker(self, thread_id: int, iterations: int) -> None:
        for _ in range(iterations):
            if self.use_lock:
                self.lock.acquire()
                try:
                    self.items.get()
                finally:
                    self.lock.release()
            else:
                self.items.get()

    def final_size(self) -> int:
        return self.items.qsize()


@mypyc_attr(native_class=True)
class LifoQueuePutOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: Any
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = queue.LifoQueue()
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = queue.LifoQueue()

    def worker(self, thread_id: int, iterations: int) -> None:
        base = thread_id * iterations

        for i in range(iterations):
            value = base + i

            if self.use_lock:
                self.lock.acquire()
                try:
                    self.items.put(value)
                finally:
                    self.lock.release()
            else:
                self.items.put(value)

    def final_size(self) -> int:
        return self.items.qsize()


@mypyc_attr(native_class=True)
class LifoQueueGetOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: Any
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = queue.LifoQueue()
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = queue.LifoQueue()

        for i in range(total_operations):
            self.items.put(i)

    def worker(self, thread_id: int, iterations: int) -> None:
        for _ in range(iterations):
            if self.use_lock:
                self.lock.acquire()
                try:
                    self.items.get()
                finally:
                    self.lock.release()
            else:
                self.items.get()

    def final_size(self) -> int:
        return self.items.qsize()


@mypyc_attr(native_class=True)
class PriorityQueuePutOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: Any
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = queue.PriorityQueue()
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = queue.PriorityQueue()

    def worker(self, thread_id: int, iterations: int) -> None:
        base = thread_id * iterations

        for i in range(iterations):
            value = base + i

            if self.use_lock:
                self.lock.acquire()
                try:
                    self.items.put((value, value))
                finally:
                    self.lock.release()
            else:
                self.items.put((value, value))

    def final_size(self) -> int:
        return self.items.qsize()


@mypyc_attr(native_class=True)
class PriorityQueueGetOnly:
    __slots__ = ("items", "use_lock", "lock")

    items: Any
    use_lock: bool
    lock: Any

    def __init__(self, use_lock: bool) -> None:
        self.items = queue.PriorityQueue()
        self.use_lock = use_lock
        self.lock = threading.Lock()

    def prepare(self, total_operations: int) -> None:
        self.items = queue.PriorityQueue()

        for i in range(total_operations):
            self.items.put((i, i))

    def worker(self, thread_id: int, iterations: int) -> None:
        for _ in range(iterations):
            if self.use_lock:
                self.lock.acquire()
                try:
                    self.items.get()
                finally:
                    self.lock.release()
            else:
                self.items.get()

    def final_size(self) -> int:
        return self.items.qsize()