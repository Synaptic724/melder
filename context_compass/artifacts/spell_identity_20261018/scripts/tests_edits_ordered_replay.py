"""melder_0, 2026-10-18: S1 and S2 edits to test_ordered_disposal_replay.py (one object, one spell; binding changes).

The captured index staged OrderedDisposalService a second time; that registration is refused now, so its staged
member is a second version of the service, defined at module level so restore and graft import it. A restore under
another disposal policy keeps every spell_id - the code did not change - and reports each changed binding hash, so
the two tests that asserted translated ids assert kept ids and the reported binding changes, under names that say so.
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tests_apply_s1_s2 import TestApplier

REPLAY = "tests/integration/melder/crystallizer/test_ordered_disposal_replay.py"

STAGED_CLASS = (
    "pytestmark = pytest.mark.usefixtures(\"reset_world_singletons\", \"cache_root\")\n"
    "\n"
    "\n"
    "class StagedDisposalService(OrderedDisposalService):\n"
    "    \"\"\"\n"
    "    The second version of OrderedDisposalService that the captured index stages.\n"
    "\n"
    "    One object is one spell (S1 of EPIC-2026-10-18-spell_identity_is_the_code): staging the service itself again\n"
    "    is refused, so the staged member is new code - one class-level value more. It is bound under the service's\n"
    "    address (spellframe \"OrderedDisposalService\"), inherits every disposal method, and is defined at module\n"
    "    level so restore and graft can import it by its module and qualname.\n"
    "    \"\"\"\n"
    "\n"
    "    version = 2\n"
)

OLD_EXPECTED = (
    "def _expected_identity(names: list[str]) -> str:\n"
    "    \"\"\"Compute the expected content ID from an explicit expected final order, without book policy.\"\"\"\n"
    "    return Bind.spell_id_inspector(\n"
    "        OrderedDisposalService,\n"
    "        spell_name=\"OrderedDisposalService\",\n"
    "        existence=Existence.many,\n"
    "        disposal_method_names=names,\n"
    "    )\n"
)
NEW_EXPECTED = (
    "def _expected_identity(target: type) -> str:\n"
    "    \"\"\"\n"
    "    Return the spell_id a bind gives `target`: the SHA256 of its code (S1 of\n"
    "    EPIC-2026-10-18-spell_identity_is_the_code). No disposal order or Book policy enters it; the resolved order\n"
    "    is the binding's, recorded in its binding hash.\n"
    "    \"\"\"\n"
    "    return Bind.spell_id_inspector(target)\n"
)

OLD_RESTORE_HEAD = (
    "def test_restore_changed_ids_preserves_anchor_and_exact_selected_member(priority: bool) -> None:\n"
    "    \"\"\"Recorded names from another policy are rebound coherently without stale anchor or selection joins.\"\"\"\n"
)
NEW_RESTORE_HEAD = (
    "def test_restore_under_another_policy_keeps_ids_and_exact_selected_member(priority: bool) -> None:\n"
    "    \"\"\"\n"
    "    Members recorded under another disposal policy keep their spell_ids and report their changed bindings.\n"
    "\n"
    "    The spell_id is the member's code, so the receiving policy changes no identity: nothing is translated, the\n"
    "    anchor and the requested selection join the recorded ids, and each member's binding hash follows the new\n"
    "    disposal order - reported, recorded beside live.\n"
    "    \"\"\"\n"
)
OLD_RESTORE_ASSERTS = (
    "            assert result[\"identity_map\"][selected_recorded] == _expected_identity(selected_names)\n"
    "            assert result[\"identity_map\"][parked_recorded] == _expected_identity(parked_names)\n"
    "            conduit = Aether().get_root_conduit_by_name(\"disposal-root\", \"disposal-source\")\n"
)
NEW_RESTORE_ASSERTS = (
    "            assert selected_recorded not in result[\"identity_map\"]\n"
    "            assert parked_recorded not in result[\"identity_map\"]\n"
    "            assert set(result[\"binding_changes\"]) == {selected_recorded, parked_recorded}\n"
    "            conduit = Aether().get_root_conduit_by_name(\"disposal-root\", \"disposal-source\")\n"
    "            for recorded_id, names in ((selected_recorded, selected_names), (parked_recorded, parked_names)):\n"
    "                member = conduit._spellbook._get_owned_spell(recorded_id)\n"
    "                assert member is not None\n"
    "                assert member.disposal_method_names == names\n"
    "                change = result[\"binding_changes\"][recorded_id]\n"
    "                assert change[\"recorded\"] != change[\"live\"]\n"
    "                assert change[\"live\"] == member.binding_hash\n"
)

OLD_GRANT_HEAD = (
    "def test_changed_id_restore_regrants_contract_details() -> None:\n"
    "    \"\"\"Contract replay follows the translated owner binding and preserves borrowed-instance cleanup.\"\"\"\n"
)
NEW_GRANT_HEAD = (
    "def test_restore_under_another_policy_regrants_contract_details() -> None:\n"
    "    \"\"\"\n"
    "    Contract replay regrants the owner's spell under another disposal policy: its spell_id is kept, its changed\n"
    "    binding reported, and the borrowed instance disposes in the receiving order.\n"
    "    \"\"\"\n"
)
OLD_GRANT_ASSERTS = (
    "            expected_id = _expected_identity([\"flush\", \"stop\", \"close\"])\n"
    "            assert result[\"identity_map\"][recorded_id] == expected_id\n"
    "            assert result[\"built_counts\"][\"contract_detail\"] >= 1\n"
    "            assert not [row for row in result[\"shortfalls\"] if row[\"kind\"] == \"contract\"]\n"
    "            restored = Aether().get_root_conduit_by_name(\"borrower\", \"disposal-grant\")\n"
    "            instance = restored.meld(spell_id=expected_id)\n"
)
NEW_GRANT_ASSERTS = (
    "            assert recorded_id == _expected_identity(OrderedDisposalService)\n"
    "            assert recorded_id not in result[\"identity_map\"]\n"
    "            assert set(result[\"binding_changes\"]) == {recorded_id}\n"
    "            change = result[\"binding_changes\"][recorded_id]\n"
    "            assert change[\"recorded\"] != change[\"live\"]\n"
    "            assert result[\"built_counts\"][\"contract_detail\"] >= 1\n"
    "            assert not [row for row in result[\"shortfalls\"] if row[\"kind\"] == \"contract\"]\n"
    "            restored = Aether().get_root_conduit_by_name(\"borrower\", \"disposal-grant\")\n"
    "            instance = restored.meld(spell_id=recorded_id)\n"
)


def apply(applier: "TestApplier") -> None:
    """Stage the replay test's edits: the staged second version, the kept ids and the binding changes."""
    applier.edit(REPLAY, [
        ("from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration\n"
         "from melder.aether.spellbook.existence.existence import Existence\n",
         "from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration\n"),
        ("pytestmark = pytest.mark.usefixtures(\"reset_world_singletons\", \"cache_root\")\n", STAGED_CLASS),
        ("    \"\"\"Capture and seal two distinct bindings, then release their source book before replay.\"\"\"\n",
         "    \"\"\"\n"
         "    Capture and seal two members of one index - the service and its staged second version - then release\n"
         "    their source book before replay.\n"
         "    \"\"\"\n"),
        ("            spell=OrderedDisposalService, spell_index=selected.spell_index,\n"
         "            existence=\"many\", disposal_method_names=[\"close\", \"flush\"],\n",
         "            spell=StagedDisposalService, spell_index=selected.spell_index,\n"
         "            existence=\"many\", spellframe=\"OrderedDisposalService\", disposal_method_names=[\"close\", \"flush\"],\n"),
        (OLD_EXPECTED, NEW_EXPECTED),
        ("    assert selected_id == _expected_identity(selected_names)\n"
         "    assert parked_id == _expected_identity(parked_names)\n",
         "    assert selected_id == _expected_identity(OrderedDisposalService)\n"
         "    assert parked_id == _expected_identity(StagedDisposalService)\n"),
        ("    \"\"\"Real cache reload restores active/staged identities and cleanup under both loader drivers.\"\"\"\n",
         "    \"\"\"Real cache reload restores active/staged identities, their bindings unchanged, and cleanup under both\n"
         "    loader drivers.\"\"\"\n"),
        ("    assert not [row for row in report[\"shortfalls\"] if row[\"kind\"] in (\"spell_crystal\", \"spell_index\")]\n",
         "    assert not [row for row in report[\"shortfalls\"] if row[\"kind\"] in (\"spell_crystal\", \"spell_index\")]\n"
         "    assert report[\"binding_changes\"] == {}\n"),
        ("    \"\"\"Fresh/merge grafts follow new binding IDs, with explicit selection adoption and ordered cleanup.\"\"\"\n",
         "    \"\"\"\n"
         "    Fresh/merge grafts keep the members' spell_ids and take the receiving Book's disposal order, with explicit\n"
         "    selection adoption and ordered cleanup.\n"
         "    \"\"\"\n"),
        ("        selected_id = _expected_identity(selected_names)\n"
         "        parked_id = _expected_identity(parked_names)\n",
         "        selected_id = _expected_identity(OrderedDisposalService)\n"
         "        parked_id = _expected_identity(StagedDisposalService)\n"),
        (OLD_RESTORE_HEAD, NEW_RESTORE_HEAD),
        (OLD_RESTORE_ASSERTS, NEW_RESTORE_ASSERTS),
        ("        parked_id = _expected_identity([\"flush\", \"close\"] if priority else [\"close\", \"flush\"])\n",
         "        parked_id = _expected_identity(StagedDisposalService)\n"),
        (OLD_GRANT_HEAD, NEW_GRANT_HEAD),
        (OLD_GRANT_ASSERTS, NEW_GRANT_ASSERTS),
    ], "ordered_replay")
