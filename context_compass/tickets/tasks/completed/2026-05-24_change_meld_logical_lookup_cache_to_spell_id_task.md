# Task: Change Meld logical lookup cache to spell_id

## Metadata
- Task ID: TASK-2026-05-24-change-meld-logical-lookup-cache-to-spell-id
- Story: none
- Status: done
- Owner: codex
- Agent Name: mutres_0
- Priority: p1
- Created: 2026-05-24T21:42:59Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Change `Meld._input_resolution_cache` from `tuple -> Spell` into
`tuple -> spell_id`, then resolve the live `Spell` through shared Spellbook
truth on cache hits instead of retaining spell objects in the per-`Meld` cache.

## Ticket Contract
- ENTRY_GATE: the direct `spell_id` cache cleanup is landed, and the user
  explicitly requested the same simplification for the logical lookup cache.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit/meld/meld.py`
  - directly implicated tests only
  - `codex/context_compass/attention_board.md`
  - this task ticket
- DEPENDENCIES:
  - `tickets/tasks/2026-05-24_remove_redundant_meld_spell_id_resolution_cache_task.md`
- EXIT_GATE: logical lookup cache values are `spell_id` strings, cache hits
  dereference through shared Spellbook maps, and focused validation is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if changing the cache value shape
  exposes a hidden consumer outside `meld.py`.

## Scope Boundaries
- In scope:
  - change `_input_resolution_cache` value shape
  - keep current key shape untouched
  - add stale-hit fallback through live Spellbook truth
  - focused validation
- Out of scope:
  - redesign the key shape itself
  - broader fast-hit lane work
  - unrelated `Meld` refactors

## State Transition Event
- from_state: draft
- to_state: review
- transition_reason: the logical cache now stores `spell_id` values, the two
  directly implicated mocked tests were aligned to shared Spellbook truth, and
  the meld unit file is green again.

## Steps / Checklist
- [ ] Change `_input_resolution_cache` to store `spell_id` strings.
- [ ] Make cache hits dereference through shared Spellbook truth.
- [ ] Preserve unhashable fallback-key behavior.
- [ ] Run focused validation.
- [ ] Summarize the cut and any remaining cache-shape issues.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further implementation.

## Deliverables
- one simpler logical lookup cache storing `spell_id`
- one focused validation result

## Files / Paths Impacted
- `src/melder/aether/conduit/meld/meld.py`
- `tests/unit/melder/aether/conduit/meld/test_meld.py`
- `codex/context_compass/attention_board.md`
- `codex/context_compass/tickets/tasks/2026-05-24_change_meld_logical_lookup_cache_to_spell_id_task.md`

## Validation
- Ran:
  - `<local-workspace>\.venv_new\Scripts\python.exe -m py_compile src\melder\aether\conduit\meld\meld.py`
  - `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\meld\test_meld.py`
- Result:
  - `84 passed, 1 warning`

## Risks / Rollback Notes
- Risk: stale cached `spell_id` could point at an id that no longer resolves.
  Rollback: on miss, recompute through the existing logical resolution path and
  rewrite the cache entry.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No widening into key-shape redesign in this task.

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
- DATETIME: 2026-05-24T21:42:59Z
  TYPE: FACT
  CLAIM: The remaining logical lookup cache still stores whole `Spell` objects
    in the per-`Meld` cache even though the user wants `tuple -> spell_id`
    followed by a second lookup through shared Spellbook truth. The directly
    implicated unit file only asserts key presence for the unhashable fallback
    path, not the cached value type, so this is a bounded shape change.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:333-369
  - src/melder/aether/conduit/meld/meld.py:491-529
  - src/melder/aether/conduit/meld/meld.py:787-823
  - tests/unit/melder/aether/conduit/meld/test_meld.py:912-919
  IMPACT: The next step can stay inside `meld.py` plus the directly implicated
    test file if needed, with no broad cache redesign.
  NEXT: patch `_input_resolution_cache` to store `spell_id` and make cache hits
    resolve through shared Spellbook truth.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-24T21:48:21Z
  TYPE: FACT
  CLAIM: The first validation failure is a test setup mismatch, not a runtime
    contradiction. The two failing meld unit tests patch `_resolve_spell(...)`
    directly and then expect the second call to hit the logical cache, but they
    never seed the shared `Spellbook._spell_id_pool` / direct-id truth that the
    new cache contract now dereferences on hit. In real runtime, the logical
    cache is only useful because resolved spells are already registered in
    shared Spellbook maps.
  EVIDENCE:
  - tests/unit/melder/aether/conduit/meld/test_meld.py:893-924
  - src/melder/aether/conduit/meld/meld.py:345-369
  - src/melder/aether/conduit/meld/meld.py:799-823
  IMPACT: The correct next step is to align the two tests to the real runtime
    contract by seeding `_spell_id_pool` for the mocked resolved spell, not to
    put whole `Spell` objects back into the per-`Meld` cache.
  NEXT: patch the two failing meld unit tests to seed `meld._spell_id_pool`
    with `target_spell` before the second call path is exercised, then rerun
    the meld unit file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-24T21:48:21Z
  TYPE: FACT
  CLAIM: The logical cache cut is landed in `meld.py`. `_input_resolution_cache`
    now stores `spell_id` strings instead of whole `Spell` objects, and cache
    hits dereference back through `Meld._spell_id_pool` first, with a
    `_resolve_spell_by_id(...)` fallback when the shared pool does not have the
    cached id.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:159-162
  - src/melder/aether/conduit/meld/meld.py:344-369
  - src/melder/aether/conduit/meld/meld.py:505-529
  - src/melder/aether/conduit/meld/meld.py:799-823
  IMPACT: The per-`Meld` logical cache now stops retaining whole `Spell`
    objects directly while preserving the existing key shape and fallback-key
    behavior.
  NEXT: rerun the directly implicated meld unit file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-24T21:48:21Z
  TYPE: MEASURE
  CLAIM: The logical cache value-shape cut passes the narrow validation ring
    after aligning the two mocked tests to shared Spellbook truth. Current
    result: `84 passed, 1 warning`.
  EVIDENCE:
  - tests/unit/melder/aether/conduit/meld/test_meld.py:893-919
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m py_compile src\melder\aether\conduit\meld\meld.py`
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\meld\test_meld.py`
  IMPACT: The cache now has the simpler `tuple -> spell_id` shape you asked
    for without breaking the directly implicated meld behavior.
  NEXT: get user acceptance on this cut, then choose whether the next move is
    key-shape cleanup or a return to the hot-path fast lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to change the logical lookup cache value shape only. It should
stay tightly scoped to `tuple -> spell_id` and not widen into key-shape or
fast-hit-lane redesign.

