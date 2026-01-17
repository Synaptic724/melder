# Epic: C4 Architecture and Components Docs for Src and Tests

- Completed: 2026-01-17
- Summary: Added C4 architecture and C3/C2/C1 component docs with diagrams and wired them into core codex_todo policies.

## Metadata
- Epic ID: EPIC-2026-01-17-c4-architecture-docs
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-17
- Updated: 2026-01-17
- Target Window: 2026-Q1
- Related Program/Initiative: Documentation system

## Problem / Opportunity
We lack a durable, structured architecture description for src and tests that survives context compaction and provides a clear map of the system. This creates repeated re-learning and weak handoffs.

## MRP Alignment (Most Reasonable Product)
Create a holistic documentation core that explains architecture and components for both src and tests using a consistent C4-based mapping. This foundation avoids documentation debt and supports long-term understanding.

## Goals (Outcomes)
- Create C4 architecture and components documentation with diagrams for src and tests.
- Define a repeatable information-gathering method and templates.
- Wire the new docs into AGENTS and SKILLS so they are required context.

## Non-Goals (Explicit Exclusions)
- Full detailed code-level documentation of every class or function.
- Large refactors or code changes.

## Scope Boundaries
- In scope: codex_todo documentation, templates, and workflow wiring.
- Out of scope: implementation changes in src or tests.

## Success Metrics
- New docs exist and are referenced by AGENTS and SKILLS.
- C4 mapping and templates are clear and usable.

## Requirements (Functional + Non-Functional)
- Provide separate src and tests docs.
- Include diagrams in ASCII form for easy reading.
- Use ASCII-only text.

## Constraints / Assumptions
- The C4 mapping is defined as: C4 architecture, C3 components, C2 subcomponents, C1 code.
- Documentation focuses on guidance and templates, not exhaustive code mapping.

## Dependencies / External References
- None.

## Milestones (Track Progress)
- [x] Milestone 1: Architecture and components docs created with templates and diagrams.
- [x] Milestone 2: AGENTS and SKILLS updated to require the new docs.

## Stories (Required to Complete)
- [x] Story: STORY-2026-01-17-c4-architecture-docs - Create C4 docs and workflow wiring.

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: Complete story STORY-2026-01-17-c4-architecture-docs.

## Acceptance Criteria (Epic Done)
- All docs are created and linked from AGENTS and SKILLS.
- Templates define how to gather and present architecture and components.

## Risks / Mitigations
- Risk: docs become too abstract. Mitigation: include concrete templates and diagram sections.

## Validation / Test Approach
- Documentation only. No tests required.

## Rollout / Adoption Plan
- Use these docs as required review during context compaction.

## Open Questions
- None.

## Decision Log
- C4 mapping is user-defined (C4 architecture, C3 components, C2 subcomponents, C1 code).

## Context / Handoff Summary
Epic completed; C4 docs and wiring are established in codex_todo.
