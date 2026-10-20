"""Ticket Notes, resume view and board row after the 0.2.8251 docs, notch and graph.

melder_1 (synaptic_python_developer), 2026-10-16. Appends two FACT Notes (docs/release note/notch; graph),
rewrites the one current Context / Handoff Summary, ticks the red/green checklist line, refreshes the Updated
stamp, and refreshes the meld_contract_scan row's `next` and `updated_at` on attention_board.md.
Every anchor must match exactly once. Run with --check first, then --apply.
"""
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
TICKET = ROOT / "tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md"
BOARD = ROOT / "attention_board.md"
A = "context_compass/artifacts/meld_contract_scan_20261015/"
D = "context_compass/system_docs/"


def notes(ts):
    return (
        f"\n- DATETIME: {ts}\n"
        "  AUTHOR: melder_1\n"
        "  AUTHOR_ROLE: synaptic_python_developer\n"
        "  TYPE: FACT\n"
        "  CLAIM: The removal fix's docs, release note and notch are in. The three patch docs are promoted:\n"
        "    src_architecture gains the invariant \"One version, one copy\" and the failure mode \"Fixed in 0.2.8251\",\n"
        "    its code map remeasures spellbook.py (7766 lines) and every numeric citation into spellbook.py below the\n"
        "    method moved seven lines (the two settle-then-inherit inner citations, stale since an earlier lane, now\n"
        "    point at :6971-6983 and :6984); src_components gains the Spellbook Core contract and the ConduitWard\n"
        "    member loop; tests_components names the new unit, component and integration tests and adds the\n"
        "    lifecycle file's code-map record; the three indexes are regenerated and check OK. The release note reads\n"
        "    \"# Melder 0.2.8251\" with the section \"Unlinking an index after a notch removes every version's copy\";\n"
        "    its example runs clean on the fixed src for PYTHONHASHSEED 0-9 with the GIL off and on, and fails on\n"
        "    0.2.8250's src for 6 of the 10 seeds (1, 3, 4, 5, 7, 8; a first wording said five, corrected before the\n"
        "    notch). `__version__` is 0.2.8251, and NOTICE M1-23 told melder_0 to notch above it and to recheck its\n"
        "    held spellbook.py decisions (the file grew seven lines inside the method).\n"
        "  EVIDENCE:\n"
        f"  - {D}src_architecture.md:1104-1118\n"
        f"  - {D}src_architecture.md:2124-2135\n"
        f"  - {D}src_architecture.md:2864-2879\n"
        f"  - {D}src_architecture.md:4361-4367\n"
        f"  - {D}src_components.md:348-360\n"
        f"  - {D}src_components.md:3207-3213\n"
        f"  - {D}src_components.md:11333-11336\n"
        f"  - {D}tests_components.md:1178-1182\n"
        f"  - {D}tests_components.md:1495-1497\n"
        f"  - {D}tests_components.md:1670-1674\n"
        f"  - {D}tests_components.md:3305-3311\n"
        "  - release_docs/next_version_release.md:779-805\n"
        "  - src/melder/__version__.py:12-12\n"
        "  - context_compass/mailbox_board.md:912-923\n"
        f"  - {A}land_docs_removal_2026_10_16.py:1-244\n"
        f"  - {A}release_note_removal_2026_10_16.py:1-76\n"
        f"  - {A}release_example_removal_2026_10_16.py:1-45\n"
        f"  - {A}runs/release_example_removal_2026_10_16.txt:1-41\n"
        f"  - {A}fix_seed_wording_2026_10_16.py:1-56\n"
        f"  - {A}notch_0_2_8251_2026_10_16.py:1-40\n"
        f"  - {A}send_m1_23_2026_10_16.py:1-63\n"
        "  IMPACT: 0.2.8251 is documented, noted for users and notched; the graph and the turn-in steps remain.\n"
        "  NEXT: Re-extract the two changed descriptors, author and accept the Spellbook node, reassemble the graph.\n"
        "  REREAD: HELPFUL\n"
        "  SCORE_0_TO_10: 8\n"
        f"\n- DATETIME: {ts}\n"
        "  AUTHOR: melder_1\n"
        "  AUTHOR_ROLE: synaptic_python_developer\n"
        "  TYPE: FACT\n"
        "  CLAIM: The graph carries 0.2.8251. spellbook.json and __version__.json were re-extracted from the real src\n"
        "    (only the two source hashes and the Spellbook node's span changed; no other descriptor touched), the\n"
        "    Spellbook node gained a 24th responsibility - it removes a borrowed copy by the spell_id it is given, the\n"
        "    active copy only when that copy's own spell_id is it, otherwise the parked copy, raising when it holds\n"
        "    neither - and, re-read against `_remove_contracted_spell`, was accepted (graph_walker rewrote the\n"
        "    descriptor at indent 2, as every accept does). Reassembled: src_graph.md is 28076 lines (sha bb75f8dc),\n"
        "    its index verified; the only differences from the 17:17Z assembly are the two source hashes and the new\n"
        "    responsibility line. The device VM rebooted at about 22:05Z and wiped /tmp: the scratch trees and\n"
        "    baselines under /tmp/cc_res/removal are gone. Nothing in the repository was lost (the scripts and runs are\n"
        "    in the artifact folder), and no scratch is left to delete.\n"
        "  EVIDENCE:\n"
        f"  - {D}src_graph.md:15736-15845\n"
        f"  - {D}src_graph_index.md:9-18\n"
        f"  - {D}graph/melder/aether/spellbook/spellbook.json:1-462\n"
        f"  - {A}graph_semantics_removal_2026_10_16.py:1-50\n"
        "  - src/melder/aether/spellbook/spellbook.py:3344-3470\n"
        "  IMPACT: Every system document and the graph carry the fix; what remains is the owner's direction on the open\n"
        "    items, the closure, the rebuild and the release NOTICE to melder_0.\n"
        "  NEXT: Ask the owner how to place the open items (the contract row's state, transfers vs contracts, the\n"
        "    transfer binding-key gap, the spell_id grant check) before the closure.\n"
        "  REREAD: REQUIRED\n"
        "  SCORE_0_TO_10: 9\n"
    )


HANDOFF = (
    "## Context / Handoff Summary\n"
    "Current state ({ts}): this ticket has landed two source changes; its closure waits on the owner.\n"
    "- 0.2.8250, rule 2 with D1-D5 (owner-accepted, Notes 18:23Z; in the owner's commit 192482b4c): a satisfied\n"
    "  SpellContract is not checked on every meld; a change of what a spell resolves marks it for revalidation (the\n"
    "  borrower Book's five contracted-map mutators; a notch's downstream walk, D2); the meld refreshes stale\n"
    "  dependencies before a plan compiles; a lost provider is named with its remedy (D1-B); a notch back makes a\n"
    "  parked version grant active again (D3). Release-note section \"A satisfied `SpellContract` is not checked on\n"
    "  every meld; a notch reaches every spell that depends on the notched one\".\n"
    "- 0.2.8251, the removal fix (owner-approved, Notes 21:22Z): `Spellbook._remove_contracted_spell` removes\n"
    "  exactly the copy of the spell_id it is given, so an index unlink after a notch completes in any member order.\n"
    "  Release-note section \"Unlinking an index after a notch removes every version's copy\".\n"
    "Both carry tests (green with the GIL off and on), system docs with their indexes, the graph and the release note.\n"
    "Patch docs: system_docs/patches/completed/contract_recheck_on_notch_2026_10_16/ (archived) and\n"
    "system_docs/patches/active/contracted_copy_removal_by_version_2026_10_16/ (promoted; archive at closure).\n"
    "Open, the owner's: whether a contract's per-version row carries active/inactive state (Notes 20:59Z); what\n"
    "borrowers get after an ownership transfer - index links and the repoint option are refused silently (18:23Z);\n"
    "rule 2's binding-key gap on the transfer flip (18:23Z; fix: pass binding_key=spell_obj._key in its\n"
    "register_index and rollback); add_spell_to_contract and remove_spell_from_contract by a parked version's\n"
    "spell_id refuse (21:36Z). Filed: TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout (its race\n"
    "test is xfail) and TASK-2026-10-16-investigate_lent_consumer_provider_loss.\n"
    "Next: (1) the owner's direction on the open items; (2) the closure - summary naming 0.2.8250 and 0.2.8251 and\n"
    "their release-note sections, the patch docs archived, board and artifact sync; (3) the rebuild last, both checks\n"
    "OK; (4) NOTICE M1-24 releasing the files melder_0 waits for (Notes 18:46Z).\n"
    "Evidence: the Notes from 09:57:21Z on; artifacts/meld_contract_scan_20261015/.\n"
)

OLD_NEXT = ("| Owner discussion: which copy an unlink removes after a notch, transfers vs contracts and rule 2's "
            "binding-key gap on transfer; then closure, rebuild last. |")
NEW_NEXT = ("| Owner's direction on the open items (contract-row state, transfers vs contracts, the transfer "
            "binding-key gap, spell_id grants); then closure, rebuild last, NOTICE M1-24. |")


def edit_ticket(text, ts):
    stamps = re.findall(r"^- Updated: \S+$", text, flags=re.M)
    if len(stamps) != 1:
        raise SystemExit(f"Updated stamp found {len(stamps)} times - refusing")
    text = text.replace(stamps[0], f"- Updated: {ts}")
    box = "- [ ] Red tests, the change, green suites (GIL off and on), measurement.\n"
    if text.count(box) != 1:
        raise SystemExit("checklist line not found exactly once - refusing")
    text = text.replace(box, box.replace("[ ]", "[x]"))
    start = text.find("\n## Context / Handoff Summary\n")
    end = text.find("\n## Project-Specific Additions\n")
    if start < 0 or end < 0 or text.count("\n## Context / Handoff Summary\n") != 1 or end < start:
        raise SystemExit("handoff section anchors not found exactly once - refusing")
    note = notes(ts)
    handoff = HANDOFF.format(ts=ts)
    for block in (note, handoff):
        long = [ln for ln in block.split("\n") if len(ln) > 120 and not ln.startswith("  - context_compass/")]
        if long:
            raise SystemExit(f"lines over 120 chars: {long} - refusing")
    return text[:start] + note + "\n" + handoff + text[end:]


def edit_board(text, ts):
    rows = [ln for ln in text.split("\n") if ln.startswith("| meld_contract_scan |")]
    if len(rows) != 1 or text.count(OLD_NEXT) != 1:
        raise SystemExit("board row or its next field not found exactly once - refusing")
    row = rows[0]
    stamp = re.findall(r"\| (2026-10-16T\d\d:\d\d:\d\dZ) \| REQUIRED \|$", row)
    if len(stamp) != 1:
        raise SystemExit("row updated_at not found - refusing")
    new_row = row.replace(OLD_NEXT, NEW_NEXT).replace(f"| {stamp[0]} | REQUIRED |", f"| {ts} | REQUIRED |")
    return text.replace(row, new_row)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--check"
    if mode not in ("--check", "--apply"):
        raise SystemExit("usage: --check | --apply")
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    t_old = TICKET.read_text(encoding="utf-8")
    b_old = BOARD.read_text(encoding="utf-8")
    if "\r\n" in t_old or "\r\n" in b_old:
        raise SystemExit("CRLF found - refusing (both files are LF)")
    t_new = edit_ticket(t_old, ts)
    b_new = edit_board(b_old, ts)
    print("ts", ts, "| ticket lines", t_old.count("\n"), "->", t_new.count("\n"),
          "| board lines", b_old.count("\n"), "->", b_new.count("\n"))
    if mode == "--check":
        print("check only - nothing written")
        return
    TICKET.write_text(t_new, encoding="utf-8")
    BOARD.write_text(b_new, encoding="utf-8")
    assert TICKET.read_text(encoding="utf-8") == t_new and BOARD.read_text(encoding="utf-8") == b_new
    print("applied and read back")


if __name__ == "__main__":
    main()
