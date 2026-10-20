"""Record S9's PLAN note (patch, red tests, exact edits E1-E7 and the mirror preview), refresh the handoff's Next and
the board row, ahead of the owner's word on the exact edits.

Each file is re-read right before it is written; every anchor must occur exactly once; LF kept; read back.
Usage: record_s9_ready_for_word.py --check | --apply
"""
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
LANE = "artifacts/direct_cleanup_refusal_20261018"
STORY_REL = "tickets/stories/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md"
NOW = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def lines_of(rel: str, base: pathlib.Path = ROOT) -> int:
    """Count the lines of a file (the evidence range's end)."""
    return len((base / rel).read_text(encoding="utf-8").splitlines())


def ev(rel: str, repo_rel: bool = False) -> str:
    """One evidence line `path:1-N` for a whole file."""
    if repo_rel:
        return "  - %s:1-%d" % (rel, lines_of(rel, ROOT.parent))
    return "  - context_compass/%s:1-%d" % (rel, lines_of(rel))


def note() -> str:
    """The PLAN note."""
    runs = ["red_tests_refusal_remedies_0_2_8255_gil0.txt", "red_tests_refusal_remedies_0_2_8255_gil1.txt",
            "preview_shard_a_gil0.txt", "preview_shard_a_gil1.txt", "preview_shard_b_gil0.txt",
            "preview_shard_b_gil1.txt", "baseline_structural_parity_gil0.txt"]
    evidence = "\n".join(
        [ev("system_docs/patches/active/direct_cleanup_refusal_2026_10_18/architecture_patch.md"),
         ev("system_docs/patches/active/direct_cleanup_refusal_2026_10_18/component_patch_spellbook_removal_path.md"),
         ev("tests/integration/melder/spellbook/"
            "test_direct_cleanup_refuses_active_member_with_parked_versions_integration.py", repo_rel=True),
         ev(LANE + "/scripts/apply_s9_refusal.py"),
         ev(LANE + "/runs/s9_refusal_preview_0_2_8255.diff")]
        + [ev(LANE + "/runs/" + name) for name in runs])
    return """- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: S9's patch, tests and exact edits for the owner's pick, ready for his word. The patch docs state the refusal
    on all three doors with its remedies. The red tests add `cleanup_spell`'s reworded message and the third remedy
    (move the parked version out, then dispose the active one) and match the new wording: on 0.2.8255, 7 failed
    and 2 passed (the sole-member controls), the same with the GIL off and on - "DID NOT RAISE" for both doors and
    the three remedies, "Regex pattern did not match" for `cleanup_spell`. The edits (apply_s9_refusal.py, E1-E7;
    the preview diff): E1 `cleanup_and_remove_spell` refuses an active member that is not its index's sole member,
    in its first Book-locked section before `unregister_index`, logging and raising "Spellbook cannot remove spell
    <id>: it is the active member of a multi-member index, and disposing it would leave the index's parked versions
    without an active one. Notch the index to one of them, dispose them with cleanup_spell, or move them out with
    remove_from_spell_index first."; E2-E4 its Contract, Raises and Threading; E5 `_dispose_spell`'s refusal
    reworded to the same tail; E6 `cleanup_spell`'s Contract; E7 `Spell.cleanup`'s Raises. Mapping, patch section
    -> step -> validation: the invariants and the component's After -> E1 -> the two door tests and probe D2-D3;
    `cleanup_spell`'s interface delta -> E5 -> its message test; the remedies -> the three remedy tests; the
    docstrings -> E2-E4, E6, E7 -> the documentation ritual. Preview in a /tmp mirror of 0.2.8255 with E1-E7
    applied: the 33 test files that call `cleanup_spell` or `cleanup_and_remove_spell` pass - 491 passed, 3 xfailed
    (open graft conflicts), 1 xpassed (an intermittent race) - with the GIL off and on, the S9 file green. The
    structural-snapshot parity tests fail when run from the repository only because their cache root sits in the
    connected folder, which refuses deletes (the same 7 on the unpatched tree); from the mirror they pass.
  EVIDENCE:
{EVIDENCE}
  IMPACT: The ENTRY_GATE is met but for the owner's word on E1-E7; nothing in src/ is written before it.
  NEXT: The exact edits to the owner; on his word, apply E1-E7 and run the tests and the probe in the repository.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
""".replace("{NOW}", NOW).replace("{EVIDENCE}", evidence)


OLD_NEXT_START = "- Next: (1) the patch docs and the red tests updated for the remedies' wording,"
NEW_NEXT = """- Next: (1) the owner's word on the exact edits E1-E7 (PLAN note of {NOW}); (2) apply them, the tests
  green with the GIL off and on in the repository, the probe re-run, docs, the release note, the next free notch
  (0.2.8256 unless it moved), closure, the rebuild last; (3) a message hands spellbook.py and spell.py back to
  melder_0.
""".replace("{NOW}", NOW)
ROW_NEXT_OLD = "Update S9's patch docs and red tests for the remedies; then the exact edits to the owner."
ROW_NEXT_NEW = "The owner's word on S9's exact edits (E1-E7); then apply, test, docs, notch and the rebuild."


def check_widths(block: str, label: str) -> None:
    """Refuse a written line over the 120-character cap (a single path token is exempt)."""
    for line in block.split("\n"):
        stripped = line.strip()
        if stripped.startswith("- ") and " " not in stripped[2:]:
            continue
        if len(line) > 120:
            raise SystemExit("%s: line over 120 chars (%d): %s" % (label, len(line), line))


def edit_story(text: str) -> str:
    """Add the PLAN note, replace Next, stamp Updated."""
    plan = note()
    check_widths(plan + NEW_NEXT, "story")
    anchor = "\n## Closure Confirmation\n"
    if text.count(anchor) != 1:
        raise SystemExit("closure anchor not found once")
    text = text.replace(anchor, "\n" + plan.rstrip("\n") + "\n\n## Closure Confirmation\n")
    end = "\n## Project-Specific Additions"
    if text.count(OLD_NEXT_START) != 1 or text.count(end) != 1:
        raise SystemExit("Next anchors not found once")
    i = text.index(OLD_NEXT_START)
    j = text.index(end)
    text = text[:i] + NEW_NEXT + text[j:]
    text, count = re.subn(r"^- Updated: \S+$", "- Updated: " + NOW, text, count=1, flags=re.M)
    if count != 1:
        raise SystemExit("no Updated line")
    return text


def edit_attention(text: str) -> str:
    """Refresh S9's row next and updated_at."""
    pattern = re.compile(r"^(\| direct_cleanup_refusal \| in_progress \| discovery \| claude \| melder_1 \| none \| )"
                         + re.escape(ROW_NEXT_OLD) + r"( \| [^\n]*?)\| (\S+) \| REQUIRED \|$", re.M)
    if len(pattern.findall(text)) != 1:
        raise SystemExit("S9 row not found once")
    return pattern.sub(lambda m: m.group(1) + ROW_NEXT_NEW + m.group(2) + "| " + NOW + " | REQUIRED |", text)


def main() -> None:
    """Re-read each file, edit it in memory, and write it only with --apply (LF kept, read back)."""
    if len(sys.argv) != 2 or sys.argv[1] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    plan = [(ROOT / STORY_REL, edit_story), (ROOT / "attention_board.md", edit_attention)]
    results = []
    for path, edit in plan:
        raw = path.read_bytes()
        if b"\r\n" in raw:
            raise SystemExit("CRLF in %s" % path.name)
        results.append((path, edit(raw.decode("utf-8"))))
    print("all anchors found; NOW =", NOW)
    if sys.argv[1] == "--apply":
        for path, text in results:
            path.write_bytes(text.encode("utf-8"))
            if path.read_bytes().decode("utf-8") != text:
                raise SystemExit("read-back mismatch in %s" % path.name)
        print("applied")


main()
