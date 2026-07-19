# Task: Migrate _root_creations off Creations onto the meld objects (Phase 1: lineage)

## Metadata
- Task ID: TASK-2026-06-18-migrate-root-creations-onto-meld
- Related: EPIC-2026-06-16-unique-per-conduit-cluster-team-store (this unblocks the clean cluster store)
- Status: in_progress (plan; no code yet)
- Owner: cowork
- Agent Name: compiler_strategy_0
- Priority: p2
- Created: 2026-06-18T23:14:00Z
- Updated: 2026-06-18T23:14:00Z

## Objective
Stop stacking store-references inside `Creations`. Move the resolver pointer
`_root_creations` off `Creations` and onto the meld objects (`ConduitMeld`,
`SpellSpaceMeld`), and have the door receive the resolved store at runtime
instead of dereferencing `caller_creations._root_creations`. Phase 1 covers
`unique_per_conduit_lineage` only; Phase 2 adds the cluster facade the same way.

## Why (design decision, user-directed 2026-06-18)
`Creations` is meant to be a dumb live-object bucket ("no ambient lineage lookup
rules", creations.py docstring), yet it carries `_root_creations` (a pointer to
another `Creations`). The resolver concern "which store does this lifetime
resolve into" belongs on the resolver (the meld), not the store. Adding a second
store-ref (`_cluster_creations`) would double the smell, so we fix the home now.

## Current state (evidence)
- Field on the store: `Creations._root_creations` (slots creations.py:40; default
  `self` :92; del :136).
- Set at: conduit.py:322 (lesser adopts root), :1590 (lesser propagate on root
  change), :1695 (upgrade -> self); spell_space.py:130 (spellspace adopts owner
  conduit root).
- Read at runtime: ONLY the compiled lineage door route
  (`creation_runtime_door_compiler.py`, `_build_no_overrides_lines` /
  `_build_with_overrides_lines`, "lineage" branch -> `root_creations =
  caller_creations._root_creations`). transfer_of_ownership.py:355 is a COMMENT
  only (lineage is skipped there).
- Meld dispatch passes `caller_creations` into the door:
  conduit_meld.py:311 `creations = self._creations` -> :334/:339/:380;
  spellspace_meld.py:317/:319 -> execute. The door derefs `_root_creations`.
- Meld construction: `ConduitMeld(creations=..., ...)` at conduit.py:284 (slots
  `["_creations"]`); `SpellSpaceMeld(spellspace_creations=..., owner_conduit_creations=..., ...)`
  at spell_space.py:132 (slots incl. `_spellspace_creations`, `_owner_conduit_creations`).

## The core mechanical change (the door runtime contract)
Today the compiled door takes only `caller_creations` and derefs the root off
it. To host the pointer on the meld, the meld must hand the resolved store IN at
runtime. So:
- The door executor gains a runtime param (e.g. `resolved_store`), uniform across
  routes; only the lineage route reads it (others ignore). Create-once stays in
  the door under `resolved_store._lock` (byte-for-byte the current lineage body,
  just sourced from the param instead of the deref).
- `CreationContext.execute` / `execute_no_hooks` (and their dynamic-gate arms)
  thread `resolved_store` to the executor.
- The meld dispatch computes the store (lineage -> `self._root_creations`, else
  `None`) and passes it, including the fast-door inline at conduit_meld.py:339
  and the spellspace inline.

This is exactly the user model: "in meld we have root_creations attached; you
pass in the root creations."

## Phase 1 steps (lineage only)
1. ConduitMeld: add `_root_creations` slot + set it. Normal conduit ->
   `self._creations`; lesser -> the lineage root's store. cleanup drops the ref
   (does NOT clean it; the conduit owns the store).
2. SpellSpaceMeld: add `_root_creations` slot; thread the owner conduit's root in
   at construction (the spellspace is not a root; it resolves into the owner
   conduit lineage root). cleanup drops the ref.
3. Creations: remove `_root_creations` (slot, `__init__` default, `del`, comment).
4. conduit.py wiring: replace the 3 `self._creations._root_creations = X` writes
   (322, 1590, 1695) with the equivalent on the meld. Normal-conduit default set
   at/after meld construction (284).
5. spell_space.py:130: set the spellspace meld's root from the owner conduit
   meld's `_root_creations` (thread it via the `conduit_meld` already passed in).
6. creation_runtime_door_compiler.py: lineage route uses the passed
   `resolved_store`; add the runtime param to the executor signature/templates.
7. creation_context.py: thread `resolved_store` through execute/execute_no_hooks
   (+ dynamic gate arms).
8. conduit_meld.py + spellspace_meld.py: compute + pass `resolved_store`
   (lineage -> meld `_root_creations`), incl. the fast-door inline paths.
9. Tests: update assertions in test_lineage_upgrade_to_normal.py,
   test_spell_space*.py, test_conduit_dynamic.py that touch `_root_creations`.
10. Docs: src_architecture.md / src_components.md lineage + Creations notes.

## Phase 2 (after Phase 1 green) — cluster, same mechanic
- ConduitMeld/SpellSpaceMeld get `_cluster_creations` (the cluster facade; user
  wants it built present/empty by default). Set when the conduit joins a cluster.
- New `cluster` door route = lineage's passed-store mechanic; meld passes the
  leader store from the facade as `resolved_store` (inert facade -> hard error).
- route_family/route-key accepts "cluster" (processor + each finalize).
- Liveness probe split (conduit_meld.py:518-523, :706-710).
- elect/unelect call sites in conduit_cluster.py with the CORRECTED envelope-only
  contract: ConduitCluster calls `cluster_creations.bind/unbind` itself inside
  the held transaction window (see the cluster call-site ticket).

## Open points (confirm before/while building)
- D1: Phase 1 alone first (recommended), then Phase 2 — vs both together.
- D2: exact shape of the door runtime param (single `resolved_store` reused by
  lineage now and cluster later) — confirm naming/contract.
- D3 (Phase 2): "empty facade on every meld" — does each meld hold its own empty
  `ClusterCreations` that gets bound on join, or a ref to the cluster's shared
  facade? Resolve when Phase 2 starts.

## Files / Paths Impacted (Phase 1)
- src/melder/aether/conduit/creations/creations.py
- src/melder/aether/conduit/meld/conduit_meld.py
- src/melder/aether/conduit/meld/spellspace_meld.py
- src/melder/aether/conduit/conduit.py
- src/melder/aether/conduit/spell_space/spell_space.py
- src/.../codegen_creation_system/shared_assets/creation_runtime_door_compiler.py
- src/melder/aether/conduit/meld/creation_context/creation_context.py
- tests/.../test_lineage_upgrade_to_normal.py, test_spell_space*.py, test_conduit_dynamic.py
- system_docs/src_architecture.md, system_docs/src_components.md

## Validation
- Not run. (Sandbox is Py3.10; repo is 3.14t.) User runs:
  `pytest tests/unit/melder/aether/conduit -q` + the lineage/spellspace suites +
  a concurrent lineage stress (mirror the 40x conjure pattern) before merge.

## Risks / Rollback
- Touches the hot path (door + CreationContext + meld dispatch) and emitted code.
  Highest-risk items: the executor signature change and the fast-door inline.
- Rollback = revert per-file; the change is mechanical (pointer relocation +
  one runtime param), no semantics change to lineage behavior.
- This is the "big refactor"; keep it Phase-1-only to bound blast radius.

## Notes
- DATETIME: 2026-06-18T23:14:00Z
  TYPE: PLAN
  CLAIM: Phased plan to move _root_creations off Creations onto the meld and
    pass the resolved store into the door at runtime, lineage first; cluster
    reuses the same passed-store mechanic in Phase 2.
  EVIDENCE:
  - creations.py:40,92,136 (field) ; conduit.py:322,1590,1695 ; spell_space.py:130
  - creation_runtime_door_compiler.py (lineage route) ; creation_context.py:execute
  - conduit_meld.py:311,334,339,380 ; spellspace_meld.py:317,319
  IMPACT: Removes the store-holds-store smell; makes the door a function of
    (caller_creations, resolved_store) with meld owning store selection.
  NEXT: confirm Phase-1-only scope, then implement file-by-file with diffs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Relocate `_root_creations` from `Creations` to the meld (`ConduitMeld` /
`SpellSpaceMeld`); the door takes the resolved store as a runtime arg instead of
dereferencing it off the caller's creations. Phase 1 = lineage; Phase 2 = the
cluster facade via the identical passed-store path. No code until Phase-1 scope
is confirmed.
