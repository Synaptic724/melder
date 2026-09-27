import sys, traceback
sys.path.insert(0, "/home/claude/work/m2/src"); sys.path.insert(0, "/home/claude/work/probes_inspect")
import probe_user_mod as um
from melder.aether.aether import Aether
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
Aether._reset_singleton_for_tests(); a = Aether(); Spellbook._aether = a; Conduit._aether = a
book = Spellbook(aetheric_frame="t")
book.bind(spell=um.Engine, existence=Existence.unique, permissions="create")
book.bind(spell=um.Car, existence=Existence.many, permissions="create")
c = book.conjure(name="t", dynamic=True)
c.meld(spell=um.Car)
book.bind(spell=um.Garage, existence=Existence.many, permissions="create")
try:
    c.meld(spell=um.Garage)
except Exception as exc:
    print(type(exc).__name__, [n for n in dir(exc) if not n.startswith("__")][:20])
    inner = getattr(exc, "errors", None) or getattr(exc, "exceptions", None)
    print("inner:", type(inner), (inner if not isinstance(inner, (list, tuple)) else len(inner)))
    for e in (inner if isinstance(inner, (list, tuple)) else []):
        err = e if isinstance(e, BaseException) else getattr(e, "error", None) or getattr(e, "exception", None) or e
        print(repr(err)[:200])
        if isinstance(err, BaseException):
            for f in traceback.extract_tb(err.__traceback__)[-14:]:
                print("   ", f.filename.split("/src/")[-1], f.lineno, f.name)
