"""Record the 0.2.8266 rebuild in the closed task and hand the shared documents to melder_1 (melder_0, 2026-10-24).

One all-or-nothing pass: Note 33 (the MEASURE of the rebuild) in the completed ticket, its "Rebuild last" step and
"Steps complete" ticked with what ran, the handoff summary's last sentence and Updated; NOTICE M0-219 to melder_1
with its alert line; melder_0's roster row refreshed. Refuses when a message addressed to melder_0 waits (consume it
first), when a file changed since it was read, or when a line breaks the width rule or holds a CR.
Usage: record_rebuild_20261024.py --check | --apply
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record

DONE = "tickets/tasks/completed/2026-10-24_cache_file_write_failure_fails_meld_task.md"
RUNS = "artifacts/cache_write_failure_20261024/runs/"
SCRIPT = "artifacts/cache_write_failure_20261024/scripts/rebuild_assets_20261024.py"
CI_TASK = "tickets/tasks/2026-10-24_ci_lane_loose_ends_task.md"
M1_STORY = "tickets/stories/2026-10-24_remove_many_child_holder_ownership_story.md"


class Pass(Record):
    """The rebuild record and the hand-off."""

    def checked_flush(self, apply: bool) -> None:
        for rel, before in self.original.items():
            if (self.ROOT / rel).read_text(encoding="utf-8") != before:
                sys.exit(f"RACE {rel}: changed since it was read; nothing written")
        for rel, text in self.staged.items():
            if "\r" in text:
                sys.exit(f"CR in {rel}")
        if not apply:
            for rel, text in self.staged.items():
                print("would write", rel, len(text.split("\n")) - 1, "lines")
            print("checked; nothing written")
            return
        self.flush()


def edit_ticket(r: Pass) -> None:
    text = r.read(DONE)
    text = r.once(text, """\
- [ ] Rebuild last: the asset runner and the llm_support builder, both --check OK.
""", """\
- [x] Rebuild last: the asset runner and the llm_support builder, both --check OK. Run (Note 33): the runner OK;
      the bundles' src and other OK, tests stale behind melder_2's CI edits in flight, left to the next landing.
""", "step")
    text = r.once(text, "- [ ] Steps complete and checked off\n", "- [x] Steps complete and checked off\n", "done")
    text = r.once(text, """\
TASK-2026-10-24-identify_windows_cache_file_holder. Last step: the asset and LLM rebuild with both checks, recorded
in the Note after closure.
""", """\
TASK-2026-10-24-identify_windows_cache_file_holder. The rebuild ran last (Note 33): the assets are OK at 0.2.8266;
the bundles' src and other corpora are OK, and tests is left to the next landing's rebuild behind melder_2's CI
edits in flight.
""", "summary")
    count = len((r.ROOT / RUNS / "rebuild_checks_0_2_8266.txt").read_text(encoding="utf-8").rstrip("\n").split("\n"))
    measure = r.note(r.now, "MEASURE", [
        "Rebuild, last (21:34-21:35): the asset runner, run in a /tmp mirror of src/ and the system documents",
        "(melder_1's procedure with its mirror root moved), rewrote eight files under src/melder/_build_assets/ for",
        "0.2.8266 - the bind guard at 629 entries with melder_1's removal - and its --check in the repository prints",
        "three OK lines. The LLM builder (--include-untracked) wrote src, tests and other; its --check prints OK for",
        "src and other and STALE for tests: melder_2's CI edits in flight (M2-32, on the owner's word, no src)",
        "rewrote three tests/unit/github_workflows files at 21:35:34, after the build. That corpus is left to the",
        "next landing's rebuild, which M2-32 asks of melder_1's 0.2.8267 landing and which covers this lane's",
        "changes too; rebuilding again would only race an edit in progress. No .git/index.lock appeared."],
        [f"context_compass/{RUNS}rebuild_assets_0_2_8266.txt:1-13",
         f"context_compass/{RUNS}rebuild_checks_0_2_8266.txt:1-{count}",
         r.whole(SCRIPT),
         r.note_range(CI_TASK, "- DATETIME: 2026-10-24T21:25:11Z", "  TYPE: PLAN"),
         r.note_range(M1_STORY, "- DATETIME: 2026-10-24T21:17:38Z", "  TYPE: FACT")],
        ["The lane is turned in: the packaged documents and assets carry 0.2.8266 and the bundles' src and other",
         "corpora are current; melder_1 applies its document edits now (its Note of 21:17:38Z waits on this)."],
        ["None in this lane; melder_1's landing rebuilds after melder_2's NOTICE that its CI edits are done."],
        "HELPFUL", 8)
    text = r.once(text, "\n\n## Context / Handoff Summary\n", "\n\n" + measure + "\n\n## Context / Handoff Summary\n",
                  "note")
    r.check_width(text, "ticket")
    r.stage(DONE, text)
    r.set_field(DONE, "Updated")


def edit_mailbox(r: Pass) -> None:
    text = r.read(r.MAILBOX)
    region = text[text.index("<!-- BEGIN USER-DEFINED: messages -->"):text.index("<!-- END USER-DEFINED: messages -->")]
    if re.search(r"^- TO: melder_0$", region, flags=re.M):
        sys.exit("MESSAGE for melder_0 waiting: consume it first; nothing written")
    rows = re.findall(r"^\| melder_0 \| claude \| 2026-09-26T22:24:06Z \| \S+ \| active \|$", text, flags=re.M)
    if len(rows) != 1:
        sys.exit(f"ROW melder_0: {len(rows)}")
    text = text.replace(rows[0], f"| melder_0 | claude | 2026-09-26T22:24:06Z | {r.now} | active |")
    message = f"""\
- TO: melder_1
  FROM: melder_0
  DATETIME: {r.now}
  TYPE: NOTICE
  CLAIM: M0-219. TASK-2026-10-24-cache_file_write_failure_fails_meld is closed and its rebuild has run, so the
    shared documents are yours (your 21:17:38Z note waits on this). The asset runner's --check is OK at 0.2.8266
    (the bind guard at 629 entries, your removal). The LLM bundles' src and other corpora check OK; tests is
    STALE: melder_2's CI edits in flight (M2-32) rewrote three tests/unit/github_workflows files at 21:35:34,
    after the build - your landing's rebuild covers them, as M2-32 asks. My patch folder
    cache_save_best_effort_2026_10_24 moved to system_docs/patches/completed/.
  EVIDENCE:
    context_compass/tickets/tasks/completed/2026-10-24_cache_file_write_failure_fails_meld_task.md (Notes 32-33)
    context_compass/{RUNS}rebuild_checks_0_2_8266.txt
  ACK_REQUESTED: false
"""
    text = r.once(text, "<!-- END USER-DEFINED: messages -->", message + "<!-- END USER-DEFINED: messages -->",
                  "message")
    r.stage(r.MAILBOX, text)
    board = r.read(r.BOARD)
    board = r.once(board, "<!-- END USER-DEFINED: alerts -->",
                   f"- NEW MESSAGE for melder_1 (from melder_0, {r.now})\n<!-- END USER-DEFINED: alerts -->", "alert")
    r.stage(r.BOARD, board)


def main() -> None:
    if sys.argv[1:] not in (["--check"], ["--apply"]):
        sys.exit(__doc__)
    r = Pass("record_rebuild")
    edit_ticket(r)
    edit_mailbox(r)
    r.checked_flush(sys.argv[1] == "--apply")


if __name__ == "__main__":
    main()
