"""
Close TASK-2026-10-15-describe_notch_borrower_follow_as_feature and sync the boards (melder_1, 2026-10-15).

Usage (from the repository root): python3 <this file> <closed_at>
Edits the task in place (status, completion block, transition, steps, validation, checklists, artifact links,
attribution, the closing DECISION note, the handoff view), then edits attention_board.md (removes the
notch_borrower_docs row and detail entry, appends the closed anchor, drops the oldest anchor to keep 12) and
artifact_board.md (adds the cleared row). The move to tickets/tasks/completed/ is done by the caller with mv -n.
Every replacement asserts exactly one match, every written line stays within 120 characters, and nothing is
written unless all edits succeed.
"""
import pathlib
import sys

CC = pathlib.Path("context_compass")
TASK = CC / "tickets/tasks/2026-10-15_describe_notch_borrower_follow_as_feature_task.md"
DONE_REL = "tickets/tasks/completed/2026-10-15_describe_notch_borrower_follow_as_feature_task.md"
BOARD = CC / "attention_board.md"
ARTS = CC / "artifact_board.md"
LANE = "artifacts/slotted_lifetime_fixes_20261014"


def one(text: str, old: str, new: str) -> str:
    """Replace exactly one occurrence of old with new, or fail."""
    count = text.count(old)
    assert count == 1, (count, old[:80])
    return text.replace(old, new, 1)


def check_width(block: str) -> None:
    """Fail when a written line is over the 120-character hard cap (table rows excepted)."""
    for line in block.splitlines():
        assert len(line) <= 120 or line.startswith("|"), (len(line), line)


def close_task(text: str, closed: str) -> str:
    """Apply every closure edit to the task text."""
    text = one(text, "- Status: in_progress\n", "- Status: done\n")
    start = text.index("- Updated: ")
    end = text.index("\n", start) + 1
    summary = (
        f"- Updated: {closed}\n\n"
        f"- Completed: {closed}\n"
        "- Summary: Docs only (no notch): `src_architecture` opens with \"What Melder Is (Read This First)\" - not a DI\n"
        "  container but a runtime agents live and build in - and the three \"known limitation\" passages describe\n"
        "  borrowers following a notch as the feature it is; indexes, assets and bundles are current; unit_top,\n"
        "  unit_build and unit_llm pass with the GIL off and on.\n"
    )
    check_width(summary)
    text = text[:start] + summary + text[end:]
    reason = "- transition_reason: the owner directed the correction (chat 2026-10-15: \"its not a limitation its a feature\").\n"
    done_event = (
        "- from_state: in_progress\n"
        "- to_state: done\n"
        "- transition_reason: exit gate met - the passages match the notch code, the owner's direction (the feature\n"
        "  reading, the top section) is recorded, indexes, assets and bundles are current with checks OK, and the\n"
        "  document, asset and bundle suites pass with the GIL off and on; routine owner-directed docs work, closed by\n"
        "  its assigned agent; the commit stays the owner's.\n"
    )
    check_width(done_event)
    text = one(text, reason, reason + done_event)
    text = one(text, "- [ ] Add the packaging line;", "- [x] Add the packaging line;")
    text = one(text, "- [ ] Run Ticket Microcycle during execution:", "- [x] Run Ticket Microcycle during execution:")
    text = one(text, "- [ ] Record meaningful attributed findings", "- [x] Record meaningful attributed findings")
    validation = (
        "- Index checks: src_architecture (61 sections over 4250 lines) and src_components (149 over 11167) current.\n"
        "- Asset check and bundle check (`--include-untracked`): three OK lines each\n"
        f"  ({LANE}/runs/rebuild_2026_10_15_closure.txt).\n"
        "- unit_top 145, unit_build 116 and unit_llm 28 passed with the GIL off and on\n"
        f"  ({LANE}/runs/docs_2026_10_15_final_gil0.txt and _gil1.txt).\n"
        "- Not run: the rest of the tree; nothing it reads changed.\n"
    )
    check_width(validation)
    text = one(text, "- Not run yet: index checks, asset check, bundle check.\n", validation)
    for item in (
        "No status transition without evidence-backed transition reason.",
        "No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.",
        "No closure without delegated acceptance or reserved-owner disposition and board-sync completion.",
    ):
        text = one(text, f"- [ ] {item}", f"- [x] {item}")
    d0 = text.index("## Done Checklist\n")
    d1 = text.index("## Artifact Links (Optional)\n")
    section = text[d0:d1]
    assert section.count("- [ ] ") == 9, section.count("- [ ] ")
    text = text[:d0] + section.replace("- [ ] ", "- [x] ") + text[d1:]
    old_links = (
        "- ARTIFACTS_REQUIRED: false\n- ARTIFACT_PATHS:\n  - none\n"
        "- DISPOSITION: delete_on_close\n- CLEANUP_TRIGGER: none\n"
    )
    new_links = (
        "- ARTIFACTS_REQUIRED: true\n- ARTIFACT_PATHS:\n"
        f"  - {LANE}/landing/notch_borrower_docs_2026_10_15.py\n"
        f"  - {LANE}/landing/what_melder_is_2026_10_15.py\n"
        f"  - {LANE}/landing/close_notch_borrower_docs_2026_10_15.py\n"
        f"  - {LANE}/runs/rebuild_2026_10_15_what_melder_is.txt\n"
        f"  - {LANE}/runs/rebuild_2026_10_15_closure.txt\n"
        f"  - {LANE}/runs/docs_2026_10_15_gil0.txt\n"
        f"  - {LANE}/runs/docs_2026_10_15_final_gil0.txt\n"
        f"  - {LANE}/runs/docs_2026_10_15_final_gil1.txt\n"
        "- DISPOSITION: retain_as_reference\n"
        "- CLEANUP_TRIGGER: none - kept in the slotted lane's evidence folder, which is rowed under its epic\n"
    )
    check_width(new_links)
    text = one(text, old_links, new_links)
    text = one(
        text,
        "  the design and the direction are the owner's.\n",
        f"  the design and the direction are the owner's; Notes and closure revisions 2026-10-15T08:56:47Z-{closed}.\n",
    )
    note = (
        f"- DATETIME: {closed}\n"
        "  AUTHOR: melder_1\n"
        "  AUTHOR_ROLE: synaptic_python_developer\n"
        "  TYPE: DECISION\n"
        "  CLAIM: Closed: the exit gate is met. Re-read after the compaction, the notch code still matches the\n"
        "    corrected passages - `notch_spell` ends its transaction, then `_deactivate_borrowed_spell` has each linked\n"
        "    peer park its copy of the outgoing version and `_emit_index_notch` moves each index-link contract to the\n"
        "    new version (park old, activate or mint new on the receiver); nothing is destroyed. The owner's direction\n"
        "    is recorded, and the indexes, assets and bundles are current with the document, asset and bundle suites\n"
        "    passing on both builds. Routine owner-directed docs work, closed by its assigned agent; no independent\n"
        "    review was asked for. Not part of this task and not started: a matching \"not a DI container\" note in\n"
        "    the beginner docs or README, which is the owner's call.\n"
        "  EVIDENCE:\n"
        "  - src/melder/aether/conduit/conduit.py:5461-5549\n"
        "  - src/melder/aether/conduit/conduit.py:5746-5775\n"
        "  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2316-2380\n"
        f"  - context_compass/{LANE}/runs/docs_2026_10_15_final_gil0.txt:1-3\n"
        f"  - context_compass/{LANE}/runs/docs_2026_10_15_final_gil1.txt:1-3\n"
        "  IMPACT: The lane is turned in; the board no longer routes it.\n"
        "  NEXT: Rerun both checks after the board sync; then nothing until the owner directs.\n"
        "  REREAD: HELPFUL\n"
        "  SCORE_0_TO_10: 8\n"
    )
    check_width(note)
    text = one(text, "\n\n## Context / Handoff Summary\n", "\n" + note + "\n## Context / Handoff Summary\n")
    h0 = text.index("## Context / Handoff Summary\n") + len("## Context / Handoff Summary\n")
    h1 = text.index("\n## Project-Specific Additions")
    handoff = (
        f"Done ({closed}). Docs only, no notch, at the owner's direction (chat 2026-10-15): `src_architecture` opens\n"
        "with \"What Melder Is (Read This First)\" - not a DI container but a runtime agents live and build in - with\n"
        "the Runtime Model under it, and the Architecture Summary, SpellIndex Mutation Entry step 6 and the\n"
        "src_components SpellIndex Mutation Surface describe borrowers following a notch while older versions stay\n"
        "alive. Indexes, assets and bundles are current (checks OK); unit_top, unit_build and unit_llm pass with the\n"
        "GIL off and on. Open, the owner's call: a matching \"not a DI container\" note in the beginner docs or\n"
        "README. Next: none.\n"
    )
    check_width(handoff)
    text = text[:h0] + handoff + text[h1:]
    return text


def sync_attention_board(text: str, closed: str) -> str:
    """Remove the row and detail entry, append the anchor and drop the oldest anchor."""
    row_start = text.index("| notch_borrower_docs | in_progress |")
    row_end = text.index("\n", row_start) + 1
    assert text.count("| notch_borrower_docs |") == 1
    text = text[:row_start] + text[row_end:]
    detail = (
        "- WORK_ITEM: notch_borrower_docs\n"
        "  SWITCH_TRIGGER: The passages are corrected with checks OK and the task closed, or the owner redirects.\n"
        "  RESUME_HIERARCHY:\n"
        "    - tickets/tasks/2026-10-15_describe_notch_borrower_follow_as_feature_task.md\n"
    )
    text = one(text, detail, "")
    a0 = text.index("<!-- BEGIN USER-DEFINED: closed_anchors -->\n") + len("<!-- BEGIN USER-DEFINED: closed_anchors -->\n")
    a1 = text.index("<!-- END USER-DEFINED: closed_anchors -->")
    rows = [r for r in text[a0:a1].split("\n") if r]
    assert len(rows) == 12 and rows[0].startswith("| slotted_lifetime_audit |"), rows[0]
    anchor = (
        f"| notch_borrower_docs | done | melder_1 | {DONE_REL} | Docs only (no notch): src_architecture opens with "
        "what Melder is (not a DI container); notch borrowers described as the feature. Next: none. "
        f"| {closed} |"
    )
    rows = rows[1:] + [anchor]
    assert len(rows) == 12
    return text[:a0] + "\n".join(rows) + "\n" + text[a1:]


def sync_artifact_board(text: str, closed: str) -> str:
    """Add the task's cleared row at the top of the cleared history."""
    marker = "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n"
    row = (
        f"| {DONE_REL} | {LANE}/ | retain_as_reference | The 2026-10-15 docs pass in the lane folder: the "
        "notch-borrower, what-Melder-is and closure scripts, both rebuild logs and the docs_2026_10_15 test runs. "
        f"| {closed} |\n"
    )
    return one(text, marker, marker + row)


def main() -> None:
    """Compute every edit first, then write the three files."""
    closed = sys.argv[1]
    task = close_task(TASK.read_text(encoding="utf-8"), closed)
    board = sync_attention_board(BOARD.read_text(encoding="utf-8"), closed)
    arts = sync_artifact_board(ARTS.read_text(encoding="utf-8"), closed)
    for text in (task, board, arts):
        assert "\r\n" not in text
    TASK.write_text(task, encoding="utf-8")
    BOARD.write_text(board, encoding="utf-8")
    ARTS.write_text(arts, encoding="utf-8")
    print("closed", closed)


if __name__ == "__main__":
    main()
