from enum import StrEnum
from typing import Optional

class IncidentStatus(StrEnum):
    """
    Lifecycle status for an `Incident`.

    Contract:
    - Status values describe where the incident sits in the operational review
      lifecycle, not the underlying runtime condition itself.
    - String values exactly match member names; historical numeric values 1-4
      remain readable by value, including in older pickle payloads.
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

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Lifecycle status for an `Incident`. Melder kernel machinery: read it
        to understand the runtime, do not drive it directly.
    """
    open = "open"
    acknowledged = "acknowledged"
    resolved = "resolved"
    suppressed = "suppressed"

    @classmethod
    def _missing_(cls, value: object) -> Optional[IncidentStatus]:
        """
        Resolve a historical numeric status to its original member.

        Exact current strings use ordinary enum lookup. Values equal to the
        four old integer values retain by-value and old-pickle readability.
        Unknown or unhashable inputs return None for normal ValueError.
        """
        legacy_values: dict[object, IncidentStatus] = {
            1: cls.open,
            2: cls.acknowledged,
            3: cls.resolved,
            4: cls.suppressed,
        }
        try:
            return legacy_values.get(value)
        except TypeError:
            return None
