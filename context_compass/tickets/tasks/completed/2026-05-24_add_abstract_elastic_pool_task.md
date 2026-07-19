# Task: Add Abstract Elastic Pool

## Metadata
- Task ID: TASK-2026-05-24-add-abstract-elastic-pool
- Story: none
- Status: done
- Owner: codex
- Agent Name: searcher_0
- Priority: p1
- Created: 2026-05-24T00:45:01Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Add one reusable abstract elastic pool base under `utilities/data_structures`
that later lesser-conduit and spellspace pool types can inherit.

## Ticket Contract
- ENTRY_GATE: certification is active for `searcher_0`, and this task is routed
  from `attention_board.md` before implementation starts.
- EXECUTION_BOUNDARY:
  - `src/melder/utilities/data_structures/abstract_elastic_pool.py`
  - `tests/unit/melder/utilities/data_structures/test_abstract_elastic_pool.py`
  - `codex/context_compass/attention_board.md`
  - this task ticket
- DEPENDENCIES:
  - current `Cleanable` lifecycle contract
  - current pooling algorithm discussion from the user
- EXIT_GATE:
  - abstract pool base exists with the requested elastic semantics
  - focused unit tests pass
  - no runtime integration is bundled into this slice
- FAILURE_ESCALATION: raise `BLOCKER` if the abstract API cannot support later
  lesser-conduit and spellspace reuse without hidden assumptions.

## Scope Boundaries
- In scope:
  - one abstract pool base class
  - elastic acquire/release/decay mechanics
  - abstract object lifecycle hooks for subclasses
  - focused unit tests
- Out of scope:
  - lesser conduit integration
  - spellspace integration
  - config wiring
  - controller/gate pooling

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested the abstract pool object now
  rather than more investigation.

## Steps / Checklist
- [ ] Add `AbstractElasticPool` under `utilities/data_structures`.
- [ ] Add focused unit tests for acquire/release/stretch/decay/cleanup semantics.
- [ ] Run the focused test file.
- [ ] Summarize the resulting abstract API and any constraints for subclasses.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further implementation.

## Deliverables
- one abstract elastic pool base class
- one focused unit test file
- one focused validation result

## Files / Paths Impacted
- `src/melder/utilities/data_structures/abstract_elastic_pool.py`
- `tests/unit/melder/utilities/data_structures/test_abstract_elastic_pool.py`
- `codex/context_compass/attention_board.md`
- this task ticket

## Validation
- Not run.
- Recommended commands:
  - `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\utilities\data_structures\test_abstract_elastic_pool.py`

## Risks / Rollback Notes
- Risk: the base API may be too narrow for later lesser-conduit/spellspace reuse.
  Rollback: adjust only the abstract hooks in this slice, not runtime integration.
- Risk: decay/stretch policy may overfit the current discussion.
  Rollback: keep the base generic and leave config/runtime tuning to later slices.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

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
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: user-directed after the base API is accepted

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
- DATETIME: 2026-05-24T00:45:01Z
  TYPE: PLAN
  CLAIM: The user wants the abstract pool object first, not runtime integration.
    The right slice is one reusable `AbstractElasticPool` with elastic
    acquire/release/decay behavior and abstract lifecycle hooks that later
    `LesserConduitElasticPool` and `SpellSpaceElasticPool` can implement.
  EVIDENCE:
  - user_request: current thread
  IMPACT: The immediate job is a small reusable base, not a half-integrated
    conduit/spellspace pooling system.
  NEXT: implement `AbstractElasticPool` and its focused test file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T11:25:55Z
  TYPE: MEASURE
  CLAIM: The abstract pool base is implemented and its focused unit file is
    green (`8 passed`). The base now owns the elastic policy state (`baseline`,
    `target_idle`, stretch/settle/decay, max idle, in-use count), provides
    `acquire(...)`, `release(...)`, `cleanup()`, and `describe()`, and leaves
    object-specific lifecycle work to `create_object`, `prepare_object`,
    `reset_object`, and `destroy_object`.
  EVIDENCE:
  - src/melder/utilities/data_structures/abstract_elastic_pool.py:1-340
  - tests/unit/melder/utilities/data_structures/test_abstract_elastic_pool.py:1-214
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\utilities\data_structures\test_abstract_elastic_pool.py`
  IMPACT: We now have the reusable base needed for later
    `LesserConduitElasticPool` and `SpellSpaceElasticPool` without bundling
    runtime integration into this slice.
  NEXT: summarize the abstract API clearly, then decide whether the next slice
    is `LesserConduitElasticPool` or `SpellSpaceElasticPool`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T11:28:37Z
  TYPE: MEASURE
  CLAIM: The abstract pool test ring is now broader and still green (`18
    passed`). The stronger coverage now proves invalid-config rejection,
    release-underflow failure, prepare-on-reuse behavior, max-idle stretch cap,
    no decay before cooldown, multi-interval multiplicative decay, baseline
    decay floor, disabled-pool destroy semantics, detached `describe()`
    snapshots, idempotent cleanup, and public-method failure after cleanup.
  EVIDENCE:
  - tests/unit/melder/utilities/data_structures/test_abstract_elastic_pool.py:1-347
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\utilities\data_structures\test_abstract_elastic_pool.py`
  IMPACT: The base now has enough coverage to serve as a stable substrate for a
    concrete `LesserConduitElasticPool` or `SpellSpaceElasticPool` slice
    without immediately rediscovering basic lifecycle bugs.
  NEXT: summarize the proven pool behavior and let the user choose which
    concrete pool subclass to wire next.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to add the reusable elastic pool base only, leaving all
runtime integration for later slices.

