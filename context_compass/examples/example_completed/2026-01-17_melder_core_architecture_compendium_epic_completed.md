

- Completed: 2026-01-17
- Summary: Delivered deep architecture and components documentation for Melder core.

# Epic: Melder Core Architecture Compendium

## Metadata
- Epic ID: EPIC-2026-01-17-melder-core-architecture-compendium
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-17
- Updated: 2026-01-17
- Target Window: 2026-Q1
- Related Program/Initiative: Melder Core

## Problem / Opportunity
The existing src architecture and components docs are too shallow to serve as a durable, context-resettable system map. We need a deep, source-anchored compendium that explains the Spectrum entrypoint, CommandCenter core wiring, and the core concurrency/synchronization foundations with sufficient detail to support future work without relying on memory.

## MRP Alignment (Most Reasonable Product)
This deep documentation is part of the holistic core. It codifies how Melder actually works and the invariants that must remain true. This prevents repeated refactors caused by partial understanding and preserves long-term value.

## Goals (Outcomes)
- Produce a deep, source-anchored architecture doc for the Melder core centered on Spectrum.
- Produce a rich components doc that maps C3/C2/C1 components and their contracts.
- Ensure the docs are usable as a standalone system map after context compaction.

## Non-Goals (Explicit Exclusions)
- Full documentation of non-core tooling or peripheral modules.
- Full documentation of tests or external tooling beyond core references.

## Scope Boundaries
- In scope: core Melder platform (Spectrum + CommandCenter + core orchestration + foundational concurrency/synchronization/utilities).
- Out of scope: peripheral tools not required to understand core platform behavior.

## Success Metrics
- Architecture doc is deep, structured, and source-referenced (target ~2000+ lines).
- Components doc includes per-component responsibilities, lifecycle, invariants, and diagrams.
- Clear entrypoint and lifecycle sequence that can be followed without external context.

## Requirements (Functional + Non-Functional)
- Use ASCII + Mermaid diagrams.
- Include creation context, lifecycle, invariants, and failure modes.
- Record information sources and file anchors.

## Constraints / Assumptions
- Scope limited to core Melder platform.
- Focus on Spectrum as the entrypoint.

## Dependencies / External References
- `src/melder/` core packages and modules.
- `system_docs/src_architecture.md` and `system_docs/src_components.md` docs.

## Milestones (Track Progress)
- [x] Milestone 1: Source inventory complete (core entrypoints and lifecycle).
- [x] Milestone 2: Architecture doc expanded and verified.
- [x] Milestone 3: Components doc expanded and verified.

## Stories (Required to Complete)
- [x] Story: STORY-2026-01-17-melder-core-architecture-compendium - Deep dive and rewrite docs.

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: Complete story STORY-2026-01-17-melder-core-architecture-compendium

## Acceptance Criteria (Epic Done)
- Both `system_docs/src_architecture.md` and `system_docs/src_components.md` are rewritten to a deep, source-anchored standard.
- Entry point is documented as Spectrum, including configure/build lifecycle and cleanup.
- Docs can be used after context compaction without external memory.

## Risks / Mitigations
- Risk: Scope creep into non-core tools. Mitigation: gate scope to Spectrum and CommandCenter core.
- Risk: Missing or incorrect lifecycle details. Mitigation: verify with source references and trace sequences.

## Validation / Test Approach
- Documentation-only change; no tests required.

## Rollout / Adoption Plan
- Use these docs as the default re-orientation step before any future work.

## Open Questions
- None.

## Decision Log
- 2026-01-17: Focus on Spectrum as entrypoint and Melder core platform only.

## Context / Handoff Summary
- Epic complete. Deep architecture and components documentation delivered for Melder core.




