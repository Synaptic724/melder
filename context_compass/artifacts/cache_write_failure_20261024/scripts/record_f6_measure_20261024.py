"""Record F6, the validation of the cache-save fix (melder_0, 2026-10-24).

TASK-2026-10-24-cache_file_write_failure_fails_meld: appends the MEASURE (full unit, component and integration trees
on a /tmp copy with the fix, the GIL off and on; the failures attributed with a baseline run; probe A-D), updates
Validation, ticks F6 and moves the board row to F5. All-or-nothing: anchors match once, lines fit 120 characters, no
CR, and a file that changed since it was read refuses the pass.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record

TICKET = "tickets/tasks/2026-10-24_cache_file_write_failure_fails_meld_task.md"
RUNS = "artifacts/cache_write_failure_20261024/runs"


class Pass(Record):
    """The F6 pass."""

    def checked_flush(self) -> None:
        for rel, before in self.original.items():
            if (self.ROOT / rel).read_text(encoding="utf-8") != before:
                sys.exit(f"RACE {rel}: changed since it was read; nothing written")
        self.flush()


def measure(r: Pass) -> str:
    names = ["f6_unit_gil0.txt", "f6_unit_gil1.txt", "f6_component_gil0.txt", "f6_component_gil1.txt",
             "f6_integration_gil0.txt", "f6_integration_gil1.txt", "f6_melder_1_red_files_on_0_2_8265_gil0.txt",
             "f6_melder_1_red_files_on_0_2_8265_gil1.txt", "f6_probe_cache_emit_failure_gil0.txt",
             "f6_probe_cache_emit_failure_gil1.txt"]
    evidence = [r.whole(f"{RUNS}/{name}") for name in names]
    return r.note(r.now, "MEASURE", [
        "F6 on a fresh /tmp copy of the working tree with the fix (/tmp/m0_mq/fix8266; Python 3.14.7 free-threaded),",
        "the GIL off and on, with the same outcome both ways. The nine regression tests and the sixteen new unit",
        "tests pass. tests/unit: 9726 passed, 3 skipped, 7 xfailed, 1 failed - test_python_runtime_matrix's",
        "manifest test: the owner's working-tree pyproject.toml declares pip, which the checkout's .github manifests",
        "do not pin until melder_2's pending set lands; it reads no src. tests/component: 2425 passed, 23 skipped, 1",
        "xfailed, 19 failed - all in melder_1's untracked red-by-design file",
        "test_conduit_component_many_child_belongs_to_the_scope_that_built_it.py. tests/integration: 2279 passed, 2",
        "skipped, 9 xfailed, 3 xpassed, 10 failed - all in melder_1's two untracked files (8 in",
        "..._holder_cleanup_leaves_its_many_children.py, 2 in ..._many_child_belongs_to_the_scope_that_built_it.py).",
        "Those 29 fail as the same set, the GIL off and on, on a copy with this lane's three src files and its stub",
        "test at HEAD (0.2.8265): they belong to melder_1's lane (Note 25), not to this change. Probe A-D: every meld",
        "returns - A the meld whose replace is refused (no temp file left), B every meld with the frame folder",
        "read-only, C conjure and the first melds with the cache root read-only, D the leasing meld returns its lease",
        "(the probe keeps that lease, so its second meld is exhausted as limit 1 requires; T4 releases and leases",
        "again). Wall time per tree: unit 59-62 s, component 30-40 s, integration 101-115 s."],
        evidence,
        ["The fix turns the bug's nine tests green with no failure of its own anywhere in the three trees; F5 can",
         "document it."],
        ["F5: src_architecture and src_components with their indexes and citations, the graph, the release note,",
         "the notch and the NOTICEs."], "REQUIRED", 9)


def ticket(r: Pass) -> None:
    text = r.read(TICKET)
    text = r.once(text, "\n\n## Context / Handoff Summary\n", "\n\n" + measure(r) + "\n\n## Context / Handoff Summary\n",
                  "notes")
    text = r.once(text, "- [ ] F6: the regression, new, related and full test trees on a /tmp copy, the GIL off and on;\n",
                  "- [x] F6: the regression, new, related and full test trees on a /tmp copy, the GIL off and on;\n",
                  "step")
    text = r.once(text, "- Run: the regression tests fail on 0.2.8265, 9 of 9, the GIL off and on (Note 17), and pass on a "
                        "/tmp\n  prototype of the fix (Note 18). Not run: the full suites, which run at the fix (F6).\n",
                  "- Run: the regression tests fail on 0.2.8265, 9 of 9, the GIL off and on (Note 17), and pass on a /tmp\n"
                  "  prototype of the fix (Note 18). At the fix (F6, Note 26): the regression and sixteen new unit tests\n"
                  "  and the full unit, component and integration trees on a /tmp copy, the GIL off and on, and probe A-D.\n"
                  "  Failures: the CI manifest test that waits for melder_2's pip pin, and 29 in melder_1's untracked\n"
                  "  red-by-design files, the same set without this change.\n", "validation")
    text = r.once(text, "M1-M2 are in\n(Note 24). Next: F6's full validation; then F5, closure, rebuild last.\n",
                  "M1-M2 are in\n(Note 24) and F6 passed (Note 26). Next: F5; then closure, rebuild last.\n", "summary")
    r.check_width(text, "ticket")
    r.stage(TICKET, text)
    r.set_field(TICKET, "Updated")


def boards(r: Pass) -> None:
    board = r.read(r.BOARD)
    rows = re.findall(r"^\| cache_write_failure \| in_progress \| validation \|.*$", board, flags=re.M)
    if len(rows) != 1:
        sys.exit(f"ROW: {len(rows)}")
    cells = rows[0].split(" | ")
    cells[2] = "implementation"
    cells[6] = "F5: src_architecture, src_components, graph, release note, notch to 0.2.8266, NOTICEs; then closure."
    cells[10] = r.now
    r.stage(r.BOARD, r.once(board, rows[0], " | ".join(cells), "board row"))


def main() -> None:
    r = Pass("record_f6")
    ticket(r)
    boards(r)
    r.checked_flush()


if __name__ == "__main__":
    main()
