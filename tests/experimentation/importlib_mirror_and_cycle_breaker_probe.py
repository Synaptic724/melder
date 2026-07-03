"""
importlib-mirror + hybrid cycle-breaker probe (persisted from the 2026-07-03 inline run).
Proves: (1) a module that eager-loads at init but has a method built ONLY to break a cycle is
managed correctly because scope-tagging keeps the deferred back-edge OUT of load-order; forcing it
load-time reintroduces the partial-init cycle. (2) Our machinery is importlib PLUGGED-IN: importlib
publishes to sys.modules BEFORE calling our exec_module (it drives cycle-safety), and a synthetic
circular ImportError is byte-identical to a physical one.
Run: python tests/experimentation/importlib_mirror_and_cycle_breaker_probe.py
"""
import ast, importlib, importlib.abc, importlib.util, os, sys, tempfile
from types import ModuleType
REG = {}; _probe = {}
class SM(ModuleType):
    def __init__(self, n, s):
        super().__init__(n); self._s = s
        self.__file__ = "<synthetic:%s>" % n; self.__loader__ = None; self.__spec__ = None
class L(importlib.abc.Loader):
    def create_module(self, spec): return REG[spec.name]
    def exec_module(self, m):
        _probe[m.__name__] = (m.__name__ in sys.modules) and (sys.modules[m.__name__] is m)
        exec(compile(m._s, m.__file__, "exec"), m.__dict__, m.__dict__)
LO = L()
class F(importlib.abc.MetaPathFinder):
    def find_spec(self, n, path=None, target=None):
        m = REG.get(n)
        if m is None: return None
        sp = importlib.util.spec_from_loader(n, LO); sp.origin = m.__file__; return sp
FI = F(); sys.meta_path.insert(0, FI)
def register(n, s): REG[n] = SM(n, s); return REG[n]
def forget(*ns):
    for n in ns: sys.modules.pop(n, None); REG.pop(n, None)
def by_scope(src):
    top, dfr = [], []
    class V(ast.NodeVisitor):
        def __init__(self): self.d = 0
        def visit_FunctionDef(self, n): self.d += 1; self.generic_visit(n); self.d -= 1
        visit_AsyncFunctionDef = visit_FunctionDef
        def visit_Import(self, n): (dfr if self.d else top).extend(a.name.split('.')[0] for a in n.names)
        def visit_ImportFrom(self, n):
            if n.module and n.level == 0: (dfr if self.d else top).append(n.module.split('.')[0])
    V().visit(ast.parse(src)); return top, dfr
R = []
def emit(l, ok, d): R.append(ok); print(("OK   " if ok else "FAIL ") + l + " :: " + d, flush=True)
print("START importlib_mirror_and_cycle_breaker (py %s)" % sys.version.split()[0])
Asrc = "import modB\nX='A'\ndef pull():\n    from modB import VALUE\n    return VALUE\n"
Bsrc = "VALUE='from-B'\ndef GET():\n    from modA import X\n    return X\n"
at, ad = by_scope(Asrc); bt, bd = by_scope(Bsrc)
emit("hybrid: load-order excludes the deferred cycle-breaker", at == ['modB'] and 'modA' not in bt and bd == ['modA'], "A top=%s ; B top=%s def=%s" % (at, bt, bd))
register("modA", Asrc); register("modB", Bsrc); importlib.import_module("modA")
emit("hybrid: both load, cycle-breaker method works", sys.modules["modA"].pull() == "from-B" and sys.modules["modB"].GET() == "A", "A.pull()=%r B.GET()=%r" % (sys.modules["modA"].pull(), sys.modules["modB"].GET()))
forget("modA", "modB")
register("cA", "import cB\nX='A'\n"); register("cB", "from cA import X\nY=X\n")
err = None
try: importlib.import_module("cA")
except ImportError as e: err = str(e)
emit("contrast: back-edge as LOAD-TIME reintroduces the cycle", err is not None and "partially initialized" in err, (err or "none")[:52])
forget("cA", "cB")
_probe.clear(); register("pm", "V=1\n"); importlib.import_module("pm")
emit("importlib publishes to sys.modules BEFORE our exec_module", _probe.get("pm") is True, "published-before-exec=%s" % _probe.get("pm"))
forget("pm")
tmp = tempfile.mkdtemp(); sys.path.insert(0, tmp)
open(os.path.join(tmp, "pA.py"), "w").write("import pB\nX='A'\n"); open(os.path.join(tmp, "pB.py"), "w").write("from pA import X\nY=X\n")
importlib.invalidate_caches()
def cap(mod):
    try: importlib.import_module(mod); return None
    except ImportError as e: return type(e).__name__ + "|" + str(e).split(" from ")[0]
pe = cap("pA"); sys.modules.pop("pA", None); sys.modules.pop("pB", None)
register("sA", "import sB\nX='A'\n"); register("sB", "from sA import X\nY=X\n"); se = cap("sA"); forget("sA", "sB")
emit("synthetic circular ImportError == physical (same class+shape)", pe and se and pe.split("|")[0] == se.split("|")[0] and "cannot import name" in se, "phys=%r synth=%r" % (pe, se))
while FI in sys.meta_path: sys.meta_path.remove(FI)
print("SUMMARY %d/%d green" % (sum(R), len(R))); print("DONE")
