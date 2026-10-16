# Task: stamp_test_boots_its_own_aether - the managed stamp test installs the Aether it needs

## Metadata
- Task ID: TASK-2026-10-16-stamp_test_boots_its_own_aether
- Story: none (standalone backlog task; found by TASK-2026-10-16-spell_id_wording_near_spell_index)
- Status: draft
- Owner: user
- Agent Name: unassigned
- Agent Role: UNKNOWN
- Priority: p3
- Created: 2026-10-16T19:11:31Z
- Updated: 2026-10-16T19:11:31Z

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
- from_state: draft
- to_state: draft
- transition_reason: created as a draft from the spell_id_wording lane's unit runs ("if you found more bugs just add
  tickets", owner, 2026-10-16); test-only, parked until scheduled.

## Steps / Checklist
- [ ] Rerun the reproducer on the current tree (the frame file, then the stamp file; GIL off and on).
- [ ] Add the fixture to the stamp file; rerun the reproducer, the stamp file alone and the unit tree, both modes.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- The stamp test file with a fixture that installs the Aether it needs; the green runs.

## Files / Paths Impacted
- tests/unit/melder/spellbook/test_spell_managed_quantity_stamp.py

## Validation
- Not run (no fix written yet). The reproducer was run; see Notes.
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
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Board sync completed for successor routing or closure anchor update.

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
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; created 2026-10-16T19:11:31Z; evidence in Notes.
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

## Context / Handoff Summary
- Scope: test-only - the managed stamp test installs the Aether it needs; no src change, no notch.
- State: draft in backlog, not routed; found by TASK-2026-10-16-spell_id_wording_near_spell_index.
- Evidence: the FACT note; the runs under artifacts/spell_id_wording_20261016/runs/.
- Next: route it, rerun the reproducer, add the fixture, run both GIL modes.

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
