Completed: 2026-02-14
Summary: Accepted in closure pass; implementation/discovery outcomes are complete and archived.

# Task: Remap Legacy Artifact References and Remove Placeholder Files

## Metadata
- Task ID: TASK-2026-02-14-context-compass-artifact-reference-cleanup
- Story: none (standalone)
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-14
- Updated: 2026-02-14

## Objective
Remap legacy `context_compass/artifacts/...` references to a stable canonical
artifact index and remove placeholder artifact files while preserving
documentation integrity.

## Scope Boundaries
- In scope:
- Documentation references under `context_compass/`.
- Placeholder files under `context_compass/artifacts/`.
- Out of scope:
- Runtime source changes in `src/` and `tests/`.

## Steps / Checklist
- [x] Add active board routing row for this cleanup.
- [x] Create canonical artifact index document.
- [x] Remap all `context_compass/artifacts/...` markdown references to canonical index.
- [x] Remove legacy artifact placeholder files.
- [x] Re-run full `context_compass/...` reference integrity scan and confirm zero missing refs.

## Deliverables
- `context_compass/artifacts/README.md` canonical index.
- Updated doc references.
- Placeholder files removed.

## Validation
- Not run.
- Executed checks:
  - `rg -n "context_compass/artifacts/.+\\.md" context_compass`
  - global `context_compass/...` reference scan (`GLOBAL_MISSING_CONTEXT_COMPASS_REFS: 0`)

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed
## Notes
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: User requested remap of all legacy artifact references and deletion of placeholder artifact files.
  EVIDENCE: user instruction in session (2026-02-14)
  IMPACT: Requires deterministic rewrite + filesystem cleanup with final integrity verification.
  NEXT: Route task on attention board and run artifact-reference inventory.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Artifact reference inventory found 124 `context_compass/artifacts/*.md` references across 57 documentation files.
  EVIDENCE: `context_compass/stories/archive/2026-01-29_phase12_precompute_meld_runtime_story.md:45`, `context_compass/epics/completed/2026-01-20_melder_change_control_test_expansion_epic.md:61`
  IMPACT: Single-file canonical remap is the lowest-risk way to remove placeholders without leaving broken links.
  NEXT: Create `context_compass/artifacts/README.md` and rewrite all artifact-path references to that canonical target.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Canonical remap applied: 123 artifact-path replacements across 56 docs now point to `context_compass/artifacts/README.md`.
  EVIDENCE: `context_compass/artifacts/README.md:1`, `context_compass/stories/archive/2026-01-29_phase12_precompute_meld_runtime_story.md:45`
  IMPACT: Placeholder files are no longer required for link integrity.
  NEXT: Remove non-README artifact files and validate global reference integrity.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Placeholder cleanup completed: removed 28 artifact files and 4 empty artifact subdirectories; only canonical `context_compass/artifacts/README.md` remains.
  EVIDENCE: `context_compass/artifacts/README.md:1`
  IMPACT: Legacy placeholder footprint is eliminated while maintaining a stable artifact reference target.
  NEXT: Run full global `context_compass/...` reference integrity scan and confirm zero missing refs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Post-remap global scan found one remaining broken reference: completed audit task still points to its pre-move active path.
  EVIDENCE: `context_compass/tasks/completed/2026-02-14_context_compass_documentation_integrity_audit_task.md:124`
  IMPACT: Global integrity is one reference away from clean.
  NEXT: Patch that audit evidence pointer to the completed task path and re-run global scan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Cleanup is complete: artifact references now point to canonical index, placeholders are removed, and global integrity scan reports zero missing `context_compass/...` references.
  EVIDENCE: `context_compass/artifacts/README.md:1`, `context_compass/tasks/completed/2026-02-14_context_compass_documentation_integrity_audit_task.md:120`
  IMPACT: Legacy artifact remap is finalized without broken links.
  NEXT: Share results with user and close task after acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Cleanup implementation complete and in review pending user acceptance.
Canonical artifact index is active and global documentation reference integrity is clean.
