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

    Registration:
        MELDER KERNEL - guarded. The ward stamps this reason when it writes a
        `Detail`; callers do not author these entries directly.

    Subsystem Context:
        The PROVENANCE half of the detail vocabulary, paired with
        `ContractTypes` (which records the owning ward's perspective rather
        than the cause). Together they answer "who wrote this entry, and why
        does it exist" for every lineage inside a contract.

    System Context:
        This enum exists to make REMOVAL correct, not to describe creation. As
        the class notes, when a root source is removed the ward must know which
        contracted details vanish with it and which were added independently -
        so `dependency` entries cascade away with their root while `manual`
        entries survive, because a manual grant was never owned by that root in
        the first place. Without this distinction a single unlink would either
        strand orphaned dependency details or silently destroy grants a user
        added deliberately. `root` and `dependency` are written by automatic
        dependency linking; `manual` marks the deliberate ad-hoc path; `other`
        is the honest fallback rather than a guess.
    """
    __melder_internal__ = _mrg.sentinel
    root = auto()
    dependency = auto()
    manual = auto()
    other = auto()
