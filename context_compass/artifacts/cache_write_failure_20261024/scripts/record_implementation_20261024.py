"""Record the implementation of M1 and M2 (melder_0, 2026-10-24).

TASK-2026-10-24-cache_file_write_failure_fails_meld: appends the implementation FACT (the src change and the tests,
with method ranges measured from the files), ticks the F1-F3 step and moves the board row's next action to F6.
All-or-nothing: anchors match once, lines fit 120 characters, no CR, and a file that changed since it was read
refuses the pass.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record

TICKET = "tickets/tasks/2026-10-24_cache_file_write_failure_fails_meld_task.md"
CACHE = "src/melder/utilities/caching_system/caching_system.py"
BOOK = "src/melder/aether/spellbook/spellbook.py"
SPELL = "src/melder/aether/spellbook/spell.py"
UNIT = "tests/unit/melder/utilities/test_caching_system_refused_save.py"
STUBS = "tests/unit/melder/spellbook/test_cache_runtime_verification.py"
SCRIPTS = "artifacts/cache_write_failure_20261024/scripts"


class Pass(Record):
    """The implementation-record pass."""

    def checked_flush(self) -> None:
        for rel, before in self.original.items():
            if (self.ROOT / rel).read_text(encoding="utf-8") != before:
                sys.exit(f"RACE {rel}: changed since it was read; nothing written")
        self.flush()


def method_range(rel: str, start_prefix: str, last_prefix: str = "") -> str:
    """`rel:a-b` from the line starting with `start_prefix` to the end of the def that starts with `last_prefix`."""
    lines = (Record.REPO / rel).read_text(encoding="utf-8").split("\n")
    starts = [i for i, line in enumerate(lines) if line.startswith(start_prefix)]
    if len(starts) != 1:
        sys.exit(f"DEF {rel} {start_prefix}: {len(starts)}")
    last = starts[0]
    if last_prefix:
        lasts = [i for i, line in enumerate(lines) if line.startswith(last_prefix)]
        if len(lasts) != 1:
            sys.exit(f"DEF {rel} {last_prefix}: {len(lasts)}")
        last = lasts[0]
    indent = len(lines[last]) - len(lines[last].lstrip())
    end = last + 1
    while end < len(lines) and (lines[end].strip() == "" or len(lines[end]) - len(lines[end].lstrip()) > indent):
        end += 1
    while lines[end - 1].strip() == "":
        end -= 1
    return f"{rel}:{starts[0] + 1}-{end}"


def note(r: Pass) -> str:
    evidence = [
        method_range(CACHE, "    RETRY_REFUSED_RENAME: ClassVar", "    REPLACE_RETRY_DELAY_SECONDS: ClassVar"),
        method_range(CACHE, "    def emit(self) -> bool:"),
        method_range(CACHE, "    def _write_current_cache_to_disk_locked", "    def _log_refused_save_locked"),
        method_range(BOOK, "    def _emit_cache_file_if_required", "    def _emit_cache_file(self"),
        method_range(SPELL, "    def emit_cache_file(self) -> bool:"),
        f"{UNIT}:1-{len((Record.REPO / UNIT).read_text(encoding='utf-8').splitlines())}",
        method_range(STUBS, "class _StubCachingSystem:"),
        f"context_compass/{SCRIPTS}/apply_fix_caching_system_20261024.py:1-"
        f"{len((Record.ROOT / SCRIPTS / 'apply_fix_caching_system_20261024.py').read_text().splitlines())}",
        f"context_compass/{SCRIPTS}/apply_fix_spellbook_spell_20261024.py:1-"
        f"{len((Record.ROOT / SCRIPTS / 'apply_fix_spellbook_spell_20261024.py').read_text().splitlines())}"]
    return r.note(r.now, "FACT", [
        "M1 and M2 are implemented (anchored edits by the two apply scripts; nothing else in src/ changed).",
        "CachingSystem: `emit() -> bool`; the write makes the folder, writes the per-writer temp file",
        "(`<conduit>.meldercache.<pid>.<thread id>.tmp`) and renames it in one try; an OSError removes the temp file",
        "it started and returns False after `_log_refused_save_locked` (WARNING once per instance, DEBUG after, with",
        "the bundle, the error and the remedies); `_replace_bundle_locked` always tries once and retries a",
        "PermissionError only while `RETRY_REFUSED_RENAME` (Windows), up to `REPLACE_ATTEMPTS` 5 with",
        "`REPLACE_RETRY_DELAY_SECONDS` 0.01 x attempt; a temp file it cannot remove is logged, not raised; slot",
        "`_refused_save_logged` (deleted in cleanup); class and method docstrings carry the contract.",
        "Spellbook: `_emit_cache_file_if_required` returns emit's bool (a refusal leaves the flag cleared; any other",
        "error restores it and raises); its and `_emit_cache_file`'s docstrings name each False. Spell:",
        "`emit_cache_file`'s docstring says a refused save returns False. Tests: the stub's emit returns a bool and",
        "can refuse; six Spellbook/Spell unit tests and ten CachingSystem unit tests are new. A first targeted run on",
        "a /tmp copy (four files, 112 tests) passes, the GIL off and on; F6 records the full runs."],
        evidence,
        ["Every meld door now gets False from a refused save instead of its OSError, without a change at the doors;",
         "the explicit save reports False (D2)."],
        ["F6: the full validation on a fresh /tmp copy, the GIL off and on, and probe A-D."], "REQUIRED", 9)


def ticket(r: Pass) -> None:
    text = r.read(TICKET)
    text = r.once(text, "\n\n## Context / Handoff Summary\n", "\n\n" + note(r) + "\n\n## Context / Handoff Summary\n",
                  "notes")
    text = r.once(text, "- [ ] F1-F3: the src change with its docstrings, the stub test and the new unit tests.\n",
                  "- [x] F1-F3: the src change with its docstrings, the stub test and the new unit tests.\n", "step")
    text = r.once(text, "Next: M1 in\ncaching_system.py, M2 in spellbook.py and spell.py, the unit tests; then F6, F5, "
                        "closure, rebuild last.\n",
                  "M1-M2 are in\n(Note 24). Next: F6's full validation; then F5, closure, rebuild last.\n", "summary")
    r.check_width(text, "ticket")
    r.stage(TICKET, text)
    r.set_field(TICKET, "Updated")


def boards(r: Pass) -> None:
    board = r.read(r.BOARD)
    rows = re.findall(r"^\| cache_write_failure \| in_progress \| implementation \|.*$", board, flags=re.M)
    if len(rows) != 1:
        sys.exit(f"ROW: {len(rows)}")
    cells = rows[0].split(" | ")
    cells[2] = "validation"
    cells[6] = "F6: regression, new, related and full test trees on a /tmp copy, GIL off and on; probe A-D; MEASURE."
    cells[10] = r.now
    r.stage(r.BOARD, r.once(board, rows[0], " | ".join(cells), "board row"))


def main() -> None:
    r = Pass("record_implementation")
    ticket(r)
    boards(r)
    r.checked_flush()


if __name__ == "__main__":
    main()
