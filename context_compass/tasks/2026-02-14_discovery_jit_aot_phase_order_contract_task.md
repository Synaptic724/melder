# Task: Discovery - JIT/AOT Phase Order Contract

## Metadata
- Task ID: TASK-2026-02-14-discovery-jit-aot-phase-order-contract
- Story: STORY-2026-02-14-jit-aot-split-discovery-and-viability
- Status: review
- Owner: codex
- Priority: p1
- Created: 2026-02-14
- Updated: 2026-02-15

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
- [x] Map current phase execution order for structural and full-run helpers.
- [x] Trace where conduit-scoped resolution phases are invoked and what they depend on.
- [x] Record compatibility verdict for requested split with evidence-backed rationale.
- [x] If incompatible, propose 2-3 alternative split models for user review.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- One phase-order contract note set with explicit viability verdict.
- One decision-ready alternatives list (if requested split is incompatible).

## Viability Verdict (2026-02-15)
Verdict: requested split shape is now contract-viable at ordering level after parity alignment.

Rationale:
- `Spell.run_all_phases` now runs `5 -> 6 -> 7 -> 8 -> 9 -> 10 -> 11`.
- `SpellbookCreationSystem` target resolution path registers local foundational phases before local plan phases.
- Residual risk moved from ordering mismatch to runtime orchestration/flag lifecycle (`resolution_required`) and builder-contract policy.

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
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Phase-order parity is now aligned: full-run spell path executes foundational phases before plan phases, matching resolution-system ordering direction.
  EVIDENCE: src/melder/spellbook/spell.py:1337-1348, src/melder/spellbook/spellbook_creation_system.py:1315-1331, src/melder/spellbook/spellbook_creation_system.py:1398-1426, context_compass/tasks/2026-02-15_align_spellcrafter_phase_order_with_spellbook_creation_system_task.md:1-110
  IMPACT: Original ordering conflict risk is reduced; split feasibility now depends primarily on runtime gating contracts.
  NEXT: Route decisions through builder/flag/assumption-challenge tasks for implementation planning.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Resolution ordering contracts currently drift across paths: `SpellbookCreationSystem` runs foundational phases (`5/6/7`) before plan phases (`8/9/10/11`), while `SpellCrafter.run_all_phases` still runs `5/8/9/10/11/6/7`.
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:852-905, src/melder/spellbook/spellbook_creation_system.py:1286-1459, src/melder/spellbook/spell_crafter/spell_crafter.py:5047-5094, src/melder/spellbook/spell.py:1299-1349
  IMPACT: Revalidation can execute a different phase order than conjure-time resolution, which weakens split-mode contract consistency.
  NEXT: Create a dedicated implementation task to align SpellCrafter/Spell ordering with SpellbookCreationSystem before continuing JIT/AOT scope expansion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Current full-run path orders 8-11 before 6-7, while structural helper covers only 1-4.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:5018-5045, src/melder/spellbook/spell_crafter/spell_crafter.py:5058-5069, src/melder/spellbook/spell.py:1270-1297, src/melder/spellbook/spell.py:1305-1319
  IMPACT: The requested 1-7 / 8-12 split is not yet a direct fit to observed sequencing.
  NEXT: Verify whether 6-7 logically require artifacts built in 8-11.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Phase-order discovery is complete and in review; ordering-level mismatch has
been addressed via parity alignment. Next gating work is assumption decision +
implementation planning for runtime resolution orchestration.
