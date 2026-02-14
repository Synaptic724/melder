# Story: Establish resolution-style matrix source of truth

- Completed: 2026-02-13
- Summary: Canonical matrix ownership was finalized in `ResolutionStyleMatrix` with family-policy source-of-truth, drift checks, and docs linkage updates in architecture/components.

## Metadata
- Story ID: STORY-2026-02-13-resolution-style-matrix-source-of-truth
- Epic: EPIC-2026-02-13-src-architecture-revalidation
- Status: closed
- Owner: codex
- Priority: p2
- Created: 2026-02-13
- Updated: 2026-02-13

## User Narrative
As a maintainer, I want a canonical, versioned resolution-style matrix, so that
SpellType/Existence combinations and ownership expectations are explicit and do
not drift across docs and implementation.

## Value / MRP Alignment
Revalidation found no dedicated maintainer-owned matrix artifact despite heavy
doc reliance on inferred combinations. A canonical source reduces ambiguity and
prevents future architecture/components drift.

## Requirements (Functional)
- Create a canonical artifact documenting supported resolution styles:
  SpellType (14) x Existence (6), with supported/unsupported semantics.
- Define ownership for maintaining the matrix and update process.
- Link architecture/components docs to the canonical artifact.
- Add a lightweight consistency check that detects enum-count drift.

## Requirements (Non-Functional)
- Artifact must be readable and diff-friendly for reviews.
- Consistency check must be deterministic and fast.
- Avoid embedding unstable assumptions; unsupported combinations must be
  explicit.

## Scope Boundaries
- In scope:
- Matrix artifact, ownership policy, and doc linkage.
- Enum count/check validation scaffold.
- Out of scope:
- Runtime behavior changes to force support for all combinations.
- Large API redesign around binding semantics.

## Dependencies / Related Work
- `src/melder/spellbook/spell_types/spell_types.py`
- `src/melder/spellbook/existence/existence.py`
- `context_compass/architecture/src_architecture.md`
- `context_compass/components/src_components.md`

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-02-13-resolution-matrix-artifact - Create canonical matrix artifact with supported semantics.
- [x] Task: TASK-2026-02-13-resolution-matrix-owner - Define maintainer ownership and update policy.
- [x] Task: TASK-2026-02-13-resolution-matrix-doc-links - Link architecture/components docs to canonical matrix.
- [x] Task: TASK-2026-02-13-resolution-matrix-check - Add enum-count drift check.
- [x] Task: TASK-2026-02-13-resolution-matrix-tests - Add targeted validation tests for check behavior.

## Acceptance Criteria
- Canonical matrix artifact exists and is linked from architecture/components.
- Ownership and update process are documented.
- Enum drift check fails when SpellType/Existence counts change without matrix
  update.

## Validation / Test Plan
- Run targeted tests/check script for matrix count validation.
- Manual doc review to verify links and consistency wording.

## UX / API / Data Notes
- Documentation and validation-only story; no required public API change.

## Risks / Mitigations
- Risk: matrix is created but not maintained.
  Mitigation: add explicit ownership and drift check gate.
- Risk: matrix over-specifies behavior not guaranteed by runtime.
  Mitigation: mark unsupported/unknown combinations explicitly.

## Open Questions
- Should unsupported combinations be formalized as errors at bind time, or only
  documented as unsupported behavior?

## Decision Log
- 2026-02-13: Story created from architecture/components open-question sweep.
- 2026-02-13: Canonical matrix finalized in `src/melder/spellbook/resolution_style_matrix.py` with family-policy source-of-truth and SpellType derived projection.
- 2026-02-13: Architecture/components docs linked to canonical matrix artifact; stale matrix unknown/open-question entries removed.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Implementation complete and validated:
- Canonical matrix artifact + owner/update policy documented in
  `src/melder/spellbook/resolution_style_matrix.py`.
- Drift checks added for SpellType/Existence counts and mapping consistency via
  `ResolutionStyleMatrix.validate()`.
- Unit validation passed:
  `python -m pytest tests/unit/melder/spellbook/test_resolution_style_matrix.py -q`
  (`7 passed`).
- Architecture/components docs now reference the canonical matrix artifact and
  no longer describe matrix ownership as unknown.
