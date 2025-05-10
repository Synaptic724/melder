import inspect
import threading
from typing import Any, Optional, Union
from melder.spellbook.bind.graph_builder.inspector.spell_examiner import (
    SpellExaminer, ClassProfile, MethodProfile
)
from melder.spellbook.spell_types.spell_types import SpellType
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spell
from melder.utilities.interfaces import IBind


class Bind(IBind):
    def __init__(self):
        super().__init__()
        self._lock = threading.RLock()

    def bind(self, spell=None, *, spellframe=None, name=None, existence=Existence.unique):
        if spell is None:
            # Decorator usage
            def decorator(obj):
                return self._bind_logic(obj, spellframe, name, existence)
            return decorator
        else:
            # Direct usage
            return self._bind_logic(spell, spellframe, name, existence)

    def _bind_logic(self, spell: Any, spellframe: Optional[Any], binding_name: Optional[str], existence: Existence) -> Spell:
        with self._lock:
            # Get the class or method profile
            profile = SpellExaminer(spell).inspect()

            # Check if spell is an instance (not a class/function)
            is_instance = not inspect.isclass(spell) and not inspect.isfunction(spell)

            self._validate_binding(profile, is_instance, binding_name, existence)

            if isinstance(profile, MethodProfile):
                if existence != Existence.unique:
                    print(
                        f"[WARN] Overriding existence to `Existence.unique` for method/lambda spell: {getattr(spell, '__name__', repr(spell))}")
                existence = Existence.unique

            # Determine the spell type
            spell_type = self._determine_spell_type(spell, profile, binding_name, spellframe, is_instance)

            # Resolve spell name and frame
            spell_name = getattr(spell, "__name__", type(spell).__name__)

            # Create the Spell instance, attach profile
            new_spell = Spell(
                spell=spell,
                spellframe=spellframe,
                binding_name=binding_name,
                spell_name=spell_name,
                existence=existence,
                spell_type=spell_type,
                existing_object=spell if is_instance else None,
                profile=profile,
            )

            print(f"[BIND] Registered: {spell_name} | Frame: {spellframe} | Type: {spell_type} | Existence: {existence}")
            return new_spell

    def _validate_binding(self, profile, is_instance, binding_name, existence):
        """
        Perform checks on the method profile to ensure it is valid for binding.
        :param profile:
        :param is_instance:
        :param binding_name:
        :return:
        """
        if is_instance and binding_name:
            raise ValueError("Existing instances cannot be bound with a binding name.")

        # Enforce lambda naming rule
        if profile and isinstance(profile, MethodProfile) and profile.lambda_fn and not binding_name:
            raise ValueError(
                "Cannot bind a lambda method without providing a `name=`. "
                "Lambdas must be registered as NAMED_LAMBDA_METHOD spells."
            )

        if isinstance(profile, MethodProfile) and existence != Existence.unique:
            raise ValueError("Method and lambda spells must use Existence.unique.")

    def _determine_spell_type(
        self,
        spell: Any,
        profile: Union[ClassProfile, MethodProfile, dict],
        name: Optional[str],
        spellframe: Optional[Any],
        is_instance: bool
    ) -> SpellType:
        if isinstance(profile, ClassProfile):
            if name and spellframe:
                return SpellType.NAMED_INTERFACED
            elif spellframe:
                return SpellType.NORMAL_INTERFACED
            elif name:
                return SpellType.NAMED
            elif is_instance:
                return SpellType.EXISTING_CLASS
            else:
                return SpellType.NORMAL

        elif isinstance(profile, MethodProfile):
            if name and profile.lambda_fn:
                return SpellType.NAMED_LAMBDA_METHOD
            elif name:
                return SpellType.NAMED_METHOD
            else:
                return SpellType.NORMAL_METHOD
        else:
            return SpellType.EXISTING_CLASS if is_instance else SpellType.NORMAL
