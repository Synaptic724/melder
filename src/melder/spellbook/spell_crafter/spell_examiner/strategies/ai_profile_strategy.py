import inspect
from typing import Any, Optional, List, Dict
# Melder Imports
from melder.spellbook.spell_crafter.spell_examiner.inspectors.class_inspector import ClassInspector
from melder.spellbook.spell_crafter.spell_examiner.inspectors.method_inspector import MethodInspector
from melder.spellbook.spell_crafter.spell_examiner.inspectors.profiles.class_profile import ClassProfile
from melder.spellbook.spell_crafter.spell_examiner.inspectors.profiles.method_profile import MethodProfile
from melder.spellbook.spell_crafter.spell_examiner.profiles.ai_profile import SpellAIProfile
from melder.spellbook.spell_crafter.spell_examiner.profiles.binding_profile import SpellBindingProfile
from melder.spellbook.spell_crafter.spell_examiner.profiles.resolution_profile import SpellResolutionProfile
from melder.spellbook.spell_crafter.spell_examiner.strategies.binding_profile_strategy import BindingProfileStrategy
from melder.spellbook.spell_crafter.spell_examiner.strategies.resolution_profile_strategy import \
    ResolutionProfileStrategy
from melder.spellbook.spell_crafter.spell_examiner.inspectors.inspector_utility import InspectorUtility
from melder.utilities.interfaces.interfaces import ISpell
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class AIProfileStrategy:
    """
    Strategy for building **SpellAIProfile** from a Spell.

    This is the heavy path:
        * It assumes resolution semantics already exist (or builds them).
        * It runs deep introspection (ClassInspector / MethodInspector).
        * It packages everything into a SpellAIProfile suitable for
          agent-based reasoning, mutation planning, etc.

    Contract:
        - Produces a SpellAIProfile with binding + resolution profiles.
        - Includes class/callable profiles when applicable.
        - Instance member inventory is collected for non-class instances.
        - Dunder visibility is controlled by show_dunders (default True).
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = ("show_dunders", "max_repr")

    def __init__(self, *, show_dunders: bool = True, max_repr: int = 120) -> None:
        """
        Initialize the AI profile strategy.

        Args:
            show_dunders: Whether dunder members are included in inspection.
            max_repr: Maximum length for repr strings in output.
        """
        self.show_dunders = show_dunders
        self.max_repr = max_repr

    def build_profile(
            self,
            spell: ISpell,
    ) -> SpellAIProfile:
        """
        Build a SpellAIProfile for the provided spell.

        Args:
            spell: Spell object providing the underlying callable/class.

        Returns:
            SpellAIProfile: Fully assembled AI profile.
        """
        # Ensure we have a binding profile for the underlying object.
        binding_strategy = BindingProfileStrategy(
            show_dunders=self.show_dunders,
            max_repr=self.max_repr,
        )
        binding_profile = binding_strategy.build_profile(spell.spell)

        # Ensure we have a resolution profile for this spell.
        resolution_strategy = ResolutionProfileStrategy()
        resolution_profile = resolution_strategy.build_profile(spell)

        class_profile: Optional[ClassProfile] = None
        callable_profile: Optional[MethodProfile] = None

        instance_members: Dict[str, Dict[str, Any]] = {}
        dynamic_access: Dict[str, bool] = {}

        # Deep introspection depends on what kind of spell this is.
        if spell.is_class_spell:
            class_profile = self._inspect_class(spell)
            callable_profile = self._inspect_callable(spell)
        elif spell.is_method_spell or spell.is_lambda_spell:
            callable_profile = self._inspect_callable(spell)
        else:
            # Fallback – if the spell wraps some other callable, we can still inspect it.
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

        return SpellAIProfile(
            spell=spell,
            binding_profile=binding_profile,
            resolution_profile=resolution_profile,
            class_profile=class_profile,
            callable_profile=callable_profile,
            metadata={},
            instance_members=instance_members,
            dynamic_access=dynamic_access,
        )

    def _inspect_class(self, spell: ISpell) -> ClassProfile:
        """
        Inspect a class-based spell and build a ClassProfile.

        Args:
            spell: Spell wrapping a class object.

        Returns:
            ClassProfile: Structured class profile for the spell.
        """
        inspector = ClassInspector(
            spell.spell,
            show_dunders=self.show_dunders,
            max_repr=self.max_repr,
        )
        data = inspector.inspect()

        method_profiles: dict[str, MethodProfile] = {}
        for name, info in data["members"].items():
            if info.get("callable"):
                try:
                    fn = getattr(spell.spell, name)
                    method_data = MethodInspector(fn, max_repr=self.max_repr).inspect()
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

    def _inspect_callable(self, spell: ISpell) -> MethodProfile:
        """
        Inspect a callable-based spell and build a MethodProfile.

        Args:
            spell: Spell wrapping a callable object.

        Returns:
            MethodProfile: Structured callable profile for the spell.
        """
        inspector = MethodInspector(spell.spell, max_repr=self.max_repr)
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
        Determine whether instance members should be collected for an object.

        Args:
            obj: Object to evaluate.

        Returns:
            bool: True when the object is an instance (not class/function/method).
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
            obj: Instance to inspect.

        Returns:
            Dict[str, Dict[str, Any]]: Map of attribute name to member record.
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
        Build a tool-shaped record for an instance attribute.

        Args:
            obj: Owning instance.
            name: Attribute name.
            value: Attribute value (best-effort; may be None).

        Returns:
            Dict[str, Any]: Structured member record.
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
            "repr": InspectorUtility.safe_repr(value, self.max_repr),
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
        Compute dynamic attribute access flags for an object.

        Args:
            obj: Object to inspect.

        Returns:
            Dict[str, bool]: Flags for __getattr__, __getattribute__, __setattr__.
        """
        cls = type(obj)
        return {
            "has_getattr": self._has_attribute_in_mro(cls, "__getattr__"),
            "has_getattribute": self._has_attribute_in_mro(cls, "__getattribute__"),
            "has_setattr": self._has_attribute_in_mro(cls, "__setattr__"),
        }

    def _has_attribute_in_mro(self, cls: type, attr: str) -> bool:
        """
        Check whether a class or its bases define a given attribute.

        Args:
            cls: Class to inspect.
            attr: Attribute name to check.

        Returns:
            bool: True if attr appears in any __dict__ in the MRO.
        """
        for base in inspect.getmro(cls):
            if attr in base.__dict__:
                return True
        return False
