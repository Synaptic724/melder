# Story: crystals vocabulary move-up (S2 - package-level twins)

- Completed: 2026-07-10T09:10:00Z
- Summary: twin vocabulary + recorded_unit_state moved to
  crystallizer/crystals/; 39 import rewrites (final paths); both grep gates
  zero repo-wide; owner-run sentinel green; owner accepted at epic closure.

## Metadata
- Story ID: STORY-2026-07-09-crystals-vocabulary-move-up
- Parent Epic: EPIC-2026-07-09-crystallizer-subsystem-decomposition
- Status: done
- Owner: cowork
- Agent Name: melder_0
- Priority: p1
- Created: 2026-07-10T02:50:00Z
- Updated: 2026-07-10T02:50:00Z

## Problem / Opportunity
The twin vocabulary lives inside the record's private folder
(persistence/crystals/), so 8 runtime emitters outside the crystallizer reach
into a subsystem's internals just to construct their twins. V3 law: crystals
are the package-level language everyone speaks; move them to
crystallizer/crystals/ (+ recorded_unit_state.py - the shared state enum the
same emitters consume).

## Ticket Contract
- ENTRY_GATE: architecture_patch.md covers S2 (mechanical; no component patch
  per its coverage matrix); S1 sentinel GREEN (owner run 3, 2026-07-10).
- EXECUTION_BOUNDARY: `git`-visible moves persistence/crystals/ ->
  crystallizer/crystals/ and persistence/recorded_unit_state.py ->
  crystals/recorded_unit_state.py; import-line rewrites ONLY, in every
  affected file (src 13 + tests ~16; sweep now because these are the FINAL
  paths - no re-pointing later). ZERO behavior change, zero signature change.
- DEPENDENCIES: S1 accepted (sentinel green).
- EXIT_GATE: grep gates - zero `persistence.crystals` and zero
  `persistence.recorded_unit_state` references repo-wide; compile floor;
  owner-run sentinel green.
- FAILURE_ESCALATION: anything beyond an import-line diff -> stop + CONFLICT.

## Tasks
- [x] T1: bash mv the package + the state enum. DONE 03:00Z (12 twin files +
      recorded_unit_state.py at crystallizer/crystals/; zero intra-package
      persistence imports - the vocabulary was already self-contained).
- [x] T2: rewrite import prefixes in all affected files (file-tool edits):
      16 src edits across 13 files + 23 test edits across 18 files. DONE 03:10Z.
- [x] T3: grep gates + compile floor + story/board sync; owner sentinel run
      REQUESTED. DONE 03:15Z.

## Acceptance Criteria
- Both grep gates zero repo-wide; no diff outside import lines and file moves.
- Owner-run sentinel set green.

## Applicable Anti-Patterns
- [ ] No behavior edits smuggled into the sweep.
- [ ] No claim of execution ("Not run." until owner runs).

## Noting Behavior
- Story notes: sweep inventory, gate evidence, and anything non-mechanical.

## Notes
- DATETIME: 2026-07-10T02:50:00Z
  TYPE: PLAN
  CLAIM: Inventory (grep, pre-move): 23 files import persistence.crystals
    (11 src + 12 tests; 55 lines), 16 files import
    persistence.recorded_unit_state (5 src + 11 tests; overlap with the first
    set). Sweep covers ALL of them now (final paths - the epic's deferred-test
    ruling exists to avoid repeated re-pointing, which cannot happen here).
  EVIDENCE:
  - codex/context_compass/tickets/epics/2026-07-09_crystallizer_subsystem_decomposition_epic.md:1-999
  IMPACT: After S2 the EDGE LAW's "anything may import crystals/" is literal.
  NEXT: T1 move.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-10T03:15:00Z
  TYPE: FACT
  CLAIM: S2 BUILD COMPLETE. Moves: persistence/crystals/ ->
    crystallizer/crystals/ (11 twins + spell_crystal) + recorded_unit_state.py
    joined the vocabulary. Sweep: 39 import-line rewrites (16 src / 23 test)
    via file-tool replace_all, two uniform prefixes only. GATES GREEN: zero
    `persistence.crystals` and zero `persistence.recorded_unit_state`
    references repo-wide (src+tests). COMPILE FLOOR: spell_crystal.py +
    recorded_unit_state.py GREEN at their new homes (bash-moved files carry
    fresh replicas); ALL 12 edited src files Not run - the null-tail replica
    variant hit every one (shortening edits leave the mount replica at the old
    byte length, null-padded); disks current via file-tool edit confirmations;
    the definitive check is the owner-run pytest against the real filesystem.
    Execution: Not run - sentinel set requested (same 4 commands; restore and
    persistence suites sit on moved imports).
  EVIDENCE:
  - src/melder/crystallizer/crystals/ (13 files)
  - codex/context_compass/tickets/stories/2026-07-09_crystals_vocabulary_move_up_story.md:1-999
  IMPACT: Emitters now import the vocabulary without touching subsystem
    internals - the friction the owner flagged is gone.
  NEXT: owner sentinel run; on green, open S3 (asset_management extraction).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Mechanical vocabulary move-up per V3; entry gate satisfied by the epic's
architecture patch; sweep executed in one pass; sentinel rerun closes it.
