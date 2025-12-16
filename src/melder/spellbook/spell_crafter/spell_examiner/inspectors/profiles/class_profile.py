from typing import Any, Dict, List, Optional
# Melder Imports
from melder.spellbook.spell_crafter.spell_examiner.inspectors.profiles.method_profile import MethodProfile
from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class ClassProfile(Cleanable):
    """Structured, IDE-friendly representation of ClassInspector output."""
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
        "source_preview",
        "members",
        "methods",
        "is_dataclass",
        "decorated",
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
            source_preview: Optional[str] = None,
            members: Optional[Dict[str, Dict[str, Any]]] = None,
            methods: Optional[Dict[str, MethodProfile]] = None,
            is_dataclass: bool = False,
            decorated: bool = False,
    ) -> None:
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
        self.source_preview = source_preview
        self.members = dict(members) if members is not None else {}
        self.methods = dict(methods) if methods is not None else {}
        self.is_dataclass = is_dataclass
        self.decorated = decorated

    def cleanup(self) -> None:
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
        self.source_preview = None
        self.members = None
        self.methods = None
        self.is_dataclass = None
        self.decorated = None
        self._cleaned = True
