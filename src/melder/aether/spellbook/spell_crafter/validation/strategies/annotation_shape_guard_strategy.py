from __future__ import annotations

import inspect
import typing
from typing import Any, Tuple, get_args, get_origin

from mypy_extensions import mypyc_attr

from melder.aether.spellbook.spell_crafter.validation.spell_validation_context import (
    SpellValidationContext,
)
from melder.aether.spellbook.spell_crafter.validation.spell_validation_issue import (
    SpellValidationIssue,
)
from melder.aether.spellbook.spell_crafter.validation.strategies.spell_validation_strategy import (
    SpellValidationStrategy,
)

@mypyc_attr(native_class=True)
class AnnotationShapeGuardStrategy(SpellValidationStrategy):
    """
    Validate DI annotation shapes for unsupported collection forms.

    This strategy focuses on catching mismatched or unsupported annotation
    shapes early (Phase 4), before resolution attempts fail at runtime.

    Contract:
    - Rejects collection-style DI annotations that Melder does not support.
    - Treats `list[T]` as the only collection DI form worth deeper inspection
      in this first cut.
    - Emits validation issues into the supplied context; it does not mutate the
      spell or attempt recovery.
    """

    __slots__ = SpellValidationStrategy.__slots__

    def __init__(self) -> None:
        """
        Initialize the annotation shape guard strategy.

        Contract:
            Seeds the stable strategy name/description published through the
            validation pipeline.
        """
        super().__init__(
            name="annotation_shape_guard",
            description="Flags unsupported DI annotation shapes (set/dict/tuple, invalid list elements).",
        )

    def validate(self, context: "SpellValidationContext") -> None:
        """
        Validate the spell's parameter annotations for unsupported DI shapes.

        Contract:
            - Stops early if the validation context has been cancelled.
            - Emits `UNSUPPORTED_COLLECTION_SHAPE`,
              `UNRESOLVED_FORWARD_REF`, and `LIST_ELEMENT_NOT_DI_TARGET`
              issues when the annotation shape violates the supported DI model.
            - Performs validation only; it does not rewrite annotations or
              normalize them.
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
            if annotation is None:
                continue

            origin = get_origin(annotation)
            args = get_args(annotation)

            if origin in (set, frozenset, dict, tuple):
                if self._collection_args_have_di_targets(args):
                    context.issues.append(
                        SpellValidationIssue(
                            severity="error",
                            code="UNSUPPORTED_COLLECTION_SHAPE",
                            message=(
                                f"Parameter {param.name!r} on spell {spell.spell_name!r} "
                                f"uses unsupported collection annotation {annotation!r} "
                                "for DI. Only list[T] is supported for collection DI."
                            ),
                            details={
                                "parameter_name": param.name,
                                "annotation": annotation,
                            },
                        )
                    )
                continue

            if origin is list and len(args) == 1:
                element = args[0]
                if isinstance(element, typing.ForwardRef):
                    context.issues.append(
                        SpellValidationIssue(
                            severity="warning",
                            code="UNRESOLVED_FORWARD_REF",
                            message=(
                                f"Parameter {param.name!r} on spell {spell.spell_name!r} "
                                "uses a list annotation with an unresolved forward reference. "
                                "Ensure the element type is resolvable or use a string frame key."
                            ),
                            details={
                                "parameter_name": param.name,
                                "annotation": annotation,
                            },
                        )
                    )
                    continue

                if not self._looks_like_di_target(element):
                    context.issues.append(
                        SpellValidationIssue(
                            severity="warning",
                            code="LIST_ELEMENT_NOT_DI_TARGET",
                            message=(
                                f"Parameter {param.name!r} on spell {spell.spell_name!r} "
                                f"uses list[{element!r}], which is not a DI frame/type. "
                                "Collection DI only works for list[FrameType]."
                            ),
                            details={
                                "parameter_name": param.name,
                                "annotation": annotation,
                            },
                        )
                    )

            if isinstance(annotation, typing.ForwardRef):
                context.issues.append(
                    SpellValidationIssue(
                        severity="warning",
                        code="UNRESOLVED_FORWARD_REF",
                        message=(
                            f"Parameter {param.name!r} on spell {spell.spell_name!r} "
                            "uses an unresolved forward reference. Ensure the annotation "
                            "can be resolved or use a string frame key."
                        ),
                        details={
                            "parameter_name": param.name,
                            "annotation": annotation,
                        },
                    )
                )

    def _collection_args_have_di_targets(self, args: Tuple[Any, ...]) -> bool:
        """
        Return True if any collection args look like DI targets.

        Contract:
            Ignores tuple-ellipsis markers and treats any remaining argument
            that looks like a DI target as enough to trigger the unsupported
            collection-shape path.
        """
        for arg in args:
            if arg is Ellipsis:
                continue
            if self._looks_like_di_target(arg):
                return True
        return False

    def _looks_like_di_target(self, annotation: Any) -> bool:
        """
        Best-effort check for whether an annotation looks like a DI target.

        Contract:
            Returns True for forward refs, string frame keys, and non-builtin
            classes. This is intentionally heuristic rather than a full type
            system.
        """
        if isinstance(annotation, typing.ForwardRef):
            return True

        if isinstance(annotation, str):
            return True

        if inspect.isclass(annotation):
            return annotation.__module__ != "builtins"

        return False
