from enum import Enum
import inspect
from functools import lru_cache
from typing import Any, Optional, Tuple, Union, TypeVar, Type


T = TypeVar("T", bound=Enum)

class EnumHelpers:
    @staticmethod
    @lru_cache(maxsize=8)
    def convert_enum_and_check(value: str | Enum, enum: Type[T]) -> T:
        """
        Converts a string input into the correct Enum member.
        Raises ValueError if the string doesn't match an enum name.

        If value is already an Enum member of the correct type, it is returned as-is.
        """
        if value is None:
            raise ValueError("Enum value cannot be None.")

        if isinstance(value, enum):
            return value

        if isinstance(value, str):
            try:
                return enum[value.lower()]
            except KeyError:
                valid_options = [e.name for e in enum]
                raise ValueError(
                    f"Invalid value '{value}' for enum {enum.__name__}. "
                    f"Expected one of: {valid_options}."
                )

        raise ValueError(
            f"Expected a string or {enum.__name__} member, got {type(value).__name__}."
        )

class SpellInputUtils:
    """
    SpellInputUtils
    ===============

    Canonical normalization utilities for spell identification in Melder.

    This class defines the *single source of truth* for how we turn:
        - spellframes (Protocols / interfaces / classes / strings)
        - spell names (class/function names)
        - binding names

    into **case-insensitive lookup keys** used by:

        - Spellbook (binding + lookup)
        - Bind (when constructing Spell._key)
        - Meld (when resolving a spell from (frame, binding_name))

    Design Rules
    ------------

    1. **Case-insensitive keys**:
       All keys are normalized to lowercase for lookups. Display names stay
       on the Spell itself (spell.spell_name, spell.spellframe, etc.).

    2. **Key shape matches Spellbook semantics**:
       We always build keys as:

           (frame_or_name, binding_name_or_default)

       where:
           frame_or_name     = spellframe if provided, else spell_name
           binding_name      = binding_name if provided, else "__default__"

       but both components are **lowercased** for the key.

    3. **Stable, deterministic**:
       The same spell + spellframe + binding_name will *always* normalize
       to the same (frame_key, binding_key) pair.

    4. **Separation of concerns**:
       - These helpers are for *keys only*.
       - Human-readable names live on Spell / SpellIndex and are not forced
         to lowercase there.

    Typical Usage
    -------------

    * When binding a spell (inside Spellbook / Bind):

        spell_name = type(spell).__name__ or spell.__name__
        key = SpellInputUtils.make_spell_key_from_parts(
            spellframe=spellframe,
            spell_name=spell_name,
            binding_name=binding_name,
        )

    * When resolving in Meld:

        frame_key, bind_key = SpellInputUtils.normalize_spell_key(
            spell=spell_obj_or_None,
            spellframe=spellframe,
            binding_name=binding_name,
        )

    After we wire this up, *all* spell key usage (bind + lookup) should
    flow through these helpers.
    """

    # Public constant so everyone uses the same default
    DEFAULT_BINDING_NAME: str = "__default__"

    # ------------------------------------------------------------------
    # Frame / name normalization
    # ------------------------------------------------------------------
    @staticmethod
    @lru_cache(maxsize=64)
    def normalize_frame_key(frame: Any) -> str:
        """
        Normalize a spellframe / frame identifier into a lowercase key.

        Inputs:
            - A Protocol class
            - A concrete class
            - A string frame name
            - Any other object (fallback to str(obj))

        Returns:
            str: Lowercased string used as the "frame" component of the key.

        Examples:
            ICache        -> "icache"
            "ICache"      -> "icache"
            MyService     -> "myservice"
        """
        if inspect.isclass(frame):
            raw = frame.__name__
        elif isinstance(frame, str):
            raw = frame
        else:
            raw = str(frame)
        return raw.lower()

    @staticmethod
    def normalize_spell_name(spell: Any) -> str:
        """
        Normalize a spell object into a canonical spell *name*.

        This is primarily used as a fallback when no spellframe is passed in.

        Returns:
            str: The spell name (NOT lowercased; this is a display name).
        """
        # This is for display/metadata; we don't lowercase here so that
        # spell.spell_name can remain pretty. The key path lowercases later.
        return getattr(spell, "__name__", type(spell).__name__)

    # ------------------------------------------------------------------
    # Binding name normalization
    # ------------------------------------------------------------------
    @staticmethod
    @lru_cache(maxsize=64)
    def normalize_binding_name(binding_name: Optional[str]) -> str:
        """
        Normalize a binding name into a lowercase key.

        If no binding name is provided, DEFAULT_BINDING_NAME ("__default__")
        is used.

        Returns:
            str: Lowercased binding name, or "__default__" if None/empty.

        Examples:
            None           -> "__default__"
            "Redis"        -> "redis"
            "MyVariant_01" -> "myvariant_01"
        """
        if not binding_name:
            return SpellInputUtils.DEFAULT_BINDING_NAME
        return binding_name.lower()

    # ------------------------------------------------------------------
    # Key construction helpers
    # ------------------------------------------------------------------
    @staticmethod
    def make_spell_key_from_parts(
            *,
            spellframe: Any | None,
            spell_name: str,
            binding_name: Optional[str],
    ) -> Tuple[str, str]:
        """
        Build a canonical (frame_key, binding_key) from explicit parts.

        This is the direct equivalent of the older Spellbook._make_spell_key,
        but with case-insensitive semantics baked in.

        Semantics:
            frame_base = spellframe if not None, else spell_name
            frame_key  = normalize_frame_key(frame_base)
            binding_key = normalize_binding_name(binding_name)

        Args:
            spellframe:
                The logical frame / interface / protocol. May be None.
            spell_name:
                The spell's explicit name (usually class.__name__).
            binding_name:
                Optional binding name (None means "__default__").

        Returns:
            Tuple[str, str]: (frame_key, binding_key)
        """
        frame_base = spellframe if spellframe is not None else spell_name
        frame_key = SpellInputUtils.normalize_frame_key(frame_base)
        bind_key = SpellInputUtils.normalize_binding_name(binding_name)
        return frame_key, bind_key

    @staticmethod
    def normalize_spell_key(
            *,
            spell: Any | None = None,
            spellframe: Any | None = None,
            binding_name: Optional[str] = None,
    ) -> Tuple[str, str]:
        """
        Derive a canonical (frame_key, binding_key) using either a spell
        object or an explicit spellframe.

        This is the helper you want for most resolution cases (e.g. Meld).

        Resolution:
            1. spell_name = normalize_spell_name(spell) if spell is provided
            2. frame_base = spellframe if not None, else spell_name
            3. frame_key  = normalize_frame_key(frame_base)
            4. binding_key = normalize_binding_name(binding_name)

        At least ONE of (spell, spellframe) must be non-None. If both are
        None, a ValueError is raised.

        Args:
            spell:
                Optional spell object (class/function/instance). Used only
                to derive a name when spellframe is not supplied.
            spellframe:
                Optional frame/interface/protocol for grouping and DI keys.
            binding_name:
                Optional binding name; None means "__default__".

        Returns:
            Tuple[str, str]: (frame_key, binding_key)

        Raises:
            ValueError: If both `spell` and `spellframe` are None.
        """
        if spell is None and spellframe is None:
            raise ValueError(
                "normalize_spell_key requires at least one of `spell` or `spellframe`."
            )

        spell_name: Optional[str] = None
        if spell is not None:
            spell_name = SpellInputUtils.normalize_spell_name(spell)

        frame_base = spellframe if spellframe is not None else spell_name
        frame_key = SpellInputUtils.normalize_frame_key(frame_base)
        bind_key = SpellInputUtils.normalize_binding_name(binding_name)
        return frame_key, bind_key
