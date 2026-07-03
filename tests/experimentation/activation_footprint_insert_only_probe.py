"""
Activation footprint + insert-only deactivate probe (persisted from the 2026-07-03 inline run).
Proves: on deactivate we do NOT remove (insert-only) - a new version goes active via the canonical
alias while the old stays resident + reimportable by callsign; and the FOOTPRINT a SpellCrystal must
document per activation = {callsign, sys.modules key, canonical alias, file}.
Run: python tests/experimentation/activation_footprint_insert_only_probe.py
"""
import hashlib, importlib, importlib.abc, importlib.util, sys
from types import ModuleType
REG = {}; ACTIVE = {}; FOOTPRINT = {}
class SM(ModuleType):
    def __init__(self, n, s, file_path=None):
        super().__init__(n); self._s = s
        self.__file__ = file_path or "<synthetic:%s>" % n; self.__loader__ = None; self.__spec__ = None
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
def activate(canonical, source, file_path=None):
    cs = callsign(canonical, source)
    if cs not in REG:
        m = SM(cs, source, file_path); REG[cs] = m; sys.modules[cs] = m
        exec(compile(m._s, m.__file__, "exec"), m.__dict__, m.__dict__)
        FOOTPRINT[cs] = {"callsign": cs, "sys_modules_key": cs, "canonical_alias": canonical, "file": file_path}
    ACTIVE[canonical] = cs; sys.modules.pop(canonical, None); return cs
R = []
def emit(l, ok, d): R.append(ok); print(("OK   " if ok else "FAIL ") + l + " :: " + d, flush=True)
print("START activation_footprint_insert_only (py %s)" % sys.version.split()[0])
c1 = activate("svc", "VERSION=1\ndef who():\n    return 'v1'\n"); importlib.import_module("svc")
c2 = activate("svc", "VERSION=2\ndef who():\n    return 'v2'\n")
fresh = importlib.import_module("svc")
emit("insert-only deactivate: v2 active, v1 NOT removed (reimportable by callsign)", fresh.who() == 'v2' and c1 in sys.modules and importlib.import_module(c1).who() == 'v1', "canonical->v2; v1 resident+reimportable")
emit("footprint documented per activation {callsign, sys.modules key, alias, file}", all({'callsign', 'sys_modules_key', 'canonical_alias', 'file'} <= set(fp) for fp in FOOTPRINT.values()), "%d versions; both resident=%s" % (len(FOOTPRINT), c1 in sys.modules and c2 in sys.modules))
while FI in sys.meta_path: sys.meta_path.remove(FI)
print("SUMMARY %d/%d green" % (sum(R), len(R))); print("DONE")
