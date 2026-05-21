import inspect
from typing import Any, Dict, List, Optional, TYPE_CHECKING, ClassVar
from types import MappingProxyType

from mypy_extensions import mypyc_attr

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.nexus.frame_descriptor.spell_descriptor_payload import (
    SpellDescriptorPayload,
)
from melder.aether.spellbook.spell_compiler.spell_examiner.inspectors.class_inspector import (
    ClassInspector,
)
from melder.aether.spellbook.spell_compiler.spell_examiner.inspectors.inspector_utility import (
    InspectorUtility,
)
from melder.aether.spellbook.spell_compiler.spell_examiner.inspectors.method_inspector import (
    MethodInspector,
)
from melder.aether.spellbook.spell_compiler.spell_examiner.inspectors.profiles.class_profile import (
    ClassProfile,
)
from melder.aether.spellbook.spell_compiler.spell_examiner.inspectors.profiles.method_profile import (
    MethodProfile,
)
from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.general_profile import (
    SpellGeneralProfile,
)
from melder.aether.spellbook.spell import Spell
from melder.utilities.general_base.cleanable import Cleanable
if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.profiles.resolution_profile import (
        SpellResolutionProfile,
    )
    from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.binding_profile import (
        SpellBindingProfile,
    )
@mypyc_attr(native_class=True)
class SpellDetailedProfile(SpellGeneralProfile):
    """
    Purpose:
        Represent the richer detailed spell profile as a superset of general.

    Contract:
        - Inherits the same two-step lifecycle as `SpellGeneralProfile`.
        - Adds class, callable, metadata, instance-member, and dynamic-access
          inspection on phase 2 completion.
        - Keeps the binding and resolution detail artifacts directly on the
          profile rather than wrapping a separate general profile object.

    Lifecycle:
        Phase 1 creates the profile with only binding data. Phase 2
        `complete_with_spell(...)` fills the inherited resolution data and then
        adds the richer inspector payloads.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = SpellGeneralProfile.__slots__ + [
        "_show_dunders",
        "_max_repr",
        "_detail_complete",
        "class_profile",
        "callable_profile",
        "metadata",
        "instance_members",
        "dynamic_access",
    ]
    __deletable__ = [
        "_show_dunders",
        "_max_repr",
        "_detail_complete",
        "class_profile",
        "callable_profile",
        "metadata",
        "instance_members",
        "dynamic_access",
    ]

    def __init__(
            self,
            *,
            binding_profile: SpellBindingProfile,
            resolution_profile: Optional[SpellResolutionProfile] = None,
            show_dunders: bool = True,
            max_repr: int = 120,
            class_profile: Optional[ClassProfile] = None,
            callable_profile: Optional[MethodProfile] = None,
            metadata: Optional[dict[str, Any]] = None,
            instance_members: Optional[dict[str, dict[str, Any]]] = None,
            dynamic_access: Optional[dict[str, bool]] = None,
    ) -> None:
        """
        Initialize one detailed spell profile.

        Args:
            binding_profile:
                Binding profile for the candidate object.
            resolution_profile:
                Resolution profile when phase 2 has completed.
            show_dunders:
                Whether dunder members should be included in deep inspection.
            max_repr:
                Maximum representation length used by the deep inspectors.
            class_profile:
                Optional class profile when the spell wraps a class.
            callable_profile:
                Optional callable profile when the spell wraps a callable.
            metadata:
                Free-form metadata map copied on assignment.
            instance_members:
                Optional instance-member inventory copied on assignment.
            dynamic_access:
                Dynamic access flags copied on assignment.

        Returns:
            None.
        """
        super().__init__(
            binding_profile=binding_profile,
            resolution_profile=resolution_profile,
        )
        self._show_dunders: bool = show_dunders
        self._max_repr: int = max_repr
        self.profile_name: str = "detailed"
        self.profile_version: str = "0.0.1"
        self._detail_complete: bool = False
        self.class_profile = class_profile
        self.callable_profile = callable_profile
        self.metadata: Optional[dict[str, Any]] = dict(metadata) if metadata is not None else {}
        self.instance_members: Optional[dict[str, dict[str, Any]]] = (
            dict(instance_members) if instance_members is not None else {}
        )
        self.dynamic_access = (
            dict(dynamic_access) if dynamic_access is not None else {}
        )

    def cleanup(self) -> None:
        """
        Idempotently clean the nested detailed-profile artifacts.

        Contract:
            Cascades cleanup into nested class/callable profiles before
            delegating to the inherited general-profile cleanup.

        Returns:
            None.
        """
        if self._cleaned:
            return
        for profile in (self.class_profile, self.callable_profile):
            if isinstance(profile, Cleanable):
                try:
                    profile.cleanup()
                except Exception:
                    pass
        if isinstance(self.metadata, dict):
            self.metadata.clear()
        super().cleanup()

        del self._show_dunders
        del self._max_repr
        del self._detail_complete
        del self.class_profile
        del self.callable_profile
        del self.metadata
        del self.instance_members
        del self.dynamic_access

    @classmethod
    def create_from_target(
            cls,
            target: Any,
            show_dunders: bool = True,
            max_repr: int = 120,
    ) -> "SpellDetailedProfile":
        """
        Create one detailed profile from a raw candidate or a fully formed spell.

        Args:
            target:
                Raw candidate object or a fully formed `Spell`.
            show_dunders:
                Whether dunder members should be included in deep inspection.
            max_repr:
                Maximum representation length used by binding and deep
                inspection.

        Contract:
            - Reuses `SpellGeneralProfile.create_from_target(...)` for the
              base phase-1/phase-2 lifecycle.
            - Re-wraps the resulting base profile into the richer detailed
              profile type before optional phase-2 completion.

        Returns:
            SpellDetailedProfile:
                New profile object. If `target` is a `Spell`, the returned
                profile is already fully completed.
        """
        base_profile = SpellGeneralProfile.create_from_target(
            target,
            show_dunders=show_dunders,
            max_repr=max_repr,
        )
        profile = cls(
            binding_profile=base_profile.binding_profile,
            resolution_profile=base_profile.resolution_profile,
            show_dunders=show_dunders,
            max_repr=max_repr,
        )
        if isinstance(target, Spell):
            profile.complete_with_spell(target)
        return profile

    def complete_with_spell(self, spell: Spell) -> None:
        """
        Complete phase 2 of the detailed profile lifecycle.

        Args:
            spell:
                Fully formed spell whose runtime metadata should drive the
                resolution and detailed inspection payloads.

        Contract:
            - Requires an object satisfying the spell protocol.
            - Delegates the inherited resolution-profile completion first.
            - Fills the richer class/callable/instance/dynamic-access payloads
              only once.

        Returns:
            None.

        Raises:
            TypeError:
                If `spell` does not satisfy the spell protocol.
        """
        self.check_cleaned()
        if not isinstance(spell, Spell):
            raise TypeError("Detailed profile completion requires a Spell instance.")
        super().complete_with_spell(spell)
        if self._detail_complete:
            return

        self._detail_complete = True
        class_profile: Optional[ClassProfile] = None
        callable_profile: Optional[MethodProfile] = None
        instance_members: Dict[str, Dict[str, Any]] = {}
        dynamic_access: Dict[str, bool] = {}

        if spell.is_class_spell:
            class_profile = self._inspect_class(spell)
            callable_profile = self._inspect_callable(spell)
        elif spell.is_method_spell or spell.is_lambda_spell:
            callable_profile = self._inspect_callable(spell)
        else:
            if callable(spell.spell) and not inspect.isclass(spell.spell):
                callable_profile = self._inspect_callable(spell)
                if self._should_collect_instance_members(spell.spell):
                    instance_members = self._inspect_instance_members(spell.spell)
                    dynamic_access = self._dynamic_access_flags(spell.spell)
            elif self._should_collect_instance_members(spell.spell):
                instance_members = self._inspect_instance_members(spell.spell)
                dynamic_access = self._dynamic_access_flags(spell.spell)

        if class_profile is not None:
            dynamic_access = class_profile.dynamic_access or {}

        self.class_profile = class_profile
        self.callable_profile = callable_profile
        self.metadata = {}
        self.instance_members = instance_members
        self.dynamic_access = dynamic_access

    def to_descriptor_payload(self) -> SpellDescriptorPayload:
        """
        Build one descriptor-safe payload from this detailed profile.

        Contract:
            Builds the descriptor payload from the current binding, resolution,
            class, callable, metadata, instance-member, and dynamic-access
            surfaces.

        Returns:
            SpellDescriptorPayload: Sanitized descriptor payload.
        """
        self.check_cleaned()
        return SpellDescriptorPayload.from_spell_profile(
            self.profile_name,
            self.profile_version,
            self.binding_profile,
            resolution_payload=self.resolution_profile,
            class_profile=self.class_profile,
            callable_profile=self.callable_profile,
            metadata=self.metadata,
            instance_members=self.instance_members,
            dynamic_access=self.dynamic_access,
        )

    def _inspect_class(self, spell: Spell) -> ClassProfile:
        """
        Inspect a class-backed spell and build a `ClassProfile`.

        Args:
            spell:
                Spell wrapping a class object.

        Contract:
            Uses `ClassInspector` for the class surface and then builds
            per-method `MethodProfile` payloads where possible.

        Returns:
            ClassProfile: Structured class profile for the spell.
        """
        inspector = ClassInspector(
            spell.spell,
            show_dunders=self._show_dunders,
            max_repr=self._max_repr,
        )
        data = inspector.inspect()

        method_profiles: Dict[str, MethodProfile] = {}
        for name, info in data["members"].items():
            if info.get("callable"):
                try:
                    fn = getattr(spell.spell, name)
                    method_data = MethodInspector(fn, max_repr=self._max_repr).inspect()
                    method_profiles[name] = MethodProfile(
                        name=method_data["name"],
                        qualname=method_data["qualname"],
                        module=method_data["module"],
                        id=method_data["id"],
                        type=method_data["type"],
                        repr=method_data["repr"],
                        builtin_mod=method_data["builtin_mod"],
                        extension_mod=method_data["extension_mod"],
                        file=method_data["file"],
                        preview=method_data["preview"],
                        src_offset=method_data["src_offset"],
                        start_line=method_data.get("start_line"),
                        end_line=method_data.get("end_line"),
                        source_text=method_data.get("source_text"),
                        signature=method_data.get("signature"),
                        parameters=method_data.get("parameters", []),
                        uninspectable=method_data.get("uninspectable", False),
                        func=method_data.get("func", False),
                        method=method_data.get("method", False),
                        builtin=method_data.get("builtin", False),
                        classmethod=method_data.get("classmethod", False),
                        staticmethod=method_data.get("staticmethod", False),
                        generator=method_data.get("generator", False),
                        async_gen=method_data.get("async_gen", False),
                        coroutine=method_data.get("coroutine", False),
                        lambda_fn=method_data.get("lambda_fn", False),
                        abstract=method_data.get("abstract", False),
                        closure=method_data.get("closure"),
                        decorated=method_data.get("decorated"),
                        wrapped_repr=method_data.get("wrapped_repr"),
                        docstring_raw=method_data.get("docstring_raw"),
                        docstring_summary=method_data.get("docstring_summary", ""),
                        behavior_summary=method_data.get("behavior_summary", ""),
                        tags=method_data.get("tags", []),
                    )
                except Exception:
                    continue

        return ClassProfile(
            name=data["name"],
            qualname=data["qualname"],
            module=data["module"],
            mro=data["mro"],
            bases=data["bases"],
            annotations=data["annotations"],
            protocols=data["protocols"],
            slots=data["slots"],
            origin_file=data["file"],
            origin_line=data["source_line_offset"],
            origin_end_line=data.get("source_end_line"),
            source_preview=data["source_preview"],
            source_text=data.get("source_text"),
            members=data["members"],
            methods=method_profiles,
            is_dataclass=data["is_dataclass"],
            decorated=data["decorated"],
            docstring_raw=data.get("docstring_raw"),
            docstring_summary=data.get("docstring_summary", ""),
            behavior_summary=data.get("behavior_summary", ""),
            tags=data.get("tags", []),
            dynamic_access=data.get("dynamic_access", {}),
        )

    def _inspect_callable(self, spell: Spell) -> MethodProfile:
        """
        Inspect a callable-backed spell and build a `MethodProfile`.

        Args:
            spell:
                Spell wrapping a callable object.

        Contract:
            Uses `MethodInspector` to derive a detached callable profile for
            the current spell object.

        Returns:
            MethodProfile: Structured callable profile for the spell.
        """
        inspector = MethodInspector(spell.spell, max_repr=self._max_repr)
        data = inspector.inspect()

        return MethodProfile(
            name=data["name"],
            qualname=data["qualname"],
            module=data["module"],
            id=data["id"],
            type=data["type"],
            repr=data["repr"],
            builtin_mod=data["builtin_mod"],
            extension_mod=data["extension_mod"],
            file=data["file"],
            preview=data["preview"],
            src_offset=data["src_offset"],
            start_line=data.get("start_line"),
            end_line=data.get("end_line"),
            source_text=data.get("source_text"),
            signature=data.get("signature"),
            parameters=data.get("parameters", []),
            uninspectable=data.get("uninspectable", False),
            func=data.get("func", False),
            method=data.get("method", False),
            builtin=data.get("builtin", False),
            classmethod=data.get("classmethod", False),
            staticmethod=data.get("staticmethod", False),
            generator=data.get("generator", False),
            async_gen=data.get("async_gen", False),
            coroutine=data.get("coroutine", False),
            lambda_fn=data.get("lambda_fn", False),
            abstract=data.get("abstract", False),
            closure=data.get("closure"),
            decorated=data.get("decorated"),
            wrapped_repr=data.get("wrapped_repr"),
            docstring_raw=data.get("docstring_raw"),
            docstring_summary=data.get("docstring_summary", ""),
            behavior_summary=data.get("behavior_summary", ""),
            tags=data.get("tags", []),
        )

    def _should_collect_instance_members(self, obj: Any) -> bool:
        """
        Return whether instance-member collection makes sense for an object.

        Args:
            obj:
                Object to evaluate.

        Contract:
            Returns True only for non-class, non-routine instance-like objects.

        Returns:
            bool: True when the object is a non-class, non-routine instance.
        """
        if inspect.isclass(obj):
            return False
        if inspect.isfunction(obj) or inspect.ismethod(obj):
            return False
        if inspect.isbuiltin(obj) or inspect.isroutine(obj):
            return False
        return True

    def _inspect_instance_members(self, obj: Any) -> Dict[str, Dict[str, Any]]:
        """
        Build a best-effort inventory of instance attributes.

        Args:
            obj:
                Instance to inspect.

        Contract:
            Builds a detached best-effort inventory from `vars(obj)` and any
            declared `__slots__`.

        Returns:
            Dict[str, Dict[str, Any]]: Structured instance-member map.
        """
        members: Dict[str, Dict[str, Any]] = {}
        attr_names: List[str] = []
        try:
            instance_dict = vars(obj)
            attr_names.extend(instance_dict.keys())
        except Exception:
            instance_dict = {}

        slots = getattr(type(obj), "__slots__", None)
        if isinstance(slots, str):
            attr_names.append(slots)
        elif isinstance(slots, (list, tuple)):
            attr_names.extend(slots)

        for name in sorted(set(attr_names)):
            try:
                value = getattr(obj, name)
            except Exception:
                value = None
            members[name] = self._build_instance_member_record(obj, name, value)
        return members

    def _build_instance_member_record(
            self,
            obj: Any,
            name: str,
            value: Any,
    ) -> Dict[str, Any]:
        """
        Build one structured instance-member record.

        Args:
            obj:
                Owning instance.
            name:
                Attribute name.
            value:
                Best-effort attribute value.

        Contract:
            Builds a detached tool-shaped record from the current attribute
            snapshot without keeping the live value object.

        Returns:
            Dict[str, Any]: Tool-shaped member record.
        """
        type_obj = type(obj)
        module = getattr(type_obj, "__module__", None)
        qualname = getattr(type_obj, "__qualname__", None)
        return {
            "name": name,
            "defined_here": True,
            "owner_class": type_obj.__name__,
            "defined_on": type_obj.__name__,
            "inherited": False,
            "kind": "instance_attribute",
            "raw_kind": "instance_attribute",
            "type": type(value).__name__ if value is not None else "NoneType",
            "callable": callable(value),
            "property": False,
            "is_dunder": name.startswith("__") and name.endswith("__"),
            "module": module,
            "qualname": qualname,
            "docstring_raw": getattr(value, "__doc__", None) if value is not None else None,
            "docstring_summary": "",
            "behavior_summary": "",
            "tags": [],
            "repr": InspectorUtility.safe_repr(value, self._max_repr),
            "signature": None,
            "parameters": [],
            "return_annotation": None,
            "src_line": None,
            "file_path": None,
            "start_line": None,
            "end_line": None,
            "source_text": None,
        }

    def _dynamic_access_flags(self, obj: Any) -> Dict[str, bool]:
        """
        Compute dynamic attribute-access flags for an object.

        Args:
            obj:
                Object to inspect.

        Contract:
            Reports the presence of `__getattr__`, `__getattribute__`, and
            `__setattr__` anywhere in the class MRO.

        Returns:
            Dict[str, bool]: Flags for `__getattr__`, `__getattribute__`, and
            `__setattr__`.
        """
        cls = type(obj)
        return {
            "has_getattr": self._has_attribute_in_mro(cls, "__getattr__"),
            "has_getattribute": self._has_attribute_in_mro(cls, "__getattribute__"),
            "has_setattr": self._has_attribute_in_mro(cls, "__setattr__"),
        }

    def _has_attribute_in_mro(self, cls: type, attr: str) -> bool:
        """
        Return whether an attribute appears anywhere in a class MRO.

        Args:
            cls:
                Class to inspect.
            attr:
                Attribute name to check.

        Contract:
            Checks only class `__dict__` entries across the MRO and does not
            invoke dynamic attribute access.

        Returns:
            bool: True when the attribute appears in any `__dict__` in the MRO.
        """
        for base in inspect.getmro(cls):
            if attr in base.__dict__:
                return True
        return False
