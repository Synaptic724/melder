from typing import Any, Optional
# Melder Imports
from melder.spellbook.spell import Spell
from melder.spellbook.spell_crafter.spell_examiner.inspectors.profiles.class_profile import ClassProfile
from melder.spellbook.spell_crafter.spell_examiner.inspectors.profiles.method_profile import MethodProfile
from melder.spellbook.spell_crafter.spell_examiner.profiles.binding_profile import SpellBindingProfile
from melder.spellbook.spell_crafter.spell_examiner.profiles.resolution_profile import SpellResolutionProfile
from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class SpellAIProfile(Cleanable):
    """
    AI-native view of a Spell.

    This is intended as the "badass" profile that can be fed into agents,
    mutation engines, analyzers, etc. It is a strict superset of the
    resolution semantics:
        * Always carries a SpellResolutionProfile.
        * Enriches that with deep introspection over the underlying class/callable.
        * Exposes hooks for future mutation lineage, runtime stats, etc.

    It is a live object graph, not a serialization.

    Contract:
        - Always carries binding and resolution profiles.
        - Optionally includes class/callable profiles, instance members, and
          dynamic-access flags.
        - Cleanup() is idempotent and clears all owned references.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "spell",
        "binding_profile",
        "resolution_profile",
        "class_profile",
        "callable_profile",
        "metadata",
        "instance_members",
        "dynamic_access",
    ]

    def __init__(
            self,
            *,
            spell: Spell,
            binding_profile: SpellBindingProfile,
            resolution_profile: SpellResolutionProfile,
            class_profile: Optional[ClassProfile] = None,
            callable_profile: Optional[MethodProfile] = None,
            metadata: Optional[dict[str, Any]] = None,
            instance_members: Optional[dict[str, dict[str, Any]]] = None,
            dynamic_access: Optional[dict[str, bool]] = None,
    ) -> None:
        """
        Initialize an AI profile snapshot.

        Args:
            spell: Spell owning the inspected object.
            binding_profile: Binding profile for the underlying object.
            resolution_profile: Resolution profile for the spell.
            class_profile: Optional class profile when the spell wraps a class.
            callable_profile: Optional method profile when the spell wraps a callable.
            metadata: Free-form metadata map (copied on assignment).
            instance_members: Optional instance-attribute inventory map.
            dynamic_access: Dynamic access flags for __getattr__/__getattribute__/__setattr__.
        """
        super().__init__()
        self.spell = spell
        self.binding_profile = binding_profile
        self.resolution_profile = resolution_profile
        self.class_profile = class_profile
        self.callable_profile = callable_profile
        self.metadata = dict(metadata) if metadata is not None else {}
        self.instance_members = dict(instance_members) if instance_members is not None else {}
        self.dynamic_access = dict(dynamic_access) if dynamic_access is not None else {}

    def cleanup(self) -> None:
        """
        Idempotently clear nested profiles and owned data.

        Contract:
            - Calls cleanup() on nested profiles when possible.
            - Clears and nulls all fields after cleanup.
        """
        if self._cleaned:
            return
        # Clean nested artifacts when they support cleanup
        for part in (
            self.binding_profile,
            self.resolution_profile,
            self.class_profile,
            self.callable_profile,
        ):
            if isinstance(part, Cleanable):
                try:
                    part.cleanup()
                except Exception:
                    pass
        if isinstance(self.metadata, dict):
            self.metadata.clear()
        self.spell = None
        self.binding_profile = None
        self.resolution_profile = None
        self.class_profile = None
        self.callable_profile = None
        self.metadata = None
        self.instance_members = None
        self.dynamic_access = None
        self._cleaned = True
