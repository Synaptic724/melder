"""Temporary diagnostic of current graft behavior; not a desired-behavior regression contract."""

import json

import pytest

from melder.crystallizer.crystal_loader_system.graft_runner import GraftRunner
from tests.component.melder.spellbook.test_ordered_disposal_binding import (
    OrderedDisposalService,
    configured_book,
    fresh_runtime,
)
from tests.unit.melder.aether.conduit.creations.test_creations_disposal_all_methods_regression import (
    MultiMethodDisposalProbe,
)


@pytest.mark.usefixtures("fresh_runtime")
@pytest.mark.parametrize("changed_host", [False, True])
def test_current_graft_host_policy_join(changed_host: bool) -> None:
    """Compare real multi-member grafts with matching versus reordered target-book policy."""
    names = ["close", "flush"]
    with configured_book(names, frame="graft-probe-source", dynamic=True) as source:
        selected_id = source.bind(spell=OrderedDisposalService, existence="many")
        selected = source.find_spell_by_id(selected_id)
        assert selected is not None
        source.conjure(dynamic=True)
        parked_id = source.bind_inactive(
            spell=MultiMethodDisposalProbe,
            spell_index=selected.spell_index,
            existence="many",
        )
        parked = source._get_owned_spell(parked_id)
        assert parked is not None
        try:
            # Feed recorded-value inputs from real source binds. This deliberately
            # excludes SpellCrystal's known sorting defect to isolate the host-policy join.
            members = {}
            for spell in (selected, parked):
                members[spell.spell_id] = {"payload": {
                    "rebindability": "hydratable",
                    "root_module_name": spell.spell.__module__,
                    "root_target_qualname": spell.spell.__qualname__,
                    "existence_name": spell.existence.name,
                    "permissions_name": spell.permissions.name,
                    "spellframe_name": None,
                    "binding_name": spell.binding_name,
                    "disposal_method_names": spell.disposal_method_names,
                    "profile_family": "general",
                }}
            record = json.loads(json.dumps({
                "graft_kind": "spell_index",
                "index_id": selected.spell_index.id,
                "index_payload": {"selected_spell_id": selected_id},
                "members": members,
                "members_without_custody": [],
            }))
        finally:
            source.cleanup_spell(spell=parked)

    host_names = ["flush", "close"] if changed_host else names
    with configured_book(host_names, changed_host, frame="graft-probe-host", dynamic=True) as host:
        host.conjure(dynamic=True)
        runner = GraftRunner(record, host)
        try:
            report = runner.run()
            live = next(spell for spell in host._spells.values() if spell.spell is OrderedDisposalService)
            print(json.dumps({
                "changed_host": changed_host,
                "recorded_names": names,
                "live_names": live.disposal_method_names,
                "recorded_id": selected_id,
                "live_id": live.spell_id,
                "bound": report["members_bound"],
                "parked": report["members_parked"],
                "shortfalls": report["shortfalls"],
            }, sort_keys=True))
            assert report["members_bound"] == 1
            assert live.disposal_method_names == host_names
            assert (live.spell_id != selected_id) is changed_host
            if changed_host:
                assert report["members_parked"] == 0
                assert report["shortfalls"][0]["reason"] == "anchor_index_unresolvable_member_skipped"
            else:
                assert report["members_parked"] == 1
                assert report["shortfalls"] == []
        finally:
            runner.cleanup()
