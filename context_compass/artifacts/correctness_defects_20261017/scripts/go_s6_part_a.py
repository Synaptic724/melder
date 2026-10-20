"""Record the owner's go on S6 part A (2026-10-18) and consume M1-26.

Run from context_compass/:  python3 artifacts/correctness_defects_20261017/scripts/go_s6_part_a.py <NOW> [--dry-run]
Order: the M1-26 FACT note and the DECISION note are appended to S6 first (append_note.py, run before this script);
this script then edits S6's other sections, the epic, the patch docs and the board row, and consumes M1-26
(deletes the message, clears its alert, refreshes melder_0's last_checked). Every replacement must match once.
"""
import pathlib
import re
import sys

NOW = sys.argv[1]
DRY = "--dry-run" in sys.argv
writes = {}


def load(path):
    p = pathlib.Path(path)
    if p not in writes:
        writes[p] = p.read_text(encoding="utf-8")
    return p


def sub(path, old, new):
    p = load(path)
    text = writes[p]
    assert text.count(old) == 1, (path, old[:80], text.count(old))
    writes[p] = text.replace(old, new.replace("<NOW>", NOW), 1)


S6 = "tickets/stories/2026-10-17_release_routes_parked_version_objects_to_active_pool_story.md"
EPIC = "tickets/epics/2026-10-17_correctness_defects_epic.md"
PATCH = "system_docs/patches/active/managed_settings_spell_id_2026_10_17/"

sub(S6, "- [ ] Task: the owner's confirmation of the scope (Open Questions).\n",
    "- [x] Task: the owner's confirmation of the scope (2026-10-18: only the four settings; DECISION note).\n")
sub(S6, "- [ ] Task: patch docs for the Binding Pipeline and the Managed Spell Pools (written 2026-10-18T00:07:52Z,\n"
        "  linked below); the owner's approval.\n",
    "- [x] Task: patch docs for the Binding Pipeline and the Managed Spell Pools (written 2026-10-18T00:07:52Z,\n"
    "  linked below); the owner's go for part A (2026-10-18).\n")
sub(S6, "- Scope (ALIGNMENT_CHECK with the owner, chat 2026-10-17T23:50:39Z): only the four managed settings leave the\n"
        "  spell_id; the address stays (one class under two binding names is two spells), and existence, disposal names and\n"
        "  resolvable stay (they shape the plan the creation cache keeps under the spell_id). Part B closes the residual\n"
        "  same-class case by refusing it at staging. Confirm, or say what else leaves the id.\n",
    "- Answered (owner, chat 2026-10-18): only the four managed settings leave the spell_id; the address, existence,\n"
    "  disposal names and resolvable stay (DECISION note).\n"
    "- Open, for the talk after part A: part B's staging refusal; a legacy record holding two settings-only versions of\n"
    "  one class in one index (with no extra code its restore fails whole on the collision); whether anything more of\n"
    "  the bind call leaves the spell_id.\n")
sub(S6, "spell_id (scope with the\n  owner for confirmation);", "spell_id (confirmed by the\n  owner, 2026-10-18);")
sub(S6, "  the spell_id; notch the version for the cache; melder_0 takes the lane (DECISION note).\n",
    "  the spell_id; notch the version for the cache; melder_0 takes the lane (DECISION note).\n"
    "- <NOW>: the owner confirmed the scope (the four settings only) and gave the go for part A;\n"
    "  part B, the legacy record and anything more are for the talk after it (DECISION note).\n")
sub(S6, "- State: in_progress (melder_0), discovery. The direction is the owner's (DECISION note); the scope is with him for\n"
        "  confirmation (Open Questions). Part A sits in free files (bind.py, managed_spell_quantity.py, creations.py,\n"
        "  caching_system.py); part B in spellbook.py (melder_1's until its release). Landing follows melder_1's 0.2.8253.\n"
        "- Next: (1) the owner's approval of the patch docs (Artifact Links) and his answers on the scope and the legacy\n"
        "  record; (2) part A after melder_1's notch, with its tests, docs, notch and the rebuild last; (3) part B after\n"
        "  melder_1's release of spellbook.py.\n",
    "- State: in_progress (melder_0), implementation. The direction and the scope are the owner's (DECISION notes\n"
    "  of 2026-10-17T23:50:39Z and <NOW>): only the four managed settings leave the spell_id.\n"
    "  melder_1's 0.2.8253 landed (M1-26). Part A sits in free files (bind.py, managed_spell_quantity.py,\n"
    "  creations.py, caching_system.py); part B in spellbook.py (melder_1's until its release).\n"
    "- Next: (1) part A with its tests, docs, notch (above 0.2.8253) and the rebuild last; (2) report to the owner\n"
    "  and talk through part B, the legacy record and anything more of the bind call; (3) part B after melder_1's\n"
    "  release of spellbook.py.\n")

sub(EPIC, "- S6's scope confirmation, with the owner (its direction chosen 2026-10-17: the managed settings leave the spell_id).\n"
          "  Every other story question is answered (S1, S2, S5, S8) or withdrawn (S10).\n",
    "- None open on the stories: the owner confirmed S6's scope (2026-10-18: only the four managed settings leave the\n"
    "  spell_id). For the talk after S6's part A: its part B refusal, its legacy record, anything more of the bind call.\n")
sub(EPIC, "  spell_id, notch for the cache; melder_0 takes S6's fix lane (DECISION note).\n",
    "  spell_id, notch for the cache; melder_0 takes S6's fix lane (DECISION note).\n"
    "- <NOW>: the owner confirmed S6's scope - the four managed settings only - and gave the go for\n"
    "  part A (DECISION note).\n")
sub(EPIC, "  (DECISION note of 2026-10-17T23:50:39Z): the managed settings leave the spell_id; melder_0 runs its fix lane.\n",
    "  (DECISION note of 2026-10-17T23:50:39Z): the managed settings leave the spell_id; melder_0 runs its fix lane.\n"
    "  The owner confirmed S6's scope (DECISION note of <NOW>); melder_1's 0.2.8253 landed (M1-26).\n")
sub(EPIC, "- Next: (1) S6's patch docs and the owner's scope confirmation, then its fix after melder_1's notch; (2) a fourth\n"
          "  tranche on the owner's word; (3) melder_1 carries S1-S4 and S7-S9 with its hand-back.\n",
    "- Next: (1) S6's part A (the owner's go, 2026-10-18; melder_1's 0.2.8253 landed), then the talk on its part B and\n"
    "  legacy record; (2) a fourth tranche on the owner's word; (3) melder_1 carries S1-S4 and S7-S9 with its hand-back.\n")

sub(PATCH + "architecture_patch.md", "- Status: draft, for the owner's approval; written before any `src/` edit of the lane\n",
    "- Status: approved for part A (owner, chat 2026-10-18: \"just do the 4\"); part B and the legacy record are open\n")
sub(PATCH + "architecture_patch.md", "- Updated: 2026-10-18T00:10:00Z\n", "- Updated: <NOW>\n")
sub(PATCH + "architecture_patch.md",
    "- DECISION_REQUEST (owner): the scope - only the four managed settings leave the spell_id (recommended), or more.\n",
    "- ANSWERED (owner, chat 2026-10-18): the scope - only the four managed settings leave the spell_id; the rest stays.\n")
sub(PATCH + "architecture_patch.md",
    "- What remains: the owner's approval and scope answer; melder_1's landing; part A; part B after melder_1's release.\n",
    "- What remains: part A (the owner's go and scope answer, 2026-10-18; melder_1's landing met, M1-26); part B and\n"
    "  the legacy record after the talk that follows part A.\n")
for name in ("component_patch_binding_fingerprint.md", "component_patch_managed_pool_rebind.md",
             "code_description_patch_managed_pool_rebind.md", "component_patch_creation_cache_generation.md"):
    sub(PATCH + name, "- Status: draft, for the owner's approval\n",
        "- Status: approved (owner, chat 2026-10-18: \"just do the 4\")\n")
    sub(PATCH + name, "- Updated: 2026-10-18T00:10:00Z\n", "- Updated: <NOW>\n")
sub(PATCH + "component_patch_binding_fingerprint.md",
    "- DECISION_REQUEST (owner): whether anything beyond the four settings leaves the fingerprint (architecture patch).\n",
    "- ANSWERED (owner, chat 2026-10-18): only the four settings leave the fingerprint (architecture patch).\n")
sub(PATCH + "component_patch_staging_refusal.md",
    "- Status: draft, for the owner's approval; lands after melder_1 releases spellbook.py\n",
    "- Status: draft; for the talk after part A (owner, 2026-10-18); lands after melder_1 releases spellbook.py\n")
sub(PATCH + "component_patch_staging_refusal.md", "- Updated: 2026-10-18T00:10:00Z\n", "- Updated: <NOW>\n")

old_row = ("| managed_settings_spell_id | in_progress | discovery | claude | melder_0 | none | The owner approves S6's patch "
           "docs and answers the scope and the legacy record; then part A after melder_1's notch. |")
new_row = ("| managed_settings_spell_id | in_progress | implementation | claude | melder_0 | none | Land part A: the "
           "fingerprint, the pool rebind and cache generation 22 with tests, docs, the notch above 0.2.8253 and the "
           "rebuild last; then report to the owner. |")
ab = load("attention_board.md")
a = writes[ab]
start = a.index(old_row)
end = a.index("\n", start)
row = a[start:end]
assert row.count("| 2026-10-18T00:07:52Z |") == 1, row
row = row.replace(old_row, new_row, 1).replace("| 2026-10-18T00:07:52Z |", "| " + NOW + " |", 1)
a = a[:start] + row + a[end:]
alert = "- NEW MESSAGE for melder_0 (from melder_1, 2026-10-18T00:26:52Z)\n"
assert a.count(alert) == 1
writes[ab] = a.replace(alert, "", 1)

mb = load("mailbox_board.md")
m = writes[mb]
mstart = m.index("- TO: melder_0\n  FROM: melder_1\n  DATETIME: 2026-10-18T00:26:52Z\n  TYPE: NOTICE\n  CLAIM: M1-26.")
mend = m.index("  ACK_REQUESTED: false\n", mstart) + len("  ACK_REQUESTED: false\n")
block = m[mstart:mend]
assert block.count("- TO:") == 1 and "M1-26" in block, block
m = m[:mstart] + m[mend:]
pat = re.compile(r"^(\| melder_0 \| claude \| 2026-09-26T22:24:06Z \| )[0-9TZ:-]+( \| active \|)$", re.M)
assert len(pat.findall(m)) == 1
writes[mb] = pat.sub(lambda g: g.group(1) + NOW + g.group(2), m, count=1)

for p, text in writes.items():
    before = set(p.read_text(encoding="utf-8").splitlines())
    added = [line for line in text.splitlines() if line not in before]
    long = [line for line in added if len(line) > 120 and "/" not in line and "|" not in line]
    assert not long, (p, long[:3])
    if not DRY:
        p.write_text(text, encoding="utf-8")
    print(("checked " if DRY else "wrote ") + str(p))
