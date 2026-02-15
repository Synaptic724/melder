# Story: JIT/AOT Split Discovery and Viability

Completed: 2026-02-15
Summary: Closed after user acceptance; linked discovery/implementation tasks are complete and validated for this story scope.


## Metadata
- Story ID: STORY-2026-02-14-jit-aot-split-discovery-and-viability
- Epic: EPIC-2026-02-14-jit-aot-phase-split-configuration
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-14
- Updated: 2026-02-15

## User Narrative
As a runtime-platform maintainer, I want proof of phase-order and lifecycle
contracts before committing to a JIT/AOT split, so that we do not implement an
invalid phase model.

## Value / MRP Alignment
This story protects the MRP by preventing speculative implementation and forcing
contract evidence for phase ordering, runtime context build behavior, and spell
validity semantics.

## Requirements (Functional)
- Produce an evidence-backed phase-order contract map for requested split shape.
- Produce an evidence-backed CreationContext builder/factory contract map under deferred artifacts.
- Produce an evidence-backed spell-level `resolution_required` lifecycle proposal.
- Produce one explicit assumption challenge and user discussion summary.

## Requirements (Non-Functional)
- Use UNKNOWN-first discipline for all unverified claims.
- Keep all meaningful findings in task `## Notes` with line-range evidence.
- Do not implement runtime behavior changes in this story.

## Scope Boundaries
- In scope:
- Discovery, risk surfacing, and decision shaping.
- Out of scope:
- Code implementation of config switch, spell flag, or runtime execution path.

## Dependencies / Related Work
- `EPIC-2026-02-14-jit-aot-phase-split-configuration`
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context_builder.py`

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-02-14-discovery-jit-aot-phase-order-contract - map and assess phase split feasibility.
- [x] Task: TASK-2026-02-14-discovery-jit-aot-creation-context-builder-runtime-contract - map builder/factory runtime behavior with deferred artifacts.
- [x] Task: TASK-2026-02-14-discovery-jit-aot-resolution-required-spell-contract - define spell-level lifecycle contract.
- [x] Task: TASK-2026-02-14-discovery-jit-aot-assumption-challenge - present explicit pushback and discussion options.
- [x] Task: TASK-2026-02-15-discovery-jit-aot-propagation-contract-surfaces - map final config/bind/transfer/runtime propagation touchpoints before implementation.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- Discovery confirms whether requested 1-7 / 8-12 split is contract-compatible.
- One explicit "challenge questionable idea" discussion output is captured for user review.
- Story concludes with a decision-ready implementation scope for downstream stories.

## Validation / Test Plan
- Discovery-only validation via source evidence and decision logs.
- No runtime test execution required in this story.

## UX / API / Data Notes
- Potential API/config changes are deferred to implementation stories after discovery.

## Risks / Mitigations
- Risk: discovery may show requested split is not viable as stated.
  Mitigation: provide alternatives with tradeoffs instead of forcing a brittle design.

## Open Questions
- Are phases 6-7 semantically allowed before 8-11 in current contracts?
- Should deferred runtime set include phase 12 explicitly or stay 8-11 focused?

## Decision Log
- 2026-02-14: Discovery story created as mandatory gate before implementation stories proceed.

## Notes
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Final discovery gate is complete; propagation map and implementation order are now evidence-backed and ready for execution.
  EVIDENCE: context_compass/tasks/2026-02-15_discovery_jit_aot_propagation_contract_surfaces_task.md:31-88
  IMPACT: Story can transition from discovery to implementation execution lanes without additional broad repo reads.
  NEXT: Route active work to `TASK-2026-02-15-implement-jit-aot-config-flag-and-fluent-api`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: DECISION
  CLAIM: User selected the `A hybrid_rule_bound` implementation lane with non-breaking default behavior (`full_ahead_of_time_compilation=true`) and propagation requirements for conjure bind, late bind, and transfer (owned spells only).
  EVIDENCE: context_compass/tasks/2026-02-14_discovery_jit_aot_assumption_challenge_task.md:31-53, context_compass/tasks/2026-02-15_discovery_jit_aot_propagation_contract_surfaces_task.md:1-88
  IMPACT: Discovery lane now focuses on one final propagation-surface mapping task rather than option selection.
  NEXT: Execute `TASK-2026-02-15-discovery-jit-aot-propagation-contract-surfaces` and then promote detailed implementation stories/tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: DECISION_REQUEST
  CLAIM: Discovery package is complete and now requires user option selection (`A hybrid_rule_bound` / `B deferred_optional_builder` / `C strict_aot_only`) to close this story and open implementation planning.
  EVIDENCE: context_compass/tasks/2026-02-14_discovery_jit_aot_phase_order_contract_task.md:31-39, context_compass/tasks/2026-02-14_discovery_jit_aot_creation_context_builder_runtime_contract_task.md:34-44, context_compass/tasks/2026-02-14_discovery_jit_aot_resolution_required_spell_contract_task.md:31-45, context_compass/tasks/2026-02-14_discovery_jit_aot_assumption_challenge_task.md:31-53
  IMPACT: Story is no longer blocked by evidence gathering; only decision capture remains.
  NEXT: Record user choice and convert approved path into implementation tasks in configuration/runtime stories.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Existing helper methods expose structural-only and full-run pathways, but full run order currently places 8-11 before 6-7.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:5018-5045, src/melder/spellbook/spell_crafter/spell_crafter.py:5058-5069, src/melder/spellbook/spell.py:1270-1297, src/melder/spellbook/spell.py:1305-1319
  IMPACT: Discovery must validate or reject the requested phase split before implementation.
  NEXT: Execute `TASK-2026-02-14-discovery-jit-aot-phase-order-contract`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Discovery story has completed option selection and propagation-surface mapping.
Next active lane is implementation, starting with config/fluent API.

