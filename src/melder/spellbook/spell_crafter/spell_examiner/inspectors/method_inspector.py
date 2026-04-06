import inspect
from inspect import Parameter
from typing import Any, Dict, Callable
# Melder imports
from melder.spellbook.spell_crafter.spell_examiner.inspectors.inspector_utility import InspectorUtility
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

#region MethodInspector
class MethodInspector:
    """
    Inspect a callable object and emit a structured, tool-ready record.

    Purpose:
        Provide a deterministic, best-effort profile of functions, methods,
        lambdas, and callable objects for AI inventory use.

    Contract:
        - Never invokes the callable.
        - Uses best-effort provenance; missing source data is represented as None.
        - Captures signature/parameters when available.

    Args:
        fn: Callable object to inspect.
        max_repr: Maximum length for repr strings.

    Raises:
        TypeError: If fn is not callable.
    """
    __melder_internal__ = _mrg.sentinel
    utility = InspectorUtility
    def __init__(self, fn: Callable, *, max_repr: int = 120):
        """
        Initializes the MethodInspector.

        Args:
            fn: The callable object to inspect.
            max_repr: Maximum length for representation strings.

        Raises:
            TypeError: If the provided 'fn' is not callable.
        """
        if not callable(fn):
            raise TypeError("MethodInspector expects a callable.")

        self.fn = fn
        self.max_repr = max_repr
        self.data: Dict[str, Any] = {}

    def _resolve_target(self) -> Callable:
        """
        Return the preferred callable for inspection.

        Purpose:
            Prefer the original callable surface when decorator wrapping would
            otherwise hide the user-authored name or signature.

        Contract:
            Falls back to the originally supplied callable when unwrapping does
            not produce a better target.
        """
        f = self.fn
        try:
            return self.utility.unwrap_callable(f)
        except Exception:
            # If unwrapping fails for any reason, fall back to the provided callable
            return f
    def inspect(self) -> Dict[str, Any]:
        """
        Perform the full callable inspection.

        Contract:
          - Resolves wrapper-vs-original view first.
          - Populates header, provenance, signature, trait, closure, and
            decoration fields in a stable order.
          - Returns a dictionary that is safe to serialize.
        """
        f = self.fn
        f_eff = self._resolve_target()  # prefer original for primary view

        self._fill_header(f_eff)
        self._fill_source(f_eff)
        self._fill_signature(f_eff)
        self._fill_traits(f_eff)
        self._fill_closure(f_eff)
        self._fill_decoration(f_eff, f)

        return self.data
    def _fill_header(self, f_eff: Callable) -> None:
        """
        Populate high-level metadata fields for the callable.

        Contract:
            Populates identity/module/docstring fields only; it does not
            inspect source or signature here.
        """
        module = inspect.getmodule(f_eff)
        qualname = getattr(f_eff, "__qualname__", None)
        name = getattr(f_eff, "__name__", None)

        self.data.update(
            {
                "name": name,
                "qualname": qualname,
                "module": getattr(f_eff, "__module__", None),
                "id": id(f_eff),
                "type": type(f_eff).__name__,
                "repr": self.utility.safe_repr(f_eff, self.max_repr),
                "builtin_mod": bool(module and inspect.isbuiltin(module)),
                "extension_mod": self.utility.is_extension_module(module),
                "docstring_raw": getattr(f_eff, "__doc__", None),
                "docstring_summary": "",
                "behavior_summary": "",
                "tags": [],
            }
        )
    def _fill_source(self, f_eff: Callable) -> None:
        """
        Best-effort population of file path, preview, and source offset.

        Contract:
            Missing provenance is represented as `None` fields rather than an
            exception.
        """
        try:
            self.data["file"] = inspect.getfile(f_eff)
        except Exception:
            self.data["file"] = None

        try:
            lines, off = inspect.getsourcelines(f_eff)
            self.data["preview"] = "".join(lines[:5]).strip()
            self.data["src_offset"] = off
            self.data["start_line"] = off
            self.data["end_line"] = off + len(lines) - 1 if lines else None
            self.data["source_text"] = "".join(lines).rstrip() if lines else None
        except Exception:
            self.data["preview"] = None
            self.data["src_offset"] = None
            self.data["start_line"] = None
            self.data["end_line"] = None
            self.data["source_text"] = None
    def _fill_signature(self, f_eff: Callable) -> None:
        """
        Extract the signature and normalized parameter list.

        Contract:
            - Sets `uninspectable=True` when signature extraction fails.
            - Otherwise populates a normalized parameter payload suitable for
              downstream profile serialization.
        """
        try:
            sig = inspect.signature(f_eff)
            self.data["signature"] = str(sig)
            self.data["parameters"] = [
                {
                    "name": p.name,
                    "kind": p.kind.name,
                    "default": None if p.default is Parameter.empty else self.utility.safe_repr(p.default, self.max_repr),
                    "annotation": None if p.annotation is Parameter.empty else self.utility.safe_repr(p.annotation, self.max_repr),
                }
                for p in sig.parameters.values()
            ]
        except (ValueError, TypeError):
            self.data["uninspectable"] = True
        else:
            self.data["uninspectable"] = False
    def _fill_traits(self, f_eff: Callable) -> None:
        """
        Populate callable trait flags (is function/method, async/gen, etc.).

        Contract:
            Uses reflection and class-dict heuristics only; never invokes the
            callable.
        """
        module = inspect.getmodule(f_eff)
        qualname = getattr(f_eff, "__qualname__", None)
        name = getattr(f_eff, "__name__", None)

        is_method = inspect.ismethod(f_eff)
        is_function = inspect.isfunction(f_eff)
        bound_self = getattr(f_eff, "__self__", None)

        # Detect staticmethod by walking back to the class dict if possible.
        static_check = False
        if qualname and module and name and "." in qualname:
            class_name = qualname.rsplit(".", 1)[0]
            container_name = class_name.split(".")[0]
            container = getattr(module, container_name, None)
            cls_obj = container
            if container and "." in class_name:
                try:
                    for part in class_name.split(".")[1:]:
                        cls_obj = getattr(cls_obj, part)
                except AttributeError:
                    cls_obj = None
            if inspect.isclass(cls_obj):
                method_attr = cls_obj.__dict__.get(name)
                static_check = isinstance(method_attr, staticmethod)

        self.data.update(
            {
                "func": is_function,
                "method": is_method,
                "builtin": inspect.isbuiltin(f_eff),
                "classmethod": is_method and isinstance(bound_self, type),
                "staticmethod": static_check,
                "generator": inspect.isgeneratorfunction(f_eff),
                "async_gen": inspect.isasyncgenfunction(f_eff),
                "coroutine": inspect.iscoroutinefunction(f_eff),
                "lambda_fn": is_function and name == "<lambda>",
                "abstract": inspect.isabstract(f_eff),
            }
        )
    def _fill_closure(self, f_eff: Callable) -> None:
        """
        Capture a safe preview of closure cell contents (if any).

        Contract:
            Best-effort only. Closure preview failures are surfaced as
            placeholder data instead of raising.
        """
        try:
            self.data["closure"] = None
            closure = getattr(f_eff, "__closure__", None)
            if closure:
                self.data["closure"] = [
                    self.utility.safe_repr(c.cell_contents, self.max_repr) for c in closure
                ]
        except Exception:
            self.data["closure"] = "<error>"

    def _fill_decoration(self, f_eff: Callable, f_wrapped: Callable) -> None:
        """
        Record decoration status:

        Contract:
          - `decorated` is True when the resolved inspection target differs
            from the originally supplied callable.
          - `wrapped_repr` points at the wrapper so the chain remains visible
            in the output.
        """
        try:
            self.data["decorated"] = (f_eff is not f_wrapped)
            self.data["wrapped_repr"] = None if (f_eff is f_wrapped) else self.utility.safe_repr(f_wrapped, self.max_repr)
        except Exception:
            self.data["decorated"] = "<error>"

#endregion
