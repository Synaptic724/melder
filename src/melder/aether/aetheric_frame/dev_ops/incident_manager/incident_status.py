from enum import auto, Enum
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class IncidentStatus(Enum):
    """
    Lifecycle status for an `Incident`.

    Contract:
    - Status values describe where the incident sits in the operational review
      lifecycle, not the underlying runtime condition itself.
    - Status transitions are driven by `Incident` methods such as
      `acknowledge()`, `resolve()`, and `suppress()`.

    States:
    - `open`: Newly created and not yet triaged.
    - `acknowledged`: Seen/triaged but not yet resolved.
    - `resolved`: The incident has been marked as addressed.
    - `suppressed`: The incident is intentionally muted or accepted.

    Threading:
        Immutable enum members; safe to read from any thread.

    Registration:
        MELDER KERNEL - guarded, readable by value. Incident vocabulary.

    Subsystem Context:
        The lifecycle axis of an `Incident`, paired with `IncidentSeverity`
        (the urgency axis). Transitions are driven by `Incident` methods -
        `acknowledge()`, `resolve()`, `suppress()` - never by direct writes.

    System Context:
        The first contract line draws a distinction that is easy to lose:
        status tracks the OPERATIONAL REVIEW lifecycle, not the underlying
        runtime condition. An incident marked `resolved` means somebody
        addressed it; it does not assert that the runtime state which caused it
        has changed. Conflating the two would let a triage action silently
        imply a runtime claim nobody verified.
        `suppressed` exists as a first-class outcome for the same honesty
        reason - "intentionally muted or accepted" is a real and common
        disposition, and without it operators would resolve incidents they had
        merely decided to live with, destroying the distinction between fixed
        and tolerated.
    """
    _ast_helper_access: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Lifecycle status for an `Incident`. Melder kernel machinery: read it "
        "to understand the runtime, do not drive it directly."
    )
    __melder_internal__ = _mrg.sentinel
    open = auto()
    acknowledged = auto()
    resolved = auto()
    suppressed = auto()
