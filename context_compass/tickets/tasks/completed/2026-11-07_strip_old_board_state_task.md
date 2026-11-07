# Task: Strip old state from the boards and the mailbox (2026-11-07)

- Completed: 2026-11-07T07:54:59Z
- Summary: Boards stripped to live state (55 KB -> 26 KB); on the owner's picks many_child_ownership and pypi_provenance closed done, the 17 artifact rows of finished tickets dropped with every file kept.

## Metadata
- Task ID: TASK-2026-11-07-strip_old_board_state
- Story: none (standalone owner-directed cleanup)
- Status: done
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-11-07T07:43:52Z
- Updated: 2026-11-07T07:54:59Z

## Objective
The owner's word (chat 2026-11-07): "also cleanup attentionboard and mailbox and focus on synaptic_python_developer
stuff, make sure you cleanup all the boards because they are legit old". Leave every board holding only live state.
Ticket closures and file deletions happen only on the owner's explicit pick (cleanup_context_compass workflow: scope,
then the candidate list, then his pick).

## Ticket Contract
- ENTRY_GATE: the owner's word above; scope "everything" (all the boards, his words); this task routed from
  attention_board.md.
- EXECUTION_BOUNDARY: context_compass/ only - attention_board.md, mailbox_board.md, artifact_board.md, issue_board.md,
  context_management/context_board.md (USER-DEFINED regions only; MANAGED text untouched); then, on his pick, the
  closure of the epics he picks and the deletion of the artifact folders he picks. No src/, tests/, docs/ or
  release_docs/ change, so no notch and no release-note entry.
- DEPENDENCIES: none. The other agents are idle (melder_1 and melder_2 last checked 2026-10-25, command_5
  2026-11-02); every board write re-reads first.
- EXIT_GATE: each board holds only live rows; the owner's picks applied; closure with board sync.
- FAILURE_ESCALATION: DECISION_REQUEST for any closure or deletion the owner has not picked; BLOCKER on a write
  conflict that re-reading cannot resolve.

## Scope Boundaries
- In scope: board history (message alerts, closed anchors, cleared artifact rows, stale messages, the departed
  agent's roster row and setup note, a superseded setup note, stale-marking idle roster rows); on the owner's pick,
  the idle epics he chooses to close and the artifact folders only finished tickets cite.
- Out of scope: MANAGED board text; src/, tests/, docs/; completed tickets' contents; the backlog; other agents'
  certification records.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: the owner's two picks applied and the boards synced (DECISION and MEASURE notes of 2026-11-07T07:54:59Z).
- earlier: ready -> in_progress on the owner's word above.

## Steps / Checklist
- [x] Strip board history (no decision needed): alerts, closed anchors, cleared artifact rows, stale messages, the
      departed roster row and setup notes; stale-mark idle roster rows.
- [x] Owner pick 1: which idle epics to close.
- [x] Owner pick 2: what to do with the artifacts of finished tickets.
- [x] Apply the picks; board and artifact sync.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.

## Deliverables
- Boards holding only live state; the owner's picks applied.

## Files / Paths Impacted
- context_compass/attention_board.md, mailbox_board.md, artifact_board.md
- on the owner's pick: the epics he picks (with their open stories) and the artifacts/ folders he picks

## Validation
- Run 2026-11-07 (/tmp/m0_clean/apply2.py): region markers intact (14, 8, 8); every active row resolves to an open
  ticket; every detail entry matches a row and its resume paths exist; every closed anchor and artifact row resolves
  to an existing path. No problems. No src/, docs/ or system_docs/ change, so no notch and no asset rebuild.

## Risks / Rollback Notes
- Board rows are pointers; the records stay in the tickets and the old board text is in git history. Untracked run
  logs in a deleted artifact folder do not come back, so deletion waits for the owner's pick.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.
- [x] No ticket closed or folder deleted that the owner did not pick.

## Done Checklist
- [x] Steps complete and checked off
- [x] Validation status recorded
- [x] Board sync completed for closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - board and artifact cleanup
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Keep notes append-only; correct history only for factual errors.

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; created 2026-11-07.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none

## Notes
- DATETIME: 2026-11-07T07:44:25Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Scope is "everything" (all the boards, the owner's word). Inventory before the strip: attention board - 5
    active rows (melder_1 x4, melder_2 x1, idle since 2026-10-24/25), 6 alerts, 12 closed anchors, 4 standing notes;
    mailbox - 5 roster rows (melder_3 departed; melder_1 and melder_2 last checked 2026-10-25, command_5 2026-11-02),
    13 messages (9 to melder_0; 4 command_5 notch notices to melder_1 and melder_2), 7 notes; artifact board - 27
    active rows (17 for finished tickets), 18 cleared rows; issue board, context board and patches/active - empty.
    Open tickets: the 5 epics and 3 ready stories (restore_drops_separated_parked_version and
    notch_back_keeps_outgoing_dependencies under correctness_defects; map_dependency_watchers_and_announcers under
    dependency_watchers); no open task. artifacts/ holds 18 folders (56 MB); 5 are cited only by finished tickets -
    cache_write_failure_20261024, codegen_room_policy_20261025, core_protection_review_20261010,
    notch_fanout_race_20261025 and rebind_live_store_tests_20261025 (about 4.3 MB, 219 files; the only other citation
    is the completed patch codegen_open_builtin_posture_2026_10_25).
  EVIDENCE:
  - context_compass/attention_board.md:101-173
  - context_compass/mailbox_board.md:86-293
  - context_compass/artifact_board.md:67-119
  IMPACT: Board history goes now, as in TASK-2026-10-24-strip_old_board_and_artifact_state; epic closures and
    folder deletions wait for the owner's two picks.
  NEXT: Strip the history with one re-reading script, then put the two picks to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-11-07T07:44:25Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: melder_0 checked in (last_checked 2026-11-07T07:43:52Z) and consumed its 9 messages (M1-70, M3-18, M1-74,
    M3-23, M1-76, M1-80, M3-25, C5-001, C5-002). Every lane they name has closed (D-11 at 0.2.8271, S2 at 0.2.8273,
    the store-slot story at 0.2.8274, command_5's tasks at 0.2.8276 and 0.2.8277), so nothing carries over except
    M1-74's observation: the device tree's git-ignored src/melder/__melder_cache__/__crystallizer_cache__ folder makes
    expert examples 02, 09, 24 and 27 fail; removing it is the owner's call.
  EVIDENCE:
  - context_compass/mailbox_board.md:98-244 (before the strip; the text is in git history)
  - src/melder/crystallizer/asset_management/crystallizer_cache.py:176-215
  IMPACT: No addressed message is left for melder_0; the cache-folder question goes to the owner in the report.
  NEXT: Strip the remaining history.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-11-07T07:44:25Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: History stripped in one re-reading pass (/tmp/m0_clean/strip1.py, USER-DEFINED regions only): attention
    board - 6 alerts and 12 closed anchors removed, this task's row and detail added, the 5 idle rows kept until the
    owner picks; mailbox - all 13 messages removed, melder_3's departed row and setup note removed, melder_0's
    superseded 2026-10-18 setup note removed, melder_1, melder_2 and command_5 stale-marked (older than a day, during
    melder_0's check-in), their notes and command_5's certification record kept; artifact board - 18 cleared rows
    removed. Bytes: attention 14912 -> 10919, mailbox 17189 -> 8223, artifact 23126 -> 16703 (55227 -> 35845).
  EVIDENCE:
  - context_compass/attention_board.md:101-160
  - context_compass/mailbox_board.md:86-145
  - context_compass/artifact_board.md:67-105
  IMPACT: The boards hold the live rows plus the 5 idle epics and 17 finished tickets' artifact rows that wait on the
    owner's picks.
  NEXT: Ask the owner which idle epics to close and what to do with finished tickets' artifacts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-11-07T07:54:59Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's picks (chat 2026-11-07). Epics: "wait I never said close as unfinished but melder_2 finished
    pypy_provincnace and many_child_ownership is done too you can close those 2 not sure about the other ones" -
    many_child_ownership and pypi_provenance close done (not unfinished); correctness_defects, dependency_watchers
    and index_binding_risks stay open and routed. Artifacts: "Drop rows, keep files" - the 17 rows of finished
    tickets come off the artifact board; every file stays on disk, the 5 folders only finished tickets cite included.
  EVIDENCE:
  - context_compass/tickets/epics/completed/2026-10-20_reassess_many_child_disposal_ownership_epic.md:1-5
  - context_compass/tickets/epics/completed/2026-10-24_pypi_provenance_attestations_epic.md:1-8
  IMPACT: Two epics closed on his directive; the three he was unsure of keep their rows.
  NEXT: Measure the result and close this task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-11-07T07:54:59Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Applied (/tmp/m0_clean/apply2.py): both epics carry a DECISION note, closure lines and checked closure
    boxes on the owner's word and sit in epics/completed/; their rows and details came off and two closed anchors
    went on; the artifact board went from 27 rows to 10, each on an open or backlog ticket. Validation found no
    problem (see Validation). Bytes after this closure: attention about 10 KB, mailbox 8223, artifact 7650 - about
    26 KB against 55 KB before the cleanup.
  EVIDENCE:
  - context_compass/attention_board.md:105-150
  - context_compass/artifact_board.md:67-80
  IMPACT: Every board holds live state only; three idle epics stay routed on the owner's word.
  NEXT: Close this task with board sync.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
- Done 2026-11-07: boards hold live state only; many_child_ownership and pypi_provenance closed done on the owner's
  word; artifact rows of finished tickets dropped, files kept.
- Left: correctness_defects, dependency_watchers and index_binding_risks stay open and routed (the owner was unsure);
  the device's git-ignored __crystallizer_cache__ folder that fails expert examples 02, 09, 24 and 27 is his call.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
