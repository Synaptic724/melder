# Story: Expand core architecture and components documentation

## Metadata
- Story ID: STORY-2026-01-17-commandops-core-deep-docs
- Epic: EPIC-2026-01-17-commandops-core-deep-docs
- Status: in_progress
- Owner:
- Priority: p0
- Created: 2026-01-17
- Updated: 2026-01-17

## User Narrative
As a maintainer, I want the architecture and components docs to be precise, deep, and source-anchored so I can understand the system after context compaction without guessing.

## Value / MRP Alignment
This ensures the core system is documented holistically and prevents repeated refactor churn from partial understanding.

## Requirements (Functional)
- Replace partial/verify placeholders with concrete behavioral definitions.
- Expand architecture with explicit wiring and lifecycle detail.
- Add method-level call flows and wiring maps in `src_components.md`.
- Keep method-level call flows out of the architecture doc.

## Requirements (Non-Functional)
- Use ASCII + Mermaid diagrams.
- Reference source files for key behaviors.
- Keep scope to core CommandOps platform.

## Scope Boundaries
- In scope: Spectrum, CommandCenter, groups, pools, agents, missions, activities, Iris, strategic command, core concurrency/synchronization/utilities.
- Out of scope: peripheral tools and tests.

## Dependencies / Related Work
- `system_docs/src_architecture.md`
- `system_docs/src_components.md`

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-01-17-commandops-deep-docs-inventory - Deep source inventory for remaining partials.
- [ ] Task: TASK-2026-01-17-commandops-deep-docs-architecture - Expand src architecture doc.
- [ ] Task: TASK-2026-01-17-commandops-deep-docs-components - Expand src components doc with call flows.
- [ ] Task: TASK-2026-01-17-commandops-deep-docs-closeout - Close out tickets and update completed list.

## Acceptance Criteria
- Architecture doc reads like a deterministic system description.
- Components doc includes method-level call flows and wiring maps.
- All partial inventory items resolved or marked out-of-scope.

## Validation / Test Plan
- Not run (documentation-only).

## UX / API / Data Notes
- No runtime changes.

## Risks / Mitigations
- Risk: over-expansion into non-core modules. Mitigation: explicit scope gating.

## Open Questions
- None.

## Decision Log
- 2026-01-17: Call flows will be documented only in `src_components.md`.

## Context / Handoff Summary
- Story in progress. Pass 1 expanded `src_components.md` with method-level call flows, deeper core component details, and updated diagrams.
- Next: expand wiring tables/registry keys, deepen concurrency/synchronization sections, and continue inventory for remaining modules.

