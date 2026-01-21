from enum import Enum, auto
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class DetailReason(Enum):
    """
    Why a contract Detail exists in a contract.

    - root: explicitly linked root spell.
    - dependency: linked because a root requires it.
    - manual: ad-hoc/manual addition.
    - other: fallback/unspecified reasons.
    """
    __melder_internal__ = _mrg.sentinel
    root = auto()
    dependency = auto()
    manual = auto()
    other = auto()
