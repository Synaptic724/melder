"""Record the regression tests' red runs on TASK-2026-10-24-cache_file_write_failure_fails_meld (melder_0, 2026-10-24).

Appends one MEASURE Note (the nine red cases, the GIL off and on), ticks nothing yet, refreshes Updated and names
the tests' authorship. All-or-nothing: anchors match once, lines fit 120 characters, no CR, and a ticket that changed
since it was read refuses the pass.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record

TICKET = "tickets/tasks/2026-10-24_cache_file_write_failure_fails_meld_task.md"
RUNS = "artifacts/cache_write_failure_20261024/runs"
REPO = pathlib.Path.home() / "mnt/melder_private"
COMPONENT = "tests/component/melder/aether/conduit/test_conduit_component_refused_cache_save_does_not_fail_meld.py"
UNIT = "tests/unit/melder/utilities/test_caching_system_refused_save.py"


class Pass(Record):
    """The MEASURE pass."""

    def checked_flush(self) -> None:
        for rel, before in self.original.items():
            if (self.ROOT / rel).read_text(encoding="utf-8") != before:
                sys.exit(f"RACE {rel}: changed since it was read; nothing written")
        self.flush()


def whole(rel: str) -> str:
    count = len((REPO / rel).read_text(encoding="utf-8").rstrip("\n").split("\n"))
    return f"{rel}:1-{count}"


def main() -> None:
    r = Pass("record_red_runs")
    measure = r.note(r.now, "MEASURE", [
        "The regression tests fail on 0.2.8265 for the bug, the GIL off and on (a copy of the tree in",
        "/tmp/m0_mq/regress; Python 3.14.7 free-threaded; pytest 9.1.1): 9 of 9 fail, identically both ways.",
        "Component, eight cases: each meld that must return raises the injected PermissionError - the late spell's",
        "first meld (tests 1 and 2, rename and temp write), the first meld after the conjure whose save failed (test 3;",
        "conjure itself returned), the leasing managed meld (test 4, `managed_spell_meld` -> `Conduit.meld`) and the",
        "spellspace meld (test 5, `SpellSpace.meld` -> `SpellSpaceMeld.meld`, line 629 - the spellspace door measured",
        "for the first time). Every one goes through `Spellbook._emit_cache_file_if_required` (spellbook.py:1175) to",
        "`CachingSystem.emit`, failing at the temp write (caching_system.py:916) or the rename (917).",
        "Unit: after the refused save the frame folder holds root.meldercache.tmp beside the bundle; the refusal",
        "fired and the bundle saved before still loads with its first payload only (the control passes).",
        "Each test removes its frame's cache folder at teardown: the copy's conjure cache was empty after both runs."],
        [f"context_compass/{RUNS}/regression_tests_0_2_8265_gil0.txt:1-182",
         f"context_compass/{RUNS}/regression_tests_0_2_8265_gil1.txt:1-190",
         whole(COMPONENT), whole(UNIT)],
        ["The bug is caught at every kind of meld door and in the save itself; a fix must turn all nine green, the",
         "GIL off and on."],
        ["Check that the tests can pass: a throwaway prototype of directions 1 and 2 in the /tmp copy only (no",
         "repository src change), then the fix PLAN mapped to the tests."], "REQUIRED", 9)
    text = r.read(TICKET)
    text = r.once(text, "\n\n## Context / Handoff Summary\n", "\n\n" + measure + "\n\n## Context / Handoff Summary\n",
                  "measure")
    text = r.once(text, "  runs; 2026-10-24; the Notes below.\n",
                  "  runs; 2026-10-24; the Notes below. Tests: the two regression test files (Note 16's PLAN, Note 17's\n"
                  "  runs); 2026-10-24.\n", "attribution")
    r.check_width(text, "ticket")
    r.stage(TICKET, text)
    r.set_field(TICKET, "Updated")
    r.checked_flush()


if __name__ == "__main__":
    main()
