from typing import Any, Dict, Optional, Union, Type
from melder.spellbook.bind.graph_builder.inspector.spell_examiner import (
    SpellExaminer,
    ClassProfile,
    MethodProfile,
)
from melder.utilities.interfaces import IBind
from melder.spellbook.spell_types.spell_types import SpellType
from melder.spellbook.existence.existence import Existence

class BoundSpell:
    def __init__(
        self,
        name: str,
        profile: Union[ClassProfile, MethodProfile, Dict[str, Any]],
        role: Optional[str] = None  # e.g., "interface", "model", etc.
    ):
        self.name = name
        self.profile = profile
        self.spell_type = self._detect_type(profile)
        self.role = role or self._infer_role()

    @staticmethod
    def _detect_type(profile: Any) -> str:
        if isinstance(profile, ClassProfile):
            return "class"
        elif isinstance(profile, MethodProfile):
            return "method"
        elif isinstance(profile, dict):
            return profile.get("object_type", "unknown")
        return "unknown"

    def _infer_role(self) -> Optional[str]:
        if isinstance(self.profile, ClassProfile):
            if self.profile.protocols.get("call"):
                return "interface"  # Heuristic fallback
            if self.profile.annotations:
                return "contract"
        return None

    def __repr__(self):
        return f"<BoundSpell name={self.name} type={self.spell_type} role={self.role}>"


class Bind(IBind):
    def __init__(self):
        super().__init__()
        self._registry: Dict[str, BoundSpell] = {}

    def bind_named(
        self,
        name: str,
        spell: Any,
        spellframe: Type = None,
        role: Optional[str] = None
    ) -> BoundSpell:
        profile = SpellExaminer(spell).inspect()
        bound = BoundSpell(name, profile, role=role)
        self._registry[name] = bound
        return bound

    def bind(self, spell: Any, spellframe: Type = None, role: Optional[str] = None) -> BoundSpell:
        name = getattr(spell, "__name__", f"unnamed_{id(spell)}")
        return self.bind_named(name, spell, spellframe, role=role)

    def get(self, name: str) -> Optional[BoundSpell]:
        return self._registry.get(name)

    def all(self) -> Dict[str, BoundSpell]:
        return self._registry

    def __repr__(self):
        return f"<Bind {len(self._registry)} spells>"

    def seal(self) -> None:
        """
        Seals the binding, preventing further modifications.
        """
        self._registry.clear()

