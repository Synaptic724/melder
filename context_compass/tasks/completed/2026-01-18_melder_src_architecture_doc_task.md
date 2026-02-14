- Completed: 2026-01-18
- Summary: Drafted `context_compass/architecture/src_architecture.md` with the C4 system map, core flows, and evidence list.

# Task: Draft src architecture doc

## Metadata
- Task ID: TASK-2026-01-17-melder-src-architecture-doc
- Story: STORY-2026-01-17-melder-architecture-components-docs
- Status: done
- Owner:
- Priority: p0
- Created: 2026-01-17
- Updated: 2026-01-18

## Objective
Produce `context_compass/architecture/src_architecture.md` with a C4-level system map of
Melder core based on `.py` source evidence.

## Scope Boundaries
- In scope: `src/melder/` Python sources and core entrypoints.
- Out of scope: tests, external docs, `__*.json` metadata.

## Steps / Checklist
- [x] Identify entrypoints, public APIs, and boot sequence from code.
- [x] Map major subsystems and boundaries (spellbook, aether/conduit, utilities).
- [x] Document lifecycle, cleanup, invariants, and failure modes.
- [x] Capture data flows and key sequences.
- [x] Add ASCII and Mermaid diagrams.
- [x] Record evidence list and open questions.

## Deliverables
- `context_compass/architecture/src_architecture.md`

## Files / Paths Impacted
- `context_compass/architecture/src_architecture.md`

## Validation
- Not run.
- Recommended commands:
  - None (documentation-only).

## Risks / Rollback Notes
- None (documentation-only).

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded

## Context / Handoff Summary
- Completed draft of `context_compass/architecture/src_architecture.md`; ready for review and follow-up passes.
