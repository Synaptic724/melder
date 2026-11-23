# component_patch_meld_resolution_runtime

## Metadata
- Patch ID: failed_late_bind_unwind_2026_11_22
- Component: Meld Resolution Runtime - `Meld._ensure_lineage_resolvable`, `Meld._ensure_runtime_resolution_ready`,
  `Meld._refresh_stale_dependencies` and a new `Meld._refuse_open_late_bind`
- Status: implemented at 0.2.8316; merged
- Owner: Mark (accountable); melder_0 (synaptic_python_developer)
- Created: 2026-11-23T10:14:18Z
- Updated: 2026-11-23T11:20:00Z

## Component Purpose and Boundary
- Current boundary: a meld in the validation lane compiles a staged late-bound spell, or a consumer's plan over it,
  while the bind's window is still open.
- Target boundary: in the lane, a meld on another thread that reaches a spell another thread is late-binding raises
  MeldExecutionError before it compiles or builds anything from it; the binding thread passes.

## Before/After Behavior Summary
- Before: such a meld compiles the spell during the window; the commit then skips it.
- After: it raises at once; after the bind commits, the same meld builds as usual; after a refusal, the spell is gone
  and the meld gets today's answer for a spell that is not bound.
- Unchanged: the warm meld doors (the Book flag is pinned up while a late bind is open, so no meld of that Book takes
  them); every meld when no late bind is open (one empty-map read in the lane).

## Interface Deltas
- New refusal: `MeldExecutionError(spell_id=<the late-bound spell's id>, spell_name=<its name>, message=...)`. For the
  spell itself: "'<name>' (spell_id <id>) is being late-bound by another thread: its bind has not committed yet, so
  nothing is built from it until the bind resolves. Meld again once that bind finishes; if the bind is refused it is
  undone and '<name>' is not bound." For a dependency, the message names the melded spell first and the late-bound
  dependency after.

## State and Lifecycle Deltas
- None: the check reads `SpellSystemStates.late_bind_thread_ids` and the calling thread's id.

## Failure Mode Deltas
- Removed: a staged spell compiled by another thread's meld, which the commit then skipped (it committed broken).
- New: a meld that lands inside another thread's late-bind window raises and must be retried (owner, 2026-11-23).

## Dependency and Ordering Constraints
1. The gate's entry, before `_may_compile` and the catch-up.
2. Each dependency the catch-up walk visits, before `_is_stale` and any refresh.
3. After the structural branch, before the resolution pass, when a compile follows: the spell's planned dependencies,
   walked as the catch-up walks them, so a plan built over a marked spell is refused before Phases 5-11.
4. The deferred lane's entry.

## Validation Expectations
- Another thread's meld of a late-bound spell raises MeldExecutionError while the window is open, and builds after the
  commit.
- Another thread's meld of a consumer that would resolve the late-bound spell raises the same error.
- The binding thread's own meld inside its window builds.
