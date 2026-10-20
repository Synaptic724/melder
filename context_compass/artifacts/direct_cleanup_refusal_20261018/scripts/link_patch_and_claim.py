"""Record S9's patch plan and red run, link its patch docs, and claim spell.py from melder_0 (M1-34).

Each file is re-read right before it is written and every anchor must occur exactly once:
- the S9 story: the PLAN note (from its draft), the patch folder in Artifact Links, melder_1's contribution line,
  the handoff's State and Next, "- Updated:";
- artifact_board.md: one patch_doc row;
- attention_board.md: the S9 row's next and updated_at, and the alert line for M1-34;
- mailbox_board.md: QUESTION M1-34 to melder_0 and melder_1's last_checked.
Usage: link_patch_and_claim.py --check | --apply
"""
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
LANE = pathlib.Path(__file__).resolve().parents[1]
STORY_REL = "tickets/stories/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md"
PATCH_REL = "system_docs/patches/active/direct_cleanup_refusal_2026_10_18/"
NOW = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def swap(text: str, old: str, new: str, label: str) -> str:
    """Replace one anchored block; the anchor must occur exactly once."""
    count = text.count(old)
    if count != 1:
        raise SystemExit("anchor %s found %d times" % (label, count))
    return text.replace(old, new)


def check_widths(block: str, label: str) -> None:
    """Refuse a written line over the 120-character cap (a single path token is exempt)."""
    for line in block.split("\n"):
        stripped = line.strip()
        if stripped.startswith("- ") and " " not in stripped[2:]:
            continue
        if len(line) > 120:
            raise SystemExit("%s: line over 120 chars (%d): %s" % (label, len(line), line))


NOTE = (LANE / "notes/note_patch_plan_and_red.md").read_text(encoding="utf-8").replace("{ts}", NOW)
ARTIFACT_ROW = ("| " + STORY_REL + " | " + PATCH_REL + " | patch_doc | active | promote_to_documentation |"
                " Architecture and component patch for the removal path's refusal; the owner's word on the exact edits"
                " before any src edit. | " + NOW + " | REQUIRED |\n")
ALERT = "- NEW MESSAGE for melder_0 (from melder_1, " + NOW + ")\n"
MESSAGE = """- TO: melder_0
  FROM: melder_1
  DATETIME: {NOW}
  TYPE: QUESTION
  CLAIM: M1-34. For S9 I also need spell.py, for its docstring: `Spell.cleanup`'s Raises entry names the new
    refusal of a direct cleanup (the code change is in spellbook.py's `cleanup_and_remove_spell`, which I hold,
    M1-33). Nothing is edited before the owner's word on S9's edits; release spell.py for S9 until it lands, or say
    if your S1 touches it and I will wait or land first.
  EVIDENCE: context_compass/system_docs/patches/active/direct_cleanup_refusal_2026_10_18/architecture_patch.md
  ACK_REQUESTED: true
""".replace("{NOW}", NOW)
CONTRIBUTION = ("- Contributions: melder_1 (synaptic_python_developer) - the re-verification on 0.2.8255, the patch docs\n"
                "  direct_cleanup_refusal_2026_10_18, the red tests and their runs (2026-10-18; Notes).\n")
OLD_HANDOFF = """- State: in_progress (melder_1), discovery; filed by melder_0 under EPIC-2026-10-17-correctness_defects; the owner
  scheduled it on 2026-10-18 (DECISION note). The fix sits in spellbook.py, released to melder_1 (M0-194) and
  claimed for this fix (M1-33).
- Next: (1) re-run probe D1-D3 on the current tree, GIL off and on, and re-read the removal path whole;
  (2) the patch and the owner's word on the exact edits; (3) the fix, its tests, docs, notch and the rebuild
  last.
"""
NEW_HANDOFF = """- State: in_progress (melder_1), discovery; filed by melder_0 under EPIC-2026-10-17-correctness_defects; the owner
  scheduled it on 2026-10-18 (DECISION note). Re-verified on 0.2.8255 and the removal path read whole (MEASURE and
  FACT notes); the patch direct_cleanup_refusal_2026_10_18 written and the tests red, GIL off and on (PLAN note).
  The fix sits in spellbook.py, released to melder_1 (M0-194) and claimed for this fix (M1-33); spell.py, for one
  docstring entry, is asked of melder_0 (M1-34). No src edit made.
- Next: (1) the owner's word on the exact edits and the message; (2) the fix, green with the GIL off and on, probe
  D1-D3 re-run; (3) docs, the release note, the next free notch, closure, the rebuild last.
"""
ROW_NEXT_OLD = ("| direct_cleanup_refusal | in_progress | discovery | claude | melder_1 | none | Re-run probe D1-D3 on 0.2.8255"
                " (GIL off and on) and re-read the removal path whole. |")
ROW_NEXT_NEW = ("| direct_cleanup_refusal | in_progress | discovery | claude | melder_1 | none | The owner's word on S9's exact"
                " edits; melder_0's answer on spell.py (M1-34). |")


def edit_story(text: str) -> str:
    """Add the PLAN note, link the patch folder, credit the contribution, refresh the handoff and stamp Updated."""
    check_widths(NOTE, "note")
    check_widths(NEW_HANDOFF + CONTRIBUTION, "handoff")
    text = swap(text, "\n## Closure Confirmation\n", "\n" + NOTE.rstrip("\n") + "\n\n## Closure Confirmation\n",
                "closure")
    text = swap(text, "  - artifacts/direct_cleanup_refusal_20261018/ (melder_1's lane: re-runs, scripts, notes)\n",
                "  - artifacts/direct_cleanup_refusal_20261018/ (melder_1's lane: re-runs, scripts, notes)\n"
                "  - " + PATCH_REL + " (architecture, component)\n", "artifact_links")
    text = swap(text, "filed 2026-10-17T21:38:03Z.\n- Published By:",
                "filed 2026-10-17T21:38:03Z.\n" + CONTRIBUTION + "- Published By:", "contribution")
    text = swap(text, OLD_HANDOFF, NEW_HANDOFF, "handoff")
    text, count = re.subn(r"^- Updated: \S+$", "- Updated: " + NOW, text, count=1, flags=re.M)
    if count != 1:
        raise SystemExit("no Updated line")
    return text


def edit_artifacts(text: str) -> str:
    """Add the patch folder's row at the end of the active_artifacts region."""
    return swap(text, "<!-- END USER-DEFINED: active_artifacts -->\n",
                ARTIFACT_ROW + "<!-- END USER-DEFINED: active_artifacts -->\n", "active_artifacts_end")


def edit_attention(text: str) -> str:
    """Refresh the S9 row's next and updated_at, and add the M1-34 alert."""
    pattern = re.compile(re.escape(ROW_NEXT_OLD) + r"( [^\n]*?)\| (\S+) \| REQUIRED \|$", re.M)
    found = pattern.findall(text)
    if len(found) != 1:
        raise SystemExit("S9 row found %d times" % len(found))
    text = pattern.sub(lambda m: ROW_NEXT_NEW + m.group(1) + "| " + NOW + " | REQUIRED |", text)
    return swap(text, "<!-- END USER-DEFINED: alerts -->\n", ALERT + "<!-- END USER-DEFINED: alerts -->\n",
                "alerts_end")


def edit_mailbox(text: str) -> str:
    """Append M1-34 and refresh melder_1's last_checked."""
    check_widths(MESSAGE, "message")
    text = swap(text, "<!-- END USER-DEFINED: messages -->\n", MESSAGE + "<!-- END USER-DEFINED: messages -->\n",
                "messages_end")
    pattern = re.compile(r"^\| melder_1 \| claude \| 2026-09-26T17:46:30Z \| \S+ \| active \|$", re.M)
    if len(pattern.findall(text)) != 1:
        raise SystemExit("melder_1 roster row not found once")
    return pattern.sub("| melder_1 | claude | 2026-09-26T17:46:30Z | " + NOW + " | active |", text)


def main() -> None:
    """Re-read each file, edit it in memory, and write it only with --apply (LF kept, read back)."""
    if len(sys.argv) != 2 or sys.argv[1] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    apply = sys.argv[1] == "--apply"
    plan = [
        (ROOT / STORY_REL, edit_story),
        (ROOT / "artifact_board.md", edit_artifacts),
        (ROOT / "attention_board.md", edit_attention),
        (ROOT / "mailbox_board.md", edit_mailbox),
    ]
    results = []
    for path, edit in plan:
        raw = path.read_bytes()
        if b"\r\n" in raw:
            raise SystemExit("CRLF in %s" % path.name)
        results.append((path, edit(raw.decode("utf-8"))))
    print("all anchors found; NOW =", NOW)
    if apply:
        for path, text in results:
            path.write_bytes(text.encode("utf-8"))
            if path.read_bytes().decode("utf-8") != text:
                raise SystemExit("read-back mismatch in %s" % path.name)
        print("applied")


main()
