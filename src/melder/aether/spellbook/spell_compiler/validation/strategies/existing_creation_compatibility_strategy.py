from __future__ import annotations

from typing import TYPE_CHECKING


from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.binding_profile import (
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
from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.general_profile import (
    SpellGeneralProfile,
)
if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.validation.spell_validation_context import (
        SpellValidationContext,
    )


class ExistingCreationCompatibilityStrategy(SpellValidationStrategy):
    """
    Validate existing-creation spells are wired with valid instances and policies.

    Purpose:
        An existing-creation spell binds an already-constructed object rather than a
        class Melder instantiates. This strategy enforces the invariants that make
        such a spell resolvable.

    Contract:
        Emits one error into `context.issues` per violated invariant:
        - EXISTING_CREATION_MISSING_INSTANCE: no bound instance.
        - EXISTING_CREATION_INVALID_EXISTENCE: existence is not `Existence.unique`.
        - EXISTING_CREATION_PROFILE_MISMATCH: no instance binding profile.
        - EXISTING_CREATION_PARAMETERS_PRESENT: it declares DI parameters (an
          existing object is never constructed, so it must not).
        Runs only when `spell.is_existing_creation` is true; it mutates nothing.

    Registration:
        MELDER KERNEL. A built-in strategy; registered, never bound.

    Subsystem Context:
        A built-in of the `validation/strategies` family, registered into
        `SpellValidationSystem`. It reads the Phase-1 requirements and the spell's
        binding profile.

    System Context:
        Phase 4 (validation) of the conjure pipeline. Existing-creation spells bypass
        the live Phase 8-11 codegen group, so this validation gate is the main
        structural check they pass through.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Phase-4 strategy for existing-creation spells: errors if there is no
        bound instance, existence is not unique, the instance binding profile is missing, or DI
        parameters are declared. No-op for non-existing-creation spells.
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

    def validate(self, context: SpellValidationContext) -> None:
        """
        Validate existing-creation spell wiring and policies.

        Contract:
            Honors the context cancel event. A no-op for non-existing-creation
            spells; for existing-creation spells it appends an error when there
            is no bound instance, existence is not unique, the instance binding
            profile is missing, or DI parameters are declared. Read-only;
            appends to `context.issues`.

        Args:
            context:
                Per-spell validation context (spell, cancel event).

        Returns:
            None.
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
        if isinstance(profile, (SpellGeneralProfile, SpellDetailedProfile)):
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
