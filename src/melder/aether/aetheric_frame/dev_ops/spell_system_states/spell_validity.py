from enum import Enum, auto
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class SpellValidity(Enum):
    """
    Coarse validity gate used for both structural and resolution state.

    Usage:
        - Structural validity (global): stored on SpellSystemState and
          reflects Phases 1-4 spell-definition correctness.
        - Resolution validity (per-conduit): stored on ConduitResolutionState
          and reflects Phases 5-7 resolution correctness for a specific conduit.

    Semantics:
        - unknown:
            Newly registered or never validated. In basic mode this can be treated
            as "implicitly valid", in advanced modes it should usually be treated
            as gated until a validation pass runs.
        - valid:
            Safe to resolve; all required checks have passed.
        - gated:
            There is some gate that must be processed first (contracts, mutation
            promotion, ops policy, etc.). Resolution should not proceed until the
            gate is cleared.
        - invalid:
            Known-bad state (structural failure, contract violation, failed
            mutation release, etc.). Only allowed in forensic / lab contexts.
        - disabled:
            Explicitly turned off by policy. Hard "do not resolve" regardless of
            other flags.
        - cleaned:
            Index state has been removed during Spellbook cleanup. Hard
            "do not resolve" until re-registered and validated.

    Contract:
        - `SpellValidity` answers "may this thing currently participate?" at a
          coarse gate level; callers should inspect `SpellState` and
          `SpellStateChangeReason` for the reason behind non-valid states.
        - The same enum is reused for frame-level structural validity and
          conduit-local resolution validity, so callers must interpret the
          value in the context of the state object that owns it.
    """
    __melder_internal__ = _mrg.sentinel
    unknown = auto()
    valid = auto()
    gated = auto()
    invalid = auto()
    disabled = auto()
    cleaned = auto()
