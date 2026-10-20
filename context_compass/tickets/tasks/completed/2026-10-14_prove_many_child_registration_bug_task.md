# Task: Prove that a slotted holder's disposal-bearing `many` child is disposed by the scope that first melded it

## Metadata
- Task ID: TASK-2026-10-14-prove_many_child_registration_bug
- Story: none - directly under EPIC-2026-10-14-many_child_follows_holder (opened under
  EPIC-2026-10-14-managed_spell_quantity as its prerequisite; moved when the owner opened the fix epic)
- Status: done
- Owner: user
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-14T02:38:36Z
- Updated: 2026-10-14T15:30:17Z

- Completed: 2026-10-14T15:30:17Z
- Summary: Defect mapped and proven on 0.2.8234: a slotted holder's disposal-bearing `many` child is
  registered in the meld's innermost scope, so 12 routes dispose it under a live holder; 11 red regression tests and
  5 green controls written (no src change, no notch). Closed on the owner's directive to fix it
  (TASK-2026-10-14-fix_many_child_follows_holder).

## Objective
Prove with regression tests that fail on today's code that a disposal-bearing `many` child built for a longer-lived
holder is recorded in the store of the scope that first melded the holder (a lesser conduit, a spellspace, a borrowing
conduit) instead of with the holder, so that scope's exit disposes a child the holder still uses. Map every holder
lifetime and meld route the defect reaches, from the source. No fix in this task: the owner continues after reviewing
the tests ("make regression tests first prove this is a problem then we'll continue show me the tests").

## Ticket Contract
- ENTRY_GATE: the board row `many_child_registration` routes here; the owner's request is recorded in Notes.
- EXECUTION_BOUNDARY: read-only investigation of `src/` (site-plan lowering and the creation-runtime door compiler,
  Creations and ConduitCreations, the Meld, ConduitMeld and SpellSpaceMeld doors); new regression tests under
  `tests/component/` (and `tests/integration/` if a case needs wider wiring); probes and run logs under
  `artifacts/many_child_registration_20261014/`. No change to `src/`.
- DEPENDENCIES: EPIC-2026-10-14-managed_spell_quantity (F10 and the prerequisite task line); the 0.2.8233 probe in
  `artifacts/melder_object_pools_20261011/`.
- EXIT_GATE: the owner has seen the tests and their red output (GIL on and off) and says how to continue.
- FAILURE_ESCALATION: DECISION_REQUEST when the corrected behaviour is not fixed by the owner's rule (for example what
  purging a holder does to its child); BLOCKER if a route cannot be reproduced through the public API.

## Scope Boundaries
- In scope: where a `many` child's disposal is recorded for each holder lifetime and first-meld route; red regression
  tests asserting the corrected behaviour (the child stays open while its holder lives and is disposed with it).
- Out of scope: the fix; Phase 6 (no change needed, epic Decision Log 2026-10-14); managed_spell_quantity itself.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the owner asked for the investigation and red regression tests before any fix (chat 2026-10-14).
- from_state: in_progress
- to_state: review
- transition_reason: the defect is mapped and proven by 11 red regression tests (GIL off and on, 2026-10-14); the
  owner reviews them and decides how to continue.
- from_state: review
- to_state: done
- transition_reason: the exit gate is met - the owner saw the red tests and directed the fix ("yeah fix the many
  child fix bro thats important make an epic for that too"), which continues in
  TASK-2026-10-14-fix_many_child_follows_holder.

## Steps / Checklist
- [x] Read the registration path in full (the many emission and the miss in site-plan lowering, the door compiler's
      many lines, `Creations.register_many`, ConduitCreations, the Meld doors) and record the finding.
- [x] Map holder lifetime x first-meld route to where the holder publishes and where its `many` child is recorded.
- [x] Write symptom-named regression tests for every affected route, plus controls that already pass.
- [x] Run them on the device VM with the GIL off and on and keep the red output.
- [x] Show the owner the tests and the output; record the owner's decision.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- `tests/component/melder/aether/conduit/test_conduit_component_many_child_disposed_with_its_holder.py`: 9 red
  route tests (7 parametrized routes, nested, override) and 5 green controls.
- `tests/integration/melder/conduit/test_conduit_integration_many_child_disposed_with_its_holder.py`: 2 red
  dynamic-route tests (borrowing root, cluster member).
- The route map in Notes; the probe and run logs under the artifact folder.

## Files / Paths Impacted
- `tests/component/melder/aether/conduit/test_conduit_component_many_child_disposed_with_its_holder.py` (new)
- `tests/integration/melder/conduit/test_conduit_integration_many_child_disposed_with_its_holder.py` (new)
- `context_compass/artifacts/many_child_registration_20261014/`

## Validation
- Run on the device VM, melder 0.2.8234, Python 3.14.7 free-threaded, `PYTHON_GIL=0` and `PYTHON_GIL=1`:
  `python -m pytest <both modules> -p no:cacheprovider -q -rA --tb=line` -> 11 failed, 5 passed in each mode; every
  failure is the corrected-behaviour assertion (the child already closed), never a precondition
  (`runs/red_regression_tests.txt`). The red result is the intended state until the fix lands.
- The full suite was Not run (the change adds tests only).

## Risks / Rollback Notes
- Red tests in the tree turn the suite red until the fix lands: whether they land as they are, wait for the fix or are
  marked is the owner's call (asked when they are shown). No `src/` change, so nothing to roll back in the library.
- A conjure writes its creation cache under the package root: run tests from the repository as the suite does.

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
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/many_child_registration_20261014/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none until the fix task closes; then kept as the evidence of the defect

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - where a disposal-bearing `many` child of a slotted holder is recorded and disposed
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_1 (synaptic_python_developer); prose, investigation and tests; the whole ticket;
  initial revision 2026-10-14T02:38:36Z; evidence in Notes.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-14T02:38:36Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Opened at the owner's request (chat 2026-10-14: "yeah so your claiming if a lesser conduit asks for a unique,
    you get a unique but your claiming all its assets are built by the lesser conduit for that unique? yeah this is a
    problem, not just for uniques but for almost all uniques that depend on root, so you need to investigate this make
    regression tests first prove this is a problem then we'll continue show me the tests"). Starting evidence: the
    0.2.8233 probe - a `unique` holder first melded through a lesser and a `unique_per_conduit` holder first melded in
    a spellspace both keep a child whose `close()` already ran once that scope ended; a holder built at the root kept
    its child open until root teardown. Plan: read the registration path, map every holder lifetime and route, write
    red tests asserting the corrected behaviour, run them GIL off and on, show the owner. No fix.
  EVIDENCE:
  - context_compass/artifacts/melder_object_pools_20261011/probe_disposal_many_under_slotted_holder.py:63-98
  - context_compass/artifacts/melder_object_pools_20261011/runs/probe_disposal_many_under_slotted_holder.txt:1-17
  - context_compass/tickets/epics/2026-10-14_managed_spell_quantity_epic.md:123-128
  - context_compass/tickets/epics/2026-10-14_managed_spell_quantity_epic.md:191-193
  IMPACT: The prerequisite of EPIC-2026-10-14 (F10) is now a routed task; the tests decide the fix's acceptance.
  NEXT: Read the many emission, the miss and the store routing in site-plan lowering, then `register_many`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-14T12:58:50Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The defect is one emission rule in the site-plan lowering, which serves the normal plan and every override
    key-set plan of the many_only and generalized families. A `many` step is placed where its one consumer is built,
    so the child of a slotted holder is emitted inside the holder's `_miss{i}`. A disposal-bearing many step
    registers with `many_store.register_many(...)`, and `many_store` is always the meld's innermost scope:
    `meld._spellspace_creations`, else `meld._conduit_creations`. The holder in the same miss publishes into `c{i}`,
    its own route: `unique` -> the owner conduit's store, `unique_per_conduit` -> `meld._conduit_creations`, lineage ->
    `meld._root_creations` (a lesser's meld points at its lineage root's store), cluster -> the elected leader's store,
    `unique_per_spell_space` -> the spellspace store. So the child goes with the holder only when the two routes name
    the same store. They differ when the holder's store outlives the melding scope: `unique` first melded through a
    lesser, a spellspace or a borrowing (linked) conduit; `unique_per_conduit` first melded in a spellspace; lineage
    first melded through a lesser or a spellspace; cluster first melded by a non-leader member; and any of these
    reached as a nested dependency of another holder. They agree for `unique` at its owner, `unique_per_conduit` at its
    conduit, lineage at its root, cluster at the leader, and `unique_per_spell_space`. The doors register no `many`
    child themselves; `register_many` appends to whatever store it is called on. Phase 6 skips `many`, so every such
    binding conjures. Not yet checked: the opt-in singleton specializer's straight-line form, which emits many steps
    through the manifest emitters with the same innermost-scope target (UNKNOWN whether it differs).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:764-770
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1307-1338
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1366-1471
  - src/melder/aether/conduit/meld/meld.py:340-353
  - src/melder/aether/conduit/conduit.py:375-394
  - src/melder/aether/conduit/creations/creations.py:715-786
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:498-695
  IMPACT: The route map decides the test matrix: automatic-world routes (lesser, spellspace, lineage, nested) and the
    dynamic routes (borrower, cluster member); a fix belongs in one place - the store a miss registers its children in.
  NEXT: Probe every route on a copy of src (GIL off and on) to confirm which reproduce before writing the tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T13:05:28Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Every route the FACT note predicts reproduces through the public API on melder 0.2.8234 (3.14.7
    free-threaded, a copy of src, GIL off and on, identical output): once the route's scope ends, the owning scope
    returns the same holder and the child's `close()` has already run. Routes: `unique` first melded through a
    lesser, a root spellspace, a lesser's spellspace and a borrowing root (link + contract, dynamic);
    `unique_per_conduit` through a root spellspace and a lesser's spellspace; lineage through a lesser and a root
    spellspace; cluster through a non-leader member (dynamic); `unique` reached as a per-conduit consumer's dependency
    in a lesser; a first build by an override meld through a lesser (key-set plan); and the same with the opt-in
    singleton specializer on (its warm root melds build no child). Controls behave: `unique`, per-conduit and lineage
    holders first built at their owner keep the child open through lesser and spellspace cycles until root teardown;
    a per-conduit holder at a lesser and a spellspace holder lose their child together with themselves. Each child
    was built once and closed once in total, so nothing is double-disposed - it is disposed early.
  EVIDENCE:
  - context_compass/artifacts/many_child_registration_20261014/probe_many_child_routes.py:145-477
  - context_compass/artifacts/many_child_registration_20261014/runs/probe_many_child_routes.txt:1-39
  IMPACT: The defect reaches every slotted lifetime except unique_per_spell_space, in automatic and dynamic worlds;
    the tests can cover the routes one by one and keep the controls as guards against an over-correcting fix.
  NEXT: Write the component module (automatic routes, nested, override, controls) and the integration module
    (borrower, cluster member), then run both GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T13:09:25Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The regression tests are written and red as intended on 0.2.8234: 11 failed and 5 passed with the GIL off and
    on, and every failure is the corrected-behaviour assertion (`child.closes == 0` after the first melding scope
    ended), never the precondition that the owning scope still returns the same holder. Component module: one test
    parametrized over 7 routes (unique through a lesser, in a root spellspace, in a lesser's spellspace; per-conduit in
    a root and in a lesser's spellspace; lineage through a lesser and in a root spellspace), the nested route and the
    override first build; 5 controls (holders built at their owner keep the child through scope cycles; a per-conduit
    holder at a lesser and a spellspace holder take their child with them) pass and guard the fix against
    registering children too far out. Integration module: the borrowing root and the cluster member. Each red test
    also asserts the child is closed exactly once at the holder's own teardown.
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_conduit_component_many_child_disposed_with_its_holder.py:184-356
  - tests/integration/melder/conduit/test_conduit_integration_many_child_disposed_with_its_holder.py:103-170
  - context_compass/artifacts/many_child_registration_20261014/runs/red_regression_tests.txt:1-111
  IMPACT: The defect is proven route by route; the fix's acceptance is these 11 turning green with the 5 controls
    staying green.
  NEXT: Show the owner the tests and the red output and ask the decisions below.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T13:09:25Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: Owner decisions before the fix: (1) how the red tests land - in the tree as they are (the suite is red until
    the fix), with `xfail(strict=True)` until the fix, or only together with the fix (recommended: together with the
    fix, in one change set, so CI never runs red); (2) what purging a holder does to its `many` child: today purge
    disposes only the holder and the child waits for its store's teardown, at the root as well (recommended: out of
    scope here, the tests assert only scope ends and teardown); (3) whether to open the fix task now - the fix is
    one rule, the store a shared site's miss registers its children in (the miss's own `c{i}` store), plus the
    opt-in specializer's straight-line form if it shares the rule.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1390-1451
  - tests/component/melder/aether/conduit/test_conduit_component_many_child_registration_trim.py:170-189
  IMPACT: Nothing in src/ changes until the owner answers; the tests are in the working tree, uncommitted.
  NEXT: Wait for the owner's answers; record them in the Decision Log of the epic and here.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-14T15:30:17Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner reviewed the red tests and directed the fix (chat 2026-10-14): "yeah fix the many child fix bro
    thats important make an epic for that too and target that first while Im gone"; then the rule: "if a root makes
    a unique its many should be owned by the root, corresponding to all the unique types, a unique per conduit is the
    same thing, same with unique per spellspace make sure the corresponding object owns it make tests to prove it
    first then hit it". The red tests land with the fix (answer 1 of the DECISION_REQUEST); purge semantics stay out
    of scope and open (answer 2 not given; recorded as open question 1 of the new epic); the fix task is opened
    (answer 3). This task is done; the work continues in TASK-2026-10-14-fix_many_child_follows_holder under
    EPIC-2026-10-14-many_child_follows_holder.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-14_many_child_follows_holder_epic.md:126-132
  IMPACT: The defect's proof is complete; the tests become the fix's acceptance.
  NEXT: None here; the fix task strengthens the tests and lands the fix.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Done (2026-10-14). The defect is mapped and proven (Notes); the 11 red regression tests and 5 controls live in
`tests/component/.../test_conduit_component_many_child_disposed_with_its_holder.py` and
`tests/integration/.../test_conduit_integration_many_child_disposed_with_its_holder.py`. The fix continues in
TASK-2026-10-14-fix_many_child_follows_holder (EPIC-2026-10-14-many_child_follows_holder).

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
