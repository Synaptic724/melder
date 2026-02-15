# Task: Discovery - JIT/AOT `resolution_required` Spell Contract

## Metadata
- Task ID: TASK-2026-02-14-discovery-jit-aot-resolution-required-spell-contract
- Story: STORY-2026-02-14-jit-aot-split-discovery-and-viability
- Status: ready
- Owner: codex
- Priority: p1
- Created: 2026-02-14
- Updated: 2026-02-14

## Objective
Define a concrete lifecycle contract for `resolution_required: bool` on spells,
including who sets it, who clears it, and how it interacts with validity gates.

## Scope Boundaries
- In scope:
- Spell lifecycle and runtime gating semantics tied to deferred resolution.
- Out of scope:
- Implementing the field and runtime behavior in code.

## Steps / Checklist
- [ ] Identify current spell lifecycle states relevant to structural and resolution readiness.
- [ ] Identify where runtime gating currently revalidates/executes resolution.
- [ ] Draft lifecycle table for `resolution_required` transitions.
- [ ] Define fail-fast conditions when deferred resolution cannot complete.
- [ ] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- One `resolution_required` lifecycle table with transitions and owners.
- One recommendation for validity behavior in split mode.

## Files / Paths Impacted
- `src/melder/spellbook/spell.py`
- `src/melder/aether/conduit/meld/meld.py`
- `src/melder/spellbook/spellbook.py`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "run_structural_phases|run_all_phases|_get_or_build_creation_context" src/melder/spellbook/spell.py`
  - `rg -n "_ensure_lineage_resolvable|_run_resolution_phases_for_target_spell" src/melder/aether/conduit/meld/meld.py src/melder/spellbook/spellbook.py`

## Risks / Rollback Notes
- Risk: Poorly defined flag semantics could hide invalid-state bugs.
- Rollback: discovery-only task; no runtime code changes in this task.

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
  CLAIM: Meld runtime already includes lineage revalidation and conduit-scoped resolution gating before instance resolution, and spells expose both structural-only and full phase helpers.
  EVIDENCE: src/melder/aether/conduit/meld/meld.py:402-430, src/melder/spellbook/spell.py:1270-1336, src/melder/spellbook/spellbook.py:3075-3150
  IMPACT: `resolution_required` should likely integrate with existing lineage gating rather than inventing a parallel state system.
  NEXT: Draft transition table and review with user in assumption-challenge discussion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Task is ready. It focuses on state/lifecycle contract definition for the new
spell flag before any implementation work.
