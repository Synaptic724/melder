"""Ordered disposal survives crystal capture, cached restore, and receiving-book graft policy."""

import json
from contextlib import contextmanager
from typing import Any, Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.bind.bind import Bind
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.configuration.crystallizer_configuration import CrystallizerConfiguration
from melder.crystallizer.crystal_loader_system.restore_engine import RestoreEngine
from melder.crystallizer.crystallizer import Crystallizer
from melder.nexus.nexus import Nexus
from tests.component.melder.spellbook.test_ordered_disposal_binding import (
    OrderedDisposalService,
)
from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration
from tests.integration.melder.crystallizer.test_crystallizer_restore_integration import (
    RestoreGamma,
    _activate_crystallizer,
    cache_root,
    reset_world_singletons,
)


pytestmark = pytest.mark.usefixtures("reset_world_singletons", "cache_root")


@contextmanager
def _recording_book(names: list[str], priority: bool, frame: str) -> Iterator[Spellbook]:
    """Use the existing recorded-world setup: freeze rich policy before binds, record it at conjure."""
    configuration = SpellbookConfiguration(frame)
    configuration.with_disposal_method_names(names).with_enforce_priority_disposal_methods(priority)
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.with_phase_scheduler_workers(1).finalize()
    book = Spellbook(aetheric_frame=frame, configuration=configuration)
    try:
        yield book
    finally:
        book.cleanup()


def _capture_world(priority: bool) -> tuple[dict[str, Any], str]:
    """Capture and seal two distinct bindings, then release their source book before replay."""
    crystallizer = _activate_crystallizer()
    with _recording_book(["flush", "missing", "flush"], priority, "disposal-source") as book:
        selected_id = book.bind(
            spell=OrderedDisposalService, existence="many",
            disposal_method_names=["stop", "close", "flush", "stop"],
        )
        selected = book.find_spell_by_id(selected_id)
        assert selected is not None
        book.conjure(dynamic=True, name="disposal-root")
        parked_id = book.bind_inactive(
            spell=OrderedDisposalService, spell_index=selected.spell_index,
            existence="many", disposal_method_names=["close", "flush"],
        )
        parked = book._get_owned_spell(parked_id)
        assert parked is not None
        try:
            record = json.loads(json.dumps(crystallizer.capture_index_graft(selected.spell_index.id)))
            checkpoint_id = crystallizer.create_checkpoint()
            crystallizer.flush_checkpoint(checkpoint_id)
        finally:
            book.cleanup_spell(spell=parked)
    return record, checkpoint_id


def _expected_identity(names: list[str]) -> str:
    """Compute the expected content ID from an explicit expected final order, without book policy."""
    return Bind.spell_id_inspector(
        OrderedDisposalService,
        spell_name="OrderedDisposalService",
        existence=Existence.many,
        disposal_method_names=names,
    )


def _fresh_recorder(parallel: bool) -> Crystallizer:
    """Use the suite's fresh-boot sequence with an explicit sequential/parallel loader choice."""
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    Spellbook._aether = Aether()
    Conduit._aether = Spellbook._aether
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.set_property("restore_parallel_enabled", parallel)
    configuration.activate()
    crystallizer = Crystallizer()
    crystallizer.activate(configuration)
    return crystallizer


@pytest.mark.parametrize("priority", [False, True])
def test_crystal_and_json_preserve_distinct_member_orders(priority: bool) -> None:
    """Custody keeps non-alphabetical spell-only order and the staged member's distinct policy."""
    record, _checkpoint_id = _capture_world(priority)
    selected_id = record["index_payload"]["selected_spell_id"]
    parked_id = next(member for member in record["members"] if member != selected_id)
    selected_names = ["flush", "stop", "close"] if priority else ["stop", "close", "flush"]
    parked_names = ["flush", "close"] if priority else ["close", "flush"]
    assert record["members"][selected_id]["payload"]["disposal_method_names"] == selected_names
    assert record["members"][parked_id]["payload"]["disposal_method_names"] == parked_names
    assert selected_id == _expected_identity(selected_names)
    assert parked_id == _expected_identity(parked_names)


@pytest.mark.parametrize("priority", [False, True])
@pytest.mark.parametrize("parallel", [False, True])
def test_cached_restore_preserves_order_and_actual_cleanup(priority: bool, parallel: bool) -> None:
    """Real cache reload restores active/staged identities and cleanup under both loader drivers."""
    record, checkpoint_id = _capture_world(priority)
    rebooted = _fresh_recorder(parallel)
    rebooted.reload_cached_checkpoint(checkpoint_id)
    report = rebooted.load_checkpoint(checkpoint_id)
    assert report["status"] == "complete"
    assert report["built_counts"]["spell_active"] == 1
    assert report["built_counts"]["spell_staged"] == 1
    assert not [row for row in report["shortfalls"] if row["kind"] in ("spell_crystal", "spell_index")]
    conduit = Aether().get_conduit_by_name("disposal-root", "disposal-source")
    selected_id = record["index_payload"]["selected_spell_id"]
    parked_id = next(member for member in record["members"] if member != selected_id)
    selected_names = ["flush", "stop", "close"] if priority else ["stop", "close", "flush"]
    parked_names = ["flush", "close"] if priority else ["close", "flush"]
    selected = conduit._spellbook._get_owned_spell(selected_id)
    parked = conduit._spellbook._get_owned_spell(parked_id)
    assert selected is not None and parked is not None
    assert selected.disposal_method_names == selected_names
    assert parked.disposal_method_names == parked_names
    assert parked.spell_index is selected.spell_index
    assert selected.spell_index.selected_spell_id == selected_id
    first = conduit.meld(spell_id=selected_id)
    conduit.notch_spell(spell_index=selected.spell_index, spell=parked)
    second = conduit.meld(spell_id=parked_id)
    conduit.permanent_cleanup()
    assert first.calls == selected_names
    assert second.calls == parked_names


@pytest.mark.parametrize("priority", [False, True])
@pytest.mark.parametrize("changed_host", [False, True])
@pytest.mark.parametrize("mode", ["fresh", "merge", "merge_adopt"])
def test_graft_preserves_members_and_receiving_book_order(
        priority: bool,
        changed_host: bool,
        mode: str,
) -> None:
    """Fresh/merge grafts follow new binding IDs, with explicit selection adoption and ordered cleanup."""
    record, _checkpoint_id = _capture_world(priority)
    host_priority = not priority if changed_host else priority
    host_names = ["close", "flush"] if changed_host else ["flush"]
    if changed_host:
        selected_names = ["close", "flush", "stop"] if host_priority else ["stop", "close", "flush"]
        parked_names = ["close", "flush"]
    else:
        selected_names = ["flush", "stop", "close"] if host_priority else ["stop", "close", "flush"]
        parked_names = ["flush", "close"] if host_priority else ["close", "flush"]
    with _recording_book(host_names, host_priority, "disposal-host") as host:
        resident_id = None
        resident = None
        merge_index = None
        if mode != "fresh":
            resident_id = host.bind(spell=RestoreGamma, existence="many")
            resident = host.find_spell_by_id(resident_id)
            assert resident is not None
            merge_index = resident.spell_index
        conduit = host.conjure(dynamic=True)
        report = Crystallizer().graft_index(
            record, host, merge_into_index=merge_index,
            adopt_recorded_selection=mode == "merge_adopt",
        )
        assert report["shortfalls"] == []
        assert report["members_bound"] == (1 if mode == "fresh" else 0)
        assert report["members_parked"] == (1 if mode == "fresh" else 2)
        selected_id = _expected_identity(selected_names)
        parked_id = _expected_identity(parked_names)
        selected = host._get_owned_spell(selected_id)
        parked = host._get_owned_spell(parked_id)
        assert selected is not None and parked is not None
        try:
            assert selected.disposal_method_names == selected_names
            assert parked.disposal_method_names == parked_names
            assert selected.spell_index is parked.spell_index
            assert report["live_index_id"] == selected.spell_index.id
            assert selected.spell_index.selected_spell_id == (resident_id if mode == "merge" else selected_id)
            if mode == "merge":
                conduit.notch_spell(spell_index=merge_index, spell=selected)
            first = conduit.meld(spell_id=selected_id)
            conduit.notch_spell(spell_index=selected.spell_index, spell=parked)
            second = conduit.meld(spell_id=parked_id)
        finally:
            # Retire inactive metadata before permanent conduit cleanup destroys
            # the index. Creations must still retain each established method list.
            for member in (selected, parked, resident):
                if (
                        member is not None
                        and not member.cleaned
                        and member.spell_index.selected_spell_id != member.spell_id
                ):
                    host.cleanup_spell(spell=member)
        conduit.permanent_cleanup()
        assert first.calls == selected_names
        assert second.calls == parked_names


@pytest.mark.parametrize("priority", [False, True])
def test_restore_changed_ids_preserves_anchor_and_exact_selected_member(priority: bool) -> None:
    """Recorded names from another policy are rebound coherently without stale anchor or selection joins."""
    record, checkpoint_id = _capture_world(not priority)
    crystallizer = Crystallizer()
    window = json.loads(json.dumps(crystallizer.checkpoint_replay_data(checkpoint_id)))
    book_payload = next(iter(window["payloads"]["spellbook"].values()))
    book_payload["configuration_payload"]["enforce_priority_disposal_methods"] = priority
    # Model the permitted selection stage explicitly: the captured inactive member
    # is the requested selection, so replay must resolve the exact parked object.
    selected_recorded = record["index_payload"]["selected_spell_id"]
    parked_recorded = next(member for member in record["members"] if member != selected_recorded)
    index_payload = window["payloads"]["spell_index"][record["index_id"]]
    index_payload["selected_spell_id"] = parked_recorded
    _fresh_recorder(False)
    engine = RestoreEngine("default", [checkpoint_id], [window])
    try:
        report = engine.restore()
        try:
            result = report.describe()
            assert result["built_counts"]["spell_staged"] == 1
            assert result["built_counts"]["selection_notch"] == 1
            selected_names = ["flush", "stop", "close"] if priority else ["stop", "close", "flush"]
            parked_names = ["flush", "close"] if priority else ["close", "flush"]
            assert result["identity_map"][selected_recorded] == _expected_identity(selected_names)
            assert result["identity_map"][parked_recorded] == _expected_identity(parked_names)
            conduit = Aether().get_conduit_by_name("disposal-root", "disposal-source")
            actual = conduit.meld("OrderedDisposalService")
            conduit.permanent_cleanup()
            assert actual.calls == parked_names
        finally:
            report.cleanup()
    finally:
        engine.cleanup()


@pytest.mark.parametrize("priority", [False, True])
def test_merge_does_not_adopt_a_skipped_resident_selection(priority: bool) -> None:
    """A skipped selected member is not reported as newly adopted from the graft."""
    record, _checkpoint_id = _capture_world(priority)
    with _recording_book(["flush"], priority, "disposal-skip-host") as host:
        resident_id = host.bind(
            spell=OrderedDisposalService, existence="many",
            disposal_method_names=["stop", "close", "flush"],
        )
        resident = host.find_spell_by_id(resident_id)
        assert resident is not None
        assert resident_id == record["index_payload"]["selected_spell_id"]
        host.conjure(dynamic=True)
        report = Crystallizer().graft_index(
            record, host, skip_resident=True, merge_into_index=resident.spell_index,
            adopt_recorded_selection=True,
        )
        assert report["members_parked"] == 1
        assert report["selection_adopted"] is False
        assert report["skipped_resident"] == [resident_id]
        assert resident.spell_index.selected_spell_id == resident_id
        assert {row["reason"] for row in report["shortfalls"]} == {
            "member_resident_in_host_skipped", "recorded_selection_not_grafted_not_adopted",
        }
        parked_id = _expected_identity(["flush", "close"] if priority else ["close", "flush"])
        parked = host._get_owned_spell(parked_id)
        assert parked is not None
        host.cleanup_spell(spell=parked)


def test_changed_id_restore_regrants_contract_details() -> None:
    """Contract replay follows the translated owner binding and preserves borrowed-instance cleanup."""
    crystallizer = _activate_crystallizer()
    with _recording_book(["flush"], False, "disposal-grant") as owner:
        with _recording_book([], False, "disposal-grant") as borrower:
            recorded_id = owner.bind(
                spell=OrderedDisposalService, existence="many",
                disposal_method_names=["stop", "close", "flush"],
            )
            owner_conduit = owner.conjure(dynamic=True, name="owner")
            borrower_conduit = borrower.conjure(dynamic=True, name="borrower")
            owner_conduit.link(borrower_conduit)
            with borrower_conduit.transaction("link", conduits=[owner_conduit, borrower_conduit]):
                borrower_conduit.add_spell_to_contract(
                    spell_id=recorded_id, conduit=owner_conduit, permissions="create",
                )
            checkpoint_id = crystallizer.create_checkpoint()
            window = json.loads(json.dumps(crystallizer.checkpoint_replay_data(checkpoint_id)))
            window["payloads"]["spellbook"][owner._id]["configuration_payload"][
                "enforce_priority_disposal_methods"
            ] = True
    _fresh_recorder(False)
    engine = RestoreEngine("default", [checkpoint_id], [window])
    try:
        report = engine.restore()
        try:
            result = report.describe()
            expected_id = _expected_identity(["flush", "stop", "close"])
            assert result["identity_map"][recorded_id] == expected_id
            assert result["built_counts"]["contract_detail"] >= 1
            assert not [row for row in result["shortfalls"] if row["kind"] == "contract"]
            restored = Aether().get_conduit_by_name("borrower", "disposal-grant")
            instance = restored.meld(spell_id=expected_id)
            restored.permanent_cleanup()
            assert instance.calls == ["flush", "stop", "close"]
        finally:
            report.cleanup()
    finally:
        engine.cleanup()
