"""Directional microbenchmarks for four static-strategy candidates (VM 3.14t, GIL off). Not a test."""
import gc, sys, time
from threading import Lock, RLock


def timeit(label, fn, n=300_000, reps=7):
    best = None
    for _ in range(reps):
        gc.disable()
        t0 = time.perf_counter_ns()
        fn(n)
        t1 = time.perf_counter_ns()
        gc.enable()
        per = (t1 - t0) / n
        best = per if best is None else min(best, per)
    print(f"{label:>52}: {best:6.1f} ns")


# S22: RLock vs Lock, uncontended acquire/release
def rlock_loop(n, lock=RLock()):
    for _ in range(n):
        with lock:
            pass

def lock_loop(n, lock=Lock()):
    for _ in range(n):
        with lock:
            pass

def rlock_explicit(n, lock=RLock()):
    acquire = lock.acquire; release = lock.release
    for _ in range(n):
        acquire()
        release()

def lock_explicit(n, lock=Lock()):
    acquire = lock.acquire; release = lock.release
    for _ in range(n):
        acquire()
        release()


# S10: dict.get + None check vs subscript on a hit
class Store:
    __slots__ = ("_creations",)
    def __init__(self):
        self._creations = {"k" * 64: object()}

STORE = Store()
KEY = "k" * 64

def get_hit(n, c=STORE, sid=KEY):
    for _ in range(n):
        v = c._creations.get(sid)
        if v is None:
            raise AssertionError

def subscript_hit(n, c=STORE, sid=KEY):
    for _ in range(n):
        try:
            v = c._creations[sid]
        except KeyError:
            raise AssertionError

def subscript_miss(n, c=STORE):
    missing = "m" * 64
    for _ in range(n):
        try:
            v = c._creations[missing]
        except KeyError:
            v = None


# S40: dict lookup with the identical key object vs an equal, distinct key object
SAME = KEY
DISTINCT = "".join(["k"] * 64)
assert DISTINCT == SAME and DISTINCT is not SAME
D = STORE._creations

def lookup_same(n, d=D, k=SAME):
    for _ in range(n):
        d.get(k)

def lookup_distinct(n, d=D, k=DISTINCT):
    for _ in range(n):
        d.get(k)


# S39: constant as a global (namespace) vs a default argument (LOAD_FAST) vs a closure cell
NS = {"c1": STORE, "sid1": KEY}
SRC_GLOBAL = """
def plan(meld):
    v1 = c1._creations.get(sid1)
    return v1
"""
SRC_DEFAULT = """
def plan(meld, c1=c1, sid1=sid1):
    v1 = c1._creations.get(sid1)
    return v1
"""
SRC_CLOSURE = """
def make(c1, sid1):
    def plan(meld):
        v1 = c1._creations.get(sid1)
        return v1
    return plan
plan = make(c1, sid1)
"""
def compile_plan(src):
    ns = dict(NS)
    exec(compile(src, "<plan>", "exec"), ns)
    return ns["plan"]

P_GLOBAL = compile_plan(SRC_GLOBAL)
P_DEFAULT = compile_plan(SRC_DEFAULT)
P_CLOSURE = compile_plan(SRC_CLOSURE)

def run_plan(plan):
    def loop(n, plan=plan):
        for _ in range(n):
            plan(None)
    return loop


if __name__ == "__main__":
    print(sys.version)
    for _round in range(2):
        timeit("S22 RLock with-statement", rlock_loop)
        timeit("S22 Lock with-statement", lock_loop)
        timeit("S22 RLock explicit acquire/release", rlock_explicit)
        timeit("S22 Lock explicit acquire/release", lock_explicit)
        timeit("S10 dict.get hit + None check", get_hit)
        timeit("S10 subscript hit (try/except)", subscript_hit)
        timeit("S10 subscript MISS (KeyError path)", subscript_miss)
        timeit("S40 dict.get, identical key object", lookup_same)
        timeit("S40 dict.get, equal but distinct key object", lookup_distinct)
        timeit("S39 plan: constants as globals", run_plan(P_GLOBAL))
        timeit("S39 plan: constants as default args", run_plan(P_DEFAULT))
        timeit("S39 plan: constants as closure cells", run_plan(P_CLOSURE))
        print("--")
