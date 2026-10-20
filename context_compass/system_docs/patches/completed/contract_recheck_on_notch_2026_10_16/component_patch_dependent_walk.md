# Component patch: a notch marks what depends on the notched spell (contract_recheck_on_notch_2026_10_16)

## Metadata
- Patch ID: contract_recheck_on_notch_2026_10_16
- Components: SpellSystemStates
  (`src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py`: `register_index`, new
  `mark_dependents_for_revalidation`, `mark_contract_dependents_dirty`, `unregister_index`, `cleanup`) and its two
  Spellbook call sites (`src/melder/aether/spellbook/spellbook.py`: `bind`, `_apply_notch`)
- Status: active; D2 decided by the owner (2026-10-16): the dependency notch is part of rule 2
- Owner: user; melder_1 (synaptic_python_developer) (patch, and writer of spell_system_states.py and of spellbook.py,
  which melder_0 released at 2026-10-16T12:33:09Z)
- Created: 2026-10-16T12:22:44Z
- Updated: 2026-10-16T12:57:39Z

## Component purpose and boundary
- Current boundary: the frame-wide registry keeps one state per lineage (validity, flags, the direct dependency
  version ids its own last Phase 3 recorded, the reverse edges `direct_dependents` as lineage ids), the per-Book
  contract-consumer index (`_contract_dependents_by_spellbook[book][key]`, filled from Phase 3 topologies) and the
  local topologies. It marks downstream lineages in two places: `compute_impact_closure` (registry edges only) when
  a definition is removed (`unregister_index`) and in an ownership transfer, and `mark_contract_dependents_dirty` (a
  Book's consumers of given keys, nobody downstream of them) for a link commit, a grant, an uncontract, a sever and
  a remove-all. A notch marks the notched lineage only (`register_index`, then `invalidate_spell`), although
  `_apply_notch`'s comment says "so dependents revalidate". The registry does not record a lineage's own binding
  key, so it cannot go from a provider to the consumers of its key.
- Target boundary: the registry records each lineage's binding key and marks everything downstream of given
  lineages - registry edges and contract keys, transitively. A notch marks from the notched lineage, and every
  contract-consumer mark walks on from the consumers it marks. Mark only: the registry changes states; nothing is
  built, disposed or extracted.

## Before / after
| event | before | after |
| --- | --- | --- |
| notch of D (any Book) | D's lineage `gated` | also every lineage downstream of D: reached by a registry edge - `gated` + `impacted_by_dependency`, transitively dirty; reached by a contract key (a consumer, in any Book, of the binding key of D or of a lineage already reached) - `gated` + `contract_unvalidated`; and on from each |
| a contract-consumer mark (the link commit hook, `ConduitWard._invalidate_contract_consumers`, rule 2's five mutators) | the Book's consumers of the keys | the same, then everything downstream of those consumers as above |
| registration at bind and at a notch | `register_index(spell_index, owner, resolvable=...)` | also `binding_key=spell._key`, recorded per lineage |
| removal (`unregister_index`), ownership transfer | `compute_impact_closure`, edges only | unchanged |

- New `SpellSystemStates.mark_dependents_for_revalidation(index_ids: Iterable[str]) -> Set[str]`: under the registry
  lock, a worklist from the given lineages. A lineage's followers are its `direct_dependents` (edge-reached) and,
  when its binding key is recorded, the consumer lineages recorded under that key in every Book's contract index
  (contract-reached). Each lineage is visited once. Every reached lineage except the given ones is marked: an
  edge-reached one with `mark_transitively_dirty()`, a contract-reached one with `set_validity(gated,
  change_reason=contract_unvalidated, flags_to_add=[contract_unvalidated], transitively_dirty=False)` (rule 2's
  mark), a lineage reached both ways with both; each joins the dirty set. A lineage with no registered state is
  skipped. Returns the ids it marked.
- `mark_contract_dependents_dirty` keeps its signature, contract and return value (the consumers it marked, which
  `_invalidate_contract_consumers` uses to extract their stored objects) and then calls the walk from them, so their
  dependents are marked too. Those dependents are only marked: nothing of theirs is extracted.
- `register_index(..., *, resolvable=None, binding_key=None)`: a non-None key - the `(frame_key, binding_key)` tuple
  of `Spell._key`, the normalization `SpellContract.canonical_key` and Phase 3's contract index use - is recorded in
  `_binding_key_by_index[index_id]`; None keeps what is recorded. Every version of a lineage shares one binding
  signature (one active signature per frame, `LookupContainer.claim`), so one key per lineage. `unregister_index`
  pops it; `cleanup` clears it with the other maps.
- Spellbook (released by melder_0): `bind` and `_apply_notch` pass `binding_key=spell._key`; `_apply_notch` calls
  `mark_dependents_for_revalidation((spell_index.id,))` right after its `register_index`, outside the Book lock as
  that call is. The comment "so dependents revalidate" becomes true; the docstring's "Contracted borrowers are NOT
  yet fanned out here ... that is the next slice" is corrected (the Conduit fans out after the window), and its step
  list gains the mark. An idempotent notch (the spell is already active) returns before both, as today.

## Interface deltas
- Inputs and outputs: `register_index` gains a keyword-only `binding_key` (default None, so the transfer's three calls
  and every other caller are unchanged); one public registry method is added; `mark_contract_dependents_dirty`'s
  signature and return value are unchanged.
- Error semantics: the walk raises nothing new; on a cleaned registry it returns an empty set like its neighbours.
  `register_index` validates nothing new (the key comes from the Spell).

## State and lifecycle deltas
- Owned state: one map, `_binding_key_by_index`, written under the registry lock with the lineage's registration and
  removed with it.
- Lifecycle: unchanged.

## Failure mode deltas
- Removed: after a notch, a spell that depends on the notched one - directly or through others, in its Book or in
  another, by annotation or through a SpellContract - kept its plan: built before, it went on building the old
  version; never built, it failed with RuntimeError "many_only manifest references unknown spell_id" (probe C1-C3,
  X1).
- Removed: after a link, grant, uncontract or sever, a contract consumer's dependents kept the plan they had; one
  compiled while the provider was missing built the consumer with its `SpellContract` default object
  (AttributeError "'SpellContract' object has no attribute 'ping'" in the probe's User, today).
- New: none. The marks are what the gate's existing structural branch and the catch-up
  (component_patch_meld_gate.md) consume.

## Dependency and ordering constraints
1. The walk marks; it does not make a dependent two hops away resolvable by itself: its plan expands the stale
   topology of the dependency between them. The meld's catch-up refreshes that dependency first; without it the
   dependent fails with a visibility error and then stays refused (probe "closure" mode). The two land together.
2. Locks: the walk runs under the registry lock (an RLock: `mark_contract_dependents_dirty` already holds it when it
   walks on), takes each state's lock inside it, and RiskManager's callbacks run inside the registry lock and outside
   the state lock - the order `compute_impact_closure` and `mark_contract_dependents_dirty` use today. Nothing under
   these takes a ward, contract, conduit or Book lock, so the callers' locks (a ward lock in the emissions, a contract
   lock in `_remove_root_from_contracts`, the notch window) gain edges into the registry only.
3. spellbook.py (released by melder_0 at 2026-10-16T12:33:09Z): its two call sites change with the five mutators.

## Validation expectations
- Unit, real SpellSystemStates, both GIL modes: a chain Q -> P -> D marks P and Q (`impacted_by_dependency`,
  transitively dirty) and leaves D; a consumer C of P's key in another Book is marked `contract_unvalidated` and C's
  dependent U `impacted_by_dependency`; a lineage reached both ways carries both flags; a second walk publishes
  nothing; a contract cycle across two Books terminates; a lineage with no recorded key is followed by edges only;
  the key is recorded at bind, kept on None, popped by `unregister_index` and cleared by `cleanup`;
  `mark_contract_dependents_dirty` returns its consumers and marks their dependents; RiskManager sees one publication
  per changed validity (a spy).
- Component, both GIL modes, with the catch-up: the chain and cross-Book scenarios of
  probe_rule2_dependency_closure.py (C1-C4, X1), as regression tests named for their symptoms - a dependent keeps
  building the old dependency after a notch; a dependent fails with "many_only manifest references unknown spell_id"
  after a notch; a contract consumer's dependent builds it with its SpellContract default after a link.

## Unknowns and open decisions
- UNKNOWN: none; the mechanics rest on the source reads and the probe recorded in the ticket.
- Decided: D2 (fold into rule 2). Approved by the owner on 2026-10-16.

## Context / Handoff Summary
- What changed: written before any edit.
- Remaining risks: see the architecture patch.
- Next entrypoint: component_patch_meld_gate.md (the catch-up).
