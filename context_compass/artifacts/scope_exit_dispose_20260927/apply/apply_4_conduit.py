"""Scope-exit dispose lane, part 4: Conduit `with` as dispose, finished pool returns and teardown. melder_0, 2026-09-27."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from source_edit import insert_after_def, replace_block, replace_def

ROOT = sys.argv[1]
CONDUIT = os.path.join(ROOT, "src/melder/aether/conduit/conduit.py")

print("conduit.py")
replace_block(CONDUIT, """
    ClassVar,
    Set,
)
""", """
    ClassVar,
    List,
    Set,
    Type,
)
""")
replace_def(CONDUIT, ["Conduit"], "cleanup", r'''
    def cleanup(self) -> None:
        """
        Public API

        Release this scope, recycling a lesser or permanently tearing down a root.

        Contract:
            - Permanent cleanup is idempotent after `_cleaned` flips. A successful
              soft lesser return ends its current use; callers must reacquire it
              through create_lesser_conduit before starting another use.
            - Soft cleanup of a lesser already in its pool (`pooled_lesser`) does
              nothing, so a second cleanup never pools the shell twice.
            - Permanent teardown fires `on_conduit_cleanup_start` and
              `on_conduit_cleanup_complete`. Soft return preserves the shell.
            - Dispatches to the lesser- or normal-conduit cleanup path based on the
              current conduit state.
            - Tears down logger state last, after the rest of the runtime surface has
              been released.
            - This is local conduit teardown only; it does not clean Aether or the
              owning frame itself.
            - Soft cleanup does not publish idle until descendants and named record/
              directory retirement finish. A descendant that cannot finish its own
              return, or a failed retirement, keeps this scope owned for retry;
              already completed disposal work is not rolled back.
            - A failing disposal method stops neither path: the lesser still returns
              to its pool and a permanent teardown still finishes, and then every
              disposal failure is raised as one ExceptionGroup (since 0.2.8201;
              permanent teardown used to only log them).

        Returns:
            None.

        Raises:
            ExceptionGroup: A disposal method failed (raised after the pool return or
                the teardown finished), or a descendant could not finish its own pool
                return (this scope stays attached for retry).
            Exception: Named record/directory retirement failed before pool return.

        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            if self._permanent_cleanup_requested:
                self._permanent_cleanup()
            else:
                self._prepare_for_pool()
''', must_contain=["self._prepare_for_pool()", "self._permanent_cleanup()"])
replace_def(CONDUIT, ["Conduit"], "_prepare_for_pool", r'''
    def _prepare_for_pool(self) -> None:
        """
        Reset one lesser conduit into the pooled idle state.

        Contract:
            - Normal conduits do not enter the lesser pool and still hard-clean.
            - A lesser already in its pool (`pooled_lesser`) returns at once, so a
              second soft cleanup never pools the shell twice.
            - Lesser conduits transition to `pooled_lesser` locally before they
              are returned to the root-owned pool.
            - Anonymous pool return stays local and does not refresh dev-ops or
              Nexus. Named return first retires its published scope metadata.
            - Disposes descendants first, then Spaces, then its own creations (the
              permanent teardown order), before clearing local lifecycle hooks and
              restoring temporary Meld hooks. The ordinary path checks one bool;
              only a modified Meld acquires its existing mutation lock.
            - Finishes the return when a disposal method fails: every child, Space
              and store is emptied before any of its methods run, so their failures
              are collected, the scope is pooled, and then one ExceptionGroup of
              them is raised. The no-failure path allocates nothing for this.
            - Named scopes unregister and clear their label before idle publication.
              Unnamed return performs only the direct name check: no directory
              call, lock, allocation or scan is introduced on that branch.
            - A descendant that cannot finish its own return, or a failed named
              record retirement or detach, keeps this scope attached and out of the
              pool so its owner can retry cleanup; failures collected before it are
              raised together with that error.

        Returns:
            None. The caller holds the conduit lock through idle publication.

        Raises:
            ExceptionGroup: Disposal failures, after this scope is back in its pool;
                or an unfinished descendant or a retirement failure together with the
                disposal failures collected before it (this scope stays attached).
            Exception: Named record retirement or detach failed and nothing else did.
        """
        # Hot path (one call per scope cycle). Read the state once: only a lesser
        # is returned, so the common case pays one comparison, as before.
        state = self._conduit_state
        if state is not ConduitState.lesser:
            if state is ConduitState.normal:
                self._permanent_cleanup()
            # pooled_lesser: already back in its pool, nothing to do.
            return
        # One read each of the ward and the pooled state serves every use below:
        # on the free-threaded build an attribute or enum-member load of a shared
        # object costs about 5-14 ns (measured 2026-09-27, scope_exit_dispose lane).
        ward = self._conduit_ward
        pooled = ConduitState.pooled_lesser
        failures: Optional[List[Exception]] = None
        # The caller holds this conduit's lock, which every new child link also
        # takes, so this unlocked read cannot miss a racing attachment.
        if ward._lesser_conduits:
            failures = ward._cleanup_children_for_pool(collect_finished=True)
        space_failures = self._cleanup_spellspaces_for_pool()
        if space_failures is not None:
            if failures is None:
                failures = space_failures
            else:
                failures.extend(space_failures)
        try:
            self._creations.reset_for_pool()
        except ExceptionGroup as store_failures:
            if failures is None:
                failures = [store_failures]
            else:
                failures.append(store_failures)
        try:
            if self._name is not None:
                self._prepare_named_for_pool()
            else:
                ward._detach_for_pool()
        except Exception as retirement_failure:
            if failures is None:
                raise
            raise ExceptionGroup(
                "Lesser conduit could not finish its pool return and stays attached for retry.",
                [*failures, retirement_failure],
            ) from None
        self._conduit_state = pooled
        ward._conduit_type = pooled
        if self._local_conduit_hooks is not None:
            self._local_conduit_hooks.clear()
        if self._meld._meld_hooks_modified:
            self._meld._reset_pooled_meld_hooks()
        self._conduit_pool.return_lesser_conduit(self)
        if failures is not None:
            raise ExceptionGroup("Lesser conduit returned to its pool with disposal failures.", failures)
''', must_contain=["self._cleanup_spellspaces_for_pool()", "self._conduit_pool.return_lesser_conduit(self)"])
replace_def(CONDUIT, ["Conduit"], "_cleanup_spellspaces_for_pool", r'''
    def _cleanup_spellspaces_for_pool(self) -> Optional[List[Exception]]:
        """
        Internal

        Soft-clean active and registered spellspaces without destroying the pool.

        Contract:
            - `_spellspace_stack` is always a `SpellSpaceThreadState`: it is
              assigned exactly once in `__init__` and only deleted during
              permanent teardown, so this path drains it directly without a
              defensive type probe.
            - Every space is cleaned even when one raises. A space finishes its
              own pool return before raising (its store is emptied first), so each
              error is collected, not logged, for the caller to raise once this
              conduit's return is complete.
            - The list is allocated only when a space failed.
            - Returns None at once when this thread has no open managed Space
              and no manual Space is registered (the common case), without the
              drain call.

        Returns:
            Optional[List[Exception]]: The spaces' cleanup errors, or None.
        """
        # Hot path: runs once per pooled lesser cleanup (one per scope cycle).
        # Nothing to sweep in the common case: return before the drain call.
        # Reads the owned thread state's per-thread stack directly (saves a
        # call per cycle, measured 2026-09-27); keep in step with
        # SpellSpaceThreadState.drain.
        if not self._spellspace_registry and not self._spellspace_stack._local.spellspace_stack:
            return None
        # The stack holder type is an owned lifecycle invariant; drain directly.
        failures: Optional[List[Exception]] = None
        active_spellspaces = self._spellspace_stack.drain()
        for spellspace in active_spellspaces:
            try:
                spellspace.cleanup()
            except Exception as error:
                if failures is None:
                    failures = [error]
                else:
                    failures.append(error)

        while self._spellspace_registry:
            try:
                self._spellspace_registry.pop().cleanup()
            except Exception as error:
                if failures is None:
                    failures = [error]
                else:
                    failures.append(error)
        return failures
''', must_contain=["self._spellspace_stack.drain()", "self._spellspace_registry.pop().cleanup()"])
replace_def(CONDUIT, ["Conduit"], "_permanent_cleanup", r'''
    def _permanent_cleanup(self) -> None:
        """
        Internal

        Cleans up all resources associated with the Conduit, including
        deregistering from Aether and Spellbook, and removing all references.

        Contract:
            - Every teardown step runs when a disposal method fails: the ward's
              lesser lineage, the SpellSpaces, the stores and (normal) the cluster
              facade each finish before their disposal failures are collected;
              other step errors stay logged.
            - Hooks fire, hook maps are deleted and the logger goes last; then the
              collected disposal failures are raised as one ExceptionGroup.

        Raises:
            ExceptionGroup: One or more owned objects failed a disposal method.
            RuntimeError: The conduit state is unknown.
        """
        if self._conduit_hooks or self._local_conduit_hooks:
            self._fire_conduit_hooks("on_conduit_cleanup_start", self)
            self._cleaned = True
            if self._conduit_state in (
                    ConduitState.lesser,
                    ConduitState.pooled_lesser,
            ):
                disposal_failures = self._cleanup_lesser_conduit()
            elif self._conduit_state == ConduitState.normal:
                disposal_failures = self._cleanup_normal_conduit()
            else:
                self._logger.error("Unknown Conduit state during cleanup", "cleanup")
                raise RuntimeError("Conduit state is unknown during cleanup")
            self._fire_conduit_hooks("on_conduit_cleanup_complete", self)

            del self._conduit_hooks
            del self._meld_hooks
            del self._local_conduit_hooks

            # Logger last
            try:
                if hasattr(self._logger, "cleanup"):
                    self._logger.cleanup()
            except Exception:
                pass
            del self._logger
        else:
            self._cleaned = True
            if self._conduit_state in (
                    ConduitState.lesser,
                    ConduitState.pooled_lesser,
            ):
                disposal_failures = self._cleanup_lesser_conduit()
            elif self._conduit_state == ConduitState.normal:
                disposal_failures = self._cleanup_normal_conduit()
            else:
                self._logger.error("Unknown Conduit state during cleanup", "cleanup")
                raise RuntimeError("Conduit state is unknown during cleanup")

            del self._conduit_hooks
            del self._meld_hooks
            del self._local_conduit_hooks

            # Logger last
            try:
                if hasattr(self._logger, "cleanup"):
                    self._logger.cleanup()
            except Exception:
                pass
            del self._logger
        if disposal_failures:
            raise ExceptionGroup("Conduit torn down with disposal failures.", disposal_failures)
''', must_contain=["self._cleanup_lesser_conduit()", "self._cleanup_normal_conduit()", "on_conduit_cleanup_complete"])
replace_block(CONDUIT, """
    def _cleanup_lesser_conduit(self) -> None:
        \"\"\"
        Internal

        Permanently retire a lesser and its owned runtime collaborators.

        Contract:
            Remove named discovery before deleting frame/ward references. Unnamed
            shells skip directory work. The shared Book and root maps remain owned
            by the lineage root; local children and stores follow existing teardown.
        Returns:
            None.
        \"\"\"
""", """
    def _cleanup_lesser_conduit(self) -> List[Exception]:
        \"\"\"
        Internal

        Permanently retire a lesser and its owned runtime collaborators.

        Contract:
            Remove named discovery before deleting frame/ward references. Unnamed
            shells skip directory work. The shared Book and root maps remain owned
            by the lineage root; local children and stores follow existing teardown.
            The ward (lesser lineage), the SpellSpaces and the own store raise their
            disposal failures only after finishing; those groups are collected and
            returned, other step errors stay logged.
        Returns:
            List[Exception]: Collected disposal failure groups; empty when none failed.
        \"\"\"
        failures: List[Exception] = []
""")
replace_block(CONDUIT, """
        try:
            if self._conduit_ward is not None:
                self._conduit_ward.cleanup()
        except Exception:
            self._logger.error("Error cleaning conduit ward", "_cleanup_lesser_conduit", exc_info=True)

        self._cleanup_spellspaces()

        try:
            if self._creations is not None:
                self._creations.cleanup()
        except Exception:
            self._logger.error("Error cleaning creations", "_cleanup_lesser_conduit", exc_info=True)
""", """
        try:
            if self._conduit_ward is not None:
                self._conduit_ward.cleanup()
        except ExceptionGroup as disposal_failures:
            failures.append(disposal_failures)
        except Exception:
            self._logger.error("Error cleaning conduit ward", "_cleanup_lesser_conduit", exc_info=True)

        failures.extend(self._cleanup_spellspaces())

        try:
            if self._creations is not None:
                self._creations.cleanup()
        except ExceptionGroup as disposal_failures:
            failures.append(disposal_failures)
        except Exception:
            self._logger.error("Error cleaning creations", "_cleanup_lesser_conduit", exc_info=True)
""")
replace_block(CONDUIT, """
        del self._configuration
        del self._root_conduit_id
        del self._nexus
""", """
        del self._configuration
        del self._root_conduit_id
        del self._nexus
        return failures
""")
replace_block(CONDUIT, """
    def _cleanup_normal_conduit(self) -> None:
        \"\"\"
        Internal

        Cleans up a normal Conduit.
        \"\"\"
        self._remove_conduit_record_from_nexus()
""", """
    def _cleanup_normal_conduit(self) -> List[Exception]:
        \"\"\"
        Internal

        Cleans up a normal Conduit.

        Contract:
            The cluster facade, the ward (lesser lineage), the SpellSpaces and the
            own store raise their disposal failures only after finishing; those
            groups are collected and returned, other step errors stay logged, and
            every later step still runs.

        Returns:
            List[Exception]: Collected disposal failure groups; empty when none failed.
        \"\"\"
        failures: List[Exception] = []
        self._remove_conduit_record_from_nexus()
""")
replace_block(CONDUIT, """
        try:
            if self._cluster_creations is not None:
                self._cluster_creations.cleanup()
        except Exception:
            self._logger.error(
                "Error cleaning cluster facade", "_cleanup_normal_conduit", exc_info=True
            )
""", """
        try:
            if self._cluster_creations is not None:
                self._cluster_creations.cleanup()
        except ExceptionGroup as disposal_failures:
            failures.append(disposal_failures)
        except Exception:
            self._logger.error(
                "Error cleaning cluster facade", "_cleanup_normal_conduit", exc_info=True
            )
""")
replace_block(CONDUIT, """
        try:
            if self._conduit_ward is not None:
                self._conduit_ward.cleanup()
        except Exception:
            self._logger.error("Error cleaning conduit ward", "_cleanup_normal_conduit", exc_info=True)

        # 2.5) Spellspaces (ensure stack is flushed)
        self._cleanup_spellspaces()

        # 3) Creations
        try:
            if self._creations is not None:
                self._creations.cleanup()
        except Exception:
            self._logger.error("Error cleaning creations", "_cleanup_normal_conduit", exc_info=True)
""", """
        try:
            if self._conduit_ward is not None:
                self._conduit_ward.cleanup()
        except ExceptionGroup as disposal_failures:
            failures.append(disposal_failures)
        except Exception:
            self._logger.error("Error cleaning conduit ward", "_cleanup_normal_conduit", exc_info=True)

        # 2.5) Spellspaces (ensure stack is flushed)
        failures.extend(self._cleanup_spellspaces())

        # 3) Creations
        try:
            if self._creations is not None:
                self._creations.cleanup()
        except ExceptionGroup as disposal_failures:
            failures.append(disposal_failures)
        except Exception:
            self._logger.error("Error cleaning creations", "_cleanup_normal_conduit", exc_info=True)
""")
replace_block(CONDUIT, """
        del self._mutation_research
        del self._nexus
""", """
        del self._mutation_research
        del self._nexus
        return failures
""")
replace_def(CONDUIT, ["Conduit"], "_cleanup_spellspaces", r'''
    def _cleanup_spellspaces(self) -> List[Exception]:
        """
        Internal

        Best-effort cleanup of any spellspaces still on the stack.

        Contract:
            - Permanently cleans the calling thread's managed spaces and every
              registry-tracked space, then the spellspace pool.
            - A space's disposal failures - the ExceptionGroup its permanent cleanup
              raises after finishing - are collected and returned; other errors are
              logged, as before.

        Returns:
            List[Exception]: Collected disposal failure groups; empty when none failed.
        """
        if self._spellspace_stack is None:
            return []
        try:
            stack_holder = self._spellspace_stack
            if isinstance(stack_holder, SpellSpaceThreadState):
                stack = list(stack_holder.drain())
            else:
                stack = list(stack_holder.get())
                stack_holder.set([])
        except Exception:
            self._logger.error(
                "Error flushing spellspace stack",
                "_cleanup_spellspaces",
                exc_info=True,
            )
            return []
        registry = list(self._spellspace_registry) if self._spellspace_registry is not None else []
        spellspaces = list(dict.fromkeys([*stack, *registry]))
        if self._spellspace_registry is not None:
            self._spellspace_registry.clear()
        failures: List[Exception] = []
        for spellspace in spellspaces:
            try:
                spellspace.permanent_cleanup()
            except ExceptionGroup as disposal_failures:
                failures.append(disposal_failures)
            except Exception:
                self._logger.error(
                    "Error cleaning spellspace",
                    "_cleanup_spellspaces",
                    exc_info=True,
                )
        if self._spellspace_pool is not None:
            try:
                self._spellspace_pool.cleanup()
            except Exception:
                self._logger.error(
                    "Error cleaning spellspace pool",
                    "_cleanup_spellspaces",
                    exc_info=True,
                )
        return failures
''', must_contain=["spellspace.permanent_cleanup()", "Error flushing spellspace stack"])
replace_def(CONDUIT, ["Conduit"], "__enter__", r'''
    def __enter__(self) -> Conduit:
        """
        Public API

        Enter a dispose scope over this conduit and return `self`.

        Purpose:
            Make `with conduit:` behave like a .NET `using` block: the conduit is
            released when the block ends. Pair it with `enter_lesser_conduit()` for a
            request-scoped lesser.

        Contract:
            - Returns `self` and does nothing else: no lock is taken and no state
              changes (changed 0.2.8201; `with conduit:` used to hold the conduit
              lock for the block).
            - Performs no cleaned-state check; entering a cleaned conduit is a caller
              contract violation, like any other use after cleanup.

        Returns:
            Conduit:
                This conduit, for use inside the block.

        """
        return self
''', must_contain=["self._lock.acquire()"])
replace_def(CONDUIT, ["Conduit"], "__exit__", r'''
    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_value: Optional[BaseException],
            traceback: Optional[TracebackType],
    ) -> None:
        """
        Public API

        End the dispose scope: clean this conduit up.

        Contract:
            - Calls `cleanup()` at every block exit, including when the block raised:
              a lesser disposes its descendants, SpellSpaces and own creations and
              returns to its pool; a normal (root) conduit is torn down permanently.
            - Never suppresses the block's exception (returns None).
            - Disposal failures are raised after the cleanup finished, as one
              ExceptionGroup; when the block raised too, that group rises with the
              block's exception as its `__context__` (Python's rule for an error
              raised in `__exit__`).
            - A lesser already returned inside the block (an explicit `cleanup()`)
              is not pooled twice while the shell is idle. If another caller
              acquired the shell in between, this exit reaches that new lease, so a
              scope must not be released inside its own block.

        Threading:
            Takes the conduit lock only inside `cleanup()`.

        Raises:
            ExceptionGroup: Disposal failures, after the scope was cleaned up.
            Exception: A named lesser's record retirement failed; the lesser stays
                attached for a retry.

        Returns:
            None.

        """
        self.cleanup()
        return None
''', must_contain=["self._lock.release()"])
replace_block(CONDUIT, """
        space = self._spellspace_pool.acquire_untracked()
        self._spellspace_stack.push(space)
        return space
""", """
        space = self._spellspace_pool.acquire_untracked()
        # Hot path (one entry per managed scope): the owned thread state's push,
        # inlined to save a call per scope (measured 2026-09-27); keep in step
        # with SpellSpaceThreadState.push.
        self._spellspace_stack._local.spellspace_stack.append(space)
        return space
""")
insert_after_def(CONDUIT, ["Conduit"], "create_lesser_conduit", r'''
    def enter_lesser_conduit(
            self,
            logger: Optional[Any] = None,
            *,
            name: Optional[str] = None,
    ) -> Conduit:
        """
        Public API

        Create a lesser conduit for use as a `with` block scope.

        Usage:
            with conduit.enter_lesser_conduit() as lesser:
                service = lesser.meld(spell_id=service_id)
            # the block exit ran lesser.cleanup(): its objects are disposed and
            # the shell is back in the root's pool

        Contract:
            - Returns exactly what `create_lesser_conduit(logger, name=name)` returns:
              a live lesser attached to this conduit, named when `name` is given.
            - `with` calls `cleanup()` at block exit, even when the block raised: the
              lesser disposes its descendants, SpellSpaces and own creations and
              returns to its pool. Disposal failures are raised after the return as
              one ExceptionGroup, carrying the block's exception as `__context__`
              when the block raised too.
            - Plain: nothing is pushed on a per-thread stack and no implicit current
              scope is tracked, so the call costs what `create_lesser_conduit` costs
              and blocks nest freely.
            - Called without `with`, the caller calls `cleanup()` itself, exactly as
              for `create_lesser_conduit`.

        Args:
            logger:
                Optional logger, passed to `create_lesser_conduit` unchanged.
            name:
                Optional exact name for this use of the child scope.

        Returns:
            Conduit: The new lesser conduit, to use as the `with` target.

        Raises:
            RuntimeError: If this conduit or the named child is cleaned during acquisition.
            ValueError: Name is empty or already owned/reserved in this frame.
            TypeError: A supplied name is not a string.
        """
        return self.create_lesser_conduit(logger, name=name)
''')
print("part 4 done")
