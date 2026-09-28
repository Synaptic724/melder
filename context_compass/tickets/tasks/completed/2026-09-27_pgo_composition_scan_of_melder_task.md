

# Task: Scan Melder's own object composition to size the PGO ceiling against real shapes

## Metadata
- Task ID: TASK-2026-09-27-pgo-composition-scan-of-melder
- Story: STORY-2026-09-27-pgo-strategy-exploration
- Status: done
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-27T19:53:07Z
- Updated: 2026-09-27T19:53:07Z
- Completed: 2026-09-27T19:53:07Z
- Summary: `tests/experimentation/pgo_composition_scanner.py` (static AST, no import) scanned src/melder: 612
  classes, 373 with `__init__`; 58% take no object collaborator, 23% one, 8% two, 9% three-four, 2% five-eight,
  none nine or more; chain depth at most 5 (76% at depth 0-1); largest tree 17 classes. The experiment's ceiling
  for those widths is 183-320 ns per creation, almost all of it the constant door.

## Objective
Owner directive (2026-09-27T19:53:07Z): before judging PGO on synthetic 8-wide, 16-wide or 6-deep shapes, measure
the shapes a
real codebase composes - Melder itself - and estimate the ceiling against that distribution.

## Ticket Contract
- ENTRY_GATE: the exploration story; task 0's per-shape ceiling.
- EXECUTION_BOUNDARY: one new tool under `tests/experimentation/`; artifacts; no src edits.
- DEPENDENCIES: task 0's model (door 183 ns; 45 ns per singleton read; 20 ns per transient site).
- EXIT_GATE: the scan recorded and the estimate reported.
- FAILURE_ESCALATION: none.

## Scope Boundaries
- In scope: constructor collaborator width, chain depth, tree size, inheritance depth; the ceiling per bucket.
- Out of scope: existence (singleton vs transient) of each class - not visible statically; user applications.

## State Transition Event
- from_state: draft
- to_state: done
- transition_reason: Tool written, run and recorded in one pass (2026-09-27T19:53:07Z); closure pre-approved.

## Steps / Checklist
- [x] Scanner: width, plain-vs-collaborator split, depth, tree, MRO depth, top lists, bucket ceilings.
- [x] Run on src/melder; output recorded under artifacts/pgo_strategies_20260927/.
- [x] Run Ticket Microcycle during execution.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- tests/experimentation/pgo_composition_scanner.py
- artifacts/pgo_strategies_20260927/melder_composition_scan_20260927.md

## Files / Paths Impacted
- tests/experimentation/pgo_composition_scanner.py (new; no src change, no notch)

## Validation
- The scan ran on the device tree (0 modules skipped). Owner-run: Not run.

## Risks / Rollback Notes
- Collaborators are matched by simple annotation name inside the package; enums such as `Existence` and
  `Permissions` count as collaborators, so real object width is slightly lower than reported.

## Applicable Anti-Patterns
- [x] No claim about user applications from Melder's own shapes without saying so.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed (closure pre-approved; estimate reported in chat)
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/pgo_strategies_20260927/melder_composition_scan_20260927.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: promoted into the catalogue when a strategy ships.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: object composition; PGO ceiling.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-27T19:53:07Z
  TYPE: MEASURE
  CLAIM: Melder's own composition is narrow and shallow: of 373 constructors, 218 take no package-class
    collaborator, 84 take one, 31 two, 32 three or four, 8 five to eight, none more (widest: SpellCodegenModel 8,
    Conduit 7, TransactionMediator 6, SpellSpaceMeld 6, SpellValidationContext 6, FrameACLProfile 6); 1105 of
    1409 constructor parameters are plain data. Chains: depth 0 for 218, 1 for 76, 2 for 29, 3 for 27, 4 for 16,
    5 for 7 (deepest: CodegenTransactionContext, FrameProjectionSet, SpellSpaceMeld, the Rift views). Trees:
    at most 17 reachable classes (the codegen creation states); 89 classes reach 1-2. Inheritance depth inside
    the package is 2 for 388 classes (the Cleanable base plus one) and never above 3. With task 0's model the
    ceiling for the common widths is 183 ns (width 0), 203-228 (1), 223-273 (2), 243-318 (3-4): the door is
    60-90% of it; the singleton-read machinery adds 45 ns per collaborator only when that collaborator is a
    stored singleton. Not visible statically: which classes are constructed per operation and which are
    singletons, and what user applications compose.
  EVIDENCE:
  - artifacts/pgo_strategies_20260927/melder_composition_scan_20260927.md
  - tests/experimentation/pgo_composition_scanner.py:1-45
  IMPACT: The owner's 8-wide, 16-wide and 6-deep priors do not describe this codebase; for shapes like these,
    profile-guided body specialization is worth 20-90 ns per creation and the profile-free door fold is worth
    ~180 ns. The squeeze for PGO proper is not justified by these shapes; the door is.
  NEXT: owner decides: park the PGO epic and open a small door-fold task, or continue on singleton-heavy
    evidence from a user application.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
STATE 2026-09-27T19:53:07Z: DONE. Scan recorded; estimate with the owner.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
