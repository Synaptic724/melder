"""
Experiment: bringing OWNED PHYSICAL modules under OUR loader, and the
physical <-> synthetic dependency relationship.

Question: for a physical source WE OWN (the project's own .py, NOT a site-package),
do we serve its in-memory ModuleType through OUR loader/registry (so we own its
lifecycle + custody), and how does it import / depend on synthetic modules?

Distinction proven:
  owned physical + synthetic  -> served by OUR loader   (world-internal graph)
  site-package (numpy/pytest) -> served by importlib     (world-external)

A "managed module" is our ModuleType; it can be codegen-backed (__file__ =
"<synthetic:...>") OR physical-backed (__file__ = the real path). Physical-backed
compiles with the real filename, so inspect/tracebacks work for free.

Run:
    python tests/experimentation/owned_physical_synthetic_relationship_probe.py
"""
import importlib
import importlib.abc
import importlib.util
import inspect
import os
import sys
import tempfile
from types import ModuleType
from typing import Dict, List, Optional

_REG: Dict[str, "Managed"] = {}


def _pick_site_pkg() -> Optional[str]:
    for c in ("numpy", "requests", "pytest", "yaml", "packaging", "setuptools", "pip"):
        try:
            s = importlib.util.find_spec(c)
        except Exception:
            s = None
        if s and s.origin and ("site-packages" in s.origin or "dist-packages" in s.origin):
            return c
    return None


class Managed(ModuleType):
    def __init__(self, name, source, authority, file_path=None):
        super().__init__(name)
        self._src = source
        self._authority = authority            # 'codegen' | 'physical'
        self.__file__ = file_path if file_path else "<synthetic:%s>" % name
        self.__loader__ = None
        self.__spec__ = None


def _exec_into(m):
    exec(compile(m._src, m.__file__, "exec"), m.__dict__, m.__dict__)


class OurLoader(importlib.abc.Loader):
    def create_module(self, spec):
        return _REG[spec.name]                 # pre-existing world object
    def exec_module(self, module):
        _exec_into(module)
    def get_source(self, fullname):
        m = _REG.get(fullname)
        return m._src if m else None


LO = OurLoader()


class OurFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path=None, target=None):
        m = _REG.get(name)
        if m is None:
            return None                        # decline -> importlib owns it
        sp = importlib.util.spec_from_loader(name, LO)
        sp.origin = m.__file__
        return sp


FI = OurFinder()


def take(name, source, authority, file_path=None):
    """Register + publish + exec a module THROUGH OUR loader (we own it)."""
    m = Managed(name, source, authority, file_path)
    _REG[name] = m
    sys.modules[name] = m                       # publish before exec (our world claims the name)
    m.__loader__ = LO
    _exec_into(m)
    return m


def take_physical_file(name, path):
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()
    return take(name, src, "physical", file_path=path)


_R = []
def emit(label, ok, detail):
    _R.append(ok)
    print("%s %s :: %s" % ("OK  " if ok else "FAIL", label, detail), flush=True)


def main():
    print("START owned-physical<->synthetic (python %s)" % sys.version.split()[0], flush=True)
    sys.meta_path.insert(0, FI)
    tmp = tempfile.mkdtemp(prefix="owned_phys_")
    sys.path.insert(0, tmp)
    pkg = _pick_site_pkg()
    print("site-package available for the external-edge test: %s" % pkg, flush=True)

    # a synthetic (codegen-born) dependency
    take("synth_dep", "def greet():\n    return 'from-synthetic'\nSVALUE = 42\n", "codegen")

    # an OWNED PHYSICAL file whose source imports the synthetic dep (+ a site-package if present)
    phys = os.path.join(tmp, "owned_phys.py")
    body = ["import synth_dep", "OWNED = 'from-physical'", "USES_SYNTH = synth_dep.greet()"]
    if pkg:
        body += ["import %s as _ext" % pkg, "USES_EXT = _ext.__name__"]
    body += ["def combined():", "    return OWNED + '+' + USES_SYNTH"]
    with open(phys, "w", encoding="utf-8") as f:
        f.write("\n".join(body) + "\n")

    m = None
    try:
        m = take_physical_file("owned_phys", phys)
        emit("owned physical served by OUR loader (not importlib SourceFileLoader)",
             sys.modules["owned_phys"] is m and isinstance(m.__loader__, OurLoader)
             and m.__file__ == phys and m._authority == "physical",
             "loader=%s authority=%s file=%s" % (type(m.__loader__).__name__, m._authority, os.path.basename(m.__file__)))
    except Exception as e:
        emit("owned physical served by OUR loader", False, "%s: %s" % (type(e).__name__, e))

    if m is not None:
        emit("owned-physical -> imports SYNTHETIC dep (world-internal, our finder resolved it)",
             m.USES_SYNTH == "from-synthetic" and m.synth_dep is sys.modules["synth_dep"],
             "USES_SYNTH=%r; shared synth object=%s" % (m.USES_SYNTH, m.synth_dep is sys.modules["synth_dep"]))

        if pkg:
            ext = sys.modules.get(pkg)
            emit("owned-physical -> imports SITE-PACKAGE (world-external, importlib served it)",
                 getattr(m, "USES_EXT", None) == pkg and ext is not None and not isinstance(ext.__loader__, OurLoader),
                 "USES_EXT=%r; %s loader=%s" % (getattr(m, "USES_EXT", None), pkg, type(ext.__loader__).__name__))
        else:
            emit("owned-physical -> imports SITE-PACKAGE (world-external, importlib served it)", True, "SKIP: no site-package in env")

        try:
            take("synth_consumer", "import owned_phys\nGOT = owned_phys.combined()\n", "codegen")
            c = sys.modules["synth_consumer"]
            emit("synthetic -> imports OWNED-PHYSICAL (reverse edge, our finder)",
                 c.GOT == "from-physical+from-synthetic" and c.owned_phys is m, "GOT=%r" % c.GOT)
        except Exception as e:
            emit("synthetic -> imports OWNED-PHYSICAL", False, "%s: %s" % (type(e).__name__, e))

        try:
            src = inspect.getsource(m.combined)
            emit("inspect.getsource works on the physical-backed managed module (real __file__)",
                 "return OWNED" in src, "%d chars read straight from the real file" % len(src))
        except Exception as e:
            emit("inspect.getsource on physical-backed managed module", False, "%s: %s" % (type(e).__name__, e))

    names = [n for n in ("synth_dep", "owned_phys", "synth_consumer") if n in sys.modules]
    ours = [n for n in names if isinstance(sys.modules[n].__loader__, OurLoader)]
    ext = sys.modules.get(pkg) if pkg else None
    ext_ours = ext is not None and isinstance(ext.__loader__, OurLoader)
    emit("ownership map: our world-internal graph vs importlib externals",
         len(ours) == len(names) and not ext_ours,
         "OUR loader owns %s ; %s ours=%s" % (ours, pkg, ext_ours))

    sys.meta_path.remove(FI)
    print("SUMMARY %d/%d green" % (sum(_R), len(_R)), flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
