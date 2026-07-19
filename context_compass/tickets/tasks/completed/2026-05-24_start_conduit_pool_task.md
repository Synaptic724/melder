# Task: Start Conduit Pool
- Completed: 2026-05-30T15:06:13Z
- Summary: Closed by explicit user instruction during the 2026-05-30 compiler-strategy lane reset. This ticket is superseded as an active route by the new execution-strategy compiler direction.


## Metadata
- Task ID: TASK-2026-05-24-start-conduit-pool
- Story: none
- Status: done
- Owner: codex
- Agent Name: searcher_0
- Priority: p1
- Created: 2026-05-24T14:20:00Z
- Updated: 2026-05-30T15:06:13Z

## Objective
Add the initial `ConduitPool` class scaffold so the root-conduit-owned conduit
pool lane has a concrete home before real lesser-conduit reuse wiring starts.

## Ticket Contract
- ENTRY_GATE: certification is active for `searcher_0`, and this task is routed
  from `attention_board.md` before implementation starts.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit/conduit_pool.py`
  - `tests/unit/melder/aether/conduit/test_conduit_pool.py`
  - `codex/context_compass/attention_board.md`
  - this task ticket
- DEPENDENCIES:
  - `src/melder/utilities/general_base/abstract_elastic_pool.py`
  - current `Conduit` ownership/lifecycle model
- EXIT_GATE:
  - `ConduitPool` exists as a concrete subclass scaffold
  - placeholder lifecycle methods are explicit
  - focused unit tests pass
- FAILURE_ESCALATION: raise `BLOCKER` if the placeholder scaffold cannot be
  added cleanly without forcing premature conduit reuse wiring.

## Scope Boundaries
- In scope:
  - one `ConduitPool` class scaffold
  - one focused unit test file
- Out of scope:
  - root conduit integration
  - lesser conduit reuse wiring
  - gate pooling
  - spellspace changes

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested starting the conduit pool
  with placeholders only.

## Steps / Checklist
- [ ] Add `ConduitPool` scaffold under `src/melder/aether/conduit/`.
- [ ] Add focused unit tests for the placeholder contract.
- [ ] Run the focused unit file.
- [ ] Summarize the scaffold and the next wiring seam.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further implementation.

## Deliverables
- one placeholder `ConduitPool` class
- one focused unit test file
- one focused validation result

## Files / Paths Impacted
- `src/melder/aether/conduit/conduit_pool.py`
- `tests/unit/melder/aether/conduit/test_conduit_pool.py`
- `codex/context_compass/attention_board.md`
- this task ticket

## Validation
- Not run.
- Recommended commands:
  - `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\test_conduit_pool.py`

## Risks / Rollback Notes
- Risk: placeholder method shapes may over-constrain the later reuse design.
  Rollback: keep the scaffold thin and explicit rather than pretending real
  wiring exists.

## Applicable Anti-Patterns
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No drive-by refactors outside the conduit-pool scaffold files.
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
- CLEANUP_TRIGGER: user-directed after the scaffold is accepted

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-24T14:20:00Z
  TYPE: PLAN
  CLAIM: The user wants only the conduit-pool starting point right now, not
    actual lesser-conduit reuse wiring. The right slice is one concrete
    `ConduitPool` subclass scaffold with explicit placeholder lifecycle methods
    and a small unit ring.
  EVIDENCE:
  - user_request: current thread
  IMPACT: This stays narrow and avoids dragging spellspace or conduit reuse
    wiring into the same change.
  NEXT: add `ConduitPool` and one focused unit test file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to add the first `ConduitPool` scaffold only, with real reuse
wiring deferred to later work.
