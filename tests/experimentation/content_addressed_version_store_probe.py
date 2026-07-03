"""
Content-addressed version store + callsign probe (persisted from the 2026-07-03 inline runs).
Proves: versions COEXIST by content-SHA callsign (no collision); identical content DEDUPS;
canonical `import`/`from` stay normal (the SHA is invisible in code); repoint switches the active
version WITHOUT removing either; version-pin by callsign (MR checkout). Callsign is identifier-safe
(`<canonical>__<hex>`, not `@` which breaks the import statement).
Run: python tests/experimentation/content_addressed_version_store_probe.py
"""
import hashlib, importlib, importlib.abc, importlib.util, sys
from types import ModuleType

REG = {}; ACTIVE = {}
class SM(ModuleType):
    def __init__(self, n, s):
        super().__init__(n); self._s = s
        self.__file__ = "<synthetic:%s>" % n; self.__loader__ = None; self.__spec__ = None
class L(importlib.abc.Loader):
    def create_module(self, spec): return REG[spec.name if spec.name in REG else ACTIVE.get(spec.name)]
    def exec_module(self, m): exec(compile(m._s, m.__file__, "exec"), m.__dict__, m.__dict__)
LO = L()
class F(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        m = REG.get(ACTIVE.get(fullname, fullname))
        if m is None: return None
        sp = importlib.util.spec_from_loader(fullname, LO); sp.origin = m.__file__; return sp
FI = F(); sys.meta_path.insert(0, FI)
def callsign(c, s): return "%s__%s" % (c, hashlib.sha256(s.encode()).hexdigest()[:12])
def store(c, s, active=True):
    n = callsign(c, s)
    if n not in REG:
        m = SM(n, s); REG[n] = m; sys.modules[n] = m; exec(compile(m._s, m.__file__, "exec"), m.__dict__, m.__dict__)
    if active: ACTIVE[c] = n
    return n
def repoint(c, n): ACTIVE[c] = n; sys.modules.pop(c, None)
R = []
def emit(l, ok, d): R.append(ok); print(("OK   " if ok else "FAIL ") + l + " :: " + d, flush=True)
print("START content_addressed_version_store (py %s)" % sys.version.split()[0])
v1 = store("svc", "MARK='v1'\ndef a():\n    return 'a-v1'\n")
v2 = store("svc", "MARK='v2'\ndef a():\n    return 'a-v2'\n", active=False)
emit("two versions coexist by callsign (no collision)", v1 != v2 and v1 in sys.modules and v2 in sys.modules, "v1..%s v2..%s" % (v1[-6:], v2[-6:]))
v2b = store("svc", "MARK='v2'\ndef a():\n    return 'a-v2'\n", active=False)
emit("identical content dedups to same callsign+object", v2b == v2 and sys.modules[v2b] is sys.modules[v2], "dedup=%s" % (v2b == v2))
ns = {}; exec(compile("import svc\nm=svc.MARK\n", "<user>", "exec"), ns, ns)
emit("plain `import svc` works (no SHA in code)", ns["m"] == "v1", "svc.MARK=%r" % ns["m"])
ns2 = {}; exec(compile("from svc import a\nr=a()\n", "<user>", "exec"), ns2, ns2)
emit("plain `from svc import a` works", ns2["r"] == "a-v1", "a()=%r" % ns2["r"])
repoint("svc", v2)
ns3 = {}; exec(compile("import svc\nfrom svc import a\nm=svc.MARK\nr=a()\n", "<user>", "exec"), ns3, ns3)
emit("repoint switches version WITHOUT removing either", ns3["m"] == "v2" and ns3["r"] == "a-v2" and v1 in sys.modules and v2 in sys.modules, "now v2; both resident=%s" % (v1 in sys.modules and v2 in sys.modules))
nsp = {}; exec(compile("import %s as pinned\nx=pinned.MARK\n" % v1, "<mr_checkout>", "exec"), nsp, nsp)
emit("version-pin by callsign (literal import + importlib string)", nsp["x"] == "v1" and importlib.import_module(v2).MARK == "v2", "pinned v1=%r" % nsp["x"])
while FI in sys.meta_path: sys.meta_path.remove(FI)
print("SUMMARY %d/%d green" % (sum(R), len(R))); print("DONE")
