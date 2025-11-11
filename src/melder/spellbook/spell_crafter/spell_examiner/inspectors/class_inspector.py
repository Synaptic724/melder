import inspect
from inspect import Parameter
from typing import Any, Dict, Type
# Melder imports
from melder.spellbook.spell_crafter.spell_examiner.inspectors.inspector_utility import InspectorUtility


#region ClassInspector
class ClassInspector:
    """
    Inspects a Python class object and gathers detailed information about it.

    Collects metadata, source information, member details (attributes, methods),
    and protocol implementation checks. (GC info removed).
    """
    utility = InspectorUtility
    def __init__(
            self,
            cls: Type, # The class object to inspect
            *,
            show_dunders: bool = False, # Whether to include dunder methods/attributes
            # Removed 'include_gc' parameter
            max_repr: int = 120,       # Max length for repr strings in the output
    ):
        """
        Initializes the ClassInspector.

        Args:
            cls: The class object to inspect.
            show_dunders: If True, include members like __init__, __repr__.
            max_repr: Maximum length for representation strings.

        Raises:
            TypeError: If the provided 'cls' is not a class object.
        """
        if not inspect.isclass(cls):
            raise TypeError("ClassInspector expects a class object.")
        self.cls = cls
        self.dunders = show_dunders
        # Removed self.include_gc assignment
        self.max_repr = max_repr
        # Dictionary to store all collected inspection data
        self.data: Dict[str, Any] = {}

    # public
    def inspect(self) -> Dict[str, Any]:
        """
        Performs the inspection of the class.

        Calls private methods to gather different categories of information
        and returns the consolidated data.

        Returns:
            A dictionary containing the inspection results.
        """
        self._header()      # Basic class metadata
        self._source()      # Source file and line information
        self._members()     # Attributes, methods, properties
        self._protocols()   # Common protocol checks (e.g., __len__, __iter__)
        self._detect_decorator_wrapping() # Check for decorator wrapping

        return self.data

    # private blocks
    def _header(self) -> None:
        """Gathers basic header information about the class."""
        c = self.cls
        module = inspect.getmodule(c) # Get the module the class belongs to

        self.data.update(
            {
                "name": getattr(c, "__name__", "<unnamed>"), # Class name
                "qualname": getattr(c, "__qualname__", "<unnamed>"), # Qualified name (e.g., Outer.Inner)
                "module": getattr(c, "__module__", "<unknown>"), # Module name
                "id": id(c), # Memory address (unique identifier)
                "decorated": self._is_probably_decorated() or hasattr(c, "_decorated") or hasattr(c, "_marked"),
                "bases": [b.__name__ for b in getattr(c, "__bases__", ())], # Names of base classes
                # eval_str=True resolves forward references if possible
                "annotations": inspect.get_annotations(c, eval_str=True, globals=getattr(module, '__dict__', None)),
                "metaclass": type(c).__name__, # Name of the metaclass
                "mro": [m.__name__ for m in inspect.getmro(c)], # Method Resolution Order (class names)
                "slots": getattr(c, "__slots__", None), # Value of __slots__ if defined
                # Check if the class belongs to a built-in or C extension module
                "is_builtin_module": bool(module and inspect.isbuiltin(module)),
                "is_extension_module": self.utility.is_extension_module(module),
                "is_dataclass": hasattr(c, "__dataclass_fields__"),
            }
        )

    def _source(self) -> None:
        """Retrieves source file and a preview of the class definition, if possible."""
        c = self.cls
        try:
            # Get the file where the class is defined
            self.data["file"] = inspect.getfile(c)
        except Exception:
            # Fails for built-in types or dynamically created classes
            self.data["file"] = None
        try:
            # Get source lines and starting line number
            lines, off = inspect.getsourcelines(c)
            self.data["source_line_offset"] = off # Starting line number in the file
            # Provide a short preview (first 5 lines)
            self.data["source_preview"] = "".join(lines[:5]).strip()
        except Exception:
            # Fails if source code is not available (e.g., interactive, built-in)
            self.data["source_line_offset"] = None
            self.data["source_preview"] = None

    def _members(self) -> None:
        """Inspects the members (attributes, methods, properties, etc.) of the class."""
        members: Dict[str, Dict[str, Any]] = {}
        mro = inspect.getmro(self.cls) # Cache MRO
        cls_dict = self.cls.__dict__ # Cache class dict

        # Python 3.11+ has classify_members; older versions don’t.
        if callable(getattr(inspect, "classify_members", None)):
            classified = inspect.classify_members(self.cls)
        else:
            # crude fallback: label callables as "method", everything else as "data"
            classified = [
                (n, "method" if callable(o) else "data", o)
                for n, o in inspect.getmembers(self.cls)
            ]

        # Include __init__ for dataclasses even when dunders are hidden
        is_dc = hasattr(self.cls, "__dataclass_fields__")

        for name, kind, obj in classified:
            # keep dunder filter but allow dataclass __init__
            if not self.dunders and name.startswith("__") and name.endswith("__"):
                if not (is_dc and name == "__init__"):
                    continue

            owner = None
            if name not in cls_dict:
                for base in mro[1:]:
                    if name in base.__dict__:
                        owner = base.__name__
                        break

            info: Dict[str, Any] = {
                "defined_here": owner is None,
                "owner_class": owner or self.cls.__name__,
                "kind": kind,
                "type": type(obj).__name__,
                "callable": callable(obj),
                "property": isinstance(obj, property),
                "abstract": bool(getattr(obj, "__isabstractmethod__", False)) if callable(obj) else False,
                "repr": self.utility.safe_repr(obj, self.max_repr),
                "signature": None,
                "src_line": None,
            }

            if callable(obj):
                try:
                    # Use the member as-is for signature (primary view == wrapper if any)
                    target = obj
                    # Keep wrapper; do not unwrap here for primary signature
                    sig = inspect.signature(target if not isinstance(target, (staticmethod, classmethod)) else target.__func__)
                    info["signature"] = str(sig)
                    info["parameters"] = [
                        {
                            "name": p.name,
                            "kind": p.kind.name,
                            "default": None if p.default is Parameter.empty else self.utility.safe_repr(p.default, self.max_repr),
                            "annotation": None if p.annotation is Parameter.empty else self.utility.safe_repr(p.annotation,
                                                                                                              self.max_repr),
                        }
                        for p in sig.parameters.values()
                    ]

                    # Also record original/unwrapped signature when it differs
                    u_target = target.__func__ if isinstance(target, (staticmethod, classmethod)) else target
                    u_target = self.utility.unwrap_callable(u_target)
                    if u_target is not (target.__func__ if isinstance(target, (staticmethod, classmethod)) else target):
                        try:
                            u_sig = inspect.signature(u_target)
                            info["original_signature"] = str(u_sig)
                            info["original_parameters"] = [
                                {
                                    "name": p.name,
                                    "kind": p.kind.name,
                                    "default": None if p.default is Parameter.empty else self.utility.safe_repr(p.default, self.max_repr),
                                    "annotation": None if p.annotation is Parameter.empty else self.utility.safe_repr(p.annotation, self.max_repr),
                                }
                                for p in u_sig.parameters.values()
                            ]
                            info["original_name"] = getattr(u_target, "__name__", None)
                            info["original_qualname"] = getattr(u_target, "__qualname__", None)
                        except Exception:
                            pass

                except (ValueError, TypeError):
                    pass
                try:
                    _, ln = inspect.getsourcelines(obj)
                    info["src_line"] = ln
                except Exception:
                    pass

            if isinstance(obj, property):
                info["property_details"] = {
                    "fget": bool(obj.fget),
                    "fset": bool(obj.fset),
                    "fdel": bool(obj.fdel),
                }

            members[name] = info
        self.data["members"] = members

    def _protocols(self) -> None:
        """Checks for the presence of common dunder methods indicating protocol support."""
        c = self.cls
        has = lambda attr: hasattr(c, attr)
        self.data["protocols"] = {
            "len": has("__len__"),
            "getitem": has("__getitem__"),
            "iter": has("__iter__"),
            "call": has("__call__"),
            "enter": has("__enter__") and has("__exit__"),
            "await": has("__await__"),
            "add": has("__add__"),
            "hash": has("__hash__"),
            "repr": has("__repr__"),
            "str": has("__str__"),
        }

    def _detect_decorator_wrapping(self) -> None:
        try:
            orig_cls = inspect.unwrap(self.cls)
            if orig_cls is not self.cls:
                self.data["decorated"] = True
                self.data["wrapped_repr"] = InspectorUtility.safe_repr(orig_cls)
                return
        except Exception:
            pass

        # Additional heuristics
        decorated = (
                hasattr(self.cls, '__wrapped__') or
                hasattr(self.cls, '_decorated') or
                type(self.cls).__name__ != 'type'
        )

        self.data["decorated"] = decorated

    def _is_probably_decorated(self) -> bool:
        """
        Heuristically determines whether the inspected class has been decorated.

        This detects cases where a decorator wraps the original class with a callable,
        modifies and returns it, or replaces it with an instance.

        Returns:
            True if the object appears to be a decorated class.
        """
        obj = self.cls

        # If it's not a class anymore, it's definitely decorated
        if not inspect.isclass(obj):
            return True

        # If the __class__ is not 'type', it's something else pretending to be a class
        if type(obj) is not type:
            return True

        # Check if functools.wraps has tagged this object (used in decorator wrappers)
        if hasattr(obj, '__wrapped__'):
            return True

        # Heuristic: decorators often return a different qualname
        qualname = getattr(obj, '__qualname__', '')
        name = getattr(obj, '__name__', '')
        if qualname and '.' in qualname and not name in qualname:
            return True

        return False
#endregion