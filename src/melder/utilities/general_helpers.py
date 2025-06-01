from enum import Enum
from typing import TypeVar, Type

T = TypeVar("T", bound=Enum)

class EnumHelpers:
    @staticmethod
    def convert_enum_and_check(value: str, enum: Type[T]) -> T:
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