from __future__ import annotations

from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.spell_examiner.profiles.binding_profile import (
    InstanceBindingProfile,
    OtherBindingProfile,
)
from melder.spellbook.spell_crafter.validation.spell_validation_issue import (
    SpellValidationIssue,
)
from melder.spellbook.spell_crafter.validation.strategies.spell_validation_strategy import (
    SpellValidationStrategy,
)
from melder.utilities.interfaces.interfaces import (
    ISpellDetailedProfile,
    ISpellGeneralProfile,
)


class ExistingCreationCompatibilityStrategy(SpellValidationStrategy):
    """
    Validate existing-creation spells are wired with valid instances and policies.
    """

    __slots__ = SpellValidationStrategy.__slots__

    def __init__(self) -> None:
        """
        Initialize the existing-creation compatibility strategy.
        """
        super().__init__(
            name="existing_creation_compatibility",
            description="Checks existing-creation spells for instance presence and compatible policies.",
        )

    def validate(self, context: "SpellValidationContext") -> None:
        """
        Validate existing-creation spell wiring and policies.
        """
        self.check_cleaned()

        cancel_event = context.cancel_event
        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()

        spell = context.spell
        if not spell.is_existing_creation:
            return

        if not spell.has_existing_object:
            context.issues.append(
                SpellValidationIssue(
                    severity="error",
                    code="EXISTING_CREATION_MISSING_INSTANCE",
                    message=(
                        f"Existing-creation spell {spell.spell_name!r} has no bound instance."
                    ),
                    details={},
                )
            )

        if spell.existence is not Existence.unique:
            context.issues.append(
                SpellValidationIssue(
                    severity="error",
                    code="EXISTING_CREATION_INVALID_EXISTENCE",
                    message=(
                        f"Existing-creation spell {spell.spell_name!r} uses "
                        f"existence {spell.existence!r}, but only Existence.unique is allowed."
                    ),
                    details={},
                )
            )

        profile = spell.profile
        binding_profile = profile
        if isinstance(profile, (ISpellGeneralProfile, ISpellDetailedProfile)):
            binding_profile = profile.binding_profile
        if binding_profile is None or not isinstance(
                binding_profile,
                (InstanceBindingProfile, OtherBindingProfile),
        ):
            context.issues.append(
                SpellValidationIssue(
                    severity="error",
                    code="EXISTING_CREATION_PROFILE_MISMATCH",
                    message=(
                        f"Existing-creation spell {spell.spell_name!r} is missing an instance binding profile."
                    ),
                    details={},
                )
            )

        requirements = context.requirements
        if requirements is not None and requirements.parameters:
            context.issues.append(
                SpellValidationIssue(
                    severity="error",
                    code="EXISTING_CREATION_PARAMETERS_PRESENT",
                    message=(
                        f"Existing-creation spell {spell.spell_name!r} has constructor parameters, "
                        "but existing creations should not declare DI parameters."
                    ),
                    details={"parameter_count": len(requirements.parameters)},
                )
            )
