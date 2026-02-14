# Task: Optimize Phase5 Root Blueprints Baseline Hotpath

## Metadata
- Task ID: TASK-2026-02-14-optimize-phase5-root-blueprints-hotpath
- Story: STORY-2026-02-14-phase-testing-optimization-backlog
- Status: ready
- Owner: codex
- Priority: p1
- Created: 2026-02-14
- Updated: 2026-02-14

## Objective
Reduce conduit-wide phase5 root-blueprints cost while preserving foundational
5-7 semantics.

## Scope Boundaries
- In scope:
- Target phase5 root-blueprints computation and attachment path.
- Preserve phase6/7 validation/change-control behavior.
- Out of scope:
- Changing conduit validity gating semantics.
- Local 5-7 flow redesign.

## Steps / Checklist
- [ ] Profile root-blueprints internals and identify high-cost loops.
- [ ] Implement low-risk reductions in repeated snapshot/attachment work.
- [ ] Add/update tests that prove phase5 behavior remains unchanged.
- [ ] Validate via component harness rerun for conduit 5-7 cold/warm variants.
- [ ] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Optimized phase5 root-blueprints path.
- Updated conduit 5-7 measurements with before/after comparison.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `tests/component/melder/spellbook/test_phase_component_cprofile_harness.py`

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q -s tests/component/melder/spellbook/test_phase_component_cprofile_harness.py`

## Risks / Rollback Notes
- Risk: phase5 refactors could break downstream phase6/7 assumptions.
- Rollback: revert phase5 changes and keep existing foundational flow.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Conduit-wide 5-7 runs are consistently dominated by phase5 root-blueprints time in both cold and warm variants.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:7-8, src/melder/spellbook/spell_crafter/spell_crafter.py:2980-3245
  IMPACT: This task is ranked third as a targeted foundational optimization candidate with clear phase attribution.
  NEXT: Instrument phase5 internals to isolate dominant sub-steps before implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Created from measured phase-testing backlog ranking as a foundational 5-7
hotspot candidate.

