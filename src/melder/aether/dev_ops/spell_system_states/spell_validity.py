from enum import Enum, auto
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class SpellValidity(Enum):
    """
    Coarse resolution gate for a spell lineage.

    This is the **first thing** Meld / Conduits should look at when deciding
    whether a lineage may be resolved for prod traffic.

    Semantics:
    - unknown:
        Newly registered or never validated. In basic mode this can be treated
        as "implicitly valid", in advanced modes it should usually be treated
        as gated until a validation pass runs.
    - valid:
        Safe to resolve in prod; all required checks have passed.
    - gated:
        There is some gate that must be processed first (contracts, mutation
        promotion, ops policy, etc.). Prod should not resolve this lineage
        until the gate is cleared.
    - invalid:
        Known-bad lineage (structural failure, contract violation, failed
        mutation release, etc.). Only allowed in forensic / lab contexts.
    - disabled:
        Explicitly turned off by policy. Hard "do not resolve" regardless of
        other flags.
    """
    __melder_internal__ = _mrg.sentinel
    unknown = auto()
    valid = auto()
    gated = auto()
    invalid = auto()
    disabled = auto()