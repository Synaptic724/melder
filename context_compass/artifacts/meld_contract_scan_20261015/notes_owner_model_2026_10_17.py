"""Ticket Notes: the owner's answers on the object walk-through (contract rows decided; notification model).

melder_1 (synaptic_python_developer), 2026-10-17. Appends a DECISION and an ALIGNMENT_CHECK Note and refreshes the
Updated stamp. Anchors must match exactly once. Run with --check first, then --apply.
"""
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
TICKET = ROOT / "tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md"
S = "src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py"
B = "src/melder/aether/spellbook/spellbook.py"
C = "src/melder/aether/conduit/conduit.py"


def notes(ts: str) -> str:
    return (
        f"\n- DATETIME: {ts}\n"
        "  AUTHOR: melder_1\n"
        "  AUTHOR_ROLE: synaptic_python_developer\n"
        "  TYPE: DECISION\n"
        "  CLAIM: Contract rows (answers the DECISION_REQUEST of 2026-10-16T20:59:43Z). The owner (chat 2026-10-17):\n"
        "    Contracts and Details do not need to know whether a version is active or inactive - that is the\n"
        "    Spellbook's responsibility; a contract is about lending a spell, not observing it; what matters is that\n"
        "    active/inactive checks and ownership transfer are handled properly. No state field is added to Detail or\n"
        "    IndexDetail; the borrower Book's active and parked maps stay the only record of a copy's state, and every\n"
        "    lookup of a borrowed or owned version checks both (as the 0.2.8251 removal does).\n"
        "  EVIDENCE: src/melder/aether/conduit/conduit_ward/contract/details.py:14-404\n"
        "  IMPACT: Item 3 is closed with no change.\n"
        "  NEXT: None for this item.\n"
        "  REREAD: HELPFUL\n"
        "  SCORE_0_TO_10: 8\n"
        f"\n- DATETIME: {ts}\n"
        "  AUTHOR: melder_1\n"
        "  AUTHOR_ROLE: synaptic_python_developer\n"
        "  TYPE: ALIGNMENT_CHECK\n"
        "  CLAIM: The owner's notification model (chat 2026-10-17, his words: SpellSystemStates has nothing to do with\n"
        "    contracts; when a notch happens the spell, its dependencies and its upstream reliances must be notified as\n"
        "    dirty; a contract change distributes the notification into the impacted spells, which then run their\n"
        "    resolution, and that updates SpellSystemStates; marking through SpellSystemStates blends responsibility).\n"
        "    Where the code routes contract notification through SpellSystemStates today: (a) every borrower Book\n"
        "    finds the spells that use a changed copy through the per-Book index `_contract_dependents_by_spellbook`,\n"
        "    there since at least 2026-05-19 (0d0f1bc94); (b) rule 2's D2 walk (`mark_dependents_for_revalidation`,\n"
        "    called by `_apply_notch`) crosses into other Books through the pair map `_binding_key_by_index` that\n"
        "    0.2.8250 added (192482b4c), and it marks every Book's users of the pair, even Books that do not borrow\n"
        "    the spell. The notch's own fan-out to borrowers already runs through the contracts (the conduit's links).\n"
        "    Open with the owner: what 'its dependencies' covers; whether (b), and (a), are reworked so the contract\n"
        "    side routes the notification; the borrowers after a transfer; the grant's exact lookup.\n"
        "  EVIDENCE:\n"
        f"  - {S}:973-1036\n"
        f"  - {S}:1697-1788\n"
        f"  - {B}:3906-4061\n"
        f"  - {B}:5089-5143\n"
        f"  - {C}:5622-5759\n"
        f"  - {C}:6236-6310\n"
        "  IMPACT: The transfer fix follows his model (notify the impacted spells through the contracts; no registry\n"
        "    record kept by the transfer), and it may reshape rule 2's landed D2 walk, which is his call.\n"
        "  NEXT: Confirm the reading with the owner and take his direction on the open points before any src edit.\n"
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
    long = [ln for ln in note.split("\n") if len(ln) > 120 and not ln.startswith("  - ")]
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
