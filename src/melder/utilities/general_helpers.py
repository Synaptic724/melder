#    Copyright [2025] [Mark Thomas Geleta]
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0

from enum import Enum
import inspect
from typing import Any, Optional, Tuple, Union, TypeVar, Type


T = TypeVar("T", bound=Enum)

class EnumHelpers:
    @staticmethod
    def convert_enum_and_check(value: str | Enum, enum: Type[T]) -> T:
        """
        Converts a string input into the correct Enum member.
        Raises ValueError if the string doesn't match an enum name.

        If value is already an Enum member of the correct type, it is returned as-is.
        """
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

        This method ensures that the keys used for spell binding and resolution are consistent,
        regardless of input casing or type.

        Parameters:
            spell (Any): The spell object (used to derive name if spellframe is not provided).
            spellframe (Any): Optional spellframe object or string.
            binding_name (Optional[str]): Optional binding name.

        Returns:
            Tuple[str, str]: Normalized (frame_or_name, binding_name) pair.
        """
        raw_name = getattr(spell, "__name__", type(spell).__name__) if spell else None
        frame_base = spellframe or raw_name
        key_frame = SpellInputUtils.normalize_spellframe(frame_base).lower()
        key_name = (binding_name or "__default__").lower()
        return key_frame, key_name

    @staticmethod
    def normalize_spell_override(
            override: Union[dict, list, tuple, None],
            *,
            normalize_keys: bool = True
    ) -> Tuple[list, dict]:
        """
        Normalize the spell_override input into a structured (args, kwargs) form.

        - Dicts are treated as keyword arguments.
        - Lists or tuples are treated as positional arguments.
        - None results in empty arguments.

        Parameters:
            override (Union[dict, list, tuple, None]): The override structure.
            normalize_keys (bool): Whether to lowercase dict keys.

        Returns:
            Tuple[list, dict]: (args, kwargs) to pass into a spell's constructor.

        Raises:
            TypeError: If the override is not a valid type.
        """
        if override is None:
            return [], {}
        elif isinstance(override, dict):
            if normalize_keys:
                kwargs = {k.lower(): v for k, v in override.items()}
            else:
                kwargs = override
            return [], kwargs
        elif isinstance(override, (list, tuple)):
            return list(override), {}
        else:
            raise TypeError("spell_override must be dict, list, tuple, or None")
