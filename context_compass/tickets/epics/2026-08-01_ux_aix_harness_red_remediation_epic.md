# Epic: UX/AIX harness red remediation - 7 reds, 4 causes, 2 contract rulings

## Metadata
- Epic ID: EPIC-2026-08-01-ux-aix-harness-red-remediation
- Status: in_progress
- Owner: cowork
- Agent Name: examples_0
- Priority: p1
- Created: 2026-08-01T11:18:00Z
- Updated: 2026-08-01T11:18:00Z

## Objective
Drive the 7 reds from the owner's 2026-08-01 3.14t run to green WITHOUT destroying
the signal that produced them. Each red is classified library-defect or
example-defect on source evidence, and the two that touch public contract get an
owner ruling before any code moves.

## Problem / Opportunity
`pytest UX_and_AIX_experiences/pytest_examples` on 3.14t: **7 failed, 113 passed**.
The tiers exist as the evidence lane for init curation, so a red is a FINDING until
proven otherwise. Triage (TASK-2026-08-01-ux-aix-harness-failure-triage) resolved
the 7 into 4 independent causes. One of them is a real library defect that makes a
documented public capability unreachable; one is a genuine runtime-semantics
question; two are example rot.

The cheap move - patch four asserts until the bar is green - would have hidden the
library defect behind a healthier-looking number. That is explicitly not the plan.

## Context (why now)
Beginner tier closed 2026-08-01 at 41/41 green. Intermediate is the live tier and
owns 3 of the 7 reds; advanced owns 2 and is still `pending`. Fixing these is the
gate on resuming intermediate authoring.

## MRP Alignment
MRP, not MVP: disposal is foundational lifecycle behavior, not polish. Shipping a
runtime where the documented route to enabling teardown cannot work is exactly the
"trap" MRP exists to refuse. FINDING-1 gets fixed properly or ruled on explicitly -
not worked around in the examples.

## Ticket Contract
- ENTRY_GATE: owner 3.14t run with full tracebacks, triaged to 4 causes with
  file:line evidence. MET.
- EXECUTION_BOUNDARY: `UX_and_AIX_experiences/` examples and, ONLY under an owner
  ruling plus patch docs, `src/melder/aether/spellbook/configuration/` and the
  phase-11 override lane. No other source.
- DEPENDENCIES: owner rulings on STORY/TASK 1 (disposal) and TASK 3 (override
  singleton contamination).
- EXIT_GATE: all 7 reds green on an owner 3.14t run; every fix classified and
  evidenced; no assert weakened to hide a library behavior; canonical docs updated
  if runtime semantics change.
- FAILURE_ESCALATION: DECISION_REQUEST on anything widening or changing the public
  surface.

## Goals
- Correctly attribute every red to library vs example.
- Get an explicit owner ruling on both contract questions.
- Land fixes that keep each lesson TRUE, not merely green.

## Non-goals
- Broad refactor of `SpellbookConfiguration`.
- Redesigning `spell_override`.
- Touching tiers or lessons unrelated to the 7 reds.

## Scope Boundaries
In: the 7 failing examples/probes and the two source surfaces named above.
Out: every other example, all of `src/melder` beyond those surfaces.

## Child Tasks
- TASK-2026-08-01-ux-aix-harness-failure-triage - discovery record (the four
  findings with evidence). DONE, kept as the durable investigation.
- TASK-2026-08-01-disposal-idempotency-default-seed - FINDING-1, 4 reds, LIBRARY
  DEFECT, owner ruling required.
- TASK-2026-08-01-shared-config-unnamed-conjure-collision - FINDING-2, 1 red,
  example defect.
- TASK-2026-08-01-override-singleton-contamination - FINDING-3, 1 red, owner
  ruling required.
- TASK-2026-08-01-frame-posture-cheatsheet-count-drift - FINDING-4, 1 red, example
  defect.

## Requirements
- Functional: harness green on 3.14t.
- Non-functional: no lesson may assert a behavior the runtime does not actually
  have; no derived count may be hand-maintained after this epic.

## Acceptance Criteria
- [ ] Owner has ruled on FINDING-1 and FINDING-3.
- [ ] All 7 reds green on an owner-run 3.14t harness.
- [ ] Any runtime change carries patch docs and canonical doc updates.
- [ ] No fix consists solely of relaxing an assertion.

## Risks / Mitigations
- RISK: fixing examples first makes the suite look healthy and de-prioritizes the
  library defect. MITIGATION: FINDING-1 is p1 and the two safe one-liners are held
  until it is ruled.
- RISK: changing disposal seeding breaks configs that rely on defaults being
  present at validate(). MITIGATION: `_validate_required_properties_exist`
  backfills optional keys; confirm disposal's required-vs-optional status before
  any change.

## Validation Plan
Owner runs `pytest UX_and_AIX_experiences/pytest_examples -v` on 3.14t after each
ruling lands. No agent claims a green run.

## Decision Log
- 2026-08-01: hold the two safe example one-liners rather than half-fixing the
  suite, so all four land under one ruling pass.

## Noting Behavior
- Epic notes: program direction, cross-task tradeoffs, tranche order.

## Artifact Links (Optional)
- none yet; a `src/melder` change requires patch docs first per
  patch_framework_gating.md.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Notes

- DATETIME: 2026-08-01T11:18:00Z
  TYPE: PLAN
  CLAIM: Tranche order is deliberate and not the order of least effort.
    Tranche 1 = FINDING-1 (library defect, 4 reds, blocks a documented public
    capability). Tranche 2 = FINDING-3 (runtime semantics ruling). Tranche 3 = the
    two example one-liners, held until 1 and 2 are ruled so the red count keeps
    pointing at the library until the library is addressed.
  EVIDENCE:
    - tickets/tasks/2026-08-01_ux_aix_harness_failure_triage_task.md
  IMPACT: Prevents the classic failure where the suite goes green and the real
    defect survives.
  NEXT: Owner ruling on FINDING-1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-01T12:46:00Z
  TYPE: DECISION
  CLAIM: OWNER SCOPE LOCK - this epic is EXAMPLES ONLY. Two rulings, both binding on
    every future agent on this lane.
    (1) `generalized_singleton_specialization_enabled` is INTERNAL, owner-only,
    reserved for the owner's own testing. FINDING-5 is KILLED, not deferred. Do NOT
    read it, set it, document it, teach it in any tier, or open a ticket about it.
    Do not "just deregister it" either - it is not ours to touch. Any future agent
    finding it in `available_properties` should leave it exactly where it is.
    (2) MY LANE IS AUTHORING EXAMPLES. Not redesigning `SpellbookConfiguration`, not
    proposing runtime semantics changes. I drifted from a harness triage into
    library-internals redesign across two turns, and the owner stopped it correctly.
    The epic's own EXECUTION_BOUNDARY already said this and I overran it.
  EVIDENCE:
    - tickets/epics/2026-08-01_ux_aix_harness_red_remediation_epic.md:32-36
  IMPACT: All four remaining findings collapse to EXAMPLE work. No source change is
    proposed by this epic. No owner ruling is needed to proceed on any of them: the
    runtime is correct in every case, and every red is an example teaching something
    the library does not do.
  NEXT: Rewrite the failing examples/probes to the configure-then-freeze shape and
    to the true override rule. Source stays untouched.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Four causes, four tasks, one discovery record. Nothing edited in examples or source.
Blocked on two owner rulings; everything else is ready to execute behind them.
