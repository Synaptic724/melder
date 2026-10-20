"""Ticket Notes: the removal fix is in the real tree (FACT) and validated (MEASURE).

melder_1 (synaptic_python_developer), 2026-10-16. Appends two Notes and refreshes the Updated stamp.
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
    a = "context_compass/artifacts/meld_contract_scan_20261015/"
    note = (
        f"\n- DATETIME: {ts}\n"
        "  AUTHOR: melder_1\n"
        "  AUTHOR_ROLE: synaptic_python_developer\n"
        "  TYPE: FACT\n"
        "  CLAIM: The removal fix is in the real tree, byte-identical to the scratch tree it was tested on.\n"
        "    `Spellbook._remove_contracted_spell` matches the active copy only by the copy's own `spell_id` (for a live\n"
        "    or a cleaned index alike) and falls back to the version's parked copy, raising as before when neither\n"
        "    exists; its docstring says so and the stale matching comment is rewritten (the diff: one docstring\n"
        "    paragraph, the loop, two comments). Tests: three unit tests in test_spellbook.py (one parametrized), two\n"
        "    integration tests in test_spell_index_meld_and_contract_lifecycle.py (one parametrized, the member order\n"
        "    fixed through `SpellIndex.spells_in_index`), and the component test that asserted the old match now\n"
        "    removes the active copy by its own id. The apply script rewrote the two CRLF test files with LF;\n"
        "    fix_crlf_removal_tests_2026_10_16.py put CRLF back on every line in both trees, so their diffs are the 11\n"
        "    and 100 lines of the change.\n"
        "  EVIDENCE:\n"
        "  - src/melder/aether/spellbook/spellbook.py:3344-3470\n"
        f"  - {a}apply_removal_src_2026_10_16.py:1-98\n"
        f"  - {a}apply_removal_tests_2026_10_16.py:1-291\n"
        f"  - {a}fix_crlf_removal_tests_2026_10_16.py:1-39\n"
        "  IMPACT: Every caller - unlink, destroy, member removal, dependency fallout, version uncontract - now gets the\n"
        "    copy of the version it names.\n"
        "  NEXT: The system docs, the graph and the release note; then the notch.\n"
        "  REREAD: REQUIRED\n"
        "  SCORE_0_TO_10: 9\n"
        f"\n- DATETIME: {ts}\n"
        "  AUTHOR: melder_1\n"
        "  AUTHOR_ROLE: synaptic_python_developer\n"
        "  TYPE: MEASURE\n"
        "  CLAIM: Green. The five red cases pass (26 targeted, GIL off and on), and the three touched files pass whole\n"
        "    after the CRLF restore (193, both modes). Every suite chunk of the tree passes with the GIL off and on\n"
        "    (unit_sb 2582 with the four new unit cases, int_aether 808 with the three new ones) but one test that was\n"
        "    already failing and that this change does not touch: unit_top's\n"
        "    `test_generated_build_assets_are_stamped_for_the_live_version`, because the generated assets still carry\n"
        "    0.2.8249 while `__version__` is 0.2.8250 - rule 2's rebuild is still pending and the last rebuild fixes it.\n"
        "    int_conduit's rule-2 race test is a non-strict xfail and xpassed in both modes (the known race, not this\n"
        "    change). probe_index_uncontract_after_notch.py with PYTHONHASHSEED 0-9 now unlinks clean on every seed -\n"
        "    no copy, active or parked, and an empty existence set; seeds 3, 4, 6, 8 and 9 raised before.\n"
        "  EVIDENCE:\n"
        f"  - {a}runs/removal_green_files.txt:1-5\n"
        f"  - {a}runs/removal_suites_gil0.txt:1-23\n"
        f"  - {a}runs/removal_suites_gil1.txt:1-23\n"
        f"  - {a}runs/probe_index_uncontract_after_notch_seeds_fixed_gil0.txt:1-11\n"
        f"  - {a}runs/probe_index_uncontract_after_notch_seeds_gil0.txt:1-20\n"
        "  IMPACT: The change is validated; the turn-in steps follow.\n"
        "  NEXT: Promote the patch docs into the system docs and regenerate their indexes.\n"
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
