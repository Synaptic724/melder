"""
Regression contracts: an executor-cache full hit requires the recorded world stamp.

The executor tier classifies its full hit on payload ids, and an existing creation or a non-resolvable
definition carries no payload. Before generation 19 a world that differed only by such a spell was still a
full hit: a consumer compiled when nothing provided one of its parameters was served its stale executor from
the warm cache (TypeError at the first meld) while a cold cache resolved it. The bundle now records the
structural tier's world stamp at staging and a full hit requires it. Each "world" is a fresh Aether reusing
the same frame, conduit name and cache directory, like the restage contracts.
"""

import inspect
import marshal
import shutil
from pathlib import Path
from typing import Iterator, Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.aetheric_frame.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.structural_snapshot.structural_snapshot import (
    StructuralSnapshot,
)
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from melder.utilities.caching_system.caching_system import CachingSystem
from melder.utilities.custom_exceptions.unresolved_input_error import UnresolvedInputError


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


class Service:
    """Provider supplied as an existing object (bound bare, no spellframe)."""


class Worker:
    """Consumer with one annotation socket that only an existing Service can fill in these worlds."""

    def __init__(self, service: Service) -> None:
        self.service = service


def _conjure_world(frame: str, cache_fragment: Path, service: Optional[Service]) -> tuple[Spellbook, Conduit]:
    """
    Bind Worker (many) and, when given, the existing `service` (unique, bare) in a fresh world; conjure.

    Returns the Book and its root conduit named `world-stamp-root` so every world shares one bundle.
    """
    book = _new_world_book(frame, cache_fragment)
    if service is not None:
        book.bind(spell=service, existence=Existence.unique, permissions="create")
    book.bind(spell=Worker, existence=Existence.many, permissions="create")
    conduit = book.conjure(name="world-stamp-root")
    return book, conduit


def _bundle(book: Spellbook) -> CachingSystem:
    """Return the Book's cache utility."""
    return book._get_or_create_caching_system()


def test_warm_cache_resolves_a_provider_added_as_an_existing_object() -> None:
    """
    Purpose: Regression for the stale solo executor served after a provider appears as an existing object.
    Contract: World 1 (Worker alone) raises UnresolvedInputError at meld and stages Worker's executor; world 2
        (a bare existing Service beside Worker) is a changed world - the warm cache must not full-hit - and its
        meld returns a Worker holding exactly that Service object.
    """
    fragment = _fresh_cache_fragment("_cache_world_stamp_provider_added")
    _book, conduit = _conjure_world("world-stamp-added", fragment, None)
    with pytest.raises(UnresolvedInputError):
        conduit.meld(spell=Worker)

    service = Service()
    book, conduit = _conjure_world("world-stamp-added", fragment, service)

    worker = conduit.meld(spell=Worker)
    assert isinstance(worker, Worker)
    assert worker.service is service
    assert _bundle(book).world_stamp == StructuralSnapshot.world_stamp(book)


def test_warm_cache_drops_a_provider_removed_as_an_existing_object() -> None:
    """
    Purpose: The inverse world change is also a miss: the cached executor names a provider the world lost.
    Contract: World 1 (existing Service beside Worker) melds a Worker; world 2 (Worker alone) raises
        UnresolvedInputError instead of running a plan that names a spell outside the world.
    """
    fragment = _fresh_cache_fragment("_cache_world_stamp_provider_removed")
    _book, conduit = _conjure_world("world-stamp-removed", fragment, Service())
    assert isinstance(conduit.meld(spell=Worker).service, Service)

    _book, conduit = _conjure_world("world-stamp-removed", fragment, None)

    with pytest.raises(UnresolvedInputError):
        conduit.meld(spell=Worker)


def test_repeat_world_is_a_full_hit_that_leaves_the_bundle_untouched() -> None:
    """
    Purpose: The stamp never turns an unchanged world into a miss.
    Contract: Conjuring the same world again (same ids, posture and borrowed set) does not rewrite the bundle
        file, the persisted envelope carries the stamp, and the consumer melds with its existing provider.
    """
    fragment = _fresh_cache_fragment("_cache_world_stamp_repeat")
    book, _conduit = _conjure_world("world-stamp-repeat", fragment, Service())
    path = _bundle(book).bundle_path
    written = (path.read_bytes(), path.stat().st_mtime_ns)
    persisted = marshal.loads(path.read_bytes())
    assert persisted["world_stamp"] == StructuralSnapshot.world_stamp(book)

    service = Service()
    _book, conduit = _conjure_world("world-stamp-repeat", fragment, service)

    assert (path.read_bytes(), path.stat().st_mtime_ns) == written
    assert conduit.meld(spell=Worker).service is service


def test_generation_19_retires_bundles_without_a_world_stamp() -> None:
    """
    Purpose: The history pins the generation that introduced the envelope field.
    Contract: Generation 19 is `executor_world_stamp` and the current version is at least 19.
    """
    assert CachingSystem.CACHE_VERSION_HISTORY[19] == "executor_world_stamp"
    assert CachingSystem.CURRENT_VERSION >= 19
