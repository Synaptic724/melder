from typing import Any, Dict, List, Optional
# Melder Imports
from melder.spellbook.spell_crafter.spell_examiner.inspectors.profiles.method_profile import MethodProfile
from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

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
        self.name = name
        self.qualname = qualname
        self.module = module
        self.mro = list(mro) if mro is not None else []
        self.bases = list(bases) if bases is not None else []
        self.annotations = dict(annotations) if annotations is not None else {}
        self.protocols = dict(protocols) if protocols is not None else {}
        self.slots = list(slots) if slots is not None else None
        self.origin_file = origin_file
        self.origin_line = origin_line
        self.origin_end_line = origin_end_line
        self.source_preview = source_preview
        self.source_text = source_text
        self.members = dict(members) if members is not None else {}
        self.methods = dict(methods) if methods is not None else {}
        self.is_dataclass = is_dataclass
        self.decorated = decorated
        self.docstring_raw = docstring_raw
        self.docstring_summary = docstring_summary
        self.behavior_summary = behavior_summary
        self.tags = list(tags) if tags is not None else []
        self.dynamic_access = dict(dynamic_access) if dynamic_access is not None else {}

    def cleanup(self) -> None:
        """
        Idempotently clear nested profiles and owned data.

        Contract:
            - Calls cleanup() on nested MethodProfile instances when possible.
            - Clears and nulls all fields after cleanup.
        """
        if self._cleaned:
            return
        # Clean nested method profiles
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
        # Drop references
        self.name = None
        self.qualname = None
        self.module = None
        self.mro = None
        self.bases = None
        self.annotations = None
        self.protocols = None
        self.slots = None
        self.origin_file = None
        self.origin_line = None
        self.origin_end_line = None
        self.source_preview = None
        self.source_text = None
        self.members = None
        self.methods = None
        self.is_dataclass = None
        self.decorated = None
        self.docstring_raw = None
        self.docstring_summary = None
        self.behavior_summary = None
        self.tags = None
        self.dynamic_access = None
        self._cleaned = True
