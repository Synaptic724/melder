"""Open melder_1's lane on STORY-2026-10-17-minted_index_missing_from_frame_registry (S4).

Each file is re-read right before it is written and every anchor must occur exactly once:
- the S4 story: Metadata, ENTRY_GATE, DEPENDENCIES, State Transition Event, Artifact Links, a DECISION note, the
  handoff summary;
- attention_board.md: S4's row and its detail entry;
- artifact_board.md: one row for the lane folder;
- mailbox_board.md: melder_1's last_checked (messages read at lane open; none addressed to melder_1 is required).
Usage: open_lane.py --check | --apply
"""
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
STORY_REL = "tickets/stories/2026-10-17_minted_index_missing_from_frame_registry_story.md"
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
  CLAIM: The owner's order puts this story with melder_1 after S9 (chat 2026-10-18): parallel - melder_0 keeps
    EPIC-2026-10-18-spell_identity_is_the_code, melder_1 takes the correctness fixes one at a time; of the stories
    after S8 he said "do the ones without open questions please" - S9, S4 and S7 - with "go over them again before
    you make changes and let him know". S8 is on hold and S9 landed at 0.2.8256, so S4 is next. The defect is
    re-verified on 0.2.8256 and its code path re-read whole before any change; the exact edits go to the owner
    before the first one; melder_0 was told (M1-38). The fix sits in spellbook.py, which melder_0 holds for S1 and
    S2 until they land, so it is claimed back by message before any edit.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:915-930
  - context_compass/tickets/stories/completed/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md:198-215
  - context_compass/tickets/stories/completed/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md:777-803
  IMPACT: The ENTRY_GATE's scheduling and assignment are met; the patch, the owner's word on the edits and the file
    claim remain before any src edit.
  NEXT: Re-run probe M1-M3 and V1-V4 on 0.2.8256 with the GIL off and on; re-read the minting seam and the frame
    registry whole.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
""".replace("{NOW}", NOW)

STORY_EDITS = [
    ("metadata",
     "- Status: ready\n- Owner: user\n- Agent Name: unassigned\n- Agent Role: UNKNOWN\n- Priority: p2\n"
     "- Created: 2026-10-17T20:32:42Z\n- Updated: 2026-10-17T21:16:35Z\n",
     "- Status: in_progress\n- Owner: user\n- Agent Name: melder_1\n- Agent Role: synaptic_python_developer\n"
     "- Priority: p2\n- Created: 2026-10-17T20:32:42Z\n- Updated: " + NOW + "\n"),
    ("entry_gate",
     "- ENTRY_GATE: the owner schedules the story and assigns an agent; spellbook.py's (and, if the fix goes there,\n"
     "  conduit.py's) holder releases it or carries the fix - melder_1, whose spell_id lookup fix meets this; an active\n"
     "  board row; a component patch for the seam.\n",
     "- ENTRY_GATE: the owner schedules the story and assigns an agent (2026-10-18: melder_1 - DECISION note);\n"
     "  spellbook.py (and conduit.py if the fix goes there) claimed from melder_0 by message before any edit - melder_0\n"
     "  holds spellbook.py for S1 and S2 of EPIC-2026-10-18-spell_identity_is_the_code (M1-38); an active board row; a\n"
     "  component patch for the seam, and the owner's word on the exact edits before the first one.\n"),
    ("dependencies",
     "  TASK-2026-10-16-recheck_contract_consumers_when_provider_changes (melder_1's spell_id lookup fix: the frame step\n"
     "  this story repairs comes before the Book step that fix changes).\n",
     "  TASK-2026-10-16-recheck_contract_consumers_when_provider_changes (melder_1's spell_id lookup fix, landed at\n"
     "  0.2.8253: the frame step this story repairs comes before the Book step that fix changed); S1 and S2 of\n"
     "  EPIC-2026-10-18-spell_identity_is_the_code, whose landing holds spellbook.py (M1-38).\n"),
    ("state_transition",
     "- from_state: draft\n- to_state: ready\n- transition_reason: the defect is proven on 0.2.8251 by a probe in fresh"
     " worlds, GIL off and on (Notes).\n",
     "- from_state: ready\n- to_state: in_progress\n- transition_reason: the owner scheduled the story for melder_1"
     " (chat 2026-10-18; DECISION note); the defect\n  is re-verified on the current tree before any change.\n"),
    ("artifact_links",
     "  - artifacts/correctness_defects_20261017/runs/probe_research_residency_moves_gil1.txt\n"
     "- DISPOSITION: retain_as_reference\n",
     "  - artifacts/correctness_defects_20261017/runs/probe_research_residency_moves_gil1.txt\n"
     "  - artifacts/minted_index_registry_20261018/ (melder_1's lane: re-runs, scripts, notes)\n"
     "- DISPOSITION: retain_as_reference\n"),
    ("note",
     "\n## Closure Confirmation\n",
     "\n" + NOTE + "\n## Closure Confirmation\n"),
    ("handoff",
     "- State: ready, unassigned; filed by melder_0 under EPIC-2026-10-17-correctness_defects. The fix sits in\n"
     "  spellbook.py (or conduit.py), which melder_1 holds; melder_1 is told by mailbox.\n"
     "- Next: (1) the owner schedules it; (2) patch docs; (3) the fix, its tests, docs, notch and the rebuild.\n",
     "- State: in_progress (melder_1), discovery; filed by melder_0 under EPIC-2026-10-17-correctness_defects; the owner\n"
     "  scheduled it on 2026-10-18 (DECISION note). The fix sits in spellbook.py (or conduit.py); melder_0 holds\n"
     "  spellbook.py for S1 and S2 of EPIC-2026-10-18-spell_identity_is_the_code (M1-38), so the code waits for its\n"
     "  hand-back.\n"
     "- Next: (1) re-run probe M1-M3 and V1-V4 on the current tree, GIL off and on, and re-read the minting seam and\n"
     "  the frame registry whole; (2) the patch and the owner's word on the exact edits; (3) the fix once spellbook.py\n"
     "  is back, its tests, docs, notch and the rebuild last.\n"),
]

ROW = ("| minted_index_registry | in_progress | discovery | claude | melder_1 | none | Re-run probe M1-M3 and V1-V4 on"
       " 0.2.8256 (GIL off and on); re-read the minting seam and the frame registry whole. | The index"
       " remove_from_spell_index mints is in the frame's spell registry, so its version is found and granted by"
       " spell_id. | The fix lands with tests, docs, notch and rebuild, or the owner redirects. | " + STORY_REL + " | "
       + NOW + " | REQUIRED |\n")
DETAIL = ("- WORK_ITEM: minted_index_registry\n"
          "  SWITCH_TRIGGER: The fix lands with tests, docs, notch and rebuild, or the owner redirects.\n"
          "  RESUME_HIERARCHY:\n"
          "    - tickets/epics/2026-10-17_correctness_defects_epic.md\n"
          "    - " + STORY_REL + "\n")
ARTIFACT_ROW = ("| " + STORY_REL + " | artifacts/minted_index_registry_20261018/ | investigation_evidence | active |"
                " retain_as_reference | melder_1's lane: the re-runs of probe M1-M3 and V1-V4 on the current tree, the"
                " scripts and notes drafts; the fix's red/green runs and rebuild logs land here. | " + NOW
                + " | HELPFUL |\n")


def edit_story(text: str) -> str:
    """Apply the story's anchored edits."""
    for label, old, new in STORY_EDITS:
        check_widths(new, "story:" + label)
        text = swap(text, old, new, "story:" + label)
    return text


def edit_attention(text: str) -> str:
    """Add S4's row and its detail entry inside their USER-DEFINED regions."""
    check_widths(DETAIL, "detail")
    text = swap(text, "<!-- END USER-DEFINED: active_items -->\n", ROW + "<!-- END USER-DEFINED: active_items -->\n",
                "active_items_end")
    return swap(text, "<!-- END USER-DEFINED: active_attention_details -->\n",
                DETAIL + "<!-- END USER-DEFINED: active_attention_details -->\n", "details_end")


def edit_artifacts(text: str) -> str:
    """Add the lane folder's row at the end of the active_artifacts region."""
    return swap(text, "<!-- END USER-DEFINED: active_artifacts -->\n",
                ARTIFACT_ROW + "<!-- END USER-DEFINED: active_artifacts -->\n", "active_artifacts_end")


def edit_mailbox(text: str) -> str:
    """Refuse when a message waits for melder_1; refresh melder_1's last_checked."""
    if re.search(r"^- TO: melder_1$", text, re.M):
        raise SystemExit("a message for melder_1 waits: consume it first")
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
