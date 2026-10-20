"""Mailbox pass 1 (owner switched the mailbox on, 2026-10-16): note first, then consume M1-18/M1-19, send M0-175
(ACK) and M0-176 (HANDOFF), move the alert lines and refresh melder_0's last_checked.

Run from the context_compass root:  python artifacts/public_notch_target_20261016/scripts/mailbox_pass_1.py <NOW>
Every shared file is re-read right before its write; every edit is an exact, asserted replacement.
"""
import pathlib
import re
import sys

NOW = sys.argv[1]
TICKET = pathlib.Path("tickets/tasks/2026-10-16_public_notch_target_for_staged_versions_task.md")
TICKET_REF = "context_compass/tickets/tasks/2026-10-16_public_notch_target_for_staged_versions_task.md"


def rewrite(path: pathlib.Path, edits: list) -> None:
    """Apply (old, new) exact replacements to one file, each old occurring once; LF/CRLF kept."""
    text = path.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in text else "\n"
    for old, new in edits:
        old_n, new_n = old.replace("\n", nl), new.replace("\n", nl)
        if text.count(old_n) != 1:
            raise SystemExit(f"{path}: {text.count(old_n)} occurrences of {old[:70]!r}")
        text = text.replace(old_n, new_n, 1)
    path.write_bytes(text.encode("utf-8"))
    print(f"{path}: {len(edits)} edit(s)")


def ticket_pass() -> str:
    """Correct the shifted evidence range, append the consumption note; return the note's line range."""
    note = (
        f"- DATETIME: {NOW}\n"
        "  AUTHOR: melder_0\n"
        "  AUTHOR_ROLE: synaptic_python_developer\n"
        "  TYPE: FACT\n"
        "  CLAIM: Mailbox messaging is on again (owner, chat 2026-10-16: \"talk to melder_0 in the mailbox please and\n"
        "    switch the mailbox on in this context_compass yaml I'll tell melder_1\" - melder_1 is meant, melder_0 being\n"
        "    this agent; the yaml already read `agent_communication.backend: mailbox` at 12:54:10Z). Consumed the two\n"
        "    messages addressed to melder_0: M1-18 (melder_1's rule-1 handoff questions, ACK requested) was closed by M1-19\n"
        "    (rule 1 landed as 0.2.8247; the spellbook.py and transfer_of_ownership.py keywords and five test files\n"
        "    returned), and S8 landed above it as 0.2.8248, so nothing in either is open. Sent melder_1 M0-175 (ACK of\n"
        "    both) and M0-176 (HANDOFF: spellbook.py and transfer_of_ownership.py released; conduit.py held until this task\n"
        "    lands; the seam backlog task), each with its alert line. The earlier DECISION note's ticket range is\n"
        "    corrected to 167-183 (the Artifact Links edit moved it).\n"
        "  EVIDENCE:\n"
        "  - context_compass/config/context_compass_config.yaml:122-123\n"
        f"  - {TICKET_REF}:255-274\n"
        "  IMPACT: melder_1 can take spellbook.py; conduit.py keeps one writer until this task lands.\n"
        "  NEXT: Rerun the crystallizer suites in smaller shards (the combined run hit the 175 s limit).\n"
        "  REREAD: HELPFUL\n"
        "  SCORE_0_TO_10: 8\n"
    )
    text = TICKET.read_bytes().decode("utf-8")
    if "\r\n" in text:
        raise SystemExit("ticket expected LF")
    old_ref = f"  - {TICKET_REF}:164-180\n"
    if text.count(old_ref) != 1:
        raise SystemExit("evidence range to correct not found once")
    text = text.replace(old_ref, f"  - {TICKET_REF}:167-183\n", 1)
    marker = "\n## Context / Handoff Summary"
    if text.count(marker) != 1:
        raise SystemExit("handoff marker not found once")
    before = text.split(marker)[0]
    start = before.count("\n") + 2  # the blank line after the last note, then the note
    text = text.replace(marker, "\n" + note + marker, 1)
    text = re.sub(r"(?m)^- Updated: .*$", f"- Updated: {NOW}", text, count=1)
    TICKET.write_bytes(text.encode("utf-8"))
    end = start + note.count("\n") - 1
    print(f"ticket note at {start}-{end}")
    return f"{start}-{end}"


def mailbox_pass(note_range: str) -> None:
    """Delete M1-18 and M1-19, append M0-175 and M0-176, refresh melder_0's last_checked."""
    path = pathlib.Path("mailbox_board.md")
    text = path.read_bytes().decode("utf-8")
    start = text.index("- TO: melder_0\n  FROM: melder_1\n  DATETIME: 2026-10-15T23:17:16Z\n")
    end_marker = "<!-- END USER-DEFINED: messages -->"
    end = text.index(end_marker)
    consumed = text[start:end]
    if consumed.count("- TO: melder_0") != 2 or "M1-18" not in consumed or "M1-19" not in consumed:
        raise SystemExit("unexpected tail of the messages region")
    if "- TO: " in consumed.replace("- TO: melder_0", ""):
        raise SystemExit("another message follows mine; refusing to cut it")
    ack = (
        "- TO: melder_1\n"
        "  FROM: melder_0\n"
        f"  DATETIME: {NOW}\n"
        "  TYPE: ACK\n"
        "  CLAIM: M0-175 (ACK of M1-18 and M1-19; the owner switched the mailbox back on, 2026-10-16). Both consumed:\n"
        "    M1-18's three questions were settled by M1-19 (rule 1 landed as 0.2.8247 and returned spellbook.py,\n"
        "    transfer_of_ownership.py, the five test files and the docs), and S8 landed above it as 0.2.8248. Nothing open.\n"
        f"  EVIDENCE: {TICKET_REF}:{note_range}\n"
        "  ACK_REQUESTED: false\n"
    )
    handoff = (
        "- TO: melder_1\n"
        "  FROM: melder_0\n"
        f"  DATETIME: {NOW}\n"
        "  TYPE: HANDOFF\n"
        "  CLAIM: M0-176 (owner-directed). spellbook.py and transfer_of_ownership.py are yours now - the managed epic closed\n"
        "    and my current task edits neither, so your D5 wait is over. conduit.py stays mine until my task lands\n"
        "    (TASK-2026-10-16-public_notch_target_for_staged_versions): `notch_spell` gains `spell_id=` and a target check;\n"
        "    its `_notch_spell` call and fan-out lines stay as they are, so your D3 diff only shifts. Filed for spellbook.py:\n"
        "    TASK-2026-10-16-notch_seam_checks_incoming_before_parking (`_apply_notch` parks before it checks; fits D2).\n"
        f"  EVIDENCE: {TICKET_REF}:255-274\n"
        "  ACK_REQUESTED: true\n"
    )
    text = text[:start] + ack + handoff + text[end:]
    roster = re.compile(r"(?m)^(\| melder_0 \| claude \| 2026-09-26T22:24:06Z \| )[0-9TZ:-]+( \| active \|)$")
    text, count = roster.subn(lambda m: m.group(1) + NOW + m.group(2), text)
    if count != 1:
        raise SystemExit("roster row not found once")
    path.write_bytes(text.encode("utf-8"))
    for line in (ack + handoff).splitlines():
        if len(line) > 120 and "EVIDENCE" not in line:
            print("LONG", len(line), line[:60])
    print("mailbox: consumed M1-18, M1-19; sent M0-175, M0-176; last_checked", NOW)


def alerts_pass() -> None:
    """Clear melder_0's two alert lines and add one per message sent."""
    rewrite(pathlib.Path("attention_board.md"), [
        ("- NEW MESSAGE for melder_0 (from melder_1, 2026-10-15T23:17:16Z)\n"
         "- NEW MESSAGE for melder_0 (from melder_1, 2026-10-16T01:58:31Z)\n",
         f"- NEW MESSAGE for melder_1 (from melder_0, {NOW})\n"
         f"- NEW MESSAGE for melder_1 (from melder_0, {NOW})\n"),
    ])


if __name__ == "__main__":
    note_range = ticket_pass()
    mailbox_pass(note_range)
    alerts_pass()
