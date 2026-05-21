from __future__ import annotations

import inspect
from typing import TYPE_CHECKING

from mypy_extensions import mypyc_attr

from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.binding_profile import (
    CallableBindingProfile,
    ClassBindingProfile,
    InstanceBindingProfile,
    OtherBindingProfile,
)
from melder.aether.spellbook.spell_compiler.validation.spell_validation_issue import (
    SpellValidationIssue,
)
from melder.aether.spellbook.spell_compiler.validation.strategies.spell_validation_strategy import (
    SpellValidationStrategy,
)
from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.detailed_profile import (
    SpellDetailedProfile,
)
if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.validation.spell_validation_context import (
        SpellValidationContext,
    )
from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.general_profile import (
    SpellGeneralProfile,
)

@mypyc_attr(native_class=True)
class CallableProfileHygieneStrategy(SpellValidationStrategy):
    """
    Validate that the bound spell target matches its binding profile and type.

    This catches mismatches such as class spells bound to non-classes or
    callable spells missing callable metadata.
    """

    __slots__ = SpellValidationStrategy.__slots__

    def __init__(self) -> None:
        """
        Initialize the callable/profile hygiene strategy.
        """
        super().__init__(
            name="callable_profile_hygiene",
            description="Ensures spell targets match binding profiles and callable/class expectations.",
        )

    def validate(self, context: SpellValidationContext) -> None:
        """
        Validate that the spell target aligns with its binding profile.
        """
        self.check_cleaned()

        cancel_event = context.cancel_event
        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()

        spell = context.spell
        profile = spell.profile
        binding_profile = profile
        if isinstance(profile, (SpellGeneralProfile, SpellDetailedProfile)):
            binding_profile = profile.binding_profile

        if binding_profile is None:
            context.issues.append(
                SpellValidationIssue(
                    severity="error",
                    code="MISSING_BINDING_PROFILE",
                    message=(
                        f"Spell {spell.spell_name!r} has no binding profile attached. "
                        "Binding metadata is required to validate callable/class targets."
                    ),
                    details={},
                )
            )
            return

        if spell.is_existing_creation:
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
            if not isinstance(binding_profile, (InstanceBindingProfile, OtherBindingProfile)):
                context.issues.append(
                    SpellValidationIssue(
                        severity="error",
                        code="EXISTING_CREATION_PROFILE_MISMATCH",
                        message=(
                            f"Existing-creation spell {spell.spell_name!r} has a non-instance binding profile."
                        ),
                        details={},
                    )
                )
            return

        if spell.is_class_spell:
            if not inspect.isclass(spell.spell):
                context.issues.append(
                    SpellValidationIssue(
                        severity="error",
                        code="NON_CLASS_SPELL_TARGET",
                        message=(
                            f"Class spell {spell.spell_name!r} is bound to a non-class target."
                        ),
                        details={},
                    )
                )
            if not isinstance(binding_profile, ClassBindingProfile):
                context.issues.append(
                    SpellValidationIssue(
                        severity="error",
                        code="CLASS_PROFILE_MISSING",
                        message=(
                            f"Class spell {spell.spell_name!r} is missing a ClassBindingProfile."
                        ),
                        details={},
                    )
                )
            return

        if spell.is_method_spell or spell.is_lambda_spell:
            if not callable(spell.spell):
                context.issues.append(
                    SpellValidationIssue(
                        severity="error",
                        code="NON_CALLABLE_SPELL_TARGET",
                        message=(
                            f"Callable spell {spell.spell_name!r} is bound to a non-callable target."
                        ),
                        details={},
                    )
                )
            if not isinstance(binding_profile, CallableBindingProfile):
                context.issues.append(
                    SpellValidationIssue(
                        severity="error",
                        code="CALLABLE_PROFILE_MISSING",
                        message=(
                            f"Callable spell {spell.spell_name!r} is missing a CallableBindingProfile."
                        ),
                        details={},
                    )
                )
