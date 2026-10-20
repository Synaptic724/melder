"""Turn S1 in (melder_1; STORY-2026-10-17-staged_version_releases_active_signature, landed at 0.2.8263).

The story gains its MEASURE and FACT notes, the completion summary and done state, then moves to completed/ (mv -n,
run by the caller after --apply); the attention board drops the lane row and its detail, adds the closed anchor
(the oldest dropped, cap 12) and refreshes the epic row; the artifact board moves the story's rows to cleared; the
epic ticks S1 and refreshes its resume view. The rebuild follows as the pass's last write.
Usage (context_compass root): close_s1.py --check|--apply
"""
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
NOW = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
OPENED = "2026-10-19T13:40:29Z"
STORY = ROOT / "tickets/stories/2026-10-17_staged_version_releases_active_signature_story.md"
TICKET = "tickets/stories/2026-10-17_staged_version_releases_active_signature_story.md"
DONE = "tickets/stories/completed/2026-10-17_staged_version_releases_active_signature_story.md"
EPIC = ROOT / "tickets/epics/2026-10-17_correctness_defects_epic.md"
BOARD = ROOT / "attention_board.md"
ARTS = ROOT / "artifact_board.md"
RUNS = "context_compass/artifacts/staged_signature_claims_20261019/runs/"

SUMMARY = f"""
- Completed: {NOW}
- Summary: landed and notched 0.2.8263 - staging a version keyed like the active one, an index move back and a
  lone parked `cleanup_spell` keep every other spell's binding signature: `Spellbook._destroy_spell_index` drops
  the Book route only when it routes the key to the destroyed index and releases only the departing member's frame
  claim, by spell_id. Six component tests (five red on 0.2.8262) green with the GIL off and on, the whole tree as
  the MEASURE note records; release-note section "Staging a version keeps the active version's name"; system
  documents and graph; the rebuild comes last in this pass. Turned in on the owner's word (chat 2026-10-19: "Yes
  do your fix", "But finish asap").
"""
MEASURE = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Re-verified, fixed and proven. On 0.2.8262 the claims cases, rewritten for the current names, reproduce
    every one with the GIL off and on: after `bind_inactive` (after and before conjure), an index move back and a
    lone parked `cleanup_spell` the active English holds no frame claim and no Book route, a meld by address raises
    KeyError, `find_spell_index` raises and another Book's bind of the signature is accepted; Book L's staging
    releases Book O's claim (C6). The six component tests are red on 0.2.8262 (5 failed, 1 passed, both modes). The
    fix (patch staged_signature_claims_2026_10_19): `_destroy_spell_index` takes the departing member's spell_id,
    pops `_lookup_spells[key]` only when it is the destroyed index and calls `release_lookup_by_spell_id` instead of
    `release_lookup`; `_apply_add_to_index` and `_dispose_spell` pass it. At the fix: 6 passed with the GIL off and
    on; the cases keep English's claim, route and address melds and refuse the other Book's bind; the release-note
    example runs OK in both modes and raises KeyError on 0.2.8262. Whole tree on 0.2.8263, both modes: unit
    4553 + 2899 + 610 + 537 passed and 1102 passed with one expected failure (assets stamped 0.2.8260 until the
    rebuild); component 2412 passed, 23 skipped, 1 xfailed; integration 846 + 1031 (3 xpassed: a non-strict race
    marker) + 398 passed; experimentation 250 passed. One gil1 failure in the spellbook unit shard was the two
    modes racing on one conjure-cache file in the shared tree (run concurrently); its file re-run alone passes.
    Not run: melder_0's restore (R1) and graft (G4) probes at the fix - both stage through `bind_inactive`, the
    path the tests cover.
  EVIDENCE:
  - context_compass/artifacts/staged_signature_claims_20261019/probes/probe_claims_current.py:1-224
  - {RUNS}probe_claims_0_2_8262_gil0.txt:1-26
  - {RUNS}probe_claims_fix_0_2_8263_gil0.txt:1-26
  - {RUNS}s1_red_0_2_8262_gil0.txt:1-12
  - {RUNS}s1_green_gil0.txt:1-2
  - src/melder/aether/spellbook/spellbook.py:4655-4732
  - src/melder/aether/spellbook/spellbook.py:4558-4653
  - src/melder/aether/spellbook/spellbook.py:4964-5132
  - tests/component/melder/spellbook/test_spellbook_component_staged_version_keeps_active_signature.py:1-380
  - {RUNS}release_note_probe_s1_gil0.txt:1-1
  - {RUNS}release_note_probe_s1_on_0_2_8262_gil0.txt:1-2
  IMPACT: Every acceptance criterion holds on the tree: the active version keeps its claim and route through
    staging, a move back and a lone parked disposal, and another Book's claim survives a staging under its key.
  NEXT: The FACT note on the landing; then the turn-in and the rebuild last.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""
FACT = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Landed and turned in at 0.2.8263 (`__version__` read 0.2.8262). The patch (architecture and Spellbook
    component docs) was written and linked before the src edit and is archived with the completed patches. The four
    system documents carry it - src_architecture an operational invariant, a fixed failure mode, the spellbook.py
    code map (8378 lines) and a handoff entry; src_components Spellbook Core's invariant and failure, the code map
    and a handoff entry; tests_components the cluster's key file, a code-map record and the counts (component 169
    of 171, 861 test modules, core union 279); tests_architecture the inventory - with their indexes regenerated
    and checked OK, and eight numeric citations into spellbook.py remapped line by line (the citation check finds
    only its two pre-existing misses). The graph: Spellbook gains a responsibility and is accepted after reading;
    re-extracted after the notch and reassembled (593 sections, check OK). The running release note gains "Staging
    a version keeps the active version's name" and a packaging bullet; the attention board a notch notice.
  EVIDENCE:
  - {RUNS}land_s1_docs_apply.txt:1-6
  - {RUNS}remap_s1_citations_apply.txt:1-40
  - {RUNS}index_check_src_architecture.txt:1-1
  - {RUNS}citation_bounds_s1.txt:1-2
  - {RUNS}graph_accept_0_2_8263.txt:1-5
  - {RUNS}graph_assemble_check_after_notch_0_2_8263.txt:1-3
  - {RUNS}notch_0_2_8263.txt:1-2
  - release_docs/next_version_release.md:1-1
  IMPACT: S1 is done; the rebuild (assets and bundles for 0.2.8263) is the pass's last write.
  NEXT: none for S1; S2 and S5 on the owner's word.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
"""
STORY_EDITS = (
    ("- Status: in_progress\n", "- Status: done\n"),
    ("- Updated: %s\n" % OPENED, "- Updated: %s\n" % NOW),
    ("- from_state: ready\n- to_state: in_progress\n"
     "- transition_reason: the owner scheduled the story for melder_1 (M1-45; chat 2026-10-19: \"try doing a few\n"
     "  small ones\"; DECISION note); the defect is re-verified on the current tree before any change.\n",
     "- from_state: in_progress\n- to_state: done\n"
     "- transition_reason: landed at 0.2.8263 and turned in on the owner's word (chat 2026-10-19: \"Yes do your fix\",\n"
     "  \"But finish asap\"; MEASURE and FACT notes). Before that, ready -> in_progress on his order (DECISION note).\n"),
    ("- [ ] Task: patch docs for the seam; the owner's approval.\n",
     "- [x] Task: patch docs for the seam (staged_signature_claims_2026_10_19); the owner's go (chat 2026-10-19:\n"
     "  \"Yes do your fix\").\n"),
    ("- [ ] Task: the fix with symptom-named regression tests, docs, notch and the rebuild last.\n",
     "- [x] Task: the fix with symptom-named regression tests (red on 0.2.8262, green at 0.2.8263), docs, notch\n"
     "  0.2.8263; the rebuild follows the closures of this pass.\n"),
    ("- [ ] Enforce Ticket Microcycle across all linked tasks.\n",
     "- [x] Enforce Ticket Microcycle across all linked tasks.\n"),
    ("- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.\n",
     "- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.\n"),
    ("- %s: scheduled for melder_1 on the owner's order, after S8 (DECISION note).\n" % OPENED,
     "- %s: scheduled for melder_1 on the owner's order, after S8 (DECISION note).\n"
     "- %s: landed at 0.2.8263 and turned in on the owner's word (MEASURE and FACT notes).\n" % (OPENED, NOW)),
    ("  - artifacts/staged_signature_claims_20261019/ (melder_1's lane: re-runs, scripts, notes)\n",
     "  - artifacts/staged_signature_claims_20261019/ (melder_1's lane: re-runs, scripts, notes)\n"
     "  - system_docs/patches/completed/staged_signature_claims_2026_10_19/ (the patch, archived at turn-in)\n"),
    ("- [ ] Work walkthrough shared with user\n",
     "- [x] Work walkthrough shared with user (the landing report, chat 2026-10-19, sent with this turn-in)\n"),
    ("- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded\n",
     "- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded\n"),
    ("- [ ] Applicable anti-pattern checks are clear or escalated with evidence.\n",
     "- [x] Applicable anti-pattern checks are clear or escalated with evidence.\n"),
    ("- State: in_progress (melder_1), discovery: scheduled on the owner's order after S8 (DECISION note); filed by\n"
     "  melder_0 under EPIC-2026-10-17-correctness_defects. The fix sits in spellbook.py, which melder_1 holds.\n"
     "- Next: (1) re-run C1-C4 and C6 on 0.2.8262 and re-read the seam whole; (2) the patch, linked here; (3) red\n"
     "  regression tests, the fix, docs, notch and the release note; the rebuild comes once, last in the pass.\n",
     "- State: done (melder_1): landed at 0.2.8263 and turned in on the owner's word (MEASURE and FACT notes); in\n"
     "  tickets/stories/completed/. The rebuild for 0.2.8263 is the pass's last write.\n"
     "- Next: none. Related, open: STORY-2026-10-17-notch_moves_signature_by_incoming_key_only (the notch's own\n"
     "  signature handling) and STORY-2026-10-17-restore_drops_separated_parked_version.\n"),
)
EPIC_EDITS = (
    ("- [ ] Story: STORY-2026-10-17-staged_version_releases_active_signature - staging, moving or\n"
     "  disposing a parked version drops the binding signature of the active spell keyed like it (sweep A1).\n",
     "- [x] Story: STORY-2026-10-17-staged_version_releases_active_signature - staging, moving or\n"
     "  disposing a parked version drops the binding signature of the active spell keyed like it (sweep A1).\n"
     "  Landed by melder_1 at 0.2.8263: `_destroy_spell_index` drops only its own route and releases only the\n"
     "  departing member's claim; turned in 2026-10-19, in tickets/stories/completed/.\n"),
    ("  S1, S2 and S5 go to melder_1 after S8, one at a time, on the owner's word",
     "  S1 done (0.2.8263; turned in 2026-10-19); S2 and S5 go to melder_1, one at a time, on the owner's word"),
    ("  STORY-2026-10-17-staged_version_releases_active_signature (p1),\n",
     "  STORY-2026-10-17-staged_version_releases_active_signature (p1; done: landed at 0.2.8263, turned in 2026-10-19),\n"),
    ("- Next: (1) small fixes melder_1 can prove, one at a time, each from a failing test with its own notch and the\n"
     "  patch gate (the owner's word; S1, S2 and S5 are the candidates); (2) the rebuild once, last in the pass;\n"
     "  (3) S11 on the owner's call; (4) a fourth tranche on the owner's word.\n",
     "- Done since: S1 landed at 0.2.8263 and is turned in (FACT note of 2026-10-19); the pass is rebuilt last.\n"
     "- Next: (1) S2 and S5 with melder_1, one at a time, on the owner's word, each from a failing test with its\n"
     "  own notch and the patch gate; (2) S11 on the owner's call; (3) a fourth tranche on the owner's word.\n"),
)
EPIC_NOTE = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: S1 (STORY-2026-10-17-staged_version_releases_active_signature) landed at 0.2.8263 and is turned in, on the
    owner's word (chat 2026-10-19: "Yes do your fix", "But finish asap"): staging a version keyed like the active
    one, an index move back and a lone parked `cleanup_spell` keep every other spell's binding signature
    (`_destroy_spell_index` drops only its own route and releases only the departing member's claim, by spell_id).
    Six component tests, red on 0.2.8262 and green at the fix with the GIL off and on; the whole tree green but
    the asset stamp the rebuild clears. The pass ends with the rebuild for 0.2.8263.
  EVIDENCE:
  - context_compass/{DONE}:1-12
  - src/melder/aether/spellbook/spellbook.py:4655-4732
  IMPACT: The epic's open stories are S2 and S5 (melder_1, on the owner's word) and S11 (the owner's call).
  NEXT: The rebuild, then the owner's signed commit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
"""
ANCHOR = ("| staged_signature_claims | done | melder_1 | %s | Landed 0.2.8263 (S1 of EPIC-2026-10-17-correctness_defects: "
          "staging, an index move back and a lone parked disposal keep the active spell's binding signature). "
          "Next: S2 and S5 on the owner's word. | %s |\n" % (DONE, NOW))
EPIC_ROW_NEXT = ("S1, S8 and S3 are turned in and the pass is rebuilt for 0.2.8263; S2 and S5 follow on the owner's "
                 "word; S11 waits for the owner.")
CLEARED = (
    "| %s | artifacts/staged_signature_claims_20261019/ | retain_as_reference | Evidence of the 0.2.8263 landing: the "
    "claims cases rewritten for 0.2.8262 with their runs before and at the fix, the red and green runs, the whole "
    "tree with the GIL off and on, the release-note probe, the docs, index, citation, graph and notch logs, and "
    "every script (open, docs, remap, graph prose, notch, closure). | %s |\n" % (DONE, NOW)
    + "| %s | system_docs/patches/completed/staged_signature_claims_2026_10_19/ | promote_to_documentation | Promoted at "
    "landing (0.2.8263) to src_architecture, src_components, tests_components and tests_architecture with their "
    "indexes, and to the graph; the two patch docs (architecture, Spellbook component) archived at turn-in. | %s |\n"
    % (DONE, NOW)
)


def load(path: pathlib.Path) -> str:
    """Return the file's text, refusing CRLF."""
    raw = path.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF in %s" % path.name)
    return raw.decode("utf-8")


def swap(text: str, old: str, new: str, name: str) -> str:
    """Replace the one `old` with `new`, checking new lines' width."""
    if text.count(old) != 1:
        raise SystemExit("%s: anchor found %d times: %r" % (name, text.count(old), old[:70]))
    for line in new.split("\n"):
        stripped = line.strip()
        if (len(line) > 120 and line not in old and not line.startswith("|")
                and not (stripped.startswith("- ") and " " not in stripped[2:])):
            raise SystemExit("%s: line over 120: %s" % (name, line))
    return text.replace(old, new)


def board_sync(text: str) -> str:
    """Drop the lane row and detail, add the anchor (cap 12, oldest out), refresh the epic row."""
    lines = text.split("\n")
    lines = [line for line in lines if not line.startswith("| staged_signature_claims | in_progress |")]
    text = "\n".join(lines)
    detail = ("- WORK_ITEM: staged_signature_claims\n"
              "  SWITCH_TRIGGER: The fix lands with tests, docs and notch (the rebuild last in the pass), or the owner "
              "redirects.\n  RESUME_HIERARCHY:\n    - tickets/epics/2026-10-17_correctness_defects_epic.md\n"
              "    - %s\n" % TICKET)
    text = swap(text, detail, "", "board detail")
    start = text.index("<!-- BEGIN USER-DEFINED: closed_anchors -->\n") + len("<!-- BEGIN USER-DEFINED: closed_anchors -->\n")
    end = text.index("<!-- END USER-DEFINED: closed_anchors -->")
    rows = [row for row in text[start:end].split("\n") if row.startswith("| ")]
    rows.append(ANCHOR.rstrip("\n"))
    while len(rows) > 12:
        oldest = min(rows, key=lambda row: row.rstrip(" |").rsplit("| ", 1)[1])
        rows.remove(oldest)
        print("anchor dropped:", oldest.split(" | ")[0])
    text = text[:start] + "\n".join(rows) + "\n" + text[end:]
    out = []
    for line in text.split("\n"):
        if line.startswith("| correctness_defects | in_progress |"):
            cells = line.split(" | ")
            cells[6] = EPIC_ROW_NEXT
            cells[10] = NOW
            line = " | ".join(cells)
        out.append(line)
    return "\n".join(out)


def arts_sync(text: str) -> str:
    """Move the story's active rows to cleared with the completed path; add the lane and patch rows."""
    moved = []
    kept = []
    for line in text.split("\n"):
        if line.startswith("| %s |" % TICKET):
            moved.append(line)
        else:
            kept.append(line)
    if len(moved) != 4:
        raise SystemExit("expected 4 active rows for the story, found %d" % len(moved))
    text = "\n".join(kept)
    cleared = CLEARED
    for line in moved:
        cells = line.split(" | ")
        path = cells[1]
        if path == "artifacts/staged_signature_claims_20261019/":
            continue
        cleared += ("| %s | %s | retain_as_reference | S1 turned in (landed at 0.2.8263): the reproducer and its runs "
                    "stay in the sweep's folder, rowed under EPIC-2026-10-17-correctness_defects; the claims cases are "
                    "re-run at the fix in the lane folder (R1 and G4 not re-run). | %s |\n" % (DONE, path, NOW))
    return swap(text, "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n",
                "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n" + cleared, "artifacts")


def main() -> None:
    """Prepare every edit; write with --apply."""
    if sys.argv[1:] not in (["--check"], ["--apply"]):
        raise SystemExit(__doc__)
    story = load(STORY)
    for old, new in STORY_EDITS:
        story = swap(story, old, new, "story")
    first_line_end = story.index("\n") + 1
    story = story[:first_line_end] + SUMMARY + story[first_line_end:]
    story = swap(story, "\n## Closure Confirmation\n", "\n" + MEASURE + "\n" + FACT + "\n## Closure Confirmation\n",
                 "story notes")
    epic = load(EPIC)
    for old, new in EPIC_EDITS:
        epic = swap(epic, old, new, "epic")
    epic = swap(epic, "\n## Closure Confirmation\n", "\n" + EPIC_NOTE + "\n## Closure Confirmation\n", "epic note")
    epic, count = re.subn(r"^- Updated: \S+$", "- Updated: " + NOW, epic, count=1, flags=re.M)
    if count != 1:
        raise SystemExit("no Updated line in the epic")
    board = board_sync(load(BOARD))
    arts = arts_sync(load(ARTS))
    print("ready:", NOW)
    if sys.argv[1] == "--apply":
        for path, text in ((STORY, story), (EPIC, epic), (BOARD, board), (ARTS, arts)):
            path.write_bytes(text.encode("utf-8"))
            if path.read_bytes().decode("utf-8") != text:
                raise SystemExit("read-back mismatch: %s" % path.name)
        print("applied")


main()
