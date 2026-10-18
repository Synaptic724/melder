"""Probe (melder_0, 2026-10-18; STORY-2026-10-18-spell_id_hashes_the_object_code): edges the design docs must state.

D1-D4: decorators and dataclass factories (do they count?). D5-D6: existing objects of third-party types, with and
without Python-visible state (does the prototype separate two of them, and does a repr fallback?). D7-D8: code a
class references but does not hold (a class-level reference to another class, a module-level helper a method calls).
D9: cost of a class whose MRO holds a large third-party base (pygments' PythonLexer). D10: equal-data objects.
Run from this folder:
    PYTHONPATH=<repo>/src PYTHONHASHSEED=1 python -X gil=0 probe_code_digest_design_edges.py
"""
import hashlib
import time

from code_digest_v2 import CodeDigest
from melder.aether.spellbook.spell_compiler.spell_examiner.inspectors.inspector_utility import InspectorUtility

PRELUDE = "import functools, dataclasses\n"


def world(source: str, module: str = "userworld") -> dict:
    """Execute one variant's source in a fresh namespace named like a module."""
    namespace = {"__name__": module}
    exec(PRELUDE + source, namespace)
    return namespace


def report(label: str, expect: str, first: str, second: str) -> None:
    got = "same" if first == second else "different"
    verdict = "ok" if got == expect else "MISMATCH"
    print(f"{label:<62} expect={expect:<9} got={got:<9} {verdict:<8} {first[:12]}/{second[:12]}")


def pair(label: str, expect: str, source_a: str, source_b: str, name: str) -> None:
    report(label, expect, CodeDigest().spell_id(world(source_a)[name]), CodeDigest().spell_id(world(source_b)[name]))


def repr_fallback(target: object) -> str:
    """Today's rule for an existing object: its type and its address-free repr."""
    kind = type(target)
    text = kind.__module__ + "." + kind.__qualname__ + " " + InspectorUtility.stable_repr(target)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def decorator_cases() -> None:
    pair("D1 dataclass default_factory list -> dict", "different",
         "@dataclasses.dataclass\nclass D:\n    items: object = dataclasses.field(default_factory=list)\n",
         "@dataclasses.dataclass\nclass D:\n    items: object = dataclasses.field(default_factory=dict)\n", "D")
    deco_a = ("def deco(fn):\n    @functools.wraps(fn)\n    def wrapper(*a, **k):\n        return fn(*a, **k)\n"
              "    return wrapper\n")
    deco_b = ("def deco(fn):\n    @functools.wraps(fn)\n    def wrapper(*a, **k):\n        return fn(*a, **k) or 0\n"
              "    return wrapper\n")
    body_a = "@deco\ndef job(x):\n    return x + 1\n"
    body_b = "@deco\ndef job(x):\n    return x + 2\n"
    pair("D2 decorator's wrapper body changed, function the same", "different", deco_a + body_a, deco_b + body_a,
         "job")
    pair("D3 decorated function body changed, decorator the same", "different", deco_a + body_a, deco_a + body_b,
         "job")
    pair("D4 the same decorated source executed twice", "same", deco_a + body_a, deco_a + body_a, "job")


def third_party_object_cases() -> None:
    from packaging.version import Version
    report("D5 two packaging Version objects (Python-visible state)", "different",
           CodeDigest().spell_id(Version("1.0")), CodeDigest().spell_id(Version("2.0")))
    from yaml._yaml import Mark
    first, second = Mark("a", 1, 1, 1, None, None), Mark("a", 9, 9, 9, None, None)
    print(f"{'D6 two yaml C Mark objects: has __dict__?':<62} {hasattr(first, '__dict__')}")
    report("D6a prototype: two C objects without Python-visible state", "different",
           CodeDigest().spell_id(first), CodeDigest().spell_id(second))
    report("D6b repr fallback (today's rule) for the same two", "different", repr_fallback(first),
           repr_fallback(second))


def reference_cases() -> None:
    other_a = "class Other:\n    def f(self):\n        return 1\n"
    other_b = "class Other:\n    def f(self):\n        return 2\n"
    holder = "class Holder:\n    strategy = Other\n    def run(self):\n        return self.strategy().f()\n"
    pair("D7 a class-level reference's class body changed (named)", "same", other_a + holder, other_b + holder,
         "Holder")
    helper_a = "def helper(x):\n    return x + 1\n"
    helper_b = "def helper(x):\n    return x + 2\n"
    user = "class User:\n    def run(self, x):\n        return helper(x)\n"
    pair("D8 a module-level helper a method calls changed (named)", "same", helper_a + user, helper_b + user, "User")


def cost_and_data_cases() -> None:
    from pygments.lexers.python import PythonLexer
    space = world("class MyLexer(Base):\n    name = 'mine'\n", "userworld") if False else None
    namespace = {"__name__": "userworld", "Base": PythonLexer}
    exec("class MyLexer(Base):\n    name = 'mine'\n", namespace)
    lexer = namespace["MyLexer"]
    plain = world("class Plain:\n    def f(self):\n        return 1\n")["Plain"]
    for label, target in (("D9 class over pygments PythonLexer", lexer), ("D9b plain one-method class", plain)):
        start = time.perf_counter()
        CodeDigest().spell_id(target)
        cold = (time.perf_counter() - start) * 1000
        digest = CodeDigest()
        digest.spell_id(target)
        start = time.perf_counter()
        digest.spell_id(target)
        warm = (time.perf_counter() - start) * 1000
        print(f"{label:<62} cold_ms={cold:8.3f} warm_ms={warm:8.3f} mro={len(target.__mro__)}")
    config = world("class Config:\n    def __init__(self, a, b):\n        self.a = a\n        self.b = b\n")["Config"]
    report("D10 two existing objects with equal data (one spell)", "same", CodeDigest().spell_id(config(1, 2)),
           CodeDigest().spell_id(config(1, 2)))


if __name__ == "__main__":
    decorator_cases()
    third_party_object_cases()
    reference_cases()
    cost_and_data_cases()
