from enum import Enum, auto
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class DetailReason(Enum):
    """
    Why one `Detail` entry exists inside a contract.

    The ward uses this enum to distinguish directly shared lineages from
    transitive dependency-linked ones. That matters later when a root source is
    removed and the ward needs to know which contracted details should vanish
    with it and which ones were added independently.

    Meanings:
        - `root`: explicitly linked root spell.
        - `dependency`: linked because a root transitively required it.
        - `manual`: ad-hoc/manual addition outside automatic dependency linking.
        - `other`: fallback/unspecified reason.
    """
    __melder_internal__ = _mrg.sentinel
    root = auto()
    dependency = auto()
    manual = auto()
    other = auto()
