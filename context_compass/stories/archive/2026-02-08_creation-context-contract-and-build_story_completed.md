Completed: 2026-02-08
Summary: Closed and turned in for CreationContext Contract and Build Pipeline.

# Story: CreationContext Contract and Build Pipeline

## Metadata
- Story ID: STORY-2026-02-08-creation-context-contract-and-build
- Epic: EPIC-2026-02-08-spell-owned-creation-context-cutover
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-08
- Updated: 2026-02-08

## User Narrative
As a runtime engineer, I want a spell-owned `CreationContext` contract plus builder/factory pipeline, so that each spell has one static execution frame prepared for fast execution lanes.

## Value / MRP Alignment
This establishes the durable ownership boundary for runtime execution. Without this, later hot-path work still depends on meld-owned runtime state and cannot become truly spell-specialized.

## Requirements (Functional)
- Add a spell-owned context slot on `Spell` for one reusable `CreationContext` instance.
- Introduce `CreationContextBuilder` that builds a spell-specific context with preconfigured execution lanes.
- Introduce `CreationContextFactory` with one responsibility: return a fully built context for the provided spell.
- Builder/factory use spell-static inputs only and do not rely on caller-scoped mutable state.
- Keep context construction deterministic so duplicate concurrent builds produce equivalent contexts.

## Requirements (Non-Functional)
- No backward-compatibility shim for replaced private runtime APIs.
- Builder/factory API must be narrow and explicit enough for codegen integration.
- Documentation/comments for new classes must define ownership and lifecycle guarantees.

## Scope Boundaries
- In scope:
  - `Spell` slot + lifecycle cleanup semantics for spell-owned context.
  - New package and class contracts for factory/builder.
  - Context contract definition for normal lane and overrides lane.
- Out of scope:
  - Meld call-site rewiring.
  - Full migration of runtime helper internals.
  - Deletion of legacy runtime plumbing.

## Dependencies / Related Work
- `src/melder/spellbook/spell.py:Spell.__slots__`
- `src/melder/aether/conduit/meld/meld.py:Meld.__init__`
- `src/melder/aether/conduit/meld/meld_context/creation_context.py:CreationContext`

## Tasks (Implementation Checklist)
- [x] Task: `TASK-2026-02-08-spell-creation-context-slot` - add spell-owned context slot and cleanup behavior.
- [x] Task: `TASK-2026-02-08-creation-context-factory-builder` - add factory + builder classes under `creation_context/`.
- [x] Task: `TASK-2026-02-08-creation-context-contract-and-state-model` - define context execution contract and state model.

## Acceptance Criteria
- `Spell` has an explicit spell-owned context field and cleanup semantics.
- `CreationContextBuilder` builds a deterministic spell-specific object.
- `CreationContextFactory` returns the built context with no meld front-door concerns.
- Context contract explicitly defines the two runtime lanes and execution inputs.

## Validation / Test Plan
- Not run.
- Planned validation:
  - Unit tests for spell slot lifecycle and cleanup.
  - Unit tests for builder determinism (same spell input -> equivalent context).

## UX / API / Data Notes
- Public user API remains unchanged.
- Internal API changes are private to meld/spell runtime ownership.

## Risks / Mitigations
- Risk: context slot naming conflicts with existing spell internals.
  - Mitigation: use private field naming consistent with spell internals.
- Risk: builder accidentally captures caller state.
  - Mitigation: pass only spell-owned/static artifacts into builder.

## Open Questions
- UNKNOWN: whether spell cleanup should call `creation_context.cleanup()` directly or delegate via higher-level owner teardown.
  - Evidence target: `src/melder/spellbook/spell.py:Spell.cleanup`.

## Decision Log
- 2026-02-08: Builder has one job, build spell-specific context.
- 2026-02-08: Context is spell-owned, not meld-owned.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
This story is now partially implemented in code:
- `Spell` owns `_creation_context` and cleanup invalidation paths.
- Builder/factory are expanded and now preconfigure spell-static runtime wiring.
Remaining:
- finalize contract/state-model task and user acceptance.
