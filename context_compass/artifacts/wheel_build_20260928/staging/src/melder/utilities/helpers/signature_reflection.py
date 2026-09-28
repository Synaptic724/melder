import inspect
from annotationlib import ForwardRef, Format, get_annotations
from typing import Any, Callable, Dict, get_args


#region SignatureReflection


class SignatureReflection:
    """
    Read callable signatures and class annotations when some annotation names are unavailable.

    Purpose:
        Python 3.14 evaluates annotations lazily. A name imported only under
        `typing.TYPE_CHECKING` - the typing style this repository recommends for
        collaborator types - is unbound when an annotation is evaluated, so the
        default `inspect.signature(...)` (VALUE format), `typing.get_type_hints`,
        and class `__annotations__` access raise `NameError`. A `Format.FORWARDREF`
        read succeeds and keeps each unavailable name as an
        `annotationlib.ForwardRef` that records the object it was read from (its
        owner). The `repr()` of such a ForwardRef embeds that owner, and a
        function's repr carries its memory address, so `str(signature)` over one
        is neither readable nor stable across processes.

        This helper is the one place Melder turns such signatures and annotation
        maps into values that are safe to render: owner-bearing ForwardRefs become
        source text, and everything else is left exactly as Python produced it.

    Contract:
        - `display_signature(...)` returns the default VALUE-format signature
          whenever that read succeeds, so rendered text is unchanged for every
          target whose annotation names are all available.
        - Only an annotation that is, or nests, an owner-bearing ForwardRef is
          replaced: a bare ForwardRef by its name (`'Decimal'`), a nested one by the
          annotation's `Format.STRING` source text (`'Optional[Decimal]'`). The
          result never embeds an object address.
        - ForwardRefs without an owner - the ones `typing` itself builds for quoted
          arguments such as `Optional['Conduit']` - are left untouched; they render
          deterministically already.
        - Stateless: every method is a static function of its arguments.

    Threading:
        Stateless and read-only; safe from any thread. Reading annotations runs the
        target's `__annotate__` function, which is user code for user targets.

    Lifecycle:
        Holds no state and needs no cleanup.
    """
    __slots__ = ()

    @staticmethod
    def display_signature(target: Callable[..., Any]) -> inspect.Signature:
        """
        Return a signature of `target` that can be rendered even when annotation names are unavailable.

        Contract:
            - Returns the default VALUE-format `inspect.signature(target)` when it
              succeeds.
            - When that read raises `NameError` (an annotation names something that
              is not bound at runtime, typically a TYPE_CHECKING-only import),
              re-reads in `Format.FORWARDREF` and returns
              `stabilize_signature(...)` of that result.
            - Other failures (`TypeError`, `ValueError` for callables without a
              signature, exceptions raised by annotation code itself) propagate
              unchanged.

        Args:
            target (Callable[..., Any]): Function, method, class or other callable
                accepted by `inspect.signature`.

        Returns:
            inspect.Signature: VALUE-format signature, or a FORWARDREF-format
            signature whose unavailable names are source text.

        Raises:
            TypeError: If `target` is not a supported callable.
            ValueError: If no signature can be provided for `target`.
        """
        try:
            return inspect.signature(target)
        except NameError:
            signature = inspect.signature(target, annotation_format=Format.FORWARDREF)
            return SignatureReflection.stabilize_signature(signature, target)

    @staticmethod
    def stabilize_signature(
            signature: inspect.Signature,
            target: Callable[..., Any],
    ) -> inspect.Signature:
        """
        Replace the owner-bearing ForwardRefs in a FORWARDREF-format signature with source text.

        Purpose:
            Let a caller that already holds a FORWARDREF signature, and must keep
            that object for other consumers, derive a variant whose `str()` is
            deterministic.

        Contract:
            - Returns `signature` itself when no parameter or return annotation
              contains an owner-bearing ForwardRef.
            - Otherwise returns a new signature in which each affected annotation
              is replaced: a bare ForwardRef by its `__forward_arg__`, and an
              annotation that nests one by the matching `Format.STRING` annotation
              of `target`. Names, kinds, defaults and every other annotation are
              unchanged, and `signature` is not modified.

        Args:
            signature (inspect.Signature): FORWARDREF-format signature previously
                read from `target`.
            target (Callable[..., Any]): The callable `signature` was read from; it
                is read again in STRING format only when a nested replacement is
                needed.

        Returns:
            inspect.Signature: `signature`, or a text-safe copy of it.

        Raises:
            TypeError: If `target` is not a supported callable.
            ValueError: If no signature can be provided for `target`.
        """
        needs = SignatureReflection.contains_unresolved_name
        if not needs(signature.return_annotation) and not any(
                needs(parameter.annotation) for parameter in signature.parameters.values()
        ):
            return signature

        source_text: Dict[str, Any] = {}
        text_return: Any = inspect.Signature.empty
        if SignatureReflection._needs_source_text(signature):
            text_signature = inspect.signature(target, annotation_format=Format.STRING)
            source_text = {
                name: parameter.annotation
                for name, parameter in text_signature.parameters.items()
            }
            text_return = text_signature.return_annotation

        parameters = []
        for name, parameter in signature.parameters.items():
            if needs(parameter.annotation):
                parameter = parameter.replace(
                    annotation=SignatureReflection._replacement(
                        parameter.annotation,
                        source_text.get(name),
                    ),
                )
            parameters.append(parameter)
        return_annotation = signature.return_annotation
        if needs(return_annotation):
            return_annotation = SignatureReflection._replacement(return_annotation, text_return)
        return signature.replace(parameters=parameters, return_annotation=return_annotation)

    @staticmethod
    def class_annotations(cls: type) -> Dict[str, Any]:
        """
        Return the class-level annotations of `cls` without evaluating unavailable names.

        Contract:
            - Reads the class's own annotations (not inherited ones) in
              `Format.FORWARDREF`, like `annotationlib.get_annotations(cls, ...)`.
            - Every annotation that is, or nests, an owner-bearing ForwardRef is
              replaced as in `stabilize_signature(...)`: a bare one by its name, a
              nested one by its `Format.STRING` source text. Other values are the
              evaluated objects.
            - String annotations (quoted, or from a module using
              `from __future__ import annotations`) are returned as written; this
              method never `eval`s them.
            - Returns an empty dict when the class declares no annotations.

        Args:
            cls (type): Class to read.

        Returns:
            Dict[str, Any]: A new mapping of attribute name to annotation value.

        Raises:
            TypeError: If `cls` does not support annotation reads.
        """
        annotations = get_annotations(cls, format=Format.FORWARDREF)
        needs = SignatureReflection.contains_unresolved_name
        if not any(needs(value) for value in annotations.values()):
            return dict(annotations)
        source_text: Dict[str, Any] = {}
        if any(needs(value) and not isinstance(value, ForwardRef) for value in annotations.values()):
            source_text = get_annotations(cls, format=Format.STRING)
        return {
            name: SignatureReflection._replacement(value, source_text.get(name)) if needs(value) else value
            for name, value in annotations.items()
        }

    @staticmethod
    def contains_unresolved_name(annotation: Any) -> bool:
        """
        Return whether an annotation value is, or nests, an owner-bearing `annotationlib.ForwardRef`.

        Contract:
            - An owner-bearing ForwardRef is what a `Format.FORWARDREF` read leaves
              for a name that could not be evaluated; its `repr()` embeds the owner.
            - Walks typing constructs through `typing.get_args(...)`, including the
              argument lists of `Callable[[...], ...]`.
            - Ownerless ForwardRefs (built by `typing` for quoted arguments),
              classes, strings, `inspect.Parameter.empty` and `Annotated` metadata
              report False.

        Args:
            annotation (Any): Annotation value from a FORWARDREF-format read.

        Returns:
            bool: True when an owner-bearing ForwardRef appears anywhere in the value.
        """
        if isinstance(annotation, ForwardRef):
            return annotation.__owner__ is not None
        if isinstance(annotation, (list, tuple)):
            return any(SignatureReflection.contains_unresolved_name(item) for item in annotation)
        return any(SignatureReflection.contains_unresolved_name(arg) for arg in get_args(annotation))

    @staticmethod
    def _needs_source_text(signature: inspect.Signature) -> bool:
        """
        Return whether any unresolved name in `signature` is nested rather than bare.

        Contract:
            A bare owner-bearing ForwardRef is replaced by its own name, so the
            second (STRING-format) read is only needed for nested ones.
        """
        values = [parameter.annotation for parameter in signature.parameters.values()]
        values.append(signature.return_annotation)
        return any(
            SignatureReflection.contains_unresolved_name(value) and not isinstance(value, ForwardRef)
            for value in values
        )

    @staticmethod
    def _replacement(annotation: Any, source_text: Any) -> Any:
        """
        Return the text that stands in for one annotation containing an unresolved name.

        Contract:
            - A bare ForwardRef is replaced by its `__forward_arg__` string.
            - Otherwise `source_text` - the `Format.STRING` annotation read for the
              same parameter, return value or attribute - is returned.
        """
        if isinstance(annotation, ForwardRef):
            return annotation.__forward_arg__
        return source_text
#endregion
