# Task: Discovery - JIT/AOT Phase Order Contract

## Metadata
- Task ID: TASK-2026-02-14-discovery-jit-aot-phase-order-contract
- Story: STORY-2026-02-14-jit-aot-split-discovery-and-viability
- Status: ready
- Owner: codex
- Priority: p1
- Created: 2026-02-14
- Updated: 2026-02-14

## Objective
Establish whether the requested split shape (run phases 1-7 at conjure and defer
8-12 to runtime) is compatible with current phase execution contracts.

## Scope Boundaries
- In scope:
- Source-level mapping of phase sequencing, dependencies, and gating points.
- Explicit viability decision with alternatives if direct request is invalid.
- Out of scope:
- Runtime code changes.

## Steps / Checklist
- [ ] Map current phase execution order for structural and full-run helpers.
- [ ] Trace where conduit-scoped resolution phases are invoked and what they depend on.
- [ ] Record compatibility verdict for requested split with evidence-backed rationale.
- [ ] If incompatible, propose 2-3 alternative split models for user review.
- [ ] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- One phase-order contract note set with explicit viability verdict.
- One decision-ready alternatives list (if requested split is incompatible).

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/spellbook/spell.py`
- `src/melder/spellbook/spellbook.py`
- `src/melder/aether/conduit/meld/meld.py`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "run_structural_phases|run_all_phases|run_phase_" src/melder/spellbook/spell_crafter/spell_crafter.py`
  - `rg -n "_run_structural_phases|_run_resolution_phases_for_" src/melder/spellbook/spellbook.py`

## Risks / Rollback Notes
- Risk: Misreading phase dependencies could create invalid implementation scope.
- Rollback: Keep this task discovery-only; no runtime changes occur here.

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
  CLAIM: Current full-run path orders 8-11 before 6-7, while structural helper covers only 1-4.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:5018-5045, src/melder/spellbook/spell_crafter/spell_crafter.py:5058-5069, src/melder/spellbook/spell.py:1270-1297, src/melder/spellbook/spell.py:1305-1319
  IMPACT: The requested 1-7 / 8-12 split is not yet a direct fit to observed sequencing.
  NEXT: Verify whether 6-7 logically require artifacts built in 8-11.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Task is ready; first action is dependency validation for 6-7 relative to 8-11
to confirm whether requested split can be used as-is or needs redesign.
