# Task: stamp_test_boots_its_own_aether - the managed stamp test installs the Aether it needs

- Completed: 2026-10-16T20:23:39Z
- Summary: tests only, no notch - test_spell_managed_quantity_stamp.py installs a fresh Aether around
  each test (autouse `fresh_aether_world`), so it passes after the frame tests: red 1 failed / 39 passed,
  green 40 passed, with the GIL off and on. The unit tree passes in both modes apart from the asset-stamp
  test (assets 0.2.8249, package 0.2.8250, melder_1's rebuild to come). No release-note entry, no rebuild;
  the tests_components code-map entry rides TASK-2026-10-16-spell_id_wording_near_spell_index.

## Metadata
- Task ID: TASK-2026-10-16-stamp_test_boots_its_own_aether
- Story: none (standalone backlog task; found by TASK-2026-10-16-spell_id_wording_near_spell_index)
- Status: done
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p3
- Created: 2026-10-16T19:11:31Z
- Updated: 2026-10-16T20:23:39Z

## Objective
`test_stamping_into_a_real_root_store_creates_the_pool_there` in
`tests/unit/melder/spellbook/test_spell_managed_quantity_stamp.py` needs a booted Aether and installs none. Its stamp
asks a real `ConduitCreations` for the version's pool, `Creations.ensure_managed_quantity` registers the pool with
`ReleaseManagedSpell()`, and that singleton's first construction without its hosting Aether raises ValueError
("ReleaseManagedSpell is created by Aether at boot; construct Aether() first ..."). The autouse fixture `fresh_aether`
of `tests/unit/melder/aether/test_aetheric_frame.py` resets the Aether singleton after each frame test and boots none,
and `Aether.cleanup` retires `ReleaseManagedSpell` with it, so the stamp test fails whenever it runs after the frame
tests and passes alone. Outcome: it passes in any order, because it installs a fresh Aether around each test, as the
managed store tests already do (`_reset_world` and `fresh_registry` in `test_creations_managed_quantities.py`).

## Ticket Contract
- ENTRY_GATE: an active board row; the reproducer, rerun on the current tree, still fails in that order.
- EXECUTION_BOUNDARY: `tests/unit/melder/spellbook/test_spell_managed_quantity_stamp.py` only - an autouse fixture
  that installs a fresh Aether (and with it a fresh `ReleaseManagedSpell`) around each test. No src change, so no
  notch, no release-note entry and nothing to rebuild.
- DEPENDENCIES: none. No lane holds the file (melder_1's held list, M1-22, does not name it).
- EXIT_GATE: the frame file then the stamp file pass with the GIL off and on; the stamp file alone and the unit tree
  pass in both modes.
- FAILURE_ESCALATION: DECISION_REQUEST if the fix belongs in the frame tests instead (their fixture leaving a booted
  Aether behind), since that changes another file's setup.

## Scope Boundaries
- In scope: the stamp test's setup - the Aether it depends on.
- Out of scope: `ReleaseManagedSpell`'s construction rule (a first construction without its host is refused by
  design); `fresh_aether` in the frame tests; other test files with the same dependence (a sweep, if one is found,
  is its own ticket).

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: the fixture is in and green in both GIL modes (MEASURE, 2026-10-16T20:23:39Z); a routine
  test-only change closed by its assignee under the owner's go-ahead (DECISION, 2026-10-16T20:23:39Z).

## Steps / Checklist
- [x] Rerun the reproducer on the current tree (the frame file, then the stamp file; GIL off and on).
- [x] Add the fixture to the stamp file; rerun the reproducer, the stamp file alone and the unit tree, both modes.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- The stamp test file with a fixture that installs the Aether it needs; the green runs.

## Files / Paths Impacted
- tests/unit/melder/spellbook/test_spell_managed_quantity_stamp.py

## Validation
- Run (MEASURE note): the reproducer red then green, the file alone and the unit tree, GIL off and on.
- Recommended commands (repository root, Python 3.14):
  - python -X gil=0 -m pytest -q -p no:cacheprovider tests/unit/melder/aether/test_aetheric_frame.py
    tests/unit/melder/spellbook/test_spell_managed_quantity_stamp.py
  - the same with -X gil=1 -W ignore::UserWarning
  - python -X gil=0 -m pytest -q -p no:cacheprovider tests/unit; the same with -X gil=1 -W ignore::UserWarning

## Risks / Rollback Notes
- The fixture tears down whatever world an earlier test left; the stamp tests build stubs and a private store only,
  so nothing in that file relies on such a world.
- Rollback: remove the fixture.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed): the module docstring; tests_components rides the wording lane
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/spell_id_wording_20261016/runs/order_dependence_probe_gil0.txt
  - artifacts/spell_id_wording_20261016/runs/order_dependence_probe_gil1.txt
  - artifacts/spell_id_wording_20261016/runs/free_unit_gil1_with_stamp.txt
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: the runs stay in the wording lane's folder; rerun the reproducer when the task is scheduled.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - the Aether a unit test needs, and who boots it
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Multiple meaningful comments or authorized documents may hold findings directly; no forced
  body copy of every finding is required before ordinary continuation.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose, test (the fixture,
  tests/unit/melder/spellbook/test_spell_managed_quantity_stamp.py:29-50);
  created 2026-10-16T19:11:31Z; evidence in Notes.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-16T19:11:31Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The stamp test fails whenever it runs after the frame tests, with the GIL off and on, and passes alone. The
    frame file then the stamp file: 1 failed, 39 passed in both modes; the 23 unit files the wording lane touched,
    GIL on: 1 failed, 677 passed, the same test; the stamp file alone: 4 passed in both modes. The stamp
    (`Spell._add_owned_conduit`) asks the store for the version's pool; `Creations.ensure_managed_quantity` calls
    `ReleaseManagedSpell().register(...)`; `ReleaseManagedSpell.__init__` refuses a first construction without its
    hosting Aether. `fresh_aether` runs `Aether._reset_singleton_for_tests()` before and after each frame test,
    `Aether.cleanup` cleans `ReleaseManagedSpell`, whose cleanup resets its singleton, and nothing boots Aether again
    before the stamp file runs. The managed store tests install a fresh Aether around each test (`_reset_world`).
  EVIDENCE:
  - context_compass/artifacts/spell_id_wording_20261016/runs/order_dependence_probe_gil0.txt:1-69
  - context_compass/artifacts/spell_id_wording_20261016/runs/order_dependence_probe_gil1.txt:1-69
  - context_compass/artifacts/spell_id_wording_20261016/runs/free_unit_gil1_with_stamp.txt:1-78
  - context_compass/artifacts/spell_id_wording_20261016/runs/free_unit_stamp_alone_gil0.txt:1-2
  - context_compass/artifacts/spell_id_wording_20261016/runs/free_unit_stamp_alone_gil1.txt:1-2
  - tests/unit/melder/spellbook/test_spell_managed_quantity_stamp.py:87-131
  - tests/unit/melder/aether/test_aetheric_frame.py:13-23
  - src/melder/aether/conduit/creations/creations.py:1118-1174
  - src/melder/aether/conduit/creations/release_managed_spell.py:127-180
  - src/melder/aether/conduit/creations/release_managed_spell.py:182-213
  - src/melder/aether/aether.py:268-361
  - tests/unit/melder/aether/conduit/creations/test_creations_managed_quantities.py:112-125
  IMPACT: A unit run that orders the two files this way reports a failure that is no regression, and the stamp
    test's own result is lost in it.
  NEXT: When scheduled, rerun the reproducer, then add the fixture to the stamp file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T20:08:18Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Routed on the owner's go-ahead (chat 2026-10-16: asked whether to fix the stamp test while the wording lane
    waits, he answered "please go ahead and do your thing"). Plan: rerun the reproducer on the current tree (the
    frame file, then the stamp file, GIL off and on); add an autouse fixture to the stamp file that installs a fresh
    Aether around each test and re-points `Spellbook._aether` and `Conduit._aether`, as `_reset_world` does in the
    managed store tests; rerun the reproducer, the stamp file alone and the unit tree in both modes; close (tests
    only: no notch, no release-note entry, no rebuild).
  EVIDENCE:
  - tests/unit/melder/aether/conduit/creations/test_creations_managed_quantities.py:112-125
  - tests/unit/melder/spellbook/test_spell_managed_quantity_stamp.py:1-152
  IMPACT: The stamp test's result stops depending on which test module ran before it.
  NEXT: Rerun the reproducer on the current tree.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-16T20:23:39Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Red, then green. On the current tree the frame file then the stamp file gave 1 failed, 39 passed with the
    GIL off and on (the same ValueError). With the autouse fixture `fresh_aether_world` - a fresh Aether around
    each test, `Spellbook._aether` and `Conduit._aether` re-pointed, as `_reset_world` does in the managed store
    tests; 33 lines added, none changed - the same order passes, 40 with the GIL off and on, and the file alone 4
    in both modes. The unit tree, run in six chunks of its 508 files, passes in both modes (9678 passed, 3 skipped,
    7 xfailed each) except test_package_version_metadata.py's asset-stamp test, which fails alone as well: the
    generated assets are stamped 0.2.8249 while `__version__` is 0.2.8250 (melder_1's notch, its rebuild still to
    come) - outside this change. tests_components.md's code-map entry for the file (end_line 152, now 185) is held
    by melder_1 with the system docs; the wording lane updates it after the release (DECISION below).
  EVIDENCE:
  - tests/unit/melder/spellbook/test_spell_managed_quantity_stamp.py:1-50
  - context_compass/artifacts/spell_id_wording_20261016/runs/stamp_red_gil0.txt:1-69
  - context_compass/artifacts/spell_id_wording_20261016/runs/stamp_red_gil1.txt:1-69
  - context_compass/artifacts/spell_id_wording_20261016/runs/stamp_green_gil0.txt:1-2
  - context_compass/artifacts/spell_id_wording_20261016/runs/stamp_green_gil1.txt:1-2
  - context_compass/artifacts/spell_id_wording_20261016/runs/stamp_alone_after_gil0.txt:1-2
  - context_compass/artifacts/spell_id_wording_20261016/runs/stamp_alone_after_gil1.txt:1-2
  - context_compass/artifacts/spell_id_wording_20261016/runs/stamp_unit_tree_gil0_chunk00.txt:1-34
  - context_compass/artifacts/spell_id_wording_20261016/runs/stamp_unit_tree_gil0_chunk01.txt:1-25
  - context_compass/artifacts/spell_id_wording_20261016/runs/stamp_unit_tree_gil0_chunk02.txt:1-23
  - context_compass/artifacts/spell_id_wording_20261016/runs/stamp_unit_tree_gil0_chunk03.txt:1-23
  - context_compass/artifacts/spell_id_wording_20261016/runs/stamp_unit_tree_gil0_chunk04.txt:1-16
  - context_compass/artifacts/spell_id_wording_20261016/runs/stamp_unit_tree_gil0_chunk05.txt:1-122
  - context_compass/artifacts/spell_id_wording_20261016/runs/stamp_unit_tree_gil1_chunk00.txt:1-34
  - context_compass/artifacts/spell_id_wording_20261016/runs/stamp_unit_tree_gil1_chunk01.txt:1-25
  - context_compass/artifacts/spell_id_wording_20261016/runs/stamp_unit_tree_gil1_chunk02.txt:1-23
  - context_compass/artifacts/spell_id_wording_20261016/runs/stamp_unit_tree_gil1_chunk03.txt:1-23
  - context_compass/artifacts/spell_id_wording_20261016/runs/stamp_unit_tree_gil1_chunk04.txt:1-16
  - context_compass/artifacts/spell_id_wording_20261016/runs/stamp_unit_tree_gil1_chunk05.txt:1-95
  - context_compass/artifacts/spell_id_wording_20261016/runs/asset_stamp_test_alone_gil0.txt:1-73
  - context_compass/system_docs/tests_components.md:3194-3199
  IMPACT: The stamp test no longer depends on the module that ran before it; the exit gate holds for this change.
  NEXT: Close the task (tests only: no notch, no release-note entry, no rebuild).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T20:23:39Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Closed as a routine test-only change under the owner's go-ahead: the criteria are met, the targeted runs are
    green in both GIL modes, the one unit-tree failure is outside it (named above), and no src changed, so no notch,
    release-note entry or rebuild. The system-doc follow-up - tests_components.md's code-map entry for the file
    (end_line and loc 185; the fresh-Aether fixture in its note) and that document's index - rides
    TASK-2026-10-16-spell_id_wording_near_spell_index, which edits tests_components.md after melder_1 releases it.
    Independent review: none (a self-check is not one; not required for this change).
  EVIDENCE: context_compass/tickets/tasks/2026-10-16_spell_id_wording_near_spell_index_task.md:1-40
  IMPACT: The board loses the row; the wording lane carries one more held item.
  NEXT: None in this task.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
- Scope: test-only - the managed stamp test installs the Aether it needs; no src change, no notch.
- State: done (melder_0), 2026-10-16T20:23:39Z. Red then green in both GIL modes; the unit tree green apart from the
  asset-stamp test, which waits for melder_1's rebuild.
- Follow-up: tests_components.md's code-map entry for the file, carried by
  TASK-2026-10-16-spell_id_wording_near_spell_index after melder_1 releases the system docs.
- Evidence: the Notes; the runs under artifacts/spell_id_wording_20261016/runs/ (stamp_*).
- Next: none in this task.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->

<!--
Anything this project needs on every ticket of this kind goes in the region
above: extra fields, a compliance checklist, a link to a local convention.

The region is yours. An upgrade replaces every other line of this template with
the new version's text and carries this region across untouched, so a local
addition here is not a divergence you re-resolve on every upgrade - which is
what editing the rest of the template would cost you.
-->
