# Task: Remove redundant Meld spell_id resolution cache

## Metadata
- Task ID: TASK-2026-05-24-remove-redundant-meld-spell-id-resolution-cache
- Story: none
- Status: done
- Owner: codex
- Agent Name: mutres_0
- Priority: p1
- Created: 2026-05-24T21:35:34Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Remove `Meld._spell_id_resolution_cache` and make direct `spell_id` resolution
use the already-maintained shared `Spellbook._spell_id_pool` path instead.

## Ticket Contract
- ENTRY_GATE: the active performance investigation already proved
  `Spellbook._spell_id_pool` is the shared union `spell_id -> Spell` map for
  owned and contracted spells, so the per-`Meld` cache is now an explicitly
  bounded cleanup target.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit/meld/meld.py`
  - directly implicated tests only if they exist
  - `codex/context_compass/attention_board.md`
  - this task ticket
- DEPENDENCIES:
  - `tickets/tasks/2026-05-24_investigate_performance_roadmap_claims_task.md`
- EXIT_GATE: `_spell_id_resolution_cache` is gone from `Meld`, direct
  `spell_id` callers still resolve through `_spell_id_pool`, and focused
  validation is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if removing the cache exposes a
  hidden dependency outside `meld.py`.

## Scope Boundaries
- In scope:
  - remove `_spell_id_resolution_cache` storage and writes
  - keep logical input cache untouched
  - focused validation
- Out of scope:
  - redesign the logical lookup cache
  - broader fast-path or seal work
  - unrelated `Meld` refactors

## State Transition Event
- from_state: draft
- to_state: review
- transition_reason: the duplicate per-`Meld` direct-id cache is removed and
  the directly implicated meld unit file is green.

## Steps / Checklist
- [ ] Remove `_spell_id_resolution_cache` from `Meld` storage and cleanup.
- [ ] Switch direct `spell_id` callers to `_resolve_spell_by_id(...)` with no
      extra cache layer.
- [ ] Run focused validation.
- [ ] Summarize the cut and any remaining cache-shape issues.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further implementation.

## Deliverables
- one simpler direct `spell_id` lookup path in `Meld`
- one focused validation result

## Files / Paths Impacted
- `src/melder/aether/conduit/meld/meld.py`
- `codex/context_compass/attention_board.md`
- `codex/context_compass/tickets/tasks/2026-05-24_remove_redundant_meld_spell_id_resolution_cache_task.md`

## Validation
- Ran:
  - `<local-workspace>\.venv_new\Scripts\python.exe -m py_compile src\melder\aether\conduit\meld\meld.py`
  - `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\meld\test_meld.py`
- Result:
  - `84 passed, 1 warning`

## Risks / Rollback Notes
- Risk: some test or helper path may have been relying on incidental warming of
  the direct-id cache.
  Rollback: restore only if a directly implicated failing seam proves a real
  dependency.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No widening into logical lookup cache redesign in this task.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: ticket closure

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-01T11:05:49Z
  TYPE: DECISION
  CLAIM: The user explicitly accepted this lane as complete and requested that
    it be turned in and moved out of active routing.
  EVIDENCE:
  - user_instruction
  IMPACT: This ticket is now closed and should no longer appear in active
    board routing.
  NEXT: none
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-24T21:35:34Z
  TYPE: FACT
  CLAIM: `Spellbook._spell_id_pool` is already the shared union
    `spell_id -> Spell` map for both owned and contracted spells, and
    `Meld._resolve_spell_by_id(...)` already checks it first. The per-`Meld`
    `_spell_id_resolution_cache` is therefore duplicating an already-maintained
    mapping instead of providing new truth.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:231-239
  - src/melder/aether/spellbook/spellbook.py:595-612
  - src/melder/aether/spellbook/spellbook.py:766-797
  - src/melder/aether/conduit/meld/meld.py:1646-1659
  IMPACT: The direct-id cache layer is a clean, bounded removal target that
    simplifies `Meld` without touching the more complex logical lookup cache.
  NEXT: patch `meld.py` to delete `_spell_id_resolution_cache` and route direct
    id callers straight through `_resolve_spell_by_id(...)`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-24T21:42:59Z
  TYPE: FACT
  CLAIM: The direct-id cache cut is landed in `meld.py`. `Meld` no longer owns
    `_spell_id_resolution_cache`, and the three direct `spell_id` callsites now
    route straight to `_resolve_spell_by_id(...)` instead of performing a
    second dict lookup and repopulation cycle on the per-`Meld` cache.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:77-97
  - src/melder/aether/conduit/meld/meld.py:159-162
  - src/melder/aether/conduit/meld/meld.py:205-226
  - src/melder/aether/conduit/meld/meld.py:331-364
  - src/melder/aether/conduit/meld/meld.py:491-523
  - src/melder/aether/conduit/meld/meld.py:785-817
  IMPACT: Direct `spell_id` resolution now depends only on the shared
    `Spellbook._spell_id_pool` truth path and no longer pays a redundant
    per-conduit cache warmup.
  NEXT: run the narrow compile check and directly implicated meld unit file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-24T21:42:59Z
  TYPE: MEASURE
  CLAIM: The direct-id cache removal passes the narrow validation ring. The
    touched file compiles, and the directly implicated meld unit file passed
    `84 passed, 1 warning`.
  EVIDENCE:
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m py_compile src\melder\aether\conduit\meld\meld.py`
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\meld\test_meld.py`
  IMPACT: The duplicate direct-id cache is gone without breaking the directly
    implicated meld contract.
  NEXT: get user acceptance on this cut, then decide whether the next cache
    discussion should target the logical lookup cache or move back to the
    fast-hit lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to remove the redundant per-`Meld` `spell_id` cache only. It
should stay tightly scoped to direct id lookup and not widen into the logical
lookup cache redesign.

