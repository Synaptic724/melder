# Component patch: RiskManager ignores non-resolvable lineages (meld_state_gate_2026_10_15)

## Metadata
- Patch ID: meld_state_gate_2026_10_15
- Component: RiskManager (`src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py`)
- Status: active
- Owner: user; melder_1 (synaptic_python_developer) (patch, and writer of this file)
- Created: 2026-10-15T21:00:00Z
- Updated: 2026-10-15T22:32:34Z

## Component purpose and boundary
- Current boundary: the aggregator that folds structural and per-conduit resolution validity into one
  validation-required flag per Book; it validates nothing and treats every non-`valid` value as risky.
- Target boundary: the same, except that the flag ignores the risk of a lineage the state model declares
  non-resolvable. The aggregator still keeps no set of its own and still validates nothing.

## Before / after
- Before: `_refresh_spellbook_flag` sets the flag when either risk set of the conduit is non-empty. A lineage whose
  selected version is resolvable=False never receives a resolution verdict, so it stays in the resolution-risk set
  and the flag stays up for the Book's life. `register_conduit` seeds every visible spell through `register_spell`,
  which refreshes once per spell.
- After:
  - The risk sets are filled and emptied exactly as before by `register_spell`, `unregister_spell` and both validity
    events.
  - `_refresh_spellbook_flag` snapshots the union of the two sets under the manager lock and then, outside it, asks
    `_has_unexcluded_risk`: the flag is up when some key is not in the registry's published set of flagged lineages
    (`SpellSystemStates.non_resolvable_index_ids`) - a `spell:` key, a lineage with no live state or one whose
    state lacks `SpellState.non_resolvable` never is - and a set made only of flagged lineages leaves it down. It
    is one subset test with no lock and no Python work per key. With both sets empty nothing else is read.
  - `register_conduit` seeds through a private `_register_spell_risk` and refreshes once at the end; `register_spell`
    is `_register_spell_risk` plus one refresh, as before. The seeding's intermediate flag values were never
    observable (the conduit is not usable before conjure returns).

## Interface deltas
- Inputs and outputs: unchanged public methods; the collaborator contract gains one read, the
  `SpellSystemStates.non_resolvable_index_ids` property.
- Error semantics: unchanged. A cleaned registry raises on that read and the error leaves the refresh, where every
  caller already contains it (`set_validity` and `set_spell_validity` swallow callback failures; the Spellbook
  logs its calls).

## State and lifecycle deltas
- Owned state: unchanged (`_conduit_states`, `_lineage_conduits`); no exclusion set.
- Lifecycle: unchanged.

## Failure mode deltas
- Removed: one resolvable=False definition no longer holds its Book's flag up for good.
- Changed: none on the risk sets. New: none.

## Dependency and ordering constraints
1. Reads of the registry run without the manager lock, as `_get_structural_validity` and `_get_resolution_validity`
   already do: the registry calls this manager under the registry lock, so the manager must never call the registry
   under its own. The published set is read without any lock.
2. The refresh order between two concurrent refreshes is unchanged (computed, then set outside the lock); see the
   architecture patch's Risks.

## Validation expectations
- Unit, both GIL modes, on a real SpellSystemStates: a flagged lineage alone in either set leaves the flag down while
  the sets still hold it; one unflagged risky lineage raises it; a `spell:` key and a removed lineage count; a
  registration that clears the flag raises the flag at the gated event, or at the re-published one when the
  lineage was already gated, with the kept resolution risk; register_conduit sets the flag once.
- The existing RiskManager unit tests stay green; their registry stub gains `non_resolvable_index_ids` (empty:
  nothing flagged).
- Component, both GIL modes (with the call sites): automatic and dynamic worlds with a Protocol definition keep the
  flag down and meld through the fast door; the definition's meld is still refused.

## Unknowns and open decisions
- UNKNOWN: none.
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: written before any edit; amended 2026-10-15T22:12:54Z: the exclusion reads the registry's published
  set (one subset test) instead of a registry probe per key, whose cost grew with the definition count.
- Remaining risks: the pre-existing refresh-ordering race.
- Next entrypoint: component_patch_registration_call_sites.md.
