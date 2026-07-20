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

    Threading:
        Immutable enum members; safe to read from any thread. It is read on the
        meld hot path, which is why the gate is coarse.

    Registration:
        MELDER KERNEL - guarded, readable by value. Control-plane vocabulary.

    Subsystem Context:
        The GATE axis of the three-axis validity model: `SpellValidity` answers
        "may this participate", `SpellState` flags explain the condition, and
        `SpellStateChangeReason` records the triggering event. Reusing one enum
        across `SpellSystemState` (structural, frame-global) and
        `ConduitResolutionState` (resolution, per-conduit) is deliberate - the
        QUESTION is identical, only the scope differs.

    System Context:
        Coarseness is the design, not a shortcut. Meld reads this value on
        every resolution, so the gate must be answerable with one comparison;
        anything richer would push parsing onto the hot path. The detail lives
        on the two companion axes for the diagnostic path, which is cold.
        The `unknown` semantics carry the load-bearing subtlety: it means
        "never validated", not "invalid", and how it is treated is MODE
        DEPENDENT - implicitly valid in basic mode, gated in advanced modes.
        That is what makes lazy validation possible at all. A newly registered
        lineage starts `unknown`, and `Meld._ensure_lineage_resolvable` reruns
        the structural phases on first resolution rather than requiring an
        eager frame-wide validation pass at bind time.
        `disabled` and `cleaned` are both hard refusals but for different
        reasons - policy versus lifecycle - and keeping them distinct is what
        lets diagnostics tell "someone turned this off" apart from "this was
        torn down", which are very different operator problems.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Coarse validity gate used for both structural and resolution state. "
        "Melder kernel machinery: read it to understand the runtime, do not drive it directly."
    )
    __melder_internal__ = _mrg.sentinel
    unknown = auto()
    valid = auto()
    gated = auto()
    invalid = auto()
    disabled = auto()
    cleaned = auto()
