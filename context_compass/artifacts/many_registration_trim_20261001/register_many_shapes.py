"""Microbenchmark of candidate register_many shapes (VM, directional). Not a test."""
import gc, sys, time
from threading import RLock


class ManyDisposalBucket:
    __slots__ = ("entries", "methods")

    def __init__(self, entries, methods):
        self.entries = entries
        self.methods = methods


class Store:
    __slots__ = ("_lock", "_cleaned", "_creations", "_disposable_creations")

    def __init__(self):
        self._lock = RLock()
        self._cleaned = False
        self._creations = {}
        self._disposable_creations = {}

    # today's shape
    def add_many_creations(self, key, item, *, has_disposal_methods=False, disposal_methods=None):
        with self._lock:
            if not self._cleaned:
                self._append_many_locked(key, item, has_disposal_methods=has_disposal_methods, disposal_methods=disposal_methods)
                return
        raise RuntimeError("cleaned")

    def _append_many_locked(self, key, item, *, has_disposal_methods, disposal_methods):
        live_value = self._creations.get(key)
        if live_value is None:
            self._creations[key] = []
            live_value = self._creations[key]
        if not isinstance(live_value, list):
            raise ValueError("non-list")
        live_value.append(item)
        if not has_disposal_methods:
            return
        disposable_value = self._disposable_creations.get(key)
        if disposable_value is None:
            self._disposable_creations[key] = []
            disposable_value = self._disposable_creations[key]
        if not isinstance(disposable_value, list):
            raise ValueError("non-list")
        disposable_value.append((item, disposal_methods if disposal_methods is not None else []))

    # candidate A1: no type check on the hot verb
    def register_many_a1(self, key, item, disposal_methods):
        with self._lock:
            if not self._cleaned:
                bucket = self._creations.get(key)
                if bucket is None:
                    bucket = []
                    self._creations[key] = bucket
                    self._disposable_creations[key] = ManyDisposalBucket(bucket, disposal_methods)
                bucket.append(item)
                return
        raise RuntimeError("cleaned")

    # candidate A2: keep the list check
    def register_many_a2(self, key, item, disposal_methods):
        with self._lock:
            if not self._cleaned:
                bucket = self._creations.get(key)
                if bucket is None:
                    bucket = []
                    self._creations[key] = bucket
                    self._disposable_creations[key] = ManyDisposalBucket(bucket, disposal_methods)
                elif type(bucket) is not list:
                    raise ValueError("non-list")
                bucket.append(item)
                return
        raise RuntimeError("cleaned")

    # candidate A3: explicit acquire/release instead of `with` (no context-manager frames)
    def register_many_a3(self, key, item, disposal_methods):
        lock = self._lock
        lock.acquire()
        try:
            if not self._cleaned:
                bucket = self._creations.get(key)
                if bucket is None:
                    bucket = []
                    self._creations[key] = bucket
                    self._disposable_creations[key] = ManyDisposalBucket(bucket, disposal_methods)
                bucket.append(item)
                return
        finally:
            lock.release()
        raise RuntimeError("cleaned")


def bench(label, fn, n=200_000, reps=7):
    best = None
    for _ in range(reps):
        store = Store()
        store._creations["sid"] = []
        store._disposable_creations["sid"] = ManyDisposalBucket(store._creations["sid"], ["close"])
        if label == "today":
            store._disposable_creations["sid"] = []
        obj = object()
        dm = ["close"]
        gc.disable()
        t0 = time.perf_counter_ns()
        for _ in range(n):
            fn(store, "sid", obj, dm)
        t1 = time.perf_counter_ns()
        gc.enable()
        per = (t1 - t0) / n
        best = per if best is None else min(best, per)
    print(f"{label:>10}: {best:7.1f} ns/registration (best of {reps})")


if __name__ == "__main__":
    print(sys.version)
    bench("today", lambda s, k, i, d: s.add_many_creations(k, i, has_disposal_methods=True, disposal_methods=d))
    bench("A1", lambda s, k, i, d: s.register_many_a1(k, i, d))
    bench("A2", lambda s, k, i, d: s.register_many_a2(k, i, d))
    bench("A3", lambda s, k, i, d: s.register_many_a3(k, i, d))
    bench("today", lambda s, k, i, d: s.add_many_creations(k, i, has_disposal_methods=True, disposal_methods=d))
    bench("A1", lambda s, k, i, d: s.register_many_a1(k, i, d))
    bench("A2", lambda s, k, i, d: s.register_many_a2(k, i, d))
    bench("A3", lambda s, k, i, d: s.register_many_a3(k, i, d))
