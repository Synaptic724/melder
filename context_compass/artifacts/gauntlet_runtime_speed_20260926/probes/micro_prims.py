"""melder_2 VM microbench: primitive costs on a worker thread, objects created on the main thread (3.14t)."""
import collections, statistics, threading, time
class L(threading.local):
    def __init__(self): self.stack = []
class O:
    __slots__ = ("a", "lock", "loc", "d", "dq", "b")
    def __init__(self):
        self.a = 1; self.lock = threading.RLock(); self.loc = L(); self.d = {}; self.dq = collections.deque(); self.b = None
    def m(self): return None
    def m_lock(self):
        with self.lock:
            return None
    def m_loc(self): return self.loc.stack
o = O()
def f(): return None
N = 200000
def bench(name, fn):
    s = []
    for _ in range(5):
        t0 = time.perf_counter_ns(); fn(); s.append((time.perf_counter_ns() - t0) / N)
    out.append((name, statistics.median(s)))
def loop_empty():
    for _ in range(N): pass
def loop_call():
    for _ in range(N): f()
def loop_meth():
    for _ in range(N): o.m()
def loop_lock():
    lk = o.lock
    for _ in range(N):
        with lk: pass
def loop_mlock():
    for _ in range(N): o.m_lock()
def loop_local():
    for _ in range(N): o.loc.stack
def loop_dict():
    d = o.d
    for i in range(N):
        d["k"] = o; d.pop("k", None)
def loop_deque():
    dq = o.dq
    for _ in range(N):
        dq.append(o); dq.pop()
def loop_attrstore():
    for _ in range(N):
        o.b = o; o.b = None
out = []
def body():
    for name, fn in [("empty loop", loop_empty), ("f()", loop_call), ("o.m()", loop_meth), ("with rlock", loop_lock),
                     ("o.m_lock()", loop_mlock), ("tlocal.attr", loop_local), ("dict set+pop", loop_dict),
                     ("deque append+pop", loop_deque), ("2x slot store", loop_attrstore)]:
        bench(name, fn)
t = threading.Thread(target=body); t.start(); t.join()
base = out[0][1]
for name, v in out:
    print(f"{name:18s} {v:6.1f} ns/iter  (net {v - base:5.1f})")
