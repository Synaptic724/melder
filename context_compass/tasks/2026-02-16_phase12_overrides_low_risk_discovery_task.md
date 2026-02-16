# Task: Phase12 Overrides Low-Risk Discovery Lane

## Metadata
- Task ID: TASK-2026-02-16-phase12-overrides-low-risk-discovery
- Story: STORY-2026-02-16-deep-phase12-overrides-codegen-strategy-discovery
- Status: ready
- Owner: codex
- Priority: p1
- Created: 2026-02-16
- Updated: 2026-02-16

## Objective
Identify low-risk override codegen candidates that can improve efficiency while
preserving existing override precedence and runtime contracts.

## Scope Boundaries
- In scope:
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
- Compile-prep and generated-source micro-structure candidates.
- Out of scope:
- Public API shape changes.
- High-blast-radius architecture rewrites.

## Steps / Checklist
- [x] Produce at least 3 low-risk candidates with source-backed evidence.
- [x] Define expected benchmark direction and rollback criteria per candidate.
- [x] Rank candidates by effort, risk, and estimated payoff.
- [ ] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Low-risk override-candidate matrix with implementation boundaries.

## Candidate Backlog (Initial Fill)
| Candidate ID | Proposal | Evidence | Expected Upside |
|---|---|---|---|
| OV-L1 | In shape metadata build, prefer row-exported static flags and skip spell object attribute probing when row fields are already present. | src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:609-748 | Low compile-prep attribute-read reduction. |
| OV-L2 | Hoist `required_fields` tuple outside per-row hydration in `_hydrate_steps_from_rows(...)` to avoid per-iteration tuple recreation. | src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2397-2441 | Low compile-prep allocation reduction. |
| OV-L3 | Add fast-empty short-circuit in `_build_step_override_targets(...)` when `override_targets_by_spell_id` is empty. | src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2516-2587 | Low branch/loop overhead reduction for no-target plans. |
| OV-L4 | Deduplicate repeated root-positional override merge emission blocks in kwargs source generator to shrink generated source size. | src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:983-1308 | Low compile-size reduction with minimal runtime risk. |
| OV-L5 | Avoid unnecessary contract payload tuple/dict conversions when `has_contract_payload` is false in row-to-step metadata paths. | src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:609-748, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2397-2486 | Low compile-prep allocation reduction. |

Execution order:
1. OV-L2
2. OV-L1
3. OV-L3
4. OV-L4
5. OV-L5

## Ops Reference (Reuse)
1. Pre-test benchmark cadence (unit + fast x2 + overrides x2).
2. Implement one low-risk candidate only.
3. Post-test same cadence + compare checkpoint.
4. Revert immediately on non-winning/failing outcome.
5. Record `RESULT` note with artifact path before next candidate.

## Files / Paths Impacted
- `context_compass/stories/2026-02-16_deep_phase12_overrides_codegen_strategy_discovery_story.md`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py` (discovery evidence only unless approved for implementation)

## Validation
- Not run.
- If implementation is attempted, enforce story benchmark gate.
- Recommended commands:
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py -q`
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py -q -s` (twice)
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py -q -s` (twice)

## Risks / Rollback Notes
- Risk: even low-risk edits can regress fast lanes.
- Mitigation: keep compact and benchmark-gated with checkpoint comparisons.
- Rollback: immediate revert on non-winning or failing deltas.

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
  CLAIM: Opened low-risk overrides discovery lane to keep a ready list of compact candidates after the first reverted slice.
  EVIDENCE: context_compass/stories/2026-02-16_deep_phase12_overrides_codegen_strategy_discovery_story.md:1-214
  IMPACT: Supports faster retries with clear risk bounds and less re-scoping overhead.
  NEXT: Populate low-risk override matrix and choose first candidate for gated implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Low-risk overrides lane now contains five compact candidates focused on metadata/prep overhead and generated-source-size trimming.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:609-748, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:983-1308, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2397-2587
  IMPACT: Overrides low-risk retries can proceed without additional broad discovery passes.
  NEXT: Execute OV-L2 first and capture checkpoint deltas.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task is the low-risk lane in the overrides discovery queue. It should
provide compact retry options that preserve the existing benchmark discipline.
