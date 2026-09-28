"""Scope-exit dispose lane, part 1: cleanup contexts, SpellSpace thread state and pool. melder_0, 2026-09-27."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from source_edit import insert_after_def, replace_block, replace_def

ROOT = sys.argv[1]
CLEANABLE = os.path.join(ROOT, "src/melder/utilities/general_base/cleanable.py")
THREAD_STATE = os.path.join(ROOT, "src/melder/aether/conduit/spell_space/spell_space_thread_state.py")
POOL = os.path.join(ROOT, "src/melder/aether/conduit/spell_space/spell_space_pool.py")

print("cleanable.py")
replace_block(CLEANABLE, """
        Contract:
            - Does not rely on the owner's own `__enter__` / `__exit__`.
            - Calls `owner.cleanup()` at most once.
            - Drops the strong owner reference after exit.
            - Never suppresses exceptions raised by the caller's block.
""", """
        Contract:
            - Does not rely on the owner's own `__enter__` / `__exit__`.
            - Calls `owner.cleanup()` at most once.
            - Drops the strong owner reference before that call, so nothing is
              leaked even when cleanup raises.
            - Never suppresses exceptions raised by the caller's block, and lets an
              exception raised by `owner.cleanup()` propagate: with a failing block
              it rises with the block's exception as its context.
""")
replace_def(CLEANABLE, ["Cleanable", "_CleanupContext"], "__exit__", r'''
        def __exit__(
                self,
                exc_type: Optional[Type[BaseException]],
                exc: Optional[BaseException],
                tb: Optional[TracebackType],
        ) -> Literal[False]:
            """
            Exit the cleanup helper context and trigger owner cleanup once.

            Contract:
                - Drops the strong owner reference first, then calls
                  `owner.cleanup()` AT MOST ONCE across repeated exits.
                - An exception raised by `owner.cleanup()` propagates (changed
                  0.2.8201; it used to be swallowed). When the block raised too,
                  it rises with the block's exception as its `__context__`,
                  Python's rule for an error raised in `__exit__`.
                - Never suppresses exceptions from the caller's `with` block.
                - Releases the context lock in a `finally`.

            Args:
                exc_type:
                    Exception type raised in the `with` block, or None.
                exc:
                    Exception instance raised in the `with` block, or None.
                tb:
                    Traceback for the `with`-block exception, or None.

            Returns:
                Literal[False]:
                    Always False so caller exceptions are never suppressed.

            Raises:
                Exception: Whatever `owner.cleanup()` raised.
            """
            # Guarantee cleanup only once; drop the reference first so nothing is
            # leaked when cleanup raises.
            try:
                owner = self._owner
                self._owner = None
                if owner is not None and not self._cleaned:
                    self._cleaned = True
                    owner.cleanup()

                # Do NOT suppress user exceptions; a cleanup error propagates.
                return False
            finally:
                self._lock.release()
''', must_contain=["except Exception:", "owner.cleanup()"])
replace_block(CLEANABLE, """
        Contract:
            - Does not rely on the owner's own `__aenter__` / `__aexit__`.
            - Awaits `owner.async_cleanup()` at most once.
            - Drops the strong owner reference after exit.
            - Never suppresses exceptions raised by the caller's block.
""", """
        Contract:
            - Does not rely on the owner's own `__aenter__` / `__aexit__`.
            - Awaits `owner.async_cleanup()` at most once.
            - Drops the strong owner reference before that await, so nothing is
              leaked even when async cleanup raises.
            - Never suppresses exceptions raised by the caller's block, and lets an
              exception raised by `owner.async_cleanup()` propagate.
""")
replace_def(CLEANABLE, ["Cleanable", "_AsyncCleanupContext"], "__aexit__", r'''
        async def __aexit__(
                self,
                exc_type: Optional[Type[BaseException]],
                exc: Optional[BaseException],
                tb: Optional[TracebackType],
        ) -> Literal[False]:
            """
            Exit the async cleanup helper context and await owner cleanup once.

            Contract:
                - Drops the strong owner reference first, then awaits
                  `owner.async_cleanup()` AT MOST ONCE across repeated exits.
                - An exception raised by `owner.async_cleanup()` propagates
                  (changed 0.2.8201; it used to be swallowed), chained to the
                  block's exception when the block raised too.
                - Never suppresses exceptions from the caller's `async with`
                  block.
                - Releases the context lock in a `finally`.

            Returns:
                Literal[False]:
                    Always False so caller exceptions are never suppressed.

            Raises:
                Exception: Whatever `owner.async_cleanup()` raised.
            """
            try:
                owner = self._owner
                self._owner = None
                if owner is not None and not self._cleaned:
                    self._cleaned = True
                    await owner.async_cleanup()

                # Do NOT suppress user exceptions; a cleanup error propagates.
                return False
            finally:
                self._lock.release()
''', must_contain=["except Exception:", "await owner.async_cleanup()"])
replace_block(CLEANABLE, """
        Contract:
        - Independent of any context-manager behavior implemented by the owner.
        - Intended for callers that want deterministic cleanup without relying
          on the object's own `__enter__` / `__exit__`.

        Returns:
            Cleanable._CleanupContext:
""", """
        Contract:
        - Independent of any context-manager behavior implemented by the owner.
        - Intended for callers that want deterministic cleanup without relying
          on the object's own `__enter__` / `__exit__`.
        - Cleanup runs at most once on exit and its errors propagate; the block's
          own exception is never suppressed.

        Returns:
            Cleanable._CleanupContext:
""")

print("spell_space_thread_state.py")
insert_after_def(THREAD_STATE, ["SpellSpaceThreadState"], "pop_expected", r'''
    def discard_expected(self, expected: Any) -> bool:
        """
        Remove `expected` from the top of the current thread's stack if it is there.

        Purpose:
            Let a managed spellspace that was already released inside its own
            `with` block (an explicit cleanup, or its conduit's pool return)
            leave that block without a stack error.

        Contract:
            - Pops only when `expected` is the top entry; otherwise changes
              nothing. Never raises.

        Args:
            expected:
                Spellspace object whose block is ending.

        Returns:
            bool: True when the entry was removed.
        """
        stack = self._local.spellspace_stack
        if stack and stack[-1] is expected:
            stack.pop()
            return True
        return False
''')

print("spell_space_pool.py")
replace_block(POOL, """
    Lifecycle / Cleanup:
        Owned by one conduit and torn down with it. Recycling a spellspace is
        NOT destruction - `reset()` clears spellspace-scoped instances and bumps
        the version, while the permanent cleanup lane is what actually destroys
        one.
""", """
    Lifecycle / Cleanup:
        Owned by one conduit and torn down with it. Recycling a spellspace is
        NOT destruction - the scope's own store is cleared and the space is
        released back here, while the permanent cleanup lane is what actually
        destroys one.
""")
replace_block(POOL, """
    System Context:
        Pooling a scope object is only safe because scope identity is VERSIONED
        rather than object-identity based. A recycled spellspace bumps its
        version on reset, so any stale handle held across the recycle boundary
        fails its active-scope check instead of silently melding into a reused
        shell that now belongs to a different request. Without that versioning
        this pool would be a correctness hazard rather than an optimization -
        which is the same reasoning that makes `pooled_lesser` a distinct
        `ConduitState` rather than just an idle `lesser`.
""", """
    System Context:
        Pooling a scope object is only safe because a pooled space knows it is
        not leased: `release()` sets its released flag, every acquisition clears
        it, and a released space refuses `meld` and `purge` with
        SpellSpaceScopeError. A handle kept across the recycle boundary therefore
        fails loudly instead of melding into an idle shell that the next request
        would be served. Using a handle after its space was leased again to
        another caller remains a caller contract violation. The same reasoning
        makes `pooled_lesser` a distinct `ConduitState` rather than just an idle
        `lesser`.
""")
replace_block(POOL, """
        Contract:
            Manual-path reactivation hook: when `track_registry` is True, marks
""", """
        Contract:
            Clears the space's released flag: the lease starts here.
            Manual-path reactivation hook: when `track_registry` is True, marks
""")
replace_block(POOL, """
        if self._conduit_meld._meld_hooks_modified:
            obj._meld._inherit_meld_hooks(self._conduit_meld)
        if track_registry:
            obj._registry_tracked = True
            obj._spellspace_registry.add(obj)
        return obj
""", """
        obj._released = False
        if self._conduit_meld._meld_hooks_modified:
            obj._meld._inherit_meld_hooks(self._conduit_meld)
        if track_registry:
            obj._registry_tracked = True
            obj._spellspace_registry.add(obj)
        return obj
""")
replace_block(POOL, """
            - A reused Space adopts temporary owner hooks only when the owner's
              divergence bool is set. Construction handles the fresh path.
        \"\"\"
        try:
            space = self._idle.pop()
        except IndexError:
            return self.create_object(*args, **kwargs)
        if self._conduit_meld._meld_hooks_modified:
""", """
            - A reused Space adopts temporary owner hooks only when the owner's
              divergence bool is set. Construction handles the fresh path.
            - Clears a reused space's released flag: the lease starts here. A new
              space starts unreleased.
        \"\"\"
        try:
            space = self._idle.pop()
        except IndexError:
            return self.create_object(*args, **kwargs)
        space._released = False
        if self._conduit_meld._meld_hooks_modified:
""")
replace_block(POOL, """
        Contract:
            - Uses a conduit-local fixed-capacity fast path.
            - Assumes trusted private callers do not double-return the same
              spellspace shell.
""", """
        Contract:
            - Uses a conduit-local fixed-capacity fast path.
            - Marks the space released first; it refuses `meld` and `purge` until
              its next acquisition.
            - Assumes trusted private callers do not double-return the same
              spellspace shell; SpellSpace cleanup and recycle return early for a
              space that is already released.
""")
replace_block(POOL, """
        self._idle.append(obj)
        if len(self._idle) <= self._target_idle:
            return
        try:
            overflow_space = self._idle.popleft()
""", """
        obj._released = True
        # Hot path (one release per managed scope): one read of the idle deque
        # serves the append, the capacity check and the overflow eviction.
        idle = self._idle
        idle.append(obj)
        if len(idle) <= self._target_idle:
            return
        try:
            overflow_space = idle.popleft()
""")
print("part 1 done")
