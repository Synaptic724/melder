Completed: 2026-02-08
Summary: Finalized and validated deterministic phase IR contracts consumed by full codegen execution paths.

# Story: Phase Contract for Full Codegen Completeness

## Metadata
- Story ID: STORY-2026-02-07-phase-contract-codegen-completeness
- Epic: EPIC-2026-02-07-full-aot-codegen-cutover
- Status: done
- Owner:
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-08

## User Narrative
As a runtime/compiler maintainer, I want phase outputs to contain complete,
deterministic generation data, so that emitted executors never need runtime
interpretation or fallback discovery.

## Value / MRP Alignment
A full codegen runtime is impossible without a hard contract from phases.

## Requirements (Functional)
- Define and freeze IR schema for `phase2_5` and `phase8_11` payloads.
- Include all fields needed to emit:
- dependency resolution
- creation target routing
- lock/reuse/register semantics
- existing-creation handling
- override/mutation targeting and payload mapping
- Include deterministic signatures for invalidation.
- Remove any best-effort fields that imply fallback behavior.

## Requirements (Non-Functional)
- Deterministic ordering of all serialized plan arrays.
- Schema validation on export.
- Contract docs updated with examples.

## Scope Boundaries
- In scope:
- Schema, signatures, export and validation wiring.
- Out of scope:
- Executor generation implementation itself.

## Dependencies / Related Work
- STORY-2026-02-07-phase12-no-overrides-full-emitted
- STORY-2026-02-07-phase12-overrides-full-emitted
- STORY-2026-02-07-phase12-mutation-overrides-full-emitted

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-02-07-phase-contract-schema-finalization
- [x] Task: TASK-2026-02-07-phase-contract-population-and-signatures
- [x] Task: TASK-2026-02-07-phase11-signature-coverage-audit
- [x] Task: TASK-2026-02-07-phase8-10-ir-payload-completeness-audit
- [x] Task: TASK-2026-02-07-phase2-5-ir-payload-completeness-audit
- [x] Task: TASK-2026-02-07-phase11-variant-semantics-audit
- [x] Task: TASK-2026-02-07-phase11-signature-expansion
- [x] Task: TASK-2026-02-07-phase8-10-ir-payload-enrichment
- [x] Task: TASK-2026-02-07-phase2-5-ir-payload-enrichment
- [x] Task: TASK-2026-02-07-phase5-8-deterministic-ordering-audit
- [x] Task: TASK-2026-02-07-phase5-8-deterministic-ordering-hardening
- [x] Task: TASK-2026-02-07-phase11-ir-serialization-boundary-audit
- [x] Task: TASK-2026-02-07-phase11-ir-serialization-normalization
- [x] Task: TASK-2026-02-08-phase11-step-row-schema-export
- [x] Task: TASK-2026-02-07-contract-payload-immutability-hardening
- [x] Task: TASK-2026-02-07-phase12-compiler-ir-contract-tests

## Acceptance Criteria
- Exported IR fully defines generated execution semantics.
- Missing required fields fail fast at compile time.
- No runtime plan interpretation requirements remain due to schema gaps.

## Validation / Test Plan
- Schema validation tests.
- Deterministic signature tests.
- Contract fixture tests for all existence and override/mutation cases.

## UX / API / Data Notes
- Internal-only data contract; no public API changes.

## Risks / Mitigations
- Risk: oversized IR payload.
- Mitigation: normalized compact arrays and shared intern tables.

## Open Questions
- None.

## Decision Log
- 2026-02-07: contract must be complete enough to eliminate runtime interpretation.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Phase contract story establishes hard prerequisites for full codegen cutover.
Added follow-on tickets for signature/invalidation audit and phase8-10 payload
completeness audit, plus implementation tickets to enrich phase data contracts
for override and mutation-specialized codegen. Added additional Phase2-5 and
variant-semantics audit/enrichment tickets after deeper pass on phase export
consumers and mutation/override plan behavior. Added further tickets for
deterministic ordering hardening, schema-only Phase11 serialization boundaries,
contract payload immutability, and direct IR/compiler contract test coverage.
Deterministic ordering and contract payload immutability hardening are now
implemented with targeted regression tests. Phase12 compiler IR contract tests
are now added, including deterministic payload coverage and signature-driven
recompile guards. Phase11 serialization audit found live object leakage in
execution payloads; step-row schema export is now landed and follow-on consumer
migration tickets are now landed (no-overrides and overrides schema consume
paths complete). Legacy object-field retirement is now complete for Phase11 IR
(`steps`/`transient_plan` removed, schema-only transient path active).
Phase8-10 and Phase2-5 enrichment is now landed with deterministic schema rows
for occurrence topology, injection specs, patch-map targets, and Phase5
socket/edge structure. `phase8_11` and `phase2_5` signatures now include these
segments so semantic payload drift invalidates cached codegen artifacts.
Phase11 signature coverage audit and variant semantics audit are now closed with
regression coverage proving broad step-semantic invalidation and explicit
variant-label signature distinctness for overrides vs overrides-with-mutations.
Phase8-10 and Phase2-5 completeness audits are now closed with evidence-backed
consumer mappings, and their required deterministic fields are implemented in
the enriched IR export contract.
Phase5-8 deterministic ordering audit is now closed with additional findings:
queue-order canonicalization, DAG fallback dependency ordering, shared
canonical-occurrence canonicalization, and sorted contract override compilation;
regression tests now assert stable outputs across equivalent occurrence-map
insertion orders.
