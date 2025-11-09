import inspect
import threading
import hashlib
from typing import Any, Optional, Union

# Melder Imports
from melder.aether.conduit.spell_crafter.inspector.spell_examiner import (
    SpellExaminer, ClassProfile, MethodProfile
)
from melder.spellbook.spell_types.spell_types import SpellType
from melder.spellbook.existence.existence import Existence
from melder.utilities.interfaces.interfaces import IBind
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.spellbook.spell import Spell


#region Bind
class Bind(IBind):
    """
    The Bind class is responsible for the core registration of classes, methods, and
    objects as formal **Spells** within the Melder system.

    It acts as the single entry point for declaring a component's lifecycle (`Existence`),
    access control (`Permissions`), and structural identity. The process involves:
    1.  **Reflection:** Examining the object using `SpellExaminer` to create a `Profile`.
    2.  **Fingerprinting:** Generating a deterministic SHA256 unique ID (`spell_id`) based on the profile.
    3.  **Validation:** Enforcing rules regarding naming conventions, existence, and spell type.
    4.  **Registration:** Creating the final `Spell` object, which encapsulates the component
        and its metadata for resolution and dependency injection.
    """
    def __init__(self):
        super().__init__()
        self._lock = threading.RLock()

    def bind(self, permissions: Permissions, *, aetheric_frame: str, spell=None, spellframe=None, binding_name=None, existence=Existence.unique) -> Union[Spell, Any]:
        """
        Public API

        Registers a class, function, or existing object as a Spell within the Melder system.

        This method supports two usage patterns:
        1. **Direct Call:** `bind(permissions, spell=MyClass, ...)`
        2. **Decorator:** `@Bind.bind(permissions, ...)` applied to a class or function.

        The binding process creates a canonical `Spell` object, assigns it a unique ID based on its
        structure, and applies lifecycle (`existence`) and access control (`permissions`) policies.

        Args:
            permissions (Permissions): The access level for this spell (e.g., read, create, block).
            aetheric_frame (str): The Aetheric Frame (logical container) this spell belongs to.
            spell (Any, optional): The class, function, or existing object to bind. Required for direct usage.
            spellframe (Optional[Any]): Logical interface or category for grouping.
            binding_name (Optional[str]): A specific key used to distinguish this spell among others in its frame.
            existence (Existence): The lifecycle scope for this spell (default is `Existence.unique`).

        Returns:
            Union[Spell, Any]:
                - If used as a decorator, returns the decorated object.
                - If used as a direct call, returns the newly created `Spell` instance.
        """
        if spell is None:
            # Decorator usage
            def decorator(obj):
                return self._bind_logic(obj, spellframe, binding_name, existence, permissions, aetheric_frame)
            return decorator
        else:
            # Direct usage
            return self._bind_logic(spell, spellframe, binding_name, existence, permissions, aetheric_frame)

    def _bind_logic(self, spell: Any, spellframe: Optional[Any], binding_name: Optional[str], existence: Existence, permissions: Permissions, aetheric_frame: str) -> Spell:
        """
        Internal logic for processing the binding of a spell object.

        Args:
            spell (Any): The class, function, or existing object to bind.
            spellframe (Optional[Any]): Logical interface or category for grouping.
            binding_name (Optional[str]): A specific key used to distinguish this spell.
            existence (Existence): The lifecycle scope for this spell.
            permissions (Permissions): The access level for this spell.
            aetheric_frame (str): The Aetheric Frame this spell belongs to.

        Returns:
            Spell: The newly created and configured Spell instance.

        Raises:
            ValueError: If the binding is invalid (e.g., instance with binding name, lambda without name, invalid existence).
        """
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
                permissions=permissions,
                aetheric_frame = aetheric_frame
            )

            print(f"[BIND] Registered: {spell_name} | Frame: {spellframe} | Type: {spell_type} | Existence: {existence}")
            return new_spell

    #region Spell Inspector Helpers
    @staticmethod
    def spell_id_inspector(spell: Any) -> str:
        """
        Generates a unique identifier (SHA256 hash) for the spell based on its reflection profile.

        The ID is deterministic, ensuring the same spell definition always results in the same ID.

        Args:
            spell (Any): The spell object (class, function, or instance) to inspect.

        Returns:
            str: A unique identifier string (SHA256 hash) for the spell.
        """
        profile = SpellExaminer(spell).inspect()
        return Bind.sha256_profile(profile)

    @staticmethod
    def sha256_profile(profile: ClassProfile | MethodProfile) -> str:
        """
        Computes the SHA256 hash of a spell's profile metadata.

        The profile includes name, module, bases, method names, and source preview to create a
        unique, versioned fingerprint of the spell's structure.

        Args:
            profile (ClassProfile | MethodProfile): The reflection profile of the spell.

        Returns:
            str: The SHA256 hash string (fingerprint).
        """
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
        Performs structural and policy checks on the binding parameters prior to registration.

        Args:
            profile (ClassProfile | MethodProfile): The reflection profile of the spell.
            is_instance (bool): True if the spell is an existing object instance, False otherwise.
            binding_name (Optional[str]): The optional binding name provided.
            existence (Existence): The lifecycle scope provided.

        Raises:
            ValueError: If the binding violates any rule:
                - Existing instance bound with a binding name.
                - Lambda/method bound without a required binding name.
                - Method/lambda bound with an existence type other than `Existence.unique`.
                - Invalid `existence` type provided.
        """
        if Bind._existence_check(existence) is False:
            # Note: _existence_check itself raises ValueError, but included here for completeness
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
        Checks if the provided object is a valid instance of the `Existence` enum.

        Args:
            existence (Existence): The object to check.

        Returns:
            bool: True if the object is a valid `Existence` instance.

        Raises:
            ValueError: If the object is not an instance of `Existence`.
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
        """
        Determines the canonical `SpellType` based on the spell's reflection profile and binding metadata.

        This helps the system categorize the spell for later resolution (e.g., class, method, named, interfaced).

        Args:
            spell (Any): The original object being bound.
            profile (Union[ClassProfile, MethodProfile, dict]): The reflection profile of the spell.
            name (Optional[str]): The optional binding name provided.
            spellframe (Optional[Any]): The optional spell frame/interface provided.
            is_instance (bool): True if the spell is an existing object instance.

        Returns:
            SpellType: The determined type of the spell.
        """
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
            # Fallback for unexpected profile types (should align with is_instance check)
            return SpellType.EXISTING_CLASS if is_instance else SpellType.NORMAL
#endregion Spell Inspector Helpers
#endregion Bind