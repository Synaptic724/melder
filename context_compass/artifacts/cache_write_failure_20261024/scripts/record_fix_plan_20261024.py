"""Record the prototype check, the fix PLAN and the owner's decisions (melder_0, 2026-10-24).

TASK-2026-10-24-cache_file_write_failure_fails_meld: appends a MEASURE (the /tmp prototype turns the nine tests
green; one existing stub test reacts), a PLAN (fix steps F1-F6 mapped to the tests) and a DECISION_REQUEST (D1-D4),
ticks the round's steps, updates Validation and the resume view, moves the board row to review/handoff and refreshes
the artifact row. All-or-nothing: anchors match once, lines fit 120 characters, no CR, and a file that changed since
it was read refuses the pass.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record

TICKET = "tickets/tasks/2026-10-24_cache_file_write_failure_fails_meld_task.md"
FOLDER = "artifacts/cache_write_failure_20261024"
STUB_TESTS = "tests/unit/melder/spellbook/test_cache_runtime_verification.py"


class Pass(Record):
    """The plan pass."""

    def checked_flush(self) -> None:
        for rel, before in self.original.items():
            if (self.ROOT / rel).read_text(encoding="utf-8") != before:
                sys.exit(f"RACE {rel}: changed since it was read; nothing written")
        self.flush()


def notes(r: Pass) -> str:
    measure = r.note(r.now, "MEASURE", [
        "The tests can pass. A throwaway prototype of directions 1 and 2, applied to the /tmp copy only (the",
        "repository's src is unchanged): `CachingSystem.emit()` returns a bool and never raises OSError - the temp",
        "file named per writer (pid and thread), the rename retried on PermissionError on Windows only, a failed save",
        "removing its temp file, logging a warning and returning False - and `_emit_cache_file_if_required` returning",
        "what emit returned, its flag left cleared after a refusal. Under it the nine tests pass, the GIL off and on.",
        "Of 272 existing cache-related tests (15 files: the CachingSystem and cache-orchestration units, the",
        "conjure-cache, structural-snapshot, world-stamp and contract-override components, the two cache integration",
        "files, three conduit components) 271 pass and one fails: `test_emit_cache_file_if_required_emits_once_",
        "when_required`, whose stub `emit()` returns None where the prototype passes emit's result on."],
        [f"context_compass/{FOLDER}/scripts/prototype_fix_in_tmp_copy_20261024.py:1-99",
         f"context_compass/{FOLDER}/runs/regression_tests_under_tmp_prototype_20261024.txt:1-31",
         f"{STUB_TESTS}:51-54",
         f"{STUB_TESTS}:262-275"],
        ["The tests are passable as written and need no change for the recommended fix; the contract change touches one",
         "existing stub test, which must return True from `emit()`."],
        ["Record the fix PLAN mapped to the tests, and the owner's decisions."], "REQUIRED", 9)
    plan = r.note(r.now, "PLAN", [
        "The fix, built around the tests; nothing is applied before the owner's go (Note 20). Tests T1-T5 are the",
        "component tests in Note 16's order, T6 the unit test.",
        "F1 `CachingSystem.emit()` returns a bool and never raises OSError: mkdir, temp write and rename under the",
        "instance lock; on OSError it removes its own temp file, logs a WARNING naming the bundle, the error and the",
        "remedy (folder permissions; on Windows a scanner exclusion), keeps the staged payloads in memory and returns",
        "False. Turns green T1-T5 (every meld door, rename or temp write, once or always) and T6 (no temp file).",
        "F2 Windows robustness in the same method: a temp file per writer (`<conduit>.meldercache.<pid>.<thread>.tmp`),",
        "so processes sharing a frame and root name never share one; a PermissionError on the rename retried on",
        "Windows only, a few times within about 100 ms (POSIX renames never refuse for sharing; a read-only folder",
        "fails fast). New unit tests: a rename refused twice then allowed saves the bundle (platform gate patched);",
        "a lasting refusal returns False and logs once; the temp name carries pid and thread.",
        "F3 `Spellbook._emit_cache_file_if_required` returns what emit returned; after an OS refusal its flag stays",
        "cleared - no retry on every meld, so no retry storm and no Windows backoff on the hot path - and the next",
        "staging or conjure saves what is still staged; any other exception keeps today's restore-and-raise (a Melder",
        "bug must surface). Docstring rewritten; the stub test returns True. Turns T2's warm melds and T3's first",
        "melds into no-save melds. `Spell.emit_cache_file()` then returns False on a refused save (D2), with a test.",
        "F4 Gates before code: patch docs for the error-semantics change (patch id cache_save_best_effort_2026_10_24:",
        "architecture, component CachingSystem and Spellbook, code description CachingSystem) linked here with the",
        "section -> step -> test mapping; the board re-read for custody (Note 15).",
        "F5 Turn-in: src_architecture (a fixed failure mode, a best-effort-save invariant, the code map) and",
        "src_components (CachingSystem, the Spellbook cache entry) with their indexes; the release-note entry; notch",
        "0.2.8265 -> 0.2.8266 and a NOTICE to the active agents; asset and LLM bundles rebuilt last, both --check OK.",
        "F6 Validation: T1-T6 and the new unit tests, the 15 related files and the full unit, component and",
        "integration trees on a /tmp copy, the GIL off and on; probe A-D rerun (every meld returns, the pool not",
        "exhausted). The owner's MelderOps run on Windows is his to rerun.",
        "Not in this fix (follow-ups for the owner): direction 3 (fewer meld-time saves), direction 4 (cache location",
        "and pruning; 55 trial folders in MelderOps) and the Windows cause (Note 5)."],
        ["src/melder/utilities/caching_system/caching_system.py:728-741",
         "src/melder/utilities/caching_system/caching_system.py:885-918",
         "src/melder/aether/spellbook/spellbook.py:1143-1180",
         "src/melder/aether/spellbook/spell.py:1185-1216",
         r.note_range(TICKET, "- DATETIME: 2026-10-24T18:29:27Z", "  TYPE: DECISION_REQUEST")],
        ["Each fix step names the tests it turns green, so the owner can judge the fix by the tests he already has."],
        ["The owner's answers to Note 20; then F4's patch docs."], "REQUIRED", 9)
    decision = r.note(r.now, "DECISION_REQUEST", [
        "Four calls for the owner before the fix starts; the tests stand whichever he makes:",
        "D1 Go for F1-F3 (directions 1 and 2) as one src change, notch 0.2.8266. Recommended.",
        "D2 `Spell.emit_cache_file()`, the explicit public save, on a refused save: return False and log - its",
        "docstring already promises \"True when ... emitted, otherwise False\" (recommended) - or keep raising the",
        "OSError, which moves the tolerance out of CachingSystem into the meld doors.",
        "D3 Retry the rename on Windows only (recommended), or on every platform.",
        "D4 Log the first refused save of a bundle at WARNING and later ones at DEBUG (recommended), or every one at",
        "WARNING."],
        ["src/melder/aether/spellbook/spell.py:1185-1216",
         "src/melder/aether/spellbook/spellbook.py:1182-1211"],
        ["D2 is a public behaviour change: today an explicit save that the OS refuses raises to its caller."],
        ["The owner answers D1-D4."], "REQUIRED", 9)
    return "\n\n".join([measure, plan, decision])


def ticket(r: Pass) -> None:
    text = r.read(TICKET)
    text = r.once(text, "\n\n## Context / Handoff Summary\n", "\n\n" + notes(r) + "\n\n## Context / Handoff Summary\n",
                  "notes")
    text = r.once(text, "- [ ] Write the regression tests (component tests through the meld doors; a unit test of the save) and run\n",
                  "- [x] Write the regression tests (component tests through the meld doors; a unit test of the save) and run\n",
                  "step tests")
    text = r.once(text, "- [ ] Record the fix PLAN mapped to the tests and report it to the owner; the fix waits for his go.\n",
                  "- [x] Record the fix PLAN mapped to the tests and report it to the owner; the fix waits for his go.\n"
                  "- [ ] On the owner's go (Note 20): patch docs, the fix F1-F3 with its unit tests, the turn-in (F5) and the\n"
                  "      validation (F6).\n", "step plan")
    text = r.once(text, "- Not run yet: the regression tests (this round runs them red on a copy of the tree).\n",
                  "- Run: the regression tests fail on 0.2.8265, 9 of 9, the GIL off and on (Note 17), and pass on a /tmp\n"
                  "  prototype of the fix (Note 18). Not run: the full suites, which run at the fix (F6).\n",
                  "validation")
    sections = re.findall(r"## Context / Handoff Summary\n(?:.+\n)+", text)
    if len(sections) != 1:
        sys.exit(f"SUMMARY: {len(sections)}")
    text = r.once(text, sections[0], "\n".join([
        "## Context / Handoff Summary",
        "Scope: the defect is documented (Notes 1-13). On the owner's word (Note 14) the regression tests exist - a",
        "component file through every kind of meld door and a unit test of the save (PLAN, Note 16) - and fail on",
        "0.2.8265 for the bug, 9 of 9, the GIL off and on (Note 17); a throwaway /tmp prototype of directions 1 and 2",
        "turns them green and moves one existing stub test (Note 18). State: in_progress, melder_0, board row in",
        "review: the fix PLAN (Note 19, F1-F6, each step mapped to the tests) waits for the owner's D1-D4 (Note 20).",
        "Holds: no src change before his go; patch docs (F4) come first; no lane holds caching_system.py or",
        "spellbook.py (Note 15). Open: the Windows cause (Note 5, HYPOTHESIS) - Process Monitor or a run with the",
        "venv excluded from real-time scanning. Next: the owner's answers; then F4-F6. Answered earlier: the",
        "mediators (Notes 11-12) and a single owner module (Note 13) - CachingSystem already is it."]) + "\n",
        "summary")
    r.check_width(text, "ticket")
    r.stage(TICKET, text)
    r.set_field(TICKET, "Updated")


def boards(r: Pass) -> None:
    board = r.read(r.BOARD)
    rows = re.findall(r"^\| cache_write_failure \| in_progress \| implementation \|.*$", board, flags=re.M)
    if len(rows) != 1:
        sys.exit(f"ROW: {len(rows)}")
    cells = rows[0].split(" | ")
    if len(cells) != 12:
        sys.exit(f"ROW CELLS: {len(cells)}")
    cells[1] = "review"
    cells[2] = "handoff"
    cells[6] = "The owner answers D1-D4 (Note 20) on the fix PLAN (Note 19); on his go, patch docs then the fix."
    cells[10] = r.now
    board = r.once(board, rows[0], " | ".join(cells), "board row")
    r.stage(r.BOARD, board)
    arts = r.read(r.ARTIFACTS)
    old_rows = re.findall(rf"^\| {re.escape(TICKET)} \| {re.escape(FOLDER)}/ \|.*$", arts, flags=re.M)
    if len(old_rows) != 1:
        sys.exit(f"ARTIFACT ROW: {len(old_rows)}")
    new_row = (f"| {TICKET} | {FOLDER}/ | defect_reproducer | active | retain_as_reference | Probe cases A-D, the "
               "regression tests' red runs on 0.2.8265 (GIL off and on) and their green run on the /tmp prototype "
               "(scripts/prototype_fix_in_tmp_copy_20261024.py); rerun the probe and the tests at the fix. | "
               f"{r.now} | REQUIRED |")
    arts = r.once(arts, old_rows[0], new_row, "artifact row")
    r.stage(r.ARTIFACTS, arts)


def main() -> None:
    r = Pass("record_fix_plan")
    ticket(r)
    boards(r)
    r.checked_flush()


if __name__ == "__main__":
    main()
