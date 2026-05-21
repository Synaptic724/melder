# Melder Imports
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell

from mypy_extensions import mypyc_attr

from melder.aether.spellbook.spell_compiler.profiles.resolution_profile import SpellResolutionProfile
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.spell_requirements_finder import (
    SpellRequirementsFinder,
)
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
@mypyc_attr(native_class=True)
class ResolutionProfileStrategy:
    """
    Strategy for producing **SpellResolutionProfile** instances from
    fully formed Spell objects.

    This is where we hook into SpellRequirementsFinder and, later, into
    symbolic graph / frame / validation phases.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = ()

    def __init__(self) -> None:
        """
        Initialize one resolution-profile strategy.

        Returns:
            None.
        """
        pass

    def build_profile(self, spell: Spell) -> SpellResolutionProfile:
        """
        Build the resolution profile for one fully formed spell.

        Contract:
            - Uses `SpellRequirementsFinder` to populate the phase-1
              requirements artifact immediately.
            - Leaves the later symbolic-graph, resolution-frame, and
              validation artifacts as `None` until those phases are wired into
              the broader spell lifecycle.

        Returns:
            SpellResolutionProfile: Resolution profile seeded with the current
            phase-1 requirements artifact.
        """
        # Phase 1 - requirements
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
