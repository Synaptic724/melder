"""
Unit tests - SpellCodeDigest at the edges of application code (STORY-2026-10-18-spell_id_hashes_the_object_code).

Decision B (the owner, 2026-10-18): installed third-party code is named by its qualified name and its distribution
version, never digested, and an object of an installed class is its type, that version and its address-free repr.
Decorators and dataclass factories count through the wrapper's closure; code a class only names (a class-level
reference to another class, a module-level helper a method calls) is named, not hashed; an object with no
Python-visible state keeps the repr rule. The design probe's cases D1-D10, with `packaging` (installed with pytest)
as the third-party package.
"""
import importlib.metadata
from typing import Any, Dict, Tuple

import pytest
from packaging.version import Version, parse

from melder.aether.spellbook.bind.spell_code_digest import SpellCodeDigest


def _world(source: str, extra: Dict[str, Any], module: str = "userworld") -> Dict[str, Any]:
    """Execute one variant's source in a fresh namespace named like a module, with `extra` bound in it."""
    namespace: Dict[str, Any] = {"__name__": module}
    namespace.update(extra)
    exec("import functools, dataclasses\n" + source, namespace)
    return namespace


def _pair(left_source: str, right_source: str, name: str) -> Tuple[str, str]:
    """Return the spell_ids of `name` in two executed variants, each from a fresh digest."""
    return (SpellCodeDigest().spell_id(_world(left_source, {})[name]),
            SpellCodeDigest().spell_id(_world(right_source, {})[name]))


def _packaging_version() -> str:
    """The `<distribution>==<version>` text the digest names `packaging` code with."""
    return "packaging==" + importlib.metadata.version("packaging")


def test_an_installed_class_is_named_by_its_distribution_version() -> None:
    """The class itself is not digested: its qualified name and `packaging==<version>` stand for it."""
    encoding = SpellCodeDigest().target_encoding(Version)
    assert encoding == "class packaging.version.Version " + _packaging_version()


def test_an_installed_function_is_named_by_its_distribution_version() -> None:
    """A third-party function target is its qualified name and version."""
    encoding = SpellCodeDigest().target_encoding(parse)
    assert encoding == "function packaging.version.parse " + _packaging_version()


def test_an_application_class_over_an_installed_base_digests_its_own_code_and_names_the_base(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The subclass's code counts; the installed base enters by name and version, not by its code, so another
    installed version of the package is another spell_id while the subclass's source stays the same."""
    source = "class Mine(Base):\n    def label(self):\n        return 1\n"
    mine = _world(source, {"Base": Version})["Mine"]
    changed = _world(source.replace("return 1", "return 2"), {"Base": Version})["Mine"]
    installed = SpellCodeDigest().spell_id(mine)
    assert installed != SpellCodeDigest().spell_id(changed)
    real_version = importlib.metadata.version
    monkeypatch.setattr(importlib.metadata, "version",
                        lambda name: "99.0" if name == "packaging" else real_version(name))
    assert SpellCodeDigest().spell_id(mine) != installed


def test_objects_of_an_installed_class_are_their_type_version_and_repr() -> None:
    """Two differently configured library objects are two spells; equal ones are one."""
    digest = SpellCodeDigest()
    encoding = digest.target_encoding(Version("1.0"))
    assert encoding.startswith("object ext:packaging.version.Version " + _packaging_version() + " ")
    assert SpellCodeDigest().spell_id(Version("1.0")) != SpellCodeDigest().spell_id(Version("2.0"))
    assert SpellCodeDigest().spell_id(Version("1.0")) == SpellCodeDigest().spell_id(Version("1.0"))


def test_an_object_without_python_visible_state_keeps_the_repr_rule() -> None:
    """Such an object is its type and address-free repr, so two bare `object()`s are one spell (the known limit)."""
    digest = SpellCodeDigest()
    assert digest.target_encoding(object()) == "repr builtins.object <object object>"
    assert SpellCodeDigest().spell_id(object()) == SpellCodeDigest().spell_id(object())


def test_a_dataclass_default_factory_change_moves_the_spell_id() -> None:
    """The generated __init__'s closure holds the factory (D1)."""
    first, second = _pair(
        "@dataclasses.dataclass\nclass D:\n    items: object = dataclasses.field(default_factory=list)\n",
        "@dataclasses.dataclass\nclass D:\n    items: object = dataclasses.field(default_factory=dict)\n", "D")
    assert first != second


def test_a_decorator_and_the_function_it_wraps_both_count() -> None:
    """A decorated function is the wrapper, whose closure holds the wrapped function (D2-D4)."""
    deco_a = ("def deco(fn):\n    @functools.wraps(fn)\n    def wrapper(*a, **k):\n        return fn(*a, **k)\n"
              "    return wrapper\n")
    deco_b = deco_a.replace("return fn(*a, **k)", "return fn(*a, **k) or 0")
    body_a = "@deco\ndef job(x):\n    return x + 1\n"
    body_b = "@deco\ndef job(x):\n    return x + 2\n"
    wrapper_changed = _pair(deco_a + body_a, deco_b + body_a, "job")
    body_changed = _pair(deco_a + body_a, deco_a + body_b, "job")
    same_source = _pair(deco_a + body_a, deco_a + body_a, "job")
    assert wrapper_changed[0] != wrapper_changed[1]
    assert body_changed[0] != body_changed[1]
    assert same_source[0] == same_source[1]


def test_a_class_a_class_level_value_names_is_not_hashed() -> None:
    """A class-level reference to another top-level class is that class's name (D7)."""
    holder = "class Holder:\n    strategy = Other\n    def run(self):\n        return self.strategy().f()\n"
    first, second = _pair("class Other:\n    def f(self):\n        return 1\n" + holder,
                          "class Other:\n    def f(self):\n        return 2\n" + holder, "Holder")
    assert first == second


def test_a_module_level_helper_a_method_calls_is_not_hashed() -> None:
    """A method names the helper it calls; the helper's body is not the method's code (D8)."""
    user = "class User:\n    def run(self, x):\n        return helper(x)\n"
    first, second = _pair("def helper(x):\n    return x + 1\n" + user,
                          "def helper(x):\n    return x + 2\n" + user, "User")
    assert first == second
