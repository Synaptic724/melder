"""Activate TASK-2026-10-16-public_notch_target_for_staged_versions: metadata, contract, transition, steps, paths,
artifact links and the handoff view (exact replacements, each asserted once; line endings kept).

Run from the context_compass root:
    python artifacts/public_notch_target_20261016/scripts/activate_task.py
"""
import pathlib

TICKET = pathlib.Path("tickets/tasks/2026-10-16_public_notch_target_for_staged_versions_task.md")

REPLACEMENTS = [
    ("- Status: draft\n", "- Status: in_progress\n"),
    ("- Agent Name: unassigned\n", "- Agent Name: melder_0\n"),
    ("- Agent Role: UNKNOWN\n", "- Agent Role: synaptic_python_developer\n"),
    (
        "- ENTRY_GATE: the owner's choice in the DECISION_REQUEST below (a public API change); an active board row; a component\n"
        "  patch for the chosen surface and the mapping note before the first `src/` edit.\n"
        "- EXECUTION_BOUNDARY: `Conduit.notch_spell` and the Spellbook notch entry it calls, or the new lookup (per the\n"
        "  choice); README's stage-notch-meld sketch; docs/expert/governed-change.md; new unit and integration tests; system\n"
        "  docs with their indexes and the graph; the release note; one notch; the rebuild last.\n",
        "- ENTRY_GATE: the shape is chosen - option A, by the owner on 2026-10-16 (DECISION note below). Still required before\n"
        "  the first `src/` edit: the active board row, the patch lane public_notch_target_2026_10_16 linked here, and the\n"
        "  mapping note.\n"
        "- EXECUTION_BOUNDARY: `Conduit.notch_spell` in src/melder/aether/conduit/conduit.py - the `spell_id=` keyword, its\n"
        "  resolution through the Book's `_get_owned_spell` and the target checks before the transaction; README's\n"
        "  stage-notch-meld sketch; docs/expert/governed-change.md; new unit and integration tests; system docs with their\n"
        "  indexes and the graph; the release note; one notch; the rebuild last. spellbook.py is read, not edited.\n",
    ),
    (
        "- FAILURE_ESCALATION: DECISION_REQUEST if the chosen shape changes the meaning of an existing argument; CONFLICT if the\n"
        "  notch transaction's metadata (it reads `spell.spell_id` and `spell._key` before admission) cannot be built from an\n"
        "  id alone without a new lookup.\n",
        "- FAILURE_ESCALATION: DECISION_REQUEST if the chosen shape changes the meaning of an existing argument; CONFLICT if the\n"
        "  notch transaction's metadata (it reads `spell.spell_id` and `spell._key` before admission) cannot be built from an\n"
        "  id alone without a new lookup; DECISION_REQUEST before the keyword reaches `add_to_spell_index` or\n"
        "  `remove_from_spell_index` (outside the scope the owner ruled on).\n",
    ),
    (
        "  return value (a spell id); `add_to_spell_index` / `remove_from_spell_index`, unless the owner extends the scope.\n",
        "  return value (a spell id); `add_to_spell_index` / `remove_from_spell_index`, unless the owner extends the scope\n"
        "  (asked 2026-10-16: the DECISION_REQUEST below).\n",
    ),
    (
        "- from_state: draft\n"
        "- to_state: draft\n"
        "- transition_reason: created as a draft from S8's finding (Notes); the owner's design choice comes first (\"if you\n"
        "  found more bugs just add tickets\", 2026-10-16).\n",
        "- from_state: draft\n"
        "- to_state: in_progress\n"
        "- transition_reason: the owner chose option A (chat 2026-10-16: \"just use the private version if its inside the\n"
        "  public call thats reasonable\") and directed this task next (\"continue onto the next stuff please\"); melder_0\n"
        "  took it out of the backlog. Previous: draft -> draft at creation, from S8's finding, the owner's design choice\n"
        "  first (\"if you found more bugs just add tickets\", 2026-10-16).\n",
    ),
    (
        "- [ ] The owner picks the shape (DECISION_REQUEST below).\n",
        "- [x] The owner picks the shape: option A (DECISION note, 2026-10-16).\n",
    ),
    (
        "- src/melder/aether/conduit/conduit.py (`Conduit.notch_spell`) and src/melder/aether/spellbook/spellbook.py (the notch\n"
        "  entry, or a new public lookup)\n",
        "- src/melder/aether/conduit/conduit.py (`Conduit.notch_spell`); src/melder/aether/spellbook/spellbook.py is read, not\n"
        "  edited (`_get_owned_spell` already resolves an owned version, active or parked)\n"
        "- src/melder/__version__.py (the notch); release_docs/next_version_release.md\n"
        "- context_compass/system_docs/ (src_architecture, src_components, tests_architecture, tests_components, their\n"
        "  indexes, conduit.py's graph descriptor and the assembled graph)\n",
    ),
    (
        "- ARTIFACTS_REQUIRED: false\n"
        "- ARTIFACT_PATHS:\n"
        "  - none yet. S8's release-note probe shows the private notch the public loop would replace; it is rowed under\n"
        "    the epic's evidence folder: artifacts/managed_spell_quantity_20261015/probes/probe_s8_release_note_example.py\n"
        "- DISPOSITION: retain_as_reference\n"
        "- CLEANUP_TRIGGER: none\n",
        "- ARTIFACTS_REQUIRED: true\n"
        "- ARTIFACT_PATHS:\n"
        "  - artifacts/public_notch_target_20261016/ (scripts, probes, runs, notes)\n"
        "  - S8's release-note probe shows the private notch the public loop replaces; it is rowed under the closed epic's\n"
        "    evidence folder: artifacts/managed_spell_quantity_20261015/probes/probe_s8_release_note_example.py\n"
        "- DISPOSITION: retain_as_reference (the folder); promote_to_documentation (the patch docs, once written)\n"
        "- CLEANUP_TRIGGER: at closure the patch docs are promoted into the system docs and archived under\n"
        "  system_docs/patches/completed/; the folder stays as the lane's evidence\n",
    ),
    (
        "- Scope: one public way to notch to a staged version; the README and docs examples run as written.\n"
        "- State: draft in the backlog; waits on the owner's choice (A, B or C; A recommended). Source revision 0.2.8248.\n"
        "- Next: the owner answers; then patch, tests, change, docs, notch, rebuild.\n"
        "- Limits: none run (Not run).\n",
        "- Scope: `Conduit.notch_spell(spell_index=..., spell_id=...)` - option A, the owner's choice - so the stage ->\n"
        "  notch -> meld loop runs on public calls; the README and docs examples run as written.\n"
        "- State: in_progress (melder_0), discovery. Source revision 0.2.8248. conduit.py is held by this task until it\n"
        "  lands (melder_1's D3 edits `notch_spell` too); spellbook.py and transfer_of_ownership.py are released to melder_1.\n"
        "- Open for the owner: whether `add_to_spell_index` / `remove_from_spell_index` get the same keyword (Notes).\n"
        "- Next: (1) read the notch path whole and probe today's target checks; (2) the patch lane and mapping note;\n"
        "  (3) red tests, the change, green with the GIL off and on, the README-loop probe; docs, notch, rebuild last.\n"
        "- Limits: nothing run yet (Not run).\n",
    ),
]


def main() -> None:
    """Apply every replacement once, asserting each old text occurs exactly once."""
    text = TICKET.read_bytes().decode("utf-8")
    newline = "\r\n" if "\r\n" in text else "\n"
    for old, new in REPLACEMENTS:
        old_n = old.replace("\n", newline)
        new_n = new.replace("\n", newline)
        count = text.count(old_n)
        if count != 1:
            raise SystemExit(f"expected 1 occurrence, found {count}: {old[:70]!r}")
        text = text.replace(old_n, new_n, 1)
    TICKET.write_bytes(text.encode("utf-8"))
    over = [ln for ln in text.split(newline) if len(ln) > 120]
    print("replacements:", len(REPLACEMENTS), "; lines over 120:", len(over))
    for ln in over:
        print(len(ln), ln[:90])


if __name__ == "__main__":
    main()
