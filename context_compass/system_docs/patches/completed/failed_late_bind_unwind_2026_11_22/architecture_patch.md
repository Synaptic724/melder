# architecture_patch

## Metadata
- Patch ID: failed_late_bind_unwind_2026_11_22
- Status: implemented at 0.2.8316; merged into src_architecture, src_components, tests_components and the source
  graph
- Owner: Mark (accountable); melder_0 (synaptic_python_developer) authors and implements
- Ticket: https://github.com/Synaptic724/melder/issues/330 (story STORY-2026-11-16-failed_late_bind_is_undone)
- Created: 2026-11-23T10:14:18Z
- Updated: 2026-11-23T11:20:00Z

## Patch Scope and Non-Goals
- Objective: a late bind - a bind after its Book is conjured - whose commit refuses it is undone inside the
  mediator's scope, before the claims are released, so the Book is as it was: a retry gets the same refusal (or binds,
  once the cause is fixed) instead of colliding on its spell id, and the spells that came to rely on the window's
  spells are flagged for revalidation. While a late-bind window is open, a meld on another thread that reaches one of
  the window's spells - melding it, or resolving it as a dependency - is refused at once and its caller retries; the
  binding thread's own melds pass. Decided by the owner on 2026-11-22 and 2026-11-23 (#330 Decision Log, the PLAN and
  the DECISION notes after it).
- Non-goals: bind-time policies; unwinding an in-window abort (a window body that raises keeps today's contract: its
  spells stay, and their marks are cleared); notch, link and transfer windows; the frame spell-id-set defect, the gate
  a successful `bind_inactive` leaks, the undrained dirty set and the Book flag's weakness (#342); objects that melds
  built during the window keep their slot; a managed pool the bind re-pointed stays; forward-only records stay (the
  bind callbacks, the research journal, crystal tap rows, the DevOps fact stamps).

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| DevOps Control Plane: `SpellState`, `SpellSystemStates` | modify | the late-bind mark: a flag on the lineage's state and a published, lock-free map of spell id to binding thread id | none |
| DevOps Control Plane: `ChangeControlManager`, `RiskManager` | modify | remember a bind request the structural validator refused; a default abort hook that has the Spellbook unwind it; refuse a staged bind spell already compiled broken; a public Book-flag refresh | SpellSystemStates |
| Spellbook Core: bind, bind_inactive, the bind window, the unwind | modify | mark and pin before publishing; window bookkeeping; the window end; `_unwind_refused_bind_window` | DevOps, Creations |
| Meld Resolution Runtime: `Meld` | modify | refuse a meld that reaches another thread's open late bind | SpellSystemStates |
| Creations | modify | `forget_slot`: drop one slot and its shelf entry without disposing the object | none |

## Interface and Boundary Deltas
- `SpellState.late_bind_in_progress`: a new member on the explanation axis; it changes no validity.
- `SpellSystemStates.register_index(..., late_bind_thread_id: Optional[int] = None)` sets the flag and publishes the
  spell id in `late_bind_thread_ids` (a dict replaced whole, read without a lock); `clear_late_bind_marks(spell_ids)`
  removes both; `unregister_index` drops the spell id from the map.
- `ChangeControlManager`: `__init__` installs `_default_abort_hook` through `set_abort_hook`; the structural validator
  refuses a staged bind spell whose Phase-4 result is already broken.
- `RiskManager.refresh_spellbook_flag(conduit_id)`: the public form of the existing refresh.
- `Creations.forget_slot(key) -> bool`.
- New refusal: `MeldExecutionError` naming the late-bound spell and saying to meld again once its bind finishes.
- A refused late bind's error keeps its type and text and gains a note naming the spells the unwind removed, and any
  step that could not be undone.

## Cross-Component Invariants
- Mark before publish: a late-bound spell's lineage carries the mark, and its Book's validation flag is up and pinned,
  before the Book maps publish the spell. So a meld on another thread that can find the spell takes the validation
  lane, and the lane sees the mark.
- The binding thread's melds pass. Every other thread's meld that reaches a marked spell raises before it compiles or
  builds anything from it.
- The unwind runs only for a bind request whose structural validator refused, from the orchestrator's commit-failure
  path, before the claims are released. An in-window abort runs the same abort hook and unwinds nothing.
- The window end - the outermost bind end, committed or not - clears every mark still registered, drops the pin and
  refreshes the Book flag from the RiskManager.
- No new lock-order edge: the unwind takes, one at a time, the locks `cleanup_and_remove_spell` and `_dispose_spell`
  take, on the committing thread, holding no Book lock across its steps.

## Migration and Rollout Order
1. Failing-first pins on 0.2.8315: component tests through public calls; unit pins for the new members.
2. `SpellState` and `SpellSystemStates`; `Creations.forget_slot`; `RiskManager.refresh_spellbook_flag`.
3. Spellbook: the marks, the window bookkeeping, the window end and the unwind.
4. ChangeControlManager: the refusal record, the default abort hook and the already-broken refusal.
5. Meld: the refusal points.
6. src_architecture, src_components, tests_components and the source graph; the release note; notch 0.2.8316; the
   rebuild last.

## Rollback Strategy
- Rollback trigger: a successful late bind or a warm meld that behaves differently; a hang at a window end.
- Rollback steps: drop the default abort hook (the unwind stops), the `register_index` argument and the meld refusals;
  the Book flag setter returns to its plain write.
- Post-rollback verification: the failing-first pins return to their 0.2.8315 results.

## Validation Expectations and Evidence Plan
- Component, public calls, the GIL off: the cases of the PLAN's step 1 as amended on 2026-11-23 (no timing tests).
- Unit: the registry's mark and map; `forget_slot`; the abort hook's request filter; the flag pin.
- Suites: the spellbook, meld, DevOps and creations suites, then the full suite, with the GIL off.

## Ticket Coverage Map
- Story: https://github.com/Synaptic724/melder/issues/330

## Unknowns and Decision Requests
- UNKNOWN (accepted): memory ordering under free threading between the mark's publication and the Book maps' insert.
  Both are program-ordered on the binding thread and each is one atomic store; a reader that finds the spell in the
  Book maps reads the map after it.
- Known limit: a consumer the binding thread itself compiled over a window spell, inside the window, serves its plan
  to other threads' warm melds until the window ends - a warm meld walks no plan. After a refusal, the unwind's edge
  closure flags that consumer.
- DECISION_REQUEST: none open.

## Context / Handoff Summary
- What changed: implemented as specified at 0.2.8316, with three refinements recorded in #330's Notes:
  `SpellState.late_bind_in_progress` is declared after `non_resolvable` (the numeric era's declaration order is
  pinned; the new member takes no legacy number); a dependency's refusal names the melded consumer as the
  MeldExecutionError's spell and the late-bound dependency in its message; a parked mate is named "(spell_id <id>,
  parked)" in the undone note. 41 older tests that pinned "a refused late bind stays registered and refused" now pin
  the undo. The deltas are merged into the canonical system docs and the graph.
- What remains: nothing in this lane.
- Next entrypoints: component_patch_spellbook_core.md, code_description_patch_unwind.md.
