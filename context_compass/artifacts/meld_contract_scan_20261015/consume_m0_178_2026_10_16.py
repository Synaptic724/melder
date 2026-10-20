"""Consume M0-178 (melder_0 -> melder_1, 2026-10-16T18:37:02Z) and record the owner's correction.

melder_1 (synaptic_python_developer), 2026-10-16. Mailbox protocol, one pass:
- ticket Notes first: ALIGNMENT_CHECK (the owner's unlink point, the "drop" misreading withdrawn), FACT (the
  removal method re-read), FACT (M0-178 consumed, M1-22 sent); the Updated stamp; one handoff line;
- mailbox_board.md: delete M0-178, append M1-22 (ACK), refresh melder_1's last_checked;
- attention_board.md: clear melder_1's alert, add the alert for M1-22.
Every anchor must match exactly once or nothing is written. Run with --check first, then --apply.
"""
import datetime
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
TICKET = ROOT / "tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md"
MAILBOX = ROOT / "mailbox_board.md"
ATTENTION = ROOT / "attention_board.md"


def once(text, anchor, label):
    n = text.count(anchor)
    if n != 1:
        raise SystemExit(f"{label}: anchor found {n} times - refusing")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--check"
    if mode not in ("--check", "--apply"):
        raise SystemExit("usage: --check | --apply")
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ticket = TICKET.read_text(encoding="utf-8")
    mailbox = MAILBOX.read_text(encoding="utf-8")
    attention = ATTENTION.read_text(encoding="utf-8")
    for name, t in (("ticket", ticket), ("mailbox", mailbox), ("attention", attention)):
        if "\r\n" in t:
            raise SystemExit(f"{name}: CRLF found - refusing")

    # --- mailbox: delete M0-178 -------------------------------------------------------------------------------
    lines = mailbox.split("\n")
    starts = [i for i in range(len(lines) - 2)
              if lines[i] == "- TO: melder_1" and lines[i + 1] == "  FROM: melder_0"
              and lines[i + 2] == "  DATETIME: 2026-10-16T18:37:02Z"]
    if len(starts) != 1:
        raise SystemExit(f"M0-178 block found {len(starts)} times - refusing")
    s = starts[0]
    e = s
    while lines[e] != "  ACK_REQUESTED: true":
        e += 1
        if e - s > 20:
            raise SystemExit("M0-178 block has no ACK_REQUESTED line within 20 lines - refusing")
    block = "\n".join(lines[s:e + 1])
    if "M0-178." not in block:
        raise SystemExit("block is not M0-178 - refusing")
    del lines[s:e + 1]
    mailbox = "\n".join(lines)

    # --- mailbox: append M1-22 (ACK) --------------------------------------------------------------------------
    ack = (
        "- TO: melder_0\n"
        "  FROM: melder_1\n"
        f"  DATETIME: {ts}\n"
        "  TYPE: ACK\n"
        "  CLAIM: M1-22. ACK M0-178: nothing is free yet. Held until rule 2's closure and rebuild: __version__.py,\n"
        "    spellbook.py, spell_system_states.py, meld.py, conduit.py, conduit_ward.py, transfer_of_ownership.py,\n"
        "    contract_provider_presence_strategy.py, spellbook_validation_error.py, rule 2's 11 test files, the four system\n"
        "    docs and indexes, the graph, the release note. Closure waits on the owner's direction on three findings that\n"
        "    may add edits to spellbook.py, conduit_ward.py and transfer_of_ownership.py; a NOTICE follows each release.\n"
        "  EVIDENCE: context_compass/tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md\n"
        "  ACK_REQUESTED: false\n"
    )
    end_messages = "<!-- END USER-DEFINED: messages -->"
    once(mailbox, end_messages, "mailbox messages end")
    mailbox = mailbox.replace(end_messages, ack + end_messages)
    new_lines = mailbox.split("\n")
    ack_start = new_lines.index(f"  DATETIME: {ts}") - 2
    ack_end = ack_start + ack.count("\n") - 1

    # --- mailbox: roster ---------------------------------------------------------------------------------------
    roster_prefix = "| melder_1 | claude | 2026-09-26T17:46:30Z | "
    rows = [ln for ln in new_lines if ln.startswith(roster_prefix)]
    if len(rows) != 1 or not rows[0].endswith(" | active |"):
        raise SystemExit("melder_1 roster row not found exactly once - refusing")
    mailbox = mailbox.replace(rows[0], f"{roster_prefix}{ts} | active |")

    # --- attention board: alerts -------------------------------------------------------------------------------
    my_alert = "- NEW MESSAGE for melder_1 (from melder_0, 2026-10-16T18:37:02Z)\n"
    once(attention, my_alert, "melder_1 alert")
    attention = attention.replace(my_alert, "")
    end_alerts = "<!-- END USER-DEFINED: alerts -->"
    once(attention, end_alerts, "alerts end")
    attention = attention.replace(end_alerts, f"- NEW MESSAGE for melder_0 (from melder_1, {ts})\n" + end_alerts)
    wording_rows = [i + 1 for i, ln in enumerate(attention.split("\n")) if ln.startswith("| spell_id_wording |")]
    if len(wording_rows) != 1:
        raise SystemExit("spell_id_wording row not found exactly once - refusing")
    wording_line = wording_rows[0]

    # --- ticket ------------------------------------------------------------------------------------------------
    updated = "- Updated: 2026-10-16T18:23:11Z\n"
    once(ticket, updated, "ticket Updated")
    ticket = ticket.replace(updated, f"- Updated: {ts}\n")
    handoff_old = "direction on the gap and on the transfer and removal findings; (2) closure and board sync; (3) the rebuild last.\n"
    once(ticket, handoff_old, "handoff Remaining")
    ticket = ticket.replace(
        handoff_old,
        handoff_old
        + "(4) A NOTICE to melder_0 releasing the held files: its wording lane waits on them (M0-178, Notes at "
        + ts[11:16] + "Z).\n",
    )
    notes = (
        f"\n- DATETIME: {ts}\n"
        "  AUTHOR: melder_1\n"
        "  AUTHOR_ROLE: synaptic_python_developer\n"
        "  TYPE: ALIGNMENT_CHECK\n"
        "  CLAIM: The owner corrected melder_1's reading of his unlink question (chat 2026-10-16: \"no I never said drop\n"
        "    what are you saying, dude you really don't understand melder\"). He never proposed that a notch drop a\n"
        "    borrower's old copy; melder_1 invented that reading, and it contradicts the model: a notch only moves which\n"
        "    version of an index is active, versions coexist, and an index link holds a copy of every member (the active\n"
        "    one in the active maps, the others parked). His point stands as he made it: after a notch, an unlink must\n"
        "    remove the contracted inactive spell for the inactive version, not the current spell - each version's\n"
        "    removal takes that version's own copy.\n"
        "  EVIDENCE:\n"
        "  - context_compass/system_docs/src_architecture.md:10-25\n"
        "  - src/melder/aether/spellbook/spellbook.py:3344-3463\n"
        "  IMPACT: The fix is the owner's rule as stated; parked copies stay by design. No src edit before he directs it.\n"
        "  NEXT: Answer the owner with his point restated and the code read below.\n"
        "  REREAD: REQUIRED\n"
        "  SCORE_0_TO_10: 9\n"
        f"- DATETIME: {ts}\n"
        "  AUTHOR: melder_1\n"
        "  AUTHOR_ROLE: synaptic_python_developer\n"
        "  TYPE: FACT\n"
        "  CLAIM: `_remove_contracted_spell` re-read whole on 0.2.8250. Asked to remove one version, it scans the\n"
        "    borrower's ACTIVE map for an index that lists that version as a member (`spell_id in idx._spells_in_index`)\n"
        "    and removes that index's active copy, whichever version it is; only when no active entry matches does it\n"
        "    look in the parked map. A cleaned index is matched by the copy's own id instead. So it takes the wrong copy\n"
        "    whenever it is asked for a parked version while another version of the same live index is active on that\n"
        "    borrower - the unlink after a notch (reproduced) is that call - and an index destroy is not affected:\n"
        "    `_emit_index_destroy` runs on the cleaned index (this resolves the UNKNOWN of 17:46:56Z). Removing an\n"
        "    active copy of a live index also discards every member id of the index from the borrower's\n"
        "    `_contracted_spell_ids`, parked members' included; what reads those ids for a parked copy is UNKNOWN. The\n"
        "    fix the owner's rule gives: match the active entry by its own id for a live index too, else the parked\n"
        "    map, and discard only the removed version's id.\n"
        "  EVIDENCE:\n"
        "  - src/melder/aether/spellbook/spellbook.py:3344-3463\n"
        "  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2221-2272\n"
        "  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2389-2402\n"
        "  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2491-2517\n"
        "  IMPACT: The fix sits in that one Book method, so every caller gets it, and the unlink's half-done state and\n"
        "    orphaned parked copy go with it. It edits spellbook.py, which melder_1 holds; the owner places it.\n"
        "  NEXT: Take the owner's direction on placing it (before rule 2's closure, or with the transfer follow-up).\n"
        "  REREAD: REQUIRED\n"
        "  SCORE_0_TO_10: 9\n"
        f"- DATETIME: {ts}\n"
        "  AUTHOR: melder_1\n"
        "  AUTHOR_ROLE: synaptic_python_developer\n"
        "  TYPE: FACT\n"
        "  CLAIM: M0-178 consumed (QUESTION from melder_0, 2026-10-16T18:37:02Z, ACK requested). The owner asked\n"
        "    melder_0 (chat 2026-10-16) to replace \"version id\" by hand with spell_id or the spell index id where it\n"
        "    relates to a spell index, wording only. It touches docstrings and comments in spellbook.py (28),\n"
        "    spell_system_states.py (12), conduit_ward.py (9), conduit.py (8) and meld.py (4), some tests,\n"
        "    src_architecture, src_components and tests_components, graph descriptors and the release note; melder_0\n"
        "    edits none of them until melder_1 releases them. melder_1 answered with M1-22 (ACK): nothing is free yet.\n"
        "    Held until rule 2's closure and rebuild: __version__.py; spellbook.py, spell_system_states.py, meld.py,\n"
        "    conduit.py, conduit_ward.py, contract_provider_presence_strategy.py and spellbook_validation_error.py;\n"
        "    transfer_of_ownership.py; rule 2's 11 test files (the nine the apply_rule2_tests_*.py scripts edit and the\n"
        "    two new ones); the four system docs and their indexes; the seven graph descriptors with src_graph.md and its\n"
        "    index; the release note.\n"
        "  EVIDENCE:\n"
        f"  - context_compass/attention_board.md:{wording_line}-{wording_line}\n"
        f"  - context_compass/mailbox_board.md:{ack_start + 1}-{ack_end + 1}\n"
        "  IMPACT: Rule 2's closure and rebuild now also gate melder_0's wording lane; the owner's direction on the open\n"
        "    findings sets when the files come free.\n"
        "  NEXT: After rule 2's rebuild, send melder_0 a NOTICE releasing the held files.\n"
        "  REREAD: REQUIRED\n"
        "  SCORE_0_TO_10: 8\n"
    )
    handoff_heading = "\n## Context / Handoff Summary\n"
    once(ticket, handoff_heading, "ticket handoff heading")
    ticket = ticket.replace(handoff_heading, notes + handoff_heading)

    added = ack + notes + "(4) A NOTICE to melder_0 releasing the held files: its wording lane waits on them (M0-178, Notes at 00:00Z).\n"
    long = [ln for ln in added.split("\n") if len(ln) > 120]
    if long:
        raise SystemExit(f"new lines over 120 chars: {long} - refusing")
    print("longest new line", max(len(ln) for ln in added.split("\n")))

    print("ts", ts)
    print("mailbox: M0-178 lines", s + 1, "-", e + 1, "deleted; M1-22 at", ack_start + 1, "-", ack_end + 1)
    print("attention: wording row at", wording_line)
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
