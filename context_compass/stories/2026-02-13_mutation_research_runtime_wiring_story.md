# Story: Wire mutation research to runtime state transitions

## Metadata
- Story ID: STORY-2026-02-13-mutation-research-runtime-wiring
- Epic: EPIC-2026-02-13-src-components-revalidation
- Status: blocked
- Owner: codex
- Priority: p1
- Created: 2026-02-13
- Updated: 2026-02-14

## User Narrative
As a mutation-systems maintainer, I want mutation research flows to emit
deterministic runtime state transitions, so that mutation lifecycle status is
observable and governable by DevOps policies.

## Value / MRP Alignment
Current mutation research objects support session/graph bookkeeping but leave
runtime propagation hooks unresolved. This story closes the execution gap between
research artifacts and SpellSystemStates/ChangeControl state.

## Requirements (Functional)
- Decide and implement one of:
  - Active wiring path from mutation research/promote flows to runtime state
    producers; or
  - Explicit "on hold" runtime gate with no-op behavior and documented contract.
- Implement concrete behavior for currently placeholder hooks where needed:
  - `SpellMutationNode.snapshot_from_spell`
  - `SpellMutationNode.apply_to_blueprint`
  - `CreationMutationNode.snapshot_from_creation`
  - `CreationMutationNode.apply_to_creation`
- Define mutation lifecycle transitions for candidate/quarantine/failure/promote
  events and connect them to SpellSystemStates.
- Ensure `Research.promote_spell_version(...)` has deterministic side effects or
  explicit de-scope behavior.

## Requirements (Non-Functional)
- Maintain deterministic cleanup and no-leak guarantees for research sessions.
- Preserve lock safety in mutation research classes.
- Keep behavior explicit: no hidden side effects in mutation entrypoints.

## Scope Boundaries
- In scope:
- Mutation research runtime wiring and transition contracts.
- Placeholder method implementation or explicit de-scope stubs with tests.
- Out of scope:
- Full mutation algorithm strategy design.
- Broad optimization work unrelated to unknown resolution.
- Entire story is currently out of scope by user direction (2026-02-13).

## Dependencies / Related Work
- `src/melder/spellbook/mutations/mutation_research.py`
- `src/melder/spellbook/mutations/research/research.py`
- `src/melder/spellbook/mutations/research/spell/spell_research.py`
- `src/melder/spellbook/mutations/research/creation/creation_research.py`
- `src/melder/spellbook/mutations/research/spell/node/spell_mutation_node.py`
- `src/melder/spellbook/mutations/research/creation/node/creation_mutation_node.py`
- `src/melder/aether/dev_ops/spell_system_states/spell_system_states.py`
- `context_compass/stories/completed/2026-02-13_spellstate_advanced_flag_producers_story_completed.md`

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-02-13-mutation-wiring-contract - Define runtime contract for mutation research transitions.
- [ ] Task: TASK-2026-02-13-mutation-node-implementation - Implement or explicitly de-scope node snapshot/apply hooks.
- [ ] Task: TASK-2026-02-13-mutation-promote-wiring - Wire `promote_spell_version` runtime effects.
- [ ] Task: TASK-2026-02-13-mutation-state-tests - Add targeted tests for mutation lifecycle transitions.
- [ ] Task: TASK-2026-02-13-mutation-doc-sync - Update unknowns/open-questions docs with resolved evidence.

## Acceptance Criteria
- Mutation research lifecycle has explicit, test-backed runtime transition
  behavior (active path or explicit blocked/de-scoped path).
- No placeholder mutation hook used in runtime path remains undocumented.
- Architecture/components docs reflect current mutation lifecycle truth.

## Validation / Test Plan
- Add/expand tests under mutation research and DevOps state modules.
- Run targeted pytest selection for changed modules.
- Validate evidence with `rg` for hook implementations and producer call sites.

## UX / API / Data Notes
- Internal behavior and documentation; no mandatory public API changes.

## Risks / Mitigations
- Risk: implementing placeholder hooks without clear policy causes unstable
  semantics.
  Mitigation: require explicit transition matrix and tests before enablement.
- Risk: current "mutation on hold" policy conflicts with new wiring.
  Mitigation: support explicit gated mode with stable no-op contract.

## Open Questions
- Should mutation candidate/quarantine/failure transitions be emitted by
  mutation research directly or by change-control orchestration?

## Decision Log
- 2026-02-13: Story created from unknowns investigation and mutation module sweep.
- 2026-02-13: User directed this story to be out of scope for now; work deferred.

## Notes
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Notes section added to enforce active_documentation for in-flight findings.
  EVIDENCE: context_compass/agent_onboarding/agent/general/skills/active_documentation.md:1
  IMPACT: Keeps ticket memory durable across compaction by requiring evidence-backed notes.
  NEXT: Append new findings here as work continues.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Story is blocked/out-of-scope for now by user direction (2026-02-13).
Investigation found mutation research graph/session scaffolding present, but
runtime transition hooks and node snapshot/apply paths remain unresolved and
are deferred until scope reopens.
