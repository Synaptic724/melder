import inspect
from annotationlib import Format
from types import ModuleType
from typing import TYPE_CHECKING, Any, Dict, List, ClassVar, Optional



# Melder Imports
from melder.aether.spellbook.spell_compiler.spell_examiner.inspectors.inspector_utility import InspectorUtility
from melder.utilities.helpers.signature_reflection import SignatureReflection
from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.binding_profile import ClassBindingProfile, \
    SpellBindingKind, CallableBindingProfile, CallableParameterBindingSummary, \
    InstanceBindingProfile, OtherBindingProfile
if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.binding_profile import (
        SpellBindingProfile,
    )

class BindingProfileStrategy:
    """
    Strategy for producing **binding profiles** from raw user objects.

    This is the only strategy used at `Bind` time. It does not depend on
    Spell or any phase artifacts.
    """
    __slots__ = ("show_dunders", "max_repr")

    def __init__(self, *, show_dunders: bool = False, max_repr: int = 120) -> None:
        """
        Initialize one binding-profile strategy.

        Args:
            show_dunders:
                Whether dunder members should be included when class binding
                profiles are built.
            max_repr:
                Maximum representation length passed to inspector helpers.

        Returns:
            None.
        """
        self.show_dunders = show_dunders
        self.max_repr = max_repr

    def build_profile(self, candidate: Any) -> SpellBindingProfile:
        """
        Dispatch one raw candidate into the appropriate binding-profile shape.

        Contract:
            - Class candidates are routed to the class profile builder.
            - Non-class callables are routed to the callable profile builder.
            - Non-callable non-class objects are treated as instance bindings.
            - The final fallback path is reserved for anything that slips past
              the earlier shape checks.

        Returns:
            SpellBindingProfile: Binding profile chosen for the candidate.
        """
        if inspect.isclass(candidate):
            return self._build_class_profile(candidate)

        if callable(candidate) and not inspect.isclass(candidate):
            return self._build_callable_profile(candidate)

        if not inspect.isclass(candidate) and not callable(candidate):
            return self._build_instance_profile(candidate)

        return self._build_other_profile(candidate)

    def _build_class_profile(self, cls: type) -> ClassBindingProfile:
        """
        Build the shallow binding-time profile for one class candidate.

        Constructor signatures preserve unresolved annotation names as Python
        3.14 ForwardRefs. TYPE_CHECKING-only imports must not erase the cached
        signature; known annotation objects and default values remain intact.

        The `init_signature` text feeds the bind fingerprint (spell id). A
        ForwardRef's repr embeds its owner, including a memory address, so the
        text renders those names as source text
        (`SignatureReflection.stabilize_signature`) and stays identical across
        processes; the cached signature object keeps the ForwardRefs.

        Class-level annotations come from `_read_class_annotations`: evaluated
        where every name resolves, otherwise read without evaluating the
        unavailable names, which stay as their source text (2026-09-26). The
        bind fingerprint hashes their keys, so every annotated field counts.
        """
        module = inspect.getmodule(cls)

        annotations = self._read_class_annotations(cls, module)

        try:
            origin_file = inspect.getfile(cls)
        except Exception:
            origin_file = None

        # No source-file read here: the v4 fingerprint hashes the constructor
        # signature instead of a source preview, and the preview itself is
        # served lazily by ClassBindingProfile.source_preview for descriptor
        # and diagnostic consumers. `__firstlineno__` (3.13+) supplies the
        # origin line without touching the file system.
        origin_line = getattr(cls, "__firstlineno__", None)

        init_signature_object: Optional[Any] = None
        try:
            init_signature_object = inspect.signature(cls, annotation_format=Format.FORWARDREF)
            init_signature: Optional[str] = str(
                SignatureReflection.stabilize_signature(init_signature_object, cls)
            )
        except Exception:
            init_signature_object = None
            init_signature = None

        bases: list[str] = [base.__name__ for base in getattr(cls, "__bases__", ())]
        mro: list[str] = [m.__name__ for m in inspect.getmro(cls)]
        is_dataclass = hasattr(cls, "__dataclass_fields__")

        method_names: list[str] = []
        for name, value in cls.__dict__.items():
            if not self.show_dunders and name.startswith("__") and name.endswith("__"):
                if not (is_dataclass and name == "__init__"):
                    continue
            if callable(value):
                method_names.append(name)

        decorated = self._is_probably_decorated_class(cls)

        return ClassBindingProfile(
            kind=SpellBindingKind.CLASS,
            original_object=cls,
            name=cls.__name__,
            qualname=getattr(cls, "__qualname__", cls.__name__),
            module=getattr(cls, "__module__", "<unknown>"),
            bases=bases,
            mro=mro,
            annotations=annotations,
            origin_file=origin_file,
            origin_line=origin_line,
            init_signature=init_signature,
            init_signature_object=init_signature_object,
            is_dataclass=is_dataclass,
            decorated=decorated,
            method_names=method_names,
        )

    @staticmethod
    def _read_class_annotations(cls: type, module: Optional[ModuleType]) -> Dict[str, Any]:
        """
        Return the class-level annotations recorded in a class binding profile.

        Contract:
            - Evaluates with `inspect.get_annotations(..., eval_str=True)` against
              the class's module, so string annotations resolve where possible.
              A class whose names all resolve gets exactly that mapping.
            - A name unbound at runtime (a TYPE_CHECKING-only import under Python
              3.14 lazy annotations) makes that evaluation raise NameError. The
              annotations are then read without evaluating it
              (`SignatureReflection.class_annotations`, the read ClassInspector
              uses): the same keys, each unavailable name as its source text
              (`'Decimal'`, `'list[Decimal]'`), quoted strings as written.
              Before 2026-09-26 this case dropped every annotation of the class.
            - Keys are always the class's own annotation names, so the bind
              fingerprint (which hashes the sorted keys) sees every annotated field.
            - Best-effort: any other failure, including one inside that fallback,
              yields an empty mapping, so binding never fails because a class's
              annotations cannot be read.

        Args:
            cls: Class candidate being profiled.
            module: Module returned by `inspect.getmodule(cls)`, or None.

        Returns:
            Dict[str, Any]: Attribute name to annotation value - the evaluated
                object, or source text for a name unavailable at runtime.
        """
        try:
            return inspect.get_annotations(
                cls,
                eval_str=True,
                globals=module.__dict__ if module is not None else None,
            )
        except NameError:
            try:
                return SignatureReflection.class_annotations(cls)
            except Exception:
                # Best-effort: annotations that cannot be read bind as none.
                return {}
        except Exception:
            # Best-effort: annotations that cannot be read bind as none.
            return {}

    def _build_callable_profile(self, fn: Any) -> CallableBindingProfile:
        """
        Build the shallow binding-time profile for one callable candidate.

        Partial annotation evaluation retains TYPE_CHECKING-only names in the
        signature without invoking the callable or dropping its parameters. The
        signature text and annotation reprs render those names as source text so
        they never embed an object address.
        `fingerprint_repr` and each parameter's `default_fingerprint_repr` carry the
        address-free, untruncated repr the bind fingerprint hashes; `repr_string` and
        `default_repr` stay the truncated display text.
        """
        effective = InspectorUtility.unwrap_callable(fn)
        module = inspect.getmodule(effective)

        name = getattr(effective, "__name__", "<unnamed>")
        qualname = getattr(effective, "__qualname__", None)

        builtin_module = module is not None and inspect.isbuiltin(module)
        extension_module = InspectorUtility.is_extension_module(module)

        try:
            signature = SignatureReflection.stabilize_signature(
                inspect.signature(effective, annotation_format=Format.FORWARDREF),
                effective,
            )
            signature_str = str(signature)
            parameter_summaries: List[CallableParameterBindingSummary] = []
            for parameter in signature.parameters.values():
                default_repr = None
                default_fingerprint_repr = None
                if parameter.default is not inspect.Parameter.empty:
                    default_repr = InspectorUtility.safe_repr(parameter.default, self.max_repr)
                    default_fingerprint_repr = InspectorUtility.stable_repr(parameter.default)
                annotation_repr = None
                if parameter.annotation is not inspect.Parameter.empty:
                    annotation_repr = InspectorUtility.safe_repr(parameter.annotation, self.max_repr)

                parameter_summaries.append(
                    CallableParameterBindingSummary(
                        name=parameter.name,
                        kind=parameter.kind.name,
                        default_repr=default_repr,
                        annotation_repr=annotation_repr,
                        default_fingerprint_repr=default_fingerprint_repr,
                    )
                )
        except (ValueError, TypeError):
            signature_str = None
            parameter_summaries = []

        lambda_function = inspect.isfunction(effective) and name == "<lambda>"
        abstract = inspect.isabstract(effective)

        return CallableBindingProfile(
            kind=SpellBindingKind.CALLABLE,
            original_object=fn,
            name=name,
            qualname=qualname,
            module=getattr(effective, "__module__", None),
            object_id=id(effective),
            type_name=type(effective).__name__,
            repr_string=InspectorUtility.safe_repr(effective, self.max_repr),
            fingerprint_repr=InspectorUtility.stable_repr(effective),
            signature=signature_str,
            parameters=parameter_summaries,
            builtin_module=builtin_module,
            extension_module=extension_module,
            lambda_function=lambda_function,
            abstract=abstract,
        )

    def _build_instance_profile(self, obj: Any) -> InstanceBindingProfile:
        """
        Build the binding-time profile for one existing instance candidate.

        The display `repr_string` is truncated; `fingerprint_repr` is the full repr with memory
        addresses removed, so a default-repr object gets the same spell id in every process.
        """
        type_name = type(obj).__name__
        module = getattr(type(obj), "__module__", "<unknown>")

        return InstanceBindingProfile(
            kind=SpellBindingKind.INSTANCE,
            original_object=obj,
            type_name=type_name,
            module=module,
            repr_string=InspectorUtility.safe_repr(obj, self.max_repr),
            fingerprint_repr=InspectorUtility.stable_repr(obj),
        )

    def _build_other_profile(self, obj: Any) -> OtherBindingProfile:
        """
        Build the fallback binding profile for unsupported candidate shapes.

        Carries the same address-free `fingerprint_repr` as the instance profile.
        """
        type_name = type(obj).__name__
        module = getattr(type(obj), "__module__", "<unknown>")

        return OtherBindingProfile(
            kind=SpellBindingKind.OTHER,
            original_object=obj,
            type_name=type_name,
            module=module,
            repr_string=InspectorUtility.safe_repr(obj, self.max_repr),
            fingerprint_repr=InspectorUtility.stable_repr(obj),
        )

    @staticmethod
    def _is_probably_decorated_class(cls: Any) -> bool:
        """
        Heuristically detect whether a class object looks decorator-wrapped.
        """
        if not inspect.isclass(cls):
            return True

        if type(cls) is not type:
            return True

        if hasattr(cls, "__wrapped__"):
            return True

        qualname = getattr(cls, "__qualname__", "")
        name = getattr(cls, "__name__", "")
        if qualname and "." in qualname and name not in qualname:
            return True

        return False
