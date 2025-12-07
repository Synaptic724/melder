from enum import Enum, auto


class DetailReason(Enum):
    """
    Why a contract Detail exists in a contract.

    - root: explicitly linked root spell.
    - dependency: linked because a root requires it.
    - manual: ad-hoc/manual addition.
    - other: fallback/unspecified reasons.
    """

    root = auto()
    dependency = auto()
    manual = auto()
    other = auto()
