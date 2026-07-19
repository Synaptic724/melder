# Task: fix safe logger and channel interface cluster

Completed: 2026-05-19T17:29:27Z
Summary: Closed per user instruction after validation handoff. Latest lane state and validation notes remain below.


## Metadata
- Task ID: TASK-2026-05-19-fix-safe-logger-and-channel-interface-cluster
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_2
- Priority: p1
- Created: 2026-05-19T14:20:41Z
- Updated: 2026-05-19T17:29:27Z

## Objective
Fix the current `safe_logger.py` and `ichannellogger.py` mypy cluster by
aligning the channel-logger protocol to the real keyword-capable channel
surface and tightening `SafeLogger` narrowing without changing runtime logging
behavior.

## Ticket Contract
- ENTRY_GATE: the user supplied a bounded logger/channel-interface mypy
  cluster.
- EXECUTION_BOUNDARY:
  - `src/melder/utilities/logger/safe_logger.py`
  - `src/melder/utilities/interfaces/ichannellogger.py`
  - directly implicated support files only if truthful contract evidence
    requires them
- DEPENDENCIES:
  - current `SafeLogger` dispatch behavior
  - current `IChannelLogger` public typing contract
  - no shims, no fake surfaces, no unrelated logging redesign
  - raise to Mark directly if the protocol truth is ambiguous
- EXIT_GATE:
  - the targeted `safe_logger.py` and `ichannellogger.py` mypy errors are gone
  - protocol changes remain truthful to the current runtime channel logger
    behavior
  - focused logger tests confirm the lane
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if fixing the protocol would
  require changing real logging call semantics instead of just making the
  contract truthful

## Scope Boundaries
- In scope:
  - channel logger protocol parameter/return annotations
  - `traceback`-type annotation correction
  - `SafeLogger` union narrowing between stdlib `Logger` and `IChannelLogger`
  - keyword dispatch typing for `_manual_stack` / `_method_name`
- Out of scope:
  - broader logging architecture redesign
  - unrelated logger/provider mypy debt

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: the user selected this exact logger/channel-interface
  mypy cluster as the next active lane.

## Steps / Checklist
- [ ] read the exact `SafeLogger` and `IChannelLogger` failing slices
- [ ] classify protocol truth versus local narrowing debt
- [ ] patch the bounded protocol and logger fixes only
- [ ] rerun focused mypy on the two-file cluster
- [ ] rerun the direct safe-logger unit ring
- [ ] continue only after documenting the result
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- a bounded `SafeLogger` / `IChannelLogger` typing fix

## Files / Paths Impacted
- `src/melder/utilities/logger/safe_logger.py`
- `src/melder/utilities/interfaces/ichannellogger.py`
- only if required by the truthful fix:
  - directly implicated support contracts

## Validation
- Ran:
  - `.\.venv_new\Scripts\python.exe -m mypy --show-error-codes --show-column-numbers --no-error-summary src\melder\utilities\logger\safe_logger.py src\melder\utilities\interfaces\ichannellogger.py 2>&1 | Select-String 'src\\melder\\utilities\\logger\\safe_logger.py:|src\\melder\\utilities\\interfaces\\ichannellogger.py:'`
  - `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\utilities\logger\test_safe_logger.py`
- Results:
  - no output for the targeted two-file mypy slice
  - `7 passed, 1 warning`

## Risks / Rollback Notes
- Medium risk. The likely fix is truthful protocol widening plus logger-side
  narrowing, but the main danger is accidentally changing the real channel
  logger call shape instead of just typing it correctly.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
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
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-19T14:20:41Z
  TYPE: FACT
  CLAIM: The new bounded mypy lane is the logger/channel-interface cluster.
    The first safe step is to read the exact `SafeLogger` dispatch slice and
    the `IChannelLogger` protocol methods around the reported lines so we can
    tell whether the runtime already expects channel-only keywords like
    `_manual_stack` and `_method_name`.
  EVIDENCE:
  - user_error_report: `src/melder/utilities/logger/safe_logger.py:155-193`
  - user_error_report: `src/melder/utilities/interfaces/ichannellogger.py:379-530`
  IMPACT: This should stay a bounded protocol/narrowing lane if the current
    runtime contract is already clear.
  NEXT: read the exact failing slices and classify protocol truth versus local
    logger narrowing debt.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T14:20:41Z
  TYPE: FACT
  CLAIM: The cluster is mixed but bounded. `IChannelLogger` is missing
    explicit method parameter annotations and is using `traceback` as a module
    type instead of a traceback object type. In `SafeLogger`, the channel path
    is entered for two distinct reasons: a real `IChannelLogger` instance or a
    manually forced `_is_channel` test/double path. That means mypy cannot
    narrow the union from `Logger | IChannelLogger` just from the current
    boolean branch, even though runtime behavior is already clear.
  EVIDENCE:
  - src/melder/utilities/interfaces/ichannellogger.py:355-530
  - src/melder/utilities/logger/safe_logger.py:148-205
  - tests/unit/melder/utilities/logger/test_safe_logger.py:8-59
  - tests/unit/melder/utilities/logger/test_safe_logger.py:111-158
  IMPACT: The fix should be a truthful protocol annotation pass plus a
    channel-path helper or explicit local narrowing in `SafeLogger`, not a
    runtime behavior change.
  NEXT: patch `IChannelLogger` annotations and traceback typing, then refactor
    `SafeLogger` channel dispatch so stdlib logger calls never see channel-only
    kwargs in the typed surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T14:20:41Z
  TYPE: FACT
  CLAIM: The clean `SafeLogger` fix needs to preserve two runtime channel-path
    entry conditions: real `IChannelLogger` instances and the `_is_channel`
    test/double path used in the logger unit tests. Because the test doubles do
    not implement the full public `IChannelLogger` protocol, a pure
    `isinstance(logger, IChannelLogger)` branch would change behavior. The
    correct bounded fix is a truthful protocol annotation pass plus a separate
    channel emit helper that keeps the existing `_is_channel` behavior while
    isolating channel-only kwargs from the stdlib logger path.
  EVIDENCE:
  - src/melder/utilities/logger/safe_logger.py:148-205
  - src/melder/utilities/interfaces/ichannellogger.py:355-530
  - tests/unit/melder/utilities/logger/test_safe_logger.py:8-59
  - tests/unit/melder/utilities/logger/test_safe_logger.py:111-158
  IMPACT: This stays behavior-preserving and avoids forcing a fake local
    protocol or a runtime contract change.
  NEXT: patch the protocol annotations and channel helper split, then rerun
    focused mypy and the safe-logger unit ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T14:20:41Z
  TYPE: MEASURE
  CLAIM: The bounded logger/channel-interface cluster is green. `IChannelLogger`
    now has explicit method annotations and a real traceback object type, and
    `SafeLogger` now routes channel-only kwargs through a dedicated helper so
    the stdlib logger path no longer sees channel-only call shapes. The direct
    safe-logger unit ring passes.
  EVIDENCE:
  - src/melder/utilities/interfaces/ichannellogger.py:1-535
  - src/melder/utilities/logger/safe_logger.py:1-359
  - validation_result: filtered mypy command for `safe_logger.py` and `ichannellogger.py` -> no output
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\utilities\logger\test_safe_logger.py` -> `7 passed, 1 warning`
  IMPACT: The user-supplied two-file cluster is fixed without changing the live
    logging behavior. A raw mypy run on the two files still exits nonzero only
    because of imported debt elsewhere in the repo, not because of residual
    errors in this cluster.
  NEXT: report the bounded fix and wait for the next exact mypy/runtime lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Active bounded mypy lane for `SafeLogger` and `IChannelLogger`.
