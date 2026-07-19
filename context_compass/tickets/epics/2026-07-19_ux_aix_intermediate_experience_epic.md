# Epic: UX/AIX Intermediate experience exploration

## Metadata
- Epic ID: EPIC-2026-07-19-ux-aix-intermediate
- Status: pending
- Owner: cowork
- Agent Name: helper_f
- Priority: p2
- Created: 2026-07-19T12:52:00Z
- Updated: 2026-07-19T12:52:00Z

## Objective
The working developer's tier: SpellBinder fluent binding, spellframes and contracts (SpellMap/SpellContract), SpellSpace scoped resolution, spellbook and aether configuration (+builders), conduit linking and the ConduitCloud, SpellIndex membership verbs, crystallizer activation + first checkpoint.

## Ticket Contract
- ENTRY_GATE: owner directive 2026-07-19 ("explore all the ways a user might use the
  library beginner -> intermediate -> expert -> Master... so we can properly explore
  what we need in init"). Examples live in UX_and_AIX_experiences/02_intermediate/.
- EXECUTION_BOUNDARY: UX_and_AIX_experiences/02_intermediate/ examples + findings notes ONLY.
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

## Context / Handoff Summary
Method: every example imports melder as md ONLY - a deep-path import in an example
IS the finding. Examples are runnable scripts with honest asserts; they ride the
owner's 3.14t runs (device VM cannot import the runtime).
