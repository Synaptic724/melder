"""Apply the disposal-failure aggregation fix to Creations (melder_0, 2026-09-27). Usage: python apply_creations_fix.py <repo root>"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eol_lines
replace_lines = eol_lines.replace_lines

root = sys.argv[1]
path = os.path.join(root, "src/melder/aether/conduit/creations/creations.py")
edits = []

# 1) class docstring: Lifecycle / Cleanup
edits.append(("""    Lifecycle / Cleanup:
        Idempotent. Cleanup runs the declared disposal methods and AGGREGATES
        failures rather than stopping at the first one - a single badly behaved
        object must not strand the rest of the scope's teardown, so callers may
        see an ExceptionGroup.
""", """    Lifecycle / Cleanup:
        Idempotent. Cleanup runs the declared disposal methods and AGGREGATES
        failures rather than stopping at the first one - a single badly behaved
        object must not strand the rest of the scope's teardown, so callers may
        see an ExceptionGroup. Aggregation is per method as well as per object
        (2026-09-27): every declared method of every object runs, and each
        failing method is one `RuntimeError` in the group, chained from the
        exception it raised. Before, an object's first failing method ended
        that object's disposal and the original exception was dropped.
"""))

# 2) _attempt_cleanup + safe text helper
edits.append(('''    def _attempt_cleanup(self, entry: StoredDisposalEntry) -> Optional[Exception]:
        """
        Attempt explicit disposal for one tracked entry.

        Args:
            entry:
                `(object, disposal_method_names)` tuple.

        Returns:
            Optional[Exception]:
                Wrapped disposal error when disposal fails, otherwise `None`.
        """
        item, method_names = entry
        for method_name in method_names:
            try:
                method = item.__getattribute__(method_name)
                method()
            except Exception as ex:
                return RuntimeError(
                    f"Failed to dispose object {item} using method '{method_name}': {ex}"
                )
        return None
''', '''    def _attempt_cleanup(self, entry: StoredDisposalEntry) -> List[Exception]:
        """
        Run every declared disposal method of one tracked entry and collect each failure.

        Purpose:
            Dispose one object as fully as its declared methods allow. Each
            method usually releases a different resource, so one failing method
            must not skip the methods declared after it (owner decision,
            2026-09-27; before, the first failure ended the object's disposal).

        Contract:
            - Invokes the method names in their declared order, each exactly
              once, whether or not an earlier one raised.
            - Every method that raises `Exception` - including a name the
              object lacks, as `AttributeError` - yields one `RuntimeError`
              naming the object and the method. Its `__cause__` is the exception
              the method raised, so the original type and traceback survive.
            - The error text never depends on the object's or the exception's
              `__str__` succeeding; see `_describe_for_disposal_error`.
            - A `BaseException` that is not an `Exception` (for example
              `KeyboardInterrupt`) propagates, as before.
            - Does not mutate the entry or its borrowed method-name list.

        Args:
            entry:
                `(object, disposal_method_names)` tuple.

        Returns:
            List[Exception]:
                One wrapped error per failing method, in declared order; empty
                when every method succeeded.
        """
        item, method_names = entry
        errors: List[Exception] = []
        for method_name in method_names:
            try:
                method = item.__getattribute__(method_name)
                method()
            except Exception as ex:
                error = RuntimeError(
                    f"Failed to dispose object {self._describe_for_disposal_error(item)} "
                    f"using method '{method_name}': {self._describe_for_disposal_error(ex)}"
                )
                # A returned (never raised) error gets no implicit chaining, so
                # attach the original explicitly: its type and traceback are what
                # the caller needs to act on the failure.
                error.__cause__ = ex
                errors.append(error)
        return errors

    @staticmethod
    def _describe_for_disposal_error(value: object) -> str:
        """
        Return text for a disposal error without trusting `value.__str__`.

        Purpose:
            A half-disposed object's `__str__` may read the very resource its
            failing disposal just broke. Formatting it inside the error path used
            to raise out of `_attempt_cleanup` and strand every object not yet
            disposed (fixed 2026-09-27).

        Contract:
            - Returns `str(value)` when that succeeds.
            - Otherwise returns `<Type object at 0x...; str() raised ErrorType>`,
              built only from the type name and `id()`, which cannot raise.
            - Best-effort reporting inside disposal: the `Exception` from
              `__str__` is named in the fallback text, not propagated.

        Args:
            value:
                The object being disposed, or the exception one of its methods
                raised.

        Returns:
            str: Text safe to embed in a disposal error message.
        """
        try:
            return str(value)
        except Exception as ex:
            return f"<{type(value).__qualname__} object at {id(value):#x}; str() raised {type(ex).__name__}>"
'''))

# 3) _dispose_many_creations contract + body
edits.append(("""            - Delegate each object to `_attempt_cleanup`, which invokes its method
              names in order and stops that object at its first failing method.
            - Collect each object's failure and continue with the other objects.
""", """            - Delegate each object to `_attempt_cleanup`, which runs every method
              name in order and returns one error per failing method.
            - Collect every failure and continue with the other objects.
"""))
edits.append(("""        errors: List[Exception] = []
        for entry in reversed(entries):
            maybe_error = self._attempt_cleanup(entry)
            if maybe_error is not None:
                errors.append(maybe_error)
        return errors
""", """        errors: List[Exception] = []
        for entry in reversed(entries):
            errors.extend(self._attempt_cleanup(entry))
        return errors
"""))

# 4) _dispose_disposable_registry contract + body
edits.append(("""            - Collected failures never prevent trying the next selected object.
            - The caller owns registry detachment and final reference release.
""", """            - Collected failures never prevent trying the next selected object;
              every failing method of every object contributes one error.
            - The caller owns registry detachment and final reference release.
"""))
edits.append(("""            if isinstance(value, tuple):
                maybe_error = self._attempt_cleanup(value)
                if maybe_error:
                    errors.append(maybe_error)
                continue
""", """            if isinstance(value, tuple):
                errors.extend(self._attempt_cleanup(value))
                continue
"""))

# 5) _refuse_publish_into_cleaned_store contract + raises + body
edits.append(("""            - Runs the object's disposal methods (when declared) outside any lock.
""", """            - Runs every declared disposal method outside any lock, even after
              one of them fails.
"""))
edits.append(("""            RuntimeError:
                Always. Chained from the disposal failure when disposal failed.
        \"\"\"
        disposal_error: Optional[Exception] = None
        if has_disposal_methods:
            disposal_error = self._attempt_cleanup(
                (item, disposal_methods if disposal_methods is not None else [])
            )
""", """            RuntimeError:
                Always. Chained from the disposal error when one method failed,
                or from an `ExceptionGroup` of every failure when several did.
        \"\"\"
        disposal_errors: List[Exception] = []
        if has_disposal_methods:
            disposal_errors = self._attempt_cleanup(
                (item, disposal_methods if disposal_methods is not None else [])
            )
"""))
edits.append(("""        if disposal_error is not None:
            raise RuntimeError(message) from disposal_error
        raise RuntimeError(message)
""", """        if len(disposal_errors) == 1:
            raise RuntimeError(message) from disposal_errors[0]
        if disposal_errors:
            raise RuntimeError(message) from ExceptionGroup(
                f"Errors occurred disposing creation '{key}'", disposal_errors
            )
        raise RuntimeError(message)
"""))

# 6) purge contract + body
edits.append(("""            - The first failing method stops that object's remaining methods;
              other selected objects are still attempted, matching cleanup.
""", """            - Every declared method runs even after one fails; each failure is
              collected and other selected objects are still attempted, matching
              cleanup.
"""))
edits.append(("""        errors: List[Exception] = []
        if isinstance(disposal, tuple):
            maybe_error = self._attempt_cleanup(disposal)
            if maybe_error is not None:
                errors.append(maybe_error)
        elif isinstance(disposal, list):
            errors = self._dispose_many_creations(disposal)
""", """        errors: List[Exception] = []
        if isinstance(disposal, tuple):
            errors = self._attempt_cleanup(disposal)
        elif isinstance(disposal, list):
            errors = self._dispose_many_creations(disposal)
"""))

for old, new in edits:
    print(replace_lines(path, old, new))
