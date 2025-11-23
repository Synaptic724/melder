from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
# Melder Imports
from melder.spellbook.spell import Spell
from melder.spellbook.spell_crafter.spell_examiner.inspectors.profiles.class_profile import ClassProfile
from melder.spellbook.spell_crafter.spell_examiner.inspectors.profiles.method_profile import (
    MethodProfile,
)
from melder.spellbook.spell_crafter.spell_examiner.profiles.binding_profile import SpellBindingProfile
from melder.spellbook.spell_crafter.spell_examiner.profiles.resolution_profile import SpellResolutionProfile


@dataclass
class SpellAIProfile:
    """
    AI-native view of a Spell.

    This is intended as the "badass" profile that can be fed into agents,
    mutation engines, analyzers, etc. It is a **strict superset** of the
    resolution semantics:

        * It always carries a SpellResolutionProfile.
        * It enriches that with deep introspection over the underlying
          class / callable.
        * It exposes hooks for future mutation lineage, runtime stats, etc.

    It is NOT JSON. It is a live object graph that you can slice, transform,
    encode into TOON, or serialize however you want later.
    """

    spell: Spell

    binding_profile: SpellBindingProfile
    resolution_profile: SpellResolutionProfile

    # Deep introspection (optional, depending on spell kind)
    class_profile: Optional[ClassProfile] = None
    callable_profile: Optional[MethodProfile] = None

    # Future: mutation lineage, version graph, runtime stats, etc.
    metadata: dict[str, Any] = field(default_factory=dict)
