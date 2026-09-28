"""Scope-exit dispose lane, part 3: ward child teardown failures and frame teardown logging. melder_0, 2026-09-27."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from source_edit import replace_block, replace_def

ROOT = sys.argv[1]
WARD = os.path.join(ROOT, "src/melder/aether/conduit/conduit_ward/conduit_ward.py")
FRAME = os.path.join(ROOT, "src/melder/aether/aetheric_frame/aetheric_frame.py")

print("conduit_ward.py")
replace_block(WARD, """
          - Cleanup all lesser conduits and clear lineage references.
          - Null internal state and mark cleaned. Logger metadata is nulled last.

        Returns:
            None
        \"\"\"
""", """
          - Permanently clean all lesser conduits and clear lineage references. Every child is
            torn down even when one raises; a child's disposal failures (the ExceptionGroup its
            teardown raises after finishing) are collected, other child errors are logged.
          - Null internal state and mark cleaned. Logger metadata is nulled last.
          - Raises the collected disposal failures last, after this ward is fully cleaned.

        Returns:
            None

        Raises:
            ExceptionGroup: One or more lesser conduits were torn down with disposal failures.
        \"\"\"
""")
replace_block(WARD, """
            # Clean up lesser conduits
            self._clean_up_lesser_conduits_links()
""", """
            # Clean up lesser conduits; their disposal failures are raised once
            # this ward has finished its own teardown.
            child_failures = self._clean_up_lesser_conduits_links()
""")
replace_block(WARD, """
            # Null logger metadata last (outside lock)
            if  hasattr(self._logger, "cleanup"):
                self._logger.cleanup()
            del self._logger
""", """
            # Null logger metadata last (still inside the ward lock)
            if  hasattr(self._logger, "cleanup"):
                self._logger.cleanup()
            del self._logger
            if child_failures:
                raise ExceptionGroup(
                    "Lesser conduits torn down with disposal failures.", child_failures
                )
""")
replace_def(WARD, ["ConduitWard"], "_clean_up_lesser_conduits_links", r'''
    def _clean_up_lesser_conduits_links(self) -> List[Exception]:
        """
        Internal

        Recursively clean up and detach all lesser conduits (children).

        Contract:
            - Attempts every child: an error from one child's cleanup does not stop its
              siblings.
            - A child's disposal failures - the ExceptionGroup its permanent teardown
              raises after finishing - are collected and returned so the owner raises
              them last.
            - Any other child error is logged, as before, and not returned.

        Returns:
            List[Exception]: Collected disposal failure groups; empty when none failed.
        """
        failures: List[Exception] = []
        if not self._lesser_conduits:
            return failures

        for lesser_conduit in list(self._lesser_conduits.values()):
            try:
                lesser_conduit.permanent_cleanup()
            except ExceptionGroup as disposal_failures:
                failures.append(disposal_failures)
            except Exception as e:
                self._logger.error(
                    f"cleanup lesser link failed: {e}",
                    method_name="_clean_up_lesser_conduits_links", exc_info=True,
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
        self._lesser_conduits.clear()
        return failures
''', must_contain=["lesser_conduit.permanent_cleanup()", "cleanup lesser link failed"])
replace_block(WARD, """
            - Failed descendants remain owned; raises before detaching this ward
              so an ancestor cannot enter the pool while a child is still live.
""", """
            - Failed descendants remain owned; raises before detaching this ward
              so an ancestor cannot enter the pool while a child is still live.
            - A descendant that finished its pool return but raised its disposal
              failures does not block the detach; those failures are logged here.
              A conduit's own pool return cleans its children first and raises
              them instead, so this path normally finds no children.
""")
replace_def(WARD, ["ConduitWard"], "_cleanup_children_for_pool", r'''
    def _cleanup_children_for_pool(self, collect_finished: bool = False) -> Optional[List[Exception]]:
        """Soft-clean current descendants; keep every child that could not finish for retry.

        Contract:
            Used by a lesser's pool return (first, before its SpellSpaces and its own
            store), by ordinary recursive detach and by named record retirement.
            Snapshot membership under the ward lock because a child that finishes its
            pool return removes its own entry; call children outside that lock and
            attempt every sibling.
            A child whose cleanup raised but which is no longer attached finished its
            pool return (a lesser raises its disposal failures after it re-pools): its
            error is returned when `collect_finished` is True and logged otherwise.
            A child still attached could not finish: it keeps its parent link, and once
            every sibling was tried one ExceptionGroup of the unfinished and finished
            failures is raised before the caller can detach or reuse its scope.
            The ordinary no-children path returns at once without allocating.
        Args:
            collect_finished: Return finished children's failures to the caller instead
                of logging them.
        Returns:
            Optional[List[Exception]]: Finished children's failures when
            `collect_finished` is True and a finished child raised; otherwise None.
        Raises:
            ExceptionGroup: One or more children could not finish; their parent links remain.
        """
        with self._lock:
            if not self._lesser_conduits:
                return None
            children = list(self._lesser_conduits.values())
        retained: List[Exception] = []
        finished: List[Exception] = []
        for lesser_conduit in children:
            try:
                lesser_conduit.cleanup()
            except Exception as error:
                # A child that finished its pool return removed its own entry (under
                # its own lock) before raising its disposal failures.
                with self._lock:
                    still_attached = lesser_conduit._id in self._lesser_conduits
                if not still_attached:
                    finished.append(error)
                    continue
                retained.append(error)
                self._logger.error(
                    f"pool descendant cleanup failed: {error}",
                    method_name="_cleanup_children_for_pool", exc_info=True,
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
        if retained:
            raise ExceptionGroup(
                "Cannot pool a conduit while descendant cleanup is incomplete.",
                [*retained, *finished],
            )
        with self._lock:
            # Normally each child removed itself. Retire any completed snapshot
            # entries still present, without discarding newly attached identities.
            for lesser_conduit in children:
                self._lesser_conduits.pop(lesser_conduit._id, None)
        if not finished:
            return None
        if collect_finished:
            return finished
        for error in finished:
            self._logger.error(
                f"pool descendant returned with disposal failures: {error}",
                method_name="_cleanup_children_for_pool", exc_info=error,
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
        return None
''', must_contain=["lesser_conduit.cleanup()", "Cannot pool a conduit while descendant cleanup is incomplete."])

print("aetheric_frame.py")
replace_block(FRAME, """
        Contract:
        - Cleans child conduits before clearing conduit registries.
""", """
        Contract:
        - Cleans child conduits before clearing conduit registries. A conduit whose
          teardown raises (disposal failures are raised only after its teardown
          finishes) is logged through the Aether logger and the frame keeps going.
""")
replace_block(FRAME, """
                try:
                    conduit.permanent_cleanup()
                except Exception:
                    # DevOps surfaces can record incidents if you want;
                    # frame cleanup never dies on conduit cleanup.
                    pass
""", """
                try:
                    conduit.permanent_cleanup()
                except Exception:
                    # Frame cleanup never dies on conduit cleanup: log the failure
                    # and keep going (DevOps surfaces can record incidents from the
                    # log). A conduit raises its disposal failures only after its
                    # own teardown finished.
                    if self._aether._logger is not None:
                        self._aether._logger.error(
                            "Error cleaning conduit during frame teardown",
                            "_cleanup_data_structures",
                            exc_info=True,
                        )
""")
print("part 3 done")
