"""Fix the epic and stories open_epic.py wrote (melder_0, 2026-10-18), after re-onboarding.

- Re-wraps prose lines over 120 characters (paths stay whole, as the line-width contract allows).
- Gives every EVIDENCE pointer its line range (the epic's, the stories' and S6's closure notes).
- Records M1-28 (melder_1 turned in its lane and released every file it held): one FACT note on the epic, and the
  Ticket Contract, Constraints, Risks and the stories' entry gates corrected in place (the PLAN note stays as written).
- New draft stories record `from_state: (new)`, the repository's convention for a ticket filed as draft.
Every replacement must match exactly once. Usage (from context_compass/): fix_open_epic.py <NOW>
"""
import pathlib
import sys

NOW = sys.argv[1]
EPIC = pathlib.Path("tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md")
S6 = pathlib.Path("tickets/stories/completed/2026-10-17_release_routes_parked_version_objects_to_active_pool_story.md")
STORIES = {slug: pathlib.Path(f"tickets/stories/2026-10-18_{slug}_story.md") for slug in (
    "spell_id_hashes_the_object_code", "binding_manifest_hash", "revalidate_on_binding_change",
    "one_registration_per_object", "spell_id_migration")}
EPIC_REF = "context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md"
OLD_PLAN_CLAIM = ("  CLAIM: Filed from the owner's direction (the epic's DECISION note of 2026-10-18T11:45:58Z); the evidence"
                  " it starts from is the\n    epic's FACT note and its probes. Nothing in src/ moves before this story's"
                  " component patch is approved.\n")
NEW_PLAN_CLAIM = ("  CLAIM: Filed from the owner's direction (the epic's DECISION note of 2026-10-18T11:45:58Z); the evidence"
                  " it\n    starts from is the epic's FACT note and its probes. Nothing in src/ moves before this story's"
                  " component patch is\n    approved.\n")
OLD_REASON = ("- transition_reason: filed under EPIC-2026-10-18-spell_identity_is_the_code on the owner's direction"
              " (chat 2026-10-18)")


def rep(text: str, old: str, new: str) -> str:
    """Replace one exact occurrence; refuse zero or several."""
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected one match, found {count}: {old[:90]!r}")
    return text.replace(old, new)


def line_of(lines: list, prefix: str, start: int = 0) -> int:
    """0-based index of the first line at or after start that begins with prefix."""
    for index in range(start, len(lines)):
        if lines[index].startswith(prefix):
            return index
    raise SystemExit(f"no line starts with {prefix!r}")


def fix_epic(text: str) -> str:
    """The epic's wraps, the M1-28 corrections in place, its new FACT note and Decision Log entry."""
    text = rep(text, "- Updated: 2026-10-18T11:45:58Z\n", f"- Updated: {NOW}\n")
    text = rep(text, "follows\n  STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool (tickets/",
               "follows\n  STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool\n  (tickets/")
    text = rep(text, "(Open Questions) before STORY-2026-10-18-spell_id_hashes_the_object_code\n  is implemented.",
               "(Open Questions) before\n  STORY-2026-10-18-spell_id_hashes_the_object_code is implemented.")
    text = rep(text,
               "(part A, 0.2.8254, done);\n  melder_1 releasing the files it holds (spellbook.py, conduit.py, spell.py,"
               " restore_engine.py, graft_runner.py) for\n  the stories that touch them; the owner's calls.\n",
               "(part A, 0.2.8254, done); the\n  owner's calls; one writer per file - melder_1 turned in its lane and"
               " released every file it held (M1-28), so\n  melder_0 writes the files these stories touch and announces"
               " each landing by mailbox (M0-193).\n")
    text = rep(text,
               "- melder_1 holds spellbook.py, conduit.py, spell.py, restore_engine.py and graft_runner.py; stories"
               " touching them wait\n  for its release (mailbox, M0-193).\n",
               "- One writer per file: melder_1 turned in its lane at 2026-10-18T11:51:41Z and released every file it"
               " held (M1-28);\n  melder_0 writes the files these stories touch and says so by mailbox before each"
               " landing (M0-193). The next notch\n  is above 0.2.8255.\n")
    text = rep(text, "- Overlap with melder_1's held files: the stories are sequenced; a mailbox NOTICE before each touch.",
               "- Overlap with another lane's files: one writer per file; a mailbox NOTICE before each landing (M0-193).")
    text = rep(text, "prose and evidence (the probes); created 2026-10-18T11:45:58Z.",
               "prose and evidence (the probes); created\n  2026-10-18T11:45:58Z.")
    text = rep(text, "  - tickets/stories/completed/2026-10-17_release_routes_parked_version_objects_to_active_pool_story.md\n",
               f"  - context_compass/{S6.as_posix()}:966-985\n")
    text = rep(text, f"  EVIDENCE: {EPIC_REF}\n  IMPACT: Nothing in src/ moves",
               f"  EVIDENCE:\n  - {EPIC_REF}:@STORIES@\n  - {EPIC_REF}:@OPENQ@\n  IMPACT: Nothing in src/ moves")
    text = rep(text, "  the probes in Artifact Links. S6 of the correctness epic is turned in; its part B and open items"
               " live here.\n",
               "  the probes in Artifact Links. S6 of the correctness epic is turned in; its part B and open items"
               " live here.\n  melder_1's lane is turned in and its files are free (M1-28); the next notch is above"
               " 0.2.8255.\n")
    text = rep(text, "- 2026-10-18T11:45:58Z: opened on the owner's direction (DECISION note); five stories filed.\n",
               "- 2026-10-18T11:45:58Z: opened on the owner's direction (DECISION note); five stories filed.\n"
               f"- {NOW}: M1-28 consumed - melder_1's files are free; the entry gates no longer wait on a release"
               " (FACT note).\n")
    note = f"""
- DATETIME: {NOW}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M1-28 from melder_1 (2026-10-18T11:51:41Z), consumed: melder_1 landed and rebuilt 0.2.8255 (docstrings and
    comments call a SpellIndex a SpellIndex; nothing renamed), turned in
    TASK-2026-10-16-recheck_contract_consumers_when_provider_changes on the owner's word, and handed back every file
    its lane held - spellbook.py, conduit.py, the lookup fix's files, the wording sweep's src files, S6's files,
    `__version__`, the release note, the system documents and the graph (not committed). No story here waits on a
    release any more: the PLAN note's step (4) loses its melder_1 condition, and the Ticket Contract, Constraints,
    Risks and the stories' entry gates are corrected in place. One writer per file still holds; melder_0 announces
    each landing by mailbox (M0-193). The next notch is above 0.2.8255.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md:15-21
  - src/melder/__version__.py:12-12
  - release_docs/next_version_release.md:1-3
  IMPACT: S2-S5 can start once their patches are approved; S1 and S2 notch 0.2.8256 at the earliest.
  NEXT: The owner's calls on the five edges.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
"""
    text = rep(text, "  NEXT: Put the five calls to the owner.\n  REREAD: REQUIRED\n  SCORE_0_TO_10: 8\n",
               "  NEXT: Put the five calls to the owner.\n  REREAD: REQUIRED\n  SCORE_0_TO_10: 8\n" + note)
    lines = text.split("\n")
    stories = line_of(lines, "## Stories (Required to Complete)")
    tasks = line_of(lines, "## Tasks (Cross-Cutting or Epic-Level)")
    openq = line_of(lines, "## Open Questions")
    dlog = line_of(lines, "## Decision Log")
    text = text.replace("@STORIES@", f"{stories + 1}-{tasks - 1}").replace("@OPENQ@", f"{openq + 1}-{dlog - 1}")
    return text


def epic_ranges(text: str) -> dict:
    """1-based ranges of the epic's DECISION + FACT notes (the first two), its DECISION note and its Stories section."""
    lines = text.split("\n")
    notes = line_of(lines, "## Notes")
    first = line_of(lines, "- DATETIME:", notes)
    second = line_of(lines, "- DATETIME:", first + 1)
    third = line_of(lines, "- DATETIME:", second + 1)
    stories = line_of(lines, "## Stories (Required to Complete)")
    tasks = line_of(lines, "## Tasks (Cross-Cutting or Epic-Level)")
    return {"notes": f"{first + 1}-{third - 1}", "decision": f"{first + 1}-{second - 1}",
            "stories": f"{stories + 1}-{tasks - 1}"}


def fix_story(slug: str, text: str, ranges: dict) -> str:
    """One story's wraps, evidence range, M1-28 gate corrections and draft transition."""
    text = rep(text, "- Updated: 2026-10-18T11:45:58Z\n", f"- Updated: {NOW}\n")
    text = rep(text, OLD_PLAN_CLAIM, NEW_PLAN_CLAIM)
    text = rep(text, f"  EVIDENCE: {EPIC_REF}\n", f"  EVIDENCE: {EPIC_REF}:{ranges['notes']}\n")
    ready_reason = OLD_REASON + "; scope and owner set, the open questions named.\n"
    draft_reasons = {
        "revalidate_on_binding_change": "stays draft until S1 and S2 land and its open questions are answered.",
        "one_registration_per_object": "stays draft until S1 lands and the epic's call 5 (scope) is made.",
        "spell_id_migration": "stays draft until S1-S4's patches are approved and the record policy is called.",
    }
    if slug in draft_reasons:
        text = rep(text, "- from_state: draft\n- to_state: draft\n" + OLD_REASON + ".\n",
                   "- from_state: (new)\n- to_state: draft\n- transition_reason: filed under"
                   " EPIC-2026-10-18-spell_identity_is_the_code on the owner's direction (chat\n  2026-10-18); "
                   + draft_reasons[slug] + "\n")
    else:
        text = rep(text, ready_reason,
                   "- transition_reason: filed under EPIC-2026-10-18-spell_identity_is_the_code on the owner's"
                   " direction (chat\n  2026-10-18); scope and owner set, the open questions named.\n")
    gates = {
        "binding_manifest_hash": [
            ("component patch approved; melder_1's release of spell.py\n  (the Spell carries the manifest); the board"
             " row.\n", "component patch approved; the board row.\n"),
            ("- DEPENDENCIES: S1 (lands with it); melder_1's release of spell.py.\n",
             "- DEPENDENCIES: S1 (lands with it).\n"),
            ("- FAILURE_ESCALATION: CONFLICT while spell.py is held; DECISION_REQUEST on which fields the binding"
             " hash covers.\n",
             "- FAILURE_ESCALATION: CONFLICT if another lane takes spell.py; DECISION_REQUEST on which fields the"
             " binding\n  hash covers.\n"),
            ("- State: ready (melder_0); waiting on S1's patch and melder_1's release of spell.py.\n",
             "- State: ready (melder_0); waiting on S1's patch (melder_1's files are free since M1-28).\n"),
        ],
        "revalidate_on_binding_change": [
            ("component patch approved; melder_1's release of spellbook.py and\n  conduit.py; the board row.\n",
             "component patch approved; the board row.\n"),
            ("- DEPENDENCIES: S1, S2; melder_1's release; the notch's", "- DEPENDENCIES: S1, S2; the notch's"),
            ("old objects; CONFLICT while\n  a needed file is held.\n",
             "old objects; CONFLICT if\n  another lane takes a needed file.\n"),
        ],
        "one_registration_per_object": [
            ("component patch approved; melder_1's release of spellbook.py; the board row.\n",
             "component patch approved; the board row.\n"),
            ("- DEPENDENCIES: S1; melder_1's release; the owner's", "- DEPENDENCIES: S1; the owner's"),
            ("CONFLICT while spellbook.py is held.\n", "CONFLICT if another lane takes spellbook.py.\n"),
        ],
        "spell_id_migration": [
            ("this story's component patch; melder_1's release of restore_engine.py and\n  graft_runner.py; the board"
             " row.\n", "this story's component patch approved; the board row.\n"),
            ("- DEPENDENCIES: S1-S4; melder_1's release; the owner's", "- DEPENDENCIES: S1-S4; the owner's"),
            ("CONFLICT while a needed file is held.\n", "CONFLICT if another lane takes a needed file.\n"),
        ],
    }
    for old, new in gates.get(slug, []):
        text = rep(text, old, new)
    if slug in gates:
        entry = "(the epic's DECISION note).\n"
        text = rep(text, entry, entry + f"- {NOW}: melder_1's files are free (M1-28; the epic's FACT note of {NOW});"
                   " the entry gate\n  no longer waits on a release.\n")
    return text


def fix_s6(text: str, ranges: dict) -> str:
    """S6's two closure notes cite the epic without ranges, and __version__ (0.2.8255 now) for part A's 0.2.8254."""
    text = rep(text, f"  - {EPIC_REF}\n  IMPACT: Part B's staging refusal",
               f"  - {EPIC_REF}:{ranges['decision']}\n  IMPACT: Part B's staging refusal")
    text = rep(text, f"  - {EPIC_REF}\n  - src/melder/__version__.py:12-12\n  IMPACT: Nothing of this story",
               f"  - {EPIC_REF}:{ranges['stories']}\n  - release_docs/next_version_release.md:434-442\n"
               "  IMPACT: Nothing of this story")
    return text


if __name__ == "__main__":
    epic_text = fix_epic(EPIC.read_text(encoding="utf-8"))
    EPIC.write_text(epic_text, encoding="utf-8")
    found = epic_ranges(epic_text)
    print("epic", found)
    for slug, path in STORIES.items():
        path.write_text(fix_story(slug, path.read_text(encoding="utf-8"), found), encoding="utf-8")
        print("story", slug)
    S6.write_text(fix_s6(S6.read_text(encoding="utf-8"), found), encoding="utf-8")
    print("s6")
