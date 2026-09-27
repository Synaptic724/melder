import inspect
import typing
from typing import TYPE_CHECKING, Any, get_args, get_origin



from melder.aether.spellbook.spell_compiler.validation.spell_validation_issue import (
    SpellValidationIssue,
)
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.aether.spellbook.spell_compiler.validation.strategies.spell_validation_strategy import (
    SpellValidationStrategy,
)
if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.validation.spell_validation_context import (
        SpellValidationContext,
    )


class AnnotationShapeGuardStrategy(SpellValidationStrategy):
    """
    Validate DI annotation shapes for unsupported collection forms.

    This strategy focuses on catching mismatched or unsupported annotation
    shapes early (Phase 4), before resolution attempts fail at runtime.

    Contract:
    - Judges only shapes Phase 1 may inject: `list[T]` elements and forward
      references. A set, frozenset, dict or tuple parameter is never injected -
      Phase 1 classifies it PLAIN, a caller input - so this strategy does not
      judge it; `RequiredHolesStrategy` reports it as a REQUIRED_HOLE whose
      message says Melder injects collections only as `list[T]` (2026-09-26).
      Phase 1 is the single decider of injection; this strategy never breaks a
      spell over a parameter Phase 1 made a caller input.
    - Emits validation issues into the supplied context; it does not mutate the
      spell or attempt recovery.
    - Non-resolvable definitions retain ordinary Python annotations without
      imposing constructor-DI shape restrictions.

    Registration:
        MELDER KERNEL. A built-in strategy; registered, never bound.

    Subsystem Context:
        A built-in of the `validation/strategies` family; it reads Phase-1
        requirements annotations and defers SpellMap/SpellContract defaults to their
        own strategies.

    System Context:
        Phase 4 (validation) of the conjure pipeline, catching unsupported
        annotation shapes before Phase-3 resolution would fail at runtime.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Phase-4 strategy: warns about list[T] elements and forward references
        Melder cannot inject. Emits LIST_ELEMENT_NOT_DI_TARGET (only when a user class sits inside
        the element, e.g. list[Optional[Plugin]]; plain data such as list[str] gets nothing) and
        UNRESOLVED_FORWARD_REF (warnings). Only list[FrameType] is collection DI; set/dict/tuple
        parameters are caller inputs, reported by RequiredHolesStrategy.
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
            description="Flags list elements and forward references Melder cannot inject.",
        )

    def validate(self, context: SpellValidationContext) -> None:
        """
        Validate the spell's parameter annotations for unsupported DI shapes.

        Contract:
            - Stops early if the validation context has been cancelled.
            - Emits `UNRESOLVED_FORWARD_REF` and `LIST_ELEMENT_NOT_DI_TARGET`
              warnings when a list element or annotation cannot be injected.
            - Emits nothing for set, frozenset, dict or tuple parameters: Phase 1
              never injects them, so they are caller inputs, not DI errors.
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
        if not spell.resolvable:
            return

        for param in requirements.parameters:
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()

            if param.di_shape in (
                ParameterDIShape.SPELLMAP_DEFAULT,
                ParameterDIShape.SPELL_CONTRACT,
            ):
                # An explicit SpellMap/SpellContract default overrides the
                # annotation, so its raw shape must not be judged for DI.
                continue

            annotation = param.annotation
            if annotation is None:
                continue

            origin = get_origin(annotation)
            args = get_args(annotation)

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

                # Plain data lists (list[str], list[Any]) are ordinary caller
                # inputs; warn only when a user class hides inside the element
                # (list[Optional[Plugin]]), where injection may have been meant.
                if not self._looks_like_di_target(element) and self._mentions_di_target(element):
                    context.issues.append(
                        SpellValidationIssue(
                            severity="warning",
                            code="LIST_ELEMENT_NOT_DI_TARGET",
                            message=(
                                f"Parameter {param.name!r} on spell {spell.spell_name!r} is "
                                f"list[{element!r}]. Melder injects a list only when its element is "
                                "one registered type (list[Plugin]), so this parameter is left for "
                                "the caller to supply."
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

    def _mentions_di_target(self, annotation: Any) -> bool:
        """
        Report whether a DI-eligible class or forward reference appears among the
        annotation's type arguments (one level down), as in `Optional[Plugin]`.

        Contract:
            Only classes and forward references count; strings and literals do not.
        """
        return any(
            (inspect.isclass(arg) or isinstance(arg, typing.ForwardRef)) and self._looks_like_di_target(arg)
            for arg in get_args(annotation)
        )

    def _looks_like_di_target(self, annotation: Any) -> bool:
        """
        Best-effort check for whether an annotation looks like a DI target.

        Contract:
            Returns True for forward refs, string frame keys, and non-builtin
            classes, and False for `typing.Any`, matching Phase 1's
            `SpellRequirementsFinder._looks_like_di_target`. This is
            intentionally heuristic rather than a full type system.
        """
        if annotation is typing.Any:
            # A class since Python 3.11; Phase 1 never injects it, so neither
            # may this check treat it as a DI target.
            return False

        if isinstance(annotation, typing.ForwardRef):
            return True

        if isinstance(annotation, str):
            return True

        if inspect.isclass(annotation):
            return annotation.__module__ != "builtins"

        return False
