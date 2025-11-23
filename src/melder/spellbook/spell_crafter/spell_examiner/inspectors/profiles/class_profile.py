from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from melder.spellbook.spell_crafter.spell_examiner.inspectors.profiles.method_profile import MethodProfile

@dataclass
class ClassProfile:
    """Structured, IDE-friendly representation of ClassInspector output."""
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