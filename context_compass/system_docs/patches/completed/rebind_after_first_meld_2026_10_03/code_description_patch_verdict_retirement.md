# code_description_patch_verdict_retirement

## Metadata
- Patch ID: rebind_after_first_meld_2026_10_03
- Status: promoted (src_architecture, src_components, graph at 0.2.8219); archived 2026-10-03T21:08:00Z
- Owner: user (agent fable_1)
- Created: 2026-10-03T20:12:00Z
- Updated: 2026-10-03T21:08:00Z

<!-- BEGIN ENTRY: "rebind after first meld: control flow after the repair" -->
## Control Flow
1. First meld (lesser `scope` under root R): `_ensure_resolution_resolvable` reads R's conduit state for id X,
   finds `unknown`, runs the target pass; Phase 6 writes `root_validity[X] = valid` and `spell_validity[X] =
   valid` into R's state (and into the peer's state when the peer melds X through its contract).
2. `root.cleanup_spell(definition)`: `Spell.invalidate_spell` clears the Spell's context and artifacts;
   `Spellbook.cleanup_and_remove_spell` -> `SpellSystemStates.unregister_index`: impact closure gates the
   dependents structurally, the lineage leaves the registry, and - NEW - every conduit state forgets X
   (`cleaned_up_spell`). RiskManager gets the structural `cleaned` callback as before. The surviving product
   stays in its scope's store.
3. Rebind of the same class at the same address: Bind mints the same X for a new Spell; `register_index`
   creates the new lineage state and - NEW - forgets X in every conduit state again (`register_or_rebind`;
   a no-op here because step 2 already did it); the eager structural pass makes the lineage valid;
   `RiskManager.register_spell` recomputes resolution risk from the live verdict (unknown -> required).
4. Second meld in any conduit: structural state valid, so no structural rerun; `_ensure_resolution_resolvable`
   reads `unknown` for X, enters the rebuild window and the spell lock, runs the target pass (Phase 5 root
   blueprints, Phase 6 verdicts valid, Phase 7, Phases 8-11 plan), and `_execute_admitted` builds the
   CreationContext from the new codegen. The override is honoured; `many` builds a new product.

## Edge / Error Semantics
- An id that was never melded in a conduit has no verdict there: forgetting is a miss, returns False, marks
  nothing dirty.
- A conduit dropped concurrently is popped from the registry under the registry lock before it is cleaned, so
  the helper never visits a cleaned state; if it ever did, `forget_spell` raises RuntimeError (contract
  violation), it is not swallowed.
- Notch back to a member that was active before: its verdicts are forgotten at re-registration, so each
  conduit reruns 5-11 for it at the next meld (one pass per conduit, the lazy recompile notch documents).
- Transfer re-registration on the target registry: same forgetting; the transfer already cleared the spell's
  phase-5 artifacts and context, so the next meld had to recompile anyway.
- The RiskManager is not called from the forgetting. The flag transition observed: True after the rebind
  (`register_spell` recompute), False after the revalidating meld (Phase 6 `valid` callback).

## Invariants / Idempotency
- Forgetting is idempotent: a second call for the same id returns False and changes nothing.
- No verdict for an unregistered id, no verdict for a freshly registered version id (frame-wide).
- Verdicts for other ids, the conduit diagnostics snapshot and `last_validated_at` are never touched.

## Explicit Non-Goals
- The surviving product's slot for slotted existences (unique_per_conduit and kin) is not retired: after a
  same-id rebind the replacement's first meld in that conduit returns the surviving old product, and an
  override against it is refused as against any stored shared instance (M7). Owner ruling 2026-10-03: the
  object is deliberately left alive; this is the contract, not a gap.
- The structural axis, the meld hot path, RiskManager's verbs, purge, the CreationContext guard and public API
  are unchanged.
<!-- END ENTRY: "rebind after first meld: control flow after the repair" -->
