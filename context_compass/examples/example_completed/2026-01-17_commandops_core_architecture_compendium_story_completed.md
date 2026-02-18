- Completed: 2026-01-17
- Summary: Rewrote src architecture and components docs with deep C3/C2/C1 detail.

# Story: Deep dive CommandOps core architecture and components

## Metadata
- Story ID: STORY-2026-01-17-commandops-core-architecture-compendium
- Epic: EPIC-2026-01-17-commandops-core-architecture-compendium
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-17
- Updated: 2026-01-17

## User Narrative
As a maintainer, I want a deep, source-anchored architecture and components compendium for the CommandOps core so that I can re-enter this codebase after context compaction and still understand the system reliably.

## Value / MRP Alignment
This documentation captures the holistic core of CommandOps (Spectrum + CommandCenter orchestration), enabling long-term maintenance without MVP-style shortcuts.

## Requirements (Functional)
- Document Spectrum as the root entrypoint and global builder.
- Document configuration pipeline, singletons publication, and cleanup ordering.
- Document CommandCenter and CommandGroup lifecycle and registries.
- Document how agents, activities, missions, and pools are constructed and orchestrated.
- Document core concurrency/synchronization foundations used by the platform.

## Requirements (Non-Functional)
- Source references for all major claims.
- ASCII + Mermaid diagrams for readability.
- Target 2000+ lines across architecture and components docs for depth.

## Scope Boundaries
- In scope: `src/command_ops/` core platform.
- Out of scope: non-core tools and peripheral modules not needed for core understanding.

## Dependencies / Related Work
- `system_docs/src_architecture.md`
- `system_docs/src_components.md`

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-01-17-commandops-core-architecture-inventory - Inventory entrypoints, lifecycle, and invariants.
- [x] Task: TASK-2026-01-17-commandops-core-architecture-doc - Rewrite src architecture doc to deep standard.
- [x] Task: TASK-2026-01-17-commandops-core-components-doc - Rewrite src components doc to deep standard.
- [x] Task: TASK-2026-01-17-commandops-core-closeout - Close out tickets and update completed list.

## Acceptance Criteria
- Architecture doc explains Spectrum configuration/build/teardown sequence in detail.
- Components doc lists C3/C2/C1 entries with responsibilities, dependencies, and failure modes.
- Diagrams for the core subsystems exist in both docs.
- Sources and open questions are recorded.

## Validation / Test Plan
- Not run (documentation-only).

## UX / API / Data Notes
- No runtime changes.

## Risks / Mitigations
- Risk: Documentation becomes too diffuse. Mitigation: keep scope to core CommandOps platform.

## Open Questions
- None.

## Decision Log
- 2026-01-17: Proceed with deep documentation, focus on Spectrum entrypoint and CommandOps core only.

## Context / Handoff Summary
- Story complete. Deep architecture and components docs updated with detailed C3/C2/C1 coverage and diagrams.

