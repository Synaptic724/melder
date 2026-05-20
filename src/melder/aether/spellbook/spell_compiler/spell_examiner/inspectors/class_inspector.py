import inspect
from inspect import Parameter
from typing import Any, Dict, Type

from mypy_extensions import mypyc_attr

# Melder imports
from melder.aether.spellbook.spell_compiler.spell_examiner.inspectors.inspector_utility import InspectorUtility
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable


#region ClassInspector

@mypyc_attr(native_class=True)
class ClassInspector(Cleanable):
    """
    Inspect a class object and emit a structured, tool-ready inventory.

    Purpose:
        Produce a deterministic, object-surface inventory for AI profile
        construction without invoking user code. This includes class metadata,
        provenance, member inventory, and protocol/dynamic-access signals.

    Contract:
        - Never calls user-defined attribute accessors.
        - Uses best-effort inspection; missing provenance is represented as None.
        - Member records share a consistent schema, even for non-callables.
        - Dunder members are included only when show_dunders=True.

    Args:
        cls: Class object to inspect.
        show_dunders: Whether to include __dunder__ members.
        max_repr: Maximum length for repr strings in output.

    Raises:
        TypeError: If cls is not a class object.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + ["cls", "dunders", "max_repr", "data"]
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
        super().__init__()
        self.cls: Type = cls
        self.dunders: bool = show_dunders
        # Removed self.include_gc assignment
        self.max_repr: int = max_repr
        # Dictionary to store all collected inspection data
        self.data: Dict[str, Any] = {}

    def cleanup(self) -> None:
        """
        Perform cleanup operations for the ClassInspector.

        Contract:
            Cleans up any resources or state held by the inspector.

        Returns:
            None
        """
        if self._cleaned:
            return
        self._cleaned = True

        self.data.clear()
        del self.cls
        del self.dunders
        del self.max_repr
        del self.data

    # public
    def inspect(self) -> Dict[str, Any]:
        """
        Perform the full class inspection.

        Contract:
            - Populates header, provenance, members, protocol, and decoration
              fields in a deterministic order.
            - Returns a dictionary that is safe to serialize.

        Returns:
            Dict[str, Any]: Structured inspection output for the class.
        """
        self._header()      # Basic class metadata
        self._source()      # Source file and line information
        self._members()     # Attributes, methods, properties
        self._protocols()   # Common protocol checks (e.g., __len__, __iter__)
        self._detect_decorator_wrapping() # Check for decorator wrapping

        return self.data

    # private blocks
    def _header(self) -> None:
        """
        Populate core class metadata and dynamic-access flags.

        Contract:
            - Populates only metadata; does not read member values.
            - Dynamic-access flags are inferred from the class MRO.
        """
        c = self.cls
        module = inspect.getmodule(c) # Get the module the class belongs to

        dynamic_flags = self._dynamic_access_flags(c)
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
                "docstring_raw": getattr(c, "__doc__", None),
                "docstring_summary": "",
                "behavior_summary": "",
                "tags": [],
                "dynamic_access": dynamic_flags,
            }
        )

    def _source(self) -> None:
        """
        Populate class provenance fields (file path, line span, source text).

        Contract:
            - All provenance fields are best-effort and may be None.
            - source_preview is derived from the first 5 lines of source_text.
        """
        source_info = self._extract_source_info(self.cls)
        self.data["file"] = source_info["file_path"]
        self.data["source_line_offset"] = source_info["start_line"]
        self.data["source_end_line"] = source_info["end_line"]
        self.data["source_text"] = source_info["source_text"]
        self.data["source_preview"] = source_info["preview"]

    def _members(self) -> None:
        """
        Inspect class members and emit normalized member records.

        Contract:
            - All members include a consistent schema (name, kind, provenance,
              docstrings, and callable metadata when applicable).
            - Dunder filtering honors show_dunders, except for dataclass __init__.
        """
        members: Dict[str, Dict[str, Any]] = {}
        mro = inspect.getmro(self.cls) # Cache MRO
        cls_dict = self.cls.__dict__ # Cache class dict

        # Python 3.11+ has classify_members; older versions do not.
        classify_members = getattr(inspect, "classify_members", None)
        if callable(classify_members):
            classified = classify_members(self.cls)
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

            member_kind = self._resolve_member_kind(name, obj)
            is_callable = self._is_callable_member(obj)
            target = self._resolve_callable_target(obj)
            abstract = bool(
                getattr(obj, "__isabstractmethod__", False)
                or getattr(target, "__isabstractmethod__", False)
            )
            module = getattr(target, "__module__", None)
            qualname = getattr(target, "__qualname__", None)
            docstring_raw = getattr(target, "__doc__", None)
            provenance = self._extract_source_info(target)
            info: Dict[str, Any] = {
                "name": name,
                "defined_here": owner is None,
                "owner_class": owner or self.cls.__name__,
                "defined_on": owner or self.cls.__name__,
                "inherited": owner is not None,
                "kind": member_kind,
                "raw_kind": kind,
                "type": type(obj).__name__,
                "callable": is_callable,
                "property": isinstance(obj, property),
                "is_dunder": name.startswith("__") and name.endswith("__"),
                "module": module,
                "qualname": qualname,
                "docstring_raw": docstring_raw,
                "docstring_summary": "",
                "behavior_summary": "",
                "tags": [],
                "abstract": abstract,
                "repr": self.utility.safe_repr(obj, self.max_repr),
                "signature": None,
                "parameters": [],
                "return_annotation": None,
                "src_line": None,
                "file_path": provenance["file_path"],
                "start_line": provenance["start_line"],
                "end_line": provenance["end_line"],
                "source_text": provenance["source_text"],
            }

            if is_callable:
                try:
                    # Use the member as-is for signature (primary view == wrapper if any)
                    # Keep wrapper; do not unwrap here for primary signature
                    sig = inspect.signature(self._resolve_signature_target(obj))
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
                    if sig.return_annotation is not Parameter.empty:
                        info["return_annotation"] = self.utility.safe_repr(
                            sig.return_annotation, self.max_repr
                        )

                    # Also record original/unwrapped signature when it differs
                    u_target = self._resolve_callable_target(obj)
                    u_target = self.utility.unwrap_callable(u_target)
                    signature_target = self._resolve_signature_target(obj)
                    if u_target is not signature_target:
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
                    _, ln = inspect.getsourcelines(self._resolve_callable_target(obj))
                    info["src_line"] = ln
                except Exception:
                    pass

            if isinstance(obj, property):
                info["property_details"] = {
                    "fget": bool(obj.fget),
                    "fset": bool(obj.fset),
                    "fdel": bool(obj.fdel),
                }
                info["accessor_docstrings"] = {
                    "fget": getattr(obj.fget, "__doc__", None),
                    "fset": getattr(obj.fset, "__doc__", None),
                    "fdel": getattr(obj.fdel, "__doc__", None),
                }
                info["accessor_provenance"] = {
                    "fget": self._extract_source_info(obj.fget) if obj.fget else None,
                    "fset": self._extract_source_info(obj.fset) if obj.fset else None,
                    "fdel": self._extract_source_info(obj.fdel) if obj.fdel else None,
                }
            elif self._is_descriptor(obj):
                info["descriptor_details"] = {
                    "has_get": bool(getattr(obj, "__get__", None)),
                    "has_set": bool(getattr(obj, "__set__", None)),
                    "has_delete": bool(getattr(obj, "__delete__", None)),
                }

            members[name] = info
        self.data["members"] = members

    def _protocols(self) -> None:
        """
        Record protocol presence flags based on dunder methods.

        Contract:
            - Uses attribute presence only; no member invocation.
        """
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
        """
        Detect decorator wrapping and record wrapper metadata.

        Contract:
            - Updates data["decorated"] and data["wrapped_repr"] when applicable.
            - Never raises on unwrap failures.
        """
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
            bool: True if the object appears to be a decorated class.
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

    def _extract_source_info(self, obj: Any) -> Dict[str, Any]:
        """
        Extract best-effort provenance fields for an object.

        Args:
            obj: Object to inspect for source metadata.

        Contract:
            Missing provenance is represented as `None` fields rather than an
            exception.

        Returns:
            Dict[str, Any]: Keys: file_path, start_line, end_line, source_text, preview.
        """
        file_path = None
        start_line = None
        end_line = None
        source_text = None
        preview = None
        if obj is None:
            return {
                "file_path": None,
                "start_line": None,
                "end_line": None,
                "source_text": None,
                "preview": None,
            }
        try:
            file_path = inspect.getfile(obj)
        except Exception:
            file_path = None
        try:
            lines, off = inspect.getsourcelines(obj)
            start_line = off
            end_line = off + len(lines) - 1 if lines else None
            source_text = "".join(lines).rstrip() if lines else None
            preview = "".join(lines[:5]).strip() if lines else None
        except Exception:
            start_line = None
            end_line = None
            source_text = None
            preview = None
        return {
            "file_path": file_path,
            "start_line": start_line,
            "end_line": end_line,
            "source_text": source_text,
            "preview": preview,
        }

    def _resolve_signature_target(self, obj: Any) -> Any:
        """
        Resolve the callable target used for signature extraction.

        Args:
            obj: Candidate member object from classify_members.

        Contract:
            Strips `staticmethod` and `classmethod` wrappers when needed so
            `inspect.signature()` sees the underlying function.

        Returns:
            Any: Callable object passed to inspect.signature.
        """
        if isinstance(obj, staticmethod):
            return obj.__func__
        if isinstance(obj, classmethod):
            return obj.__func__
        return obj

    def _resolve_callable_target(self, obj: Any) -> Any:
        """
        Resolve the underlying callable for provenance and docstrings.

        Args:
            obj: Candidate member object.

        Contract:
            Resolves `staticmethod`, `classmethod`, and `property` wrappers to
            the underlying function when possible.

        Returns:
            Any: Underlying function when available, otherwise obj.
        """
        if isinstance(obj, staticmethod):
            return obj.__func__
        if isinstance(obj, classmethod):
            return obj.__func__
        if isinstance(obj, property):
            return obj.fget if obj.fget is not None else obj
        return obj

    def _is_callable_member(self, obj: Any) -> bool:
        """
        Decide whether a member should be treated as callable.

        Args:
            obj: Candidate member object.

        Contract:
            Treats wrapped static/class methods as callable even before wrapper
            resolution.

        Returns:
            bool: True if the member is callable or a method descriptor.
        """
        if isinstance(obj, (staticmethod, classmethod)):
            return True
        return callable(obj)

    def _is_descriptor(self, obj: Any) -> bool:
        """
        Determine whether an object behaves like a data descriptor.

        Args:
            obj: Candidate member object.

        Contract:
            Excludes `property` because properties are handled by their own
            branch in member normalization.

        Returns:
            bool: True if the object has descriptor methods and is not a property.
        """
        if isinstance(obj, property):
            return False
        return bool(getattr(obj, "__get__", None) or getattr(obj, "__set__", None) or getattr(obj, "__delete__", None))

    def _resolve_member_kind(self, name: str, obj: Any) -> str:
        """
        Normalize member kind for the tool-shaped schema.

        Args:
            name: Member name.
            obj: Member object.

        Contract:
            Returns a stable normalized kind label so downstream profiles do
            not need to reason about raw inspect/classify labels directly.

        Returns:
            str: Normalized member kind label.
        """
        if isinstance(obj, property):
            return "property"
        if isinstance(obj, classmethod):
            return "classmethod"
        if isinstance(obj, staticmethod):
            return "staticmethod"
        if self._is_descriptor(obj) and not callable(obj):
            return "descriptor"
        if callable(obj):
            return "method"
        if name.startswith("__") and name.endswith("__"):
            return "dunder"
        return "data"

    def _dynamic_access_flags(self, cls: Type) -> Dict[str, bool]:
        """
        Compute dynamic attribute access flags for a class.

        Args:
            cls: Class to inspect.

        Contract:
            Reports only the presence of dynamic access hooks in the MRO; it
            does not invoke them.

        Returns:
            Dict[str, bool]: Flags for __getattr__, __getattribute__, __setattr__.
        """
        return {
            "has_getattr": self._has_attribute_in_mro(cls, "__getattr__"),
            "has_getattribute": self._has_attribute_in_mro(cls, "__getattribute__"),
            "has_setattr": self._has_attribute_in_mro(cls, "__setattr__"),
        }

    def _has_attribute_in_mro(self, cls: Type, attr: str) -> bool:
        """
        Check whether a class or its bases define a given attribute.

        Args:
            cls: Class to inspect.
            attr: Attribute name to check.

        Contract:
            Checks only class `__dict__` entries across the MRO and does not
            trigger dynamic attribute access.

        Returns:
            bool: True if attr appears in any __dict__ in the MRO.
        """
        for base in inspect.getmro(cls):
            if attr in base.__dict__:
                return True
        return False
#endregion
