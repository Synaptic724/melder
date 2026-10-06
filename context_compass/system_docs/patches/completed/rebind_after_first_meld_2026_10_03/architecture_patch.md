# architecture_patch

## Metadata
- Patch ID: rebind_after_first_meld_2026_10_03
- Status: promoted (src_architecture, src_components, graph at 0.2.8219); archived 2026-10-03T21:08:00Z
- Owner: user (agent fable_1)
- Created: 2026-10-03T20:12:00Z
- Updated: 2026-10-03T21:08:00Z

<!-- BEGIN ENTRY: "rebind after first meld: scope, deltas, invariants" -->
## Patch Scope and Non-Goals
- Objective: `bind -> meld -> cleanup_spell -> bind the same class at the same address -> meld` returns a new
  product instead of raising RuntimeError "Cannot build CreationContext before spell_codegen_creation exists."
  The cause is in the DevOps control plane: per-conduit resolution verdicts (`ConduitResolutionState`, Phases
  5-11) are keyed by the content-stable spell id and survive `SpellSystemStates.unregister_index`; the rebind
  mints the same id for a new Spell with no compiler artifact and a structural state that late binding makes
  valid eagerly, so `Meld._ensure_resolution_resolvable` reads the dead definition's `valid`, skips phases 5-11
  and the context builder fails. The repair retires an id's conduit verdicts when its definition leaves the
  frame and when a definition is registered under that id.
- Non-goals: no change to the CreationContext guard, to what `cleanup_spell` promises about the surviving
  product, to purge, to the structural axis (`SpellSystemState`), to the meld hot path, to `RiskManager`'s
  verbs, or to any public API. Slotted existences keep their rule (owner ruling 2026-10-03): the object built
  from the removed definition is deliberately left alive in its id-keyed slot, so the replacement's first
  meld in that scope returns it; this patch documents that rule and changes nothing about it.

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| DevOps Control Plane / Conduit Resolution State | modify (one new verb) | the state has no way to retire one id's verdicts; only cleanup wipes all | none |
| DevOps Control Plane / SpellSystemStates Registry | modify (two new verbs, two call sites) | unregister never touched `_resolution_by_conduit_id`; register gated only the structural state | the state verb |

## Interface and Boundary Deltas
- Internal addition: `ConduitResolutionState.forget_spell(spell_id, *, change_reason=None) -> bool` - pops the
  spell-level and root-level verdict for the id, marks the state dirty with the reason when one existed, fires
  no RiskManager callback, returns whether a verdict existed.
- Internal additions: `SpellSystemStates.forget_spell_resolution_verdicts(spell_id, *, change_reason=None)
  -> int` (public form, takes the registry lock) and `SpellSystemStates._forget_resolution_verdicts_locked(
  spell_id, *, change_reason) -> int` (caller holds the lock), applying `forget_spell` to every live conduit
  state and returning how many held a verdict.
- Behaviour deltas: `unregister_index` calls the locked helper for the removed current spell id (reason
  `cleaned_up_spell`) in both its branches; `register_index` calls it for `spell_index.selected_spell_id`
  (reason `register_or_rebind`) before the structural gate. No public API change, no new error type.

## Cross-Component Invariants
- A spell id that no registered `SpellSystemState` carries has no resolution verdict in any conduit.
- Registering an index publishes a version id with no resolution verdict anywhere; the first meld of that
  version in each conduit runs phases 5-11 there (unknown -> `_ensure_resolution_resolvable` -> target pass),
  exactly as a never-melded late bind does today.
- Lock order stays registry -> conduit state; the forgetting verbs take no other lock and run no callback, so
  the registry may hold its lock across them (which is what makes them race-free against
  `drop_conduit_resolution_state` and `cleanup`, both of which pop under that lock before cleaning).
- The risk model is informed through its existing owner-scoped verbs: `RiskManager.register_spell` on the
  rebind recomputes resolution risk from the live (now unknown) verdict, so the Book's
  `_spellbook_validation_required` is True until the replacement's revalidating meld writes `valid`.
- Dependents of a removed definition are unchanged: `unregister_index` already gates them structurally through
  the impact closure, and their next meld rebuilds against the rebound address (measured green before and
  after).

## Migration Order
1. Patch lane linked; owner confirms the exact edit.
2. Regressions red on the unpatched tree (four-case probe, M1/M3/M4/M5, the registry unit tests).
3. The two-file source change (`fix/apply_forget_verdicts.py`), docstrings included; green; four tiers green.
4. Notch `__version__` (read at landing), release-note section, system docs + indexes, graph descriptors.
5. Assets and LLM bundles last; both `--check` runs OK; patch docs promoted and archived at turn-in.

## Rollback
- Revert the two files together; no record, cache or API shape changes. Tests added with the repair are
  removed with it.

## Ticket Coverage Matrix
| patch section | ticket |
|---|---|
| all | tickets/tasks/2026-10-03_repair_rebind_after_first_meld_task.md |
| cause and prototype evidence | tickets/tasks/2026-10-03_reproduce_rebind_after_first_meld_task.md |
<!-- END ENTRY: "rebind after first meld: scope, deltas, invariants" -->
