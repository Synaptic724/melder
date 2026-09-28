# architecture_patch

## Metadata
- Patch ID: spellspace_probe_many_2026_09_28
- Status: promoted
- Owner: user (agent melder_0)
- Created: 2026-09-28T00:34:00Z
- Updated: 2026-09-28T01:00:17Z

## Patch Scope and Non-Goals
- Objective: the live-creation probe of the SpellSpace door (`SpellSpaceMeld._describe_spell_live_creation_status`)
  reads `many` from the store where that door tracks it - the space's own store - instead of the owner
  conduit's store.
- Non-goals: storage routing of any lifetime, purge, the meld path, the ConduitMeld probe (it already reads the
  store its door writes), the payload's keys, a public SpellSpace probe.

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| Meld Resolution Runtime (SpellSpaceMeld) | modify | probe read `many` from a store this door never writes | none |

## Interface and Boundary Deltas
- Boundary delta: none. The probe stays on the door (`has_live_creation`, `describe_live_creation_status`).
- Interface delta: for a `many` spell probed through a SpellSpace door, `storage_scope_kind` is "spellspace_many"
  (was "owner_conduit_many"), `active_spellspace_id` is the space's id (was None) and `creation_count` /
  `is_live` count the space's bucket (was the owner conduit's). Payload keys are unchanged.

## Cross-Component Invariants
- A door's live-creation probe reads, for each lifetime, the store that door's meld registers into and its
  purge retires from. Through a SpellSpace: `many` and `unique_per_spell_space` -> the space store;
  `unique_per_conduit` -> the owner conduit store; `unique_per_conduit_lineage` -> the lineage root;
  `unique_per_conduit_cluster` -> the elected leader; `unique` -> the Spell owner's store.
- Disposal-bearing `many` is registered in the innermost scope by every emitter (solo, generalized manifest,
  site-plan lowering); a `many` without disposal methods is never tracked and probes as 0 through any door.

## Migration and Rollout Order
1. Red tests on 0.2.8203 (unit: space-held `many` counted, owner-conduit `many` not; component: real space).
2. Change the branch and its docstrings; tests green; suites on 3.14t (GIL 0 and 1) and the GIL build.
3. `__version__` notch, release note, src_components, graph; assets and LLM bundles last.

## Rollback Strategy
- Rollback trigger: a caller found that relies on the space door reporting owner-conduit `many` objects.
- Rollback steps: revert the branch, the docstrings and the three tests; restore the failure-mode bullet.
- Post-rollback verification: test_concrete_meld_subclasses.py and the spellspace creations component tests.

## Validation Expectations and Evidence Plan
- Validation item: the new tests fail on 0.2.8203 and pass after; the conduit and spellspace suites stay green.
- Evidence source: context_compass/artifacts/spellspace_probe_many_20260928/ (repro, red and green logs).

## Ticket Coverage Map
- Epic: none
- Story: none
- Tasks: tickets/tasks/2026-09-28_count_space_held_many_in_spellspace_live_creation_probe_task.md

## Unknowns and Decision Requests
- UNKNOWN: none. The routing and purge code settle which store the probe must read.
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: landed at 0.2.8204 (the probe's `many` branch and its contracts, three tests) and promoted
  into src_components (Meld Resolution Runtime "Live-creation probe scope", the store-selection bullet, the
  conduit-door failure mode, probe flow step 4, C1, handoff; the Creations and SpellSpace failure mode
  removed); graph, release note, assets and bundles current.
- What remains: nothing in this patch.
- Next entrypoint: tickets/tasks/completed/2026-09-28_count_space_held_many_in_spellspace_live_creation_probe_task.md
