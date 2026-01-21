import inspect
from typing import Any, Optional
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

#region InspectorUtility
class InspectorUtility:
    __melder_internal__ = _mrg.sentinel
    @staticmethod
    def safe_repr(obj: Any, max_len: int = 120) -> str:
        """
        Return a defensive, truncated repr() string.

        Handles potential exceptions during repr() calls and limits the length
        of the representation string, indicating truncation and original length.

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
        """Checks if a module object points to a C extension module (.so, .pyd)."""
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

        Strategy:
          1) Try inspect.unwrap to follow __wrapped__ chains.
          2) If unchanged and it's a closure-based decorator (no wraps),
             walk closure cells for a captured function and recurse.
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