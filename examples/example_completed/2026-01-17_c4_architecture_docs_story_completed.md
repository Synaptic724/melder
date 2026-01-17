# Story: C4 Architecture and Components Docs for Src and Tests

- Completed: 2026-01-17
- Summary: Created architecture/components docs with diagrams and wired them into AGENTS/SKILLS/WORKFLOW/README/CONTEXT.

## Metadata
- Story ID: STORY-2026-01-17-c4-architecture-docs
- Epic: EPIC-2026-01-17-c4-architecture-docs
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-17
- Updated: 2026-01-17

## User Narrative
As a maintainer, I want a structured C4-based documentation system for src and tests, so that I can understand the architecture quickly and preserve context through compaction.

## Value / MRP Alignment
This establishes the holistic documentation core needed for long-term clarity without repeated rework.

## Requirements (Functional)
- Create architecture docs with C4 mapping and diagrams for src and tests.
- Create components docs with C3/C2/C1 mapping and diagrams for src and tests.
- Document how to gather information and apply templates.
- Update AGENTS and SKILLS to require these docs.

## Requirements (Non-Functional)
- ASCII-only content.
- Clear templates with consistent structure.

## Scope Boundaries
- In scope: codex_todo documentation and workflow wiring.
- Out of scope: code changes in src or tests.

## Dependencies / Related Work
- None.

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-01-17-architecture-docs - Architecture docs and templates.
- [x] Task: TASK-2026-01-17-components-docs - Components docs and templates.
- [x] Task: TASK-2026-01-17-agents-skills-wiring - Update AGENTS, SKILLS, README, and compaction docs.

## Acceptance Criteria
- Architecture and components docs exist for src and tests with diagrams and templates.
- AGENTS and SKILLS reference the new docs.
- Context compaction guidance includes the new docs.

## Validation / Test Plan
- Not run (documentation only).

## UX / API / Data Notes
- Not applicable.

## Risks / Mitigations
- Risk: docs become boilerplate. Mitigation: add concrete prompts and structure.

## Open Questions
- None.

## Decision Log
- Use user-defined C4 mapping instead of standard naming.

## Context / Handoff Summary
Story completed; C4 docs and wiring are in place for src and tests.
