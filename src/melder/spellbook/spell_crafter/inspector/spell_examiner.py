import inspect
from inspect import Parameter
import json
from typing import Any, Dict, List, Optional, Type, Callable
from dataclasses import dataclass, field

#region InspectorUtility
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
#endregion
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

#region MethodInspector
class MethodInspector:
    """
    Inspects a Python callable object (function, method, lambda, etc.)
    and gathers detailed information about it.
    """
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
#endregion

#region Profiles
@dataclass
class MethodProfile:
    """Structured, IDE‑friendly representation of MethodInspector output."""
    # Required fields
    name: str
    qualname: Optional[str]
    module: Optional[str]
    id: int
    type: str
    repr: str
    builtin_mod: bool
    extension_mod: bool

    # Optional / defaulted
    file: Optional[str] = None
    preview: Optional[str] = None
    src_offset: Optional[int] = None
    signature: Optional[str] = None
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    uninspectable: bool = False

    # Callable trait flags – default to False
    func: bool = False
    method: bool = False
    builtin: bool = False
    classmethod: bool = False
    staticmethod: bool = False
    generator: bool = False
    async_gen: bool = False
    coroutine: bool = False
    lambda_fn: bool = False
    abstract: bool = False

    # Advanced details
    closure: Optional[List[str]] = None
    decorated: Optional[bool] = None
    wrapped_repr: Optional[str] = None

@dataclass
class ClassProfile:
    """Structured, IDE‑friendly representation of ClassInspector output."""
    # Required (no defaults)
    name: str
    qualname: str
    module: str

    # Optional / defaulted – must come after required fields (dataclass rule)
    mro: List[str] = field(default_factory=list)
    bases: List[str] = field(default_factory=list)
    annotations: Dict[str, str] = field(default_factory=dict)
    protocols: Dict[str, bool] = field(default_factory=dict)
    slots: Optional[List[str]] = None
    origin_file: Optional[str] = None
    origin_line: Optional[int] = None
    source_preview: Optional[str] = None
    members: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    methods: Dict[str, MethodProfile] = field(default_factory=dict)
    is_dataclass: bool = False
    decorated: bool = False



#endregion
#region SpellExaminer
class SpellExaminer:
    utility = InspectorUtility
    def __init__(
        self,
        obj: Any,
        *,
        show_dunders: bool = False,
        max_repr: int = 120,
    ):
        self.obj = obj
        self.dunders = show_dunders
        self.max_repr = max_repr

    def inspect(self) -> Any:
        if inspect.isclass(self.obj):
            inspector = ClassInspector(self.obj, show_dunders=self.dunders, max_repr=self.max_repr)
            data = inspector.inspect()

            method_profiles: Dict[str, MethodProfile] = {}
            for name, info in data["members"].items():
                if info.get("callable"):
                    try:
                        # Get the actual method reference from the class
                        fn = getattr(self.obj, name)
                        method_data = MethodInspector(fn, max_repr=self.max_repr).inspect()
                        method_profiles[name] = MethodProfile(
                            name=method_data["name"],
                            qualname=method_data["qualname"],
                            module=method_data["module"],
                            id=method_data["id"],
                            type=method_data["type"],
                            repr=method_data["repr"],
                            builtin_mod=method_data["builtin_mod"],
                            extension_mod=method_data["extension_mod"],
                            file=method_data["file"],
                            preview=method_data["preview"],
                            src_offset=method_data["src_offset"],
                            signature=method_data.get("signature"),
                            parameters=method_data.get("parameters", []),
                            uninspectable=method_data.get("uninspectable", False),
                            func=method_data.get("func", False),
                            method=method_data.get("method", False),
                            builtin=method_data.get("builtin", False),
                            classmethod=method_data.get("classmethod", False),
                            staticmethod=method_data.get("staticmethod", False),
                            generator=method_data.get("generator", False),
                            async_gen=method_data.get("async_gen", False),
                            coroutine=method_data.get("coroutine", False),
                            lambda_fn=method_data.get("lambda_fn", False),
                            abstract=method_data.get("abstract", False),
                            closure=method_data.get("closure"),
                            decorated=method_data.get("decorated"),
                            wrapped_repr=method_data.get("wrapped_repr"),
                        )
                    except Exception as e:
                        # fallback if something goes wrong
                        continue

            return ClassProfile(
                name=data["name"],
                qualname=data["qualname"],
                module=data["module"],
                mro=data["mro"],
                bases=data["bases"],
                annotations=data["annotations"],
                protocols=data["protocols"],
                slots=data["slots"],
                origin_file=data["file"],
                origin_line=data["source_line_offset"],
                source_preview=data["source_preview"],
                members=data["members"],  #original dict
                methods=method_profiles,  #structured MethodProfile dict
                is_dataclass=data["is_dataclass"],
                decorated=data["decorated"],
            )

        elif callable(self.obj) and not inspect.isclass(self.obj):
            inspector = MethodInspector(self.obj, max_repr=self.max_repr)
            data = inspector.inspect()
            return MethodProfile(
                name=data["name"],
                qualname=data["qualname"],
                module=data["module"],
                id=data["id"],
                type=data["type"],
                repr=data["repr"],
                builtin_mod=data["builtin_mod"],
                extension_mod=data["extension_mod"],
                file=data["file"],
                preview=data["preview"],
                src_offset=data["src_offset"],
                signature=data.get("signature"),
                parameters=data.get("parameters", []),
                uninspectable=data.get("uninspectable", False),
                func=data.get("func", False),
                method=data.get("method", False),
                builtin=data.get("builtin", False),
                classmethod=data.get("classmethod", False),
                staticmethod=data.get("staticmethod", False),
                generator=data.get("generator", False),
                async_gen=data.get("async_gen", False),
                coroutine=data.get("coroutine", False),
                lambda_fn=data.get("lambda_fn", False),
                abstract=data.get("abstract", False),
                closure=data.get("closure"),
                decorated=data.get("decorated"),
                wrapped_repr=data.get("wrapped_repr"),
            )

        return {
            "object_type": "instance_or_other",
            "repr": self.utility.safe_repr(self.obj, self.max_repr),
            "id": id(self.obj),
            "type": type(self.obj).__name__,
        }

    def to_json(self) -> str:
        result = self.inspect()
        if isinstance(result, (ClassProfile, MethodProfile)):
            return json.dumps(result.__dict__, default=str, indent=2)
        return json.dumps(result, default=str, indent=2)
#endregion