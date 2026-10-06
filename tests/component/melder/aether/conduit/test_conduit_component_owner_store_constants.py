"""
Component tests of owner-store constants (S9, 2026-10-03) through real conjures.

Scope:
    A Worker over a `unique` Service is melded through a real Conduit in both postures and on a creation-cache
    full hit. In the automatic world the normal plan emitted at hydration binds the Service's owner store as a
    namespace constant and reads no `spells[i]._owner_creations` per creation; a full hit of the same world
    binds the live world's store, never a recorded one; in the dynamic world (ownership transfer can repoint
    the store) the per-creation read is kept. Every world returns one Service object across melds.
"""

import inspect
import shutil
from pathlib import Path
from typing import Any, Dict, Iterator, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.aetheric_frame.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_lowering import (
    SitePlanLowering,
)
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from tests._frame_posture_test_support import (
    configure_frame_posture_for_spellbook_configuration,
)


class Service:
    """The unique provider."""

    def __init__(self) -> None:
        self.calls = 0


class Worker:
    """Transient root over the unique Service."""

    def __init__(self, service: Service) -> None:
        self.service = service


def _reset_world() -> None:
    """Replace the process singletons with a fresh Aether and Nexus, as the cache component tests do."""
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def isolated_worlds() -> Iterator[None]:
    """Fresh worlds before and after each case."""
    _reset_world()
    yield
    _reset_world()


@pytest.fixture
def captured_plans(monkeypatch: pytest.MonkeyPatch) -> Dict[str, Tuple[str, Dict[str, Any]]]:
    """Record every normal plan's (source, namespace) by root spell id as the lowering emits it."""
    captured: Dict[str, Tuple[str, Dict[str, Any]]] = {}
    original = SitePlanLowering.emit.__func__

    def capturing(cls: type, **kwargs: Any) -> Any:
        result = original(cls, **kwargs)
        if kwargs.get("normal_mode"):
            captured[kwargs["root_spell_id"]] = (result[0], result[1])
        return result

    monkeypatch.setattr(SitePlanLowering, "emit", classmethod(capturing))
    return captured


def _spellbook(dynamic: bool) -> Spellbook:
    """A Spellbook in the requested posture with the conjure cache off."""
    configuration = SpellbookConfiguration()
    configuration.load_default_dictionary()
    configure_frame_posture_for_spellbook_configuration(configuration, dynamic=dynamic)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook = Spellbook(configuration=configuration)
    spellbook.configure_aether_frame(
        system_state="dynamic" if dynamic else None, disposal=None, disposal_method_names=None,
        system_caching_enabled=False,
    )
    return spellbook


def _bind_world(dynamic: bool) -> Tuple[Spellbook, str, str]:
    """Bind Service (unique) and Worker (many); return (spellbook, service_id, worker_id)."""
    spellbook = _spellbook(dynamic)
    service_id = spellbook.bind(spell=Service, existence=Existence.unique, permissions="create")
    worker_id = spellbook.bind(spell=Worker, existence=Existence.many, permissions="create")
    return spellbook, service_id, worker_id


def test_automatic_world_binds_the_owner_store_and_reuses_the_service(captured_plans: Dict[str, Any]) -> None:
    """The normal plan reads no `spells[i]._owner_creations`; `c0` is the Service's owner store; one Service."""
    spellbook, service_id, worker_id = _bind_world(dynamic=False)
    conduit = spellbook.conjure(name="s9-owner-store-root", dynamic=False)
    try:
        first = conduit.meld(spell_id=worker_id)
        second = conduit.meld(spell_id=worker_id)
        assert isinstance(first, Worker) and first is not second
        assert first.service is second.service and isinstance(first.service, Service)
        source, namespace = captured_plans[worker_id]
        assert "._owner_creations" not in source
        service_spell = spellbook._spell_id_pool[service_id]
        assert namespace["c0"] is service_spell._owner_creations
        assert namespace["c0"]._creations[service_id] is first.service
    finally:
        conduit.cleanup()
        spellbook.cleanup()


def test_dynamic_world_keeps_the_per_creation_owner_store_read(captured_plans: Dict[str, Any]) -> None:
    """A dynamic conduit's plan reads the owner store per creation (transfer may repoint it); same Service."""
    spellbook, _service_id, worker_id = _bind_world(dynamic=True)
    conduit = spellbook.conjure(name="s9-owner-store-dynamic-root", dynamic=True)
    try:
        first = conduit.meld(spell_id=worker_id)
        second = conduit.meld(spell_id=worker_id)
        assert first.service is second.service
        source, namespace = captured_plans[worker_id]
        assert "    c0 = spells[0]._owner_creations" in source
        assert "c0" not in namespace
    finally:
        conduit.cleanup()
        spellbook.cleanup()


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


def _cached_world(frame: str, cache_fragment: Path) -> Tuple[Spellbook, Conduit, str, str]:
    """A fresh automatic world with caching on under the fragment; Service (unique) and Worker (many) conjured."""
    _reset_world()
    configuration = Aether()._ensure_frame(frame).frame_configuration
    configuration.with_system_caching_enabled(True)
    configuration.with_system_cache_root_path(cache_fragment)
    spellbook = Spellbook(aetheric_frame=frame)
    spellbook.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    service_id = spellbook.bind(spell=Service, existence=Existence.unique, permissions="create")
    worker_id = spellbook.bind(spell=Worker, existence=Existence.many, permissions="create")
    conduit = spellbook.conjure(name="s9-owner-store-cached-root")
    return spellbook, conduit, service_id, worker_id


def test_cache_full_hit_binds_the_live_worlds_owner_store(captured_plans: Dict[str, Any]) -> None:
    """A repeat world hydrated from the bundle binds `c0` to ITS Service spell's store and builds its own Service."""
    fragment = _fresh_cache_fragment("_cache_owner_store_constants")
    spellbook, conduit, _service_id, worker_id = _cached_world("s9-owner-store-cached", fragment)
    first_world_service = conduit.meld(spell_id=worker_id).service
    path = spellbook._get_or_create_caching_system().bundle_path
    written = (path.read_bytes(), path.stat().st_mtime_ns)
    conduit.cleanup()
    spellbook.cleanup()

    spellbook, conduit, service_id, worker_id = _cached_world("s9-owner-store-cached", fragment)
    try:
        # The repeat world is a full hit: the bundle is left untouched (the restage contracts' witness).
        assert (path.read_bytes(), path.stat().st_mtime_ns) == written
        first = conduit.meld(spell_id=worker_id)
        second = conduit.meld(spell_id=worker_id)
        assert first.service is second.service and first.service is not first_world_service
        source, namespace = captured_plans[worker_id]
        assert "._owner_creations" not in source
        assert namespace["c0"] is spellbook._spell_id_pool[service_id]._owner_creations
        assert namespace["c0"]._creations[service_id] is first.service
    finally:
        conduit.cleanup()
        spellbook.cleanup()
