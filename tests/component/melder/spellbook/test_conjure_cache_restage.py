"""
Regression contracts: a conduit cache bundle always holds one consistent world.

A consumer's cached manifest names its providers' spell ids. Before generation 12, a non-full-hit conjure
staged only the MISSING payloads, so after a provider's id changed the consumer kept a plan naming the old id;
the next full hit failed at the consumer's first meld ("generalized manifest references unknown spell_id"),
and ids that were no longer live stayed in the bundle forever. Each "world" here is a fresh Aether - the
in-process stand-in for a new process - that reuses the same frame, conduit name and cache directory.
"""

import inspect
import shutil
import types
from pathlib import Path
from typing import Callable, Iterator, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.aetheric_frame.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.conduit.conduit import Conduit
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


def _world_classes(variant: str) -> Tuple[type, type]:
    """
    Build a provider/consumer pair whose provider constructor depends on `variant`.

    Both classes carry the same qualname in every variant, so only the provider's constructor signature -
    and therefore only the provider's spell id - differs between variants A and B.
    """
    if variant == "A":
        class Engine:
            def __init__(self) -> None:
                self.variant = "A"
    else:
        class Engine:
            def __init__(self, size: int = 2) -> None:
                self.variant = "B"

    class Car:
        def __init__(self, engine: Engine) -> None:
            self.engine = engine

    Engine.__qualname__ = "Engine"
    Car.__qualname__ = "Car"
    return Engine, Car


def _conjure_variant(frame: str, cache_fragment: Path, variant: str) -> Tuple[Spellbook, Conduit, type, str, str]:
    """Bind the variant's Engine (unique) and Car (many) in a fresh world and conjure it."""
    engine_cls, car_cls = _world_classes(variant)
    book = _new_world_book(frame, cache_fragment)
    engine_id = book.bind(spell=engine_cls, existence="unique", permissions="create")
    car_id = book.bind(spell=car_cls, existence="many", permissions="create")
    conduit = book.conjure(name="root")
    return book, conduit, car_cls, engine_id, car_id


def _bundle(book: Spellbook) -> CachingSystem:
    """Return the Book's cache utility."""
    return book._get_or_create_caching_system()


def test_provider_id_change_never_breaks_the_consumer_on_a_later_full_hit() -> None:
    """
    Purpose: Regression for "generalized manifest references unknown spell_id" after a provider edit.
    Contract: Worlds A, B, B, B all meld the consumer with the current provider.
    """
    fragment = _fresh_cache_fragment("_cache_restage_provider_change")

    for variant in ("A", "B", "B", "B"):
        _book, conduit, car_cls, _engine_id, _car_id = _conjure_variant("restage-provider", fragment, variant)
        car = conduit.meld(spell=car_cls)
        assert car.engine.variant == variant


def test_non_full_hit_conjure_rewrites_the_bundle_to_the_live_spells() -> None:
    """
    Purpose: The bundle equals the current world after a conjure that did not fully hit.
    Contract: The old provider id is dropped; the consumer's payload names the new provider id.
    """
    fragment = _fresh_cache_fragment("_cache_restage_live_set")
    _conjure_variant("restage-live", fragment, "A")
    book, _conduit, _car_cls, engine_id, car_id = _conjure_variant("restage-live", fragment, "B")

    bundle = _bundle(book)

    assert set(bundle.cached_spell_ids) == {engine_id, car_id}
    assert engine_id in str(bundle.get_spell_payload(car_id))


def test_repeat_world_is_a_full_hit_and_leaves_the_bundle_untouched() -> None:
    """
    Purpose: The rewrite happens only when the world changed.
    Contract: Conjuring the same world again does not rewrite the bundle file, and the consumer melds.
    """
    fragment = _fresh_cache_fragment("_cache_restage_full_hit")
    book, _conduit, _car_cls, _engine_id, _car_id = _conjure_variant("restage-hit", fragment, "B")
    path = _bundle(book).bundle_path
    written = (path.read_bytes(), path.stat().st_mtime_ns)

    _book, conduit, car_cls, _engine_id, _car_id = _conjure_variant("restage-hit", fragment, "B")

    assert (path.read_bytes(), path.stat().st_mtime_ns) == written
    assert conduit.meld(spell=car_cls).engine.variant == "B"


def _function_world(frame: str, cache_fragment: Path, factory: Callable[..., object]) -> Tuple[Spellbook, type]:
    """Bind a function provider (spellframe = its product type) and a class consumer, then conjure."""
    product = factory.__annotations__["return"]

    class Consumer:
        def __init__(self, product: product) -> None:
            self.product = product

    Consumer.__qualname__ = "Consumer"
    book = _new_world_book(frame, cache_fragment)
    book.bind(spell=factory, spellframe=product, existence="unique", permissions="create")
    book.bind(spell=Consumer, existence="many", permissions="create")
    book.conjure(name="root")
    return book, Consumer


class _Product:
    """Product built by the function provider."""


def _make_product() -> _Product:
    """Function provider."""
    return _Product()


def _clone(function: types.FunctionType) -> types.FunctionType:
    """Return a distinct function object (new address) with the same code, name and annotations."""
    clone = types.FunctionType(function.__code__, function.__globals__, function.__name__, function.__defaults__)
    clone.__qualname__ = function.__qualname__
    clone.__annotate__ = function.__annotate__
    return clone


def test_function_provider_book_reaches_a_full_hit_in_the_next_world() -> None:
    """
    Purpose: Regression for function spells defeating the cache (new id per process, bundle growth).
    Contract: A second world with a different function object of the same content full-hits: the bundle
        file is not rewritten and still holds exactly two payloads.
    """
    fragment = _fresh_cache_fragment("_cache_restage_function_provider")
    book, _consumer = _function_world("restage-function", fragment, _make_product)
    path = _bundle(book).bundle_path
    written = (path.read_bytes(), path.stat().st_mtime_ns)

    book, consumer = _function_world("restage-function", fragment, _clone(_make_product))

    assert (path.read_bytes(), path.stat().st_mtime_ns) == written
    assert len(_bundle(book).cached_spell_ids) == 2
    assert isinstance(book._conduit.meld(spell=consumer).product, _Product)
