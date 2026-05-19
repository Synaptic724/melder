from __future__ import annotations

from mypy_extensions import mypyc_attr

from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.spellbook.spell_crafter.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.spellbook.spell_crafter.validation.spell_validation_context import (
    SpellValidationContext,
)
from melder.spellbook.spell_crafter.validation.spell_validation_issue import (
    SpellValidationIssue,
)
from melder.spellbook.spell_crafter.validation.strategies.spell_validation_strategy import (
    SpellValidationStrategy,
)
from melder.utilities.helpers.general_helpers import SpellInputUtils

@mypyc_attr(native_class=True)
class SpellMapShapeValidationStrategy(SpellValidationStrategy):
    """
    Validate SpellMap defaults for structural correctness.

    This checks that SpellMap defaults are present, have valid targets,
    and use normalized binding names.
    """

    __slots__ = SpellValidationStrategy.__slots__

    def __init__(self) -> None:
        """
        Initialize the SpellMap shape validation strategy.
        """
        super().__init__(
            name="spellmap_shape_validation",
            description="Validates SpellMap defaults for required fields and normalized binding names.",
        )

    def validate(self, context: "SpellValidationContext") -> None:
        """
        Validate SpellMap defaults attached to constructor parameters.
        """
        self.check_cleaned()

        cancel_event = context.cancel_event
        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()

        requirements = context.requirements
        if requirements is None:
            return

        spell = context.spell

        for param in requirements.parameters:
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()

            if param.di_shape is not ParameterDIShape.SPELLMAP_DEFAULT:
                continue

            spellmap = param.spellmap_default
            if spellmap is None:
                context.issues.append(
                    SpellValidationIssue(
                        severity="error",
                        code="SPELLMAP_DEFAULT_MISSING",
                        message=(
                            f"Parameter {param.name!r} on spell {spell.spell_name!r} "
                            "is marked as SpellMap default but no SpellMap instance was captured."
                        ),
                        details={"parameter_name": param.name},
                    )
                )
                continue

            if not isinstance(spellmap, SpellMap):
                context.issues.append(
                    SpellValidationIssue(
                        severity="error",
                        code="SPELLMAP_DEFAULT_INVALID",
                        message=(
                            f"Parameter {param.name!r} on spell {spell.spell_name!r} "
                            f"has an invalid SpellMap default: {spellmap!r}."
                        ),
                        details={"parameter_name": param.name},
                    )
                )
                continue

            if spellmap.spell is None and spellmap.spellframe is None:
                context.issues.append(
                    SpellValidationIssue(
                        severity="error",
                        code="SPELLMAP_MISSING_TARGET",
                        message=(
                            f"Parameter {param.name!r} on spell {spell.spell_name!r} "
                            "has a SpellMap default with no spell or spellframe target."
                        ),
                        details={"parameter_name": param.name},
                    )
                )

            binding_name = spellmap.binding_name
            if binding_name is not None:
                normalized = SpellInputUtils.normalize_binding_name(binding_name)
                if normalized != binding_name:
                    context.issues.append(
                        SpellValidationIssue(
                            severity="warning",
                            code="SPELLMAP_BINDING_NAME_NOT_NORMALIZED",
                            message=(
                                f"Parameter {param.name!r} on spell {spell.spell_name!r} "
                                f"uses a SpellMap binding_name {binding_name!r} that is not normalized. "
                                f"Use {normalized!r} for consistent lookup behavior."
                            ),
                            details={
                                "parameter_name": param.name,
                                "binding_name": binding_name,
                                "normalized_binding_name": normalized,
                            },
                        )
                    )
