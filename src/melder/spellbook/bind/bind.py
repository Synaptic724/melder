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
import hashlib

#region Bind
class Bind(IBind):
    def __init__(self):
        super().__init__()
        self._lock = threading.RLock()

    def bind(self, spell=None, *, spellframe=None, name=None, existence=Existence.unique, whitelist=True):
        if spell is None:
            # Decorator usage
            def decorator(obj):
                return self._bind_logic(obj, spellframe, name, existence, whitelist)
            return decorator
        else:
            # Direct usage
            return self._bind_logic(spell, spellframe, name, existence, whitelist)

    def _bind_logic(self, spell: Any, spellframe: Optional[Any], binding_name: Optional[str], existence: Existence, whitelist:bool) -> Spell:
        with self._lock:
            # Get the class or method profile
            profile = SpellExaminer(spell).inspect()
            fingerprint = Bind.sha256_profile(profile)

            # Check if spell is an instance (not a class/function)
            is_instance = not inspect.isclass(spell) and not inspect.isfunction(spell)

            Bind._validate_binding(profile, is_instance, binding_name, existence)

            if isinstance(profile, MethodProfile):
                if existence != Existence.unique:
                    print(
                        f"[WARN] Overriding existence to `Existence.unique` for method/lambda spell: {getattr(spell, '__name__', repr(spell))}")
                existence = Existence.unique

            # Determine the spell type
            spell_type = Bind._determine_spell_type(spell, profile, binding_name, spellframe, is_instance)

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
                spell_id=fingerprint,
                whitelist=whitelist
            )

            print(f"[BIND] Registered: {spell_name} | Frame: {spellframe} | Type: {spell_type} | Existence: {existence}")
            return new_spell

#region Spell Inspector Helpers
    @staticmethod
    def spell_id_inspector(spell: Any) -> str:
        """
        Generate a unique identifier for the spell based on its profile.
        :param spell: The spell object to inspect.
        :return: A unique identifier string for the spell.
        """
        profile = SpellExaminer(spell).inspect()
        return Bind.sha256_profile(profile)

    @staticmethod
    def sha256_profile(profile: ClassProfile | MethodProfile) -> str:
        parts = ["v1"]  # fingerprint version tag

        if isinstance(profile, ClassProfile):
            parts += [
                profile.name,
                profile.qualname,
                profile.module,
                ",".join(sorted(profile.bases)),
                ",".join(sorted(profile.mro)),
                ",".join(sorted(profile.annotations.keys())),
                ",".join(sorted(profile.methods.keys())),
                (profile.source_preview or "").strip(),
            ]
        elif isinstance(profile, MethodProfile):
            param_parts = [
                f"{p['name']}:{p['kind']}={p['default']}" for p in profile.parameters
            ]
            parts += [
                profile.name,
                profile.qualname or "",
                profile.module or "",
                profile.signature or "",
                ",".join(param_parts),
                (profile.preview or "").strip(),
            ]

        key = "::".join(parts)
        return hashlib.sha256(key.encode("utf-8")).hexdigest()
    @staticmethod
    def _validate_binding(profile, is_instance, binding_name, existence):
        """
        Perform checks on the method profile to ensure it is valid for binding.
        :param profile:
        :param is_instance:
        :param binding_name:
        :return:
        """
        if Bind._existence_check(existence) is False:
            raise ValueError(f"Invalid existence type: {existence}. Must be an instance of Existence.")

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


    @staticmethod
    def _existence_check(existence: Existence):
        """
        Check if the existence type is valid.
        :param existence: The existence type to check.
        :return: True if valid, False otherwise.
        """
        if not isinstance(existence, Existence):
            raise ValueError(f"Invalid existence type: {existence}. Must be an instance of Existence.")
        return True

    @staticmethod
    def _determine_spell_type(
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
#endregion Spell Inspector Helpers
#endregion Bind