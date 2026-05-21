import inspect
from typing import Any, Optional, ClassVar

from mypy_extensions import mypyc_attr

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

#region InspectorUtility

@mypyc_attr(native_class=True)
class InspectorUtility:
    """
    Shared low-level helpers for the spell examiner inspector layer.

    Purpose:
        Centralize the small defensive operations that every inspector needs:
        safe stringification, extension-module detection, and best-effort
        callable unwrapping.

    Contract:
        - Helper methods are best-effort and should not be the thing that
          causes inspection to fail.
        - The utility does not own any mutable runtime state.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = ()
    @staticmethod
    def safe_repr(obj: Any, max_len: int = 120) -> str:
        """
        Return a defensive, truncated repr() string.

        Purpose:
            Produce a stable human-readable representation for inspection
            output without letting a broken or overly large `repr()` poison the
            rest of the inspector result.

        Contract:
            - Never raises when `repr()` itself fails.
            - Truncates long representations while preserving the original
              length in the output.

        Args:
            obj: The object to get the representation of.
            max_len: The maximum allowed length for the representation string.

        Returns:
            A string representation, truncated if necessary (with original length),
            or an error placeholder.
        """
        try:
            r = repr(obj)
            r_len = len(r)
            # Truncate the string and add ellipsis + original length if it exceeds max_len
            if r_len > max_len:
                # Keep space for "... (len NNN)" approx 10-15 chars
                trunc_len = max(10, max_len - 15)
                return f"{r[:trunc_len]}... (len {r_len})"
            else:
                return r
        except Exception:
            # If repr() fails for any reason, return a placeholder indicating the type
            return f"<unrepr-able {type(obj).__name__}>"

    @staticmethod
    def is_extension_module(module: Optional[object]) -> bool:
        """
        Return whether a module object appears to point at a native extension.

        Contract:
            Uses `__spec__.origin` only and returns False when the module or
            origin metadata is missing.
        """
        if not module:
            return False
        # Use __spec__.origin which should point to the file path for extensions
        spec = getattr(module, "__spec__", None)
        origin = getattr(spec, "origin", None)
        return bool(origin and origin.lower().endswith((".so", ".pyd", ".dylib")))

    # Robust unwrapping for decorator cases without functools.wraps
    @staticmethod
    def unwrap_callable(obj: Any) -> Any:
        """
        Return the most 'original' callable we can find.

        Purpose:
            Recover a more user-authored callable surface for inspection when
            decorators or wrappers would otherwise hide the underlying
            function's name or signature.

        Strategy:
          1) Try inspect.unwrap to follow __wrapped__ chains.
          2) If unchanged and it's a closure-based decorator (no wraps),
             walk closure cells for a captured function and recurse.

        Contract:
            Returns the input object unchanged when no better callable target
            can be recovered.
        """
        try:
            unwrapped = inspect.unwrap(obj)
        except Exception:
            unwrapped = obj

        if unwrapped is not obj:
            return unwrapped

        # Closure-based unwrapping (handles decorators that didn't use functools.wraps)
        try:
            if inspect.isfunction(obj) and obj.__closure__:
                for cell in obj.__closure__:
                    try:
                        captured = cell.cell_contents
                    except Exception:
                        continue
                    if inspect.isfunction(captured) and captured is not obj:
                        return InspectorUtility.unwrap_callable(captured)
        except Exception:
            pass

        return obj
#endregion
