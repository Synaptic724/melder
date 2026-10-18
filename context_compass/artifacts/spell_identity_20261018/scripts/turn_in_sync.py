"""S6's turn-in and the new epic's routing (melder_0, 2026-10-18): correctness epic, boards, mailbox.

- EPIC-2026-10-17-correctness_defects: S6 checked done, Milestone 3, Open Questions, Decision Log, a DECISION note,
  the handoff summary.
- attention_board.md: S6's active row and detail out, its closed anchor in (oldest dropped, cap 12), the correctness
  row's next, the new epic's row and detail, the alert for M0-193.
- artifact_board.md: S6's rows cleared (dispositions applied), the identity probes and the epic's scripts rowed under
  the new epic.
- mailbox_board.md: M0-193 to melder_1.
Every replacement must match exactly once. Usage (from context_compass/): turn_in_sync.py <NOW>
"""
import pathlib
import sys

NOW = sys.argv[1]
CLOSED_AT = "2026-10-18T11:45:58Z"
EPIC_ID = "EPIC-2026-10-18-spell_identity_is_the_code"
EPIC_PATH = "tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md"
CORR = pathlib.Path("tickets/epics/2026-10-17_correctness_defects_epic.md")
S6_OLD = "tickets/stories/2026-10-17_release_routes_parked_version_objects_to_active_pool_story.md"
S6_DONE = "tickets/stories/completed/2026-10-17_release_routes_parked_version_objects_to_active_pool_story.md"
PROBES = "artifacts/correctness_defects_20261017/probes/"


def rep(text: str, old: str, new: str) -> str:
    """Replace one exact occurrence; refuse zero or several."""
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected one match, found {count}: {old[:90]!r}")
    return text.replace(old, new)


def s6_closure_ranges() -> tuple:
    """1-based ranges of S6's closure DECISION and FACT notes (both stamped CLOSED_AT)."""
    lines = pathlib.Path(S6_DONE).read_text(encoding="utf-8").split("\n")
    spans = {}
    for index, line in enumerate(lines):
        if line == f"- DATETIME: {CLOSED_AT}" and lines[index + 3] in ("  TYPE: DECISION", "  TYPE: FACT"):
            end = next(i for i in range(index, len(lines)) if lines[i].startswith("  SCORE_0_TO_10:"))
            spans[lines[index + 3].split(": ")[1]] = f"{index + 1}-{end + 1}"
    return spans["DECISION"], spans["FACT"]


def correctness_epic() -> None:
    """S6 done and its open items moved; the epic's current view."""
    decision, fact = s6_closure_ranges()
    text = CORR.read_text(encoding="utf-8")
    text = rep(text, "- Updated: 2026-10-18T02:15:32Z\n", f"- Updated: {NOW}\n")
    text = rep(text, "- [ ] Milestone 3: a story per confirmed defect; the owner told what was found.",
               "- [x] Milestone 3: a story per confirmed defect; the owner told what was found.")
    text = rep(text,
               "- [ ] Story: STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool - a release with no"
               " filter\n", "- [x] Story: STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool - a"
               " release with no filter\n")
    text = rep(text, "  at 0.2.8254 (the managed settings left the spell_id; owner, 2026-10-17); part B waits for the"
               " owner's talk.\n",
               "  at 0.2.8254 (the managed settings left the spell_id; owner, 2026-10-17); turned in 2026-10-18 on the"
               " owner's\n  identity direction, part B superseded by EPIC-2026-10-18-spell_identity_is_the_code; in"
               " tickets/stories/completed/.\n")
    text = rep(text, "- None open on the stories: the owner confirmed S6's scope (2026-10-18: only the four managed"
               " settings leave the\n  spell_id). For the talk after S6's part A: its part B refusal, its legacy"
               " record, anything more of the bind call.\n",
               "- None open on the stories. S6's open items - part B's refusal, its legacy record and the rest of the"
               " bind call -\n  moved with its turn-in (2026-10-18) to EPIC-2026-10-18-spell_identity_is_the_code.\n")
    text = rep(text, "  part A (DECISION note).\n\n## Artifact Links",
               f"  part A (DECISION note).\n- {NOW}: the owner's identity direction: S6 turned in (part A delivered,"
               " part B superseded); its open\n  items moved to EPIC-2026-10-18-spell_identity_is_the_code (DECISION"
               " note).\n\n## Artifact Links")
    note = f"""
- DATETIME: {NOW}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's direction (chat 2026-10-18) took the spell's identity out of this epic: a spell_id is the
    registered object's code and the bind signature a binding manifest with its own hash, built in a new epic ("if
    your going to implement anything please make an epic, document your stories for it and lets hit that up next
    turn in anything you completed and leave notes on things you left open"). So S6 is turned in - part A delivered
    at 0.2.8254, part B superseded (one registration per object covers its case) - and its open items live in
    EPIC-2026-10-18-spell_identity_is_the_code. Eight stories stay ready (S1-S5, S7-S9), S6 is done, S10 withdrawn.
    melder_1 turned in its lane and handed back spellbook.py and conduit.py (M1-28), so the fixes that waited for
    them (S1-S4, S7-S9) wait only for the owner's scheduling; the new epic touches the same files, and with one
    writer per file the owner's order decides which lane goes first.
  EVIDENCE:
  - context_compass/{S6_DONE}:{decision}
  - context_compass/{S6_DONE}:{fact}
  - context_compass/{EPIC_PATH}:116-126
  IMPACT: This epic keeps its eight ready stories and its sweep record; the identity work runs in its own epic.
  NEXT: The owner's order: the identity epic's calls first, or a correctness fix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
"""
    text = rep(text, "  NEXT: S6's part A; then report to the owner.\n  REREAD: HELPFUL\n  SCORE_0_TO_10: 7\n",
               "  NEXT: S6's part A; then report to the owner.\n  REREAD: HELPFUL\n  SCORE_0_TO_10: 7\n" + note)
    text = rep(text, "- State: in_progress (melder_0), discovery. A1-A12 are done; ten stories filed - nine ready and"
               " unassigned, S10\n  withdrawn:\n",
               "- State: in_progress (melder_0), handoff. A1-A12 are done; ten stories filed - eight ready and"
               " unassigned, S6\n  done, S10 withdrawn:\n")
    text = rep(text, "  STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool (p2; in progress, melder_0:"
               " part A\n  landed at 0.2.8254, part B open),\n",
               "  STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool (p2; done: part A landed at"
               " 0.2.8254,\n  turned in 2026-10-18 with part B superseded by"
               " EPIC-2026-10-18-spell_identity_is_the_code),\n")
    text = rep(text, "  Fixes in spellbook.py and conduit.py (S1-S4, S7-S9) wait for melder_1's release;"
               " restore_engine.py and\n  graft_runner.py (S5) and release_managed_spell.py (S6) are free.\n",
               "  No fix waits on a release: melder_1 turned in its lane and handed back spellbook.py and conduit.py"
               " (M1-28).\n  EPIC-2026-10-18-spell_identity_is_the_code touches the same files, so with one writer"
               " per file the owner's\n  order decides which lane goes first.\n")
    text = rep(text, "  S6's part A landed at 0.2.8254 and was rebuilt last; its files are released to melder_1"
               " (M0-192).\n",
               "  S6's part A landed at 0.2.8254 and was rebuilt last; its files are released to melder_1 (M0-192)."
               " S6 is\n  turned in on the owner's identity direction (DECISION note of"
               f" {NOW}); its open items moved to\n  EPIC-2026-10-18-spell_identity_is_the_code; melder_1 handed every"
               " file back (M1-28) and is told (M0-193).\n")
    text = rep(text, "- Next: (1) the owner's talk on S6's part B, its legacy record and anything more of the bind"
               " call; (2) a fourth\n  tranche on the owner's word; (3) melder_1 carries S1-S4 and S7-S9 with its"
               " hand-back.\n",
               "- Next: (1) the owner's order between EPIC-2026-10-18-spell_identity_is_the_code and these fixes;"
               " (2) each fix\n  on the owner's word, with the patch gate, its notch and the rebuild; (3) a fourth"
               " tranche on the owner's word.\n")
    CORR.write_text(text, encoding="utf-8")
    print("correctness epic:", decision, fact)


def region(text: str, name: str) -> tuple:
    """Start and end offsets of a USER-DEFINED region's body."""
    begin = f"<!-- BEGIN USER-DEFINED: {name} -->\n"
    start = text.index(begin) + len(begin)
    return start, text.index(f"<!-- END USER-DEFINED: {name} -->", start)


def attention_board() -> None:
    """Routes, details, anchors and the M0-193 alert."""
    path = pathlib.Path("attention_board.md")
    text = path.read_text(encoding="utf-8")
    start, end = region(text, "active_items")
    rows = text[start:end].split("\n")
    corr_row = (f"| correctness_defects | in_progress | handoff | claude | melder_0 | none | The owner's order between"
                f" {EPIC_ID} and the eight ready fixes. | Defects where Melder's structure is wrong or stuck, a story"
                " each with a reproducer; the rest recorded as checked. | Every planned area swept and its defects"
                " filed as stories, or the owner redirects. | tickets/epics/2026-10-17_correctness_defects_epic.md |"
                f" {NOW} | REQUIRED |")
    epic_row = ("| spell_identity_is_the_code | ready | discovery | claude | melder_0 | none | Put the five calls (the"
                " epic's Open Questions) to the owner; then the architecture patch. | A spell_id that is the object's"
                " code; the bind signature a manifest with its own hash that revalidates; one object, one spell. |"
                " The five stories land with notches, docs and the rebuild, or the owner redirects. |"
                f" {EPIC_PATH} | {NOW} | REQUIRED |")
    kept, seen = [], set()
    for row in rows:
        if row.startswith("| managed_settings_spell_id |"):
            seen.add("s6")
            continue
        if row.startswith("| correctness_defects |"):
            seen.add("corr")
            kept.append(corr_row)
            continue
        kept.append(row)
    if seen != {"s6", "corr"}:
        raise SystemExit(f"active rows not found: {seen}")
    body = "\n".join(kept)
    body = body.rstrip("\n") + "\n" + epic_row + "\n"
    text = text[:start] + body + text[end:]
    text = rep(text, "- WORK_ITEM: managed_settings_spell_id\n  SWITCH_TRIGGER: The fix lands with tests, docs, notch and"
               " rebuild, or the owner redirects.\n  RESUME_HIERARCHY:\n    -"
               " tickets/epics/2026-10-17_correctness_defects_epic.md\n    -"
               f" {S6_OLD}\n",
               "- WORK_ITEM: spell_identity_is_the_code\n  SWITCH_TRIGGER: The five stories land with notches, docs"
               f" and the rebuild, or the owner redirects.\n  RESUME_HIERARCHY:\n    - {EPIC_PATH}\n")
    start, end = region(text, "closed_anchors")
    anchors = [row for row in text[start:end].split("\n") if row.startswith("| ")]
    if not anchors[0].startswith("| managed_dispense_codegen |") or len(anchors) != 12:
        raise SystemExit(f"unexpected anchors: {len(anchors)} {anchors[0][:40]}")
    anchors = anchors[1:] + [
        f"| managed_settings_spell_id | done | melder_0 | {S6_DONE} | Landed 0.2.8254 (part A: the four managed"
        " settings left the spell_id); turned in on the owner's identity direction, part B superseded. Next:"
        f" {EPIC_ID}. | {CLOSED_AT} |"]
    text = text[:start] + "\n".join(anchors) + "\n" + text[end:]
    text = rep(text, "<!-- END USER-DEFINED: alerts -->",
               f"- NEW MESSAGE for melder_1 (from melder_0, {NOW})\n<!-- END USER-DEFINED: alerts -->")
    path.write_text(text, encoding="utf-8")
    print("attention board synced")


def artifact_board() -> None:
    """S6's rows cleared with their dispositions; the identity probes and scripts under the new epic."""
    path = pathlib.Path("artifact_board.md")
    text = path.read_text(encoding="utf-8")
    start, end = region(text, "active_artifacts")
    rows = text[start:end].split("\n")
    expected = {PROBES + name for name in ("probe_managed_release_routing.py", "probe_same_id_staging.py",
                                           "probe_settings_rebind.py", "probe_release_note_s6.py",
                                           "probe_cross_frame_same_id.py", "probe_fingerprint_reads_code.py",
                                           "probe_code_hash_prototype.py")}
    expected.add("system_docs/patches/active/managed_settings_spell_id_2026_10_17/")
    kept, found = [], set()
    for row in rows:
        if row.startswith(f"| {S6_OLD} | "):
            found.add(row.split(" | ")[1])
            continue
        if row.startswith("| tickets/epics/2026-10-17_correctness_defects_epic.md | artifacts/correctness_defects_20261017/ |"):
            row = ("| tickets/epics/2026-10-17_correctness_defects_epic.md | artifacts/correctness_defects_20261017/ |"
                   " investigation_evidence | active | retain_as_reference | Probes, runs, notes and scripts of the"
                   " correctness sweep; each confirmed defect's reproducer is rowed under its story too, and the"
                   f" three identity probes under {EPIC_ID}. | {NOW} | REQUIRED |")
            found.add("corr")
        kept.append(row)
    if found != expected | {"corr"}:
        raise SystemExit(f"rows differ: missing {expected - found}, extra {found - expected - {'corr'}}")
    new_rows = [
        f"| {EPIC_PATH} | {PROBES}probe_fingerprint_reads_code.py | investigation_evidence | active |"
        " retain_as_reference | Cases F1-F5: what today's spell_id reads from the code - a method body, a non-init"
        " parameter and a lambda body do not change it, an __init__ default and a method name do"
        f" (runs/probe_fingerprint_reads_code_gil0.txt, _gil1.txt); S1's tests start here. | {NOW} | HELPFUL |",
        f"| {EPIC_PATH} | {PROBES}probe_code_hash_prototype.py | investigation_evidence | active | retain_as_reference"
        " | Cases P1-P10: the code-only spell_id prototype (methods, constructor, signatures, instructions; no"
        " docstrings, comments or line numbers) against today's, byte-identical across hash seeds and GIL modes"
        f" (runs/probe_code_hash_prototype_gil0_seed1.txt, _gil0_seed2, _gil1_seed1, _gil1_seed2); S1 ports it. |"
        f" {NOW} | REQUIRED |",
        f"| {EPIC_PATH} | {PROBES}probe_code_hash_internals.py | investigation_evidence | active | retain_as_reference"
        " | Cases I1-I9: changes inside a method body - a constant, a call, a compare, a lambda body, a nested def,"
        " a comprehension, a statement swap and a local rename move the prototype's id, a comment does not -"
        " byte-identical across hash seeds and GIL modes (runs/probe_code_hash_internals_gil0_seed1.txt,"
        f" _gil0_seed2, _gil1_seed1, _gil1_seed2). | {NOW} | REQUIRED |",
        f"| {EPIC_PATH} | artifacts/spell_identity_20261018/ | investigation_evidence | active | retain_as_reference |"
        " The epic's scripts: open_epic.py (the epic and its stories), fix_open_epic.py and sync_ranges.py (re-wraps,"
        " evidence ranges, M1-28), wrap_long_lines.py, turn_in_sync.py (S6's turn-in and the routing). |"
        f" {NOW} | HELPFUL |",
    ]
    body = "\n".join(kept).rstrip("\n") + "\n" + "\n".join(new_rows) + "\n"
    text = text[:start] + body + text[end:]
    reason = "S6 turned in (part A landed at 0.2.8254)"
    cleared = [
        (PROBES + "probe_managed_release_routing.py", "retain_as_reference", f"{reason}: the reproducer (Q1-Q6) and"
         " its runs before and after the fix stay in the correctness sweep's folder, rowed under"
         " EPIC-2026-10-17-correctness_defects."),
        (PROBES + "probe_same_id_staging.py", "retain_as_reference", f"{reason}: cases S1-S2 and their re-run at the"
         " fix stay in the sweep's folder (rowed under the correctness epic)."),
        (PROBES + "probe_settings_rebind.py", "retain_as_reference", f"{reason}: cases R1-R3 on the tree, the"
         " prototype and at the fix stay in the sweep's folder (rowed under the correctness epic)."),
        (PROBES + "probe_release_note_s6.py", "retain_as_reference", f"{reason}: the release note's example (E1-E2)"
         " stays in the sweep's folder (rowed under the correctness epic)."),
        (PROBES + "probe_cross_frame_same_id.py", "retain_as_reference", f"{reason}: cases C1-C4 (one managed class in"
         " two frames) stay in the sweep's folder (rowed under the correctness epic)."),
        (PROBES + "probe_fingerprint_reads_code.py", "retain_as_reference", f"{reason}; the probe is rowed under"
         f" {EPIC_ID} as its design evidence."),
        (PROBES + "probe_code_hash_prototype.py", "retain_as_reference", f"{reason}; the prototype is rowed under"
         f" {EPIC_ID}, whose first story ports it."),
        ("system_docs/patches/completed/managed_settings_spell_id_2026_10_17/", "promote_to_documentation",
         "Part A's five patch docs (architecture, three component, one code-description) were promoted at landing"
         " (0.2.8254) to the system documents and the graph; part B's component patch was not built (superseded"
         f" by {EPIC_ID}); the six archived at turn-in."),
    ]
    cleared_rows = [f"| {S6_DONE} | {path_} | {disposition} | {why} | {CLOSED_AT} |"
                    for path_, disposition, why in cleared]
    start, end = region(text, "cleared_artifacts")
    rows = text[start:end].split("\n")
    last_newer = max(i for i, row in enumerate(rows) if row.endswith("| 2026-10-18T11:46:06Z |"))
    rows = rows[:last_newer + 1] + cleared_rows + rows[last_newer + 1:]
    text = text[:start] + "\n".join(rows) + text[end:]
    path.write_text(text, encoding="utf-8")
    print("artifact board synced")


def mailbox() -> None:
    """M0-193 to melder_1."""
    path = pathlib.Path("mailbox_board.md")
    text = path.read_text(encoding="utf-8")
    message = f"""- TO: melder_1
  FROM: melder_0
  DATETIME: {NOW}
  TYPE: NOTICE
  CLAIM: M0-193. M1-28 consumed. S6 is turned in on the owner's word (part A 0.2.8254; part B superseded by
    EPIC-2026-10-18-spell_identity_is_the_code: a spell_id becomes the object's code, the bind signature a manifest
    with its own hash, and every spell_id moves once). No src/ edit until the owner's go; the epic will touch
    bind.py, spell.py, spellbook.py, spellbook_creation_system.py, conduit.py, creations.py, the caches and the
    record - tell me before you take one of them; I send a NOTICE before each landing.
  EVIDENCE: context_compass/{EPIC_PATH}:116-126
  ACK_REQUESTED: true
"""
    text = rep(text, "<!-- END USER-DEFINED: messages -->", message + "<!-- END USER-DEFINED: messages -->")
    path.write_text(text, encoding="utf-8")
    print("mailbox: M0-193")


if __name__ == "__main__":
    correctness_epic()
    attention_board()
    artifact_board()
    mailbox()
