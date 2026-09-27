"""Probe current Melder behavior that the override/caller-input design depends on.

Read-only against the source tree: disk caching is disabled and each case runs in a fresh world.
Records outcomes; asserts nothing. Run from the repository root with PYTHONPATH=src:. on CPython 3.14.
"""
import json
import sys
import time
from typing import Any, Callable, Dict

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import configure_frame_posture_for_spellbook_configuration


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

    def conjure(self) -> Conduit:
        self.conduit = self.book.conjure()
        return self.conduit

    def cleanup(self) -> None:
        try:
            if self.conduit is not None:
                self.conduit.permanent_cleanup()
        finally:
            self.book.cleanup()
            Aether._reset_singleton_for_tests()


def classes(source: str) -> Dict[str, Any]:
    """Define test classes from source so annotations resolve in a real module namespace."""
    namespace: Dict[str, Any] = {"__name__": "probe_models", "COUNTS": {}}
    exec(compile(source, "probe_models", "exec"), namespace)
    return namespace


def guard(call: Callable[[], Any]) -> Dict[str, Any]:
    try:
        return {"status": "ok", "value": call()}
    except Exception as error:
        return {"status": "error", "type": type(error).__name__, "message": str(error)[:300]}


COUNTING = """
def hit(name):
    COUNTS[name] = COUNTS.get(name, 0) + 1
"""


def case_ordinary_reuse_waste() -> Dict[str, Any]:
    ns = classes(COUNTING + """
class Leaf:
    def __init__(self):
        hit('Leaf')
class Middle:
    def __init__(self, leaf: Leaf):
        hit('Middle'); self.leaf = leaf
class Root:
    def __init__(self, middle: Middle):
        hit('Root'); self.middle = middle
""")
    world = World()
    try:
        world.book.bind(spell=ns["Leaf"], existence="many")
        world.book.bind(spell=ns["Middle"], existence="unique")
        world.book.bind(spell=ns["Root"], existence="many")
        conduit = world.conjure()
        first = conduit.meld(ns["Root"])
        second = conduit.meld(ns["Root"])
        return {"counts": dict(ns["COUNTS"]), "same_middle": first.middle is second.middle}
    finally:
        world.cleanup()


def case_supplied_dependencies() -> Dict[str, Any]:
    ns = classes(COUNTING + """
class A:
    def __init__(self):
        hit('A')
class B:
    def __init__(self):
        hit('B')
class C:
    def __init__(self):
        hit('C')
class Consumer:
    def __init__(self, a: A, b: B, c: C):
        hit('Consumer'); self.a = a; self.b = b; self.c = c
""")
    world = World()
    try:
        for name in ("A", "B", "C", "Consumer"):
            world.book.bind(spell=ns[name], existence="many")
        conduit = world.conjure()
        supplied_a, supplied_b = object(), object()
        result = conduit.meld(ns["Consumer"], override={"a": supplied_a, "b": supplied_b})
        return {
            "counts": dict(ns["COUNTS"]),
            "identity_kept": result.a is supplied_a and result.b is supplied_b,
        }
    finally:
        world.cleanup()


def case_caller_input_unbound() -> Dict[str, Any]:
    ns = classes(COUNTING + """
class Package:
    pass
class Task:
    def __init__(self, work: Package):
        hit('Task'); self.work = work
""")
    world = World()
    try:
        world.book.bind(spell=ns["Task"], existence="many")
        conjured = guard(lambda: world.conjure() is not None)
        return {"conjure": conjured}
    finally:
        world.cleanup()


def case_path_expansion(depth: int) -> Dict[str, Any]:
    lines = [COUNTING, f"class L{depth}:\n    def __init__(self):\n        hit('L{depth}')\n"]
    for level in range(depth - 1, -1, -1):
        lines.append(
            f"class L{level}:\n"
            f"    def __init__(self, left: L{level + 1}, right: L{level + 1}):\n"
            f"        hit('L{level}')\n"
        )
    ns = classes("\n".join(lines))
    world = World()
    try:
        for level in range(depth + 1):
            world.book.bind(spell=ns[f"L{level}"], existence="unique")
        started = time.perf_counter()
        conduit = world.conjure()
        conjure_seconds = time.perf_counter() - started
        root_spell = next(
            spell for spell in world.book._spell_id_pool.values() if spell.spell is ns["L0"]
        )
        blueprint = root_spell._compiler_artifact._root_blueprint_phase5
        socket_refs = len(blueprint.socket_refs) if blueprint is not None else None
        started = time.perf_counter()
        conduit.meld(ns["L0"])
        first_meld_seconds = time.perf_counter() - started
        return {
            "depth": depth,
            "physical_sites": depth + 1,
            "root_socket_refs": socket_refs,
            "conjure_seconds": round(conjure_seconds, 4),
            "first_meld_seconds": round(first_meld_seconds, 4),
            "constructed": sum(ns["COUNTS"].values()),
        }
    finally:
        world.cleanup()


def main() -> None:
    report: Dict[str, Any] = {
        "python": sys.version.split()[0],
        "gil_enabled": sys._is_gil_enabled(),
        "cases": {
            "ordinary_reuse_waste": guard(case_ordinary_reuse_waste),
            "supplied_dependencies": guard(case_supplied_dependencies),
            "caller_input_unbound": guard(case_caller_input_unbound),
        },
    }
    report["cases"]["path_expansion"] = [guard(lambda d=d: case_path_expansion(d)) for d in (4, 8, 10, 12, 14)]
    print(json.dumps(report, indent=1, default=str))


if __name__ == "__main__":
    main()
