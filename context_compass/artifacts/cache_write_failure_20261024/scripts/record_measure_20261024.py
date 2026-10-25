"""Record the probe and hand TASK-2026-10-24-cache_file_write_failure_fails_meld to the owner (melder_0, 2026-10-24).

Appends three Notes (the other meld doors, the probe's MEASURE, the fix directions), corrects Note 4's cache size,
moves the task to ready with no executor, removes its attention_board.md row and detail entry and marks its
artifact row ready. All-or-nothing, as the opening pass: anchors match once, lines fit 120 characters, no CR, and a
board changed since it was read is refused.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record

TICKET = "tickets/tasks/2026-10-24_cache_file_write_failure_fails_meld_task.md"
FOLDER = "artifacts/cache_write_failure_20261024"
PROBE = FOLDER + "/probes/probe_cache_emit_failure.py"
RUN0 = FOLDER + "/runs/probe_cache_emit_failure_gil0.txt"
RUN1 = FOLDER + "/runs/probe_cache_emit_failure_gil1.txt"


class Measure(Record):
    """The recording pass."""

    def checked_flush(self) -> None:
        for rel, before in self.original.items():
            if (self.ROOT / rel).read_text(encoding="utf-8") != before:
                sys.exit(f"RACE {rel}: changed since it was read; nothing written")
        self.flush()


def notes(r: Measure) -> list:
    doors = r.note(r.now, "FACT", [
        "Every meld door writes the bundle this way, not only `ConduitMeld.meld`: `Conduit.meld`'s front door (lines",
        "5040-5041), `SpellSpace.meld`'s front door (lines 683-684) and `SpellSpaceMeld.meld` (lines 427-428, 462-463,",
        "628-629, 668-669) call `_emit_cache_file_if_required()` when the flag is set, with the object in hand, and",
        "none catches."],
        ["src/melder/aether/conduit/conduit.py:4864-5090",
         "src/melder/aether/conduit/spell_space/spell_space.py:577-707",
         "src/melder/aether/conduit/meld/spellspace_meld.py:241-677"],
        ["Spell spaces and warm front-door melds fail the same way; one change in `_emit_cache_file_if_required`",
         "covers all nine call sites."],
        ["Record the probe's MEASURE."], "HELPFUL", 8)
    measure = r.note(r.now, "MEASURE", [
        "Probe on the VM: melder 0.2.8265 (a copy of the tree in /tmp/m0_mq/wincache/src), Python 3.14.7",
        "free-threaded, the GIL off and on - the same outcome both ways.",
        "A (the next replace refused once, as Windows did): the first meld of a spell bound after conjure raised",
        "PermissionError after building its object once; the temp file stayed; the next two melds returned that",
        "object (still built once) and the temp file was gone - the retry at the next meld succeeded.",
        "B (frame folder read-only after conjure): the late spell's first meld and three melds of a spell built",
        "earlier (nothing new staged) all raised PermissionError; with the folder writable again the meld returned.",
        "C (conjure-cache root read-only before conjure): conjure returned (its write failed and was only logged), no",
        "frame folder was made, and the first two melds raised PermissionError; writable again, the meld returned.",
        "D (limited_quantity managed spell, limit 1, the leasing meld's replace refused once): the managed meld",
        "raised PermissionError and the next raised ManagedSpellExhaustedError (\"has all 1 objects out\"): the",
        "lease the failed meld took is lost for good (Note 6's UNKNOWN answered: yes)."],
        [r.whole(PROBE), r.whole(RUN0), r.whole(RUN1)],
        ["Notes 2 and 6 are measured: one refused write fails one meld after its work is done, a lasting refusal",
         "fails every meld of the Book, and a managed pool can lose a place until its root is torn down. The",
         "Windows cause (Note 5) is still unmeasured."],
        ["Record the fix directions for the owner (DECISION_REQUEST)."], "REQUIRED", 9)
    decision = r.note(r.now, "DECISION_REQUEST", [
        "Fix directions; the choice is the owner's and nothing is applied.",
        "1. Contract: a creation-cache write is best-effort on every path, as conjure's already is.",
        "`Spellbook._emit_cache_file_if_required` logs a failed write (once per Book, not per meld) and the meld",
        "returns its object; the bundle stays staged in memory for the next conjure or a later write. Fixes A-D and",
        "the owner's failure whatever the Windows cause.",
        "2. Windows robustness in `CachingSystem._write_current_cache_to_disk_locked`: retry `Path.replace` on",
        "PermissionError a few times with a short backoff, remove the temp file when the write still fails, and name",
        "the temp file per writer (process and thread) so two processes on one bundle never share it.",
        "3. Fewer rewrites: coalesce the meld-time writes (the failing configure wrote one bundle twice within 1 ms),",
        "for example at conjure end and then at most once per short interval or at the Book's teardown.",
        "4. Location and growth: allow a cache root outside the package (an absolute path or a per-user cache",
        "folder) and prune frame folders a run will not reuse (55 trial folders sit in the MelderOps venv).",
        "Recommended: 1 with 2 (1 fixes the contract, 2 the Windows symptom); 3 and 4 as follow-ups. Tests at the",
        "fix: a CachingSystem unit test (a refused replace retried; a lasting one logged, its temp file removed) and",
        "component tests through the meld doors (the object returned, the flag kept, a managed lease intact)."],
        [f"context_compass/{TICKET}:1-12", r.whole(RUN0)],
        ["Without 1, any failed write (a Windows scanner, a full disk, a read-only install) fails a user meld after",
         "the work is done and can strand a managed lease for good."],
        ["The owner picks a direction and an executor (spellbook.py is held by melder_1's correctness epic); the",
         "probe is rerun at the fix as its reproducer."], "REQUIRED", 9)
    return [doors, measure, decision]


def main() -> None:
    r = Measure("measure_cache_write_failure")
    text = r.read(TICKET)
    text = r.once(text, "55 per-trial c8pg_ folders (6.4 MB in all)", "55 per-trial c8pg_ folders (5.9 MB of files in all)",
                  "note 4 size")
    text = r.once(text, "- Status: in_progress\n", "- Status: ready\n", "status")
    text = r.once(text, "- Agent Name: melder_0\n", "- Agent Name: unassigned\n", "agent name")
    text = r.once(text, "- Agent Role: synaptic_python_developer\n", "- Agent Role: UNKNOWN\n", "agent role")
    text = r.once(text, """- from_state: draft
- to_state: in_progress
- transition_reason: the owner's "document:" request (chat 2026-10-24) and this task's board row.
""", """- from_state: in_progress
- to_state: ready
- transition_reason: the defect is documented and measured (Notes 1-9) and the fix directions wait for the owner
  (DECISION_REQUEST); no executor is assigned, so the board row is removed.
""", "transition")
    text = r.once(text, "- [ ] Probe cases A-D on a copy of the tree, the GIL off and on; record the MEASURE.\n",
                  "- [x] Probe cases A-D on a copy of the tree, the GIL off and on; record the MEASURE.\n", "step probe")
    text = r.once(text, "- [ ] Record the fix directions as a DECISION_REQUEST; set ready; remove the board row.\n",
                  "- [x] Record the fix directions as a DECISION_REQUEST; set ready; remove the board row.\n",
                  "step decision")
    text = r.once(text, "- [ ] Run Ticket Microcycle during execution:\n",
                  "- [x] Run Ticket Microcycle during execution:\n", "step microcycle")
    text = r.once(text, "- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence\n",
                  "- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence\n",
                  "step findings")
    r.stage(TICKET, text)
    r.set_field(TICKET, "Updated")
    text = r.read(TICKET)
    text = r.once(text, "\n\n## Context / Handoff Summary\n",
                  "\n\n" + "\n\n".join(notes(r)) + "\n\n## Context / Handoff Summary\n", "notes")
    old_summary = re.search(r"\n## Context / Handoff Summary\n(.*?)\n\n## Project-Specific Additions\n", text, re.S)
    if old_summary is None:
        sys.exit("SUMMARY anchor")
    summary = "\n".join([
        "Scope: the defect is documented (the owner's \"document:\", chat 2026-10-24); no src change. State: ready,",
        "no executor, waiting for the owner's pick among the fix directions (the DECISION_REQUEST, last note).",
        "Evidence: the write, its nine meld-door call sites, the conjure-end write and the cache location (Notes 1-3",
        "and 8); the owner's run and its cache folder (Note 4, runs/melderops_cache_listing_20261024.txt); the probe,",
        "cases A-D with the GIL off and on (Note 9, runs/probe_cache_emit_failure_gil0.txt and _gil1.txt). Open: the",
        "Windows cause (Note 5, HYPOTHESIS: a scanner or indexer holding the just-written bundle) - verify with",
        "Process Monitor or a run with the venv excluded from real-time scanning. Holds: spellbook.py is held by",
        "melder_1's correctness epic; MelderOps is another repository. Next: the owner picks a direction and an",
        "executor; the probe is rerun at the fix."])
    text = text.replace(old_summary.group(0),
                        "\n## Context / Handoff Summary\n" + summary + "\n\n## Project-Specific Additions\n", 1)
    r.check_width(text, "ticket")
    r.stage(TICKET, text)
    board = r.read(r.BOARD)
    rows = re.findall(r"^\| cache_write_failure \|.*\n", board, flags=re.M)
    if len(rows) != 1:
        sys.exit(f"ROW: {len(rows)}")
    board = r.once(board, rows[0], "", "board row")
    detail = ("- WORK_ITEM: cache_write_failure\n"
              "  SWITCH_TRIGGER: Ticket ready with its MEASURE and DECISION_REQUEST recorded, or the owner redirects.\n"
              "  RESUME_HIERARCHY:\n"
              f"    - {TICKET}\n")
    board = r.once(board, detail, "", "board detail")
    r.stage(r.BOARD, board)
    arts = r.read(r.ARTIFACTS)
    old_rows = re.findall(rf"^\| {re.escape(TICKET)} \| {re.escape(FOLDER)}/ \|.*$", arts, flags=re.M)
    if len(old_rows) != 1:
        sys.exit(f"ARTIFACT ROW: {len(old_rows)}")
    new_row = (f"| {TICKET} | {FOLDER}/ | defect_reproducer | ready | retain_as_reference | Rerun probe cases A-D "
               "(GIL off and on) at the fix; runs/probe_cache_emit_failure_gil0.txt and _gil1.txt hold the 0.2.8265 "
               f"baseline, runs/melderops_cache_listing_20261024.txt the owner's cache folder. | {r.now} | REQUIRED |")
    arts = r.once(arts, old_rows[0], new_row, "artifact row")
    r.stage(r.ARTIFACTS, arts)
    r.checked_flush()


if __name__ == "__main__":
    main()
