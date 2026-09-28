"""Scope-exit dispose lane, part 2: SpellSpace lease flag, released refusal, finished exits. melder_0, 2026-09-27."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from source_edit import insert_after_def, replace_block, replace_def

ROOT = sys.argv[1]
SPACE = os.path.join(ROOT, "src/melder/aether/conduit/spell_space/spell_space.py")

print("spell_space.py")
replace_block(SPACE, """
from typing import TYPE_CHECKING, Optional, Type, Union, ClassVar
""", """
from typing import TYPE_CHECKING, NoReturn, Optional, Type, Union, ClassVar
""")
replace_block(SPACE, """
from melder.aether.conduit.meld.spellspace_meld import SpellSpaceMeld
""", """
from melder.aether.conduit.meld.spellspace_meld import SpellSpaceMeld
from melder.utilities.custom_exceptions.spell_space_scope_error import SpellSpaceScopeError
""")
replace_block(SPACE, """
        - One managed activation per acquisition: after `__exit__` recycles
          the space back to the pool, re-entering the same object is a caller
          contract violation (the trusted-private-caller posture documented
          on `SpellSpacePool.release`); LIFO validation in `pop_expected`
          fails fast on the common misuse shapes.
""", """
        - One managed activation per acquisition: after `__exit__` recycles
          the space back to the pool, re-entering the same object is a caller
          contract violation (the trusted-private-caller posture documented
          on `SpellSpacePool.release`); LIFO validation in `pop_expected`
          fails fast on the common misuse shapes.
        - Carries one lease flag, `_released`: the pool sets it on release and
          clears it on acquisition, and a released space refuses `meld` and
          `purge` with SpellSpaceScopeError. After permanent cleanup it stays
          True as a documented tombstone.
        - Every exit finishes its pool return (or destroy) when a disposal
          method fails - the store is emptied before any method runs - and then
          raises the disposal ExceptionGroup.
""")
replace_block(SPACE, """
        This is how the DGR gives a caller an EXPLICIT, nestable resolution
        window without leaking conduit-wide state into it: instances resolved as
        `unique_per_spell_space` live and die with the space, and `reset()` clears
        them and bumps a version so a recycled space cannot serve stale
        instances. Making the space its own context manager (trivial `__enter__`,
""", """
        This is how the DGR gives a caller an EXPLICIT, nestable resolution
        window without leaking conduit-wide state into it: instances resolved as
        `unique_per_spell_space` live and die with the space - every exit clears
        them before the space goes back to its pool, and a released space
        refuses `meld`, so a recycled shell cannot serve an object built through
        a stale handle. Making the space its own context manager (trivial `__enter__`,
""")
replace_block(SPACE, """
        access: public. Explicit request scope for Existence.unique_per_spell_space. Enter via
        conduit.enter_spellspace(); meld only while it is the ACTIVE spellspace; reset() clears
        spellspace-scoped instances and bumps the version.
""", """
        access: public. Explicit request scope for Existence.unique_per_spell_space. Enter via
        conduit.enter_spellspace(); the block exit clears spellspace-scoped instances and returns
        the space to its pool; a released space refuses meld and purge.
""")
replace_block(SPACE, """
        "_spellspace_stack_state",
        "_permanent_cleanup_requested",
    ]
""", """
        "_spellspace_stack_state",
        "_permanent_cleanup_requested",
        "_released",
    ]
""")
replace_block(SPACE, """
        Contract:
            - Builds a POOLED, REUSABLE scope object. Its identity is versioned rather
              than object-based precisely so the pool can recycle it: a handle held
              across a recycle boundary fails its active-scope check instead of
              silently attaching to a different request.
""", """
        Contract:
            - Builds a POOLED, REUSABLE scope object. It starts leased (`_released`
              False); the pool sets the flag on release and clears it on
              acquisition, and a released space refuses `meld` and `purge`, so a
              handle held across a recycle boundary fails loudly instead of
              melding into an idle shell.
""")
replace_block(SPACE, """
        Lifecycle / Cleanup:
            Reset returns it to the pool and bumps its version; permanent cleanup is
            what actually destroys it.
""", """
        Lifecycle / Cleanup:
            Recycling clears its store and returns it to the pool; permanent cleanup
            is what actually destroys it.
""")
replace_block(SPACE, """
        self._permanent_cleanup_requested: bool = False
""", """
        self._permanent_cleanup_requested: bool = False
        self._released: bool = False
""")
replace_def(SPACE, ["SpellSpace"], "__exit__", r'''
    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_value: Optional[BaseException],
            traceback: Optional[TracebackType],
    ) -> None:
        """
        Pop this scope off the per-thread stack and recycle it.

        Contract:
            - Validates LIFO integrity: this space must be the current
              top-of-stack scope for the calling thread (nested scopes must
              unwind innermost-first).
            - Recycles through the managed pooled fast lane, which clears
              spellspace-local creations before pool return so scope teardown
              stays deterministic and owner-driven. The return finishes even
              when a disposal method fails; the disposal ExceptionGroup then
              propagates, with the block's exception as its context when the
              block raised.
            - A space already released or destroyed inside the block (an
              explicit `cleanup()`, or its conduit's pool return or teardown)
              only leaves the stack and returns: its store was already
              disposed.
            - The common lane of `recycle_from_managed_context` (untracked, no
              permanent teardown requested) runs inline here, saving a call per
              scope; every other lane goes through that method.
            - Runs on exceptions too, exactly like the former wrapper.
            - After exit this object belongs to the pool again; re-entering
              it without a fresh `enter_spellspace()` acquisition is a caller
              contract violation.

        Raises:
            SpellSpaceScopeError:
                If this space is not the calling thread's active top-of-stack
                scope.
            ExceptionGroup:
                Disposal failures, raised after the space is back in its pool.

        Returns:
            None.
        """
        if self._released:
            self._leave_after_early_release()
            return None
        self._spellspace_stack_state.pop_expected(self)
        # Hot path (one exit per managed scope): the common lane of
        # `recycle_from_managed_context`, inlined to save a call frame and a
        # second read of the lease flag. Keep the two in step.
        if self._permanent_cleanup_requested or self._registry_tracked:
            self.cleanup()
            return None
        try:
            self._creations.reset_for_pool_unlocked()
        finally:
            # Finish the return even when a disposal method failed: the store
            # was swapped empty before any method ran, so the shell is clean.
            if self._meld._meld_hooks_modified:
                self._meld._reset_pooled_meld_hooks()
            self._spellspace_pool.release(self)
        return None
''', must_contain=["pop_expected(self)", "recycle_from_managed_context()"])
replace_def(SPACE, ["SpellSpace"], "cleanup", r'''
    def cleanup(self) -> None:
        """
        Cleanup this spellspace through either the reusable or permanent lane.

        Contract:
            - Normal cleanup returns this spellspace to the conduit-local pool
              after reusable cleanup. A space that is already released is left
              as it is, so a second cleanup never pools it twice.
            - `permanent_cleanup()` forces the destructive lane even when a
              pool is attached.
            - Either lane finishes when a disposal method fails (the store is
              emptied before any method runs), then the disposal ExceptionGroup
              propagates.

        Raises:
            ExceptionGroup: Disposal failures, after the space is pooled or destroyed.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            if self._permanent_cleanup_requested:
                self._cleanup_for_destroy()
                return
            if self._released:
                return
            try:
                self._cleanup_for_pool_reuse()
            finally:
                self._spellspace_pool.release(self)
''', must_contain=["self._cleanup_for_pool_reuse()", "self._spellspace_pool.release(self)"])
replace_def(SPACE, ["SpellSpace"], "recycle_from_managed_context", r'''
    def recycle_from_managed_context(self) -> None:
        """
        Recycle one managed pooled spellspace through the fast common lane.

        Purpose:
            Avoid the generic cleanup branch work on the common
            `enter_spellspace()` managed exit path, where the spellspace is
            untracked in the registry and is expected to return directly to the
            conduit-local pool after clearing only spellspace-local state.

        Contract:
            - Valid only for live managed spellspaces acquired through the
              untracked pool path; a space that is already released (or
              destroyed) returns at once.
            - Falls back to the generic cleanup entrypoint when permanent
              teardown was requested or the spellspace is registry-tracked.
            - Clears spellspace-local creations before returning this
              spellspace to the pool.
            - Keeps collaborator references intact for later reuse, restoring
              temporary hooks after disposal and before idle publication.
            - Finishes the hook reset and pool release when a disposal method
              fails (the store was swapped empty first), then the disposal
              ExceptionGroup propagates.

        Threading / Concurrency:
            - This lane runs without the spellspace `RLock` because managed
              spellspaces are thread-confined by construction: the pool's
              deque pop hands the object to exactly one thread, the object
              lives only on that thread's `SpellSpaceThreadState` stack, and
              `pop_expected(...)` validates LIFO ownership before this method
              runs. The pool's deque append on release is the hand-off point
              to the next acquiring thread.
            - The spellspace-local clear uses
              `Creations.reset_for_pool_unlocked()`: the same thread
              confinement that justifies skipping the spellspace lock also
              covers the store's internal lock on this lane. The clear remains
              explicit and immediate, not deferred; disposal-bearing stores
              still fall back to the fully locked teardown flow inside that
              method.
            - Concurrent external `cleanup()` / `permanent_cleanup()` against
              an in-flight managed spellspace is a caller contract violation
              (the object is not idle in the pool and not registry-tracked),
              matching the trusted-private-caller posture documented on
              `SpellSpacePool.release(...)`.

        Raises:
            ExceptionGroup: Disposal failures, after the space is back in its pool.

        Returns:
            None.
        """
        if self._released:
            return
        if self._permanent_cleanup_requested or self._registry_tracked:
            self.cleanup()
            return
        # Common unchanged path is lock-free by the confinement contract above;
        # a temporary hook map uses the existing Meld lock only while resetting.
        # The unlocked variant is valid here precisely because this lane is
        # the confinement-guaranteed managed exit; the explicit
        # spellspace-local clear still happens before pool return so scope
        # teardown stays deterministic and owner-driven.
        try:
            self._creations.reset_for_pool_unlocked()
        finally:
            # Finish the return even when a disposal method failed: the store
            # was swapped empty before any method ran, so the shell is clean.
            if self._meld._meld_hooks_modified:
                self._meld._reset_pooled_meld_hooks()
            self._spellspace_pool.release(self)
''', must_contain=["reset_for_pool_unlocked()", "if self._cleaned:"])
replace_def(SPACE, ["SpellSpace"], "_cleanup_for_pool_reuse", r'''
    def _cleanup_for_pool_reuse(self) -> None:
        """
        Clear spellspace-scoped runtime state so this object can be retained.

        Contract:
            - Clears spellspace-scoped creations for this spellspace id.
            - Removes this spellspace from the active registry only when the
              current lifecycle path registered it there.
            - Still tolerates direct/manual registry insertion paths by
              discarding the spellspace when it is currently present.
            - Keeps collaborator references intact for later reuse.
            - Restores temporary Meld hooks after disposal, before idle publication.
            - Finishes the registry discard and hook reset when a disposal method
              fails; the disposal ExceptionGroup then propagates.
        """
        try:
            self._creations.reset_for_pool()
        finally:
            if self._registry_tracked or self in self._spellspace_registry:
                self._spellspace_registry.discard(self)
                self._registry_tracked = False
            self._permanent_cleanup_requested = False
            if self._meld._meld_hooks_modified:
                self._meld._reset_pooled_meld_hooks()
''', must_contain=["self._creations.reset_for_pool()"])
replace_def(SPACE, ["SpellSpace"], "_cleanup_for_destroy", r'''
    def _cleanup_for_destroy(self) -> None:
        """
        Permanently destroy this spellspace and release collaborator references.

        Contract:
            - Clears spellspace-scoped creations before dropping references.
            - Removes this spellspace from the current registry when tracked.
            - Still tolerates direct/manual registry insertion paths by
              discarding the spellspace when it is currently present.
            - Deletes the pool reference as part of final teardown.
            - Cleans the owned Meld before dropping it, releasing both hook references.
            - Every step runs when a disposal method fails; the disposal
              ExceptionGroup then propagates.
            - `_released` is set and kept as a documented tombstone (True), so a
              later `meld`, `purge` or block exit reads it instead of hitting a
              deleted attribute; `_id` and `_lock` are kept as before.
            - Removes this space from the top of the destroying thread's
              spellspace stack when it is there (destroyed inside its own
              managed block), before the thread-state reference is deleted, so
              later scopes on that thread keep a consistent stack.
        """
        self._released = True
        try:
            self._creations.cleanup()
        finally:
            self._meld.cleanup()
            if self._registry_tracked or self in self._spellspace_registry:
                self._spellspace_registry.discard(self)
            self._spellspace_stack_state.discard_expected(self)
            self._cleaned = True
            del self._registry_tracked
            del self._spellspace_registry
            del self._owner_conduit_id
            del self._meld
            del self._creations
            del self._owner_conduit_creations
            del self._spellspace_pool
            del self._spellspace_stack_state
            del self._permanent_cleanup_requested
''', must_contain=["self._creations.cleanup()", "del self._permanent_cleanup_requested"])
insert_after_def(SPACE, ["SpellSpace"], "_cleanup_for_destroy", r'''
    def _leave_after_early_release(self) -> None:
        """
        Internal

        End a managed block whose space was released or destroyed inside it.

        Contract:
            - A destroyed space already left the stack top in
              `_cleanup_for_destroy`; there is nothing to do.
            - A released space drops itself from the top of the calling thread's
              stack when it is still there (an explicit cleanup inside the
              block); its conduit's pool return has already drained the stack
              otherwise. Nothing is disposed again and nothing is pooled twice.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._spellspace_stack_state.discard_expected(self)

    def _refuse_released(self) -> NoReturn:
        """
        Internal

        Refuse use of a space that is not leased.

        Contract:
            - A destroyed space raises the standard cleaned RuntimeError.
            - A space released to its pool raises SpellSpaceScopeError naming the
              space and how to get a live one.

        Raises:
            RuntimeError: If this space was permanently cleaned.
            SpellSpaceScopeError: If this space was released to its pool.
        """
        self.check_cleaned()
        raise SpellSpaceScopeError(
            f"SpellSpace {self._id} was released to its pool and cannot meld or purge. "
            "Use a space only inside its `with conduit.enter_spellspace()` block, or before "
            "cleanup() for a create_spellspace() space; acquire a new one to continue."
        )
''')
replace_block(SPACE, """
            - Propagates runtime failures from the meld pipeline unchanged.
""", """
            - Propagates runtime failures from the meld pipeline unchanged.
            - A space released to its pool raises SpellSpaceScopeError before any
              lookup; a permanently cleaned one raises RuntimeError.
""")
replace_block(SPACE, """
        # Warm lanes (id 2026-09-26, name/class 2026-09-27): the scoped calls `spell_id=...` alone,
""", """
        if self._released:
            self._refuse_released()
        # Warm lanes (id 2026-09-26, name/class 2026-09-27): the scoped calls `spell_id=...` alone,
""")
replace_block(SPACE, """
            RuntimeError:
                If permanently cleaned or the target has a broader lifetime.
""", """
            RuntimeError:
                If permanently cleaned or the target has a broader lifetime.
            SpellSpaceScopeError:
                If this space was released to its pool.
""")
replace_block(SPACE, """
            Managed thread confinement and pool ownership rules remain unchanged;
            a returned/recycled space must not be used through an old reference.
        \"\"\"
        self.check_cleaned()
        if spell is not None and spell_id is not None:
            raise ValueError("purge accepts either `spell` or `spell_id`, not both.")
""", """
            Managed thread confinement and pool ownership rules remain unchanged;
            a returned/recycled space refuses purge until it is acquired again.
        \"\"\"
        if self._released:
            self._refuse_released()
        if spell is not None and spell_id is not None:
            raise ValueError("purge accepts either `spell` or `spell_id`, not both.")
""")
print("part 2 done")
