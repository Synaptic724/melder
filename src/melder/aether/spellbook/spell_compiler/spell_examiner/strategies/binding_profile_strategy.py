import inspect
from typing import TYPE_CHECKING, Any, List, ClassVar



# Melder Imports
from melder.aether.spellbook.spell_compiler.spell_examiner.inspectors.inspector_utility import InspectorUtility
from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.binding_profile import ClassBindingProfile, \
    SpellBindingKind, CallableBindingProfile, CallableParameterBindingSummary, \
    InstanceBindingProfile, OtherBindingProfile
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
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
    __melder_internal__: ClassVar[object] = _mrg.sentinel
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
        """
        module = inspect.getmodule(cls)

        try:
            annotations = inspect.get_annotations(
                cls,
                eval_str=True,
                globals=module.__dict__ if module is not None else None,
            )
        except Exception:
            annotations = {}

        try:
            origin_file = inspect.getfile(cls)
        except Exception:
            origin_file = None

        try:
            lines, origin_line = inspect.getsourcelines(cls)
            source_preview = "".join(lines[:5]).strip()
        except Exception:
            origin_line = None
            source_preview = None

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
            source_preview=source_preview,
            is_dataclass=is_dataclass,
            decorated=decorated,
            method_names=method_names,
        )

    def _build_callable_profile(self, fn: Any) -> CallableBindingProfile:
        """
        Build the shallow binding-time profile for one callable candidate.
        """
        effective = InspectorUtility.unwrap_callable(fn)
        module = inspect.getmodule(effective)

        name = getattr(effective, "__name__", "<unnamed>")
        qualname = getattr(effective, "__qualname__", None)

        builtin_module = module is not None and inspect.isbuiltin(module)
        extension_module = InspectorUtility.is_extension_module(module)

        try:
            signature = inspect.signature(effective)
            signature_str = str(signature)
            parameter_summaries: List[CallableParameterBindingSummary] = []
            for parameter in signature.parameters.values():
                default_repr = None
                if parameter.default is not inspect.Parameter.empty:
                    default_repr = InspectorUtility.safe_repr(parameter.default, self.max_repr)
                annotation_repr = None
                if parameter.annotation is not inspect.Parameter.empty:
                    annotation_repr = InspectorUtility.safe_repr(parameter.annotation, self.max_repr)

                parameter_summaries.append(
                    CallableParameterBindingSummary(
                        name=parameter.name,
                        kind=parameter.kind.name,
                        default_repr=default_repr,
                        annotation_repr=annotation_repr,
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
        """
        type_name = type(obj).__name__
        module = getattr(type(obj), "__module__", "<unknown>")

        return InstanceBindingProfile(
            kind=SpellBindingKind.INSTANCE,
            original_object=obj,
            type_name=type_name,
            module=module,
            repr_string=InspectorUtility.safe_repr(obj, self.max_repr),
        )

    def _build_other_profile(self, obj: Any) -> OtherBindingProfile:
        """
        Build the fallback binding profile for unsupported candidate shapes.
        """
        type_name = type(obj).__name__
        module = getattr(type(obj), "__module__", "<unknown>")

        return OtherBindingProfile(
            kind=SpellBindingKind.OTHER,
            original_object=obj,
            type_name=type_name,
            module=module,
            repr_string=InspectorUtility.safe_repr(obj, self.max_repr),
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
