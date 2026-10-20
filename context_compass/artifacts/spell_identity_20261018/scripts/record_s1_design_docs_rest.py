"""Finish recording S1's design docs (melder_0, 2026-10-18). record_s1_design_docs.py wrote the story's part
(13:30:00Z) and stopped at an epic anchor that did not exist; this script does the rest: the epic's tasks, open
questions, decision log, artifact links, DECISION_REQUEST note and handoff; two story fixes (a long line, a task
date); one code-description patch line; the board rows. Exact-anchor edits; each anchor must occur once."""
import datetime
import pathlib
import sys

ROOT = pathlib.Path.home() / "mnt/melder_private/context_compass"
TS = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
EPIC = "tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md"
STORY = "tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md"
PATCH = "system_docs/patches/active/spell_identity_is_the_code_2026_10_18"


def apply(text: str, path: str, pairs: list) -> str:
    for old, new in pairs:
        count = text.count(old)
        if count != 1:
            sys.exit(f"{path}: anchor found {count} times: {old[:90]!r}")
        text = text.replace(old, new)
    return text


def edit(path: str, pairs: list) -> None:
    p = ROOT / path
    p.write_text(apply(p.read_text(encoding="utf-8"), path, pairs), encoding="utf-8")


def replace_bullet(text: str, path: str, head: str, stop: str, new: str) -> str:
    if text.count(head) != 1:
        sys.exit(f"{path}: bullet head found {text.count(head)} times: {head[:60]!r}")
    start = text.index(head)
    end = text.index(stop, start)
    return text[:start] + new + text[end:]


epic_note = f"""- DATETIME: {TS}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: S1's design docs are written for the owner's approval (the architecture patch, the Binding Pipeline and
    Spell Examination Profiles component patches and the code-description patch, in
    system_docs/patches/active/spell_identity_is_the_code_2026_10_18/), with three decisions for him: (1) the
    "conduit manifest" reading (S2; asked 2026-10-18); (2) third-party code and objects - A (recommended):
    digested like the application's, so a package upgrade moves the ids and a third-party object with per-process
    state makes its holder's id differ per process; B: named by qualified name and distribution version, bounded
    but blind to settings kept inside library objects; (3) a record made before the change that holds one object
    twice: restore the first and file a shortfall per dropped duplicate (recommended), or refuse the restore whole.
    Stated for him rather than asked: one object binds once per process by default (call 5), so a second Book that
    binds the same class is refused and shares it instead; a closure's captured values count; equal-data objects
    are one spell; code a spell only names is not hashed.
  EVIDENCE:
  - context_compass/{PATCH}/architecture_patch.md:51-75
  - context_compass/{PATCH}/architecture_patch.md:159-180
  - context_compass/artifacts/spell_identity_20261018/runs/probe_code_digest_design_edges_gil0_seed1.txt:1-13
  IMPACT: No src/ edit before his approval; S2's patches follow his answer on (1); (2) decides whether S1 digests
    installed packages; (3) decides how S5 restores old records.
  NEXT: Report the docs to the owner plainly, with the Greeter example; on approval, the blast-radius run in a
    /tmp mirror.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation"""

new_state = """- State: in_progress (melder_0), discovery. The owner made all five calls (DECISION notes of
  2026-10-18T12:15:14Z and 2026-10-18T13:06:51Z: renames count). S1 is in_progress: its four patch docs are
  written and wait for his approval and three decisions (DECISION_REQUEST note); S2 ready, S3-S5 draft; nothing
  in src/ yet. Evidence: the probes and the patch folder in Artifact Links. S6 of the correctness epic is turned
  in; its part B and open items live here. The owner's order is parallel (M1-30, M1-32): melder_1 fixes
  correctness stories one at a time (S8, then S4, S7 and S9) and holds spellbook.py, conduit.py,
  spellbook_validation_error.py and change_control_manager.py for S8 until it lands; three correctness stories
  wait for this epic (Constraints); the next notch is above 0.2.8255, or above S8's.
"""

new_next = """- Next: (1) the owner's approval of the architecture patch and S1's patches (written 2026-10-18) and his three
  decisions - the "conduit manifest" reading, third-party code, legacy duplicates (DECISION_REQUEST note); (2) the
  blast-radius run in a /tmp mirror; (3) S2's component patches; (4) claim spellbook.py back from melder_1 before
  S1's src edit.
"""

p = ROOT / EPIC
text = p.read_text(encoding="utf-8")
text = apply(text, EPIC, [
    ("- Updated: 2026-10-18T13:06:51Z\n", f"- Updated: {TS}\n"),
    ("- [ ] Task: the owner's calls on the open edges (Open Questions).\n",
     "- [x] Task: the owner's calls on the open edges (Open Questions; all five made 2026-10-18).\n"),
    ("- [ ] Task: the architecture patch for the epic; a component patch per story before its code.\n",
     "- [ ] Task: the architecture patch for the epic; a component patch per story before its code (the architecture\n"
     "  patch and S1's patches written 2026-10-18; the owner's approval pending).\n"),
    ("- For S3: which binding fields revalidate and which only rebind",
     "- Third-party code and objects (S1): A, digested like the application's (recommended), or B, named by qualified\n"
     "  name and distribution version (architecture patch; DECISION_REQUEST note).\n"
     "- A record made before the change that holds one object twice (S5): restore the first and file a shortfall per\n"
     "  dropped duplicate (recommended), or refuse the restore whole (architecture patch; DECISION_REQUEST note).\n"
     "- For S3: which binding fields revalidate and which only rebind"),
    ("  S8 until it lands (FACT note).\n",
     "  S8 until it lands (FACT note).\n"
     f"- {TS}: S1's design docs written; three decisions with the owner (DECISION_REQUEST note).\n"),
    ("  - artifacts/spell_identity_20261018/ (the epic's scripts)\n",
     "  - artifacts/spell_identity_20261018/ (the epic's scripts)\n"
     f"  - {PATCH}/ (the architecture patch; S1's component and code-description patches)\n"),
    ("- DISPOSITION: retain_as_reference\n",
     "- DISPOSITION: retain_as_reference (the probes and scripts); promote_to_documentation (the patch docs, at landing)\n"),
    ("## Closure Confirmation", epic_note),
])
text = replace_bullet(text, EPIC, "- State: in_progress (melder_0), discovery. The owner made all five calls",
                      "- Next: (1) S1's design docs", new_state)
text = replace_bullet(text, EPIC, "- Next: (1) S1's design docs", "\n## Project-Specific Additions", new_next)
p.write_text(text, encoding="utf-8")

edit(STORY, [
    ("- Updated: 2026-10-18T13:30:00Z\n", f"- Updated: {TS}\n"),
    ("  is the code-description patch (system_docs/patches/active/spell_identity_is_the_code_2026_10_18/"
     "code_description_patch_spell_code_digest.md; corrected here\n  2026-10-18T13:30:00Z).\n",
     "  is the code-description patch, corrected here 2026-10-18T13:30:00Z:\n"
     f"  {PATCH}/code_description_patch_spell_code_digest.md.\n"),
    ("  code-description) - written 2026-10-18T13:30:00Z, the owner's approval pending.\n",
     "  code-description) - written 2026-10-18, the owner's approval pending.\n"),
])

edit(f"{PATCH}/code_description_patch_spell_code_digest.md", [
    ("- Updated: 2026-10-18T13:21:00Z\n", f"- Updated: {TS}\n"),
    ("- Cost: the corpus probe (782 targets of src/melder) and D9 against the bind-cost budget the architecture patch\n"
     "  sets.\n",
     "- Cost: the corpus probe (782 targets of src/melder) and D9 against today's fingerprint, as the architecture\n"
     "  patch's Validation Expectations and Evidence Plan list them.\n"),
])

# attention board rows (re-read just before the write)
ab = ROOT / "attention_board.md"
lines = ab.read_text(encoding="utf-8").split("\n")
new_next_cells = {
    "correctness_defects": "Keep the record current as melder_1 fixes S8, then S4, S7 and S9, one at a time (M1-30, M1-32).",
    "spell_identity_is_the_code": "The owner's approval of S1's patches and his three decisions (conduit manifest, third-party code, legacy duplicates).",
    "spell_id_code_hash": "The owner's approval of the patches; then the blast-radius run in a /tmp mirror.",
}
seen = set()
for index, line in enumerate(lines):
    if not line.startswith("| "):
        continue
    cells = line.split(" | ")
    key = cells[0][2:]
    if key in new_next_cells and len(cells) == 12:
        cells[6] = new_next_cells[key]
        cells[10] = TS
        lines[index] = " | ".join(cells)
        seen.add(key)
if seen != set(new_next_cells):
    sys.exit(f"attention rows updated: {sorted(seen)}")
ab.write_text("\n".join(lines), encoding="utf-8")

edit("artifact_board.md", [
    ("record_s1_measure.py and sync_s1_artifact_rows.py (S1's MEASURE note and rows); probes/ and runs/ are rowed under S1."
     " | 2026-10-18T12:45:46Z |",
     "record_s1_measure.py and sync_s1_artifact_rows.py (S1's MEASURE note and rows), record_s1_design_docs.py (its story"
     " part ran; it stopped at a missed epic anchor) and record_s1_design_docs_rest.py (the rest of S1's design-doc record);"
     f" probes/ and runs/ are rowed under S1. | {TS} |"),
    ("(probe_code_digest_cases.py) and the src/melder corpus and cost probe (probe_code_digest_corpus.py), with their runs"
     " under runs/ (hash seeds 1 and 2, GIL 0 and 1); S1's tests start here. | 2026-10-18T12:45:46Z | REQUIRED |",
     "(probe_code_digest_cases.py), the src/melder corpus and cost probe (probe_code_digest_corpus.py) and the design"
     " edges D1-D10 (probe_code_digest_design_edges.py), with their runs under runs/ (hash seeds 1 and 2, GIL 0 and 1;"
     f" the design edges seed 1 only); S1's tests start here. | {TS} | REQUIRED |\n"
     f"| tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md | {PATCH}/ | patch_doc | active |"
     " promote_to_documentation | The epic's architecture patch and S1's Binding Pipeline, Spell Examination Profiles and"
     " code-description patches; the owner's approval before any src edit; S2-S5 add theirs."
     f" | {TS} | REQUIRED |"),
])
print("TS", TS)
