"""Bring S4's contract, plan and resume view to the owner's word of 2026-10-18 (melder_1); sync its board row.

The owner's word (the story's DECISION note of 2026-10-18T18:00:11Z): A registers the minted index as `bind` registers
the index it creates, with B (the root's teardown) and C (residency); no new index state. Exact anchored
replacements; LF only; each anchor once; read-back verified. Usage: --check | --apply
"""
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
STORY = ROOT / "tickets/stories/2026-10-17_minted_index_missing_from_frame_registry_story.md"
BOARD = ROOT / "attention_board.md"
TS = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

STORY_PAIRS = [
("""- ENTRY_GATE: the owner schedules the story and assigns an agent (2026-10-18: melder_1 - DECISION note);
  spellbook.py (and conduit.py if the fix goes there) claimed from melder_0 by message before any edit - melder_0
  holds spellbook.py for S1 and S2 of EPIC-2026-10-18-spell_identity_is_the_code (M1-38); an active board row; a
  component patch for the seam, and the owner's word on the exact edits before the first one.
- EXECUTION_BOUNDARY: `Spellbook._apply_remove_from_index` (or the `Conduit.remove_from_spell_index` facade):
  register the minted index under the owning conduit in the frame registry once the Book is conjured, as a
  post-conjure `bind` registers its new index; regression tests; system docs with their indexes and the graph; the
  release note; one notch; the rebuild last.
""",
"""- ENTRY_GATE: the owner schedules the story and assigns an agent (2026-10-18: melder_1 - DECISION note); the
  owner's word on the edits (2026-10-18: A registers the minted index as `bind` registers the index it creates,
  with B and C - DECISION note); spellbook.py claimed back from melder_0 by message once S1 and S2 of
  EPIC-2026-10-18-spell_identity_is_the_code land (M1-38), mutation_research.py claimed by message; an active
  board row; patch docs for the seam, the teardown and residency before the first src edit.
- EXECUTION_BOUNDARY (widened on the owner's word, 2026-10-18): (A) `Spellbook._apply_remove_from_index`
  registers the index it mints in the frame's spell registry as a post-conjure `bind` registers the index it
  creates - bind's guard and call, the Book's root conduit; (B) `Spellbook._unregister_conduit_spells_from_aether`,
  which only the root's teardown calls, also unregisters the indexes that hold only parked versions; (C)
  `MutationResearch._locate_live_membership` calls a version active only when the frame's lineage registry tracks
  it as its index's current version; their docstrings and their entries' (`_remove_from_spell_index`,
  `residency_view`); regression tests; system docs with their indexes and the graph; the release note; one notch;
  the rebuild last.
"""),
("""- EXIT_GATE: the probe's M2 and M3 show the frame finding the minted index and its conduit, `get_spell_by_id` and
  `get_conduit_by_spell_id` answering, and the M3 grant accepted; regression tests pass with the GIL off and on;
  docs, notch and the rebuild with both checks OK.
- FAILURE_ESCALATION: CONFLICT if melder_1's lookup fix moves the frame step; DECISION_REQUEST if the owner wants a
  minted index registered only once it holds an active version.
""",
"""- EXIT_GATE: on the fixed tree the probes read right - M2 and M3: the frame finds the minted index and its conduit,
  `get_spell_by_spell_id` and `get_conduit_by_spell_id` answer, the grant is accepted; M4b and M5b: the second
  bind is refused; M6: nothing is left for the torn-down root; M7: the transfer by spell_id is accepted; V2 parked
  and V3 active - and the regression tests pass with the GIL off and on, the whole tree in a mirror; docs, notch
  and the rebuild with both checks OK.
- FAILURE_ESCALATION: CONFLICT if melder_0's S1 and S2 landing changes the seam, the teardown or bind's
  registration; DECISION_REQUEST if a test shows a case the three edits do not cover.
"""),
("""## Requirements (Functional)
- After `remove_from_spell_index` on a conjured Book, the frame's spell registry lists the minted index under the
  Book's root conduit, so `find_index_for_spell` and `find_conduit_id_for_spell` find the separated version.
- That holds while the version stays parked and after a notch makes it active in the minted index; the existing
  destroy path keeps unregistering the index when it empties (`_destroy_spell_index`).

## Requirements (Non-Functional)
- No new lock or lock-order edge: the registration takes the frame lock alone, after the seam's Book-locked section,
  as the destroy path's unregistration does.

## Scope Boundaries
- In scope: the frame registration of the minted index.
- Out of scope: what `get_spell_by_id` answers once the conduit is found (melder_1's lookup fix); the binding
  signature an active version in a minted index takes (STORY-2026-10-17-notch_moves_signature_by_incoming_key_only).
""",
"""## Requirements (Functional)
- After `remove_from_spell_index` on a conjured Book, the frame's spell registry lists the minted index under the
  Book's root conduit, registered as `bind` registers the index it creates, so `find_index_for_spell` and
  `find_conduit_id_for_spell` find the separated version - and so do the lookups, grants and transfers by
  spell_id and bind's collision guard, which walk that registry.
- That holds while the version stays parked and after a notch makes it active in the minted index; the existing
  destroy path keeps unregistering the index when it empties (`_destroy_spell_index`), and the root's teardown
  unregisters it with the root's other indexes.
- `residency_view` reads the version parked in the minted index, and active once a notch makes it active there.

## Requirements (Non-Functional)
- No new lock or lock-order edge: the registration takes the frame lock alone, after the seam's Book-locked section,
  as bind's registration and the destroy path's unregistration do; the teardown reads each parked version's index
  under the Book lock (Book -> spell, the order Book teardown takes) and unregisters with the frame lock alone after
  it; residency's lineage read takes the registry lock, then the state's lock, each alone, with no other lock held.

## Scope Boundaries
- In scope: the frame registration of the minted index, its unregistration at the root's teardown, and residency's
  verdict for a version in it.
- Out of scope: the binding signature an active version in a minted index takes
  (STORY-2026-10-17-notch_moves_signature_by_incoming_key_only); the parked versions Book teardown leaves uncleaned
  (STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned); a restore or graft of a separated version
  (STORY-2026-10-17-restore_drops_separated_parked_version); a new index state (withdrawn by the owner,
  ALIGNMENT_CHECK note).
"""),
("""- [ ] Task: patch docs for the seam; the owner's approval.
""",
"""- [x] Task: the owner's word on the edits (2026-10-18; DECISION note).
- [ ] Task: patch docs for the seam, the teardown and residency.
"""),
("""## Acceptance Criteria
- After `remove_from_spell_index(spell_id=X)`: `frame.find_index_for_spell(X)` returns the minted index,
  `get_conduit_by_spell_id(X)` returns the owning root, and `get_spell_by_id(X)` no longer raises "Spell version
  <id> not found in any conduit." (what it returns is melder_1's rule).
- After a notch makes X active in the minted index: the same, and a borrower's `add_spell_to_contract(spell_id=X)`
  is accepted.
- After X moves back with `add_to_spell_index`, the emptied minted index is gone from the registry again.

## Validation / Test Plan
- Regression tests named for the symptom, e.g. `test_a_version_separated_into_its_own_index_is_found_by_spell_id`,
  `test_a_version_notched_active_in_its_own_index_can_be_granted_by_spell_id`; GIL off and on; the probe re-run.

## UX / API / Data Notes
- No public signature changes. Visible today: `get_spell_by_id` and `get_conduit_by_spell_id` raise ValueError for a
  version the conduit's own Book owns (parked or active), and a grant of it by spell_id raises the same error.
""",
"""## Acceptance Criteria
- After `remove_from_spell_index(spell_id=X)`: `frame.find_index_for_spell(X)` returns the minted index,
  `get_conduit_by_spell_id(X)` returns the owning root, `get_spell_by_spell_id(X)` returns X, and `residency_view`
  reads X parked.
- After a notch makes X active in the minted index: the same, `residency_view` reads X active, a borrower's
  `add_spell_to_contract(spell_id=X)` is accepted, and a transfer by spell_id moves X to its target.
- While X is in the minted index, a bind of X's spell_id by another Book - of the frame, or of another frame under
  process-wide spell ids - is refused, as it is for a version in any registered index.
- After X moves back with `add_to_spell_index`, the emptied minted index is gone from the registry; after the root's
  teardown the frame holds no entry for the root.

## Validation / Test Plan
- Regression tests named for the symptom, e.g. `test_a_version_separated_into_its_own_index_is_found_by_spell_id`,
  `test_a_version_notched_active_in_its_own_index_can_be_granted_by_spell_id`,
  `test_a_version_in_its_own_index_cannot_be_bound_again_by_another_book` and
  `test_a_torn_down_root_leaves_no_registry_entry_for_a_separated_version`; red on 0.2.8256 and green with the
  three edits, GIL off and on; the probes M1-M7 and V1-V4 re-run; the whole tree in a mirror.

## UX / API / Data Notes
- No public signature changes. Visible today: `get_spell_by_spell_id` and `get_conduit_by_spell_id` raise
  ValueError for a version the conduit's own Book owns in a minted index (parked or active), a grant or a transfer
  of it by spell_id raises the same error, another Book may bind its spell_id, and `residency_view` reads it
  `declared_only`. After the fix all four answer as they do for a version in any other index.
"""),
("""- 2026-10-17T20:32:42Z: filed under EPIC-2026-10-17-correctness_defects from sweep A3 (Notes).
""",
"""- 2026-10-17T20:32:42Z: filed under EPIC-2026-10-17-correctness_defects from sweep A3 (Notes).
- 2026-10-18T17:35:35Z: the boundary's widening asked of the owner - B (the root's teardown) and C (residency)
  (DECISION_REQUEST note).
- 2026-10-18T18:00:11Z: the owner's word - A registers the minted index as `bind` registers the index it creates,
  with B and C; no new index state (DECISION and ALIGNMENT_CHECK notes).
"""),
("""- Scope: the index `remove_from_spell_index` mints is registered in the frame's spell registry under its owning
  conduit (Requirements). Defect proven on 0.2.8251 and re-verified on 0.2.8256 (Notes); probes and runs in
  Artifact Links.
- State: in_progress (melder_1), discovery; filed by melder_0 under EPIC-2026-10-17-correctness_defects; the owner
  scheduled it on 2026-10-18 (DECISION note). Re-verified on 0.2.8256, the readers read whole (FACT note); bind's
  collision guard and a transfer by spell_id miss the version too (MEASURE note, M4-M7). The fix is three edits -
  A the seam registers the minted index, B the root's teardown unregisters it, C residency reads the lineage -
  proven in /tmp copies (MEASURE note); B and C widen the EXECUTION_BOUNDARY, so the owner's word is asked
  (DECISION_REQUEST note). spellbook.py is melder_0's until S1 and S2 of
  EPIC-2026-10-18-spell_identity_is_the_code land; no src edit yet.
- Next: (1) the owner's word on A + B + C; (2) the boundary, the patch docs, the red tests and M1-39 to melder_0
  (spellbook.py after his landing, mutation_research.py); (3) the fix once both files are ours, its tests, docs,
  notch and the rebuild last.
""",
"""- Scope: the index `remove_from_spell_index` mints is registered in the frame's spell registry as `bind` registers
  the index it creates, unregistered at the root's teardown with the rest, and residency reads its version parked
  (Requirements; widened on the owner's word). Defect proven on 0.2.8251 and re-verified on 0.2.8256 (Notes);
  probes and runs in Artifact Links.
- State: in_progress (melder_1), implementation. The owner's word is given (DECISION note of
  2026-10-18T18:00:11Z): A follows bind's registration (guard and call), with B and C; no new index state
  (ALIGNMENT_CHECK notes). The three edits are proven in /tmp copies, GIL off and on (MEASURE notes); the preview to
  land is runs/s4_preview_0_2_8256_bind_guard.diff in the lane folder. spellbook.py is melder_0's until S1 and S2
  of EPIC-2026-10-18-spell_identity_is_the_code land; mutation_research.py is on no lane's list; no src edit yet.
- Next: (1) the patch docs (architecture; the Spellbook seam and teardown; MutationResearch residency) and M1-39 to
  melder_0; (2) the red tests, red on 0.2.8256 with the GIL off and on; (3) the fix once both files are ours,
  green, the whole tree, docs, notch, closure and the rebuild last.
"""),
]

ROW_OLD = ("| minted_index_registry | in_progress | discovery | claude | melder_1 | none | The owner's word on edits A + B + C "
           "(the seam, the root's teardown, residency); then the patch docs and the red tests. |")
ROW_NEW = ("| minted_index_registry | in_progress | implementation | claude | melder_1 | none | Patch docs and red tests "
           "for the owner-approved edits (A registers as bind does, B, C); M1-39 to melder_0. |")
STAMP_OLD = ("tickets/stories/2026-10-17_minted_index_missing_from_frame_registry_story.md | 2026-10-18T17:35:35Z | "
             "REQUIRED |")
STAMP_NEW = ("tickets/stories/2026-10-17_minted_index_missing_from_frame_registry_story.md | " + TS + " | REQUIRED |")


def replace_once(path: pathlib.Path, pairs: list, apply: bool) -> None:
    """Replace each (old, new) pair exactly once in `path`; refuse lines over 120 chars; write with `apply`."""
    raw = path.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF in %s" % path.name)
    text = raw.decode("utf-8")
    for old, new in pairs:
        if text.count(old) != 1:
            raise SystemExit("%s: anchor found %d times: %s" % (path.name, text.count(old), old[:80]))
        if path == STORY:
            for line in new.split("\n"):
                if len(line) > 120:
                    raise SystemExit("line over 120 chars (%d): %s" % (len(line), line))
        text = text.replace(old, new)
    if path == STORY:
        text, count = re.subn(r"^- Updated: \S+$", "- Updated: " + TS, text, count=1, flags=re.M)
        if count != 1:
            raise SystemExit("no Updated line")
    print("%s: %d replacement(s) ready (ts %s)" % (path.name, len(pairs), TS))
    if apply:
        path.write_bytes(text.encode("utf-8"))
        if path.read_bytes().decode("utf-8") != text:
            raise SystemExit("read-back mismatch: %s" % path.name)
        print("%s: applied" % path.name)


def main() -> None:
    """Check or apply the story, then the board."""
    if len(sys.argv) != 2 or sys.argv[1] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    apply = sys.argv[1] == "--apply"
    replace_once(STORY, STORY_PAIRS, apply)
    replace_once(BOARD, [(ROW_OLD, ROW_NEW), (STAMP_OLD, STAMP_NEW)], apply)


main()
