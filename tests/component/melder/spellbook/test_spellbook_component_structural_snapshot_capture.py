"""
Component contracts: conjure end captures one structural payload per owned spell into the bundle.

The capture reads durable state only (Spell.dependencies, the registered local topology, the lineage
validity and the bind-time requirements), so it runs on every cache path - including an executor full
hit - and flags the conjure-end emit only when the structural bytes changed. Each "world" is a fresh
Aether reusing the same frame, conduit name and cache directory, like the restage contracts.
"""

import inspect
import marshal
import shutil
from pathlib import Path
from typing import Iterator, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.aetheric_frame.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spell_compiler.structural_snapshot.structural_snapshot import (
    StructuralSnapshot,
)
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from melder.utilities.caching_system.caching_system import CachingSystem


def _reset_world() -> None:
    """Replace the process singletons with a fresh Aether and Nexus."""
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def isolated_worlds() -> Iterator[None]:
    """
    Purpose: Give each case fresh worlds and leave a fresh one behind.
    Yields: None while the case runs.
    """
    _reset_world()
    yield
    _reset_world()


def _package_root() -> Path:
    """Return the melder package root the runtime anchors relative cache fragments against."""
    return Path(inspect.getfile(AethericFrameConfiguration)).resolve().parents[2]


def _fresh_cache_fragment(name: str) -> Path:
    """Empty one repo-local cache root and return it as a package-relative fragment."""
    root = _package_root() / "tests/component/melder/spellbook" / name
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    return root.resolve().relative_to(_package_root())


def _new_world_book(frame: str, cache_fragment: Path) -> Spellbook:
    """Start a fresh world with caching enabled under the fragment and return a Book on `frame`."""
    _reset_world()
    configuration = Aether()._ensure_frame(frame).frame_configuration
    configuration.with_system_caching_enabled(True)
    configuration.with_system_cache_root_path(cache_fragment)
    book = Spellbook(aetheric_frame=frame)
    book.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    return book


class Engine:
    """Provider without dependencies."""


class Car:
    """Consumer with one annotation socket."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine


def _conjure_pair(frame: str, cache_fragment: Path) -> Tuple[Spellbook, str, str]:
    """Bind Engine (unique) and Car (many) in a fresh world, conjure, and return the Book and both ids."""
    book = _new_world_book(frame, cache_fragment)
    engine_id = book.bind(spell=Engine, existence="unique", permissions="create")
    car_id = book.bind(spell=Car, existence="many", permissions="create")
    book.conjure(name="root")
    return book, engine_id, car_id


def _bundle(book: Spellbook) -> CachingSystem:
    """Return the Book's cache utility."""
    return book._get_or_create_caching_system()


def test_conjure_end_captures_a_structural_payload_per_owned_spell() -> None:
    """
    Purpose: The bundle holds phase 3-4 rows for Engine and Car after a full-miss conjure.
    Contract: Executor and structural tiers name the same ids; Car's rows point at Engine by id; both
        payloads share the world stamp and are replayable; the rows survive the emit on disk.
    """
    fragment = _fresh_cache_fragment("_cache_structural_capture_rows")
    book, engine_id, car_id = _conjure_pair("structural-capture", fragment)
    bundle = _bundle(book)

    assert set(bundle.cached_structural_spell_ids) == {engine_id, car_id} == set(bundle.cached_spell_ids)
    engine_payload = bundle.get_structural_payload(engine_id)
    car_payload = bundle.get_structural_payload(car_id)
    assert engine_payload["key"] == {"format": StructuralSnapshot.PAYLOAD_FORMAT, "spell_id": engine_id, "annotation_refs": []}
    assert car_payload["key"] == {
        "format": StructuralSnapshot.PAYLOAD_FORMAT,
        "spell_id": car_id,
        "annotation_refs": [(Engine.__module__, Engine.__qualname__)],
    }
    assert engine_payload["world_stamp"] == car_payload["world_stamp"] == StructuralSnapshot.world_stamp(book)
    assert engine_payload["replayable"] is True and car_payload["replayable"] is True
    assert engine_payload["phase3"] == {"dependency_ids": [], "sockets": []}
    assert car_payload["phase3"]["dependency_ids"] == [engine_id]
    (socket,) = car_payload["phase3"]["sockets"]
    assert socket[0] == "engine" and socket[2] == "NORMAL" and socket[5] == (engine_id,)
    assert engine_payload["phase4"] == {"validity": "valid", "contract_unvalidated": False}
    assert car_payload["phase4"] == {"validity": "valid", "contract_unvalidated": False}

    persisted = marshal.loads(bundle.bundle_path.read_bytes())
    assert marshal.loads(persisted["structural_payloads"][car_id]) == car_payload


def test_repeat_world_full_hit_keeps_structural_rows_and_does_not_rewrite_the_bundle() -> None:
    """
    Purpose: Capture on an executor full hit is a no-op when the world is unchanged.
    Contract: The bundle file bytes and mtime are untouched by the second world; its rows equal the first's.
    """
    fragment = _fresh_cache_fragment("_cache_structural_capture_full_hit")
    book, _engine_id, car_id = _conjure_pair("structural-full-hit", fragment)
    path = _bundle(book).bundle_path
    written = (path.read_bytes(), path.stat().st_mtime_ns)
    first_rows = _bundle(book).get_structural_payload(car_id)

    book, _engine_id, car_id = _conjure_pair("structural-full-hit", fragment)

    assert (path.read_bytes(), path.stat().st_mtime_ns) == written
    assert _bundle(book).get_structural_payload(car_id) == first_rows


def test_eq_risky_pool_marks_every_payload_non_replayable() -> None:
    """
    Purpose: Replayability is decided per pool, by the phase-3 eq-safety rule.
    Contract: One spellframe with a custom __eq__ makes both payloads carry replayable False.
    """

    class Frame:
        def __eq__(self, other: object) -> bool:
            return isinstance(other, Frame)

        __hash__ = object.__hash__

    fragment = _fresh_cache_fragment("_cache_structural_capture_eq_risky")
    book = _new_world_book("structural-eq-risky", fragment)
    engine_id = book.bind(spell=Engine, existence="unique", permissions="create")
    car_id = book.bind(spell=Car, existence="many", permissions="create")
    book.bind(spell=Frame, spellframe=Frame(), existence="unique", permissions="create")
    book.conjure(name="root")

    bundle = _bundle(book)
    assert bundle.get_structural_payload(engine_id)["replayable"] is False
    assert bundle.get_structural_payload(car_id)["replayable"] is False
