# Task: Phase12 Overrides Medium-Risk Discovery Lane

Completed: 2026-02-16
Summary: Turned in per user direction after medium-risk overrides discovery
backlog was expanded and execution ordering was finalized.

## Metadata
- Task ID: TASK-2026-02-16-phase12-overrides-medium-risk-discovery
- Story: STORY-2026-02-16-deep-phase12-overrides-codegen-strategy-discovery
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-16
- Updated: 2026-02-16

## Objective
Define medium-risk/medium-reward override codegen candidates for
`phase12_overrides_executor.py` with explicit implementation boundaries and
benchmark criteria.

## Scope Boundaries
- In scope:
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
- Compile-miss preparation and shape-source generation strategies.
- Out of scope:
- Unapproved cross-module architecture changes.
- Public contract changes.

## Steps / Checklist
- [x] Produce at least 3 medium-risk candidates with tradeoff analysis.
- [x] Define measurable hypotheses and non-winning `DECISION_REQUEST` conditions per candidate.
- [x] Rank candidates for execution order under current benchmark gate.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Ranked medium-risk candidate list for overrides codegen.

## Candidate Backlog (Initial Fill)
| Candidate ID | Proposal | Evidence | Expected Upside |
|---|---|---|---|
| OV-M1 | Reuse one prefiltered step-target tuple result for both step-target counts and compile namespace binding (avoid duplicate prefilter passes). | src/melder/aether/conduit/meld/creation_context/creation_context.py:1109-1177, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:269-334, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:337-433, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2516-2587 | Medium compile-miss reduction in override specialization path. |
| OV-M2 | Hydrate plan rows once and pass hydrated structures through compile pipeline instead of rebuilding row-derived objects in multiple steps. | src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:609-748, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2397-2486, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:337-433 | Medium compile-prep reduction with moderate plumbing risk. |
| OV-M3 | Split shape-source emission into targeted-overrides and no-targeted-overrides variants to reduce emitted branch mass per shape. | src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:751-848, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1691-2380 | Medium compile-size reduction and possibly better instruction-cache locality. |
| OV-M4 | Extract only heavy dependency-count>2 kwargs error/collection emission into shared helper path while keeping fast inline paths for 0/1/2. | src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:983-1308 | Medium source-size reduction with controlled runtime call overhead. |
| OV-M5 | Precompute dependency literal fragments in metadata phase and reuse during source emission to reduce repeated repr/string formatting. | src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:609-748, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:983-1308 | Medium compile-prep and source-emission reduction. |
| OV-M6 | Add a context-local cache for grouped `override_targets_by_spell_id` keyed by socket shape to avoid rebuilding row-to-socket maps on repeated miss compiles. | src/melder/aether/conduit/meld/creation_context/creation_context.py:653-675, src/melder/aether/conduit/meld/creation_context/creation_context.py:875-924 | Medium compile-miss preprocessing reduction for recurring shape keys. |
| OV-M7 | Thread precomputed `step_override_targets` directly into compile-core namespace binding path to avoid second `_build_step_override_targets(...)` dispatch on miss compile. | src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:269-334, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:337-433, src/melder/aether/conduit/meld/creation_context/creation_context.py:1109-1177 | Medium compile-miss reduction with moderate compile API churn. |
| OV-M8 | Pre-normalize dependency-order and contract-payload fields in exported plan rows so metadata and hydration stages reuse pre-baked immutable tuples. | src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:609-748, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2397-2486 | Medium compile-prep reduction at the cost of row-schema evolution risk. |

Execution order:
1. OV-M1
2. OV-M6
3. OV-M2
4. OV-M8
5. OV-M4
6. OV-M3
7. OV-M5
8. OV-M7

## Ops Reference (Reuse)
1. Pre-test (unit + fast x2 + overrides x2).
2. Execute one medium-risk candidate per tranche.
3. Post-test same cadence; compare checkpoint.
4. On any non-winning delta or test failure, raise `DECISION_REQUEST` and wait for user keep/revert direction.
5. Publish `RESULT` note and artifact path before moving to next candidate.

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
- Risk: medium-risk candidates may shift compile/runtime balance unexpectedly.
- Mitigation: strict checkpoint comparison and mandatory `DECISION_REQUEST` escalation on non-winning deltas.
- Rollback: if validation fails or delta loses, raise `DECISION_REQUEST`; revert only on user decision.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [x] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: RESULT: TURNED_IN - phase12 overrides medium-risk discovery ticket is closed per user direction.
  EVIDENCE: context_compass/tasks/completed/2026-02-16_phase12_overrides_medium_risk_discovery_task.md:1-95, context_compass/stories/2026-02-16_deep_phase12_overrides_codegen_strategy_discovery_story.md:42-53, context_compass/epics/2026-02-15_creationcontext_phase12_codegen_optimization_epic.md:90-111
  IMPACT: Medium overrides queue remains documented for reuse while active routing can continue in high-risk lanes.
  NEXT: Continue high-risk overrides/creationcontext execution with the same benchmark gate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: PLAN
  CLAIM: Opened medium-risk overrides discovery lane to target medium-reward strategies after the first compact candidate reverted.
  EVIDENCE: context_compass/stories/2026-02-16_deep_phase12_overrides_codegen_strategy_discovery_story.md:1-214
  IMPACT: Establishes a pre-ranked queue for next attempts without repeating broad discovery.
  NEXT: Populate medium-risk matrix and select first candidate for benchmark-gated implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Medium-risk overrides lane is now loaded with five candidates and ranked toward reuse-first compile-miss reductions before larger emitter restructuring.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context.py:1109-1177, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:337-433, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:983-1308, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2516-2587
  IMPACT: Medium lane can be executed iteratively from this task without re-scouting candidate options.
  NEXT: Start with OV-M1 under benchmark gate and only advance if RESULT is retained.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: PLAN
  CLAIM: Discovery iteration 2 expanded the medium-risk overrides backlog from five to eight candidates, prioritizing additional compile-miss preprocessing reuse options.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context.py:653-675, src/melder/aether/conduit/meld/creation_context/creation_context.py:875-924, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:269-334, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:609-748, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2397-2486
  IMPACT: The medium lane now has enough depth for multiple cycles without leaving the queue.
  NEXT: Keep `OV-M1` first; if reverted, move to `OV-M6` then `OV-M2`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task is the medium-risk lane for overrides strategy discovery and is the
recommended reference lane for medium-reward iteration attempts. It is now
turned in per user direction.
