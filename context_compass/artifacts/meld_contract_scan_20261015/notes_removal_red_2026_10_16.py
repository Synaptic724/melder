"""Ticket Note: the removal fix's red run.

melder_1 (synaptic_python_developer), 2026-10-16. Appends one MEASURE Note and refreshes the Updated stamp.
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
        "  TYPE: MEASURE\n"
        "  CLAIM: Red on the unchanged src (0.2.8250), GIL off, scratch tree /tmp/cc_res/removal/tree (the real tree\n"
        "    plus apply_removal_tests_2026_10_16.py): 5 failed, 21 passed - exactly the five cases the fix is for. Unit:\n"
        "    removing parked sid-1 removed the active sid-2 copy; a copyless member id did not raise (it took the\n"
        "    active copy); the parked-first order raised \"Spell version sid-2 not found\". Integration (public calls):\n"
        "    the unlink after a notch, parked member first, raised \"Spell version <new> not found for conduit ID\n"
        "    <owner>\"; removing the old version's grant (by its Spell) took the new version's active copy. The\n"
        "    active-first orders and the component file, with its updated test, pass on the old src as predicted.\n"
        "    Found on the way, outside the fix: `add_spell_to_contract` and `remove_spell_from_contract` by `spell_id=`\n"
        "    of a parked version raise \"Provided spell_id ... does not match inspected ID ...\" (their argument check\n"
        "    resolves a parked id to the index's active member, as `notch_spell` did before 0.2.8249); the grant test\n"
        "    passes the Spell object it kept while the version was active.\n"
        "  EVIDENCE:\n"
        "  - context_compass/artifacts/meld_contract_scan_20261015/apply_removal_tests_2026_10_16.py:1-291\n"
        "  - context_compass/artifacts/meld_contract_scan_20261015/runs/removal_red_gil0.txt:1-20\n"
        "  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1472-1568\n"
        "  IMPACT: The tests fail for the defect and pass for harmless orders; the src change can go in.\n"
        "  NEXT: Apply the one-method change on the scratch tree and rerun these tests, then the suites.\n"
        "  REREAD: REQUIRED\n"
        "  SCORE_0_TO_10: 9\n"
    )
    long = [ln for ln in note.split("\n") if len(ln) > 120 and not ln.startswith("  - context_compass/")]
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
