# Task: Phase12 No-Overrides Low-Risk Discovery Lane

## Metadata
- Task ID: TASK-2026-02-16-phase12-no-overrides-low-risk-discovery
- Story: STORY-2026-02-16-deep-phase12-no-overrides-codegen-strategy-discovery
- Status: ready
- Owner: codex
- Priority: p1
- Created: 2026-02-16
- Updated: 2026-02-16

## Objective
Identify low-risk efficiency candidates in
`phase12_no_overrides_executor.py` that preserve executor contracts and can be
implemented in compact slices.

## Scope Boundaries
- In scope:
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
- Generated-source structure and compile preparation overhead.
- Out of scope:
- Overrides emitter behavior.
- Public API or semantic contract changes.

## Steps / Checklist
- [x] Build a low-risk candidate list (minimum 3) with evidence and expected impact.
- [x] Label each candidate with blast radius and rollback conditions.
- [x] Define which unit + benchmark lanes gate candidate retention.
- [ ] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Low-risk discovery matrix for no-overrides codegen.

## Candidate Backlog (Initial Fill)
| Candidate ID | Proposal | Evidence | Expected Upside |
|---|---|---|---|
| NO-L1 | Emit static creations-target routing per step (CALLER/SPELLSPACE/OWNER) using compile-time `plan_step.creations_target_kind` instead of runtime branch ladders. | src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:523-579 | Low runtime branch reduction on every step execution. |
| NO-L2 | Emit registration blocks only when `plan_step.must_register` requires it across non-`many` lanes (not just `many`). | src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:523-717, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:728-826 | Low write-path overhead reduction for steps that do not need registration. |
| NO-L3 | Tighten `_normalize_transient_schema(...)` conversions to avoid unnecessary tuple allocations when schema payload already contains tuples. | src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:331-390 | Low compile-prep allocation reduction on transient compile path. |
| NO-L4 | Unify the duplicated transient-vs-step-plan compile decision logic used by two public compile entrypoints into one shared helper path. | src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:114-145, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:206-235 | Low maintenance + low compile-path overhead from duplicate setup removal. |
| NO-L5 | Precompute and cache `_supports_transient_unrolled_plan(...)` eligibility on plan signature to skip repeated lane checks for identical shapes. | src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:421-435 | Low compile decision overhead on repeated identical plans. |

Execution order:
1. NO-L1
2. NO-L4
3. NO-L2
4. NO-L3
5. NO-L5

## Ops Reference (Reuse)
1. Pre-test: unit + fast cprofile x2 + overrides cprofile x2.
2. Execute one low-risk candidate.
3. Post-test same cadence + checkpoint comparison.
4. Revert on any failure/non-winning delta.
5. Record explicit `RESULT` and artifact path before next candidate.

## Files / Paths Impacted
- `context_compass/stories/2026-02-16_deep_phase12_no_overrides_codegen_strategy_discovery_story.md`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py` (discovery evidence only unless approved for implementation)

## Validation
- Not run.
- If implementation is attempted, enforce story benchmark gate.
- Recommended commands:
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py -q`
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py -q -s` (twice)
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py -q -s` (twice)

## Risks / Rollback Notes
- Risk: low-risk candidates can still leak into hot-path semantics.
- Mitigation: keep strict evidence + benchmark gating before retain decisions.
- Rollback: raise `DECISION_REQUEST` on non-winning/failing outcomes; revert only on user decision.

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
  CLAIM: Opened low-risk no-overrides discovery lane so iteration can pull bounded candidates from a persistent queue.
  EVIDENCE: context_compass/stories/2026-02-16_deep_phase12_no_overrides_codegen_strategy_discovery_story.md:1-123
  IMPACT: Reduces time lost on repeated rediscovery and keeps work organized by risk.
  NEXT: Populate low-risk matrix with evidence-backed options.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Low-risk no-overrides lane is now loaded with five compact candidates focused on routing-branch elimination, registration gating, and compile-path deduplication.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:114-145, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:331-435, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:523-826
  IMPACT: Low-risk ticket can move directly into benchmark-gated implementation attempts without further broad scans.
  NEXT: Start with NO-L1 and record checkpoint deltas before selecting NO-L4.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task is the low-risk lane for no-overrides codegen strategy work. It
should feed compact implementation attempts with clear user-directed decision criteria (`DECISION_REQUEST` on non-winning/failing outcomes).
