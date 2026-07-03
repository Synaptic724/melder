"""
Import & Module Lifecycle Management Suite — consolidates the 2026-07-02 session's
inline probes into one runnable regression suite. Mirrors the production
SyntheticModule mechanism: a class-level registry, a finder at the FRONT of
sys.meta_path that returns None for names it does not own, a loader whose
create_module returns the PRE-EXISTING registered object, and publish-before-exec.

Covers: physical->synthetic seed/unseed management (G3), load-time vs deferred
(in-method) imports (G4), `from b import a` inside exec'd code (G5), a physical
method actioning into our synthetic world (G6), circular-dependency cycle-safety
(G7), and the three removal depths (G8).

Companion standalone probes (not duplicated here):
  synthetic_module_external_library_probe.py  (external site-packages; confirmed 3.14t)
  owned_physical_synthetic_relationship_probe.py  (owned physical under our loader)

Run: python tests/experimentation/import_lifecycle_management_suite.py
"""
import ast, importlib, importlib.abc, importlib.util, os, sys, tempfile
from types import ModuleType
from typing import Dict, List

_REG: Dict[str, "Managed"] = {}


class Managed(ModuleType):
    def __init__(self, name, source, file_path=None, is_pkg=False):
        super().__init__(name); self._src = source; self._is_pkg = is_pkg
        self.__file__ = file_path if file_path else "<synthetic:%s>" % name
        if is_pkg: self.__path__ = [self.__file__]
        self.__loader__ = None; self.__spec__ = None


def _exec(m): exec(compile(m._src, m.__file__, "exec"), m.__dict__, m.__dict__)


class OurLoader(importlib.abc.Loader):
    def create_module(self, spec): return _REG[spec.name]
    def exec_module(self, module): _exec(module)
    def get_source(self, fullname):
        m = _REG.get(fullname); return m._src if m else None


LO = OurLoader()


class OurFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path=None, target=None):
        m = _REG.get(name)
        if m is None: return None
        sp = importlib.util.spec_from_loader(name, LO, is_package=m._is_pkg); sp.origin = m.__file__
        if m._is_pkg: sp.submodule_search_locations = [m.__file__]
        return sp


FI = OurFinder()
def install():
    if FI not in sys.meta_path: sys.meta_path.insert(0, FI)
def uninstall():
    while FI in sys.meta_path: sys.meta_path.remove(FI)

def register(name, source, is_pkg=False, file_path=None):
    _REG[name] = Managed(name, source, file_path, is_pkg); return _REG[name]
def publish(name):
    m = _REG[name]; sys.modules[name] = m; m.__loader__ = LO; _exec(m); return m
def materialize(name, source, is_pkg=False, file_path=None):
    register(name, source, is_pkg, file_path); return publish(name)
def unpublish(*names):                 # depth 2: reversible, holders survive
    for n in names: sys.modules.pop(n, None); _REG.pop(n, None)
def cleanup(name):                     # depth 3: destroy the namespace
    m = sys.modules.get(name) or _REG.get(name)
    if m is not None:
        for k in [k for k in list(m.__dict__) if not (k.startswith("__") and k.endswith("__"))]:
            del m.__dict__[k]
    unpublish(name)

_TMP = tempfile.mkdtemp(prefix="ilm_suite_"); sys.path.insert(0, _TMP)
def phys(name, body):
    open(os.path.join(_TMP, name + ".py"), "w", encoding="utf-8").write(body)
    importlib.invalidate_caches()

def imports_by_scope(source):
    top, deferred = [], []
    class V(ast.NodeVisitor):
        def __init__(self): self.d = 0
        def visit_FunctionDef(self, n): self.d += 1; self.generic_visit(n); self.d -= 1
        visit_AsyncFunctionDef = visit_FunctionDef
        def visit_Import(self, n): (deferred if self.d else top).extend(a.name.split('.')[0] for a in n.names)
        def visit_ImportFrom(self, n):
            if n.module and n.level == 0: (deferred if self.d else top).append(n.module.split('.')[0])
    V().visit(ast.parse(source)); return top, deferred

_R: List[bool] = []
def emit(l, ok, d): _R.append(ok); print(("OK   " if ok else "FAIL ") + l + " :: " + d, flush=True)


def g3():
    print("-- G3 physical->synthetic seeding + unseed --")
    phys("g3a", "import g3_synth\nV = g3_synth.ping()\n")
    try:
        importlib.import_module("g3a"); emit("G3 unseeded physical->synthetic", False, "unexpectedly ok")
    except ModuleNotFoundError:
        emit("G3 unseeded physical->synthetic FAILS (seed is a prereq)", True, "ModuleNotFoundError")
    unpublish("g3a")
    materialize("g3_synth", "def ping():\n    return 'svc'\n"); install()
    phys("g3b", "import g3_synth\nV = g3_synth.ping()\n")
    mb = importlib.import_module("g3b")
    emit("G3 seeded-first: importlib-owned physical imports our synthetic",
         mb.V == "svc" and type(mb.__loader__).__name__ == "SourceFileLoader" and isinstance(sys.modules["g3_synth"].__loader__, OurLoader),
         "V=%r phys-loader=%s" % (mb.V, type(mb.__loader__).__name__))
    unpublish("g3b", "g3_synth")
    register("g3_lazy", "TOKEN = 'lz'\n"); install()
    phys("g3c", "import g3_lazy\nT = g3_lazy.TOKEN\n")
    mc = importlib.import_module("g3c")
    emit("G3 registered-only synthetic resolves lazily on physical import", mc.T == "lz" and "g3_lazy" in sys.modules, "T=%r" % mc.T)
    unpublish("g3c", "g3_lazy")


def g4():
    print("-- G4 load-time vs deferred (in-method) imports --")
    top, dfr = imports_by_scope("import json\nfrom top_x import A\ndef work():\n    import lazy_y\n    from numpy import array\n    return 1\n")
    emit("G4 AST splits load-time vs deferred", set(top) == {"json", "top_x"} and set(dfr) == {"lazy_y", "numpy"}, "top=%s deferred=%s" % (sorted(top), sorted(dfr)))
    install()
    m = materialize("g4svc", "def run():\n    import g4dep\n    return g4dep.answer()\n")
    emit("G4 in-method import of ABSENT synthetic still LOADS", "g4dep" not in sys.modules and callable(m.run), "loaded")
    materialize("g4dep", "def answer():\n    return 42\n")
    emit("G4 in-method import resolves at CALL time once seeded", m.run() == 42, "run()=%s" % m.run())
    m2 = materialize("g4svc2", "def run():\n    import g4missing\n    return 1\n")
    try: m2.run(); f = False
    except ModuleNotFoundError: f = True
    emit("G4 missing deferred dep fails at CALL time, not load", callable(m2.run) and f, "call-failed=%s" % f)
    materialize("g4dep2", "def answer():\n    return 'y1'\n")
    m3 = materialize("g4svc3", "def run():\n    import g4dep2\n    return g4dep2.answer()\n")
    first = m3.run(); unpublish("g4dep2")
    try: m3.run(); broke = False
    except ModuleNotFoundError: broke = True
    emit("G4 unseed breaks a later deferred call", first == "y1" and broke, "first=%r broke=%s" % (first, broke))
    unpublish("g4svc", "g4dep", "g4svc2", "g4svc3")


def g5():
    print("-- G5 `from b import a` inside exec'd code --")
    install()
    register("g5b", "class Widget:\n    tag='w'\nCONST=7\n")
    ns = {}; exec(compile("from g5b import Widget, CONST\nobj=Widget()\nval=CONST\n", "<codegen>", "exec"), ns, ns)
    emit("G5 from b import <attr>: resolves+execs lazily into the exec ns", ns["obj"].tag == "w" and ns["val"] == 7, "obj.tag=%r val=%r" % (ns["obj"].tag, ns["val"]))
    register("g5pkg", "P=1\n", is_pkg=True); publish("g5pkg"); register("g5pkg.leaf", "LV='leaf'\n")
    ns2 = {}; exec(compile("from g5pkg import leaf\nlv=leaf.LV\n", "<codegen>", "exec"), ns2, ns2)
    emit("G5 from pkg import <submodule>: triggers synthetic submodule", ns2["lv"] == "leaf", "lv=%r" % ns2["lv"])
    e = None
    try: exec(compile("from g5b import nope\n", "<codegen>", "exec"), {}, {})
    except ImportError as x: e = str(x)
    emit("G5 from b import <missing>: ImportError (contract, not seeding)", e is not None and "nope" in e, (e or "none")[:55])
    e2 = None
    try: exec(compile("from absentmod import x\n", "<codegen>", "exec"), {}, {})
    except ModuleNotFoundError as x: e2 = str(x)
    emit("G5 from <absent module>: ModuleNotFoundError (seed b first)", e2 is not None, e2 or "none")
    g = {"__name__": "bare"}; e3 = None
    try: exec(compile("from . import sib\n", "<codegen>", "exec"), g, g)
    except ImportError: e3 = "ImportError"
    emit("G5 relative `from . import a` in a bare ns FAILS (needs package ctx)", e3 is not None, e3 or "none")
    unpublish("g5b", "g5pkg", "g5pkg.leaf")


def g6():
    print("-- G6 physical METHOD -> our synthetic --")
    install()
    materialize("g6svc", "def greet():\n    return 'hello'\n")
    phys("g6app", "class App:\n    def run(self):\n        from g6svc import greet\n        return greet()\n")
    app_mod = importlib.import_module("g6app"); app = app_mod.App()
    emit("G6 physical method imports+calls our synthetic at call time",
         app.run() == "hello" and type(app_mod.__loader__).__name__ == "SourceFileLoader", "run()=%r" % app.run())
    unpublish("g6svc")
    try: app.run(); broke = False
    except ModuleNotFoundError: broke = True
    emit("G6 unseed breaks the physical method's next call", broke, "broke=%s" % broke)
    materialize("g6svc2", "def greet():\n    return 'v2'\n")
    phys("g6app2", "import g6svc2\nclass App2:\n    def __init__(self):\n        self.cap = g6svc2\n    def run(self):\n        return self.cap.greet()\n")
    app2_mod = importlib.import_module("g6app2"); a2 = app2_mod.App2()
    b = a2.run(); unpublish("g6svc2"); af = a2.run()
    emit("G6 captured reference survives unpublish (depth 2)", b == "v2" and af == "v2", "before=%r after-unseed=%r" % (b, af))


def g7():
    print("-- G7 circular dependency (publish-before-exec) --")
    install()
    register("g7A", "A_BEFORE='ab'\nimport g7B\nA_AFTER='aa'\ndef af():\n    return g7B.bf()+100\n")
    register("g7B", "import g7A\nSEEN=[n for n in ('A_BEFORE','A_AFTER') if hasattr(g7A,n)]\ndef bf():\n    return 1\n")
    importlib.import_module("g7A"); a = sys.modules["g7A"]; b = sys.modules["g7B"]
    emit("G7 circular resolves; B saw PARTIAL A mid-cycle", b.SEEN == ['A_BEFORE'] and a.af() == 101, "SEEN=%r af()=%s" % (b.SEEN, a.af()))
    emit("G7 mutual __dict__ refs exist (cleanup must clear namespace)", a.__dict__.get("g7B") is b and b.__dict__.get("g7A") is a, "mutual=%s" % (a.__dict__.get("g7B") is b))
    unpublish("g7A", "g7B")
    register("g7fA", "import g7fB\nVALUE='v'\n"); register("g7fB", "from g7fA import VALUE\n")
    e = None
    try: importlib.import_module("g7fA")
    except ImportError as x: e = str(x)
    emit("G7 `from A import X` in a cycle fails (A partial)", e is not None and "g7fA" in e, (e or "none")[:55])
    unpublish("g7fA", "g7fB")
    register("g7dA", "import g7dB\nVALUE='v'\ndef use():\n    return g7dB.grab()\n"); register("g7dB", "def grab():\n    from g7dA import VALUE\n    return VALUE\n")
    importlib.import_module("g7dA")
    emit("G7 deferring the back-edge into a method breaks the cycle", sys.modules["g7dA"].use() == "v", "use()=%r" % sys.modules["g7dA"].use())
    unpublish("g7dA", "g7dB")


def g8():
    print("-- G8 removal depth: unpublish vs cleanup --")
    install()
    materialize("g8m", "VALUE='live'\ndef read():\n    return VALUE\n")
    holder = sys.modules["g8m"]; unpublish("g8m")
    emit("G8 unpublish: gone from sys.modules but a holder still works (ghost)",
         holder.read() == "live" and "g8m" not in sys.modules, "holder.read()=%r; in sys.modules=%s" % (holder.read(), "g8m" in sys.modules))
    materialize("g8n", "VALUE='live2'\ndef read():\n    return VALUE\n")
    fn = sys.modules["g8n"].read; cleanup("g8n")
    try: fn(); broke = False
    except NameError: broke = True
    emit("G8 cleanup: namespace cleared so even a captured function breaks", broke, "captured fn() raised NameError=%s" % broke)


def main():
    print("START import_lifecycle_management_suite (py %s)" % sys.version.split()[0])
    for g in (g3, g4, g5, g6, g7, g8):
        g()
    uninstall()
    print("SUMMARY %d/%d green" % (sum(_R), len(_R))); print("DONE")


if __name__ == "__main__":
    main()
