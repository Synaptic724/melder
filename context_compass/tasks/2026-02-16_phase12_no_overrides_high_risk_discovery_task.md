# Task: Phase12 No-Overrides High-Risk Discovery Lane

## Metadata
- Task ID: TASK-2026-02-16-phase12-no-overrides-high-risk-discovery
- Story: STORY-2026-02-16-deep-phase12-no-overrides-codegen-strategy-discovery
- Status: ready
- Owner: codex
- Priority: p1
- Created: 2026-02-16
- Updated: 2026-02-16

## Objective
Investigate high-risk/high-reward redesign options for
`phase12_no_overrides_executor.py` that may unlock larger gains but require
stronger controls and explicit decision points.

## Scope Boundaries
- In scope:
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
- Large generator architecture alternatives.
- Out of scope:
- Public contract breaks without explicit approval.
- Implementation beyond bounded experiments.

## Steps / Checklist
- [x] Document at least 2 high-risk redesign candidates and their architecture impact.
- [x] Define prerequisite guards (tests, instrumentation, rollback) per candidate.
- [x] Provide recommendation criteria for promotion to implementation.
- [ ] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- High-risk candidate briefs with migration concerns and payoff hypotheses.

## Candidate Backlog (Initial Fill)
| Candidate ID | Proposal | Evidence | Expected Upside |
|---|---|---|---|
| NO-H1 | Replace transient string-generated executor with a vectorized runtime loop over callable and dependency-index arrays (no generated source path). | src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:1257-1419, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:1428-1531 | High compile-time reduction; high runtime model-change risk. |
| NO-H2 | Segment large step-plan emitted executors into chunked helper functions plus dispatcher to cap function size and compile latency. | src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:469-717 | High win on large plans; higher complexity for exception/diagnostic parity. |
| NO-H3 | Expand transient-unrolled eligibility beyond `Existence.many` by introducing dedicated state carriers for reusable lanes. | src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:421-435, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:523-717 | Potentially high runtime win; high correctness risk around reuse semantics. |
| NO-H4 | Replace source-string generation with direct code-object/AST construction to cut parser overhead and tighten compile artifacts. | src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:440-466, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:1257-1419 | High compile-latency upside; high implementation and debug complexity. |
| NO-H5 | Introduce optional native fast-path call dispatcher for transient call modes (`CALL0..CALL8`) with Python fallback. | src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:1428-1531 | High potential runtime win; high build/distribution risk. |

Execution order:
1. NO-H2
2. NO-H1
3. NO-H4
4. NO-H3
5. NO-H5

## Ops Reference (Reuse)
1. Keep this lane discovery-first; implementation only after explicit decision.
2. If promoted, run full benchmark gate (pre/post/revert).
3. Run one candidate per tranche.
4. Record `RESULT` and artifact path in notes before moving to next candidate.

## Files / Paths Impacted
- `context_compass/stories/2026-02-16_deep_phase12_no_overrides_codegen_strategy_discovery_story.md`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py` (discovery evidence only unless approved for implementation)

## Validation
- Not run.
- If high-risk experiments are implemented, enforce story benchmark gate and revert policy.
- Recommended commands:
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py -q`
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py -q -s` (twice)
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py -q -s` (twice)

## Risks / Rollback Notes
- Risk: high-risk redesign can destabilize generated executor contracts.
- Mitigation: keep this lane discovery-only until explicit promotion decision.
- Rollback: design-stage only; code-stage uses immediate revert on failure/non-win.

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
  CLAIM: Opened high-risk no-overrides discovery lane to isolate deep redesign concepts from regular compact optimization loops.
  EVIDENCE: context_compass/stories/2026-02-16_deep_phase12_no_overrides_codegen_strategy_discovery_story.md:1-123
  IMPACT: Enables deliberate evaluation of high-upside options without disrupting medium/low iteration cadence.
  NEXT: Build candidate briefs with explicit migration and rollback plans.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: STRATEGY_DISCUSSION
  CLAIM: High-risk no-overrides lane is loaded with five redesign candidates and a conservative execution order that prioritizes segmented generator changes before runtime model replacement.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:421-435, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:469-717, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:1257-1531
  IMPACT: High-risk path is now fully documented for future escalation without additional rediscovery.
  NEXT: Keep lane parked until user explicitly promotes high-risk experimentation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task is the high-risk lane for no-overrides strategy discovery. It should
capture deep options and decision criteria before any implementation work.
