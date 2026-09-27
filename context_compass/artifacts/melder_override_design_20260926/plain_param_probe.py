import sys
sys.path.insert(0, ".")
from codegen_capture_v2 import World, COUNTING
src = COUNTING + """
class A:
    def __init__(self):
        hit('A')
class Root:
    def __init__(self, a: A, timeout: int = 5, *, name: str = "x"):
        hit('Root'); self.a = a; self.timeout = timeout; self.name = name
"""
ns = {"__name__": "plainprobe", "COUNTS": {}}
exec(compile(src, "plainprobe", "exec"), ns)
w = World()
try:
    for n in ("A", "Root"):
        w.book.bind(spell=ns[n], existence="many")
    w.conduit = w.book.conjure()
    for payload in ({"timeout": 9}, {"name": "y"}, {"*timeout": 9}, {"**name": "z"}, {"nosuch": 1}, {"a>nosuch": 1}):
        try:
            r = w.conduit.meld(ns["Root"], override=payload)
            print(payload, "ok", r.timeout, r.name)
        except Exception as e:
            print(payload, "ERR", type(e).__name__, str(e)[:200])
    sp = w.book._spells if hasattr(w.book, "_spells") else None
finally:
    w.cleanup()
