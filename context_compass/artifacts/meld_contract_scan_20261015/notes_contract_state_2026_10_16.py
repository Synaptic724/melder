"""Ticket Note: the owner's contract-state principle and what the contract and the borrower Book record today.

melder_1 (synaptic_python_developer), 2026-10-16. Appends one DECISION_REQUEST Note and refreshes the Updated
stamp. Anchors must match exactly once. Run with --check first, then --apply.
"""
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
TICKET = ROOT / "tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md"


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--check"
    if mode not in ("--check", "--apply"):
        raise SystemExit("usage: --check | --apply")
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    text = TICKET.read_text(encoding="utf-8")
    stamps = re.findall(r"^- Updated: \S+$", text, flags=re.M)
    if len(stamps) != 1:
        raise SystemExit(f"Updated stamp found {len(stamps)} times - refusing")
    text = text.replace(stamps[0], f"- Updated: {ts}")
    note = (
        f"\n- DATETIME: {ts}\n"
        "  AUTHOR: melder_1\n"
        "  AUTHOR_ROLE: synaptic_python_developer\n"
        "  TYPE: DECISION_REQUEST\n"
        "  CLAIM: The owner (chat 2026-10-16): the contract must be kept up to date with the changes that occur - when a\n"
        "    spell goes inactive, that should show - and he asked for the unlink defect as an example. What is recorded\n"
        "    today (read whole): the borrower Book keeps each borrowed copy, by version id, in exactly one of two lists,\n"
        "    active (`_contracted_spells_by_id` with the index-keyed and lookup maps) or inactive\n"
        "    (`_inactive_contracted_spells`); a notch moves the outgoing copy to inactive (`_deactivate_contracted_spell`)\n"
        "    and the incoming one to active (`_reactivate_contracted_spell`, `_ensure_contracted_active`). On the ward\n"
        "    side an index link's `IndexDetail.selected_spell_id` follows the active version (`update_selected` in\n"
        "    `_emit_index_notch`), but the per-version `Detail` rows carry version, permission, reason and sources and no\n"
        "    active/inactive state. `_remove_contracted_spell` consults neither by version. The owner decides whether the\n"
        "    contract's per-version row should carry the state too, or the removal reads the Book's lists, which already\n"
        "    show it.\n"
        "  EVIDENCE:\n"
        "  - src/melder/aether/conduit/conduit_ward/contract/details.py:14-247\n"
        "  - src/melder/aether/conduit/conduit_ward/contract/details.py:249-404\n"
        "  - src/melder/aether/conduit/conduit_ward/contract/contract.py:99-124\n"
        "  - src/melder/aether/spellbook/spellbook.py:1623-1774\n"
        "  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2322-2387\n"
        "  - src/melder/aether/spellbook/spellbook.py:3344-3463\n"
        "  IMPACT: The removal fix needs no new state; a state field on the contract row is a design addition that every\n"
        "    notch fan-out would have to keep in step with the Book's lists.\n"
        "  NEXT: The owner's answer on the contract row; no src edit before it.\n"
        "  REREAD: REQUIRED\n"
        "  SCORE_0_TO_10: 9\n"
    )
    long = [ln for ln in note.split("\n") if len(ln) > 120]
    if long:
        raise SystemExit(f"lines over 120 chars: {long} - refusing")
    heading = "\n## Context / Handoff Summary\n"
    if text.count(heading) != 1:
        raise SystemExit("handoff heading not found exactly once - refusing")
    text = text.replace(heading, note + heading)
    print("ts", ts, "longest", max(len(ln) for ln in note.split("\n")))
    if mode == "--check":
        print("check only - nothing written")
        return
    TICKET.write_text(text, encoding="utf-8")
    assert TICKET.read_text(encoding="utf-8") == text
    print("applied and read back")


if __name__ == "__main__":
    main()
