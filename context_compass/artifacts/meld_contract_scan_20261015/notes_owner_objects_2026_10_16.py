"""Ticket Notes: the owner asked for a deeper explanation with real objects; what the object probe shows.

melder_1 (synaptic_python_developer), 2026-10-16. Appends an ALIGNMENT_CHECK and a MEASURE Note and refreshes the
Updated stamp. Anchors must match exactly once. Run with --check first, then --apply.
"""
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
TICKET = ROOT / "tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md"
A = "context_compass/artifacts/meld_contract_scan_20261015/"
T = "src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py"
S = "src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py"


def notes(ts: str) -> str:
    return (
        f"\n- DATETIME: {ts}\n"
        "  AUTHOR: melder_1\n"
        "  AUTHOR_ROLE: synaptic_python_developer\n"
        "  TYPE: ALIGNMENT_CHECK\n"
        "  CLAIM: The owner found the explanation of the four open items too superficial (chat 2026-10-16) and asked\n"
        "    to talk them through with the real objects instead of examples. His own reading: (1) after a transfer the\n"
        "    moved spell, what it depends on and what depends on it should be flagged for revalidation; (2) borrowers\n"
        "    should be flagged the same way; (3) unclear; (4) we already settled checking active then inactive, and\n"
        "    resolution happens only from active spells. Nothing is decided; no src edit before his direction.\n"
        f"  EVIDENCE: {A}probe_owner_objects_2026_10_16.py:1-254\n"
        "  IMPACT: The closure waits for this discussion; the probe below answers each item with object dumps.\n"
        "  NEXT: Walk the owner through the object dumps, item by item, and take his direction.\n"
        "  REREAD: REQUIRED\n"
        "  SCORE_0_TO_10: 8\n"
        f"\n- DATETIME: {ts}\n"
        "  AUTHOR: melder_1\n"
        "  AUTHOR_ROLE: synaptic_python_developer\n"
        "  TYPE: MEASURE\n"
        "  CLAIM: probe_owner_objects (0.2.8251, a copy of src, GIL off and on alike). Lender: Bang (Mark-index) and\n"
        "    English(mark: Mark) (Greeter-index); borrower: Banner with SpellContract(Greeter, \"greeter\"), index links\n"
        "    to both. notch: the lender notches Mark to Dot, the walk marks Greeter-index by edge (impacted) and Banner by\n"
        "    its contract pair (\"greeter\", \"greeter\"), and Banner melds HELLO. (rebuilt). transfer: the lender first\n"
        "    moves English to a third root; the flip unregisters the lineage and registers a NEW state, so Greeter-index\n"
        "    has no edges either way (Mark-index lists no dependents) and no pair (None); Banner is not flagged; the\n"
        "    contract keeps its index rows and the borrower its copies (the swallowed refusal); after the same notch\n"
        "    nothing is marked and Banner melds HELLO! - the old Mark. So the gap is the whole registry record, not\n"
        "    the pair alone (the 'two lines' estimate was wrong). `_gate_transfer_impacts` dirties conduits through\n"
        "    `mark_conduit_dirty`, a flag no meld path reads (`ConduitResolutionState.is_dirty` has no caller).\n"
        "    contract: a notch changes IndexDetail.selected_spell_id and moves the Book's copies between active and\n"
        "    parked; Detail rows never change, so a version grant's contract shows nothing when its version is parked.\n"
        "    lookup: find_spell_by_id and get_spell_by_id answer the parked French with the active English,\n"
        "    _get_owned_spell answers French; add_spell_to_contract(spell_id=French) refuses (\"does not match inspected\n"
        "    ID\"); given the French Spell, the borrower holds a parked copy, Banner cannot resolve it (no active\n"
        "    provider), and after the notch to French Banner melds BONJOUR!. Aside: `_contracted_spell_ids` lists every\n"
        "    member of the index even for a one-version grant.\n"
        "  EVIDENCE:\n"
        f"  - {A}runs/probe_owner_objects_notch_gil0.txt:1-37\n"
        f"  - {A}runs/probe_owner_objects_transfer_gil0.txt:1-69\n"
        f"  - {A}runs/probe_owner_objects_contract_gil0.txt:1-46\n"
        f"  - {A}runs/probe_owner_objects_lookup_gil0.txt:1-24\n"
        f"  - {T}:1383-1507\n"
        f"  - {T}:719-757\n"
        f"  - {S}:1147-1259\n"
        f"  - {S}:973-1036\n"
        f"  - {S}:1581-1603\n"
        "  - src/melder/aether/spellbook/spellbook.py:2052-2131\n"
        "  - src/melder/aether/spellbook/spellbook.py:3323-3341\n"
        "  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1472-1568\n"
        "  IMPACT: A transfer silently disconnects the moved spell from rule 2 until it is recompiled and notched again,\n"
        "    and nobody downstream of it through a contract is flagged; the fix is a transfer that keeps the record and\n"
        "    flags what depends on the moved spell, which is the owner's (1) and (2).\n"
        "  NEXT: Put the dumps to the owner item by item; take his direction before any src edit.\n"
        "  REREAD: REQUIRED\n"
        "  SCORE_0_TO_10: 9\n"
    )


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "--check"
    if mode not in ("--check", "--apply"):
        raise SystemExit("usage: --check | --apply")
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    text = TICKET.read_text(encoding="utf-8")
    stamps = re.findall(r"^- Updated: \S+$", text, flags=re.M)
    if len(stamps) != 1:
        raise SystemExit(f"Updated stamp found {len(stamps)} times - refusing")
    text = text.replace(stamps[0], f"- Updated: {ts}")
    note = notes(ts)
    long = [ln for ln in note.split("\n") if len(ln) > 120 and not ln.startswith("  - ") and "EVIDENCE: context" not in ln]
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
