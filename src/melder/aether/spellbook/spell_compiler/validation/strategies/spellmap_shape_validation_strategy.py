from __future__ import annotations

from typing import TYPE_CHECKING


from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.aether.spellbook.spell_compiler.validation.spell_validation_issue import (
    SpellValidationIssue,
)
from melder.aether.spellbook.spell_compiler.validation.strategies.spell_validation_strategy import (
    SpellValidationStrategy,
)
from melder.utilities.helpers.general_helpers import SpellInputUtils
if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.validation.spell_validation_context import (
        SpellValidationContext,
    )


class SpellMapShapeValidationStrategy(SpellValidationStrategy):
    """
    Validate SpellMap defaults for structural correctness.

    This checks that SpellMap defaults are present, have valid targets,
    and use normalized binding names.

    Contract:
        Runs per SPELLMAP_DEFAULT parameter. Errors on SPELLMAP_DEFAULT_MISSING (no
        captured SpellMap), SPELLMAP_DEFAULT_INVALID (default is not a SpellMap), and
        SPELLMAP_MISSING_TARGET (neither spell nor spellframe). Warns
        SPELLMAP_BINDING_NAME_NOT_NORMALIZED. Validation only; mutates nothing.

    Registration:
        MELDER KERNEL. A built-in strategy; registered, never bound.

    Subsystem Context:
        A built-in of the `validation/strategies` family; it inspects the SpellMap
        defaults captured on Phase-1 parameters and normalizes binding names via
        `SpellInputUtils`.

    System Context:
        Phase 4 (validation) of the conjure pipeline, guarding the explicit
        SpellMap DI descriptor shape.
    """

    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Phase-4 strategy for SPELLMAP_DEFAULT params: errors on missing / "
        "invalid SpellMap or a SpellMap with no spell/spellframe target; warns when binding_name "
        "is not normalized. Validation only."
    )
    __slots__ = SpellValidationStrategy.__slots__

    def __init__(self) -> None:
        """
        Initialize the SpellMap shape validation strategy.
        """
        super().__init__(
            name="spellmap_shape_validation",
            description="Validates SpellMap defaults for required fields and normalized binding names.",
        )

    def validate(self, context: SpellValidationContext) -> None:
        """
        Validate SpellMap defaults attached to constructor parameters.

        Contract:
            Honors the context cancel event, returns early when the spell has no
            requirements, and otherwise scans each parameter's SpellMap default,
            appending issues for missing required fields and non-normalized
            binding names. Read-only; appends to `context.issues` rather than
            raising.

        Args:
            context:
                Per-spell validation context (requirements, spell, cancel event).

        Returns:
            None.
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
