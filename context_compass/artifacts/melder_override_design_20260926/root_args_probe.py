import sys
sys.path.insert(0, ".")
from codegen_capture_v2 import World, COUNTING
src = COUNTING + """
class A:
    def __init__(self):
        hit('A')
class B:
    def __init__(self):
        hit('B')
class Root:
    def __init__(self, a: A, b: B):
        hit('Root'); self.a = a; self.b = b
"""
for existence_root in ("many",):
    ns = {"__name__": "argsprobe", "COUNTS": {}}
    exec(compile(src, "argsprobe", "exec"), ns)
    w = World()
    try:
        for n in ("A", "B", "Root"):
            w.book.bind(spell=ns[n], existence="many")
        w.conduit = w.book.conjure()
        s = object()
        for payload in ((s,), [s], {"__args__": (s,), "b": s}):
            ns["COUNTS"].clear()
            try:
                r = w.conduit.meld(ns["Root"], override=payload)
                print(type(payload).__name__, "ok a_is_s", r.a is s, "b_is_s", r.b is s, dict(ns["COUNTS"]))
            except Exception as e:
                print(type(payload).__name__, "ERR", type(e).__name__, str(e)[:250])
    finally:
        w.cleanup()
