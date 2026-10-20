"""Open melder_1's lane on STORY-2026-10-17-direct_cleanup_of_active_member_orphans_parked_versions (S9), and park
S8's board row as blocked on the owner's hold.

Each file is re-read right before it is written and every anchor must occur exactly once:
- the S9 story: Metadata, ENTRY_GATE, DEPENDENCIES, State Transition Event, Artifact Links, a DECISION note, the
  handoff summary;
- attention_board.md: S8's row blocked; S9's row, its detail entry and the alert line for M1-33;
- artifact_board.md: one row for the lane folder;
- mailbox_board.md: NOTICE M1-33 to melder_0 and melder_1's last_checked.
Usage: open_lane.py --check | --apply
"""
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
STORY_REL = "tickets/stories/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md"
S8_REL = "tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md"
NOW = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def swap(text: str, old: str, new: str, label: str) -> str:
    """Replace one anchored block; the anchor must occur exactly once."""
    count = text.count(old)
    if count != 1:
        raise SystemExit("anchor %s found %d times" % (label, count))
    return text.replace(old, new)


def check_widths(block: str, label: str) -> None:
    """Refuse a written line over the 120-character hard cap (a single path token is exempt)."""
    for line in block.split("\n"):
        stripped = line.strip()
        if stripped.startswith("- ") and " " not in stripped[2:]:
            continue
        if len(line) > 120:
            raise SystemExit("%s: line over 120 chars (%d): %s" % (label, len(line), line))


NOTE = """- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner scheduled this story for melder_1 (chat 2026-10-18). His order is parallel: melder_0 keeps
    EPIC-2026-10-18-spell_identity_is_the_code, melder_1 takes the correctness fixes one at a time; of the stories
    after S8 he said "do the ones without open questions please" - S9, S4 and S7 - with "go over them again before
    you make changes and let him know". S8 is on hold by his word (its DECISION note), so S9 goes next, in his
    original order with S3 (open question) skipped. The defect is re-verified on 0.2.8255 and its code path re-read
    whole before any change; the exact edits go to the owner before the first one; melder_0 is told (M1-33).
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:904-919
  - context_compass/tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md:435-450
  IMPACT: The ENTRY_GATE's scheduling and assignment are met; the patch, the owner's word on the edits and the file
    claim remain before any src edit.
  NEXT: Re-run probe D1-D3 on 0.2.8255 with the GIL off and on; re-read the removal path whole.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
""".replace("{NOW}", NOW)

STORY_EDITS = [
    ("metadata",
     "- Status: ready\n- Owner: user\n- Agent Name: unassigned\n- Agent Role: UNKNOWN\n- Priority: p2\n"
     "- Created: 2026-10-17T21:38:03Z\n- Updated: 2026-10-17T21:38:03Z\n",
     "- Status: in_progress\n- Owner: user\n- Agent Name: melder_1\n- Agent Role: synaptic_python_developer\n"
     "- Priority: p2\n- Created: 2026-10-17T21:38:03Z\n- Updated: " + NOW + "\n"),
    ("entry_gate",
     "- ENTRY_GATE: the owner schedules the story and assigns an agent; melder_1 has released spellbook.py (its rule-2\n"
     "  hold); an active board row; a component patch for the Spellbook's removal path.\n",
     "- ENTRY_GATE: the owner schedules the story and assigns an agent (2026-10-18: melder_1 - DECISION note);\n"
     "  spellbook.py claimed from melder_0 by message before any edit (M1-33); an active board row; a component patch\n"
     "  for the Spellbook's removal path, and the owner's word on the exact edits before the first one.\n"),
    ("dependencies",
     "  its own route); melder_1's release of spellbook.py.\n",
     "  its own route); spellbook.py, released by melder_1 (M1-28) and claimed back from melder_0 for this fix (M1-33).\n"),
    ("state_transition",
     "- from_state: draft\n- to_state: ready\n- transition_reason: the defect is proven on 0.2.8252 by a probe with the"
     " GIL off and on (Notes).\n",
     "- from_state: ready\n- to_state: in_progress\n- transition_reason: the owner scheduled the story for melder_1"
     " (chat 2026-10-18; DECISION note); the\n  defect is re-verified on the current tree before any change.\n"),
    ("artifact_links",
     "  - artifacts/correctness_defects_20261017/runs/probe_direct_cleanup_active_member_gil1.txt\n"
     "- DISPOSITION: retain_as_reference\n",
     "  - artifacts/correctness_defects_20261017/runs/probe_direct_cleanup_active_member_gil1.txt\n"
     "  - artifacts/direct_cleanup_refusal_20261018/ (melder_1's lane: re-runs, scripts, notes)\n"
     "- DISPOSITION: retain_as_reference\n"),
    ("note",
     "  SCORE_0_TO_10: 9\n\n## Closure Confirmation\n",
     "  SCORE_0_TO_10: 9\n\n" + NOTE + "\n## Closure Confirmation\n"),
    ("handoff",
     "- State: ready, unassigned; filed by melder_0 under EPIC-2026-10-17-correctness_defects. The fix sits in\n"
     "  spellbook.py, which melder_1 holds.\n"
     "- Next: (1) the owner's scheduling; (2) patch docs; (3) the fix, its tests, docs, notch and the rebuild.\n",
     "- State: in_progress (melder_1), discovery; filed by melder_0 under EPIC-2026-10-17-correctness_defects; the owner\n"
     "  scheduled it on 2026-10-18 (DECISION note). The fix sits in spellbook.py, released to melder_1 (M0-194) and\n"
     "  claimed for this fix (M1-33).\n"
     "- Next: (1) re-run probe D1-D3 on the current tree, GIL off and on, and re-read the removal path whole;\n"
     "  (2) the patch and the owner's word on the exact edits; (3) the fix, its tests, docs, notch and the rebuild\n"
     "  last.\n"),
]

S8_ROW_PREFIX = "| failed_notch_refusal | in_progress | implementation | claude | melder_1 | none | "
S8_ROW = ("| failed_notch_refusal | blocked | handoff | claude | melder_1 | the owner's hold (chat 2026-10-18) |"
          " The owner's word to resume S8 (the edit list and its refinement). | A notch whose incoming version fails"
          " its commit check is refused with nothing moved; lender and borrowers stay on the outgoing version. |"
          " The fix lands with tests, docs, notch and rebuild, or the owner redirects. | " + S8_REL + " | " + NOW
          + " | REQUIRED |")
ROW = ("| direct_cleanup_refusal | in_progress | discovery | claude | melder_1 | none | Re-run probe D1-D3 on 0.2.8255"
       " (GIL off and on) and re-read the removal path whole. | A direct cleanup of an index's active member that has"
       " parked versions is refused with nothing changed, as cleanup_spell refuses it. | The fix lands with tests,"
       " docs, notch and rebuild, or the owner redirects. | " + STORY_REL + " | " + NOW + " | REQUIRED |\n")
DETAIL = ("- WORK_ITEM: direct_cleanup_refusal\n"
          "  SWITCH_TRIGGER: The fix lands with tests, docs, notch and rebuild, or the owner redirects.\n"
          "  RESUME_HIERARCHY:\n"
          "    - tickets/epics/2026-10-17_correctness_defects_epic.md\n"
          "    - " + STORY_REL + "\n")
ALERT = "- NEW MESSAGE for melder_0 (from melder_1, " + NOW + ")\n"
ARTIFACT_ROW = ("| " + STORY_REL + " | artifacts/direct_cleanup_refusal_20261018/ | investigation_evidence | active |"
                " retain_as_reference | melder_1's lane: the re-runs of probe D1-D3 on the current tree, the scripts"
                " and notes drafts; the fix's red/green runs and rebuild logs land here. | " + NOW + " | HELPFUL |\n")
MESSAGE = """- TO: melder_0
  FROM: melder_1
  DATETIME: {NOW}
  TYPE: NOTICE
  CLAIM: M1-33. The owner put S8 on hold (no src edit was made): conduit.py, spellbook_validation_error.py and
    change_control_manager.py, released for S8 (M0-194), are free for you while it waits; I claim them again before
    S8 resumes. Next for melder_1, on the owner's word: S9 direct_cleanup_of_active_member_orphans_parked_versions.
    I keep spellbook.py for it (`cleanup_and_remove_spell` and its docstring) until it lands; no edit before the
    owner's word on the exact edits. Claim it back by message if your S1 needs it first.
  EVIDENCE: context_compass/tickets/stories/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md
  ACK_REQUESTED: false
""".replace("{NOW}", NOW)


def edit_story(text: str) -> str:
    """Apply the story's anchored edits."""
    for label, old, new in STORY_EDITS:
        check_widths(new, "story:" + label)
        text = swap(text, old, new, "story:" + label)
    return text


def edit_attention(text: str) -> str:
    """Block S8's row; add S9's row, its detail entry and the M1-33 alert inside their USER-DEFINED regions."""
    lines = text.split("\n")
    hits = [i for i, line in enumerate(lines) if line.startswith(S8_ROW_PREFIX)]
    if len(hits) != 1:
        raise SystemExit("S8 row found %d times" % len(hits))
    lines[hits[0]] = S8_ROW
    text = "\n".join(lines)
    check_widths(DETAIL, "detail")
    text = swap(text, "<!-- END USER-DEFINED: active_items -->\n", ROW + "<!-- END USER-DEFINED: active_items -->\n",
                "active_items_end")
    text = swap(text, "<!-- END USER-DEFINED: active_attention_details -->\n",
                DETAIL + "<!-- END USER-DEFINED: active_attention_details -->\n", "details_end")
    return swap(text, "<!-- END USER-DEFINED: alerts -->\n", ALERT + "<!-- END USER-DEFINED: alerts -->\n",
                "alerts_end")


def edit_artifacts(text: str) -> str:
    """Add the lane folder's row at the end of the active_artifacts region."""
    return swap(text, "<!-- END USER-DEFINED: active_artifacts -->\n",
                ARTIFACT_ROW + "<!-- END USER-DEFINED: active_artifacts -->\n", "active_artifacts_end")


def edit_mailbox(text: str) -> str:
    """Append M1-33 and refresh melder_1's last_checked."""
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
        (ROOT / "attention_board.md", edit_attention),
        (ROOT / "artifact_board.md", edit_artifacts),
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
