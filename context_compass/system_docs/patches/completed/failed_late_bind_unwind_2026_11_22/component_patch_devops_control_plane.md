# component_patch_devops_control_plane

## Metadata
- Patch ID: failed_late_bind_unwind_2026_11_22
- Component: DevOps Control Plane - `SpellState`, `SpellSystemStates`, `ChangeControlManager`, `RiskManager`
- Status: implemented at 0.2.8316; merged
- Owner: Mark (accountable); melder_0 (synaptic_python_developer)
- Created: 2026-11-23T10:14:18Z
- Updated: 2026-11-23T11:20:00Z

## Component Purpose and Boundary
- Current boundary: a lineage's state says nothing about an open bind; the orchestrator's abort slot runs no hook
  (`_abort_hook` is None and nothing sets it); the structural validator compiles only staged spells with no Phase-4
  result, so a staged spell a meld compiled broken during the window commits.
- Target boundary: a late-bound lineage carries `SpellState.late_bind_in_progress` and its spell id sits in the
  registry's published `late_bind_thread_ids` with the binding thread's id; the manager remembers the bind request
  its structural validator refused, and its default abort hook has the Spellbook unwind that request's window; the
  validator also refuses a staged bind spell whose Phase-4 result is already broken.

## Before/After Behavior Summary
- Before: a late bind refused at commit raises, and its spell stays registered everywhere (a retry collides on the
  spell id); a meld on another thread can compile the staged spell during the window and the commit skips it.
- After: the refused window is unwound before the claims are released and the error carries a note naming the spells
  removed; a broken staged spell is refused whoever compiled it. A committed window, and every request that is not a
  refused bind, behaves as before.

## Interface Deltas
- `SpellState.late_bind_in_progress` (member). It changes no validity; `SpellSystemStates` owns setting and clearing
  it.
- `SpellSystemStates.register_index(..., late_bind_thread_id: Optional[int] = None)`: an int sets the flag on the
  state and publishes `{selected_spell_id: late_bind_thread_id}` in the map; None leaves both as they are. A value that
  is neither raises TypeError before anything is registered.
- `SpellSystemStates.late_bind_thread_ids -> Dict[str, int]`: the published map, read without a lock; never mutated.
- `SpellSystemStates.clear_late_bind_marks(spell_ids: Iterable[str]) -> None`: removes the flag from each registered
  state and the ids from the map; ids not marked are ignored.
- `SpellSystemStates.unregister_index`: also drops the removed state's spell id from the map.
- `ChangeControlManager._default_abort_hook(staged)`, installed in `__init__`; the refusal record
  `_refused_bind_requests` (request id -> the refusal).
- `RiskManager.refresh_spellbook_flag(conduit_id) -> None`.

## State and Lifecycle Deltas
- `SpellSystemStates._late_bind_thread_by_spell_id` (Dict[str, int]): replaced whole under the registry lock; left as
  an empty dict at cleanup (a tombstone for lock-free readers), as `_non_resolvable_index_ids` is.
- `ChangeControlManager._refused_bind_requests` (Dict[str, BaseException]): written under the manager lock by the
  commit-validator dispatch, popped by the abort hook; cleared and deleted at cleanup.

## Failure Mode Deltas
- Removed: a refused late bind leaves its registration behind; a broken staged spell commits.
- New: none for callers; an unwind step that fails is logged at ERROR by the Spellbook and named in a note on the
  refusal, and the remaining steps still run.

## Dependency and Ordering Constraints
1. The refusal is recorded before the orchestrator calls the abort hook (same thread, the dispatch's except clause).
2. The hook resolves the Spellbook from the staged mutation as the validator does, and delegates the unwind to it.
3. `unregister_index` drops the mark with the lineage, so an unwound spell leaves no mark.

## Validation Expectations
- Unit: the flag and the map after `register_index(..., late_bind_thread_id=...)`, after `clear_late_bind_marks` and
  after `unregister_index`; TypeError for a bad id; the hook acts only for a recorded request and pops it; the
  validator refuses an already-broken staged bind spell.
- Component: through public calls, the cases in component_patch_spellbook_core.md.
