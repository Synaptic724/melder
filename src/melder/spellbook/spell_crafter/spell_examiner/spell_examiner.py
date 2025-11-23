from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Optional, Union

from melder.spellbook.spell import Spell
from melder.spellbook.spell_crafter.spell_examiner.profiles.binding_profile import (
    SpellBindingProfile,
)
from melder.spellbook.spell_crafter.spell_examiner.profiles.resolution_profile import (
    SpellResolutionProfile,
)
from melder.spellbook.spell_crafter.spell_examiner.profiles.ai_profile import (
    SpellAIProfile,
)
from melder.spellbook.spell_crafter.spell_examiner.strategies.ai_profile_strategy import AIProfileStrategy
from melder.spellbook.spell_crafter.spell_examiner.strategies.resolution_profile_strategy import AIProfileStrategy
from melder.spellbook.spell_crafter.spell_examiner.strategies.binding_profile_strategy import BindingProfileStrategy



class SpellExaminationKind(Enum):
    """
    High-level mode selector for SpellExaminer.

    This enum exists so you can easily add more profile types later
    without changing the overall shape of the API.
    """

    BINDING = auto()
    RESOLUTION = auto()
    AI = auto()


@dataclass
class SpellExaminer:
    """
    Central façade over profile strategies.

    Responsibilities:
        * Provide a clean, mode-based API:
            - binding_profile_for_object(...)
            - resolution_profile_for_spell(...)
            - ai_profile_for_spell(...)
        * Delegate real work to pluggable strategies.
        * Stay dumb and composable – no hard coupling to Bind or Meld.

    This class does **not** own any global state. Each instance is a thin
    coordinator; strategies are stateless or short-lived.
    """

    show_dunders: bool = False
    max_repr: int = 120

    def __post_init__(self) -> None:
        self._binding_strategy = BindingProfileStrategy(
            show_dunders=self.show_dunders,
            max_repr=self.max_repr,
        )
        self._resolution_strategy = ResolutionProfileStrategy()
        self._ai_strategy = AIProfileStrategy(
            show_dunders=self.show_dunders,
            max_repr=self.max_repr,
        )

    # ------------------------------------------------------------------ #
    # Explicit mode-specific entrypoints
    # ------------------------------------------------------------------ #

    def binding_profile_for_object(self, candidate: Any) -> SpellBindingProfile:
        """
        Produce a SpellBindingProfile from a raw user-provided object.

        This is the entrypoint Bind will eventually use.
        """
        return self._binding_strategy.build_profile(candidate)

    def resolution_profile_for_spell(self, spell: Spell) -> SpellResolutionProfile:
        """
        Produce a SpellResolutionProfile for a fully-formed Spell.

        This will be integrated into the resolution / conjure pipeline.
        """
        return self._resolution_strategy.build_profile(spell)

    def ai_profile_for_spell(
            self,
            spell: Spell,
            *,
            binding_profile: Optional[SpellBindingProfile] = None,
            resolution_profile: Optional[SpellResolutionProfile] = None,
    ) -> SpellAIProfile:
        """
        Produce a SpellAIProfile for a Spell.

        If AI-native mode is enabled, the conjure pipeline can call this
        to materialize the heavy, agent-facing view of the spell, including
        deep introspection and resolution semantics.
        """
        return self._ai_strategy.build_profile(
            spell=spell,
            binding_profile=binding_profile,
            resolution_profile=resolution_profile,
        )

    # ------------------------------------------------------------------ #
    # Generic dispatch if you want a single entrypoint
    # ------------------------------------------------------------------ #

    def examine(
            self,
            target: Union[Any, Spell],
            kind: SpellExaminationKind,
            *,
            binding_profile: Optional[SpellBindingProfile] = None,
            resolution_profile: Optional[SpellResolutionProfile] = None,
    ) -> Union[SpellBindingProfile, SpellResolutionProfile, SpellAIProfile]:
        """
        Generic dispatcher if you want a single public entrypoint that can
        produce any profile type.

        Typical usage:
            examiner = SpellExaminer()
            binding = examiner.examine(MyService, SpellExaminationKind.BINDING)
        """
        if kind is SpellExaminationKind.BINDING:
            return self.binding_profile_for_object(target)

        if kind is SpellExaminationKind.RESOLUTION:
            if not isinstance(target, Spell):
                raise TypeError(
                    "Resolution examination requires a Spell instance as target."
                )
            return self.resolution_profile_for_spell(target)

        if kind is SpellExaminationKind.AI:
            if not isinstance(target, Spell):
                raise TypeError(
                    "AI examination requires a Spell instance as target."
                )
            return self.ai_profile_for_spell(
                spell=target,
                binding_profile=binding_profile,
                resolution_profile=resolution_profile,
            )

        raise ValueError(f"Unsupported SpellExaminationKind: {kind!r}")
