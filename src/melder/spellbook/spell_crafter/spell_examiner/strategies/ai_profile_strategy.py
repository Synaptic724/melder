from __future__ import annotations
import inspect
from typing import Any, Optional, List
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
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = ("show_dunders", "max_repr")

    def __init__(self, *, show_dunders: bool = False, max_repr: int = 120) -> None:
        self.show_dunders = show_dunders
        self.max_repr = max_repr

    def build_profile(
            self,
            spell: ISpell,
            binding_profile: Optional[SpellBindingProfile] = None,
            resolution_profile: Optional[SpellResolutionProfile] = None,
    ) -> SpellAIProfile:
        # Ensure we have a binding profile for the underlying object.
        if binding_profile is None:
            binding_strategy = BindingProfileStrategy(
                show_dunders=self.show_dunders,
                max_repr=self.max_repr,
            )
            binding_profile = binding_strategy.build_profile(spell.spell)

        # Ensure we have a resolution profile for this spell.
        if resolution_profile is None:
            resolution_strategy = ResolutionProfileStrategy()
            resolution_profile = resolution_strategy.build_profile(spell)

        class_profile: Optional[ClassProfile] = None
        callable_profile: Optional[MethodProfile] = None

        # Deep introspection depends on what kind of spell this is.
        if spell.is_class_spell:
            class_profile = self._inspect_class(spell)
        elif spell.is_method_spell or spell.is_lambda_spell:
            callable_profile = self._inspect_callable(spell)
        else:
            # Fallback – if the spell wraps some other callable, we can still inspect it.
            if callable(spell.spell) and not inspect.isclass(spell.spell):
                callable_profile = self._inspect_callable(spell)

        return SpellAIProfile(
            spell=spell,
            binding_profile=binding_profile,
            resolution_profile=resolution_profile,
            class_profile=class_profile,
            callable_profile=callable_profile,
            metadata={},
        )

    def _inspect_class(self, spell: ISpell) -> ClassProfile:
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
            source_preview=data["source_preview"],
            members=data["members"],
            methods=method_profiles,
            is_dataclass=data["is_dataclass"],
            decorated=data["decorated"],
        )

    def _inspect_callable(self, spell: ISpell) -> MethodProfile:
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
        )
