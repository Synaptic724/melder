# architecture_patch

## Metadata
- Patch ID: remove_many_child_holder_ownership_2026_10_24
- Status: draft
- Owner: Mark (decision); melder_1 (executor)
- Created: 2026-10-24T20:06:55Z
- Updated: 2026-10-24T20:06:55Z

## Patch Scope and Non-Goals
- Objective: remove holder ownership of `many` dependencies. A disposal-bearing `many` dependency built for a
  slotted holder of any kind (`unique`, `unique_per_conduit`, `unique_per_spell_space`, `unique_per_conduit_lineage`,
  `unique_per_conduit_cluster`) is recorded in, and disposed by, the meld's innermost scope - the spellspace store,
  else the melding conduit's store - exactly as a `many` root is. Cleaning up a holder runs only its own disposal
  methods. Owner's decision, chat 2026-10-24: "it should behave like autofac not mysteriously cleanup transient
  objects".
- Non-goals: managed pools' recorded children (`ManagedSpellQuantity.adopt`); the opt-in singleton specializer's
  decline of graphs that feed a `many` step into a non-`many` step (it stops an unused dependency being built on
  every warm meld); cache generations or Crystallizer record formats; the transfer default (`move_creations=True`).

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| Codegen site-plan lowering (`SitePlanEmission`) | modify | a miss's `many` children register through `many_store`, the adoption line goes (0.2.8235 and 0.2.8238 emission reverted) | Creations |
| Creations store (`Creations`) | modify/remove | `HolderDisposalEntry`, `adopt_children` and every holder branch go; two disposal shapes remain | none |
| Ownership transfer (`TransferOfOwnership`), `Conduit.transfer_spell_ownership` | modify (docs) | a moved holder's row no longer carries children | Creations |
| Generalized compiler and hydrator | modify (docs) | the specializer decline's rationale no longer cites holder ownership | none |

## Interface and Boundary Deltas
- Boundary delta 1: the disposal obligation of a `many` dependency belongs to the scope that built it; no store
  records a dependency because of the holder it was passed to.
- Interface delta 1: `Creations.adopt_children` and the class `HolderDisposalEntry` are removed (internal, never
  public); `extract_spell_creations` rows no longer carry `children`; `restore_spell_creations` accepts the plain rows
  only. No public signature changes.

## Cross-Component Invariants
- Invariant 1: a `many` key's bucket holds every disposal-bearing object of that spell its store recorded; purge,
  live-creation probes and teardown read it whole.
- Invariant 2: a holder's disposal value is its `(holder, methods)` tuple when it declares disposal methods, else
  absent; disposal of one value never reaches another key.
- Invariant 3: warm `_site_plan_executor` bodies are unchanged; misses register their children through the same
  prologue a top-level `many` uses. The store lock stays a leaf; no lock-order edge is added.

## Migration and Rollout Order
1. Tests to the new contract, red on 0.2.8265 (GIL off and on).
2. `site_plan_lowering.py` and `creations.py`, then the docstrings.
3. Tests green; full suite; system docs; release note; notch; rebuild last.

## Rollback Strategy
- Rollback trigger: the owner reverses the decision, or the full suite shows a regression the change caused.
- Rollback steps: restore the two src files and their tests from 0.2.8265.
- Post-rollback verification: the 0.2.8265 feature tests green again.

## Validation Expectations and Evidence Plan
- Validation item 1: per route (lesser, root spellspace, lesser spellspace, nested per-conduit consumer, override
  meld, borrowing root, cluster member) the child is recorded by the melding scope and closed when it ends, once.
- Validation item 2: a holder's purge and its store's teardown run only the holder's methods; a transfer leaves the
  child in the source store; a purge of the child's spell counts it.
- Validation item 3: emission unit tests - misses register through `many_store` after the prologue, no adoption line.
- Evidence source 1: runs under artifacts/many_child_removal_20261024/runs/.

## Ticket Coverage Map
- Epic: EPIC-2026-10-20-reassess_many_child_disposal_ownership
- Story: STORY-2026-10-24-remove_many_child_holder_ownership
- Tasks: none (the story carries the checklist)

## Unknowns and Decision Requests
- UNKNOWN: none blocking.
- DECISION_REQUEST: none; the owner decided on 2026-10-24.

## Context / Handoff Summary
- What changed: the patch is written; no src edit yet.
- What remains: tests, the change, docs, notch, release note, rebuild.
- Next entrypoint: component_patch_site_plan_lowering.md, then component_patch_creations.md.
