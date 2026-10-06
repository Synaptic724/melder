"""
Integration: a Protocol spellframe survives a restore as a CONTRACT, not as a same-named category.

Restore and graft rebind spells by the frame NAME the crystal recorded. Since 2026-10-04 Phase 3 matches by
kind - a category never satisfies an annotation - so a Protocol frame rebound as a string would strand every
Protocol-typed consumer of the restored world. The crystal now records `spellframe_kind` and the Protocol's
module coordinates (record 4.1.0); the loaders hydrate the Protocol through the import lane and, when it
cannot be imported, bind the recorded name as a category and file a shortfall that says so.

Runs only on 3.14t (melder package root import chain).
"""
import sys
import types
from typing import Protocol

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.spellbook.spellframe_kind.spellframe_kind import SpellframeKind
from melder.crystallizer.configuration.crystallizer_configuration import (
    CrystallizerConfiguration,
)
from melder.crystallizer.crystallizer import Crystallizer
from melder.nexus.nexus import Nexus
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)


class IRestoreService(Protocol):
    """
    The contract the provider is bound under; module-scoped so a restore can import it by qualname.
    """

    def serve(self) -> str:
        """Return a marker."""
        ...


class RestoreServiceImpl:
    """
    Provider bound under the `IRestoreService` contract; module-scoped for hydration.
    """

    def serve(self) -> str:
        """Return the provider's marker."""
        return "served"


class RestoreServiceClient:
    """
    Consumer typed with the contract; module-scoped for hydration.
    """

    def __init__(self, svc: IRestoreService) -> None:
        """Hold the injected provider."""
        self.svc = svc


@pytest.fixture(autouse=True)
def reset_world_singletons():
    """
    Purpose:
        Isolate each test behind fresh Aether/Nexus/Crystallizer singletons.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture()
def cache_root(tmp_path, monkeypatch):
    """
    Route the crystallizer cache into a per-test directory.
    Returns:
        Path: The isolated cache root.
    """
    from melder.crystallizer.asset_management import crystallizer_cache

    root = tmp_path / "__melder_cache__" / "__crystallizer_cache__"
    monkeypatch.setattr(
        crystallizer_cache.CrystallizerCache,
        "resolve_cache_root_path",
        staticmethod(lambda: root),
    )
    return root


def _activate_crystallizer() -> Crystallizer:
    """Activate the Aether-hosted crystallizer with default knobs."""
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.activate()
    crystallizer = Crystallizer()
    crystallizer.activate(configuration)
    return crystallizer


def _dynamic_book() -> Spellbook:
    """Build one dynamic-posture Spellbook with its configuration finalized first."""
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.finalize()
    return Spellbook(configuration=configuration)


def _fresh_boot() -> Crystallizer:
    """Simulate a process restart and return the fresh activated crystallizer."""
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    return _activate_crystallizer()


def _restored_root() -> Conduit:
    """Return the rebuilt root conduit named "root" on the default frame."""
    return Aether().get_root_conduit_by_name("root")


def test_protocol_frame_restores_as_a_contract_and_its_consumer_resolves(cache_root) -> None:
    """
    Purpose:
        A provider bound under a Protocol frame is rebound under that Protocol after a restore, so the
        consumer typed with the Protocol resolves it exactly as in the recorded world.
    Contract:
        - The crystal carries kind "contract" and the Protocol's coordinates.
        - The report completes with no spell-crystal shortfall; the rebuilt spell's kind is `contract`.
        - Melding the consumer injects the provider.
    """
    crystallizer = _activate_crystallizer()
    book = _dynamic_book()
    provider_id = book.bind(
        spell=RestoreServiceImpl, existence=Existence.unique, permissions="create", spellframe=IRestoreService,
    )
    book.bind(spell=RestoreServiceClient, existence=Existence.many, permissions="create")
    book.conjure(dynamic=True, name="root")
    crystal = crystallizer.get_spell_crystal(provider_id)
    assert crystal.spellframe_kind == "contract"
    assert crystal.spellframe_module == IRestoreService.__module__
    assert crystal.spellframe_qualname == "IRestoreService"
    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)

    rebooted = _fresh_boot()
    rebooted.reload_cached_checkpoint(checkpoint_id)
    report = rebooted.load_checkpoint(checkpoint_id)

    assert report["status"] == "complete"
    assert [entry for entry in report["shortfalls"] if entry["kind"] == "spell_crystal"] == []
    root = _restored_root()
    rebuilt = root.meld(spellframe=IRestoreService)
    assert isinstance(rebuilt, RestoreServiceImpl)
    client = root.meld(spell=RestoreServiceClient)
    assert client.svc is rebuilt
    kinds = {entry["spell_name"]: entry for entry in root.spellbook.describe_spells_in_spellbook()}
    provider_spell = root.spellbook.find_spell_by_id(kinds["RestoreServiceImpl"]["spell_id"])
    assert provider_spell.spellframe_kind is SpellframeKind.contract
    assert provider_spell.implemented_protocols == (IRestoreService,)


def test_unimportable_protocol_frame_degrades_to_a_category_with_a_shortfall(cache_root) -> None:
    """
    Purpose:
        When the recorded Protocol cannot be imported at restore, the spell is still rebuilt - under its
        recorded NAME as a category - and the report says which spell lost its contract.
    Contract:
        - The report completes; one shortfall names `spellframe_contract_hydration_failed` and the spell.
        - The rebuilt spell has kind `category` and is addressable by the frame name.
    """
    module_name = "melder_tests_vanishing_contract_module"
    module = types.ModuleType(module_name)
    exec(
        "from typing import Protocol\n"
        "class IVanishing(Protocol):\n"
        "    def serve(self) -> str: ...\n",
        module.__dict__,
    )
    sys.modules[module_name] = module
    vanishing = module.__dict__["IVanishing"]
    try:
        crystallizer = _activate_crystallizer()
        book = _dynamic_book()
        provider_id = book.bind(
            spell=RestoreServiceImpl, existence=Existence.unique, permissions="create", spellframe=vanishing,
        )
        book.conjure(dynamic=True, name="root")
        assert crystallizer.get_spell_crystal(provider_id).spellframe_module == module_name
        checkpoint_id = crystallizer.create_checkpoint()
        crystallizer.flush_checkpoint(checkpoint_id)
    finally:
        sys.modules.pop(module_name, None)

    rebooted = _fresh_boot()
    rebooted.reload_cached_checkpoint(checkpoint_id)
    report = rebooted.load_checkpoint(checkpoint_id)

    assert report["status"] == "complete"
    reasons = [entry["reason"] for entry in report["shortfalls"] if entry["kind"] == "spell_crystal"]
    assert len(reasons) == 1
    assert reasons[0].startswith("spellframe_contract_hydration_failed (" + module_name + ".IVanishing)")
    assert "bound as the category 'IVanishing'" in reasons[0]
    root = _restored_root()
    rebuilt = root.meld(spellframe="IVanishing")
    assert isinstance(rebuilt, RestoreServiceImpl)
    kinds = {entry["spell_name"]: entry for entry in root.spellbook.describe_spells_in_spellbook()}
    provider_spell = root.spellbook.find_spell_by_id(kinds["RestoreServiceImpl"]["spell_id"])
    assert provider_spell.spellframe_kind is SpellframeKind.category
    assert provider_spell.implemented_protocols == ()


def test_index_graft_carries_the_protocol_frame_kind_into_the_host_book(cache_root) -> None:
    """
    Purpose:
        The spell-index graft lane rebinds the selected member through the same frame hydration as a
        restore: a member recorded under a Protocol frame is bound into the host book under that Protocol,
        not under a same-named category. The source world is torn down before the graft so the member's
        process-wide spell id is free for the host frame.
    Contract:
        - The graft report completes with no shortfall and a fresh live index id.
        - The grafted spell's kind is `contract` with the Protocol recorded as its implemented contract.
        - A consumer typed with the Protocol, bound on the host book, resolves the grafted member.
    """
    crystallizer = _activate_crystallizer()
    source_book = _dynamic_book()
    provider_id = source_book.bind(
        spell=RestoreServiceImpl, existence=Existence.unique, permissions="create", spellframe=IRestoreService,
    )
    source_root = source_book.conjure(dynamic=True, name="graft-source")
    recorded_index_id = source_book.find_spell_by_id(provider_id).spell_index.id
    record = crystallizer.capture_index_graft(recorded_index_id)
    assert record["graft_kind"] == "spell_index"
    assert record["members"][provider_id]["payload"]["spellframe_kind"] == "contract"
    # Release the source's claim on the id first: under process-wide spell ids a live member cannot be
    # grafted into a second frame (EPIC-2026-08-02); the lane under test is the frame hydration.
    source_root.cleanup()
    source_book.cleanup()

    host_configuration = SpellbookConfiguration(aether_frame="graft-host-frame")
    apply_dynamic_defaults_for_spellbook_configuration(host_configuration)
    host_configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    host_configuration.finalize()
    host_book = Spellbook(aetheric_frame="graft-host-frame", configuration=host_configuration)
    host_root = host_book.conjure(dynamic=True, name="graft-host")

    report = crystallizer.graft_index(record, host_book)
    assert report["status"] == "complete"
    assert report["members_bound"] == 1
    assert report["shortfalls"] == []
    assert report["live_index_id"] not in (None, recorded_index_id)
    grafted = host_book.find_spell_by_id(provider_id)
    assert grafted is not None
    assert grafted.spellframe_kind is SpellframeKind.contract
    assert grafted.implemented_protocols == (IRestoreService,)

    host_book.bind(spell=RestoreServiceClient, existence=Existence.many, permissions="create")
    client = host_root.meld(spell=RestoreServiceClient)
    assert isinstance(client.svc, RestoreServiceImpl)
    assert client.svc is host_root.meld(spellframe=IRestoreService)
