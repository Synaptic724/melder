"""Promote the scope_exit_dispose_2026_09_27 patch into src_architecture.md (0.2.8203).

Every edit is an exact-match anchor that must occur once; the script refuses to write otherwise.
Usage: python edit_src_architecture.py <doc path> <verified_at UTC>
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


# 1. Boundary list.
swap(
    "- `Conduit.create_lesser_conduit(...)` for child scopes.\n",
    "- `Conduit.create_lesser_conduit(...)` for child scopes.\n"
    "- `Conduit.enter_lesser_conduit(...)` (0.2.8203) for a child scope used as a `with` block. `with` on any\n"
    "  Conduit is a dispose scope: at block exit a lesser returns to its root's pool and a root is torn down, and\n"
    "  disposal failures are raised after that. Spellbook, Aether, AethericFrame, ConduitWard and SpellIndex keep\n"
    "  `with` as a lock. `Cleanable.using_cleanup()` and `async_using_cleanup()` (every Cleanable) let cleanup\n"
    "  errors propagate.\n",
)

# 2. Create Lesser Conduit, step 5.
swap(
    "5. On named return, complete disposal/descendants, retire records and named discovery, clear the name\n"
    "   and detach, restore temporary hooks, then publish the ready shell idle. Anonymous leaf return\n"
    "   checks the name once and performs no Cloud/recorder/Nexus work.\n",
    "5. Pool return (`cleanup()`, or the exit of a `with` block over the lesser) disposes descendants first,\n"
    "   then the lesser's SpellSpaces, then its own store. A named scope then retires records and named\n"
    "   discovery and clears its name; an anonymous leaf checks the name once and performs no\n"
    "   Cloud/recorder/Nexus work. Both detach, restore temporary hooks and publish the ready shell idle.\n"
    "   Disposal failures do not stop the return: they are raised as one ExceptionGroup once the shell is\n"
    "   back in its pool (0.2.8203). A descendant still attached after failing, or a failed named\n"
    "   retirement, keeps the lesser attached for retry. A second soft cleanup of a pooled shell does nothing.\n",
)

# 3. SpellSpace Usage.
swap(
    "1. `conduit.enter_spellspace()` creates and activates SpellSpace.\n"
    "2. `SpellSpace.meld(...)` enforces active scope and delegates to Conduit.\n"
    "3. `SpellSpace.reset()` clears spellspace-scoped instances and bumps version.\n",
    "1. `conduit.enter_spellspace()` takes a pooled space, clears its released flag and pushes it on the\n"
    "   calling thread's stack; `create_spellspace()` takes one for manual use and registers it with the conduit.\n"
    "2. `SpellSpace.meld(...)` and `purge(...)` refuse a released space with SpellSpaceScopeError, then run\n"
    "   through the space's own SpellSpaceMeld door. There is no active-scope check, no `reset()` and no version\n"
    "   (corrected 2026-09-27; this sequence used to name all three).\n"
    "3. The block exit pops the space (LIFO-checked), disposes its own store, restores temporary hooks and\n"
    "   releases it to the pool, which sets the released flag; manual `cleanup()` does the same and unregisters\n"
    "   it. A disposal failure is raised after the release (0.2.8203). A space released or destroyed inside its\n"
    "   own block only leaves the stack at exit, and a second cleanup of a released space does nothing.\n",
)

# 4. Cleanup sequence, item 1 and item 7.
swap(
    "1. `Conduit.cleanup()` fires hooks, tears down Meld, ConduitWard and Creations,\n"
    "   clears hooks, logger last.\n",
    "1. `Conduit.cleanup()` on a root, and `permanent_cleanup()` on a lesser, fire hooks and tear down\n"
    "   Meld, ConduitWard (the lesser lineage), SpellSpaces and Creations, clear hooks, logger last, and\n"
    "   then raise the collected disposal failures as one ExceptionGroup (0.2.8203; before, they were only\n"
    "   logged). On a lesser, `cleanup()` is the pool return of the Create Lesser Conduit sequence.\n",
)
swap(
    "   `ExceptionGroup` - it is the one teardown here that AGGREGATES failures\n"
    "   rather than stopping at the first, so a single bad object cannot strand the\n"
    "   rest of the scope. Since 0.2.80 that holds per method too: every declared method\n"
    "   runs even after one fails, and each failure is chained from what the method raised.\n",
    "   `ExceptionGroup` - it AGGREGATES failures rather than stopping at the first, so a\n"
    "   single bad object cannot strand the rest of the scope. Since 0.2.80 that holds per\n"
    "   method too: every declared method runs even after one fails, and each failure is\n"
    "   chained from what the method raised. Since 0.2.8203 the Conduit, ConduitWard and\n"
    "   SpellSpace teardowns above it finish the same way and raise its groups last.\n",
)

# 5. Operational invariant for the scope exits (newest first).
swap(
    "## Operational Invariants\n- Disposal failures (2026-09-27, 0.2.80):",
    "## Operational Invariants\n"
    "- Scope exits finish, then raise (2026-09-27, 0.2.8203): `with conduit:` disposes - `Conduit.__enter__`\n"
    "  returns the conduit and takes no lock, `__exit__` calls `cleanup()` - so a lesser returns to its root's\n"
    "  pool and a root is torn down; Spellbook, Aether, AethericFrame, ConduitWard and SpellIndex keep `with` as a\n"
    "  lock. Every scope exit (SpellSpace managed exit and manual cleanup, lesser pool return, permanent teardown)\n"
    "  runs all its steps when a disposal method raises, then raises the collected failures as one\n"
    "  ExceptionGroup. That is safe because Creations swaps a store empty before any disposal method runs, so a\n"
    "  failed method leaves nothing behind to retry. A lesser's pool return disposes descendants, then\n"
    "  SpellSpaces, then its own store - the order permanent teardown already used; a descendant still attached\n"
    "  after failing, or a failed named retirement, keeps the lesser attached and out of the pool for retry. Soft\n"
    "  cleanup of a pooled lesser or a released SpellSpace is a no-op, so no scope is pooled twice and two\n"
    "  acquisitions never share one object. A SpellSpace carries one lease flag: pool release sets it,\n"
    "  acquisition clears it, and a released space refuses meld and purge. The flag's two writes per cycle are\n"
    "  paid back on the same path (inline managed exit and stack push, one idle-deque read, no SpellSpace sweep\n"
    "  call when none is open), so a scope cycle costs no more than before on 3.14t and the GIL build (measured\n"
    "  2026-09-27). A pooled lesser handle is not checked on `Conduit.meld`, the hottest door: using a scope\n"
    "  after cleanup stays a caller contract violation there.\n"
    "  EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit.__exit__`, `Conduit._prepare_for_pool`,\n"
    "  `Conduit._permanent_cleanup`, `src/melder/aether/conduit/spell_space/spell_space.py:SpellSpace.__exit__`,\n"
    "  `SpellSpace.cleanup`, `src/melder/aether/conduit/spell_space/spell_space_pool.py:SpellSpacePool.release`\n"
    "  and `src/melder/aether/conduit/conduit_ward/conduit_ward.py:ConduitWard._cleanup_children_for_pool`.\n"
    "- Disposal failures (2026-09-27, 0.2.80):",
)

# 6. The stale active-spellspace invariant.
swap(
    "- SpellSpace can only meld when it is the active spellspace for a Conduit.\n",
    "- A SpellSpace melds and purges only while leased: a space released to its pool refuses both with\n"
    "  SpellSpaceScopeError, and a destroyed one raises the cleaned RuntimeError. There is no active-scope\n"
    "  check - a leased space melds whether or not it is the top of its thread's stack (corrected 2026-09-27:\n"
    "  this line claimed an active-spellspace rule the source never had).\n"
    "  EVIDENCE: `src/melder/aether/conduit/spell_space/spell_space.py:SpellSpace.meld` and\n"
    "  `SpellSpace._refuse_released`.\n",
)

# 7. Failure modes.
swap(
    "  retain ownership for retry and never publish idle; failed descendants prevent ancestor return.\n",
    "  retain ownership for retry and never publish idle; a descendant that could not finish its own return\n"
    "  prevents ancestor return (one that finished but raised disposal failures does not, 0.2.8203).\n",
)
swap(
    "- SpellSpaceScopeError if a non-active SpellSpace is used for meld.\n",
    "- SpellSpaceScopeError when a SpellSpace released to its pool is used for meld or purge (0.2.8203), and\n"
    "  when a managed exit is not the top of the calling thread's stack (\"stack corruption\"). A space released\n"
    "  or destroyed inside its own block leaves the stack without error. Before 0.2.8203 a kept handle melded\n"
    "  into the idle shell and the next lease was served what it built, and a lesser cleaned inside its own\n"
    "  managed SpellSpace made that block's exit raise \"stack corruption\".\n"
    "  EVIDENCE: `src/melder/aether/conduit/spell_space/spell_space.py:SpellSpace._refuse_released` and\n"
    "  `src/melder/aether/conduit/spell_space/spell_space_thread_state.py:SpellSpaceThreadState.pop_expected`.\n",
)
swap(
    "- Cleanup errors are logged; Creations may raise ExceptionGroup. Since 0.2.80 it holds one error per failing\n"
    "  disposal method, each chained from what that method raised; before, an object's first failure ended its\n"
    "  disposal and the original exception was dropped.\n",
    "- Disposal failures are raised, not logged (0.2.8203): a scope exit or teardown finishes - the scope is\n"
    "  pooled or destroyed - and then raises one ExceptionGroup of the Creations groups it collected (\"Lesser\n"
    "  conduit returned to its pool with disposal failures.\", \"Conduit torn down with disposal failures.\",\n"
    "  \"Lesser conduits torn down with disposal failures.\"); a SpellSpace exit raises its store's group. When the\n"
    "  `with` block raised too, the group rises with the block's exception as its `__context__`. Other teardown\n"
    "  errors (gate unregistration, record retirement, Nexus publication, Spellbook and pool cleanup) stay\n"
    "  logged, and frame teardown logs a failing conduit and keeps going. Each Creations group holds one error\n"
    "  per failing disposal method, chained from what that method raised (0.2.80); before 0.2.80 an object's\n"
    "  first failure ended its disposal and the original exception was dropped, and before 0.2.8203 conduit\n"
    "  paths only logged these groups.\n"
    "  EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit._permanent_cleanup`,\n"
    "  `src/melder/aether/conduit/conduit_ward/conduit_ward.py:ConduitWard.cleanup` and\n"
    "  `src/melder/aether/aetheric_frame/aetheric_frame.py:AethericFrame._cleanup_data_structures`.\n"
    "- `with conduit:` no longer holds the conduit lock (Breaking, 0.2.8203): code that used it as a lock now\n"
    "  disposes the scope at block exit. `Cleanable.using_cleanup()` and `async_using_cleanup()` let cleanup\n"
    "  errors propagate (0.2.8203; they used to be swallowed).\n",
)

# 8. Diagram.
swap(
    "### ASCII Context Diagram (C4)\n",
    "### Scope Exit and Pool Return\n"
    "```text\n"
    "with lesser: / lesser.cleanup():\n"
    "  descendants -> SpellSpaces -> own store -> retire name | detach -> hooks -> pool -> raise failures\n"
    "with conduit.enter_spellspace() as space:\n"
    "  pop (LIFO) -> dispose space store -> reset hooks -> release (released=True) -> raise failures\n"
    "  released space: meld / purge -> SpellSpaceScopeError; the next acquisition clears the flag\n"
    "with root: / root.cleanup():\n"
    "  ward (lesser lineage) -> SpellSpaces -> stores -> hooks -> logger -> raise failures\n"
    "```\n"
    "\n"
    "```mermaid\n"
    "flowchart LR\n"
    "  X[with block exit or cleanup] --> K{Scope}\n"
    "  K -->|lesser| D[Descendants return first]\n"
    "  D --> S[SpellSpaces, then own store]\n"
    "  S --> P[Retire or detach, reset hooks, back to pool]\n"
    "  K -->|root| T[Permanent teardown, logger last]\n"
    "  K -->|SpellSpace| R[Dispose store, reset hooks, release sets the flag]\n"
    "  P --> E[Raise the collected disposal failures]\n"
    "  T --> E\n"
    "  R --> E\n"
    "  R -.->|kept handle| F[meld or purge refused]\n"
    "```\n"
    "\n"
    "### ASCII Context Diagram (C4)\n",
)

# 9. Information sources.
swap(
    "- `src/melder/aether/conduit/creations/creations.py`\n",
    "- `src/melder/aether/conduit/creations/creations.py`\n"
    "- `src/melder/aether/conduit/conduit_ward/conduit_ward.py`\n"
    "- `src/melder/aether/conduit/spell_space/spell_space.py`\n"
    "- `src/melder/aether/conduit/spell_space/spell_space_pool.py`\n"
    "- `src/melder/aether/conduit/spell_space/spell_space_thread_state.py`\n"
    "- `src/melder/aether/conduit/meld/spellspace_meld.py`\n"
    "- `src/melder/utilities/general_base/cleanable.py`\n"
    "- `src/melder/utilities/custom_exceptions/spell_space_scope_error.py`\n",
)

# 10. C1 remeasure.
def remeasure(path: str, old_end: int, old_at: str, new_end: int) -> None:
    swap(
        f"- path: `{path}`\n  start_line: 1\n  end_line: {old_end}\n  loc: {old_end}\n  verified_at: {old_at}\n",
        f"- path: `{path}`\n  start_line: 1\n  end_line: {new_end}\n  loc: {new_end}\n  verified_at: {verified_at}\n",
    )

remeasure("src/melder/aether/aetheric_frame/aetheric_frame.py", 1136, "2026-09-26T20:10:34Z", 1145)
remeasure("src/melder/aether/conduit/conduit.py", 6897, "2026-09-26T20:10:34Z", 7102)
remeasure("src/melder/aether/conduit/conduit_ward/conduit_ward.py", 3813, "2026-09-27T11:46:59Z", 3872)
remeasure("src/melder/aether/conduit/spell_space/spell_space.py", 650, "2026-09-26T20:10:34Z", 792)
remeasure("src/melder/utilities/general_base/cleanable.py", 420, "2026-09-26T20:10:34Z", 429)
swap(
    f"- path: `src/melder/aether/conduit/spell_space/spell_space.py`\n  start_line: 1\n  end_line: 792\n"
    f"  loc: 792\n  verified_at: {verified_at}\n  note: spellspace scoping.\n",
    f"- path: `src/melder/aether/conduit/spell_space/spell_space.py`\n  start_line: 1\n  end_line: 792\n"
    f"  loc: 792\n  verified_at: {verified_at}\n  note: spellspace scoping; lease flag and finished exits.\n"
    f"- path: `src/melder/aether/conduit/spell_space/spell_space_pool.py`\n  start_line: 1\n  end_line: 301\n"
    f"  loc: 301\n  verified_at: {verified_at}\n  note: spellspace pool; release sets and acquisition clears the lease flag.\n"
    f"- path: `src/melder/aether/conduit/spell_space/spell_space_thread_state.py`\n  start_line: 1\n  end_line: 328\n"
    f"  loc: 328\n  verified_at: {verified_at}\n  note: per-thread managed spellspace stack.\n",
)

# 11. Handoff summary.
swap(
    "## Context / Handoff Summary\n\n2026-09-27 meld entry cache by name and class:",
    "## Context / Handoff Summary\n\n"
    "2026-09-27 scope exits (0.2.8203): `with conduit:` disposes the scope instead of holding the conduit lock, and\n"
    "`Conduit.enter_lesser_conduit()` makes a lesser for such a block. Every scope exit - SpellSpace managed exit\n"
    "and manual cleanup, lesser pool return, permanent teardown - finishes when a disposal method fails and then\n"
    "raises the failures as one ExceptionGroup; a lesser's pool return disposes its descendants first; a second\n"
    "soft cleanup does nothing; a released SpellSpace refuses meld and purge; `using_cleanup()` lets cleanup\n"
    "errors propagate. The boundary list, the lesser, SpellSpace and cleanup sequences, the operational\n"
    "invariants (the stale active-spellspace line corrected), the failure modes, a diagram and the code map carry\n"
    "it; the component map carries the per-method contracts. Still open: this document's `## Indexing` section\n"
    "names maintenance tool paths, which a reader outside the repository cannot resolve (pre-existing).\n"
    "\n"
    "2026-09-27 meld entry cache by name and class:",
)

doc.write_bytes(text.encode("utf-8"))
print("edited", doc, len(text.splitlines()))
