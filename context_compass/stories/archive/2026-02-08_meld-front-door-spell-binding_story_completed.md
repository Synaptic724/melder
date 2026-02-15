Completed: 2026-02-08
Summary: Closed and turned in for Meld Front-Door Spell Binding.

# Story: Meld Front-Door Spell Binding

## Metadata
- Story ID: STORY-2026-02-08-meld-front-door-spell-binding
- Epic: EPIC-2026-02-08-spell-owned-creation-context-cutover
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-08
- Updated: 2026-02-08

## User Narrative
As a meld runtime owner, I want Meld to perform spell-context get-or-build and delegate execution, so that Meld stays a validator/hook front door and execution runs through spell-owned context.

## Value / MRP Alignment
This story enforces the architectural split: Meld handles input, validity, and hooks; spell-owned context handles runtime execution. That split is required for a durable hot path and later codegen specialization.

## Requirements (Functional)
- Keep spell resolution and front-door validation in `Meld.meld`.
- Keep all hook firing in Meld (`pre`, `activation`, `post`, meld hooks).
- Replace meld-owned runtime invocation with spell-owned context invocation.
- Implement lock-free context miss path:
  - read spell context
  - if missing, build via factory/builder
  - assign directly to spell with no lock
  - execute through spell-owned context
- Runtime execute call takes `caller_creations` and `overrides`.

## Requirements (Non-Functional)
- Duplicate context builds under race are acceptable only if equivalent.
- No new global caches in Meld for runtime execution objects.
- Preserve existing hook order and error behavior contracts.

## Scope Boundaries
- In scope:
  - `Meld` front-door rewrite to get-or-build spell context.
  - Remove meld-owned context field usage.
  - Preserve/verify front-door hook flow.
- Out of scope:
  - Deep runtime helper migration internals.
  - codegen emitter redesign.

## Dependencies / Related Work
- `src/melder/aether/conduit/meld/meld.py:Meld.meld`
- `src/melder/aether/conduit/meld/meld.py:Meld._meld_without_hooks`
- `src/melder/aether/conduit/meld/meld.py:Meld._comprehensive_meld_with_hooks`
- `src/melder/aether/conduit/meld/meld.py:Meld._fire_meld_hooks`

## Tasks (Implementation Checklist)
- [x] Task: `TASK-2026-02-08-meld-get-or-build-creation-context` - rewire Meld to spell-owned get-or-build execution.
- [x] Task: `TASK-2026-02-08-meld-frontdoor-hook-validation-boundary` - lock down front-door boundary and hook behavior.
- [x] Task: `TASK-2026-02-08-remove-meld-owned-runtime-context` - remove meld-owned runtime context field and stale paths.

## Acceptance Criteria
- `Meld` does not own a runtime context object for execution.
- `Meld` resolves spell, runs validity gates, runs hooks, and delegates execute only.
- Lock-free context miss path is implemented in Meld and documented.
- Hook behavior parity is preserved for pre/activation/post and meld hooks.

## Validation / Test Plan
- Not run.
- Planned validation:
  - Unit tests covering hook order before/after cutover.
  - Unit tests for lock-free context get-or-build path.

## UX / API / Data Notes
- No user-facing API change.
- Internal runtime ownership and call path change only.

## Risks / Mitigations
- Risk: hook behavior drift during front-door rewrite.
  - Mitigation: preserve existing hook entry points and assertions.
- Risk: stale meld-owned field remains and causes mixed routing.
  - Mitigation: delete old field and routes in same story.

## Open Questions
- UNKNOWN: whether meld cleanup should clear spell-owned context references, or spell cleanup alone should own that lifecycle.
  - Evidence target: `src/melder/aether/conduit/meld/meld.py:cleanup` and `src/melder/spellbook/spell.py:cleanup`.

## Decision Log
- 2026-02-08: Hooks stay in Meld.
- 2026-02-08: Missing context path is lock-free and race-tolerant.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
This story applies the front-door ownership split in runtime code. After completion, Meld only gates/validates/hooks and then executes spell-owned context.
