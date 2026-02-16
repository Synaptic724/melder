# Task: Phase12 Overrides High-Risk Discovery Lane

## Metadata
- Task ID: TASK-2026-02-16-phase12-overrides-high-risk-discovery
- Story: STORY-2026-02-16-deep-phase12-overrides-codegen-strategy-discovery
- Status: ready
- Owner: codex
- Priority: p1
- Created: 2026-02-16
- Updated: 2026-02-16

## Objective
Investigate high-risk/high-reward override codegen redesign options that may
unlock larger gains but require explicit architectural safeguards.

## Scope Boundaries
- In scope:
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
- Deep generator architecture alternatives and migration risks.
- Out of scope:
- Public API breaks without explicit approval.
- Immediate large implementation changes.

## Steps / Checklist
- [x] Define at least 2 high-risk redesign candidates with architecture impact notes.
- [x] Specify required instrumentation, tests, and rollback guardrails per candidate.
- [x] Produce decision criteria for promotion to implementation.
- [ ] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- High-risk redesign briefs and promotion criteria.

## Candidate Backlog (Initial Fill)
| Candidate ID | Proposal | Evidence | Expected Upside |
|---|---|---|---|
| OV-H1 | Segment monolithic shape-generated executor into per-step helper callables plus a thin coordinator to shrink compile payloads. | src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:751-848, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1691-2380 | High compile-size reduction; high runtime-call overhead/regression risk. |
| OV-H2 | Replace socket-ref keyed override map with compact indexed payload tables resolved at compile time. | src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:869-981, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:983-1308, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2516-2587 | High runtime lookup and source-size improvements; high contract-change risk. |
| OV-H3 | Replace string-line source generation with AST/code-object construction for shape lanes. | src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:751-848, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:869-1689 | High compile-path reduction potential; very high complexity. |
| OV-H4 | Introduce two-tier execution model: generic interpreter lane for cold shapes and compiled lane only for hot shapes. | src/melder/aether/conduit/meld/creation_context/creation_context.py:741-818, src/melder/aether/conduit/meld/creation_context/creation_context.py:1046-1107, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:337-433 | High end-to-end efficiency potential; high architecture and observability requirements. |
| OV-H5 | Precompile top-N override shapes during conjure/warm phase and defer tail shapes to on-demand compile. | src/melder/aether/conduit/meld/creation_context/creation_context.py:1046-1235, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:337-433 | High latency improvement for common shapes; high upfront compile and invalidation risk. |

Execution order:
1. OV-H1
2. OV-H4
3. OV-H3
4. OV-H5
5. OV-H2

## Ops Reference (Reuse)
1. Keep lane discovery-first until explicit promotion.
2. If promoted, execute one high-risk candidate at a time.
3. Full pre/post/revert benchmark gate is mandatory.
4. Do not proceed to next high-risk candidate without explicit `RESULT` note.

## Files / Paths Impacted
- `context_compass/stories/2026-02-16_deep_phase12_overrides_codegen_strategy_discovery_story.md`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py` (discovery evidence only unless approved for implementation)

## Validation
- Not run.
- If high-risk implementation is approved, enforce story benchmark gate.
- Recommended commands:
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py -q`
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py -q -s` (twice)
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py -q -s` (twice)

## Risks / Rollback Notes
- Risk: high-risk changes can regress both fast and override lanes.
- Mitigation: discovery-first, bounded experiments only after explicit decision.
- Rollback: if coded, revert immediately on first failing/non-winning gate.

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
  CLAIM: Opened high-risk overrides discovery lane to isolate deeper redesign exploration from regular compact optimization passes.
  EVIDENCE: context_compass/stories/2026-02-16_deep_phase12_overrides_codegen_strategy_discovery_story.md:1-214
  IMPACT: Keeps high-upside options visible while protecting current execution cadence.
  NEXT: Draft candidate redesign briefs with migration and fallback strategy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: STRATEGY_DISCUSSION
  CLAIM: High-risk overrides lane now has five architectural options and a conservative execution order prioritizing compile-size reduction before contract-level payload redesign.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:751-848, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:869-2380, src/melder/aether/conduit/meld/creation_context/creation_context.py:741-1235
  IMPACT: High-risk exploration can be resumed from this task without additional discovery setup.
  NEXT: Keep this lane parked unless explicitly selected after low/medium outcomes plateau.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task is the high-risk lane for overrides strategy discovery. It captures
major redesign options and decision criteria before any implementation push.
