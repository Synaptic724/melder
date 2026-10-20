"""Probe (melder_0, 2026-10-18; STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool): a PROTOTYPE of
the spell_id the owner asked for - the registered object's actual code (its methods and constructor, their bodies,
parameters and defaults), never its docstrings or comments, and nothing from the bind call - compared with the
spell_id bind gives today. Nothing here is in src/.

The prototype hashes, for a class: its module and qualname, its bases by name, and for every function its class body
defines (methods, constructor, static and class methods, property accessors) the signature text (parameters, defaults,
annotations; memory addresses removed) and the instruction stream read through `dis` with each operand resolved to
its value (constants, names, nested code hashed the same way). Line numbers, the docstring constant and unused
constants are not read, so comments, blank lines and docstrings cannot change it. For a function or lambda: its
module, qualname, signature text and instructions.

Cases (each a pair; "today" is `Bind.spell_id_inspector` as bind computes it, no address, existence unique):
  P1 a method body changed            P2 a parameter added to a method     P3 an __init__ default changed
  P4 a method renamed                 P5 two lambdas, different bodies     P6 a comment added in a method
  P7 a docstring reworded             P8 a docstring added                 P9 blank lines (every line moved)
  P10 two empty subclasses of one base under different names

Run twice with different PYTHONHASHSEED values and with the GIL off and on: the prototype ids must not move.
    PYTHONPATH=<repo>/src PYTHONHASHSEED=1 python -X gil=0 probes/probe_code_hash_prototype.py
"""
import dis
import hashlib
import inspect
import re
import types
from annotationlib import Format

from melder.aether.spellbook.bind.bind import Bind
from melder.aether.spellbook.existence.existence import Existence

ADDRESS = re.compile(r" at 0x[0-9a-fA-F]+")


def canonical(value: object) -> str:
    """Render one operand value the same way in every process (sets sorted, addresses removed)."""
    if isinstance(value, types.CodeType):
        return "code:" + code_digest(value)
    if isinstance(value, frozenset):
        return "frozenset(" + ",".join(sorted(canonical(item) for item in value)) + ")"
    if isinstance(value, tuple):
        return "(" + ",".join(canonical(item) for item in value) + ")"
    return ADDRESS.sub("", repr(value))


def code_digest(code: types.CodeType) -> str:
    """Hash a code object's instructions with resolved operands; no line numbers, no docstring, no unused constants."""
    parts = [
        code.co_name,
        f"{code.co_argcount},{code.co_posonlyargcount},{code.co_kwonlyargcount}",
        str(code.co_flags & ~inspect.CO_HAS_DOCSTRING),
        ",".join(code.co_varnames),
        ",".join(code.co_freevars),
    ]
    for instruction in dis.get_instructions(code):
        parts.append(f"{instruction.opname} {canonical(instruction.argval)}")
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()


def function_digest(function: types.FunctionType) -> str:
    """Signature text (parameters, defaults, annotations) plus the code digest."""
    function = inspect.unwrap(function)
    try:
        signature = ADDRESS.sub("", str(inspect.signature(function, annotation_format=Format.FORWARDREF)))
    except (TypeError, ValueError):
        signature = ""
    return signature + "|" + code_digest(function.__code__)


def code_spell_id(target: object) -> str:
    """The prototype spell_id: the object's code only."""
    if inspect.isclass(target):
        parts = [target.__module__, target.__qualname__, ",".join(base.__qualname__ for base in target.__bases__)]
        for name, value in sorted(target.__dict__.items()):
            if isinstance(value, (staticmethod, classmethod)):
                value = value.__func__
            if isinstance(value, property):
                for role, accessor in (("get", value.fget), ("set", value.fset), ("del", value.fdel)):
                    if accessor is not None:
                        parts.append(f"{name}.{role}:{function_digest(accessor)}")
                continue
            if inspect.isfunction(value):
                parts.append(f"{name}:{function_digest(value)}")
    else:
        parts = [target.__module__, target.__qualname__, function_digest(target)]
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()


def today_spell_id(target: object) -> str:
    """The spell_id bind gives today, with no address and existence unique."""
    return Bind.spell_id_inspector(target, spell_name=target.__name__, existence=Existence.unique)


class Worker:
    """Base version."""

    def __init__(self, retries: int = 1) -> None:
        self.retries = retries

    def run(self) -> str:
        """Run once."""
        return "v1"


Base = Worker


class Worker:
    """P1: run's body differs."""

    def __init__(self, retries: int = 1) -> None:
        self.retries = retries

    def run(self) -> str:
        """Run once."""
        return "v1 " + str(sum(range(10)))


BodyChanged = Worker


class Worker:
    """P2: run takes a parameter."""

    def __init__(self, retries: int = 1) -> None:
        self.retries = retries

    def run(self, fast: bool = False) -> str:
        """Run once."""
        return "v1"


ParameterAdded = Worker


class Worker:
    """P3: the __init__ default differs."""

    def __init__(self, retries: int = 5) -> None:
        self.retries = retries

    def run(self) -> str:
        """Run once."""
        return "v1"


DefaultChanged = Worker


class Worker:
    """P4: run is renamed execute."""

    def __init__(self, retries: int = 1) -> None:
        self.retries = retries

    def execute(self) -> str:
        """Run once."""
        return "v1"


Renamed = Worker


class Worker:
    """P6: a comment in run."""

    def __init__(self, retries: int = 1) -> None:
        self.retries = retries

    def run(self) -> str:
        """Run once."""
        # a comment the owner says must not count
        return "v1"


Commented = Worker


class Worker:
    """P7: every docstring reworded."""

    def __init__(self, retries: int = 1) -> None:
        self.retries = retries

    def run(self) -> str:
        """A completely different docstring for run."""
        return "v1"


Redocumented = Worker


class Worker:
    """P8: __init__ gains a docstring it did not have."""

    def __init__(self, retries: int = 1) -> None:
        """Now documented."""
        self.retries = retries

    def run(self) -> str:
        """Run once."""
        return "v1"


DocstringAdded = Worker


class Worker:
    """P9: blank lines move every line."""



    def __init__(self, retries: int = 1) -> None:

        self.retries = retries



    def run(self) -> str:
        """Run once."""

        return "v1"


Reflowed = Worker

add_one = lambda x: x + 1
times_hundred = lambda x: x * 100


class Primary(Base):
    """P10: an empty subclass."""


class Replica(Base):
    """P10: another empty subclass."""


def main() -> None:
    """Print each pair: today's spell_id and the prototype's, same or different."""
    pairs = [
        ("P1 method body changed", Base, BodyChanged),
        ("P2 parameter added to run", Base, ParameterAdded),
        ("P3 __init__ default changed", Base, DefaultChanged),
        ("P4 run renamed execute", Base, Renamed),
        ("P5 two lambdas, different bodies", add_one, times_hundred),
        ("P6 comment added in run", Base, Commented),
        ("P7 docstrings reworded", Base, Redocumented),
        ("P8 docstring added to __init__", Base, DocstringAdded),
        ("P9 blank lines (every line moved)", Base, Reflowed),
        ("P10 empty subclasses Primary / Replica", Primary, Replica),
    ]
    for label, left, right in pairs:
        today = "same" if today_spell_id(left) == today_spell_id(right) else "different"
        proto_left, proto_right = code_spell_id(left), code_spell_id(right)
        proto = "same" if proto_left == proto_right else "different"
        print(f"{label:<42} today: {today:<9} code hash: {proto:<9} ({proto_left[:12]} / {proto_right[:12]})")


if __name__ == "__main__":
    main()
