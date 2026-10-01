# Story: Meld door strategies - measure D1-D4 on the live door, then ship the certified ones

## Metadata
- Story ID: STORY-2026-10-01-meld-door-strategies
- Epic: EPIC-2026-10-01-static-codegen-and-door-strategies
- Status: ready
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-10-01T00:55:51Z
- Updated: 2026-10-01T00:55:51Z

## User Narrative
As the Melder owner, I want the warm lane of `Conduit.meld` and `SpellSpace.meld` measured with each door
strategy installed over the real entries - guard folding (D1), executor hold with epoch re-validation (D2),
route inline for singleton roots (D3), the instance at the door (D4) - so that the 0-2 object melds most users
make, where the door IS the cost (~130-180 ns, the whole of a 164-177 ns singleton meld), get the strategies
that are proven to win and none that are guessed.

## Value / MRP Alignment
The plan-level strategies do nothing for a warm singleton meld, which never enters a plan. The door strategies
are predictions (-30..-40 ns for D1, -10..-20 for D2, -60..-70 for D3, ~80-90 ns per singleton meld for D4) and
the harness discipline that certified S1/S8/S2a applies unchanged: a door harness installs variant doors on a
live conduit over the real entries and times melds by name; the table decides. Every door strategy keeps what a
meld returns after purge, cleanup, notch, transfer and pool return - each retirement path must bump the epoch
the door compares, and that is verified in source before any door is built.

## Ticket Contract
- ENTRY_GATE: S1 landed; the door harness task routed; patch docs (component: Meld Resolution Runtime, Conduit
  Runtime; code description: the guard ladder and epoch bumps) written before any door edit.
- EXECUTION_BOUNDARY: harness: `tests/experimentation/` (new module), reads of `conduit.py` (warm lane),
  `meld.py` (`_fast_meld_doors`, `_fast_input_doors`, `_door_epoch`), `spell_space.py`; implementation: the
  warm lanes of `Conduit.meld` and `SpellSpace.meld`, the entry minting in the door subclasses, the epoch bumps
  on every retirement path, tests.
- DEPENDENCIES: the certification harness story (method); S1 (so the plan numbers under the door are current).
- EXIT_GATE: the door table (plain vs D1 vs D2 vs D3 vs D4 vs certified set) landed; each shipped door with a
  differential test over purge/cleanup/notch/transfer/pool return; suites green; owner-run gauntlet.
- FAILURE_ESCALATION: DECISION_REQUEST on any retirement path that does not bump the epoch today (D4's
  precondition); BLOCKER if the live door cannot be instrumented without a src change.

## Requirements (Functional)
- The harness measures melds by name and by id, singleton and `many` roots, automatic and dynamic posture.
- A shipped door returns exactly what the plain door returns after every retirement path.

## Requirements (Non-Functional)
- A door strategy ships only when the table shows a win on the singleton meld and no loss elsewhere.

## Scope Boundaries
- In scope: the door harness, D1-D4, the epoch-bump audit, tests, docs.
- Out of scope: the plan bodies (other stories); hooks semantics; the dynamic gate ticket.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Drafted from the epic's door section and the owner's split (2026-10-01T00:55:51Z); opens
  after S1.

## Dependencies / Related Work
- tickets/epics/2026-09-27_adaptive_creation_contexts_epic.md (Concrete Strategies: door strategies D1-D4)
- tickets/stories/2026-09-28_codegen_strategy_certification_harness_story.md (the method)
- tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md (melder_2's single-check fast door lever)

## Tasks (Implementation Checklist)
- [ ] Task: audit in source every retirement path for its `_door_epoch` bump (purge, cleanup, notch, transfer,
      pool return, SpellSpace release); record the matrix.
- [ ] Task: build the door harness over the live door and land the D1-D4 table.
- [ ] Task: per certified door strategy, patch docs, implementation, differential tests, landing.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- The table exists with the certified door set named; each shipped door keeps every result after every
  retirement path, proven by tests; owner-run numbers recorded.

## Validation / Test Plan
- The harness (VM); unit tests on the entry shapes; component tests through real conduits and spaces across the
  retirement matrix; owner-run gauntlet.

## UX / API / Data Notes
- No public API change.

## Risks / Mitigations
- A retirement path without an epoch bump -> the audit comes first; D4 is refused until every path bumps.
- melder_2's gauntlet lane names a single-check fast door lever -> coordinate through the mailbox before any
  door edit.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.
- [ ] No perf claim from agent-side runs; ranking numbers are owner-run.

## Open Questions
- Does every retirement path bump `_door_epoch` today (D4's precondition)?
- Does the hooks flag fold into the epoch without changing when a temporary hook map becomes visible (D1)?

## Decision Log
- 2026-09-30T19:54:46Z (owner): most people meld 0-2 objects, so a range of strategies is wanted. fable_0: the
  door strategies D1-D4 drafted as predictions.
- 2026-10-01T00:55:51Z (owner): non-PGO strategies first, as their own epic. fable_0: the doors are static (rows
  and posture), so this story is here; harness before any door edit.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/pgo_strategies_20260927/ (the door table lands beside the plan table)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: promoted into the canonical maps when the story ships.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - meld doors; guard ladder; door epoch; retirement paths
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-10-01T00:55:51Z
  TYPE: HYPOTHESIS
  CLAIM: Predicted door savings (unmeasured): D1 -30..-40 ns, D2 -10..-20 ns, D3 -60..-70 ns of a 170 ns singleton
    meld, D4 ~80-90 ns per singleton meld; the warm lane today pays about twelve attribute reads, one dict get,
    the four-guard ladder, the executor frame and its store read, and the `_cache_emit_required` pair.
  EVIDENCE:
  - tickets/epics/2026-09-27_adaptive_creation_contexts_epic.md:230-262
  - src/melder/aether/conduit/conduit.py:4755-4820
  IMPACT: The harness turns these into measurements before any door is touched.
  NEXT: opens after S1 lands; the epoch-bump audit is its first task.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-01T01:33:15Z
  TYPE: ALIGNMENT_CHECK
  CLAIM: Owner (2026-10-01): Melder's real use is dynamic, and the dynamic checks are the point - a meld must know
    whether the spell can have changed under it, and those checks lead to the ticket, the rebuild window and the
    validation reruns. Agreed, and D5 is bound by it: a dynamic warm lane keeps every guard inline and in order
    (epoch compare, context identity, `_spellbook_validation_required`, `resolution_required`, ticket append /
    closed / enabled, the post-admission `resolution_required` re-check, executor under the ticket, release in
    `finally`) and removes only the door frame, the keyword marshaling and the `_execute_admitted` frame; every
    non-admitted case (gate closed or draining, flag set, hooks, unhashable input) falls through to the full lane
    unchanged. Gates that are not per-spell chokepoints (link/sever, transfer, ChangeControl dirty roots) must be
    proven covered by a live read or an epoch bump in the audit; an uncovered gate refuses D5 or gets a bump.
  EVIDENCE:
  - src/melder/aether/conduit/meld/conduit_meld.py:384-470
  - src/melder/aether/conduit/meld/conduit_meld.py:555-610
  - src/melder/aether/conduit/meld/meld.py:826-891
  - src/melder/utilities/synchronization/creation_gate.py:349-418
  - src/melder/aether/conduit/conduit.py:4754-4820
  IMPACT: Door order becomes audit -> harness in dynamic posture -> D5 -> D1-D3 on both lanes; a dynamic meld's
    cost is UNMEASURED today (the -100..-200 ns is inferred from the automatic lane's 209 -> 111).
  NEXT: when this story opens, the epoch/gate audit first, then the harness measures a dynamic meld before any
    door edit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
STATE 2026-10-01T00:55:51Z: READY. Drafted under the static epic; opens after S1 lands with the epoch-bump audit.
Not routed.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
