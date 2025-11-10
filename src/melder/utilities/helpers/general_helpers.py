

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

    A utility class to standardize and normalize spell-related input data in the Melder framework.

    This includes:
    - Normalizing spellframes (class or string) into consistent lowercase string identifiers.
    - Resolving consistent keys for spell registration and lookup.
    - Standardizing the structure of spell overrides passed into meld or spell construction.

    This utility ensures consistency between spell binding and resolution.

    Usage Examples:
    ---------------

    1. Normalize spell key for registration and lookup:
        >>> SpellInputUtils.normalize_spell_key(spell=MyService, spellframe=IMyService)
        ('imyservice', '__default__')

    2. Normalize positional or keyword overrides:
        >>> SpellInputUtils.normalize_spell_override({"Url": "http://...", "Timeout": 5})
        ([], {'url': 'http://...', 'timeout': 5})

        >>> SpellInputUtils.normalize_spell_override(["localhost", 123])
        (['localhost', 123], {})

        >>> SpellInputUtils.normalize_spell_override(None)
        ([], {})

    Author: Mark Thomas Geleta
    License: Apache 2.0
    """


    @staticmethod
    @lru_cache(maxsize=16)
    def normalize_spellframe(spellframe: Any) -> str:
        """
        Normalize a spellframe into a consistent string identifier.

        Parameters:
            spellframe (Any): The object, class, or string representing the spellframe.

        Returns:
            str: Normalized string version of the spellframe.
        """
        if inspect.isclass(spellframe):
            return spellframe.__name__
        if isinstance(spellframe, str):
            return spellframe
        return str(spellframe)

    @staticmethod
    def normalize_spell_key(
        spell: Any = None,
        spellframe: Any = None,
        binding_name: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Generate a normalized key for spellbook lookup and registration.

        Parameters:
            spell (Any): The spell object (used to derive name if spellframe is not provided).
            spellframe (Any): Optional spellframe object or string.
            binding_name (Optional[str]): Optional binding name.

        Returns:
            Tuple[str, str]: Normalized (frame_or_name, binding_name) pair.
        """
        raw_name = getattr(spell, "__name__", type(spell).__name__) if spell else None
        frame_base = spellframe or raw_name
        frame_key = SpellInputUtils._normalize_frame_cached(frame_base)
        name_key = SpellInputUtils._normalize_binding_name(binding_name)
        return frame_key, name_key

    @staticmethod
    @lru_cache(maxsize=64)
    def _normalize_frame_cached(spellframe: Any) -> str:
        """
        Cached normalization of the spellframe for consistent lookup keys.
        """
        return SpellInputUtils._normalize_frame_uncached(spellframe).lower()

    @staticmethod
    def _normalize_frame_uncached(spellframe: Any) -> str:
        """
        Uncached normalization logic.
        """
        if inspect.isclass(spellframe):
            return spellframe.__name__
        if isinstance(spellframe, str):
            return spellframe
        return str(spellframe)

    @staticmethod
    @lru_cache(maxsize=64)
    def _normalize_binding_name(name: Optional[str]) -> str:
        """
        Cached normalization for binding names (defaults to '__default__').
        """
        return (name or "__default__").lower()