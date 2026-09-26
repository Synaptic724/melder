import inspect
import re
from typing import Any, Optional, ClassVar




#region InspectorUtility


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
    __slots__ = ()
    # CPython's default reprs embed the object's address as " at 0x<hex>"; it changes per process.
    _MEMORY_ADDRESS_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r" at 0x[0-9a-fA-F]+")

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
    def stable_repr(obj: Any) -> str:
        """
        Return the complete repr() of an object with every CPython memory address removed.

        Purpose:
            Give the bind fingerprint a representation that is identical in every process for the
            same object content. CPython's default reprs embed the object's address
            (`<function f at 0x...>`, `<C object at 0x...>`, `functools.partial(<function f at
            0x...>, ...)`), which differs between processes and would give the same spell a new id
            every run.

        Contract:
            - Removes every " at 0x<hex>" fragment from the full repr() text.
            - Never truncates: cutting after the removal would still depend on how many digits
              the removed addresses had, so the whole text is kept.
            - Never raises; a failing repr() yields the same placeholder as `safe_repr`.
            - Addresses printed in any other form (a custom __repr__ showing hex ids) are left
              untouched; they are that object's own identity text.

        Args:
            obj: Object to represent.

        Returns:
            str: Address-free, untruncated representation text.
        """
        try:
            text = repr(obj)
        except Exception:
            # Same best-effort placeholder as safe_repr: a broken repr must not fail binding.
            return f"<unrepr-able {type(obj).__name__}>"
        return InspectorUtility.strip_memory_addresses(text)

    @staticmethod
    def strip_memory_addresses(text: str) -> str:
        """
        Remove every CPython " at 0x<hex>" memory-address fragment from a representation text.

        Contract:
            - Pure and deterministic; only the fragment is removed, the rest of the text is kept.

        Args:
            text: Representation text, possibly containing addresses.

        Returns:
            str: The text without memory addresses.
        """
        return InspectorUtility._MEMORY_ADDRESS_PATTERN.sub("", text)

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
