"""Probe (melder_0, 2026-10-18; STORY-2026-10-18-spell_id_hashes_the_object_code): does the code digest v2
(code_digest_v2.py) follow the owner's calls of 2026-10-18 - (1) inherited code counts, (2) class-level values are
code, (3) an object is its class's code plus its data - and stay blind to docstrings, comments and runtime state
the rules exclude? Each case builds two targets from source (exec into a module named "userworld", so module and
qualname match and only the code differs) and compares their prototype spell_ids; "today" is the spell_id
`Bind.spell_id_inspector` gives (existence unique, no address), where it applies.
Run from this folder, twice per hash seed and GIL mode; the ids printed in the last column must not move:
    PYTHONPATH=<repo>/src PYTHONHASHSEED=1 python -X gil=0 probe_code_digest_cases.py
"""
import abc
import dataclasses
import functools
import inspect
import logging
import sys
import threading
import typing

from code_digest_v2 import CodeDigest
from melder.aether.spellbook.bind.bind import Bind
from melder.aether.spellbook.existence.existence import Existence

PRELUDE = "import functools, dataclasses, enum, abc, typing, threading, logging\n"


def world(source: str, module: str = "userworld") -> dict:
    """Execute one variant's source in a fresh namespace named like a module."""
    namespace = {"__name__": module}
    exec(PRELUDE + source, namespace)
    return namespace


def today(target: object) -> str:
    """Today's spell_id, or 'n/a' when the inspector cannot take the target."""
    try:
        name = getattr(target, "__name__", type(target).__name__)
        return Bind.spell_id_inspector(target, spell_name=name, existence=Existence.unique)
    except Exception as error:  # the probe reports, it does not fail
        return "n/a:" + type(error).__name__


def compare(label: str, expect: str, left: object, right: object, show_today: bool = True) -> None:
    """Print one case: expected, the prototype's verdict, today's verdict and the two prototype ids."""
    digest = CodeDigest()
    left_id, right_id = digest.spell_id(left), CodeDigest().spell_id(right)
    got = "same" if left_id == right_id else "different"
    if show_today:
        left_today, right_today = today(left), today(right)
        now = "n/a" if "n/a" in left_today + right_today else ("same" if left_today == right_today else "different")
    else:
        now = "-"
    verdict = "ok" if got == expect else "MISMATCH"
    print(f"{label:<54} expect={expect:<9} got={got:<9} today={now:<9} {verdict:<8} {left_id[:12]}/{right_id[:12]}")


CLASS_CASES = [
    ("E01 base class method body changed (subclass)",
     "class Base:\n    def run(self):\n        return 1\nclass Sub(Base):\n    pass\n",
     "class Base:\n    def run(self):\n        return 2\nclass Sub(Base):\n    pass\n", "Sub", "different"),
    ("E02 class-level value changed (retries 3 -> 5)",
     "class W:\n    retries = 3\n", "class W:\n    retries = 5\n", "W", "different"),
    ("E03 class-level tuple order changed",
     "class W:\n    tags = ('a', 'b')\n", "class W:\n    tags = ('b', 'a')\n", "W", "different"),
    ("E04 nested class body changed",
     "class W:\n    class Inner:\n        z = 1\n", "class W:\n    class Inner:\n        z = 2\n", "W", "different"),
    ("E05 decorator argument changed (@tag(3) -> @tag(5))",
     "def tag(n):\n    def deco(fn):\n        @functools.wraps(fn)\n        def wrapper(*a, **k):\n"
     "            return (n, fn(*a, **k))\n        return wrapper\n    return deco\n"
     "class W:\n    @tag(3)\n    def run(self):\n        return 1\n",
     "def tag(n):\n    def deco(fn):\n        @functools.wraps(fn)\n        def wrapper(*a, **k):\n"
     "            return (n, fn(*a, **k))\n        return wrapper\n    return deco\n"
     "class W:\n    @tag(5)\n    def run(self):\n        return 1\n", "W", "different"),
    ("E06 property getter body changed",
     "class W:\n    @property\n    def p(self):\n        return 1\n",
     "class W:\n    @property\n    def p(self):\n        return 2\n", "W", "different"),
    ("E07 staticmethod body changed",
     "class W:\n    @staticmethod\n    def s():\n        return 1\n",
     "class W:\n    @staticmethod\n    def s():\n        return 2\n", "W", "different"),
    ("E08 classmethod body changed",
     "class W:\n    @classmethod\n    def c(cls):\n        return 1\n",
     "class W:\n    @classmethod\n    def c(cls):\n        return 2\n", "W", "different"),
    ("E09 dataclass default changed",
     "@dataclasses.dataclass\nclass D:\n    a: int = 1\n", "@dataclasses.dataclass\nclass D:\n    a: int = 2\n",
     "D", "different"),
    ("E10 enum member value changed",
     "class C(enum.Enum):\n    RED = 1\n", "class C(enum.Enum):\n    RED = 2\n", "C", "different"),
    ("E11 class field annotation changed (int -> str)",
     "class W:\n    x: int\n", "class W:\n    x: str\n", "W", "different"),
    ("E12 method parameter annotation changed",
     "class W:\n    def run(self, x: int) -> int:\n        return x\n",
     "class W:\n    def run(self, x: str) -> int:\n        return x\n", "W", "different"),
    ("E13 user metaclass method body changed",
     "class Meta(type):\n    def describe(cls):\n        return 1\nclass W(metaclass=Meta):\n    pass\n",
     "class Meta(type):\n    def describe(cls):\n        return 2\nclass W(metaclass=Meta):\n    pass\n", "W", "different"),
    ("E14 same source executed twice",
     "class W:\n    def run(self, x=3):\n        return [v + x for v in range(4)]\n",
     "class W:\n    def run(self, x=3):\n        return [v + x for v in range(4)]\n", "W", "same"),
    ("E16 docstrings, comments and blank lines added",
     "class W:\n    def run(self):\n        return 1\n",
     "class W:\n    '''Doc.'''\n\n\n    def run(self):\n        '''Run doc.'''\n        # a comment\n\n        return 1\n",
     "W", "same"),
    ("E17 except clause type changed (ValueError -> KeyError)",
     "class W:\n    def run(self, f):\n        try:\n            f()\n        except ValueError:\n            return 0\n",
     "class W:\n    def run(self, f):\n        try:\n            f()\n        except KeyError:\n            return 0\n",
     "W", "different"),
    ("E18 try/except method gains a docstring",
     "class W:\n    def run(self, f):\n        try:\n            f()\n        except ValueError:\n            return 0\n",
     "class W:\n    def run(self, f):\n        '''Doc.'''\n        try:\n            f()\n        except ValueError:\n"
     "            return 0\n", "W", "same"),
    ("E27 local variable renamed (call 4: counted)",
     "class W:\n    def run(self, x):\n        total = x * 2\n        return total\n",
     "class W:\n    def run(self, x):\n        amount = x * 2\n        return amount\n", "W", "different"),
    ("E31 type parameter bound changed (T: int -> T: str)",
     "class G[T: int]:\n    def f(self, x: T) -> T:\n        return x\n",
     "class G[T: str]:\n    def f(self, x: T) -> T:\n        return x\n", "G", "different"),
]


def class_cases() -> None:
    for label, left_source, right_source, name, expect in CLASS_CASES:
        compare(label, expect, world(left_source)[name], world(right_source)[name])
    source = "class W:\n    def run(self):\n        return 1\n"
    compare("E15 same code, another module", "different", world(source)["W"], world(source, "otherworld")["W"])


FACTORY = "def make(n):\n    class W:\n        def run(self):\n            return n\n    return W\n"
OBJECTS = (
    "class Cfg:\n    def __init__(self, a, b):\n        self.a = a\n        self.b = b\n"
    "    def describe(self):\n        return (self.a, self.b)\n"
    "class Outer:\n    def __init__(self, inner):\n        self.inner = inner\n"
    "class Svc:\n    def __init__(self, lock, log):\n        self.lock = lock\n        self.log = log\n"
    "class Node:\n    def __init__(self, v):\n        self.v = v\n        self.me = self\n"
    "class Lazy:\n    def __init__(self, v):\n        self.v = v\n"
    "    @functools.cached_property\n    def doubled(self):\n        return self.v * 2\n"
    "class Slotted:\n    __slots__ = ('a', '__b')\n    def __init__(self, a, b):\n        self.a = a\n        self.__b = b\n"
    "def f(x, y):\n    return x + y\n"
)


def object_cases() -> None:
    factory = world(FACTORY)["make"]
    compare("E18b factory classes, captured 1 vs 2", "different", factory(1), factory(2), show_today=False)
    compare("E18c factory classes, captured 1 vs 1", "same", factory(1), factory(1), show_today=False)
    space = world(OBJECTS)
    cfg = space["Cfg"]
    compare("E19 objects with equal data", "same", cfg(1, 2), cfg(1, 2))
    compare("E19b objects with different data", "different", cfg(1, 2), cfg(1, 3))
    compare("E20 nested user object data differs", "different", space["Outer"](cfg(1, 2)), space["Outer"](cfg(1, 9)))
    locked = threading.Lock()
    locked.acquire()
    compare("E21 lock and logger held: by type only", "same",
            space["Svc"](threading.Lock(), logging.getLogger("x")), space["Svc"](locked, logging.getLogger("y")))
    compare("E22 self-referencing objects, equal", "same", space["Node"](1), space["Node"](1))
    lazy = space["Lazy"](4)
    before = CodeDigest().spell_id(lazy)
    _ = lazy.doubled
    after = CodeDigest().spell_id(lazy)
    print(f"{'E23 cached_property read between two digests':<54} expect=same      got={'same' if before == after else 'different':<9}"
          f" today=-         {'ok' if before == after else 'MISMATCH':<8} {before[:12]}/{after[:12]}")
    compare("E28 slotted objects, mangled slot differs", "different", space["Slotted"](1, 2), space["Slotted"](1, 3))
    compare("E29 bound methods of equal-data objects", "same", cfg(1, 2).describe, cfg(1, 2).describe)
    compare("E29b bound methods of different-data objects", "different", cfg(1, 2).describe, cfg(1, 3).describe)
    compare("E30 partials with different arguments", "different",
            functools.partial(space["f"], 1), functools.partial(space["f"], 2), show_today=False)
    lambdas = world("a = lambda x, k=1: x + k\nb = lambda x, k=2: x + k\n")
    compare("E26 lambdas, same body, different default", "different", lambdas["a"], lambdas["b"])
    compare("E32 stdlib object targets: two loggers", "different", logging.getLogger("a"), logging.getLogger("b"))
    compare("E32b the same stdlib object twice", "same", logging.getLogger("a"), logging.getLogger("a"))


def runtime_state_cases() -> None:
    hot = world("class Hot:\n    def f(self, x):\n        return x + 1\n")["Hot"]
    cold = CodeDigest().spell_id(hot)
    instance = hot()
    for value in range(20000):
        instance.f(value)
    warm = CodeDigest().spell_id(hot)
    print(f"{'E24 method run 20000 times between digests':<54} expect=same      got={'same' if cold == warm else 'different':<9}"
          f" today=-         {'ok' if cold == warm else 'MISMATCH':<8} {cold[:12]}/{warm[:12]}")
    space = world("@dataclasses.dataclass\nclass D:\n    a: int = 1\n"
                  "@typing.runtime_checkable\nclass P(typing.Protocol):\n    def f(self) -> int: ...\n"
                  "class A(abc.ABC):\n    @abc.abstractmethod\n    def g(self): ...\n"
                  "class Registry:\n    entries = {}\n")
    checks = []
    before = CodeDigest().spell_id(space["D"]); inspect.get_annotations(space["D"])
    checks.append(("E25 dataclass annotations read", before, CodeDigest().spell_id(space["D"]), "same"))
    before = CodeDigest().spell_id(space["P"]); isinstance(object(), space["P"])
    checks.append(("E25b runtime-checkable isinstance run", before, CodeDigest().spell_id(space["P"]), "same"))
    before = CodeDigest().spell_id(space["A"]); space["A"].register(int)
    checks.append(("E25c ABC.register run", before, CodeDigest().spell_id(space["A"]), "same"))
    before = CodeDigest().spell_id(space["Registry"]); space["Registry"].entries["k"] = 1
    checks.append(("E33 class-level dict mutated at runtime", before, CodeDigest().spell_id(space["Registry"]),
                   "different"))
    for label, first, second, expect in checks:
        got = "same" if first == second else "different"
        print(f"{label:<54} expect={expect:<9} got={got:<9} today=-         {'ok' if got == expect else 'MISMATCH':<8}"
              f" {first[:12]}/{second[:12]}")


def instrumentation_cases() -> None:
    """E34: code under sys.monitoring line/instruction events, and under sys.settrace, digests as when idle."""
    traced = world("class Traced:\n    def f(self, x):\n        if x:\n            return x + 1\n        return 0\n")["Traced"]
    idle = CodeDigest().spell_id(traced)
    monitoring = sys.monitoring
    tool = monitoring.COVERAGE_ID if monitoring.get_tool(monitoring.COVERAGE_ID) is None else monitoring.OPTIMIZER_ID
    monitoring.use_tool_id(tool, "probe")
    events = monitoring.events.LINE | monitoring.events.INSTRUCTION
    monitoring.register_callback(tool, monitoring.events.LINE, lambda code, line: None)
    monitoring.register_callback(tool, monitoring.events.INSTRUCTION, lambda code, offset: None)
    monitoring.set_local_events(tool, traced.f.__code__, events)
    for value in range(50):
        traced().f(value)
    monitored = CodeDigest().spell_id(traced)
    monitoring.set_local_events(tool, traced.f.__code__, 0)
    monitoring.free_tool_id(tool)
    sys.settrace(lambda frame, event, arg: None)
    try:
        for value in range(50):
            traced().f(value)
        tracing = CodeDigest().spell_id(traced)
    finally:
        sys.settrace(None)
    for label, other in (("E34 sys.monitoring LINE+INSTRUCTION events on", monitored),
                         ("E34b sys.settrace active", tracing)):
        got = "same" if other == idle else "different"
        print(f"{label:<54} expect=same      got={got:<9} today=-         {'ok' if got == 'same' else 'MISMATCH':<8}"
              f" {idle[:12]}/{other[:12]}")


if __name__ == "__main__":
    class_cases()
    object_cases()
    runtime_state_cases()
    instrumentation_cases()
