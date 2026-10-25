"""Record the patch docs and their mapping before the src change (melder_0, 2026-10-24).

TASK-2026-10-24-cache_file_write_failure_fails_meld, F4: appends the PLAN note that maps each patch section to an
implementation step and its tests (patch_artifact_consumption), links the patch folder in the ticket and on the
artifact board, ticks F4, brings the scope boundaries up to the owner's go, and moves the board row's next action to
the src change. All-or-nothing: anchors match once, lines fit 120 characters, no CR, and a file that changed since
it was read refuses the pass.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record

TICKET = "tickets/tasks/2026-10-24_cache_file_write_failure_fails_meld_task.md"
PATCH = "system_docs/patches/active/cache_save_best_effort_2026_10_24"


class Pass(Record):
    """The mapping pass."""

    def checked_flush(self) -> None:
        for rel, before in self.original.items():
            if (self.ROOT / rel).read_text(encoding="utf-8") != before:
                sys.exit(f"RACE {rel}: changed since it was read; nothing written")
        self.flush()


def mapping(r: Pass) -> str:
    arch = f"{PATCH}/architecture_patch.md"
    cache = f"{PATCH}/component_patch_caching_system.md"
    book = f"{PATCH}/component_patch_spellbook_cache_save.md"
    code = f"{PATCH}/code_description_patch_caching_system.md"
    lines = r.read(r.BOARD).split("\n")
    rows = [i for i, line in enumerate(lines) if line.startswith("| correctness_defects |")
            or line.startswith("| ci_python_315 |")]
    if len(rows) != 2:
        sys.exit(f"OTHER ROWS: {len(rows)}")
    return r.note(r.now, "PLAN", [
        "F4 done: the patch docs (cache_save_best_effort_2026_10_24) are written, indexed and read in the consumption",
        "order - architecture, component CachingSystem, component Spellbook cache save, code description",
        "CachingSystem - with no conflict among them or with src_architecture/src_components. Mapping, patch section",
        "-> implementation step -> validation:",
        "M1 architecture Interface deltas + CachingSystem After + code description steps 1-7 -> caching_system.py:",
        "`emit() -> bool`, the write in one try, `_temp_bundle_path`, `_replace_bundle_locked`,",
        "`_discard_temp_bundle_locked`, `_log_refused_save_locked`, slot `_refused_save_logged`, three ClassVars, the",
        "class docstring -> T6 and the new CachingSystem unit tests (save True; refusal False then the next save",
        "writes all; retry on: two refusals then saved; retry off: one refusal; retry budget exhausted; one WARNING;",
        "per-writer temp name; refused temp write; refused folder; unremovable temp file logged).",
        "M2 Spellbook cache save After -> spellbook.py `_emit_cache_file_if_required` returns emit's bool (flag left",
        "cleared on False; other errors restore and raise), docstrings of it and `_emit_cache_file`; spell.py",
        "`emit_cache_file` docstring -> T1-T5, the stub test (emit returns True) and new Spellbook unit tests",
        "(refusal False with the flag cleared; conjure end leaves the flag cleared; `_emit_cache_file` and",
        "`Spell.emit_cache_file` return False).",
        "M3 architecture invariants, Locks, Migration step 4 -> F6 on a /tmp copy, the GIL off and on: regression and",
        "new unit tests, the 15 related files, the full unit, component and integration trees; probe A-D rerun.",
        "M4 architecture Migration step 5 -> F5: an operational invariant, a fixed failure mode (Breaking for",
        "`Spell.emit_cache_file`) and the code map in src_architecture; the CachingSystem and Spellbook cache entries",
        "in src_components; the graph; the release note; the notch to 0.2.8266.",
        "Custody, re-read now: the board's other lanes (melder_1's correctness epic in handoff, melder_2's CI task",
        "blocked on the owner) hold none of the three src files."],
        [r.whole(arch), r.whole(cache), r.whole(book), r.whole(code),
         f"context_compass/{r.BOARD}:{rows[0] + 1}-{rows[1] + 1}"],
        ["The patch gate is met (docs linked, read in order, mapping recorded), so the src change can start; each",
         "step names the tests that prove it."],
        ["Implement M1 in caching_system.py, then M2, then the unit tests."], "REQUIRED", 9)


def ticket(r: Pass) -> None:
    text = r.read(TICKET)
    text = r.once(text, "\n\n## Context / Handoff Summary\n", "\n\n" + mapping(r) + "\n\n## Context / Handoff Summary\n",
                  "notes")
    text = r.once(text, "- [ ] F4: write the patch docs (cache_save_best_effort_2026_10_24), link them and record the\n",
                  "- [x] F4: write the patch docs (cache_save_best_effort_2026_10_24), link them and record the\n",
                  "step F4")
    old_scope = "\n".join([
        "- In scope: the creation-cache bundle write (`CachingSystem`), its callers on the meld and conjure paths, the",
        "  cache location and defaults, the Windows replace refusal and the orphaned temp file.",
        "- Out of scope: the bind-guard and agent-documentation build-asset caches; the Crystallizer's cache; MelderOps",
        "  changes (its per-trial unique frame is its own choice); the fix itself (the owner's word)."])
    new_scope = "\n".join([
        "- In scope: the creation-cache bundle write (`CachingSystem`), its callers on the meld and conjure paths, the",
        "  cache location and defaults, the Windows replace refusal and the orphaned temp file; since the owner's go",
        "  (Note 21) the fix F1-F3 - a best-effort, Windows-robust save - to land as 0.2.8266 with its tests and docs.",
        "- Out of scope: the bind-guard and agent-documentation build-asset caches; the Crystallizer's cache; MelderOps",
        "  changes (its per-trial unique frame is its own choice); directions 3 and 4 (fewer meld-time saves; the cache",
        "  location and frame-folder pruning) and the Windows cause (Note 5), which are follow-ups."])
    text = r.once(text, old_scope, new_scope, "scope")
    text = r.once(text, "  - artifacts/cache_write_failure_20261024/scripts/\n", "\n".join([
        "  - artifacts/cache_write_failure_20261024/scripts/",
        f"  - {PATCH}/ (four patch docs and their indexes)"]) + "\n",
        "artifact paths")
    text = r.once(text, "- DISPOSITION: retain_as_reference\n",
                  "- DISPOSITION: retain_as_reference (the artifact folder); promote_to_documentation (the patch docs)\n",
                  "disposition")
    text = r.once(text, "- CLEANUP_TRIGGER: kept as the defect's reproducer; rerun at the fix, then disposed with the "
                  "fix's turn-in.\n",
                  "- CLEANUP_TRIGGER: kept as the defect's reproducer; rerun at the fix, then disposed with the "
                  "fix's turn-in.\n"
                  "  The patch docs are promoted into src_architecture and src_components at turn-in and their folder\n"
                  "  moves to system_docs/patches/completed/.\n", "cleanup trigger")
    sections = re.findall(r"## Context / Handoff Summary\n(?:.+\n)+", text)
    if len(sections) != 1:
        sys.exit(f"SUMMARY: {len(sections)}")
    text = r.once(text, sections[0], "\n".join([
        "## Context / Handoff Summary",
        "Scope: the defect is documented (Notes 1-13); the regression tests (Notes 14-17) fail on 0.2.8265, 9 of 9, the",
        "GIL off and on, and a /tmp prototype turns them green (Note 18). The owner approved the fix PLAN (Note 19)",
        "with every recommended call (Note 21: D1 F1-F3 as 0.2.8266; D2 `Spell.emit_cache_file()` returns False on a",
        "refused save; D3 the rename retried on Windows only; D4 a bundle's first refused save at WARNING, later ones",
        "at DEBUG). F4 is done: the patch docs cache_save_best_effort_2026_10_24 are linked and mapped (Note 23).",
        "State: in_progress, melder_0, board row in implementation. Holds: the tests_* system docs, pyproject.toml,",
        "uv.lock, README.md and .github/ are melder_2's pending set (Note 22) and stay untouched; the owner stages",
        "named paths, never git add -A, then rebuilds. Open: the Windows cause (Note 5, HYPOTHESIS). Next: M1 in",
        "caching_system.py, M2 in spellbook.py and spell.py, the unit tests; then F6, F5, closure, rebuild last."]) + "\n",
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
    cells[6] = "M1 in caching_system.py, M2 in spellbook.py and spell.py, the unit tests; then F6, F5, closure, rebuild."
    cells[10] = r.now
    board = r.once(board, rows[0], " | ".join(cells), "board row")
    r.stage(r.BOARD, board)
    arts = r.read(r.ARTIFACTS)
    if f"| {TICKET} | {PATCH}/ |" in arts:
        sys.exit("PATCH ROW already present")
    row = (f"| {TICKET} | {PATCH}/ | patch_doc | active | promote_to_documentation | The fix's architecture, component "
           "and code-description patches (with indexes), consumed before the src change (Note 23); promoted into "
           "src_architecture and src_components at turn-in, then the folder moves to system_docs/patches/completed/. | "
           f"{r.now} | REQUIRED |")
    arts = r.once(arts, "\n<!-- END USER-DEFINED: active_artifacts -->",
                  "\n" + row + "\n<!-- END USER-DEFINED: active_artifacts -->", "artifact row")
    r.stage(r.ARTIFACTS, arts)


def main() -> None:
    r = Pass("record_patch_mapping")
    ticket(r)
    boards(r)
    r.checked_flush()


if __name__ == "__main__":
    main()
