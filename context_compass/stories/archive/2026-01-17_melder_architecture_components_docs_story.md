- Completed: 2026-01-20
- Summary: Architecture and component docs authored and aligned with DI contract updates.

# Story: Document Melder src architecture and components

## Metadata
- Story ID: STORY-2026-01-17-melder-architecture-components-docs
- Epic:
- Status: completed
- Owner:
- Priority: p0
- Created: 2026-01-17
- Updated: 2026-01-20

## User Narrative
As a maintainer, I want architecture and component docs for the Melder core so I can
re-enter the codebase after context compaction without guessing.

## Value / MRP Alignment
This documentation anchors the core system boundaries, lifecycles, and invariants so the
MRP core remains coherent and maintainable as Melder evolves.

## Requirements (Functional)
- Create `context_compass/architecture/src_architecture.md` modeled on the example architecture doc.
- Create `context_compass/components/src_components.md` modeled on the example components doc.
- Use only `.py` sources under `src/melder/`; ignore `__*.json` sidecars.
- Document entrypoints, lifecycles, invariants, failure modes, and data flows.
- Include ASCII and Mermaid diagrams.
- Record an explicit evidence list of source files used.

## Requirements (Non-Functional)
- No handwaving; mark unknowns and add the next verification step.
- Use the example structure and section naming for consistency.
- Keep scope to Melder core (no tests or peripheral tools).

## Scope Boundaries
- In scope: `src/melder/` core packages (spellbook, aether/conduit, utilities, crystallizer).
- Out of scope: tests, external docs, `__*.json` metadata files.

## Dependencies / Related Work
- `context_compass/architecture/README.md`
- `context_compass/components/README.md`
- `examples/example_architecture/src_architecture.md`
- `examples/example_components/src_components.md`
- `README.md`
- `src/melder/` (code sources)

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-01-17-melder-src-architecture-doc - Draft src architecture doc.
- [x] Task: TASK-2026-01-17-melder-src-components-doc - Draft src components doc.
- [x] Task: TASK-2026-01-17-melder-capabilities-verification-docs - Verify capabilities and update docs.
- [x] Task: TASK-2026-01-17-melder-di-resolution-contract-docs - Integrate DI resolution contract into docs.
- [x] Task: TASK-2026-01-17-melder-di-contract-decisions-doc-alignment - Decide deep scan requirement and align meld contract docs.
- [x] Task: TASK-2026-01-17-melder-deepscan-investigation-docs - Investigate deep scan wiring and document findings.

## Acceptance Criteria
- Architecture doc provides a C4-level system description with evidence and diagrams.
- Components doc provides a C3/C2/C1 map with responsibilities, contracts, and call flows.
- All claims are source-anchored or explicitly marked unknown.

## Validation / Test Plan
- Not run (documentation-only).

## UX / API / Data Notes
- Documentation only; no runtime changes.

## Risks / Mitigations
- Risk: incomplete or ambiguous behavior from code. Mitigation: mark unknowns and list follow-up verification steps.

## Open Questions
- None yet.

## Decision Log
- 2026-01-17: Use `.py` sources only; ignore `__*.json` metadata.

## Context / Handoff Summary
- Drafted `context_compass/architecture/src_architecture.md` and
  `context_compass/components/src_components.md`; ready for acceptance and closeout.
