"""
Unit tests - SpellCodeDigest: a spell_id is the registered object's code
(STORY-2026-10-18-spell_id_hashes_the_object_code).

A spell_id is the SHA256 of the registered object's code: a class's methods, constructor, class-level values, nested
code and the classes it inherits from; a function's instructions, constants by value, local names, defaults and
closure; an existing object's class code plus its data. Docstrings, comments, blank lines and line numbers never enter
it, and neither does anything from the bind call. Each case executes two variants of source in a namespace named like a
module, so module and qualname match and only the code differs (the design probes' cases E01-E34, P1-P10, I1-I9 and
A1-A3, and the four contract refinements of 2026-10-18).
"""
import annotationlib
import functools
import hashlib
import inspect
import logging
import os
import pathlib
import subprocess
import sys
import sysconfig
import threading
from typing import Any, ClassVar, Dict, List, Tuple

import pytest

import melder
from melder.aether.spellbook.bind.spell_code_digest import SpellCodeDigest


def _world(source: str, module: str = "userworld") -> Dict[str, Any]:
    """Execute one variant's source in a fresh namespace named like a module, with the probes' imports."""
    namespace: Dict[str, Any] = {"__name__": module}
    exec("import functools, dataclasses, enum, abc, typing, threading, logging\n" + source, namespace)
    return namespace


def _spell_id(target: Any) -> str:
    """Return a target's spell_id from a fresh digest, so the two sides of a case share no memo."""
    return SpellCodeDigest().spell_id(target)


def _pair(left_source: str, right_source: str, name: str) -> Tuple[str, str]:
    """Return the spell_ids of `name` in two executed variants."""
    return _spell_id(_world(left_source)[name]), _spell_id(_world(right_source)[name])


class TestClassCode:
    """A class's code: its methods, constructor, class-level values, nested code and the classes it inherits."""

    WORKER: ClassVar[str] = (
        "class Worker:\n    '''Base.'''\n    def __init__(self, retries: int = 1) -> None:\n"
        "        self.retries = retries\n    def run(self) -> str:\n        '''Run once.'''\n        return 'v1'\n")
    CHANGES: ClassVar[List[Any]] = [
        pytest.param("class Base:\n    def run(self):\n        return 1\nclass Sub(Base):\n    pass\n",
                     "class Base:\n    def run(self):\n        return 2\nclass Sub(Base):\n    pass\n", "Sub",
                     id="a_base_class_method_body"),
        pytest.param("class W:\n    retries = 3\n", "class W:\n    retries = 5\n", "W", id="a_class_level_value"),
        pytest.param("class W:\n    tags = ('a', 'b')\n", "class W:\n    tags = ('b', 'a')\n", "W",
                     id="a_class_level_tuple_order"),
        pytest.param("class W:\n    class Inner:\n        z = 1\n", "class W:\n    class Inner:\n        z = 2\n", "W",
                     id="a_nested_class_body"),
        pytest.param("class W:\n    @property\n    def p(self):\n        return 1\n",
                     "class W:\n    @property\n    def p(self):\n        return 2\n", "W", id="a_property_body"),
        pytest.param("class W:\n    @staticmethod\n    def s():\n        return 1\n",
                     "class W:\n    @staticmethod\n    def s():\n        return 2\n", "W", id="a_staticmethod_body"),
        pytest.param("class W:\n    @classmethod\n    def c(cls):\n        return 1\n",
                     "class W:\n    @classmethod\n    def c(cls):\n        return 2\n", "W", id="a_classmethod_body"),
        pytest.param("@dataclasses.dataclass\nclass D:\n    a: int = 1\n",
                     "@dataclasses.dataclass\nclass D:\n    a: int = 2\n", "D", id="a_dataclass_default"),
        pytest.param("class C(enum.Enum):\n    RED = 1\n", "class C(enum.Enum):\n    RED = 2\n", "C",
                     id="an_enum_member_value"),
        pytest.param("class W:\n    x: int\n", "class W:\n    x: str\n", "W", id="a_field_annotation"),
        pytest.param("class W:\n    def run(self, x: int) -> int:\n        return x\n",
                     "class W:\n    def run(self, x: str) -> int:\n        return x\n", "W",
                     id="a_parameter_annotation"),
        pytest.param("class W:\n    def run(self, x):\n        return x\n",
                     "class W:\n    def run(self, *x):\n        return x\n", "W", id="a_parameter_kind"),
        pytest.param("class Meta(type):\n    def describe(cls):\n        return 1\n"
                     "class W(metaclass=Meta):\n    pass\n",
                     "class Meta(type):\n    def describe(cls):\n        return 2\n"
                     "class W(metaclass=Meta):\n    pass\n",
                     "W", id="a_user_metaclass_method_body"),
        pytest.param("class W:\n    def run(self, f):\n        try:\n            f()\n        except ValueError:\n"
                     "            return 0\n",
                     "class W:\n    def run(self, f):\n        try:\n            f()\n        except KeyError:\n"
                     "            return 0\n", "W", id="an_except_clause_type"),
        pytest.param("class W:\n    def run(self, x):\n        total = x * 2\n        return total\n",
                     "class W:\n    def run(self, x):\n        amount = x * 2\n        return amount\n", "W",
                     id="a_renamed_local_variable"),
        pytest.param("class G[T: int]:\n    def f(self, x: T) -> T:\n        return x\n",
                     "class G[T: str]:\n    def f(self, x: T) -> T:\n        return x\n", "G",
                     id="a_type_parameter_bound"),
        pytest.param(WORKER, WORKER.replace("return 'v1'", "return 'v1 ' + str(sum(range(10)))"), "Worker",
                     id="a_method_body"),
        pytest.param(WORKER, WORKER.replace("def run(self)", "def run(self, fast: bool = False)"), "Worker",
                     id="a_parameter_added_to_a_method"),
        pytest.param(WORKER, WORKER.replace("retries: int = 1", "retries: int = 2"), "Worker",
                     id="a_constructor_default"),
        pytest.param(WORKER, WORKER.replace("def run(self)", "def execute(self)"), "Worker", id="a_renamed_method"),
    ]
    SAME: ClassVar[List[Any]] = [
        pytest.param("class W:\n    def run(self, x=3):\n        return [v + x for v in range(4)]\n",
                     "class W:\n    def run(self, x=3):\n        return [v + x for v in range(4)]\n", "W",
                     id="the_same_source_executed_twice"),
        pytest.param("class W:\n    def a(self):\n        return 1\n    def b(self):\n        return 2\n",
                     "class W:\n    def b(self):\n        return 2\n    def a(self):\n        return 1\n", "W",
                     id="methods_defined_in_another_order"),
        pytest.param("class W:\n    def run(self):\n        return 1\n",
                     "class W:\n    '''Doc.'''\n\n\n    def run(self):\n        '''Run doc.'''\n        # a comment\n\n"
                     "        return 1\n", "W", id="docstrings_comments_and_blank_lines"),
        pytest.param("class W:\n    def run(self, f):\n        try:\n            f()\n        except ValueError:\n"
                     "            return 0\n",
                     "class W:\n    def run(self, f):\n        '''Doc.'''\n        try:\n            f()\n"
                     "        except ValueError:\n            return 0\n", "W",
                     id="a_docstring_on_a_try_except_method"),
        pytest.param(WORKER, WORKER.replace("'''Run once.'''", "'''Run exactly once, then stop.'''"), "Worker",
                     id="a_reworded_docstring"),
        pytest.param(WORKER,
                     WORKER.replace("        self.retries", "        '''Keep the retries.'''\n        self.retries"),
                     "Worker", id="a_docstring_added_to_the_constructor"),
        pytest.param(WORKER, "\n\n\n" + WORKER.replace("\n    def", "\n\n\n    def"), "Worker",
                     id="blank_lines_moving_every_line"),
        pytest.param(WORKER, WORKER.replace("        return 'v1'", "        # the first version\n        return 'v1'"),
                     "Worker", id="a_comment_in_a_method"),
    ]

    @pytest.mark.parametrize(("left", "right", "name"), CHANGES)
    def test_a_code_change_moves_the_spell_id(self, left: str, right: str, name: str) -> None:
        """Every real change of a class's code - a body, a value, a parameter, a name, a base - is a new spell_id."""
        first, second = _pair(left, right, name)
        assert first != second

    @pytest.mark.parametrize(("left", "right", "name"), SAME)
    def test_documentation_and_layout_do_not_move_the_spell_id(self, left: str, right: str, name: str) -> None:
        """Docstrings, comments, blank lines and re-executing the same source keep the spell_id."""
        first, second = _pair(left, right, name)
        assert first == second

    def test_the_same_code_in_another_module_is_another_spell(self) -> None:
        """The module is part of the code's identity."""
        source = "class W:\n    def run(self):\n        return 1\n"
        assert _spell_id(_world(source)["W"]) != _spell_id(_world(source, "otherworld")["W"])

    def test_two_empty_subclasses_under_different_names_are_two_spells(self) -> None:
        """A class's qualified name is part of its code."""
        space = _world("class Base:\n    def run(self):\n        return 1\nclass Primary(Base):\n    pass\n"
                       "class Replica(Base):\n    pass\n")
        assert _spell_id(space["Primary"]) != _spell_id(space["Replica"])

    def test_a_decorator_argument_change_moves_the_spell_id(self) -> None:
        """A decorated method is its wrapper, whose closure holds the decorator's argument."""
        decorator = ("def tag(n):\n    def deco(fn):\n        @functools.wraps(fn)\n        def wrapper(*a, **k):\n"
                     "            return (n, fn(*a, **k))\n        return wrapper\n    return deco\n")
        first, second = _pair(decorator + "class W:\n    @tag(3)\n    def run(self):\n        return 1\n",
                              decorator + "class W:\n    @tag(5)\n    def run(self):\n        return 1\n", "W")
        assert first != second


class TestInsideAMethod:
    """The instructions inside a method count, not only its outline (cases I1-I9)."""

    SAVER: ClassVar[str] = (
        "class Saver:\n    def handle(self, x: int) -> tuple:\n        total = x * 2\n        if x > 0:\n"
        "            self.save(total)\n        helper = lambda y: y + 1\n        def inner(z: int) -> int:\n"
        "            return z - 1\n        values = [v + 1 for v in range(x)]\n"
        "        return helper(total), inner(total), values\n    def save(self, value: int) -> None:\n"
        "        self.last = value\n    def store(self, value: int) -> None:\n        self.kept = value\n")
    CHANGES: ClassVar[List[Any]] = [
        pytest.param("total = x * 2", "total = x * 3", id="a_constant"),
        pytest.param("self.save(total)", "self.store(total)", id="the_method_called"),
        pytest.param("if x > 0:", "if x >= 0:", id="a_comparison"),
        pytest.param("lambda y: y + 1", "lambda y: y + 2", id="a_lambda_body"),
        pytest.param("return z - 1", "return z - 2", id="a_nested_function_body"),
        pytest.param("[v + 1 for v", "[v * 2 for v", id="a_comprehension_body"),
        pytest.param("total = x * 2\n        if x > 0:\n            self.save(total)\n",
                     "if x > 0:\n            self.save(x)\n        total = x * 2\n", id="two_statements_swapped"),
        pytest.param("total", "amount", id="a_renamed_local"),
    ]

    @pytest.mark.parametrize(("old", "new"), CHANGES)
    def test_a_change_inside_a_method_moves_the_spell_id(self, old: str, new: str) -> None:
        """Constants, calls, comparisons, lambdas, nested functions and comprehensions are all read."""
        first, second = _pair(self.SAVER, self.SAVER.replace(old, new), "Saver")
        assert first != second

    def test_a_comment_inside_a_nested_function_keeps_the_spell_id(self) -> None:
        """Comments are not code, wherever they are."""
        commented = self.SAVER.replace("            return z - 1", "            # one less\n            return z - 1")
        first, second = _pair(self.SAVER, commented, "Saver")
        assert first == second


class TestFunctionsAndValues:
    """Functions, lambdas, partials and bound methods are their code and the values they carry."""

    def test_two_lambdas_with_different_bodies_are_two_spells(self) -> None:
        """A lambda is its instructions; today's outline hashed only its signature."""
        space = _world("a = lambda x: x + 1\nb = lambda x: x * 100\n")
        assert _spell_id(space["a"]) != _spell_id(space["b"])

    def test_two_lambdas_differing_only_by_a_default_are_two_spells(self) -> None:
        """Defaults are part of a function's code."""
        space = _world("a = lambda x, k=1: x + k\nb = lambda x, k=2: x + k\n")
        assert _spell_id(space["a"]) != _spell_id(space["b"])

    def test_partials_with_different_arguments_are_two_spells(self) -> None:
        """A partial is its function and its bound arguments."""
        add = _world("def f(x, y):\n    return x + y\n")["f"]
        assert _spell_id(functools.partial(add, 1)) != _spell_id(functools.partial(add, 2))

    def test_classes_a_factory_makes_differ_by_their_captured_values(self) -> None:
        """A closure's captured values count: equal captures are one spell, different ones two."""
        make = _world("def make(n):\n    class W:\n        def run(self):\n            return n\n"
                      "    return W\n")["make"]
        assert _spell_id(make(1)) != _spell_id(make(2))
        assert _spell_id(make(1)) == _spell_id(make(1))

    def test_bound_methods_follow_their_object_data(self) -> None:
        """A bound method is its function and its object's data."""
        config = _world(_objects_source())["Cfg"]
        assert _spell_id(config(1, 2).describe) == _spell_id(config(1, 2).describe)
        assert _spell_id(config(1, 2).describe) != _spell_id(config(1, 3).describe)

    def test_a_string_constant_holding_an_address_like_text_is_read_exactly(self) -> None:
        """A literal is its exact repr: " at 0x1F" inside a string is text, not an address to strip."""
        first, second = _pair("def f():\n    return 'listening at 0x1F'\n", "def f():\n    return 'listening'\n", "f")
        assert first != second

    def test_an_integer_constant_too_long_for_decimal_text_digests_in_hex(self) -> None:
        """A code constant past the interpreter's decimal limit never makes the digest raise, and still counts."""
        first, second = _pair("def f():\n    return 0x" + "f" * 5000 + "\n",
                              "def f():\n    return 0x" + "e" * 5000 + "\n", "f")
        assert first != second

    def test_an_eager_type_variable_bound_counts(self) -> None:
        """A TypeVar given its bound eagerly is read by its stored bound."""
        first, second = _pair("class W:\n    T = typing.TypeVar('T', bound=int)\n",
                              "class W:\n    T = typing.TypeVar('T', bound=str)\n", "W")
        assert first != second

    def test_a_container_subclass_is_read_through_its_builtin_type(self) -> None:
        """A tuple subclass whose __iter__ raises is read as a tuple: the digest neither runs nor fails on it."""
        odd = "class Odd(tuple):\n    def __iter__(self):\n        raise RuntimeError('never iterated')\n"
        first, second = _pair(odd + "class W:\n    tags = Odd(('a', 'b'))\n",
                              odd + "class W:\n    tags = Odd(('b', 'a'))\n", "W")
        assert first != second


def _objects_source() -> str:
    """The source of the object cases' classes (a function, so the module holds no constant)."""
    return (
        "class Cfg:\n    def __init__(self, a, b):\n        self.a = a\n        self.b = b\n"
        "    def describe(self):\n        return (self.a, self.b)\n"
        "class Outer:\n    def __init__(self, inner):\n        self.inner = inner\n"
        "class Svc:\n    def __init__(self, lock, log):\n        self.lock = lock\n        self.log = log\n"
        "class Node:\n    def __init__(self, v):\n        self.v = v\n        self.me = self\n"
        "class Lazy:\n    def __init__(self, v):\n        self.v = v\n"
        "    @functools.cached_property\n    def doubled(self):\n        return self.v * 2\n"
        "class Slotted:\n    __slots__ = ('a', '__b')\n    def __init__(self, a, b):\n        self.a = a\n"
        "        self.__b = b\n")


class TestExistingObjects:
    """An existing object is its class's code plus its data, read as it is at bind."""

    def test_objects_with_equal_data_are_one_spell(self) -> None:
        """Equal data, one spell (a second registration is refused as the same spell)."""
        config = _world(_objects_source())["Cfg"]
        assert _spell_id(config(1, 2)) == _spell_id(config(1, 2))

    def test_objects_with_different_data_are_two_spells(self) -> None:
        """Data counts, nested user objects included."""
        space = _world(_objects_source())
        config, outer = space["Cfg"], space["Outer"]
        assert _spell_id(config(1, 2)) != _spell_id(config(1, 3))
        assert _spell_id(outer(config(1, 2))) != _spell_id(outer(config(1, 9)))

    def test_a_held_lock_or_logger_counts_by_its_type_only(self) -> None:
        """Runtime state of standard-library resources - a lock's state, a logger's name - is not data."""
        service = _world(_objects_source())["Svc"]
        held = threading.Lock()
        held.acquire()
        try:
            assert (_spell_id(service(threading.Lock(), logging.getLogger("x")))
                    == _spell_id(service(held, logging.getLogger("y"))))
        finally:
            held.release()

    def test_self_referencing_objects_with_equal_data_are_one_spell(self) -> None:
        """Cycles are marked, not followed."""
        node = _world(_objects_source())["Node"]
        assert _spell_id(node(1)) == _spell_id(node(1))

    def test_reading_a_cached_property_keeps_the_spell_id(self) -> None:
        """A cached_property's stored value is not part of the object's data."""
        lazy = _world(_objects_source())["Lazy"](4)
        before = _spell_id(lazy)
        assert lazy.doubled == 8
        assert _spell_id(lazy) == before

    def test_a_mangled_slot_counts(self) -> None:
        """Slots are read, private (mangled) ones included."""
        slotted = _world(_objects_source())["Slotted"]
        assert _spell_id(slotted(1, 2)) != _spell_id(slotted(1, 3))

    def test_standard_library_objects_are_their_type_and_repr(self) -> None:
        """Two loggers differ by their repr; the same logger is one spell."""
        assert _spell_id(logging.getLogger("a")) != _spell_id(logging.getLogger("b"))
        assert _spell_id(logging.getLogger("a")) == _spell_id(logging.getLogger("a"))


class TestRuntimeStateDoesNotCount:
    """What the interpreter or a caller does to a class after it is defined does not move its spell_id."""

    def test_running_a_method_many_times_keeps_the_spell_id(self) -> None:
        """Specialization rewrites a code object's cache, never the instructions the digest reads."""
        hot = _world("class Hot:\n    def f(self, x):\n        return x + 1\n")["Hot"]
        cold = _spell_id(hot)
        instance = hot()
        for value in range(20000):
            instance.f(value)
        assert _spell_id(hot) == cold

    def test_reading_annotations_keeps_the_spell_id(self) -> None:
        """Python 3.14 adds `__annotate_func__` and `__annotations_cache__` to a class when they are read."""
        space = _world("class Plain:\n    def f(self):\n        return 1\nclass Typed:\n    x: int = 1\n"
                       "@dataclasses.dataclass\nclass D:\n    a: int = 1\n")
        for name in ("Plain", "Typed", "D"):
            before = _spell_id(space[name])
            annotationlib.get_annotations(space[name])
            inspect.get_annotations(space[name])
            assert _spell_id(space[name]) == before, name

    def test_isinstance_against_a_runtime_checkable_protocol_and_abc_register_keep_the_spell_id(self) -> None:
        """Protocol and ABC caches are interpreter bookkeeping."""
        space = _world("@typing.runtime_checkable\nclass P(typing.Protocol):\n    def f(self) -> int: ...\n"
                       "class A(abc.ABC):\n    @abc.abstractmethod\n    def g(self): ...\n")
        protocol_before, abc_before = _spell_id(space["P"]), _spell_id(space["A"])
        assert isinstance(object(), space["P"]) is False
        space["A"].register(int)
        assert _spell_id(space["P"]) == protocol_before
        assert _spell_id(space["A"]) == abc_before

    def test_a_class_level_dict_mutated_at_runtime_moves_the_spell_id(self) -> None:
        """A class is hashed as it is at bind: its values are its code."""
        registry = _world("class Registry:\n    entries = {}\n")["Registry"]
        before = _spell_id(registry)
        registry.entries["k"] = 1
        assert _spell_id(registry) != before

    def test_tracing_and_monitoring_keep_the_spell_id(self) -> None:
        """Instrumented code (sys.monitoring line and instruction events, sys.settrace) digests as when idle."""
        traced = _world("class Traced:\n    def f(self, x):\n        if x:\n            return x + 1\n"
                        "        return 0\n")["Traced"]
        idle = _spell_id(traced)
        monitoring = sys.monitoring
        free = [tool for tool in range(6) if monitoring.get_tool(tool) is None]
        if not free:
            pytest.skip("every sys.monitoring tool id is in use")
        tool = free[-1]
        events = monitoring.events.LINE | monitoring.events.INSTRUCTION
        monitoring.use_tool_id(tool, "spell_code_digest_test")
        try:
            monitoring.register_callback(tool, monitoring.events.LINE, lambda code, line: None)
            monitoring.register_callback(tool, monitoring.events.INSTRUCTION, lambda code, offset: None)
            monitoring.set_local_events(tool, traced.f.__code__, events)
            for value in range(50):
                traced().f(value)
            monitored = _spell_id(traced)
        finally:
            monitoring.set_local_events(tool, traced.f.__code__, 0)
            monitoring.free_tool_id(tool)
        previous = sys.gettrace()
        sys.settrace(lambda frame, event, arg: None)
        try:
            for value in range(50):
                traced().f(value)
            tracing = _spell_id(traced)
        finally:
            sys.settrace(previous)
        assert monitored == idle
        assert tracing == idle


class TestContract:
    """The id's form, its stability and the digest's lifecycle."""

    def test_the_spell_id_is_the_sha256_of_the_tag_the_cache_tag_and_the_encoding(self) -> None:
        """The documented formula, 64 lowercase hex characters."""
        target = _world("class W:\n    def run(self):\n        return 1\n")["W"]
        digest = SpellCodeDigest()
        expected = hashlib.sha256(
            (SpellCodeDigest.TAG + "\n" + str(sys.implementation.cache_tag) + "\n" + digest.target_encoding(target))
            .encode("utf-8", "surrogatepass")).hexdigest()
        assert digest.spell_id(target) == expected
        assert len(expected) == 64 and expected == expected.lower()

    def test_each_kind_of_target_has_its_encoding(self) -> None:
        """Classes, functions, values, application objects and standard-library objects are told apart."""
        space = _world("class W:\n    def run(self):\n        return 1\ndef f(x):\n    return x\n" + _objects_source())
        digest = SpellCodeDigest()
        assert digest.target_encoding(space["W"]).startswith("class ")
        assert digest.target_encoding(space["f"]).startswith("function userworld f ")
        assert digest.target_encoding(functools.partial(space["f"], 1)).startswith("value ")
        assert digest.target_encoding(space["Cfg"](1, 2)).startswith("object objclass:")
        assert digest.target_encoding(logging.getLogger("a")).startswith("repr logging.Logger ")

    def test_unicode_identifiers_digest_stably(self) -> None:
        """Non-ASCII class and method names are code like any other: one 64-hex id, apart from an ASCII twin."""
        source = "class ΔSpell:\n    def α(self):\n        return 1\n    def β(self):\n        return 2\n"
        first, second = _pair(source, source, "ΔSpell")
        ascii_twin = _spell_id(_world(source.replace("α", "a"))["ΔSpell"])
        assert first == second and len(first) == 64
        assert ascii_twin != first

    def test_a_warm_digest_gives_the_cold_answer(self) -> None:
        """Memoized code digests never change an id."""
        target = _world("class W:\n    def run(self):\n        return [v * 2 for v in range(3)]\n")["W"]
        digest = SpellCodeDigest()
        assert digest.spell_id(target) == digest.spell_id(target) == _spell_id(target)

    def test_cleanup_is_idempotent_and_ends_the_digest(self) -> None:
        """After cleanup the digest refuses work."""
        digest = SpellCodeDigest()
        digest.cleanup()
        digest.cleanup()
        with pytest.raises(RuntimeError):
            digest.spell_id(int)

    @pytest.mark.parametrize("seed", ["1", "2"])
    def test_the_spell_id_is_the_same_in_another_process(self, seed: str) -> None:
        """No memory address, hash seed or process state enters an id."""
        script = (
            "import sys\nfrom melder.aether.spellbook.bind.spell_code_digest import SpellCodeDigest\n"
            "space = {'__name__': 'userworld'}\n"
            "exec(\"class W:\\n    tags = {'b', 'a'}\\n    def run(self, x=object):\\n        return [x]\\n"
            "f = lambda y: y + 1\\n\", space)\n"
            "print(SpellCodeDigest().spell_id(space['W']), SpellCodeDigest().spell_id(space['f']))\n")
        source_root = str(pathlib.Path(melder.__file__).resolve().parents[1])
        environment = dict(os.environ, PYTHONHASHSEED=seed, PYTHONPATH=source_root)
        here = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, env=environment,
                              check=True, timeout=120)
        space: Dict[str, Any] = {"__name__": "userworld"}
        exec("class W:\n    tags = {'b', 'a'}\n    def run(self, x=object):\n        return [x]\n"
             "f = lambda y: y + 1\n", space)
        assert here.stdout.split() == [_spell_id(space["W"]), _spell_id(space["f"])]

    @pytest.mark.skipif(not sysconfig.get_config_var("Py_GIL_DISABLED"), reason="free-threaded builds only")
    def test_the_spell_id_is_the_same_with_the_gil_on_and_off(self) -> None:
        """A free-threaded interpreter compiles the same instructions whether the GIL runs or not."""
        script = (
            "from melder.aether.spellbook.bind.spell_code_digest import SpellCodeDigest\n"
            "space = {'__name__': 'userworld'}\n"
            "exec('class W:\\n    def run(self, x):\\n        return [v + x for v in range(3)]\\n', space)\n"
            "print(SpellCodeDigest().spell_id(space['W']))\n")
        source_root = str(pathlib.Path(melder.__file__).resolve().parents[1])
        environment = dict(os.environ, PYTHONPATH=source_root)
        answers = set()
        for gil in ("0", "1"):
            done = subprocess.run([sys.executable, "-X", "gil=" + gil, "-W", "ignore", "-c", script],
                                  capture_output=True, text=True, env=environment, check=True, timeout=120)
            answers.add(done.stdout.strip())
        assert len(answers) == 1
