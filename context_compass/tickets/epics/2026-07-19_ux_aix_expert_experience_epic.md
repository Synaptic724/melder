# Epic: UX/AIX Expert experience exploration

## Metadata
- Epic ID: EPIC-2026-07-19-ux-aix-expert
- Status: pending
- Owner: cowork
- Agent Name: helper_f
- Priority: p2
- Created: 2026-07-19T12:52:00Z
- Updated: 2026-07-19T12:52:00Z

## Objective
The operator's tier: CrystallizerBootstrap pod restart, external persistence meshes (user DB callables), profile/checkpoint operations, group composition and campaign evolution, synthesis previews, class_wraps-built custom decorators over bound spells, multi-frame orchestration.

## Ticket Contract
- ENTRY_GATE: owner directive 2026-07-19 ("explore all the ways a user might use the
  library beginner -> intermediate -> expert -> Master... so we can properly explore
  what we need in init"). Examples live in UX_and_AIX_experiences/04_expert/.
- EXECUTION_BOUNDARY: UX_and_AIX_experiences/04_master/ examples + findings notes ONLY.
- DEPENDENCIES: init composition story (the 66-name root is the surface under test);
  prior tiers' findings.
- EXIT_GATE: every example runs green on the owner's 3.14t; every discovered
  init-surface gap either landed on the init story or recorded as a rejected
  curation call with reasons; owner walkthrough of the tier.
- FAILURE_ESCALATION: DECISION_REQUEST on any gap whose fix would widen the public
  surface beyond the ConduitWard law.

## Noting Behavior
- MEASURE per authoring wave (examples written, surfaces exercised, gaps found).
- DECISION for every init-surface change the tier proposes.

## Notes

## DECISION - 2026-07-25 19:23 UTC - tier renamed to EXPERT (README ladder match)
  RULING: owner (2026-07-22) - the ladder is Beginner/Intermediate/Advanced/
    Expert per the shipped README. This epic (formerly "Master", folder
    04_master) is now the EXPERT tier: AR rooms, transactions, checkpoints,
    governed mutation, external DB meshes. Folder renamed 04_master ->
    04_expert. Historical notes below keep their original wording.
  REREAD: OPTIONAL
  SCORE_0_TO_10: -

## Context / Handoff Summary
Method: every example imports melder as md ONLY - a deep-path import in an example
IS the finding. Examples are runnable scripts with honest asserts; they ride the
owner's 3.14t runs (device VM cannot import the runtime).
