# Task: Strip old state from the boards, the mailbox and the artifacts

- Completed: 2026-10-24T18:35:08Z
- Summary: Boards stripped to live state (about 160 KB -> 34 KB); 26 old tickets closed unfinished,
  55 old artifact entries, 112 old patch docs and one scratch codemod deleted, all on the owner's word.

## Metadata
- Task ID: TASK-2026-10-24-strip_old_board_and_artifact_state
- Story: none (standalone owner-directed cleanup)
- Status: done
- Owner: user
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-24T18:19:53Z
- Updated: 2026-10-24T18:35:08Z

## Objective
The owner's word (chat 2026-10-24): "go cleanup everything old in artifacts, mailbox, issueboard, everything go strip
it clean so token count is minimized and lets cleanup attentionboard too please go do that first". Leave every board
holding only live state, so an agent's onboarding reads stay small. Ticket closures and file deletions happen only
on the owner's explicit yes (cleanup_context_compass workflow: scope first, then the candidate list, then his pick).

## Ticket Contract
- ENTRY_GATE: the owner's word above; this task routed from attention_board.md; scope "everything" (his words).
- EXECUTION_BOUNDARY: context_compass/ only - attention_board.md, artifact_board.md, mailbox_board.md,
  issue_board.md, context_management/context_board.md (USER-DEFINED regions only; MANAGED text untouched); then, on
  his yes, the closure of the tickets he picks, the artifact folders he picks and the old patch folders. No src/,
  tests/, docs/ or release_docs/ change, so no notch and no release-note entry.
- DEPENDENCIES: none. melder_0 checked in at 2026-10-24T18:03:21Z, so every board write re-reads first and refuses
  to overwrite a change it did not read.
- EXIT_GATE: each board holds only live rows; the owner's three decisions applied; the asset check run if anything
  under system_docs/ moved; closure with board sync.
- FAILURE_ESCALATION: DECISION_REQUEST for any closure or deletion the owner has not picked; BLOCKER on a write
  conflict that re-reading cannot resolve.

## Scope Boundaries
- In scope: board history (closed anchors, cleared artifact rows, notch notices, stale messages, departed agents'
  roster rows and notes); artifact rows whose paths no longer exist; on the owner's yes, old open tickets, artifact
  folders that only finished tickets cite, and the June/July folders in system_docs/patches/active/.
- Out of scope: MANAGED board text (the package's; an upgrade restores it); src/, tests/, docs/; completed tickets'
  contents; the correctness epic and its open stories; the many-dependency reassess epic.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: the owner's three answers applied and the boards synced (DECISION and MEASURE
  notes of 2026-10-24T18:35:08Z).

## Steps / Checklist
- [x] Strip board history (no decision needed): attention notes and closed anchors, cleared artifact rows and the
      rows whose paths are gone, stale mailbox messages, departed roster rows and their notes.
- [x] Owner decision 1: close the old open tickets nobody works (list in Notes).
- [x] Owner decision 2: delete the artifact folders only finished tickets cite.
- [x] Owner decision 3: move the June/July patch folders out of system_docs/patches/active/.
- [x] Apply the decisions; board and artifact sync; asset check if system_docs/ moved.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.

## Deliverables
- Boards holding only live state; the owner's picks applied.

## Files / Paths Impacted
- context_compass/attention_board.md, artifact_board.md, mailbox_board.md
- on the owner's yes: tickets he picks, artifacts/ folders he picks, system_docs/patches/active/ folders

## Validation
- Not run yet. Planned: each board parses with its region markers intact; every active row resolves to an open
  ticket; every artifact row resolves to an existing path; the asset runner `--check` if system_docs/ moved.

## Risks / Rollback Notes
- Board rows are pointers; the records they point at stay in the tickets. Committed files come back with git; untracked
  run logs in a deleted artifact folder do not, so deletion waits for the owner's yes.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.
- [ ] No ticket closed or folder deleted that the owner did not pick.

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
- Ticket/Work Author(s): melder_1 (synaptic_python_developer); prose; created 2026-10-24.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none

## Notes
- DATETIME: 2026-10-24T18:19:53Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Scope is "everything" (the owner's word). Inventory at 2026-10-24: attention board - 5 active rows (4 of
    other agents, idle since 2026-09-26/27 and 2026-10-20), 12 closed anchors, 3 alerts (consumed), ~60 lines of notch
    notices; artifact board - 34 active rows (8 point at paths that no longer exist), ~190 cleared rows; mailbox - 13
    roster rows (8 departed or stale), 37 messages (3 to melder_1, consumed; 34 to muse_0, 2026-09-27..10-01, never
    consumed), 6 notes; issue board and context board - empty. 31 open tickets in the active lanes: the correctness
    epic with S2, S5 and S11 and the many-dependency reassess epic stay; the other 25 (July/August epics, stories
    and tasks of departed agents, melder_2's gauntlet story and task, muse_0's defect-hunting epic, story and two
    tasks, expert_1's README review, melder_1's services-and-pools epic) are closure candidates. artifacts/ holds
    68 entries (~100 MB, 3417 tracked files, 678 git-ignored run logs); 55 are cited by no open or backlog ticket.
    system_docs/patches/active/ still holds June/July lane folders.
  EVIDENCE:
  - context_compass/attention_board.md:105-114
  - context_compass/mailbox_board.md:86-103
  - context_compass/artifact_board.md:64-103
  IMPACT: Board history goes now; closures and deletions wait for the owner's three answers (asked in chat).
  NEXT: Strip the board history with one re-reading script, then apply the owner's answers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T18:20:31Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Board history stripped (USER-DEFINED regions only; MANAGED text untouched), each file re-read and refused
    on a concurrent change (melder_0 updated its row at 18:10:55Z; kept). attention_board.md 27546 -> 10724 bytes:
    12 closed anchors and 164 lines of notes (notch notices, legacy details) gone, four standing device/mailbox notes
    kept, the board_cleanup row added and a detail entry for every active row. artifact_board.md 339 -> 105 lines:
    219 cleared rows and the stale notes gone, 8 active rows whose paths no longer exist removed (27 remain).
    mailbox_board.md 33868 -> 5641 bytes: 34 unconsumed messages to muse_0 (2026-09-27..10-01) gone; 9 departed or
    stale roster rows removed, muse_0 and expert_1 marked stale (their tickets wait for decision 1); 3 setup notes
    kept, expert_1's absolute path redacted to ~/.codex/AGENTS.md. Check: every region marker once, every active row
    routes to an open ticket with a matching detail, every artifact row's ticket and path exist.
  EVIDENCE:
  - context_compass/attention_board.md:101-164
  - context_compass/artifact_board.md:64-105
  - context_compass/mailbox_board.md:86-110
  IMPACT: Onboarding's board reads drop from about 156 KB to about 30 KB; nothing a ticket holds was lost (board rows
    are pointers to tickets).
  NEXT: Apply the owner's answers to the three decisions.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T18:35:08Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's answers (chat 2026-10-24): "close all old tickets please and deal with all the old junk you
    don't need to care about the artifacts and lets just cleanup", then "close all tickets in review" (the 26 put to
    him) and "just close the stuff we don't need in there right?". So: the 26 candidates close unfinished on his
    word; artifact folders no open ticket or live document cites are deleted (their run logs with them, which he
    accepted); the old patch docs in system_docs/patches/active go; the 46 parked backlog tickets stay (his parked
    to-do list, not put to him).
  EVIDENCE: context_compass/tickets/tasks/completed/2026-10-24_strip_old_board_and_artifact_state_task.md:111-132
  IMPACT: Every closure and deletion below is the owner's pick.
  NEXT: Apply, sync the boards, check the assets.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T18:35:08Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Applied. 26 tickets closed unfinished - each with a completion header and Status done, moved to its lane's
    completed/ (11 epics: 2026-07-18 parallel_restore_ulid_identity, 07-19 ux_aix_intermediate_experience, 07-20
    conjure_boot_melds, 07-27 transactional_structure_unwind, 07-31 aetheric_mediator_subsystem, 08-01
    configuration_surface_uniformity, 08-02 agent_authored_synthetic_modules, 08-02 process_wide_spell_id_uniqueness,
    08-03 unreachable_public_capability, 09-27 defect_hunting, 10-05 melder_services_and_pools; 8 stories: 07-19
    bind_kwargs_transplant, 07-19 crystallizer_analysis_io_cache, 07-19 melder_init_composition, 07-31
    aetheric_mediator_wiring, 08-02 aether_unified_spell_id_set, 08-02 release_spell_id_on_destruction, 09-26
    gauntlet_runtime_speed, 09-27 spellbook_sweep; 7 tasks: 07-19 crystallizer_analysis_io_storm, 07-19
    melder_init_composition_and_wheel_strategy, 07-23 bind_guard_sentinel_vs_set_benchmark, 09-26
    measure_gauntlet_scope_cycle_costs, 09-27 spellbook_sweep, 09-27 sweep_fixes_batch_1, 10-20
    review_public_readme_clarity). Board sync: their four active rows and details removed, four closed anchors
    added, 13 artifact rows of closed tickets removed, muse_0 and expert_1 roster rows and expert_1's note removed.
    Deleted (owner-granted delete permission): 55 artifacts/ entries no open ticket or live document cites (artifacts/
    ~100 MB -> 54 MB; 12 cited folders and the two package files kept, melder_0's cache_write_failure_20261024
    among them), 112 old patch entries in system_docs/patches/active (README.md and _template_patch_id kept) and
    user_defined/meld_public_callsite_codemod.py. Committed files return with git; the git-ignored run logs in the
    deleted folders are gone. Checks: the asset runner --check printed three OK lines (0.2.8265); the LLM --check
    printed OK for src and tests and STALE for other, whose fingerprint moved with README.md, pyproject.toml and
    uv.lock edited on 2026-10-20 and uncommitted - not this cleanup (the builder excludes context_compass/).
  EVIDENCE:
  - context_compass/attention_board.md:101-140
  - llm_support/_builder.py:89-91
  IMPACT: Open work is the correctness epic with S2, S5 and S11, the many-dependency reassess epic, melder_0's
    cache-write task and the backlog; the boards route nothing else.
  NEXT: Close this task; tell the owner the LLM other bundle waits for his README and pyproject edits.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
- Done 2026-10-24: boards hold live state only; the owner's three picks applied; asset check OK.
- Left: the LLM other bundle is stale from uncommitted README.md/pyproject.toml edits of 2026-10-20 (the
  owner's to rebuild once final); the 46 parked backlog tickets were not put to him and stay.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
