"""
Unit tests - BindingManifest: how a spell is kept, with its own SHA256 (STORY-2026-10-18-binding_manifest_hash).

The binding manifest holds the bind call - address, spellframe, binding name, existence, disposal order, resolvable
and the managed settings - and its `binding_hash` is a SHA256 over exactly those twelve fields, so a binding changed
under one spell_id (the object's code) is seen by the creation cache and the record. Equal settings written
differently hash alike; nothing else enters the hash.
"""
import hashlib
from typing import Any, Dict, Protocol

import pytest

from melder.aether.spellbook.bind.binding_manifest import BindingManifest
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode
from melder.aether.spellbook.spellframe_kind.spellframe_kind import SpellframeKind


class _Greeting(Protocol):
    """A Protocol contract to bind under."""

    def greet(self) -> str:
        """Say hello."""


def _fields(**changes: Any) -> Dict[str, Any]:
    """The twelve constructor fields of one managed binding, with `changes` applied."""
    values: Dict[str, Any] = {
        "frame_key": "greeter", "binding_key": "__default__", "spellframe": "", "spellframe_kind": "none",
        "binding_name": None, "existence": "managed_spell_quantity", "disposal_method_names": ("close",),
        "resolvable": True, "managed_spell_mode": "queue", "managed_spell_limit": 2,
        "managed_spell_timeout_seconds": 5.0, "managed_spell_reset_methods": ("reset",),
    }
    values.update(changes)
    return values


@pytest.mark.parametrize(("field", "value"), [
    ("frame_key", "other"), ("binding_key", "fast"), ("spellframe", "workers"), ("spellframe_kind", "category"),
    ("binding_name", "fast"), ("existence", "many"), ("disposal_method_names", ("close", "flush")),
    ("resolvable", False), ("managed_spell_mode", "elastic"), ("managed_spell_limit", 3),
    ("managed_spell_timeout_seconds", 6.0), ("managed_spell_reset_methods", ()),
])
def test_every_field_moves_the_binding_hash(field: str, value: Any) -> None:
    """A change of any one binding field is another binding hash."""
    assert BindingManifest(**_fields()).binding_hash != BindingManifest(**_fields(**{field: value})).binding_hash


def test_the_disposal_order_moves_the_binding_hash() -> None:
    """Disposal runs in order, so the order is part of the binding."""
    first = BindingManifest(**_fields(disposal_method_names=("close", "flush")))
    second = BindingManifest(**_fields(disposal_method_names=("flush", "close")))
    assert first.binding_hash != second.binding_hash


def test_the_binding_hash_is_the_sha256_of_the_tag_and_the_field_lines() -> None:
    """The documented formula: `v1-binding` and one `<field>=<repr>` line per field, in order."""
    manifest = BindingManifest(**_fields())
    lines = "\n".join(name + "=" + repr(value) for name, value in manifest.fields())
    expected = hashlib.sha256((BindingManifest.TAG + "\n" + lines).encode("utf-8", "surrogatepass")).hexdigest()
    assert manifest.binding_hash == expected
    assert [name for name, _ in manifest.fields()] == list(_fields())


def test_build_writes_equal_settings_alike() -> None:
    """Enums by name, lists as tuples, an int timeout as a float: one binding, one hash."""
    common: Dict[str, Any] = {
        "key": ("greeter", "__default__"), "spellframe": None, "spellframe_kind": SpellframeKind.none,
        "binding_name": None, "existence": Existence.managed_spell_quantity, "resolvable": True,
        "managed_spell_mode": ManagedSpellMode.queue, "managed_spell_limit": 2,
    }
    from_lists = BindingManifest.build(disposal_method_names=["close"], managed_spell_timeout_seconds=5,
                                       managed_spell_reset_methods=["reset"], **common)
    from_tuples = BindingManifest.build(disposal_method_names=("close",), managed_spell_timeout_seconds=5.0,
                                        managed_spell_reset_methods=("reset",), **common)
    assert from_lists.binding_hash == from_tuples.binding_hash == BindingManifest(**_fields()).binding_hash


def test_describe_gives_the_hash_and_the_fields_as_plain_data() -> None:
    """Twelve fields plus the hash; the name tuples as lists."""
    manifest = BindingManifest(**_fields())
    payload = manifest.describe()
    assert payload["binding_hash"] == manifest.binding_hash
    assert payload["disposal_method_names"] == ["close"]
    assert payload["managed_spell_reset_methods"] == ["reset"]
    assert set(payload) == {"binding_hash"} | set(_fields())


@pytest.mark.parametrize(("spellframe", "text"), [
    (None, ""), ("workers", "workers"),
    (_Greeting, __name__ + "._Greeting"),
])
def test_a_spellframe_is_written_as_text(spellframe: Any, text: str) -> None:
    """None, a category as written, a Protocol by module and qualified name."""
    assert BindingManifest.spellframe_text(spellframe) == text


def test_a_spellframe_object_that_is_not_a_class_is_written_by_its_type_in_angle_brackets() -> None:
    """Any other object is its type's name, never its repr (no code of it runs)."""
    assert BindingManifest.spellframe_text(3) == "<builtins.int>"
