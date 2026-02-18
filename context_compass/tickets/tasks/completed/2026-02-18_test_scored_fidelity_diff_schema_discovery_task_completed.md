# Task: Discover Test-Scored Fidelity Diff Schema Realignment

## Metadata
- Task ID: TASK-2026-02-18-test-scored-fidelity-diff-schema-discovery
- Story: STORY-2026-02-18-skill-gate-first-compaction-discovery
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-18T16:53:27Z
- Updated: 2026-02-18T18:05:56Z

## Objective
Define schema/reporting changes so cycle success is driven by graded test
results (`knowledge_test`) rather than parity-only `fidelity_diff` attestations.

## Ticket Contract
- ENTRY_GATE: minimum-read onboarding discovery outputs are available.
- EXECUTION_BOUNDARY: differential board schema and policy/reporting docs only.
- DEPENDENCIES: current row-type semantics and cycle summary formulas.
- EXIT_GATE: documented mapping from current schema to score-grounded schema,
  including compatibility considerations.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if historical-row compatibility
  cannot be maintained without migration.

## Scope Boundaries
- In scope:
  - row-type meaning and cycle summary success semantics
  - pass/fail status and `Not run` handling
  - compatibility strategy for existing board rows
- Out of scope:
  - targeted relearn routing
  - generator shrink logic

## State Transition Event
- from_state: ready
- to_state: ready
- transition_reason: queued pending upstream onboarding-minimum-read discovery.

## Steps / Checklist
- [x] Map current `fidelity_diff` and `knowledge_test` semantic roles.
- [x] Define score-grounded cycle summary fields and pass/fail interpretation.
- [x] Propose row-type naming/compatibility strategy.
- [x] Specify migration/transition rules for existing rows.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- Discovery spec for schema realignment and cycle summary semantics.

## Files / Paths Impacted
- `tickets/tasks/completed/2026-02-18_test_scored_fidelity_diff_schema_discovery_task_completed.md`
- (discovery references only)
  - `compacting_differential_board.md`
  - `skill_check/skill_check_policy.md`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "fidelity_diff|knowledge_test|Cycle Summary" context_compass/compacting_differential_board.md`
  - `rg -n "knowledge_score|global_score|rank|anti-cheat" context_compass/skill_check/skill_check_policy.md`

## Risks / Rollback Notes
- Naming/semantic shifts may confuse existing analytics unless compatibility is
  explicit.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/2026-02-18_skill_gate_first_compaction_success_model.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: story closure

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-02-18T16:53:27Z
  TYPE: FACT
  CLAIM: Current board defines `fidelity_diff` as semantic parity and
    `knowledge_test` as question-level graded evidence, creating a split between
    attestation and scoring.
  EVIDENCE:
  - compacting_differential_board.md:47-51
  - compacting_differential_board.md:55-91
  - compacting_differential_board.md:95-119
  IMPACT: Cycle success can appear complete without scored answers unless schema
    semantics are realigned.
  NEXT: define score-primary reporting model and compatibility path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-18T17:07:51Z
  TYPE: FACT
  CLAIM: Differential board semantics were realigned so scored
    `knowledge_test` rows are primary completion evidence and
    `knowledge_score: Not run` is explicitly `incomplete`.
  EVIDENCE:
  - compacting_differential_board.md:6-13
  - compacting_differential_board.md:107-109
  - skill_check/skill_check_policy.md:21-24
  - skill_check/skill_check_policy.md:203-205
  IMPACT: Cycle success is now tied to graded outcomes instead of parity-only
    attestation rows.
  NEXT: finalize relearn and reset/shrink lane closure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-18T18:05:56Z
  TYPE: MEASURE
  CLAIM: Current scoring semantics are operational and validated in a fresh cycle with graded output.
  EVIDENCE:
  - compacting_differential_board.md:1-126
  - skill_check/skill_check_policy.md:1-132
  - skill_check/historical_test_results/cycle_2026-02-18T175200Z_hard_mcq_grade.md:1-66
  IMPACT: Schema-discovery outcomes remain valid and closure-ready.
  NEXT: finalize story/epic closure and archive this task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Task outcome captured and implemented: board and policy now enforce score-first
cycle completion semantics.

## Closure Note
Closed after user requested finishing the epic and validation confirmed score-grounded reporting works.
