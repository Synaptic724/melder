from typing import Any, Optional, Type, TypeVar

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.spellbook.spell import Spell
from melder.spellbook.spell_crafter.spell_examiner.profiles.binding_profile import (
    SpellBindingProfile,
)
from melder.spellbook.spell_crafter.spell_examiner.profiles.resolution_profile import (
    SpellResolutionProfile,
)
from melder.spellbook.spell_crafter.spell_examiner.strategies.binding_profile_strategy import (
    BindingProfileStrategy,
)
from melder.spellbook.spell_crafter.spell_examiner.strategies.resolution_profile_strategy import (
    ResolutionProfileStrategy,
)
from melder.utilities.general_base.cleanable import Cleanable


GeneralProfileT = TypeVar("GeneralProfileT", bound="SpellGeneralProfile")


class SpellGeneralProfile(Cleanable):
    """
    Purpose:
        Represent the normal combined spell profile in a lifecycle-aware form.

    Contract:
        - Phase 1 builds the binding profile from a raw candidate object.
        - Phase 2 completes the same profile object with resolution data after
          a real `Spell` exists.
        - Binding and resolution remain separate internal detail artifacts and
          are exposed through this profile for downstream consumers.
        - Cleanup cascades to the nested binding and resolution profiles.

    Lifecycle:
        The profile may exist in a partially built state after phase 1. Once
        `complete_with_spell(...)` succeeds, the profile is fully usable as the
        spell-owned `.profile` payload.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "binding_profile",
        "resolution_profile",
    ]

    def __init__(
            self,
            *,
            binding_profile: SpellBindingProfile,
            resolution_profile: Optional[SpellResolutionProfile] = None,
    ) -> None:
        """
        Initialize one general spell profile.

        Args:
            binding_profile:
                Binding profile for the candidate object.
            resolution_profile:
                Resolution profile for the spell when phase 2 has completed.

        Returns:
            None.
        """
        super().__init__()
        self.binding_profile = binding_profile
        self.resolution_profile = resolution_profile

    @classmethod
    def create_from_target(
            cls: Type[GeneralProfileT],
            target: Any,
            show_dunders: bool = False,
            max_repr: int = 120,
    ) -> GeneralProfileT:
        """
        Create one general profile from a raw candidate or a fully formed spell.

        Args:
            target:
                Raw candidate object or a fully formed `Spell`.
            show_dunders:
                Whether dunder members should be included in binding reflection.
            max_repr:
                Maximum representation length passed to the binding strategy.

        Returns:
            GeneralProfileT:
                New profile object. If `target` is a `Spell`, the returned
                profile is already fully completed.
        """
        binding_target = target.spell if isinstance(target, Spell) else target
        binding_profile = BindingProfileStrategy(
            show_dunders=show_dunders,
            max_repr=max_repr,
        ).build_profile(binding_target)
        profile = cls(binding_profile=binding_profile)
        if isinstance(target, Spell):
            profile.complete_with_spell(target)
        return profile

    def complete_with_spell(self, spell: Spell) -> None:
        """
        Complete phase 2 of the profile lifecycle using a real `Spell`.

        Args:
            spell:
                Fully formed spell whose runtime metadata should drive the
                resolution-profile build.

        Returns:
            None.

        """
        self.check_cleaned()
        if self.resolution_profile is not None:
            return
        self.resolution_profile = ResolutionProfileStrategy().build_profile(spell)

    def cleanup(self) -> None:
        """
        Idempotently clean the nested general-profile artifacts.

        Returns:
            None.
        """
        if self._cleaned:
            return
        for profile in (self.binding_profile, self.resolution_profile):
            if isinstance(profile, Cleanable):
                try:
                    profile.cleanup()
                except Exception:
                    pass
        self.binding_profile = None
        self.resolution_profile = None
        self._cleaned = True
