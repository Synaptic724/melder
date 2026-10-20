"""Consume M0-198 for melder_1 (S9 lane): note into the S9 story, delete the message, clear the alert,
refresh melder_1's check-in row. Run from the repository root. Prints what it changed."""
import datetime
import pathlib
import sys

ROOT = pathlib.Path("context_compass")
STORY = ROOT / "tickets/stories/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md"
MAILBOX = ROOT / "mailbox_board.md"
BOARD = ROOT / "attention_board.md"
APPLY = ROOT / "artifacts/direct_cleanup_refusal_20261018/scripts/apply_s9_refusal.py"


def now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def line_of(lines: list, prefix: str) -> int:
    for i, line in enumerate(lines, 1):
        if line.startswith(prefix):
            return i
    raise SystemExit("anchor not found: " + prefix)


def main() -> None:
    stamp = now()
    story_text = STORY.read_text(encoding="utf-8")
    lines = story_text.split("\n")
    eb_start = line_of(lines, "- EXECUTION_BOUNDARY:")
    eb_end = line_of(lines, "- DEPENDENCIES:") - 1
    apply_len = len(APPLY.read_text(encoding="utf-8").splitlines())
    note = "\n".join([
        "- DATETIME: " + stamp,
        "  AUTHOR: melder_1",
        "  AUTHOR_ROLE: synaptic_python_developer",
        "  TYPE: FACT",
        "  CLAIM: M0-198 from melder_0 (2026-10-18T16:24:40Z, NOTICE), consumed. S1 and S2 of",
        "    EPIC-2026-10-18-spell_identity_is_the_code are built and run in a /tmp mirror while S9 lands; nothing of",
        "    theirs enters the repository's src until spellbook.py and spell.py are handed back, and both notch above",
        "    0.2.8256. Besides those two they will edit bind.py, the new spell_code_digest.py and binding_manifest.py,",
        "    binding_profile.py, binding_profile_strategy.py, structural_snapshot.py, caching_system.py (generation",
        "    23), spellbook_creation_system.py, the two generalized manifest modules, spell_crystal.py and",
        "    record_version.py (restore_engine.py and graft_runner.py if the record patch needs them), and docstrings in",
        "    lookup_container.py, aether.py, aether_configuration.py, conduit_meld.py, meld.py, spellspace_meld.py,",
        "    contract/details.py, inspector_utility.py and maybe spell_index.py; the bind-guard manifest regenerates",
        "    (628 -> 630). He asked whether S9 touches any of them: it does not. S9's src edits are E1-E7 in",
        "    spellbook.py and spell.py and the notch in __version__.py; the answer rides M1-38 with the landing notice.",
        "  EVIDENCE:",
        "  - context_compass/tickets/stories/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md:"
        + str(eb_start) + "-" + str(eb_end),
        "  - context_compass/artifacts/direct_cleanup_refusal_20261018/scripts/apply_s9_refusal.py:1-" + str(apply_len),
        "  IMPACT: S9 and S1/S2 share no src file but the two handed back at S9's landing; they meet again in the",
        "    system documents, the graph descriptors and the release note, which S1/S2 change in the mirror, so their",
        "    landing re-reads what S9 lands there (M1-38 names it).",
        "  NEXT: Land S9 - docs, indexes, graph, notch 0.2.8256, release note, closure, rebuild; then M1-38.",
        "  REREAD: HELPFUL",
        "  SCORE_0_TO_10: 7",
        "",
    ])
    anchor = "\n## Closure Confirmation\n"
    if story_text.count(anchor) != 1:
        raise SystemExit("story closure anchor not unique")
    if "M0-198 from melder_0" in story_text:
        raise SystemExit("note already present")
    story_text = story_text.replace(anchor, "\n" + note + anchor[1:], 1)
    old_upd = "- Updated: 2026-10-18T16:02:48Z\n"
    if story_text.count(old_upd) != 1:
        raise SystemExit("story Updated anchor not unique")
    story_text = story_text.replace(old_upd, "- Updated: " + stamp + "\n", 1)
    STORY.write_text(story_text, encoding="utf-8", newline="\n")
    print("story note added at", stamp)

    mail = MAILBOX.read_text(encoding="utf-8")
    start = mail.find("- TO: melder_1\n  FROM: melder_0\n  DATETIME: 2026-10-18T16:24:40Z\n")
    if start < 0:
        raise SystemExit("M0-198 not found")
    end_marker = "  ACK_REQUESTED: false\n"
    end = mail.find(end_marker, start)
    if end < 0:
        raise SystemExit("M0-198 end not found")
    end += len(end_marker)
    block = mail[start:end]
    if "M0-198" not in block or block.count("- TO:") != 1:
        raise SystemExit("unexpected block")
    mail = mail[:start] + mail[end:]
    old_row = "| melder_1 | claude | 2026-09-26T17:46:30Z | 2026-10-18T15:41:09Z | active |\n"
    if mail.count(old_row) != 1:
        raise SystemExit("check-in row anchor not unique")
    mail = mail.replace(old_row, "| melder_1 | claude | 2026-09-26T17:46:30Z | " + stamp + " | active |\n", 1)
    MAILBOX.write_text(mail, encoding="utf-8", newline="\n")
    print("M0-198 deleted (" + str(block.count("\n")) + " lines); check-in row refreshed")

    board = BOARD.read_text(encoding="utf-8")
    alert = "- NEW MESSAGE for melder_1 (from melder_0, 2026-10-18T16:24:40Z)\n"
    if board.count(alert) != 1:
        raise SystemExit("alert not unique")
    board = board.replace(alert, "", 1)
    BOARD.write_text(board, encoding="utf-8", newline="\n")
    print("alert cleared")


if __name__ == "__main__":
    main()
