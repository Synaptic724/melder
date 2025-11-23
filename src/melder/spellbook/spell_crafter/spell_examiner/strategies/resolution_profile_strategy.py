from __future__ import annotations
from dataclasses import dataclass

from melder.spellbook.spell_crafter.spell_examiner.profiles.resolution_profile import SpellResolutionProfile
# Melder Imports
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.spell_requirements_finder import (
    SpellRequirementsFinder,
)
from melder.utilities.interfaces.interfaces import ISpell


@dataclass
class ResolutionProfileStrategy:
    """
    Strategy for producing **SpellResolutionProfile** instances from
    fully-formed Spell objects.

    This is where we hook into SpellRequirementsFinder and, later, into
    symbolic graph / frame / validation phases.
    """

    def build_profile(self, spell: ISpell) -> SpellResolutionProfile:
        # Phase 1 – requirements
        finder = SpellRequirementsFinder(spell)
        requirements = finder.build_requirements(cancel_event=None)

        # NOTE:
        # -----
        # SymbolicGraph / ResolutionFrame / Validation are left as None for now.
        # They will be populated by the per-spell phase methods once those
        # phases are implemented on Spell.
        return SpellResolutionProfile(
            spell_id=spell.spell_id,
            existence=spell.existence,
            spellframe=spell.spellframe,
            binding_name=spell.binding_name,
            requirements=requirements,
            symbolic_graph=None,
            resolution_frame=None,
            validation=None,
        )