from __future__ import annotations

import inspect
import typing
from typing import TYPE_CHECKING, Any

from mypy_extensions import mypyc_attr

from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.aether.spellbook.spell_compiler.validation.spell_validation_issue import (
    SpellValidationIssue,
)
from melder.aether.spellbook.spell_compiler.validation.strategies.spell_validation_strategy import (
    SpellValidationStrategy,
)
if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.validation.spell_validation_context import (
        SpellValidationContext,
    )

@mypyc_attr(native_class=True)
class ParameterPolicyStrategy(SpellValidationStrategy):
    """
    Enforce parameter policies around DI usage.

    This strategy ensures DI is not requested on variadic parameters and
    checks for contradictory DI classifications.
    """

    __slots__ = SpellValidationStrategy.__slots__

    def __init__(self) -> None:
        """
        Initialize the parameter policy strategy.
        """
        super().__init__(
            name="parameter_policy",
            description="Flags DI usage on variadic parameters and inconsistent DI annotations.",
        )

    def validate(self, context: SpellValidationContext) -> None:
        """
        Validate parameter shapes against DI policy constraints.
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

            annotation = param.annotation

            if param.is_var_positional or param.is_var_keyword:
                if annotation is not None and self._looks_like_di_target(annotation):
                    context.issues.append(
                        SpellValidationIssue(
                            severity="error",
                            code="VARIADIC_DI_UNSUPPORTED",
                            message=(
                                f"Parameter {param.name!r} on spell {spell.spell_name!r} "
                                "is variadic but annotated for DI. Variadic DI is not supported."
                            ),
                            details={"parameter_name": param.name},
                        )
                    )
                continue

            if param.di_shape in (
                ParameterDIShape.SINGLE_BY_ANNOTATION,
                ParameterDIShape.COLLECTION_BY_ANNOTATION,
            ):
                if annotation is None:
                    context.issues.append(
                        SpellValidationIssue(
                            severity="error",
                            code="DI_MISSING_ANNOTATION",
                            message=(
                                f"Parameter {param.name!r} on spell {spell.spell_name!r} "
                                "is marked for DI but has no annotation."
                            ),
                            details={"parameter_name": param.name},
                        )
                    )
                    continue

            if param.di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION:
                if inspect.isclass(annotation) and annotation.__module__ == "builtins":
                    context.issues.append(
                        SpellValidationIssue(
                            severity="error",
                            code="DI_BUILTIN_ANNOTATION",
                            message=(
                                f"Parameter {param.name!r} on spell {spell.spell_name!r} "
                                f"uses builtin annotation {annotation!r} for DI, which is not supported."
                            ),
                            details={"parameter_name": param.name},
                        )
                    )

            if param.di_shape is ParameterDIShape.COLLECTION_BY_ANNOTATION:
                element = param.collection_element_annotation
                if element is None:
                    context.issues.append(
                        SpellValidationIssue(
                            severity="error",
                            code="DI_COLLECTION_MISSING_ELEMENT",
                            message=(
                                f"Parameter {param.name!r} on spell {spell.spell_name!r} "
                                "is marked as a collection DI parameter but has no element type."
                            ),
                            details={"parameter_name": param.name},
                        )
                    )
                    continue

                if not self._looks_like_di_target(element):
                    context.issues.append(
                        SpellValidationIssue(
                            severity="error",
                            code="DI_COLLECTION_NON_FRAME",
                            message=(
                                f"Parameter {param.name!r} on spell {spell.spell_name!r} "
                                f"uses non-DI element annotation {element!r} for collection DI."
                            ),
                            details={"parameter_name": param.name},
                        )
                    )

    def _looks_like_di_target(self, annotation: Any) -> bool:
        """
        Best-effort check for DI-eligible annotations.
        """
        if isinstance(annotation, typing.ForwardRef):
            return True

        if isinstance(annotation, str):
            return True

        if inspect.isclass(annotation):
            return annotation.__module__ != "builtins"

        return False
