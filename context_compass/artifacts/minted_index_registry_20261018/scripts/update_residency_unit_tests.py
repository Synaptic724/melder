"""Update the residency unit tests for S4's edit C (melder_1; STORY-2026-10-17-minted_index_missing_from_frame_registry).

Under edit C a version reads active only when its index selects it AND the frame's lineage registry tracks it as the
index's current version. The two unit tests whose frame doubles left the lineage unset get doubles whose lineage tracks
the selected id (what bind and a notch register); `_fake_frame` takes `lineage_tracks_selected`; a new test reads a
selected version no lineage tracks (the minted index before a notch) as parked. The file is CRLF throughout and stays
so. Usage: --root <tree> --check|--apply
"""
import pathlib
import sys

TEST = "tests/unit/melder/mutation_research/test_mutation_research_root.py"

EDITS = [
    ("join double",
     "    frame.find_index_for_spell.side_effect = (\n"
     "        lambda sha: index if sha in (\"sha-active\", \"sha-parked\") else None\n"
     "    )\n"
     "    aether._aetheric_frames = {\"default\": frame}\n",
     "    frame.find_index_for_spell.side_effect = (\n"
     "        lambda sha: index if sha in (\"sha-active\", \"sha-parked\") else None\n"
     "    )\n"
     "    # The lineage registry tracks the index's selected version, as bind and\n"
     "    # a notch register it.\n"
     "    frame.spell_system_states.get_by_index_id.return_value.current_spell_id = (\n"
     "        \"sha-active\"\n"
     "    )\n"
     "    aether._aetheric_frames = {\"default\": frame}\n"),
    ("fake frame",
     "def _fake_frame(index_id: str, selected_spell_id: str) -> MagicMock:\n"
     "    \"\"\"\n"
     "    Build one live frame double whose index scan answers a fixed index.\n"
     "\n"
     "    Args:\n"
     "        index_id:\n"
     "            Index id the frame reports for any queried spell.\n"
     "        selected_spell_id:\n"
     "            The index's currently selected member.\n"
     "\n"
     "    Returns:\n"
     "        MagicMock: Frame double for `_locate_live_membership` scans.\n"
     "    \"\"\"\n"
     "    index = MagicMock()\n"
     "    index.cleaned = False\n"
     "    index.id = index_id\n"
     "    index.selected_spell_id = selected_spell_id\n"
     "    frame = MagicMock()\n"
     "    frame.cleaned = False\n"
     "    frame.find_index_for_spell.return_value = index\n"
     "    return frame\n",
     "def _fake_frame(\n"
     "        index_id: str,\n"
     "        selected_spell_id: str,\n"
     "        *,\n"
     "        lineage_tracks_selected: bool = True,\n"
     ") -> MagicMock:\n"
     "    \"\"\"\n"
     "    Build one live frame double whose index scan answers a fixed index.\n"
     "\n"
     "    Args:\n"
     "        index_id:\n"
     "            Index id the frame reports for any queried spell.\n"
     "        selected_spell_id:\n"
     "            The index's currently selected member.\n"
     "        lineage_tracks_selected:\n"
     "            When True the frame's lineage registry tracks the selected\n"
     "            member as the index's current version, as `bind` and a notch\n"
     "            register it; when False no lineage is registered for the\n"
     "            index, as for the index `remove_from_spell_index` mints before\n"
     "            a notch.\n"
     "\n"
     "    Returns:\n"
     "        MagicMock: Frame double for `_locate_live_membership` scans.\n"
     "    \"\"\"\n"
     "    index = MagicMock()\n"
     "    index.cleaned = False\n"
     "    index.id = index_id\n"
     "    index.selected_spell_id = selected_spell_id\n"
     "    frame = MagicMock()\n"
     "    frame.cleaned = False\n"
     "    frame.find_index_for_spell.return_value = index\n"
     "    lineages = frame.spell_system_states.get_by_index_id\n"
     "    if lineage_tracks_selected:\n"
     "        lineages.return_value.current_spell_id = selected_spell_id\n"
     "    else:\n"
     "        lineages.return_value = None\n"
     "    return frame\n"),
    ("new test",
     "    assert view[\"runtime\"] == \"parked\"\n"
     "    assert view[\"frame_name\"] == \"frame_one\"\n"
     "    assert view[\"index_id\"] == \"idx-one\"\n",
     "    assert view[\"runtime\"] == \"parked\"\n"
     "    assert view[\"frame_name\"] == \"frame_one\"\n"
     "    assert view[\"index_id\"] == \"idx-one\"\n"
     "\n"
     "\n"
     "def test_residency_view_reads_a_selected_version_no_lineage_tracks_as_parked(\n"
     ") -> None:\n"
     "    \"\"\"\n"
     "    Regression (minted_index_registry, probe V2): the index\n"
     "    `remove_from_spell_index` mints selects its parked member - activation\n"
     "    takes a notch - so once that index is registered with the frame, the\n"
     "    index's selection alone read the parked version as active. Corrected\n"
     "    behavior: a selected version reads active only while the frame's\n"
     "    lineage registry tracks it as the index's current version.\n"
     "    \"\"\"\n"
     "    spell_id = \"s\" * 64\n"
     "    aether = _mock_aether(recording=True)\n"
     "    aether.cleaned = False\n"
     "    aether._aetheric_frames = {\n"
     "        \"frame_minted\": _fake_frame(\n"
     "            \"idx-minted\",\n"
     "            selected_spell_id=spell_id,\n"
     "            lineage_tracks_selected=False,\n"
     "        ),\n"
     "    }\n"
     "    root = MutationResearch(aether=aether)\n"
     "\n"
     "    view = root.residency_view(spell_id)\n"
     "\n"
     "    assert view[\"runtime\"] == \"parked\"\n"
     "    assert view[\"frame_name\"] == \"frame_minted\"\n"
     "    assert view[\"index_id\"] == \"idx-minted\"\n"),
]


def main() -> None:
    """Apply the three edits in memory, keeping CRLF; write only with --apply."""
    args = sys.argv[1:]
    if len(args) != 3 or args[0] != "--root" or args[2] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    path = pathlib.Path(args[1]) / TEST
    raw = path.read_bytes()
    if raw.count(b"\r\n") != raw.count(b"\n"):
        raise SystemExit("expected CRLF throughout: %s" % TEST)
    text = raw.decode("utf-8").replace("\r\n", "\n")
    for label, old, new in EDITS:
        for line in new.split("\n"):
            if len(line) > 120:
                raise SystemExit("%s: line over 120 chars" % label)
        if text.count(old) != 1:
            raise SystemExit("%s: anchor found %d times" % (label, text.count(old)))
        text = text.replace(old, new)
    print("all anchors found")
    if args[2] == "--apply":
        data = text.replace("\n", "\r\n").encode("utf-8")
        path.write_bytes(data)
        if path.read_bytes() != data:
            raise SystemExit("read-back mismatch")
        print("applied (CRLF kept)", TEST)


main()
