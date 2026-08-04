# Epic: Optimize Meld Hotpath

## Metadata
- Epic ID: EPIC-2026-06-07-optimize-meld-hotpath
- Status: in_progress
- Owner: codex
- Agent Name: tester_0
- Priority: p0
- Created: 2026-06-07T12:11:50Z
- Updated: 2026-06-07T12:11:50Z
- Target Window: 2026-Q3
- Related Program/Initiative: meld runtime hotpath optimization

## Problem / Opportunity
The existing forced-family harness already proves that the narrow emitted
`CreationContext` seam and the broader front-door `conduit.meld(...)` path are
not the same cost surface. The user explicitly redirected the lane away from
harness modification and toward real meld-hotpath optimization. That means the
work now is:
- establish a clean baseline using the current harness unchanged,
- map where the front-door cost actually lives across `Conduit`, `Meld`,
  `CreationContext`, `Creations`, `SpellSpace`, and `Spellbook`,
- then optimize the true runtime hot path rather than polishing benchmark
  presentation.

## MRP Alignment (Most Reasonable Product)
The MRP is not "a faster benchmark file." The MRP is a truthful optimization
program for the real runtime path that users pay on every meld call, while
preserving:
- no-GIL threading correctness,
- structural and conduit-local validation semantics,
- change-control and creation-gate behavior,
- correct reuse vs create behavior across every existence route.

## Ticket Contract
- ENTRY_GATE: the user explicitly ordered a new epic for meld-hotpath
  optimization and narrowed the immediate job to running the existing harness,
  not editing it.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit/meld/`
  - `src/melder/aether/conduit/creations/`
  - `src/melder/aether/conduit/spell_space/`
  - `src/melder/aether/conduit/conduit.py`
  - `src/melder/aether/spellbook/spellbook.py`
  - `tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py`
  - `codex/context_compass/tickets/epics/`
  - `codex/context_compass/tickets/tasks/`
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `tickets/tasks/2026-06-07_experiment_forced_phase10_phase11_creation_context_harness_task.md`
  - `system_docs/src_architecture.md`
  - `system_docs/src_components.md`
  - `system_docs/readable_src_graph.json`
- EXIT_GATE:
  - a baseline harness run is recorded under the new optimization lane,
  - the front-door vs creation-seam hot-path map is explicit,
  - first optimization slices are defined from measured bottlenecks rather than
    guesswork.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the requested optimization
  would require changing harness semantics or removing correctness gates without
  direct evidence.

## Goals (Outcomes)
- Record a stable baseline for the current meld hot path using the existing
  harness unchanged.
- Separate front-door meld cost from emitted `CreationContext` cost with
  concrete source evidence.
- Identify the first real runtime bottlenecks worth optimizing.
- Sequence the work so future optimization tasks stay on the real hot path.

## Non-Goals (Explicit Exclusions)
- No harness redesign in this epic's first task.
- No benchmark theater or table-format work as a substitute for runtime
  optimization.
- No correctness-regression shortcuts that bypass validation, gate, or reuse
  semantics.

## Scope Boundaries
- In scope:
  - meld-front-door runtime cost attribution
  - baseline harness execution
  - optimization-task planning for the real hot path
- Out of scope:
  - unrelated compiler exploration lanes
  - harness feature work
  - broad architecture redesign outside the meld path

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly created a new epic for meld-hotpath
  optimization and redirected the immediate work into that lane.

## Success Metrics
- One baseline run from the unchanged harness is recorded in this epic's child
  task.
- One evidence-backed map explains the extra cost layers on top of
  `CreationContext.execute_no_hooks(...)`.
- The next optimization task targets a measured runtime bottleneck.

## Requirements (Functional + Non-Functional)
- Preserve correctness under Python 3.14t / no-GIL threading.
- Preserve change-control, creation-gate, and spell validity semantics.
- Keep harness usage read-only in the first baseline slice.
- Use measured results and concrete source evidence before choosing any runtime
  optimization target.

## Constraints / Assumptions
- `Conduit`, `Meld`, and `CreationContext` are all hot-path surfaces, but they
  pay different kinds of cost.
- `many`, `unique_per_conduit`, `unique_per_spell_space`, and shared routes may
  expose different bottlenecks.
- Warm reuse and cold create must stay distinguished.

## Dependencies / External References
- Existing harness baseline lane:
  `tickets/tasks/2026-06-07_experiment_forced_phase10_phase11_creation_context_harness_task.md`
- Runtime docs:
  `system_docs/src_architecture.md`
  `system_docs/src_components.md`
  `system_docs/readable_src_graph.json`

## Milestones (Track Progress)
- [ ] Milestone 1: Baseline harness run recorded under the new epic.
- [ ] Milestone 2: Runtime hot-path attribution recorded with evidence.
- [ ] Milestone 3: First measured optimization target selected.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-06-07-meld-hotpath-baseline-and-attribution
  Run the unchanged harness and map the real front-door runtime path.
- [ ] Story: STORY-2026-06-07-meld-frontdoor-cost-reduction
  Reduce front-door overhead once the baseline cost layers are explicit.
- [ ] Story: STORY-2026-06-07-creation-seam-followup-optimization
  Optimize emitted execution or route-specific behavior only after front-door
  attribution is clear.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Run the unchanged harness and capture the baseline result.
- [ ] Task: Keep the optimization lane separated from harness-edit work.
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The unchanged harness has been run and recorded under this epic.
- The meld hot path is described with concrete source evidence and measured
  boundaries.
- Follow-up optimization tasks are derived from measured runtime bottlenecks.

## Risks / Mitigations
- Risk: optimize the benchmark instead of the runtime.
  - Mitigation: first task forbids harness edits and requires source-backed
    hot-path attribution.
- Risk: remove correctness gates that matter in no-GIL runtime conditions.
  - Mitigation: treat validation, locking, and gate semantics as first-class
    cost centers that need proof before change.

## Applicable Anti-Patterns
- [ ] No harness modification in the baseline task.
- [ ] No runtime optimization chosen from intuition alone.
- [ ] No closure while the baseline and attribution are still ambiguous.

## Validation / Test Approach
- Run the existing experiment harness unchanged.
- Use source-backed analysis for hot-path attribution.
- Record runtime measurements exactly; if a command is not run, report
  `"Not run."`

## Rollout / Adoption Plan
- Baseline first.
- Hot-path attribution second.
- Optimization tasks only after the runtime bottleneck order is explicit.

## Open Questions
- Which front-door layers dominate cold create versus warm reuse today?
- Are the biggest remaining costs in lookup/gating, creations-store dispatch,
  or route-specific emitted executor work?

## Decision Log
- The unchanged harness is baseline infrastructure, not the active edit surface
  for this epic's first slice.
- The real target is the meld runtime path, not benchmark presentation.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
  - meld front-door runtime layers
  - unchanged harness baseline
  - first measured optimization target
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-06-07T12:11:50Z
  TYPE: PLAN
  CLAIM: The user created a new epic and explicitly narrowed the immediate job:
    run the existing forced-family harness unchanged, map the real meld hot
    path, and treat optimization as the active lane instead of harness work.
  EVIDENCE:
  - user_instruction
  - tickets/tasks/2026-06-07_experiment_forced_phase10_phase11_creation_context_harness_task.md:1-906
  IMPACT: The first child task should be a read-and-measure baseline slice, not
    another experiment-design pass.
  NEXT: create a baseline task under this epic and route the board to it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-task sequencing, and measured
  optimization priorities.
- Add notes when the bottleneck order or optimization sequencing changes.
- Keep notes append-only and preserve UNKNOWN-first discipline.

## Context / Handoff Summary
This epic owns the meld-hotpath optimization program. The first slice is a
baseline run of the existing harness plus a source-backed map of the front-door
runtime path through `Conduit`, `Meld`, `CreationContext`, `Creations`,
`SpellSpace`, and `Spellbook`.
