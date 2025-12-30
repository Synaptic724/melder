"""
context_compass.tools._shared.work_ids

Work identifier helpers.
"""

from secrets import choice
from string import ascii_lowercase, digits


_ALPHABET = ascii_lowercase + digits


def generate_work_id(length: int = 8) -> str:
    """
    Generate a short random work_id.

    Contract:
    - Uses lowercase letters and digits only.
    - Default length is 8 characters.

    Args:
        length (int): Desired id length.

    Returns:
        str: Random work id.
    """
    if length <= 0:
        raise ValueError("length must be positive")
    return "".join(choice(_ALPHABET) for _ in range(length))
