# Task: Align public Spellbook entrypoint with README

- Completed: 2026-01-22
- Summary: Updated README to import `Spellbook` directly, matching current
  public exports.

## Metadata
- Task ID: TASK-2026-01-22-melder-public-spellbook-entrypoint
- Story: N/A (task-only request)
- Status: done
- Owner:
- Priority: p2
- Created: 2026-01-22
- Updated: 2026-01-22

## Objective
Resolve the README vs package export mismatch for the Spellbook entrypoint by
confirming the intended public API and aligning docs or exports accordingly.

## Scope Boundaries
- In scope:
  - Inspect README/docs referencing `from melder import spellbook`.
  - Verify `src/melder/__init__.py` exports and current public API.
  - Implement the minimal alignment (doc update or export).
  - Add/update tests if an export change is made.
- Out of scope:
  - Behavioral changes to Spellbook internals.
  - Packaging/refactor work beyond public export alignment.

## Steps / Checklist
- [x] Review README/docs for spellbook entrypoint references.
- [x] Inspect `src/melder/__init__.py` and confirm current public exports.
- [x] Decide on doc vs export alignment and implement the minimal fix.
- [x] Add/update tests if exports change.
- [x] Update task context with final decision and evidence.

## Deliverables
- Public API alignment for Spellbook entrypoint (docs or export).
- Updated task summary with evidence references.

## Files / Paths Impacted
- `README.md`

## Validation
- Not run.
- Recommended commands:
  - `python -c "import melder; print(hasattr(melder, 'spellbook'))"`
  - `pytest` (only if new tests are added)

## Risks / Rollback Notes
- Risk: Changing exports alters public API expectations.
  - Mitigation: Prefer doc alignment unless maintainers confirm export intent.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Open question from `context_compass/components/src_components.md` notes README usage
(`from melder import spellbook`) but `src/melder/__init__.py` lacks a Spellbook
export. This task will confirm intended public API and align docs or exports
with evidence.
Decision: align README with current public API. `src/melder/__init__.py` only
exports metadata in `__all__` and does not expose a spellbook factory or class,
so README now imports `Spellbook` from
`src/melder/spellbook/spellbook.py`. No export changes or tests were needed.
Acceptance confirmed.
