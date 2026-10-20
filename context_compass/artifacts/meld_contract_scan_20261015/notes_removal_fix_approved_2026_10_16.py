"""Ticket Note: the owner approved the contracted-copy removal fix; scope, notch and patch gate recorded.

melder_1 (synaptic_python_developer), 2026-10-16. Appends one DECISION Note and refreshes the Updated stamp.
Anchors must match exactly once. Run with --check first, then --apply.
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
        "  TYPE: DECISION\n"
        "  CLAIM: The owner approved the removal fix (chat 2026-10-16, \"yeah sure this makes sense\", answering \"Want me\n"
        "    to make the change now, with a test that runs the unlink with each version going first?\"; his rule: \"you\n"
        "    remove that spell if its not active, you look in inactive, thats it\"). `Spellbook._remove_contracted_spell`\n"
        "    removes the copy of exactly the version it is asked for: the active copy only when that copy IS the version,\n"
        "    otherwise the parked copy, and it raises only when the Book holds neither; rule 2's mark stays on an active\n"
        "    removal. It joins this ticket as its own source change with its own notch (0.2.8251 if `__version__` still\n"
        "    reads 0.2.8250 at landing). The existence set `_contracted_spell_ids` keeps today's handling: it is\n"
        "    index-level by design (both add paths record every member id of the index) and only `snapshot_state` and the\n"
        "    per-conduit key checks read it; melder_1's earlier word that the fix would discard only the removed id is\n"
        "    withdrawn, and the owner was told before any edit. One existing test asserts the old behaviour - it removes a\n"
        "    member id that has no copy and expects the active copy gone - and is changed to remove the active copy by its\n"
        "    own id. The patch gate applies (a contract-removal behaviour change with a src_architecture failure-mode\n"
        "    entry): patch docs under system_docs/patches/active/contracted_copy_removal_by_version_2026_10_16/ come before\n"
        "    the src edit. Still the owner's, untouched: the contract row's active/inactive state, transfers vs contracts,\n"
        "    and rule 2's binding-key gap on the transfer path.\n"
        "  EVIDENCE:\n"
        "  - src/melder/aether/spellbook/spellbook.py:3344-3463\n"
        "  - src/melder/aether/spellbook/spellbook.py:3178-3247\n"
        "  - src/melder/aether/spellbook/spellbook.py:3249-3291\n"
        "  - src/melder/aether/spellbook/spellbook.py:1989-2046\n"
        "  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2221-2272\n"
        "  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2389-2438\n"
        "  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2491-2517\n"
        "  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2557-2589\n"
        "  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2770-2900\n"
        "  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:3189-3330\n"
        "  - tests/component/melder/spellbook/test_spellbook_component_contracts.py:379-418\n"
        "  IMPACT: Every caller asks for one version's copy - the index unlink, destroy and member removal (through\n"
        "    `_uncontract_member_spell`), a root's dependency fallout (`_remove_root_from_contracts`) and a version\n"
        "    uncontract (`_remove_spell_from_contract`) - so each now gets that copy, and the unlink completes in either\n"
        "    member order instead of raising in about half of all processes.\n"
        "  NEXT: Write the patch docs and link them; then the red tests.\n"
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
