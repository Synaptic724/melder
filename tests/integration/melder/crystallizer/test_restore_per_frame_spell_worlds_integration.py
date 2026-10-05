"""
Integration tests: per-frame spell-id worlds record and restore intact (0.2.8214).

WHY THIS EXISTS. Measured on 0.2.8212: under per-frame spell ids the same class bound in two frames recorded ONE
spell crystal - custody was keyed by the spell id alone, so the second frame's bind displaced the first frame's
copy - and the restore reported "complete" over a frame that came back empty. Custody is now keyed
"<spell_id>@<frame>" under per-frame ids (the bare spell id under process-wide ids), the Aether twin carries the
regime (0.2.8213), and restore rebuilds each Book's own copy.

Contract under test:
    1. the same class in two frames records one custody entry per frame and restores both bindings, their parked
       members and their selections in their own Books, under per-frame ids;
    2. a per-frame world with distinct classes restores per-frame;
    3. a process-wide world keeps bare spell-id keys and restores as before;
    4. a host running process-wide ids refuses a same-class per-frame record before building anything;
    5. removing a spell in one frame removes only that frame's custody.

Runs only on 3.14t (melder package root import chain).
"""
from typing import Dict, List, Optional, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_configuration import AetherConfiguration
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.configuration.crystallizer_configuration import CrystallizerConfiguration
from melder.crystallizer.crystallizer import Crystallizer
from melder.nexus.nexus import Nexus


class TenantService:
    """Importable restore target bound in both tenant frames."""

    def __init__(self) -> None:
        """Initialize the marker service."""
        self.alive: bool = True


class TenantServiceNext:
    """Importable second version of the tenant service, parked in each tenant's index."""

    def __init__(self) -> None:
        """Initialize the marker service."""
        self.alive: bool = True


class OtherService:
    """Importable restore target bound only in tenant_b (the distinct-class world)."""

    def __init__(self) -> None:
        """Initialize the marker service."""
        self.alive: bool = True


def _reset_world() -> None:
    """Reset every world singleton and rebind the static Aether references, as a new process would start."""
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def reset_world_singletons():
    """Isolate each test behind fresh Aether/Nexus/Crystallizer singletons."""
    _reset_world()
    yield
    _reset_world()


@pytest.fixture()
def cache_root(tmp_path, monkeypatch):
    """Route the crystallizer cache into a per-test directory."""
    from melder.crystallizer.asset_management import crystallizer_cache

    root = tmp_path / "__melder_cache__" / "__crystallizer_cache__"
    monkeypatch.setattr(
        crystallizer_cache.CrystallizerCache,
        "resolve_cache_root_path",
        staticmethod(lambda: root),
    )
    return root


def _install_regime(process_wide: bool) -> None:
    """Configure and activate the live Aether with one spell-id regime before any frame exists."""
    policy = AetherConfiguration().with_defaults().with_process_wide_unique_spell_ids(process_wide)
    policy.activate()
    Aether().activate(policy)


def _activate_crystallizer() -> Crystallizer:
    """Activate the Aether-hosted crystallizer with default knobs."""
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.activate()
    crystallizer = Crystallizer()
    crystallizer.activate(configuration)
    return crystallizer


def _tenant_book(frame: str, service: type, root_name: str) -> Tuple[Spellbook, Conduit, str]:
    """
    Build one tenant: a Book in a frame postured dynamic before its bind, one bind, one named dynamic conjure.

    configure_aether_frame is the public pre-settlement door the recorded lane needs: it settles the frame dynamic
    and freezes the Book's configuration, so the bind records and the conjure passes the recorded-world discipline.
    """
    book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    book.configure_aether_frame(system_state="dynamic", disposal=None, disposal_method_names=None)
    spell_id = book.bind(spell=service, existence="many")
    conduit = book.conjure(name=root_name, dynamic=True)
    return book, conduit, spell_id


def _park_next_version(book: Spellbook, conduit: Conduit, spell_id: str) -> str:
    """Stage TenantServiceNext as a parked member of the tenant service's index; return its spell id."""
    index = book.find_spell_by_id(spell_id).spell_index
    return conduit.bind_inactive(spell=TenantServiceNext, spell_index=index, existence="many")


def _record(crystallizer: Crystallizer) -> str:
    """Seal and flush one checkpoint of the current world; return its id."""
    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)
    return checkpoint_id


def _custody_keys(crystallizer: Crystallizer, checkpoint_id: str) -> List[str]:
    """Return the sorted custody keys one sealed checkpoint carries."""
    return sorted(crystallizer.checkpoint_replay_data(checkpoint_id)["payloads"]["spell_crystal"])


def _restore_in_a_fresh_world(checkpoint_id: str) -> Tuple[Crystallizer, Dict[str, object]]:
    """Reset the world as a new process would, reload the flushed checkpoint and restore it."""
    _reset_world()
    rebooted = _activate_crystallizer()
    rebooted.reload_cached_checkpoint(checkpoint_id)
    return rebooted, rebooted.load_checkpoint(checkpoint_id)


def _live_book(frame: str, root_name: str) -> Spellbook:
    """Return the restored Book of one tenant through its named root conduit."""
    return Aether().get_conduit_by_name(root_name, aetheric_frame_name=frame).spellbook


def _messages(error: BaseException) -> List[str]:
    """Return the messages of one exception and its chained causes."""
    messages: List[str] = []
    current: Optional[BaseException] = error
    while current is not None:
        messages.append(str(current))
        current = current.__cause__ or current.__context__
    return messages


def test_same_class_in_two_frames_restores_both_tenants_under_per_frame_ids(cache_root) -> None:
    """
    Purpose:
        The multi-tenant shape per-frame ids exist for survives a record and a fresh restore.
    Contract:
        The record keeps one custody entry per frame for each version (four keys "<spell_id>@<frame>"); the restore
        completes with both active bindings and both parked members rebuilt in their own Books and no custody
        shortfall; tenant_a keeps the version it notched and tenant_b its own; per-frame ids are in force; the rebuilt
        world re-records per-frame keys.
    """
    _install_regime(False)
    crystallizer = _activate_crystallizer()
    book_a, conduit_a, tenant_id = _tenant_book("tenant_a", TenantService, "root_a")
    book_b, conduit_b, tenant_id_b = _tenant_book("tenant_b", TenantService, "root_b")
    assert tenant_id_b == tenant_id
    next_id = _park_next_version(book_a, conduit_a, tenant_id)
    assert _park_next_version(book_b, conduit_b, tenant_id) == next_id
    conduit_a.notch_spell(
        spell_index=book_a.find_spell_by_id(tenant_id).spell_index,
        spell=book_a._inactive_spells[next_id],
    )
    checkpoint_id = _record(crystallizer)
    assert _custody_keys(crystallizer, checkpoint_id) == sorted([
        f"{tenant_id}@tenant_a", f"{tenant_id}@tenant_b", f"{next_id}@tenant_a", f"{next_id}@tenant_b",
    ])

    rebooted, report = _restore_in_a_fresh_world(checkpoint_id)

    assert report["status"] == "complete"
    assert report["built_counts"]["spell_active"] == 2
    assert report["built_counts"]["spell_staged"] == 2
    assert [entry for entry in list(report["shortfalls"]) if entry["kind"] == "spell_crystal"] == []
    assert Aether().process_wide_unique_spell_ids is False
    index_a = _live_book("tenant_a", "root_a").find_spell_by_id(tenant_id).spell_index
    index_b = _live_book("tenant_b", "root_b").find_spell_by_id(tenant_id).spell_index
    assert index_a.selected_spell_id == next_id
    assert index_b.selected_spell_id == tenant_id
    assert rebooted.get_spell_crystal(tenant_id, frame_name="tenant_b").custody_key == f"{tenant_id}@tenant_b"


def test_per_frame_world_with_distinct_classes_restores_per_frame(cache_root) -> None:
    """
    Purpose:
        A per-frame world restored in a fresh process runs per-frame ids again (the recorded regime, 0.2.8213).
    Contract:
        The restore completes with both bindings; binding tenant_a's class into tenant_b afterwards is accepted, as
        it was in the recorded world (under process-wide ids it collides).
    """
    _install_regime(False)
    crystallizer = _activate_crystallizer()
    _tenant_book("tenant_a", TenantService, "root_a")
    _tenant_book("tenant_b", OtherService, "root_b")
    checkpoint_id = _record(crystallizer)

    _rebooted, report = _restore_in_a_fresh_world(checkpoint_id)

    assert report["status"] == "complete"
    assert report["built_counts"]["spell_active"] == 2
    assert Aether().process_wide_unique_spell_ids is False
    follow_up = Spellbook(
        aetheric_frame="tenant_b",
        configuration=SpellbookConfiguration("tenant_b").with_defaults().finalize(),
    )
    assert follow_up.bind(spell=TenantService, existence="many")


def test_process_wide_world_keeps_bare_custody_keys(cache_root) -> None:
    """
    Purpose:
        Worlds under the default regime keep their record shape.
    Contract:
        Custody keys are bare spell ids; the restore completes with both bindings; the rebuilt world runs
        process-wide ids and re-records bare keys.
    """
    crystallizer = _activate_crystallizer()
    _book_a, _conduit_a, tenant_id = _tenant_book("tenant_a", TenantService, "root_a")
    _book_b, _conduit_b, other_id = _tenant_book("tenant_b", OtherService, "root_b")
    checkpoint_id = _record(crystallizer)
    assert _custody_keys(crystallizer, checkpoint_id) == sorted([tenant_id, other_id])

    rebooted, report = _restore_in_a_fresh_world(checkpoint_id)

    assert report["status"] == "complete"
    assert report["built_counts"]["spell_active"] == 2
    assert Aether().process_wide_unique_spell_ids is True
    assert rebooted.get_spell_crystal(tenant_id).custody_key == tenant_id


def test_process_wide_host_refuses_a_same_class_per_frame_record(cache_root) -> None:
    """
    Purpose:
        A record only per-frame ids can hold is refused, not half-built, by a host running process-wide ids.
    Contract:
        load_checkpoint raises at stage aether_configuration with a cause naming the two-frame binding; no tenant
        frame is born.
    """
    _install_regime(False)
    crystallizer = _activate_crystallizer()
    _tenant_book("tenant_a", TenantService, "root_a")
    _tenant_book("tenant_b", TenantService, "root_b")
    checkpoint_id = _record(crystallizer)

    _reset_world()
    _install_regime(True)
    rebooted = _activate_crystallizer()
    rebooted.reload_cached_checkpoint(checkpoint_id)
    with pytest.raises(RuntimeError) as raised:
        rebooted.load_checkpoint(checkpoint_id)

    messages = _messages(raised.value)
    assert any("aether_configuration" in message for message in messages)
    assert any("two frames" in message for message in messages)
    assert "tenant_a" not in Aether().list_frame_names()
    assert "tenant_b" not in Aether().list_frame_names()


def test_removing_a_spell_in_one_frame_keeps_the_other_frames_custody(cache_root) -> None:
    """
    Purpose:
        True removal in one tenant must not take the other tenant's recorded binding with it.
    Contract:
        After tenant_a removes the tenant service, the record holds tenant_b's copy and no longer tenant_a's.
    """
    _install_regime(False)
    crystallizer = _activate_crystallizer()
    book_a, _conduit_a, tenant_id = _tenant_book("tenant_a", TenantService, "root_a")
    _tenant_book("tenant_b", TenantService, "root_b")
    book_a.cleanup_and_remove_spell(tenant_id)

    assert crystallizer.describe_profile()["spell_crystal_count"] == 1
    assert crystallizer.get_spell_crystal(tenant_id, frame_name="tenant_b").frame_name == "tenant_b"
    with pytest.raises(KeyError):
        crystallizer.get_spell_crystal(tenant_id, frame_name="tenant_a")
