# Task: Phase12 No-Overrides Medium-Risk Discovery Lane

## Metadata
- Task ID: TASK-2026-02-16-phase12-no-overrides-medium-risk-discovery
- Story: STORY-2026-02-16-deep-phase12-no-overrides-codegen-strategy-discovery
- Status: ready
- Owner: codex
- Priority: p1
- Created: 2026-02-16
- Updated: 2026-02-16

## Objective
Define medium-risk/medium-reward strategy candidates for
`phase12_no_overrides_executor.py` that can improve generated executor
efficiency without changing external behavior.

## Scope Boundaries
- In scope:
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
- Internal generator architecture and compile-miss preparation.
- Out of scope:
- Overrides path internals.
- Unapproved cross-module refactors.

## Steps / Checklist
- [x] Produce at least 3 medium-risk candidates with tradeoff analysis.
- [x] For each candidate, define expected benchmark impact and revert thresholds.
- [x] Rank candidates by reward potential and contract risk.
- [ ] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Ranked medium-risk strategy list for no-overrides codegen.

## Candidate Backlog (Initial Fill)
| Candidate ID | Proposal | Evidence | Expected Upside |
|---|---|---|---|
| NO-M1 | Emit transient executor signatures/namespaces only for dependency arrays actually used by observed `call_modes` (not fixed `dep1..dep8h`). | src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:1257-1419, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:1536-1591 | Medium compile-size and compile-time reduction for small/medium arity plans. |
| NO-M2 | Add transient-source/code-object cache keyed by normalized transient schema tuple to avoid recompiling identical transient plans. | src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:55-145, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:331-390 | Medium compile-miss reduction on repeated plan signatures. |
| NO-M3 | Introduce shape-specialized step-plan emitter families for dominant plan patterns instead of one monolithic branch-heavy generator. | src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:469-717 | Medium runtime branch-depth and source-size reduction. |
| NO-M4 | Rework kwargs/dependency extraction emission into compact precomputed dependency op lists to reduce emitted source length per step. | src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:523-717 | Medium compile-time improvement with moderate runtime risk. |
| NO-M5 | Cache compiled step-plan source by plan signature when compiling from plan rows to avoid repeated source regeneration for same shape. | src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:151-235, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:469-520 | Medium compile-miss reduction for repeated graph shapes. |

Execution order:
1. NO-M1
2. NO-M2
3. NO-M5
4. NO-M3
5. NO-M4

## Ops Reference (Reuse)
1. Pre-test: unit + fast cprofile x2 + overrides cprofile x2.
2. Implement one candidate only.
3. Post-test: same cadence.
4. Compare against retained checkpoint.
5. If non-winning or failing: immediate revert + post-revert validation pass.
6. Publish explicit `RESULT: RETAINED` or `RESULT: REVERTED` note with artifact path.

## Files / Paths Impacted
- `context_compass/stories/2026-02-16_deep_phase12_no_overrides_codegen_strategy_discovery_story.md`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py` (discovery evidence only unless approved for implementation)

## Validation
- Not run.
- If a candidate moves to implementation, enforce story benchmark gate.
- Recommended commands:
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py -q`
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py -q -s` (twice)
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py -q -s` (twice)

## Risks / Rollback Notes
- Risk: medium-risk changes can alter generated function shape significantly.
- Mitigation: compact slices and strict benchmark keep/revert gate.
- Rollback: immediate revert on any non-winning or failing run.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-16
  TYPE: PLAN
  CLAIM: Opened medium-risk no-overrides discovery lane to maintain a ready queue of candidates between micro and architectural scales.
  EVIDENCE: context_compass/stories/2026-02-16_deep_phase12_no_overrides_codegen_strategy_discovery_story.md:1-123
  IMPACT: Improves iteration speed and consistency by predefining medium-risk options.
  NEXT: Populate ranked medium-risk matrix with measurable hypotheses.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Medium-risk no-overrides lane now contains five ranked candidates, with NO-M1 and NO-M2 prioritized as the first medium-reward compile-size/compile-cache attempts.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:55-145, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:331-390, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:1257-1591
  IMPACT: Ticket now functions as a reusable medium-risk ops queue with ordered next actions.
  NEXT: Execute NO-M1 under benchmark gate and record retained/reverted outcome before NO-M2.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task is the medium-risk lane for no-overrides codegen strategy discovery.
It should produce benchmark-gated candidates ready for compact implementation
attempts.
