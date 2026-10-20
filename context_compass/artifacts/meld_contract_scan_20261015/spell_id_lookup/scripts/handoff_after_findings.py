"""Rewrite the lane ticket's handoff summary after the owner accepted fix #1 and the findings were re-examined.

melder_1 (synaptic_python_developer), 2026-10-18. Replaces the summary's first line and its "Open" and "Next"
paragraphs in place (exact-once anchors), refreshes the Updated stamp, keeps LF endings, and refuses prose lines
over 120 characters. Run with --check first, then --apply.
"""
import datetime
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
TICKET = ROOT / "tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md"

OLD_HEAD = ("Current state (2026-10-18T00:16:49Z): this ticket has landed three source changes; fix #1 is landed whole "
            "and rebuilt (Notes 00:26Z).\n")
NEW_HEAD = ("Current state ({ts}): three source changes landed and rebuilt; the owner accepted fix #1 (Notes 00:40Z).\n")
OLD_START = "Open, the owner's: origins 2-6 - the contract-side lookups that still resolve a spell_id through its index\n"
OLD_END = "him the shared documents are free); (2) the owner's direction on the open items above.\n"
NEW_BLOCK = """Open, the owner's, re-examined id by id on 0.2.8253 (Notes 00:55Z-00:56Z): the version-row reads on the
borrower side - `_find_contracted_spell_by_id` / `find_contracted_spell`, `get_spell_in_contracts` and the inbound
listing answer a version's spell_id with its index's active copy; `_validate_contracts_and_define` reports a grant
parked by a notch invalid and `get_all_spells_in_contracts()` raises; removing a parked grant invalidates every
SpellContract consumer of the Book; `Detail`'s docstring and `has_spell`. By design, withdrawn:
`Meld._current_in_pool`; not shown, withdrawn: the selected-id filing. Also open: what borrowers get after an
ownership transfer and its binding-key gap (18:23Z, unchanged at 0.2.8253); the crystallizer cache's retention,
which orders checkpoints of different processes by a per-process number (cause reproduced, 00:56Z); SpellIndex's two
stale graph edges (00:11Z); `Contract`'s inverted map-direction docstring (00:56Z); the stamp test's stale record in
tests_components (00:16Z); the flake `test_concurrent_adds_of_same_conduit_admit_exactly_one` (22:08Z). From
melder_0's correctness epic this lane's set is S1-S4 and S7-S9, waiting for the owner; S6's fix runs in melder_0's
lane, its Part B waits for spellbook.py (Notes 23:54Z).
Next: (1) the owner's direction on the open items above, after the explanation sent 2026-10-18; (2) his word on
closure - summary naming 0.2.8250, 0.2.8251 and 0.2.8253 with their release-note sections, the two active patch
folders archived, board and artifact sync, then a rebuild only if a closure step touches system_docs - and on
releasing spellbook.py, conduit.py and fix #1's other files to melder_0 (M1-26 told him the shared documents are
free).
"""


def main() -> None:
    """Validate the anchors and line widths, then print the plan (--check) or write and read back (--apply)."""
    if len(sys.argv) != 2 or sys.argv[1] not in ("--check", "--apply"):
        raise SystemExit("usage: handoff_after_findings.py --check|--apply")
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    raw = TICKET.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("the ticket has CRLF line endings - refusing")
    text = raw.decode("utf-8")
    for anchor in (OLD_HEAD, OLD_START, OLD_END):
        if text.count(anchor) != 1:
            raise SystemExit("anchor found %d times: %r - refusing" % (text.count(anchor), anchor[:60]))
    start = text.index(OLD_START)
    end = text.index(OLD_END) + len(OLD_END)
    if end <= start:
        raise SystemExit("anchors out of order - refusing")
    head = NEW_HEAD.replace("{ts}", ts)
    for line in (head + NEW_BLOCK).split("\n"):
        if len(line) > 120:
            raise SystemExit("line over 120 chars: %r - refusing" % line)
    text = text[:start] + NEW_BLOCK + text[end:]
    text = text.replace(OLD_HEAD, head)
    marker = "\n- Updated: "
    if text.count(marker) != 1:
        raise SystemExit("Updated stamp found %d times - refusing" % text.count(marker))
    stamp_start = text.index(marker) + len(marker)
    stamp_end = text.index("\n", stamp_start)
    text = text[:stamp_start] + ts + text[stamp_end:]
    print("ts", ts, "replaced", OLD_START[:40], "...", OLD_END[-40:].strip())
    if sys.argv[1] == "--check":
        print("check only - nothing written")
        return
    TICKET.write_bytes(text.encode("utf-8"))
    if TICKET.read_bytes().decode("utf-8") != text:
        raise SystemExit("read-back mismatch")
    print("applied and read back")


if __name__ == "__main__":
    main()
