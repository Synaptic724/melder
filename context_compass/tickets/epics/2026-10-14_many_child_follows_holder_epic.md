# Epic: many_child_follows_holder - a slotted holder's `many` children are owned and disposed with the holder

## Metadata
- Epic ID: EPIC-2026-10-14-many_child_follows_holder
- Status: in_progress
- Owner: user
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-14T15:29:53Z
- Updated: 2026-10-14T18:42:13Z
- Target Window: 2026-Q4
- Related Program/Initiative: EPIC-2026-10-14-managed_spell_quantity (requirement F10 depends on this epic)

## Problem / Opportunity
A disposal-bearing `many` child built for a slotted holder is registered in the store of the scope that melded the
holder (a spellspace, else the melding conduit), not in the store that owns the holder. When that scope ends first -
a lesser's pool return, a spellspace exit, a borrowing or member root's teardown - Melder runs the child's disposal
methods while the holder keeps handing the child out. TASK-2026-10-14-prove_many_child_registration_bug proved it
on 0.2.8234 for every slotted lifetime but `unique_per_spell_space`, in automatic and dynamic worlds (11 red
regression tests, 5 green controls), and found that the opt-in singleton specializer additionally builds and records
an unused child on every warm meld.

## MRP Alignment (Most Reasonable Product)
One ownership rule, stated by the owner, applied where children are registered: a child belongs to whatever owns
its holder. No new public surface, no change to warm meld paths, no change to purge semantics; the specializer
declines the graphs its straight-line form cannot express correctly instead of growing a second placement engine.

## Ticket Contract
- ENTRY_GATE: the owner's directive (chat 2026-10-14, Decision Log); the red regression tests from the prove task;
  patch docs written and linked before any `src/` edit.
- EXECUTION_BOUNDARY: site-plan lowering (`SitePlanEmission`), the generalized hydrator's specializing door and its
  emission helpers, their docstrings; regression and ownership tests; system docs, indexes and graph; the release
  note, the version notch, assets and llm_support.
- DEPENDENCIES: TASK-2026-10-14-prove_many_child_registration_bug (done); EPIC-2026-10-14-managed_spell_quantity
  waits on this epic for F10.
- EXIT_GATE: every task accepted; the red tests green and the controls green with the GIL off and on; the full tree
  green; the owner accepts.
- FAILURE_ESCALATION: DECISION_REQUEST when the fix would change purge semantics, a persisted format or cache
  generation, or a warm meld path; BLOCKER when the full tree shows new failures that cannot be resolved in scope.

## Goals (Outcomes)
- A slotted holder's `many` children are recorded in, and disposed with, the store that owns the holder: the
  spell-owning root for `unique`, that conduit for `unique_per_conduit`, that spellspace for
  `unique_per_spell_space`, the lineage root for lineage, the elected leader for cluster.
- A `many` root's own `many` children keep going to the meld's innermost scope, as the root does.
- The opt-in singleton specializer builds no child its holder does not need.

## Non-Goals (Explicit Exclusions)
- Purge semantics: purging a holder still disposes only the holder; its children wait for its store's teardown
  (unchanged; open question 1).
- Ownership transfer moving a holder's children with it (open question 2).
- The managed_spell_quantity pools and their per-object children (that epic's item (j)).

## Scope Boundaries
- In scope: where a `many` step built inside a shared site's first build registers; the specializer's eligibility;
  tests, docs, graph, release note, notch and rebuild.
- Out of scope: purge, transfer, managed pools, public API, warm paths.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: opened at the owner's request (chat 2026-10-14) to fix the proven defect while the owner is away.

## Success Metrics
- The 11 red regression tests pass and the 5 controls still pass, GIL off and on.
- New ownership tests show each child recorded in its holder's owning store and disposed exactly when that owner
  ends.
- Warm-path plan source unchanged (emission diff), the full tree green.

## Requirements (Functional + Non-Functional)
- F1 A disposal-bearing `many` step placed inside a shared site's first build (`_miss{i}`) registers in that site's
  store `c{i}` - the store the holder is published to - not in the meld's innermost scope.
- F2 A `many` step placed at the plan's top level keeps the innermost-scope store (unchanged).
- F3 The singleton specializer declines a graph in which a `many` step feeds a non-`many` step.
- N1 No warm meld path changes: misses and specializer eligibility only.
- N2 Lock discipline unchanged: `register_many` stays a leaf; children are built before the site's build lock.
- N3 The synaptic_python_developer code rules; rich docstrings on every touched method.

## Constraints / Assumptions
- Phase 6 needs no change (Decision Log 2026-10-14 of EPIC-2026-10-14-managed_spell_quantity).
- Site plans are emitted at hydration from manifest rows, so no persisted plan text has to be retired (to verify).

## Dependencies / External References
- tickets/tasks/completed/2026-10-14_prove_many_child_registration_bug_task.md (route map, probes, red tests)
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py

## Milestones (Track Progress)
- [x] Milestone 1: Defect proven route by route (prove task).
- [x] Milestone 2: Fix landed with green tests, docs, graph, release note and notch (0.2.8235, 2026-10-14).
- [ ] Milestone 3: Owner acceptance.

## Stories (Required to Complete)
- [ ] None - two tasks directly under the epic.

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: TASK-2026-10-14-prove_many_child_registration_bug - map and prove the defect (done 2026-10-14).
- [ ] Task: TASK-2026-10-14-fix_many_child_follows_holder - implement the owner's rule and land it (landed
      0.2.8235; in review).

## Acceptance Criteria (Epic Done)
- Both tasks done with recorded evidence; the owner accepts the fix.

## Risks / Mitigations
- A cold race's losing children now live until the holder's store ends instead of the melding scope -> bounded (one
  set per lost race), documented.
- Tests pinning the old registration target -> found and updated in the fix task with the reason recorded.
- The specializer loses some graphs -> it declined them for correctness; measured graphs without many children keep it.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Component and integration regression tests (prove task), ownership tests, specializer tests, the full tree with the
  GIL off and on, an emission diff for warm paths.

## Rollout / Adoption Plan
- A behaviour fix in the next release; no user action. Release note under the running note.

## Open Questions
- 1) Purge: should purging a holder dispose its `many` children with it (today they wait for the store's teardown)?
- 2) Ownership transfer: should a transferred holder's children move with it?

## Decision Log
- 2026-10-14: the fix rule. The owner: "if a root makes a unique its many should be owned by the root, corresponding
  to all the unique types, a unique per conduit is the same thing, same with unique per spellspace make sure the
  corresponding object owns it make tests to prove it first then hit it".
- 2026-10-14: this epic first, implemented while the owner is away. The owner: "fix the many child fix bro thats
  important make an epic for that too and target that first while Im gone you know what to do there implement a
  concrete fix for that"; "if you know what to do go ahead and implement all this stuff please".

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/many_child_registration_20261014/ (probes, red runs; shared with both tasks)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - ownership of a slotted holder's `many` children
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_1 (synaptic_python_developer); prose and design; the whole ticket; initial revision
  2026-10-14T15:29:53Z; the rule is the owner's, quoted in the Decision Log.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-14T15:29:53Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Opened at the owner's request to fix the proven defect first, while the owner is away. Tranche order: close
    the prove task (its exit gate is the owner's directive), open the fix task, strengthen the tests to prove
    ownership (recorded in the holder's store, disposed when that owner ends), patch docs, the site-plan fix, the
    specializer decline, full tree GIL off and on, docs, graph, release note, notch 0.2.8235, rebuild last; the fix
    task then goes to review for the owner.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-10-14_prove_many_child_registration_bug_task.md:1-60
  IMPACT: The managed_spell_quantity design waits; this epic unblocks its F10.
  NEXT: Strengthen the regression tests and add the ownership tests, red on 0.2.8234.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-14T17:19:37Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Milestone 2 reached: the fix landed as 0.2.8235 and its task is in review. The tranche ran in the planned
    order (tests red first, patch docs, src, the pinned unit test, green GIL off and on, full tree, docs, graph,
    notch, release note, rebuild last); invariant 4 holds (12/12 warm executor bodies identical). Nothing changed
    for purge or ownership transfer (questions 1-2). Found on the way and left to the owner: a flaky 0.2.8234 clock
    test (about 1% of runs) and the experimentation harness's prologue regex, which no longer matches a miss.
    EPIC-2026-10-14-managed_spell_quantity's F10 prerequisite is met for today's holders once this is accepted; its
    item (j) (children of a managed object destroyed alone) is still its own requirement.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-14_fix_many_child_follows_holder_task.md:215-349
  - context_compass/artifacts/many_child_registration_20261014/runs/full_tree_summary_gil1.txt:1-23
  IMPACT: The epic waits only on the owner's acceptance of the fix task.
  NEXT: On acceptance, close the fix task and this epic and run the closure syncs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

- DATETIME: 2026-10-14T18:42:13Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The owner asked whether the other slotted lifetimes are set up properly; TASK-2026-10-14-audit_slotted_lifetime_ownership
    answers it. For this epic's scope the answer is yes: on 0.2.8235 every lifetime's `many` children follow the
    holder's store on every probed route, including the two without a dedicated test (lineage in a lesser's
    spellspace, cluster in a member's spellspace). Its open questions now have reproducers and their own
    investigation tasks: question 1 (purge) is D5, question 2 (transfer) is D4. The audit also proved four defect
    groups outside this epic (cluster membership and ownership, D1-D2; instances dropped without disposal, D3;
    upgrade, D6), each opened as a ready task for the owner to turn into an epic.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-10-14_audit_slotted_lifetime_ownership_task.md:306-340
  - context_compass/artifacts/slotted_lifetime_audit_20261014/runs/probe_lifetime_owners_all_gil0.txt:1-80
  IMPACT: This epic still waits only on the owner's acceptance of the fix; questions 1-2 move to D5 and D4.
  NEXT: On acceptance, close the fix task and this epic; D4 and D5 carry the open questions.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Opened 2026-10-14 to land the owner's rule: a slotted holder's `many` children belong to whatever owns the holder.
The defect is proven (prove task, done) and the fix landed as 0.2.8235 (fix task, in review): children register
in the holder's store, the opt-in specializer declines graphs that feed a `many` step into a non-`many` step, the
full tree is green GIL off and on. Waiting on the owner's acceptance; open questions 1-2 (purge, transfer) stay
open and out of scope.

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
