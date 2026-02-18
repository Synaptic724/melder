# Epic: Melder Core Deep Documentation Expansion

## Metadata
- Epic ID: EPIC-2026-01-17-melder-core-deep-docs
- Status: in_progress
- Owner:
- Priority: p0
- Created: 2026-01-17
- Updated: 2026-01-17
- Target Window: 2026-Q1
- Related Program/Initiative: Melder Core

## Problem / Opportunity
The current architecture and components docs remain too high-level, with partial coverage and handwavy descriptions. We need full, source-anchored detail for every core component, including explicit wiring and method-level call flows, so the docs can stand in for memory.

## MRP Alignment (Most Reasonable Product)
This is the durable documentation core. It captures the holistic system wiring and contracts to prevent repeated re-learning and refactor churn.

## Goals (Outcomes)
- Replace all remaining "partial/verify" placeholders with concrete definitions.
- Provide method-level call flows and wiring maps in `src_components.md`.
- Expand system-level architecture description with concrete, source-anchored detail.

## Non-Goals (Explicit Exclusions)
- Documenting non-core peripheral tools or tests.

## Scope Boundaries
- In scope: core Melder platform (Spectrum, CommandCenter, agents/pools/activities/missions, Iris, strategic command, concurrency, synchronization, core utilities).
- Out of scope: peripheral tools not required for core understanding.

## Success Metrics
- `src_architecture.md` and `src_components.md` provide standalone understanding without memory.
- All partial inventory entries are replaced by concrete definitions or explicitly marked out-of-scope.
- Wiring and call flows are explicitly documented in `src_components.md`.

## Requirements (Functional + Non-Functional)
- Use ASCII + Mermaid diagrams.
- Method-level call flows only in `src_components.md`.
- Record sources and file anchors for each major behavior.

## Constraints / Assumptions
- Focus on Melder core platform only.
- Deepest detail prioritized in components doc.

## Dependencies / External References
- `system_docs/src_architecture.md`
- `system_docs/src_components.md`
- `src/melder/` core modules

## Milestones (Track Progress)
- [ ] Milestone 1: Source deep inventory completed (all remaining partials).
- [ ] Milestone 2: Architecture doc expanded with concrete behavior.
- [ ] Milestone 3: Components doc expanded with method-level wiring/call flows.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-01-17-melder-core-deep-docs - Expand architecture and components with full detail.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-2026-01-17-melder-core-deep-docs

## Acceptance Criteria (Epic Done)
- All partial coverage items resolved with concrete details or explicit out-of-scope tags.
- Architecture and components docs provide rich, deterministic understanding of core wiring.
- Method-level call flow sections exist in `src_components.md`.

## Risks / Mitigations
- Risk: Scope creep into non-core tooling. Mitigation: keep a strict core list and mark out-of-scope items explicitly.

## Validation / Test Approach
- Documentation-only change; no tests required.

## Rollout / Adoption Plan
- Use these docs as the default orientation reference before any code work.

## Open Questions
- None.

## Decision Log
- 2026-01-17: Method-level call flows will be added only to `src_components.md`.

## Context / Handoff Summary
- Epic in progress. Components doc pass 1 completed: method-level call flows added and core runtime components expanded.
- Remaining: deeper wiring tables, concurrency/synchronization expansion, and final ticket closeout.

