"""Capture the executors Melder emits today for normal and override melds (design v2 evidence).

Read-only against the source tree: every compile seam is wrapped (the original cache function is
called unchanged), disk caching is disabled, and each graph runs in a fresh world. Writes emitted
sources plus constructor counts into the output directory given as argv[1].
Run from the repository root with PYTHONPATH=src:. on CPython 3.14.
"""
import importlib
import json
import sys
from pathlib import Path
from types import CodeType
from typing import Any, Callable, Dict, List
from unittest.mock import patch

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.spell_compiler.executor_code_cache import get_or_compile_executor_code
from melder.aether.spellbook.spell_compiler.executor_factory_cache import get_or_build_executor_factory
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import configure_frame_posture_for_spellbook_configuration

SEAM_MODULES = (
    "melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation.spell_codegen_creation_cache",
    "melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.creation_runtime_door_compiler",
    "melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_no_overrides_codegen_creation_compiler",
    "melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_overrides_codegen_creation_compiler",
    "melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.compilers.many_only_no_overrides_codegen_creation_compiler",
    "melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.compilers.many_only_overrides_codegen_creation_compiler",
    "melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.compilers.solo_no_overrides_codegen_creation_compiler",
    "melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.compilers.solo_overrides_codegen_creation_compiler",
)

FACTORY_SEAM_MODULES = (
    "melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_manifest_no_overrides_compiler",
    "melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_manifest_overrides_runtime",
)

COUNTING = """
def hit(name):
    COUNTS[name] = COUNTS.get(name, 0) + 1
"""

GRAPHS: Dict[str, Dict[str, Any]] = {
    "many_shallow": {
        "source": COUNTING + """
class A:
    def __init__(self):
        hit('A')
class B:
    def __init__(self):
        hit('B')
class Root:
    def __init__(self, a: A, b: B):
        hit('Root'); self.a = a; self.b = b
""",
        "bindings": (("A", "many"), ("B", "many"), ("Root", "many")),
        "calls": (("normal", None), ("override_a", {"a": "SUPPLIED"})),
    },
    "gen_mixed": {
        "source": COUNTING + """
class X:
    def __init__(self):
        hit('X')
class S:
    def __init__(self, x: X):
        hit('S'); self.x = x
class A:
    def __init__(self):
        hit('A')
class Root:
    def __init__(self, a: A, s: S):
        hit('Root'); self.a = a; self.s = s
""",
        "bindings": (("X", "many"), ("S", "unique_per_conduit"), ("A", "many"), ("Root", "many")),
        "calls": (("normal_cold", None), ("normal_warm", None), ("override_s", {"s": "SUPPLIED"}),
                  ("override_a", {"a": "SUPPLIED"})),
    },
    "gen_diamond": {
        "source": COUNTING + """
class S:
    def __init__(self):
        hit('S')
class L:
    def __init__(self, s: S):
        hit('L'); self.s = s
class R:
    def __init__(self, s: S):
        hit('R'); self.s = s
class Root:
    def __init__(self, l: L, r: R):
        hit('Root'); self.l = l; self.r = r
""",
        "bindings": (("S", "unique_per_conduit"), ("L", "many"), ("R", "many"), ("Root", "many")),
        "calls": (("normal", None), ("override_l", {"l": "SUPPLIED"}), ("override_path_l_s", {"l>s": "SUPPLIED"})),
    },
}


class World:
    """One isolated Book/Conduit pair with disk caching disabled."""

    def __init__(self) -> None:
        Aether._reset_singleton_for_tests()
        Spellbook._aether = Aether()
        Conduit._aether = Spellbook._aether
        configuration = SpellbookConfiguration().with_defaults()
        configuration.with_phase_scheduler_workers(1)
        posture = configure_frame_posture_for_spellbook_configuration(configuration, dynamic=False)
        posture.with_system_caching_enabled(False)
        self.book = Spellbook(configuration=configuration)
        self.conduit = None

    def cleanup(self) -> None:
        try:
            if self.conduit is not None:
                self.conduit.permanent_cleanup()
        finally:
            self.book.cleanup()
            Aether._reset_singleton_for_tests()


class Capture:
    """Record every compile request under the current stage label."""

    def __init__(self) -> None:
        self.stage = "setup"
        self.sources: List[Dict[str, str]] = []

    def compile(self, *, source: str, source_name: str) -> CodeType:
        self.sources.append({"stage": self.stage, "source_name": source_name, "source": source})
        return get_or_compile_executor_code(source=source, source_name=source_name)

    def factory(self, *, factory_source: str, source_name: str, static_namespace: Dict[str, Any]) -> Any:
        self.sources.append({"stage": self.stage, "source_name": source_name, "source": factory_source})
        return get_or_build_executor_factory(
            factory_source=factory_source, source_name=source_name, static_namespace=static_namespace)


def run_graph(capture: Capture, name: str, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    namespace: Dict[str, Any] = {"__name__": f"capture_{name}", "COUNTS": {}}
    exec(compile(spec["source"], f"capture_{name}", "exec"), namespace)
    world = World()
    rows: List[Dict[str, Any]] = []
    try:
        for class_name, existence in spec["bindings"]:
            world.book.bind(spell=namespace[class_name], existence=existence)
        capture.stage = f"{name}_conjure"
        world.conduit = world.book.conjure()
        for label, override in spec["calls"]:
            capture.stage = f"{name}_{label}"
            namespace["COUNTS"].clear()
            payload = None if override is None else {key: object() for key in override}
            try:
                if payload is None:
                    world.conduit.meld(namespace["Root"])
                else:
                    world.conduit.meld(namespace["Root"], override=payload)
                rows.append({"stage": capture.stage, "constructors": dict(namespace["COUNTS"])})
            except Exception as error:
                rows.append({"stage": capture.stage, "error": f"{type(error).__name__}: {str(error)[:300]}"})
    finally:
        world.cleanup()
    return rows


def main(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    capture = Capture()
    patches = []
    for module_name in SEAM_MODULES:
        module = importlib.import_module(module_name)
        if hasattr(module, "get_or_compile_executor_code"):
            patches.append(patch.object(module, "get_or_compile_executor_code", capture.compile))
    for module_name in FACTORY_SEAM_MODULES:
        module = importlib.import_module(module_name)
        patches.append(patch.object(module, "get_or_build_executor_factory", capture.factory))
    cases: List[Dict[str, Any]] = []
    for active in patches:
        active.start()
    try:
        for name, spec in GRAPHS.items():
            cases.extend(run_graph(capture, name, spec))
    finally:
        for active in patches:
            active.stop()
    index = []
    for number, row in enumerate(capture.sources):
        filename = f"{number:03d}_{row['stage']}.py"
        (out / filename).write_text(row["source"] + "\n", encoding="utf-8")
        index.append({"file": filename, "stage": row["stage"], "source_name": row["source_name"],
                      "lines": row["source"].count("\n") + 1})
    report = {"python": sys.version, "gil_enabled": sys._is_gil_enabled(), "cases": cases, "sources": index}
    (out / "capture.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"cases": cases, "sources": index}, indent=1))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
