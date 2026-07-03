"""
Experiment: how do SYNTHETIC (in-memory, registry-served) modules interact with
EXTERNAL libraries (stdlib + site-packages)?

Question answered empirically:
  When a synthetic module's source imports an external library, does OUR synthetic
  system have to MANAGE that library, or does it resolve for free through the
  standard finders sitting BEHIND our front-of-meta_path finder? And what must a
  crystal TRACK for persistence/restore?

Self-contained, pure-stdlib mirror of src/melder/crystallizer/synthetic_module.py:
  - class-level registry of live module objects
  - finder at FRONT of sys.meta_path (returns None for names it does not own)
  - loader.create_module returns the PRE-EXISTING registered object
  - publish-into-sys.modules BEFORE exec

Site-package scenarios auto-detect an installed third-party lib. If you pass one
that is not installed, the probe says so and falls back to auto-detect; if your
env has NO third-party packages, those scenarios SKIP (they do not FAIL).

Run:
    python tests/experimentation/synthetic_module_external_library_probe.py [pkg]
"""
import ast
import importlib
import importlib.abc
import importlib.util
import sys
from types import ModuleType
from typing import Dict, List, Optional, Tuple

_REGISTRY: Dict[str, "SynthModule"] = {}


class SynthModule(ModuleType):
    def __init__(self, name: str, source: str) -> None:
        super().__init__(name)
        self._synth_source = source
        self.__file__ = "<synthetic:{0}>".format(name)
        self.__package__ = name.rpartition(".")[0]
        self.__loader__ = None
        self.__spec__ = None


class _SynthLoader(importlib.abc.Loader):
    def create_module(self, spec):
        m = _REGISTRY.get(spec.name)
        if m is None:
            raise ImportError("no synthetic module '{0}'".format(spec.name))
        return m

    def exec_module(self, module):
        exec(module._synth_source, module.__dict__, module.__dict__)


_LOADER = _SynthLoader()


class _SynthFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        m = _REGISTRY.get(fullname)
        if m is None:
            return None  # not ours -> fall through to the standard finders
        spec = importlib.util.spec_from_loader(fullname, _LOADER)
        spec.origin = m.__file__
        return spec


_FINDER = _SynthFinder()


def install():
    if _FINDER not in sys.meta_path:
        sys.meta_path.insert(0, _FINDER)


def remove():
    if _FINDER in sys.meta_path:
        sys.meta_path.remove(_FINDER)


def materialize(name: str, source: str) -> SynthModule:
    m = SynthModule(name, source)
    _REGISTRY[name] = m
    sys.modules[name] = m          # publish BEFORE exec
    exec(m._synth_source, m.__dict__, m.__dict__)
    return m


def _forget(*names: str) -> None:
    for n in names:
        sys.modules.pop(n, None)
        _REGISTRY.pop(n, None)


def is_installed_site_pkg(name: Optional[str]) -> bool:
    if not name:
        return False
    try:
        spec = importlib.util.find_spec(name)
    except Exception:
        return False
    origin = (spec.origin or "") if spec else ""
    return bool(spec) and ("site-packages" in origin or "dist-packages" in origin)


def classify_import(name: str) -> str:
    if name in _REGISTRY:
        return "synthetic"
    try:
        spec = importlib.util.find_spec(name)
    except (ImportError, ValueError, ModuleNotFoundError):
        return "missing"
    if spec is None:
        return "missing"
    origin = spec.origin or ""
    if origin in ("built-in", "frozen") or name in getattr(sys, "stdlib_module_names", frozenset()):
        return "stdlib"
    if "site-packages" in origin or "dist-packages" in origin:
        return "site_package"
    return "other_local"


def extract_top_imports(source: str) -> List[str]:
    tree = ast.parse(source)
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out += [a.name.split(".")[0] for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            out.append(node.module.split(".")[0])
    return out


_CANDIDATES = ("numpy", "requests", "pytest", "yaml", "packaging", "attr",
               "wheel", "setuptools", "pip")


def available_site_packages() -> List[str]:
    return [c for c in _CANDIDATES if is_installed_site_pkg(c)]


def resolve_pkg(arg: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    avail = available_site_packages()
    if arg and is_installed_site_pkg(arg):
        return arg, None
    if arg:
        alt = avail[0] if avail else None
        return alt, "requested '{0}' is NOT installed here; {1}".format(
            arg, "using '{0}'".format(alt) if alt else "no third-party pkg found -> site scenarios SKIP")
    return (avail[0] if avail else None), None


_RESULTS = []


def emit(label, ok, detail):
    _RESULTS.append(ok)
    print("{0} {1} :: {2}".format("OK  " if ok else "FAIL", label, detail), flush=True)


def s_stdlib():
    label = "synthetic imports STDLIB (json) resolves for free + shares the object"
    try:
        install()
        m = materialize("synth_json", "import json\nP=json.dumps({'a':1})\ndef rt(s):\n    return json.loads(s)\n")
        import json as real
        ok = m.P == '{"a": 1}' and m.rt(m.P) == {"a": 1} and m.json is real and sys.modules["json"] is real
        emit(label, ok, "same json object as a normal import: {0}".format(m.json is real))
    except Exception as e:
        emit(label, False, "{0}: {1}".format(type(e).__name__, e))
    finally:
        _forget("synth_json")


def s_site(pkg):
    label = "synthetic imports SITE-PACKAGE ({0})".format(pkg or "n/a")
    if not pkg:
        emit(label, True, "SKIP: no third-party site-package installed in this env")
        return
    try:
        install()
        m = materialize("synth_ext", "import {0} as x\nN=x.__name__\n".format(pkg))
        real = importlib.import_module(pkg)
        ok = m.N == pkg and m.x is real and sys.modules[pkg] is real
        emit(label, ok, "shared object (not duplicated): {0}".format(m.x is real))
    except Exception as e:
        emit(label, False, "{0}: {1}".format(type(e).__name__, e))
    finally:
        _forget("synth_ext")


def s_classify(pkg):
    label = "AST dep classification (what the crystal records)"
    try:
        install()
        materialize("dep_helper", "H=1\n")
        extra = pkg or ""
        src = "import json\nimport dep_helper\nimport totally_missing_xyz\n" + ("import {0}\n".format(pkg) if pkg else "")
        cls = {n: classify_import(n) for n in extract_top_imports(src)}
        ok = (cls.get("dep_helper") == "synthetic" and cls.get("json") == "stdlib"
              and cls.get("totally_missing_xyz") == "missing")
        if pkg:
            ok = ok and cls.get(pkg) == "site_package"
        emit(label, ok, str(cls))
    except Exception as e:
        emit(label, False, "{0}: {1}".format(type(e).__name__, e))
    finally:
        _forget("dep_helper")


def s_missing():
    label = "synthetic imports a MISSING external -> error at ACTIVATE (validate-before-restore)"
    try:
        install()
        raised = False
        try:
            materialize("synth_bad", "import definitely_not_installed_pkg_123\nX=1\n")
        except ModuleNotFoundError:
            raised = True
        left = "synth_bad" in sys.modules  # publish-before-exec leaves a half-published module on failure
        emit(label, raised, "raised ModuleNotFoundError (half-published module still in sys.modules: {0}) => validate env / rollback on exec-failure".format(left))
    except Exception as e:
        emit(label, False, "{0}: {1}".format(type(e).__name__, e))
    finally:
        _forget("synth_bad")


def s_unseed(pkg):
    label = "unseed of a synthetic does NOT unload the external lib it used"
    tgt = pkg or "json"  # falls back to stdlib so this always exercises something real
    try:
        install()
        materialize("synth_tmp", "import {0} as x\nV=x.__name__\n".format(tgt))
        before = tgt in sys.modules
        _forget("synth_tmp")
        after = tgt in sys.modules
        ours_gone = "synth_tmp" not in sys.modules
        emit(label, before and after and ours_gone,
             "external '{0}' still loaded after our unseed: {1}; our module removed: {2}".format(tgt, after, ours_gone))
    except Exception as e:
        emit(label, False, "{0}: {1}".format(type(e).__name__, e))


def main():
    print("START_SYNTH_EXTERNAL_LIB_PROBE (python {0})".format(sys.version.split()[0]), flush=True)
    avail = available_site_packages()
    print("installed third-party pkgs detected: {0}".format(avail or "(none)"), flush=True)
    pkg, note = resolve_pkg(sys.argv[1] if len(sys.argv) > 1 else None)
    if note:
        print("NOTE: {0}".format(note), flush=True)
    print("site-package under test: {0}".format(pkg), flush=True)
    s_stdlib()
    s_site(pkg)
    s_classify(pkg)
    s_missing()
    s_unseed(pkg)
    remove()
    print("SUMMARY {0}/{1} green".format(sum(_RESULTS), len(_RESULTS)), flush=True)
    print("DONE_SYNTH_EXTERNAL_LIB_PROBE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
