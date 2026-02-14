# Task: Optimize Conjure Activation and Validation Scan Fastpath

## Metadata
- Task ID: TASK-2026-02-14-conjure-activation-and-validation-scan-fastpath
- Story: STORY-2026-02-13-optimize-conjure-paths
- Status: review
- Owner: codex
- Priority: p1
- Created: 2026-02-14
- Updated: 2026-02-14

## Objective
Reduce repeated full-spell scans in conjure validation and activation wiring
while preserving correctness and diagnostic behavior.

## Scope Boundaries
- In scope:
- `_check_all_spells` scan path in `Spellbook`.
- `_collect_broken_spells` and conduit wiring scan paths in
  `SpellbookCreationSystem`.
- Targeted regression tests for duplicate checks and conduit ownership wiring.
- Out of scope:
- Changes to SpellState semantics.
- Mutation runtime wiring.

## Steps / Checklist
- [x] Baseline scan-heavy paths and identify safe short-circuit opportunities.
- [x] Implement scan fastpath(s) with unchanged error contracts.
- [x] Validate duplicate-detection and ownership-wiring behavior.
- [x] Capture performance delta using existing profile harness/tests.

## Deliverables
- Reduced scan overhead in conjure activation/validation path.
- Tests proving no regression in duplicate checks or conduit wiring behavior.

## Files / Paths Impacted
- `src/melder/spellbook/spellbook.py`
- `src/melder/spellbook/spellbook_creation_system.py`
- `tests/unit/melder/spellbook/` (targeted updates as needed)

## Validation
- `python -m pytest -q tests/unit/melder/spellbook/test_spellbook.py -k "check_system_state or _check_all_spells or conjure_hooks_fire_in_order"` -> `12 passed`.
- Artifact:
  - `context_compass/artifacts/2026-02-14_conjure_activation_validation_scan_fastpath_pytests.txt`

## Risks / Rollback Notes
- Risk: weakening duplicate detection or ownership metadata stamping.
- Rollback: revert to current full-scan behavior.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Fresh targeted validation run passes for scan/activation guardrails after removing the redundant conjure duplicate-id recheck (`12 passed`).
  EVIDENCE: context_compass/artifacts/2026-02-14_conjure_activation_validation_scan_fastpath_pytests.txt:1-12
  IMPACT: Task is now evidence-complete in review with current-run regression confirmation.
  NEXT: Walk outcomes with user for acceptance and completion move.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Removed conjure-path duplicate-id recheck call from `_resolve_conjure_policy`; duplicate SHA checks remain at bind front door and `_check_all_spells` remains available as utility.
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:258-285, src/melder/spellbook/spellbook.py:1269-1312, src/melder/spellbook/spellbook.py:2496-2508
  IMPACT: Avoids redundant duplicate-id scan during conjure path and reduces startup overhead.
  NEXT: Confirm acceptance and decide whether to also simplify `_check_all_spells` to a set-intersection implementation for optional future use.

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Focused spellbook tests covering `check_system_state`, `_check_all_spells`, and conjure paths pass after removing conjure recheck call.
  EVIDENCE: tests/unit/melder/spellbook/test_spellbook.py:3072-3142, tests/unit/melder/spellbook/test_spellbook.py:3568-3701
  IMPACT: No regression detected in targeted conjure/duplicate-check contracts.
  NEXT: If accepted, mark this task done and move to the next conjure optimization item.

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Notes section added to enforce active_documentation for in-flight findings.
  EVIDENCE: context_compass/agent_onboarding/agent/general/skills/active_documentation.md:1
  IMPACT: Keeps ticket memory durable across compaction by requiring evidence-backed notes.
  NEXT: Append new findings here as work continues.

## Context / Handoff Summary
Activation/validation scan fastpath is implemented and in review.
Conjure duplicate-id recheck was removed from `_resolve_conjure_policy` while
retaining bind-time duplicate SHA protection and `_check_all_spells` utility
behavior; focused regression coverage is attached for closure review.
