# Epic: Populate C4 Architecture and Components Docs

- Completed: 2026-01-17
- Summary: Populated src/tests architecture and components docs and documented pytest policy.

## Metadata
- Epic ID: EPIC-2026-01-17-architecture-population
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-17
- Updated: 2026-01-17
- Target Window: 2026-Q1
- Related Program/Initiative: Documentation system

## Problem / Opportunity
Architecture and component templates exist but lack concrete content. Without populated docs, context compaction and onboarding remain slow and error-prone.

## MRP Alignment (Most Reasonable Product)
Populate the architecture and components docs with high-signal system mapping to create a durable documentation core.

## Goals (Outcomes)
- Fill src and tests architecture docs with current system understanding.
- Fill src and tests components docs with C3/C2/C1 details.
- Update AGENTS to enforce pytest usage going forward.

## Non-Goals (Explicit Exclusions)
- Exhaustive per-class documentation for all files.
- Code refactors or behavior changes.

## Scope Boundaries
- In scope: codex_todo docs and policy updates.
- Out of scope: changes to src or tests code.

## Success Metrics
- Architecture/components docs are populated and reflect current structure.
- Policy clearly states pytest requirement.

## Requirements (Functional + Non-Functional)
- ASCII-only documentation with ASCII and Mermaid diagrams.
- Separate src and tests views.

## Constraints / Assumptions
- Use directory layout and key entrypoints as sources.
- Tests are currently unittest; pytest required for new tests.

## Dependencies / External References
- None.

## Milestones (Track Progress)
- [x] Milestone 1: Architecture docs populated with C4 mapping.
- [x] Milestone 2: Components docs populated with C3/C2/C1 mapping.
- [x] Milestone 3: AGENTS updated for pytest requirement.

## Stories (Required to Complete)
- [x] Story: STORY-2026-01-17-architecture-population - Populate docs and update policy.

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: Complete story STORY-2026-01-17-architecture-population.

## Acceptance Criteria (Epic Done)
- Docs are populated and current.
- Pytest requirement is documented in AGENTS.

## Risks / Mitigations
- Risk: docs become stale. Mitigation: require updates in SKILLS and compaction.

## Validation / Test Approach
- Documentation only.

## Rollout / Adoption Plan
- Use docs as required context before major changes.

## Open Questions
- None.

## Decision Log
- Populate docs using layout and key files as sources.

## Context / Handoff Summary
Epic completed; docs are populated and pytest policy is recorded.
