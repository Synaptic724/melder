"""Promote the scope_exit_dispose_2026_09_27 patch into src_components.md (0.2.8203).

Every edit is an exact-match anchor that must occur once; the script refuses to write otherwise.
Usage: python edit_src_components.py <doc path> <verified_at UTC>
"""
import pathlib
import sys

doc = pathlib.Path(sys.argv[1])
verified_at = sys.argv[2]
text = doc.read_bytes().decode("utf-8")
assert "\r\n" not in text


def swap(old: str, new: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"anchor found {count} times:\n{old}")
    text = text.replace(old, new)


# ---------------------------------------------------------------- AethericFrame Services
swap("  - src/melder/aether/aetheric_frame/aetheric_frame.py:209 (DevOpsManager owned)\n",
     "  - src/melder/aether/aetheric_frame/aetheric_frame.py:208 (DevOpsManager owned)\n")
swap("  Other live pairs: `src/melder/aether/conduit/conduit_ward/conduit_ward.py:799` (two peer wards), `:973`\n",
     "  Other live pairs: `src/melder/aether/conduit/conduit_ward/conduit_ward.py:893` (two peer wards), `:1067`\n")
swap("  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:799, 973\n",
     "  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:893, 1067\n")
swap(
    "Failure Modes:\n- Cleanup is best-effort; errors are suppressed to complete teardown.\n",
    "Failure Modes:\n"
    "- Teardown never stops on a conduit: a conduit whose teardown raises (its disposal failures come after its\n"
    "  own teardown finished, 0.2.8203) is logged through the Aether logger and the next conduit is cleaned.\n"
    "  Before 0.2.8203 that failure was swallowed with a bare `pass`. The later service cleanups are not wrapped.\n"
    "  EVIDENCE: `src/melder/aether/aetheric_frame/aetheric_frame.py:AethericFrame._cleanup_data_structures`.\n",
)
swap(
    "- EXACTLY ONE log call in the whole module, and it is a `warning`, not an error:\n"
    "  a conflicting `AethericFrameConfiguration` for an already-configured frame is\n"
    "  IGNORED rather than rejected, and the warning reports the existing posture\n"
    "  alongside the attempted one so the discarded intent is recoverable. It is\n"
    "  routed through `self._aether._logger` after a `None` guard, because the frame\n"
    "  has no logger of its own - during early boot the Aether logger may not exist\n"
    "  yet.\n"
    "- Everything else is exceptions. A frame that is misbehaving without raising\n"
    "  will produce no log output at all; do not read silence as health.\n"
    "  EVIDENCE:\n"
    "  - src/melder/aether/aetheric_frame/aetheric_frame.py:750-761\n",
    "- TWO log calls in the whole module (the second since 0.2.8203), both routed\n"
    "  through `self._aether._logger` after a `None` guard, because the frame has no\n"
    "  logger of its own - during early boot the Aether logger may not exist yet.\n"
    "  A `warning`: a conflicting `AethericFrameConfiguration` for an\n"
    "  already-configured frame is IGNORED rather than rejected, and the warning\n"
    "  reports the existing posture alongside the attempted one so the discarded\n"
    "  intent is recoverable. An `error` with `exc_info`: a conduit raised during\n"
    "  frame teardown (\"Error cleaning conduit during frame teardown\").\n"
    "- Everything else is exceptions. A frame that is misbehaving without raising\n"
    "  will produce no log output at all; do not read silence as health.\n"
    "  EVIDENCE:\n"
    "  - src/melder/aether/aetheric_frame/aetheric_frame.py:759-770\n"
    "  - src/melder/aether/aetheric_frame/aetheric_frame.py:292-307\n",
)

# ---------------------------------------------------------------- Conduit Runtime
swap(
    "- Execution scope for resolving spells and managing object lifecycles.\n\nNamed lifecycle (2026-09-23):",
    "- Execution scope for resolving spells and managing object lifecycles.\n"
    "\n"
    "Scope exits (2026-09-27, 0.2.8203): `with conduit:` is a dispose scope. `__enter__` returns the conduit and\n"
    "takes no lock; `__exit__` calls `cleanup()` and never suppresses the block's exception, so at block exit a\n"
    "lesser returns to its root's pool and a root is torn down. `enter_lesser_conduit(logger=None, *, name=None)`\n"
    "returns exactly `create_lesser_conduit(logger, name=name)` for such a block: plain, no per-thread stack.\n"
    "`cleanup()` keeps its dispatch; `_prepare_for_pool` reads the state once and returns for `pooled_lesser`, so\n"
    "a second soft cleanup never pools the shell twice. A lesser's return then runs, in order: descendants\n"
    "(`ConduitWard._cleanup_children_for_pool(collect_finished=True)`, only when the ward has children),\n"
    "SpellSpaces (`_cleanup_spellspaces_for_pool`, which returns None before the drain call when this thread has\n"
    "no open managed space and none is registered), the own store (`reset_for_pool`), named retirement or\n"
    "`_detach_for_pool`, local hook clear, Meld hook reset and `ConduitPool.return_lesser_conduit`. Disposal\n"
    "failures from those steps are collected (no list is allocated on the clean path) and raised as one\n"
    "ExceptionGroup after the shell is back in its pool. A retirement or detach failure raises at once, grouped\n"
    "with the failures collected before it, and the lesser stays attached for retry. Permanent teardown\n"
    "(`_permanent_cleanup`) collects the disposal groups `_cleanup_lesser_conduit` / `_cleanup_normal_conduit`\n"
    "return - ward, SpellSpaces (`_cleanup_spellspaces`), own store and, for a root, the cluster facade - keeps\n"
    "logging every other step error, and raises them after hooks, logger and field deletes. `enter_spellspace`\n"
    "pushes onto the owned thread stack inline. `Cleanable.using_cleanup()`, the dispose helper every Cleanable\n"
    "carries, now lets the cleanup error propagate instead of swallowing it.\n"
    "EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit.__exit__`, `Conduit.enter_lesser_conduit`,\n"
    "`Conduit._prepare_for_pool`, `Conduit._cleanup_spellspaces_for_pool`, `Conduit._permanent_cleanup`,\n"
    "`Conduit.enter_spellspace` and\n"
    "`src/melder/utilities/general_base/cleanable.py:Cleanable._CleanupContext.__exit__`.\n"
    "\n"
    "Named lifecycle (2026-09-23):",
)
swap(
    "Named soft return runs Space/creation disposal and descendant cleanup first, then structural\n"
    "retirement, cleared pooled Nexus publication, Cloud removal, frame-summary publication, name clearing\n"
    "and own detachment. The retained name/parent permits retry before fallible publication finishes.\n"
    "Failed descendants prevent ancestor return. Hook restoration and idle publication remain last.\n",
    "Named soft return runs descendant cleanup, then Space and creation disposal, then structural\n"
    "retirement, cleared pooled Nexus publication, Cloud removal, frame-summary publication, name clearing\n"
    "and own detachment. The retained name/parent permits retry before fallible publication finishes.\n"
    "A descendant still attached after failing prevents ancestor return; one that finished its return but\n"
    "raised disposal failures does not (0.2.8203). Hook restoration and idle publication remain last.\n",
)
swap(
    "_prepare_for_pool disposes Spaces and creations first, clears local lifecycle overlays, restores\n",
    "_prepare_for_pool disposes descendants, Spaces and creations first, clears local lifecycle overlays, restores\n",
)
swap(
    "- Boolean link/sever results.\n- Ownership transfer preflight summary (dict).\n",
    "- Boolean link/sever results.\n- Ownership transfer preflight summary (dict).\n"
    "- A lesser conduit from `create_lesser_conduit(...)`, or `enter_lesser_conduit(...)` for a `with` block.\n",
)
swap(
    "- Cleanup fires hooks, tears down Meld, ConduitWard, Creations, then logger.\n",
    "- Root cleanup (and a lesser's permanent cleanup) fires hooks, tears down Meld, ConduitWard, SpellSpaces\n"
    "  and Creations, then the logger, and raises the collected disposal failures last (0.2.8203). A lesser's\n"
    "  soft cleanup is its pool return: descendants, SpellSpaces, own store, retirement or detach, hooks, pool,\n"
    "  then its disposal failures. `with conduit:` runs that cleanup at block exit.\n",
)
swap(
    "- Internal RLock guards conduit operations.\n"
    "- `CreationGate` uses an internal RLock and Event to block/unblock meld calls\n",
    "- Internal RLock guards conduit operations.\n"
    "- `with conduit:` takes no lock (0.2.8203; it used to hold the conduit lock for the block); `cleanup()`\n"
    "  holds the conduit lock for the pool return or teardown.\n"
    "- `CreationGate` uses an internal RLock and Event to block/unblock meld calls\n",
)
swap(
    "- Spellspace-local request work is routed through `SpellSpaceMeld`, not\n"
    "  through the conduit front door.\n\nFailure Modes:\n",
    "- Spellspace-local request work is routed through `SpellSpaceMeld`, not\n"
    "  through the conduit front door.\n"
    "- Soft cleanup of a pooled lesser is a no-op, so no two acquisitions receive one shell (0.2.8203).\n"
    "- A disposal failure never stops a pool return or a teardown: the scope finishes, then the failures\n"
    "  are raised (0.2.8203).\n"
    "\nFailure Modes:\n",
)
swap(
    "- Meld calls block while the local `CreationGate` is disabled.\n\nObservability:\n",
    "- Meld calls block while the local `CreationGate` is disabled.\n"
    "- ExceptionGroup from `cleanup()` or a `with` block exit, after the pool return or teardown finished\n"
    "  (0.2.8203; before, conduit paths only logged these): \"Lesser conduit returned to its pool with disposal\n"
    "  failures.\" or \"Conduit torn down with disposal failures.\", each holding Creations groups. With a failing\n"
    "  block it carries the block's exception as `__context__`. A retirement or detach failure after disposal\n"
    "  failures raises \"Lesser conduit could not finish its pool return and stays attached for retry.\" and\n"
    "  the lesser stays attached.\n"
    "\nObservability:\n",
)
swap("  EVIDENCE: src/melder/aether/conduit/conduit.py:5024-5026.\n",
     "  EVIDENCE: src/melder/aether/conduit/conduit.py:5229-5231.\n")

# ---------------------------------------------------------------- ConduitWard and Contracts
swap("  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:277-281\n",
     "  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:284-288\n")
swap(
    "  EVIDENCE:\n  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:250-283\n",
    "  EVIDENCE:\n  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:251-314\n"
    "- Lesser children are torn down with `permanent_cleanup()` (`_clean_up_lesser_conduits_links`): every\n"
    "  child is attempted, a child's disposal ExceptionGroup is collected, and `cleanup()` raises them as one\n"
    "  group (\"Lesser conduits torn down with disposal failures.\") after its own teardown, logger last\n"
    "  (0.2.8203); other child errors stay logged.\n"
    "- Pool return uses `_cleanup_children_for_pool(collect_finished=False)`: children are soft-cleaned outside\n"
    "  the ward lock from a snapshot. A child that raised but is no longer attached finished its return - its\n"
    "  error is returned when `collect_finished` (a lesser's own pool return, which runs this first) and logged\n"
    "  otherwise. A child still attached is retained, and once every sibling was tried \"Cannot pool a conduit\n"
    "  while descendant cleanup is incomplete.\" is raised so the parent stays attached for retry.\n"
    "  EVIDENCE: `src/melder/aether/conduit/conduit_ward/conduit_ward.py:ConduitWard._clean_up_lesser_conduits_links`\n"
    "  and `ConduitWard._cleanup_children_for_pool`.\n",
)
swap("  EVIDENCE: src/melder/aether/conduit/conduit_ward/conduit_ward.py:708-721.\n",
     "  EVIDENCE: src/melder/aether/conduit/conduit_ward/conduit_ward.py:801-814.\n")
swap("  EVIDENCE: src/melder/aether/conduit/conduit_ward/conduit_ward.py:527-580.\n",
     "  EVIDENCE: src/melder/aether/conduit/conduit_ward/conduit_ward.py:614-672.\n")
swap("  EVIDENCE: src/melder/aether/conduit/conduit_ward/conduit_ward.py:2508-2562.\n",
     "  EVIDENCE: src/melder/aether/conduit/conduit_ward/conduit_ward.py:2567-2621.\n")
swap("  EVIDENCE: src/melder/aether/conduit/conduit_ward/conduit_ward.py:572-579.\n",
     "  EVIDENCE: src/melder/aether/conduit/conduit_ward/conduit_ward.py:665-672.\n")
swap(
    "  EVIDENCE: src/melder/aether/conduit/conduit_ward/conduit_ward.py:992-1010\n"
    "  (`_sever_link` at :992, `SafeGuard` acquired at :1008, contract lookup at\n"
    "  :1009 - the guard is taken BEFORE the lookup, which is the ordering claim).\n",
    "  EVIDENCE: src/melder/aether/conduit/conduit_ward/conduit_ward.py:1051-1069\n"
    "  (`_sever_link` at :1051, `SafeGuard` acquired at :1067, contract lookup at\n"
    "  :1068 - the guard is taken BEFORE the lookup, which is the ordering claim).\n",
)
swap(
    "- RuntimeError if `_sever_link` finds no contract to remove.\n",
    "- RuntimeError if `_sever_link` finds no contract to remove.\n"
    "- ExceptionGroup from `cleanup()` after the ward finished its teardown, when a lesser child's permanent\n"
    "  cleanup raised disposal failures (0.2.8203; before, they were logged).\n",
)
swap(
    "- `SafeLogger` with 79 `error` sites and, unusually for this codebase, 11 `info`\n",
    "- `SafeLogger` with 80 `error` sites (recounted 2026-09-27) and, unusually for this codebase, 11 `info`\n",
)
swap(
    "  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:283-285\n"
    "  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:565-567\n",
    "  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:290-292\n"
    "  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:659-660\n",
)

# ---------------------------------------------------------------- Creations and SpellSpace
swap(
    "- Instance lifecycle registry for Conduits and scoped spellspaces.\n\nPooled hook lifetime (2026-09-22):",
    "- Instance lifecycle registry for Conduits and scoped spellspaces.\n"
    "\n"
    "Scope lease and finished exits (2026-09-27, 0.2.8203): a SpellSpace carries one lease flag, `_released`.\n"
    "`SpellSpacePool.release` sets it first, before the idle append; `acquire`/`prepare_object` and\n"
    "`acquire_untracked` clear it; `_cleanup_for_destroy` sets it and keeps it True as a documented tombstone.\n"
    "`meld` and `purge` read it first and call `_refuse_released`: SpellSpaceScopeError for a released space, the\n"
    "cleaned RuntimeError for a destroyed one. `cleanup()` and `recycle_from_managed_context` return early for a\n"
    "released space, so a space is never released twice. Every exit finishes when a disposal method raises -\n"
    "Creations swapped the store empty first: the managed exit (its common lane runs inline in `__exit__`) and\n"
    "`recycle_from_managed_context` reset hooks and release in `finally`; manual cleanup runs\n"
    "`_cleanup_for_pool_reuse` (registry discard and hook reset in its `finally`) and releases in `finally`;\n"
    "permanent cleanup cleans its Meld, discards itself from the registry, leaves the thread stack\n"
    "(`SpellSpaceThreadState.discard_expected`) and deletes its fields in `finally`. The store's ExceptionGroup\n"
    "then propagates. `__exit__` of a space released or destroyed inside its own block calls\n"
    "`_leave_after_early_release` (a released space drops itself from its stack top when still there) and\n"
    "returns, so an owner cleaned inside its own managed space no longer makes that exit raise \"stack\n"
    "corruption\".\n"
    "EVIDENCE: `src/melder/aether/conduit/spell_space/spell_space.py:SpellSpace.__exit__`, `SpellSpace.cleanup`,\n"
    "`SpellSpace._cleanup_for_destroy`, `SpellSpace._refuse_released`,\n"
    "`src/melder/aether/conduit/spell_space/spell_space_pool.py:SpellSpacePool.release` and\n"
    "`src/melder/aether/conduit/spell_space/spell_space_thread_state.py:SpellSpaceThreadState.discard_expected`.\n"
    "\n"
    "Pooled hook lifetime (2026-09-22):",
)
swap(
    "- `_lock` (leaf store lock; retained after cleanup as a documented tombstone)\n- owner/scope ids\n",
    "- `_lock` (leaf store lock; retained after cleanup as a documented tombstone)\n- owner/scope ids\n"
    "- SpellSpace `_released` lease flag: True while the space is pooled, and kept True after destroy as a\n"
    "  documented tombstone (0.2.8203).\n",
)
swap(
    "- SpellSpace cleanup resets scope and unregisters from owner.\n",
    "- SpellSpace exits dispose the space's own store, reset temporary hooks and release it to its pool, which\n"
    "  sets its lease flag; manual cleanup also unregisters it, and permanent cleanup destroys it. Each exit\n"
    "  finishes when a disposal method fails, then raises the store's group (0.2.8203).\n",
)
swap(
    "- Lock order: build lock first, store lock last, never the reverse; the store lock\n"
    "  is never held around user code or while acquiring another lock.\n",
    "- Lock order: build lock first, store lock last, never the reverse; the store lock\n"
    "  is never held around user code or while acquiring another lock.\n"
    "- The SpellSpace lease flag needs no lock: the leasing thread and the pool write it, and the idle-deque\n"
    "  hand-off orders it for the next lease; the managed lane stays lock-free (0.2.8203).\n",
)
swap(
    "  no global chronology across interleaved buckets or scopes is added.\n",
    "  no global chronology across interleaved buckets or scopes is added.\n"
    "- A released SpellSpace refuses meld and purge, and it is never released twice (0.2.8203).\n",
)
swap(
    "- `SpellSpaceScopeError` if scope is misused. NOT RAISED BY THIS COMPONENT -\n"
    "  the sole raise site in the tree is `SpellSpaceThreadState`, at\n"
    "  `src/melder/aether/conduit/spell_space/spell_space_thread_state.py:245`, and\n"
    "  it signals STACK CORRUPTION at exit rather than a caller mistake. See\n"
    "  `### Subcomponent: SpellSpace Thread State`.\n",
    "- `SpellSpaceScopeError` from `SpellSpace.meld` / `purge` on a space released to its pool\n"
    "  (`SpellSpace._refuse_released`, 0.2.8203), and from `SpellSpaceThreadState.pop_expected`, at\n"
    "  `src/melder/aether/conduit/spell_space/spell_space_thread_state.py:245`, when a managed exit is not\n"
    "  its thread's stack top - STACK CORRUPTION rather than a caller mistake. Before 0.2.8203 the thread\n"
    "  state was the sole raise site. See `### Subcomponent: SpellSpace Thread State`.\n"
    "- Known probe inaccuracy (2026-09-27): `SpellSpaceMeld._describe_spell_live_creation_status` reads `many`\n"
    "  from the owner conduit's store, but a disposal-bearing `many` melded through a space lives in the space's\n"
    "  own store, so a live-creation probe through a space can report 0 while the space holds one. Lifetimes\n"
    "  are unaffected.\n"
    "  EVIDENCE: `src/melder/aether/conduit/meld/spellspace_meld.py:SpellSpaceMeld._describe_spell_live_creation_status`.\n",
)
swap(
    "- `src/melder/aether/conduit/creations/conduit_creations.py`\n"
    "- `src/melder/aether/conduit/spell_space/spell_space.py`\n",
    "- `src/melder/aether/conduit/creations/conduit_creations.py`\n"
    "- `src/melder/aether/conduit/spell_space/spell_space.py`\n"
    "- `src/melder/aether/conduit/spell_space/spell_space_pool.py`\n"
    "- `src/melder/aether/conduit/spell_space/spell_space_thread_state.py`\n",
)
swap(
    "SpellSpace enforces active-scope semantics and supports reset/versioning.\n",
    "SpellSpace enforces active-scope semantics and supports reset/versioning.\n"
    "CORRECTED 2026-09-27: the line above is stale - SpellSpace has no active-scope check, no `reset()` and no\n"
    "version; it carries a lease flag (see this entry's \"Scope lease and finished exits\").\n",
)

# ---------------------------------------------------------------- C2 subcomponents
swap(
    "Contract/Interface:\n- `create_lesser_conduit(...)`.\n",
    "Contract/Interface:\n"
    "- `create_lesser_conduit(...)`; `enter_lesser_conduit(...)` returns it for a `with` block, whose exit\n"
    "  returns the lesser to its pool (0.2.8203).\n"
    "- `cleanup()` returns it: descendants, SpellSpaces, own store, retirement or detach, hooks, pool, then\n"
    "  the disposal failures; a pooled lesser's second soft cleanup does nothing.\n",
)
swap(
    "Purpose:\n"
    "- Enforce spellspace activation for unique_per_spell_space.\n"
    "Contract/Interface:\n"
    "- `SpellSpace.meld()` checks active scope and delegates to Conduit.\n"
    "Data Structures:\n"
    "- SpellSpace id and version counter.\n"
    "Concurrency/Threading:\n"
    "- No explicit lock; owner Conduit lock used upstream.\n"
    "Key Files (C1):\n"
    "- `src/melder/aether/conduit/spell_space/spell_space.py`\n",
    "Purpose:\n"
    "- Refuse use of a SpellSpace outside its lease (0.2.8203; corrected 2026-09-27 - this entry used to\n"
    "  describe an active-scope check and a version counter that the source never had).\n"
    "Contract/Interface:\n"
    "- `SpellSpace.meld()` and `purge()` read `_released` first and call `_refuse_released()` when it is set:\n"
    "  SpellSpaceScopeError for a space released to its pool, the cleaned RuntimeError after destroy. A\n"
    "  leased space then runs through its own SpellSpaceMeld door (the warm lanes, or `SpellSpaceMeld.meld`);\n"
    "  it need not be the top of its thread's stack.\n"
    "- `SpellSpacePool.release()` sets the flag; `acquire()`/`prepare_object()` and `acquire_untracked()`\n"
    "  clear it.\n"
    "Data Structures:\n"
    "- The space id and one bool lease flag, `_released`; no version counter.\n"
    "Concurrency/Threading:\n"
    "- No lock on the check: the leasing thread and the pool write the flag, and the idle-deque hand-off\n"
    "  orders it for the next lease.\n"
    "Key Files (C1):\n"
    "- `src/melder/aether/conduit/spell_space/spell_space.py`\n"
    "- `src/melder/aether/conduit/spell_space/spell_space_pool.py`\n",
)
swap(
    "- IT IS THE SOLE RAISER OF `SpellSpaceScopeError` in the entire tree, at\n"
    "  `src/melder/aether/conduit/spell_space/spell_space_thread_state.py:245`, when\n"
    "  the exiting spellspace is not the one on top of the current thread's stack -\n"
    "  i.e. stack corruption, not a user error. Two component entries document that\n"
    "  exception in their Failure Modes; NEITHER owns this file, which is why it is\n"
    "  catalogued here.\n",
    "- `pop_expected(space)` raises `SpellSpaceScopeError`, at\n"
    "  `src/melder/aether/conduit/spell_space/spell_space_thread_state.py:245`, when\n"
    "  the exiting spellspace is not the one on top of the current thread's stack -\n"
    "  i.e. stack corruption, not a user error. Until 0.2.8203 that was the sole raise\n"
    "  site in the tree; `SpellSpace._refuse_released` now raises it too, for a space\n"
    "  used after its release. Two component entries document that exception in their\n"
    "  Failure Modes; NEITHER owns this file, which is why it is catalogued here.\n"
    "- `discard_expected(space)` (0.2.8203) pops only when `space` is the top entry and\n"
    "  never raises; a SpellSpace released or destroyed inside its own block uses it to\n"
    "  leave the stack. `Conduit.enter_spellspace` pushes onto this holder's per-thread\n"
    "  list inline (the hot path), in step with `push`.\n",
)

# ---------------------------------------------------------------- Flows
swap(
    "### Flow: Create Lesser Conduit\n"
    "1. `Conduit.create_lesser_conduit(...)` fires pre-create hook.\n"
    "2. Constructs lesser Conduit with inherited Spellbook/`SpellbookConfiguration`.\n"
    "3. Wires root Creations and root conduit into lesser conduit.\n"
    "4. Links lesser into ConduitWard lineage tree.\n"
    "5. Fires activated and post-create hooks.\n",
    "### Flow: Create Lesser Conduit\n"
    "1. `Conduit.create_lesser_conduit(...)` fires pre-create hook (`enter_lesser_conduit(...)` makes the same\n"
    "   call for a `with` block).\n"
    "2. Constructs lesser Conduit with inherited Spellbook/`SpellbookConfiguration`.\n"
    "3. Wires root Creations and root conduit into lesser conduit.\n"
    "4. Links lesser into ConduitWard lineage tree.\n"
    "5. Fires activated and post-create hooks.\n"
    "6. Return (`cleanup()`, or the `with` block exit): `Conduit._prepare_for_pool()` ->\n"
    "   `ConduitWard._cleanup_children_for_pool(collect_finished=True)` -> `Conduit._cleanup_spellspaces_for_pool()`\n"
    "   -> `Creations.reset_for_pool()` -> `Conduit._prepare_named_for_pool()` or `ConduitWard._detach_for_pool()`\n"
    "   -> hook reset -> `ConduitPool.return_lesser_conduit()` -> raise the collected disposal failures (0.2.8203).\n",
)
swap(
    "### Flow: SpellSpace Scoped Meld\n"
    "1. `conduit.enter_spellspace()` creates and activates a SpellSpace.\n"
    "2. `SpellSpace.meld(...)` verifies it is the active scope.\n"
    "3. Delegates to `Conduit.meld(...)` for resolution.\n"
    "4. `SpellSpace.reset()` clears spellspace-scoped instances and increments version.\n",
    "### Flow: SpellSpace Scoped Meld\n"
    "1. `conduit.enter_spellspace()` -> `SpellSpacePool.acquire_untracked()` (clears `_released`) -> push on the\n"
    "   calling thread's stack (inline) -> returns the space.\n"
    "2. `SpellSpace.meld(...)` -> `_released` check (`_refuse_released()` when set) -> warm lane\n"
    "   (`_fast_meld_doors` / `_fast_input_doors`) or `SpellSpaceMeld.meld(...)`.\n"
    "3. Block exit, `SpellSpace.__exit__` -> `SpellSpaceThreadState.pop_expected(space)` ->\n"
    "   `Creations.reset_for_pool_unlocked()` -> Meld hook reset -> `SpellSpacePool.release(space)` (sets\n"
    "   `_released`) -> the store's ExceptionGroup, if a disposal method failed (0.2.8203).\n"
    "Corrected 2026-09-27: this flow used to delegate to `Conduit.meld` and end in `SpellSpace.reset()`,\n"
    "neither of which happens.\n",
)

# ---------------------------------------------------------------- other remapped citations
swap("  - src/melder/aether/conduit/conduit.py:5124, 5200, 5280 (notch/add/remove\n",
     "  - src/melder/aether/conduit/conduit.py:5329, 5405, 5485 (notch/add/remove\n")
swap("`src/melder/aether/conduit/conduit.py:5147`, then calls",
     "`src/melder/aether/conduit/conduit.py:5352`, then calls")
swap("`src/melder/aether/conduit/conduit.py:5220`, then calls",
     "`src/melder/aether/conduit/conduit.py:5425`, then calls")
swap("`remove_from_index` at `src/melder/aether/conduit/conduit.py:5291`, then calls",
     "`remove_from_index` at `src/melder/aether/conduit/conduit.py:5496`, then calls")
swap("  - src/melder/aether/conduit/conduit.py:5075, 5165, 5243 (public verbs)",
     "  - src/melder/aether/conduit/conduit.py:5280, 5370, 5448 (public verbs)")
swap("`src/melder/aether/aetheric_frame/aetheric_frame.py:463`) +",
     "`src/melder/aether/aetheric_frame/aetheric_frame.py:479`) +")
swap("(`src/melder/aether/aetheric_frame/aetheric_frame.py:841`; resident member",
     "(`src/melder/aether/aetheric_frame/aetheric_frame.py:867`; resident member")

# ---------------------------------------------------------------- C1 remeasure
def remeasure(path: str, old_end: int, old_at: str, new_end: int) -> None:
    swap(
        f"- path: `{path}`\n  start_line: 1\n  end_line: {old_end}\n  loc: {old_end}\n  verified_at: {old_at}\n",
        f"- path: `{path}`\n  start_line: 1\n  end_line: {new_end}\n  loc: {new_end}\n  verified_at: {verified_at}\n",
    )

remeasure("src/melder/aether/aetheric_frame/aetheric_frame.py", 1136, "2026-09-26T20:10:34Z", 1145)
remeasure("src/melder/aether/conduit/conduit.py", 6897, "2026-09-26T20:10:34Z", 7102)
remeasure("src/melder/aether/conduit/conduit_ward/conduit_ward.py", 3813, "2026-09-27T11:46:59Z", 3872)
remeasure("src/melder/aether/conduit/spell_space/spell_space.py", 650, "2026-09-26T20:10:34Z", 792)
remeasure("src/melder/aether/conduit/meld/spellspace_meld.py", 989, "2026-09-26T20:10:34Z", 1031)
remeasure("src/melder/aether/conduit/spell_space/spell_space_thread_state.py", 302, "2026-08-02T16:29:16Z", 328)
swap(
    f"- path: `src/melder/aether/conduit/spell_space/spell_space.py`\n  start_line: 1\n  end_line: 792\n"
    f"  loc: 792\n  verified_at: {verified_at}\n",
    f"- path: `src/melder/aether/conduit/spell_space/spell_space.py`\n  start_line: 1\n  end_line: 792\n"
    f"  loc: 792\n  verified_at: {verified_at}\n"
    f"- path: `src/melder/aether/conduit/spell_space/spell_space_pool.py`\n  start_line: 1\n  end_line: 301\n"
    f"  loc: 301\n  verified_at: {verified_at}\n",
)

# ---------------------------------------------------------------- Information sources
swap(
    "- `src/melder/aether/conduit/meld/spellspace_meld.py`\n- `src/melder/aether/conduit/spell_space/spell_space.py`\n",
    "- `src/melder/aether/conduit/meld/spellspace_meld.py`\n- `src/melder/aether/conduit/spell_space/spell_space.py`\n"
    "- `src/melder/aether/conduit/spell_space/spell_space_pool.py`\n"
    "- `src/melder/aether/conduit/spell_space/spell_space_thread_state.py`\n"
    "- `src/melder/utilities/general_base/cleanable.py`\n"
    "- `src/melder/utilities/custom_exceptions/spell_space_scope_error.py`\n",
)

# ---------------------------------------------------------------- Handoff
swap(
    "## Context / Handoff Summary\n\n2026-09-27 meld entry cache by name and class:",
    "## Context / Handoff Summary\n\n"
    "2026-09-27 scope exits (0.2.8203): `with conduit:` disposes (a lesser returns to its pool, a root is torn\n"
    "down) and `Conduit.enter_lesser_conduit()` makes a lesser for such a block; every scope exit finishes when a\n"
    "disposal method fails and then raises the failures as one ExceptionGroup; a lesser's pool return disposes its\n"
    "descendants first; soft cleanup of a pooled or released scope does nothing; a released SpellSpace refuses\n"
    "meld and purge (one lease flag); frame teardown logs a failing conduit. Promoted into Conduit Runtime (\"Scope\n"
    "exits\"), ConduitWard, Creations and SpellSpace (\"Scope lease and finished exits\"), AethericFrame Services, the\n"
    "Lesser Conduit Creation, SpellSpace Scope Gate and SpellSpace Thread State subcomponents, and the Create\n"
    "Lesser Conduit and SpellSpace Scoped Meld flows; the stale SpellSpace active-scope, reset and version claims\n"
    "are corrected. Citations the change moved were remapped by symbol (conduit.py, conduit_ward.py,\n"
    "aetheric_frame.py; three ward and two frame citations that already pointed elsewhere were corrected), and\n"
    "`spell_space_pool.py` joined the core map. Known and not changed: a live-creation probe through a space can\n"
    "miss a disposal-bearing `many` held in the space's store (Creations and SpellSpace, Failure Modes).\n"
    "\n"
    "2026-09-27 meld entry cache by name and class:",
)

doc.write_bytes(text.encode("utf-8"))
print("edited", doc, len(text.splitlines()))
