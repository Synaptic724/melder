"""
Integration: a managed spell's options survive a crystallizer record and restore, and a spell-index graft
(STORY-2026-10-15-managed_bind_options, S2; record 4.2.0).

The crystal records the four options of a managed spell; the restore engine and the graft runner replay them
through bind, so each rebuilt version gets the same normalized options, and the same spell id, as the recorded one.
An active member and a parked member are covered on both lanes; the parked member differs by its disposal names,
since a managed spell's settings are not part of its spell_id (0.2.8254). Managed spells are not melded here:
dispensing arrives with STORY-2026-10-15-managed_dispense_codegen (S5).

Runs only on 3.14t (melder package root import chain).
"""
from collections.abc import Iterator
from typing import Any, Dict

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.configuration.crystallizer_configuration import CrystallizerConfiguration
from melder.crystallizer.crystallizer import Crystallizer
from melder.nexus.nexus import Nexus
from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration


class RecordedPool:
    """Managed target; module-scoped so a restore can import it by qualname."""

    def reset(self) -> None:
        """Clear per-holder state."""

    def flush(self) -> None:
        """Write out buffered lines."""


class RecordedAnchor:
    """A plain unique spell so the recorded root has an ordinary member too."""


ACTIVE_OPTIONS: Dict[str, Any] = {
    "managed_spell_mode": "queue",
    "managed_spell_limit": 3,
    "managed_spell_timeout_seconds": 0.75,
    "managed_spell_reset_methods": ["reset", "flush"],
}
PARKED_OPTIONS: Dict[str, Any] = {
    "managed_spell_mode": "limited_quantity",
    "managed_spell_limit": 5,
    "managed_spell_timeout_seconds": None,
    "managed_spell_reset_methods": ["flush"],
}


def _reset_world() -> None:
    """Fresh Aether, utility system, Nexus and Crystallizer singletons."""
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def reset_world_singletons() -> Iterator[None]:
    """Isolate each test behind fresh singletons."""
    _reset_world()
    yield
    _reset_world()


@pytest.fixture()
def cache_root(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> Any:
    """Route the crystallizer cache into a per-test directory."""
    from melder.crystallizer.asset_management import crystallizer_cache

    root = tmp_path / "__melder_cache__" / "__crystallizer_cache__"
    monkeypatch.setattr(
        crystallizer_cache.CrystallizerCache, "resolve_cache_root_path", staticmethod(lambda: root),
    )
    return root


def _activate_crystallizer() -> Crystallizer:
    """Activate the Aether-hosted crystallizer with default knobs."""
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.activate()
    crystallizer = Crystallizer()
    crystallizer.activate(configuration)
    return crystallizer


def _dynamic_book(frame: str = "default") -> Spellbook:
    """One dynamic-posture Spellbook with its configuration finalized first."""
    configuration = SpellbookConfiguration(aether_frame=frame)
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.finalize()
    return Spellbook(aetheric_frame=frame, configuration=configuration)


def _record_world() -> tuple:
    """Bind an anchor and an active managed spell, conjure, park a second managed version; return the ids."""
    book = _dynamic_book()
    book.bind(spell=RecordedAnchor, existence=Existence.unique)
    active_id = book.bind(spell=RecordedPool, existence=Existence.managed_spell_quantity, **ACTIVE_OPTIONS)
    root = book.conjure(dynamic=True, name="root")
    parked_id = root.bind_inactive(
        spell=RecordedPool, spell_index=book.find_spell_by_spell_id(active_id).spell_index,
        existence=Existence.managed_spell_quantity, disposal_method_names=["flush"], **PARKED_OPTIONS,
    )
    return book, root, active_id, parked_id


def _assert_options(spell: Any, options: Dict[str, Any]) -> None:
    """The live Spell carries exactly the recorded options."""
    assert spell.existence is Existence.managed_spell_quantity
    assert spell.managed_spell_mode is ManagedSpellMode[options["managed_spell_mode"]]
    assert spell.managed_spell_limit == options["managed_spell_limit"]
    assert spell.managed_spell_timeout_seconds == options["managed_spell_timeout_seconds"]
    assert spell.managed_spell_reset_methods == tuple(options["managed_spell_reset_methods"])


def test_the_crystal_records_both_versions_options(cache_root: Any) -> None:
    """The active and the parked versions each carry their own recorded options."""
    crystallizer = _activate_crystallizer()
    _book, _root, active_id, parked_id = _record_world()
    assert crystallizer.get_spell_crystal(active_id).managed_spell_options == ACTIVE_OPTIONS
    assert crystallizer.get_spell_crystal(parked_id).managed_spell_options == PARKED_OPTIONS


def test_a_restore_rebinds_both_versions_with_their_options(cache_root: Any) -> None:
    """After a restart the rebuilt active and parked versions keep their options and their spell ids."""
    crystallizer = _activate_crystallizer()
    _book, _root, active_id, parked_id = _record_world()
    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)

    _reset_world()
    rebooted = _activate_crystallizer()
    rebooted.reload_cached_checkpoint(checkpoint_id)
    report = rebooted.load_checkpoint(checkpoint_id)

    assert report["status"] == "complete"
    assert [entry for entry in report["shortfalls"] if entry["kind"] == "spell_crystal"] == []
    book = Aether().get_root_conduit_by_name("root").spellbook
    _assert_options(book.find_spell_by_spell_id(active_id), ACTIVE_OPTIONS)
    _assert_options(book._get_owned_spell(parked_id), PARKED_OPTIONS)


def test_a_graft_rebinds_the_selected_and_parked_versions_with_their_options(cache_root: Any) -> None:
    """The spell-index graft carries the options of both members into a host Book in another frame."""
    crystallizer = _activate_crystallizer()
    source_book, source_root, active_id, parked_id = _record_world()
    record = crystallizer.capture_index_graft(source_book.find_spell_by_spell_id(active_id).spell_index.id)
    assert record["members"][active_id]["payload"]["managed_spell_mode"] == "queue"
    assert record["members"][parked_id]["payload"]["managed_spell_mode"] == "limited_quantity"
    # Process-wide spell ids: release the source's claim before grafting the same ids into another frame.
    source_root.cleanup()
    source_book.cleanup()

    host_book = _dynamic_book("managed-graft-host")
    host_book.conjure(dynamic=True, name="graft-host")
    report = crystallizer.graft_index(record, host_book)

    # A fresh-index graft binds the selected member and parks the rest (GraftRunner.run's report contract).
    assert report["status"] == "complete"
    assert report["members_bound"] == 1
    assert report["members_parked"] == 1
    assert report["shortfalls"] == []
    _assert_options(host_book.find_spell_by_spell_id(active_id), ACTIVE_OPTIONS)
    _assert_options(host_book._get_owned_spell(parked_id), PARKED_OPTIONS)
