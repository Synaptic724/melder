"""Link the removal fix's patch docs: ticket Artifact Links + a PLAN Note (patch mapping), artifact board row.

melder_1 (synaptic_python_developer), 2026-10-16. Anchors must match exactly once. --check, then --apply.
"""
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
TICKET = ROOT / "tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md"
BOARD = ROOT / "artifact_board.md"
PATCH = "system_docs/patches/active/contracted_copy_removal_by_version_2026_10_16/"
TICKET_REF = "tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md"


def once(text, anchor, label):
    n = text.count(anchor)
    if n != 1:
        raise SystemExit(f"{label}: anchor found {n} times - refusing")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--check"
    if mode not in ("--check", "--apply"):
        raise SystemExit("usage: --check | --apply")
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for f in ("architecture_patch.md", "component_patch_borrower_contracted_removal.md",
              "code_description_patch_remove_contracted_spell.md"):
        if not (ROOT / PATCH / f).is_file():
            raise SystemExit(f"missing patch doc {f}")

    text = TICKET.read_text(encoding="utf-8")
    stamps = re.findall(r"^- Updated: \S+$", text, flags=re.M)
    if len(stamps) != 1:
        raise SystemExit("Updated stamp not found exactly once")
    text = text.replace(stamps[0], f"- Updated: {ts}")
    link_anchor = ("  - system_docs/patches/completed/contract_recheck_on_notch_2026_10_16/ (the seven patch docs, "
                   "archived at promotion)\n")
    once(text, link_anchor, "ticket artifact link")
    text = text.replace(link_anchor, link_anchor + f"  - {PATCH} (the removal fix's three patch docs)\n")
    note = (
        f"\n- DATETIME: {ts}\n"
        "  AUTHOR: melder_1\n"
        "  AUTHOR_ROLE: synaptic_python_developer\n"
        "  TYPE: PLAN\n"
        "  CLAIM: Patch docs for the removal fix are written and linked (patch id\n"
        "    contracted_copy_removal_by_version_2026_10_16: architecture, one component, one code description), read in\n"
        "    the gate's order. Mapping, patch section -> implementation -> validation: architecture Invariants (one\n"
        "    version, one copy) -> the active-entry match in `Spellbook._remove_contracted_spell` by the copy's own\n"
        "    `spell_id`, the parked branch and its raise unchanged -> the unit tests (parked removal beside an active\n"
        "    version; a copyless member id raises and keeps the active copy); component Before/after -> the same method\n"
        "    and the one component test that asserted the old match -> that test removing the active copy by its own id;\n"
        "    component Validation (integration) -> the unlink after a notch with each member first, order forced ->\n"
        "    both copies gone, the index untracked, nothing raised; code description Control flow 5 -> rule 2's mark\n"
        "    kept on the active branch -> the existing rule 2 unit tests stay green. Unknowns: none for the target path.\n"
        "  EVIDENCE:\n"
        f"  - context_compass/{PATCH}architecture_patch.md:1-44\n"
        f"  - context_compass/{PATCH}component_patch_borrower_contracted_removal.md:1-35\n"
        f"  - context_compass/{PATCH}code_description_patch_remove_contracted_spell.md:1-22\n"
        "  IMPACT: The patch gate's entry checklist is met; the src edit waits only on the red tests.\n"
        "  NEXT: Write the red tests and run them on the current tree.\n"
        "  REREAD: REQUIRED\n"
        "  SCORE_0_TO_10: 8\n"
    )
    # Evidence paths are unbreakable tokens (configuration_standards.md exceptions); prose lines must fit.
    long = [ln for ln in note.split("\n") if len(ln) > 120 and not ln.startswith("  - context_compass/")]
    if long:
        raise SystemExit(f"lines over 120 chars: {long}")
    heading = "\n## Context / Handoff Summary\n"
    once(text, heading, "handoff heading")
    text = text.replace(heading, note + heading)

    board = BOARD.read_text(encoding="utf-8")
    row_prefix = f"| {TICKET_REF} | artifacts/meld_contract_scan_20261015/ |"
    rows = [ln for ln in board.split("\n") if ln.startswith(row_prefix)]
    if len(rows) != 1:
        raise SystemExit(f"board row found {len(rows)} times")
    new_row = (f"| {TICKET_REF} | {PATCH} | patch_doc | active | promote_to_documentation | The removal fix's "
               "entry-gate docs (architecture, one component, one code description); promote at landing (0.2.8251) "
               f"and archive. | {ts} | REQUIRED |")
    if new_row.split(" | ")[1] in board:
        raise SystemExit("board already lists the patch folder")
    board = board.replace(rows[0] + "\n", rows[0] + "\n" + new_row + "\n", 1)

    print("ts", ts, "note longest", max(len(ln) for ln in note.split("\n")))
    if mode == "--check":
        print("check only - nothing written")
        return
    TICKET.write_text(text, encoding="utf-8")
    BOARD.write_text(board, encoding="utf-8")
    assert TICKET.read_text(encoding="utf-8") == text
    assert BOARD.read_text(encoding="utf-8") == board
    print("applied and read back")


if __name__ == "__main__":
    main()
