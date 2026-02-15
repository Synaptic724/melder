- Completed: 2026-02-13
- Summary: Closed after doc revalidation narrowed the unknown set; SpellContract/MutationContract descriptor behavior was evidenced and documented, and remaining mutation-runtime wiring work stays tracked in `STORY-2026-02-13-mutation-research-runtime-wiring`.

# Story: Wire advanced SpellState flag producers

## Metadata
- Story ID: STORY-2026-02-13-spellstate-advanced-flag-producers
- Epic: EPIC-2026-02-13-src-components-revalidation
- Status: completed
- Owner: codex
- Priority: p1
- Created: 2026-02-13
- Updated: 2026-02-13

## User Narrative
As a runtime/operator maintainer, I want explicit producer paths for advanced
SpellState flags, so that diagnostics and gating behavior are aligned with real
runtime events.

## Value / MRP Alignment
This story closes a source-of-truth gap discovered in architecture/components
revalidation: `contract_violation` and mutation-state flags exist in enums but
do not have confirmed producer call sites. Wiring these paths hardens runtime
observability and prevents docs-to-code drift.

## Requirements (Functional)
- Define and document producer events for:
  - `SpellState.contract_violation`
  - `SpellState.mutation_candidate`
  - `SpellState.mutation_quarantined`
  - `SpellState.mutation_failed`
- Add explicit state-transition helper APIs in `SpellSystemStates` and/or
  `SpellSystemState` for these events.
- Wire call sites from the owning runtime paths (validation, mutation flow,
  incident/policy flow) so producers are traceable.
- Ensure transitions set both `SpellState` flags and matching
  `SpellStateChangeReason` values.

## Requirements (Non-Functional)
- Preserve current locking and thread-safety discipline in DevOps state classes.
- Avoid silent fallback paths that swallow transition failures without evidence.
- Keep transitions deterministic and idempotent for repeated signals.

## Scope Boundaries
- In scope:
- Design and implementation of producer APIs and call sites.
- Targeted documentation updates for architecture/components unknowns.
- Out of scope:
- Broad redesign of mutation systems.
- New user-facing public API surface.

## Dependencies / Related Work
- `src/melder/aether/dev_ops/spell_system_states/spell_system_states.py`
- `src/melder/aether/dev_ops/spell_system_states/spell_system_state.py`
- `src/melder/aether/dev_ops/spell_system_states/spell_state.py`
- `src/melder/aether/dev_ops/spell_system_states/spell_state_change_reason.py`
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/aether/dev_ops/change_control_manager/change_control_manager.py`
- `context_compass/stories/2026-02-13_mutation_research_runtime_wiring_story.md`

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-02-13-state-flag-transition-map - Define transition matrix for advanced flags and reasons.
- [ ] Task: TASK-2026-02-13-state-flag-api - Implement explicit producer helper methods in DevOps state layer.
- [ ] Task: TASK-2026-02-13-state-flag-call-sites - Wire producer call sites from owning runtime paths.
- [ ] Task: TASK-2026-02-13-state-flag-tests - Add unit tests for each producer and transition.
- [ ] Task: TASK-2026-02-13-state-flag-doc-sync - Update architecture/components unknowns with verified evidence.

## Acceptance Criteria
- Every advanced flag/reason pair has at least one concrete producer call site
  or an explicit de-scope decision documented with evidence.
- Runtime tests verify `flags_to_add`/`flags_to_remove` behavior for each new
  producer path.
- Architecture/components docs no longer claim "unknown producer" for any flag
  resolved by this story.

## Validation / Test Plan
- Add targeted tests under DevOps state and owning runtime modules.
- Run targeted pytest selection for changed modules.
- Verify `rg` evidence for producer call sites after implementation.

## UX / API / Data Notes
- Internal runtime behavior only; no direct external API changes expected.

## Risks / Mitigations
- Risk: Overlapping producer paths create inconsistent final flags.
  Mitigation: centralize transition helpers and assert idempotence in tests.
- Risk: Mutation subsystem hold state blocks full wiring.
  Mitigation: implement contract-violation path now and gate mutation paths with
  explicit blocked markers plus follow-up hooks.

## Open Questions
- Should `contract_violation` map to `SpellValidity.invalid` or `gated` in all
  call sites, or vary by policy context?

## Decision Log
- 2026-02-13: Story created from revalidation unknowns sweep.
- 2026-02-13: Closed after evidence pass showed SpellContract/MutationContract descriptor behavior is documented and no immediate implementation work is authorized in this story.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Story closed after docs were updated to reflect the resolved descriptor unknowns
for SpellContract/MutationContract. Remaining runtime producer unknowns are
still documented in architecture/components and tracked for future design/work
via `STORY-2026-02-13-mutation-research-runtime-wiring`.
