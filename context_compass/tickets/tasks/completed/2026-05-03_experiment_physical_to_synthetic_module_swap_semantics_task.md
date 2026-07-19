# Task: Experiment Physical To Synthetic Module Swap Semantics
- Completed: 2026-05-10T00:06:36Z
- Summary: Closed after the physical-to-synthetic swap matrix made the eager-
  retention versus lazy/reload rebinding semantics explicit.

## Metadata
- Task ID: TASK-2026-05-03-experiment-physical-to-synthetic-module-swap-semantics
- Story:
- Epic: EPIC-2026-04-26-design-crystallizer-asset-provenance-layer
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-03T16:24:51Z
- Updated: 2026-05-10T00:06:36Z

## Objective
Build one focused experimentation bench that proves what actually happens when
file-backed Python modules are swapped to synthetic modules under a live
runtime, including eager import retention, lazy import rebinding, reload
behavior, and Melder bind/conjure/meld implications.

## Ticket Contract
- ENTRY_GATE: the user explicitly approved implementing the full semantic test
  matrix after the prior read-only analysis.
- EXECUTION_BOUNDARY:
  - `tests/experimentation/`
  - this task ticket
  - `attention_board.md`
- DEPENDENCIES:
  - `tests/experimentation/synthetic_module_import_testbench.py`
  - `tests/experimentation/melder_bind_dropped_synthetic_dependency_testbench.py`
  - crystallizer runtime-reorientation lane
- EXIT_GATE: the bench exists, the targeted experiment run completes, and the
  findings are recorded with evidence.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the matrix reveals that the
  requested physical->synthetic swap behavior is fundamentally undefined or too
  split-brained to pursue without a stricter reload boundary.

## Scope Boundaries
- In scope:
  - eager vs lazy import behavior after swapping provider modules
  - class/function global retention
  - importlib reload effects
  - package/submodule swap behavior
  - existing instance coexistence
  - bind/conjure/meld outcomes after swap
- Out of scope:
  - production crystallizer implementation
  - broad loader redesign
  - performance benchmarking beyond semantic proof

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested the full semantic matrix as
  experiments before moving the design forward.

## Steps / Checklist
- [ ] Create the bounded experimentation bench in `tests/experimentation/`.
- [ ] Cover the full semantic matrix discussed in the design pass.
- [ ] Run the targeted bench and capture the result.
- [ ] Record the findings in `## Notes`.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- one semantic experimentation bench for physical->synthetic module swap
- one targeted execution result for that bench

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-05-03_experiment_physical_to_synthetic_module_swap_semantics_task.md
- codex/context_compass/attention_board.md
- tests/experimentation/

## Validation
- Executed:
  - `python tests/experimentation/physical_to_synthetic_module_swap_semantics_testbench.py`
- Result:
  - full semantic matrix passed

## Risks / Rollback Notes
- Risk: the bench proves that transparent dynamic reassociation is too
  split-brained to support safely.
  Rollback: keep physical->synthetic morphing behind explicit rebuild/reload
  boundaries instead of treating it as a transparent live swap.

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
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: task closure

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-03T16:24:51Z
  TYPE: PLAN
  CLAIM: The next bounded move is to build the full semantic matrix around
    physical->synthetic module swapping before any more crystallizer or
    morphing design is treated as trustworthy. The matrix needs to prove eager
    retention, lazy rebinding, reload behavior, package swap behavior, existing
    instance coexistence, and Melder bind/conjure/meld consequences.
  EVIDENCE:
  - user_instruction: "yeah do those tests please all of them"
  - tests/experimentation/melder_bind_dropped_synthetic_dependency_testbench.py:1-384
  - tests/experimentation/unittest_synthetic_module_edge_cases_testbench.py:606-841
  IMPACT: The next design decisions around file->synthetic morphing should be
    driven by experiment results, not intuition.
  NEXT: implement the bench in `tests/experimentation/` and run it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T16:30:57Z
  TYPE: MEASURE
  CLAIM: The targeted swap bench is now landed and green. The results split
    the semantics cleanly: eager `from ... import ...`, eager module-object
    references, function globals, class-method globals, existing instances, and
    bind/conjure/meld against old imported class objects all retain the old
    physical world after a provider swap. Lazy imports and `importlib.reload`
    see the swapped synthetic provider, and lazy Melder meld paths follow the
    current provider world at runtime.
  EVIDENCE:
  - tests/experimentation/physical_to_synthetic_module_swap_semantics_testbench.py:1-856
  - validation_result:
    `python tests/experimentation/physical_to_synthetic_module_swap_semantics_testbench.py` ->
    `OK_PHYSICAL_TO_SYNTHETIC_MODULE_SWAP_SEMANTICS`
  IMPACT: Transparent live reassociation of already-imported physical code to
    synthetic modules is not generally safe. The evidence supports treating
    physical->synthetic morphing as a controlled rebuild/reload boundary rather
    than as an invisible hot swap under existing references.
  NEXT: use this result when deciding whether file-backed code may move into
    synthetic-module mode only through explicit reload or loader boundaries.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the experimentation tranche for physical->synthetic module swap
semantics before any production crystallizer or loader design assumes such a
swap is safe.
