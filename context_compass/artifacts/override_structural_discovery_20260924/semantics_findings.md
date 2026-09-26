# Structural override discovery: admission and lifecycle

Lead: updater_0. Date: 2026-09-24. Status: source/diagnostic findings, no production changes.
Task: tickets/tasks/2026-09-24_discover_override_execution_semantics_task.md.
Peer task: tickets/tasks/2026-09-24_discover_override_occurrence_slicing_task.md.

## Preserved prototype and selected direction

The prior prototype changes generated instructions while retaining every constructor. Its public
original-workload throughput reaches 41.8%/53.3%/41.6%/95.3% of normal for shallow/wide/diamond/deep.
Its 1.64x-4.68x improvement is relative to old overrides. That evidence remains frozen under
artifacts/override_emission_prototype_20260924/. It does not solve supplied-dependency orchestration.

The owner now selects structural planning: supplied sockets must remove unnecessary construction
before execution. Definitions and already-owned creations remain registered; the change concerns
this call's demand, not unbinding, purging or transferring ownership.

## Current behavior reproduced

probe_semantics.py runs isolated real worlds with disk caching disabled and no timings. The report
includes runtime source hashes. The initial report is preserved separately; the refined report also
checks call order and the actual nested contract value.

| Case | Observed behavior | Structural design implication |
| --- | --- | --- |
| many root whose only dependency is per-Space, dependency supplied | Conduit still refuses before construction | Derived scope demand must use retained work. |
| root itself is per-Space, dependency supplied | Conduit refuses; explicit Space succeeds | Root's own lifetime remains mandatory. |
| supplied dependency through explicit Space | Unused resource is constructed and disposed | A supplied edge must terminate construction demand. |
| direct root has missing SpellContract provider | Refuses with or without supply, including override-first | Root-wide readiness currently precedes input substitution. |
| same missing contract nested below another root | Normal call passes the SpellContract descriptor as the service | Validate every retained constructor's required sockets consistently. |
| valid nested rule under externally replaced child | Builds a discarded child with the rule; supplied child stays unchanged | Decide reachability before executing nested construction. |
| invalid nested rule under externally replaced child | Targeting rejects it before constructors | Preserve selector validation separately from active execution. |
| reusable Middle already exists above many Leaf | Later normal and override calls create unused new Leaves | Static supplied-edge cuts and live reuse short-circuiting are distinct. |
| child pre/activation/post hooks | Direct child meld fires them; nested compiled construction in this fixture does not | Record existing hook behavior; do not silently redesign hooks in the pruning change. |
| root pre-hook with invalid nested selector | Root pre fires, then targeting raises; constructors and root activation/post do not run | Effective-plan preparation has an observable placement relative to entry hooks. |

The shared-reuse scenario constructs Leaf/Middle/Root on the first call. A second normal call, a
third root-parameter override and a fourth whole-Middle replacement each construct another Leaf.
The same Middle survives the first three calls, and cleanup disposes all four Leaves. This confirms
the problem is not limited to the override emitter, although changing the no-override shared path
must remain an explicit part of implementation scope.

The nested-contract success is not valid service resolution: descriptor_leaked is true in both
normal-first and override-first experiments. This is existing behavior, not a change made here.

Evidence:
- artifacts/override_structural_discovery_20260924/probe_semantics.py
- artifacts/override_structural_discovery_20260924/semantics_observations.json
- artifacts/override_structural_discovery_20260924/semantics_observations_initial.json

## Source boundaries

ConduitMeld checks the full-graph requires_spellspace_request flag before normalizing overrides.
Phase 5 assigns that flag from the full reachable Spell-ID closure. An emitter-only cut cannot change
this earlier refusal. Explicit Space uses a different door and already has its own store.

Evidence:
- src/melder/aether/conduit/meld/conduit_meld.py:443-535
- src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:165-193
- src/melder/aether/spellbook/spell_compiler/system/spell_system_root_blueprint_builder.py:238-341
- src/melder/aether/conduit/meld/spellspace_meld.py:235-536

When enabled, structural/per-conduit validation precedes CreationContext execution. Direct contract
checks inspect the selected root's signature. Phase-9 injection derives sources from occurrence
edges, specially retains OVERRIDE_REQUIRED, and merges recorded contract payloads; missing-provider
readiness is not a distinct source in the inspected builder. Empty non-collection dependency arguments
can be omitted at execution, exposing a Python descriptor default instead of a resolved service.

Evidence:
- src/melder/aether/conduit/meld/meld.py:748-1240
- src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_injection_processor_strategy.py:119-342
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_no_overrides_codegen_creation_compiler.py:992-1199

Root reuse refusal already lives in the generated outer door with the selected lifetime's store/Spell
lock. Dependency steps also retain their own store and lock requirements. Preserve that authority;
Creations remains the creation/disposal store rather than the owner of override graph policy.

Evidence:
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:689-871
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:1818-2311

Dynamic admission has two distinct boundaries. The public Conduit holds an outer creation ticket
before lookup. Explicit SpellSpace.meld delegates directly. CreationContext later admits the index
ticket around executor execution. A future effective-plan preparation stage must preserve these
version/lifetime guarantees on both doors; moving a check earlier is not automatically safe.

Evidence:
- src/melder/aether/conduit/conduit.py:4417-4570
- src/melder/aether/conduit/spell_space/spell_space.py:455-507
- src/melder/aether/conduit/meld/creation_context/creation_context.py:237-309

## Recommended semantic ordering to investigate

1. Retain absolute root/identity/closed-state/transaction authority and obtain current graph-version facts.
2. Normalize the effective payload, preserving per-call replacement of mutation defaults and explicit empties.
3. Resolve selector validity and precedence against declared socket/path metadata, without touching supplied objects.
4. Mark supplied argument sockets as value sources. Follow only unsatisfied construction edges from the root.
5. Preserve all remaining uses of shared providers; resolve alias/path provenance before choosing shared recipes.
6. Derive request-specific scope/provider readiness for every retained constructor, including unresolved contracts.
7. Emit the remaining construction program with existing lifetime locks, registration and disposal semantics.
8. Keep cached-instance reuse as a runtime conditional, not a permanent shape-cache assumption.

This is a proposed separation of responsibilities, not an implemented API or a claim that current
rows contain every required fact. The peer is testing exactly what occurrence/path provenance survives.

Ordinary no-override execution should retain its fast route. Cached effective plans belong to the
existing compiler/context invalidation lifecycle. Cache shapes and static operands, not this call's
supplied objects or a transient observation that a shared instance currently exists. Purge can remove
a live instance while keeping the context reusable, so a later call may need the construction branch again.

## Suggested behavior choices for the structural contract

- A whole supplied dependency cuts its exclusive descendants; a parameter override still constructs its owner.
- None and falsey values are supplied by key presence. Do not infer absence from their truthiness.
- Keep syntactically invalid, unmatched or ambiguous selectors as errors. A valid descendant selector under
  a supplied ancestor has no construction effect and never mutates the supplied object; retain other live targets.
- Keep hard root lifecycle/capability and caller-scope ownership checks. Recompute demand-derived requirements
  from retained work rather than granting a blanket validation bypass.
- A retained unresolved contract must fail consistently. A cut branch must not force its provider's creation.
- Preserve ordinary Python missing-argument failures for retained constructors. Do not add a general
  per-call required-input validator; unresolved descriptor readiness is a distinct problem.
- Supplied references keep existing external ownership. Pruning never disposes, registers or purges them implicitly.
- Existing root reuse with overrides remains rejected. Any broader adjustment is a separate explicit decision.

## Remaining design work

Peer graph results provide a counterexample to simple expand-then-group processing. One shared Branch
has one constructor input Token, even when Token's Existence is many. Expanding left/right aliases and
grouping only the Branch leaves two Token path keys, creating a ghost input. A proposed construction
identity should relate that input to the shared parent's constructor context and socket, while keeping
both logical paths for targeting. This does not propose a new lifetime or storage owner.

Likewise, a descendant rule under a removed logical alias must not leak into a surviving alias merely
because both previously used the same canonical shared row. Grouping and conflict adjudication must
consume the surviving logical requirements, with explicit treatment of two incompatible requirements
for one shared constructor. The source and eleven diagnostic scenes are recorded in the peer task.

The relationship between call-specific readiness and baseline SpellValidity must be defined before
implementation; a successful supplied call must not mark an unresolved baseline graph globally valid.
Alias-aware shared construction and contract conflicts require the peer's occurrence representation.
The safe cold-preparation admission boundary and concurrent purge/reuse behavior need targeted tests.
Child-hook consistency is an observed adjacent concern to catalogue, not an automatic expansion.
The root pre-hook currently runs before invalid-selector rejection. Select and test its placement
relative to effective-plan preparation/admission; do not accidentally change failure callback ordering.

No production patch, cache-schema change, version bump or build-asset regeneration has been made by
this structural discovery lane. Prior prototype measurements retain their own historical source hashes.
