- Completed: 2026-02-03
- Summary: Documented dependency-injector public API surface with line-evidenced mapping.

# Task: Dependency-injector report 05 - public API surface map

## Metadata
- Task ID: TASK-2026-02-03-dependency-injector-report-05-public-api-surface
- Story: N/A
- Status: done
- Owner:
- Priority: p1
- Created: 2026-02-03
- Updated: 2026-02-03

## Objective
Document the public API entrypoints for dependency-injector and map them to
internal modules using line-anchored evidence.

## Scope Boundaries
- In scope:
  - Analyze containers, providers, wiring, and top-level exports in the code dump.
  - Create `benchmarks/competitors/dependency-injector/final_outcomes/dependency_injector_report_05_public_api_surface.md`.
- Out of scope:
  - Modifying dependency-injector source code.
  - Running benchmarks or tests.

## Steps / Checklist
- [x] Identify public entrypoints from containers, providers, wiring, and ext modules.
- [x] Map entrypoints to internal implementations with line anchors.
- [x] Record validation status.

## Deliverables
- `benchmarks/competitors/dependency-injector/final_outcomes/dependency_injector_report_05_public_api_surface.md`

## Files / Paths Impacted
- `benchmarks/competitors/dependency-injector/final_outcomes/dependency_injector_report_05_public_api_surface.md`
- `benchmarks/competitors/dependency-injector/code/dependency-injector_code.txt` (read-only evidence)

## Validation
- Not run.
- Recommended commands:
  - (Not applicable; documentation-only update.)

## Risks / Rollback Notes
- Risk: Missing export list in __init__.py; may need UNKNOWNs.
- Rollback: Revert the doc or update line mappings.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Created report 05 (public API surface) with line-evidenced entrypoints mapping.
Awaiting user acceptance.