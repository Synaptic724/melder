"""
Probe C: the owner's simpler shape (chat 2026-10-14) - the holder IS a deque of idle objects, kept in the
Creations object under the spell id; the mode comes from the Spell; no out-record, no identity checks; release
appends; the elastic trim is optional on the subclass. Measured against the spike's ManagedShell on the same VM.
"""
import gc
import os
import statistics
import sys
import threading
import time
from collections import deque
from typing import Callable, Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import managed_shell as ms


class Thing:
    def __init__(self) -> None:
        self.state = 0

    def reset(self) -> None:
        self.state = 0

    def close(self) -> None:
        self.state = -1


class ManagedSpellQuantity(deque):
    """Idle objects of one managed spell in one root; the mode and numbers composed from the Spell at creation."""

    def __init__(self, mode: str, limit: int, timeout_seconds: float, max_idle: int,
                 reset_method_names: Tuple[str, ...], disposal_method_names: Tuple[str, ...]) -> None:
        super().__init__()
        self.mode = mode
        self.limit = limit
        self.timeout_seconds = timeout_seconds
        self.max_idle = max_idle            # elastic only; 0 = no trim
        self.reset_method_names = reset_method_names
        self.disposal_method_names = disposal_method_names
        self.count = 0                      # objects built and alive (limited / queue accounting)
        self._lock = threading.Lock()
        self._cond = threading.Condition(self._lock)

    def build_place(self, build: Callable[[], object]) -> object:
        """The miss: limited raises at the limit, queue waits for a release, elastic always builds."""
        if self.mode == "elastic":
            with self._lock:
                self.count += 1
            return build()
        with self._lock:
            if self.mode == "queue":
                if not self._cond.wait_for(lambda: self.count < self.limit or len(self) > 0,
                                           timeout=self.timeout_seconds):
                    raise ms.ManagedQuantityExhausted("no place freed within the timeout")
                if len(self) > 0:
                    return self.pop()
            elif self.count >= self.limit:
                raise ms.ManagedQuantityExhausted("every place is taken")
            self.count += 1
        try:
            return build()
        except BaseException:
            with self._lock:
                self.count -= 1
            raise

    def put_back(self, item: object) -> None:
        """Release: reset outside any lock, append; elastic trims the oldest idle above max_idle; queue notifies."""
        for name in self.reset_method_names:
            item.__getattribute__(name)()
        self.append(item)
        if self.mode == "elastic":
            if self.max_idle and len(self) > self.max_idle:
                surplus = self.popleft()
                with self._lock:
                    self.count -= 1
                for name in self.disposal_method_names:
                    surplus.__getattribute__(name)()
        elif self.mode == "queue":
            with self._lock:
                self._cond.notify()


class ReleaseManagedSpellSimple:
    """type -> the holders of that class (one per root that binds it); the common case is one."""

    _by_type: Dict[type, Tuple[ManagedSpellQuantity, ...]] = {}

    @classmethod
    def release(cls, item: object) -> None:
        holders = cls._by_type[type(item)]
        if len(holders) == 1:
            holders[0].put_back(item)
        else:
            raise RuntimeError("the class is managed by several roots: pass the target")


def timed(fn: Callable[[], object], n: int = 40000, reps: int = 5, warm: int = 10000) -> float:
    for _ in range(warm):
        fn()
    samples: List[float] = []
    for _ in range(reps):
        t0 = time.perf_counter_ns()
        for _ in range(n):
            fn()
        samples.append((time.perf_counter_ns() - t0) / n)
    return statistics.median(samples)


def main() -> int:
    release = ReleaseManagedSpellSimple.release
    gc.disable()
    try:
        for label, mode, limit, max_idle, reset in (("elastic, no reset", "elastic", 0, 256, ()),
                                                    ("elastic, reset()", "elastic", 0, 256, ("reset",)),
                                                    ("limited_quantity(4)", "limited_quantity", 4, 0, ()),
                                                    ("queue(4, 1.0s)", "queue", 4, 0, ())):
            h = ManagedSpellQuantity(mode, limit, 1.0, max_idle, reset, ("close",))
            ReleaseManagedSpellSimple._by_type = {Thing: (h,)}
            h.put_back(h.build_place(Thing))

            def emitted_site_cycle() -> object:
                # what the plan would emit inline: a try/pop, the miss out of line; then the user's release
                try:
                    v = h.pop()
                except IndexError:
                    v = h.build_place(Thing)
                release(v)
                return v

            def direct_holder_cycle() -> object:
                try:
                    v = h.pop()
                except IndexError:
                    v = h.build_place(Thing)
                h.put_back(v)
                return v

            a = timed(emitted_site_cycle)
            b = timed(direct_holder_cycle)
            print(f"{label}: inline pop + ReleaseManagedSpell.release {a:.0f} ns; inline pop + holder put_back "
                  f"{b:.0f} ns; idle {len(h)}, count {h.count}")
        # the stress checks that matter: limited never exceeds its limit under 8 threads; queue waits and is served
        h = ManagedSpellQuantity("limited_quantity", 3, 1.0, 0, (), ("close",))
        ReleaseManagedSpellSimple._by_type = {Thing: (h,)}
        peak = [0]
        lk = threading.Lock()
        exhausted = [0]

        def worker() -> None:
            for _ in range(2000):
                try:
                    try:
                        v = h.pop()
                    except IndexError:
                        v = h.build_place(Thing)
                except ms.ManagedQuantityExhausted:
                    exhausted[0] += 1
                    continue
                with lk:
                    peak[0] = max(peak[0], h.count)
                time.sleep(0)
                release(v)

        ts = [threading.Thread(target=worker) for _ in range(8)]
        [t.start() for t in ts]
        [t.join() for t in ts]
        print(f"limited(3) under 8 threads: peak count {peak[0]} (built {h.count}), exhausted {exhausted[0]}, idle {len(h)}")
        q = ManagedSpellQuantity("queue", 1, 0.25, 0, (), ("close",))
        ReleaseManagedSpellSimple._by_type = {Thing: (q,)}
        first = q.build_place(Thing)
        t0 = time.perf_counter()
        try:
            q.build_place(Thing)
            print("queue: FAIL - built past the limit")
        except ms.ManagedQuantityExhausted:
            print(f"queue(1, 0.25s): waits then raises at the timeout ({time.perf_counter() - t0:.2f}s)")
        served: List[object] = []
        t = threading.Thread(target=lambda: served.append(q.build_place(Thing)))
        t.start()
        time.sleep(0.05)
        release(first)
        t.join(1.0)
        print(f"queue: a waiter is served by a release: {served and served[0] is first}, count {q.count}")
    finally:
        gc.enable()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
