# Task: Publish Pinned Mean Baseline for Phase12 Routes

## Metadata
- Task ID: TASK-2026-02-18-codegen-phase12-baseline-mean-profile
- Story: STORY-2026-02-18-codegen-baseline-and-hotspot-map
- Status: in_progress
- Owner: codex
- Priority: p0
- Created: 2026-02-18T10:23:05Z
- Updated: 2026-02-18T10:24:40Z

## Objective
Compute and record the pinned route mean baseline from raw samples, excluding
spellspace from decision metrics.

## Ticket Contract
- ENTRY_GATE: story is active on board and pinned discovery artifacts are available.
- EXECUTION_BOUNDARY: benchmark result interpretation only; no code edits in runtime modules.
- DEPENDENCIES: pinned deep benchmark JSON and epic metric policy.
- EXIT_GATE: means and cold ratios documented with evidence pointers.
- FAILURE_ESCALATION: raise `BLOCKER` if baseline artifact integrity fails.

## Scope Boundaries
- In scope:
  - `benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned_deep.json`
  - mean and ratio derivation from raw sample arrays
- Out of scope:
  - re-running benchmarks
  - runtime code changes

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: baseline computation is required to drive hotspot prioritization.

## Steps / Checklist
- [x] Extract route raw samples for non-spellspace routes.
- [x] Compute per-route means and route-to-cold mean ratios.
- [x] Record results in task notes with evidence anchors.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Mean baseline table (non-spellspace routes).
- Cold ratio table for the same routes.

## Files / Paths Impacted
- `benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned_deep.json`
- `tickets/tasks/2026-02-18_codegen_phase12_baseline_mean_profile_task.md`

## Validation
- Not run.
- Recommended commands:
  - `powershell -Command "$j = Get-Content -Raw benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned_deep.json | ConvertFrom-Json; ..."`

## Risks / Rollback Notes
- Risk: accidental inclusion of spellspace route in decision baseline.
  - Mitigation: explicit non-spellspace filter in computation.

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
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-02-18T10:23:05Z
  TYPE: MEASURE
  CLAIM: Non-spellspace route means from pinned deep samples are warm_mixed=23100, warm_override_targeted=6700, warm_override_root_args=6133.33, warm_root=600.
  EVIDENCE:
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned_deep.json:1066-1084
  IMPACT: Baseline prioritizes mixed and override routes for first optimization tranches.
  NEXT: Add route-to-cold ratios and hand off to hotspot-op mapping task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-18T10:23:05Z
  TYPE: MEASURE
  CLAIM: Non-spellspace route-to-cold mean ratios are warm_mixed=0.003666, warm_override_targeted=0.001063, warm_override_root_args=0.000973, warm_root=0.000095.
  EVIDENCE:
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned_deep.json:1058-1088
  IMPACT: Warm mixed remains the dominant route even after cold normalization.
  NEXT: Complete hotspot-op ranking for mixed and override routes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Baseline means and ratios are captured from pinned deep samples with spellspace
excluded from decision metrics. Next step is converting this route weighting
into ranked concrete phase12/codegen ops.
