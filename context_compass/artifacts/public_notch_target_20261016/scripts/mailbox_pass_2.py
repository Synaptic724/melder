"""Mailbox pass 2 (after the 13:39Z re-onboarding): note first, then consume M1-20, clear its alert line and refresh
melder_0's last_checked.

Run from the context_compass root:  python artifacts/public_notch_target_20261016/scripts/mailbox_pass_2.py <NOW>
Every shared file is re-read right before its write; every edit is an exact, asserted replacement.
"""
import pathlib
import re
import sys

NOW = sys.argv[1]
TICKET = pathlib.Path("tickets/tasks/2026-10-16_public_notch_target_for_staged_versions_task.md")
PEER = "context_compass/tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md"
ALERT = "- NEW MESSAGE for melder_0 (from melder_1, 2026-10-16T12:57:39Z)\n"
M1_20_HEAD = "- TO: melder_0\n  FROM: melder_1\n  DATETIME: 2026-10-16T12:57:39Z\n  TYPE: ACK\n"


def row_line_after_alert_removal() -> int:
    """Line number melder_1's board row will have once melder_0's alert line above it is removed."""
    lines = pathlib.Path("attention_board.md").read_text(encoding="utf-8").split("\n")
    rows = [i + 1 for i, ln in enumerate(lines) if ln.startswith("| meld_contract_scan | in_progress")]
    alerts = [i + 1 for i, ln in enumerate(lines) if ln + "\n" == ALERT]
    if len(rows) != 1 or len(alerts) != 1 or alerts[0] > rows[0]:
        raise SystemExit(f"board shape unexpected: rows={rows} alerts={alerts}")
    return rows[0] - 1


def ticket_pass(row_line: int) -> None:
    """Append the consumption note before the handoff summary and set Updated."""
    note = (
        f"- DATETIME: {NOW}\n"
        "  AUTHOR: melder_0\n"
        "  AUTHOR_ROLE: synaptic_python_developer\n"
        "  TYPE: FACT\n"
        "  CLAIM: Re-onboarded after a context compaction (attestation 13:39Z, self-certified on the owner's standing\n"
        "    instruction) and consumed M1-20, melder_1's ACK of M0-175 and M0-176 (no ACK requested). The owner approved\n"
        "    melder_1's rule-2 patch; its build runs on a scratch copy of the tree over spellbook.py,\n"
        "    spell_system_states.py, meld.py, the contract presence strategy, spellbook_validation_error.py and\n"
        "    conduit_ward.py (docstring and comment), with tests - not transfer_of_ownership.py. conduit.py stays with\n"
        "    this task until it lands; then melder_0 hands it over and names the notch it took, and melder_1's D3 lines\n"
        "    follow one notch above. The seam task stays a backlog draft unless the owner adds it to melder_1's lane.\n"
        "  EVIDENCE:\n"
        f"  - {PEER}:686-747\n"
        f"  - context_compass/attention_board.md:{row_line}-{row_line}\n"
        "  IMPACT: The closure NOTICE (M0-177) releases conduit.py and names the notch; melder_1's landing comes after\n"
        "    this one and re-extracts its own files' graph descriptors and rebuilds then.\n"
        "  NEXT: Land the docs and probes MEASURE note.\n"
        "  REREAD: HELPFUL\n"
        "  SCORE_0_TO_10: 8\n"
    )
    text = TICKET.read_bytes().decode("utf-8")
    if "\r\n" in text:
        raise SystemExit("ticket expected LF")
    marker = "\n## Context / Handoff Summary"
    if text.count(marker) != 1:
        raise SystemExit("handoff marker not found once")
    start = text.split(marker)[0].count("\n") + 2
    text = text.replace(marker, "\n" + note + marker, 1)
    text, count = re.subn(r"(?m)^- Updated: .*$", f"- Updated: {NOW}", text, count=1)
    if count != 1:
        raise SystemExit("Updated line not found")
    TICKET.write_bytes(text.encode("utf-8"))
    print(f"ticket note at {start}-{start + note.count(chr(10)) - 1}")
    for line in note.splitlines():
        if len(line) > 120:
            print("LONG", len(line), line[:60])


def mailbox_pass() -> None:
    """Delete M1-20 (the last message of the region) and refresh melder_0's last_checked."""
    path = pathlib.Path("mailbox_board.md")
    text = path.read_bytes().decode("utf-8")
    if "\r\n" in text:
        raise SystemExit("mailbox expected LF")
    if text.count(M1_20_HEAD) != 1:
        raise SystemExit("M1-20 not found once")
    start = text.index(M1_20_HEAD)
    end = text.index("<!-- END USER-DEFINED: messages -->")
    consumed = text[start:end]
    if consumed.count("- TO: ") != 1 or "M1-20" not in consumed:
        raise SystemExit("unexpected tail of the messages region")
    text = text[:start] + text[end:]
    roster = re.compile(r"(?m)^(\| melder_0 \| claude \| 2026-09-26T22:24:06Z \| )[0-9TZ:-]+( \| active \|)$")
    text, count = roster.subn(lambda m: m.group(1) + NOW + m.group(2), text)
    if count != 1:
        raise SystemExit("roster row not found once")
    path.write_bytes(text.encode("utf-8"))
    print("mailbox: consumed M1-20; last_checked", NOW)


def alerts_pass() -> None:
    """Clear melder_0's alert line for M1-20."""
    path = pathlib.Path("attention_board.md")
    text = path.read_bytes().decode("utf-8")
    if "\r\n" in text or text.count(ALERT) != 1:
        raise SystemExit("alert line not found once (or CRLF board)")
    path.write_bytes(text.replace(ALERT, "", 1).encode("utf-8"))
    print("attention_board: alert cleared")


if __name__ == "__main__":
    row = row_line_after_alert_removal()
    ticket_pass(row)
    mailbox_pass()
    alerts_pass()
