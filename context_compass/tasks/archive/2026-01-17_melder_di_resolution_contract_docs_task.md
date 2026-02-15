# Task: Integrate DI resolution contract into docs

- Completed: 2026-01-17
- Summary: Integrated DI resolution contract details into architecture/components docs with spec-vs-implementation notes.

## Metadata
- Task ID: TASK-2026-01-17-melder-di-resolution-contract-docs
- Story: STORY-2026-01-17-melder-architecture-components-docs
- Status: done
- Owner:
- Priority: p0
- Created: 2026-01-17
- Updated: 2026-01-22

## Objective
Integrate the Melder DI Resolution Contract (19-item spec) into architecture
and components docs, including explicit spec vs implementation notes.

## Scope Boundaries
- In scope: `context_compass/architecture/src_architecture.md`,
  `context_compass/components/src_components.md`.
- Out of scope: code changes, tests, `__*.json` metadata, external docs.

## Steps / Checklist
- [x] Embed contract summary (Sections A–H) in architecture doc.
- [x] Reflect contract behavior in components doc (root entry modes, DI shapes,
      SpellMap semantics, uniqueness/ambiguity, collection DI, deep scan).
- [x] Record explicit spec vs current implementation gaps.
- [x] Update information sources and open questions.

## Deliverables
- Updated `context_compass/architecture/src_architecture.md`
- Updated `context_compass/components/src_components.md`

## Files / Paths Impacted
- `context_compass/architecture/src_architecture.md`
- `context_compass/components/src_components.md`

## Validation
- Not run.
- Recommended commands:
  - None (documentation-only).

## Risks / Rollback Notes
- Risk: misrepresenting spec vs implementation; mitigate with explicit gaps.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded

## Context / Handoff Summary
- DI resolution contract integrated into architecture and components docs with
  spec-vs-implementation notes and updated evidence lists.
- Update (2026-01-22): Post-init SpellMap deep scan is not planned; constructor
  DI remains the supported wiring path.
