# code_description_patch_meld_refusal

## Metadata
- Patch ID: failed_late_bind_unwind_2026_11_22
- Component: `Meld._refuse_open_late_bind` and its four call sites
- Status: implemented at 0.2.8316; merged
- Owner: Mark (accountable); melder_0 (synaptic_python_developer)
- Created: 2026-11-23T10:14:18Z
- Updated: 2026-11-23T11:20:00Z

## Control Flow Commitments
- `_refuse_open_late_bind(spell, consumer=None)`: read `spell._spell_system_states.late_bind_thread_ids`; an empty map
  returns at once. Otherwise read the entry for `spell.spell_id`; none, or the calling thread's id, returns. Any other
  thread id raises MeldExecutionError: for the melded spell itself, naming it; for a dependency, naming the consumer
  first and the late-bound dependency after.
- `_ensure_lineage_resolvable(spell)`: refuse the spell first; then the catch-up (`_refresh_stale_dependencies`
  refuses each dependency it visits); after the structural branch, when a compile follows, walk the spell's planned
  dependencies with the catch-up's walk and refuse a marked one, before `_ensure_resolution_resolvable`.
- `_ensure_runtime_resolution_ready(spell)`: refuse the spell first; its catch-up refuses dependencies as above.

## Edge and Error Semantics
- The binding thread passes everywhere, so its window can meld what it binds.
- The check never reads the spell's index: the map is keyed by spell id, which a cleaned Spell keeps.
- No wait: the caller retries (owner, 2026-11-23).

## Invariants and Idempotency
- Reads only. No lock is taken: the map is replaced whole and read once per check.

## Explicit Non-Goals
- No check on the warm doors: the Book flag is pinned up while a late bind is open, so no meld of that Book reaches
  them.
- No walk of a valid spell's existing plan on a warm meld in the lane (the known limit in architecture_patch.md).
