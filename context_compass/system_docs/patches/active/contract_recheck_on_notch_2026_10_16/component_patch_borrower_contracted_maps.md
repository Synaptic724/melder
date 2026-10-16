# Component patch: the borrower Book's contracted maps mark their consumers (contract_recheck_on_notch_2026_10_16)

## Metadata
- Patch ID: contract_recheck_on_notch_2026_10_16
- Component: Spellbook contracted-map mutators (`src/melder/aether/spellbook/spellbook.py`)
- Status: active
- Owner: user; melder_1 (synaptic_python_developer) (patch); the file is melder_0's: its handoff comes first
- Created: 2026-10-16T10:32:18Z
- Updated: 2026-10-16T10:32:18Z

## Component purpose and boundary
- Current boundary: a Book keeps the copies it borrows per peer conduit - active copies in `_contracted_spells`,
  `_lookup_contracted_spells` and `_contracted_spells_by_id` (and the shared `_spell_id_pool`), parked copies in
  `_inactive_contracted_spells`. Five mutators change the active copies. Besides the maps they mark the Book's
  `list[Frame]` consumers on an add (when conjured), register or unregister the copy with RiskManager on an add, a
  removal and a clear, and refresh a LINK transaction's staged contract keys. They mark no SpellContract consumer.
- Target boundary: the same, and every mutator that changes an active copy marks the Book's consumers of that copy's
  key once its Book lock is released, when the Book is conjured. The Book still owns no consumer state: the registry
  owns it, and the mark is one call into it.

## Before / after
| mutator | what it changes | before | after |
| --- | --- | --- | --- |
| `_add_contracted_spell` | adds an active copy | marks the frame key's collection consumers (conjured) | also marks the copy key's contract consumers (conjured) |
| `_deactivate_contracted_spell` | parks an active copy | marks nothing | marks the copy's key (conjured) |
| `_reactivate_contracted_spell` | restores a parked copy | marks nothing | marks the copy's key (conjured) |
| `_remove_contracted_spell` | removes an active copy, or a parked one | marks nothing | the active branch marks the removed copy's key (conjured); the parked branch marks nothing |
| `_clear_contracted_spells_for_conduit` | removes every copy one peer lent | marks nothing | marks the keys of the active copies it removed (conjured) |

- New private helper `_mark_contract_dependents_dirty(contract_keys)`: a no-op for an empty set; otherwise one
  `SpellSystemStates.mark_contract_dependents_dirty(spellbook_id=self._id, contract_keys=contract_keys)` call, with
  `_mark_collection_dependents_dirty`'s policy (RuntimeError when the registry is missing; a failure is logged and
  re-raised).
- Each mutator reads `_conjured` and computes the key inside the critical section that changes the maps (the add
  and the removal already compute it there), and calls the helper after releasing the Book lock, next to the
  existing collection mark, before the staged-key refresh and the RiskManager call.
- The key is the copy's own (`spell._key` where the mutator already uses it, `_make_spell_key(...)` where it
  already computes that); both give `SpellInputUtils.make_spell_key_from_parts(...)`, the normalization
  `SpellContract.canonical_key` and Phase 3's contract index use.
- Unchanged: `_add_inactive_contracted_spell` (parked only), the delegating `_inactivate_contract_spell`,
  `_activate_contract_spell` and `_ensure_contracted_active`, the sever seams (`_detach_link_contract`,
  `_reattach_link_contract`, `_destroy_detached_link_contract` - a sever is marked by the ward), the RiskManager
  calls and the staged-key refresh.

## Interface deltas
- Inputs and outputs: the five mutators keep their signatures and returns; one private helper is added.
- Error semantics: a mutator whose mark raises propagates the error after its map change, as
  `_add_contracted_spell` already does for its collection mark. The registry raises only when it was cleaned while
  its Book is conjured and live, a teardown-ordering violation.

## State and lifecycle deltas
- Owned state: unchanged. The consumers' lineages go `gated` + `contract_unvalidated` in the registry.
- Lifecycle: unchanged.

## Failure mode deltas
- Removed: once the meld's scan is gone (component_patch_meld_gate.md), a consumer would keep building the
  provider version its plan was compiled against after its lender's notch, notch back or index destroy. The mark
  is what replaces the scan.
- New: none.

## Dependency and ordering constraints
1. The mark lands with the scan's removal, in one notch.
2. The mark runs with the Book lock released, so the Book lock spans exactly what it spans today. Callers may hold
   the owner's ward lock (`_emit_index_notch`, `_emit_index_destroy`, `_emit_index_member_removed`) or a contract
   lock (`_remove_root_from_contracts`); the mark adds edges from them into the registry only, and the registry,
   the state and RiskManager take none of those locks (code_description_patch_contract_recheck.md).
3. melder_0 owns spellbook.py: the handoff precedes the edit, and the edit follows S8's landing.

## Validation expectations
- Unit, both GIL modes, a conjured Book on a real SpellSystemStates with a consumer registered under the key: each
  mutator gates the consumer with `contract_unvalidated`; nothing is marked before conjure; a parked add or a
  parked removal marks nothing; a clear marks only the keys of the active copies; the helper runs with the Book lock
  free (a registry double asserts `not book._lock._is_owned()` or equivalent); a mixed-case contract binding name is
  matched; a registry failure is logged and propagates after the map change.
- Component, both GIL modes: the coverage matrix of the architecture patch (notch, notch back, repeat notch, grant,
  index destroy, member removal, uncontract, remove-all, transfer repoint, lent consumer).

## Unknowns and open decisions
- UNKNOWN: none.
- DECISION_REQUEST: D5 (the handoff of spellbook.py and the landing after S8).

## Context / Handoff Summary
- What changed: written before any edit.
- Remaining risks: see the architecture patch.
- Next entrypoint: component_patch_meld_gate.md.
