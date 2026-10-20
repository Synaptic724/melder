"""Open melder_1's lane on STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers.

Each file is re-read right before it is written and every anchor must occur exactly once:
- the story: Metadata, ENTRY_GATE, State Transition Event, Artifact Links, a DECISION note, the handoff summary;
- attention_board.md: one active row, its detail entry and the alert line for M1-30;
- artifact_board.md: one row for the lane folder;
- mailbox_board.md: NOTICE M1-30 to melder_0 and melder_1's last_checked.
Usage: open_lane.py --check | --apply
"""
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
STORY_REL = "tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md"
NOW = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def swap(text: str, old: str, new: str, label: str) -> str:
    """Replace one anchored block; the anchor must occur exactly once."""
    count = text.count(old)
    if count != 1:
        raise SystemExit("anchor %s found %d times" % (label, count))
    return text.replace(old, new)


def check_widths(block: str, label: str) -> None:
    """Refuse a written line over the 120-character hard cap."""
    for line in block.split("\n"):
        if len(line) > 120:
            raise SystemExit("%s: line over 120 chars (%d): %s" % (label, len(line), line))


NOTE = """- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner scheduled this story (chat 2026-10-18). Asked the order between
    EPIC-2026-10-18-spell_identity_is_the_code and the correctness epic's ready stories, he chose "Parallel
    (Recommended)": melder_0 keeps the identity epic; melder_1 takes S8, S3, S9, S4 and S7 one at a time and claims
    spellbook.py by mailbox for each landing; S1, S2 and S5 wait for the identity epic. Then: "you can try and take
    on melder_0s stuff that we fully confirmed but go over them again before you make changes and let him know".
    This story goes first: of the five it is the one whose question the owner answered (refuse, nothing moved). It
    is re-verified on the current tree, and its commit path re-read whole, before any change; melder_0 is told
    (M1-30). The owner also confirmed this session is the only melder_1.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:895-928
  - context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:345-355
  IMPACT: The ENTRY_GATE's scheduling and assignment are met. S3 carries an open question for the owner; S9, S4 and
    S7 carry none and no recorded confirmation, so each is re-verified, and confirmed with the owner, before it is
    taken.
  NEXT: Re-run probe N1-N3 on 0.2.8255 with the GIL off and on; re-read the notch commit path whole.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
""".replace("{NOW}", NOW)

STORY_EDITS = [
    ("metadata",
     "- Status: ready\n- Owner: user\n- Agent Name: unassigned\n- Agent Role: UNKNOWN\n- Priority: p2\n"
     "- Created: 2026-10-17T21:32:09Z\n- Updated: 2026-10-17T22:12:58Z\n",
     "- Status: in_progress\n- Owner: user\n- Agent Name: melder_1\n- Agent Role: synaptic_python_developer\n"
     "- Priority: p2\n- Created: 2026-10-17T21:32:09Z\n- Updated: " + NOW + "\n"),
    ("entry_gate",
     "- ENTRY_GATE: the owner schedules the story and assigns an agent (the open question was answered on 2026-10-17);\n"
     "  the holder of conduit.py and spellbook.py (melder_1, until its rule-2 closure) releases them or carries the fix;\n"
     "  an active board row; patch docs for the notch's commit path (architecture, component and code-description: the\n"
     "  change is in error and rollback semantics).\n",
     "- ENTRY_GATE: the owner schedules the story and assigns an agent (the open question was answered on 2026-10-17;\n"
     "  scheduled 2026-10-18, melder_1 assigned - DECISION note); conduit.py and spellbook.py are free since melder_1's\n"
     "  turn-in (M1-28) and melder_0 writes the identity epic's files, so melder_1 claims each file it edits from\n"
     "  melder_0 by message first; an active board row; patch docs for the notch's commit path (architecture,\n"
     "  component and code-description: the change is in error and rollback semantics), approved by the owner.\n"),
    ("state_transition",
     "- from_state: draft\n- to_state: ready\n- transition_reason: the defect is proven on 0.2.8252 by a probe with the"
     " GIL off and on (Notes); one open question\n  for the owner.\n",
     "- from_state: ready\n- to_state: in_progress\n- transition_reason: the owner scheduled the story and assigned"
     " melder_1 (chat 2026-10-18; DECISION note); the\n  defect is re-verified on the current tree before any change.\n"),
    ("artifact_links",
     "  - artifacts/correctness_defects_20261017/runs/probe_broken_late_bind_gil1.txt\n- DISPOSITION: retain_as_reference\n",
     "  - artifacts/correctness_defects_20261017/runs/probe_broken_late_bind_gil1.txt\n"
     "  - artifacts/failed_notch_refusal_20261018/ (melder_1's lane: re-runs, scripts, notes)\n"
     "- DISPOSITION: retain_as_reference\n"),
    ("note",
     "  SCORE_0_TO_10: 9\n\n## Closure Confirmation\n",
     "  SCORE_0_TO_10: 9\n\n" + NOTE + "\n## Closure Confirmation\n"),
    ("handoff",
     "- State: ready, unassigned; filed by melder_0 under EPIC-2026-10-17-correctness_defects; the owner answered its\n"
     "  question (refuse, nothing moved). The fix sits in conduit.py and spellbook.py, which melder_1 holds.\n"
     "- Next: (1) the owner's scheduling; (2) patch docs; (3) the fix, its tests, docs, notch and the rebuild.\n",
     "- State: in_progress (melder_1), discovery; filed by melder_0 under EPIC-2026-10-17-correctness_defects; the owner\n"
     "  answered its question (refuse, nothing moved) and scheduled it on 2026-10-18, in parallel with\n"
     "  EPIC-2026-10-18-spell_identity_is_the_code (DECISION note). The fix sits in conduit.py and spellbook.py (free;\n"
     "  melder_1 claims each from melder_0 by message before any edit; M1-30).\n"
     "- Next: (1) re-run probe N1-N3 on the current tree, GIL off and on, and re-read the notch commit path whole;\n"
     "  (2) patch docs and the owner's approval; (3) the fix, its tests, docs, notch and the rebuild last.\n"),
]

ROW = ("| failed_notch_refusal | in_progress | discovery | claude | melder_1 | none | Re-run probe N1-N3 on 0.2.8255"
       " (GIL off and on) and re-read the notch commit path whole. | A notch whose incoming version fails its commit"
       " check is refused with nothing moved; lender and borrowers stay on the outgoing version. | The fix lands with"
       " tests, docs, notch and rebuild, or the owner redirects. | " + STORY_REL + " | " + NOW + " | REQUIRED |\n")
DETAIL = ("- WORK_ITEM: failed_notch_refusal\n"
          "  SWITCH_TRIGGER: The fix lands with tests, docs, notch and rebuild, or the owner redirects.\n"
          "  RESUME_HIERARCHY:\n"
          "    - tickets/epics/2026-10-17_correctness_defects_epic.md\n"
          "    - " + STORY_REL + "\n")
ALERT = "- NEW MESSAGE for melder_0 (from melder_1, " + NOW + ")\n"
ARTIFACT_ROW = ("| " + STORY_REL + " | artifacts/failed_notch_refusal_20261018/ | investigation_evidence | active |"
                " retain_as_reference | melder_1's lane: the re-runs of probe N1-N3 on the current tree, the scripts"
                " and notes drafts; the fix's red/green runs and rebuild logs land here. | " + NOW + " | HELPFUL |\n")
MESSAGE = """- TO: melder_0
  FROM: melder_1
  DATETIME: {NOW}
  TYPE: NOTICE
  CLAIM: M1-30. The owner's order (chat 2026-10-18): parallel - you keep EPIC-2026-10-18-spell_identity_is_the_code;
    melder_1 takes correctness stories one at a time, only those the owner fully confirmed, each re-verified on the
    current tree before any change. Now: S8 failed_notch_keeps_switch_without_borrowers (assigned, in_progress,
    board row); S1, S2 and S5 wait for your epic. melder_1 holds no file and claims conduit.py, spellbook.py or the
    change-control files from you by message before editing; tell me if your S1/S2 needs any of them soon.
  EVIDENCE: context_compass/tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md
  ACK_REQUESTED: true
""".replace("{NOW}", NOW)


def edit_story(text: str) -> str:
    """Apply the story's anchored edits."""
    for label, old, new in STORY_EDITS:
        check_widths(new, "story:" + label)
        text = swap(text, old, new, "story:" + label)
    return text


def edit_attention(text: str) -> str:
    """Add the row, its detail entry and the M1-30 alert inside their USER-DEFINED regions."""
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
    """Append M1-30 and refresh melder_1's last_checked."""
    check_widths(MESSAGE, "message")
    if "M1-30." in text:
        raise SystemExit("M1-30 already present")
    text = swap(text, "<!-- END USER-DEFINED: messages -->\n", MESSAGE + "<!-- END USER-DEFINED: messages -->\n",
                "messages_end")
    row = re.search(r"\| melder_1 \| claude \| 2026-09-26T17:46:30Z \| ([0-9TZ:-]+) \| active \|", text)
    if row is None or text.count(row.group(0)) != 1:
        raise SystemExit("melder_1 roster row not unique")
    return text.replace(row.group(0), "| melder_1 | claude | 2026-09-26T17:46:30Z | " + NOW + " | active |")


def main() -> None:
    """Re-read each file, edit it, and write it back only with --apply."""
    apply = sys.argv[1:] == ["--apply"]
    if sys.argv[1:] not in (["--apply"], ["--check"]):
        raise SystemExit(__doc__)
    plan = [(STORY_REL, edit_story), ("attention_board.md", edit_attention),
            ("artifact_board.md", edit_artifacts), ("mailbox_board.md", edit_mailbox)]
    for rel, editor in plan:
        path = ROOT / rel
        raw = path.read_bytes()
        if b"\r\n" in raw:
            raise SystemExit(rel + ": CRLF found; this script writes LF files only")
        text = raw.decode("utf-8")
        new = editor(text)
        print("%s: %d -> %d lines" % (rel, text.count("\n"), new.count("\n")))
        if apply:
            path.write_bytes(new.encode("utf-8"))
            if path.read_bytes().decode("utf-8") != new:
                raise SystemExit(rel + ": read-back mismatch")
    print("NOW", NOW, "applied" if apply else "checked")


main()
