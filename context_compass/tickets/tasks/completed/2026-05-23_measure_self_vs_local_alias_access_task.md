# Task: Measure Self Vs Local Alias Access

## Metadata
- Task ID: TASK-2026-05-23-measure-self-vs-local-alias-access
- Story: none
- Status: done
- Owner: codex
- Agent Name: searcher_0
- Priority: p1
- Created: 2026-05-23T23:17:41Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Build and run one focused experimentation benchmark that compares repeated
attribute access through `self` versus local aliasing so we have actual timing
data instead of arguing by intuition.

## Ticket Contract
- ENTRY_GATE: certification is active for `searcher_0`, and this task is routed
  from `attention_board.md` before the experiment file is added or run.
- EXECUTION_BOUNDARY:
  - `tests/experimentation/`
  - `codex/context_compass/attention_board.md`
  - this task ticket
- DEPENDENCIES:
  - local `.venv_new` pytest environment
  - no runtime code changes outside experimentation scope
- EXIT_GATE:
  - one experiment file exists under `tests/experimentation`
  - the experiment is run through `.venv_new`
  - timing output is summarized truthfully
- FAILURE_ESCALATION: raise `BLOCKER` if the local pytest environment cannot
  run the experiment or if the experiment design cannot fairly isolate the
  requested access pattern.

## Scope Boundaries
- In scope:
  - one focused experimentation benchmark for repeated `self` access versus
    local alias access
  - running the experiment
  - summarizing the measured result
- Out of scope:
  - runtime optimization changes
  - unrelated benchmark or hook changes
  - wider codebase profiling

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a direct measurement of
  repeated `self` access versus local aliasing under `tests/experimentation`.

## Steps / Checklist
- [ ] Add one focused experimentation benchmark file under `tests/experimentation`.
- [ ] Run the benchmark through `.venv_new`.
- [ ] Record the measured result in ticket notes.
- [ ] Summarize the result to the user.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further execution.

## Deliverables
- one experimentation benchmark file
- one benchmark run result
- one grounded summary of the timing difference

## Files / Paths Impacted
- `tests/experimentation/`
- `codex/context_compass/attention_board.md`
- this task ticket

## Validation
- Not run.
- Recommended commands:
  - `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q -s tests\experimentation\test_self_vs_local_alias_access_experiment.py`

## Risks / Rollback Notes
- Risk: loop overhead can dominate if the experiment is too small.
  Rollback: use sufficiently large inner and outer counts and report exact shape.
- Risk: “local alias” is ambiguous between binding `self` versus binding a field.
  Rollback: measure both and report them separately if needed.

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
- CLEANUP_TRIGGER: user-directed after the measurement is accepted

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
- DATETIME: 2026-05-23T23:17:41Z
  TYPE: PLAN
  CLAIM: The user explicitly wants a direct experiment, not more reasoning:
    write one large repeated-access benchmark under `tests/experimentation`,
    run it through the local venv, and compare `self` access against local
    aliasing with the requested 1000-by-1000 shape.
  EVIDENCE:
  - user_request: current thread
  IMPACT: The next correct move is implementation of the experiment file, not
    further architecture or runtime discussion.
  NEXT: add the experiment file under `tests/experimentation`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-23T23:20:46Z
  TYPE: MEASURE
  CLAIM: The direct experiment shows a real but bounded difference. Across the
    requested 1000 outer runs x 1000 inner attribute accesses, the best
    repeated `self._value` pass measured `14.893 ms`, binding `self` to a local
    and then using `bound_self._value` measured `15.097 ms` (about `1.4%`
    slower than plain `self`), and binding `self._value` to a local scalar
    measured `13.441 ms` (about `9.8%` faster than plain `self`).
  EVIDENCE:
  - tests/experimentation/test_self_vs_local_alias_access_experiment.py:1-197
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q -s tests\experimentation\test_self_vs_local_alias_access_experiment.py`
  IMPACT: Local aliasing of the attribute value is real and measurable in a
    tight loop, while binding `self` to a local is not helpful here. This still
    does not prove that broad codebase performance is dominated by aliasing, but
    it does prove the micro-cost exists in the expected direction for direct
    attribute reads.
  NEXT: summarize the measurement to the user and decide whether to widen into
    a second experiment that mirrors one of Melder's actual hot-path access
    patterns instead of this isolated scalar loop.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-23T23:25:43Z
  TYPE: MEASURE
  CLAIM: The exact requested giant-method experiment gives the opposite result
    from the first scalar-loop proxy. With one method containing 1000 bare
    `self._vN` touches and another containing 1000 `local_N = self._vN`
    bindings, both run 1000 times per sample, the direct-self method measured
    `3.981 ms` best-case while the local-alias method measured `5.192 ms`
    best-case. In this exact shape, local alias binding is about `30.4%`
    slower than direct self attribute touches.
  EVIDENCE:
  - tests/experimentation/test_self_vs_local_alias_access_experiment.py:1-162
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q -s tests\experimentation\test_self_vs_local_alias_access_experiment.py`
  IMPACT: The earlier scalar-loop result does not generalize to the concrete
    giant-method form you asked for. For one-time 1000-attribute binding,
    aliasing is worse, not better.
  NEXT: summarize the exact-shape result to the user and let them decide
    whether to mirror an even closer Melder hot-path code shape next.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-23T23:35:59Z
  TYPE: MEASURE
  CLAIM: The reuse-count experiment gives a clean crossover point. With direct
    `self._value` reads versus `value = self._value` local aliasing, both run
    at 1000 outer calls x 1000 inner loop iterations, aliasing is slower at
    `1x` reuse (`+13.5%`) and `2x` reuse (`+3.0%`), then becomes faster at
    `3x` reuse (`-2.6%`), `4x` reuse (`-4.7%`), and `5x` reuse (`-7.4%`).
  EVIDENCE:
  - tests/experimentation/test_self_vs_local_alias_access_experiment.py:1-217
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q -s tests\experimentation\test_self_vs_local_alias_access_experiment.py`
  IMPACT: We now have a measured threshold instead of folklore. One-shot or
    two-shot aliasing is a loss in this shape; aliasing starts paying back only
    when the same field is reused at least about three times in a tight loop.
  NEXT: summarize the threshold to the user and let them decide whether to
    apply that rule to a narrow hot-path cleanup pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to measure repeated `self` attribute access versus local
aliasing in isolation under the local pytest environment.

