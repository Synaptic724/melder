# melder/spellbook/spell_crafter/spell_examiner/spell_examiner.py

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
from melder.spellbook.spell_crafter.spell_examiner.strategies.binding_profile_strategy import (
    BindingProfileStrategy,
)
from melder.spellbook.spell_crafter.spell_examiner.strategies.resolution_profile_strategy import (
    ResolutionProfileStrategy,
)
from melder.spellbook.spell_crafter.spell_examiner.strategies.ai_profile_strategy import (
    AIProfileStrategy,
)


class SpellExaminationKind(Enum):
    """
    High–level modes of spell examination.

    * BINDING    – Lightweight structural view used by `Bind` to classify spells,
                   enforce binding rules, and compute fingerprints.
    * RESOLUTION – Resolution–time view of the spell’s dependencies and DAG edges.
    * AI         – Heavy, AI–oriented profile that merges binding + resolution +
                   deep reflection profiles (ClassProfile / MethodProfile).
    """

    BINDING = auto()
    RESOLUTION = auto()
    AI = auto()


@dataclass
class SpellExaminer:
    """
    Facade over the spell–examination strategies.

    This keeps the binding / resolution / AI profiles decoupled:

    * BindingProfileStrategy        → SpellBindingProfile
    * ResolutionProfileStrategy     → SpellResolutionProfile
    * AIProfileStrategy             → SpellAIProfile
    """

    show_dunders: bool = False
    max_repr: int = 120

    # ----------------------------------------------------------------------
    # Binding layer
    # ----------------------------------------------------------------------
    def binding_profile_for_object(self, candidate: Any) -> SpellBindingProfile:
        """
        Build a lightweight `SpellBindingProfile` for any candidate object.

        This is the **only** thing `Bind` needs at registration time.
        """
        strategy = BindingProfileStrategy(
            show_dunders=self.show_dunders,
            max_repr=self.max_repr,
        )
        return strategy.build_profile(candidate)

    # Optional backwards-compat alias (so you can keep `.inspect(...)` in Bind).
    def inspect(self, candidate: Any) -> SpellBindingProfile:
        """
        Backwards–compatible alias for `binding_profile_for_object`.

        Old code that expected `.inspect()` can now simply work with the
        new `SpellBindingProfile` instead of `ClassProfile / MethodProfile`.
        """
        return self.binding_profile_for_object(candidate)

    # ----------------------------------------------------------------------
    # Resolution layer
    # ----------------------------------------------------------------------
    def resolution_profile_for_spell(self, spell: Spell) -> SpellResolutionProfile:
        """
        Build a `SpellResolutionProfile` from a fully registered Spell instance.

        This is used by the Spellbook / DAG builder to understand dependency
        edges (constructor parameters, field injections, etc.).
        """
        if not isinstance(spell, Spell):
            raise TypeError(
                "resolution_profile_for_spell expects a Spell instance. "
                f"Got: {type(spell)!r}"
            )

        strategy = ResolutionProfileStrategy()
        return strategy.build_profile(spell)

    # ----------------------------------------------------------------------
    # AI layer
    # ----------------------------------------------------------------------
    def ai_profile_for_spell(
            self,
            spell: Spell,
            *,
            binding_profile: Optional[SpellBindingProfile] = None,
            resolution_profile: Optional[SpellResolutionProfile] = None,
    ) -> SpellAIProfile:
        """
        Build the full AI profile for a spell.

        This merges:
        * Binding profile  → lightweight structural view.
        * Resolution       → how the spell participates in the DAG.
        * Deep reflection  → ClassProfile / MethodProfile via the inspector layer.
        """
        if not isinstance(spell, Spell):
            raise TypeError(
                "ai_profile_for_spell expects a Spell instance. "
                f"Got: {type(spell)!r}"
            )

        if binding_profile is None:
            binding_profile = self.binding_profile_for_object(spell.spell)

        if resolution_profile is None:
            resolution_profile = self.resolution_profile_for_spell(spell)

        strategy = AIProfileStrategy(
            show_dunders=self.show_dunders,
            max_repr=self.max_repr,
        )
        return strategy.build_profile(
            spell=spell,
            binding_profile=binding_profile,
            resolution_profile=resolution_profile,
        )

    # ----------------------------------------------------------------------
    # Unified facade
    # ----------------------------------------------------------------------
    def examine(
            self,
            target: Union[Any, Spell],
            kind: SpellExaminationKind,
            *,
            binding_profile: Optional[SpellBindingProfile] = None,
            resolution_profile: Optional[SpellResolutionProfile] = None,
    ) -> Union[SpellBindingProfile, SpellResolutionProfile, SpellAIProfile]:
        """
        Unified entry point over the three examination modes.

        * BINDING    – `target` can be a raw class/function/instance or a Spell.
        * RESOLUTION – `target` must be a Spell.
        * AI         – `target` must be a Spell.
        """
        if kind is SpellExaminationKind.BINDING:
            # Allow passing a Spell directly: we peel back to its underlying object.
            if isinstance(target, Spell):
                target = target.spell
            return self.binding_profile_for_object(target)

        if kind is SpellExaminationKind.RESOLUTION:
            if not isinstance(target, Spell):
                raise TypeError(
                    "Resolution examination requires a Spell instance as target."
                )
            return self.resolution_profile_for_spell(target)

        if kind is SpellExaminationKind.AI:
            if not isinstance(target, Spell):
                raise TypeError("AI examination requires a Spell instance as target.")
            return self.ai_profile_for_spell(
                target,
                binding_profile=binding_profile,
                resolution_profile=resolution_profile,
            )

        raise ValueError(f"Unknown SpellExaminationKind: {kind!r}")
