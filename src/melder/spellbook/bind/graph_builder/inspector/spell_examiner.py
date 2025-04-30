import inspect
from inspect import Parameter
import json
from typing import Any, Dict, List, Optional, Type, Callable

class InspectorUtility:
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




class ClassInspector:
    """
    Inspects a Python class object and gathers detailed information about it.

    Collects metadata, source information, member details (attributes, methods),
    and protocol implementation checks. (GC info removed).
    """
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
        self.utility = InspectorUtility()
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
        # Removed GC-related call
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
                "bases": [b.__name__ for b in getattr(c, "__bases__", ())], # Names of base classes
                # eval_str=True resolves forward references if possible
                "annotations": inspect.get_annotations(c, eval_str=True, globals=getattr(module, '__dict__', None)),
                "metaclass": type(c).__name__, # Name of the metaclass
                "mro": [m.__name__ for m in inspect.getmro(c)], # Method Resolution Order (class names)
                "slots": getattr(c, "__slots__", None), # Value of __slots__ if defined
                # Check if the class belongs to a built-in or C extension module
                "is_builtin_module": bool(module and inspect.isbuiltin(module)),
                "is_extension_module": self.utility.is_extension_module(module),
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
        if hasattr(inspect, "classify_members"):
            classified = inspect.classify_members(self.cls)
        else:
            # crude fallback: label callables as "method", everything else as "data"
            classified = [
                (n, "method" if callable(o) else "data", o)
                for n, o in inspect.getmembers(self.cls)
            ]

        for name, kind, obj in classified:
            if not self.dunders and name.startswith("__") and name.endswith("__"):
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
                "abstract": inspect.isabstract(obj) if callable(obj) else False,
                "repr": self.utility.safe_repr(obj, self.max_repr),
                "signature": None,
                "src_line": None,
            }

            if callable(obj):
                try:
                    sig = inspect.signature(obj)
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

class MethodInspector:
    """
    Inspects a Python callable object (function, method, lambda, etc.)
    and gathers detailed information about it.
    """
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
        self.utility = InspectorUtility()
        self.fn = fn
        self.max_repr = max_repr
        self.data: Dict[str, Any] = {}

    def inspect(self) -> Dict[str, Any]:
        """
        Performs the inspection of the callable.

        Gathers metadata, source info, signature, callable traits,
        closure details, and decoration status.

        Returns:
            A dictionary containing the inspection results.
        """
        f = self.fn
        module = inspect.getmodule(f)
        qualname = getattr(f, "__qualname__", None)
        name = getattr(f, "__name__", None)

        self.data.update(
            {
                "name": name,
                "qualname": qualname,
                "module": getattr(f, "__module__", None),
                "id": id(f),
                "type": type(f).__name__,
                "repr": self.utility.safe_repr(f, self.max_repr),
                "builtin_mod": bool(module and inspect.isbuiltin(module)),
                "extension_mod": self.utility.is_extension_module(module),
            }
        )

        try:
            self.data["file"] = inspect.getfile(f)
        except Exception:
            self.data["file"] = None
        try:
            lines, off = inspect.getsourcelines(f)
            self.data["preview"] = "".join(lines[:5]).strip()
            self.data["src_offset"] = off
        except Exception:
            self.data["preview"] = None
            self.data["src_offset"] = None

        try:
            sig = inspect.signature(f)
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

        is_method = inspect.ismethod(f)
        is_function = inspect.isfunction(f)
        bound_self = getattr(f, "__self__", None)

        static_check = False
        if qualname and module and name and '.' in qualname:
            class_name = qualname.rsplit('.', 1)[0]
            container_name = class_name.split('.')[0]
            container = getattr(module, container_name, None)
            cls_obj = container
            if container and '.' in class_name:
                try:
                    for part in class_name.split('.')[1:]:
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
                "builtin": inspect.isbuiltin(f),
                "classmethod": is_method and isinstance(bound_self, type),
                "staticmethod": static_check,
                "generator": inspect.isgeneratorfunction(f),
                "async_gen": inspect.isasyncgenfunction(f),
                "coroutine": inspect.iscoroutinefunction(f),
                "lambda_fn": is_function and name == "<lambda>",
                "abstract": inspect.isabstract(f),
            }
        )

        try:
            self.data["closure"] = None
            closure = getattr(f, "__closure__", None)
            if closure:
                self.data["closure"] = [self.utility.safe_repr(c.cell_contents, self.max_repr) for c in closure]
        except Exception:
            self.data["closure"] = "<error>"

        try:
            unwrapped = inspect.unwrap(f, stop=None)
            if unwrapped is not f:
                self.data["decorated"] = True
                self.data["wrapped_repr"] = self.utility.safe_repr(unwrapped, self.max_repr)
            else:
                self.data["decorated"] = False
        except Exception:
            self.data["decorated"] = "<error>"

        return self.data


class SpellExaminer:
    """
    A dispatcher class that examines a Python object and routes it
    to the appropriate inspector (ClassInspector or MethodInspector)
    based on its type. Handles unsupported types gracefully.
    """
    def __init__(
        self,
        obj: Any, # The object to examine
        *,
        show_dunders: bool = False, # Passed to ClassInspector
        max_repr   : int  = 120,    # Passed to both inspectors
    ):
        """
        Initializes the SpellExaminer.

        Args:
            obj: The Python object to inspect.
            show_dunders: Configures dunder visibility for class inspection.
            max_repr: Configures max repr length for all inspections.
        """
        self.utility = InspectorUtility()
        self.obj = obj
        self.dunders = show_dunders
        self.max_repr = max_repr

    def inspect(self) -> Dict[str, Any]:
        """
        Inspects the stored object.

        Determines if the object is a class, a callable, or something else,
        then calls the appropriate inspector or provides basic info.

        Returns:
            A dictionary containing the type of object inspected ('object_type')
            and the specific inspection data ('class_data' or 'callable_data').
            For unsupported types, returns basic info like repr and id.
        """
        # Check if the object is a class
        if inspect.isclass(self.obj):
            return {
                "object_type": "class", # Indicate the type
                # Delegate inspection to ClassInspector
                "class_data": ClassInspector(
                    self.obj,
                    show_dunders=self.dunders,
                    # Removed include_gc argument
                    max_repr=self.max_repr,
                ).inspect(),
            }
        # Check if the object is callable (function, method, lambda, callable class instance)
        # Exclude classes themselves here, as they are handled above
        if callable(self.obj) and not inspect.isclass(self.obj):
            return {
                "object_type": "callable", # Indicate the type
                # Delegate inspection to MethodInspector
                "callable_data": MethodInspector(
                    self.obj,
                    max_repr=self.max_repr,
                ).inspect(),
            }
        # Fallback for objects that are neither specifically handled classes nor callables
        return {
            "object_type": "instance_or_other", # Clarify it's not class/callable
            "repr": self.utility.safe_repr(self.obj, self.max_repr), # Provide basic info
            "id": id(self.obj),
            "type": type(self.obj).__name__, # Add type name for clarity
        }

    def to_json(self) -> str:
        """
        Convenience method to get the inspection results as a formatted JSON string.

        Returns:
            A JSON string representation of the inspection data.
        """
        return json.dumps(self.inspect(), default=str, indent=2)
