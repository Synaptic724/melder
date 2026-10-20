"""The contracted-copy removal fix (contracted_copy_removal_by_version_2026_10_16): Spellbook._remove_contracted_spell
matches the active copy by its own version id, never by index membership.

melder_1 (synaptic_python_developer), 2026-10-16. Edits src/melder/aether/spellbook/spellbook.py under TREE.
usage: python apply_removal_src_2026_10_16.py <tree root> --check | --apply. Anchors must match exactly once.
"""
import pathlib
import py_compile
import sys

SRC = "src/melder/aether/spellbook/spellbook.py"

EDITS = [
    (
        "docstring",
        "        Removing an ACTIVE copy (an uncontract, an index unlink or destroy, a\n"
        "        version leaving its index) marks the Book's SpellContract consumers of\n",
        "        It removes the copy of exactly the version `spell_id` names: the active\n"
        "        copy only when that copy's own `spell_id` is `spell_id`, otherwise the\n"
        "        version's parked copy; when the Book holds neither it raises and changes\n"
        "        nothing. The index's member set is never consulted, so with one version\n"
        "        parked and another version of the same index active (an index link after\n"
        "        a notch, or two version grants) removing the parked version leaves the\n"
        "        active copy alone, and an index unlink completes in any member order\n"
        "        (contracted_copy_removal_by_version_2026_10_16, 0.2.8251).\n"
        "\n"
        "        Removing an ACTIVE copy (an uncontract, an index unlink or destroy, a\n"
        "        version leaving its index) marks the Book's SpellContract consumers of\n",
    ),
    (
        "active match",
        "            # Find the contracted SpellIndex holding this member id. A destroyed\n"
        "            # (cleaned) contracted index can no longer report its member set, so\n"
        "            # fall back to matching the contracted spell's own id -- the removed\n"
        "            # member's live copy -- so its stale entry is still dropped.\n"
        "            spell_index = None\n"
        "            spell = None\n"
        "            for idx, s in spell_map.items():\n"
        "                if idx._cleaned:\n"
        "                    if s.spell_id == spell_id:\n"
        "                        spell_index = idx\n"
        "                        spell = s\n"
        "                        break\n"
        "                    continue\n"
        "                member_ids = idx._spells_in_index\n"
        "                if member_ids and spell_id in member_ids:\n"
        "                    spell_index = idx\n"
        "                    spell = s\n"
        "                    break\n",
        "            # Find the ACTIVE copy of exactly this version: the entry whose copy's own\n"
        "            # id is `spell_id`, for a live or a destroyed (cleaned) index alike. Never\n"
        "            # match by index membership: a live index lists every version, so a\n"
        "            # membership match took another version's active copy whenever this\n"
        "            # version was parked beside it (the unlink after a notch), and the later\n"
        "            # removal of that version then raised\n"
        "            # (contracted_copy_removal_by_version_2026_10_16, 0.2.8251). The index comes\n"
        "            # from the map key, so neither a cleaned index's member set nor a cleaned\n"
        "            # copy's `spell_index` is read.\n"
        "            spell_index = None\n"
        "            spell = None\n"
        "            for idx, s in spell_map.items():\n"
        "                if s.spell_id == spell_id:\n"
        "                    spell_index = idx\n"
        "                    spell = s\n"
        "                    break\n",
    ),
    (
        "parked comment",
        "                # Not in the ACTIVE contracted maps. A borrowed member can be\n",
        "                # No ACTIVE copy of this version. A borrowed member can be\n",
    ),
]


def main() -> None:
    if len(sys.argv) != 3 or sys.argv[2] not in ("--check", "--apply"):
        raise SystemExit("usage: <tree root> --check | --apply")
    path = pathlib.Path(sys.argv[1]) / SRC
    text = path.read_text(encoding="utf-8")
    for label, old, new in EDITS:
        n = text.count(old)
        if n != 1:
            raise SystemExit(f"{label}: anchor found {n} times - refusing")
        text = text.replace(old, new)
    long = [i + 1 for i, ln in enumerate(text.split("\n")) if len(ln) > 120]
    old_long = [i + 1 for i, ln in enumerate(path.read_text(encoding="utf-8").split("\n")) if len(ln) > 120]
    print(SRC, "lines", text.count("\n"), "over-120 before/after", len(old_long), len(long))
    if sys.argv[2] == "--check":
        print("check only - nothing written")
        return
    path.write_text(text, encoding="utf-8")
    assert path.read_text(encoding="utf-8") == text
    py_compile.compile(str(path), cfile="/tmp/cc_res/tmp/removal_src_check.pyc", doraise=True)
    print("applied, read back and compiled")


if __name__ == "__main__":
    main()
