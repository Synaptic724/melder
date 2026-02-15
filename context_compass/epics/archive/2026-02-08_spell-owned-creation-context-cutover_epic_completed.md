Completed: 2026-02-08
Summary: Closed and turned in for Spell-Owned CreationContext Runtime Cutover.

# Epic: Spell-Owned CreationContext Runtime Cutover

## Metadata
- Epic ID: EPIC-2026-02-08-spell-owned-creation-context-cutover
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-08
- Updated: 2026-02-08
- Target Window: 2026-Q1
- Related Program/Initiative: Meld runtime hot-path specialization

## Problem / Opportunity
Current runtime ownership is still meld-instance scoped, not spell scoped.
Today `Meld` owns one `_creation_context` and delegates each call into it.
That keeps extra routing on the hot path and does not align with the target
model where each spell owns a static specialized executor frame.

Evidence:
- `src/melder/aether/conduit/meld/meld.py:Meld.__init__` creates `self._creation_context`.
- `src/melder/aether/conduit/meld/meld.py:Meld._meld_without_hooks` calls `self._creation_context._resolver(...)`.
- `src/melder/aether/conduit/meld/meld.py:Meld._comprehensive_meld_with_hooks` calls `self._creation_context._resolver(...)`.
- `src/melder/aether/conduit/meld/meld_context/creation_context.py:CreationContext._resolver` owns existence routing.
- `src/melder/aether/conduit/meld/meld_context/creation_context.py:CreationContext._get_or_compile_override_executor` owns override specialization cache.
- `src/melder/spellbook/spell.py:Spell.__slots__` has no spell-owned creation-context slot.

## MRP Alignment (Most Reasonable Product)
Build a durable execution core where each spell holds one static `CreationContext`
prepared for that spell's execution routes. Meld stays as front-door validation and
hook orchestration only, then performs a lock-free get-or-build on spell context and
executes the spell-owned path with `(caller_creations, overrides)`.

## Goals (Outcomes)
- Move runtime execution ownership from meld instance state to spell-owned context.
- Keep hooks and validation at the Meld front door.
- Support two execution lanes in spell-owned context: normal lane and overrides lane.
- Make context build on miss lock-free and race-tolerant (equivalent output required).
- Remove backward-compatibility shims and delete replaced runtime paths.

## Non-Goals (Explicit Exclusions)
- No epoch system.
- No revalidation/invalidation framework for context misses.
- No backward-compat adapters preserving legacy private runtime APIs.
- No redesign of spell crafting phases beyond wiring required for this cutover.

## Scope Boundaries
- In scope:
  - Add `creation_context` package in meld area for new runtime owner classes.
  - Add `CreationContextBuilder` and `CreationContextFactory`.
  - Add spell-owned context slot and bind/reuse semantics.
  - Rewire Meld to get-or-build spell context and execute it.
  - Migrate runtime methods from `_resolver` and downstream helpers into spell-owned context.
  - Keep hook lifecycle (`pre`, `activation`, `post`, meld hooks) in Meld.
- Out of scope:
  - New override policy semantics.
  - Additional lock model changes for creations/spell locks.
  - Benchmark framework redesign.

## Success Metrics
- Hot path becomes: resolve spell -> validate/hook gate -> spell context lookup/build -> execute.
- No per-call walk through meld-owned runtime helper stack after context exists.
- Spell-owned context executes both no-overrides and overrides lanes with parity.
- Legacy meld-owned runtime artifacts are deleted.

## Requirements (Functional + Non-Functional)
- Functional:
  - `Spell` owns and reuses its `CreationContext`.
  - Missing context is built by Meld via factory/builder and attached to spell.
  - Runtime execute contract takes `caller_creations` and `overrides`.
  - Overrides remain rare-path and branch quickly to fast normal lane when absent.
  - Hooks remain in Meld and do not move into `CreationContext`.
- Non-functional:
  - Miss-path build is lock-free by design.
  - Duplicate concurrent builds are acceptable only if deterministic/equivalent.
  - No backward compatibility shim layer.
  - Ticket documentation must remain compaction-safe.

## Constraints / Assumptions
- Constraint: no lock on missing spell context attach path.
- Constraint: existing creations/spell lock contracts stay intact for instance creation paths.
- Constraint: builder has one job, build a spell-specific context object.
- Assumption: spell-specific context configuration is static until spell is regenerated.

## Dependencies / External References
- `src/melder/aether/conduit/meld/meld.py`
- `src/melder/aether/conduit/meld/meld_context/creation_context.py`
- `src/melder/aether/conduit/meld/meld_context/meld_context.py`
- `src/melder/spellbook/spell.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`

## Milestones (Track Progress)
- [x] Milestone 1: Context Contract and Build Pipeline
  - Success: story `STORY-2026-02-08-creation-context-contract-and-build` accepted.
- [x] Milestone 2: Meld Front-Door Spell Binding
  - Success: story `STORY-2026-02-08-meld-front-door-spell-binding` accepted.
- [x] Milestone 3: Runtime + Codegen Cutover
  - Success: story `STORY-2026-02-08-runtime-migration-codegen-cutover` accepted.

## Stories (Required to Complete)
- [x] Story: `STORY-2026-02-08-creation-context-contract-and-build` - define spell-owned context contract plus builder/factory.
- [x] Story: `STORY-2026-02-08-meld-front-door-spell-binding` - make Meld perform lock-free get-or-build and delegate execution.
- [x] Story: `STORY-2026-02-08-runtime-migration-codegen-cutover` - migrate runtime internals into spell-owned context and remove legacy paths.

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: Complete story `STORY-2026-02-08-creation-context-contract-and-build`.
- [x] Task: Complete story `STORY-2026-02-08-meld-front-door-spell-binding`.
- [x] Task: Complete story `STORY-2026-02-08-runtime-migration-codegen-cutover`.
- [x] Task: `TASK-2026-02-08-creation-context-architecture-components-docs` - align `context_compass/architecture/` and `context_compass/components/` docs with final ownership model.

## Acceptance Criteria (Epic Done)
- `Spell` stores one reusable `CreationContext` for runtime execution.
- `Meld` no longer owns a global runtime context object/cache.
- Meld keeps hooks/validation and delegates execution to spell-owned context.
- Lock-free miss build path is implemented and documented as benign-race.
- Legacy runtime classes/paths replaced by spell-owned cutover are deleted.
- Story/task handoff summaries are complete for compaction.

## Risks / Mitigations
- Risk: mixed ownership during migration causes behavior drift.
  - Mitigation: land by story boundary and remove replaced path immediately.
- Risk: non-deterministic context build under race.
  - Mitigation: constrain builder to spell-static inputs and deterministic output.
- Risk: override lane semantics diverge from existing behavior.
  - Mitigation: keep current Phase 10-12 semantics as immutable contract during cutover.

## Validation / Test Approach
- Unit validation focus:
  - spell-owned context attach/reuse
  - lock-free get-or-build behavior under concurrent calls
  - lane selection parity (normal vs overrides)
  - hook ordering parity at Meld front door
- Benchmark validation focus:
  - compare pre/post hot-path call count and runtime delta on representative spells.

## Rollout / Adoption Plan
- Step 1: land contract/build classes and spell slot.
- Step 2: wire Meld front door to spell-owned get-or-build execution.
- Step 3: migrate runtime internals into spell-owned context and delete legacy path.
- Step 4: run parity checks, then update architecture/components docs.

## Open Questions
- UNKNOWN: regeneration trigger for refreshing a spell-owned context after spell recompilation.
  - Evidence target: `src/melder/spellbook/spell.py` lifecycle + spell crafter regeneration flow.
- UNKNOWN: exact ownership location for override specialization cache after migration.
  - Evidence target: `src/melder/aether/conduit/meld/meld_context/creation_context.py:_override_specialization_cache`.

## Decision Log
- 2026-02-08: `CreationContext` is spell-owned and static per spell instance.
- 2026-02-08: Meld keeps hooks and front-door validation only.
- 2026-02-08: Missing context build path is lock-free; benign races are accepted.
- 2026-02-08: No backward compatibility shims for replaced private runtime methods.
- 2026-02-08: Builder has one job, construct spell-specific `CreationContext`.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
This epic captures a hard cut from meld-owned runtime execution to spell-owned
`CreationContext`. The target flow is deterministic and minimal: Meld validates and
hooks, then executes a spell-owned context built once on demand. The active stories
and tasks below define each boundary so context compaction can resume work safely.

Current implementation status:
- Spell-owned `CreationContext` path is live in code.
- Legacy `MeldContext` runtime files are deleted.
- Phase 12 executor call signatures now use direct creations parameters.
- Pending: broader validation/benchmark evidence and final user acceptance.

