Completed: 2026-02-08
Summary: Closed full AOT codegen cutover with generated-only runtime paths, parity/perf gates, and synchronized architecture docs.

# Epic: Full AOT Codegen Cutover (All Spells, Overrides, Mutations)

## Metadata
- Epic ID: EPIC-2026-02-07-full-aot-codegen-cutover
- Status: done
- Owner:
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-08
- Target Window: 2026-Q1
- Related Program/Initiative: Meld full codegen migration

## Problem / Opportunity
Current runtime still uses interpreter-style execution helpers for general plans.
That is partial codegen. We need full AOT-generated executors from phase plans,
for every spell kind and every override path, with no legacy fallback behavior.

## MRP Alignment (Most Reasonable Product)
Single execution model: phase-planned, generated executors only. Runtime becomes
dispatch + cache management, not planner/interpreter. This is the smallest
coherent long-term architecture for sustained speed and predictability.

## Goals (Outcomes)
- Full generated execution for all no-override plans.
- Full generated execution for override plans.
- Full generated execution for mutation-override plans.
- All spell lifetimes/existences supported in generated paths.
- No backward compatibility fallbacks.

## Non-Goals (Explicit Exclusions)
- Supporting legacy engine/interpreter behavior.
- Temporary dual-path execution.
- API redesign of `Conduit.meld`.

## Scope Boundaries
- In scope:
- Phase contract hardening so phases emit complete codegen data.
- Phase12 compiler generation for all plan variants.
- Runtime cutover to dispatch-only generated executors.
- Deletion of interpreter and engine execution dependencies.
- Tests, performance gates, and architecture docs.
- Out of scope:
- Non-meld unrelated subsystems.

## Success Metrics
- 100% meld execution routes run generated executors only.
- 0 runtime fallback branches to legacy/interpreter behavior.
- Override and mutation routes execute generated specializations.
- Performance meets or beats baseline for representative benchmarks.

## Requirements (Functional + Non-Functional)
- Functional:
- Phases must emit deterministic, complete IR for code generation.
- IR must include everything needed to emit lock/reuse/register logic per step.
- Generated executors must support all existences:
  `unique`, `unique_per_conduit`, `unique_per_conduit_lineage`,
  `unique_per_conduit_cluster`, `many`, `unique_per_spell_space`.
- Generated executors must support existing-creation spells in valid existences.
- Generated executors must support contract payloads and root positional args.
- Override and mutation executors must be generated from phase plans, not interpreted.
- Shape specialization must compile once per shape key and use bounded cache.
- Non-Functional:
- No backward compatibility fallback branches.
- Deterministic signature-based invalidation/recompile.
- Clear hard-fail errors for missing phase artifacts (not silent fallback).
- Runtime object model remains thread-safe and lock-order deterministic.

## Constraints / Assumptions
- Branch policy is no backward compatibility.
- Phase plan artifacts are the single source of truth.
- Existing frontend override contracts (TargetSpec/SocketRef/path registry) remain input contracts.

## Dependencies / External References
- `context_compass/architecture/src_architecture.md`
- `context_compass/components/src_components.md`

## Milestones (Track Progress)
- [x] Milestone 1: Phase IR contracts finalized and frozen.
- [x] Milestone 2: No-overrides full emitted executor path complete.
- [x] Milestone 3: Overrides full emitted executor path complete.
- [x] Milestone 4: Mutation-overrides full emitted executor path complete.
- [x] Milestone 5: Runtime cutover and legacy deletion complete.
- [x] Milestone 6: Full test and perf gates green.

## Stories (Required to Complete)
- [x] Story: STORY-2026-02-07-phase-contract-codegen-completeness - Phase data contract freeze for full generation.
- [x] Story: STORY-2026-02-07-phase12-no-overrides-full-emitted - Full emitted no-overrides executors.
- [x] Story: STORY-2026-02-07-phase12-overrides-full-emitted - Full emitted override executors.
- [x] Story: STORY-2026-02-07-phase12-mutation-overrides-full-emitted - Full emitted mutation-override executors.
- [x] Story: STORY-2026-02-07-runtime-cutover-delete-legacy - Dispatch-only runtime and legacy removal.
- [x] Story: STORY-2026-02-07-validation-perf-gates - End-to-end verification and perf guardrails.

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: Complete all linked stories.
- [x] Task: Keep docs (`src_architecture`, `src_components`) synchronized with each milestone.
- [x] Task: Produce benchmark deltas per milestone with repeatable scripts.

## Acceptance Criteria (Epic Done)
- No interpreter-style execution helper is used for meld execution.
- No runtime or meld fallback to legacy paths exists.
- All spell existences, overrides, and mutation overrides are generated-executor routes.
- Full regression suite and targeted perf gates pass.
- User confirms acceptance criteria.

## Risks / Mitigations
- Risk: generator complexity creates regressions.
- Mitigation: per-variant parity tests and deterministic signatures.
- Risk: cache explosion from override shapes.
- Mitigation: bounded LRU specialization cache and metrics.
- Risk: lock ordering regressions.
- Mitigation: explicit generated lock protocol tests.

## Validation / Test Approach
- Unit: generator output, signature invalidation, lock protocol, registration semantics.
- Component/integration: all existences + override/mutation matrices.
- Benchmark: cold compile, warm meld, mixed override shapes, spellspace and shared scopes.

## Rollout / Adoption Plan
- Implement behind branch-only full-cutover.
- Remove legacy execution modules in same migration set.
- Promote generated paths as only supported execution model.

## Open Questions
- Final cache key composition for override and mutation specialization.
- Whether to keep compiled source snapshots for diagnostics by default.

## Decision Log
- 2026-02-07: No backward compatibility; full codegen only.
- 2026-02-07: All execution variants must be generated from phase plans.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Epic created to replace partial codegen/interpreter hybrid with strict full AOT
codegen for all meld execution variants.
All linked implementation stories are now complete. The validation/perf-gates
story now includes a repeatable benchmark delta runner and runtime baseline
delta evaluation API so milestone-to-milestone regression checks are scriptable.

