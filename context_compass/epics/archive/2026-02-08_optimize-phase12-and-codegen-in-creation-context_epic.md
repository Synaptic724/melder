# Epic: Optimize Phase 12 and Codegen in CreationContext

- Completed: 2026-02-13
- Summary: Closed on user request to bulk-close all active tickets in this batch.

## Metadata
- Epic ID: EPIC-2026-02-08-optimize-phase12-and-codegen-in-creation-context
- Status: done
- Owner:
- Priority: p0
- Created: 2026-02-08
- Updated: 2026-02-13
- Target Window: 2026-Q1
- Related Program/Initiative: CreationContext execution fast-path program

## Problem / Opportunity
The current CreationContext integration is functional, but there is still avoidable
dispatch and branch overhead between the front door, CreationContext execution,
and the Phase 12 connector executors. This is the next focused optimization wave
to reduce per-call overhead and keep the codegen-only runtime model.

## MRP Alignment (Most Reasonable Product)
This epic hardens the core runtime shape: spell-bound CreationContext, explicit
no-hook and hook lanes, and existence-specialized emitted execution routes that
hand off directly into the Phase 12 executors with no legacy path dependency.

## Goals (Outcomes)
- Split CreationContext execution into explicit no-hook and hook compiled lanes.
- Emit existence-specialized codegen routes in CreationContext.
- Reduce front-door to Phase 12 connector call count and branch depth.
- Preserve override and mutation-override semantics while keeping non-override
  paths fast by default.
- Keep spell-bound CreationContext reusable across conduits.

## Non-Goals (Explicit Exclusions)
- Public API redesign of `Conduit.meld`.
- Reintroduction of `MeldContext` or legacy interpreter lanes.
- Broad refactors outside `meld` + CreationContext + Phase 12 codegen boundaries.

## Scope Boundaries
- In scope:
- `src/melder/aether/conduit/meld/creation_context/creation_context.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context_builder.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context_factory.py`
- `src/melder/aether/conduit/meld/meld.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
- Benchmarks and targeted unit tests for creation/execution hot paths.
- Out of scope:
- Non-runtime spellbook architecture changes unrelated to runtime execution.

## Success Metrics
- Lower warm-call median latency in Melder benchmark lanes that use transients.
- Observable reduction in call/branch overhead from CreationContext entry to
  Phase 12 execution routes.
- No semantic regressions in overrides, mutation overrides, and creation reuse.
- Existing unit suites and benchmark smoke runs remain green.

## Requirements (Functional + Non-Functional)
- Functional:
- No-hook lane entry must be directly callable and use its own emitted path.
- Hook lane must keep current semantics and remain isolated from no-hook path.
- CreationContext must accept caller creations and overrides as runtime inputs.
- Spell-bound CreationContext publish path must stay lock-minimal (write-lock only).
- Non-Functional:
- Keep hot-path checks lean; avoid defensive normalization inside CreationContext.
- Preserve deterministic behavior under concurrent usage across conduits.
- Keep codegen route ownership inside CreationContext-focused modules.

## Constraints / Assumptions
- Overrides and mutation overrides are low-frequency relative to non-override path.
- `Meld` remains front-door validator/binder.
- CreationContext instances are rebuilt after cleanup events when needed.

## Dependencies / External References
- `context_compass/architecture/src_architecture.md`
- `context_compass/components/src_components.md`
- `src/melder/aether/conduit/meld/creation_context/creation_context.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`

## Milestones (Track Progress)
- [ ] Milestone 1: Compile and wire split no-hook/hook CreationContext doors end-to-end.
- [ ] Milestone 2: Emit existence-specialized codegen routes from CreationContext to Phase 12 connectors.
- [ ] Milestone 3: Remove remaining generalized dispatch overhead in CreationContext hot paths.
- [ ] Milestone 4: Validate performance and semantic parity with focused tests and benchmark runs.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-02-08-creation-context-hook-lane-split - Separate and optimize no-hook vs hook lanes.
- [ ] Story: STORY-2026-02-08-creation-context-phase12-route-emission - Emit existence-specialized routes to Phase 12 connectors.
- [ ] Story: STORY-2026-02-08-creation-context-perf-parity-validation - Validate gains and ensure no semantic regressions.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: TASK-2026-02-08-creation-context-lane-doors-definition
- [ ] Task: TASK-2026-02-08-meld-entry-lane-door-wiring
- [ ] Task: TASK-2026-02-08-creation-context-phase12-nohooks-direct-route
- [ ] Task: TASK-2026-02-08-creation-context-phase12-hooks-direct-route
- [ ] Task: TASK-2026-02-08-creation-context-benchmark-regression-matrix
- [ ] Task: TASK-2026-02-08-creation-context-phase12-docs-and-ticket-sync

## Acceptance Criteria (Epic Done)
- CreationContext has explicit split no-hook and hook compiled entry routes.
- Existence-specialized codegen routes reach Phase 12 connectors directly.
- No override/mutation override behavior regressions in targeted tests.
- Benchmarks show measurable improvement relative to current baseline.
- User confirms acceptance criteria.

## Risks / Mitigations
- Risk: aggressive inlining/specialization can drift semantics.
- Mitigation: preserve lane-specific tests and parity assertions for overrides and mutation overrides.
- Risk: benchmark noise can hide regressions.
- Mitigation: use repeatable benchmark command set and compare medians over repeated runs.

## Validation / Test Approach
- Run targeted unit tests for meld front door, CreationContext lanes, and Phase 12 executors.
- Run benchmark scripts already used in current performance workflow.
- Keep validation reporting truthful when runs are skipped.

## Rollout / Adoption Plan
- Implement lane split first, then existence route emission, then tune hot-path dispatch.
- Keep each step isolated so regressions can be identified quickly.
- Keep tickets and handoff summaries updated after each pass.

## Open Questions
- UNKNOWN: final target threshold for warm and deep transient lanes after this wave.
- UNKNOWN: whether additional lane-specific compilers are required for mutation overrides.

## Decision Log
- 2026-02-08: User directed a new epic focused on Phase 12 and CreationContext codegen optimization.
- 2026-02-08: Story/task tree created for lane split, direct route emission, and validation.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
This epic is the next optimization pass after the initial CreationContext migration.
Focus is direct no-hook/hook lane split, existence-specialized codegen emission,
and tighter handoff into Phase 12 executors with measurable benchmark gains.
Initial explicit lane-door wiring landed in CreationContext and Meld.
