# Task: Investigate a transfer with move_creations that moves a holder but leaves its many children behind

## Metadata
- Task ID: TASK-2026-10-14-investigate_transfer_leaves_holder_children_behind
- Story: none - D4 of EPIC-2026-10-14-slotted_lifetime_ownership_fixes (opened by
  TASK-2026-10-14-audit_slotted_lifetime_ownership, done)
- Status: review
- Owner: user
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-14T18:40:43Z
- Updated: 2026-10-15T00:07:24Z

## Objective
`TransferOfOwnership._move_creations` carries the transferred index members' entries to the target store; a
holder's `many` children are registered under their own spell ids and stay in the source store. Proven on
0.2.8235 (t4b): moving a `unique` holder alone, its child stays in the source store and the source's teardown
disposes it while the target serves the same holder; with `include_dependencies=True` the child spell moves and
its entries with it (t4). This is open question 2 of EPIC-2026-10-14-many_child_follows_holder, now with a
reproducer. Find how a holder's children could follow it and lay out options for the owner's epic.

The owner's rule this is checked against: a holder's `many` children belong to whatever owns the holder
(EPIC-2026-10-14-many_child_follows_holder).

## Ticket Contract
- ENTRY_GATE: the epic's board row routes it; the reproducer is rerun on the current tree; red tests fail before
  any src edit; the epic's patch docs are written, linked and mapped.
- EXECUTION_BOUNDARY: the code paths below, the fix, its tests and docstrings (owner directive 2026-10-14: fix it
  under EPIC-2026-10-14-slotted_lifetime_ownership_fixes); system docs, release note and notch with the epic.
- DEPENDENCIES: TASK-2026-10-14-audit_slotted_lifetime_ownership (the probe and its runs);
  EPIC-2026-10-14-many_child_follows_holder (0.2.8235).
- EXIT_GATE: root cause recorded; red tests red before and green after the fix, GIL off and on; the probe case
  clean; no warm meld path change; the owner accepts.
- FAILURE_ESCALATION: DECISION_REQUEST for every behaviour that is a design choice; BLOCKER if the reproducer no
  longer fails on the current tree (record it and stop).

## Scope Boundaries
- In scope: the defect named in the objective, its code paths and every caller that shares the cause.
- Out of scope: the fix itself; the other audit findings (their own tasks).

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: opened from the audit with a reproducer that fails on 0.2.8235, GIL off and on (owner directive,
  chat 2026-10-14: "make a task to investigate it and then we'll turn it into an epic").
- from_state: ready
- to_state: in_progress
- transition_reason: the epic's tranche reached D4 (code re-read, fix shape recorded, 2026-10-14).
- from_state: in_progress
- to_state: review
- transition_reason: the fix landed with its red tests green GIL off and on; the lane's full tree is green GIL off and
  on at 0.2.8240 and the change is promoted into the system docs (epic Notes 2026-10-14T23:39:45Z and
  2026-10-15T00:00:12Z); the owner accepts.


## Steps / Checklist
- [x] Read how `many` children are registered (`register_many`) and what a store knows of which holder built
      which child; record what a transfer can find.
- [x] Write a red test from the probe's t4b.
- [x] Lay out options (recording children per holder; moving children by holder; refusing a move that would split
      them) and their cost on the warm path, for the owner.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Root cause with evidence, red tests, and fix options for the owner's epic.

## Files / Paths Impacted
- `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py`
- `src/melder/aether/conduit/creations/creations.py`
- `tests/` (red tests, when the investigation runs)

## Validation
- Reproducer run on 0.2.8235 (Python 3.14.7t, GIL off and on, identical): see Notes.
- Not run: anything else (the investigation has not started).
- Reproduce (from a tree root with src/ and tests/):
  `PYTHONPATH=src:. python context_compass/artifacts/slotted_lifetime_audit_20261014/probe_lifetime_owners.py t4 t4b`

## Risks / Rollback Notes
- Investigation only; nothing to roll back.

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

## Open Questions
- Answered (owner, 2026-10-14: "moving the many is fine"): a moved holder's adopted children move with
  it (0.2.8238); since 0.2.8239 the move is the transfer default unless the caller passes
  `move_creations=False`.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/slotted_lifetime_audit_20261014/ (the probe and its runs, shared with the audit task)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: decided when the owner's epic closes

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - a moved holder's many children
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_1 (synaptic_python_developer); prose and evidence; the whole ticket; initial revision
  2026-10-14T18:40:43Z; the reproducer is the audit's probe. The rule and the directive are the owner's.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-14T18:40:43Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Opened from TASK-2026-10-14-audit_slotted_lifetime_ownership with a reproducer: probe case(s)
    t4 t4b fail the owner's rule on 0.2.8235 as described in the Objective, with identical output GIL off and
    on. The code paths below were read in full during the audit; the root-cause analysis, red tests and fix options
    are this task's work.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1506-1545
  - src/melder/aether/conduit/creations/creations.py:715-846
  - context_compass/artifacts/slotted_lifetime_audit_20261014/runs/probe_lifetime_owners_all_gil0.txt:31-48
  - context_compass/artifacts/slotted_lifetime_audit_20261014/probe_lifetime_owners.py:1-608
  IMPACT: The defect is real on today's tree; the owner can turn this task into an epic.
  NEXT: Rerun the reproducer on the current tree, then read the paths in Steps and record the root cause.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-14T18:55:12Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner turned the audit's tasks into one fix lane and put it first ("all these need to be fixed
    go ahead and target all these fixes since you have context first"); this task is now the epic's D4
    and covers the fix as well as the investigation (Ticket Contract updated).
    Scope per the owner's transfer guidance ("transfer of ownership with many can leave its objects behind
    optionally unless its a unique kind of some sort"): leaving a `many` spell's own objects behind stays legal;
    the `many` children built for a unique kind's holder are part of that holder and move with it.
  EVIDENCE: context_compass/tickets/epics/2026-10-14_slotted_lifetime_ownership_fixes_epic.md:147-159
  IMPACT: Investigation, red tests and the fix land here; docs, notes and the notch go with the epic's pass.
  NEXT: Wait for the epic's tranche order (D6 verdict, patch docs), then rerun the reproducer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-14T19:23:31Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Root cause re-read and fix shape chosen (shared with D5). Since 0.2.8235 a holder's disposal-bearing `many`
    children register in the holder's store under their own spell ids (`c{i}.register_many` in `_miss{i}`, before
    the build lock), so a store verb keyed by the holder (move, purge, retire) cannot reach them without scanning the
    child spell's bucket. Fix: after the holder publishes, the same miss moves its children out of their buckets into
    the holder's disposal record (`Creations.adopt_children`, cold path only: the child was just appended, so the
    identity scan from the bucket's end is O(1) in practice). The record (`HolderDisposalEntry`: holder, its methods,
    its children with theirs) is keyed by the holder's spell id, so extract/restore carry the children with the
    holder (transfer move), purge and every retirement dispose holder then children, and whole-store disposal keeps
    reverse creation order. A lost cold race, a pinned-override refusal or a failing holder constructor leaves the
    children in their bucket as today. Warm `_site_plan_executor` bodies are unchanged; only misses gain one line.
    Deliberate consequence: a `many` purge or live-creation probe of the child spell no longer counts children owned
    by a holder (disposing them there would recreate the many-child bug); 0.2.8235 tests that pin the bucket
    representation move to the holder record.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1319-1488
  - src/melder/aether/conduit/creations/creations.py:419-466
  - src/melder/aether/conduit/creations/creations.py:858-1137
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1506-1545
  - tests/component/melder/aether/conduit/test_conduit_component_many_child_disposed_with_its_holder.py:169-182
  IMPACT: D4 (move) and D5 (purge) fall out of one representation; O(1) by key on every retirement path.
  NEXT: Write the epic's patch docs from these decisions, then red tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T20:29:11Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Red test written and run on the 0.2.8237 scratch tree (Python 3.14.7t), identical GIL off and on: moving a
    unique holder alone with move_creations=True leaves its child in the source, and the source's teardown closes it
    (closes 1) while the target serves the holder - probe case t4b. The t4 control (holder moved with its
    dependencies) passes: the child's spell moves too and the target disposes holder and child once each.
  EVIDENCE:
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/landing/test_conduit_integration_holder_children_lifetime_0_2_8238.py:345-401
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/red_d4_d5_holder_children_0_2_8237_gil0.txt:1-21
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/red_d4_d5_holder_children_0_2_8237_gil1.txt:1-21
  IMPACT: The entry gate for the 0.2.8238 src edit is met for D4 (red before the fix, the right reason).
  NEXT: Implement the holder record and the miss adoption (0.2.8238) and rerun the module.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-14T20:30:45Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: 0.2.8238 mapping after re-reading the three patch docs and the code in full. (1) Creations patch "Before /
    after" -> creations.py: `HolderDisposalEntry` (item, methods, children; borrowed refs, no cleanup), `adopt_children`
    under the leaf store lock (slot must still hold the holder; identity scan from the bucket end; emptied buckets
    and their records dropped; tuple replaced in place, a holder without methods gets methods=[]), one dispatch
    `_dispose_entry` (tuple / bucket / holder record: holder methods, then children newest-first) used by whole-store
    disposal and purge, extract rows gain `children` and restore rebuilds the record -> unit tests (adoption with and
    without holder methods, missing child skipped, cleaned or swapped store refused silently, disposal order, purge,
    extract/restore round trip). (2) Codegen patch -> site_plan_lowering.py `_emit_miss`: one
    `c{i}.adopt_children(sid{i}, v{i}, ((sidN, vN), ...))` after publication inside the build lock and the
    `if v{i} is None:` branch, for exactly the children `_emit_many` registered -> emission diff over normal,
    override, door-held and nested shapes (only those misses differ). (3) Holder-children description -> the red
    module green GIL off and on; the 0.2.8235 many-child tests read the holder record. The specializer path needs no
    change: it declines every graph that feeds a many step into a non-many step. D3's two helpers stay in 0.2.8239.
  EVIDENCE:
  - context_compass/system_docs/patches/active/slotted_lifetime_ownership_2026_10_14/component_patch_creations.md:5-51
  - context_compass/system_docs/patches/active/slotted_lifetime_ownership_2026_10_14/component_patch_spellcompiler_codegen.md:5-29
  - context_compass/system_docs/patches/active/slotted_lifetime_ownership_2026_10_14/code_description_patch_holder_children.md:3-32
  - src/melder/aether/conduit/creations/creations.py:377-469
  - src/melder/aether/conduit/creations/creations.py:859-1226
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1319-1488
  IMPACT: Every retirement keyed by the holder reaches its children with one O(1) lookup; meld warm paths unchanged.
  NEXT: Implement (1) and (2) on the scratch tree as a landing script, then run the red module.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T20:53:11Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Landed as 0.2.8238. Extract rows of a holder carry `children`, restore rebuilds the record, so
    `_move_creations` (unchanged) carries the children to the target and its rollback brings them back. The t4b
    test and probe: the source's teardown leaves the moved holder's child open, the target disposes holder and child
    once (t4 control unchanged). Emission diff over eight shapes (normal, override, door-held, nested, unique root,
    plain child): every `_site_plan_executor` body identical; only misses with disposal-bearing children gain one
    `adopt_children` line. Release note section rewritten (the 0.2.8235 section, one subject); scopes.md and
    ownership.md say it; the example verified (passes on 0.2.8238, fails on 0.2.8237 at its documented line).
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:1302-1376
  - src/melder/aether/conduit/creations/creations.py:1377-1475
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1490-1499
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/emission_diff_d45_0_2_8238.txt:1-9
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/probe_t4_t4b_p5_0_2_8238_gil0.txt:10-18
  - release_docs/next_version_release.md:146-200
  IMPACT: D4 is fixed with no transfer code change; warm meld paths unchanged.
  NEXT: D3 (0.2.8239): red tests for default transfer, contract invalidation and many left behind.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T00:07:24Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Status to review. D4 (0.2.8238) holds at the end of the lane's pass: the audit probe's t4 and t4b show the
    holder's child moved with it (in neither the source store nor a bucket of its own), the source's teardown closing
    nothing and the child closed once with the holder at the target; the full tree is green GIL off and on at
    0.2.8240; the system docs carry the holder-record invariant and the transfer contract.
  EVIDENCE:
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/probe_lifetime_owners_all_0_2_8240_gil0.txt:30-47
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/full_tree_0_2_8240_gil0.txt:1-28
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/full_tree_0_2_8240_gil1.txt:1-20
  - context_compass/system_docs/src_architecture.md:974-986
  - context_compass/system_docs/src_components.md:6163-6190
  IMPACT: The task waits for closure with the epic.
  NEXT: Close with the epic once the owner accepts it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
In review (2026-10-15). Fixed as 0.2.8238 and accepted in substance by the owner ("moving the many is fine"): a
holder's extract row carries its adopted children and the restore rebuilds its record, so a moved holder's `many`
children move with it and a rollback brings them back; since 0.2.8239 the move is the transfer default. Red tests
green GIL off and on; the lane's full tree green at 0.2.8240; promoted into the system docs. Remaining: closure
with the epic; commit and push are the owner's.

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
