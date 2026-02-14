# Task: Optimize Phase8-10 Codegen Row Builders Contract Fastpath

## Metadata
- Task ID: TASK-2026-02-14-optimize-phase8-10-codegen-row-builders-contract-fastpath
- Story: STORY-2026-02-13-optimize-spellcrafter-phases
- Status: ready
- Owner: codex
- Priority: p1
- Created: 2026-02-14
- Updated: 2026-02-14

## Objective
Reduce phase8-10 IR row-builder overhead by replacing defensive probing with
contract-strict access on known spell-crafter artifact types.

## Scope Boundaries
- In scope:
- `_build_injection_instance_rows`, `_build_override_target_rows`,
  `_build_mutation_target_rows` fastpath cleanup.
- Contract-backed fail-fast behavior for invalid cleaned/malformed artifacts.
- Out of scope:
- Changing Phase8/9/10 artifact schemas.
- Runtime behavior outside codegen export row building.

## Steps / Checklist
- [ ] Confirm and document contract guarantees for injection and patch-map artifact types.
- [ ] Replace hot-path defensive `try/except AttributeError` probes with direct access where contract-backed.
- [ ] Keep deterministic sorting and payload schema unchanged.
- [ ] Add/adjust tests to prove behavior and error semantics remain correct.
- [ ] Validate with focused unit tests and component harness cProfile.
- [ ] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Contract-strict row builders with lower warm-path overhead.
- Evidence-backed validation for unchanged schema outputs.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/spellbook/spell_crafter/blueprints/injection_plan.py`
- `src/melder/spellbook/spell_crafter/blueprints/patch_maps.py`
- `tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
- `tests/component/melder/spellbook/test_phase_component_cprofile_harness.py`

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py -k "phase8 or phase9 or phase10"`
  - `python -m pytest -q -s tests/component/melder/spellbook/test_phase_component_cprofile_harness.py`

## Risks / Rollback Notes
- Risk: tighter contract enforcement could expose latent invalid-state paths.
- Rollback: restore previous defensive probe behavior while documenting failing contracts.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Current row builders spend hot-path time in methods that still use defensive attribute probing, while upstream builders construct contract-defined `InjectionPlan`/`InjectionSpec` and `OverridePatchMap` artifacts.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase5_opt_rerun_clean_output_run2.txt:23-23, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase5_opt_rerun_clean_output_run2.txt:43-43, src/melder/spellbook/spell_crafter/spell_crafter.py:1419-1478, src/melder/spellbook/spell_crafter/spell_crafter.py:1523-1562, src/melder/spellbook/spell_crafter/blueprints/injection_plan.py:321-427, src/melder/spellbook/spell_crafter/blueprints/injection_plan.py:516-655, src/melder/spellbook/spell_crafter/blueprints/patch_maps.py:75-151, src/melder/spellbook/spell_crafter/blueprints/patch_maps.py:660-696
  IMPACT: Contract-fastpath cleanup is a practical third-ranked optimization with correctness hardening benefits.
  NEXT: Verify cleaned-state call contracts and define explicit fail-fast points before edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Task created from SpellCrafter discovery ranking. Next step is contract audit
and targeted row-builder cleanup design.
