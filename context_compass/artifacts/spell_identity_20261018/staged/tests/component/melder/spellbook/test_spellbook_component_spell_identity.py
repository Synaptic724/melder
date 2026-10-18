"""
Component tests - a spell_id is the object's code and its binding a manifest
(EPIC-2026-10-18-spell_identity_is_the_code, STORY-2026-10-18-spell_id_hashes_the_object_code and
STORY-2026-10-18-binding_manifest_hash).

Through the Spellbook: the id `bind` returns is the object's code digest; binding the same class another way keeps
its spell_id and changes only its binding hash; a second registration of one object is refused, naming its
spell_id; an edited class is a new spell_id that stages beside the old one and melds after a notch (the F1 loop
that was refused as a collision); `inspect_spell` finds an object by its code; a Spell keeps its binding after
cleanup; and a binding changed under one spell_id is another world to the creation cache.
"""
import inspect
import shutil
from pathlib import Path
from typing import Any, Dict, Iterator, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.aetheric_frame.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.bind.spell_code_digest import SpellCodeDigest
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.structural_snapshot.structural_snapshot import StructuralSnapshot
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus


def _reset_world() -> None:
    """Replace the process singletons with a fresh Aether and Nexus."""
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def isolated_worlds() -> Iterator[None]:
    """Give each case a fresh world and leave a fresh one behind."""
    _reset_world()
    yield
    _reset_world()


def _book(frame: str = "default") -> Spellbook:
    """A Spellbook on `frame` with one phase worker."""
    book = Spellbook(aetheric_frame=frame)
    book.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    return book


def _variant(source: str) -> Dict[str, Any]:
    """Execute a class's source as if it were this module's, so variants differ only in their code."""
    namespace: Dict[str, Any] = {"__name__": __name__}
    exec(source, namespace)
    return namespace


class Greeter:
    """A plain application class."""

    def greet(self) -> str:
        """Say hello."""
        return "hi"


class Settings:
    """An application object bound as an existing creation."""

    def __init__(self, level: int) -> None:
        self.level = level


def test_the_spell_id_bind_returns_is_the_object_code_digest() -> None:
    """S1: nothing from the bind call enters the id."""
    spell_id = _book().bind(spell=Greeter, permissions="read", existence="unique")
    assert spell_id == SpellCodeDigest().spell_id(Greeter)


def test_binding_a_class_another_way_keeps_its_spell_id_and_changes_its_binding_hash() -> None:
    """S1 and S2: identity is the code; existence, binding name and spellframe are the binding manifest."""
    first_book = _book()
    first_id = first_book.bind(spell=Greeter, permissions="read", existence="unique")
    first = first_book.find_spell_by_spell_id(first_id)
    first_hash, first_existence = first.binding_hash, first.binding_manifest.existence
    _reset_world()
    second_book = _book()
    second_id = second_book.bind(spell=Greeter, permissions="read", existence="many", binding_name="fresh",
                                 spellframe="greeters")
    second = second_book.find_spell_by_spell_id(second_id)
    assert second_id == first_id
    assert second.binding_hash != first_hash
    assert (first_existence, second.binding_manifest.existence) == ("unique", "many")
    assert second.binding_manifest.binding_name == "fresh"


def test_a_second_registration_of_one_object_is_refused_naming_its_spell_id() -> None:
    """One object is one spell: another binding name and existence do not make a second spell."""
    book = _book()
    spell_id = book.bind(spell=Greeter, permissions="read", existence="unique")
    with pytest.raises(RuntimeError, match="this object is already registered as spell_id " + spell_id):
        book.bind(spell=Greeter, permissions="read", existence="many", binding_name="again")


def _host() -> Tuple[Spellbook, Conduit, Any, Dict[str, Any], Dict[str, Any]]:
    """A dynamic world with version 1 of `Worker` bound and conjured, and version 2 ready to stage."""
    version_one = _variant("class Worker:\n    def run(self) -> str:\n        return 'v1'\n")
    version_two = _variant("class Worker:\n    def run(self) -> str:\n        return 'v2'\n")
    book = _book("identity-f1")
    book.bind(spell=version_one["Worker"], existence="unique")
    conduit = book.conjure(dynamic=True, name="identity-f1-root")
    spell_index = next(iter(book.spells.keys()))
    return book, conduit, spell_index, version_one, version_two


def test_an_edited_class_stages_beside_the_old_one_and_melds_after_a_notch() -> None:
    """The F1 loop: a changed method body is a new spell_id, so staging it is no collision."""
    book, conduit, spell_index, version_one, version_two = _host()
    old_id = SpellCodeDigest().spell_id(version_one["Worker"])
    new_id = book.bind_inactive(spell=version_two["Worker"], spell_index=spell_index, existence="unique")
    assert new_id != old_id
    assert conduit.meld(spell_id=old_id).run() == "v1"
    conduit.notch_spell(spell_index=spell_index, spell_id=new_id)
    assert conduit.meld(spell_id=new_id).run() == "v2"


def test_staging_the_same_class_again_is_refused_naming_its_spell_id() -> None:
    """bind_inactive refuses an object already registered, as bind does."""
    book, _conduit, spell_index, version_one, _version_two = _host()
    old_id = SpellCodeDigest().spell_id(version_one["Worker"])
    with pytest.raises(RuntimeError, match="this object is already registered as spell_id " + old_id):
        book.bind_inactive(spell=version_one["Worker"], spell_index=spell_index, existence="many")


def test_inspect_spell_finds_an_existing_object_by_its_code_and_data() -> None:
    """Stage 3: an equal-data object identity misses is found by the id its code and data give."""
    book = _book()
    spell_id = book.bind(spell=Settings(3), permissions="read", existence="unique")
    book.conjure(name="identity-inspect-root")
    assert book.inspect_spell(Settings(3)) == spell_id
    assert book.inspect_spell(Settings(4)) is None


def test_a_spell_keeps_its_binding_after_cleanup() -> None:
    """The binding manifest and hash stay readable after `cleanup_spell` disposes the Spell, like its spell_id."""
    book = _book("identity-cleanup")
    spell_id = book.bind(spell=Greeter, permissions="read", existence="unique")
    conduit = book.conjure(dynamic=True, name="identity-cleanup-root")
    spell = book.find_spell_by_spell_id(spell_id)
    binding_hash = spell.binding_hash
    conduit.cleanup_spell(spell=spell)
    assert book.find_spell_by_spell_id(spell_id) is None
    assert spell.binding_hash == binding_hash
    assert spell.binding_manifest.binding_hash == binding_hash


def _package_root() -> Path:
    """The melder package root the runtime anchors relative cache fragments against."""
    return Path(inspect.getfile(AethericFrameConfiguration)).resolve().parents[2]


def _cached_world(fragment: Path, existence: Existence) -> Tuple[Spellbook, Conduit]:
    """A fresh world with caching on under `fragment`, `Greeter` bound with `existence`, conjured as one root."""
    _reset_world()
    configuration = Aether()._ensure_frame("identity-cache").frame_configuration
    configuration.with_system_caching_enabled(True)
    configuration.with_system_cache_root_path(fragment)
    book = _book("identity-cache")
    book.bind(spell=Greeter, existence=existence, permissions="create")
    return book, book.conjure(name="identity-cache-root")


def test_a_binding_changed_under_one_spell_id_is_another_world_to_the_creation_cache() -> None:
    """S2: the stamp and keys carry the binding hash, so a `unique` bundle is never replayed for a `many` binding."""
    root = _package_root() / "tests/component/melder/spellbook/_cache_spell_identity_binding"
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    fragment = root.resolve().relative_to(_package_root())
    book, conduit = _cached_world(fragment, Existence.unique)
    assert conduit.meld(spell=Greeter) is conduit.meld(spell=Greeter)
    unique_stamp = StructuralSnapshot.world_stamp(book)
    book, conduit = _cached_world(fragment, Existence.many)
    assert StructuralSnapshot.world_stamp(book) != unique_stamp
    assert conduit.meld(spell=Greeter) is not conduit.meld(spell=Greeter)
    shutil.rmtree(root)
