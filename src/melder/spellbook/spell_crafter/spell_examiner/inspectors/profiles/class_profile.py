from typing import Any, Dict, List, Optional

from mypy_extensions import mypyc_attr

# Melder Imports
from melder.spellbook.spell_crafter.spell_examiner.inspectors.profiles.method_profile import MethodProfile
from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
@mypyc_attr(native_class=True)
class ClassProfile(Cleanable):
    """
    Structured, IDE-friendly representation of ClassInspector output.

    Purpose:
        Provide a stable, serializable record of class-level inspection results
        for AI profile consumption.

    Contract:
        - Mirrors ClassInspector fields without invoking user code.
        - Provenance fields are best-effort and may be None.
        - Cleanup() is idempotent and clears all owned references.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "name",
        "qualname",
        "module",
        "mro",
        "bases",
        "annotations",
        "protocols",
        "slots",
        "origin_file",
        "origin_line",
        "origin_end_line",
        "source_preview",
        "source_text",
        "members",
        "methods",
        "is_dataclass",
        "decorated",
        "docstring_raw",
        "docstring_summary",
        "behavior_summary",
        "tags",
        "dynamic_access",
    ]

    def __init__(
            self,
            *,
            name: str,
            qualname: str,
            module: str,
            mro: Optional[List[str]] = None,
            bases: Optional[List[str]] = None,
            annotations: Optional[Dict[str, Any]] = None,
            protocols: Optional[Dict[str, bool]] = None,
            slots: Optional[List[str]] = None,
            origin_file: Optional[str] = None,
            origin_line: Optional[int] = None,
            origin_end_line: Optional[int] = None,
            source_preview: Optional[str] = None,
            source_text: Optional[str] = None,
            members: Optional[Dict[str, Dict[str, Any]]] = None,
            methods: Optional[Dict[str, MethodProfile]] = None,
            is_dataclass: bool = False,
            decorated: bool = False,
            docstring_raw: Optional[str] = None,
            docstring_summary: str = "",
            behavior_summary: str = "",
            tags: Optional[List[str]] = None,
            dynamic_access: Optional[Dict[str, bool]] = None,
    ) -> None:
        """
        Initialize a ClassProfile snapshot.

        Args:
            name: Class name.
            qualname: Qualified class name.
            module: Module path for the class.
            mro: Method resolution order names.
            bases: Base class names.
            annotations: Class-level annotations mapping.
            protocols: Protocol flags (len, iter, call, etc.).
            slots: Slots list when defined, otherwise None.
            origin_file: Source file path for the class definition.
            origin_line: Starting line number for the class definition.
            origin_end_line: Ending line number for the class definition.
            source_preview: Short preview of the class source.
            source_text: Full class source text when available.
            members: Member inventory map keyed by member name.
            methods: MethodProfile map keyed by member name.
            is_dataclass: Whether the class is a dataclass.
            decorated: Whether decorator wrapping was detected.
            docstring_raw: Raw class docstring.
            docstring_summary: Derived docstring summary (may be empty).
            behavior_summary: Derived behavior summary (may be empty).
            tags: Derived tag list (may be empty).
            dynamic_access: Dynamic access flags for __getattr__/__getattribute__/__setattr__.
        """
        super().__init__()
        self.name: str = name
        self.qualname: str = qualname
        self.module: str = module
        self.mro: Optional[List[str]] = list(mro) if mro is not None else []
        self.bases: Optional[List[str]] = list(bases) if bases is not None else []
        self.annotations: Optional[Dict[str, Any]] = dict(annotations) if annotations is not None else {}
        self.protocols: Optional[Dict[str, bool]] = dict(protocols) if protocols is not None else {}
        self.slots: Optional[List[str]] = list(slots) if slots is not None else None
        self.origin_file: Optional[str] = origin_file
        self.origin_line: Optional[int] = origin_line
        self.origin_end_line: Optional[int] = origin_end_line
        self.source_preview: Optional[str] = source_preview
        self.source_text: Optional[str] = source_text
        self.members: Optional[Dict[str, Dict[str, Any]]] = dict(members) if members is not None else {}
        self.methods: Optional[Dict[str, MethodProfile]] = dict(methods) if methods is not None else {}
        self.is_dataclass: bool = is_dataclass
        self.decorated: bool = decorated
        self.docstring_raw: Optional[str] = docstring_raw
        self.docstring_summary: str = docstring_summary
        self.behavior_summary: str = behavior_summary
        self.tags: Optional[List[str]] = list(tags) if tags is not None else []
        self.dynamic_access: Optional[Dict[str, bool]] = dict(dynamic_access) if dynamic_access is not None else {}

    def cleanup(self) -> None:
        """
        Idempotently clear nested profiles and owned data.

        Contract:
            - Calls cleanup() on nested MethodProfile instances when possible.
            - Clears owned collection fields before nulling references.
            - Drops detached provenance/source/member metadata rather than
              touching any live runtime object.
            - Leaves the profile unusable after cleanup.
        """
        if self._cleaned:
            return
        # Clean nested method profiles
        if self.methods is not None:
            for method in self.methods.values():
                if isinstance(method, Cleanable):
                    try:
                        method.cleanup()
                    except Exception:
                        pass
        # Clear collections
        for lst in (self.mro, self.bases, self.slots):
            if isinstance(lst, list):
                lst.clear()
        for dct in (self.annotations, self.protocols, self.members, self.methods):
            if isinstance(dct, dict):
                dct.clear()
        self._cleaned = True

        if isinstance(self.tags, list):
            self.tags.clear()
        if isinstance(self.dynamic_access, dict):
            self.dynamic_access.clear()

        del self.name
        del self.qualname
        del self.module
        del self.mro
        del self.bases
        del self.annotations
        del self.protocols
        del self.slots
        del self.origin_file
        del self.origin_line
        del self.origin_end_line
        del self.source_preview
        del self.source_text
        del self.members
        del self.methods
        del self.is_dataclass
        del self.decorated
        del self.docstring_raw
        del self.docstring_summary
        del self.behavior_summary
        del self.tags
        del self.dynamic_access
