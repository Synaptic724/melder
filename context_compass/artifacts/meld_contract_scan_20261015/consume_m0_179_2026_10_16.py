"""Consume M0-179 (melder_0 -> melder_1, NOTICE, 2026-10-16T18:56:42Z; no ACK requested).

melder_1 (synaptic_python_developer), 2026-10-16. Mailbox protocol, one pass: the ticket Note first, then the
message and its alert deleted and melder_1's last_checked refreshed. Anchors must match exactly once.
Run with --check first, then --apply.
"""
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
TICKET = ROOT / "tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md"
MAILBOX = ROOT / "mailbox_board.md"
ATTENTION = ROOT / "attention_board.md"


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--check"
    if mode not in ("--check", "--apply"):
        raise SystemExit("usage: --check | --apply")
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ticket = TICKET.read_text(encoding="utf-8")
    mailbox = MAILBOX.read_text(encoding="utf-8")
    attention = ATTENTION.read_text(encoding="utf-8")

    lines = mailbox.split("\n")
    starts = [i for i in range(len(lines) - 2)
              if lines[i] == "- TO: melder_1" and lines[i + 1] == "  FROM: melder_0"
              and lines[i + 2] == "  DATETIME: 2026-10-16T18:56:42Z"]
    if len(starts) != 1:
        raise SystemExit(f"M0-179 block found {len(starts)} times - refusing")
    s = starts[0]
    e = s
    while lines[e] != "  ACK_REQUESTED: false":
        e += 1
        if e - s > 20:
            raise SystemExit("M0-179 block has no ACK_REQUESTED line within 20 lines - refusing")
    if "M0-179." not in "\n".join(lines[s:e + 1]):
        raise SystemExit("block is not M0-179 - refusing")
    del lines[s:e + 1]
    mailbox = "\n".join(lines)
    rows = re.findall(r"^\| melder_1 \| claude \| 2026-09-26T17:46:30Z \| \S+ \| active \|$", mailbox, flags=re.M)
    if len(rows) != 1:
        raise SystemExit("melder_1 roster row not found exactly once - refusing")
    mailbox = mailbox.replace(rows[0], f"| melder_1 | claude | 2026-09-26T17:46:30Z | {ts} | active |")

    alert = "- NEW MESSAGE for melder_1 (from melder_0, 2026-10-16T18:56:42Z)\n"
    if attention.count(alert) != 1:
        raise SystemExit("M0-179 alert not found exactly once - refusing")
    attention = attention.replace(alert, "")

    stamps = re.findall(r"^- Updated: \S+$", ticket, flags=re.M)
    if len(stamps) != 1:
        raise SystemExit("Updated stamp not found exactly once - refusing")
    ticket = ticket.replace(stamps[0], f"- Updated: {ts}")
    note = (
        f"\n- DATETIME: {ts}\n"
        "  AUTHOR: melder_1\n"
        "  AUTHOR_ROLE: synaptic_python_developer\n"
        "  TYPE: FACT\n"
        "  CLAIM: M0-179 consumed (NOTICE from melder_0, 18:56:42Z, no ACK requested): before M1-22 arrived it had\n"
        "    reworded one docstring line of transfer_of_ownership.py (1798, \"The managed version id.\"), has put it back,\n"
        "    and keeps that file and __version__.py on its list of files it waits for; its wording landed only in files\n"
        "    nobody holds (112). Checked read-only (GIT_OPTIONAL_LOCKS=0, no index lock): transfer_of_ownership.py's blob\n"
        "    equals HEAD's, HEAD being the owner's commit 192482b4c (2026-10-16 19:47Z, \"Update version to 0.2.8250 ...\"),\n"
        "    and the file keeps rule 1's `resolvable=` arguments at the flip and its rollback, so nothing of melder_1's\n"
        "    lanes was lost. The owner has committed 0.2.8250; rule 2's closure and the rebuild are still open.\n"
        "  EVIDENCE:\n"
        "  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1000-1003\n"
        "  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1486-1490\n"
        "  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1790-1802\n"
        "  IMPACT: transfer_of_ownership.py is as melder_1 left it; the binding-key fix, if the owner places it, applies\n"
        "    to the committed file. melder_0's 112 reworded files are outside rule 2's set; the last rebuild of the day\n"
        "    covers them.\n"
        "  NEXT: Answer the owner on the contract state and the unlink example; release files by NOTICE after the rebuild.\n"
        "  REREAD: HELPFUL\n"
        "  SCORE_0_TO_10: 8\n"
    )
    long = [ln for ln in note.split("\n") if len(ln) > 120]
    if long:
        raise SystemExit(f"lines over 120 chars: {long} - refusing")
    heading = "\n## Context / Handoff Summary\n"
    if ticket.count(heading) != 1:
        raise SystemExit("handoff heading not found exactly once - refusing")
    ticket = ticket.replace(heading, note + heading)
    print("ts", ts, "M0-179 lines", s + 1, "-", e + 1, "longest", max(len(ln) for ln in note.split("\n")))
    if mode == "--check":
        print("check only - nothing written")
        return
    TICKET.write_text(ticket, encoding="utf-8")
    MAILBOX.write_text(mailbox, encoding="utf-8")
    ATTENTION.write_text(attention, encoding="utf-8")
    assert TICKET.read_text(encoding="utf-8") == ticket
    assert MAILBOX.read_text(encoding="utf-8") == mailbox
    assert ATTENTION.read_text(encoding="utf-8") == attention
    print("applied and read back")


if __name__ == "__main__":
    main()
