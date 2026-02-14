# Story: Optimize Meld Paths

## Metadata
- Story ID: STORY-2026-02-13-optimize-meld-paths
- Epic: EPIC-2026-02-13-optimize-melder
- Status: in_progress
- Owner: codex
- Priority: p0
- Created: 2026-02-13
- Updated: 2026-02-14

## User Narrative
As a Melder maintainer, I want meld path hotspots mapped and prioritized, so
that high-frequency runtime resolution remains fast and predictable.

## Value / MRP Alignment
Meld is a core hot path. Discovery-first optimization ensures we improve
throughput without introducing semantic drift in resolution behavior.

## Requirements (Functional)
- Identify key meld path cost centers in entry, gating, lookup, and dispatch.
- Produce a ranked optimization candidate list with evidence.
- Capture follow-up implementation tasks from discovery findings.

## Requirements (Non-Functional)
- Discovery pass must avoid behavior changes.
- Evidence must include concrete file/symbol references and any measured output.

## Scope Boundaries
- In scope:
- `Conduit.meld` and `Meld` runtime path analysis.
- Resolution dispatch and gating behavior cost analysis.
- Out of scope:
- Conjure-phase planning.
- Mutation research runtime wiring.

## Dependencies / Related Work
- `src/melder/aether/conduit/conduit.py`
- `src/melder/aether/conduit/meld/meld.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context.py`
- `src/melder/spellbook/spell.py`
- `benchmarks/testing_other_di/run_codegen_benchmark_deltas.py`
- `benchmarks/testing_other_di/results/codegen_benchmark_report_smoke_v2_pass12.json`
- `tests/component/melder/utilities/synchronization/test_creation_gate_component.py`
- `EPIC-2026-02-13-optimize-melder`

## Discovery Findings (How Meld Works)
### 1) Conduit boundary behavior
- `Conduit.meld` is the front door and always delegates to `self._meld.meld(...)`.
- In dynamic mode, it enforces CreationGate admission before delegation:
  - fail fast if closed,
  - wait when disabled,
  - register/unregister one ticket around the meld call.
- In automatic mode, it bypasses gate checks and directly delegates.
- Evidence: `src/melder/aether/conduit/conduit.py:2261`, `src/melder/aether/conduit/conduit.py:2345`, `src/melder/aether/conduit/conduit.py:2367`.

### 2) Meld front-door resolution and execution lanes
- `Meld.meld` first normalizes per-call overrides (`dict` copy or `__args__` list wrapper).
- Spell resolution then takes one of two cache-backed paths:
  - `spell` as `str` -> `_spell_id_resolution_cache` -> `_resolve_spell_by_id` on miss.
  - non-string inputs -> `_input_resolution_cache` keyed by `(spell_name, spell, spellframe, binding_name)` (or id-based fallback when unhashable) -> `_resolve_spell(...)` on miss.
- If spellbook validation is enabled, it runs lineage/resolution gating before execute.
- Execute branch:
  - no-hooks lane -> call precompiled no-hooks executor,
  - hooks-enabled lane -> run pre hooks, execute compiled hooks executor, optional activation hooks (when `created=True`), then post hooks.
- Evidence: `src/melder/aether/conduit/meld/meld.py:288`, `src/melder/aether/conduit/meld/meld.py:297`, `src/melder/aether/conduit/meld/meld.py:308`, `src/melder/aether/conduit/meld/meld.py:336`, `src/melder/aether/conduit/meld/meld.py:342`, `src/melder/aether/conduit/meld/meld.py:365`.

### 3) Spell identity resolution model
- `_resolve_spell` supports:
  - direct spell_id path,
  - spell/spellframe/binding normalized lookup path,
  - spell_name-only lookup path via `SpellInputUtils.make_spell_key_from_parts`.
- `_resolve_spell_by_lookup_key` checks local first, then contracted maps.
- Evidence: `src/melder/aether/conduit/meld/meld.py:869`, `src/melder/aether/conduit/meld/meld.py:933`, `src/melder/aether/conduit/meld/meld.py:993`, `src/melder/aether/conduit/meld/meld.py:1032`, `src/melder/aether/conduit/meld/meld.py:1038`.

### 4) Validation and revalidation gates on hot path
- `_ensure_lineage_resolvable` can trigger:
  - structural revalidation (`spell.run_structural_phases`) when state is unknown/gated,
  - per-conduit resolution revalidation (`_run_resolution_phases_for_target_spell`) when resolution validity is unknown/gated.
- `_gated_validation_required` also checks change-control dirty roots on each call path and raises when gated dirty.
- `_check_contracts_and_force_revalidation` inspects call signatures for `SpellContract` defaults and forces resolution validity to gated when contracts are present/resolved.
- Evidence: `src/melder/aether/conduit/meld/meld.py:400`, `src/melder/aether/conduit/meld/meld.py:439`, `src/melder/aether/conduit/meld/meld.py:458`, `src/melder/aether/conduit/meld/meld.py:517`, `src/melder/aether/conduit/meld/meld.py:569`, `src/melder/aether/conduit/meld/meld.py:661`.

### 5) CreationContext runtime execution shape
- CreationContext builds four compiled runtime doors at init:
  - hooks+overrides,
  - hooks+no-overrides,
  - no-hooks+overrides,
  - no-hooks+no-overrides.
- Override path behavior:
  - split `__args__` positional payload,
  - apply phase10 patch-map normalization when targeted payload exists,
  - derive socket-shape signature,
  - fetch/compile cached phase12 override executor keyed by `(plan_signature, socket_shape, positional_arity)`.
- Evidence: `src/melder/aether/conduit/meld/creation_context/creation_context.py:240`, `src/melder/aether/conduit/meld/creation_context/creation_context.py:246`, `src/melder/aether/conduit/meld/creation_context/creation_context.py:277`, `src/melder/aether/conduit/meld/creation_context/creation_context.py:503`, `src/melder/aether/conduit/meld/creation_context/creation_context.py:547`, `src/melder/aether/conduit/meld/creation_context/creation_context.py:581`, `src/melder/aether/conduit/meld/creation_context/creation_context.py:766`, `src/melder/aether/conduit/meld/creation_context/creation_context.py:784`.

### 6) Existing baseline artifact (no new benchmark run in this discovery)
- Current stored benchmark report includes route medians showing wide spread between warm root and override-heavy lanes.
- Example from pass12 report:
  - `warm_root_ns`: 3500
  - `warm_spellspace_ns`: 104200
  - `warm_override_root_args_ns`: 512900
  - `warm_override_targeted_ns`: 800000
  - `warm_mixed_ns`: 58100
- Evidence: `benchmarks/testing_other_di/results/codegen_benchmark_report_smoke_v2_pass12.json:20`.

## Hotspot Candidates (Ranked)
1. Contract-default inspection on meld path:
   - `_iter_spell_contract_defaults` uses `inspect.signature` at runtime when contracts are checked.
   - Evidence: `src/melder/aether/conduit/meld/meld.py:594`, `src/melder/aether/conduit/meld/meld.py:661`.
2. Dynamic gate/ticket overhead in dynamic-mode front door:
   - gate checks + ticket register/unregister happen on each dynamic call.
   - Evidence: `src/melder/aether/conduit/conduit.py:2345`, `src/melder/aether/conduit/conduit.py:2356`, `src/melder/aether/conduit/conduit.py:2365`.
3. Front-door input resolution key handling:
   - tuple construction + hash attempt + fallback key building when unhashable.
   - Evidence: `src/melder/aether/conduit/meld/meld.py:309`, `src/melder/aether/conduit/meld/meld.py:311`, `src/melder/aether/conduit/meld/meld.py:313`.
4. Override-lane shape building for targeted overrides:
   - override payload normalization, socket-shape grouping/sorting, specialization lookup/compile.
   - Evidence: `src/melder/aether/conduit/meld/creation_context/creation_context.py:554`, `src/melder/aether/conduit/meld/creation_context/creation_context.py:646`, `src/melder/aether/conduit/meld/creation_context/creation_context.py:744`, `src/melder/aether/conduit/meld/creation_context/creation_context.py:798`.
5. Revalidation gate checks in validation-required environments:
   - repeated validity checks and potential lock-protected revalidation path.
   - Evidence: `src/melder/aether/conduit/meld/meld.py:336`, `src/melder/aether/conduit/meld/meld.py:439`, `src/melder/aether/conduit/meld/meld.py:545`.

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-02-13-discovery-meld-paths - Build discovery baseline, hotspot map, and prioritized optimization candidates for meld.
- [x] Task: TASK-2026-02-13-meld-contract-defaults-caching - Closed as out-of-scope for current wave by user direction (no implementation). (`context_compass/tasks/completed/2026-02-13_meld_contract_defaults_caching_task.md`)
- [x] Task: TASK-2026-02-13-meld-dynamic-gate-fastdoor - Implemented local-alias fastdoor for dynamic gate entry in `Conduit.meld` with preserved closure/wait/ticket semantics; task in review pending acceptance. (`context_compass/tasks/2026-02-13_meld_dynamic_gate_fastdoor_task.md`)
- [x] Task: TASK-2026-02-13-meld-input-resolution-keypath - Implemented direct cache lookup with id-fallback for unhashable inputs; validated in meld unit tests. (`context_compass/tasks/completed/2026-02-13_meld_input_resolution_keypath_task.md`)
- [x] Task: TASK-2026-02-13-meld-override-shape-hotpath - Implemented shape-first override specialization cache lookup with miss-only grouped-target collection; validated with unit and integration suites. (`context_compass/tasks/completed/2026-02-13_meld_override_shape_hotpath_task.md`)
- [x] Task: TASK-2026-02-13-meld-validation-gate-microprofile - Implemented per-frame change-control manager cache in Meld gating path; accepted and moved to completed. (`context_compass/tasks/completed/2026-02-13_meld_validation_gate_microprofile_task.md`)

## Acceptance Criteria
- Discovery output identifies top meld hotspots with evidence.
- Follow-up optimization tasks are documented and prioritized.
- Story documents end-to-end meld call flow (Conduit -> Meld -> CreationContext).

## Validation / Test Plan
- Use targeted code-path inspection and relevant existing test/benchmark hooks.
- Record commands and outputs for any executed measurements.
- Discovery pass in this update used source inspection and existing benchmark
  artifacts only (no new benchmark execution).

## UX / API / Data Notes
- Internal runtime optimization planning only; no API change in discovery pass.

## Risks / Mitigations
- Risk: overfitting to a narrow workload.
  Mitigation: include warm/cold and mixed-route scenarios in discovery notes.

## Open Questions
- Should optimization ranking use:
  1) weighted production-like route mix, or
  2) worst-case route envelope (`override_targeted`) as the primary gate?

## Decision Log
- 2026-02-13: Story created from user-requested optimization epic setup.
- 2026-02-13: Discovery completed with detailed meld call-flow documentation and hotspot ranking; follow-up implementation tasks added.
- 2026-02-13: `TASK-2026-02-13-meld-contract-defaults-caching` closed as out-of-scope/deferred by user direction due incomplete mutation/revalidation scope.
- 2026-02-13: `TASK-2026-02-13-meld-input-resolution-keypath` completed with unit-test validation (`54 passed`) and user acceptance.
- 2026-02-14: `TASK-2026-02-13-meld-override-shape-hotpath` completed with contract-preserving cache-hit short-circuit and validation (`38 passed`), accepted by user.
- 2026-02-14: Activated `TASK-2026-02-13-meld-validation-gate-microprofile` as the next in-scope meld optimization task.
- 2026-02-14: `TASK-2026-02-13-meld-validation-gate-microprofile` implemented with cached per-frame change-control manager lookup in `Meld`; validation passed (`55` meld unit tests, `63` resolution-contract integration tests) and was accepted/closed.
- 2026-02-14: Activated `TASK-2026-02-13-meld-dynamic-gate-fastdoor` as the next in-scope meld optimization task.
- 2026-02-14: `TASK-2026-02-13-meld-dynamic-gate-fastdoor` implemented with local alias fastdoor in dynamic `Conduit.meld` and gate-contract tests (`41` facade+component passes, `15` lifecycle passes). Task state moved to review pending user acceptance.

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
Discovery is complete:
- Documented how meld flows from `Conduit.meld` through `Meld.meld` and
  `CreationContext` runtime lanes.
- Captured five ranked hotspot candidates with source evidence.
- Added follow-up implementation tasks for contract-default caching, dynamic
  gate fastdoor, resolution-key path, override-shape path, and validation-gate
  microprofiling.
Implementation update:
- `TASK-2026-02-13-meld-override-shape-hotpath` now uses shape-first
  specialization cache lookup in `CreationContext._execute_with_overrides`,
  with grouped target collection deferred to cache misses.
- Tests added/updated in meld-runtime to assert shape-helper parity and cache-hit
  bypass behavior; override integration and meld-engine suites pass.
Next step:
- Confirm acceptance for `TASK-2026-02-13-meld-dynamic-gate-fastdoor`, then close/move story if no further meld tasks remain.
