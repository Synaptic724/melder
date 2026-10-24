"""Record the owner's go for the cache-save fix (melder_0, 2026-10-24).

First authorized pass after the re-onboarding: refresh melder_0's roster row, consume M2-28 (delete it, clear its
alert, carry its facts into the ticket), record the owner's go on D1-D4 as a DECISION, widen the task's boundary to
the fix's files, split the remaining work into steps, and move the board row to in_progress/implementation.
All-or-nothing: anchors match once, lines fit 120 characters, no CR, and a file that changed since it was read
refuses the pass.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record

TICKET = "tickets/tasks/2026-10-24_cache_file_write_failure_fails_meld_task.md"
CI_TICKET = "tickets/tasks/2026-10-24_ci_python_315_and_release_test_rerun_task.md"
OWNER_GO = '"yeah go ahead with all hte recommended things you need to do"'
EXIT_SIGNAL = "0.2.8266 landed with tests green, docs and release note done, assets rebuilt and the ticket closed."


class Pass(Record):
    """The go pass."""

    def checked_flush(self) -> None:
        for rel, before in self.original.items():
            if (self.ROOT / rel).read_text(encoding="utf-8") != before:
                sys.exit(f"RACE {rel}: changed since it was read; nothing written")
        self.flush()


def mailbox(r: Pass) -> None:
    text = r.read(r.MAILBOX)
    rows = re.findall(r"^\| melder_0 \| claude \| 2026-09-26T22:24:06Z \| \S+ \| active \|$", text, flags=re.M)
    if len(rows) != 1:
        sys.exit(f"ROSTER: {len(rows)}")
    text = r.once(text, rows[0], f"| melder_0 | claude | 2026-09-26T22:24:06Z | {r.now} | active |", "roster")
    messages = re.findall(r"^- TO: melder_0\n(?:  .*\n)+", text, flags=re.M)
    if len(messages) != 1 or "M2-28." not in messages[0]:
        sys.exit(f"MESSAGES for melder_0: {len(messages)}")
    text = r.once(text, messages[0], "", "consume M2-28")
    r.stage(r.MAILBOX, text)


def boards(r: Pass) -> None:
    board = r.read(r.BOARD)
    board = r.once(board, "- NEW MESSAGE for melder_0 (from melder_2, 2026-10-24T19:41:15Z)\n", "", "alert")
    rows = re.findall(r"^\| cache_write_failure \| review \| handoff \|.*$", board, flags=re.M)
    if len(rows) != 1:
        sys.exit(f"ROW: {len(rows)}")
    cells = rows[0].split(" | ")
    if len(cells) != 12:
        sys.exit(f"ROW CELLS: {len(cells)}")
    cells[1] = "in_progress"
    cells[2] = "implementation"
    cells[6] = ("Write the patch docs (F4) and their mapping note, then F1-F3 with tests; F6, F5, closure, "
                "rebuild last.")
    cells[7] = ("A refused cache save never fails a meld: F1-F3 as 0.2.8266 with tests, patch and system docs, "
                "release note.")
    cells[8] = EXIT_SIGNAL
    cells[10] = r.now
    board = r.once(board, rows[0], " | ".join(cells), "board row")
    old_trigger = ("  SWITCH_TRIGGER: Tests red on 0.2.8265 with runs recorded and the fix PLAN noted; the owner gives "
                   "a go or redirects.\n")
    board = r.once(board, old_trigger, f"  SWITCH_TRIGGER: {EXIT_SIGNAL}\n", "board detail")
    r.stage(r.BOARD, board)


def contract(r: Pass, text: str) -> str:
    blocks = re.findall(r"^- EXECUTION_BOUNDARY: .*\n(?:  .*\n)*", text, flags=re.M)
    if len(blocks) != 1:
        sys.exit(f"BOUNDARY: {len(blocks)}")
    text = r.once(text, blocks[0], "\n".join([
        "- EXECUTION_BOUNDARY: this ticket, its board row, artifacts/cache_write_failure_20261024/ with its artifact row,",
        "  the two regression test files, and, on the owner's go (chat 2026-10-24:",
        f"  {OWNER_GO}), the fix:",
        "  src/melder/utilities/caching_system/caching_system.py, src/melder/aether/spellbook/spellbook.py",
        "  (`_emit_cache_file_if_required`, `_emit_cache_file`) and src/melder/aether/spellbook/spell.py",
        "  (`emit_cache_file`); the stub test in tests/unit/melder/spellbook/test_cache_runtime_verification.py and new",
        "  unit tests; the patch docs under system_docs/patches/active/cache_save_best_effort_2026_10_24/ with their",
        "  artifact row; src_architecture.md, src_components.md and their indexes; the graph descriptors of the",
        "  changed files and the reassembled graph; release_docs/next_version_release.md; src/melder/__version__.py",
        "  (0.2.8266); the generated assets and llm_support bundles, rebuilt last. Not touched: tests_architecture.md,",
        "  tests_components.md, pyproject.toml, uv.lock, README.md and .github/ (melder_2's pending set, M2-28).",
        "  MelderOps (priv_commandops) is read, never written."]) + "\n", "boundary")
    deps = re.findall(r"^- DEPENDENCIES: .*\n(?:  .*\n)*", text, flags=re.M)
    if len(deps) != 1:
        sys.exit(f"DEPENDENCIES: {len(deps)}")
    text = r.once(text, deps[0], "\n".join([
        "- DEPENDENCIES: no lane holds the fix's files - melder_1 holds no src file (M1-48) and melder_2's pending set",
        "  touches none of them (M2-28); the board is re-read before the src change. The owner stages this lane's",
        "  named paths with melder_2's set, never git add -A, and rebuilds after staging."]) + "\n", "dependencies")
    gates = re.findall(r"^- EXIT_GATE: .*\n(?:  .*\n)*", text, flags=re.M)
    if len(gates) != 1:
        sys.exit(f"EXIT_GATE: {len(gates)}")
    text = r.once(text, gates[0], "\n".join([
        "- EXIT_GATE: the record and test rounds' gates are met (Notes 1-20). This round: F1-F3 land as 0.2.8266 - the",
        "  nine regression tests and the new unit tests green, the related and full trees run on a /tmp copy, the GIL",
        "  off and on, probe A-D rerun; the patch docs consumed and promoted; src_architecture, src_components, the",
        "  release note and the notch; NOTICEs sent; the ticket closed with board sync; assets and bundles rebuilt",
        "  last with both checks OK."]) + "\n", "exit gate")
    events = re.findall(r"^- from_state: .*\n- to_state: .*\n- transition_reason: .*\n(?:  .*\n)*", text, flags=re.M)
    if len(events) != 1:
        sys.exit(f"STATE EVENT: {len(events)}")
    text = r.once(text, events[0], "\n".join([
        "- from_state: in_progress (review: the fix PLAN waiting for the owner's D1-D4)",
        "- to_state: in_progress (implementation)",
        "- transition_reason: the owner's go (chat 2026-10-24),",
        f"  {OWNER_GO};",
        "  melder_0 executes the fix."]) + "\n", "state event")
    return text


def body(r: Pass, text: str) -> str:
    text = r.once(text, "- [ ] On the owner's go (Note 20): patch docs, the fix F1-F3 with its unit tests, the turn-in "
                  "(F5) and the\n      validation (F6).\n", "\n".join([
                      "- [x] Record the owner's go on D1-D4 (Note 21) and consume M2-28 (Note 22).",
                      "- [ ] F4: write the patch docs (cache_save_best_effort_2026_10_24), link them and record the",
                      "      section -> step -> test mapping before any src edit.",
                      "- [ ] F1-F3: the src change with its docstrings, the stub test and the new unit tests.",
                      "- [ ] F6: the regression, new, related and full test trees on a /tmp copy, the GIL off and on;",
                      "      probe A-D rerun; the MEASURE.",
                      "- [ ] F5: src_architecture and src_components (indexes, citations), the graph, the release note,",
                      "      the notch to 0.2.8266 and the NOTICEs.",
                      "- [ ] Closure: summary, move to completed/, board and artifact sync, the patch folder to",
                      "      completed/, follow-ups filed.",
                      "- [ ] Rebuild last: the asset runner and the llm_support builder, both --check OK."]) + "\n",
                  "steps")
    text = r.once(text, "- tests/unit/melder/utilities/test_caching_system_refused_save.py (new)\n", "\n".join([
        "- tests/unit/melder/utilities/test_caching_system_refused_save.py (new)",
        "- src/melder/utilities/caching_system/caching_system.py",
        "- src/melder/aether/spellbook/spellbook.py",
        "- src/melder/aether/spellbook/spell.py",
        "- tests/unit/melder/spellbook/test_cache_runtime_verification.py",
        "- context_compass/system_docs/patches/active/cache_save_best_effort_2026_10_24/ (new; completed/ at turn-in)",
        "- context_compass/system_docs/src_architecture.md, src_components.md and their indexes",
        "- context_compass/system_docs/graph/ (the changed files' descriptors), src_graph.md and its index",
        "- release_docs/next_version_release.md, src/melder/__version__.py",
        "- src/melder/_build_assets/ (generated payloads and manifests) and llm_support/ (generated bundles)"]) + "\n",
        "paths")
    text = r.once(text, "- artifacts/cache_write_failure_20261024/: the probe (cases A-D) and its runs, the MelderOps "
                  "cache listing, the scripts.\n",
                  "- artifacts/cache_write_failure_20261024/: the probe (cases A-D) and its runs, the MelderOps "
                  "cache listing, the scripts.\n"
                  "- The fix F1-F3 as 0.2.8266 with its tests, patch docs, system docs and release note (Note 21).\n",
                  "deliverables")
    return text


def notes(r: Pass, text: str) -> str:
    staged = text.split("\n")
    starts = [i for i, line in enumerate(staged) if line.startswith("- EXECUTION_BOUNDARY: ")]
    ends = [i for i, line in enumerate(staged) if line.startswith("- DEPENDENCIES: ")]
    if len(starts) != 1 or len(ends) != 1:
        sys.exit("CONTRACT LINES")
    boundary = f"context_compass/{TICKET}:{starts[0] + 1}-{ends[0]}"
    decision = r.note(r.now, "DECISION", [
        "The owner's go (chat 2026-10-24), answering Note 20:",
        f"{OWNER_GO}.",
        "Every recommended call is taken: D1 F1-F3 (directions 1 and 2) as one src change, notch 0.2.8265 ->",
        "0.2.8266; D2 `Spell.emit_cache_file()` returns False and logs on a refused save, as its docstring promises;",
        "D3 the rename retried on Windows only; D4 a bundle's first refused save logged at WARNING, later ones at",
        "DEBUG. With them come the PLAN's gates and turn-in (F4-F6). The boundary widens to the fix's files; the",
        "tests_* system docs, pyproject.toml, uv.lock, README.md and .github/ stay out (melder_2's set, next note)."],
        [boundary,
         r.note_range(TICKET, "- DATETIME: 2026-10-24T19:13:54Z", "  TYPE: PLAN"),
         r.note_range(TICKET, "- DATETIME: 2026-10-24T19:13:54Z", "  TYPE: DECISION_REQUEST")],
        ["The fix starts with its public change (D2) decided by the owner; nothing outside the boundary moves."],
        ["Write the patch docs (F4) with the section -> step -> test mapping, then the src change."], "REQUIRED", 9)
    custody = r.note(r.now, "FACT", [
        "M2-28 (melder_2's NOTICE, 2026-10-24T19:41:15Z, consumed here): a 23-file CI change waits for the owner in",
        "build/ci_python_315_change.zip - 18 files under .github/, test_workflow_contracts.py, tests_architecture.md,",
        "tests_components.md and their indexes - to be committed with his modified pyproject.toml, uv.lock and",
        "README.md. llm_support/_builder.py reads tracked files from the working tree and untracked ones only with",
        "--include-untracked, so a rebuild between his extraction and his staging matches no commit: stage first,",
        "then rebuild. His steps name paths, never git add -A, because this ticket's tests are untracked."],
        [r.doc_section(CI_TICKET, "## Context / Handoff Summary"),
         r.doc_section(CI_TICKET, "## Files / Paths Impacted")],
        ["This lane leaves that set alone: the tests_* doc entries for the new tests become a follow-up after it",
         "lands, this lane's own rebuild runs with --include-untracked, and the owner stages this lane's named paths",
         "with his set before his final rebuild."],
        ["Re-read the board for custody right before the src change."], "REQUIRED", 8)
    return r.once(text, "\n\n## Context / Handoff Summary\n",
                  "\n\n" + decision + "\n\n" + custody + "\n\n## Context / Handoff Summary\n", "notes")


def summary(r: Pass, text: str) -> str:
    sections = re.findall(r"## Context / Handoff Summary\n(?:.+\n)+", text)
    if len(sections) != 1:
        sys.exit(f"SUMMARY: {len(sections)}")
    new = "\n".join([
        "## Context / Handoff Summary",
        "Scope: the defect is documented (Notes 1-13); the regression tests (Notes 14-17) fail on 0.2.8265, 9 of 9, the",
        "GIL off and on, and a /tmp prototype turns them green (Note 18). The owner approved the fix PLAN (Note 19)",
        "with every recommended call (Note 21: D1 F1-F3 as 0.2.8266; D2 `Spell.emit_cache_file()` returns False on a",
        "refused save; D3 the rename retried on Windows only; D4 a bundle's first refused save at WARNING, later ones",
        "at DEBUG). State: in_progress, melder_0, board row in implementation. Holds: patch docs (F4) before any src",
        "edit; the tests_* system docs, pyproject.toml, uv.lock, README.md and .github/ are melder_2's pending set",
        "(Note 22) and stay untouched; the owner stages named paths, never git add -A, then rebuilds. Open: the",
        "Windows cause (Note 5, HYPOTHESIS). Next: F4's patch docs and mapping note; F1-F3 with tests; F6; F5;",
        "closure; rebuild last."]) + "\n"
    return r.once(text, sections[0], new, "summary")


def main() -> None:
    r = Pass("reonboard_fix_go")
    mailbox(r)
    boards(r)
    text = r.read(TICKET)
    text = contract(r, text)
    text = body(r, text)
    text = notes(r, text)
    text = summary(r, text)
    r.check_width(text, "ticket")
    r.stage(TICKET, text)
    r.set_field(TICKET, "Updated")
    r.checked_flush()


if __name__ == "__main__":
    main()
