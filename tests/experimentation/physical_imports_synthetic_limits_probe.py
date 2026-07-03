"""
Experiment: can a PHYSICAL (file-backed) module import a SYNTHETIC (in-memory)
module, and where are the limits?

Self-contained, pure stdlib (no melder import) so it runs on any CPython >= 3.10
AND on the 3.14t build. It mirrors the production synthetic-module mechanism in
`src/melder/crystallizer/synthetic_module.py`:
  - a class-level registry of live module objects
  - a MetaPathFinder installed at the FRONT of sys.meta_path
  - a Loader whose create_module RETURNS THE PRE-EXISTING registered object
  - publish-into-sys.modules BEFORE exec (cycle-safe)
  - __spec__ / __loader__ stamped onto the live module object

Run:
    python tests/experimentation/physical_imports_synthetic_limits_probe.py
"""
import importlib
import importlib.abc
import importlib.util
import inspect
import pickle
import shutil
import sys
import tempfile
from importlib.machinery import ModuleSpec
from pathlib import Path
from types import ModuleType
from typing import Dict, List, Optional, Tuple


# --------------------------------------------------------------------------
# Minimal mirror of the production synthetic-module machinery (pure stdlib).
# --------------------------------------------------------------------------
class SynthModule(ModuleType):
    def __init__(self, name: str, source: str, is_package: bool = False) -> None:
        super().__init__(name)
        self._synth_source = source
        self._is_package = is_package
        self.__file__ = "<synthetic:{0}>".format(name)
        self.__package__ = name if is_package else name.rpartition(".")[0]
        if is_package:
            self.__path__ = [self.__file__]
        self.__loader__ = None
        self.__spec__ = None


_REGISTRY: Dict[str, SynthModule] = {}


class _SynthLoader(importlib.abc.Loader):
    def create_module(self, spec: ModuleSpec) -> ModuleType:
        module = _REGISTRY.get(spec.name)
        if module is None:
            raise ImportError("no synthetic module '{0}'".format(spec.name))
        return module  # hand importlib the PRE-EXISTING registered object

    def exec_module(self, module: ModuleType) -> None:
        _attach_metadata(module)
        exec(module._synth_source, module.__dict__, module.__dict__)

    def get_source(self, fullname: str) -> Optional[str]:
        # importlib.abc.InspectLoader hook. inspect/linecache fall back to this
        # when there is no file on disk -- this is the piece that makes
        # inspect.getsource() and traceback source lines work on synthetics.
        module = _REGISTRY.get(fullname)
        return module._synth_source if module is not None else None


_LOADER = _SynthLoader()


class _SynthFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None) -> Optional[ModuleSpec]:
        module = _REGISTRY.get(fullname)
        if module is None:
            return None
        spec = importlib.util.spec_from_loader(
            fullname, _LOADER, is_package=module._is_package
        )
        spec.origin = module.__file__
        if module._is_package:
            spec.submodule_search_locations = [module.__file__]
        return spec


_FINDER = _SynthFinder()


def _attach_metadata(module: SynthModule) -> None:
    spec = importlib.util.spec_from_loader(
        module.__name__, _LOADER, is_package=module._is_package
    )
    spec.origin = module.__file__
    module.__loader__ = _LOADER
    module.__spec__ = spec


def install_finder() -> None:
    if _FINDER not in sys.meta_path:
        sys.meta_path.insert(0, _FINDER)


def remove_finder() -> None:
    if _FINDER in sys.meta_path:
        sys.meta_path.remove(_FINDER)


def register(name: str, source: str, is_package: bool = False) -> SynthModule:
    module = SynthModule(name, source, is_package=is_package)
    _REGISTRY[name] = module
    return module


def materialize(name: str) -> SynthModule:
    """Eager path: publish into sys.modules BEFORE exec, then exec, then attach parent."""
    module = _REGISTRY[name]
    sys.modules[name] = module
    _attach_metadata(module)
    exec(module._synth_source, module.__dict__, module.__dict__)
    parent = module.__name__.rpartition(".")[0]
    if parent and parent in sys.modules:
        setattr(sys.modules[parent], module.__name__.rpartition(".")[-1], module)
    return module


# --------------------------------------------------------------------------
# Harness
# --------------------------------------------------------------------------
_RESULTS: List[Tuple[str, bool, str]] = []
_TMP: Optional[Path] = None


def _emit(label: str, ok: bool, detail: str) -> None:
    _RESULTS.append((label, ok, detail))
    print("{0} {1} :: {2}".format("OK  " if ok else "FAIL", label, detail), flush=True)


def _write(relpath: str, source: str) -> None:
    p = _TMP / relpath
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(source, encoding="utf-8")
    importlib.invalidate_caches()


def _forget(*names: str) -> None:
    for n in names:
        sys.modules.pop(n, None)
        _REGISTRY.pop(n, None)


def scenario_physical_imports_synthetic() -> None:
    label = "physical_imports_synthetic (via finder, lazy)"
    try:
        register(
            "synlib_thing",
            "def make():\n    return 'from-synthetic'\nVALUE = 'synthetic-value'\n",
        )
        install_finder()  # NOT materialized -> physical import must resolve via the finder
        _write(
            "phys_consumer_a.py",
            "import synlib_thing\nRESULT = synlib_thing.make()\nVALUE = synlib_thing.VALUE\n",
        )
        mod = importlib.import_module("phys_consumer_a")
        ok = mod.RESULT == "from-synthetic" and mod.VALUE == "synthetic-value"
        _emit(label, ok, "physical module got RESULT={0!r} VALUE={1!r}".format(mod.RESULT, mod.VALUE))
    except Exception as exc:
        _emit(label, False, "raised {0}: {1}".format(type(exc).__name__, exc))
    finally:
        _forget("phys_consumer_a", "synlib_thing")


def scenario_physical_package_synthetic_submodule() -> None:
    label = "physical_package imports SYNTHETIC submodule (abs + relative)"
    try:
        _write("mixpkg/__init__.py", "PKG = 'physical-package'\n")
        _write(
            "mixpkg/consumer.py",
            "from mixpkg.helper import H\nABS = H\nfrom . import helper as _h\nREL = _h.H\n",
        )
        importlib.import_module("mixpkg")  # physical package first
        register("mixpkg.helper", "H = 'synthetic-helper'\n")  # synthetic submodule under physical pkg
        materialize("mixpkg.helper")  # attaches to physical parent via setattr
        install_finder()
        mod = importlib.import_module("mixpkg.consumer")
        ok = mod.ABS == "synthetic-helper" and mod.REL == "synthetic-helper"
        _emit(label, ok, "abs={0!r} rel={1!r}".format(mod.ABS, mod.REL))
    except Exception as exc:
        _emit(label, False, "raised {0}: {1}".format(type(exc).__name__, exc))
    finally:
        _forget("mixpkg.consumer", "mixpkg.helper", "mixpkg")


def scenario_sys_modules_precedence() -> None:
    label = "sys.modules precedence (already-loaded physical wins)"
    try:
        _write("dual.py", "ORIGIN = 'physical'\n")
        importlib.import_module("dual")  # physical now cached in sys.modules
        register("dual", "ORIGIN = 'synthetic'\n")  # same name registered synthetically
        install_finder()
        mod = importlib.import_module("dual")  # sys.modules hit -> finder never consulted
        ok = mod.ORIGIN == "physical"
        _emit(label, ok, "same-name import -> ORIGIN={0!r} (sys.modules checked before meta_path)".format(mod.ORIGIN))
    except Exception as exc:
        _emit(label, False, "raised {0}: {1}".format(type(exc).__name__, exc))
    finally:
        _forget("dual")


def scenario_hotswap_eager_vs_lazy() -> None:
    label = "hot-swap: eager keeps OLD, lazy/reload sees NEW"
    try:
        _write("provider.py", "VALUE = 'physical'\n")
        _write("eager_consumer.py", "from provider import VALUE as CAPTURED\n")
        importlib.import_module("provider")
        eager = importlib.import_module("eager_consumer")  # eagerly captured 'physical'
        register("provider", "VALUE = 'synthetic'\n")       # swap in synthetic
        sys.modules.pop("provider", None)                    # evict physical
        install_finder()
        fresh = importlib.import_module("provider")           # lazy -> synthetic
        ok = eager.CAPTURED == "physical" and fresh.VALUE == "synthetic"
        _emit(label, ok, "eager captured={0!r}, fresh lazy import={1!r}".format(eager.CAPTURED, fresh.VALUE))
    except Exception as exc:
        _emit(label, False, "raised {0}: {1}".format(type(exc).__name__, exc))
    finally:
        _forget("provider", "eager_consumer")


def scenario_reload_physical_with_synthetic_dep() -> None:
    label = "reload physical module whose dep is synthetic (re-exec'd v1->v2)"
    try:
        register("syndep", "VALUE = 'v1'\n")
        materialize("syndep")
        install_finder()
        _write("dependent.py", "import syndep\nSEEN = syndep.VALUE\n")
        dep = importlib.import_module("dependent")
        first = dep.SEEN
        live = _REGISTRY["syndep"]           # re-exec the SAME synthetic object with new source
        live._synth_source = "VALUE = 'v2'\n"
        live.__dict__.pop("VALUE", None)
        exec(live._synth_source, live.__dict__, live.__dict__)
        importlib.reload(dep)
        second = dep.SEEN
        ok = first == "v1" and second == "v2"
        _emit(label, ok, "before={0!r} after={1!r}".format(first, second))
    except Exception as exc:
        _emit(label, False, "raised {0}: {1}".format(type(exc).__name__, exc))
    finally:
        _forget("dependent", "syndep")


def scenario_inspect_and_pickle() -> None:
    try:
        register(
            "pmod",
            "class Widget:\n    def __init__(self):\n        self.tag = 'w'\n    def who(self):\n        return 'widget'\n",
        )
        materialize("pmod")
        install_finder()
        widget_cls = sys.modules["pmod"].Widget

        label1 = "inspect.getsource(synthetic class)"
        try:
            src = inspect.getsource(widget_cls)
            _emit(label1, True, "WORKED ({0} chars) via loader.get_source() -> linecache fallback".format(len(src)))
        except Exception as exc:
            _emit(label1, False, "LIMIT: {0}: {1} (no get_source / no linecache entry -> fixable by loader.get_source)".format(type(exc).__name__, exc))

        label2 = "pickle instance of synthetic class (in-process, by qualname)"
        try:
            inst = widget_cls()
            back = pickle.loads(pickle.dumps(inst))
            ok = back.tag == "w" and back.who() == "widget" and back.__class__.__module__ == "pmod"
            _emit(label2, ok, "roundtrip ok; __module__={0!r} (needs finder installed to unpickle)".format(back.__class__.__module__))
        except Exception as exc:
            _emit(label2, False, "{0}: {1}".format(type(exc).__name__, exc))
    finally:
        _forget("pmod")


def main() -> int:
    global _TMP
    _TMP = Path(tempfile.mkdtemp(prefix="phys_synth_probe_"))
    sys.path.insert(0, str(_TMP))
    importlib.invalidate_caches()
    print("START_PHYSICAL_IMPORTS_SYNTHETIC_PROBE (python {0})".format(sys.version.split()[0]), flush=True)
    try:
        scenario_physical_imports_synthetic()
        scenario_physical_package_synthetic_submodule()
        scenario_sys_modules_precedence()
        scenario_hotswap_eager_vs_lazy()
        scenario_reload_physical_with_synthetic_dep()
        scenario_inspect_and_pickle()
        remove_finder()
        if str(_TMP) in sys.path:
            sys.path.remove(str(_TMP))
        shutil.rmtree(_TMP, ignore_errors=True)
    passed = sum(1 for _, ok, _ in _RESULTS if ok)
    print("SUMMARY {0}/{1} scenarios green".format(passed, len(_RESULTS)), flush=True)
    print("DONE_PHYSICAL_IMPORTS_SYNTHETIC_PROBE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
