import time, threading, sys
N = 2_000_000
def t(label, fn):
    fn(); s = time.perf_counter_ns()
    fn()
    print(f"{label:40} {(time.perf_counter_ns()-s)/N:6.1f} ns", flush=True)
r = threading.RLock(); r2 = threading.RLock(); l = threading.Lock()
d = {"k": r}
class C:
    __slots__ = ("_g", "_lock", "_cleaned", "_c")
    def __init__(self): self._g = {"k": r}; self._lock = r2; self._cleaned = False; self._c = {}
    def slot_guard(self, k):
        g = self._g.get(k)
        if g is None:
            g = self._g.setdefault(k, threading.RLock())
        return g
    def add_locked(self, k, v):
        with self._lock:
            if not self._cleaned:
                if k in self._c: raise ValueError
                self._c[k] = v
                return
    def add_plain(self, k, v):
        if k in self._c: raise ValueError
        self._c[k] = v
c = C()
def loop_empty():
    for _ in range(N): pass
def loop_rlock():
    for _ in range(N):
        with r: pass
def loop_rlock_reentrant():
    with r:
        for _ in range(N):
            with r: pass
def loop_lock():
    for _ in range(N):
        with l: pass
def loop_slot_guard_call():
    for _ in range(N):
        c.slot_guard("k")
def loop_inline_get():
    g = c._g
    for _ in range(N):
        c._g.get("k")
def loop_add_locked():
    for _ in range(N):
        c._c.clear(); c.add_locked("k", 1)
def loop_add_plain():
    for _ in range(N):
        c._c.clear(); c.add_plain("k", 1)
print(sys.version.split()[0], "gil" if sys._is_gil_enabled() else "nogil")
t("empty loop", loop_empty)
t("with RLock (uncontended, fresh)", loop_rlock)
t("with RLock (re-entrant)", loop_rlock_reentrant)
t("with Lock", loop_lock)
t("slot_guard() method hit", loop_slot_guard_call)
t("inline _g.get()", loop_inline_get)
t("add_creation locked (+clear)", loop_add_locked)
t("add_creation plain (+clear)", loop_add_plain)
